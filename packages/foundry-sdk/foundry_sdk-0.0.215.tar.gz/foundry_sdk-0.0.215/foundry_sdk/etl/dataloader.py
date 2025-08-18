import logging
from datetime import date

import polars as pl
from sqlalchemy import or_
from sqlalchemy.ext.declarative import DeclarativeMeta

from foundry_sdk.db_mgmt import SQLAlchemyDatabase
from foundry_sdk.db_mgmt.tables import (
    Categories,
    CategoryLevelDescriptions,
    CategoryRelations,
    Companies,
    Datapoints,
    FeatureDescriptions,
    FeatureLevels,
    ProductCategories,
    ProductFeatures,
    Products,
    Regions,
    SkuFeatures,
    SkuTable,
    StoreFeatures,
    Stores,
    TimeProductFeatures,
    TimeRegionFeatures,
    TimeSkuFeatures,
    TimeStoreFeatures,
)
from foundry_sdk.db_mgmt.utils.data_retrieval import get_all_dates

from .constants import FlagLevels

# from foundry_sdk.etl.constants import FlagLevels

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading of data into the database using the write_* methods."""

    def __init__(self, db: SQLAlchemyDatabase, insertion_mode: str) -> None:
        """
        Args:
            db (SQLAlchemyDatabase): Database connection object.
            insertion_mode (InsertionMode): Mode for database insertion.

        """
        # db ignored, is legacy, will be removed from arguments in the future
        self.insertion_mode = insertion_mode
        self.db = db  # to be removed in the future

    #################################### Mandatory data ############################################

    @staticmethod
    def check_check_passed(*, check_passed: bool) -> None:
        if not check_passed:
            raise ValueError("wait for all checks to pass")

    def write_company(
        self,
        name: str,
        dataset_type: str,
        description: str,
        min_date: date,
        max_date: date,
        frequency: int,
        *,
        check_passed: bool,
    ) -> int:
        """Writes the company metadata and returns the company ID."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        # Prepare company data as dictionary
        company_data = {
            "name": name,
            "dataset_type": dataset_type,
            "description": description,
            "min_date": min_date,
            "max_date": max_date,
            "frequency": frequency,
        }

        # Use the modern insertion method with configured mode
        company_id = db.handle_insertion_single_line(
            model_class=Companies,
            data=company_data,
            mode=self.insertion_mode,
            returning_id=True,
        )

        logger.info("Writing company '%s' to db complete, got ID %s", name, company_id)
        return company_id

    def write_stores(self, store_region_map: pl.DataFrame, company_id: int, *, check_passed: bool) -> pl.DataFrame:
        """Write store entries to the database."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        # Get unique combinations of region, country, level to look up region IDs
        region_lookup = store_region_map.select(["region", "country", "level"]).unique()

        with db.get_session(read_only=True) as session:
            # Query region IDs from database
            country_abbrevs = region_lookup.select("country").unique().to_series().to_list()
            country_query = (
                session.query(Regions.id, Regions.abbreviation)
                .filter(Regions.abbreviation.in_(country_abbrevs), Regions.type == "country")
                .all()
            )

            country_id_map = {abbrev: region_id for region_id, abbrev in country_query}

            # Build region lookup with country IDs
            region_lookup_with_country_ids = region_lookup.with_columns(
                pl.col("country").replace(country_id_map).alias("country_id").cast(pl.Int64)
            )

            # Query all region IDs in one batch
            region_conditions = [
                (Regions.abbreviation == row["region"])
                & (Regions.type == row["level"])
                & (Regions.country == row["country_id"])
                for row in region_lookup_with_country_ids.to_dicts()
            ]

            region_results = (
                session.query(Regions.id, Regions.abbreviation, Regions.type, Regions.country)
                .filter(or_(*region_conditions))
                .all()
            )

            # Build Polars DataFrame directly from results
            region_id_df = pl.DataFrame(
                [
                    {
                        "region_id": region_id,
                        "region": abbreviation,
                        "level": region_type,
                        "country_id": country_id,
                    }
                    for region_id, abbreviation, region_type, country_id in region_results
                ]
            )

        store_region_map = (
            store_region_map.join(region_lookup_with_country_ids, on=["region", "country", "level"], how="left")
            .join(region_id_df, on=["region", "country_id", "level"], how="left")
            .select(["store", "region_id"])
            .rename({"region_id": "regionID", "store": "name"})
            .with_columns(companyID=pl.lit(company_id))
        )

        # Use bulk insertion method
        result = db.handle_insertion_multi_line(
            model_class=Stores,
            data=store_region_map,
            mode=self.insertion_mode,
            returning_id=True,
        )

        logger.info("Writing stores to db complete, got %d store IDs back", len(result))

        return result

    def write_categories(
        self,
        categories_dict: dict,
        categories_level_description: pl.DataFrame,
        company_id: int,
        *,
        check_passed: bool,
    ) -> pl.DataFrame:
        """Writes categories and their relations to the database."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        # Prepare category level descriptions
        categories_level_description = categories_level_description.with_columns(companyID=pl.lit(company_id)).sort(
            "level"
        )

        # Write category level descriptions
        db.handle_insertion_multi_line(
            model_class=CategoryLevelDescriptions,
            data=categories_level_description,
            mode=self.insertion_mode,
            returning_id=False,
        )
        logger.info("Successfully wrote %d category level descriptions", len(categories_level_description))

        all_categories = []
        all_relations = []

        # Process categories by level
        for row in categories_level_description.to_dicts():
            level = row["level"]
            level_name = row["name"]
            logger.info("Processing level %d: %s", level, level_name)

            relevant_categories = categories_dict[level]

            # Prepare unique categories for this level
            unique_categories = pl.DataFrame(
                {"name": list(relevant_categories.keys()), "companyID": [company_id] * len(relevant_categories)}
            )

            # Write categories for this level
            categories_result = db.handle_insertion_multi_line(
                model_class=Categories,
                data=unique_categories,
                mode=self.insertion_mode,
                returning_id=True,
            )

            all_categories.append(categories_result)

            # Process category relations if there are parent-child relationships
            if relevant_categories:
                relations_data = self._extract_category_relations(relevant_categories)
                if not relations_data.is_empty():
                    # Get category IDs for relations
                    relations_with_ids = self._resolve_category_relation_ids(
                        db, relations_data, company_id, is_top_level=level == categories_level_description[0, "level"]
                    )

                    if not relations_with_ids.is_empty():
                        # Write category relations
                        db.handle_insertion_multi_line(
                            model_class=CategoryRelations,
                            data=relations_with_ids,
                            mode=self.insertion_mode,
                            returning_id=False,
                        )
                        all_relations.append(relations_with_ids)

            logger.info("Successfully wrote level %d categories (%s) into the database", level, level_name)

        # Combine all category results
        if all_categories:
            return pl.concat(all_categories)

        return pl.DataFrame(schema={"name": pl.Utf8, "companyID": pl.Int64, "ID": pl.Int64})

    def _extract_category_relations(self, categories_dict: dict) -> pl.DataFrame:
        """Extract parent-child relationships from categories dictionary."""
        relations = []

        for child_name, parents in categories_dict.items():
            if isinstance(parents, list | tuple | dict):
                parent_names = parents if isinstance(parents, list | tuple) else list(parents.keys())
                for parent_name in parent_names:
                    relations.append({"parentCategory": parent_name, "subCategory": child_name})

        if relations:
            return pl.DataFrame(relations)

        return pl.DataFrame(schema={"parentCategory": pl.Utf8, "subCategory": pl.Utf8})

    def _resolve_category_relation_ids(
        self,
        db: SQLAlchemyDatabase,
        relations_df: pl.DataFrame,
        company_id: int,
        *,
        is_top_level: bool,
    ) -> pl.DataFrame:
        """Resolve category names to IDs for relations."""
        if relations_df.is_empty():
            return pl.DataFrame(schema={"subID": pl.Int64, "parentID": pl.Int64})

        # Get unique category names
        sub_categories = relations_df.select("subCategory").unique().to_series().to_list()
        parent_categories = relations_df.select("parentCategory").unique().to_series().to_list()
        all_category_names = list(set(sub_categories + parent_categories))

        # Query category IDs in batch
        with db.get_session(read_only=True) as session:
            category_results = (
                session.query(Categories.id, Categories.name)
                .filter(Categories.company_id == company_id, Categories.name.in_(all_category_names))
                .all()
            )

        # Build category name to ID mapping
        category_id_map = {name: cat_id for cat_id, name in category_results}

        # Add IDs to relations
        relations_with_ids = relations_df.with_columns(
            [
                pl.col("subCategory").replace(category_id_map).alias("subID").cast(pl.Int64),
                pl.col("parentCategory").replace(category_id_map).alias("parentID").cast(pl.Int64),
            ]
        ).select(["subID", "parentID"])

        # For top level, remove relations where parent ID is null (no parent)
        if is_top_level:
            relations_with_ids = relations_with_ids.drop_nulls()

        return relations_with_ids

    def write_products(self, products: pl.DataFrame, company_id: int, *, check_passed: bool) -> pl.DataFrame:
        """Writes product entries to the database."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        products = (
            products.with_columns(
                companyID=pl.lit(company_id),
            )
            .drop("category")
            .rename({"product": "name"})
            .unique()
        )

        # Use bulk insertion method
        result = db.handle_insertion_multi_line(
            model_class=Products,
            data=products,
            mode=self.insertion_mode,
            returning_id=True,
        )

        logger.info("Writing products to db complete, got %d product IDs back", len(result))

        return result

    def write_product_categories(
        self,
        products: pl.DataFrame,
        product_ids: pl.DataFrame,
        category_ids: pl.DataFrame,
        *,
        check_passed: bool,
    ) -> pl.DataFrame:
        """Link products to categories and write associations."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        # Create product-category mapping using polars-native operations
        products = (
            products.join(
                product_ids.rename({"name": "product", "ID": "productID"}),
                on="product",
                how="left",
            )
            .join(
                category_ids.select(["name", "ID"]).rename({"name": "category", "ID": "categoryID"}),
                on="category",
                how="left",
            )
            .select(["productID", "categoryID"])
        )

        # Use bulk insertion method
        db.handle_insertion_multi_line(
            model_class=ProductCategories,
            data=products,
            mode=self.insertion_mode,
            returning_id=False,
        )

        logger.info("Writing product categories to db complete, linked %d product-category pairs", len(products))

        return True

    def write_skus(
        self,
        time_sku_data: pl.DataFrame,
        store_ids: pl.DataFrame,
        product_ids: pl.DataFrame,
        *,
        check_passed: bool,
    ) -> pl.DataFrame:
        """Write SKU entries (product-store combinations) to the database."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        # Get unique store-product pairs
        time_sku_data = (
            time_sku_data.select(["store", "product"])
            .unique()
            .join(store_ids.drop("companyID").rename({"name": "store", "ID": "storeID"}), on="store", how="left")
            .join(
                product_ids.drop("companyID").rename({"name": "product", "ID": "productID"}), on="product", how="left"
            )
        )
        time_sku_combinations = time_sku_data.select(["storeID", "productID"])

        # Write to SKU table
        result = db.handle_insertion_multi_line(
            model_class=SkuTable,
            data=time_sku_combinations,
            mode=self.insertion_mode,
            returning_id=True,
        )

        time_sku_data = time_sku_data.join(result.rename({"ID": "skuID"}), on=["storeID", "productID"], how="left")

        logger.info("Writing SKUs to db complete, got %d sku IDs back", len(result))

        return time_sku_data  # this is sku_ids in the next function

    def write_datapoints(
        self,
        time_sku_data: pl.DataFrame,
        sku_ids: pl.DataFrame,
        *,
        check_passed: bool,
    ) -> pl.DataFrame:
        """Create and write datapoint entries (sku-time combinations)."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        # Get all dates from the database
        dates_df = get_all_dates(db)

        # Merge time_sku_data with sku_ids on product, store
        time_sku_data = (
            time_sku_data.select(["product", "store", "date"])
            .unique()
            .join(sku_ids, on=["product", "store"], how="left")
            .join(dates_df, on="date", how="left")
            .select(["skuID", "dateID"])
        )

        # Write to Datapoints table
        result = db.handle_insertion_multi_line(
            model_class=Datapoints,
            data=time_sku_data,
            mode=self.insertion_mode,
            returning_id=True,
            parallel_workers=4,
        )

        logger.info("Writing datapoints to db complete, got %d datapoint IDs back", len(result))

        result = (
            result.rename({"ID": "datapointID"})
            .join(sku_ids, on=["skuID"], how="left")
            .join(dates_df, on=["dateID"], how="left")
        )

        return result

    def write_time_sku_data(
        self,
        time_sku_feature_description_map: pl.DataFrame,
        time_sku_data: pl.DataFrame,
        datapoint_ids: pl.DataFrame,
        company_id: int,
        *,
        check_passed: bool,
    ) -> bool:
        """Write Time-SKU-data into the database."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        # Prepare feature description map
        time_sku_feature_description_map = time_sku_feature_description_map.with_columns(
            companyID=pl.lit(company_id), feature_type=pl.lit("time_sku")
        ).drop("levels")

        # Write feature descriptions
        feature_description_result = db.handle_insertion_multi_line(
            model_class=FeatureDescriptions,
            data=time_sku_feature_description_map,
            mode=self.insertion_mode,
            returning_id=True,
        )

        time_sku_data = (
            time_sku_data.join(
                feature_description_result.rename({"name": "feature", "ID": "featureID"}),
                on="feature",
                how="left",
            )
            .join(
                datapoint_ids.select(["datapointID", "product", "store", "date"]),
                on=["product", "store", "date"],
                how="left",
            )
            .select(["datapointID", "featureID", "value"])
        )
        
        db.handle_insertion_multi_line(
            model_class=TimeSkuFeatures,
            data=time_sku_data,
            mode=self.insertion_mode,
            returning_id=False,
            parallel_workers=4,
        )

        logger.info("Writing time-sku features to the database complete, wrote %d rows", len(time_sku_data))

        return True

    def write_flags(
        self,
        flags: pl.DataFrame,
        datapoint_ids: pl.DataFrame,
        company_id: int,
        *,
        check_passed: bool,
    ) -> bool:
        """Write flags to the database."""
        DataLoader.check_check_passed(check_passed=check_passed)

        if flags.is_empty():
            logger.info("No flags to write")
            return True

        db = SQLAlchemyDatabase.from_kedro()

        all_flags = [f.value for f in FlagLevels]

        flag_description_map = pl.DataFrame(
            {
                "name": all_flags,
                "description": ["Flag indicating ..."] * len(all_flags),
                "var_type": ["binary"] * len(all_flags),
                "companyID": [company_id] * len(all_flags),
                "feature_type": ["time_sku"] * len(all_flags),
            }
        )

        feature_description_result = db.handle_insertion_multi_line(
            model_class=FeatureDescriptions,
            data=flag_description_map,
            mode=self.insertion_mode,
            returning_id=True,
            parallel_workers=4,
        )

        # Prepare flags
        flags = (
            flags.with_columns(
                value=pl.lit(1).cast(pl.Float64),  # Assuming flags are binary indicators
            )
            .rename({"flag": "feature"})
            .join(
                feature_description_result.rename({"ID": "featureID", "name": "feature"}),
                on="feature",
                how="left",
            )
            .join(
                datapoint_ids.select(["datapointID", "product", "store", "date"]),
                on=["product", "store", "date"],
                how="left",
            )
            .select(["datapointID", "featureID", "value"])
        )

        # Write flags to the database
        db.handle_insertion_multi_line(
            model_class=TimeSkuFeatures,  # Assuming TimeSkuFeatures can also handle flags
            data=flags,
            mode=self.insertion_mode,
            returning_id=False,
            parallel_workers=4,
        )

        logger.info("Writing flags to the database complete, wrote %d rows", len(flags))

        return True

    # #################################### Optional data #############################################

    def _write_levels(
        self,
        db: SQLAlchemyDatabase,
        feature_description_map: pl.DataFrame,
        feature_description_result: pl.DataFrame,
    ) -> None:
        num_cat = feature_description_map.filter(pl.col("var_type") == "categorical").shape[0]

        if num_cat == 0:
            return

        feature_description_map = (
            feature_description_map.filter(pl.col("var_type") == "categorical")
            .join(
                feature_description_result.rename({"ID": "featureID"}),
                on="name",
                how="left",
            )
            .drop(["description", "name", "var_type", "companyID"])
            .explode("levels")
            .with_row_index("order")
            .rename({"levels": "level"})
            .select(["featureID", "level", pl.col("order").cast(pl.Int32)])
        )

        db.handle_insertion_multi_line(
            model_class=FeatureLevels,
            data=feature_description_map,
            mode=self.insertion_mode,
            returning_id=False,
        )

    def _write_feature_data(
        self,
        feature_description_map: pl.DataFrame,
        feature_map: pl.DataFrame,
        ids: pl.DataFrame,
        company_id: int,
        feature_type: str,
        id_col_names: dict[str, str],
        merge_col_names: list[str],
        select_col_names: list[str],
        sql_table_class: DeclarativeMeta,
        dates_df: pl.DataFrame | None = None,
    ) -> bool:
        db = SQLAlchemyDatabase.from_kedro()

        if feature_description_map.is_empty():
            logger.info("No feature data to write for %s features", feature_type)
            return True

        # Prepare feature description map
        feature_description_map_for_insert = feature_description_map.with_columns(
            companyID=pl.lit(company_id), feature_type=pl.lit(feature_type)
        ).drop("levels")

        # Write feature descriptions
        feature_description_result = db.handle_insertion_multi_line(
            model_class=FeatureDescriptions,
            data=feature_description_map_for_insert,
            mode=self.insertion_mode,
            returning_id=True,
        )

        self._write_levels(db, feature_description_map, feature_description_result)

        feature_map = feature_map.join(
            feature_description_result.rename({"name": "feature", "ID": "featureID"}),
            on="feature",
            how="left",
        ).join(
            ids.rename(id_col_names),
            on=merge_col_names,
            how="left",
        )

        # Optionally join with dates if provided
        if dates_df is not None:
            feature_map = feature_map.join(dates_df, on="date", how="left")

        feature_map = feature_map.select(select_col_names)

        db.handle_insertion_multi_line(
            model_class=sql_table_class,
            data=feature_map,
            mode=self.insertion_mode,
            returning_id=False,
            parallel_workers=2,  # anything not time-sku should use 2 worker
        )

        logger.info("Writing %s features to the database complete, wrote %d rows", feature_type, len(feature_map))

        return True

    def write_store_data(
        self,
        store_feature_description_map: pl.DataFrame,
        store_feature_map: pl.DataFrame,
        store_ids: pl.DataFrame,
        company_id: int,
        *,
        check_passed: bool,
    ) -> bool:
        """Write store data into the database."""
        DataLoader.check_check_passed(check_passed=check_passed)

        feature_type = "store"
        id_col_names = {"name": "store", "ID": "storeID"}
        merge_col_names = ["store"]
        select_col_names = ["storeID", "featureID", "value"]
        sql_table_class = StoreFeatures

        return self._write_feature_data(
            feature_description_map=store_feature_description_map,
            feature_map=store_feature_map,
            ids=store_ids,
            company_id=company_id,
            feature_type=feature_type,
            id_col_names=id_col_names,
            merge_col_names=merge_col_names,
            select_col_names=select_col_names,
            sql_table_class=sql_table_class,
        )

    def write_product_data(
        self,
        product_feature_description_map: pl.DataFrame,
        product_feature_map: pl.DataFrame,
        product_ids: pl.DataFrame,
        company_id: int,
        *,
        check_passed: bool,
    ) -> bool:
        """Write product data into the database."""
        DataLoader.check_check_passed(check_passed=check_passed)

        feature_type = "product"
        id_col_names = {"name": "product", "ID": "productID"}
        merge_col_names = ["product"]
        select_col_names = ["productID", "featureID", "value"]
        sql_table_class = ProductFeatures

        return self._write_feature_data(
            feature_description_map=product_feature_description_map,
            feature_map=product_feature_map,
            ids=product_ids,
            company_id=company_id,
            feature_type=feature_type,
            id_col_names=id_col_names,
            merge_col_names=merge_col_names,
            select_col_names=select_col_names,
            sql_table_class=sql_table_class,
        )

    def write_sku_data(
        self,
        sku_feature_description_map: pl.DataFrame,
        sku_feature_map: pl.DataFrame,
        sku_ids: pl.DataFrame,
        company_id: int,
        *,
        check_passed: bool,
    ) -> bool:
        """Write SKU data into the database."""
        DataLoader.check_check_passed(check_passed=check_passed)

        feature_type = "sku"
        id_col_names = {"skuID": "skuID"}  # SKU already has the ID we need
        merge_col_names = ["product", "store"]  # Match on both product and store
        select_col_names = ["skuID", "featureID", "value"]
        sql_table_class = SkuFeatures

        return self._write_feature_data(
            feature_description_map=sku_feature_description_map,
            feature_map=sku_feature_map,
            ids=sku_ids,
            company_id=company_id,
            feature_type=feature_type,
            id_col_names=id_col_names,
            merge_col_names=merge_col_names,
            select_col_names=select_col_names,
            sql_table_class=sql_table_class,
        )

    def write_time_product_data(
        self,
        time_product_feature_description_map: pl.DataFrame,
        time_product_feature_map: pl.DataFrame,
        product_ids: pl.DataFrame,
        company_id: int,
        *,
        check_passed: bool,
    ) -> bool:
        """Write time-product data into the database."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        # Get all dates from the database
        dates_df = get_all_dates(db)

        feature_type = "time_product"
        id_col_names = {"name": "product", "ID": "productID"}
        merge_col_names = ["product"]  # Match on product
        select_col_names = ["dateID", "productID", "featureID", "value"]  # Include dateID for time features
        sql_table_class = TimeProductFeatures

        return self._write_feature_data(
            feature_description_map=time_product_feature_description_map,
            feature_map=time_product_feature_map,
            ids=product_ids,
            company_id=company_id,
            feature_type=feature_type,
            id_col_names=id_col_names,
            merge_col_names=merge_col_names,
            select_col_names=select_col_names,
            sql_table_class=sql_table_class,
            dates_df=dates_df,
        )

    def write_time_store_data(
        self,
        time_store_feature_description_map: pl.DataFrame,
        time_store_feature_map: pl.DataFrame,
        store_ids: pl.DataFrame,
        company_id: int,
        *,
        check_passed: bool,
    ) -> bool:
        """Write time-store data into the database."""
        DataLoader.check_check_passed(check_passed=check_passed)

        db = SQLAlchemyDatabase.from_kedro()

        # Get all dates from the database
        dates_df = get_all_dates(db)

        feature_type = "time_store"
        id_col_names = {"name": "store", "ID": "storeID"}
        merge_col_names = ["store"]  # Match on store
        select_col_names = ["dateID", "storeID", "featureID", "value"]  # Include dateID for time features
        sql_table_class = TimeStoreFeatures

        return self._write_feature_data(
            feature_description_map=time_store_feature_description_map,
            feature_map=time_store_feature_map,
            ids=store_ids,
            company_id=company_id,
            feature_type=feature_type,
            id_col_names=id_col_names,
            merge_col_names=merge_col_names,
            select_col_names=select_col_names,
            sql_table_class=sql_table_class,
            dates_df=dates_df,
        )

    def write_time_region_data(
        self,
        time_region_feature_description_map: pl.DataFrame,
        time_region_feature_map: pl.DataFrame,
        company_id: int,
        *,
        check_passed: bool,
    ) -> bool:
        """Write time-region data into the database."""
        DataLoader.check_check_passed(check_passed=check_passed)

        if time_region_feature_description_map.is_empty():
            logger.info("No time-region feature data to write")
            return True

        db = SQLAlchemyDatabase.from_kedro()

        # Get all dates from the database
        dates_df = get_all_dates(db)

        # Get unique combinations of region, country, level to look up region IDs
        region_lookup = time_region_feature_map.select(["region", "country", "level"]).unique()

        with db.get_session(read_only=True) as session:
            # Query region IDs from database
            country_abbrevs = region_lookup.select("country").unique().to_series().to_list()
            country_query = (
                session.query(Regions.id, Regions.abbreviation)
                .filter(Regions.abbreviation.in_(country_abbrevs), Regions.type == "country")
                .all()
            )

            country_id_map = {abbrev: region_id for region_id, abbrev in country_query}

            # Build region lookup with country IDs
            region_lookup_with_country_ids = region_lookup.with_columns(
                pl.col("country").replace(country_id_map).alias("country_id").cast(pl.Int64)
            )

            # Query all region IDs in one batch
            region_conditions = [
                (Regions.abbreviation == row["region"])
                & (Regions.type == row["level"])
                & (Regions.country == row["country_id"])
                for row in region_lookup_with_country_ids.to_dicts()
            ]

            region_results = (
                session.query(Regions.id, Regions.abbreviation, Regions.type, Regions.country)
                .filter(or_(*region_conditions))
                .all()
            )

            # Build Polars DataFrame for region IDs
            region_ids = pl.DataFrame(
                [
                    {
                        "regionID": region_id,
                        "region": abbreviation,
                        "level": region_type,
                        "country_id": country_id,
                    }
                    for region_id, abbreviation, region_type, country_id in region_results
                ]
            )

        # Join with country lookup to get country names back
        region_ids = region_ids.join(
            region_lookup_with_country_ids, on=["region", "country_id", "level"], how="left"
        ).select(["regionID", "region", "country", "level"])

        feature_type = "time_region"
        id_col_names = {"regionID": "regionID"}  # Region IDs are already mapped
        merge_col_names = ["region", "country", "level"]  # Match on region, country, level
        select_col_names = ["dateID", "regionID", "featureID", "value"]  # Include dateID for time features
        sql_table_class = TimeRegionFeatures

        return self._write_feature_data(
            feature_description_map=time_region_feature_description_map,
            feature_map=time_region_feature_map,
            ids=region_ids,
            company_id=company_id,
            feature_type=feature_type,
            id_col_names=id_col_names,
            merge_col_names=merge_col_names,
            select_col_names=select_col_names,
            sql_table_class=sql_table_class,
            dates_df=dates_df,
        )
