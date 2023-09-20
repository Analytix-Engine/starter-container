import humanize
import pandas as pd
from sqlalchemy import Engine, create_engine, text


class SQLDatabaseConnection:
    def __init__(self, engine: Engine, query_row_limit: int = 100_000):
        self.engine = engine
        self.query_row_limit = query_row_limit

    def execute_transaction(self, sql: str):
        """
        Executes a transaction on the database.

        Args:
            sql (str): SQL query to execute.
        """
        with self.engine.begin() as conn:
            conn.execute(text(sql))

    def read_sql_into_df(self, sql: str) -> pd.DataFrame:
        """
        Executes a query on the database and returns the result as a pandas DataFrame.

        Args:
            sql (str): SQL query to execute.

        Returns:
            pd.DataFrame: Result of the query.
        """
        with self.engine.connect() as connection:
            result = connection.execute(text(sql))
            if result.returns_rows > self.query_row_limit:
                raise ValueError(
                    f"""
                    Query returns too many rows. Please limit the query to {humanize.intword(self.query_row_limit)} rows or less.
                """
                )
            df = pd.DataFrame(result.fetchall())
            return df

    def insert_snapshot_df(self, df: pd.DataFrame, table_name: str):
        """
        Inserts a snapshot of a pandas DataFrame into the database.
        """
        with self.engine.connect() as conn:
            df.to_sql(table_name, con=conn, if_exists="append", index=False)
            conn.commit()


if __name__ == "__main__":
    # Create a SQLite Connection
    sqlite_engine = create_engine("sqlite:///bswbsw.db")
    sqlite_connection = SQLDatabaseConnection(sqlite_engine)

    # Create a PostgreSQL Connection (requires a running PostgreSQL server)
    POSTGRES_DB = "postgres"
    POSTGRES_USER = "postgres"
    POSTGRES_PASSWORD = "postgres"
    POSTGRES_HOST = "localhost"
    POSTGRES_PORT = "5432"
    postgres_engine = create_engine(
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    postgres_connection = SQLDatabaseConnection(postgres_engine)

    create_dummy_table_queries = [
        "DROP TABLE IF EXISTS test_table;",
        """CREATE TABLE test_table (
            name TEXT NOT NULL
        );""",
        "INSERT INTO test_table (name) VALUES ('John');",
        "INSERT INTO test_table (name) VALUES ('Jane');",
        "INSERT INTO test_table (name) VALUES ('Joe');",
    ]
    for query in create_dummy_table_queries:
        sqlite_connection.execute_transaction(query)
        postgres_connection.execute_transaction(query)

    select_all_from_test_table = """
        SELECT * FROM test_table;
    """

    sqlite_df = sqlite_connection.read_sql_into_df(select_all_from_test_table)
    print(f"Printing sqlite: \n{sqlite_df}")
    postgres_df = postgres_connection.read_sql_into_df(select_all_from_test_table)
    print(f"Printing postgres: \n{postgres_df}")

    snapshot_df = pd.DataFrame([["Piet"], ["Ben"], ["Jan"]], columns=["name"])

    sqlite_connection.insert_snapshot_df(snapshot_df, "test_table")
    postgres_connection.insert_snapshot_df(snapshot_df, "test_table")

    sqlite_df = sqlite_connection.read_sql_into_df(select_all_from_test_table)
    print(f"Printing sqlite: \n{sqlite_df}")
    postgres_df = postgres_connection.read_sql_into_df(select_all_from_test_table)
    print(f"Printing postgres: \n{postgres_df}")
