"""
dashboard_show.py - versao 2 (show) do dashboard. O original continua em dashboard.py.

Mesmos dados e mesmas consultas do original. Muda a apresentacao:
  - os numeros do topo contam ate o valor final quando a pagina abre;
  - Pergunta -> Metodo -> Resultado e "O que encontramos?";
  - graficos interativos (Plotly): passe o mouse para ver os detalhes;
  - a sazonalidade ganha um botao de play;
  - o K-Means roda passo a passo na frente da turma;
  - os outliers aparecem com efeito "detetive";
  - vida o tempo todo: pontos de luz no fundo, um mosquito voando, letreiro de achados;
  - abertura animada (barras crescem, linha se desenha) e o botao "Reproduzir abertura";
  - a constelacao viva: cada municipio e um ponto que respira com a sazonalidade real.

Abrir: dois cliques em "Abrir Dashboard Show.bat"
"""

import time

import duckdb
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.cluster import kmeans_plusplus
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Dengue & IDH | Show", layout="wide", page_icon="🦟")

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

ORDEM = ["Baixo", "Médio", "Alto", "Muito Alto"]
CORES = {"Muito Alto": "#C0392B", "Alto": "#E67E22", "Médio": "#F1C40F", "Baixo": "#27AE60"}   # as do original
MESES = {"01": "Jan", "02": "Fev", "03": "Mar", "04": "Abr", "05": "Mai", "06": "Jun",
         "07": "Jul", "08": "Ago", "09": "Set", "10": "Out", "11": "Nov", "12": "Dez"}
CORES_GRUPOS = ["#2980B9", "#E84393", "#27AE60", "#E67E22", "#8E44AD", "#C0392B"]
CINZA = "rgba(110,120,135,0.40)"
CONFIG = {"displayModeBar": False}


# ── DADOS (as mesmas consultas do dashboard.py) ─────────────
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


