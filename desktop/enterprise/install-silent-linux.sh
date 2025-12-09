#!/bin/bash
# MIA Enterprise AGI - Silent Installation Script
# Usage: ./install-silent.sh [options]

set -e

INSTALL_PATH="/opt/mia-enterprise-agi"
SILENT_MODE=false
START_SERVICE=false
PACKAGE_TYPE="auto"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--silent)
            SILENT_MODE=true
            shift
            ;;
        -p|--path)
            INSTALL_PATH="$2"
            shift 2
            ;;
        -t|--type)
            PACKAGE_TYPE="$2"
            shift 2
            ;;
        --start-service)
            START_SERVICE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "  -s, --silent        Silent installation"
            echo "  -p, --path PATH     Installation directory"
            echo "  -t, --type TYPE     Package type (deb, rpm, appimage, auto)"
            echo "  --start-service     Start service after installation"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Installing MIA Enterprise AGI..."

# Detect package manager if auto
if [[ "$PACKAGE_TYPE" == "auto" ]]; then
    if command -v apt-get >/dev/null 2>&1; then
        PACKAGE_TYPE="deb"
    elif command -v yum >/dev/null 2>&1 || command -v dnf >/dev/null 2>&1; then
        PACKAGE_TYPE="rpm"
    else
        PACKAGE_TYPE="appimage"
    fi
fi

# Install based on package type
case $PACKAGE_TYPE in
    deb)
        if [[ -f "mia-enterprise-agi.deb" ]]; then
            dpkg -i mia-enterprise-agi.deb
            apt-get install -f -y
        else
            echo "ERROR: DEB package not found"
            exit 1
        fi
        ;;
    rpm)
        if [[ -f "mia-enterprise-agi.rpm" ]]; then
            if command -v dnf >/dev/null 2>&1; then
                dnf install -y mia-enterprise-agi.rpm
            else
                yum install -y mia-enterprise-agi.rpm
            fi
        else
            echo "ERROR: RPM package not found"
            exit 1
        fi
        ;;
    appimage)
        if [[ -f "MIA Enterprise AGI.AppImage" ]]; then
            mkdir -p "$INSTALL_PATH"
            cp "MIA Enterprise AGI.AppImage" "$INSTALL_PATH/"
            chmod +x "$INSTALL_PATH/MIA Enterprise AGI.AppImage"
            
            # Create desktop entry
            cat > /usr/share/applications/mia-enterprise-agi.desktop << EOF
[Desktop Entry]
Name=MIA Enterprise AGI
Comment=Ultimate Local AI Platform
Exec=$INSTALL_PATH/MIA Enterprise AGI.AppImage
Icon=mia-enterprise-agi
Terminal=false
Type=Application
Categories=Office;Development;
EOF
        else
            echo "ERROR: AppImage not found"
            exit 1
        fi
        ;;
    *)
        echo "ERROR: Unknown package type: $PACKAGE_TYPE"
        exit 1
        ;;
esac

# Configure enterprise settings
./configure-enterprise.sh

# Create systemd service if requested
if [[ "$START_SERVICE" == "true" ]]; then
    ./create-systemd-service.sh
fi

echo "MIA Enterprise AGI installation completed successfully"
