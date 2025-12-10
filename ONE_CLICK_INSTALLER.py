#!/usr/bin/env python3
"""
🚀 MIA ONE-CLICK INSTALLER & LAUNCHER
====================================

Popoln installer za MIA Enterprise AGI sistem:
- Avtomatska detekcija strojne opreme
- Namestitev vseh odvisnosti
- Iskanje in prepoznavanje LLM modelov
- Ustvarjanje desktop ikon
- Avtomatski zagon sistema
- Internet learning setup

CILJ: Dvoklikom na ikono zaženi celoten sistem!
"""

import os
import sys
import platform
import subprocess
import asyncio
import logging
import json
import time
import shutil
import tempfile
import urllib.request
import zipfile
import tarfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import webbrowser

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mia_installer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MIAOneClickInstaller:
    """
    One-click installer for MIA Enterprise AGI
    Handles everything from download to desktop integration
    """
    
    def __init__(self):
        self.install_dir = None
        self.system_info = self._detect_system()
        self.installation_steps = []
        self.current_step = 0
        self.total_steps = 12
        
        # GUI components
        self.root = None
        self.progress_var = None
        self.status_var = None
        self.log_text = None
        
    def _detect_system(self) -> Dict[str, Any]:
        """Detect system information"""
        try:
            import psutil
            
            return {
                'os': platform.system(),
                'os_version': platform.version(),
                'architecture': platform.architecture()[0],
                'cpu_count': psutil.cpu_count(),
                'memory_gb': psutil.virtual_memory().total // (1024**3),
                'python_version': sys.version_info,
                'drives': self._get_drives()
            }
        except ImportError:
            return {
                'os': platform.system(),
                'os_version': platform.version(),
                'architecture': platform.architecture()[0],
                'cpu_count': os.cpu_count() or 2,
                'memory_gb': 8,  # Default assumption
                'python_version': sys.version_info,
                'drives': ['.']
            }
            
    def _get_drives(self) -> List[str]:
        """Get all available drives"""
        drives = []
        
        if platform.system() == "Windows":
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
        else:
            # Unix-like systems
            drives = ['/']
            # Add common mount points
            for mount in ['/mnt', '/media', '/Volumes']:
                if os.path.exists(mount):
                    for item in os.listdir(mount):
                        mount_path = os.path.join(mount, item)
                        if os.path.ismount(mount_path):
                            drives.append(mount_path)
                            
        return drives
        
    def create_gui(self):
        """Create installer GUI"""
        self.root = tk.Tk()
        self.root.title("MIA Enterprise AGI - One-Click Installer")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🧠 MIA Enterprise AGI", font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="One-Click Installer & Launcher", font=("Arial", 14))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # System info
        info_frame = ttk.LabelFrame(main_frame, text="System Information", padding="10")
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        info_text = f"""Operating System: {self.system_info['os']} {self.system_info['architecture']}
CPU Cores: {self.system_info['cpu_count']}
Memory: {self.system_info['memory_gb']}GB
Python: {self.system_info['python_version'].major}.{self.system_info['python_version'].minor}
Drives: {len(self.system_info['drives'])} detected"""
        
        ttk.Label(info_frame, text=info_text, font=("Courier", 10)).grid(row=0, column=0, sticky=tk.W)
        
        # Installation directory
        dir_frame = ttk.LabelFrame(main_frame, text="Installation Directory", padding="10")
        dir_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.install_dir_var = tk.StringVar(value=str(Path.home() / "MIA"))
        ttk.Entry(dir_frame, textvariable=self.install_dir_var, width=60).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).grid(row=0, column=1)
        
        # Progress
        progress_frame = ttk.LabelFrame(main_frame, text="Installation Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Ready to install")
        ttk.Label(progress_frame, textvariable=self.status_var).grid(row=1, column=0, sticky=tk.W)
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text="Installation Log", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        self.log_text = tk.Text(log_frame, height=15, width=80)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        
        self.install_button = ttk.Button(button_frame, text="🚀 Install & Launch MIA", 
                                       command=self.start_installation, style="Accent.TButton")
        self.install_button.grid(row=0, column=0, padx=(0, 10))
        
        self.launch_button = ttk.Button(button_frame, text="🧠 Launch MIA", 
                                      command=self.launch_mia, state=tk.DISABLED)
        self.launch_button.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Exit", command=self.root.quit).grid(row=0, column=2)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def browse_directory(self):
        """Browse for installation directory"""
        directory = filedialog.askdirectory(initialdir=self.install_dir_var.get())
        if directory:
            self.install_dir_var.set(directory)
            
    def log_message(self, message: str, level: str = "INFO"):
        """Log message to GUI and file"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        if self.log_text:
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
            self.root.update()
            
        if level == "INFO":
            logger.info(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "ERROR":
            logger.error(message)
            
    def update_progress(self, step: int, status: str):
        """Update progress bar and status"""
        self.current_step = step
        progress = (step / self.total_steps) * 100
        
        if self.progress_var:
            self.progress_var.set(progress)
            
        if self.status_var:
            self.status_var.set(f"Step {step}/{self.total_steps}: {status}")
            
        if self.root:
            self.root.update()
            
    def start_installation(self):
        """Start installation process"""
        self.install_dir = Path(self.install_dir_var.get())
        self.install_button.config(state=tk.DISABLED)
        
        # Run installation in separate thread
        install_thread = threading.Thread(target=self.run_installation)
        install_thread.daemon = True
        install_thread.start()
        
    async def run_installation(self):
        """Run complete installation process"""
        try:
            self.log_message("🚀 Starting MIA Enterprise AGI installation...")
            
            # Step 1: Create installation directory
            await self.step_create_directory()
            
            # Step 2: Download MIA repository
            await self.step_download_repository()
            
            # Step 3: Detect hardware capabilities
            await self.step_detect_hardware()
            
            # Step 4: Install Python dependencies
            await self.step_install_dependencies()
            
            # Step 5: Discover LLM models
            await self.step_discover_models()
            
            # Step 6: Setup internet learning
            await self.step_setup_internet_learning()
            
            # Step 7: Create configuration
            await self.step_create_configuration()
            
            # Step 8: Create desktop integration
            await self.step_create_desktop_integration()
            
            # Step 9: Setup auto-startup
            await self.step_setup_auto_startup()
            
            # Step 10: Run system tests
            await self.step_run_tests()
            
            # Step 11: Create launcher scripts
            await self.step_create_launchers()
            
            # Step 12: Final setup
            await self.step_final_setup()
            
            self.log_message("✅ Installation completed successfully!")
            self.log_message("🧠 MIA Enterprise AGI is ready to use!")
            
            # Enable launch button
            if self.launch_button:
                self.launch_button.config(state=tk.NORMAL)
                
            # Show completion message
            if self.root:
                messagebox.showinfo("Installation Complete", 
                                  "MIA Enterprise AGI has been installed successfully!\n\n"
                                  "You can now launch the system using the Launch button or "
                                  "the desktop shortcut.")
                                  
        except Exception as e:
            self.log_message(f"❌ Installation failed: {e}", "ERROR")
            messagebox.showerror("Installation Failed", f"Installation failed with error:\n{e}")
            
    async def step_create_directory(self):
        """Step 1: Create installation directory"""
        self.update_progress(1, "Creating installation directory...")
        
        try:
            self.install_dir.mkdir(parents=True, exist_ok=True)
            self.log_message(f"📁 Created installation directory: {self.install_dir}")
        except Exception as e:
            raise Exception(f"Failed to create installation directory: {e}")
            
    async def step_download_repository(self):
        """Step 2: Download MIA repository"""
        self.update_progress(2, "Downloading MIA repository...")
        
        try:
            # For this demo, we'll copy from current directory
            # In real deployment, this would download from GitHub
            current_dir = Path(__file__).parent
            
            # Copy essential files
            essential_files = [
                'mia_hybrid_launcher.py',
                'mia_main.py',
                'requirements.txt',
                'requirements_hybrid.txt',
                'test_hybrid_system.py'
            ]
            
            for file_name in essential_files:
                src = current_dir / file_name
                if src.exists():
                    dst = self.install_dir / file_name
                    shutil.copy2(src, dst)
                    self.log_message(f"📄 Copied {file_name}")
                    
            # Copy mia directory
            mia_src = current_dir / 'mia'
            if mia_src.exists():
                mia_dst = self.install_dir / 'mia'
                if mia_dst.exists():
                    shutil.rmtree(mia_dst)
                shutil.copytree(mia_src, mia_dst)
                self.log_message("📁 Copied MIA source code")
                
            self.log_message("✅ Repository download completed")
            
        except Exception as e:
            raise Exception(f"Failed to download repository: {e}")
            
    async def step_detect_hardware(self):
        """Step 3: Detect hardware capabilities"""
        self.update_progress(3, "Detecting hardware capabilities...")
        
        try:
            # CPU detection
            cpu_count = self.system_info['cpu_count']
            self.log_message(f"🖥️ Detected {cpu_count} CPU cores")
            
            # Memory detection
            memory_gb = self.system_info['memory_gb']
            self.log_message(f"💾 Detected {memory_gb}GB RAM")
            
            # GPU detection
            gpu_info = self._detect_gpu()
            if gpu_info:
                self.log_message(f"🎮 Detected GPU: {gpu_info}")
            else:
                self.log_message("🎮 No GPU detected - using CPU processing")
                
            # Storage detection
            drives = self.system_info['drives']
            self.log_message(f"💽 Detected {len(drives)} storage drives")
            
            # Create hardware config
            hardware_config = {
                'cpu_cores': cpu_count,
                'memory_gb': memory_gb,
                'gpu_available': bool(gpu_info),
                'gpu_info': gpu_info,
                'drives': drives,
                'recommended_settings': self._get_recommended_settings()
            }
            
            config_file = self.install_dir / 'hardware_config.json'
            with open(config_file, 'w') as f:
                json.dump(hardware_config, f, indent=2)
                
            self.log_message("✅ Hardware detection completed")
            
        except Exception as e:
            raise Exception(f"Failed to detect hardware: {e}")
            
    def _detect_gpu(self) -> Optional[str]:
        """Detect GPU information"""
        try:
            # Try nvidia-smi
            result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
            
        try:
            # Try lspci on Linux
            if platform.system() == "Linux":
                result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'VGA' in line or 'Display' in line:
                            return line.split(': ')[-1]
        except:
            pass
            
        return None
        
    def _get_recommended_settings(self) -> Dict[str, Any]:
        """Get recommended settings based on hardware"""
        cpu_count = self.system_info['cpu_count']
        memory_gb = self.system_info['memory_gb']
        
        return {
            'max_workers': min(cpu_count, 8),
            'memory_limit_gb': max(2, memory_gb // 2),
            'enable_gpu': self._detect_gpu() is not None,
            'batch_size': 32 if memory_gb >= 16 else (16 if memory_gb >= 8 else 8),
            'cache_size_mb': min(1024, memory_gb * 64)
        }
        
    async def step_install_dependencies(self):
        """Step 4: Install Python dependencies"""
        self.update_progress(4, "Installing Python dependencies...")
        
        try:
            # Install critical dependencies
            critical_deps = [
                'rdflib>=6.2.0',
                'sentence-transformers>=2.2.0',
                'spacy>=3.4.0',
                'z3-solver>=4.11.0',
                'scikit-learn>=1.1.0',
                'nltk>=3.7',
                'fastapi>=0.68.0',
                'uvicorn>=0.15.0',
                'psutil>=5.8.0',
                'requests>=2.25.0'
            ]
            
            for dep in critical_deps:
                self.log_message(f"📦 Installing {dep}...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', dep
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    self.log_message(f"✅ Installed {dep}")
                else:
                    self.log_message(f"⚠️ Warning: Failed to install {dep}", "WARNING")
                    
            # Install spaCy model
            self.log_message("📦 Installing spaCy English model...")
            result = subprocess.run([
                sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log_message("✅ Installed spaCy English model")
            else:
                self.log_message("⚠️ Warning: Failed to install spaCy model", "WARNING")
                
            self.log_message("✅ Dependencies installation completed")
            
        except Exception as e:
            raise Exception(f"Failed to install dependencies: {e}")
            
    async def step_discover_models(self):
        """Step 5: Discover LLM models across all drives"""
        self.update_progress(5, "Discovering LLM models...")
        
        try:
            found_models = []
            
            # Model file patterns
            model_patterns = ['*.gguf', '*.bin', '*.safetensors', '*.pt', '*.pth', '*.onnx']
            model_dirs = ['models', 'llm', 'ai_models', '.cache/huggingface', '.ollama']
            
            self.log_message("🔍 Scanning drives for LLM models...")
            
            for drive in self.system_info['drives']:
                try:
                    drive_path = Path(drive)
                    self.log_message(f"🔍 Scanning drive: {drive}")
                    
                    # Search in common model directories
                    for model_dir in model_dirs:
                        search_path = drive_path / model_dir
                        if search_path.exists():
                            for pattern in model_patterns:
                                for model_file in search_path.rglob(pattern):
                                    if model_file.is_file() and model_file.stat().st_size > 1024*1024:  # > 1MB
                                        found_models.append({
                                            'path': str(model_file),
                                            'size_mb': model_file.stat().st_size // (1024*1024),
                                            'type': model_file.suffix,
                                            'name': model_file.stem
                                        })
                                        
                except Exception as e:
                    self.log_message(f"⚠️ Error scanning drive {drive}: {e}", "WARNING")
                    continue
                    
            # Remove duplicates and sort by size
            unique_models = {}
            for model in found_models:
                key = model['name']
                if key not in unique_models or model['size_mb'] > unique_models[key]['size_mb']:
                    unique_models[key] = model
                    
            found_models = list(unique_models.values())
            found_models.sort(key=lambda x: x['size_mb'], reverse=True)
            
            self.log_message(f"🤖 Found {len(found_models)} LLM models:")
            for model in found_models[:10]:  # Show first 10
                self.log_message(f"  📄 {model['name']} ({model['size_mb']}MB) - {model['type']}")
                
            # Save model registry
            model_registry = {
                'discovered_models': found_models,
                'discovery_date': time.time(),
                'total_models': len(found_models)
            }
            
            registry_file = self.install_dir / 'model_registry.json'
            with open(registry_file, 'w') as f:
                json.dump(model_registry, f, indent=2)
                
            if not found_models:
                self.log_message("⚠️ No local models found - system will use internet learning", "WARNING")
                
            self.log_message("✅ Model discovery completed")
            
        except Exception as e:
            raise Exception(f"Failed to discover models: {e}")
            
    async def step_setup_internet_learning(self):
        """Step 6: Setup internet learning capabilities"""
        self.update_progress(6, "Setting up internet learning...")
        
        try:
            # Test internet connectivity
            self.log_message("🌐 Testing internet connectivity...")
            
            test_urls = [
                "https://www.google.com",
                "https://en.wikipedia.org",
                "https://api.github.com"
            ]
            
            internet_available = False
            for url in test_urls:
                try:
                    urllib.request.urlopen(url, timeout=10)
                    internet_available = True
                    self.log_message(f"✅ Internet connectivity confirmed: {url}")
                    break
                except:
                    continue
                    
            if not internet_available:
                self.log_message("⚠️ No internet connectivity - offline mode only", "WARNING")
                
            # Create internet learning config
            internet_config = {
                'internet_available': internet_available,
                'learning_sources': [
                    'https://en.wikipedia.org',
                    'https://www.reddit.com',
                    'https://news.ycombinator.com',
                    'https://stackoverflow.com'
                ],
                'learning_schedule': {
                    'enabled': internet_available,
                    'interval_hours': 6,
                    'max_pages_per_session': 100
                },
                'content_filters': {
                    'min_content_length': 500,
                    'exclude_domains': ['ads.', 'tracker.', 'analytics.'],
                    'allowed_content_types': ['text/html', 'application/json']
                }
            }
            
            config_file = self.install_dir / 'internet_learning_config.json'
            with open(config_file, 'w') as f:
                json.dump(internet_config, f, indent=2)
                
            self.log_message("✅ Internet learning setup completed")
            
        except Exception as e:
            raise Exception(f"Failed to setup internet learning: {e}")
            
    async def step_create_configuration(self):
        """Step 7: Create system configuration"""
        self.update_progress(7, "Creating system configuration...")
        
        try:
            # Main system configuration
            config = {
                'system': {
                    'name': 'MIA Enterprise AGI',
                    'version': '2.0.0',
                    'installation_date': time.time(),
                    'installation_path': str(self.install_dir)
                },
                'hardware': self._get_recommended_settings(),
                'features': {
                    'hybrid_ai': True,
                    'internet_learning': True,
                    'model_discovery': True,
                    'web_interface': True,
                    'desktop_integration': True
                },
                'network': {
                    'web_port': 8000,
                    'api_port': 8001,
                    'websocket_port': 8002
                },
                'logging': {
                    'level': 'INFO',
                    'file': 'mia.log',
                    'max_size_mb': 100,
                    'backup_count': 5
                },
                'security': {
                    'enable_auth': False,
                    'api_key_required': False,
                    'cors_enabled': True
                }
            }
            
            config_file = self.install_dir / 'mia_config.json'
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            self.log_message("✅ System configuration created")
            
        except Exception as e:
            raise Exception(f"Failed to create configuration: {e}")
            
    async def step_create_desktop_integration(self):
        """Step 8: Create desktop integration"""
        self.update_progress(8, "Creating desktop integration...")
        
        try:
            os_name = platform.system()
            
            if os_name == "Windows":
                await self._create_windows_integration()
            elif os_name == "Darwin":  # macOS
                await self._create_macos_integration()
            elif os_name == "Linux":
                await self._create_linux_integration()
                
            self.log_message("✅ Desktop integration created")
            
        except Exception as e:
            self.log_message(f"⚠️ Desktop integration failed: {e}", "WARNING")
            
    async def _create_windows_integration(self):
        """Create Windows desktop integration"""
        try:
            # Create desktop shortcut
            desktop_path = Path.home() / "Desktop"
            if desktop_path.exists():
                shortcut_content = f"""[InternetShortcut]
