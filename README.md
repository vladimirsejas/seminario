# Sistema Inteligente de Mineração Epidemiológica da Dengue

## Utilizando Dados Oficiais do DATASUS/SINAN e Integração DICOM

Este projeto foi desenvolvido como uma aplicação acadêmica de engenharia de software, mineração de dados e ciência de dados em saúde pública utilizando Python.

O sistema tem como objetivo demonstrar o uso integrado de bibliotecas reais do ecossistema científico para análise epidemiológica da dengue no Brasil utilizando dados oficiais do DATASUS/SINAN.

O foco principal do projeto não é realizar diagnóstico médico nem prever doenças com inteligência artificial clínica.

O objetivo científico é identificar padrões epidemiológicos ocultos relacionados à sazonalidade, perfil demográfico, comportamento regional, distribuição socioeconômica e concentração territorial da dengue.

O sistema utiliza dados públicos reais do governo federal brasileiro através da biblioteca PySUS e integra técnicas de mineração de dados, análise estatística, clusterização e visualização analítica.

A arquitetura foi construída de forma modular e separada por responsabilidades, permitindo expansão futura para novas pesquisas acadêmicas envolvendo saúde pública, mineração epidemiológica e ciência de dados.

---

# Duas formas de ver o dashboard: o antes e o depois

Este projeto tem **duas versões do dashboard**, lado a lado, para mostrar a evolução:

1. **O antes (versão 1): `dashboard.py`.** O dashboard original, com gráficos científicos
   em matplotlib. Continua **exatamente como foi feito**.
2. **O depois (versão 2): `dashboard_show.py`.** Os **mesmos dados e as mesmas consultas**,
   apresentados com movimento, interação e narrativa.

Nenhum arquivo do projeto original foi apagado. A versão 2 só **acrescenta** arquivos novos.

| | Versão 1: `dashboard.py` | Versão 2: `dashboard_show.py` |
|---|---|---|
| **Como abrir** | `Abrir Dashboard.bat` ou ▶ no `main.py` | `Abrir Dashboard Show.bat` |
| **Endereço** | `localhost:8501` | `localhost:8502` |
| **Nome da aba** | Dengue & IDH | Dengue & IDH \| Show |
| **Gráficos** | Imagens fixas (matplotlib) | Interativos (Plotly e desenho no navegador) |
| **Abertura** | Tudo aparece pronto | Os números contam, as barras crescem e a linha se desenha |
| **Narrativa** | Métricas e gráficos | Pergunta → Método → Resultado, "O que encontramos?" e letreiro de achados |
| **Visão geral** | — | **Constelação viva** com os 5.210 municípios |
| **Detalhes** | — | **Lupa** que amplia os gráficos e mostra fichas completas |
| **Clustering** | O resultado pronto | O K-Means roda **passo a passo** na tela |
| **Outliers** | Tabelas | Efeito **detetive**: o limite aparece e as anomalias acendem |
| **Visual** | Padrão do Streamlit | Título colorido em movimento, mosquito voando, pontos de luz |

Os números são os mesmos nas duas versões, porque as duas leem os mesmos arquivos com as mesmas consultas.

---

## O que há de novo na versão 2, parte por parte

**Cabeçalho.** Título com cores que se movem, um 🦟 voando, o indicador "● AO VIVO" e o botão
**🎬 Reproduzir abertura**, que repete toda a animação de abertura quando você quiser.

**Os quatro números.** Contam do zero até o valor final, no formato brasileiro (4.412.090 e 84,8%),
com uma borda que "respira".

**🌌 Constelação viva.** Cada município é um ponto de luz: a posição vem do IDHM e dos casos, e a cor,
da faixa de IDH. Um relógio percorre o ano (JAN → DEZ) e os pontos **crescem com os casos de cada mês**,
seguindo a sazonalidade real. Anéis marcam surtos nas cidades com mais casos. O mouse vira uma lente
que mostra a cidade, os casos e o IDHM; sem mouse, a lente passeia sozinha.

**Pergunta → Método → Resultado.** Três cartões que explicam o trabalho em uma frase cada, mais o quadro
**"O que encontramos?"** e um letreiro com os principais achados.

**🔍 Lupas nos gráficos.** Uma lente de aumento de verdade (amplia o que está embaixo dela) com um cartão
de informações. Sem mouse, ela passeia sozinha pelas barras e pelos meses.
- *Casos por faixa de IDH:* casos, % do total, nº de municípios, média por município, IDHM médio,
  % de mulheres, idade média e as 3 cidades com mais casos.
