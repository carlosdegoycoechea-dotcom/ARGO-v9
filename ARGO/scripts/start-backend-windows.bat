@echo off
REM ============================================================================
REM ARGO - Backend Startup (Windows)
REM ============================================================================

echo.
echo ==========================================
echo    ARGO Backend
echo ==========================================
echo.

REM Get directories
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set BACKEND_DIR=%PROJECT_ROOT%\backend

cd /d "%BACKEND_DIR%"

REM Check .env file
if not exist ".env" (
    echo Creando archivo .env desde template...
    copy .env.example .env
    echo.
    echo IMPORTANTE: Edita backend\.env y agrega tu OPENAI_API_KEY
    echo.
    pause
)

REM Setup virtual environment
if not exist "venv" (
    echo Creando entorno virtual Python...
    python -m venv venv
)

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo Instalando dependencias Python...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

REM Create directories
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "temp" mkdir temp

echo.
echo ==========================================
echo    Backend iniciado
echo ==========================================
echo.
echo URL: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.

REM Start backend
python main.py
