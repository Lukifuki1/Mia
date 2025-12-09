#!/bin/bash
echo "🍎 Building MIA Enterprise AGI for macOS..."

# Install dependencies
npm install

# Build for macOS
npm run build-mac

echo "✅ macOS build completed!"
echo "📦 Installers available in dist/ directory:"
echo "   - MIA Enterprise AGI.dmg (DMG installer)"
echo "   - MIA Enterprise AGI-mac.zip (ZIP archive)"
