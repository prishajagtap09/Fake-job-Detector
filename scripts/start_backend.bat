@echo off
title FakeJob Detector - Backend Setup
color 0A

echo ============================================
echo   FakeJob Detector - Backend Setup (Windows)
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.10+ from https://python.org
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo [OK] Python found.

REM Create virtual environment if not exists
if not exist "backend\venv" (
    echo.
    echo [STEP 1/3] Creating virtual environment...
    python -m venv backend\venv
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment already exists.
)

REM Activate venv and install dependencies
echo.
echo [STEP 2/3] Installing Python dependencies...
call backend\venv\Scripts\activate.bat
pip install --upgrade pip --quiet
pip install -r backend\requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo [OK] Dependencies installed.

REM Run the FastAPI server
echo.
echo [STEP 3/3] Starting FastAPI backend server...
echo.
echo ============================================
echo   Backend running at: http://localhost:8000
echo   API Docs at:        http://localhost:8000/docs
echo   Press Ctrl+C to stop
echo ============================================
echo.

cd backend
python -m uvicorn main:app --reload --port 8000 --host 0.0.0.0

pause
