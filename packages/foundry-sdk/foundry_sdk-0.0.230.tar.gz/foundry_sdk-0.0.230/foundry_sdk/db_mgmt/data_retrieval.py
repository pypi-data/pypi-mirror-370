from typing import List, Tuple, Union, Optional
from foundry_sdk.db_mgmt import SQLDatabase


def retrieve_data(
    db: SQLDatabase, table: str, columns: Union[str, List[str]], condition: Optional[str] = None
) -> List[Tuple]:
    """
    Retrieve data from a table in the database.

    Ensures column names are enclosed in double quotes for PostgreSQL,
    unless columns == "*", in which case it is used as-is.
    Allows single column name as a string or multiple as a list.
    """
    # Handle special case for selecting all columns
    if isinstance(columns, str) and columns == "*":
        columns_string = "*"
    else:
        # Ensure columns is a list
        if isinstance(columns, str):
            columns = [columns]
        # Enclose column names in double quotes
        columns_string = ", ".join(f'"{col}"' for col in columns)

    # Construct query with optional condition
    query = f"SELECT {columns_string} FROM {table}"
    if condition:
        query += f" WHERE {condition}"

    result = db.execute_query(query, fetchall=True)
    db.close()

    return result
