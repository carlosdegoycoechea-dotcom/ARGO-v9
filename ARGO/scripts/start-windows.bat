@echo off
REM ============================================================================
REM ARGO - Windows Startup Script
REM ============================================================================

echo.
echo ==========================================
echo    ARGO Enterprise Platform
echo ==========================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado
    echo.
    echo Por favor instala Python 3.11 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Marca "Add Python to PATH" durante la instalacion
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js no encontrado
    echo.
    echo Por favor instala Node.js 18 o superior desde:
    echo https://nodejs.org/
    pause
    exit /b 1
)

echo Iniciando ARGO...
echo.
echo Backend estara disponible en: http://localhost:8000
echo Frontend estara disponible en: http://localhost:5000
echo.
echo Presiona Ctrl+C para detener el sistema
echo.

REM Start backend in new window
start "ARGO Backend" cmd /k "%SCRIPT_DIR%start-backend-windows.bat"

REM Wait 5 seconds for backend to initialize
timeout /t 5 /nobreak >nul

REM Start frontend in new window
start "ARGO Frontend" cmd /k "%SCRIPT_DIR%start-frontend-windows.bat"

echo.
echo ==========================================
echo    ARGO iniciado correctamente
echo ==========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5000
echo API Docs: http://localhost:8000/docs
echo.
