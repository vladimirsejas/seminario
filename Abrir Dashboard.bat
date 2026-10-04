@echo off
title Dashboard - Seminario Dengue
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo Nao encontrei a pasta venv aqui.
    echo Este atalho precisa ficar dentro da pasta do seminario, junto do dashboard.py.
    pause
    exit /b 1
)

if not exist "dashboard.py" (
    echo Nao encontrei o dashboard.py nesta pasta.
    echo Coloque este atalho dentro da pasta do seminario, por exemplo C:\seminario.
    pause
    exit /b 1
)

echo Abrindo o dashboard no navegador... (http://localhost:8501)
echo.
venv\Scripts\python.exe -m streamlit run dashboard.py
pause
