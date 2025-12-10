#!/usr/bin/env python3
"""
MIA Model Discovery System
Automatically discovers and manages local LLM models
"""

import os
import json
import logging
import hashlib
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import psutil

class ModelType(Enum):
    """Types of AI models"""
    LLM = "llm"
    EMBEDDING = "embedding"
    VISION = "vision"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"
    UNKNOWN = "unknown"

class ModelFormat(Enum):
    """Model file formats"""
    GGUF = "gguf"
    SAFETENSORS = "safetensors"
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    ONNX = "onnx"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    UNKNOWN = "unknown"

@dataclass
class ModelInfo:
    """Information about discovered model"""
    name: str
    path: str
    size: int
    format: ModelFormat
    model_type: ModelType
    hash: str
    created_time: float
    modified_time: float
    metadata: Dict[str, Any] = None
    is_loaded: bool = False
    performance_score: float = 0.0

class ModelDiscoveryEngine:
    """Engine for discovering and managing local AI models"""
    
    def __init__(self, config_path: str = "mia/data/models/discovery_config.json"):
        self.config_path = Path(config_path)
        self.logger = self._setup_logging()
        self.discovered_models = {}
        self.scan_paths = []
        self.model_cache = {}
        self.discovery_thread = None
        self.is_scanning = False
        
        self._load_config()
        self._initialize_scan_paths()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup model discovery logging"""
        logger = logging.getLogger("MIA.ModelDiscovery")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _load_config(self):
        """Load discovery configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                self.scan_paths = config.get('scan_paths', [])
                self.file_extensions = config.get('file_extensions', [])
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
        
        # Default configuration
        if not self.scan_paths:
            self.scan_paths = []
        if not hasattr(self, 'file_extensions'):
            self.file_extensions = ['.gguf', '.bin', '.safetensors', '.pt', '.pth', '.onnx']
    
    def _initialize_scan_paths(self):
        """Initialize default scan paths"""
        default_paths = [
            # Common model directories
            Path.home() / "models",
            Path.home() / ".cache" / "huggingface",
            Path.home() / ".ollama" / "models",
            Path.home() / "Downloads",
            Path.home() / "Documents" / "AI_Models",
            
            # System-wide directories
            Path("/opt/models") if os.name != 'nt' else Path("C:/Models"),
            Path("/usr/local/share/models") if os.name != 'nt' else Path("C:/ProgramData/Models"),
            
            # Current project directory
            Path.cwd() / "models",
            Path.cwd() / "mia" / "data" / "models",
        ]
        
        # Add external drives
        external_drives = self._find_external_drives()
        for drive in external_drives:
            default_paths.extend([
                drive / "models",
                drive / "AI_Models",
                drive / "Downloads",
            ])
        
        # Add existing paths and filter valid ones
        all_paths = list(set(self.scan_paths + [str(p) for p in default_paths]))
        self.scan_paths = [p for p in all_paths if Path(p).exists() or self._is_potential_path(p)]
        
        self.logger.info(f"Initialized {len(self.scan_paths)} scan paths")
    
    def _find_external_drives(self) -> List[Path]:
        """Find external drives and USB devices"""
        external_drives = []
        
        try:
            # Get all disk partitions
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    # Skip system drives on Windows
                    if os.name == 'nt' and partition.device in ['C:\\', 'D:\\']:
                        continue
                    
                    # Check if it's a removable drive
                    if 'removable' in partition.opts or 'usb' in partition.opts.lower():
                        external_drives.append(Path(partition.mountpoint))
                        continue
                    
                    # Check disk usage to identify external drives
                    usage = psutil.disk_usage(partition.mountpoint)
                    # If drive is smaller than 2TB, might be external
                    if usage.total < 2 * 1024**4:  # 2TB
                        external_drives.append(Path(partition.mountpoint))
                        
                except (PermissionError, OSError):
                    continue
                    
        except Exception as e:
            self.logger.warning(f"Failed to find external drives: {e}")
        
        self.logger.info(f"Found {len(external_drives)} external drives")
        return external_drives
    
    def _is_potential_path(self, path: str) -> bool:
        """Check if path could potentially exist"""
        path_obj = Path(path)
        return path_obj.parent.exists() if path_obj.parent else False
    
    def start_discovery(self, continuous: bool = True):
        """Start model discovery process"""
        if self.is_scanning:
            self.logger.warning("Discovery already running")
            return
        
        self.is_scanning = True
        
        if continuous:
            self.discovery_thread = threading.Thread(
                target=self._continuous_discovery,
                daemon=True
            )
            self.discovery_thread.start()
            self.logger.info("Started continuous model discovery")
        else:
            self._scan_all_paths()
    
    def stop_discovery(self):
        """Stop model discovery process"""
        self.is_scanning = False
        if self.discovery_thread and self.discovery_thread.is_alive():
            self.discovery_thread.join(timeout=5)
        self.logger.info("Stopped model discovery")
    
    def _continuous_discovery(self):
        """Continuous discovery loop"""
        while self.is_scanning:
            try:
                self._scan_all_paths()
                time.sleep(300)  # Scan every 5 minutes
            except Exception as e:
                self.logger.error(f"Discovery error: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def _scan_all_paths(self):
        """Scan all configured paths for models"""
        self.logger.info("Starting model scan...")
        start_time = time.time()
        
        new_models = 0
        for scan_path in self.scan_paths:
            try:
                path_obj = Path(scan_path)
                if path_obj.exists() and path_obj.is_dir():
                    models_found = self._scan_directory(path_obj)
                    new_models += models_found
                    self.logger.debug(f"Scanned {scan_path}: {models_found} models")
            except Exception as e:
                self.logger.warning(f"Failed to scan {scan_path}: {e}")
        
        scan_time = time.time() - start_time
        self.logger.info(f"Model scan completed: {new_models} new models found in {scan_time:.2f}s")
        
        # Save discovered models
        self._save_model_cache()
    
    def _scan_directory(self, directory: Path) -> int:
        """Scan directory for model files"""
        models_found = 0
        
        try:
            # Recursively scan directory
            for file_path in directory.rglob("*"):
                if file_path.is_file() and self._is_model_file(file_path):
                    model_info = self._analyze_model_file(file_path)
                    if model_info:
                        model_key = self._get_model_key(model_info)
                        if model_key not in self.discovered_models:
                            self.discovered_models[model_key] = model_info
                            models_found += 1
                            self.logger.debug(f"Discovered model: {model_info.name}")
                        
        except (PermissionError, OSError) as e:
            self.logger.warning(f"Cannot access directory {directory}: {e}")
        
        return models_found
    
    def _is_model_file(self, file_path: Path) -> bool:
        """Check if file is a potential model file"""
        # Check file extension
        if file_path.suffix.lower() not in self.file_extensions:
            return False
        
        # Check file size (models are usually large)
        try:
            file_size = file_path.stat().st_size
            if file_size < 1024 * 1024:  # Less than 1MB
                return False
        except OSError:
            return False
        
        # Check filename patterns
        filename_lower = file_path.name.lower()
        model_indicators = [
            'model', 'llm', 'gpt', 'bert', 'transformer', 'neural',
            'embedding', 'vision', 'audio', 'multimodal', 'chat',
            'instruct', 'base', 'fine', 'tune', 'lora', 'adapter'
        ]
        
        return any(indicator in filename_lower for indicator in model_indicators)
    
    def _analyze_model_file(self, file_path: Path) -> Optional[ModelInfo]:
        """Analyze model file and extract information"""
        try:
            stat = file_path.stat()
            
            # Calculate file hash (for smaller files)
            file_hash = self._calculate_file_hash(file_path)
            
            # Determine model format
            model_format = self._detect_model_format(file_path)
            
            # Determine model type
            model_type = self._detect_model_type(file_path)
            
            # Extract metadata
            metadata = self._extract_metadata(file_path, model_format)
            
            model_info = ModelInfo(
                name=file_path.stem,
                path=str(file_path),
                size=stat.st_size,
                format=model_format,
                model_type=model_type,
                hash=file_hash,
                created_time=stat.st_ctime,
                modified_time=stat.st_mtime,
                metadata=metadata
            )
            
            return model_info
            
        except Exception as e:
            self.logger.warning(f"Failed to analyze {file_path}: {e}")
            return None
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate file hash for identification"""
        try:
            # For large files, hash only first and last 1MB
            file_size = file_path.stat().st_size
            hash_obj = hashlib.sha256()
            
            with open(file_path, 'rb') as f:
                if file_size > 2 * 1024 * 1024:  # > 2MB
                    # Hash first 1MB
                    hash_obj.update(f.read(1024 * 1024))
                    # Hash last 1MB
                    f.seek(-1024 * 1024, 2)
                    hash_obj.update(f.read(1024 * 1024))
                else:
                    # Hash entire file
                    hash_obj.update(f.read())
            
            return hash_obj.hexdigest()[:16]  # First 16 chars
            
        except Exception as e:
            self.logger.warning(f"Failed to hash {file_path}: {e}")
            return "unknown"
    
    def _detect_model_format(self, file_path: Path) -> ModelFormat:
        """Detect model file format"""
        suffix = file_path.suffix.lower()
        
        format_map = {
            '.gguf': ModelFormat.GGUF,
            '.safetensors': ModelFormat.SAFETENSORS,
            '.pt': ModelFormat.PYTORCH,
            '.pth': ModelFormat.PYTORCH,
            '.bin': ModelFormat.PYTORCH,
            '.onnx': ModelFormat.ONNX,
            '.pb': ModelFormat.TENSORFLOW,
        }
        
        # Check for Hugging Face models
        if file_path.parent.name == 'models--' or 'huggingface' in str(file_path):
            return ModelFormat.HUGGINGFACE
        
        # Check for Ollama models
        if '.ollama' in str(file_path):
            return ModelFormat.OLLAMA
        
        return format_map.get(suffix, ModelFormat.UNKNOWN)
    
    def _detect_model_type(self, file_path: Path) -> ModelType:
        """Detect model type from filename and path"""
        path_str = str(file_path).lower()
        filename = file_path.name.lower()
        
        # Vision models
        if any(term in path_str for term in ['vision', 'clip', 'vit', 'image', 'visual']):
            return ModelType.VISION
        
        # Audio models
        if any(term in path_str for term in ['audio', 'speech', 'whisper', 'wav2vec', 'tts', 'stt']):
            return ModelType.AUDIO
        
        # Embedding models
        if any(term in path_str for term in ['embedding', 'sentence', 'e5', 'bge', 'gte']):
            return ModelType.EMBEDDING
        
        # Multimodal models
        if any(term in path_str for term in ['multimodal', 'llava', 'blip', 'flamingo']):
            return ModelType.MULTIMODAL
        
        # LLM models (default for most)
        if any(term in path_str for term in ['llm', 'gpt', 'llama', 'mistral', 'chat', 'instruct']):
            return ModelType.LLM
        
        return ModelType.LLM  # Default assumption
    
    def _extract_metadata(self, file_path: Path, model_format: ModelFormat) -> Dict[str, Any]:
        """Extract metadata from model file"""
        metadata = {
            'file_name': file_path.name,
            'directory': str(file_path.parent),
            'format': model_format.value
        }
        
        # Try to extract more specific metadata based on format
        try:
            if model_format == ModelFormat.HUGGINGFACE:
                config_path = file_path.parent / 'config.json'
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        metadata.update({
                            'architecture': config.get('architectures', []),
                            'model_type': config.get('model_type', 'unknown'),
                            'vocab_size': config.get('vocab_size', 0)
                        })
        except Exception as e:
            self.logger.debug(f"Failed to extract metadata from {file_path}: {e}")
        
        return metadata
    
    def _get_model_key(self, model_info: ModelInfo) -> str:
        """Generate unique key for model"""
        return f"{model_info.name}_{model_info.hash}"
    
    def _save_model_cache(self):
        """Save discovered models to cache"""
        try:
            cache_path = Path("mia/data/models/discovered_models.json")
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert models to dict with enum serialization
            models_dict = {}
            for k, v in self.discovered_models.items():
                model_dict = asdict(v)
                # Convert enums to strings for JSON serialization
                model_dict['format'] = v.format.value
                model_dict['model_type'] = v.model_type.value
                models_dict[k] = model_dict
            
            cache_data = {
                'last_scan': time.time(),
                'models': models_dict
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
            self.logger.debug(f"Saved {len(self.discovered_models)} models to cache")
            
        except Exception as e:
            self.logger.error(f"Failed to save model cache: {e}")
    
    def load_model_cache(self):
        """Load discovered models from cache"""
        try:
            cache_path = Path("mia/data/models/discovered_models.json")
            if cache_path.exists():
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)
                
                for key, model_data in cache_data.get('models', {}).items():
                    # Convert back to ModelInfo object
                    model_data['format'] = ModelFormat(model_data['format'])
                    model_data['model_type'] = ModelType(model_data['model_type'])
                    self.discovered_models[key] = ModelInfo(**model_data)
                
                self.logger.info(f"Loaded {len(self.discovered_models)} models from cache")
                
        except Exception as e:
            self.logger.warning(f"Failed to load model cache: {e}")
    
    def get_discovered_models(self) -> Dict[str, ModelInfo]:
        """Get all discovered models"""
        return self.discovered_models.copy()
    
    def get_models_by_type(self, model_type: ModelType) -> List[ModelInfo]:
        """Get models filtered by type"""
        return [model for model in self.discovered_models.values() 
                if model.model_type == model_type]
    
    def get_best_llm_models(self, limit: int = 5) -> List[ModelInfo]:
        """Get best LLM models based on size and performance"""
        llm_models = self.get_models_by_type(ModelType.LLM)
        
        # Sort by size (larger models often better) and performance score
        sorted_models = sorted(
            llm_models,
            key=lambda m: (m.performance_score, m.size),
            reverse=True
        )
        
        return sorted_models[:limit]
    
    def add_scan_path(self, path: str):
        """Add new path to scan"""
        if path not in self.scan_paths:
            self.scan_paths.append(path)
            self.logger.info(f"Added scan path: {path}")
    
    def remove_scan_path(self, path: str):
        """Remove path from scan"""
        if path in self.scan_paths:
            self.scan_paths.remove(path)
            self.logger.info(f"Removed scan path: {path}")
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get discovery statistics"""
        stats = {
            'total_models': len(self.discovered_models),
            'scan_paths': len(self.scan_paths),
            'is_scanning': self.is_scanning,
            'models_by_type': {},
            'models_by_format': {},
            'total_size': 0
        }
        
        for model in self.discovered_models.values():
            # Count by type
            type_name = model.model_type.value
            stats['models_by_type'][type_name] = stats['models_by_type'].get(type_name, 0) + 1
            
            # Count by format
            format_name = model.format.value
            stats['models_by_format'][format_name] = stats['models_by_format'].get(format_name, 0) + 1
            
            # Total size
            stats['total_size'] += model.size
        
        return stats

# Global model discovery instance
model_discovery = ModelDiscoveryEngine()

def discover_models(continuous: bool = True):
    """Start model discovery"""
    model_discovery.start_discovery(continuous)

def get_available_models() -> Dict[str, ModelInfo]:
    """Get all available models"""
    return model_discovery.get_discovered_models()

def get_best_llm_models(limit: int = 5) -> List[ModelInfo]:
    """Get best available LLM models"""
    return model_discovery.get_best_llm_models(limit)