import streamlit as st
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np

st.set_page_config(page_title="Dengue & IDH", layout="wide", page_icon="🦟")

PEA = "data/epidemiologia/DENG_PEA.parquet"
IDH = "data/epidemiologia/idhm_municipios.parquet"

NOMES = {
    "355030": "São Paulo (SP)", "530010": "Brasília (DF)",
    "310620": "Belo Horizonte (MG)", "350950": "Campinas (SP)",
    "354990": "Ribeirão Preto (SP)", "420910": "Joinville (SC)",
    "420240": "Blumenau (SC)", "354340": "Santo André (SP)",
    "431490": "Porto Alegre (RS)", "355410": "São Bernardo (SP)",
    "330455": "Rio de Janeiro (RJ)", "292740": "Salvador (BA)",
    "261160": "Recife (PE)", "230440": "Fortaleza (CE)",
    "130260": "Manaus (AM)", "150140": "Belém (PA)",
}

@st.cache_data
def load_base():
    con = duckdb.connect()
    df = con.execute(f"""
        SELECT
            CAST(d.ID_MUNICIP AS VARCHAR) as cod_municipio,
            i.idhm,
            i.faixa_idh,
            COUNT(*) as casos,
            SUM(CASE WHEN d.CS_SEXO = 'F' THEN 1 ELSE 0 END) as casos_f,
            SUM(CASE WHEN d.CS_SEXO = 'M' THEN 1 ELSE 0 END) as casos_m,
            AVG(TRY_CAST(d.NU_IDADE_N AS INTEGER) - 4000) as idade_media
        FROM read_parquet('{PEA}') d
        JOIN read_parquet('{IDH}') i ON CAST(d.ID_MUNICIP AS VARCHAR) = i.cod_municipio
        GROUP BY CAST(d.ID_MUNICIP AS VARCHAR), i.idhm, i.faixa_idh
    """).df()
    df["nome"] = df["cod_municipio"].map(NOMES).fillna(df["cod_municipio"])
    df["pct_feminino"] = df["casos_f"] / df["casos"] * 100
    return df

