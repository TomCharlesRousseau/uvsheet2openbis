#!/bin/bash
# Setup script for UV Sheet Parser - Streamlit UI
# This script installs all dependencies

echo ""
echo "========================================="
echo "  UV Sheet Parser Streamlit UI Setup"
echo "========================================="
echo ""

# Check if Python is installed
python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.10+ from https://www.python.org"
    exit 1
fi

echo "[1/3] Installing required packages..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install packages"
    exit 1
fi

echo ""
echo "[2/3] Verifying installation..."
python3 -c "import streamlit; print(f'✓ Streamlit {streamlit.__version__}')"
python3 -c "import pandas; print(f'✓ Pandas installed')"
python3 -c "import openpyxl; print('✓ OpenPyXL installed')"
python3 -c "import pybis; print('✓ pybis installed')"
python3 -c "import keyring; print('✓ Keyring installed')"

echo ""
echo "[3/3] Setup configuration..."
if [ ! -f "config/settings.json" ]; then
    echo "Copying default configuration..."
    cp config/settings.json.example config/settings.json 2>/dev/null
    echo "Please edit config/settings.json with your openBIS URL and credentials"
fi

echo ""
echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo ""
echo "You can now run the UI with:"
echo "  streamlit run streamlit_app.py"
echo ""
