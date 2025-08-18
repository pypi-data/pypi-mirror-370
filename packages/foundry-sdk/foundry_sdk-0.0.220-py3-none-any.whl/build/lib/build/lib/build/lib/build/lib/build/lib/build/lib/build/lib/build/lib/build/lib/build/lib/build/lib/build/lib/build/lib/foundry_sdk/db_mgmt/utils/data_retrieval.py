"""Reusable database utility functions for data retrieval."""

import polars as pl

from foundry_sdk.db_mgmt.sql_db_alchemy import SQLAlchemyDatabase
from foundry_sdk.db_mgmt.tables import Dates


def get_all_dates(db: SQLAlchemyDatabase) -> pl.DataFrame:
    """
    Get all dates from the database as polars DataFrame.

    Args:
        db: SQLAlchemy database instance

    Returns:
        DataFrame with columns: dateID, date

    """
    # Get all dates from the db as polars DataFrame
    with db.get_session(read_only=True) as session:
        date_rows = session.query(Dates.id, Dates.date).all()
    dates_df = pl.DataFrame([{"dateID": row[0], "date": row[1]} for row in date_rows])

    return dates_df
