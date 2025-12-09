#!/bin/bash
echo "🌍 Building MIA Enterprise AGI for all platforms..."

# Install dependencies
npm install

# Build for all platforms
npm run build-all

echo "✅ Universal build completed!"
echo "📦 All installers available in dist/ directory"
