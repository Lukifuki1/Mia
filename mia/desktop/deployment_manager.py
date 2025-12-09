import time
import base64
from datetime import datetime
#!/usr/bin/env python3
"""
MIA Enterprise AGI - Deployment Manager
======================================

Cross-platform deployment and distribution system.
"""

import os
import sys
import subprocess
import shutil
import logging
import zipfile
import tarfile
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import tempfile


class DeploymentManager:
    """Cross-platform deployment manager"""
    
    def __init__(self, platform_detector=None):
        self.logger = self._setup_logging()
        self.platform_detector = platform_detector
        
        # Deployment configuration
        self.deploy_dir = Path("desktop/deploy")
        self.packages_dir = Path("desktop/packages")
        self.installers_dir = Path("desktop/installers")
        
        # Create directories
        for dir_path in [self.deploy_dir, self.packages_dir, self.installers_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.package_formats = {
            "windows": ["msi", "exe", "zip"],
            "darwin": ["dmg", "pkg", "zip"],
            "linux": ["deb", "rpm", "appimage", "tar.gz"]
        }
        
        self.logger.info("📦 Deployment Manager initialized")
    

    def deploy_application(self, build_artifacts: List[str], deployment_config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy application to target environment"""
        try:
            deployment_result = {
                "success": True,
                "deployment_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "deployed_artifacts": [],
                "deployment_path": "",
                "status": "deployed"
            }
            
            # Create deployment directory
            deploy_dir = Path(f"deployments/{deployment_config.get('name', 'app')}")
            deploy_dir.mkdir(parents=True, exist_ok=True)
            deployment_result["deployment_path"] = str(deploy_dir)
            
            # Deploy each artifact
            for artifact in build_artifacts:
                artifact_path = Path(artifact)
                if artifact_path.exists():
                    # Copy artifact to deployment directory
                    deployed_artifact = deploy_dir / artifact_path.name
                    deployed_artifact.write_bytes(artifact_path.read_bytes())
                    deployment_result["deployed_artifacts"].append(str(deployed_artifact))
            
            # Create deployment manifest
            manifest = {
                "app_name": deployment_config.get('name', 'app'),
                "version": deployment_config.get('version', '1.0.0'),
                "deployment_date": deployment_result["deployment_timestamp"],
                "artifacts": deployment_result["deployed_artifacts"]
            }
            
            manifest_file = deploy_dir / "deployment_manifest.json"
            import json
from .deterministic_helpers import deterministic_helpers
            manifest_file.write_text(json.dumps(manifest, indent=2))
            
            self.logger.info(f"🚀 Application deployed: {deployment_config.get('name', 'app')}")
            return deployment_result
            
        except Exception as e:
            self.logger.error(f"Application deployment error: {e}")
            return {
                "success": False,
                "error": str(e),
                "deployment_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.Desktop.DeploymentManager")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def create_package(self, 
                      build_result: Dict[str, Any],
                      package_config: Dict[str, Any],
                      target_platform: Optional[str] = None) -> Dict[str, Any]:
        """Create deployment package"""
        self.logger.info("📦 Creating deployment package...")
        
        try:
            # Validate inputs
            if not build_result.get("success", False):
                return {
                    "success": False,
                    "error": "Build result indicates failure"
                }
            
            executable_path = build_result.get("executable_path")
            if not executable_path or not Path(executable_path).exists():
                return {
                    "success": False,
                    "error": "Executable not found"
                }
            
            # Determine package format
            package_format = self._determine_package_format(package_config, target_platform)
            
            # Create package based on format
            package_result = self._create_package_by_format(
                executable_path, 
                package_config, 
                package_format,
                target_platform
            )
            
            return package_result
            
        except Exception as e:
            self.logger.error(f"Package creation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _determine_package_format(self, 
                                 config: Dict[str, Any], 
                                 target_platform: Optional[str]) -> str:
        """Determine appropriate package format"""
        # Use specified format if provided
        if "format" in config:
            return config["format"]
        
        # Use platform default
        platform_key = target_platform or (
            self.platform_detector.current_os if self.platform_detector else "linux"
        )
        
        platform_formats = self.package_formats.get(platform_key, ["zip"])
        return platform_formats[0]  # Use first (default) format
    
    def _create_package_by_format(self, 
                                 executable_path: Path,
                                 config: Dict[str, Any],
                                 package_format: str,
                                 target_platform: Optional[str]) -> Dict[str, Any]:
        """Create package based on format"""
        
        format_handlers = {
            "zip": self._create_zip_package,
            "tar.gz": self._create_tarball_package,
            "msi": self._create_msi_package,
            "dmg": self._create_dmg_package,
            "deb": self._create_deb_package,
            "rpm": self._create_rpm_package,
            "appimage": self._create_appimage_package
        }
        
        handler = format_handlers.get(package_format, self._create_zip_package)
        return handler(executable_path, config, target_platform)
    
    def _create_zip_package(self, 
                           executable_path: Path,
                           config: Dict[str, Any],
                           target_platform: Optional[str]) -> Dict[str, Any]:
        """Create ZIP package"""
        self.logger.info("📦 Creating ZIP package...")
        
        try:
            app_name = config.get("name", "MIA")
            version = config.get("version", "1.0.0")
            
            package_name = f"{app_name}-{version}-{target_platform or 'universal'}.zip"
            package_path = self.packages_dir / package_name
            
            with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add executable
                zipf.write(executable_path, executable_path.name)
                
                # Add additional files
                for file_path in config.get("additional_files", []):
                    file_path = Path(file_path)
                    if file_path.exists():
                        zipf.write(file_path, file_path.name)
                
                # Add documentation
                self._add_documentation_to_package(zipf, config)
            
            return {
                "success": True,
                "package_format": "zip",
                "package_path": package_path,
                "package_size_mb": round(package_path.stat().st_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            return {
                "success": False,
                "package_format": "zip",
                "error": str(e)
            }
    
    def _create_tarball_package(self, 
                               executable_path: Path,
                               config: Dict[str, Any],
                               target_platform: Optional[str]) -> Dict[str, Any]:
        """Create tar.gz package"""
        self.logger.info("📦 Creating tar.gz package...")
        
        try:
            app_name = config.get("name", "MIA")
            version = config.get("version", "1.0.0")
            
            package_name = f"{app_name}-{version}-{target_platform or 'universal'}.tar.gz"
            package_path = self.packages_dir / package_name
            
            with tarfile.open(package_path, 'w:gz') as tarf:
                # Add executable
                tarf.add(executable_path, executable_path.name)
                
                # Add additional files
                for file_path in config.get("additional_files", []):
                    file_path = Path(file_path)
                    if file_path.exists():
                        tarf.add(file_path, file_path.name)
            
            return {
                "success": True,
                "package_format": "tar.gz",
                "package_path": package_path,
                "package_size_mb": round(package_path.stat().st_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            return {
                "success": False,
                "package_format": "tar.gz",
                "error": str(e)
            }
    
    def _create_msi_package(self, 
                           executable_path: Path,
                           config: Dict[str, Any],
                           target_platform: Optional[str]) -> Dict[str, Any]:
        """Create MSI package for Windows"""
        self.logger.info("📦 Creating MSI package...")
        
        try:
            # Check if WiX Toolset is available
            try:
                subprocess.run(["candle", "-?"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {
                    "success": False,
                    "package_format": "msi",
                    "error": "WiX Toolset not available. Install WiX Toolset to create MSI packages."
                }
            
            # Create WiX source file
            wix_content = self._generate_wix_source(executable_path, config)
            wix_file = self.deploy_dir / "installer.wxs"
            
            with open(wix_file, 'w') as f:
                f.write(wix_content)
            
            # Compile with candle
            obj_file = self.deploy_dir / "installer.wixobj"
            candle_cmd = ["candle", "-out", str(obj_file), str(wix_file)]
            
            result = subprocess.run(candle_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return {
                    "success": False,
                    "package_format": "msi",
                    "error": f"Candle compilation failed: {result.stderr}"
                }
            
            # Link with light
            app_name = config.get("name", "MIA")
            version = config.get("version", "1.0.0")
            msi_file = self.packages_dir / f"{app_name}-{version}.msi"
            
            light_cmd = ["light", "-out", str(msi_file), str(obj_file)]
            
            result = subprocess.run(light_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return {
                    "success": False,
                    "package_format": "msi",
                    "error": f"Light linking failed: {result.stderr}"
                }
            
            # Cleanup
            wix_file.unlink(missing_ok=True)
            obj_file.unlink(missing_ok=True)
            
            return {
                "success": True,
                "package_format": "msi",
                "package_path": msi_file,
                "package_size_mb": round(msi_file.stat().st_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            return {
                "success": False,
                "package_format": "msi",
                "error": str(e)
            }
    
    def _create_dmg_package(self, 
                           executable_path: Path,
                           config: Dict[str, Any],
                           target_platform: Optional[str]) -> Dict[str, Any]:
        """Create DMG package for macOS"""
        self.logger.info("📦 Creating DMG package...")
        
        try:
            app_name = config.get("name", "MIA")
            version = config.get("version", "1.0.0")
            
            # Create app bundle structure
            app_bundle = self.deploy_dir / f"{app_name}.app"
            contents_dir = app_bundle / "Contents"
            macos_dir = contents_dir / "MacOS"
            resources_dir = contents_dir / "Resources"
            
            for dir_path in [macos_dir, resources_dir]:
                dir_path.mkdir(parents=True, exist_ok=True)
            
            # Copy executable
            shutil.copy2(executable_path, macos_dir / app_name)
            
            # Create Info.plist
            plist_content = self._generate_info_plist(config)
            with open(contents_dir / "Info.plist", 'w') as f:
                f.write(plist_content)
            
            # Create DMG
            dmg_file = self.packages_dir / f"{app_name}-{version}.dmg"
            
            hdiutil_cmd = [
                "hdiutil", "create",
                "-srcfolder", str(app_bundle),
                "-volname", app_name,
                "-format", "UDZO",
                str(dmg_file)
            ]
            
            result = subprocess.run(hdiutil_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return {
                    "success": False,
                    "package_format": "dmg",
                    "error": f"DMG creation failed: {result.stderr}"
                }
            
            # Cleanup
            shutil.rmtree(app_bundle, ignore_errors=True)
            
            return {
                "success": True,
                "package_format": "dmg",
                "package_path": dmg_file,
                "package_size_mb": round(dmg_file.stat().st_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            return {
                "success": False,
                "package_format": "dmg",
                "error": str(e)
            }
    
    def _create_deb_package(self, 
                           executable_path: Path,
                           config: Dict[str, Any],
                           target_platform: Optional[str]) -> Dict[str, Any]:
        """Create DEB package for Debian/Ubuntu"""
        self.logger.info("📦 Creating DEB package...")
        
        try:
            app_name = config.get("name", "mia").lower()
            version = config.get("version", "1.0.0")
            
            # Create package structure
            package_dir = self.deploy_dir / f"{app_name}_{version}"
            debian_dir = package_dir / "DEBIAN"
            usr_bin_dir = package_dir / "usr" / "bin"
            usr_share_dir = package_dir / "usr" / "share" / "applications"
            
            for dir_path in [debian_dir, usr_bin_dir, usr_share_dir]:
                dir_path.mkdir(parents=True, exist_ok=True)
            
            # Copy executable
            shutil.copy2(executable_path, usr_bin_dir / app_name)
            
            # Create control file
            control_content = self._generate_deb_control(config)
            with open(debian_dir / "control", 'w') as f:
                f.write(control_content)
            
            # Create desktop file
            desktop_content = self._generate_desktop_file(config)
            with open(usr_share_dir / f"{app_name}.desktop", 'w') as f:
                f.write(desktop_content)
            
            # Build package
            deb_file = self.packages_dir / f"{app_name}_{version}_amd64.deb"
            
            dpkg_cmd = ["dpkg-deb", "--build", str(package_dir), str(deb_file)]
            
            result = subprocess.run(dpkg_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return {
                    "success": False,
                    "package_format": "deb",
                    "error": f"DEB creation failed: {result.stderr}"
                }
            
            # Cleanup
            shutil.rmtree(package_dir, ignore_errors=True)
            
            return {
                "success": True,
                "package_format": "deb",
                "package_path": deb_file,
                "package_size_mb": round(deb_file.stat().st_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            return {
                "success": False,
                "package_format": "deb",
                "error": str(e)
            }
    
    def _create_rpm_package(self, 
                           executable_path: Path,
                           config: Dict[str, Any],
                           target_platform: Optional[str]) -> Dict[str, Any]:
        """Create RPM package for Red Hat/CentOS/Fedora"""
        self.logger.info("📦 Creating RPM package...")
        
        # For now, fall back to tar.gz for RPM
        return self._create_tarball_package(executable_path, config, target_platform)
    
    def _create_appimage_package(self, 
                                executable_path: Path,
                                config: Dict[str, Any],
                                target_platform: Optional[str]) -> Dict[str, Any]:
        """Create AppImage package for Linux"""
        self.logger.info("📦 Creating AppImage package...")
        
        # For now, fall back to tar.gz for AppImage
        return self._create_tarball_package(executable_path, config, target_platform)
    
    def _generate_wix_source(self, executable_path: Path, config: Dict[str, Any]) -> str:
        """Generate WiX source file for MSI"""
        app_name = config.get("name", "MIA")
        version = config.get("version", "1.0.0")
        manufacturer = config.get("manufacturer", "MIA Enterprise")
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
    <Product Id="*" Name="{app_name}" Language="1033" Version="{version}" 
             Manufacturer="{manufacturer}" UpgradeCode="{{12345678-1234-1234-1234-123456789012}}">
        <Package InstallerVersion="200" Compressed="yes" InstallScope="perMachine" />
        
        <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
        <MediaTemplate EmbedCab="yes" />
        
        <Feature Id="ProductFeature" Title="{app_name}" Level="1">
            <ComponentGroupRef Id="ProductComponents" />
        </Feature>
    </Product>
    
    <Fragment>
        <Directory Id="TARGETDIR" Name="SourceDir">
            <Directory Id="ProgramFilesFolder">
                <Directory Id="INSTALLFOLDER" Name="{app_name}" />
            </Directory>
        </Directory>
    </Fragment>
    
    <Fragment>
        <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
            <Component Id="MainExecutable">
                <File Source="{executable_path}" />
            </Component>
        </ComponentGroup>
    </Fragment>
</Wix>'''
    
    def _generate_info_plist(self, config: Dict[str, Any]) -> str:
        """Generate Info.plist for macOS app bundle"""
        app_name = config.get("name", "MIA")
        version = config.get("version", "1.0.0")
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.mia.{app_name.lower()}</string>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundleVersion</key>
    <string>{version}</string>
    <key>CFBundleShortVersionString</key>
    <string>{version}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>'''
    
    def _generate_deb_control(self, config: Dict[str, Any]) -> str:
        """Generate control file for DEB package"""
        app_name = config.get("name", "mia").lower()
        version = config.get("version", "1.0.0")
        description = config.get("description", "MIA Enterprise AGI Desktop Application")
        
        return f'''Package: {app_name}
Version: {version}
Section: utils
Priority: optional
Architecture: amd64
Maintainer: MIA Enterprise <support@mia-enterprise.com>
Description: {description}
 MIA Enterprise AGI is a local digital intelligence system
 with consciousness, emotion, and multimodal capabilities.
'''
    
    def _generate_desktop_file(self, config: Dict[str, Any]) -> str:
        """Generate .desktop file for Linux"""
        app_name = config.get("name", "MIA")
        description = config.get("description", "MIA Enterprise AGI")
        
        return f'''[Desktop Entry]
Version=1.0
Type=Application
Name={app_name}
Comment={description}
Exec={app_name.lower()}
Icon={app_name.lower()}
Terminal=false
Categories=Utility;
'''
    
    def _add_documentation_to_package(self, package_archive, config: Dict[str, Any]):
        """Add documentation files to package"""
        doc_files = ["README.md", "LICENSE", "CHANGELOG.md"]
        
        for doc_file in doc_files:
            doc_path = Path(doc_file)
            if doc_path.exists():
                if hasattr(package_archive, 'write'):  # ZIP file
                    package_archive.write(doc_path, doc_path.name)
                elif hasattr(package_archive, 'add'):  # TAR file
                    package_archive.add(doc_path, doc_path.name)
    
    def create_installer(self, 
                        package_result: Dict[str, Any],
                        installer_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create installer from package"""
        self.logger.info("🔧 Creating installer...")
        
        try:
            if not package_result.get("success", False):
                return {
                    "success": False,
                    "error": "Package creation failed"
                }
            
            package_path = package_result.get("package_path")
            if not package_path or not Path(package_path).exists():
                return {
                    "success": False,
                    "error": "Package file not found"
                }
            
            # For now, the package IS the installer for most formats
            # In the future, we could add custom installer wrappers
            
            return {
                "success": True,
                "installer_path": package_path,
                "installer_format": package_result.get("package_format"),
                "installer_size_mb": package_result.get("package_size_mb")
            }
            
        except Exception as e:
            self.logger.error(f"Installer creation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }