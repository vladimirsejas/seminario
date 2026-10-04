@echo off
title Dashboard Show - Seminario Dengue
cd /d "%~dp0"

echo.
echo ==========================================
echo    DASHBOARD SHOW - SEMINARIO DENGUE
echo ==========================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo Nao encontrei a pasta venv aqui.
    echo Este atalho precisa ficar dentro da pasta do seminario, junto do dashboard_show.py.
    pause
    exit /b 1
)

rem Na primeira vez, instala o Plotly, que deixa os graficos interativos
venv\Scripts\python.exe -c "import plotly" 2>nul
if errorlevel 1 (
    echo Primeira vez: instalando o Plotly. Precisa de internet...
    venv\Scripts\python.exe -m pip install -r requirements_show.txt
)

echo Abrindo o dashboard show no navegador: http://localhost:8502
echo (o dashboard original, sem movimento, fica em http://localhost:8501)
echo Para encerrar, feche esta janela.
echo.
rem Usa o Python da venv e abre o dashboard_show.py, a versao com movimento
venv\Scripts\python.exe -m streamlit run dashboard_show.py --theme.base light --server.port 8502
pause
