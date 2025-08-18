# import typing as t
# from foundry_sdk.db_mgmt.sql_db import SQLDatabase


# import logging
# logger = logging.getLogger(__name__)


# def handle_time_sku_table_creation(db: SQLDatabase, table_name: str, create_new_time_sku_table: bool):

#     # check if the table exists
#     query = f"""
#     SELECT EXISTS (
#         SELECT FROM information_schema.tables
#         WHERE table_schema = 'public'
#         AND table_name = '{table_name}'
#     );
#     """
#     table_exists = db.execute_query(query, fetchone=True)[0]
#     if table_exists:
#         logger.info(f"Table {table_name} exists: {table_exists}")
#         return
#     else:
#         if not create_new_time_sku_table:
#             raise ValueError(f"Table {table_name} does not exist. Features thate are time-sku specific (varying over time, store, product) have their own table. To automatically create one set create_new_time_sku_table is set to True.")
#         else:
#             logger.warning(f"Table {table_name} does not exist. Creating table {table_name}")

#             query = f"""
#             CREATE TABLE {table_name} (
#                 "datapointID" INTEGER PRIMARY KEY,
#                 "value" TEXT,
#                 CONSTRAINT fk_datapoint FOREIGN KEY ("datapointID")
#                 REFERENCES datapoints("ID") ON DELETE CASCADE
#             );
#             """
#             db.execute_query(query, commit=True)
