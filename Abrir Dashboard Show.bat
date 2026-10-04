@echo off
title Seminario - Dashboard Dengue
cd /d "%~dp0"

echo.
echo ==========================================
echo    DASHBOARD - SEMINARIO DENGUE
echo ==========================================
echo.

REM Primeiro tenta o Python Launcher do Windows
where py >nul 2>&1
if %errorlevel%==0 (
    echo Iniciando com Python Launcher...
    py -m streamlit run dashboard.py
    if not errorlevel 1 goto fim
)

REM Se nao funcionar, tenta o Python da venv
if exist "venv\Scripts\python.exe" (
    echo.
    echo Iniciando com Python da venv...
    "venv\Scripts\python.exe" -m streamlit run dashboard.py
    goto fim
)

echo.
echo ERRO: nao encontrei um Python capaz de iniciar o dashboard.
echo.
echo Verifique se o Python e o Streamlit estao instalados.
echo.
pause
goto fim

:fim
pause
