#!/bin/bash

# MIA Enterprise AGI - Linux Desktop Launcher
# Make this script executable: chmod +x start_mia_linux.sh

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

echo -e "${GREEN}🚀 Starting MIA Enterprise AGI...${NC}"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.8+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Python $PYTHON_VERSION found, but Python $REQUIRED_VERSION+ is required${NC}"
    exit 1
fi

# Check if required packages are installed
echo -e "${YELLOW}📦 Checking dependencies...${NC}"
python3 -c "import fastapi, uvicorn, psutil" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}📥 Installing required packages...${NC}"
    pip3 install --user fastapi uvicorn psutil cryptography pyjwt pillow numpy
    
    # Check if installation was successful
    python3 -c "import fastapi, uvicorn, psutil" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install required packages${NC}"
        echo "Please install manually: pip3 install fastapi uvicorn psutil cryptography pyjwt pillow numpy"
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

echo
echo -e "${GREEN}🔧 Initializing MIA systems...${NC}"
echo -e "${BLUE}🌐 Web interface will be available at: http://localhost:12000${NC}"
echo -e "${BLUE}🔌 API gateway will be available at: http://localhost:8000${NC}"
echo
echo -e "${YELLOW}💡 Press Ctrl+C to stop MIA${NC}"
echo

# Function to handle cleanup on exit
cleanup() {
    echo
    echo -e "${YELLOW}🛑 Stopping MIA Enterprise AGI...${NC}"
    echo -e "${GREEN}👋 MIA Enterprise AGI stopped${NC}"
    exit 0
}

# Set trap to catch Ctrl+C
trap cleanup SIGINT SIGTERM

# Start MIA
python3 mia_main.py

# If we get here, the script ended normally
echo
echo -e "${GREEN}👋 MIA Enterprise AGI stopped${NC}"