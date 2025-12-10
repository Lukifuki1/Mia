@echo off
REM 🚀 MIA Enterprise AGI - Windows Start Script
REM ==============================================
REM Universal launcher script for Windows systems.
REM Automatically detects system and starts MIA in optimal configuration.

setlocal enabledelayedexpansion

REM Colors (limited in Windows CMD)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "PURPLE=[95m"
set "CYAN=[96m"
set "NC=[0m"

REM Banner
echo %CYAN%
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🧠 MIA Enterprise AGI                     ║
echo ║                  Windows Start Script                        ║
echo ║                                                              ║
echo ║  🚀 Automatic system detection and optimization             ║
echo ║  🌐 Web, Desktop, and Enterprise modes                      ║
echo ║  🔧 Intelligent configuration management                    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo %NC%

REM Function to detect Python
:detect_python
echo %BLUE%🔍 Detecting Python...%NC%
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo %GREEN%✅ Found Python !PYTHON_VERSION!%NC%
    goto :check_dependencies
)

python3 --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python3
    for /f "tokens=2" %%i in ('python3 --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo %GREEN%✅ Found Python !PYTHON_VERSION!%NC%
    goto :check_dependencies
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py
    for /f "tokens=2" %%i in ('py --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo %GREEN%✅ Found Python !PYTHON_VERSION!%NC%
    goto :check_dependencies
)

echo %RED%❌ Python not found. Please install Python 3.8+%NC%
pause
exit /b 1

:check_dependencies
echo %BLUE%🔍 Checking dependencies...%NC%

if not exist "requirements.txt" (
    echo %YELLOW%⚠️ requirements.txt not found%NC%
    goto :detect_system
)

echo %GREEN%✅ Requirements file found%NC%

REM Check if virtual environment exists
if not exist "venv" if not exist ".venv" (
    echo %YELLOW%💡 Creating virtual environment...%NC%
    %PYTHON_CMD% -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    echo %GREEN%✅ Virtual environment found%NC%
    if exist "venv" (
        call venv\Scripts\activate.bat
    ) else (
        call .venv\Scripts\activate.bat
    )
)

:detect_system
echo %BLUE%🖥️ Detecting system capabilities...%NC%
echo %GREEN%✅ Windows system detected%NC%

REM Set default ports
set WEB_PORT=12000
set API_PORT=8000

REM Check if ports are in use (simplified check)
netstat -an | findstr ":12000 " >nul 2>&1
if %errorlevel% == 0 (
    echo %YELLOW%⚠️ Port 12000 is in use%NC%
    set WEB_PORT=12002
)

netstat -an | findstr ":8000 " >nul 2>&1
if %errorlevel% == 0 (
    echo %YELLOW%⚠️ Port 8000 is in use%NC%
    set API_PORT=8001
)

echo %GREEN%✅ Web port: !WEB_PORT!, API port: !API_PORT!%NC%

:show_menu
echo %PURPLE%
echo 🎯 Select MIA Enterprise AGI Mode:
echo ==================================
echo 1) 🏢 Enterprise Mode (Full features)
echo 2) 🌐 Web Mode (Web interface only)
echo 3) 🖥️ Desktop Mode (Desktop app only)
echo 4) 🔄 Hybrid Mode (Web + Desktop)
echo 5) 🚀 Quick Start (Minimal features)
echo 6) 🧪 Test Mode (System validation)
echo 7) 🔧 Development Mode (Debug enabled)
echo 8) 🏭 Production Mode (Optimized)
echo 9) ⚡ Minimal Mode (Basic features)
echo 0) ❓ Custom Mode (Manual configuration)
echo %NC%

set /p choice="Enter your choice (1-9, 0 for custom): "

:start_mia
echo %GREEN%🚀 Starting MIA Enterprise AGI...%NC%

REM Create data directories
if not exist "mia_data" mkdir mia_data
if not exist "mia_data\enterprise" mkdir mia_data\enterprise
if not exist "mia_data\desktop" mkdir mia_data\desktop
if not exist "mia_data\models" mkdir mia_data\models
if not exist "mia_data\projects" mkdir mia_data\projects
if not exist "mia_data\logs" mkdir mia_data\logs

