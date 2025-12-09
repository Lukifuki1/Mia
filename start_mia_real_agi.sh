#!/bin/bash

# 🧠 MIA Real AGI Startup Script
# ===============================

echo "🧠 Starting MIA Real AGI System..."
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if required packages are installed
echo "🔍 Checking AI packages..."
python3 -c "import torch, transformers, ollama, flask, flask_socketio" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing required AI packages..."
    pip install torch transformers accelerate datasets ollama openai flask flask-socketio beautifulsoup4
fi

# Start MIA Real AGI
echo "🚀 Launching MIA Real AGI..."
cd "$(dirname "$0")"
python3 mia_real_agi_chat.py

echo "✅ MIA Real AGI started successfully!"
echo "🌐 Open your browser to: http://localhost:12002"