- *Sazonalidade:* total do mês, casos de cada faixa, variação em relação ao mês anterior, % do ano e
  posição do mês no ranking.
- *Top municípios:* posição no Brasil, casos, % dentro da faixa, IDHM, % de mulheres e idade média.

**🔬 Clustering.** O botão **▶ Executar agrupamento** mostra o K-Means trabalhando: os centros (✖) se movem
e as cores se reorganizam a cada passo, até o algoritmo parar. No fim, uma tabela descreve cada grupo
em português (por exemplo, "IDH alto · mais casos").

**⚠️ Outliers.** O botão **🔎 Encontrar anomalias** traça o limite do padrão (Z-score > 2) e revela, aos poucos,
os municípios que fogem dele, com os nomes dos maiores.

---

## As novas bibliotecas e tecnologias da versão 2

| Biblioteca / tecnologia | Precisa instalar? | Função no dashboard show |
|---|---|---|
| **Plotly** | Sim, uma vez (`requirements_show.txt`) | Gráficos interativos do clustering e dos outliers: passar o mouse, aproximar e animar cada passo |
| **streamlit.components** | Não (já vem no Streamlit) | Permite colocar dentro do dashboard páginas com desenho próprio (a constelação e as lupas) |
| **HTML5 Canvas + JavaScript** | Não (roda no próprio navegador) | Desenha a constelação e as lupas dezenas de vezes por segundo, reagindo ao mouse, **sem internet** |
| **CSS (animações)** | Não | O título colorido em movimento, o mosquito voando, o letreiro, o "AO VIVO" e os pontos de luz do fundo |
| **scikit-learn** (`kmeans_plusplus`) | Não (já estava no projeto) | Escolhe os centros iniciais do K-Means; os passos seguintes são calculados um a um para a animação |
| **NumPy** | Não (vem junto com o pandas) | Calcula as distâncias entre os municípios e os centros dos grupos em cada passo do K-Means |

As bibliotecas da versão 1 (DuckDB, pandas, Streamlit, scikit-learn, matplotlib) continuam sendo usadas:
o **DuckDB** faz exatamente as mesmas consultas nos arquivos Parquet, e o **Streamlit** monta a página.

### Como cada novidade funciona, em uma frase

- **Números que contam:** o Python atualiza o valor dezenas de vezes em menos de dois segundos.
- **Constelação e lupas:** o Python prepara os dados e os entrega ao navegador, que desenha tudo sozinho,
  quadro a quadro.
- **K-Means passo a passo:** em vez de pedir só o resultado final, o dashboard guarda cada etapa do
  algoritmo (escolher centros → agrupar → mover os centros → repetir) e mostra uma por uma.
- **Outliers:** o Z-score mede quantos desvios-padrão um município está acima da média; acima de 2, ele
  está fora do padrão.

---

## Como abrir (Windows)

| Para... | Use | Endereço |
|---|---|---|
| Gerar os gráficos e abrir o dashboard original | ▶ no `main.py` (VS Code) | `localhost:8501` |
| Abrir só o dashboard original | `Abrir Dashboard.bat` | `localhost:8501` |
| Abrir o dashboard show | `Abrir Dashboard Show.bat` | `localhost:8502` |

- Os dois dashboards podem ficar **abertos ao mesmo tempo**, em abas diferentes.
- Na primeira vez, o `Abrir Dashboard Show.bat` instala o Plotly sozinho (precisa de internet).
- Para encerrar um dashboard, feche a janela preta (ou o terminal) que o mantém aberto.
- **Não use o ▶ no `dashboard.py` nem no `dashboard_show.py`:** um dashboard Streamlit precisa ser aberto pelo
  Streamlit, por isso existem os atalhos.

### Sobre a segurança do Windows

- Em computadores com essa proteção ligada, o Windows bloqueia o programa `streamlit.exe` (aviso do *Device Guard* / *Controle de Aplicativo
  Inteligente*). Por isso os atalhos e o `main.py` abrem o Streamlit **pelo `python.exe`**
  (`python -m streamlit run ...`), que é permitido.
- Um `.bat` **baixado da internet** pode ser bloqueado. Os atalhos chegam pelo `git pull`, que não tem esse
  problema. Se precisar usar um baixado: botão direito → Propriedades → ☑ Desbloquear.
