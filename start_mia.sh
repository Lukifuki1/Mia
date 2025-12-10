#!/bin/bash
"""
🚀 MIA Enterprise AGI - Universal Start Script
==============================================

Universal launcher script for all platforms and modes.
Automatically detects system and starts MIA in optimal configuration.
"""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🧠 MIA Enterprise AGI                     ║"
echo "║                  Universal Start Script                      ║"
echo "║                                                              ║"
echo "║  🚀 Automatic system detection and optimization             ║"
echo "║  🌐 Web, Desktop, and Enterprise modes                      ║"
echo "║  🔧 Intelligent configuration management                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to detect Python
detect_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Python not found. Please install Python 3.8+${NC}"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}✅ Found Python $PYTHON_VERSION${NC}"
}

# Function to check dependencies
check_dependencies() {
    echo -e "${BLUE}🔍 Checking dependencies...${NC}"
    
    if [ ! -f "requirements.txt" ]; then
        echo -e "${YELLOW}⚠️ requirements.txt not found${NC}"
    else
        echo -e "${GREEN}✅ Requirements file found${NC}"
        
        # Check if virtual environment exists
        if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
            echo -e "${YELLOW}💡 Creating virtual environment...${NC}"
            $PYTHON_CMD -m venv venv
            source venv/bin/activate
            pip install -r requirements.txt
        else
            echo -e "${GREEN}✅ Virtual environment found${NC}"
            if [ -d "venv" ]; then
                source venv/bin/activate
            else
                source .venv/bin/activate
            fi
        fi
    fi
}

# Function to detect system capabilities
detect_system() {
    echo -e "${BLUE}🖥️ Detecting system capabilities...${NC}"
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        echo -e "${GREEN}✅ Linux system detected${NC}"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        echo -e "${GREEN}✅ macOS system detected${NC}"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
        echo -e "${GREEN}✅ Windows system detected${NC}"
    else
        OS="unknown"
        echo -e "${YELLOW}⚠️ Unknown OS: $OSTYPE${NC}"
    fi
    
    # Detect available ports
    if command -v netstat &> /dev/null; then
        if netstat -tuln | grep -q ":12000 "; then
            echo -e "${YELLOW}⚠️ Port 12000 is in use${NC}"
            WEB_PORT=12002
        else
            WEB_PORT=12000
        fi
        
        if netstat -tuln | grep -q ":8000 "; then
            echo -e "${YELLOW}⚠️ Port 8000 is in use${NC}"
            API_PORT=8001
        else
            API_PORT=8000
        fi
    else
        WEB_PORT=12000
        API_PORT=8000
    fi
    
    echo -e "${GREEN}✅ Web port: $WEB_PORT, API port: $API_PORT${NC}"
}

# Function to show menu
show_menu() {
    echo -e "${PURPLE}"
    echo "🎯 Select MIA Enterprise AGI Mode:"
    echo "=================================="
    echo "1) 🏢 Enterprise Mode (Full features)"
    echo "2) 🌐 Web Mode (Web interface only)"
    echo "3) 🖥️ Desktop Mode (Desktop app only)"
    echo "4) 🔄 Hybrid Mode (Web + Desktop)"
    echo "5) 🚀 Quick Start (Minimal features)"
    echo "6) 🧪 Test Mode (System validation)"
    echo "7) 🔧 Development Mode (Debug enabled)"
    echo "8) 🏭 Production Mode (Optimized)"
    echo "9) ⚡ Minimal Mode (Basic features)"
    echo "0) ❓ Custom Mode (Manual configuration)"
    echo -e "${NC}"
    
    read -p "Enter your choice (1-9, 0 for custom): " choice
}

