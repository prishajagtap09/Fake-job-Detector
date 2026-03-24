@echo off
title FakeJob Detector - Frontend Setup
color 0B

echo ============================================
echo  FakeJob Detector - Frontend Setup (Windows)
echo ============================================
echo.

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found!
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

echo [OK] Node.js found.

REM Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm not found! Please reinstall Node.js.
    pause
    exit /b 1
)

echo [OK] npm found.

cd frontend

REM Install dependencies
if not exist "node_modules" (
    echo.
    echo [STEP 1/2] Installing Node dependencies (this may take a minute)...
    npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed.
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed.
) else (
    echo [OK] node_modules already exists.
)

REM Start dev server
echo.
echo [STEP 2/2] Starting React development server...
echo.
echo ============================================
echo   Frontend running at: http://localhost:3000
echo   Make sure backend is also running!
echo   Press Ctrl+C to stop
echo ============================================
echo.

npm run dev

pause
