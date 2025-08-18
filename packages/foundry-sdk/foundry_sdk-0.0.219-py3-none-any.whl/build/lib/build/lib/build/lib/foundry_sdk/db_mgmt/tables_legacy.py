from datetime import datetime

from foundry_sdk.db_mgmt import InsertionMode, SQLDatabase, Writer

#######################################################################################
############################# Data Tables for Raw Data ################################
#######################################################################################


############################# Mandatory tables ################################
class Company(Writer):
    TABLE = "companies"
    COLUMNS = [
        "name",
        "dataset_type",
        "description",
        "min_date",
        "max_date",
        "frequency",
    ]
    TYPES = [str, str, str, datetime, datetime, int]
    UNIQUE = ["name"]
    AUTO_ID = True

    def __init__(self, db: SQLDatabase, insertion_mode: InsertionMode):
        super().__init__(db, insertion_mode)


class Stores(Writer):
    TABLE = "stores"
    COLUMNS = ["companyID", "regionID", "name"]
    TYPES = [int, int, str]
    UNIQUE = ["companyID", "name"]
    AUTO_ID = True

    def __init__(self, db: SQLDatabase, insertion_mode: InsertionMode):
        super().__init__(db, insertion_mode)


class CategoryLevelDescriptions(Writer):
    TABLE = "category_level_descriptions"
    COLUMNS = ["level", "name", "companyID"]
    UNIQUE = ["level", "name", "companyID"]
    TYPES = [int, str, int]
    AUTO_ID = True


class CategoryRelations(Writer):
    TABLE = "category_relations"
    COLUMNS = ["subID", "parentID"]
    TYPES = [int, int]
    UNIQUE = ["subID", "parentID"]
    AUTO_ID = False


class Categories(Writer):
    TABLE = "categories"
    COLUMNS = ["companyID", "name"]
    TYPES = [int, str]
    UNIQUE = ["companyID", "name"]
    AUTO_ID = True


class Products(Writer):
    TABLE = "products"
    COLUMNS = ["name", "companyID"]
    TYPES = [str, int]
    UNIQUE = ["name", "companyID"]
    AUTO_ID = True


class ProductCategories(Writer):
    TABLE = "product_categories"
    COLUMNS = ["productID", "categoryID"]
    TYPES = [int, int]
    UNIQUE = ["productID", "categoryID"]
    AUTO_ID = False


class SKUTable(Writer):
    TABLE = "sku_table"
    COLUMNS = [
        "productID",
        "storeID",
    ]
    TYPES = [int, int]
    UNIQUE = ["productID", "storeID"]
    AUTO_ID = True


class DataPoints(Writer):
    TABLE = "datapoints"
    COLUMNS = ["skuID", "dateID"]
    TYPES = [int, int]
    UNIQUE = ["skuID", "dateID"]
    AUTO_ID = True


class Flags(Writer):
    TABLE = "flags"
    COLUMNS = ["datapointID", "name"]
    TYPES = [int, str]
    UNIQUE = ["datapointID", "name"]


class TimeSkuFeatures(Writer):
    TABLE = "time_sku_features"
    COLUMNS = ["datapointID", "featureID", "value"]
    TYPES = [int, int, str]
    UNIQUE = ["datapointID", "featureID"]
    AUTO_ID = False


# class GENERIC_TIME_SKU_DATA(Writer):
#     COLUMNS = ["datapointID", "value"]
#     TYPES = [int, str]
#     UNIQUE = ["datapointID"]
#     AUTO_ID = False

#     def __init__(self, db: SQLDatabase, insertion_mode: InsertionMode, table_name: str):
#         self.TABLE = table_name
#         super().__init__(db, insertion_mode)


class FeatureDescriptions(Writer):
    TABLE = "feature_descriptions"
    COLUMNS = ["name", "description", "var_type", "feature_type", "companyID"]
    TYPES = [str, str, str, str, int]
    UNIQUE = ["name", "companyID"]
    AUTO_ID = True


class FeatureLevels(Writer):
    TABLE = "feature_levels"
    COLUMNS = ["featureID", "level", "order"]
    TYPES = [int, str, int]
    UNIQUE = ["featureID", "level"]
    AUTO_ID = False


############################# Optional tables ################################


class StoreFeatures(Writer):
    TABLE = "store_features"
    COLUMNS = ["storeID", "featureID", "value"]
    TYPES = [int, int, str]
    UNIQUE = ["storeID", "featureID"]
    AUTO_ID = False


class ProductFeatures(Writer):
    TABLE = "product_features"
    COLUMNS = ["productID", "featureID", "value"]
    TYPES = [int, int, str]
    UNIQUE = ["productID", "featureID"]
    AUTO_ID = False


class SKUFeatures(Writer):
    TABLE = "sku_features"
    COLUMNS = ["skuID", "featureID", "value"]
    TYPES = [int, int, str]
    UNIQUE = ["skuID", "featureID"]
    AUTO_ID = False


class TimeProductFeatures(Writer):
    TABLE = "time_product_features"
    COLUMNS = ["dateID", "productID", "featureID", "value"]
    TYPES = [int, int, int, str]
    UNIQUE = ["productID", "dateID", "featureID"]
    AUTO_ID = False


class TimeRegionFeatures(Writer):
    TABLE = "time_region_features"
    COLUMNS = ["regionID", "dateID", "featureID", "value"]
    TYPES = [int, int, int, str]
    UNIQUE = ["regionID", "dateID", "featureID"]
    AUTO_ID = False


class TimeStoreFeatures(Writer):
    TABLE = "time_store_features"
    COLUMNS = ["storeID", "dateID", "featureID", "value"]
    TYPES = [int, int, int, str]
    UNIQUE = ["storeID", "dateID", "featureID"]
    AUTO_ID = False


#######################################################################################
############################# Tables for training process #############################
#######################################################################################


class ExperimentGroups(Writer):
    TABLE = "experiment_groups"
    COLUMNS = ["name", "description"]
    TYPES = [str, str]
    UNIQUE = ["name"]
    AUTO_ID = True


class Datasets(Writer):
    TABLE = "datasets"
    COLUMNS = [
        "experiment_groupID",
        "type",
        "start_date",
        "end_date",
        "name",
        "description",
    ]
    TYPES = [int, str, datetime, datetime, str, str]
    UNIQUE = ["name"]
    AUTO_ID = True


class DatasetMatching(Writer):
    TABLE = "dataset_matching"
    COLUMNS = ["datasetID", "skuID"]
    TYPES = [int, int]
    UNIQUE = ["datasetID", "skuID"]
    AUTO_ID = False
