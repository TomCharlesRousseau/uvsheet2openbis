@echo off
REM Launch script for UV Sheet Parser - Streamlit UI
REM This script installs dependencies (if needed) and launches the app

echo.
echo =========================================
echo  UV Sheet Parser - Launching App
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

echo [1/2] Checking dependencies...
python -m pip install -q -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo [2/2] Launching UV Sheet Parser...
echo.
echo The app will open in your browser at: http://localhost:8501
echo Close the command window to stop the app.
echo.

python -m streamlit run streamlit_app.py

pause
