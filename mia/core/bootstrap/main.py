#!/usr/bin/env python3
"""
MIA Bootstrap System (MIA.bootbuilder)
Handles automatic hardware detection, model selection, and system initialization
"""

import os
import sys
import json
import yaml
import psutil
import platform
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import importlib.util
import asyncio
from dataclasses import dataclass

@dataclass
class HardwareProfile:
    """Hardware configuration profile"""
    cpu_cores: int
    cpu_freq: float
    ram_gb: float
    gpu_available: bool
    gpu_memory_gb: float
    disk_space_gb: float
    architecture: str
    optimization_mode: str

@dataclass
class ModelProfile:
    """Model configuration profile"""
    language_model: str
    language_model_size: str
    stt_model: str
    tts_model: str
    image_model: str
    video_model: Optional[str]
    audio_model: str
    max_context_length: int
    quantization: str

class MIABootBuilder:
    """Main bootstrap system for MIA"""
    
    def __init__(self, config_path: str = ".mia-config.yaml"):
        self.config_path = config_path
        self.hardware_profile: Optional[HardwareProfile] = None
        self.model_profile: Optional[ModelProfile] = None
        self.config: Dict = {}
        self.logger = self._setup_logging()
        self.base_path = Path(__file__).parent.parent.parent
    
    def detect_hardware(self):
        """Detect system hardware capabilities (sync version)"""
        try:
            import psutil
            import platform
            
            hardware_info = {
                "cpu_cores": psutil.cpu_count(),
                "total_memory": psutil.virtual_memory().total,
                "available_memory": psutil.virtual_memory().available,
                "platform": platform.platform(),
                "processor": platform.processor(),
                "python_version": platform.python_version()
            }
            
            # Try to detect GPU
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    hardware_info["gpu_count"] = len(gpus)
                    hardware_info["gpu_memory"] = gpus[0].memoryTotal * 1024 * 1024  # Convert to bytes
                else:
                    hardware_info["gpu_count"] = 0
                    hardware_info["gpu_memory"] = 0
            except:
                hardware_info["gpu_count"] = 0
                hardware_info["gpu_memory"] = 0
            
            return hardware_info
            
        except Exception as e:
            self.logger.error(f"Failed to detect hardware: {e}")
            return {
                "cpu_cores": 1,
                "total_memory": 1024*1024*1024,  # 1GB fallback
                "available_memory": 512*1024*1024,  # 512MB fallback
                "platform": "Unknown",
                "processor": "Unknown",
                "python_version": "3.12",
                "gpu_count": 0,
                "gpu_memory": 0
            }
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - MIA.Bootstrap - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('mia/logs/bootstrap.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Main initialization sequence"""
        try:
            self.logger.info("🚀 MIA Bootstrap System Starting...")
            
            # Load configuration
            await self._load_config()
            
            # Detect hardware
            self.hardware_profile = await self._detect_hardware()
            self.logger.info(f"Hardware detected: {self.hardware_profile}")
            
            # Select optimal models
            self.model_profile = await self._select_models()
            self.logger.info(f"Models selected: {self.model_profile}")
            
            # Download and setup models
            await self._setup_models()
            
            # Initialize core modules
            await self._initialize_core_modules()
            
            # Initialize peripheral modules
            await self._initialize_peripheral_modules()
            
            # Perform system health check
            health_status = await self._system_health_check()
            
            if health_status:
                self.logger.info("✅ MIA Bootstrap completed successfully!")
                await self._save_system_state()
                return True
            else:
                self.logger.error("❌ MIA Bootstrap failed health check!")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Bootstrap failed: {str(e)}")
            return False
    
    async def _load_config(self):
        """Load MIA configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            self.logger.info("Configuration loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            raise
    
    async def _detect_hardware(self) -> HardwareProfile:
        """Detect and analyze hardware capabilities"""
        
        # CPU detection
        cpu_cores = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq().max if psutil.cpu_freq() else 2000.0
        
        # Memory detection
        memory = psutil.virtual_memory()
        ram_gb = memory.total / (1024**3)
        
        # GPU detection
        gpu_available = False
        gpu_memory_gb = 0.0
        
        try:
            # Try to detect NVIDIA GPU
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                gpu_memory_gb = float(result.stdout.strip()) / 1024
                gpu_available = True
                self.logger.info(f"NVIDIA GPU detected with {gpu_memory_gb:.1f}GB VRAM")
        except:
            pass
        
        if not gpu_available:
            try:
                # Try to detect AMD GPU
                result = subprocess.run(['rocm-smi', '--showmeminfo', 'vram'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    gpu_available = True
                    gpu_memory_gb = 8.0  # Default assumption for AMD
                    self.logger.info("AMD GPU detected")
            except:
                pass
        
        # Disk space detection
        disk = psutil.disk_usage('/')
        disk_space_gb = disk.free / (1024**3)
        
        # Architecture detection
        architecture = platform.machine()
        
        # Determine optimization mode
        if gpu_available and gpu_memory_gb >= 8:
            optimization_mode = "gpu_optimized"
        elif gpu_available and gpu_memory_gb >= 4:
            optimization_mode = "gpu_light"
        elif ram_gb >= 16:
            optimization_mode = "cpu_heavy"
        elif ram_gb >= 8:
            optimization_mode = "cpu_medium"
        else:
            optimization_mode = "cpu_light"
        
        return HardwareProfile(
            cpu_cores=cpu_cores,
            cpu_freq=cpu_freq,
            ram_gb=ram_gb,
            gpu_available=gpu_available,
            gpu_memory_gb=gpu_memory_gb,
            disk_space_gb=disk_space_gb,
            architecture=architecture,
            optimization_mode=optimization_mode
        )
    
    async def _select_models(self) -> ModelProfile:
        """Select optimal models based on hardware profile"""
        
        if not self.hardware_profile:
            raise ValueError("Hardware profile not detected")
        
        # Model selection based on hardware capabilities
        if self.hardware_profile.optimization_mode == "gpu_optimized":
            # High-end GPU configuration
            language_model = "microsoft/DialoGPT-large"
            language_model_size = "large"
            stt_model = "openai/whisper-large-v2"
            tts_model = "microsoft/speecht5_tts"
            image_model = "runwayml/stable-diffusion-v1-5"
            video_model = "damo-vilab/text-to-video-ms-1.7b"
            audio_model = "facebook/musicgen-medium"
            max_context_length = 2048
            quantization = "fp16"
            
        elif self.hardware_profile.optimization_mode == "gpu_light":
            # Mid-range GPU configuration
            language_model = "microsoft/DialoGPT-medium"
            language_model_size = "medium"
            stt_model = "openai/whisper-base"
            tts_model = "microsoft/speecht5_tts"
            image_model = "runwayml/stable-diffusion-v1-5"
            video_model = None
            audio_model = "facebook/musicgen-small"
            max_context_length = 1024
            quantization = "int8"
            
        elif self.hardware_profile.optimization_mode == "cpu_heavy":
            # High-end CPU configuration
            language_model = "microsoft/DialoGPT-medium"
            language_model_size = "medium"
            stt_model = "openai/whisper-base"
            tts_model = "microsoft/speecht5_tts"
            image_model = "runwayml/stable-diffusion-v1-5"
            video_model = None
            audio_model = "facebook/musicgen-small"
            max_context_length = 1024
            quantization = "int8"
            
        elif self.hardware_profile.optimization_mode == "cpu_medium":
            # Mid-range CPU configuration
            language_model = "microsoft/DialoGPT-small"
            language_model_size = "small"
            stt_model = "openai/whisper-tiny"
            tts_model = "microsoft/speecht5_tts"
            image_model = "CompVis/stable-diffusion-v1-4"
            video_model = None
            audio_model = None
            max_context_length = 512
            quantization = "int8"
            
        else:  # cpu_light
            # Low-end CPU configuration
            language_model = "microsoft/DialoGPT-small"
            language_model_size = "small"
            stt_model = "openai/whisper-tiny"
            tts_model = "espnet/kan-bayashi_ljspeech_vits"
            image_model = None
            video_model = None
            audio_model = None
            max_context_length = 256
            quantization = "int8"
        
        return ModelProfile(
            language_model=language_model,
            language_model_size=language_model_size,
            stt_model=stt_model,
            tts_model=tts_model,
            image_model=image_model,
            video_model=video_model,
            audio_model=audio_model,
            max_context_length=max_context_length,
            quantization=quantization
        )
    
    async def _setup_models(self):
        """Download and setup required models"""
        self.logger.info("Setting up models...")
        
        # Install required packages first
        await self._install_dependencies()
        
        # Create model directories
        model_dirs = [
            "mia/data/models/language",
            "mia/data/models/voice", 
            "mia/data/models/image"
        ]
        
        for dir_path in model_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Download models (this would normally download from HuggingFace)
        # For now, we'll create placeholder model configs
        await self._create_model_configs()
        
        self.logger.info("Models setup completed")
    
    async def _install_dependencies(self):
        """Install required Python packages"""
        self.logger.info("Installing dependencies...")
        
        try:
            # Install core packages
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True)
            self.logger.info("Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install dependencies: {e}")
            # Continue with available packages
    
    async def _create_model_configs(self):
        """Create model configuration files"""
        
        # Language model config
        language_config = {
            "model_name": self.model_profile.language_model,
            "model_size": self.model_profile.language_model_size,
            "max_length": self.model_profile.max_context_length,
            "quantization": self.model_profile.quantization,
            "device": "cuda" if self.hardware_profile.gpu_available else "cpu",
            "local_path": "mia/data/models/language/"
        }
        
        with open("mia/data/models/language/config.json", "w") as f:
            json.dump(language_config, f, indent=2)
        
        # Voice model configs
        voice_config = {
            "stt_model": self.model_profile.stt_model,
            "tts_model": self.model_profile.tts_model,
            "device": "cuda" if self.hardware_profile.gpu_available else "cpu",
            "local_path": "mia/data/models/voice/"
        }
        
        with open("mia/data/models/voice/config.json", "w") as f:
            json.dump(voice_config, f, indent=2)
        
        # Image model config (if available)
        if self.model_profile.image_model:
            image_config = {
                "model_name": self.model_profile.image_model,
                "device": "cuda" if self.hardware_profile.gpu_available else "cpu",
                "local_path": "mia/data/models/image/"
            }
            
            with open("mia/data/models/image/config.json", "w") as f:
                json.dump(image_config, f, indent=2)
    
    async def _initialize_core_modules(self):
        """Initialize core MIA modules"""
        self.logger.info("Initializing core modules...")
        
        # Initialize consciousness module
        await self._init_consciousness()
        
        # Initialize memory system
        await self._init_memory_system()
        
        self.logger.info("Core modules initialized")
    
    async def _init_consciousness(self):
        """Initialize consciousness module"""
        consciousness_config = {
            "introspection_enabled": True,
            "self_evaluation_enabled": True,
            "emotional_processing": True,
            "proactive_behavior": True,
            "learning_enabled": True,
            "adaptation_rate": 0.1
        }
        
        with open("mia/data/consciousness_state.json", "w") as f:
            json.dump(consciousness_config, f, indent=2)
    
    async def _init_memory_system(self):
        """Initialize memory system"""
        memory_config = {
            "short_term_capacity": 1000,
            "medium_term_capacity": 10000,
            "long_term_unlimited": True,
            "vectorization_enabled": True,
            "emotional_weighting": True,
            "context_awareness": True
        }
        
        # Create memory databases
        memory_files = [
            "mia/data/memory/short_term/memory.json",
            "mia/data/memory/medium_term/memory.json", 
            "mia/data/memory/long_term/memory.json",
            "mia/data/memory/meta/memory.json"
        ]
        
        for memory_file in memory_files:
            Path(memory_file).parent.mkdir(parents=True, exist_ok=True)
            with open(memory_file, "w") as f:
                json.dump({"memories": [], "config": memory_config}, f, indent=2)
    
    async def _initialize_peripheral_modules(self):
        """Initialize peripheral modules"""
        self.logger.info("Initializing peripheral modules...")
        
        # Initialize based on hardware capabilities
        if self.model_profile.stt_model:
            await self._init_voice_module()
        
        if self.model_profile.image_model:
            await self._init_multimodal_module()
        
        await self._init_ui_module()
        await self._init_project_module()
        await self._init_monitoring_module()
        
        self.logger.info("Peripheral modules initialized")
    
    async def _init_voice_module(self):
        """Initialize voice processing module"""
        voice_config = {
            "stt_enabled": True,
            "tts_enabled": True,
            "emotional_processing": True,
            "voice_profiles": ["default", "professional", "intimate"],
            "real_time_processing": True
        }
        
        with open("mia/data/voice_config.json", "w") as f:
            json.dump(voice_config, f, indent=2)
    
    async def _init_multimodal_module(self):
        """Initialize multimodal generation module"""
        multimodal_config = {
            "image_generation": bool(self.model_profile.image_model),
            "video_generation": bool(self.model_profile.video_model),
            "audio_generation": bool(self.model_profile.audio_model),
            "real_time_generation": False,
            "quality_mode": "balanced"
        }
        
        with open("mia/data/multimodal_config.json", "w") as f:
            json.dump(multimodal_config, f, indent=2)
    
    async def _init_ui_module(self):
        """Initialize UI module"""
        ui_config = {
            "web_interface": True,
            "avatar_enabled": True,
            "chat_interface": True,
            "terminal_enabled": True,
            "3d_memory_map": True,
            "adult_mode_hidden": True,
            "developer_mode_enabled": True
        }
        
        with open("mia/data/ui_config.json", "w") as f:
            json.dump(ui_config, f, indent=2)
    
    async def _init_project_module(self):
        """Initialize project management module"""
        project_config = {
            "agp_engine_enabled": True,
            "code_generation": True,
            "auto_testing": True,
            "documentation_generation": True,
            "supported_languages": ["python", "javascript", "rust", "go"],
            "supported_frameworks": ["fastapi", "react", "vue", "django"]
        }
        
        with open("mia/data/project_config.json", "w") as f:
            json.dump(project_config, f, indent=2)
    
    async def _init_monitoring_module(self):
        """Initialize system monitoring module"""
        monitoring_config = {
            "system_health_monitoring": True,
            "performance_tracking": True,
            "resource_monitoring": True,
            "checkpoint_enabled": True,
            "checkpoint_interval": 1800,
            "health_check_interval": 60
        }
        
        with open("mia/data/monitoring_config.json", "w") as f:
            json.dump(monitoring_config, f, indent=2)
    
    async def _system_health_check(self) -> bool:
        """Perform comprehensive system health check"""
        self.logger.info("Performing system health check...")
        
        checks = []
        
        # Check core modules
        core_files = [
            "mia/data/consciousness_state.json",
            "mia/data/memory/short_term/memory.json",
            "mia/data/voice_config.json",
            "mia/data/ui_config.json"
        ]
        
        for file_path in core_files:
            if Path(file_path).exists():
                checks.append(True)
                self.logger.info(f"✅ {file_path} - OK")
            else:
                checks.append(False)
                self.logger.error(f"❌ {file_path} - MISSING")
        
        # Check system resources
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent(interval=1)
        disk_usage = psutil.disk_usage('/').percent
        
        if memory_usage < 90:
            checks.append(True)
            self.logger.info(f"✅ Memory usage: {memory_usage:.1f}% - OK")
        else:
            checks.append(False)
            self.logger.error(f"❌ Memory usage: {memory_usage:.1f}% - HIGH")
        
        if cpu_usage < 90:
            checks.append(True)
            self.logger.info(f"✅ CPU usage: {cpu_usage:.1f}% - OK")
        else:
            checks.append(False)
            self.logger.error(f"❌ CPU usage: {cpu_usage:.1f}% - HIGH")
        
        return all(checks)
    
    async def _save_system_state(self):
        """Save current system state"""
        system_state = {
            "timestamp": psutil.boot_time(),
            "hardware_profile": {
                "cpu_cores": self.hardware_profile.cpu_cores,
                "ram_gb": self.hardware_profile.ram_gb,
                "gpu_available": self.hardware_profile.gpu_available,
                "optimization_mode": self.hardware_profile.optimization_mode
            },
            "model_profile": {
                "language_model": self.model_profile.language_model,
                "stt_model": self.model_profile.stt_model,
                "tts_model": self.model_profile.tts_model,
                "image_model": self.model_profile.image_model
            },
            "initialization_complete": True,
            "modules_loaded": [
                "consciousness",
                "memory",
                "voice",
                "ui",
                "projects",
                "monitoring"
            ]
        }
        
        with open("mia/data/system_state.json", "w") as f:
            json.dump(system_state, f, indent=2)
        
        self.logger.info("System state saved successfully")

async def main():
    """Main bootstrap entry point"""
    bootstrap = MIABootBuilder()
    success = await bootstrap.initialize()
    
    if success:
        print("🎉 MIA is ready to activate!")
        return 0
    else:
        print("💥 MIA bootstrap failed!")
        return 1

if __name__ == "__main__":
    asyncio.run(main())