#!/bin/bash

# MIA Enterprise AGI - macOS Desktop Launcher
# Double-click this file to start MIA

# Change to script directory
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Clear screen and show banner
clear
echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                    🤖 MIA Enterprise AGI                     ║
║                  Desktop Application v1.0.0                 ║
║                                                              ║
║  🧠 Local Digital Intelligence System                       ║
║  🔍 Automatic Model Discovery                               ║
║  📚 Self-Learning from Local Models                         ║
║  🔒 Enterprise Security & Analytics                         ║
║  🌐 Web Interface & API Gateway                             ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${GREEN}🚀 Starting MIA Enterprise AGI on macOS...${NC}"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.8+ from:"
    echo "  - Official Python: https://python.org"
    echo "  - Homebrew: brew install python3"
    echo "  - MacPorts: sudo port install python39"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Python $PYTHON_VERSION found, but Python $REQUIRED_VERSION+ is required${NC}"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if Xcode Command Line Tools are installed (needed for some packages)
if ! xcode-select -p &> /dev/null; then
    echo -e "${YELLOW}⚠️  Xcode Command Line Tools not found${NC}"
    echo "Installing Xcode Command Line Tools (required for some packages)..."
    xcode-select --install
    echo "Please run this script again after installation completes."
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if required packages are installed
echo -e "${YELLOW}📦 Checking dependencies...${NC}"
python3 -c "import fastapi, uvicorn, psutil" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}📥 Installing required packages...${NC}"
    
    # Try to install with pip3
    pip3 install --user fastapi uvicorn psutil cryptography pyjwt pillow numpy
    
    # Check if installation was successful
    python3 -c "import fastapi, uvicorn, psutil" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install required packages${NC}"
        echo "Please install manually:"
        echo "  pip3 install fastapi uvicorn psutil cryptography pyjwt pillow numpy"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Create data directories
echo -e "${YELLOW}📁 Creating data directories...${NC}"
mkdir -p mia/data/{models,learning,analytics,security}
mkdir -p mia/logs

# Set permissions
chmod 755 mia/data
chmod 755 mia/logs

# Check for common model directories on macOS
echo -e "${YELLOW}🔍 Scanning for AI models in common macOS locations...${NC}"
MODEL_PATHS=(
    "$HOME/Downloads"
    "$HOME/Documents/AI_Models"
    "$HOME/Library/Application Support/LM Studio/models"
    "$HOME/Library/Application Support/Ollama/models"
    "/Applications/LM Studio.app/Contents/Resources/models"
    "/opt/homebrew/share/models"
    "/usr/local/share/models"
)

FOUND_MODELS=0
for path in "${MODEL_PATHS[@]}"; do
    if [ -d "$path" ]; then
        MODEL_COUNT=$(find "$path" -name "*.gguf" -o -name "*.bin" -o -name "*.safetensors" 2>/dev/null | wc -l)
        if [ $MODEL_COUNT -gt 0 ]; then
            echo -e "${GREEN}  ✓ Found $MODEL_COUNT model files in $path${NC}"
            FOUND_MODELS=$((FOUND_MODELS + MODEL_COUNT))
        fi
    fi
done

if [ $FOUND_MODELS -gt 0 ]; then
    echo -e "${GREEN}🎉 Discovered $FOUND_MODELS AI model files total${NC}"
else
    echo -e "${YELLOW}ℹ️  No AI models found in common locations${NC}"
    echo "   MIA will continue scanning for models in the background"
fi

echo
echo -e "${GREEN}🔧 Initializing MIA systems...${NC}"
echo -e "${BLUE}🌐 Web interface will be available at: http://localhost:12000${NC}"
echo -e "${BLUE}🔌 API gateway will be available at: http://localhost:8000${NC}"
echo
echo -e "${YELLOW}💡 Press Cmd+C to stop MIA${NC}"
echo -e "${YELLOW}💡 You can close this terminal window to run MIA in background${NC}"
echo

# Function to handle cleanup on exit
cleanup() {
    echo
    echo -e "${YELLOW}🛑 Stopping MIA Enterprise AGI...${NC}"
    echo -e "${GREEN}👋 MIA Enterprise AGI stopped${NC}"
    read -p "Press Enter to close..."
    exit 0
}

# Set trap to catch Ctrl+C
trap cleanup SIGINT SIGTERM

# Start MIA
python3 mia_main.py

# If we get here, the script ended normally
echo
echo -e "${GREEN}👋 MIA Enterprise AGI stopped${NC}"
read -p "Press Enter to close..."