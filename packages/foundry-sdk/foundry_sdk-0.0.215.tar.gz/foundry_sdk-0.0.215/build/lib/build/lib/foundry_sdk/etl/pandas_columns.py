from enum import Enum

import pandas as pd


class CategoriesLevelColumns(Enum):
    LEVEL = "level"
    NAME = "name"
    _TYPES = [int, object]


class StoresColumns(Enum):
    STORE = "store"
    COUNTRY = "country"
    ADDITIONAL_COLUMNS = ["subdivision", "city"]
    _TYPES = [object, object, object]


class ProductsColumns(Enum):
    PRODUCT = "product"
    CATEGORY = "category"
    _TYPES = [object, object]


class FeatureDescriptionsColumns(Enum):
    NAME = "name"
    DESCRIPTION = "description"
    VAR_TYPE = "var_type"
    LEVELS = "levels"
    _TYPES = [object, object, object, object]


class TimeSkuColumns(Enum):
    DATE = "date"
    STORE = "store"
    PRODUCT = "product"
    FEATURE = "feature"
    VALUE = "value"
    _TYPES = [pd.Timestamp, object, object, object, object]


class FlagsColumns(Enum):
    DATE = "date"
    STORE = "store"
    PRODUCT = "product"
    FLAG = "flag"
    _TYPES = [pd.Timestamp, object, object, object]


class StoreFeatureColumns(Enum):
    STORE = "store"
    FEATURE = "feature"
    VALUE = "value"
    _TYPES = [object, object, object]


class ProductFeatureColumns(Enum):
    PRODUCT = "product"
    FEATURE = "feature"
    VALUE = "value"
    _TYPES = [object, object, object]


class SKUFeatureColumns(Enum):
    PRODUCT = "product"
    STORE = "store"
    FEATURE = "feature"
    VALUE = "value"
    _TYPES = [object, object, object, object]


class TimeProductFeatureColumns(Enum):
    DATE = "date"
    PRODUCT = "product"
    FEATURE = "feature"
    VALUE = "value"
    _TYPES = [pd.Timestamp, object, object, object]


class TimeRegionFeatureColumns(Enum):
    DATE = "date"
    COUNTRY = "country"
    FEATURE = "feature"
    VALUE = "value"
    ADDITIONAL_COLUMNS = ["subdivision", "city"]
    _TYPES = [pd.Timestamp, object, object, object, object, object]


class TimeStoreFeatureColumns(Enum):
    DATE = "date"
    STORE = "store"
    FEATURE = "feature"
    VALUE = "value"
    _TYPES = [pd.Timestamp, object, object, object]
