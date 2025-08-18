import typing as t
from datetime import datetime

from sqlalchemy import (
    REAL,
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

#######################################################################################
############################# Data Tables SQLAlchemy ##################################
#######################################################################################

# SQLAlchemy Base
Base = declarative_base()


class Companies(Base):
    __tablename__ = "companies"

    id = Column("ID", Integer, Identity(always=True), primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, unique=True)
    frequency = Column(Integer, nullable=False)

    # Columns re-added to match existing DB schema
    dataset_type = Column(Text, nullable=False)
    min_date = Column(Date, nullable=False)
    max_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    stores = relationship("Stores", back_populates="company")
    products = relationship("Products", back_populates="company")
    categories = relationship("Categories", back_populates="company")
    category_level_descriptions = relationship("CategoryLevelDescriptions", back_populates="company")
    feature_descriptions = relationship("FeatureDescriptions", back_populates="company")

    __unique_keys__: t.ClassVar[list[str]] = ["name"]


class Dates(Base):
    __tablename__ = "dates"

    id = Column("ID", Integer, Identity(always=True), primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True)

    # Relationships
    datapoints = relationship("Datapoints", back_populates="date")
    time_product_features = relationship("TimeProductFeatures", back_populates="date")
    time_region_features = relationship("TimeRegionFeatures", back_populates="date")
    time_store_features = relationship("TimeStoreFeatures", back_populates="date")

    __unique_keys__: t.ClassVar[list[str]] = ["date"]


class Regions(Base):
    __tablename__ = "regions"

    id = Column("ID", Integer, Identity(always=True), primary_key=True, autoincrement=True)
    abbreviation = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    country = Column(Integer, nullable=False)

    # Columns re-added to match existing DB schema
    name = Column(Text, nullable=False)
    parent_region_id = Column(
        "parent_regionID",
        Integer,
        ForeignKey("regions.ID", name="link_to_parent_regions", onupdate="RESTRICT", ondelete="CASCADE"),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("abbreviation", "type", "country"),
        Index("unique_region_index", "parent_regionID", "name", "abbreviation", "type", unique=True),
        Index("unique_top_level_regions", "name", "abbreviation", "type", unique=True),
    )

    # Relationships
    stores = relationship("Stores", secondary="stores_regions", back_populates="regions")
    time_region_features = relationship("TimeRegionFeatures", back_populates="region")

    __unique_keys__: t.ClassVar[list[str]] = ["abbreviation", "type", "country"]


class Stores(Base):
    __tablename__ = "stores"

    id = Column("ID", Integer, Identity(always=True), primary_key=True, autoincrement=True)
    company_id = Column(
        "companyID",
        Integer,
        ForeignKey("companies.ID", name="link_to_companies", onupdate="RESTRICT", ondelete="CASCADE"),
        nullable=False,
    )
    region_id = Column(
        "regionID",
        Integer,
        ForeignKey("regions.ID", name="link_to_regions", onupdate="RESTRICT", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(Text, nullable=False)

    __table_args__ = (UniqueConstraint("companyID", "name"),)

    # Relationships
    company = relationship("Companies", back_populates="stores")
    regions = relationship("Regions", secondary="stores_regions", back_populates="stores")
    sku_table = relationship("SkuTable", back_populates="store")
    store_features = relationship("StoreFeatures", back_populates="store")
    time_store_features = relationship("TimeStoreFeatures", back_populates="store")

    __unique_keys__: t.ClassVar[list[str]] = ["companyID", "name"]


# REMOVE IN FUTURE VERSIONS, PART OF STORES NOW
class StoresRegions(Base):
    __tablename__ = "stores_regions"

    store_id = Column(
        "storeID",
        Integer,
        ForeignKey("stores.ID", name="link_to_stores", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    region_id = Column(
        "regionID",
        Integer,
        ForeignKey("regions.ID", name="link_to_regions", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )


class Categories(Base):
    __tablename__ = "categories"

    id = Column("ID", Integer, Identity(always=True), primary_key=True, autoincrement=True)

    company_id = Column(
        "companyID",
        Integer,
        ForeignKey(
            "companies.ID",
            name="company_link",  # match DB constraint name
            onupdate="RESTRICT",  # match DB onupdate
            ondelete="CASCADE",  # match DB ondelete
        ),
        nullable=False,
    )

    name = Column(Text)

    __table_args__ = (
        UniqueConstraint("companyID", "name"),
        Index("idx_categoryid_categories", "ID"),
    )

    # Relationships
    company = relationship("Companies", back_populates="categories")
    product_categories = relationship("ProductCategories", back_populates="category")
    parent_relations = relationship(
        "CategoryRelations", foreign_keys="CategoryRelations.parent_id", back_populates="parent"
    )
    sub_relations = relationship("CategoryRelations", foreign_keys="CategoryRelations.sub_id", back_populates="sub")

    __unique_keys__: t.ClassVar[list[str]] = ["companyID", "name"]


class CategoryLevelDescriptions(Base):
    __tablename__ = "category_level_descriptions"

    id = Column("ID", Integer, Identity(always=True), primary_key=True, autoincrement=True)
    level = Column(Integer, nullable=False)
    name = Column(Text, nullable=False)
    company_id = Column(
        "companyID",
        Integer,
        ForeignKey(
            "companies.ID",
            name="link_to_company",  # match the DB constraint name
            onupdate="RESTRICT",  # match ON UPDATE behavior
            ondelete="CASCADE",  # match ON DELETE behavior
        ),
        nullable=True,
    )

    __table_args__ = (UniqueConstraint("level", "name", "companyID"),)

    # Relationships
    company = relationship("Companies", back_populates="category_level_descriptions")

    __unique_keys__: t.ClassVar[list[str]] = ["level", "name", "companyID"]


class CategoryRelations(Base):
    __tablename__ = "category_relations"

    sub_id = Column(
        "subID",
        Integer,
        ForeignKey("categories.ID", name="link_to_categories", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )

    parent_id = Column(
        "parentID",
        Integer,
        ForeignKey("categories.ID", name="link_to_categories_parent", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )

    __table_args__ = (UniqueConstraint("subID", "parentID"),)

    # Relationships
    sub = relationship("Categories", foreign_keys=[sub_id], back_populates="sub_relations")
    parent = relationship("Categories", foreign_keys=[parent_id], back_populates="parent_relations")

    __unique_keys__: t.ClassVar[list[str]] = ["subID", "parentID"]


class Products(Base):
    __tablename__ = "products"

    id = Column("ID", Integer, Identity(always=True), primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    company_id = Column(
        "companyID",
        Integer,
        ForeignKey("companies.ID", name="link_to_companies", onupdate="RESTRICT", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (UniqueConstraint("name", "companyID"),)

    # Relationships
    company = relationship("Companies", back_populates="products")
    product_categories = relationship("ProductCategories", back_populates="product")
    sku_table = relationship("SkuTable", back_populates="product")
    product_features = relationship("ProductFeatures", back_populates="product")
    time_product_features = relationship("TimeProductFeatures", back_populates="product")

    __unique_keys__: t.ClassVar[list[str]] = ["name", "companyID"]


class ProductCategories(Base):
    __tablename__ = "product_categories"

    product_id = Column(
        "productID",
        Integer,
        ForeignKey("products.ID", name="link_to_products", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    category_id = Column(
        "categoryID",
        Integer,
        ForeignKey("categories.ID", name="link_to_categories", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )

    __table_args__ = (Index("idx_productid_product_categories", "productID"),)

    # Relationships
    product = relationship("Products", back_populates="product_categories")
    category = relationship("Categories", back_populates="product_categories")

    __unique_keys__: t.ClassVar[list[str]] = ["productID", "categoryID"]


class SkuTable(Base):
    __tablename__ = "sku_table"

    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    product_id = Column(
        "productID",
        Integer,
        ForeignKey("products.ID", name="link_to_products", onupdate="RESTRICT", ondelete="CASCADE"),
        nullable=False,
    )
    store_id = Column(
        "storeID",
        Integer,
        ForeignKey("stores.ID", name="link_to_stores", onupdate="RESTRICT", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("productID", "storeID"),
        Index("idx_sku_table_id", "ID"),
        Index("idx_skuid_sku_table", "ID"),
    )

    # Relationships
    product = relationship("Products", back_populates="sku_table")
    store = relationship("Stores", back_populates="sku_table")
    datapoints = relationship("Datapoints", back_populates="sku")
    sku_features = relationship("SkuFeatures", back_populates="sku")

    __unique_keys__: t.ClassVar[list[str]] = ["productID", "storeID"]


class Datapoints(Base):
    __tablename__ = "datapoints"

    id = Column("ID", Integer, Identity(always=True), primary_key=True, autoincrement=True)
    sku_id = Column(
        "skuID",
        Integer,
        ForeignKey("sku_table.ID", name="datapoints_SKU_ID_fkey", onupdate="RESTRICT", ondelete="CASCADE"),
        nullable=False,
    )

    date_id = Column(
        "dateID",
        Integer,
        ForeignKey("dates.ID", name="datapoints_dateID_fkey", onupdate="RESTRICT", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("skuID", "dateID"),
        Index("idx_datapoints_skuid_dateid", "skuID", "dateID"),
        Index("idx_skuid_datapoints", "skuID"),
    )

    # Relationships
    sku = relationship("SkuTable", back_populates="datapoints")
    date = relationship("Dates", back_populates="datapoints")
    flags = relationship("Flags", back_populates="datapoint")
    time_sku_features = relationship("TimeSkuFeatures", back_populates="datapoint")
    predictions = relationship("Predictions", back_populates="datapoint")

    __unique_keys__: t.ClassVar[list[str]] = ["skuID", "dateID"]


class FeatureDescriptions(Base):
    __tablename__ = "feature_descriptions"

    id = Column("ID", Integer, Identity(always=True), primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    var_type = Column(Text, nullable=False)
    feature_type = Column(Text, nullable=False)
    company_id = Column(
        "companyID",
        Integer,
        ForeignKey("companies.ID", name="link_to_companies", onupdate="RESTRICT", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (UniqueConstraint("name", "companyID"),)

    # Relationships
    company = relationship("Companies", back_populates="feature_descriptions")
    feature_levels = relationship("FeatureLevels", back_populates="feature")
    store_features = relationship("StoreFeatures", back_populates="feature")
    product_features = relationship("ProductFeatures", back_populates="feature")
    sku_features = relationship("SkuFeatures", back_populates="feature")
    time_product_features = relationship("TimeProductFeatures", back_populates="feature")
    time_region_features = relationship("TimeRegionFeatures", back_populates="feature")
    time_store_features = relationship("TimeStoreFeatures", back_populates="feature")
    time_sku_features = relationship("TimeSkuFeatures", back_populates="feature")

    __unique_keys__: t.ClassVar[list[str]] = ["name", "companyID"]


class FeatureLevels(Base):
    __tablename__ = "feature_levels"

    feature_id = Column(
        "featureID",
        Integer,
        ForeignKey(
            "feature_descriptions.ID", name="link_to_feature_descriptions", onupdate="RESTRICT", ondelete="CASCADE"
        ),
        primary_key=True,
    )
    level = Column(Text, primary_key=True)
    order = Column(Text, nullable=False)

    __table_args__ = (UniqueConstraint("order", "featureID"),)

    # Relationships
    feature = relationship("FeatureDescriptions", back_populates="feature_levels")

    __unique_keys__: t.ClassVar[list[str]] = ["featureID", "level"]


class Flags(Base):
    __tablename__ = "flags"

    name = Column(Text, primary_key=True)
    datapoint_id = Column(
        "datapointID",
        Integer,
        ForeignKey("datapoints.ID", name="link_to_datapoints", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )

    __table_args__ = (
        Index("idx_datapointid_flags", "datapointID"),
        Index("idx_flags_datapointID", "datapointID"),
        Index("idx_flags_not_for_sale", "datapointID"),
    )

    # Relationships
    datapoint = relationship("Datapoints", back_populates="flags")

    __unique_keys__: t.ClassVar[list[str]] = ["name", "datapointID"]


class StoreFeatures(Base):
    __tablename__ = "store_features"

    store_id = Column(
        "storeID",
        Integer,
        ForeignKey("stores.ID", name="link_to_stores", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    feature_id = Column(
        "featureID",
        Integer,
        ForeignKey(
            "feature_descriptions.ID", name="link_to_feature_descriptions", onupdate="RESTRICT", ondelete="CASCADE"
        ),
        primary_key=True,
    )
    value = Column(Text)

    # Relationships
    store = relationship("Stores", back_populates="store_features")
    feature = relationship("FeatureDescriptions", back_populates="store_features")

    __unique_keys__: t.ClassVar[list[str]] = ["storeID", "featureID"]


class ProductFeatures(Base):
    __tablename__ = "product_features"

    product_id = Column(
        "productID",
        Integer,
        ForeignKey("products.ID", name="link_to_products", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    feature_id = Column(
        "featureID",
        Integer,
        ForeignKey(
            "feature_descriptions.ID", name="link_to_feature_descriptions", onupdate="RESTRICT", ondelete="CASCADE"
        ),
        primary_key=True,
    )
    value = Column(Text)

    # Relationships
    product = relationship("Products", back_populates="product_features")
    feature = relationship("FeatureDescriptions", back_populates="product_features")

    __unique_keys__: t.ClassVar[list[str]] = ["productID", "featureID"]


class SkuFeatures(Base):
    __tablename__ = "sku_features"

    sku_id = Column(
        "skuID",
        Integer,
        ForeignKey("sku_table.ID", name="link_to_sku_table", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    feature_id = Column(
        "featureID",
        Integer,
        ForeignKey(
            "feature_descriptions.ID", name="link_to_feature_descriptions", onupdate="RESTRICT", ondelete="CASCADE"
        ),
        primary_key=True,
    )
    value = Column(Text)

    # Relationships
    sku = relationship("SkuTable", back_populates="sku_features")
    feature = relationship("FeatureDescriptions", back_populates="sku_features")

    __unique_keys__: t.ClassVar[list[str]] = ["skuID", "featureID"]


class TimeProductFeatures(Base):
    __tablename__ = "time_product_features"

    date_id = Column(
        "dateID",
        Integer,
        ForeignKey("dates.ID", name="link_to_dates", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    product_id = Column(
        "productID",
        Integer,
        ForeignKey("products.ID", name="link_to_products", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    feature_id = Column(
        "featureID",
        Integer,
        ForeignKey(
            "feature_descriptions.ID", name="link_to_feature_descriptions", onupdate="RESTRICT", ondelete="CASCADE"
        ),
        primary_key=True,
    )
    value = Column(Text)

    # Relationships
    date = relationship("Dates", back_populates="time_product_features")
    product = relationship("Products", back_populates="time_product_features")
    feature = relationship("FeatureDescriptions", back_populates="time_product_features")

    __unique_keys__: t.ClassVar[list[str]] = ["dateID", "productID", "featureID"]


class TimeRegionFeatures(Base):
    __tablename__ = "time_region_features"

    date_id = Column(
        "dateID",
        Integer,
        ForeignKey("dates.ID", name="link_to_dates", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    region_id = Column(
        "regionID",
        Integer,
        ForeignKey("regions.ID", name="link_to_regions", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    feature_id = Column(
        "featureID",
        Integer,
        ForeignKey(
            "feature_descriptions.ID", name="link_to_feature_descriptions", onupdate="RESTRICT", ondelete="CASCADE"
        ),
        primary_key=True,
    )
    value = Column(Text)

    # Relationships
    date = relationship("Dates", back_populates="time_region_features")
    region = relationship("Regions", back_populates="time_region_features")
    feature = relationship("FeatureDescriptions", back_populates="time_region_features")

    __unique_keys__: t.ClassVar[list[str]] = ["dateID", "regionID", "featureID"]


class TimeStoreFeatures(Base):
    __tablename__ = "time_store_features"

    date_id = Column(
        "dateID",
        Integer,
        ForeignKey("dates.ID", name="link_to_dates", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    store_id = Column(
        "storeID",
        Integer,
        ForeignKey("stores.ID", name="link_to_stores", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    feature_id = Column(
        "featureID",
        Integer,
        ForeignKey(
            "feature_descriptions.ID", name="link_to_feature_descriptions", onupdate="RESTRICT", ondelete="CASCADE"
        ),
        primary_key=True,
    )
    value = Column(Text)

    # Relationships
    date = relationship("Dates", back_populates="time_store_features")
    store = relationship("Stores", back_populates="time_store_features")
    feature = relationship("FeatureDescriptions", back_populates="time_store_features")

    __unique_keys__: t.ClassVar[list[str]] = ["dateID", "storeID", "featureID"]


class TimeSkuFeatures(Base):
    __tablename__ = "time_sku_features"

    datapoint_id = Column(
        "datapointID",
        BigInteger,
        ForeignKey("datapoints.ID", name="link_to_datapoints", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    feature_id = Column(
        "featureID",
        Integer,
        ForeignKey(
            "feature_descriptions.ID", name="link_to_feature_descriptions", onupdate="RESTRICT", ondelete="CASCADE"
        ),
        primary_key=True,
    )
    value = Column(Numeric)

    # Relationships
    datapoint = relationship("Datapoints", back_populates="time_sku_features")
    feature = relationship("FeatureDescriptions", back_populates="time_sku_features")

    __unique_keys__: t.ClassVar[list[str]] = ["datapointID", "featureID"]


class Datasets(Base):
    __tablename__ = "datasets"

    id = Column("ID", Integer, Identity(always=True), primary_key=True, autoincrement=True)
    type = Column(Text, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    name = Column(Text, nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("type = ANY (ARRAY['train'::text, 'test'::text])"),
        Index("idx_datasets_name_unique", "name", unique=True),
    )

    # Relationships
    dataset_matching = relationship("DatasetMatching", back_populates="dataset")
    dataset_matching_test = relationship("DatasetMatchingTest", back_populates="dataset")
    train_test_mapping = relationship("TrainTestMapping", back_populates="dataset")

    __unique_keys__: t.ClassVar[list[str]] = ["name"]


class DatasetMatching(Base):
    __tablename__ = "dataset_matching"

    dataset_id = Column(
        "datasetID",
        Integer,
        ForeignKey("datasets.ID", name="dataset_matching_datasetID_fkey", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )

    sku_id = Column(
        "skuID",
        Integer,
        ForeignKey("sku_table.ID", name="dataset_matching_SKU_ID_fkey", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )

    __table_args__ = (
        UniqueConstraint("datasetID", "skuID"),
        Index("idx_skuid_dataset_matching", "skuID"),
    )

    # Relationships
    dataset = relationship("Datasets", back_populates="dataset_matching")
    sku = relationship("SkuTable")

    __unique_keys__: t.ClassVar[list[str]] = ["datasetID", "skuID"]


class DatasetMatchingTest(Base):
    __tablename__ = "dataset_matching_test"

    dataset_id = Column(
        "datasetID",
        Integer,
        ForeignKey("datasets.ID", name="link_to_datasets", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    sku_id = Column(
        "skuID",
        Integer,
        ForeignKey("sku_table.ID", name="link_to_sku_table", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    subtype = Column(String(50))

    __table_args__ = (UniqueConstraint("datasetID", "skuID"),)

    # Relationships
    dataset = relationship("Datasets", back_populates="dataset_matching_test")
    sku = relationship("SkuTable")

    __unique_keys__: t.ClassVar[list[str]] = ["datasetID", "skuID"]


class TrainGroups(Base):
    __tablename__ = "train_groups"

    id = Column("ID", Integer, Identity(always=True), primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    restriction_file_path = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    restrictions_json = Column(JSONB, nullable=False)

    # Relationships
    train_test_mapping = relationship("TrainTestMapping", back_populates="train_group")
    train_group_entities = relationship("TrainGroupEntities", back_populates="train_group")

    __unique_keys__: t.ClassVar[list[str]] = ["name"]


class TrainGroupEntities(Base):
    __tablename__ = "train_group_entities"

    id = Column("ID", Integer, Identity(always=True), primary_key=True, autoincrement=True)
    train_group_id = Column(
        "train_groupID",
        Integer,
        ForeignKey("train_groups.ID", name="link_to_train_groups", onupdate="RESTRICT", ondelete="CASCADE"),
    )
    sku_id = Column("skuID", Integer)
    product_id = Column("productID", Integer)
    store_id = Column("storeID", Integer)
    company_id = Column("companyID", Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_train_group_entities_companyid", "companyID"),
        Index("idx_train_group_entities_productid", "productID"),
        Index("idx_train_group_entities_skuid", "skuID"),
        Index("idx_train_group_entities_storeid", "storeID"),
        Index("idx_train_group_entities_train_groupid", "train_groupID"),
    )

    # Relationships
    train_group = relationship("TrainGroups", back_populates="train_group_entities")


class TrainTestMapping(Base):
    __tablename__ = "train_test_mapping"

    train_group_id = Column(
        "train_groupID",
        Integer,
        ForeignKey("train_groups.ID", name="link_to_train_groups", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    dataset_id = Column(
        "datasetID",
        Integer,
        ForeignKey("datasets.ID", name="link_to_datasets", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    dataset_type = Column(String(50), nullable=False)

    __table_args__ = (UniqueConstraint("train_groupID", "datasetID"),)

    # Relationships
    train_group = relationship("TrainGroups", back_populates="train_test_mapping")
    dataset = relationship("Datasets", back_populates="train_test_mapping")

    __unique_keys__: t.ClassVar[list[str]] = ["train_groupID", "datasetID"]


class Predictions(Base):
    __tablename__ = "predictions"

    frequency = Column(Text, primary_key=True)
    quantile = Column(REAL, primary_key=True)
    datapoint_id = Column(
        "datapointID",
        BigInteger,
        ForeignKey("datapoints.ID", name="link_to_datapoints", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    model = Column(Text, primary_key=True)
    time_step = Column(Integer, primary_key=True)
    prediction = Column(REAL, nullable=False)

    __table_args__ = (UniqueConstraint("frequency", "quantile", "datapointID", "model", "time_step"),)

    # Relationships
    datapoint = relationship("Datapoints", back_populates="predictions")


class CompanySpecificFeatureList(Base):
    __tablename__ = "company_specific_feature_list"

    id = Column("ID", Integer, Identity(always=True), primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    description = Column(Text)


class ViewRegistry(Base):
    __tablename__ = "view_registry"

    view_name = Column(Text, primary_key=True)
    feature_filter = Column(JSONB, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    build_complete = Column(Boolean, nullable=False)


# Normalization and metrics tables
class EngineeredFeaturesOverview(Base):
    __tablename__ = "engineered_features_overview"

    dataset_id = Column(
        "datasetID",
        Integer,
        ForeignKey("datasets.ID", name="link_to_datasets", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    feature = Column(Text, primary_key=True)
    company_id = Column(
        "companyID",
        Integer,
        ForeignKey("companies.ID", name="link_to_companies", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    start_date_hash = Column(Text, primary_key=True)
    end_date_hash = Column(Text, primary_key=True)

    # Relationships
    dataset = relationship("Datasets")
    company = relationship("Companies")


class EngineeredSalesFeatures(Base):
    __tablename__ = "engineered_sales_features"

    dataset_id = Column(
        "datasetID",
        Integer,
        ForeignKey("datasets.ID", name="link_to_datasets", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    mean_demand = Column(Float)
    std_demand = Column(Float)
    moores_excess_kurtosis_demand = Column(Float)
    kellys_skewness_demand = Column(Float)
    percentile_10_demand = Column(Float)
    percentile_30_demand = Column(Float)
    median_demand = Column(Float)
    percentile_70_demand = Column(Float)
    percentile_90_demand = Column(Float)
    inter_quartile_range = Column(Float)
    sku_id = Column(
        "skuID",
        Integer,
        ForeignKey("sku_table.ID", name="link_to_skus", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    start_date_hash = Column(Text, primary_key=True)
    end_date_hash = Column(Text, primary_key=True)

    # Relationships
    dataset = relationship("Datasets")
    sku = relationship("SkuTable")


class MetricsSkuLevel(Base):
    __tablename__ = "metrics_sku_level"

    sku_id = Column(
        "skuID",
        Integer,
        ForeignKey("sku_table.ID", name="link_to_sku_table", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    frequency = Column(String(50), primary_key=True)
    time_step = Column(Integer, primary_key=True)
    min_date = Column(Date, primary_key=True)
    max_date = Column(Date, primary_key=True)
    model = Column(String(100), primary_key=True)
    metric = Column(String(100), primary_key=True)
    value = Column(Float)
    max_base_date = Column(Date, primary_key=True)

    # Relationships
    sku = relationship("SkuTable")


class NormalizationDataProduct(Base):
    __tablename__ = "normalization_data_product"

    dataset_id = Column(
        "datasetID",
        Integer,
        ForeignKey("datasets.ID", name="link_to_datasets", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    feature_name = Column(Text, primary_key=True)
    end_date = Column(Date, primary_key=True)
    start_date = Column(Date, primary_key=True)
    mean = Column(Numeric)
    std = Column(Numeric)
    min = Column(Numeric)
    max = Column(Numeric)
    feature_id = Column(
        "featureID",
        Integer,
        ForeignKey(
            "feature_descriptions.ID", name="link_to_feature_descriptions", onupdate="RESTRICT", ondelete="CASCADE"
        ),
        primary_key=True,
    )

    # Relationships
    dataset = relationship("Datasets")
    feature = relationship("FeatureDescriptions")


class NormalizationDataStore(Base):
    __tablename__ = "normalization_data_store"

    dataset_id = Column(
        "datasetID",
        Integer,
        ForeignKey("datasets.ID", name="link_to_datasets", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    feature_name = Column(Text, primary_key=True)
    end_date = Column(Date, primary_key=True)
    start_date = Column(Date, primary_key=True)
    mean = Column(Numeric)
    std = Column(Numeric)
    max = Column(Numeric)
    min = Column(Numeric)
    feature_id = Column(
        "featureID",
        Integer,
        ForeignKey(
            "feature_descriptions.ID", name="link_to_feature_descriptions", onupdate="RESTRICT", ondelete="CASCADE"
        ),
        primary_key=True,
    )

    # Relationships
    dataset = relationship("Datasets")
    feature = relationship("FeatureDescriptions")


class NormalizationDataTime(Base):
    __tablename__ = "normalization_data_time"

    dataset_id = Column(
        "datasetID",
        Integer,
        ForeignKey("datasets.ID", name="link_to_datasets", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    feature_name = Column(Text, primary_key=True)
    mean = Column(Numeric)
    std = Column(Numeric)
    min = Column(Numeric)
    max = Column(Numeric)
    end_date = Column(Date, primary_key=True)
    start_date = Column(Date, primary_key=True)

    # Relationships
    dataset = relationship("Datasets")


class NormalizationDataTimeProduct(Base):
    __tablename__ = "normalization_data_time_product"

    dataset_id = Column(
        "datasetID",
        Integer,
        ForeignKey("datasets.ID", name="link_to_datasets", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    feature_name = Column(Text, primary_key=True)
    end_date = Column(Date, primary_key=True)
    start_date = Column(Date, primary_key=True)
    product_id = Column(
        "productID",
        Integer,
        ForeignKey("products.ID", name="link_to_products", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    mean = Column(Numeric)
    std = Column(Numeric)
    min = Column(Numeric)
    max = Column(Numeric)

    # Relationships
    dataset = relationship("Datasets")
    product = relationship("Products")


class NormalizationDataTimeRegion(Base):
    __tablename__ = "normalization_data_time_region"

    dataset_id = Column(
        "datasetID",
        Integer,
        ForeignKey("datasets.ID", name="link_to_datasets", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    feature_name = Column(Text, primary_key=True)
    end_date = Column(Date, primary_key=True)
    start_date = Column(Date, primary_key=True)
    region_id = Column(
        "regionID",
        Integer,
        ForeignKey("regions.ID", name="link_to_regions", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    mean = Column(Numeric)
    std = Column(Numeric)
    min = Column(Numeric)
    max = Column(Numeric)
    company_id = Column(
        "companyID",
        Integer,
        ForeignKey("companies.ID", name="link_to_companies", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relationships
    dataset = relationship("Datasets")
    region = relationship("Regions")
    company = relationship("Companies")


class NormalizationDataTimeSku(Base):
    __tablename__ = "normalization_data_time_sku"

    dataset_id = Column(
        "datasetID",
        Integer,
        ForeignKey("datasets.ID", name="link_to_datasets", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    feature_name = Column(Text, primary_key=True)
    mean = Column(Numeric)
    std = Column(Numeric)
    min = Column(Numeric)
    max = Column(Numeric)
    sku_id = Column(
        "skuID",
        Integer,
        ForeignKey("sku_table.ID", name="link_to_sku_table", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    end_date = Column(Date, primary_key=True)
    start_date = Column(Date, primary_key=True)

    # Relationships
    dataset = relationship("Datasets")
    sku = relationship("SkuTable")


class NormalizationDataTimeStore(Base):
    __tablename__ = "normalization_data_time_store"

    dataset_id = Column(
        "datasetID",
        Integer,
        ForeignKey("datasets.ID", name="link_to_datasets", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    end_date = Column(Date, primary_key=True)
    start_date = Column(Date, primary_key=True)
    store_id = Column(
        "storeID",
        Integer,
        ForeignKey("stores.ID", name="link_to_stores", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    std = Column(Numeric)
    mean = Column(Numeric)
    min = Column(Numeric)
    max = Column(Numeric)
    feature_name = Column(Text, primary_key=True)

    # Relationships
    dataset = relationship("Datasets")
    store = relationship("Stores")


class NormalizationFlags(Base):
    __tablename__ = "normalization_flags"

    dataset_id = Column(
        "datasetID",
        Integer,
        ForeignKey("datasets.ID", name="link_to_datasets", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    standardize = Column(Boolean)
    scale = Column(Boolean)
    feature_name = Column(Text, primary_key=True)
    start_date = Column(Text, primary_key=True)
    end_date = Column(Text, primary_key=True)
    company_id = Column(
        "companyID",
        Integer,
        ForeignKey("companies.ID", name="link_to_companies", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    )
    feature_type = Column(Text, primary_key=True)

    # Relationships
    dataset = relationship("Datasets")
    company = relationship("Companies")