URL=file:///{self.install_dir / 'mia_hybrid_launcher.py'}
IconFile={self.install_dir / 'mia_icon.ico'}
"""
                shortcut_file = desktop_path / "MIA Enterprise AGI.url"
                with open(shortcut_file, 'w') as f:
                    f.write(shortcut_content)
                    
                self.log_message("🖥️ Created desktop shortcut")
                
            # Create Start Menu entry
            start_menu = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs"
            if start_menu.exists():
                mia_folder = start_menu / "MIA Enterprise AGI"
                mia_folder.mkdir(exist_ok=True)
                
                shortcut_file = mia_folder / "MIA Enterprise AGI.url"
                with open(shortcut_file, 'w') as f:
                    f.write(shortcut_content)
                    
                self.log_message("📋 Created Start Menu entry")
                
        except Exception as e:
            raise Exception(f"Windows integration failed: {e}")
            
    async def _create_macos_integration(self):
        """Create macOS desktop integration"""
        try:
            # Create .app bundle structure
            app_name = "MIA Enterprise AGI.app"
            app_path = self.install_dir / app_name
            
            # Create directory structure
            contents_dir = app_path / "Contents"
            macos_dir = contents_dir / "MacOS"
            resources_dir = contents_dir / "Resources"
            
            for dir_path in [contents_dir, macos_dir, resources_dir]:
                dir_path.mkdir(parents=True, exist_ok=True)
                
            # Create Info.plist
            info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>mia_launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.mia.enterprise.agi</string>
    <key>CFBundleName</key>
    <string>MIA Enterprise AGI</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0</string>
</dict>
</plist>"""
            
            with open(contents_dir / "Info.plist", 'w') as f:
                f.write(info_plist)
                
            # Create launcher script
            launcher_script = f"""#!/bin/bash
cd "{self.install_dir}"
python3 mia_hybrid_launcher.py
"""
            
            launcher_file = macos_dir / "mia_launcher"
            with open(launcher_file, 'w') as f:
                f.write(launcher_script)
                
            # Make executable
            os.chmod(launcher_file, 0o755)
            
            self.log_message("🍎 Created macOS app bundle")
            
        except Exception as e:
            raise Exception(f"macOS integration failed: {e}")
            
    async def _create_linux_integration(self):
        """Create Linux desktop integration"""
        try:
            # Create .desktop file
            desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=MIA Enterprise AGI
