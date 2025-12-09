import time
from datetime import datetime
#!/usr/bin/env python3
"""
MIA Enterprise AGI - Cross Platform Utils
========================================

Utility functions for cross-platform desktop development.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import json
import tempfile


class CrossPlatformUtils:
    """Cross-platform utility functions"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.logger.info("🔧 Cross Platform Utils initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.Desktop.CrossPlatformUtils")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def normalize_path(self, path: Union[str, Path], target_platform: Optional[str] = None) -> str:
        """Normalize path for target platform"""
        path_obj = Path(path)
        
        if target_platform == "windows":
            return str(path_obj).replace("/", "\\")
        else:
            return str(path_obj).replace("\\", "/")
    
    def get_executable_extension(self, target_platform: Optional[str] = None) -> str:
        """Get executable extension for target platform"""
        platform = target_platform or sys.platform
        
        if platform.startswith("win"):
            return ".exe"
        else:
            return ""
    
    def get_library_extension(self, target_platform: Optional[str] = None) -> str:
        """Get library extension for target platform"""
        platform = target_platform or sys.platform
        
        if platform.startswith("win"):
            return ".dll"
        elif platform.startswith("darwin"):
            return ".dylib"
        else:
            return ".so"
    
    def execute_command(self, 
                       command: List[str],
                       working_dir: Optional[Path] = None,
                       timeout: int = 300,
                       capture_output: bool = True) -> Dict[str, Any]:
        """Execute command with cross-platform compatibility"""
        try:
            self.logger.info(f"Executing: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                cwd=working_dir,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout if capture_output else "",
                "stderr": result.stderr if capture_output else "",
                "command": command
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "command": command
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"Command not found: {command[0]}",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    def check_tool_availability(self, tool_name: str) -> Dict[str, Any]:
        """Check if a tool is available on the system"""
        try:
            result = subprocess.run(
                [tool_name, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "available": result.returncode == 0,
                "version": result.stdout.strip() if result.returncode == 0 else None,
                "error": result.stderr.strip() if result.returncode != 0 else None
            }
            
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return {
                "available": False,
                "version": None,
                "error": f"Tool not found: {tool_name}"
            }
    
    def install_dependencies(self, dependencies: List[str]) -> Dict[str, Any]:
        """Install Python dependencies"""
        self.logger.info(f"Installing dependencies: {dependencies}")
        
        try:
            cmd = [sys.executable, "-m", "pip", "install"] + dependencies
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            return {
                "success": result.returncode == 0,
                "installed_packages": dependencies if result.returncode == 0 else [],
                "output": result.stdout,
                "errors": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Installation timed out",
                "installed_packages": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "installed_packages": []
            }
    
    def create_virtual_environment(self, venv_path: Path) -> Dict[str, Any]:
        """Create virtual environment"""
        self.logger.info(f"Creating virtual environment: {venv_path}")
        
        try:
            cmd = [sys.executable, "-m", "venv", str(venv_path)]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                # Get activation script path
                if sys.platform.startswith("win"):
                    activate_script = venv_path / "Scripts" / "activate.bat"
                    python_executable = venv_path / "Scripts" / "python.exe"
                else:
                    activate_script = venv_path / "bin" / "activate"
                    python_executable = venv_path / "bin" / "python"
                
                return {
                    "success": True,
                    "venv_path": venv_path,
                    "activate_script": activate_script,
                    "python_executable": python_executable
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "output": result.stdout
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def copy_file_with_permissions(self, 
                                  source: Path, 
                                  destination: Path,
                                  preserve_permissions: bool = True) -> Dict[str, Any]:
        """Copy file with proper permissions"""
        try:
            import shutil
            
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            if preserve_permissions:
                shutil.copy2(source, destination)
            else:
                shutil.copy(source, destination)
            
            # Set executable permissions on Unix-like systems
            if not sys.platform.startswith("win") and source.suffix in [".sh", ""]:
                os.chmod(destination, 0o755)
            
            return {
                "success": True,
                "source": source,
                "destination": destination,
                "size_bytes": destination.stat().st_size
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": source,
                "destination": destination
            }
    
    def create_desktop_shortcut(self, 
                               app_name: str,
                               executable_path: Path,
                               icon_path: Optional[Path] = None,
                               description: Optional[str] = None) -> Dict[str, Any]:
        """Create desktop shortcut"""
        self.logger.info(f"Creating desktop shortcut for {app_name}")
        
        try:
            if sys.platform.startswith("win"):
                return self._create_windows_shortcut(app_name, executable_path, icon_path, description)
            elif sys.platform.startswith("darwin"):
                return self._create_macos_shortcut(app_name, executable_path, icon_path, description)
            else:
                return self._create_linux_shortcut(app_name, executable_path, icon_path, description)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_windows_shortcut(self, 
                                app_name: str,
                                executable_path: Path,
                                icon_path: Optional[Path],
                                description: Optional[str]) -> Dict[str, Any]:
        """Create Windows shortcut"""
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = Path(desktop) / f"{app_name}.lnk"
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(executable_path)
            shortcut.WorkingDirectory = str(executable_path.parent)
            
            if icon_path:
                shortcut.IconLocation = str(icon_path)
            
            if description:
                shortcut.Description = description
            
            shortcut.save()
            
            return {
                "success": True,
                "shortcut_path": shortcut_path,
                "platform": "windows"
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "Windows shortcut creation requires pywin32 and winshell packages"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_macos_shortcut(self, 
                              app_name: str,
                              executable_path: Path,
                              icon_path: Optional[Path],
                              description: Optional[str]) -> Dict[str, Any]:
        """Create macOS alias"""
        # For macOS, we typically create app bundles instead of shortcuts
        return {
            "success": True,
            "message": "macOS uses app bundles instead of shortcuts",
            "platform": "macos"
        }
    
    def _create_linux_shortcut(self, 
                              app_name: str,
                              executable_path: Path,
                              icon_path: Optional[Path],
                              description: Optional[str]) -> Dict[str, Any]:
        """Create Linux desktop file"""
        try:
            desktop_dir = Path.home() / "Desktop"
            if not desktop_dir.exists():
                desktop_dir = Path.home()
            
            desktop_file = desktop_dir / f"{app_name}.desktop"
            
            content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={app_name}
Comment={description or app_name}
Exec={executable_path}
Terminal=false
Categories=Utility;
"""
            
            if icon_path:
                content += f"Icon={icon_path}\n"
            
            with open(desktop_file, 'w') as f:
                f.write(content)
            
            # Make executable
            os.chmod(desktop_file, 0o755)
            
            return {
                "success": True,
                "shortcut_path": desktop_file,
                "platform": "linux"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            import platform
            
            system_info = {
                "platform": {
                    "system": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "architecture": platform.architecture(),
                    "python_version": platform.python_version(),
                    "python_implementation": platform.python_implementation()
                },
                "environment": {
                    "python_executable": sys.executable,
                    "python_path": sys.path,
                    "environment_variables": dict(os.environ)
                }
            }
            
            # Add system resources if psutil is available
            try:
                import psutil
                
                system_info["resources"] = {
                    "cpu_count": psutil.cpu_count(),
                    "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                    "disk_free_gb": round(psutil.disk_usage('/').free / (1024**3), 2)
                }
            except ImportError:
                system_info["resources"] = {"note": "psutil not available"}
            
            return system_info
            
        except Exception as e:
            return {
                "error": str(e)
            }
    
    def validate_file_integrity(self, file_path: Path) -> Dict[str, Any]:
        """Validate file integrity"""
        try:
            import hashlib
            
            if not file_path.exists():
                return {
                    "valid": False,
                    "error": "File does not exist"
                }
            
            # Calculate file hash
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            
            file_stats = file_path.stat()
            
            return {
                "valid": True,
                "file_path": file_path,
                "size_bytes": file_stats.st_size,
                "size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                "sha256": hash_sha256.hexdigest(),
                "modified_time": file_stats.st_mtime,
                "is_executable": os.access(file_path, os.X_OK)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def cleanup_temp_files(self, temp_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Clean up temporary files"""
        try:
            import shutil
            
            if temp_dir is None:
                temp_dir = Path(tempfile.gettempdir()) / "mia_build"
            
            cleaned_files = []
            
            if temp_dir.exists():
                for item in temp_dir.iterdir():
                    try:
                        if item.is_file():
                            item.unlink()
                            cleaned_files.append(str(item))
                        elif item.is_dir():
                            shutil.rmtree(item)
                            cleaned_files.append(str(item))
                    except Exception as e:
                        self.logger.warning(f"Failed to clean {item}: {e}")
            
            return {
                "success": True,
                "cleaned_files": cleaned_files,
                "temp_dir": temp_dir
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }