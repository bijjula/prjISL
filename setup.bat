@echo off
REM Voice-to-ISL Translation System - Windows Setup Script
REM Run this once to prepare your environment

setlocal enabledelayedexpansion

echo.
echo 🔧 Voice-to-ISL Translation System Setup
echo =======================================

REM Check if we're in the right directory
if not exist "backend\main.py" (
    echo ❌ backend\main.py not found
    goto :error
)
if not exist "frontend\package.json" (
    echo ❌ frontend\package.json not found
    goto :error
)

REM Check Python
echo 🐍 Checking Python...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    where python3 >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Python not found. Please install Python 3.9+ first.
        echo    Download from: https://www.python.org/downloads/
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found

REM Check Node.js
echo 📦 Checking Node.js...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js not found. Please install Node.js 16+ first.
    echo    Download from: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=1" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js %NODE_VERSION% found

where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ npm not found. Please install Node.js with npm.
    pause
    exit /b 1
)

REM Setup backend
echo 🔧 Setting up backend environment...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo   Creating Python virtual environment...
    %PYTHON_CMD% -m venv venv
)

REM Activate and install dependencies
echo   Installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1

echo ✅ Backend environment ready
cd ..

REM Setup frontend
echo 🎨 Setting up frontend environment...
cd frontend

echo   Installing Node.js dependencies...
call npm install >nul 2>&1

echo ✅ Frontend environment ready
cd ..

echo.
echo 🎉 Setup Complete!
echo ==================
echo To start the application:
echo   start.bat       (Windows)
echo   .\start.sh      (Git Bash/WSL)
echo.
echo To stop the application:
echo   stop.bat        (Windows)
echo   .\stop.sh       (Git Bash/WSL)
echo.
echo 💡 Next steps:
echo 1. Run the start script to launch the application
echo 2. Open http://localhost:3000 in your browser
echo 3. Test the Voice-to-ISL translation workflow
echo.
pause
goto :eof

:error
echo ❌ Please run this script from the project root directory
echo    (The directory containing backend\ and frontend\ folders)
pause
exit /b 1
