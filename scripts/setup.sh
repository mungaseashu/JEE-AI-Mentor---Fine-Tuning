#!/bin/bash
# ==============================================================================
# JEE MENTOR AI - AUTOMATED UNIX SETUP SCRIPT
# ==============================================================================
set -e

# ANSI Color Codes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${CYAN}🚀 Starting JEE Mentor AI Setup Wizard...${NC}"

# 1. Check for Python
if command -v python3 &>/dev/null; then
    python_version=$(python3 --version)
    echo -e "${GREEN}✅ Python detected: ${python_version}${NC}"
else
    echo -e "${RED}❌ Error: Python 3.8+ is required but was not found. Please install Python and try again.${NC}"
    exit 1
fi

# 2. Check for Node.js
if command -v npm &>/dev/null; then
    node_version=$(node --version)
    echo -e "${GREEN}✅ Node.js detected: ${node_version}${NC}"
else
    echo -e "${YELLOW}⚠️ Warning: Node.js (npm) was not found. Frontend development server requires Node.js.${NC}"
fi

# 3. Create Virtual Environment
if [ ! -d "venv" ]; then
    echo -e "${CYAN}📦 Creating Python virtual environment (venv)...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created.${NC}"
else
    echo -e "${NC}ℹ️ Virtual environment 'venv' already exists. Skipping creation.${NC}"
fi

# 4. Activate Venv and Install dependencies
echo -e "${CYAN}🔌 Installing Python backend dependencies (this might take a couple of minutes)...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Backend dependencies successfully installed.${NC}"

# 5. Handle environment configuration
if [ ! -f ".env" ]; then
    echo -e "${CYAN}📝 Copying environment variable template to '.env'...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Custom .env file initialized! You can customize database and model choices inside it.${NC}"
else
    echo -e "${NC}ℹ️ Custom '.env' file already exists. Skipping initialization.${NC}"
fi

# 6. Initialize Folder Structures
echo -e "${CYAN}📂 Ensuring directory structure matches clean architecture guidelines...${NC}"
mkdir -p backend frontend training rag dataset evaluation deployment docker scripts tests docs models/adapters data/chroma backend/plots
echo -e "${GREEN}✅ Folder structures successfully verified.${NC}"

echo -e "\n${MAGENTA}🎉 SETUP COMPLETED SUCCESSFULLY! 🎉${NC}"
echo -e "To start the application locally in development mode:"
echo -e "1. Activate virtual environment: ${YELLOW}source venv/bin/activate${NC}"
echo -e "2. Launch backend API: ${YELLOW}uvicorn backend.main:app --reload --port 8000${NC}"
echo -e "3. Setup and start Frontend: ${YELLOW}cd frontend; npm install; npm run dev${NC}"
echo -e "4. Alternatively, launch everything using multi-container Docker: ${YELLOW}docker-compose up --build${NC}"
