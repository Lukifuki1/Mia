@echo off
title MIA Enterprise AGI - Desktop Application
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🤖 MIA Enterprise AGI                     ║
echo ║                  Desktop Application v1.0.0                 ║
echo ║                                                              ║
echo ║  🧠 Local Digital Intelligence System                       ║
echo ║  🔍 Automatic Model Discovery                               ║
echo ║  📚 Self-Learning from Local Models                         ║
echo ║  🔒 Enterprise Security ^& Analytics                         ║
echo ║  🌐 Web Interface ^& API Gateway                             ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🚀 Starting MIA Enterprise AGI...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo 📦 Checking dependencies...
python -c "import fastapi, uvicorn, psutil" >nul 2>&1
if errorlevel 1 (
    echo 📥 Installing required packages...
    pip install fastapi uvicorn psutil cryptography pyjwt pillow numpy
)

REM Create data directories
if not exist "mia\data\models" mkdir "mia\data\models"
if not exist "mia\data\learning" mkdir "mia\data\learning"
if not exist "mia\data\analytics" mkdir "mia\data\analytics"
if not exist "mia\data\security" mkdir "mia\data\security"
if not exist "mia\logs" mkdir "mia\logs"

echo.
echo 🔧 Initializing MIA systems...
echo 🌐 Web interface will be available at: http://localhost:12000
echo 🔌 API gateway will be available at: http://localhost:8000
echo.
echo 💡 Press Ctrl+C to stop MIA
echo.

REM Start MIA
python mia_main.py

echo.
echo 👋 MIA Enterprise AGI stopped
pause