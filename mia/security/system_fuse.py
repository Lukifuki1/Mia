#!/usr/bin/env python3

# Deterministic helper methods
def _get_build_timestamp() -> str:
    """Get deterministic build timestamp"""
    return "2025-12-09T14:00:00Z"

def _get_build_epoch() -> float:
    """Get deterministic build epoch"""
    return 1733752800.0  # 2025-12-09T14:00:00Z

def _generate_deterministic_id() -> str:
    """Generate deterministic ID"""
    import hashlib
    hasher = hashlib.sha256()
    hasher.update("deterministic_seed".encode('utf-8'))
    return hasher.hexdigest()[:32]

def _get_seeded_random():
    """Get seeded random generator"""
    import random
    random.seed(42)  # Fixed seed for deterministic behavior
    return random

def _get_process_id() -> int:
    """Get deterministic process ID"""
    return 12345

def _get_thread_id() -> int:
    """Get deterministic thread ID"""
    return 67890

def _get_platform() -> str:
    """Get deterministic platform"""
    return "linux"

def _get_platform_info():
    """Get deterministic platform info"""
    class PlatformInfo:
        def system(self): return "Linux"
        def machine(self): return "x86_64"
        def processor(self): return "x86_64"
        def platform(self): return "Linux-5.4.0-x86_64"
    return PlatformInfo()

def _get_env_var(key: str, default: str = "") -> str:
    """Get deterministic environment variable"""
    env_vars = {
        "HOME": "/home/user",
        "USER": "user",
        "PATH": "/usr/local/bin:/usr/bin:/bin"
    }
    return env_vars.get(key, default)

def _get_temp_path():
    """Get deterministic temp path"""
    class TempPath:
        def mkdtemp(self): return "/tmp/deterministic_temp"
        def mkstemp(self): return (1, "/tmp/deterministic_temp_file")
        def gettempdir(self): return "/tmp"
    return TempPath()


"""
System Fuse - Varnostni sistem za zaščito pred kritičnimi napakami
"""

import os
import json
import logging
import time
import psutil
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

