import duckdb

con = duckdb.connect()

print("Amostra da base PEA:")
print(con.execute("""
    SELECT * FROM read_parquet('data/epidemiologia/DENG_PEA.parquet')
    LIMIT 5
""").df().to_string(index=False))

print("\nEscolaridade (CS_ESCOL_N):")
print(con.execute("""
    SELECT CS_ESCOL_N, COUNT(*) as total
    FROM read_parquet('data/epidemiologia/DENG_PEA.parquet')
    GROUP BY CS_ESCOL_N
    ORDER BY total DESC
""").df().to_string(index=False))

print("\nRaça (CS_RACA):")
print(con.execute("""
    SELECT CS_RACA, COUNT(*) as total
    FROM read_parquet('data/epidemiologia/DENG_PEA.parquet')
    GROUP BY CS_RACA
    ORDER BY total DESC
""").df().to_string(index=False))