#!/usr/bin/env python3
"""
Adaptive Resource Manager for MIA
=================================

Avtomatsko spremljanje sistemskih zmogljivosti in prilagajanje MIA delovanja.
Preprečuje crash sistema z dinamičnim upravljanjem virov.
"""

import psutil
import time
import logging
import json
import threading
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path

# GPU detection (optional)
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class SystemCapabilities:
    """Sistemske zmogljivosti"""
    cpu_cores: int
    cpu_frequency_mhz: float
    total_memory_gb: float
    available_memory_gb: float
    gpu_available: bool
    gpu_memory_gb: float
    disk_free_gb: float
    
@dataclass
class ResourceLimits:
    """Omejitve virov za MIA"""
    max_cpu_percent: float
    max_memory_percent: float
    max_gpu_percent: float
    max_concurrent_processes: int
    model_size_limit_gb: float
    chunk_size_limit: int

@dataclass
class CurrentUsage:
    """Trenutna uporaba virov"""
    cpu_percent: float
    memory_percent: float
    gpu_percent: float
    disk_usage_percent: float
    mia_processes: int
    timestamp: float

class AdaptiveResourceManager:
    """
    Upravljalec virov, ki avtomatsko prilagaja MIA delovanje sistemskim zmogljivostim.
    
    Ključne funkcionalnosti:
    - Avtomatska detekcija sistemskih zmogljivosti
    - Kontinuirano spremljanje uporabe virov
    - Dinamično prilagajanje MIA nastavitev
    - Preprečevanje crash-a sistema
    - Optimizacija performance
    """
    
    def __init__(self, config_dir: str = "data/system"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # System info
        self.capabilities: Optional[SystemCapabilities] = None
        self.current_usage: Optional[CurrentUsage] = None
        self.resource_limits: Optional[ResourceLimits] = None
        
        # Monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_interval = 30  # seconds
        
        # Callbacks for resource changes
        self.resource_callbacks: Dict[str, Callable] = {}
        
        # Emergency thresholds
        self.emergency_thresholds = {
            'cpu': 95.0,
            'memory': 95.0,
            'gpu': 98.0
        }
        
        # Initialize
        self.detect_system_capabilities()
        self.calculate_optimal_limits()
        
        logger.info("Adaptive Resource Manager initialized")
        
    def detect_system_capabilities(self) -> SystemCapabilities:
        """Zaznaj sistemske zmogljivosti"""
        try:
            # CPU info
            cpu_info = psutil.cpu_freq()
            cpu_cores = psutil.cpu_count()
            cpu_frequency = cpu_info.max if cpu_info else 0
            
            # Memory info
            memory = psutil.virtual_memory()
            total_memory_gb = memory.total / (1024**3)
            available_memory_gb = memory.available / (1024**3)
            
            # GPU info
            gpu_available = False
            gpu_memory_gb = 0
            
            if GPU_AVAILABLE:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]  # Primary GPU
                        gpu_available = True
                        gpu_memory_gb = gpu.memoryTotal / 1024  # Convert MB to GB
                except Exception as e:
                    logger.warning(f"GPU detection failed: {e}")
            
            # Disk info
            disk = psutil.disk_usage('/')
            disk_free_gb = disk.free / (1024**3)
            
            self.capabilities = SystemCapabilities(
                cpu_cores=cpu_cores,
                cpu_frequency_mhz=cpu_frequency,
                total_memory_gb=total_memory_gb,
                available_memory_gb=available_memory_gb,
                gpu_available=gpu_available,
                gpu_memory_gb=gpu_memory_gb,
                disk_free_gb=disk_free_gb
            )
            
            logger.info(f"Detected system capabilities: {asdict(self.capabilities)}")
            
            # Save to file
            self.save_capabilities()
            
            return self.capabilities
            
        except Exception as e:
            logger.error(f"Error detecting system capabilities: {e}")
            # Fallback to minimal capabilities
            self.capabilities = SystemCapabilities(
                cpu_cores=2, cpu_frequency_mhz=2000, total_memory_gb=4,
                available_memory_gb=2, gpu_available=False, gpu_memory_gb=0,
                disk_free_gb=10
            )
            return self.capabilities
            
    def calculate_optimal_limits(self) -> ResourceLimits:
        """Izračunaj optimalne omejitve na podlagi zmogljivosti"""
        if not self.capabilities:
            self.detect_system_capabilities()
            
        caps = self.capabilities
        
        # Conservative limits to prevent system crash
        max_cpu_percent = min(80.0, 60.0 + (caps.cpu_cores - 2) * 5)  # More cores = higher limit
        max_memory_percent = 75.0 if caps.total_memory_gb >= 8 else 60.0
        max_gpu_percent = 85.0 if caps.gpu_available else 0.0
        
        # Concurrent processes based on CPU cores
        max_concurrent = max(1, caps.cpu_cores // 2)
        
        # Model size limit based on available memory
        if caps.total_memory_gb >= 32:
            model_size_limit = 8.0  # 8GB models
        elif caps.total_memory_gb >= 16:
            model_size_limit = 4.0  # 4GB models
        elif caps.total_memory_gb >= 8:
            model_size_limit = 2.0  # 2GB models
        else:
            model_size_limit = 1.0  # 1GB models
            
        # Chunk size based on memory
        chunk_size = int(caps.total_memory_gb * 1000)  # 1000 per GB
        chunk_size = max(500, min(chunk_size, 10000))  # Between 500-10000
        
        self.resource_limits = ResourceLimits(
            max_cpu_percent=max_cpu_percent,
            max_memory_percent=max_memory_percent,
            max_gpu_percent=max_gpu_percent,
            max_concurrent_processes=max_concurrent,
            model_size_limit_gb=model_size_limit,
            chunk_size_limit=chunk_size
        )
        
        logger.info(f"Calculated optimal limits: {asdict(self.resource_limits)}")
        
        # Save to file
        self.save_limits()
        
        return self.resource_limits
        
    def get_current_usage(self) -> CurrentUsage:
        """Pridobi trenutno uporabo virov"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # GPU usage
            gpu_percent = 0.0
            if GPU_AVAILABLE and self.capabilities.gpu_available:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu_percent = gpus[0].load * 100
                except:
                    pass
                    
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Count MIA processes (simplified)
            mia_processes = len([p for p in psutil.process_iter(['name']) 
                               if 'mia' in p.info['name'].lower()])
            
            self.current_usage = CurrentUsage(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                gpu_percent=gpu_percent,
                disk_usage_percent=disk_percent,
                mia_processes=mia_processes,
                timestamp=time.time()
            )
            
            return self.current_usage
            
        except Exception as e:
            logger.error(f"Error getting current usage: {e}")
            return CurrentUsage(0, 0, 0, 0, 0, time.time())
            
    def is_system_overloaded(self) -> Dict[str, bool]:
        """Preveri, ali je sistem preobremenjeni"""
        usage = self.get_current_usage()
        limits = self.resource_limits
        
        overload_status = {
            'cpu': usage.cpu_percent > limits.max_cpu_percent,
            'memory': usage.memory_percent > limits.max_memory_percent,
            'gpu': usage.gpu_percent > limits.max_gpu_percent,
            'emergency_cpu': usage.cpu_percent > self.emergency_thresholds['cpu'],
            'emergency_memory': usage.memory_percent > self.emergency_thresholds['memory'],
            'emergency_gpu': usage.gpu_percent > self.emergency_thresholds['gpu']
        }
        
        return overload_status
        
    def get_recommended_settings(self) -> Dict[str, Any]:
        """Pridobi priporočene nastavitve za MIA"""
        usage = self.get_current_usage()
        limits = self.resource_limits
        overload = self.is_system_overloaded()
        
        # Base settings from limits
        settings = {
            'max_concurrent_processes': limits.max_concurrent_processes,
            'model_size_limit_gb': limits.model_size_limit_gb,
            'chunk_size': limits.chunk_size_limit,
            'enable_gpu': self.capabilities.gpu_available,
            'memory_limit_gb': self.capabilities.total_memory_gb * (limits.max_memory_percent / 100),
            'cpu_threads': self.capabilities.cpu_cores
        }
        
        # Adjust based on current load
        if overload['cpu'] or overload['memory']:
            # Reduce load
            settings['max_concurrent_processes'] = max(1, settings['max_concurrent_processes'] // 2)
            settings['chunk_size'] = max(100, settings['chunk_size'] // 2)
            settings['model_size_limit_gb'] = max(0.5, settings['model_size_limit_gb'] / 2)
            
        if any(overload[key] for key in ['emergency_cpu', 'emergency_memory', 'emergency_gpu']):
            # Emergency mode - minimal settings
            settings['max_concurrent_processes'] = 1
            settings['chunk_size'] = 100
            settings['model_size_limit_gb'] = 0.5
            settings['enable_gpu'] = False
            
        return settings
        
    def start_monitoring(self):
        """Začni kontinuirano spremljanje virov"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("Started resource monitoring")
        
    def stop_monitoring(self):
        """Ustavi spremljanje virov"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
            
        logger.info("Stopped resource monitoring")
        
    def _monitoring_loop(self):
        """Glavna zanka za spremljanje virov"""
        while self.monitoring_active:
            try:
                # Get current usage
                usage = self.get_current_usage()
                overload = self.is_system_overloaded()
                
                # Log status
                logger.debug(f"Resource usage: CPU={usage.cpu_percent:.1f}%, "
                           f"Memory={usage.memory_percent:.1f}%, "
                           f"GPU={usage.gpu_percent:.1f}%")
                
                # Check for overload
                if any(overload.values()):
                    logger.warning(f"System overload detected: {overload}")
                    self._handle_overload(overload)
                    
                # Call registered callbacks
                for name, callback in self.resource_callbacks.items():
                    try:
                        callback(usage, overload)
                    except Exception as e:
                        logger.error(f"Error in callback {name}: {e}")
                        
                # Wait before next check
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Short wait on error
                
    def _handle_overload(self, overload_status: Dict[str, bool]):
        """Obravnavaj preobremenjeni sistem"""
        emergency = any(overload_status[key] for key in ['emergency_cpu', 'emergency_memory', 'emergency_gpu'])
        
        if emergency:
            logger.critical("EMERGENCY: System critically overloaded!")
            # Trigger emergency callbacks
            for name, callback in self.resource_callbacks.items():
                if 'emergency' in name:
                    try:
                        callback(overload_status)
                    except Exception as e:
                        logger.error(f"Error in emergency callback {name}: {e}")
        else:
            logger.warning("System overloaded, adjusting MIA settings")
            # Trigger adjustment callbacks
            for name, callback in self.resource_callbacks.items():
                if 'adjust' in name:
                    try:
                        callback(overload_status)
                    except Exception as e:
                        logger.error(f"Error in adjustment callback {name}: {e}")
                        
    def register_callback(self, name: str, callback: Callable):
        """Registriraj callback za spremembe virov"""
        self.resource_callbacks[name] = callback
        logger.info(f"Registered callback: {name}")
        
    def unregister_callback(self, name: str):
        """Odstrani callback"""
        if name in self.resource_callbacks:
            del self.resource_callbacks[name]
            logger.info(f"Unregistered callback: {name}")
            
    def save_capabilities(self):
        """Shrani zmogljivosti na disk"""
        if self.capabilities:
            caps_file = self.config_dir / 'system_capabilities.json'
            with open(caps_file, 'w') as f:
                json.dump(asdict(self.capabilities), f, indent=2)
                
    def save_limits(self):
        """Shrani omejitve na disk"""
        if self.resource_limits:
            limits_file = self.config_dir / 'resource_limits.json'
            with open(limits_file, 'w') as f:
                json.dump(asdict(self.resource_limits), f, indent=2)
                
    def get_system_info(self) -> Dict[str, Any]:
        """Pridobi celotne informacije o sistemu"""
        return {
            'capabilities': asdict(self.capabilities) if self.capabilities else None,
            'current_usage': asdict(self.current_usage) if self.current_usage else None,
            'resource_limits': asdict(self.resource_limits) if self.resource_limits else None,
            'overload_status': self.is_system_overloaded(),
            'recommended_settings': self.get_recommended_settings(),
            'monitoring_active': self.monitoring_active
        }

# Example usage and testing
def main():
    """Primer uporabe AdaptiveResourceManager"""
    
    # Initialize resource manager
    arm = AdaptiveResourceManager("data/test_system")
    
    print("=== MIA Adaptive Resource Manager Test ===")
    
    # Display system capabilities
    print(f"\n1. System Capabilities:")
    caps = arm.capabilities
    print(f"   CPU: {caps.cpu_cores} cores @ {caps.cpu_frequency_mhz:.0f} MHz")
    print(f"   Memory: {caps.total_memory_gb:.1f} GB total, {caps.available_memory_gb:.1f} GB available")
    print(f"   GPU: {'Available' if caps.gpu_available else 'Not available'}")
    if caps.gpu_available:
        print(f"   GPU Memory: {caps.gpu_memory_gb:.1f} GB")
    print(f"   Disk Free: {caps.disk_free_gb:.1f} GB")
    
    # Display resource limits
    print(f"\n2. Resource Limits:")
    limits = arm.resource_limits
    print(f"   Max CPU: {limits.max_cpu_percent:.1f}%")
    print(f"   Max Memory: {limits.max_memory_percent:.1f}%")
    print(f"   Max GPU: {limits.max_gpu_percent:.1f}%")
    print(f"   Max Processes: {limits.max_concurrent_processes}")
    print(f"   Model Size Limit: {limits.model_size_limit_gb:.1f} GB")
    print(f"   Chunk Size: {limits.chunk_size_limit}")
    
    # Display current usage
    print(f"\n3. Current Usage:")
    usage = arm.get_current_usage()
    print(f"   CPU: {usage.cpu_percent:.1f}%")
    print(f"   Memory: {usage.memory_percent:.1f}%")
    print(f"   GPU: {usage.gpu_percent:.1f}%")
    print(f"   Disk: {usage.disk_usage_percent:.1f}%")
    print(f"   MIA Processes: {usage.mia_processes}")
    
    # Check overload status
    print(f"\n4. Overload Status:")
    overload = arm.is_system_overloaded()
    for resource, is_overloaded in overload.items():
        status = "⚠️ OVERLOADED" if is_overloaded else "✅ OK"
        print(f"   {resource}: {status}")
        
    # Get recommended settings
    print(f"\n5. Recommended Settings:")
    settings = arm.get_recommended_settings()
    for key, value in settings.items():
        print(f"   {key}: {value}")
        
    print("\n=== Test completed ===")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()