@echo off
echo 🖥️ Building MIA Enterprise AGI for Windows...

REM Install dependencies
call npm install

REM Build for Windows
call npm run build-win

echo ✅ Windows build completed!
echo 📦 Installers available in dist/ directory:
echo    - MIA Enterprise AGI Setup.exe (NSIS installer)
echo    - MIA Enterprise AGI.msi (MSI installer)
echo    - MIA Enterprise AGI.exe (Portable)

pause
