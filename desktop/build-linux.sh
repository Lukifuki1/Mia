#!/bin/bash
echo "🐧 Building MIA Enterprise AGI for Linux..."

# Install dependencies
npm install

# Build for Linux
npm run build-linux

echo "✅ Linux build completed!"
echo "📦 Installers available in dist/ directory:"
echo "   - MIA Enterprise AGI.AppImage (AppImage)"
echo "   - mia-enterprise-agi.deb (Debian package)"
echo "   - mia-enterprise-agi.rpm (RPM package)"
echo "   - mia-enterprise-agi.snap (Snap package)"
echo "   - MIA Enterprise AGI.tar.gz (Archive)"
