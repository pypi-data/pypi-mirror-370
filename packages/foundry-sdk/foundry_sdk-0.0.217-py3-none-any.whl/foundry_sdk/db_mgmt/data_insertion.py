from typing import List, Tuple, Union
from foundry_sdk.db_mgmt import SQLDatabase, InsertionMode


def insert_data(
    db: SQLDatabase,
    table: str,
    columns: Union[str, List[str]],
    data: List[Tuple],
    insertion_mode: InsertionMode,
    condition: str = None,
) -> None:
    """Retrieve data from a table in the database.

    Ensures column names are enclosed in double quotes for PostgreSQL.
    Allows single column name as a string or multiple as a list.
    """

    # Enclose column names in double quotes
    columns_string = ", ".join(f'"{col}"' for col in columns)

    # Construct query with optional condition
    query = f"IN {columns_string} FROM {table}"
    if condition:
        query += f" WHERE {condition}"

    result = db.execute_query(query, fetchall=True)
    db.close()

    return result