Comment=Neural-Symbolic AI System
Exec=python3 "{self.install_dir / 'mia_hybrid_launcher.py'}"
Icon={self.install_dir / 'mia_icon.png'}
Terminal=false
Categories=Development;Science;Education;
StartupNotify=true
"""
            
            # Save to applications directory
            apps_dir = Path.home() / ".local/share/applications"
            apps_dir.mkdir(parents=True, exist_ok=True)
            
            desktop_file = apps_dir / "mia-enterprise-agi.desktop"
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
                
            # Make executable
            os.chmod(desktop_file, 0o755)
            
            # Also create on desktop if it exists
            desktop_path = Path.home() / "Desktop"
            if desktop_path.exists():
                desktop_shortcut = desktop_path / "MIA Enterprise AGI.desktop"
                with open(desktop_shortcut, 'w') as f:
                    f.write(desktop_content)
                os.chmod(desktop_shortcut, 0o755)
                
            self.log_message("🐧 Created Linux desktop integration")
            
        except Exception as e:
            raise Exception(f"Linux integration failed: {e}")
            
    async def step_setup_auto_startup(self):
        """Step 9: Setup auto-startup (optional)"""
        self.update_progress(9, "Setting up auto-startup...")
        
        try:
            # For now, just create the configuration
            # User can enable auto-startup later through the interface
            
            startup_config = {
                'auto_startup_enabled': False,
                'startup_delay_seconds': 30,
                'minimize_on_startup': True,
                'check_for_updates': True
            }
            
            config_file = self.install_dir / 'startup_config.json'
            with open(config_file, 'w') as f:
                json.dump(startup_config, f, indent=2)
                
            self.log_message("✅ Auto-startup configuration created (disabled by default)")
            
        except Exception as e:
            self.log_message(f"⚠️ Auto-startup setup failed: {e}", "WARNING")
            
    async def step_run_tests(self):
        """Step 10: Run system tests"""
        self.update_progress(10, "Running system tests...")
        
        try:
            # Run basic import tests
            test_imports = [
                'mia.core.agi_core',
                'mia.enterprise.security',
                'mia.interfaces.chat'
            ]
            
            sys.path.insert(0, str(self.install_dir))
            
            for import_name in test_imports:
                try:
                    __import__(import_name)
                    self.log_message(f"✅ Import test passed: {import_name}")
                except ImportError as e:
                    self.log_message(f"⚠️ Import test failed: {import_name} - {e}", "WARNING")
                    
            # Test configuration loading
            config_file = self.install_dir / 'mia_config.json'
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                self.log_message("✅ Configuration test passed")
            else:
                self.log_message("⚠️ Configuration file not found", "WARNING")
                
            self.log_message("✅ System tests completed")
            
        except Exception as e:
            self.log_message(f"⚠️ System tests failed: {e}", "WARNING")
            
    async def step_create_launchers(self):
        """Step 11: Create launcher scripts"""
        self.update_progress(11, "Creating launcher scripts...")
        
        try:
            # Create simple launcher script
            launcher_content = f"""#!/usr/bin/env python3
