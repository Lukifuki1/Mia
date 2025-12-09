@echo off
REM MIA Enterprise AGI - Deterministic Windows Build Script

setlocal enabledelayedexpansion

REM Set deterministic environment
set PYTHONHASHSEED=0
set SOURCE_DATE_EPOCH=1640995200
set TZ=UTC

REM Build configuration
set BUILD_VERSION=1.0.0
set BUILD_TIMESTAMP=1640995200
set BUILD_PLATFORM=windows

echo 🔨 Starting deterministic Windows build...
echo Version: %BUILD_VERSION%
echo Timestamp: %BUILD_TIMESTAMP%
echo Platform: %BUILD_PLATFORM%

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
for /d %%i in (*.egg-info) do rmdir /s /q "%%i"

REM Install locked dependencies
pip install --no-cache-dir --no-deps -r requirements.lock

REM Run deterministic tests
python -m pytest tests/ --tb=short

REM Build application
python setup.py build --build-base=build/windows

REM Create distribution
python setup.py bdist_wheel --dist-dir=dist/windows

REM Generate deterministic MSI
python scripts/build_msi.py --platform=windows --timestamp=%BUILD_TIMESTAMP%

REM Calculate build hash
for /f %%i in ('dir /b dist\windows\*.whl') do (
    for /f %%j in ('certutil -hashfile "dist\windows\%%i" SHA256 ^| find /v ":" ^| find /v "CertUtil"') do set BUILD_HASH=%%j
)

echo Build hash: !BUILD_HASH!

REM Save build metadata
(
echo {
echo     "platform": "%BUILD_PLATFORM%",
echo     "version": "%BUILD_VERSION%",
echo     "timestamp": %BUILD_TIMESTAMP%,
echo     "build_hash": "!BUILD_HASH!",
echo     "built_at": "2022-01-01T00:00:00Z"
echo }
) > build_metadata_windows.json

echo ✅ Windows build completed successfully
