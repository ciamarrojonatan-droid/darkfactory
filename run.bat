@echo off
cd /d "%~dp0"

if not exist "%~dp0venv\Scripts\python.exe" (
    echo [ERRO] Ambiente virtual 'venv' nao encontrado em:
    echo        %~dp0venv
    pause
    exit /b 1
)

"%~dp0venv\Scripts\python.exe" run_pilot_pipeline.py %*

if errorlevel 1 (
    echo.
    echo [AVISO] Ocorreu um erro durante a execucao.
    pause
)
