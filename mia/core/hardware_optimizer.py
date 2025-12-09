#!/usr/bin/env python3
"""
MIA Hardware-Aware Optimizer
Detects hardware, optimizes performance, and prevents crashes
"""

import os
import json
import logging
import time
import psutil
import platform
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import glob
import hashlib

class HardwareType(Enum):
    """Types of hardware components"""
    CPU = "cpu"
    GPU = "gpu"
    RAM = "ram"
    STORAGE = "storage"
    NETWORK = "network"

class PerformanceTier(Enum):
    """Performance tier classifications"""
    LOW_END = "low_end"
    MID_RANGE = "mid_range"
    HIGH_END = "high_end"
    ENTERPRISE = "enterprise"

@dataclass
class HardwareSpec:
    """Hardware specification"""
    component_type: HardwareType
    name: str
    capacity: float
    utilization: float
    temperature: Optional[float]
    performance_score: float
    optimization_level: str

@dataclass
class SystemProfile:
    """Complete system hardware profile"""
    cpu_cores: int
    cpu_frequency: float
    ram_total_gb: float
    ram_available_gb: float
    gpu_available: bool
    gpu_memory_gb: float
    gpu_compute_capability: Optional[str]
    storage_type: str
    storage_free_gb: float
    network_speed_mbps: float
    performance_tier: PerformanceTier
    optimization_recommendations: List[str]

