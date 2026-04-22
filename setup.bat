@echo off
REM Setup script for UV Sheet Parser - Streamlit UI
REM This script installs all dependencies

echo.
echo =========================================
echo  UV Sheet Parser Streamlit UI Setup
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

echo [1/3] Installing required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo [2/3] Verifying installation...
python -c "import streamlit; print(f'✓ Streamlit {streamlit.__version__}')" && (
    python -c "import pandas; print(f'✓ Pandas {pd.__version__}')"
    python -c "import openpyxl; print('✓ OpenPyXL installed')"
    python -c "import pybis; print('✓ pybis installed')"
    python -c "import keyring; print('✓ Keyring installed')"
) || (
    echo WARNING: Some modules may not be properly installed
)

echo.
echo [3/3] Setup configuration...
if not exist "config\settings.json" (
    echo Copying default configuration...
    copy config\settings.json.example config\settings.json 2>nul
    echo Please edit config\settings.json with your openBIS URL and credentials
)

echo.
echo =========================================
echo  Setup Complete!
echo =========================================
echo.
echo You can now run the UI with:
echo   streamlit run streamlit_app.py
echo Or simply double-click: run_streamlit.bat
echo.
pause