\"\"\"
MIA Enterprise AGI - Simple Launcher
\"\"\"

import os
import sys
from pathlib import Path

# Set working directory
install_dir = Path(__file__).parent
os.chdir(install_dir)

# Add to Python path
sys.path.insert(0, str(install_dir))

try:
    # Try to launch hybrid system
    import subprocess
    result = subprocess.run([sys.executable, 'mia_hybrid_launcher.py'], cwd=install_dir)
    sys.exit(result.returncode)
except Exception as e:
    print(f"Failed to launch MIA: {{e}}")
    sys.exit(1)
"""
            
            launcher_file = self.install_dir / "launch_mia.py"
            with open(launcher_file, 'w') as f:
                f.write(launcher_content)
                
            # Make executable on Unix systems
            if platform.system() != "Windows":
                os.chmod(launcher_file, 0o755)
                
            self.log_message("✅ Launcher scripts created")
            
        except Exception as e:
            raise Exception(f"Failed to create launchers: {e}")
            
    async def step_final_setup(self):
        """Step 12: Final setup and cleanup"""
        self.update_progress(12, "Finalizing installation...")
        
        try:
            # Create installation info file
            install_info = {
                'installation_completed': True,
                'installation_date': time.time(),
                'installation_version': '2.0.0',
                'system_info': self.system_info,
                'install_directory': str(self.install_dir),
                'features_installed': [
                    'hybrid_ai_system',
                    'internet_learning',
                    'model_discovery',
                    'desktop_integration',
                    'web_interface'
                ]
            }
            
            info_file = self.install_dir / 'installation_info.json'
            with open(info_file, 'w') as f:
                json.dump(install_info, f, indent=2)
                
            # Create README file
            readme_content = f"""# MIA Enterprise AGI - Installation Complete

