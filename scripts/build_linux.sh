#!/bin/bash
# MIA Enterprise AGI - Deterministic Linux Build Script

set -euo pipefail

# Set deterministic environment
export PYTHONHASHSEED=0
export SOURCE_DATE_EPOCH=1640995200
export TZ=UTC
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

# Build configuration
BUILD_VERSION="1.0.0"
BUILD_TIMESTAMP="1640995200"
BUILD_PLATFORM="linux"

echo "🔨 Starting deterministic Linux build..."
echo "Version: $BUILD_VERSION"
echo "Timestamp: $BUILD_TIMESTAMP"
echo "Platform: $BUILD_PLATFORM"

# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Install locked dependencies
pip install --no-cache-dir --no-deps -r requirements.lock


# Run deterministic loop test before build
echo "🔄 Running deterministic loop test..."
python scripts/test_deterministic_loop.py
if [ $? -ne 0 ]; then
    echo "❌ Deterministic loop test failed - aborting build"
    exit 1
fi
echo "✅ Deterministic loop test passed - proceeding with build"

# Run deterministic tests
python -m pytest tests/ --tb=short

# Build application
python setup.py build --build-base=build/linux

# Create distribution
python setup.py bdist_wheel --dist-dir=dist/linux

# Generate deterministic AppImage
python scripts/build_appimage.py --platform=linux --timestamp=$BUILD_TIMESTAMP

# Calculate build hash
BUILD_HASH=$(find dist/linux -name "*.whl" -exec sha256sum {} \; | sha256sum | cut -d' ' -f1)
echo "Build hash: $BUILD_HASH"

# Save build metadata
cat > build_metadata_linux.json << EOF
{
    "platform": "$BUILD_PLATFORM",
    "version": "$BUILD_VERSION",
    "timestamp": $BUILD_TIMESTAMP,
    "build_hash": "$BUILD_HASH",
    "built_at": "$(date -u -d @$BUILD_TIMESTAMP +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "✅ Linux build completed successfully"
