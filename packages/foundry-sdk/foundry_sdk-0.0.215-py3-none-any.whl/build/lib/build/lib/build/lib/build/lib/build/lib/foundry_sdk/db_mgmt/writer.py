from foundry_sdk.db_mgmt import SQLDatabase, InsertionMode
import pandas as pd
from tqdm import tqdm
import io
import math
import datetime
import random
import hashlib


class Writer:
    """
    Class to write data to a database table - all tables will inherit from this class

    """

    def __init__(self, db: SQLDatabase, insertion_mode: InsertionMode):
        self.db = db
        self.insertion_mode = insertion_mode

    def write_to_db_single_row(self, *args, save_ids=True):
        query = self.build_query()
        ids = self.db.execute_query(query, args, fetchone=True, commit=True)[0]
        self.db.close()
        self.ids = ids if save_ids else None

    def write_to_db_multi_row(
        self, df: pd.DataFrame, save_ids: bool = True, show_progress_bar: bool = False, chunk_size: int = 1_000_000
    ):
        """

        Bulk upsert a DataFrame into self.TABLE using COPY-into-staging for speed.

        Parameters:
        - df: pandas DataFrame with columns matching self.COLUMNS
        - save_ids: if True, falls back to execute_multi_query and returns IDs
        - show_progress_bar: print progress per chunk
        - chunk_size: number of rows per COPY batch

        """
        # Ensure target table is defined
        if not hasattr(self, "TABLE") or not isinstance(self.TABLE, str):
            raise AttributeError("Instance attribute TABLE must be defined as the target table name")

        # 1) Validate & reorder columns
        if set(df.columns) != set(self.COLUMNS):
            raise ValueError(f"Columns in DataFrame {df.columns} do not match target columns: {self.COLUMNS}")
        df = df[self.COLUMNS]

        # 2) If IDs must be returned, use existing execute_multi_query path
        if save_ids:
            args = [tuple(None if pd.isna(val) else t(val) for t, val in zip(self.TYPES, row)) for row in df.values]
            query = self.build_query(single_placeholder=False)
            ids = self.db.execute_multi_query(
                query, args, fetchone=True, commit=True, show_progress_bar=show_progress_bar
            )
            self.db.close()
            self.ids = ids
            return

        target_table = self.TABLE
        cols_sql = ", ".join(f'"{c}"' for c in self.COLUMNS)

        # Build conflict and update clauses
        conflict_map = {
            InsertionMode.IGNORE: "DO NOTHING",
            InsertionMode.RAISE: "",
            InsertionMode.UPDATE: "DO UPDATE",
            InsertionMode.INSERT_MISSING: "DO NOTHING",
        }
        conflict_columns = getattr(self, "UNIQUE", None)
        if conflict_columns:
            cols = ", ".join(f'"{c}"' for c in conflict_columns)
            clause = conflict_map[self.insertion_mode]
            conflict_clause = f"ON CONFLICT ({cols}) {clause}"
            if self.insertion_mode == InsertionMode.UPDATE:
                set_sql = ", ".join(f'"{col}" = EXCLUDED."{col}"' for col in self.COLUMNS if col.upper() != "ID")
                update_clause = f"SET {set_sql}"
            else:
                update_clause = ""
        else:
            conflict_clause = ""
            update_clause = ""

        # Template for upsert per chunk
        base_upsert = (
            f"INSERT INTO {target_table} ({cols_sql}) "
            f"SELECT {cols_sql} FROM {{staging_table}} "
            f"{conflict_clause} {update_clause};"
        )

        # 3) FAST PATH: chunked COPY into uniquely-named staging, no ID returning
        self.db.connect()
        conn = self.db.connection
        cursor = conn.cursor()

        total = len(df)
        num_chunks = math.ceil(total / chunk_size)
        if show_progress_bar:
            pbar = tqdm(total=total, unit="rows", disable=not show_progress_bar)
        for i in range(num_chunks):
            # Generate a unique staging table name per chunk
            timestamp = datetime.datetime.utcnow().isoformat()
            rand_int = random.randint(0, 1000)
            hash_input = f"{timestamp}_{rand_int}".encode("utf-8")
            suffix = hashlib.md5(hash_input).hexdigest()[:8]
            staging_table = f"staging_{suffix}"  # hash-only name

            # Create temporary staging table
            cursor.execute(f"CREATE TEMPORARY TABLE {staging_table} (LIKE {target_table});")

            # Write chunk to in-memory CSV with '\\N' for NULLs
            start = i * chunk_size
            end = min(start + chunk_size, total)
            chunk = df.iloc[start:end]
            buf = io.StringIO()
            chunk.to_csv(buf, index=False, header=False, sep=",", na_rep="\\N")
            buf.seek(0)

            # COPY into staging
            copy_sql = f"COPY {staging_table} ({cols_sql}) FROM STDIN WITH (FORMAT csv, DELIMITER ',', NULL '\\N')"
            cursor.copy_expert(copy_sql, buf)

            # Upsert into target
            upsert_sql = base_upsert.format(staging_table=staging_table)
            cursor.execute(upsert_sql)

            # Drop staging table to release resources
            cursor.execute(f"DROP TABLE {staging_table};")

            if show_progress_bar:
                pbar.update(end - start)
                pbar.set_postfix_str(f"{end:,} of {total:,} rows loaded")

        # Finalize
        conn.commit()
        cursor.close()
        conn.close()
        self.db.close()
        self.ids = None

    def build_query(self, single_placeholder=False):
        # If a UNIQUE attribute is defined, use it; otherwise default to the first column

        confict_resulution = {
            InsertionMode.IGNORE: "DO NOTHING",
            InsertionMode.RAISE: "",
            InsertionMode.UPDATE: "DO UPDATE",
            InsertionMode.INSERT_MISSING: "DO NOTHING",
        }
        if self.insertion_mode == InsertionMode.UPDATE:
            update_clause = "SET" + ", ".join(f'"{col}" = EXCLUDED."{col}"' for col in self.COLUMNS if col != "ID")
        else:
            update_clause = ""

        conflict_columns = getattr(self, "UNIQUE")
        if conflict_columns is None:
            conflict_clause = ""
            update_clause = ""
        else:
            conflict_clause = (
                "ON CONFLICT ("
                + ", ".join(f'"{col}"' for col in conflict_columns)
                + f") {confict_resulution[self.insertion_mode]}"
            )

        if single_placeholder:
            placeholders = "%s"
        else:
            placeholders = ", ".join(["%s" for _ in range(len(self.COLUMNS))])
        column_names = ", ".join(f'"{col}"' for col in self.COLUMNS)
        returning_clause = 'RETURNING "ID"' if getattr(self, "AUTO_ID", False) else ""

        query = f"""
            INSERT INTO {self.TABLE} ({column_names})
            VALUES ({placeholders})
            {conflict_clause}
            {update_clause}
            {returning_clause}
            """

        return query.strip()