@st.cache_data
def load_temporal():
    con = duckdb.connect()
    return con.execute(f"""
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

# ── HEADER ──────────────────────────────────────────────
st.title("🦟 Mineração Epidemiológica da Dengue")
st.markdown("**Padrões ocultos na população economicamente ativa (18–61 anos) — Brasil 2024**")
st.divider()

df = load_base()

# ── MÉTRICAS ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Casos (PEA)", f"{df['casos'].sum():,.0f}")
col2.metric("Municípios Analisados", f"{len(df):,.0f}")
col3.metric("Casos em IDH Alto/Muito Alto", f"{df[df['faixa_idh'].isin(['Alto','Muito Alto'])]['casos'].sum():,.0f}")
col4.metric("% em Municípios Ricos", f"{df[df['faixa_idh'].isin(['Alto','Muito Alto'])]['casos'].sum()/df['casos'].sum()*100:.1f}%")

st.divider()

# ── ABAS ─────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "🗺️ Municípios", "🔬 Clustering", "⚠️ Outliers"])

# ── ABA 1: VISÃO GERAL ───────────────────────────────────
with tab1:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Casos por Faixa de IDH")
        df_idh = df.groupby("faixa_idh")["casos"].sum().reset_index().sort_values("casos", ascending=True)
        CORES = {"Muito Alto":"#C0392B","Alto":"#E67E22","Médio":"#F1C40F","Baixo":"#27AE60"}
        fig, ax = plt.subplots(figsize=(7,4))
        cores = [CORES.get(f,"#95A5A6") for f in df_idh["faixa_idh"]]
        bars = ax.barh(df_idh["faixa_idh"], df_idh["casos"], color=cores, edgecolor="white")
        for bar, val in zip(bars, df_idh["casos"]):
            ax.text(bar.get_width()+5000, bar.get_y()+bar.get_height()/2, f'{val:,.0f}', va='center', fontsize=9, fontweight='bold')
        ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='x', alpha=0.3)
        st.pyplot(fig)
        plt.close()

    with col_b:
        st.subheader("Sazonalidade por Faixa de IDH")
        df_temp = load_temporal()
        MESES = {'01':'Jan','02':'Fev','03':'Mar','04':'Abr','05':'Mai','06':'Jun',
                 '07':'Jul','08':'Ago','09':'Set','10':'Out','11':'Nov','12':'Dez'}
        fig, ax = plt.subplots(figsize=(7,4))
        for faixa, cor in CORES.items():
            sub = df_temp[df_temp["faixa_idh"]==faixa].copy()
            if sub.empty: continue
            sub["mes_nome"] = sub["mes"].map(MESES)
            ax.plot(sub["mes_nome"], sub["casos"], marker='o', label=faixa, color=cor, linewidth=2)
        ax.legend(fontsize=8)
        ax.spines[['top','right']].set_visible(False)
        ax.grid(alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig)
        plt.close()

# ── ABA 2: MUNICÍPIOS ────────────────────────────────────
with tab2:
    st.subheader("Top Municípios por Faixa de IDH")
    faixa_sel = st.selectbox("Faixa de IDH", ["Muito Alto","Alto","Médio","Baixo"])
    n_top = st.slider("Quantidade de municípios", 5, 30, 10)

    df_top = df[df["faixa_idh"]==faixa_sel].nlargest(n_top, "casos")[["nome","idhm","casos","pct_feminino","idade_media"]]
    df_top.columns = ["Município","IDHM","Casos","% Feminino","Idade Média"]
    df_top["IDHM"] = df_top["IDHM"].round(3)
    df_top["% Feminino"] = df_top["% Feminino"].round(1)
    df_top["Idade Média"] = df_top["Idade Média"].round(1)
    st.dataframe(df_top, use_container_width=True, hide_index=True)

# ── ABA 3: CLUSTERING ────────────────────────────────────
with tab3:
    st.subheader("Clustering de Municípios por Perfil Epidemiológico")
    st.markdown("K-Means agrupa municípios com perfil semelhante de dengue.")

    n_clusters = st.slider("Número de clusters", 2, 6, 3)

    df_cluster = df[["casos","idhm","pct_feminino","idade_media"]].dropna().copy()
    idx = df_cluster.index

    scaler = StandardScaler()
    X = scaler.fit_transform(df_cluster)
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X)

    df_resultado = df.loc[idx].copy()
    df_resultado["cluster"] = labels

    st.markdown("**Dispersão: IDH vs Casos (por cluster)**")
    fig, ax = plt.subplots(figsize=(9,5))
    cores_cluster = plt.cm.tab10(np.linspace(0,1,n_clusters))
    for i in range(n_clusters):
        sub = df_resultado[df_resultado["cluster"]==i]
        ax.scatter(sub["idhm"], sub["casos"], label=f"Cluster {i}", alpha=0.7, s=40, color=cores_cluster[i])
    ax.set_xlabel("IDHM")
    ax.set_ylabel("Casos de Dengue")
    ax.legend()
    ax.spines[['top','right']].set_visible(False)
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    plt.close()

    st.markdown("**Perfil médio por cluster**")
    perfil = df_resultado.groupby("cluster")[["casos","idhm","pct_feminino","idade_media"]].mean().round(2)
    perfil.columns = ["Casos Médios","IDHM Médio","% Feminino","Idade Média"]
    st.dataframe(perfil, use_container_width=True)

# ── ABA 4: OUTLIERS ──────────────────────────────────────
with tab4:
    st.subheader("Outliers — Municípios Fora do Padrão")

    media_casos = df["casos"].mean()
    std_casos = df["casos"].std()

    df["z_casos"] = (df["casos"] - media_casos) / std_casos
    outliers = df[df["z_casos"].abs() > 2].sort_values("z_casos", ascending=False)

    st.markdown(f"Municípios com Z-score > 2 (fora de 2 desvios padrão): **{len(outliers)}**")

    col_x, col_y = st.columns(2)

    with col_x:
        st.markdown("**🔴 IDH Alto mas MUITOS casos (surto)**")
        surpresa_alta = outliers[outliers["faixa_idh"].isin(["Alto","Muito Alto"]) & (outliers["z_casos"] > 2)]
        if not surpresa_alta.empty:
            st.dataframe(surpresa_alta[["nome","idhm","casos","faixa_idh"]].rename(
                columns={"nome":"Município","idhm":"IDHM","casos":"Casos","faixa_idh":"Faixa IDH"}
            ), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum outlier nessa categoria.")

    with col_y:
        st.markdown("**🟢 IDH Baixo mas muitos casos (vulnerabilidade)**")
        surpresa_baixa = outliers[outliers["faixa_idh"].isin(["Baixo","Médio"]) & (outliers["z_casos"] > 2)]
        if not surpresa_baixa.empty:
            st.dataframe(surpresa_baixa[["nome","idhm","casos","faixa_idh"]].rename(
                columns={"nome":"Município","idhm":"IDHM","casos":"Casos","faixa_idh":"Faixa IDH"}
            ), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum outlier nessa categoria.")

    st.markdown("**Todos os outliers**")
    st.dataframe(outliers[["nome","idhm","casos","faixa_idh","z_casos"]].rename(
        columns={"nome":"Município","idhm":"IDHM","casos":"Casos","faixa_idh":"Faixa IDH","z_casos":"Z-Score"}
    ).head(20), use_container_width=True, hide_index=True)