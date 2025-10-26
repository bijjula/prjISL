#!/bin/bash
# Voice-to-ISL Translation System - One-time Setup Script
# Run this once to prepare your environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Voice-to-ISL Translation System Setup${NC}"
echo "======================================="

# Check if we're in the right directory
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    echo -e "${RED}❌ Please run this script from the project root directory${NC}"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
echo -e "${BLUE}🐍 Checking Python...${NC}"
PYTHON_CMD=""
if command_exists python3; then
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found. Please install Python 3.9+ first.${NC}"
    echo "   Download from: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Check Node.js
echo -e "${BLUE}📦 Checking Node.js...${NC}"
if ! command_exists node; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 16+ first.${NC}"
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node.js $NODE_VERSION found${NC}"

# Check npm
if ! command_exists npm; then
    echo -e "${RED}❌ npm not found. Please install Node.js with npm.${NC}"
    exit 1
fi

# Setup backend
echo -e "${BLUE}🔧 Setting up backend environment...${NC}"
cd backend

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo "Creating requirements.txt..."
    cat > requirements.txt << EOF
# FastAPI and ASGI server
fastapi>=0.100.0
uvicorn[standard]>=0.20.0

# Data validation and serialization
pydantic>=2.0.0

# HTTP client and file upload support
python-multipart>=0.0.6

# Testing and development
pytest>=7.0.0
httpx>=0.24.0
EOF
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate and install dependencies
echo "Installing Python dependencies..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✅ Backend environment ready${NC}"
cd ..

# Setup frontend
echo -e "${BLUE}🎨 Setting up frontend environment...${NC}"
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

echo -e "${GREEN}✅ Frontend environment ready${NC}"
cd ..

# Make scripts executable
echo -e "${BLUE}🔧 Making scripts executable...${NC}"
chmod +x start.sh stop.sh setup.sh

echo
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo "=================="
echo -e "${BLUE}To start the application:${NC}"
echo "  ./start.sh      (macOS/Linux)"
echo "  start.bat       (Windows)"
echo
echo -e "${BLUE}To stop the application:${NC}"
echo "  ./stop.sh       (macOS/Linux)"
echo "  stop.bat        (Windows)"
echo
echo -e "${YELLOW}💡 Next steps:${NC}"
echo "1. Run the start script to launch the application"
echo "2. Open http://localhost:3000 in your browser"
echo "3. Test the Voice-to-ISL translation workflow"
echo
