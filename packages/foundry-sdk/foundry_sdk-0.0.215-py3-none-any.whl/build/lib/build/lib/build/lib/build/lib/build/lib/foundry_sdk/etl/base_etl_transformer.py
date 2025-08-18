from abc import ABC, abstractmethod
import typing as t
import pandas as pd
from foundry_sdk.db_mgmt import SQLDatabase

import logging
logger = logging.getLogger(__name__)

class BaseETLTransformer(ABC):
    
    """Contains methods for extracting and transforming dataset information.

    See documentation how to get started with new test database:
    https://github.com/d3group/foundry-master/blob/main/documentation/new_db_set_up.md

    See documentation how to onboard a new dataset:
    https://github.com/d3group/foundry-master/blob/main/documentation/new_dataset_onboarding.md

    Dockstrings for all methods can be found in the template repository:
    https://github.com/d3group/foundry-etl-TEMPLATE_REPO.git

    """

    def __init__(
        self,
        db: SQLDatabase,
        # all datasets indivially ...
    ):
        """Initialize the ETLTransformer object.

        Args:
            db (SQLDatabase): Database connection object.
            all datasets indivially ...
        """

        self.db = db
        # all datasets indivially ...

        self.clean_data()


    #################################### OPTIONAL: Data Cleaning ####################################
    
    def clean_data(self):
        pass
    
#########################################################################################################
#################################### MANDATORY DATA EXTRACTION ##########################################
#########################################################################################################

    #################################### MANDATORY: Dates ###########################################

    @abstractmethod  
    def get_dates(self) -> t.Tuple[t.List, pd.Timestamp, pd.Timestamp]:
        pass

 

    #################################### MANDATORY: Store-Region mapping ############################
    @abstractmethod
    def get_store_region_map(self) -> pd.DataFrame:
        pass



    #################################### MANDATORY: Categories ######################################

    @abstractmethod
    def get_category_level_description_map(self) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_categories(self) -> pd.DataFrame:
        pass

    #################################### MANDATORY: Products ########################################
    
    @abstractmethod
    def get_products(self) -> pd.DataFrame:
        pass
    
    
    #################################### MANDATORY: Time-SKU data ###################################

    @abstractmethod
    def get_time_sku_data(self) -> pd.DataFrame:
        pass
    

    #################################### MANDATORY: Flags ###########################################
    
    @abstractmethod
    def get_flags_map(self) -> pd.DataFrame:
        pass
    
#########################################################################################################
#################################### OPTIONAL DATA EXTRACTION ###########################################
#########################################################################################################
    
    #################################### OPTIONAL: Store features ###################################
    
    @abstractmethod
    def get_store_feature_description_map(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_store_feature_map(self) -> pd.DataFrame:    
        pass
    
    #################################### OPTIONAL: Product features ###################################
    
    @abstractmethod
    def get_product_feature_description_map(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_product_feature_map(self) -> pd.DataFrame:    
        pass

    #################################### OPTIONAL: SKU features ###################################
    
    @abstractmethod
    def get_sku_feature_description_map(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_sku_feature_map(self) -> pd.DataFrame:    
        pass

    #################################### OPTIONAL: Time-Product features ############################
    
    @abstractmethod
    def get_time_product_feature_description_map(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_time_product_feature_map(self) -> pd.DataFrame:    
        pass


    #################################### OPTIONAL: Time-Region features #############################
    
    @abstractmethod 
    def get_time_region_feature_description_map(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_time_region_feature_map(self) -> pd.DataFrame:    
        pass

    #################################### OPTIONAL: Time-Store features ##############################

    @abstractmethod
    def get_time_store_feature_description_map(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_time_store_feature_map(self) -> pd.DataFrame:
        pass