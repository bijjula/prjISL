#!/bin/bash
# Voice-to-ISL Translation System - Cross-Platform Startup Script
# Compatible with macOS, Linux, and Windows (with Git Bash/WSL)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
PYTHON_MIN_VERSION="3.9"
NODE_MIN_VERSION="16"

echo -e "${BLUE}🚀 Voice-to-ISL Translation System Startup${NC}"
echo "======================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to compare versions
version_compare() {
    if [[ $1 == $2 ]]; then
        return 0
    fi
    local IFS=.
    local i ver1=($1) ver2=($2)
    # fill empty fields in ver1 with zeros
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do
        ver1[i]=0
    done
    for ((i=0; i<${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            # fill empty fields in ver2 with zeros
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]})); then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]})); then
            return 2
        fi
    done
    return 0
}

# Function to kill processes on ports
cleanup_ports() {
    echo -e "${YELLOW}🧹 Cleaning up existing processes...${NC}"
    
    # Kill processes on backend port
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "  Stopping processes on port $BACKEND_PORT..."
        lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
    fi
    
    # Kill processes on frontend port
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "  Stopping processes on port $FRONTEND_PORT..."
        lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
    fi
    
    sleep 2
}

# Function to check Python version
check_python() {
    echo -e "${BLUE}🐍 Checking Python installation...${NC}"
    
    PYTHON_CMD=""
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Python not found. Please install Python $PYTHON_MIN_VERSION or higher.${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    
    version_compare $PYTHON_VERSION $PYTHON_MIN_VERSION
    case $? in
        0|1) echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}" ;;
        2) echo -e "${RED}❌ Python $PYTHON_VERSION is too old. Minimum required: $PYTHON_MIN_VERSION${NC}"; exit 1 ;;
    esac
    
    echo $PYTHON_CMD
}

# Function to check Node.js version
check_node() {
    echo -e "${BLUE}📦 Checking Node.js installation...${NC}"
    
    if ! command_exists node; then
        echo -e "${RED}❌ Node.js not found. Please install Node.js $NODE_MIN_VERSION or higher.${NC}"
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    
    if [ "$NODE_VERSION" -lt "$NODE_MIN_VERSION" ]; then
        echo -e "${RED}❌ Node.js $NODE_VERSION is too old. Minimum required: $NODE_MIN_VERSION${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Node.js v$NODE_VERSION found${NC}"
}

# Function to setup backend
setup_backend() {
    echo -e "${BLUE}🔧 Setting up backend...${NC}"
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "  Creating Python virtual environment..."
        $PYTHON_CMD -m venv venv
    fi
    
    # Activate virtual environment
    echo "  Activating virtual environment..."
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    # Upgrade pip
    echo "  Upgrading pip..."
    pip install --upgrade pip >/dev/null 2>&1
    
    # Install dependencies
    echo "  Installing Python dependencies..."
    pip install -r requirements.txt >/dev/null 2>&1
    
    echo -e "${GREEN}✅ Backend setup complete${NC}"
    cd ..
}

# Function to setup frontend
setup_frontend() {
    echo -e "${BLUE}🎨 Setting up frontend...${NC}"
    
    cd frontend
    
    # Install dependencies
    echo "  Installing Node.js dependencies..."
    npm install >/dev/null 2>&1
    
    echo -e "${GREEN}✅ Frontend setup complete${NC}"
    cd ..
}

# Function to start backend
start_backend() {
    echo -e "${BLUE}🚀 Starting backend server...${NC}"
    
    cd backend
    
    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    # Start FastAPI server in background
    echo "  FastAPI server starting on http://localhost:$BACKEND_PORT"
    uvicorn main:app --reload --host 0.0.0.0 --port $BACKEND_PORT >/dev/null 2>&1 &
    BACKEND_PID=$!
    
    # Wait for backend to start
    echo "  Waiting for backend to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:$BACKEND_PORT/health >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend server ready${NC}"
            cd ..
            return 0
        fi
        sleep 1
    done
    
    echo -e "${RED}❌ Backend server failed to start${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    cd ..
    exit 1
}

# Function to start frontend
start_frontend() {
    echo -e "${BLUE}🎨 Starting frontend server...${NC}"
    
    cd frontend
    
    # Start React development server in background
    echo "  React development server starting on http://localhost:$FRONTEND_PORT"
    npm start >/dev/null 2>&1 &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    echo "  Waiting for frontend to be ready..."
    for i in {1..60}; do
        if curl -s http://localhost:$FRONTEND_PORT >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Frontend server ready${NC}"
            cd ..
            return 0
        fi
        sleep 1
    done
    
    echo -e "${RED}❌ Frontend server failed to start${NC}"
    kill $FRONTEND_PID 2>/dev/null || true
    cd ..
    exit 1
}

# Function to open application in browser
open_browser() {
    echo -e "${BLUE}🌐 Opening application in browser...${NC}"
    
    # Detect OS and open browser
    case "$OSTYPE" in
        darwin*)  # macOS
            open http://localhost:$FRONTEND_PORT
            ;;
        linux*)   # Linux
            if command_exists xdg-open; then
                xdg-open http://localhost:$FRONTEND_PORT
            fi
            ;;
        msys*|win32*)  # Windows
            start http://localhost:$FRONTEND_PORT
            ;;
    esac
}

# Function to show status
show_status() {
    echo
    echo -e "${GREEN}🎉 Voice-to-ISL Translation System is now running!${NC}"
    echo "==========================================="
    echo -e "📊 ${BLUE}Backend API:${NC}     http://localhost:$BACKEND_PORT"
    echo -e "📊 ${BLUE}API Docs:${NC}        http://localhost:$BACKEND_PORT/api/docs"
    echo -e "📊 ${BLUE}Health Check:${NC}    http://localhost:$BACKEND_PORT/health"
    echo -e "🖥️  ${BLUE}Frontend App:${NC}    http://localhost:$FRONTEND_PORT"
    echo
    echo -e "${YELLOW}📝 To stop the application:${NC}"
    echo "   Press Ctrl+C or run: ./stop.sh"
    echo
    echo -e "${YELLOW}🔧 To view logs:${NC}"
    echo "   Backend logs: tail -f backend/logs/*.log"
    echo "   Frontend logs: Check browser developer console"
    echo
}

# Main execution
main() {
    # Check if help requested
    if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --clean        Clean install (removes node_modules and venv)"
        echo "  --no-browser   Don't open browser automatically"
        echo
        exit 0
    fi
    
    # Clean install if requested
    if [[ "$1" == "--clean" ]]; then
        echo -e "${YELLOW}🧹 Performing clean installation...${NC}"
        rm -rf backend/venv frontend/node_modules frontend/package-lock.json
    fi
    
    # Cleanup existing processes
    cleanup_ports
    
    # Check prerequisites
    PYTHON_CMD=$(check_python)
    check_node
    
    # Setup environment
    setup_backend
    setup_frontend
    
    # Start services
    start_backend
    start_frontend
    
    # Open browser unless --no-browser flag is used
    if [[ "$1" != "--no-browser" ]] && [[ "$2" != "--no-browser" ]]; then
        sleep 3  # Give frontend time to fully load
        open_browser
    fi
    
    # Show status
    show_status
    
    # Keep script running and handle shutdown
    trap 'echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"; ./stop.sh; exit 0' INT TERM
    
    # Wait for user interrupt
    echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"
    while true; do
        sleep 1
    done
}

# Run main function with all arguments
main "$@"
