@echo off
REM Voice-to-ISL Translation System - Windows Stop Script
REM Compatible with Windows 10/11

setlocal enabledelayedexpansion

REM Configuration
set BACKEND_PORT=8000
set FRONTEND_PORT=3000

echo.
echo 🛑 Voice-to-ISL Translation System Shutdown
echo =======================================

echo 🔄 Stopping Backend (FastAPI) on port %BACKEND_PORT%...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%BACKEND_PORT% ^| findstr LISTENING') do (
    echo   Terminating process PID %%a
    taskkill /PID %%a /F >nul 2>nul
)

echo 🔄 Stopping Frontend (React) on port %FRONTEND_PORT%...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%FRONTEND_PORT% ^| findstr LISTENING') do (
    echo   Terminating process PID %%a
    taskkill /PID %%a /F >nul 2>nul
)

echo 🐍 Cleaning up Python processes...
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq uvicorn*" >nul 2>nul
taskkill /F /IM "python.exe" /FI "COMMANDLINE eq *uvicorn*main:app*" >nul 2>nul

echo 📦 Cleaning up Node.js processes...
taskkill /F /IM "node.exe" /FI "COMMANDLINE eq *react-scripts*start*" >nul 2>nul

REM Wait for processes to terminate
timeout /t 2 /nobreak >nul

echo.
echo 🎉 All Voice-to-ISL services have been stopped!
echo =============================================
echo ℹ️  Ports %BACKEND_PORT% and %FRONTEND_PORT% are now available
echo.

REM Verify ports are free
netstat -ano | findstr :%BACKEND_PORT% | findstr LISTENING >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠️  Some processes may still be running on port %BACKEND_PORT%
) else (
    echo ✅ Port %BACKEND_PORT% successfully freed
)

netstat -ano | findstr :%FRONTEND_PORT% | findstr LISTENING >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠️  Some processes may still be running on port %FRONTEND_PORT%
) else (
    echo ✅ Port %FRONTEND_PORT% successfully freed
)

echo.
pause
