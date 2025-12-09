import time
from datetime import datetime
#!/usr/bin/env python3
"""
MIA Enterprise AGI - Platform Detector
=====================================

Cross-platform detection and configuration system.
"""

import os
import sys
import platform
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional


class PlatformDetector:
    """Platform detection and configuration system"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.current_os = platform.system().lower()
        self.supported_platforms = ["windows", "darwin", "linux"]
        
        # Platform-specific configurations
        self.platform_configs = {
            "windows": {
                "executable_extension": ".exe",
                "installer_format": "msi",
                "package_manager": "chocolatey",
                "shell": "cmd",
                "path_separator": "\\",
                "default_install_path": "C:\\Program Files\\MIA"
            },
            "darwin": {
                "executable_extension": "",
                "installer_format": "dmg",
                "package_manager": "homebrew",
                "shell": "bash",
                "path_separator": "/",
                "default_install_path": "/Applications/MIA.app"
            },
            "linux": {
                "executable_extension": "",
                "installer_format": "deb",
                "package_manager": "apt",
                "shell": "bash",
                "path_separator": "/",
                "default_install_path": "/opt/mia"
            }
        }
        
        self.logger.info(f"🔍 Platform Detector initialized for {self.current_os}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.Desktop.PlatformDetector")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def detect_platform(self) -> Dict[str, Any]:
        """Detect current platform and capabilities"""
        self.logger.info("🔍 Detecting platform capabilities...")
        
        try:
            # Basic platform info
            platform_info = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "architecture": platform.architecture(),
                "python_version": platform.python_version(),
                "python_implementation": platform.python_implementation()
            }
            
            # Platform-specific configuration
            config = self.platform_configs.get(self.current_os, {})
            
            # Detect available tools
            available_tools = self._detect_build_tools()
            
            # Detect system capabilities
            system_capabilities = self._detect_system_capabilities()
            
            return {
                "platform_info": platform_info,
                "platform_config": config,
                "available_tools": available_tools,
                "system_capabilities": system_capabilities,
                "is_supported": self.current_os in self.supported_platforms,
                "normalized_os": self.current_os
            }
            
        except Exception as e:
            self.logger.error(f"Platform detection error: {e}")
            return {
                "error": str(e),
                "is_supported": False,
                "normalized_os": "unknown"
            }
    
    def _detect_build_tools(self) -> Dict[str, bool]:
        """Detect available build tools"""
        tools = {
            "python": False,
            "pip": False,
            "pyinstaller": False,
            "nuitka": False,
            "cx_freeze": False,
            "auto_py_to_exe": False,
            "docker": False,
            "git": False,
            "node": False,
            "npm": False
        }
        
        for tool in tools.keys():
            try:
                result = subprocess.run(
                    [tool, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                tools[tool] = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                tools[tool] = False
        
        return tools
    
    def _detect_system_capabilities(self) -> Dict[str, Any]:
        """Detect system capabilities"""
        try:
            import psutil
            
            # Memory info
            memory = psutil.virtual_memory()
            
            # Disk info
            disk = psutil.disk_usage('/')
            
            # CPU info
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            capabilities = {
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "percent_used": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent_used": round((disk.used / disk.total) * 100, 2)
                },
                "cpu": {
                    "cores": cpu_count,
                    "frequency_mhz": cpu_freq.current if cpu_freq else None,
                    "max_frequency_mhz": cpu_freq.max if cpu_freq else None
                },
                "build_capable": memory.total >= 2 * (1024**3),  # At least 2GB RAM
                "packaging_capable": disk.free >= 5 * (1024**3)  # At least 5GB free space
            }
            
            return capabilities
            
        except ImportError:
            self.logger.warning("psutil not available, using basic capabilities")
            return {
                "memory": {"total_gb": "unknown"},
                "disk": {"free_gb": "unknown"},
                "cpu": {"cores": "unknown"},
                "build_capable": True,
                "packaging_capable": True
            }
        except Exception as e:
            self.logger.error(f"Capability detection error: {e}")
            return {
                "error": str(e),
                "build_capable": False,
                "packaging_capable": False
            }
    
    def get_platform_config(self, target_platform: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for target platform"""
        platform_key = target_platform or self.current_os
        
        if platform_key not in self.platform_configs:
            self.logger.warning(f"Unsupported platform: {platform_key}")
            return {}
        
        return self.platform_configs[platform_key].copy()
    
    def is_platform_supported(self, platform_name: str) -> bool:
        """Check if platform is supported"""
        return platform_name.lower() in self.supported_platforms
    
    def get_executable_name(self, base_name: str, target_platform: Optional[str] = None) -> str:
        """Get executable name for target platform"""
        config = self.get_platform_config(target_platform)
        extension = config.get("executable_extension", "")
        return f"{base_name}{extension}"
    
    def get_installer_format(self, target_platform: Optional[str] = None) -> str:
        """Get installer format for target platform"""
        config = self.get_platform_config(target_platform)
        return config.get("installer_format", "zip")
    
    def get_default_install_path(self, target_platform: Optional[str] = None) -> str:
        """Get default installation path for target platform"""
        config = self.get_platform_config(target_platform)
        return config.get("default_install_path", "/opt/mia")
    
    def validate_build_environment(self) -> Dict[str, Any]:
        """Validate build environment"""
        self.logger.info("🔧 Validating build environment...")
        
        try:
            platform_info = self.detect_platform()
            
            validation_results = {
                "platform_supported": platform_info["is_supported"],
                "build_tools_available": False,
                "system_capable": False,
                "recommendations": []
            }
            
            # Check build tools
            tools = platform_info.get("available_tools", {})
            essential_tools = ["python", "pip"]
            
            missing_tools = [tool for tool in essential_tools if not tools.get(tool, False)]
            
            if not missing_tools:
                validation_results["build_tools_available"] = True
            else:
                validation_results["recommendations"].extend([
                    f"Install missing tool: {tool}" for tool in missing_tools
                ])
            
            # Check system capabilities
            capabilities = platform_info.get("system_capabilities", {})
            
            if capabilities.get("build_capable", False) and capabilities.get("packaging_capable", False):
                validation_results["system_capable"] = True
            else:
                if not capabilities.get("build_capable", False):
                    validation_results["recommendations"].append("Increase system memory (minimum 2GB)")
                if not capabilities.get("packaging_capable", False):
                    validation_results["recommendations"].append("Free up disk space (minimum 5GB)")
            
            # Overall validation
            validation_results["environment_ready"] = (
                validation_results["platform_supported"] and
                validation_results["build_tools_available"] and
                validation_results["system_capable"]
            )
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Environment validation error: {e}")
            return {
                "environment_ready": False,
                "error": str(e),
                "recommendations": ["Fix environment validation errors"]
            }