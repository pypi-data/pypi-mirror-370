# Description: Functions to filter data from the database.

# from foundry_sdk.db_mgmt.data_retrieval import retrieve_data
# from foundry_sdk.db_mgmt.sql_db import SQLDatabase
# import pandas as pd
# import typing as t


# def get_data_ids(db: SQLDatabase, table_name: str, column_name: str, datapoints: t.List[str], output_column_name=None, output_column_ID=None):

#     """
#     Get the category IDs from the database for a given company and list of category names.

#     """

#     if output_column_name is None:
#         output_column_name = column_name

#     if output_column_ID is None:
#         output_column_ID = "ID"

#     escaped_datapoints = [
#         str(datapoint).replace("'", "''") if pd.notna(datapoint) else 'NULL'
#         for datapoint in datapoints
#     ]
#     condition = f"""
#         {column_name} IN ({", ".join([f"'{datapoint}'" if datapoint != 'NULL' else datapoint for datapoint in escaped_datapoints])})
#     """

#     retrieved_data = retrieve_data(db, table_name, ["ID", column_name], condition=condition)
#     retrieved_data = {column_name: ID for ID, column_name in retrieved_data}
#     retrieved_data_df = pd.DataFrame({output_column_name: list(retrieved_data.keys()), output_column_ID: list(retrieved_data.values())})

#     return retrieved_data_df


# def get_data_ids_by_company(db: SQLDatabase, company_id: int, table_name: str, column_name: str, datapoints: t.List[str], output_column_name=None, output_column_ID=None):

#     """
#     Get the category IDs from the database for a given company and list of category names.

#     """

#     if output_column_name is None:
#         output_column_name = column_name

#     if output_column_ID is None:
#         output_column_ID = "ID"

#     escaped_datapoints = [
#         str(datapoint).replace("'", "''") if pd.notna(datapoint) else 'NULL'
#         for datapoint in datapoints
#     ]
#     condition = f"""
#         {column_name} IN ({", ".join([f"'{datapoint}'" if datapoint != 'NULL' else datapoint for datapoint in escaped_datapoints])}) AND "companyID" = {company_id}
#     """

#     retrieved_data = retrieve_data(db, table_name, ["ID", column_name], condition=condition)
#     retrieved_data = {column_name: ID for ID, column_name in retrieved_data}
#     retrieved_data_df = pd.DataFrame({output_column_name: list(retrieved_data.keys()), output_column_ID: list(retrieved_data.values())})

#     return retrieved_data_df

