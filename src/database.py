import duckdb
import logging

logger = logging.getLogger(__name__)


class Database:

    def __init__(self):
        self.connection = duckdb.connect()

    def read_parquet(self, path, columns=None, limit=None):
        try:
            cols = ", ".join(columns) if columns else "*"
            lim = f"LIMIT {limit}" if limit else ""
            query = f"SELECT {cols} FROM read_parquet('{path}') {lim}"
            logger.info(f"Executando query no parquet...")
            result = self.connection.execute(query).df()
            logger.info(f"Dados carregados: {len(result):,} registros")
            return result
        except Exception as e:
            logger.error(f"Erro ao ler parquet: {e}")
            return None

    def query(self, sql):
        try:
            return self.connection.execute(sql).df()
        except Exception as e:
            logger.error(f"Erro na query: {e}")
            return None