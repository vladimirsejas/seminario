import urllib.request
import pandas as pd
import duckdb
import io

print("=== CRUZAMENTO IDHM x DENGUE ===")

# 1. Baixa tabela de códigos IBGE
print("\n1. Baixando códigos IBGE dos municípios...")
url = "https://raw.githubusercontent.com/kelvins/Municipios-Brasileiros/main/csv/municipios.csv"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=30) as r:
    df_cod = pd.read_csv(io.StringIO(r.read().decode("utf-8")))

UF_MAP = {
    11:'RO',12:'AC',13:'AM',14:'RR',15:'PA',16:'AP',17:'TO',
    21:'MA',22:'PI',23:'CE',24:'RN',25:'PB',26:'PE',27:'AL',
    28:'SE',29:'BA',31:'MG',32:'ES',33:'RJ',35:'SP',
    41:'PR',42:'SC',43:'RS',50:'MS',51:'MT',52:'GO',53:'DF'
}
df_cod["uf"] = df_cod["codigo_uf"].map(UF_MAP)
df_cod["codigo_ibge"] = df_cod["codigo_ibge"].astype(str).str[:6]
df_cod["nome_upper"] = df_cod["nome"].str.upper().str.strip()
print(f"   {len(df_cod)} municípios carregados.")

# 2. Carrega IDHM do Atlas Brasil
print("\n2. Carregando IDHM do Atlas Brasil...")
df_idh = pd.read_excel("data/epidemiologia/data.xlsx")
df_idh["uf"] = df_idh["Territorialidade"].str.extract(r'\((\w+)\)$')
df_idh["nome_mun"] = df_idh["Territorialidade"].str.replace(r'\s*\(\w+\)$', '', regex=True).str.strip()
df_idh["nome_upper"] = df_idh["nome_mun"].str.upper().str.strip()
print(f"   {len(df_idh)} municípios no IDHM.")

# 3. Cruza por nome + UF
print("\n3. Cruzando...")
df_merged = df_idh.merge(
    df_cod[["codigo_ibge","nome_upper","uf"]],
    on=["nome_upper","uf"],
    how="left"
)
encontrados = df_merged["codigo_ibge"].notna().sum()
print(f"   {encontrados} de {len(df_merged)} municípios cruzados ({encontrados/len(df_merged)*100:.1f}%)")

# 4. Salva IDHM com código IBGE
df_final = df_merged[["codigo_ibge","IDHM"]].dropna().copy()
df_final.columns = ["cod_municipio","idhm"]
df_final["faixa_idh"] = pd.cut(
    df_final["idhm"],
    bins=[0, 0.599, 0.699, 0.799, 1.0],
    labels=["Baixo","Médio","Alto","Muito Alto"]
)
df_final.to_parquet("data/epidemiologia/idhm_municipios.parquet", index=False)
print(f"\n4. Salvo: data/epidemiologia/idhm_municipios.parquet")

# 5. Cruza com dengue e mostra resultado
print("\n5. Cruzando com casos de dengue...")
con = duckdb.connect()
resultado = con.execute("""
    SELECT
        i.faixa_idh,
        COUNT(*) as casos,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as pct
    FROM read_parquet('data/epidemiologia/DENG_PEA.parquet') d
    JOIN read_parquet('data/epidemiologia/idhm_municipios.parquet') i
        ON CAST(d.ID_MUNICIP AS VARCHAR) = i.cod_municipio
    GROUP BY i.faixa_idh
    ORDER BY i.faixa_idh DESC
""").df()

print("\n=== CASOS DE DENGUE POR FAIXA DE IDH ===")
print(resultado.to_string(index=False))

# 6. Top municípios de IDH Muito Alto
print("\n=== TOP 10 MUNICÍPIOS IDH MUITO ALTO COM MAIS CASOS ===")
top = con.execute("""
    SELECT
        i.cod_municipio,
        i.idhm,
        COUNT(*) as casos
    FROM read_parquet('data/epidemiologia/DENG_PEA.parquet') d
    JOIN read_parquet('data/epidemiologia/idhm_municipios.parquet') i
        ON CAST(d.ID_MUNICIP AS VARCHAR) = i.cod_municipio
    WHERE i.faixa_idh = 'Muito Alto'
    GROUP BY i.cod_municipio, i.idhm
    ORDER BY casos DESC
    LIMIT 10
""").df()
print(top.to_string(index=False))

print("\n=== CONCLUÍDO ===")