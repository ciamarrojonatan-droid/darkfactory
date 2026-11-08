@echo off
chcp 65001 > nul
title DarkFactory Cinema Studio — Dashboard (:8502)

echo ======================================================================
echo    🎬 DarkFactory Cinema Studio — Faceless YouTube Production Cockpit
echo    Nolan Showrunner v2.0 • 4K IMAX • Sound Lab • 1-Click Approval
echo ======================================================================
echo.

cd /d "%~dp0"

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [!] venv local nao encontrado. Usando python do sistema...
)

echo [✓] Iniciando servidor FastAPI na porta 8502...
start http://localhost:8502

python -m uvicorn src.dashboard.app:app --host 127.0.0.1 --port 8502 --reload
pause
