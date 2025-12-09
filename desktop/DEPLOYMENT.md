# MIA Enterprise AGI - Cross-Platform Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Git

### Installation
```bash
# Clone repository
git clone <repository-url>
cd mia-enterprise-agi

# Install desktop dependencies
cd desktop
npm install

# Build for current platform
npm run build
```

## 🖥️ Platform-Specific Builds

### Windows
```bash
# Build Windows installers
npm run build-win

# Output files:
# - dist/MIA Enterprise AGI Setup.exe (NSIS installer)
# - dist/MIA Enterprise AGI.msi (MSI installer)
# - dist/MIA Enterprise AGI.exe (Portable)
```

### macOS
```bash
# Build macOS installers
npm run build-mac

# Output files:
# - dist/MIA Enterprise AGI.dmg (DMG installer)
# - dist/MIA Enterprise AGI-mac.zip (ZIP archive)
```

### Linux
```bash
# Build Linux packages
npm run build-linux

# Output files:
# - dist/MIA Enterprise AGI.AppImage (AppImage)
# - dist/mia-enterprise-agi.deb (Debian package)
# - dist/mia-enterprise-agi.rpm (RPM package)
# - dist/mia-enterprise-agi.snap (Snap package)
# - dist/MIA Enterprise AGI.tar.gz (Archive)
```

### Universal Build
```bash
# Build for all platforms (requires appropriate OS or CI/CD)
npm run build-all
```

## 📦 Distribution

### Windows Distribution
1. **NSIS Installer**: Full installer with registry entries, shortcuts, uninstaller
2. **MSI Package**: Enterprise-friendly MSI for Group Policy deployment
3. **Portable**: Single executable, no installation required

### macOS Distribution
1. **DMG**: Standard macOS installer with drag-to-Applications
2. **ZIP**: Archive for manual installation
3. **App Store**: (Future) Mac App Store distribution

### Linux Distribution
1. **AppImage**: Universal Linux binary, no installation required
2. **DEB**: Debian/Ubuntu package manager
3. **RPM**: Red Hat/SUSE package manager
4. **Snap**: Universal Linux package
5. **Flatpak**: (Future) Flatpak distribution

## 🔧 Configuration

### Environment Variables
- `MIA_DESKTOP_MODE=1`: Enable desktop mode
- `MIA_PORT=8000`: Backend port
- `MIA_DATA_DIR`: Custom data directory
- `MIA_LOG_LEVEL`: Logging level (DEBUG, INFO, WARN, ERROR)

### Configuration Files
- `config/desktop.json`: Desktop-specific settings
- `config/mia.yaml`: Main MIA configuration
- User settings stored in OS-specific locations:
  - Windows: `%APPDATA%/MIA Enterprise AGI/`
  - macOS: `~/Library/Application Support/MIA Enterprise AGI/`
  - Linux: `~/.config/mia-enterprise-agi/`

## 🚀 Auto-Updates

### Setup
1. Configure update server in `package.json`
2. Generate code signing certificates
3. Upload releases to update server

### Update Process
1. App checks for updates on startup
2. Downloads updates in background
3. Prompts user to restart for installation
4. Automatic rollback on failure

## 🔐 Code Signing

### Windows
```bash
# Sign with certificate
signtool sign /f certificate.p12 /p password /t http://timestamp.digicert.com "MIA Enterprise AGI.exe"
```

### macOS
```bash
# Sign application
codesign --force --options runtime --sign "Developer ID Application: Your Name" "MIA Enterprise AGI.app"

# Notarize for Gatekeeper
xcrun notarytool submit "MIA Enterprise AGI.dmg" --keychain-profile "notarytool-profile"
```

### Linux
```bash
# Sign AppImage
gpg --armor --detach-sig "MIA Enterprise AGI.AppImage"
```

## 🏢 Enterprise Deployment

### Group Policy (Windows)
1. Deploy MSI via Group Policy
2. Configure registry settings
3. Set startup policies

### MDM (macOS)
1. Create configuration profile
2. Deploy via MDM solution
3. Configure security settings

### Package Managers (Linux)
1. Create repository packages
2. Deploy via configuration management
3. Set systemd services

## 🔍 Troubleshooting

### Common Issues
1. **Python not found**: Install Python 3.11+ or configure path
2. **Permission denied**: Run as administrator/sudo for system-wide install
3. **Antivirus blocking**: Add exception for MIA executable
4. **Port conflicts**: Change MIA_PORT environment variable

### Logs Location
- Windows: `%APPDATA%/MIA Enterprise AGI/logs/`
- macOS: `~/Library/Logs/MIA Enterprise AGI/`
- Linux: `~/.local/share/mia-enterprise-agi/logs/`

### Debug Mode
```bash
# Enable debug logging
export MIA_LOG_LEVEL=DEBUG

# Run with console output
./MIA\ Enterprise\ AGI --debug
```

## 📊 Monitoring

### System Requirements
- **Minimum**: 4GB RAM, 2 CPU cores, 10GB disk
- **Recommended**: 16GB RAM, 8 CPU cores, 50GB disk, GPU
- **Enterprise**: 32GB RAM, 16 CPU cores, 100GB disk, dedicated GPU

### Performance Monitoring
- Built-in system monitor
- Resource usage tracking
- Performance metrics export
- Health check endpoints

## 🔄 Updates & Maintenance

### Update Channels
- **Stable**: Production releases
- **Beta**: Pre-release testing
- **Alpha**: Development builds

### Maintenance Tasks
- Log rotation
- Cache cleanup
- Database optimization
- Model updates

## 📞 Support

### Documentation
- User Guide: https://docs.mia-enterprise-agi.com
- API Reference: https://api.mia-enterprise-agi.com
- Troubleshooting: https://support.mia-enterprise-agi.com

### Community
- GitHub Issues: Bug reports and feature requests
- Discord: Community support and discussions
- Forums: Technical discussions and tutorials

---

*MIA Enterprise AGI - Ultimate Local AI Platform*
