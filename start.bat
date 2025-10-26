@echo off
REM Voice-to-ISL Translation System - Windows Startup Script
REM Compatible with Windows 10/11

setlocal enabledelayedexpansion

REM Configuration
set BACKEND_PORT=8000
set FRONTEND_PORT=3000
set PYTHON_MIN_VERSION=3.9
set NODE_MIN_VERSION=16

echo.
echo 🚀 Voice-to-ISL Translation System Startup
echo ======================================

REM Function to check if command exists
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    where python3 >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Python not found. Please install Python %PYTHON_MIN_VERSION% or higher.
        echo    Download from: https://www.python.org/downloads/
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

REM Check Python version
echo 🐍 Checking Python installation...
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found

REM Check Node.js
echo 📦 Checking Node.js installation...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js not found. Please install Node.js %NODE_MIN_VERSION% or higher.
    echo    Download from: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=1" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js %NODE_VERSION% found

REM Cleanup existing processes
echo 🧹 Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%BACKEND_PORT%') do taskkill /PID %%a /F >nul 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%FRONTEND_PORT%') do taskkill /PID %%a /F >nul 2>nul

REM Setup backend
echo 🔧 Setting up backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo   Creating Python virtual environment...
    %PYTHON_CMD% -m venv venv
)

REM Activate virtual environment and install dependencies
echo   Activating virtual environment...
call venv\Scripts\activate.bat

echo   Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

echo   Installing Python dependencies...
pip install -r requirements.txt >nul 2>&1

echo ✅ Backend setup complete
cd ..

REM Setup frontend
echo 🎨 Setting up frontend...
cd frontend

echo   Installing Node.js dependencies...
call npm install >nul 2>&1

echo ✅ Frontend setup complete
cd ..

REM Start backend
echo 🚀 Starting backend server...
cd backend
call venv\Scripts\activate.bat
echo   FastAPI server starting on http://localhost:%BACKEND_PORT%
start /B "" uvicorn main:app --reload --host 0.0.0.0 --port %BACKEND_PORT%

REM Wait for backend to start
echo   Waiting for backend to be ready...
:wait_backend
timeout /t 1 /nobreak >nul
curl -s http://localhost:%BACKEND_PORT%/health >nul 2>&1
if %ERRORLEVEL% NEQ 0 goto wait_backend

echo ✅ Backend server ready
cd ..

REM Start frontend
echo 🎨 Starting frontend server...
cd frontend
echo   React development server starting on http://localhost:%FRONTEND_PORT%
start /B "" npm start

REM Wait for frontend to start
echo   Waiting for frontend to be ready...
timeout /t 5 /nobreak >nul

echo ✅ Frontend server ready
cd ..

REM Open browser
echo 🌐 Opening application in browser...
timeout /t 3 /nobreak >nul
start http://localhost:%FRONTEND_PORT%

REM Show status
echo.
echo 🎉 Voice-to-ISL Translation System is now running!
echo ===========================================
echo 📊 Backend API:     http://localhost:%BACKEND_PORT%
echo 📊 API Docs:        http://localhost:%BACKEND_PORT%/api/docs
echo 📊 Health Check:    http://localhost:%BACKEND_PORT%/health
echo 🖥️  Frontend App:    http://localhost:%FRONTEND_PORT%
echo.
echo 📝 To stop the application:
echo    Run: stop.bat
echo.
echo Press any key to stop all services...
pause >nul

REM Cleanup on exit
call stop.bat
