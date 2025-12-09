import time
import base64
from datetime import datetime
#!/usr/bin/env python3
"""
MIA Enterprise AGI - Build System
================================

Cross-platform build system for desktop applications.
"""

import os
import sys
import subprocess
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import tempfile


class BuildSystem:
    """Cross-platform build system"""
    
    def __init__(self, platform_detector=None):
        self.logger = self._setup_logging()
        self.platform_detector = platform_detector
        
        # Build configuration
        self.build_dir = Path("desktop/build")
        self.dist_dir = Path("desktop/dist")
        self.assets_dir = Path("desktop/assets")
        
        # Create directories
        for dir_path in [self.build_dir, self.dist_dir, self.assets_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.build_tools = {
            "pyinstaller": self._build_with_pyinstaller,
            "nuitka": self._build_with_nuitka,
            "cx_freeze": self._build_with_cx_freeze
        }
        
        self.logger.info("🔨 Build System initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.Desktop.BuildSystem")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def build_application(self, 
                         app_config: Dict[str, Any],
                         build_tool: str = "pyinstaller",
                         target_platform: Optional[str] = None) -> Dict[str, Any]:
        """Build desktop application"""
        self.logger.info(f"🔨 Building application with {build_tool}...")
        
        try:
            # Validate build configuration
            validation_result = self._validate_build_config(app_config)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Invalid build configuration",
                    "details": validation_result["errors"]
                }
            
            # Select build tool
            if build_tool not in self.build_tools:
                return {
                    "success": False,
                    "error": f"Unsupported build tool: {build_tool}",
                    "available_tools": list(self.build_tools.keys())
                }
            
            # Prepare build environment
            build_env = self._prepare_build_environment(app_config, target_platform)
            
            # Execute build
            build_function = self.build_tools[build_tool]
            build_result = build_function(app_config, build_env)
            
            if build_result["success"]:
                # Post-process build
                post_process_result = self._post_process_build(build_result, app_config)
                build_result.update(post_process_result)
            
            return build_result
            
        except Exception as e:
            self.logger.error(f"Build error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_build_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate build configuration"""
        required_fields = ["name", "version", "main_script"]
        errors = []
        
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate main script exists
        if "main_script" in config:
            main_script = Path(config["main_script"])
            if not main_script.exists():
                errors.append(f"Main script not found: {main_script}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _prepare_build_environment(self, 
                                  config: Dict[str, Any], 
                                  target_platform: Optional[str]) -> Dict[str, Any]:
        """Prepare build environment"""
        self.logger.info("🔧 Preparing build environment...")
        
        # Get platform configuration
        platform_config = {}
        if self.platform_detector:
            platform_config = self.platform_detector.get_platform_config(target_platform)
        
        # Create build environment
        build_env = {
            "app_name": config["name"],
            "app_version": config["version"],
            "main_script": Path(config["main_script"]),
            "build_dir": self.build_dir,
            "dist_dir": self.dist_dir,
            "assets_dir": self.assets_dir,
            "platform_config": platform_config,
            "target_platform": target_platform,
            "additional_files": config.get("additional_files", []),
            "hidden_imports": config.get("hidden_imports", []),
            "exclude_modules": config.get("exclude_modules", []),
            "icon_file": config.get("icon_file"),
            "console": config.get("console", False),
            "onefile": config.get("onefile", True)
        }
        
        return build_env
    
    def _build_with_pyinstaller(self, config: Dict[str, Any], build_env: Dict[str, Any]) -> Dict[str, Any]:
        """Build with PyInstaller"""
        self.logger.info("🔨 Building with PyInstaller...")
        
        try:
            # Prepare PyInstaller command
            cmd = [
                "pyinstaller",
                "--clean",
                "--noconfirm",
                f"--distpath={build_env['dist_dir']}",
                f"--workpath={build_env['build_dir']}",
                f"--name={build_env['app_name']}"
            ]
            
            # Add options
            if build_env["onefile"]:
                cmd.append("--onefile")
            else:
                cmd.append("--onedir")
            
            if not build_env["console"]:
                cmd.append("--windowed")
            
            # Add icon
            if build_env["icon_file"]:
                icon_path = Path(build_env["icon_file"])
                if icon_path.exists():
                    cmd.extend(["--icon", str(icon_path)])
            
            # Add hidden imports
            for import_name in build_env["hidden_imports"]:
                cmd.extend(["--hidden-import", import_name])
            
            # Add additional files
            for file_path in build_env["additional_files"]:
                cmd.extend(["--add-data", f"{file_path};."])
            
            # Add main script
            cmd.append(str(build_env["main_script"]))
            
            # Execute PyInstaller
            self.logger.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            
            if result.returncode == 0:
                # Find built executable
                executable_path = self._find_built_executable(build_env)
                
                return {
                    "success": True,
                    "build_tool": "pyinstaller",
                    "executable_path": executable_path,
                    "build_output": result.stdout,
                    "build_warnings": result.stderr
                }
            else:
                return {
                    "success": False,
                    "build_tool": "pyinstaller",
                    "error": "PyInstaller build failed",
                    "build_output": result.stdout,
                    "build_errors": result.stderr
                }
                
        except Exception as e:
            return {
                "success": False,
                "build_tool": "pyinstaller",
                "error": str(e)
            }
    
    def _build_with_nuitka(self, config: Dict[str, Any], build_env: Dict[str, Any]) -> Dict[str, Any]:
        """Build with Nuitka"""
        self.logger.info("🔨 Building with Nuitka...")
        
        try:
            # Prepare Nuitka command
            cmd = [
                "nuitka",
                "--standalone" if not build_env["onefile"] else "--onefile",
                f"--output-dir={build_env['dist_dir']}",
                f"--output-filename={build_env['app_name']}"
            ]
            
            # Add options
            if not build_env["console"]:
                cmd.append("--windows-disable-console")
            
            # Add icon
            if build_env["icon_file"]:
                icon_path = Path(build_env["icon_file"])
                if icon_path.exists():
                    cmd.extend(["--windows-icon-from-ico", str(icon_path)])
            
            # Add hidden imports
            for import_name in build_env["hidden_imports"]:
                cmd.extend(["--include-module", import_name])
            
            # Add main script
            cmd.append(str(build_env["main_script"]))
            
            # Execute Nuitka
            self.logger.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            
            if result.returncode == 0:
                executable_path = self._find_built_executable(build_env)
                
                return {
                    "success": True,
                    "build_tool": "nuitka",
                    "executable_path": executable_path,
                    "build_output": result.stdout,
                    "build_warnings": result.stderr
                }
            else:
                return {
                    "success": False,
                    "build_tool": "nuitka",
                    "error": "Nuitka build failed",
                    "build_output": result.stdout,
                    "build_errors": result.stderr
                }
                
        except Exception as e:
            return {
                "success": False,
                "build_tool": "nuitka",
                "error": str(e)
            }
    
    def _build_with_cx_freeze(self, config: Dict[str, Any], build_env: Dict[str, Any]) -> Dict[str, Any]:
        """Build with cx_Freeze"""
        self.logger.info("🔨 Building with cx_Freeze...")
        
        try:
            # Create setup.py for cx_Freeze
            setup_content = self._generate_cx_freeze_setup(config, build_env)
            setup_path = Path("setup_cx_freeze.py")
            
            with open(setup_path, 'w') as f:
                f.write(setup_content)
            
            # Execute cx_Freeze
            cmd = [sys.executable, str(setup_path), "build"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            
            # Cleanup
            if setup_path.exists():
                setup_path.unlink()
            
            if result.returncode == 0:
                executable_path = self._find_built_executable(build_env)
                
                return {
                    "success": True,
                    "build_tool": "cx_freeze",
                    "executable_path": executable_path,
                    "build_output": result.stdout,
                    "build_warnings": result.stderr
                }
            else:
                return {
                    "success": False,
                    "build_tool": "cx_freeze",
                    "error": "cx_Freeze build failed",
                    "build_output": result.stdout,
                    "build_errors": result.stderr
                }
                
        except Exception as e:
            return {
                "success": False,
                "build_tool": "cx_freeze",
                "error": str(e)
            }
    
    def _generate_cx_freeze_setup(self, config: Dict[str, Any], build_env: Dict[str, Any]) -> str:
        """Generate setup.py for cx_Freeze"""
        setup_template = f'''
import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_options = {{
    'packages': [],
    'excludes': {build_env["exclude_modules"]},
    'include_files': {build_env["additional_files"]}
}}

base = 'Win32GUI' if sys.platform == 'win32' and not {build_env["console"]} else None

executables = [
    Executable(
        '{build_env["main_script"]}',
        base=base,
        target_name='{build_env["app_name"]}'
    )
]

setup(
    name='{build_env["app_name"]}',
    version='{build_env["app_version"]}',
    description='MIA Enterprise AGI Desktop Application',
    options={{'build_exe': build_options}},
    executables=executables
)
'''
        return setup_template
    
    def _find_built_executable(self, build_env: Dict[str, Any]) -> Optional[Path]:
        """Find the built executable"""
        dist_dir = build_env["dist_dir"]
        app_name = build_env["app_name"]
        
        # Common executable locations
        possible_paths = [
            dist_dir / f"{app_name}.exe",
            dist_dir / app_name,
            dist_dir / app_name / f"{app_name}.exe",
            dist_dir / app_name / app_name
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        # Search in dist directory
        for item in dist_dir.rglob("*"):
            if item.is_file() and item.stem == app_name:
                return item
        
        return None
    
    def _post_process_build(self, build_result: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process build results"""
        self.logger.info("🔧 Post-processing build...")
        
        try:
            post_process_result = {
                "post_process_success": True,
                "file_size_mb": 0,
                "optimizations_applied": []
            }
            
            executable_path = build_result.get("executable_path")
            if executable_path and executable_path.exists():
                # Get file size
                file_size = executable_path.stat().st_size
                post_process_result["file_size_mb"] = round(file_size / (1024 * 1024), 2)
                
                # Apply optimizations if requested
                if config.get("optimize", False):
                    optimization_result = self._optimize_executable(executable_path)
                    post_process_result["optimizations_applied"] = optimization_result
            
            return post_process_result
            
        except Exception as e:
            self.logger.error(f"Post-processing error: {e}")
            return {
                "post_process_success": False,
                "post_process_error": str(e)
            }
    
    def _optimize_executable(self, executable_path: Path) -> List[str]:
        """Optimize built executable"""
        optimizations = []
        
        try:
            # UPX compression (if available)
            try:
                result = subprocess.run(
                    ["upx", "--best", str(executable_path)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    optimizations.append("UPX compression applied")
                else:
                    optimizations.append("UPX compression failed")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                optimizations.append("UPX not available")
            
        except Exception as e:
            optimizations.append(f"Optimization error: {e}")
        
        return optimizations
    
    def clean_build_artifacts(self) -> Dict[str, Any]:
        """Clean build artifacts"""
        self.logger.info("🧹 Cleaning build artifacts...")
        
        try:
            cleaned_items = []
            
            # Clean build directory
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
                self.build_dir.mkdir(exist_ok=True)
                cleaned_items.append("build directory")
            
            # Clean spec files
            for spec_file in Path.cwd().glob("*.spec"):
                spec_file.unlink()
                cleaned_items.append(f"spec file: {spec_file.name}")
            
            return {
                "success": True,
                "cleaned_items": cleaned_items
            }
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
            return {
                "success": False,
                "error": str(e)
            }