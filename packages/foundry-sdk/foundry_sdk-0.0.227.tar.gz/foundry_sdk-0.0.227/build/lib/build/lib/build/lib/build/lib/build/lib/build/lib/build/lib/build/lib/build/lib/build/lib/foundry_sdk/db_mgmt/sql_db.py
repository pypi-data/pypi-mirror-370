import logging
from pathlib import Path

import numpy as np
import psycopg2
from kedro.config import OmegaConfigLoader
from kedro.framework.project import settings
from tqdm import tqdm

# Configure logging as needed (this is just a basic config)
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


class SQLDatabase:
    @staticmethod
    def get_db_credentials():
        """
        Fetch PostgreSQL database credentials from the Kedro configuration.
        Uses `OmegaConfigLoader` to load credentials stored under `credentials.postgres`.
        Returns:
            dict: A dictionary with the database connection details (e.g., host, port, user, password, dbname).
        """
        conf_path = str(Path(settings.CONF_SOURCE))
        conf_loader = OmegaConfigLoader(conf_source=conf_path)
        db_credentials = conf_loader["credentials"]["postgres"]

        return db_credentials

    @staticmethod
    def clean_params(params: list[tuple]) -> list[tuple]:
        return [tuple(int(x) if isinstance(x, np.integer) else x for x in row) for row in params]

    def __init__(self, autocommit=False):
        self._credentials = self.get_db_credentials()["con"]
        self.connection = None
        self.autocommit = autocommit

    def connect(self):
        if not self.connection:
            self.connection = psycopg2.connect(self._credentials)
            self.connection.autocommit = self.autocommit

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.connection.rollback()
        elif not self.autocommit:
            self.connection.commit()
        self.close()

    def execute_query(
        self,
        query: str,
        params: tuple = None,
        fetchall: bool = False,
        fetchone: bool = False,
        commit: bool = True,
        close_connection: bool = True,
    ):
        if fetchall and fetchone:
            raise ValueError("Both fetchall and fetchone cannot be True")
        if not self.connection:
            self.connect()
        try:
            with self.connection.cursor() as cur:
                cur.execute(query, params)
                result = cur.fetchall() if fetchall else cur.fetchone() if fetchone else None
            if commit:
                self.connection.commit()
            if close_connection:
                self.close()
            return result
        except Exception as e:
            error_msg = f"Error executing query: {query}. Parameters: {params}. Exception: {e}"
            logging.error(error_msg)
            raise Exception(error_msg) from e

    def execute_multi_query(
        self,
        query: str,
        params: tuple = None,
        fetchall: bool = False,
        fetchone: bool = False,
        commit: bool = True,
        commit_frequency: int = 1000,
        close_connection: bool = True,
        show_progress_bar: bool = False,
    ):
        if fetchall and fetchone:
            raise ValueError("Both fetchall and fetchone cannot be True")
        if not self.connection:
            self.connect()
        try:
            with self.connection.cursor() as cur:
                results = []
                last_commit = 0
                for param in tqdm(params) if show_progress_bar else params:
                    cur.execute(query, param)
                    result = cur.fetchall() if fetchall else cur.fetchone() if fetchone else None
                    if result is not None:
                        result = result[0] if fetchone else result
                    results.append(result)
                    last_commit += 1
                    if last_commit >= commit_frequency:
                        if commit:
                            self.connection.commit()
                        last_commit = 0
            if commit:
                self.connection.commit()
            if close_connection:
                self.close()
            return results
        except Exception as e:
            error_msg = f"Error executing query: {query}. Parameters: {params}. Exception: {e}"
            logging.error(error_msg)
            raise Exception(error_msg) from e
