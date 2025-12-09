#!/bin/bash
# MIA Enterprise AGI - Deterministic macOS Build Script

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
BUILD_PLATFORM="macos"

echo "🔨 Starting deterministic macOS build..."
echo "Version: $BUILD_VERSION"
echo "Timestamp: $BUILD_TIMESTAMP"
echo "Platform: $BUILD_PLATFORM"

# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Install locked dependencies
pip install --no-cache-dir --no-deps -r requirements.lock

# Run deterministic tests
python -m pytest tests/ --tb=short

# Build application
python setup.py build --build-base=build/macos

# Create distribution
python setup.py bdist_wheel --dist-dir=dist/macos

# Generate deterministic DMG
python scripts/build_dmg.py --platform=macos --timestamp=$BUILD_TIMESTAMP

# Calculate build hash
BUILD_HASH=$(find dist/macos -name "*.whl" -exec shasum -a 256 {} \; | shasum -a 256 | cut -d' ' -f1)
echo "Build hash: $BUILD_HASH"

# Save build metadata
cat > build_metadata_macos.json << EOF
{
    "platform": "$BUILD_PLATFORM",
    "version": "$BUILD_VERSION",
    "timestamp": $BUILD_TIMESTAMP,
    "build_hash": "$BUILD_HASH",
    "built_at": "$(date -u -r $BUILD_TIMESTAMP +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "✅ macOS build completed successfully"
