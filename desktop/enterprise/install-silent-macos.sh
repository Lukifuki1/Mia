#!/bin/bash
# MIA Enterprise AGI - Silent Installation Script
# Usage: ./install-silent.sh [options]

set -e

INSTALL_PATH="/Applications"
SILENT_MODE=false
START_SERVICE=false

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
        --start-service)
            START_SERVICE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "  -s, --silent        Silent installation"
            echo "  -p, --path PATH     Installation directory"
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

# Check for admin privileges
if [[ $EUID -ne 0 ]]; then
    echo "ERROR: Administrator privileges required"
    echo "Please run with sudo"
    exit 1
fi

# Mount DMG and install
DMG_FILE="MIA Enterprise AGI.dmg"
if [[ ! -f "$DMG_FILE" ]]; then
    echo "ERROR: $DMG_FILE not found"
    exit 1
fi

# Mount DMG
MOUNT_POINT=$(hdiutil attach "$DMG_FILE" | grep "/Volumes" | awk '{print $3}')
if [[ -z "$MOUNT_POINT" ]]; then
    echo "ERROR: Failed to mount DMG"
    exit 1
fi

# Copy application
cp -R "$MOUNT_POINT/MIA Enterprise AGI.app" "$INSTALL_PATH/"

# Unmount DMG
hdiutil detach "$MOUNT_POINT"

# Set permissions
chown -R root:admin "$INSTALL_PATH/MIA Enterprise AGI.app"
chmod -R 755 "$INSTALL_PATH/MIA Enterprise AGI.app"

# Configure enterprise settings
./configure-enterprise.sh

# Create launch daemon if requested
if [[ "$START_SERVICE" == "true" ]]; then
    ./create-launch-daemon.sh
fi

echo "MIA Enterprise AGI installation completed successfully"