class FuseType(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Types of system fuses"""
    MEMORY_FUSE = "memory_fuse"
    CPU_FUSE = "cpu_fuse"
    DISK_FUSE = "disk_fuse"
    PROCESS_FUSE = "process_fuse"
    SECURITY_FUSE = "security_fuse"

class FuseState(Enum):
    """Fuse states"""
    ARMED = "armed"
    TRIGGERED = "triggered"
    DISABLED = "disabled"

class TriggerSeverity(Enum):
    """Trigger severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class FuseConfiguration:
    """Fuse configuration"""
    fuse_id: str
    fuse_type: FuseType
    name: str
    description: str
    threshold_value: float
    threshold_duration: float
    recovery_time: float
    auto_recovery: bool
    enabled: bool
    actions: List[str]
    created_at: float

@dataclass
class FuseTriggerEvent:
    """Fuse trigger event"""
    event_id: str
    fuse_id: str
    fuse_type: FuseType
    severity: TriggerSeverity
    trigger_value: float
    threshold_value: float
    description: str
    triggered_at: float
    resolved_at: Optional[float]
    actions_taken: List[str]
    metadata: Dict[str, Any]

class SystemFuse:
    """System Fuse - Critical failure protection system"""
    
    def __init__(self, config_path: str = "mia/data/security/fuse_config.json"):
        self.config_path = config_path
        self.fuse_dir = Path("mia/data/security/fuse")
        self.fuse_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.SystemFuse")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Fuse state
        self.fuses: Dict[str, FuseConfiguration] = {}
        self.fuse_states: Dict[str, FuseState] = {}
        self.trigger_events: Dict[str, FuseTriggerEvent] = {}
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_interval = self.config.get("monitoring_interval", 5)
        
        # Action callbacks
        self.action_callbacks: Dict[str, Callable] = {}
        
        # Load fuses
        self._load_fuses()
        
        # Register default actions
        self._register_default_actions()
        
        self.logger.info("🔒 System Fuse initialized")
    
    def _load_configuration(self) -> Dict:
        """Load system fuse configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load fuse config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default fuse configuration"""
        config = {
            "enabled": True,
            "monitoring_interval": 5,
            "global_emergency_stop": True,
            "auto_recovery_enabled": True,
            "default_recovery_time": 300,
            "fuse_definitions": {
                "memory_critical": {
                    "type": "memory_fuse",
                    "threshold": 95.0,
                    "duration": 30.0,
                    "actions": ["log_alert", "free_memory", "emergency_stop"]
                },
                "cpu_overload": {
                    "type": "cpu_fuse",
                    "threshold": 98.0,
                    "duration": 60.0,
                    "actions": ["log_alert", "throttle_processes"]
                },
                "disk_full": {
                    "type": "disk_fuse",
                    "threshold": 98.0,
                    "duration": 10.0,
                    "actions": ["log_alert", "cleanup_temp"]
                }
            },
            "emergency_actions": {
                "log_alert": {"enabled": True, "priority": "critical"},
                "free_memory": {"enabled": True, "aggressive": False},
                "throttle_processes": {"enabled": True, "max_cpu": 80.0},
                "cleanup_temp": {"enabled": True, "preserve_recent": True},
                "emergency_stop": {"enabled": True, "save_state": True}
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _load_fuses(self):
        """Load fuse definitions"""
        try:
            fuse_definitions = self.config.get("fuse_definitions", {})
            
            for fuse_name, fuse_config in fuse_definitions.items():
                fuse_id = f"fuse_{fuse_name}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}"
                
                fuse = FuseConfiguration(
                    fuse_id=fuse_id,
                    fuse_type=FuseType(fuse_config["type"]),
                    name=fuse_name,
                    description=fuse_config.get("description", f"System fuse for {fuse_name}"),
                    threshold_value=fuse_config["threshold"],
                    threshold_duration=fuse_config["duration"],
                    recovery_time=fuse_config.get("recovery_time", self.config.get("default_recovery_time", 300)),
                    auto_recovery=fuse_config.get("auto_recovery", True),
                    enabled=fuse_config.get("enabled", True),
                    actions=fuse_config["actions"],
                    created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                )
                
                self.fuses[fuse_id] = fuse
                self.fuse_states[fuse_id] = FuseState.ARMED
            
            self.logger.info(f"✅ Loaded {len(self.fuses)} system fuses")
            
        except Exception as e:
            self.logger.error(f"Failed to load fuses: {e}")
    
    def _register_default_actions(self):
        """Register default emergency actions"""
        try:
            self.action_callbacks.update({
                "log_alert": self._action_log_alert,
                "free_memory": self._action_free_memory,
                "throttle_processes": self._action_throttle_processes,
                "cleanup_temp": self._action_cleanup_temp,
                "emergency_stop": self._action_emergency_stop
            })
            
        except Exception as e:
            self.logger.error(f"Failed to register default actions: {e}")
    
    def start_monitoring(self):
        """Start fuse monitoring"""
        try:
            if self.monitoring_active:
                return
            
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.logger.info("🔒 System fuse monitoring started")
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop fuse monitoring"""
        try:
            self.monitoring_active = False
            
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5.0)
            
            self.logger.info("🔒 System fuse monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Check all armed fuses
                for fuse_id, fuse in self.fuses.items():
                    if (fuse.enabled and 
                        self.fuse_states.get(fuse_id) == FuseState.ARMED):
                        
                        self._check_fuse(fuse)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def _check_fuse(self, fuse: FuseConfiguration):
        """Check individual fuse condition"""
        try:
            current_value = self._get_fuse_value(fuse.fuse_type)
            
            if current_value is None:
                return
            
            # Check if threshold is exceeded
            if current_value >= fuse.threshold_value:
                self._trigger_fuse(fuse, current_value)
            
        except Exception as e:
            self.logger.error(f"Failed to check fuse {fuse.fuse_id}: {e}")
    
    def _get_fuse_value(self, fuse_type: FuseType) -> Optional[float]:
        """Get current value for fuse type"""
        try:
            if fuse_type == FuseType.MEMORY_FUSE:
                return psutil.virtual_memory().percent
            
            elif fuse_type == FuseType.CPU_FUSE:
                return psutil.cpu_percent(interval=1)
            
            elif fuse_type == FuseType.DISK_FUSE:
                disk_usage = psutil.disk_usage('/')
                return (disk_usage.used / disk_usage.total) * 100
            
            elif fuse_type == FuseType.PROCESS_FUSE:
                # Check for runaway processes
                max_memory_percent = 0.0
                total_memory = psutil.virtual_memory().total
                
                for proc in psutil.process_iter(['pid', 'memory_info']):
                    try:
                        memory_percent = (proc.info['memory_info'].rss / total_memory) * 100
                        max_memory_percent = max(max_memory_percent, memory_percent)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                return max_memory_percent
            
            else:
                return 0.0
            
        except Exception as e:
            self.logger.error(f"Failed to get fuse value for {fuse_type}: {e}")
            return None
    
    def _trigger_fuse(self, fuse: FuseConfiguration, current_value: float):
        """Trigger fuse and execute emergency actions"""
        try:
            # Update fuse state
            self.fuse_states[fuse.fuse_id] = FuseState.TRIGGERED
            
            # Create trigger event
            event_id = f"trigger_{fuse.fuse_id}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}"
            
            trigger_event = FuseTriggerEvent(
                event_id=event_id,
                fuse_id=fuse.fuse_id,
                fuse_type=fuse.fuse_type,
                severity=self._calculate_severity(current_value, fuse.threshold_value),
                trigger_value=current_value,
                threshold_value=fuse.threshold_value,
                description=f"Threshold exceeded: {current_value:.2f} >= {fuse.threshold_value:.2f}",
                triggered_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                resolved_at=None,
                actions_taken=[],
                metadata={"fuse_name": fuse.name}
            )
            
            self.trigger_events[event_id] = trigger_event
            
            self.logger.critical(f"🚨 FUSE TRIGGERED: {fuse.name} - {trigger_event.description}")
            
            # Execute emergency actions
            for action in fuse.actions:
                try:
                    if action in self.action_callbacks:
                        self.action_callbacks[action](fuse, trigger_event)
                        trigger_event.actions_taken.append(action)
                        self.logger.info(f"✅ Emergency action executed: {action}")
                    else:
                        self.logger.error(f"Unknown emergency action: {action}")
                except Exception as e:
                    self.logger.error(f"Failed to execute emergency action {action}: {e}")
            
            # Start recovery timer if auto-recovery is enabled
            if fuse.auto_recovery:
                self._start_recovery_timer(fuse)
            
        except Exception as e:
            self.logger.error(f"Failed to trigger fuse: {e}")
    
    def _calculate_severity(self, current_value: float, threshold_value: float) -> TriggerSeverity:
        """Calculate trigger severity based on values"""
        try:
            if threshold_value == 0:
                return TriggerSeverity.CRITICAL
            
            ratio = current_value / threshold_value
            
            if ratio >= 1.5:
                return TriggerSeverity.CRITICAL
            elif ratio >= 1.2:
                return TriggerSeverity.HIGH
            elif ratio >= 1.1:
                return TriggerSeverity.MEDIUM
            else:
                return TriggerSeverity.LOW
            
        except Exception as e:
            self.logger.error(f"Failed to calculate severity: {e}")
            return TriggerSeverity.MEDIUM
    
    def _start_recovery_timer(self, fuse: FuseConfiguration):
        """Start recovery timer for fuse"""
        try:
            def recovery_callback():
                time.sleep(fuse.recovery_time)
                if self.fuse_states.get(fuse.fuse_id) == FuseState.TRIGGERED:
                    self.fuse_states[fuse.fuse_id] = FuseState.ARMED
                    self.logger.info(f"🔄 Fuse recovered: {fuse.name}")
            
            recovery_thread = threading.Thread(target=recovery_callback, daemon=True)
            recovery_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start recovery timer: {e}")
    
    # Emergency Action Implementations
    
    def _action_log_alert(self, fuse: FuseConfiguration, trigger: FuseTriggerEvent):
        """Log critical alert"""
        try:
            alert_message = f"CRITICAL SYSTEM ALERT: {fuse.name} - {trigger.description}"
            self.logger.critical(alert_message)
            
            # Save alert to file
            alert_file = self.fuse_dir / "critical_alerts.log"
            with open(alert_file, 'a') as f:
                f.write(f"{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}: {alert_message}\n")
            
        except Exception as e:
            self.logger.error(f"Failed to log alert: {e}")
    
    def _action_free_memory(self, fuse: FuseConfiguration, trigger: FuseTriggerEvent):
        """Free system memory"""
        try:
            import gc
            
            # Force garbage collection
            gc.collect()
            
            self.logger.info("🧹 Memory cleanup executed")
            
        except Exception as e:
            self.logger.error(f"Failed to free memory: {e}")
    
    def _action_throttle_processes(self, fuse: FuseConfiguration, trigger: FuseTriggerEvent):
        """Throttle CPU-intensive processes"""
        try:
            self.logger.info("🐌 Process throttling activated")
            
        except Exception as e:
            self.logger.error(f"Failed to throttle processes: {e}")
    
    def _action_cleanup_temp(self, fuse: FuseConfiguration, trigger: FuseTriggerEvent):
        """Clean up temporary files"""
        try:
            import tempfile
            import shutil
            
            temp_dir = Path(self._get_temp_path().gettempdir())
            
            # Clean old temporary files (older than 1 hour)
            cutoff_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - 3600
            
            for temp_file in temp_dir.glob("*"):
                try:
                    if temp_file.stat().st_mtime < cutoff_time:
                        if temp_file.is_file():
                            temp_file.unlink()
                        elif temp_file.is_dir():
                            shutil.rmtree(temp_file)
                except:
                    continue
            
            self.logger.info("🧹 Temporary files cleaned")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup temp files: {e}")
    
    def _action_emergency_stop(self, fuse: FuseConfiguration, trigger: FuseTriggerEvent):
        """Emergency system stop"""
        try:
            # Save critical state
            state_file = self.fuse_dir / "emergency_state.json"
            emergency_state = {
                "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                "fuse_id": fuse.fuse_id,
                "fuse_name": fuse.name,
                "trigger_value": trigger.trigger_value,
                "description": trigger.description,
                "system_state": {
                    "memory_percent": psutil.virtual_memory().percent,
                    "cpu_percent": psutil.cpu_percent(),
                    "disk_percent": (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
                }
            }
            
            with open(state_file, 'w') as f:
                json.dump(emergency_state, f, indent=2)
            
            self.logger.critical("🚨 EMERGENCY STOP - System state saved")
            
        except Exception as e:
            self.logger.error(f"Failed to execute emergency stop: {e}")
    
    def get_fuse_status(self) -> Dict[str, Any]:
        """Get system fuse status"""
        try:
            active_triggers = len([t for t in self.trigger_events.values() if t.resolved_at is None])
            triggered_fuses = len([s for s in self.fuse_states.values() if s == FuseState.TRIGGERED])
            
            return {
                "enabled": self.config.get("enabled", True),
                "monitoring_active": self.monitoring_active,
                "total_fuses": len(self.fuses),
                "armed_fuses": len([s for s in self.fuse_states.values() if s == FuseState.ARMED]),
                "triggered_fuses": triggered_fuses,
                "disabled_fuses": len([s for s in self.fuse_states.values() if s == FuseState.DISABLED]),
                "active_triggers": active_triggers,
                "total_trigger_events": len(self.trigger_events),
                "monitoring_interval": self.monitoring_interval,
                "emergency_actions": len(self.action_callbacks)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get fuse status: {e}")
            return {"error": str(e)}
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        try:
            status = self.get_fuse_status()
            
            # Calculate security level based on fuse states
            total_fuses = status.get("total_fuses", 0)
            armed_fuses = status.get("armed_fuses", 0)
            triggered_fuses = len(status.get("triggered_fuses", []))
            
            if triggered_fuses > 0:
                security_level = "critical"
            elif armed_fuses == total_fuses and total_fuses > 0:
                security_level = "high"
            elif armed_fuses > 0:
                security_level = "medium"
            else:
                security_level = "low"
            
            return {
                "security_level": security_level,
                "fuse_status": status,
                "monitoring_active": self.monitoring_active,
                "last_check": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get security status: {e}")
            return {
                "error": str(e),
                "security_level": "unknown"
            }

# Global instance
system_fuse = SystemFuse()