## 🎉 Installation Successful!

MIA Enterprise AGI has been successfully installed on your system.

### 📁 Installation Directory
{self.install_dir}

### 🚀 How to Launch MIA

1. **Desktop Shortcut**: Double-click the MIA Enterprise AGI icon on your desktop
2. **Command Line**: Run `python launch_mia.py` in the installation directory
3. **Direct Launch**: Run `python mia_hybrid_launcher.py`

### 🌐 Web Interface

Once launched, MIA will be available at: http://localhost:8000

### 🔧 Configuration

- Main config: `mia_config.json`
- Hardware config: `hardware_config.json`
- Model registry: `model_registry.json`
- Internet learning: `internet_learning_config.json`

### 📊 System Information

- OS: {self.system_info['os']} {self.system_info['architecture']}
- CPU Cores: {self.system_info['cpu_count']}
- Memory: {self.system_info['memory_gb']}GB
- Python: {self.system_info['python_version'].major}.{self.system_info['python_version'].minor}

### 🆘 Support

If you encounter any issues:
1. Check the installation log: `mia_installer.log`
2. Check the system log: `mia.log`
3. Run system tests: `python test_hybrid_system.py`

### 🔄 Updates

To update MIA, run the installer again or use the built-in update feature.

---

**Installation completed on:** {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            readme_file = self.install_dir / 'README.md'
            with open(readme_file, 'w') as f:
                f.write(readme_content)
                
            self.log_message("✅ Final setup completed")
            
        except Exception as e:
            raise Exception(f"Failed to complete final setup: {e}")
            
    def launch_mia(self):
        """Launch MIA system"""
        try:
            if not self.install_dir or not (self.install_dir / 'mia_hybrid_launcher.py').exists():
                messagebox.showerror("Launch Error", "MIA is not installed or installation is incomplete.")
                return
                
            self.log_message("🚀 Launching MIA Enterprise AGI...")
            
            # Launch in separate process
            launcher_script = self.install_dir / 'mia_hybrid_launcher.py'
            subprocess.Popen([sys.executable, str(launcher_script)], 
                           cwd=self.install_dir,
                           creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == "Windows" else 0)
            
            # Open web browser after a delay
            def open_browser():
                time.sleep(5)  # Wait for system to start
                webbrowser.open('http://localhost:8000')
                
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            self.log_message("✅ MIA launched successfully!")
            self.log_message("🌐 Web interface will open at http://localhost:8000")
            
        except Exception as e:
            self.log_message(f"❌ Failed to launch MIA: {e}", "ERROR")
            messagebox.showerror("Launch Error", f"Failed to launch MIA:\n{e}")
            
    def run(self):
        """Run the installer GUI"""
        self.create_gui()
        
        # Show welcome message
        welcome_msg = f"""Welcome to MIA Enterprise AGI One-Click Installer!

This installer will:
• Detect your hardware capabilities
• Install all required dependencies
• Discover LLM models across all drives
• Setup internet learning capabilities
• Create desktop shortcuts
• Configure the system for optimal performance

System detected:
• OS: {self.system_info['os']} {self.system_info['architecture']}
• CPU: {self.system_info['cpu_count']} cores
• Memory: {self.system_info['memory_gb']}GB
• Python: {self.system_info['python_version'].major}.{self.system_info['python_version'].minor}

Click 'Install & Launch MIA' to begin!"""
        
        messagebox.showinfo("Welcome to MIA Installer", welcome_msg)
        
        self.root.mainloop()

def main():
    """Main entry point"""
    print("🚀 MIA Enterprise AGI - One-Click Installer")
    print("=" * 50)
    
    try:
        installer = MIAOneClickInstaller()
        installer.run()
    except KeyboardInterrupt:
        print("\n⚠️ Installation cancelled by user")
    except Exception as e:
        print(f"\n❌ Installer failed: {e}")
        logging.exception("Installer failed")

if __name__ == "__main__":
    main()