import logging
import typing as t
from datetime import date
from types import TracebackType

import polars as pl
from sqlalchemy import select
from sqlalchemy.orm import aliased

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

from foundry_sdk.db_mgmt.sql_db_alchemy import SQLAlchemyDatabase
from foundry_sdk.db_mgmt.tables import Regions
from foundry_sdk.etl.constants import FREQUENCY_MAPPING, DatasetTypes, FlagLevels, VariableTypes
from foundry_sdk.etl.polars_tables import (
    ColumnSpec,
    SchemaSpec,
    categories_level_description_schema,
    description_map_schema,
    flags_schema,
    product_feature_data_schema,
    products_schema,
    sku_feature_data_schema,
    store_feature_data_schema,
    store_region_map_schema,
    time_product_feature_data_schema,
    time_region_feature_data_schema,
    time_sku_data_schema,
    time_store_feature_data_schema,
)
from foundry_sdk.etl.validation import category_validation

# Use the Kedro-aware logger from utils
logger = logging.getLogger(__name__)


########################################################################################################
###################################### New validation functions ########################################
########################################################################################################


class DataValidator:
    def __init__(self, db: SQLAlchemyDatabase) -> None:
        self.db = db
        self.session: Session | None = None
        self._session_context = None

    def __enter__(self) -> "DataValidator":
        self._session_context = self.db.get_session(read_only=True)
        self.session = self._session_context.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session_context:
            self._session_context.__exit__(exc_type, exc_value, traceback)
        self.session = None
        self._session_context = None

    def validate_schema(self, df: pl.DataFrame, schema: SchemaSpec, df_name: str = "dataframe") -> None:
        """
        Validate a Polars DataFrame against a defined schema.

        This method performs comprehensive validation including:
        1. No unexpected columns are present (only expected columns are allowed)
        2. All required (non-optional) columns are present in the DataFrame
        3. Exclusive optional groups are respected (only one column from each group)
        4. Each column's data type matches one of the allowed types defined in the schema
        5. Columns marked as non-nullable do not contain any null values
        6. Key columns (if specified) form a unique combination - no duplicates allowed

        Args:
            df: The Polars DataFrame to validate.
            schema: A SchemaSpec object defining expected columns, types, nullability, keys,
                   and exclusive optional groups.
            df_name: Optional name of the DataFrame for use in error messages.

        Raises:
            ValueError: If any required column is missing, if unexpected columns are present,
                       if exclusive optional groups are violated, if non-nullable columns
                       contain nulls, or if key constraints are violated.
            TypeError: If any column's data type does not match the allowed types in the schema.

        """
        if not isinstance(df, pl.DataFrame):
            msg = f"Expected a Polars DataFrame, got {type(df).__name__} for {df_name}"
            raise TypeError(msg)

        if df.is_empty():
            msg = f"{df_name} is empty. Validation will be skipped."
            logger.warning(msg)
            return

        expected = schema.column_names()
        unexpected = set(df.columns) - expected
        if unexpected:
            msg = f"{df_name}: Contains unexpected columns: {sorted(unexpected)}. Expected only: {sorted(expected)}"
            raise ValueError(msg)

        missing = set(schema.required_columns()) - set(df.columns)
        if missing:
            msg = f"{df_name}: Missing required columns: {sorted(missing)}"
            raise ValueError(msg)

        if schema.exclusive_optional_groups:
            for group in schema.exclusive_optional_groups:
                present = [col for col in group if col in df.columns]
                if len(present) > 1:
                    msg = f"{df_name}: Columns {present} are mutually exclusive. Only one of {group} may be present."
                    raise ValueError(msg)

        for spec in schema.columns:
            if spec.name not in df.columns:
                if spec.optional:
                    continue
                msg = f"{df_name}: Missing column '{spec.name}'"
                raise ValueError(msg)

            series = df[spec.name]
            self._validate_column_properties(series, spec, df_name)

        if schema.keys and df.select(schema.keys).unique(maintain_order=True).height != df.height:
            msg = f"{df_name}: Columns {schema.keys} must form a unique key — duplicates found."
            raise ValueError(msg)

    @staticmethod
    def _validate_column_properties(series: pl.Series, spec: ColumnSpec, df_name: str) -> None:
        """Validate individual column properties against its specification."""
        dtype = series.dtype

        if dtype not in spec.types:
            allowed = ", ".join(str(t) for t in spec.types)
            msg = f"{df_name}: Column '{spec.name}' has type {dtype}, expected one of: {allowed}"
            raise TypeError(msg)

        if not spec.nullable and series.null_count() > 0:
            msg = f"{df_name}: Column '{spec.name}' contains nulls but is not nullable"
            raise ValueError(msg)

        if spec.unique and series.n_unique() != series.len():
            # Find and show sample duplicate values
            df_with_column = pl.DataFrame({spec.name: series})
            duplicate_counts = df_with_column.group_by(spec.name).len().filter(pl.col("len") > 1).sort(spec.name)

            sample_duplicates = duplicate_counts.head(10)
            total_duplicate_values = duplicate_counts.height

            msg = (
                f"{df_name}: Column '{spec.name}' needs to have unique values but contains duplicates. "
                f"Found {total_duplicate_values} distinct values with duplicates.\n"
                f"Sample duplicate values:\n{sample_duplicates}"
            )
            raise ValueError(msg)

    @staticmethod
    def check_for_duplicate_combinations(
        df: pl.DataFrame,
        unique_cols: list[str],
        df_name: str = "DataFrame",
        sample_size: int = 10,
    ) -> None:
        """
        Check for duplicate combinations in the specified columns of a Polars DataFrame.

        Args:
            df: The Polars DataFrame to check
            unique_cols: List of column names that should form unique combinations
            df_name: Name of the DataFrame for error messages
            sample_size: Number of duplicate rows to show in the error message

        Raises:
            ValueError: If duplicate combinations are found

        """
        # Count occurrences of each key combination
        counts = df.select(unique_cols).group_by(unique_cols).len().filter(pl.col("len") > 1)

        if counts.is_empty():
            return  # No duplicates

        num_duplicates = counts["len"].sum()
        duplicates_df = df.join(counts.drop("len"), on=unique_cols).head(sample_size)

        combination_str = "-".join(unique_cols)
        msg = (
            f"Found {num_duplicates} duplicate {combination_str} combinations in {df_name}. "
            f"Each {combination_str} combination should have at most one entry.\n"
            f"Sample duplicate entries:\n{duplicates_df}"
        )
        raise ValueError(msg)

    def check_company_name(self, company_name: str) -> None:
        """
        Validate company name format.

        Requirements:
        - Must be all lowercase
        - No spaces allowed
        - Hyphens are allowed but discouraged (warning issued)
        """
        if not isinstance(company_name, str):
            msg = f"Company name must be a string. Got {type(company_name).__name__}: {company_name}"
            raise TypeError(msg)

        if not company_name:
            raise ValueError("Company name cannot be empty.")

        # Check for uppercase characters
        if not company_name.islower():
            raise ValueError("Company name must be all lowercase.")

        # Check for spaces
        if " " in company_name:
            raise ValueError("Company name cannot contain spaces. Use underscores instead.")

        # Check for hyphens and warn
        if "-" in company_name:
            logger.warning(
                "Company name '%s' contains hyphens. "
                "Consider using underscores instead of hyphens for better consistency, "
                "unless the first part encodes a set of company datasets",
                company_name,
            )
        logger.info("Check on company name '%s' passed.", company_name)

    def check_dataset_type(self, dataset_type: str, company_name: str) -> None:
        """
        Validate dataset type format and rules.

        Requirements:
        - Must be all lowercase
        - Must be one of the allowed types from DatasetTypes enum
        - If dataset_type is 'competition', company_name must contain at least one underscore
        """
        if not isinstance(dataset_type, str):
            msg = f"Dataset type must be a string. Got {type(dataset_type).__name__}: {dataset_type}"
            raise TypeError(msg)

        if not dataset_type:
            raise ValueError("Dataset type cannot be empty.")

        # Check for lowercase
        if not dataset_type.islower():
            raise ValueError("Dataset type must be all lowercase.")

        # Check if dataset type is allowed
        allowed_types = [dt.value for dt in DatasetTypes]
        if dataset_type not in allowed_types:
            msg = f"Dataset type '{dataset_type}' is not allowed. Allowed types are: {', '.join(allowed_types)}"
            raise ValueError(msg)

        # Special rule for competition datasets
        if dataset_type == DatasetTypes.COMPETITION.value and "_" not in company_name:
            msg = (
                f"For competition datasets, company name must contain at least one underscore. "
                f"The name should include the competition host or website name before '_'. "
                f"Got: '{company_name}'"
            )
            raise ValueError(msg)
        logger.info("Check on dataset type '%s' passed.", dataset_type)

    def check_date_range(self, min_date: date, max_date: date) -> None:
        """
        Validate date range.

        Requirements:
        - Both dates must be datetime or date objects
        - min_date must be before max_date
        - Dates should be reasonable (not too far in the past or future)
        - Warn if the date range is very large (> 10 years)
        """
        # Constants for date validation
        min_allowed_year = 1900
        max_allowed_year = 2100
        max_years_warning = 10

        if not isinstance(min_date, date):
            msg = f"min_date must be a date object. Got {type(min_date).__name__}: {min_date}"
            raise TypeError(msg)

        if not isinstance(max_date, date):
            msg = f"max_date must be a date object. Got {type(max_date).__name__}: {max_date}"
            raise TypeError(msg)

        # Check that min_date is before max_date
        if min_date >= max_date:
            msg = (
                f"min_date ({min_date}) must be before max_date ({max_date}). "
                f"Got a date range of {(max_date - min_date).days} days."
            )
            raise ValueError(msg)

        # Get year from either datetime or date objects
        min_year = min_date.year
        max_year = max_date.year

        # Check for reasonable date bounds
        if min_year < min_allowed_year:
            msg = f"min_date year ({min_year}) seems too early. Expected year >= {min_allowed_year}."
            raise ValueError(msg)

        if max_year > max_allowed_year:
            msg = f"max_date year ({max_year}) seems too far in the future. Expected year <= {max_allowed_year}."
            raise ValueError(msg)

        # Warn if date range is very large (more than 10 years)
        date_range_days = (max_date - min_date).days
        if date_range_days > max_years_warning * 365:  # approximately 10 years
            years = date_range_days / 365.25
            logger.warning(
                "Date range is very large: %.1f years (%d days). From %s to %s. Ensure this is on purpose.",
                years,
                date_range_days,
                min_date,
                max_date,
            )

        logger.info("Check on date range from %s to %s passed.", min_date, max_date)

    def check_frequency(self, frequency: int) -> None:
        """
        Validate frequency parameter.

        Args:
            frequency: The frequency integer to validate

        Raises:
            TypeError: If frequency is not an integer
            ValueError: If frequency is not in allowed values

        """
        if not isinstance(frequency, int):
            # Create a mapping for error message: {1: 'daily', 2: 'weekly', ...}
            value_to_name = {v: k for k, v in FREQUENCY_MAPPING.items()}
            allowed_values = list(FREQUENCY_MAPPING.values())
            allowed_mappings = [f"{v}={value_to_name[v]}" for v in allowed_values]
            msg = (
                f"frequency must be an integer, got {type(frequency).__name__}. "
                f"Allowed values: {', '.join(allowed_mappings)}"
            )
            raise TypeError(msg)

        allowed_values = list(FREQUENCY_MAPPING.values())
        if frequency not in allowed_values:
            # Create a mapping for error message: {1: 'daily', 2: 'weekly', ...}
            value_to_name = {v: k for k, v in FREQUENCY_MAPPING.items()}
            allowed_mappings = [f"{v}={value_to_name[v]}" for v in allowed_values]
            msg = f"frequency must be one of {allowed_values} ({', '.join(allowed_mappings)}), got {frequency}"
            raise ValueError(msg)

        logger.info("Check on frequency %d passed.", frequency)

    def check_store_region_map(self, store_region_map: pl.DataFrame) -> None:
        self.validate_schema(store_region_map, store_region_map_schema, "store_region_map")

        countries = store_region_map.select("country").unique().to_series().to_list()
        db_countries = (
            self.session.execute(select(Regions.abbreviation).where(Regions.type == "country")).scalars().all()
        )
        missing_countries = sorted(set(countries) - set(db_countries))
        if missing_countries:
            msg = f"Unknown countries in store_region_map: {missing_countries}. "
            raise ValueError(msg)

        region_df = store_region_map.select(["region", "level", "country"]).unique()
        region_values = region_df.rows()

        # First, get country IDs from country abbreviations in a single query
        country_abbrevs = region_df.select("country").unique().to_series().to_list()
        country_results = self.session.execute(
            select(Regions.id, Regions.abbreviation)
            .where(Regions.type == "country")
            .where(Regions.abbreviation.in_(country_abbrevs))
        ).all()
        country_id_mapping = {abbrev: country_id for country_id, abbrev in country_results}

        # Now query database regions with the actual country IDs
        db_regions = self.session.execute(select(Regions.abbreviation, Regions.type, Regions.country)).all()

        # Create sets for validation
        db_region_combinations = {(abbrev, type_, country_id) for abbrev, type_, country_id in db_regions}

        # Validate each (region, level, country) combination from the data
        invalid_combinations = []
        for region, level, country_abbrev in region_values:
            country_id = country_id_mapping.get(country_abbrev)
            if country_id is None:
                continue  # Country validation already handled above

            if (region, level, country_id) not in db_region_combinations:
                invalid_combinations.append((region, level, country_abbrev))

        messages = []
        if invalid_combinations:
            formatted = "\n".join(f"- {r} / {lvl} / {c}" for r, lvl, c in invalid_combinations)
            messages.append(f"Invalid (region, level, country) combinations not found in database:\n{formatted}")

        if messages:
            raise ValueError("\n\n".join(messages))

        logger.info("Check on store_region_map passed.")

    def check_products_and_categories(
        self, categories_dict: dict, categories_level_description: pl.DataFrame, products: pl.DataFrame
    ) -> None:
        self.validate_schema(
            categories_level_description, categories_level_description_schema, "categories_level_description"
        )
        self.validate_schema(products, products_schema, "products")
        self._check_categories_dict(categories_dict)
        self._validate_categories_dict_consistency(categories_dict, categories_level_description)
        self._validate_product_categories(categories_dict, products)

    def check_time_sku_data(self, time_sku_feature_description_map: pl.DataFrame, time_sku_data: pl.DataFrame) -> None:
        self._description_and_data_check(
            time_sku_feature_description_map,
            time_sku_data,
            description_map_schema,
            time_sku_data_schema,
            table_name="time_sku_data",
            check_sales=True,
        )

        # error if feature type categorical is in time_sku_feature_description_map
        categorical_features = time_sku_feature_description_map.filter(
            pl.col("var_type") == VariableTypes.CATEGORICAL.value
        )
        if not categorical_features.is_empty():
            msg = (
                "time_sku_feature_description_map contains categorical features. "
                "Categorical features should not be in time_sku_data, "
                "Convert them to binary features first."
            )
            raise ValueError(msg)

    def check_flags(self, flags: pl.DataFrame, time_sku_data: pl.DataFrame) -> None:
        if flags.is_empty():
            logger.info("Flags DataFrame is empty, skipping validation.")
            return
        self.validate_schema(flags, flags_schema, "flags")

        # Check that all flag values are valid according to FlagLevels enum using Polars native functions
        allowed_flags = [flag.value for flag in FlagLevels]
        invalid_flags_df = flags.select("flag").unique().filter(~pl.col("flag").is_in(allowed_flags))

        if not invalid_flags_df.is_empty():
            invalid_flags_list = invalid_flags_df["flag"].to_list()
            msg = f"Invalid flag values found: {sorted(invalid_flags_list)}. Allowed flag values: {allowed_flags}"
            raise ValueError(msg)

        sales_data = time_sku_data.filter(pl.col("feature") == "sales")
        self._check_missing_sales_are_null(flags, sales_data)
        self._check_all_missing_value_flags_exist(flags, sales_data)
        self._check_zero_value_flags_consistency(flags, sales_data)

        logger.info("Flags consistency check passed.")

    def check_store_feature_data(
        self, store_feature_description_map: pl.DataFrame, store_feature_map: pl.DataFrame
    ) -> None:
        self._description_and_data_check(
            store_feature_description_map,
            store_feature_map,
            description_map_schema,
            store_feature_data_schema,
            table_name="store_feature_data",
        )

    def check_product_feature_data(
        self, product_feature_description_map: pl.DataFrame, product_feature_map: pl.DataFrame
    ) -> None:
        self._description_and_data_check(
            product_feature_description_map,
            product_feature_map,
            description_map_schema,
            product_feature_data_schema,
            table_name="product_feature_data",
        )

    def check_sku_feature_data(self, sku_feature_description_map: pl.DataFrame, sku_feature_map: pl.DataFrame) -> None:
        self._description_and_data_check(
            sku_feature_description_map,
            sku_feature_map,
            description_map_schema,
            sku_feature_data_schema,
            table_name="sku_feature_data",
        )

    def check_time_product_feature_data(
        self, time_product_feature_description_map: pl.DataFrame, time_product_feature_map: pl.DataFrame
    ) -> None:
        self._description_and_data_check(
            time_product_feature_description_map,
            time_product_feature_map,
            description_map_schema,
            time_product_feature_data_schema,
            table_name="time_product_feature_data",
        )

    def check_time_region_feature_data(
        self, time_region_feature_description_map: pl.DataFrame, time_region_feature_map: pl.DataFrame
    ) -> None:
        self._description_and_data_check(
            time_region_feature_description_map,
            time_region_feature_map,
            description_map_schema,
            time_region_feature_data_schema,
            table_name="time_region_feature_data",
        )

        # Validate countries exist in database
        countries = time_region_feature_map.select("country").unique().to_series().to_list()
        db_countries = (
            self.session.execute(select(Regions.abbreviation).where(Regions.type == "country")).scalars().all()
        )
        missing_countries = sorted(set(countries) - set(db_countries))
        if missing_countries:
            msg = f"Unknown countries in time_region_feature_data: {missing_countries}."
            raise ValueError(msg)

        region_level_df = time_region_feature_map.select(["region", "level", "country"]).unique()
        region_level_values = region_level_df.rows()

        # Query database regions with this type (level), joining with countries to get abbreviations
        # We need to join Regions table with itself to get country abbreviations
        country_region = aliased(Regions)

        db_regions = self.session.execute(
            select(
                Regions.abbreviation.label("region_abbrev"),
                Regions.type.label("region_type"),
                country_region.abbreviation.label("country_abbrev"),
            )
            .join(country_region, Regions.country == country_region.id)
            .where(country_region.type == "country")
        ).all()

        # Create valid combinations: {(region_abbrev, region_type, country_abbrev)}
        db_valid_combinations = {(region, level, country) for region, level, country in db_regions}

        # Get all region abbreviations and levels from database
        db_region_abbrevs = {region for region, _, _ in db_regions}
        db_levels = {level for _, level, _ in db_regions}

        # Check for invalid regions
        region_values = region_level_df.select("region").unique().to_series().to_list()
        missing_regions = sorted(set(region_values) - db_region_abbrevs)

        # Check for invalid levels
        level_values = region_level_df.select("level").unique().to_series().to_list()
        missing_levels = sorted(set(level_values) - db_levels)

        # Check for invalid (region, level, country) combinations
        mismatched_combinations = [
            (region, level, country)
            for region, level, country in region_level_values
            if region in db_region_abbrevs
            and level in db_levels
            and (region, level, country) not in db_valid_combinations
        ]

        messages = []
        if missing_regions:
            messages.append(f"Invalid region values (not found in database): {missing_regions}")

        if missing_levels:
            messages.append(f"Invalid level values (not found in database): {missing_levels}")

        if mismatched_combinations:
            formatted = "\n".join(f"- {r} / {lvl} / {c}" for r, lvl, c in mismatched_combinations)
            messages.append(f"Invalid (region, level, country) combinations:\n{formatted}")

        if messages:
            raise ValueError("\n\n".join(messages))

        logger.info("Check on time_region_feature_data passed.")

    def check_time_store_feature_data(
        self, time_store_feature_description_map: pl.DataFrame, time_store_feature_map: pl.DataFrame
    ) -> None:
        self._description_and_data_check(
            time_store_feature_description_map,
            time_store_feature_map,
            description_map_schema,
            time_store_feature_data_schema,
            table_name="time_store_feature_data",
        )

    def check_feature_descriptions(
        self,
        time_sku_feature_description_map: pl.DataFrame,
        store_feature_description_map: pl.DataFrame,
        product_feature_description_map: pl.DataFrame,
        sku_feature_description_map: pl.DataFrame,
        time_product_feature_description_map: pl.DataFrame,
        time_region_feature_description_map: pl.DataFrame,
        time_store_feature_description_map: pl.DataFrame,
    ) -> None:
        """
        Check that feature names are unique across all feature description DataFrames.

        Raises:
            ValueError: If duplicate feature names are found across DataFrames

        """
        # Ensure all DataFrames have compatible schemas for concatenation
        # Cast levels column to consistent type (list[str]) for all DataFrames
        dataframes = []
        for df in [
            time_sku_feature_description_map,
            store_feature_description_map,
            product_feature_description_map,
            sku_feature_description_map,
            time_product_feature_description_map,
            time_region_feature_description_map,
            time_store_feature_description_map,
        ]:
            if df.is_empty():
                continue
            df_normalized = df.with_columns(pl.col("levels").cast(pl.List(pl.Utf8)))
            dataframes.append(df_normalized)

        all_descriptions = pl.concat(dataframes)

        duplicate_counts = all_descriptions.group_by("name").len().filter(pl.col("len") > 1)

        if not duplicate_counts.is_empty():
            duplicate_names = sorted(duplicate_counts["name"].to_list())
            msg = f"Duplicate feature names found across feature description DataFrames: {duplicate_names}"
            raise ValueError(msg)

        logger.info("Feature description uniqueness check passed.")

    @staticmethod
    def _check_categories_dict(categories_dict: dict) -> None:
        """
        Validate the categories dictionary structure and hierarchy.

        The categories are specified in a nested dictionary where:
        - Each first-level key represents a hierarchy level (0 being highest level)
        - Values contain dictionaries with category names as keys and parent lists as values
        - Level 0 categories must have None as parent value
        - Other levels must have lists of parent category names (even for single parent)

        Args:
            categories_dict: The categories dictionary to validate

        Raises:
            TypeError: If the structure doesn't match expected types
            ValueError: If validation rules are violated

        """
        category_validation.validate_basic_structure(categories_dict)
        levels, categories_by_level = category_validation.validate_levels_structure(categories_dict)
        all_categories = category_validation.validate_category_names(categories_dict, categories_by_level)
        multi_parent_categories = category_validation.validate_parent_child_relationships(
            categories_dict, categories_by_level
        )
        category_validation.check_circular_dependencies(categories_dict)
        category_validation.check_reachability(categories_dict, categories_by_level)
        category_validation.validate_dummy_category(all_categories)
        category_validation.log_warnings_and_success(multi_parent_categories, all_categories, len(categories_dict))

    def _validate_categories_dict_consistency(
        self, categories_dict: dict, categories_level_description: pl.DataFrame
    ) -> None:
        """
        Validate consistency between categories_dict and categories_level_description.

        Ensures that:
        1. All levels in categories_level_description exist in categories_dict
        2. All levels in categories_dict exist in categories_level_description

        Args:
            categories_dict: Dictionary with category hierarchy
            categories_level_description: DataFrame with level descriptions

        Raises:
            ValueError: If levels are inconsistent between the two structures

        """
        # Get levels from categories_dict
        dict_levels = set(categories_dict.keys())

        # Get levels from categories_level_description DataFrame
        df_levels = set(categories_level_description["level"].to_list())

        # Check for levels in DataFrame but not in dict
        missing_in_dict = df_levels - dict_levels
        if missing_in_dict:
            msg = (
                f"Levels found in categories_level_description but missing in categories_dict: "
                f"{sorted(missing_in_dict)}"
            )
            raise ValueError(msg)

        # Check for levels in dict but not in DataFrame
        missing_in_df = dict_levels - df_levels
        if missing_in_df:
            msg = (
                f"Levels found in categories_dict but missing in categories_level_description: {sorted(missing_in_df)}"
            )
            raise ValueError(msg)

        logger.info("Consistency check between categories_dict and categories_level_description passed.")

    def _validate_product_categories(self, categories_dict: dict, products: pl.DataFrame) -> None:
        """
        Validate that all categories in the products DataFrame exist in the categories dictionary.

        Args:
            categories_dict: Dictionary with category hierarchy
            products: DataFrame containing products with their assigned categories

        Raises:
            ValueError: If any category in products is not found in categories_dict

        """
        # Get all categories from the categories dictionary across all levels
        all_dict_categories = set()
        for level_categories in categories_dict.values():
            all_dict_categories.update(level_categories.keys())

        # Get all unique categories from the products DataFrame
        product_categories = set(products["category"].unique().to_list())

        # Find categories in products that are not in the categories dictionary
        missing_categories = product_categories - all_dict_categories

        if missing_categories:
            msg = f"Categories found in products but missing in categories_dict: {sorted(missing_categories)}"
            raise ValueError(msg)

        logger.info("Validation of product categories against categories_dict passed.")

    def _description_and_data_check(
        self,
        description: pl.DataFrame,
        data: pl.DataFrame,
        description_schema: SchemaSpec,
        data_schema: SchemaSpec,
        *,
        table_name: str = "feature_data",
        check_sales: bool = False,
    ) -> None:
        """
        Helper function to validate feature description and data consistency.

        Args:
            description: DataFrame with feature descriptions (name, description, var_type, levels)
            data: DataFrame with actual feature data
            description_schema: Schema specification for the description DataFrame
            data_schema: Schema specification for the data DataFrame
            table_name: Name of the table/dataset for error messages
            check_sales: Whether to require 'sales' feature in the description

        Raises:
            ValueError: If validation fails

        """
        # Validate schemas
        if description.is_empty() and data.is_empty():
            msg = f"{table_name} is empty. Validation will be skipped."
            logger.warning(msg)
            return
        self.validate_schema(description, description_schema, f"{table_name}_description")
        self.validate_schema(data, data_schema, table_name)

        # Validate var_type values
        allowed_var_types = [vt.value for vt in VariableTypes]
        invalid_var_types = set(description["var_type"].unique().to_list()) - set(allowed_var_types)
        if invalid_var_types:
            msg = (
                f"Invalid var_type values in description: {sorted(invalid_var_types)}. "
                f"Allowed values: {allowed_var_types}"
            )
            raise ValueError(msg)

        # Check if sales feature is required and present
        if check_sales:
            has_sales = description.filter(pl.col("name") == "sales").height > 0
            if not has_sales:
                raise ValueError("Feature 'sales' is required but not found in description")

        # Validate categorical features have non-null levels
        categorical_features = description.filter(pl.col("var_type") == VariableTypes.CATEGORICAL.value)
        null_levels = categorical_features.filter(pl.col("levels").is_null())
        if not null_levels.is_empty():
            invalid_features = null_levels["name"].to_list()
            msg = f"Categorical features must have non-null levels: {invalid_features}"
            raise ValueError(msg)

        text_features = description.filter(pl.col("var_type") == VariableTypes.TEXT.value)

        # Determine required value column type based on categorical features
        has_categorical = not categorical_features.is_empty()
        has_text = not text_features.is_empty()
        expected_value_type = pl.Utf8 if has_categorical or has_text else pl.Float64

        # Validate value column type
        actual_value_type = data["value"].dtype
        if actual_value_type != expected_value_type:
            msg = (
                f"Value column has type {actual_value_type}, expected {expected_value_type}. "
                f"{'Categorical features present - all values must be strings' if has_categorical else 'No categorical features - values must be numeric'}"
            )
            raise ValueError(msg)

        # Check that all features in data exist in description
        missing_features = (
            data.select("feature")
            .unique()
            .join(description.select("name"), left_on="feature", right_on="name", how="anti")
        )
        if not missing_features.is_empty():
            missing_list = sorted(missing_features["feature"].to_list())
            msg = f"Features in data not found in description: {missing_list}"
            raise ValueError(msg)

        # Validate categorical feature values against levels
        self._validate_categorical_feature_values(description, data)

        # Validate binary feature values
        self._validate_binary_feature_values(description, data)

        # Validate continuous feature values
        self._validate_continuous_feature_values(description, data)

        # Validate text feature values
        self._validate_text_feature_values(description, data)

        # Validate date range if data has date column
        if "date" in data.columns:
            dates = data["date"].unique().sort()
            min_date = dates.min()
            max_date = dates.max()
            self.check_date_range(min_date, max_date)

        logger.info("Feature description and data validation passed.")

    def _validate_categorical_feature_values(self, description: pl.DataFrame, data: pl.DataFrame) -> None:
        """Validate that categorical feature values match their defined levels."""
        # Get categorical features from description
        categorical_features = description.filter(pl.col("var_type") == VariableTypes.CATEGORICAL.value).select(
            ["name", "var_type", "levels"]
        )

        if categorical_features.is_empty():
            return  # No categorical features to validate
        
        # Create allowed values DataFrame
        levels_df = (
            categorical_features
            .select("name", "levels")
            .explode("levels")
            .rename({"name": "feature", "levels": "allowed_value"})
        )

        # Get only categorical feature data by joining with categorical_features
        categorical_data = data.join(
            categorical_features.select("name"), 
            left_on="feature", 
            right_on="name", 
            how="inner"
        ).filter(pl.col("value").is_not_null())

        if categorical_data.is_empty():
            return

        # Find invalid values using left join and check for nulls
        invalid_data = (
            categorical_data
            .join(levels_df, left_on=["feature", "value"], right_on=["feature", "allowed_value"], how="left")
            .filter(pl.col("feature").is_null())  # Invalid values will have null allowed_value
        )

        if not invalid_data.is_empty():
            # Join back with categorical_features to get the levels for error message
            invalid_summary = (
                invalid_data
                .join(categorical_features.select(["name", "levels"]), left_on="feature", right_on="name")
                .group_by(["feature", "levels"])
                .agg(pl.col("value").unique().head(10).alias("invalid_values"))
                .sort("feature")
            )

            error_details = []
            for row in invalid_summary.rows(named=True):
                feature_name = row["feature"]
                allowed_levels = row["levels"]
                invalid_values = row["invalid_values"]
                # Truncate long level lists for readability
                levels_display = allowed_levels[:10] if len(allowed_levels) > 10 else allowed_levels
                levels_suffix = "..." if len(allowed_levels) > 10 else ""
                error_details.append(
                    f"  - {feature_name}: invalid values {invalid_values}, allowed: {levels_display}{levels_suffix} (plus null)"
                )

            msg = "Categorical features have invalid values:\n" + "\n".join(error_details)
            raise ValueError(msg)
    
    def _validate_text_feature_values(self, description: pl.DataFrame, data: pl.DataFrame) -> None:
        """Validate that text feature values are strings or null."""

        if description.filter(pl.col("var_type") == VariableTypes.TEXT.value).is_empty():
            return  # No text features to validate

        # If text features present, the entire value columns must be String
        if data.select(pl.col("value")).dtypes[0] != pl.Utf8:
            raise TypeError("Text feature values must be of type Utf8")
            


    def _validate_binary_feature_values(self, description: pl.DataFrame, data: pl.DataFrame) -> None:
        """Validate that binary feature values are only 0 or 1."""
        # Get binary features from description
        binary_features = description.filter(pl.col("var_type") == VariableTypes.BINARY.value).select(
            ["name", "var_type"]
        )

        if binary_features.is_empty():
            return  # No binary features to validate

        # Join data with binary features to get only binary feature data
        invalid_data = (
            data.join(binary_features, left_on="feature", right_on="name", how="inner")
            .filter(pl.col("var_type") == VariableTypes.BINARY.value)
            .with_columns(value=pl.col("value").cast(pl.Float64, strict=True))
            .filter(pl.col("value").is_not_null() & ~pl.col("value").is_in([0.0, 1.0]))
        )

        if not invalid_data.is_empty():
            # Get sample of invalid values per feature for error message (limit to 10)
            invalid_summary = (
                invalid_data.group_by("feature")
                .agg(pl.col("value").unique().head(10).alias("invalid_values"))
                .sort("feature")
            )

            error_details = []
            for row in invalid_summary.rows(named=True):
                feature_name = row["feature"]
                invalid_values = row["invalid_values"]
                error_details.append(f"  - {feature_name}: {invalid_values}")

            msg = "Binary features have invalid values (expected only 0, 1, or null for missing values):\n" + "\n".join(
                error_details
            )
            raise ValueError(msg)

    def _validate_continuous_feature_values(self, description: pl.DataFrame, data: pl.DataFrame) -> None:
        """Validate that continuous feature values are finite numeric values or null."""
        # Single chain: filter continuous features, join with data, validate, and collect errors
        invalid_summary = (
            description.filter(pl.col("var_type") == VariableTypes.CONTINUOUS.value)
            .select(["name", "var_type"])
            .join(data, left_on="name", right_on="feature", how="inner")
            .with_columns(
                numeric_value=pl.col("value").cast(pl.Float64, strict=False),
                was_not_null=pl.col("value").is_not_null(),
            )
            .filter(
                pl.col("was_not_null")
                & (
                    pl.col("numeric_value").is_null()  # Failed conversion
                    | pl.col("numeric_value").is_nan()  # NaN values
                    | pl.col("numeric_value").is_infinite()  # Infinite values
                )
            )
            .group_by("name")
            .agg(pl.col("value").unique().head(10).alias("invalid_values"))
            .sort("name")
        )

        if not invalid_summary.is_empty():
            error_details = []
            for row in invalid_summary.rows(named=True):
                feature_name = row["name"]
                invalid_values = row["invalid_values"]
                error_details.append(f"  - {feature_name}: {invalid_values}")

            msg = "Continuous features have non-finite values (expected finite numeric values or null):\n" + "\n".join(
                error_details
            )
            raise ValueError(msg)

    @staticmethod
    def _check_missing_sales_are_null(flags: pl.DataFrame, sales_data: pl.DataFrame) -> None:
        sales_on_missing_value = (
            flags.filter(pl.col("flag") == FlagLevels.MISSING_VALUE.value)
            .select(["date", "product", "store"])
            .join(
                sales_data.select(["date", "product", "store", "value"]),
                on=["date", "product", "store"],
                how="left",
            )
            .filter(pl.col("value").is_not_null())
        )
        if not sales_on_missing_value.is_empty():
            sample_invalid = sales_on_missing_value.head(10)
            msg = (
                f"Found {sales_on_missing_value.height} missing_value flags where sales data is not null/missing. "
                f"missing_value flags should only exist where sales data is null or missing.\n"
                f"Sample invalid cases:\n{sample_invalid}"
            )
            raise ValueError(msg)

    @staticmethod
    def _check_all_missing_value_flags_exist(flags: pl.DataFrame, sales_data: pl.DataFrame) -> None:
        missing_sales_without_flags = (
            sales_data.filter(pl.col("value").is_null())
            .select(["date", "product", "store"])
            .join(
                flags.filter(pl.col("flag") == FlagLevels.MISSING_VALUE.value).select(["date", "product", "store"]),
                on=["date", "product", "store"],
                how="anti",  # Get sales records without corresponding flags
            )
        )
        if not missing_sales_without_flags.is_empty():
            sample_missing = missing_sales_without_flags.head(10)
            msg = (
                f"Found {missing_sales_without_flags.height} sales records with null/empty values that lack missing_value flags. "
                f"All null/empty sales values should have corresponding missing_value flags.\n"
                f"Sample missing flags:\n{sample_missing}"
            )
            raise ValueError(msg)

    @staticmethod
    def _check_zero_value_flags_consistency(flags: pl.DataFrame, sales_data: pl.DataFrame) -> None:
        flag_sales_validation = (
            flags.filter(pl.col("flag").is_in([FlagLevels.NOT_FOR_SALE.value, FlagLevels.OUT_OF_STOCK.value]))
            .join(
                sales_data.select(["date", "product", "store", "value"]),
                on=["date", "product", "store"],
                how="left",  # Keep all flags, even if no sales data
            )
            .with_columns(
                sales_missing=pl.col("value").is_null(),
                sales_not_zero=(pl.col("value").is_not_null() & (pl.col("value").cast(pl.Float64, strict=True) != 0.0)),
            )
        )

        # Find all validation failures in one pass
        validation_failures = flag_sales_validation.filter(pl.col("sales_missing") | pl.col("sales_not_zero"))

        if not validation_failures.is_empty():
            # Separate different types of failures for detailed error messages
            missing_sales = validation_failures.filter(pl.col("sales_missing"))
            non_zero_sales = validation_failures.filter(pl.col("sales_not_zero"))

            error_messages = []

            if not missing_sales.is_empty():
                sample_missing = missing_sales.select(["date", "product", "store", "flag"]).head(10)
                error_messages.append(
                    f"Found {missing_sales.height} not_for_sale/out_of_stock flags without corresponding sales data entries. "
                    f"These flags require sales data entries.\n"
                    f"Sample missing cases:\n{sample_missing}"
                )

            if not non_zero_sales.is_empty():
                sample_non_zero = non_zero_sales.select(["date", "product", "store", "flag", "value"]).head(10)
                error_messages.append(
                    f"Found {non_zero_sales.height} not_for_sale/out_of_stock flags where sales value is not 0. "
                    f"These flags should only exist where sales value is 0.\n"
                    f"Sample invalid cases:\n{sample_non_zero}"
                )

            raise ValueError("\n\n".join(error_messages))
