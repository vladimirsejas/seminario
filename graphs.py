import duckdb
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

os.makedirs("data/graficos", exist_ok=True)

con = duckdb.connect()
PEA = "data/epidemiologia/DENG_PEA.parquet"
IDH = "data/epidemiologia/idhm_municipios.parquet"

# Paleta
CORES = {
    "Muito Alto": "#C0392B",
    "Alto":       "#E67E22",
    "Médio":      "#F1C40F",
    "Baixo":      "#27AE60",
}

print("Gerando gráficos...")

# ─────────────────────────────────────────────
# 1. CASOS POR FAIXA DE IDH
# ─────────────────────────────────────────────
df1 = con.execute(f"""
    SELECT i.faixa_idh, COUNT(*) as casos
    FROM read_parquet('{PEA}') d
    JOIN read_parquet('{IDH}') i ON CAST(d.ID_MUNICIP AS VARCHAR) = i.cod_municipio
    GROUP BY i.faixa_idh
    ORDER BY casos DESC
""").df()

fig, ax = plt.subplots(figsize=(9, 5))
cores = [CORES.get(f, "#95A5A6") for f in df1["faixa_idh"]]
bars = ax.barh(df1["faixa_idh"], df1["casos"], color=cores, edgecolor="white", height=0.6)
for bar, val in zip(bars, df1["casos"]):
    ax.text(bar.get_width() + 5000, bar.get_y() + bar.get_height()/2,
            f'{val:,.0f}', va='center', fontsize=10, fontweight='bold')
