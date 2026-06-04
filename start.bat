@echo off
echo ============================================
echo   AI Search Algorithm Visualizer
echo   Starting server...
echo ============================================
echo.

cd /d "%~dp0backend"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [SETUP] Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo [SETUP] Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo ============================================
echo   Server running at: http://localhost:8000
echo   Press Ctrl+C to stop
echo ============================================
echo.

REM Start the server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
