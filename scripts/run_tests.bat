@echo off
title FakeJob Detector - Run Tests
color 0E

echo ============================================
echo   FakeJob Detector - Running Tests
echo ============================================
echo.

call backend\venv\Scripts\activate.bat

echo Running pytest...
echo.
pytest tests\ -v --tb=short

echo.
echo ============================================
echo   Tests complete.
echo ============================================
pause