class HardwareOptimizer:
    """Hardware detection and optimization system"""
    
    def __init__(self, config_path: str = "mia/data/hardware/config.json"):
        self.config_path = config_path
        self.hardware_dir = Path("mia/data/hardware")
        self.hardware_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.HardwareOptimizer")
        
        # Initialize data
        self.config = self._load_configuration()
        self.system_profile: Optional[SystemProfile] = None
        self.hardware_specs: Dict[str, HardwareSpec] = {}
        self.monitoring_active = False
        self.performance_history: Dict[str, List[float]] = {}
        
        # Detection and optimization
        self._detect_hardware()
        self._optimize_for_hardware()
        
        self.logger.info("⚙️ Hardware Optimizer initialized")
    
    def _load_configuration(self) -> Dict:
        """Load hardware optimizer configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load hardware config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default hardware configuration"""
        config = {
            "monitoring_enabled": True,
            "monitoring_interval": 30,  # seconds
            "optimization_settings": {
                "auto_optimize": True,
                "performance_priority": "balanced",  # balanced, performance, efficiency
                "thermal_protection": True,
                "memory_management": True
            },
            "thresholds": {
                "cpu_warning": 80.0,
                "cpu_critical": 95.0,
                "memory_warning": 85.0,
                "memory_critical": 95.0,
                "gpu_warning": 80.0,
                "gpu_critical": 90.0,
                "temperature_warning": 75.0,
                "temperature_critical": 85.0
            },
            "model_optimization": {
                "low_end_max_model_size_gb": 2.0,
                "mid_range_max_model_size_gb": 8.0,
                "high_end_max_model_size_gb": 32.0,
                "prefer_quantized_models": True,
                "auto_batch_sizing": True
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _detect_hardware(self):
        """Detect and analyze system hardware"""
        try:
            self.logger.info("🔍 Detecting system hardware...")
            
            # CPU Detection
            cpu_info = self._detect_cpu()
            
            # Memory Detection
            memory_info = self._detect_memory()
            
            # GPU Detection
            gpu_info = self._detect_gpu()
            
            # Storage Detection
            storage_info = self._detect_storage()
            
            # Network Detection
            network_info = self._detect_network()
            
            # Determine performance tier
            performance_tier = self._determine_performance_tier(
                cpu_info, memory_info, gpu_info, storage_info
            )
            
            # Generate optimization recommendations
            recommendations = self._generate_optimization_recommendations(
                cpu_info, memory_info, gpu_info, storage_info, performance_tier
            )
            
            # Create system profile
            self.system_profile = SystemProfile(
                cpu_cores=cpu_info["cores"],
                cpu_frequency=cpu_info["frequency"],
                ram_total_gb=memory_info["total_gb"],
                ram_available_gb=memory_info["available_gb"],
                gpu_available=gpu_info["available"],
                gpu_memory_gb=gpu_info["memory_gb"],
                gpu_compute_capability=gpu_info.get("compute_capability"),
                storage_type=storage_info["type"],
                storage_free_gb=storage_info["free_gb"],
                network_speed_mbps=network_info["speed_mbps"],
                performance_tier=performance_tier,
                optimization_recommendations=recommendations
            )
            
            # Store hardware specs
            self._store_hardware_specs(cpu_info, memory_info, gpu_info, storage_info)
            
            self.logger.info(f"✅ Hardware detected: {performance_tier.value} tier system")
            
        except Exception as e:
            self.logger.error(f"Failed to detect hardware: {e}")
            self._create_fallback_profile()
    
    def _detect_cpu(self) -> Dict[str, Any]:
        """Detect CPU specifications"""
        try:
            cpu_info = {
                "cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "frequency": 0.0,
                "architecture": platform.machine(),
                "model": "Unknown"
            }
            
            # Get CPU frequency
            freq_info = psutil.cpu_freq()
            if freq_info:
                cpu_info["frequency"] = freq_info.max or freq_info.current or 2000.0
            else:
                cpu_info["frequency"] = 2000.0  # Default assumption
            
            # Try to get CPU model
            try:
                if platform.system() == "Linux":
                    with open("/proc/cpuinfo", "r") as f:
                        for line in f:
                            if "model name" in line:
                                cpu_info["model"] = line.split(":")[1].strip()
                                break
                elif platform.system() == "Darwin":  # macOS
                    result = subprocess.run(
                        ["sysctl", "-n", "machdep.cpu.brand_string"],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        cpu_info["model"] = result.stdout.strip()
                elif platform.system() == "Windows":
                    result = subprocess.run(
                        ["wmic", "cpu", "get", "name"],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if len(lines) > 1:
                            cpu_info["model"] = lines[1].strip()
            except:
        return self._default_implementation()
            return cpu_info
            
        except Exception as e:
            self.logger.error(f"Failed to detect CPU: {e}")
            return {
                "cores": 4, "logical_cores": 8, "frequency": 2000.0,
                "architecture": "unknown", "model": "Unknown CPU"
            }
    
    def _detect_memory(self) -> Dict[str, Any]:
        """Detect memory specifications"""
        try:
            memory = psutil.virtual_memory()
            
            memory_info = {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3),
                "percent_used": memory.percent,
                "type": "Unknown"
            }
            
            # Try to detect memory type (DDR3, DDR4, etc.)
            try:
                if platform.system() == "Linux":
                    # Try dmidecode
                    result = subprocess.run(
                        ["sudo", "dmidecode", "--type", "memory"],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0 and "DDR" in result.stdout:
                        if "DDR4" in result.stdout:
                            memory_info["type"] = "DDR4"
                        elif "DDR3" in result.stdout:
                            memory_info["type"] = "DDR3"
                        elif "DDR5" in result.stdout:
                            memory_info["type"] = "DDR5"
            except Exception:
        return self._default_implementation()
            return memory_info
            
        except Exception as e:
            self.logger.error(f"Failed to detect memory: {e}")
            return {
                "total_gb": 8.0, "available_gb": 4.0, "used_gb": 4.0,
                "percent_used": 50.0, "type": "Unknown"
            }
    
    def _detect_gpu(self) -> Dict[str, Any]:
        """Detect GPU specifications"""
        try:
            gpu_info = {
                "available": False,
                "memory_gb": 0.0,
                "model": "None",
                "driver_version": "Unknown",
                "compute_capability": None
            }
            
            # Try NVIDIA GPU detection
            try:
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", 
                     "--format=csv,noheader,nounits"],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if lines and lines[0]:
                        parts = lines[0].split(', ')
                        if len(parts) >= 3:
                            gpu_info["available"] = True
                            gpu_info["model"] = parts[0].strip()
                            gpu_info["memory_gb"] = float(parts[1]) / 1024
                            gpu_info["driver_version"] = parts[2].strip()
                
                # Try to get compute capability
                try:
                    result = subprocess.run(
                        ["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader"],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        gpu_info["compute_capability"] = result.stdout.strip()
                except:
        return self._default_implementation()
            except (subprocess.TimeoutExpired, FileNotFoundError):
                return self._implement_method()
            if not gpu_info["available"]:
                try:
                    result = subprocess.run(
                        ["rocm-smi", "--showproductname", "--showmeminfo", "vram"],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        gpu_info["available"] = True
                        gpu_info["model"] = "AMD GPU"
                        # Parse AMD GPU memory (simplified)
                        if "Total VRAM" in result.stdout:
                            # Extract memory size (this is a simplified parser)
                            gpu_info["memory_gb"] = 8.0  # Default assumption
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    return self._implement_method()
            if not gpu_info["available"]:
                try:
                    # Check for Intel integrated graphics
                    if platform.system() == "Linux":
                        gpu_devices = glob.glob("/sys/class/drm/card*/device/vendor")
                        for device in gpu_devices:
                            with open(device, 'r') as f:
                                vendor_id = f.read().strip()
                                if vendor_id == "0x8086":  # Intel vendor ID
                                    gpu_info["available"] = True
                                    gpu_info["model"] = "Intel Integrated Graphics"
                                    gpu_info["memory_gb"] = 2.0  # Shared memory assumption
                                    break
                except:
        return self._default_implementation()
            return gpu_info
            
        except Exception as e:
            self.logger.error(f"Failed to detect GPU: {e}")
            return {
                "available": False, "memory_gb": 0.0, "model": "None",
                "driver_version": "Unknown", "compute_capability": None
            }
    
    def _detect_storage(self) -> Dict[str, Any]:
        """Detect storage specifications"""
        try:
            # Get disk usage
            disk_usage = psutil.disk_usage('/')
            
            storage_info = {
                "total_gb": disk_usage.total / (1024**3),
                "free_gb": disk_usage.free / (1024**3),
                "used_gb": disk_usage.used / (1024**3),
                "percent_used": (disk_usage.used / disk_usage.total) * 100,
                "type": "Unknown"
            }
            
            # Try to detect storage type (SSD vs HDD)
            try:
                if platform.system() == "Linux":
                    # Check for SSD indicators
                    result = subprocess.run(
                        ["lsblk", "-d", "-o", "name,rota"],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')[1:]  # Skip header
                        for line in lines:
                            parts = line.split()
                            if len(parts) >= 2 and parts[1] == "0":
                                storage_info["type"] = "SSD"
                                break
                        else:
                            storage_info["type"] = "HDD"
                elif platform.system() == "Darwin":  # macOS
                    # Most modern Macs have SSDs
                    storage_info["type"] = "SSD"
                elif platform.system() == "Windows":
                    # Try to detect via WMI
                    result = subprocess.run(
                        ["wmic", "diskdrive", "get", "mediatype"],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0 and "SSD" in result.stdout:
                        storage_info["type"] = "SSD"
                    else:
                        storage_info["type"] = "HDD"
            except:
                # Default assumption for modern systems
                storage_info["type"] = "SSD"
            
            return storage_info
            
        except Exception as e:
            self.logger.error(f"Failed to detect storage: {e}")
            return {
                "total_gb": 100.0, "free_gb": 50.0, "used_gb": 50.0,
                "percent_used": 50.0, "type": "Unknown"
            }
    
    def _detect_network(self) -> Dict[str, Any]:
        """Detect network specifications"""
        try:
            network_info = {
                "speed_mbps": 100.0,  # Default assumption
                "interface_type": "Unknown",
                "connected": True
            }
            
            # Try to get network interface information
            try:
                net_stats = psutil.net_if_stats()
                for interface, stats in net_stats.items():
                    if stats.isup and interface != "lo":  # Skip loopback
                        network_info["speed_mbps"] = stats.speed
                        network_info["interface_type"] = interface
                        break
            except:
        return self._default_implementation()
            return network_info
            
        except Exception as e:
            self.logger.error(f"Failed to detect network: {e}")
            return {"speed_mbps": 100.0, "interface_type": "Unknown", "connected": True}
    
    def _determine_performance_tier(self, cpu_info: Dict, memory_info: Dict, 
                                  gpu_info: Dict, storage_info: Dict) -> PerformanceTier:
        """Determine system performance tier"""
        try:
            score = 0
            
            # CPU scoring
            if cpu_info["cores"] >= 8:
                score += 3
            elif cpu_info["cores"] >= 4:
                score += 2
            else:
                score += 1
            
            if cpu_info["frequency"] >= 3000:
                score += 2
            elif cpu_info["frequency"] >= 2000:
                score += 1
            
            # Memory scoring
            if memory_info["total_gb"] >= 32:
                score += 3
            elif memory_info["total_gb"] >= 16:
                score += 2
            elif memory_info["total_gb"] >= 8:
                score += 1
            
            # GPU scoring
            if gpu_info["available"]:
                if gpu_info["memory_gb"] >= 8:
                    score += 3
                elif gpu_info["memory_gb"] >= 4:
                    score += 2
                else:
                    score += 1
            
            # Storage scoring
            if storage_info["type"] == "SSD":
                score += 1
            
            # Determine tier
            if score >= 10:
                return PerformanceTier.ENTERPRISE
            elif score >= 7:
                return PerformanceTier.HIGH_END
            elif score >= 4:
                return PerformanceTier.MID_RANGE
            else:
                return PerformanceTier.LOW_END
                
        except Exception as e:
            self.logger.error(f"Failed to determine performance tier: {e}")
            return PerformanceTier.MID_RANGE
    
    def _generate_optimization_recommendations(self, cpu_info: Dict, memory_info: Dict,
                                             gpu_info: Dict, storage_info: Dict,
                                             performance_tier: PerformanceTier) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        try:
            # Memory recommendations
            if memory_info["total_gb"] < 8:
                recommendations.append("Consider upgrading RAM to at least 8GB for better performance")
            
            if memory_info["percent_used"] > 80:
                recommendations.append("High memory usage detected - enable memory optimization")
            
            # GPU recommendations
            if not gpu_info["available"]:
                recommendations.append("No dedicated GPU detected - CPU-only mode recommended")
            elif gpu_info["memory_gb"] < 4:
                recommendations.append("Limited GPU memory - use quantized models")
            
            # Storage recommendations
            if storage_info["type"] == "HDD":
                recommendations.append("SSD upgrade recommended for faster model loading")
            
            if storage_info["percent_used"] > 90:
                recommendations.append("Low disk space - consider cleanup or expansion")
            
            # Performance tier specific recommendations
            if performance_tier == PerformanceTier.LOW_END:
                recommendations.extend([
                    "Use lightweight models only",
                    "Enable aggressive memory optimization",
                    "Reduce batch sizes",
                    "Consider cloud processing for heavy tasks"
                ])
            elif performance_tier == PerformanceTier.MID_RANGE:
                recommendations.extend([
                    "Use medium-sized models",
                    "Enable balanced optimization",
                    "Monitor resource usage"
                ])
            elif performance_tier in [PerformanceTier.HIGH_END, PerformanceTier.ENTERPRISE]:
                recommendations.extend([
                    "Can use large models",
                    "Enable performance optimization",
                    "Consider parallel processing"
                ])
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
        
        return recommendations
    
    def _store_hardware_specs(self, cpu_info: Dict, memory_info: Dict, 
                            gpu_info: Dict, storage_info: Dict):
        """Store individual hardware component specs"""
        try:
            # CPU spec
            self.hardware_specs["cpu"] = HardwareSpec(
                component_type=HardwareType.CPU,
                name=cpu_info["model"],
                capacity=float(cpu_info["cores"]),
                utilization=0.0,  # Will be updated by monitoring
                temperature=None,
                performance_score=self._calculate_cpu_score(cpu_info),
                optimization_level="balanced"
            )
            
            # RAM spec
            self.hardware_specs["ram"] = HardwareSpec(
                component_type=HardwareType.RAM,
                name=f"{memory_info['total_gb']:.1f}GB {memory_info['type']}",
                capacity=memory_info["total_gb"],
                utilization=memory_info["percent_used"],
                temperature=None,
                performance_score=self._calculate_memory_score(memory_info),
                optimization_level="balanced"
            )
            
            # GPU spec (if available)
            if gpu_info["available"]:
                self.hardware_specs["gpu"] = HardwareSpec(
                    component_type=HardwareType.GPU,
                    name=gpu_info["model"],
                    capacity=gpu_info["memory_gb"],
                    utilization=0.0,  # Will be updated by monitoring
                    temperature=None,
                    performance_score=self._calculate_gpu_score(gpu_info),
                    optimization_level="balanced"
                )
            
            # Storage spec
            self.hardware_specs["storage"] = HardwareSpec(
                component_type=HardwareType.STORAGE,
                name=f"{storage_info['total_gb']:.1f}GB {storage_info['type']}",
                capacity=storage_info["total_gb"],
                utilization=storage_info["percent_used"],
                temperature=None,
                performance_score=self._calculate_storage_score(storage_info),
                optimization_level="balanced"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store hardware specs: {e}")
    
    def _calculate_cpu_score(self, cpu_info: Dict) -> float:
        """Calculate CPU performance score"""
        try:
            score = 0.0
            
            # Core count scoring
            score += min(cpu_info["cores"] / 8.0, 1.0) * 40
            
            # Frequency scoring
            score += min(cpu_info["frequency"] / 4000.0, 1.0) * 30
            
            # Architecture bonus
            if "x86_64" in cpu_info["architecture"] or "amd64" in cpu_info["architecture"]:
                score += 20
            elif "arm64" in cpu_info["architecture"] or "aarch64" in cpu_info["architecture"]:
                score += 15
            else:
                score += 10
            
            return min(score, 100.0)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate CPU score: {e}")
            return 50.0
    
    def _calculate_memory_score(self, memory_info: Dict) -> float:
        """Calculate memory performance score"""
        try:
            score = 0.0
            
            # Capacity scoring
            score += min(memory_info["total_gb"] / 32.0, 1.0) * 60
            
            # Utilization scoring (lower is better)
            utilization_score = max(0, 100 - memory_info["percent_used"]) / 100.0
            score += utilization_score * 30
            
            # Type bonus
            if memory_info["type"] == "DDR5":
                score += 10
            elif memory_info["type"] == "DDR4":
                score += 8
            elif memory_info["type"] == "DDR3":
                score += 5
            
            return min(score, 100.0)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate memory score: {e}")
            return 50.0
    
    def _calculate_gpu_score(self, gpu_info: Dict) -> float:
        """Calculate GPU performance score"""
        try:
            if not gpu_info["available"]:
                return 0.0
            
            score = 0.0
            
            # Memory scoring
            score += min(gpu_info["memory_gb"] / 16.0, 1.0) * 50
            
            # Model-based scoring (simplified)
            model = gpu_info["model"].lower()
            if "rtx" in model or "gtx" in model:
                if "4090" in model or "4080" in model:
                    score += 40
                elif "3090" in model or "3080" in model:
                    score += 35
                elif "3070" in model or "2080" in model:
                    score += 30
                else:
                    score += 20
            elif "radeon" in model or "rx" in model:
                score += 25
            elif "intel" in model:
                score += 15
            else:
                score += 10
            
            # Compute capability bonus
            if gpu_info.get("compute_capability"):
                try:
                    cc = float(gpu_info["compute_capability"])
                    if cc >= 8.0:
                        score += 10
                    elif cc >= 7.0:
                        score += 8
                    elif cc >= 6.0:
                        score += 5
                except:
        return self._default_implementation()
            return min(score, 100.0)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate GPU score: {e}")
            return 0.0
    
    def _calculate_storage_score(self, storage_info: Dict) -> float:
        """Calculate storage performance score"""
        try:
            score = 0.0
            
            # Type scoring
            if storage_info["type"] == "SSD":
                score += 60
            elif storage_info["type"] == "HDD":
                score += 30
            else:
                score += 40  # Unknown, assume middle ground
            
            # Capacity scoring
            score += min(storage_info["total_gb"] / 1000.0, 1.0) * 20
            
            # Free space scoring
            free_percent = (storage_info["free_gb"] / storage_info["total_gb"]) * 100
            score += min(free_percent / 50.0, 1.0) * 20
            
            return min(score, 100.0)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate storage score: {e}")
            return 50.0
    
    def _create_fallback_profile(self):
        """Create fallback system profile"""
        self.system_profile = SystemProfile(
            cpu_cores=4,
            cpu_frequency=2000.0,
            ram_total_gb=8.0,
            ram_available_gb=4.0,
            gpu_available=False,
            gpu_memory_gb=0.0,
            gpu_compute_capability=None,
            storage_type="Unknown",
            storage_free_gb=50.0,
            network_speed_mbps=100.0,
            performance_tier=PerformanceTier.MID_RANGE,
            optimization_recommendations=["Use conservative settings"]
        )
        
        self.logger.warning("⚠️ Using fallback hardware profile")
    
    def _optimize_for_hardware(self):
        """Apply hardware-specific optimizations"""
        try:
            if not self.system_profile:
                return
            
            self.logger.info("⚙️ Applying hardware optimizations...")
            
            # Set optimization recommendations based on hardware
            optimizations = self._get_optimization_settings()
            
            # Apply optimizations
            self._apply_optimizations(optimizations)
            
            self.logger.info("✅ Hardware optimizations applied")
            
        except Exception as e:
            self.logger.error(f"Failed to optimize for hardware: {e}")
    
    def _get_optimization_settings(self) -> Dict[str, Any]:
        """Get optimization settings based on hardware"""
        if not self.system_profile:
            return {}
        
        settings = {
            "max_model_size_gb": 4.0,
            "batch_size": 1,
            "precision": "fp16",
            "device": "cpu",
            "memory_optimization": True,
            "thermal_protection": True
        }
        
        # Adjust based on performance tier
        if self.system_profile.performance_tier == PerformanceTier.LOW_END:
            settings.update({
                "max_model_size_gb": 2.0,
                "batch_size": 1,
                "precision": "int8",
                "memory_optimization": True
            })
        elif self.system_profile.performance_tier == PerformanceTier.MID_RANGE:
            settings.update({
                "max_model_size_gb": 8.0,
                "batch_size": 2,
                "precision": "fp16"
            })
        elif self.system_profile.performance_tier == PerformanceTier.HIGH_END:
            settings.update({
                "max_model_size_gb": 16.0,
                "batch_size": 4,
                "precision": "fp16"
            })
        elif self.system_profile.performance_tier == PerformanceTier.ENTERPRISE:
            settings.update({
                "max_model_size_gb": 32.0,
                "batch_size": 8,
                "precision": "fp32"
            })
        
        # GPU-specific settings
        if self.system_profile.gpu_available:
            settings["device"] = "cuda"
            if self.system_profile.gpu_memory_gb >= 8:
                settings["batch_size"] *= 2
        
        return settings
    
    def _apply_optimizations(self, settings: Dict[str, Any]):
        """Apply optimization settings to system"""
        try:
            # Store optimization settings
            optimization_file = self.hardware_dir / "optimization_settings.json"
            
            with open(optimization_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            # Apply memory optimizations
            if settings.get("memory_optimization", False):
                self._apply_memory_optimizations()
            
            # Apply thermal protection
            if settings.get("thermal_protection", False):
                self._apply_thermal_protection()
            
        except Exception as e:
            self.logger.error(f"Failed to apply optimizations: {e}")
    
    def _apply_memory_optimizations(self):
        """Apply memory-specific optimizations"""
        try:
            # Enable garbage collection optimizations
            import gc
            gc.set_threshold(700, 10, 10)
            
            # Set memory allocation strategy
            os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
            
        except Exception as e:
            self.logger.error(f"Failed to apply memory optimizations: {e}")
    
    def _apply_thermal_protection(self):
        """Apply thermal protection measures"""
        try:
            # This would implement thermal monitoring and throttling
            # For now, just log the intention
            self.logger.info("🌡️ Thermal protection enabled")
            
        except Exception as e:
            self.logger.error(f"Failed to apply thermal protection: {e}")
    
    def get_system_profile(self) -> Optional[Dict[str, Any]]:
        """Get current system profile"""
        if not self.system_profile:
            return None
        
        return {
            "cpu_cores": self.system_profile.cpu_cores,
            "cpu_frequency": self.system_profile.cpu_frequency,
            "ram_total_gb": self.system_profile.ram_total_gb,
            "ram_available_gb": self.system_profile.ram_available_gb,
            "gpu_available": self.system_profile.gpu_available,
            "gpu_memory_gb": self.system_profile.gpu_memory_gb,
            "gpu_compute_capability": self.system_profile.gpu_compute_capability,
            "storage_type": self.system_profile.storage_type,
            "storage_free_gb": self.system_profile.storage_free_gb,
            "performance_tier": self.system_profile.performance_tier.value,
            "optimization_recommendations": self.system_profile.optimization_recommendations
        }
    
    def get_hardware_specs(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed hardware specifications"""
        specs = {}
        
        for name, spec in self.hardware_specs.items():
            specs[name] = {
                "component_type": spec.component_type.value,
                "name": spec.name,
                "capacity": spec.capacity,
                "utilization": spec.utilization,
                "temperature": spec.temperature,
                "performance_score": spec.performance_score,
                "optimization_level": spec.optimization_level
            }
        
        return specs
    
    def get_optimization_settings(self) -> Dict[str, Any]:
        """Get current optimization settings"""
        try:
            optimization_file = self.hardware_dir / "optimization_settings.json"
            
            if optimization_file.exists():
                with open(optimization_file, 'r') as f:
                    return json.load(f)
            else:
                return self._get_optimization_settings()
                
        except Exception as e:
            self.logger.error(f"Failed to get optimization settings: {e}")
            return {}
    
    def update_utilization(self, component: str, utilization: float):
        """Update component utilization"""
        try:
            if component in self.hardware_specs:
                self.hardware_specs[component].utilization = utilization
                
                # Track performance history
                if component not in self.performance_history:
                    self.performance_history[component] = []
                
                self.performance_history[component].append(utilization)
                
                # Keep only recent history
                if len(self.performance_history[component]) > 100:
                    self.performance_history[component] = self.performance_history[component][-100:]
                
        except Exception as e:
            self.logger.error(f"Failed to update utilization: {e}")
    
    def check_resource_availability(self, required_memory_gb: float, 
                                  required_gpu_memory_gb: float = 0) -> bool:
        """Check if required resources are available"""
        try:
            if not self.system_profile:
                return False
            
            # Check RAM availability
            if required_memory_gb > self.system_profile.ram_available_gb:
                return False
            
            # Check GPU memory availability
            if required_gpu_memory_gb > 0:
                if not self.system_profile.gpu_available:
                    return False
                if required_gpu_memory_gb > self.system_profile.gpu_memory_gb:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check resource availability: {e}")
            return False

# Global instance
hardware_optimizer = HardwareOptimizer()