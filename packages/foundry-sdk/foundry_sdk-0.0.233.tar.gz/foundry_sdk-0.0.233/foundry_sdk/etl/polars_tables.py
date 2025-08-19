from dataclasses import dataclass

import polars as pl


@dataclass
class ColumnSpec:
    name: str
    types: list[pl.DataType]
    nullable: bool = False
    optional: bool = False
    unique: bool = False


@dataclass
class SchemaSpec:
    columns: list[ColumnSpec]
    keys: list[str] = None
    exclusive_optional_groups: list[list[str]] = None

    def required_columns(self) -> list[str]:
        return [col.name for col in self.columns if not col.optional]

    def optional_columns(self) -> list[str]:
        return [col.name for col in self.columns if col.optional]

    def column_names(self) -> set[str]:
        return {col.name for col in self.columns}

    def unique_columns(self) -> list[str]:
        return [col.name for col in self.columns if col.unique]


store_region_map_schema = SchemaSpec(
    columns=[
        ColumnSpec(name="store", types=[pl.Utf8], nullable=False, unique=True),
        ColumnSpec(name="region", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="level", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="country", types=[pl.Utf8], nullable=False, unique=False),
    ],
    keys=["store"],
)

# One product can also belong to multiple categories, hence the composite key
products_schema = SchemaSpec(
    columns=[
        ColumnSpec(name="product", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="category", types=[pl.Utf8], nullable=False, unique=False),
    ],
    keys=["product", "category"],
)

categories_level_description_schema = SchemaSpec(
    columns=[
        ColumnSpec(name="level", types=[pl.Int32], nullable=False, unique=True),
        ColumnSpec(name="name", types=[pl.Utf8], nullable=False, unique=True),
    ],
    keys=["level"],  # Composite uniqueness
)

description_map_schema = SchemaSpec(
    columns=[
        ColumnSpec(name="name", types=[pl.Utf8], nullable=False, unique=True),
        ColumnSpec(name="description", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="var_type", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(
            name="levels", types=[pl.List(pl.Utf8), pl.Null], nullable=True, unique=False
        ),  # Can be null if there are no categorical features
    ],
    keys=["name"],
)

time_sku_data_schema = SchemaSpec(
    columns=[
        ColumnSpec(name="date", types=[pl.Date], nullable=False, unique=False),
        ColumnSpec(name="product", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="store", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="feature", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(
            name="value", types=[pl.Float64], nullable=True, unique=False
        ),  # time sku features cannot be categorical
    ],
    keys=["date", "product", "store", "feature"],
)

store_feature_data_schema = SchemaSpec(
    columns=[
        ColumnSpec(name="store", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="feature", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(
            name="value", types=[pl.Float64, pl.Utf8], nullable=True, unique=False
        ),  # Can be string in case of categorical features
    ],
    keys=["store", "feature"],
)

product_feature_data_schema = SchemaSpec(
    columns=[
        ColumnSpec(name="product", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="feature", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(
            name="value", types=[pl.Float64, pl.Utf8], nullable=True, unique=False
        ),  # Can be string in case of categorical features
    ],
    keys=["product", "feature"],
)

sku_feature_data_schema = SchemaSpec(
    columns=[
        ColumnSpec(name="product", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="store", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="feature", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(
            name="value", types=[pl.Float64, pl.Utf8], nullable=True, unique=False
        ),  # Can be string in case of categorical features
    ],
    keys=["product", "store", "feature"],
)

time_product_feature_data_schema = SchemaSpec(
    columns=[
        ColumnSpec(name="date", types=[pl.Date], nullable=False, unique=False),
        ColumnSpec(name="product", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="feature", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(
            name="value", types=[pl.Float64, pl.Utf8], nullable=True, unique=False
        ),  # Can be string in case of categorical features
    ],
    keys=["date", "product", "feature"],
)

time_region_feature_data_schema = SchemaSpec(
    columns=[
        ColumnSpec(name="date", types=[pl.Date], nullable=False, unique=False),
        ColumnSpec(name="country", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="region", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="feature", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="level", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(
            name="value", types=[pl.Float64, pl.Utf8], nullable=True, unique=False
        ),  # Can be string in case of categorical features
    ],
    keys=["date", "country", "feature", "region"],
)

time_store_feature_data_schema = SchemaSpec(
    columns=[
        ColumnSpec(name="date", types=[pl.Date], nullable=False, unique=False),
        ColumnSpec(name="store", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="feature", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(
            name="value", types=[pl.Float64, pl.Utf8], nullable=True, unique=False
        ),  # Can be string in case of categorical features
    ],
    keys=["date", "store", "feature"],
)

flags_schema = SchemaSpec(
    columns=[
        ColumnSpec(name="date", types=[pl.Date], nullable=False, unique=False),
        ColumnSpec(name="product", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="store", types=[pl.Utf8], nullable=False, unique=False),
        ColumnSpec(name="flag", types=[pl.Utf8], nullable=False, unique=False),
    ],
    keys=["date", "product", "store", "flag"],
)
