import pandas as pd
import duckdb

# Ver como está o ID_MUNICIP no SINAN
con = duckdb.connect()
print("Amostra de ID_MUNICIP no DENG_PEA:")
print(con.execute("""
    SELECT ID_MUNICIP, COUNT(*) as casos
    FROM read_parquet('data/epidemiologia/DENG_PEA.parquet')
    GROUP BY ID_MUNICIP
    ORDER BY casos DESC
    LIMIT 10
""").df().to_string(index=False))