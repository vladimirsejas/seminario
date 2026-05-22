import duckdb


class Database:

    def __init__(self):

        self.connection = duckdb.connect()

    def read_parquet(self, path):

        query = f"""
            SELECT *
            FROM read_parquet('{path}')
        """

        return self.connection.execute(query).df()