REM Start MIA based on choice
if "%choice%"=="1" (
    echo %GREEN%🏢 Starting Enterprise Mode...%NC%
    %PYTHON_CMD% mia_enterprise_agi.py --mode enterprise --web-port !WEB_PORT! --api-port !API_PORT!
) else if "%choice%"=="2" (
    echo %GREEN%🌐 Starting Web Mode...%NC%
    %PYTHON_CMD% mia_enterprise_agi.py --web-only --web-port !WEB_PORT! --api-port !API_PORT!
) else if "%choice%"=="3" (
    echo %GREEN%🖥️ Starting Desktop Mode...%NC%
    %PYTHON_CMD% mia_enterprise_agi.py --desktop-only --desktop-port !WEB_PORT!
) else if "%choice%"=="4" (
    echo %GREEN%🔄 Starting Hybrid Mode...%NC%
    %PYTHON_CMD% mia_enterprise_agi.py --mode hybrid --web-port !WEB_PORT! --api-port !API_PORT!
) else if "%choice%"=="5" (
    echo %GREEN%🚀 Starting Quick Start Mode...%NC%
    %PYTHON_CMD% mia_enterprise_agi.py --quick-start --web-port !WEB_PORT! --api-port !API_PORT!
) else if "%choice%"=="6" (
    echo %GREEN%🧪 Starting Test Mode...%NC%
    %PYTHON_CMD% mia_enterprise_agi.py --test
) else if "%choice%"=="7" (
    echo %GREEN%🔧 Starting Development Mode...%NC%
    %PYTHON_CMD% mia_enterprise_agi.py --mode development --log-level DEBUG --web-port !WEB_PORT! --api-port !API_PORT!
) else if "%choice%"=="8" (
    echo %GREEN%🏭 Starting Production Mode...%NC%
    %PYTHON_CMD% mia_enterprise_agi.py --mode production --web-port !WEB_PORT! --api-port !API_PORT!
) else if "%choice%"=="9" (
    echo %GREEN%⚡ Starting Minimal Mode...%NC%
    %PYTHON_CMD% mia_enterprise_agi.py --minimal --web-port !WEB_PORT! --api-port !API_PORT!
) else if "%choice%"=="0" (
    echo %CYAN%💡 Custom mode - you can add any arguments:%NC%
    set /p custom_args="Enter custom arguments: "
    %PYTHON_CMD% mia_enterprise_agi.py !custom_args!
) else (
    echo %RED%❌ Invalid choice%NC%
    pause
    exit /b 1
)

REM Handle command line arguments
if "%1"=="--help" (
    echo MIA Enterprise AGI Windows Start Script
    echo Usage: %0 [mode]
    echo.
    echo Modes:
    echo   --enterprise    Enterprise mode (default)
    echo   --web          Web interface only
    echo   --desktop      Desktop application only
    echo   --hybrid       Web + Desktop hybrid
    echo   --quick        Quick start mode
    echo   --test         Test mode
    echo   --development  Development mode
    echo   --production   Production mode
    echo   --minimal      Minimal features
    echo.
    echo Examples:
    echo   %0 --enterprise
    echo   %0 --web
    echo   %0 --test
    pause
    exit /b 0
)

if "%1"=="--enterprise" (
    %PYTHON_CMD% mia_enterprise_agi.py --mode enterprise --web-port !WEB_PORT! --api-port !API_PORT!
    goto :end
)

if "%1"=="--web" (
    %PYTHON_CMD% mia_enterprise_agi.py --web-only --web-port !WEB_PORT! --api-port !API_PORT!
    goto :end
)

if "%1"=="--desktop" (
    %PYTHON_CMD% mia_enterprise_agi.py --desktop-only --desktop-port !WEB_PORT!
    goto :end
)

if "%1"=="--hybrid" (
    %PYTHON_CMD% mia_enterprise_agi.py --mode hybrid --web-port !WEB_PORT! --api-port !API_PORT!
    goto :end
)

if "%1"=="--quick" (
    %PYTHON_CMD% mia_enterprise_agi.py --quick-start --web-port !WEB_PORT! --api-port !API_PORT!
    goto :end
)

if "%1"=="--test" (
    %PYTHON_CMD% mia_enterprise_agi.py --test
    goto :end
)

if "%1"=="--development" (
    %PYTHON_CMD% mia_enterprise_agi.py --mode development --log-level DEBUG --web-port !WEB_PORT! --api-port !API_PORT!
    goto :end
)

if "%1"=="--production" (
    %PYTHON_CMD% mia_enterprise_agi.py --mode production --web-port !WEB_PORT! --api-port !API_PORT!
    goto :end
)

if "%1"=="--minimal" (
    %PYTHON_CMD% mia_enterprise_agi.py --minimal --web-port !WEB_PORT! --api-port !API_PORT!
    goto :end
)

REM If no arguments, run interactive mode
if "%1"=="" goto :show_menu

:end
echo.
echo %YELLOW%👋 MIA Enterprise AGI session ended%NC%
pause