- Não é recomendado desligar o Controle de Aplicativo Inteligente: depois de desligado, ele só volta
  reinstalando o Windows.

---

## Um cuidado científico

Os números são **casos absolutos**. Municípios de IDH alto costumam ser os mais populosos, então
concentram mais casos também por terem mais gente. Por isso o dashboard diz que os casos **se concentram**
em municípios de IDH alto, sem afirmar que o IDH causa mais dengue. Para comparar o **risco**, o ideal é a
**taxa por 100 mil habitantes**, que depende de dados de população.

---

## Arquivos acrescentados pela versão 2

```text
seminario/
├── dashboard_show.py          ← o dashboard com movimento (versão 2)
├── requirements_show.txt      ← só o Plotly
├── Abrir Dashboard Show.bat   ← abre a versão 2 em localhost:8502
├── Abrir Dashboard.bat        ← abre a versão 1 em localhost:8501
└── .gitattributes             ← mantém os .bat no formato do Windows
```

O `main.py` recebeu uma única mudança: a última linha abre o dashboard pelo `python.exe` (veja acima, em
segurança do Windows). Todo o resto do projeto original está como foi feito.

---

# Documentação do projeto original (versão 1)

A partir daqui, a documentação original do projeto, sem alterações.

---

# Objetivo Científico

O projeto busca responder perguntas analíticas fundamentais como:

Existem padrões epidemiológicos ocultos na distribuição da dengue no Brasil?

Existem relações entre a incidência de dengue e o IDHM municipal?

Quais regiões apresentam comportamento sazonal semelhante?

Existem grupos demográficos mais afetados?

Municípios de alto desenvolvimento humano apresentam maior concentração de casos absolutos?

Existem municípios considerados outliers epidemiológicos fora do padrão nacional?

---

# Tecnologias Utilizadas

## Python 3.11

Linguagem principal utilizada no desenvolvimento do sistema.

## PySUS

Biblioteca utilizada para acesso, download e estruturação dos dados epidemiológicos oficiais do DATASUS e SINAN.

## pandas

Manipulação tabular de DataFrames, cruzamento de bases, agrupamentos, filtros e análises estatísticas.

## DuckDB

Banco analítico utilizado para leitura extremamente rápida de arquivos Parquet sem necessidade de carregar toda a base na memória RAM.

## matplotlib

Biblioteca utilizada para geração de gráficos científicos e visualizações epidemiológicas.

## Streamlit

Framework utilizado para construção do dashboard interativo local.

## scikit-learn

Biblioteca utilizada para mineração de dados, clusterização e identificação de padrões utilizando KMeans.

## openpyxl

Leitura de planilhas Excel contendo indicadores socioeconômicos municipais.

## pydicom

Biblioteca prevista para integração futura com imagens médicas no padrão DICOM.

## sqlite3

Persistência local de dados estruturados e histórico de execução.

## logging

Sistema de monitoramento e rastreamento de erros durante a execução do pipeline.

---

# Estrutura Real do Projeto

# Estrutura Real do Projeto

```text
seminario/

├── main.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── baixar_idh.py
├── cruzar_idh.py
├── diagnostico.py
├── gerar_base_reduzida.py
├── dashboard.py
├── graphs.py
├── teste_pysus.py
├── testes_dados.py
│
├── data/
│   ├── epidemiologia/
│   └── graficos/
│
├── src/
│   ├── database.py
│   ├── epidemiology_service.py
│   └── risk_engine.py
│
└── venv/
```

---

# Explicação dos Arquivos

## main.py

Arquivo principal responsável pela orquestração do pipeline epidemiológico e integração entre os módulos centrais do sistema.

## baixar_idh.py

Responsável pelo download e preparação inicial dos dados municipais de IDHM utilizados no cruzamento socioeconômico.

## cruzar_idh.py

Realiza o cruzamento entre os casos de dengue e os indicadores de desenvolvimento humano municipal utilizando códigos IBGE.

## diagnostico.py

Arquivo utilizado para inspeção, validação e diagnóstico das colunas presentes nas bases epidemiológicas.

## gerar_base_reduzida.py

Cria uma base reduzida focada na população economicamente ativa entre 18 e 61 anos para otimizar as análises.

## dashboard.py

Implementa o dashboard interativo utilizando Streamlit contendo tabelas, métricas, clusterização, sazonalidade e análise epidemiológica.

