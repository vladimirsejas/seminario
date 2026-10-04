import subprocess
import sys
import os

PYTHON = sys.executable

def rodar(script, descricao):
    print(f"\n>>> {descricao}...")
    resultado = subprocess.run([PYTHON, script], check=True)
    print(f"    Concluido.")

def main():
    print("=== SISTEMA DE MINERACAO EPIDEMIOLOGICA DA DENGUE ===")
    print("Populacao Economicamente Ativa (18-61 anos) | Brasil 2024")

    # Etapa 1 - Gera base reduzida se ainda nao existe
    if not os.path.exists("data/epidemiologia/DENG_PEA.parquet"):
        rodar("gerar_base_reduzida.py", "Etapa 1 - Gerando base reduzida da PEA")
    else:
        print("\n>>> Etapa 1 - Base PEA ja existe. Pulando.")

    # Etapa 2 - Cruza com IDHM se ainda nao existe
    if not os.path.exists("data/epidemiologia/idhm_municipios.parquet"):
        rodar("cruzar_idh.py", "Etapa 2 - Cruzando com IDHM municipal")
    else:
        print(">>> Etapa 2 - IDHM ja cruzado. Pulando.")

    # Etapa 3 - Gera graficos
    rodar("graphs.py", "Etapa 3 - Gerando graficos")

    # Etapa 4 - Sobe dashboard
    print("\n>>> Etapa 4 - Iniciando dashboard...")
    print("    Abrindo no navegador em http://localhost:8501")
    print("    Pressione Ctrl+C para encerrar.\n")
    subprocess.run([PYTHON, "-m", "streamlit", "run", "dashboard.py"])   # pelo python.exe: o Windows bloqueia o streamlit.exe

if __name__ == "__main__":
    main()