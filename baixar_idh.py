import urllib.request
import pandas as pd
import io

print("Baixando IDHM municipal...")

url = "https://raw.githubusercontent.com/tbrugz/geodata-br/master/ibge-municipios/municipios-2020.csv"

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=30) as r:
    conteudo = r.read().decode("utf-8")

df = pd.read_csv(io.StringIO(conteudo))
print(f"Linhas: {len(df)}")
print(f"Colunas: {list(df.columns)}")
print(df.head())