## graphs.py

Responsável pela geração dos gráficos científicos e exportação das visualizações para a pasta `data/graficos`.

## teste_pysus.py

Arquivo inicial de validação do funcionamento da biblioteca PySUS.

## testes_dados.py

Executa verificações estruturais das bases Parquet e validação de colunas.

## src/database.py

Implementa consultas analíticas utilizando DuckDB para leitura eficiente dos arquivos Parquet.

## src/epidemiology_service.py

Responsável pelo carregamento e processamento dos dados epidemiológicos oriundos do SINAN/DATASUS.

## src/risk_engine.py

Motor analítico do sistema responsável por agrupamentos, estatísticas, classificação epidemiológica, sazonalidade, distribuição demográfica e identificação de padrões.

---

# Estrutura de Dados

O sistema trabalha principalmente com arquivos no formato Parquet.

O formato Parquet foi escolhido porque:

Alta compressão de dados.

Leitura extremamente rápida.

Baixo consumo de memória RAM.

Excelente integração com DuckDB.

Ampla utilização em engenharia de dados e Big Data.

---

# Bases Utilizadas

## DENGBR24.parquet

Base completa contendo notificações nacionais de dengue referentes ao ano de 2024.

## DENG_PEA.parquet

Base reduzida contendo apenas indivíduos pertencentes à população economicamente ativa entre 18 e 61 anos.

## idhm_municipios.parquet

Base contendo indicadores municipais de IDHM utilizados nas análises socioeconômicas.

---

# Dashboard Analítico

O dashboard desenvolvido em Streamlit permite:

Visualização de sazonalidade.

Análise por faixa de IDH.

Distribuição por sexo.

Análise por faixa etária.

Clusterização de municípios.

Detecção de outliers epidemiológicos.

Análise territorial.

Ranking de municípios.

Métricas epidemiológicas agregadas.

---

# Clusterização

O projeto utiliza o algoritmo KMeans da biblioteca scikit-learn para identificar grupos ocultos de municípios com comportamento epidemiológico semelhante.

As variáveis utilizadas incluem:

Número de casos.

IDHM municipal.

Idade média.

Distribuição demográfica.

---

# Integração Socioeconômica

O sistema realiza cruzamento entre:

Casos de dengue.

IDHM municipal.

Códigos IBGE.

Esse cruzamento permite análises epidemiológicas associadas ao desenvolvimento humano, urbanização e desigualdade regional.

---

# Integração DICOM

A integração DICOM foi mantida como camada experimental complementar.

O objetivo não é realizar diagnóstico médico automatizado.

O papel do DICOM no projeto é:

Demonstrar integração tecnológica.

Extrair metadados clínicos.

Contextualizar análises hospitalares.

Servir como prova de integração com imagens médicas.

---

# Sobre o .gitignore

O arquivo `.gitignore` impede que arquivos desnecessários sejam enviados ao GitHub.

Arquivos ignorados:

## venv/

Ambiente virtual local do Python.

## __pycache__/

Arquivos temporários gerados automaticamente pelo interpretador Python.

## *.pyc

Arquivos compilados temporários.

## .env

Variáveis de ambiente locais.

## *.parquet

Bases de dados grandes que não devem ser enviadas ao repositório.

---

# Sobre o requirements.txt

O arquivo `requirements.txt` lista todas as bibliotecas necessárias para execução do projeto.

Bibliotecas utilizadas:

```txt
duckdb
pandas
matplotlib
streamlit
scikit-learn
openpyxl
pysus
pydicom
```

---

# Como Executar

## Criar ambiente virtual

```bash
python -m venv venv
```

## Ativar ambiente virtual

```bash
venv\Scripts\activate
```

## Instalar dependências

```bash
pip install -r requirements.txt
```

## Executar dashboard

```bash
streamlit run dashboard.py
```

## Executar pipeline principal

```bash
python main.py
```

---

# Considerações Acadêmicas

Este projeto demonstra na prática:

Engenharia de software modular.

Consumo de dados públicos brasileiros.

Mineração de dados em saúde pública.

Visualização científica.

Engenharia de dados.

Clusterização.

Análise epidemiológica.

Uso de Parquet e DuckDB.

Integração de bibliotecas científicas reais.

Construção de dashboard analítico.

Tratamento estatístico de dados reais.

Arquitetura escalável para futuras pesquisas acadêmicas.