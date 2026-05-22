import duckdb

con = duckdb.connect()

# Mostra as colunas sem carregar tudo na memória
result = con.execute("""
    SELECT * FROM read_parquet('C:/seminario/data/epidemiologia/DENGBR24.parquet')
    LIMIT 5
""").df()

print(f"Colunas ({len(result.columns)}):")
print(list(result.columns))
print("\nPrimeiras linhas:")
print(result)

# Conta total sem carregar tudo
total = con.execute("""
    SELECT COUNT(*) FROM read_parquet('C:/seminario/data/epidemiologia/DENGBR24.parquet')
""").fetchone()[0]

print(f"\nTotal de linhas: {total}")

