#!/usr/bin/env python3
"""
🖥️ MIA Enterprise AGI - Cross-Platform Desktop Builder
====================================================

Modularized cross-platform desktop application builder using dedicated modules.
"""

import json
import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import modularized components
from mia.desktop import (
    PlatformDetector,
    BuildSystem,
    DeploymentManager,
    CrossPlatformUtils
)


class CrossPlatformDesktopBuilder:
    """Modularized Cross-Platform Desktop Application Builder"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # Initialize modular components
        self.platform_detector = PlatformDetector()
        self.build_system = BuildSystem(self.platform_detector)
        self.deployment_manager = DeploymentManager(self.platform_detector)
        self.utils = CrossPlatformUtils()
        
        # Directory setup
        self.desktop_dir = Path("desktop")
        self.desktop_dir.mkdir(exist_ok=True)
        
        self.logger.info("🖥️ Modularized Cross-Platform Desktop Builder initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("MIA.DesktopBuilder")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def build_desktop_application(self, app_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build desktop application using modular components"""
        try:
            self.logger.info("🚀 Building desktop application...")
            
            # 1. Validate platform and environment
            platform_info = self.platform_detector.detect_platform()
            if not platform_info["is_supported"]:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform_info.get('normalized_os', 'unknown')}"
                }
            
            # 2. Validate build environment
            env_validation = self.platform_detector.validate_build_environment()
            if not env_validation["environment_ready"]:
                return {
                    "success": False,
                    "error": "Build environment not ready",
                    "recommendations": env_validation.get("recommendations", [])
                }
            
            # 3. Build application
            build_result = self.build_system.build_application(
                app_config,
                build_tool=app_config.get("build_tool", "pyinstaller"),
                target_platform=app_config.get("target_platform")
            )
            
            if not build_result["success"]:
                return build_result
            
            # 4. Create deployment package
            package_config = app_config.get("package", {})
            package_result = self.deployment_manager.create_package(
                build_result,
                package_config,
                app_config.get("target_platform")
            )
            
            if not package_result["success"]:
                return package_result
            
            # 5. Create installer (optional)
            installer_result = None
            if app_config.get("create_installer", False):
                installer_config = app_config.get("installer", {})
                installer_result = self.deployment_manager.create_installer(
                    package_result,
                    installer_config
                )
            
            # 6. Generate build report
            build_report = self._generate_build_report(
                platform_info,
                build_result,
                package_result,
                installer_result
            )
            
            return {
                "success": True,
                "platform_info": platform_info,
                "build_result": build_result,
                "package_result": package_result,
                "installer_result": installer_result,
                "build_report": build_report
            }
            
        except Exception as e:
            self.logger.error(f"Desktop application build error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_build_report(self, 
                              platform_info: Dict[str, Any],
                              build_result: Dict[str, Any],
                              package_result: Dict[str, Any],
                              installer_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive build report"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "platform": platform_info.get("normalized_os", "unknown"),
                "build_tool": build_result.get("build_tool", "unknown"),
                "package_format": package_result.get("package_format", "unknown"),
                "executable_size_mb": build_result.get("file_size_mb", 0),
                "package_size_mb": package_result.get("package_size_mb", 0),
                "build_time_seconds": 0,  # Could be calculated from timestamps
                "success": True
            }
            
            if installer_result:
                report["installer_format"] = installer_result.get("installer_format", "unknown")
                report["installer_size_mb"] = installer_result.get("installer_size_mb", 0)
            
            return report
            
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }


def main():
    """Main execution function"""
    print("🖥️ MIA Enterprise AGI - Cross-Platform Desktop Builder")
    print("=" * 60)
    
    builder = CrossPlatformDesktopBuilder()
    
    # Example application configuration
    app_config = {
        "name": "MIA",
        "version": "1.0.0",
        "main_script": "mia_main.py",  # This would need to exist
        "build_tool": "pyinstaller",
        "onefile": True,
        "console": False,
        "package": {
            "format": "zip"
        },
        "create_installer": False
    }
    
    # Check if main script exists, if not create a simple one
    main_script = Path(app_config["main_script"])
    if not main_script.exists():
        print(f"📝 Creating example main script: {main_script}")
        with open(main_script, 'w') as f:
            f.write('''#!/usr/bin/env python3
"""
MIA Enterprise AGI - Main Application
"""

import sys
from pathlib import Path

def main():
    print("🤖 MIA Enterprise AGI - Desktop Application")
    print("Local Digital Intelligence System")
    print("Version 1.0.0")
    
    # Keep application running
    try:
        input("Press Enter to exit...")
    except KeyboardInterrupt:
        print("\\n🛑 Application interrupted by user")
    print("👋 Goodbye!")

if __name__ == "__main__":
    main()
''')
    
    # Build application
    result = builder.build_desktop_application(app_config)
    
    # Display results
    print(f"\n📊 BUILD RESULTS:")
    print(f"Success: {'✅ YES' if result.get('success', False) else '❌ NO'}")
    
    if result.get("success", False):
        build_report = result.get("build_report", {})
        print(f"Platform: {build_report.get('platform', 'unknown')}")
        print(f"Build Tool: {build_report.get('build_tool', 'unknown')}")
        print(f"Package Format: {build_report.get('package_format', 'unknown')}")
        print(f"Package Size: {build_report.get('package_size_mb', 0):.2f} MB")
        
        if "package_result" in result:
            package_path = result["package_result"].get("package_path")
            if package_path:
                print(f"Package Location: {package_path}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        if "recommendations" in result:
            print("Recommendations:")
            for rec in result["recommendations"]:
                print(f"  - {rec}")
    
    return result


if __name__ == "__main__":
    main()