# Function to start MIA
start_mia() {
    local mode=$1
    local extra_args=$2
    
    echo -e "${GREEN}🚀 Starting MIA Enterprise AGI in $mode mode...${NC}"
    
    # Create data directories
    mkdir -p mia_data/{enterprise,desktop,models,projects,logs}
    
    # Start MIA
    case $mode in
        "enterprise")
            $PYTHON_CMD mia_enterprise_agi.py --mode enterprise --web-port $WEB_PORT --api-port $API_PORT $extra_args
            ;;
        "web")
            $PYTHON_CMD mia_enterprise_agi.py --web-only --web-port $WEB_PORT --api-port $API_PORT $extra_args
            ;;
        "desktop")
            $PYTHON_CMD mia_enterprise_agi.py --desktop-only --desktop-port $WEB_PORT $extra_args
            ;;
        "hybrid")
            $PYTHON_CMD mia_enterprise_agi.py --mode hybrid --web-port $WEB_PORT --api-port $API_PORT $extra_args
            ;;
        "quick")
            $PYTHON_CMD mia_enterprise_agi.py --quick-start --web-port $WEB_PORT --api-port $API_PORT $extra_args
            ;;
        "test")
            $PYTHON_CMD mia_enterprise_agi.py --test $extra_args
            ;;
        "development")
            $PYTHON_CMD mia_enterprise_agi.py --mode development --log-level DEBUG --web-port $WEB_PORT --api-port $API_PORT $extra_args
            ;;
        "production")
            $PYTHON_CMD mia_enterprise_agi.py --mode production --web-port $WEB_PORT --api-port $API_PORT $extra_args
            ;;
        "minimal")
            $PYTHON_CMD mia_enterprise_agi.py --minimal --web-port $WEB_PORT --api-port $API_PORT $extra_args
            ;;
        "custom")
            echo -e "${CYAN}💡 Custom mode - you can add any arguments:${NC}"
            read -p "Enter custom arguments: " custom_args
            $PYTHON_CMD mia_enterprise_agi.py $custom_args
            ;;
        *)
            echo -e "${RED}❌ Invalid mode: $mode${NC}"
            exit 1
            ;;
    esac
}

# Main execution
main() {
    # Check if direct mode specified
    if [ $# -gt 0 ]; then
        case $1 in
            "--enterprise"|"-e")
                MODE="enterprise"
                ;;
            "--web"|"-w")
                MODE="web"
                ;;
            "--desktop"|"-d")
                MODE="desktop"
                ;;
            "--hybrid"|"-h")
                MODE="hybrid"
                ;;
            "--quick"|"-q")
                MODE="quick"
                ;;
            "--test"|"-t")
                MODE="test"
                ;;
            "--development"|"--dev")
                MODE="development"
                ;;
            "--production"|"-p")
                MODE="production"
                ;;
            "--minimal"|"-m")
                MODE="minimal"
                ;;
            "--help")
                echo "MIA Enterprise AGI Start Script"
                echo "Usage: $0 [mode] [extra_args...]"
                echo ""
                echo "Modes:"
                echo "  --enterprise, -e    Enterprise mode (default)"
                echo "  --web, -w          Web interface only"
                echo "  --desktop, -d      Desktop application only"
                echo "  --hybrid, -h       Web + Desktop hybrid"
                echo "  --quick, -q        Quick start mode"
                echo "  --test, -t         Test mode"
                echo "  --development      Development mode"
                echo "  --production, -p   Production mode"
                echo "  --minimal, -m      Minimal features"
                echo ""
                echo "Examples:"
                echo "  $0 --enterprise"
                echo "  $0 --web --log-level DEBUG"
                echo "  $0 --test"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Unknown option: $1${NC}"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
        
        # Get extra arguments
        shift
        EXTRA_ARGS="$@"
    else
        # Interactive mode
        detect_python
        check_dependencies
        detect_system
        show_menu
        
        case $choice in
            1) MODE="enterprise" ;;
            2) MODE="web" ;;
            3) MODE="desktop" ;;
            4) MODE="hybrid" ;;
            5) MODE="quick" ;;
            6) MODE="test" ;;
            7) MODE="development" ;;
            8) MODE="production" ;;
            9) MODE="minimal" ;;
            0) MODE="custom" ;;
            *) 
                echo -e "${RED}❌ Invalid choice${NC}"
                exit 1
                ;;
        esac
        
        EXTRA_ARGS=""
    fi
    
    # Ensure Python is detected
    if [ -z "$PYTHON_CMD" ]; then
        detect_python
    fi
    
    # Start MIA
    start_mia $MODE "$EXTRA_ARGS"
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}👋 MIA Enterprise AGI startup cancelled${NC}"; exit 0' INT

# Run main function
main "$@"