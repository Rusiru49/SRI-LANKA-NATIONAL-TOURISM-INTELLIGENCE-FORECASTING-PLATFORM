#!/bin/bash

echo "========================================"
echo "Sri Lanka Tourism Platform Setup"
echo "========================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -e "\n${YELLOW}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.8 or higher${NC}"
    exit 1
fi

# Check Node.js
echo -e "\n${YELLOW}Checking Node.js installation...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js $NODE_VERSION found${NC}"
else
    echo -e "${RED}✗ Node.js not found. Please install Node.js 14 or higher${NC}"
    exit 1
fi

# Backend Setup
echo -e "\n${YELLOW}Setting up Backend...${NC}"
cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run data collection
echo -e "\n${YELLOW}Collecting tourism data...${NC}"
python data_collection.py

# Run preprocessing
echo -e "\n${YELLOW}Preprocessing data...${NC}"
python preprocessing.py

# Train models
echo -e "\n${YELLOW}Training ML models (this may take a few minutes)...${NC}"
python modeling.py

cd ..

# Frontend Setup
echo -e "\n${YELLOW}Setting up Frontend...${NC}"
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

echo -e "\n${GREEN}========================================"
echo "Setup completed successfully!"
echo "========================================${NC}"
echo ""
echo "To start the platform, run: ./scripts/run.sh"
echo "Or manually:"
echo "  1. Backend:  cd backend && source venv/bin/activate && python app.py"
echo "  2. Frontend: cd frontend && npm start"
echo ""