ax.set_title("Casos de Dengue por Faixa de IDH Municipal\nPopulação Economicamente Ativa (18–61 anos) — 2024",
             fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel("Número de Casos", fontsize=11)
ax.set_xlim(0, df1["casos"].max() * 1.2)
ax.spines[['top','right']].set_visible(False)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig("data/graficos/01_casos_por_idh.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ 01_casos_por_idh.png")

# ─────────────────────────────────────────────
# 2. TOP 10 MUNICÍPIOS IDH MUITO ALTO
# ─────────────────────────────────────────────
NOMES = {
    "355030": "São Paulo (SP)",
    "530010": "Brasília (DF)",
    "310620": "Belo Horizonte (MG)",
    "350950": "Campinas (SP)",
    "354990": "Ribeirão Preto (SP)",
    "420910": "Joinville (SC)",
    "420240": "Blumenau (SC)",
    "354340": "Santo André (SP)",
    "431490": "Porto Alegre (RS)",
    "355410": "São Bernardo (SP)",
    "330455": "Rio de Janeiro (RJ)",
}

df2 = con.execute(f"""
    SELECT i.cod_municipio, i.idhm, COUNT(*) as casos
    FROM read_parquet('{PEA}') d
    JOIN read_parquet('{IDH}') i ON CAST(d.ID_MUNICIP AS VARCHAR) = i.cod_municipio
    WHERE i.faixa_idh = 'Muito Alto'
    GROUP BY i.cod_municipio, i.idhm
    ORDER BY casos DESC
    LIMIT 10
""").df()

df2["nome"] = df2["cod_municipio"].map(NOMES).fillna(df2["cod_municipio"])

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(df2["nome"][::-1], df2["casos"][::-1], color="#C0392B", edgecolor="white", height=0.6)
for bar, val in zip(bars, df2["casos"][::-1]):
    ax.text(bar.get_width() + 2000, bar.get_y() + bar.get_height()/2,
            f'{val:,.0f}', va='center', fontsize=9, fontweight='bold')
ax.set_title("Top 10 Municípios de IDH Muito Alto com Mais Casos\nDengue na PEA (18–61 anos) — 2024",
             fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel("Número de Casos", fontsize=11)
ax.set_xlim(0, df2["casos"].max() * 1.25)
ax.spines[['top','right']].set_visible(False)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig("data/graficos/02_top_municipios_idh_alto.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ 02_top_municipios_idh_alto.png")

# ─────────────────────────────────────────────
# 3. SAZONALIDADE POR FAIXA DE IDH
# ─────────────────────────────────────────────
df3 = con.execute(f"""
    SELECT
        SUBSTR(CAST(d.DT_NOTIFIC AS VARCHAR), 5, 2) as mes,
        i.faixa_idh,
        COUNT(*) as casos
    FROM read_parquet('{PEA}') d
    JOIN read_parquet('{IDH}') i ON CAST(d.ID_MUNICIP AS VARCHAR) = i.cod_municipio
    WHERE SUBSTR(CAST(d.DT_NOTIFIC AS VARCHAR), 1, 4) = '2024'
    GROUP BY mes, i.faixa_idh
    ORDER BY mes
""").df()

MESES = {'01':'Jan','02':'Fev','03':'Mar','04':'Abr','05':'Mai','06':'Jun',
         '07':'Jul','08':'Ago','09':'Set','10':'Out','11':'Nov','12':'Dez'}

fig, ax = plt.subplots(figsize=(12, 6))
for faixa, cor in CORES.items():
    sub = df3[df3["faixa_idh"] == faixa].copy()
    if sub.empty:
        continue
    sub["mes_nome"] = sub["mes"].map(MESES)
    ax.plot(sub["mes_nome"], sub["casos"], marker='o', label=faixa, color=cor, linewidth=2.5, markersize=6)

ax.set_title("Sazonalidade da Dengue por Faixa de IDH — 2024\nPopulação Economicamente Ativa (18–61 anos)",
             fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel("Mês", fontsize=11)
ax.set_ylabel("Número de Casos", fontsize=11)
ax.legend(title="Faixa IDH", fontsize=10)
ax.spines[['top','right']].set_visible(False)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("data/graficos/03_sazonalidade_por_idh.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ 03_sazonalidade_por_idh.png")

# ─────────────────────────────────────────────
# 4. SEXO NOS MUNICÍPIOS DE IDH MUITO ALTO
# ─────────────────────────────────────────────
df4 = con.execute(f"""
    SELECT d.CS_SEXO as sexo, COUNT(*) as casos
    FROM read_parquet('{PEA}') d
    JOIN read_parquet('{IDH}') i ON CAST(d.ID_MUNICIP AS VARCHAR) = i.cod_municipio
    WHERE i.faixa_idh = 'Muito Alto'
    AND d.CS_SEXO IN ('M','F')
    GROUP BY d.CS_SEXO
""").df()

fig, ax = plt.subplots(figsize=(6, 6))
labels = df4["sexo"].map({"M": "Masculino", "F": "Feminino"})
ax.pie(df4["casos"], labels=labels, autopct='%1.1f%%',
       colors=["#2980B9","#E74C3C"], startangle=90,
       textprops={'fontsize': 12}, wedgeprops={'edgecolor':'white','linewidth':2})
ax.set_title("Distribuição por Sexo\nMunicípios IDH Muito Alto — Dengue PEA 2024",
             fontsize=12, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig("data/graficos/04_sexo_idh_alto.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ 04_sexo_idh_alto.png")

# ─────────────────────────────────────────────
# 5. FAIXA ETÁRIA NOS MUNICÍPIOS IDH MUITO ALTO
# ─────────────────────────────────────────────
df5 = con.execute(f"""
    SELECT
        CASE
            WHEN TRY_CAST(d.NU_IDADE_N AS INTEGER) BETWEEN 4018 AND 4025 THEN '18-25'
            WHEN TRY_CAST(d.NU_IDADE_N AS INTEGER) BETWEEN 4026 AND 4035 THEN '26-35'
            WHEN TRY_CAST(d.NU_IDADE_N AS INTEGER) BETWEEN 4036 AND 4045 THEN '36-45'
            WHEN TRY_CAST(d.NU_IDADE_N AS INTEGER) BETWEEN 4046 AND 4055 THEN '46-55'
            WHEN TRY_CAST(d.NU_IDADE_N AS INTEGER) BETWEEN 4056 AND 4061 THEN '56-61'
        END as faixa,
        COUNT(*) as casos
    FROM read_parquet('{PEA}') d
    JOIN read_parquet('{IDH}') i ON CAST(d.ID_MUNICIP AS VARCHAR) = i.cod_municipio
    WHERE i.faixa_idh = 'Muito Alto'
    GROUP BY faixa
    ORDER BY faixa
""").df().dropna()

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(df5["faixa"], df5["casos"], color="#C0392B", edgecolor="white", width=0.6)
for bar, val in zip(bars, df5["casos"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2000,
            f'{val:,.0f}', ha='center', fontsize=10, fontweight='bold')
ax.set_title("Casos por Faixa Etária — Municípios IDH Muito Alto\nDengue PEA 2024",
             fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel("Faixa Etária", fontsize=11)
ax.set_ylabel("Número de Casos", fontsize=11)
ax.spines[['top','right']].set_visible(False)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig("data/graficos/05_faixa_etaria_idh_alto.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ 05_faixa_etaria_idh_alto.png")

print("\nTodos os gráficos salvos em data/graficos/")