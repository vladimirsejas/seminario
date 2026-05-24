Sistema Inteligente de Mineração Epidemiológica da Dengue
Utilizando Dados Oficiais do DATASUS/SINAN e Integração DICOM

Este projeto foi desenvolvido como uma aplicação acadêmica de engenharia de software, mineração de dados e ciência de dados em saúde pública utilizando Python. O sistema tem como objetivo demonstrar o uso integrado de bibliotecas reais do ecossistema científico para análise epidemiológica da dengue no Brasil utilizando dados oficiais do DATASUS/SINAN.

O foco principal do projeto não é realizar diagnóstico médico nem prever doenças com inteligência artificial clínica. O objetivo científico é identificar padrões epidemiológicos ocultos relacionados à sazonalidade, perfil demográfico, comportamento regional, distribuição socioeconômica e concentração territorial da dengue.

O sistema utiliza dados públicos reais do governo federal brasileiro através da biblioteca PySUS e integra técnicas de mineração de dados, análise estatística, clusterização e visualização analítica.

A arquitetura foi construída de forma modular e separada por responsabilidades, permitindo expansão futura para novas pesquisas acadêmicas envolvendo saúde pública, mineração epidemiológica e ciência de dados.

Objetivo Científico

O projeto busca responder perguntas analíticas fundamentais como:
Existem padrões epidemiológicos ocultos na distribuição da dengue no Brasil?

Existem relações entre a incidência de dengue e o IDHM municipal?

Quais regiões apresentam comportamento sazonal semelhante?

Existem grupos demográficos mais afetados?

Municípios de alto desenvolvimento humano apresentam maior concentração de casos absolutos?

Existem municípios considerados outliers epidemiológicos fora do padrão nacional?

Tecnologias Utilizadas
Python 3.11
Linguagem principal utilizada no desenvolvimento do sistema.

PySUS

Biblioteca utilizada para acesso, download e estruturação dos dados epidemiológicos oficiais do DATASUS e SINAN.
Pandas
Manipulação tabular de DataFrames, cruzamento de bases, agrupamentos, filtros e análises estatísticas.

DuckDB

Banco analítico utilizado para leitura extremamente rápida de arquivos Parquet sem necessidade de carregar toda a base na memória RAM.

matplotlib

Biblioteca utilizada para geração de gráficos científicos e visualizações epidemiológicas.

Streamlit

Framework utilizado para construção do dashboard interativo local.

scikit-learn

Biblioteca utilizada para mineração de dados, clusterização e identificação de padrões utilizando KMeans.

openpyxl

Leitura de planilhas Excel contendo indicadores socioeconômicos municipais.

pydicom

Biblioteca prevista para integração futura com imagens médicas no padrão DICOM.

sqlite3

Persistência local de dados estruturados e histórico de execução.

logging

Sistema de monitoramento e rastreamento de erros durante a execução do pipeline.

Estrutura Real do Projeto
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
Explicação dos Arquivos

main.py

Arquivo principal responsável pela orquestração do pipeline epidemiológico e integração entre os módulos centrais do sistema.

baixar_idh.py

Responsável pelo download e preparação inicial dos dados municipais de IDHM utilizados no cruzamento socioeconômico.

cruzar_idh.py

Realiza o cruzamento entre os casos de dengue e os indicadores de desenvolvimento humano municipal utilizando códigos IBGE.

diagnostico.py

Arquivo utilizado para inspeção, validação e diagnóstico das colunas presentes nas bases epidemiológicas.

gerar_base_reduzida.py

Cria uma base reduzida focada na população economicamente ativa entre 18 e 61 anos para otimizar as análises.

dashboard.py

Implementa o dashboard interativo utilizando Streamlit contendo tabelas, métricas, clusterização, sazonalidade e análise epidemiológica.

graphs.py

Responsável pela geração dos gráficos científicos e exportação das visualizações para a pasta data/graficos.

teste_pysus.py

Arquivo inicial de validação do funcionamento da biblioteca PySUS.

testes_dados.py

Executa verificações estruturais das bases Parquet e validação de colunas.

src/database.py

Implementa consultas analíticas utilizando DuckDB para leitura eficiente dos arquivos Parquet.

src/epidemiology_service.py

Responsável pelo carregamento e processamento dos dados epidemiológicos oriundos do SINAN/DATASUS.

src/risk_engine.py

Motor analítico do sistema responsável por agrupamentos, estatísticas, classificação epidemiológica, sazonalidade, distribuição demográfica e identificação de padrões.

Estrutura de Dados

O sistema trabalha principalmente com arquivos no formato Parquet.

O formato Parquet foi escolhido porque:

possui alta compressão

permite leitura extremamente rápida

consome menos memória RAM

funciona muito bem com DuckDB

é amplamente utilizado em engenharia de dados e Big Data

Bases Utilizadas

DENGBR24.parquet

Base completa contendo notificações nacionais de dengue referentes ao ano de 2024.

DENG_PEA.parquet

Base reduzida contendo apenas indivíduos pertencentes à população economicamente ativa entre 18 e 61 anos.

idhm_municipios.parquet

Base contendo indicadores municipais de IDHM utilizados nas análises socioeconômicas.

Dashboard Analítico

O dashboard desenvolvido em Streamlit permite:

visualização de sazonalidade

análise por faixa de IDH

distribuição por sexo

análise por faixa etária

clusterização de municípios

detecção de outliers epidemiológicos

análise territorial

ranking de municípios

métricas epidemiológicas agregadas

Clusterização

O projeto utiliza o algoritmo KMeans da biblioteca scikit-learn para identificar grupos ocultos de municípios com comportamento epidemiológico semelhante.

As variáveis utilizadas incluem:

número de casos

IDHM municipal

idade média

distribuição demográfica

Integração Socioeconômica

O sistema realiza cruzamento entre:

casos de dengue

IDHM municipal

códigos IBGE

Esse cruzamento permite análises epidemiológicas associadas ao desenvolvimento humano, urbanização e desigualdade regional.

Integração DICOM

A integração DICOM foi mantida como camada experimental complementar.

O objetivo não é realizar diagnóstico médico automatizado.

O papel do DICOM no projeto é:

demonstrar integração tecnológica

extrair metadados clínicos

contextualizar análises hospitalares

servir como prova de integração com imagens médicas

Sobre o .gitignore

O arquivo .gitignore impede que arquivos desnecessários sejam enviados ao GitHub.

Foram ignorados:

venv/

Ambiente virtual local do Python.

pycache/

Arquivos temporários gerados automaticamente pelo interpretador Python.

*.pyc

Arquivos compilados temporários.

.env

Variáveis de ambiente locais.

*.parquet

Bases de dados grandes que não devem ser enviadas ao repositório.

Sobre o requirements.txt

O arquivo requirements.txt lista todas as bibliotecas necessárias para execução do projeto.

Bibliotecas utilizadas:

duckdb

pandas

matplotlib

streamlit

scikit-learn

openpyxl

pysus

pydicom

Como Executar

Criar ambiente virtual:

python -m venv venv

Ativar ambiente virtual:

venv\Scripts\activate

Instalar dependências:

pip install -r requirements.txt

Executar dashboard:

streamlit run dashboard.py

Executar pipeline principal:

python main.py
Considerações Acadêmicas

Este projeto demonstra na prática:

engenharia de software modular

consumo de dados públicos brasileiros

mineração de dados em saúde pública

visualização científica

engenharia de dados

clusterização

análise epidemiológica

uso de parquet e DuckDB

integração de bibliotecas científicas reais

construção de dashboard analítico

tratamento estatístico de dados reais

arquitetura escalável para futuras pesquisas acadêmicas