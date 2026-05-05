@echo off
REM UV Sheet Parser - Complete Setup & Launch in ONE Script
REM Just run this file and everything happens automatically

cls
color 0A
echo.
echo ========================================
echo UV Sheet Parser - Automated Setup
echo ========================================
echo.

REM Configuration
set INSTALL_PATH=C:\uvsheet2openbis
set REPO_URL=https://github.com/TomCharlesRousseau/uvsheet2openbis.git

REM Check if Python is installed
echo [1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo OK: Python %PYTHON_VER%
echo.

REM Check if Git is installed
echo [2/6] Checking Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git not found. Please install Git first.
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)
for /f "tokens=3" %%i in ('git --version 2^>^&1') do set GIT_VER=%%i
echo OK: Git %GIT_VER%
echo.

REM Clone or pull repo
echo [3/6] Setting up repository...
if exist "%INSTALL_PATH%" (
    echo Repository already exists. Updating...
    cd /d "%INSTALL_PATH%"
    git pull
) else (
    echo Cloning repository...
    git clone %REPO_URL% "%INSTALL_PATH%"
    if errorlevel 1 (
        echo ERROR: Failed to clone repository
        pause
        exit /b 1
    )
    cd /d "%INSTALL_PATH%"
)
echo OK: Repository ready at %INSTALL_PATH%
echo.

REM Install dependencies
echo [4/6] Installing Python packages (this may take 1-2 minutes)...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo OK: All packages installed
echo.

REM Verify installation
echo [5/6] Verifying installation...
python -c "import pandas, openpyxl, pybis, keyring, streamlit; print('OK: All packages loaded')"
if errorlevel 1 (
    echo ERROR: Package verification failed
    pause
    exit /b 1
)
echo.

REM Launch Streamlit
echo [6/6] Launching Streamlit app...
echo.
echo ========================================
echo SUCCESS! App launching...
echo ========================================
echo.
echo Opening: http://localhost:8501
echo.
echo To stop the app: Press Ctrl+C
echo.
timeout /t 2 /nobreak

python -m streamlit run streamlit_app.py

pause
