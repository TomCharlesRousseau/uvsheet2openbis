#!/bin/bash
# UV Sheet Parser - Complete Setup & Launch in ONE Script (macOS/Linux)
# Just run: chmod +x setup_and_run.sh && ./setup_and_run.sh

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}UV Sheet Parser - Automated Setup${NC}"
echo -e "${GREEN}======================================${NC}\n"

# Configuration
INSTALL_PATH="$HOME/uvsheet2openbis"
REPO_URL="https://github.com/TomCharlesRousseau/uvsheet2openbis.git"

# Check if Python is installed
echo -e "${YELLOW}[1/6]${NC} Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 not found${NC}"
    echo "Install with: brew install python (macOS) or apt-get install python3 (Linux)"
    exit 1
fi
PYTHON_VER=$(python3 --version)
echo -e "${GREEN}OK${NC}: $PYTHON_VER\n"

# Check if Git is installed
echo -e "${YELLOW}[2/6]${NC} Checking Git..."
if ! command -v git &> /dev/null; then
    echo -e "${RED}ERROR: Git not found${NC}"
    echo "Install with: brew install git (macOS) or apt-get install git (Linux)"
    exit 1
fi
GIT_VER=$(git --version)
echo -e "${GREEN}OK${NC}: $GIT_VER\n"

# Clone or pull repo
echo -e "${YELLOW}[3/6]${NC} Setting up repository..."
if [ -d "$INSTALL_PATH" ]; then
    echo "Repository already exists. Updating..."
    cd "$INSTALL_PATH"
    git pull
else
    echo "Cloning repository..."
    git clone "$REPO_URL" "$INSTALL_PATH"
    cd "$INSTALL_PATH"
fi
echo -e "${GREEN}OK${NC}: Repository ready at $INSTALL_PATH\n"

# Install dependencies
echo -e "${YELLOW}[4/6]${NC} Installing Python packages (this may take 1-2 minutes)..."
python3 -m pip install --upgrade pip > /dev/null 2>&1
python3 -m pip install -r requirements.txt
echo -e "${GREEN}OK${NC}: All packages installed\n"

# Verify installation
echo -e "${YELLOW}[5/6]${NC} Verifying installation..."
python3 -c "import pandas, openpyxl, pybis, keyring, streamlit; print('OK: All packages loaded')"
echo ""

# Launch Streamlit
echo -e "${YELLOW}[6/6]${NC} Launching Streamlit app...\n"
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}SUCCESS! App launching...${NC}"
echo -e "${GREEN}======================================${NC}\n"
echo "Opening: http://localhost:8501"
echo "To stop the app: Press Ctrl+C"
echo ""

sleep 2
python3 -m streamlit run streamlit_app.py
