@echo off
REM MIA Enterprise AGI - Silent Installation Script
REM Usage: install-silent.bat [/S] [/D=install_path]

echo Installing MIA Enterprise AGI silently...

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Administrator privileges required
    echo Please run as administrator
    pause
    exit /b 1
)

REM Default installation path
set INSTALL_PATH=%ProgramFiles%\MIA Enterprise Team\MIA Enterprise AGI

REM Parse command line arguments
:parse_args
if "%1"=="/D" (
    set INSTALL_PATH=%2
    shift
    shift
    goto parse_args
)
if "%1"=="/S" (
    set SILENT_MODE=1
    shift
    goto parse_args
)
if "%1"=="/?" (
    echo Usage: install-silent.bat [/S] [/D=install_path]
    echo   /S          Silent installation
    echo   /D=path     Installation directory
    exit /b 0
)
if not "%1"=="" (
    shift
    goto parse_args
)

REM Run installer silently
if defined SILENT_MODE (
    "MIA Enterprise AGI Setup.exe" /S /D="%INSTALL_PATH%"
) else (
    "MIA Enterprise AGI Setup.exe" /D="%INSTALL_PATH%"
)

if %errorLevel% equ 0 (
    echo Installation completed successfully
    
    REM Configure enterprise settings
    call configure-enterprise.bat
    
    REM Start service if requested
    if defined START_SERVICE (
        sc start "MIA Enterprise AGI Service"
    )
) else (
    echo Installation failed with error code %errorLevel%
    exit /b %errorLevel%
)

echo MIA Enterprise AGI installation completed
