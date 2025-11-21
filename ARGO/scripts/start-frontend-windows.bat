@echo off
REM ============================================================================
REM ARGO - Frontend Startup (Windows)
REM ============================================================================

echo.
echo ==========================================
echo    ARGO Frontend
echo ==========================================
echo.

REM Get directories
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set FRONTEND_DIR=%PROJECT_ROOT%\frontend

cd /d "%FRONTEND_DIR%"

REM Check .env file
if not exist ".env" (
    echo Creando archivo .env desde template...
    copy .env.example .env
)

REM Install dependencies
if not exist "node_modules" (
    echo Instalando dependencias npm...
    echo Esto puede tomar varios minutos...
    call npm install
)

echo.
echo ==========================================
echo    Frontend iniciado
echo ==========================================
echo.
echo URL: http://localhost:5000
echo.

REM Start frontend
call npm run dev:client