# ── AJUDANTES ──────────────────────────────────────────────
def br(valor, casas=0):
    """4412090 -> '4.412.090' | 84.83 -> '84,8' (formato brasileiro)."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def estilo(fig, altura=420):
    fig.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", height=altura, separators=",.",
                      margin=dict(l=10, r=10, t=40, b=10), font=dict(size=14),
                      hoverlabel=dict(font_size=15), showlegend=True)
    return fig


def mostrar(fig, onde=None, key=None):
    (onde or st).plotly_chart(fig, use_container_width=True, config=CONFIG, key=key)


def achado(texto, nota=None):
    html = f'<div class="achado">🔎 <b>O que encontramos?</b><br>{texto}'
    if nota:
        html += f'<div class="nota">{nota}</div>'
    st.markdown(html + "</div>", unsafe_allow_html=True)


st.markdown("""
<style>
.cartao {border: 1px solid rgba(0,0,0,.08); border-radius: 14px; padding: 16px 20px; height: 100%;
         background: #ffffff; box-shadow: 0 6px 18px rgba(0,0,0,.06);}
.cartao h4 {margin: 0 0 8px 0; font-size: .78rem; letter-spacing: .14em; text-transform: uppercase;
            color: #2980B9;}
.cartao p {margin: 0; font-size: 1.02rem; line-height: 1.45;}
.achado {border-left: 5px solid #FF9F2E; padding: 14px 20px; margin: 8px 0 14px 0;
         background: rgba(230,126,34,.10); border-radius: 10px; font-size: 1.08rem;}
.nota {color: #5f6b7a; font-size: .88rem; margin-top: 6px;}
div[data-testid="stMetricValue"] {font-size: 2.6rem;}

/* pontos de luz flutuando no fundo, como mosquitos (so CSS: funciona sem internet) */
.stApp::before {content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0; opacity: .7;
    background-image:
        radial-gradient(3px 3px at 20% 30%, rgba(41,128,185,.55), transparent 60%),
        radial-gradient(2.5px 2.5px at 70% 65%, rgba(230,126,34,.55), transparent 60%),
        radial-gradient(3px 3px at 45% 85%, rgba(39,174,96,.5), transparent 60%),
        radial-gradient(2.5px 2.5px at 85% 15%, rgba(192,57,43,.5), transparent 60%);
    background-size: 310px 310px, 430px 430px, 530px 530px, 370px 370px;
    animation: deriva 70s linear infinite;}
@keyframes deriva {to {background-position: 620px 930px, -860px 430px, 530px -1060px, -740px -370px;}}
.block-container {position: relative; z-index: 1;}

/* cabecalho: titulo com brilho passando, mosquito voando, ponto AO VIVO */
.topo {position: relative; padding: 18px 0 6px 0; overflow: hidden;}
.titulo {font-size: 2.9rem; font-weight: 800; margin: 0; line-height: 1.15;
    background: linear-gradient(90deg, #C0392B, #E67E22, #D4AC0D, #27AE60, #2980B9, #8E44AD, #C0392B);
    background-size: 300% auto; -webkit-background-clip: text; background-clip: text;
    color: transparent !important; -webkit-text-fill-color: transparent;   /* o Streamlit forca a cor do h1 */
    animation: brilho 9s linear infinite;}
@keyframes brilho {from {background-position: 0% center;} to {background-position: 300% center;}}
.mosquito {position: absolute; top: 4px; left: 0; font-size: 1.9rem; animation: voo 16s ease-in-out infinite;}
@keyframes voo {
    0% {transform: translate(-60px, 30px) rotate(10deg);}   25% {transform: translate(32vw, -2px) rotate(-12deg);}
    50% {transform: translate(64vw, 40px) rotate(14deg);}   75% {transform: translate(34vw, 10px) rotate(-170deg);}
    100% {transform: translate(-60px, 30px) rotate(10deg);}}
.sub {color: #3d4752; font-size: 1.02rem; margin-top: 6px;}
.aovivo {display: inline-block; color: #ff4d4d; margin-right: 6px; animation: pulso 1.4s ease-in-out infinite;}
@keyframes pulso {0%, 100% {opacity: 1; transform: scale(1);} 50% {opacity: .25; transform: scale(.7);}}

/* letreiro com os achados, correndo devagar */
.letreiro {overflow: hidden; white-space: nowrap; border-radius: 10px; padding: 9px 0; margin: 10px 0 4px 0;
    background: linear-gradient(90deg, rgba(230,126,34,.12), rgba(41,128,185,.12)); color: #8a4b08; font-weight: 600;}
.letreiro span {display: inline-block; padding-left: 100%; animation: correr 38s linear infinite;}
@keyframes correr {to {transform: translateX(-100%);}}

/* os quatro numeros com um brilho que respira */
div[data-testid="stMetric"] {border: 1px solid rgba(41,128,185,.22); border-radius: 14px; padding: 12px 16px;
    background: #ffffff; animation: respira 4s ease-in-out infinite;}
@keyframes respira {0%, 100% {box-shadow: 0 2px 8px rgba(41,128,185,.08);} 50% {box-shadow: 0 6px 26px rgba(41,128,185,.30);}}
div[data-testid="stMetricValue"] {color: #1b4f72;}
</style>
""", unsafe_allow_html=True)


# ── CABECALHO ──────────────────────────────────────────────
st.markdown('<div class="topo"><span class="mosquito">🦟</span>'
            '<h1 class="titulo">Mineração Epidemiológica da Dengue</h1>'
            '<div class="sub"><span class="aovivo">●</span><b>AO VIVO</b> · Padrões ocultos na população '
            'economicamente ativa (18–61 anos) — Brasil 2024</div></div>', unsafe_allow_html=True)

df = load_base()
temporal = load_temporal()
ricos = df[df["faixa_idh"].isin(["Alto", "Muito Alto"])]["casos"].sum()
total = df["casos"].sum()
pct_ricos = ricos / total * 100

NUMEROS = [("Total de Casos (PEA)", total, lambda v: br(v)),
           ("Municípios Analisados", len(df), lambda v: br(v)),
           ("Casos em IDH Alto/Muito Alto", ricos, lambda v: br(v)),
           ("% em Municípios Ricos", pct_ricos, lambda v: br(v, 1) + "%")]

# Os numeros contam so na primeira abertura. Nas proximas (o Streamlit roda a pagina
# de novo a cada clique), aparecem direto no valor final.
reproduzir = st.button("🎬  Reproduzir abertura", help="Repete a animação de abertura: números e gráficos")
lugares = [coluna.empty() for coluna in st.columns(4)]
ja_contou = st.session_state.get("ja_contou", False) and not reproduzir
for lugar, (rotulo, valor, formato) in zip(lugares, NUMEROS):
    lugar.metric(rotulo, formato(valor if ja_contou else 0))

st.divider()

# ── A CONSTELACAO VIVA (desenhada no navegador, sem internet) ──
CONSTELACAO_HTML = """
<div id="caixa" style="position:relative;border-radius:18px;overflow:hidden;
     background:radial-gradient(ellipse at 30% 20%,#ffffff 0%,#eef6fc 55%,#e3eef8 100%);
     box-shadow:0 10px 30px rgba(41,128,185,.18);font-family:'Source Sans Pro',sans-serif">
  <canvas id="tela" style="display:block;width:100%;height:__ALTURA__px"></canvas>
</div>
<script>
const D = __DADOS__;
const cv = document.getElementById('tela'), ctx = cv.getContext('2d');
let W = 0, H = __ALTURA__, dpr = Math.min(window.devicePixelRatio || 1, 2);
function medir() { W = cv.clientWidth; cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
medir(); window.addEventListener('resize', medir);

const M = {l: 70, r: 40, t: 70, b: 92};
const [i0, i1] = [Math.min(...D.idhm) - 0.01, Math.max(...D.idhm) + 0.01];
const lc = D.casos.map(c => Math.log10(Math.max(c, 1)));
const [c0, c1] = [Math.min(...lc), Math.max(...lc) + 0.15];
const cmax = Math.max(...D.casos);
const pontos = D.idhm.map((v, k) => ({
  u: (v - i0) / (i1 - i0), w: (lc[k] - c0) / (c1 - c0), f: D.faixa[k], c: D.casos[k], n: D.nome[k],
  r: 2.0 + 4.0 * Math.sqrt(D.casos[k] / cmax), fase: Math.random() * 6.28, ativ: 0, x: 0, y: 0}));
const surtos = pontos.map((p, k) => k).sort((a, b) => pontos[b].c - pontos[a].c).slice(0, 60);
const aneis = [];
let mouse = null, tempoMouse = -99;
cv.addEventListener('mousemove', e => { const b = cv.getBoundingClientRect(); mouse = {x: e.clientX - b.left, y: e.clientY - b.top}; tempoMouse = performance.now() / 1000; });
cv.addEventListener('mouseleave', () => { mouse = null; });

function rgba(hex, a) { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; }
function fmt(n) { return Math.round(n).toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, '.'); }
let ultimoSurto = 0;

function quadro(ms) {
  const t = ms / 1000;
  ctx.clearRect(0, 0, W, H);
  // o relogio do ano: 1,4 s por mes, sem parar
  const pos = (t / 1.4) % D.meses.length, m = Math.floor(pos), frac = pos - m, m2 = (m + 1) % D.meses.length;
  const forca = D.series.map(s => s[m] * (1 - frac) + s[m2] * frac);
  // a lente: o mouse, ou passeando sozinha quando o mouse nao esta no painel
  const autoLente = !mouse || t - tempoMouse > 6;
  const lente = autoLente ? {x: M.l + (W - M.l - M.r) * (0.5 + 0.42 * Math.sin(t * 0.23)),
                             y: M.t + (H - M.t - M.b) * (0.45 + 0.35 * Math.sin(t * 0.37 + 1))} : mouse;
  const R = 105;
  // eixos discretos
  ctx.strokeStyle = 'rgba(27,79,114,.18)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(M.l, H - M.b); ctx.lineTo(W - M.r, H - M.b); ctx.moveTo(M.l, M.t - 10); ctx.lineTo(M.l, H - M.b); ctx.stroke();
  ctx.fillStyle = 'rgba(27,79,114,.55)'; ctx.font = '13px sans-serif';
  ctx.fillText('IDHM →', W - M.r - 52, H - M.b + 20); ctx.save(); ctx.translate(M.l - 18, M.t + 120); ctx.rotate(-Math.PI / 2); ctx.fillText('casos (escala log) →', 0, 0); ctx.restore();
  // os pontos
  const perto = [];
  for (const p of pontos) {
    p.x = M.l + p.u * (W - M.l - M.r) + Math.sin(t * 0.6 + p.fase) * 1.6;
    p.y = H - M.b - p.w * (H - M.t - M.b) + Math.cos(t * 0.5 + p.fase) * 1.6;
    const d = Math.hypot(p.x - lente.x, p.y - lente.y);
    const alvo = d < R ? 1 - d / R : 0;
    p.ativ += (alvo - p.ativ) * 0.12;                         // acende e apaga devagar
    if (d < R) perto.push([d, p]);
    const pulso = 0.7 + 1.1 * forca[p.f];                    // a sazonalidade real fazendo o ponto respirar
    const raio = p.r * pulso * (1 + 1.6 * p.ativ) + 0.4 * Math.sin(t * 2 + p.fase);
    ctx.fillStyle = rgba(D.cores[p.f], 0.42 + 0.4 * forca[p.f] + 0.18 * p.ativ);
    ctx.beginPath(); ctx.arc(p.x, p.y, Math.max(raio, 0.8), 0, 6.283); ctx.fill();
  }
  // surtos: aneis que se expandem a partir das cidades com mais casos
  if (t - ultimoSurto > 1.6) {
    ultimoSurto = t; const p = pontos[surtos[Math.floor(Math.random() * surtos.length)]];
    aneis.push({p, t0: t});
  }
  for (let k = aneis.length - 1; k >= 0; k--) {
    const a = aneis[k], idade = t - a.t0; if (idade > 2.2) { aneis.splice(k, 1); continue; }
    ctx.strokeStyle = rgba(D.cores[a.p.f], 0.7 * (1 - idade / 2.2)); ctx.lineWidth = 2.5;
    ctx.beginPath(); ctx.arc(a.p.x, a.p.y, 6 + idade * 38, 0, 6.283); ctx.stroke();
  }
  // a lente: anel, linhas ate os vizinhos e a etiqueta do municipio mais proximo
  perto.sort((a, b) => a[0] - b[0]);
  ctx.strokeStyle = 'rgba(41,128,185,.55)'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.arc(lente.x, lente.y, R, 0, 6.283); ctx.stroke();
  ctx.strokeStyle = 'rgba(41,128,185,.28)'; ctx.lineWidth = 1;
  for (const [, p] of perto.slice(0, 10)) { ctx.beginPath(); ctx.moveTo(lente.x, lente.y); ctx.lineTo(p.x, p.y); ctx.stroke(); }
  if (perto.length) {
    const p = perto.reduce((a, b) => (b[1].c > a[1].c ? b : a))[1];      // o de mais casos dentro da lente
    const txt = `${p.n}  ·  ${fmt(p.c)} casos  ·  IDHM ${D.idhmTxt[pontos.indexOf(p)]}`;
    ctx.font = 'bold 14px sans-serif'; const lw = ctx.measureText(txt).width + 22;
    const bx = Math.min(Math.max(p.x - lw / 2, 8), W - lw - 8), by = Math.max(p.y - 46, 8);
    ctx.fillStyle = 'rgba(255,255,255,.95)'; ctx.strokeStyle = rgba(D.cores[p.f], .9); ctx.lineWidth = 2;
    ctx.beginPath(); ctx.roundRect(bx, by, lw, 28, 9); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#1b2631'; ctx.fillText(txt, bx + 11, by + 19);
    ctx.strokeStyle = rgba(D.cores[p.f], .9); ctx.beginPath(); ctx.arc(p.x, p.y, 9, 0, 6.283); ctx.stroke();
  }
  // titulo e o relogio do ano
  ctx.fillStyle = '#1b4f72'; ctx.font = 'bold 20px sans-serif';
  ctx.fillText(`Os ${fmt(pontos.length)} municípios, ao vivo`, 22, 34);
  ctx.fillStyle = 'rgba(27,79,114,.65)'; ctx.font = '14px sans-serif';
  ctx.fillText(autoLente ? 'passe o mouse para investigar uma cidade' : 'investigando...', 22, 54);
  ctx.textAlign = 'right'; ctx.fillStyle = rgba('#C0392B', 0.85); ctx.font = 'bold 44px sans-serif';
  ctx.fillText(D.nomesMeses[m].toUpperCase(), W - 30, 52); ctx.textAlign = 'left';
  const bx0 = M.l, bw = W - M.l - M.r, by0 = H - 46, passo = bw / D.meses.length;
  D.total.forEach((v, k) => {
    const h = 6 + 26 * v; ctx.fillStyle = k === m ? 'rgba(192,57,43,.85)' : 'rgba(41,128,185,.28)';
    ctx.fillRect(bx0 + k * passo + 4, by0 + 30 - h, passo - 8, h);
    ctx.fillStyle = k === m ? '#C0392B' : 'rgba(27,79,114,.6)'; ctx.font = (k === m ? 'bold ' : '') + '12px sans-serif';
    ctx.fillText(D.nomesMeses[k], bx0 + k * passo + passo / 2 - 10, by0 + 44);
  });
  ctx.fillStyle = 'rgba(192,57,43,.9)';
  ctx.beginPath(); ctx.arc(bx0 + ((pos + 0.5) % D.meses.length) * passo, by0 - 4, 5, 0, 6.283); ctx.fill();
  requestAnimationFrame(quadro);
}
requestAnimationFrame(quadro);
</script>
"""


def constelacao(df, temporal, altura=470):
    """Monta o painel vivo: cada municipio e um ponto; a sazonalidade real faz os pontos respirarem."""
    import json
    import streamlit.components.v1 as components
    base = df.dropna(subset=["idhm"])
    indice = {f: k for k, f in enumerate(ORDEM)}
    meses = sorted(temporal["mes"].dropna().unique())
    series = []
    for faixa in ORDEM:
        s = temporal[temporal["faixa_idh"] == faixa].set_index("mes")["casos"].reindex(meses).fillna(0)
        series.append([round(float(v), 4) for v in (s / s.max() if s.max() else s)])
    total = temporal.groupby("mes")["casos"].sum().reindex(meses).fillna(0)
    dados = {
        "idhm": [round(float(v), 4) for v in base["idhm"]],
        "idhmTxt": [f"{v:.3f}".replace(".", ",") for v in base["idhm"]],
        "casos": [int(v) for v in base["casos"]],
        "faixa": [indice.get(f, 0) for f in base["faixa_idh"]],
        "nome": [str(n) for n in base["nome"]],
        "cores": [CORES[f] for f in ORDEM],
        "meses": meses, "nomesMeses": [MESES.get(m, m) for m in meses],
        "series": series, "total": [round(float(v), 4) for v in (total / total.max())],
    }
    html = (CONSTELACAO_HTML.replace("__DADOS__", json.dumps(dados, ensure_ascii=False))
            .replace("__ALTURA__", str(altura)))
    components.html(html, height=altura + 8)


constelacao(df, temporal)
st.caption("Cada ponto é um município (dados reais). O relógio percorre o ano: os pontos crescem com os "
           "casos de cada mês. Os anéis marcam as cidades com mais casos. Passe o mouse para investigar.")


# ── PERGUNTA -> METODO -> RESULTADO ────────────────────────
c1, c2, c3 = st.columns(3)
c1.markdown('<div class="cartao"><h4>❓ Pergunta</h4><p>Onde se concentram os casos de dengue '
            'quando olhamos o IDHM dos municípios?</p></div>', unsafe_allow_html=True)
c2.markdown('<div class="cartao"><h4>⚙️ Método</h4><p>DuckDB cruza a base do SINAN com o IDHM → '
            'análise exploratória → K-Means (grupos) → Z-score (anomalias)</p></div>',
            unsafe_allow_html=True)
c3.markdown(f'<div class="cartao"><h4>✅ Resultado</h4><p><b>{br(pct_ricos, 1)}%</b> dos casos '
            'estão em municípios de IDH Alto ou Muito Alto.</p></div>', unsafe_allow_html=True)

pico_geral = temporal.groupby("mes")["casos"].sum().idxmax()
ACHADOS = [f"🔎 {br(pct_ricos, 1)}% dos casos em municípios de IDH Alto ou Muito Alto",
           f"📍 {br(len(df))} municípios analisados",
           f"🦟 {br(total)} casos na população de 18 a 61 anos",
           f"📅 o pico da epidemia acontece em {MESES.get(pico_geral, pico_geral)}",
           "🔬 K-Means encontra grupos sozinho — veja na aba Clustering",
           "⚠️ Z-score revela os municípios fora do padrão — veja na aba Outliers"]
st.markdown('<div class="letreiro"><span>' + " &nbsp;&nbsp;•&nbsp;&nbsp; ".join(ACHADOS) + "</span></div>",
            unsafe_allow_html=True)

st.write("")
quanto = f"{br(ricos / 1e6, 2)} milhões de casos" if ricos >= 1e6 else f"{br(ricos)} casos"
achado(f"<b>{quanto}</b> se concentram em municípios de IDH Alto ou "
       f"Muito Alto — <b>{br(pct_ricos, 1)}%</b> do total analisado.",
       "Atenção: são casos absolutos. Municípios de IDH alto costumam ser os mais populosos; "
       "para comparar o risco, o ideal é a taxa por 100 mil habitantes.")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "🗺️ Municípios", "🔬 Clustering", "⚠️ Outliers"])

# ── ABA 1: VISAO GERAL ─────────────────────────────────────
with tab1:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Casos por Faixa de IDH")
        por_faixa = df.groupby("faixa_idh")["casos"].sum().reindex(ORDEM).dropna()

        def barras(fracao=1.0):
            valores = por_faixa.values * fracao
            fig = go.Figure(go.Bar(
                x=valores, y=por_faixa.index, orientation="h",
                marker=dict(color=[CORES[f] for f in por_faixa.index], line=dict(width=0)),
                text=[br(v) for v in valores], textposition="outside",
                customdata=por_faixa.values / total * 100,
                hovertemplate="<b>IDH %{y}</b><br>%{x:,.0f} casos<br>%{customdata:.1f}% do total<extra></extra>"))
            fig.update_xaxes(range=[0, por_faixa.max() * 1.25], showgrid=True, gridcolor="rgba(0,0,0,.08)")
            fig.update_yaxes(type="category")
            return estilo(fig).update_layout(showlegend=False)

        lugar_barras = st.empty()
        mostrar(barras(1.0 if ja_contou else 0.0), lugar_barras, key="barras_inicio")
        lider = por_faixa.idxmax()
        st.caption(f"Passe o mouse nas barras. A faixa com mais casos é **{lider}** "
                   f"({br(por_faixa.max() / total * 100, 1)}% do total).")

    with col_b:
        st.subheader("Sazonalidade por Faixa de IDH")
        meses = sorted(temporal["mes"].dropna().unique())
        nomes_meses = [MESES.get(m, m) for m in meses]
        series = {f: temporal[temporal["faixa_idh"] == f].set_index("mes")["casos"].reindex(meses)
                  for f in ORDEM if f in set(temporal["faixa_idh"])}

        def linhas(ate):
            return [go.Scatter(x=nomes_meses[:ate], y=s.values[:ate], name=f, mode="lines+markers",
                               line=dict(color=CORES[f], width=3), marker=dict(size=8),
                               hovertemplate=f"<b>{f}</b><br>%{{x}}: %{{y:,.0f}} casos<extra></extra>")
                    for f, s in series.items()]

        maior = max(s.max() for s in series.values())

        def sazonalidade(ate):
            fig = go.Figure(data=linhas(ate),
                            frames=[go.Frame(data=linhas(k), name=str(k)) for k in range(1, len(meses) + 1)])
            fig.update_xaxes(categoryorder="array", categoryarray=nomes_meses, range=[-0.5, len(meses) - 0.5])
            fig.update_yaxes(range=[0, maior * 1.12], gridcolor="rgba(0,0,0,.08)")
            fig.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.12),
                              updatemenus=[dict(type="buttons", x=0, y=-0.12, xanchor="left", showactive=False,
                                                buttons=[dict(label="▶  Animar o ano", method="animate",
                                                              args=[None, dict(frame=dict(duration=260, redraw=True),
                                                                               transition=dict(duration=200),
                                                                               fromcurrent=False, mode="immediate")])])])
            return estilo(fig, 450)

        lugar_linhas = st.empty()
        mostrar(sazonalidade(len(meses) if ja_contou else 1), lugar_linhas, key="linhas_inicio")
        pico = pico_geral
        st.caption(f"Aperte **▶ Animar o ano** e veja a epidemia crescer. O pico acontece em "
                   f"**{MESES.get(pico, pico)}**.")

# ── ABA 2: MUNICIPIOS ──────────────────────────────────────
with tab2:
    st.subheader("Top Municípios por Faixa de IDH")
    faixa_sel = st.selectbox("Faixa de IDH", ["Muito Alto", "Alto", "Médio", "Baixo"])
    n_top = st.slider("Quantidade de municípios", 5, 30, 10)

    top = df[df["faixa_idh"] == faixa_sel].nlargest(n_top, "casos").iloc[::-1]
    fig = go.Figure(go.Bar(
        x=top["casos"], y=top["nome"], orientation="h", marker_color=CORES[faixa_sel],
        text=[br(v) for v in top["casos"]], textposition="outside",
        customdata=np.column_stack([top["idhm"], top["pct_feminino"], top["idade_media"]]),
        hovertemplate=("<b>%{y}</b><br>%{x:,.0f} casos<br>IDHM %{customdata[0]:.3f}<br>"
                       "%{customdata[1]:.1f}% mulheres · idade média %{customdata[2]:.1f}<extra></extra>")))
    fig.update_xaxes(range=[0, top["casos"].max() * 1.2], gridcolor="rgba(0,0,0,.08)")
    fig.update_yaxes(type="category")
    mostrar(estilo(fig, max(320, 34 * len(top))).update_layout(showlegend=False))

    tabela = top.iloc[::-1][["nome", "idhm", "casos", "pct_feminino", "idade_media"]]
    tabela.columns = ["Município", "IDHM", "Casos", "% Feminino", "Idade Média"]
    st.dataframe(tabela.round({"IDHM": 3, "% Feminino": 1, "Idade Média": 1}),
                 use_container_width=True, hide_index=True)

# ── ABA 3: CLUSTERING ──────────────────────────────────────
@st.cache_data
def kmeans_passo_a_passo(X, n, max_passos=30):
    """K-Means (algoritmo de Lloyd) guardando cada passo: escolhe centros, agrupa, move os centros..."""
    centros = kmeans_plusplus(X, n, random_state=42)[0]
    passos = []
    for _ in range(max_passos):
        distancias = ((X[:, None, :] - centros[None, :, :]) ** 2).sum(axis=2)
        grupos = distancias.argmin(axis=1)
        passos.append((grupos, centros.copy()))
        novos = np.array([X[grupos == k].mean(axis=0) if (grupos == k).any() else centros[k]
                          for k in range(n)])
        if np.allclose(novos, centros):
            break
        centros = novos
    return passos


def grafico_grupos(base, grupos=None, centros=None, titulo=""):
    fig = go.Figure()
    if grupos is None:
        fig.add_trace(go.Scatter(x=base["idhm"], y=base["casos"], mode="markers", name="Municípios",
                                   marker=dict(color=CINZA, size=6), text=base["nome"],
                                   hovertemplate="<b>%{text}</b><br>IDHM %{x:.3f}<br>%{y:,.0f} casos<extra></extra>"))
    else:
        for k in range(int(grupos.max()) + 1):
            sub = base[grupos == k]
            fig.add_trace(go.Scatter(x=sub["idhm"], y=sub["casos"], mode="markers", name=f"Grupo {k + 1}",
                                       marker=dict(color=CORES_GRUPOS[k], size=7, opacity=0.8),
                                       text=sub["nome"],
                                       hovertemplate=f"<b>%{{text}}</b><br>Grupo {k + 1}<br>IDHM %{{x:.3f}}"
                                                     "<br>%{y:,.0f} casos<extra></extra>"))
        if centros is not None:
            fig.add_trace(go.Scatter(x=centros[:, 0], y=np.maximum(centros[:, 1], 1), mode="markers",
                                     name="Centros", hoverinfo="skip",
                                     marker=dict(symbol="x", size=22, color=CORES_GRUPOS[:len(centros)],
                                                 line=dict(width=3, color="#1b1f24"))))
    fig.update_xaxes(title="IDHM", range=[base["idhm"].min() - 0.02, base["idhm"].max() + 0.02],
                     gridcolor="rgba(0,0,0,.08)")
    fig.update_yaxes(title="Casos de dengue (escala log)", type="log", gridcolor="rgba(0,0,0,.08)")
    return estilo(fig, 520).update_layout(title=titulo, legend=dict(orientation="h", y=-0.15))


def nome_do_grupo(linha, ordem_casos):
    if linha["idhm"] < 0.6:
        nivel = "IDH baixo"
    elif linha["idhm"] < 0.7:
        nivel = "IDH médio"
    elif linha["idhm"] < 0.8:
        nivel = "IDH alto"
    else:
        nivel = "IDH muito alto"
    posicao = ordem_casos[linha.name]
    if posicao == 0:
        casos = "mais casos"
    elif posicao == len(ordem_casos) - 1:
        casos = "menos casos"
    else:
        casos = "casos intermediários"
    return f"{nivel} · {casos}"


with tab3:
    st.subheader("Encontrar grupos sem dizer ao algoritmo quais são os grupos")
    st.markdown("O **K-Means** recebe os municípios (casos, IDHM, % de mulheres e idade média) e "
                "**ninguém diz a ele quais são os grupos**. Ele escolhe centros, junta cada município "
                "ao centro mais próximo, move os centros e repete — até nada mais mudar.")

    n_grupos = st.slider("Número de grupos", 2, 6, 3)
    dados_grupo = df[["casos", "idhm", "pct_feminino", "idade_media"]].dropna()
    base_grupo = df.loc[dados_grupo.index]
    escala = StandardScaler().fit(dados_grupo)
    passos = kmeans_passo_a_passo(escala.transform(dados_grupo), n_grupos)

    def centros_reais(centros):
        return escala.inverse_transform(centros)[:, [1, 0]]      # colunas (idhm, casos) para o grafico

    executar = st.button("▶  Executar agrupamento", type="primary")
    if st.session_state.get("grupos_prontos") != n_grupos:
        st.session_state["grupos_prontos"] = None
    lugar_grafico = st.empty()
    lugar_texto = st.empty()

    if executar:
        for i, (grupos, centros) in enumerate(passos, start=1):
            mostrar(grafico_grupos(base_grupo, grupos, centros_reais(centros),
                                   f"Passo {i} de {len(passos)}: agrupando e movendo os centros..."),
                    lugar_grafico, key=f"passo_{n_grupos}_{i}")
            time.sleep(0.6 if i < 4 else 0.25)      # devagar no comeco, depois acelera
        st.session_state["grupos_prontos"] = n_grupos

    if st.session_state.get("grupos_prontos") == n_grupos:
        grupos, centros = passos[-1]
        mostrar(grafico_grupos(base_grupo, grupos, centros_reais(centros),
                               f"Pronto: o algoritmo parou de mudar em {len(passos)} passos"),
                lugar_grafico, key=f"final_{n_grupos}")
        lugar_texto.success(f"Ninguém disse ao algoritmo onde estavam os grupos: ele encontrou "
                            f"{n_grupos} perfis sozinho, em {len(passos)} passos.")

        perfil = base_grupo.assign(grupo=grupos).groupby("grupo").agg(
            municipios=("casos", "size"), casos=("casos", "mean"), idhm=("idhm", "mean"),
            pct_feminino=("pct_feminino", "mean"), idade_media=("idade_media", "mean"))
        ordem_casos = {g: i for i, g in enumerate(perfil["casos"].sort_values(ascending=False).index)}
        perfil.insert(0, "descricao", perfil.apply(nome_do_grupo, axis=1, ordem_casos=ordem_casos))
        perfil.index = [f"Grupo {g + 1}" for g in perfil.index]
        perfil.columns = ["Perfil", "Municípios", "Casos Médios", "IDHM Médio", "% Feminino", "Idade Média"]
        st.markdown("**Perfil médio de cada grupo**")
        st.dataframe(perfil.round({"Casos Médios": 1, "IDHM Médio": 3, "% Feminino": 1, "Idade Média": 1}),
                     use_container_width=True)
    elif not executar:
        mostrar(grafico_grupos(base_grupo, titulo="Antes: todos os municípios, sem grupos"),
                lugar_grafico, key="antes_grupos")
        lugar_texto.info("Aperte **▶ Executar agrupamento** e veja os grupos se formando.")

# ── ABA 4: OUTLIERS ────────────────────────────────────────
def grafico_outliers(base, achados, limite, titulo):
    normais = base.drop(achados.index)
    fig = go.Figure(go.Scatter(x=normais["idhm"], y=normais["casos"], mode="markers", name="Dentro do padrão",
                                 marker=dict(color=CINZA, size=6), text=normais["nome"],
                                 hovertemplate="<b>%{text}</b><br>IDHM %{x:.3f}<br>%{y:,.0f} casos<extra></extra>"))
    if limite is not None:
        fig.add_hline(y=limite, line=dict(color="#E67E22", dash="dash", width=2),
                      annotation_text="limite: 2 desvios-padrão acima da média", annotation_font_color="#B9570F")
    if len(achados):
        fig.add_trace(go.Scatter(x=achados["idhm"], y=achados["casos"], mode="markers", name="Fora do padrão",
                                 marker=dict(color="#E74C3C", size=14, line=dict(width=2, color="#7B241C")),
                                 text=achados["nome"], customdata=achados["z_casos"],
                                 hovertemplate="<b>%{text}</b><br>IDHM %{x:.3f}<br>%{y:,.0f} casos"
                                               "<br>Z-score %{customdata:.1f}<extra></extra>"))
        for i, (_, linha) in enumerate(achados.head(5).iterrows()):      # os 5 maiores, com setas desencontradas
            fig.add_annotation(x=linha["idhm"], y=np.log10(linha["casos"]), text=linha["nome"],
                               showarrow=True, arrowcolor="#7B241C", font=dict(color="#7B241C", size=13),
                               ax=(-70 if i % 2 else 70), ay=-30 - 22 * i)
    fig.update_xaxes(title="IDHM", gridcolor="rgba(0,0,0,.08)")
    fig.update_yaxes(title="Casos de dengue (escala log)", type="log", gridcolor="rgba(0,0,0,.08)")
    return estilo(fig, 520).update_layout(title=titulo, legend=dict(orientation="h", y=-0.15))


with tab4:
    st.subheader("O que foge do padrão?")
    st.markdown("O **Z-score** mede quantos desvios-padrão um município está longe da média de casos. "
                "Acima de **2**, ele está **fora do padrão**.")

    base_z = df.copy()
    media_casos, desvio_casos = base_z["casos"].mean(), base_z["casos"].std()
    base_z["z_casos"] = (base_z["casos"] - media_casos) / desvio_casos
    outliers = base_z[base_z["z_casos"].abs() > 2].sort_values("z_casos", ascending=False)
    limite = media_casos + 2 * desvio_casos

    procurar = st.button("🔎  Encontrar anomalias", type="primary")
    lugar_z = st.empty()

    if procurar:
        vazio = outliers.iloc[0:0]
        mostrar(grafico_outliers(base_z, vazio, limite, "Traçando o limite do padrão..."), lugar_z, key="z_limite")
        time.sleep(0.9)
        lotes = np.linspace(0, len(outliers), 6).astype(int)[1:]
        for i, ate in enumerate(lotes, start=1):
            mostrar(grafico_outliers(base_z, outliers.iloc[:ate], limite, f"Procurando... {ate} encontrados"),
                    lugar_z, key=f"z_lote_{i}")
            time.sleep(0.45)
        st.session_state["outliers_prontos"] = True

    if st.session_state.get("outliers_prontos"):
        mostrar(grafico_outliers(base_z, outliers, limite,
                                 f"{len(outliers)} municípios fora do padrão (Z-score > 2)"), lugar_z, key="z_final")

        col_x, col_y = st.columns(2)
        colunas = {"nome": "Município", "idhm": "IDHM", "casos": "Casos", "faixa_idh": "Faixa IDH"}
        with col_x:
            st.markdown("**🔴 IDH Alto mas MUITOS casos (surto)**")
            alta = outliers[outliers["faixa_idh"].isin(["Alto", "Muito Alto"]) & (outliers["z_casos"] > 2)]
            if not alta.empty:
                st.dataframe(alta[list(colunas)].rename(columns=colunas), use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum outlier nessa categoria.")
        with col_y:
            st.markdown("**🟢 IDH Baixo mas muitos casos (vulnerabilidade)**")
            baixa = outliers[outliers["faixa_idh"].isin(["Baixo", "Médio"]) & (outliers["z_casos"] > 2)]
            if not baixa.empty:
                st.dataframe(baixa[list(colunas)].rename(columns=colunas), use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum outlier nessa categoria.")

        st.markdown("**Todos os outliers**")
        st.dataframe(outliers[["nome", "idhm", "casos", "faixa_idh", "z_casos"]].rename(
            columns={**colunas, "z_casos": "Z-Score"}).head(20), use_container_width=True, hide_index=True)
    elif not procurar:
        mostrar(grafico_outliers(base_z, outliers.iloc[0:0], None, "Todos os municípios: algum foge do padrão?"),
                lugar_z, key="z_antes")
        st.info("Aperte **🔎 Encontrar anomalias** para o algoritmo procurar o que foge do padrão.")

st.divider()
st.caption("Versão show do dashboard · o original continua em dashboard.py · mesmos dados, nova apresentação")

# ── OS NUMEROS DO TOPO CONTANDO (so na primeira abertura) ──
if not ja_contou:
    passos_contagem = 36
    for passo in range(1, passos_contagem + 1):
        fracao = 1 - (1 - passo / passos_contagem) ** 3          # comeca rapido e freia no final
        for lugar, (rotulo, valor, formato) in zip(lugares, NUMEROS):
            lugar.metric(rotulo, formato(valor * fracao))
        if passo % 3 == 0 or passo == passos_contagem:            # os graficos a cada 3 passos (mais leve)
            mostrar(barras(fracao), lugar_barras, key=f"barras_{passo}")      # cada quadro com nome unico
            mostrar(sazonalidade(max(1, round(len(meses) * passo / passos_contagem))), lugar_linhas,
                    key=f"linhas_{passo}")
        time.sleep(0.05)
    st.session_state["ja_contou"] = True
