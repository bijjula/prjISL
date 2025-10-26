#!/bin/bash
# Voice-to-ISL Translation System - Stop Script
# Compatible with macOS, Linux, and Windows (with Git Bash/WSL)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000

echo -e "${BLUE}🛑 Voice-to-ISL Translation System Shutdown${NC}"
echo "======================================="

# Function to kill processes on a specific port
kill_port() {
    local port=$1
    local service_name=$2
    
    if command -v lsof >/dev/null 2>&1; then
        # Unix-like systems
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "${YELLOW}🔄 Stopping $service_name on port $port...${NC}"
            lsof -Pi :$port -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
            echo -e "${GREEN}✅ $service_name stopped${NC}"
        else
            echo -e "${BLUE}ℹ️  No $service_name process found on port $port${NC}"
        fi
    elif command -v netstat >/dev/null 2>&1 && command -v taskkill >/dev/null 2>&1; then
        # Windows systems
        local pid=$(netstat -ano | findstr :$port | findstr LISTENING | awk '{print $5}' | head -1)
        if [ ! -z "$pid" ]; then
            echo -e "${YELLOW}🔄 Stopping $service_name (PID: $pid)...${NC}"
            taskkill /PID $pid /F >/dev/null 2>&1 || true
            echo -e "${GREEN}✅ $service_name stopped${NC}"
        else
            echo -e "${BLUE}ℹ️  No $service_name process found on port $port${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Cannot detect processes on port $port. Please stop manually.${NC}"
    fi
}

# Function to cleanup Python virtual environment processes
cleanup_python_processes() {
    if command -v pkill >/dev/null 2>&1; then
        echo -e "${YELLOW}🐍 Cleaning up Python processes...${NC}"
        pkill -f "uvicorn.*main:app" 2>/dev/null || true
        pkill -f "python.*uvicorn" 2>/dev/null || true
    fi
}

# Function to cleanup Node.js processes
cleanup_node_processes() {
    if command -v pkill >/dev/null 2>&1; then
        echo -e "${YELLOW}📦 Cleaning up Node.js processes...${NC}"
        pkill -f "react-scripts.*start" 2>/dev/null || true
        pkill -f "node.*react-scripts" 2>/dev/null || true
    fi
}

# Main cleanup function
main() {
    # Kill processes on specific ports
    kill_port $BACKEND_PORT "Backend (FastAPI)"
    kill_port $FRONTEND_PORT "Frontend (React)"
    
    # Additional cleanup
    cleanup_python_processes
    cleanup_node_processes
    
    # Wait a moment for processes to terminate
    sleep 2
    
    echo
    echo -e "${GREEN}🎉 All Voice-to-ISL services have been stopped!${NC}"
    echo "============================================="
    echo -e "${BLUE}ℹ️  Ports $BACKEND_PORT and $FRONTEND_PORT are now available${NC}"
    echo
    
    # Verify ports are free
    if command -v lsof >/dev/null 2>&1; then
        if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1 || lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  Some processes may still be running. You may need to restart your terminal.${NC}"
        else
            echo -e "${GREEN}✅ All ports successfully freed${NC}"
        fi
    fi
}

main "$@"
