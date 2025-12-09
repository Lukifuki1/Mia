#!/usr/bin/env python3
"""
MIA Health Monitor
Real-time system health monitoring with checkpointing and recovery
"""

import os
import json
import logging
import time
import threading
import psutil
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import queue
import asyncio

class HealthStatus(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """System health status levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILURE = "failure"

class ComponentStatus(Enum):
    """Individual component status"""
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    ERROR = "error"

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_usage_percent: float
    disk_free_gb: float
    gpu_memory_percent: float
    gpu_temperature: Optional[float]
    network_bytes_sent: int
    network_bytes_recv: int
    process_count: int
    thread_count: int
    load_average: List[float]

@dataclass
class ComponentHealth:
    """Component health information"""
    name: str
    status: ComponentStatus
    last_check: float
    response_time: float
    error_count: int
    uptime: float
    memory_usage_mb: float
    cpu_usage_percent: float
    custom_metrics: Dict[str, Any]

@dataclass
class HealthAlert:
    """Health alert information"""
    timestamp: float
    severity: HealthStatus
    component: str
    message: str
    metrics: Dict[str, Any]
    resolved: bool = False
    resolution_time: Optional[float] = None

@dataclass
class SystemCheckpoint:
    """System state checkpoint"""
    timestamp: float
    checkpoint_id: str
    system_metrics: SystemMetrics
    component_states: Dict[str, Dict[str, Any]]
    active_processes: List[str]
    memory_snapshot: bytes
    config_snapshot: Dict[str, Any]

class HealthMonitor:
    """Real-time system health monitoring"""
    
    def __init__(self, config_path: str = "mia/data/monitoring/config.json"):
        self.config_path = config_path
        self.monitoring_dir = Path("mia/data/monitoring")
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        self.checkpoints_dir = self.monitoring_dir / "checkpoints"
        self.checkpoints_dir.mkdir(exist_ok=True)
        
        self.logs_dir = self.monitoring_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger("MIA.HealthMonitor")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_thread = None
        self.checkpoint_thread = None
        
        # System metrics
        self.current_metrics: Optional[SystemMetrics] = None
        self.metrics_history: List[SystemMetrics] = []
        self.max_history_size = self.config.get("max_history_size", 1000)
        
        # Component health
        self.components: Dict[str, ComponentHealth] = {}
        self.component_callbacks: Dict[str, Callable] = {}
        
        # Alerts
        self.active_alerts: List[HealthAlert] = []
        self.alert_callbacks: List[Callable] = []
        
        # Checkpoints
        self.checkpoints: List[SystemCheckpoint] = []
        self.max_checkpoints = self.config.get("max_checkpoints", 50)
        
        # Performance baselines
        self.performance_baselines = self._load_performance_baselines()
        
        # Initialize components
        self._initialize_system_components()
        
        self.logger.info("💊 Health Monitor initialized")
    
    def _load_configuration(self) -> Dict:
        """Load health monitor configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load monitoring config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default monitoring configuration"""
        config = {
            "enabled": True,
            "monitoring_interval": 5.0,  # seconds
            "checkpoint_interval": 300.0,  # 5 minutes
            "max_history_size": 1000,
            "max_checkpoints": 50,
            "thresholds": {
                "cpu_warning": 80.0,
                "cpu_critical": 95.0,
                "memory_warning": 85.0,
                "memory_critical": 95.0,
                "disk_warning": 90.0,
                "disk_critical": 95.0,
                "gpu_memory_warning": 90.0,
                "gpu_memory_critical": 95.0,
                "response_time_warning": 5.0,
                "response_time_critical": 10.0
            },
            "alerts": {
                "enabled": True,
                "email_notifications": False,
                "log_alerts": True,
                "auto_resolve": True,
                "resolution_timeout": 300.0
            },
            "recovery": {
                "auto_recovery": True,
                "max_recovery_attempts": 3,
                "recovery_delay": 30.0,
                "safe_mode_threshold": "critical"
            },
            "components": {
                "consciousness": {"enabled": True, "timeout": 10.0},
                "memory": {"enabled": True, "timeout": 5.0},
                "voice": {"enabled": True, "timeout": 15.0},
                "project_builder": {"enabled": True, "timeout": 30.0},
                "lora_manager": {"enabled": True, "timeout": 20.0},
                "email_client": {"enabled": True, "timeout": 10.0}
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _load_performance_baselines(self) -> Dict[str, float]:
        """Load performance baselines"""
        try:
            baselines_file = self.monitoring_dir / "baselines.json"
            
            if baselines_file.exists():
                with open(baselines_file, 'r') as f:
                    return json.load(f)
            else:
                # Create default baselines
                return {
                    "cpu_baseline": 20.0,
                    "memory_baseline": 50.0,
                    "response_time_baseline": 1.0,
                    "disk_io_baseline": 100.0
                }
                
        except Exception as e:
            self.logger.error(f"Failed to load performance baselines: {e}")
            return {}
    
    def _save_performance_baselines(self):
        """Save performance baselines"""
        try:
            baselines_file = self.monitoring_dir / "baselines.json"
            
            with open(baselines_file, 'w') as f:
                json.dump(self.performance_baselines, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save performance baselines: {e}")
    
    def _initialize_system_components(self):
        """Initialize system components for monitoring"""
        try:
            components_config = self.config.get("components", {})
            
            for component_name, component_config in components_config.items():
                if component_config.get("enabled", True):
                    self.components[component_name] = ComponentHealth(
                        name=component_name,
                        status=ComponentStatus.OFFLINE,
                        last_check=0.0,
                        response_time=0.0,
                        error_count=0,
                        uptime=0.0,
                        memory_usage_mb=0.0,
                        cpu_usage_percent=0.0,
                        custom_metrics={}
                    )
            
            self.logger.info(f"✅ Initialized {len(self.components)} components for monitoring")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
    
    def start_monitoring(self) -> bool:
        """Start health monitoring"""
        try:
            if self.is_monitoring:
                self.logger.warning("Health monitoring already active")
                return True
            
            if not self.config.get("enabled", True):
                self.logger.info("Health monitoring is disabled")
                return False
            
            self.is_monitoring = True
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            # Start checkpoint thread
            self.checkpoint_thread = threading.Thread(
                target=self._checkpoint_loop,
                daemon=True
            )
            self.checkpoint_thread.start()
            
            self.logger.info("💊 Started health monitoring")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start health monitoring: {e}")
            return False
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.is_monitoring = False
        self.logger.info("💊 Stopped health monitoring")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        monitoring_interval = self.config.get("monitoring_interval", 5.0)
        
        while self.is_monitoring:
            try:
                start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                
                # Collect system metrics
                metrics = self._collect_system_metrics()
                
                if metrics:
                    self.current_metrics = metrics
                    self.metrics_history.append(metrics)
                    
                    # Trim history
                    if len(self.metrics_history) > self.max_history_size:
                        self.metrics_history = self.metrics_history[-self.max_history_size:]
                    
                    # Check system health
                    self._check_system_health(metrics)
                
                # Check component health
                self._check_component_health()
                
                # Process alerts
                self._process_alerts()
                
                # Update performance baselines
                self._update_performance_baselines()
                
                # Calculate sleep time
                elapsed = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
                sleep_time = max(0, monitoring_interval - elapsed)
                
                time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(monitoring_interval)
    
    def _collect_system_metrics(self) -> Optional[SystemMetrics]:
        """Collect system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024**3)
            
            # GPU metrics (if available)
            gpu_memory_percent = 0.0
            gpu_temperature = None
            
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    gpu_memory_percent = (gpu.memoryUsed / gpu.memoryTotal) * 100
                    gpu_temperature = gpu.temperature
            except ImportError:
                pass
            
            # Network metrics
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv
            
            # Process metrics
            process_count = len(psutil.pids())
            
            # Thread count
            thread_count = 0
            for proc in psutil.process_iter(['num_threads']):
                try:
                    thread_count += proc.info['num_threads'] or 0
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Load average
            try:
                load_average = list(os.getloadavg())
            except (OSError, AttributeError):
                load_average = [0.0, 0.0, 0.0]
            
            return SystemMetrics(
                timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_gb=memory_available_gb,
                disk_usage_percent=disk_usage_percent,
                disk_free_gb=disk_free_gb,
                gpu_memory_percent=gpu_memory_percent,
                gpu_temperature=gpu_temperature,
                network_bytes_sent=network_bytes_sent,
                network_bytes_recv=network_bytes_recv,
                process_count=process_count,
                thread_count=thread_count,
                load_average=load_average
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            return None
    
    def _check_system_health(self, metrics: SystemMetrics):
        """Check system health against thresholds"""
        try:
            thresholds = self.config.get("thresholds", {})
            
            # Check CPU
            if metrics.cpu_percent >= thresholds.get("cpu_critical", 95):
                self._create_alert(HealthStatus.CRITICAL, "system", 
                                f"CPU usage critical: {metrics.cpu_percent:.1f}%",
                                {"cpu_percent": metrics.cpu_percent})
            elif metrics.cpu_percent >= thresholds.get("cpu_warning", 80):
                self._create_alert(HealthStatus.WARNING, "system",
                                f"CPU usage high: {metrics.cpu_percent:.1f}%",
                                {"cpu_percent": metrics.cpu_percent})
            
            # Check Memory
            if metrics.memory_percent >= thresholds.get("memory_critical", 95):
                self._create_alert(HealthStatus.CRITICAL, "system",
                                f"Memory usage critical: {metrics.memory_percent:.1f}%",
                                {"memory_percent": metrics.memory_percent})
            elif metrics.memory_percent >= thresholds.get("memory_warning", 85):
                self._create_alert(HealthStatus.WARNING, "system",
                                f"Memory usage high: {metrics.memory_percent:.1f}%",
                                {"memory_percent": metrics.memory_percent})
            
            # Check Disk
            if metrics.disk_usage_percent >= thresholds.get("disk_critical", 95):
                self._create_alert(HealthStatus.CRITICAL, "system",
                                f"Disk usage critical: {metrics.disk_usage_percent:.1f}%",
                                {"disk_usage_percent": metrics.disk_usage_percent})
            elif metrics.disk_usage_percent >= thresholds.get("disk_warning", 90):
                self._create_alert(HealthStatus.WARNING, "system",
                                f"Disk usage high: {metrics.disk_usage_percent:.1f}%",
                                {"disk_usage_percent": metrics.disk_usage_percent})
            
            # Check GPU Memory
            if metrics.gpu_memory_percent >= thresholds.get("gpu_memory_critical", 95):
                self._create_alert(HealthStatus.CRITICAL, "system",
                                f"GPU memory critical: {metrics.gpu_memory_percent:.1f}%",
                                {"gpu_memory_percent": metrics.gpu_memory_percent})
            elif metrics.gpu_memory_percent >= thresholds.get("gpu_memory_warning", 90):
                self._create_alert(HealthStatus.WARNING, "system",
                                f"GPU memory high: {metrics.gpu_memory_percent:.1f}%",
                                {"gpu_memory_percent": metrics.gpu_memory_percent})
            
        except Exception as e:
            self.logger.error(f"Failed to check system health: {e}")
    
    def _check_component_health(self):
        """Check health of individual components"""
        try:
            for component_name, component in self.components.items():
                try:
                    # Get component health check callback
                    if component_name in self.component_callbacks:
                        callback = self.component_callbacks[component_name]
                        
                        start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                        health_data = callback()
                        response_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
                        
                        # Update component health
                        component.last_check = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                        component.response_time = response_time
                        
                        if health_data:
                            component.status = ComponentStatus(health_data.get("status", "online"))
                            component.memory_usage_mb = health_data.get("memory_usage_mb", 0.0)
                            component.cpu_usage_percent = health_data.get("cpu_usage_percent", 0.0)
                            component.custom_metrics = health_data.get("custom_metrics", {})
                            
                            # Reset error count on successful check
                            if component.status == ComponentStatus.ONLINE:
                                component.error_count = 0
                        
                        # Check response time
                        thresholds = self.config.get("thresholds", {})
                        if response_time >= thresholds.get("response_time_critical", 10.0):
                            self._create_alert(HealthStatus.CRITICAL, component_name,
                                            f"Component response time critical: {response_time:.2f}s",
                                            {"response_time": response_time})
                        elif response_time >= thresholds.get("response_time_warning", 5.0):
                            self._create_alert(HealthStatus.WARNING, component_name,
                                            f"Component response time high: {response_time:.2f}s",
                                            {"response_time": response_time})
                    
                    else:
                        # No callback - try basic health check
                        component.status = ComponentStatus.ONLINE
                        component.last_check = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                
                except Exception as e:
                    component.error_count += 1
                    component.status = ComponentStatus.ERROR
                    
                    self._create_alert(HealthStatus.WARNING, component_name,
                                    f"Component health check failed: {str(e)}",
                                    {"error_count": component.error_count})
            
        except Exception as e:
            self.logger.error(f"Failed to check component health: {e}")
    
    def _create_alert(self, severity: HealthStatus, component: str, 
                     message: str, metrics: Dict[str, Any]):
        """Create health alert"""
        try:
            # Check if similar alert already exists
            for alert in self.active_alerts:
                if (alert.component == component and 
                    alert.message == message and 
                    not alert.resolved):
                    return  # Don't create duplicate alert
            
            alert = HealthAlert(
                timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                severity=severity,
                component=component,
                message=message,
                metrics=metrics
            )
            
            self.active_alerts.append(alert)
            
            # Log alert
            if self.config.get("alerts", {}).get("log_alerts", True):
                self.logger.warning(f"🚨 {severity.value.upper()} Alert - {component}: {message}")
            
            # Notify callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"Alert callback error: {e}")
            
            # Auto-recovery if enabled
            if (self.config.get("recovery", {}).get("auto_recovery", True) and
                severity in [HealthStatus.CRITICAL, HealthStatus.FAILURE]):
                self._attempt_auto_recovery(component, alert)
            
        except Exception as e:
            self.logger.error(f"Failed to create alert: {e}")
    
    def _process_alerts(self):
        """Process and resolve alerts"""
        try:
            if not self.config.get("alerts", {}).get("auto_resolve", True):
                return
            
            resolution_timeout = self.config.get("alerts", {}).get("resolution_timeout", 300.0)
            current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            for alert in self.active_alerts:
                if not alert.resolved:
                    # Check if alert should be auto-resolved
                    if current_time - alert.timestamp > resolution_timeout:
                        # Check if condition still exists
                        if not self._check_alert_condition(alert):
                            alert.resolved = True
                            alert.resolution_time = current_time
                            
                            self.logger.info(f"✅ Auto-resolved alert: {alert.component} - {alert.message}")
            
            # Clean up old resolved alerts
            self.active_alerts = [
                alert for alert in self.active_alerts
                if not alert.resolved or (current_time - alert.resolution_time < 3600)
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to process alerts: {e}")
    
    def _check_alert_condition(self, alert: HealthAlert) -> bool:
        """Check if alert condition still exists"""
        try:
            if not self.current_metrics:
                return False
            
            thresholds = self.config.get("thresholds", {})
            
            # Check system alerts
            if alert.component == "system":
                if "cpu_percent" in alert.metrics:
                    return self.current_metrics.cpu_percent >= thresholds.get("cpu_warning", 80)
                elif "memory_percent" in alert.metrics:
                    return self.current_metrics.memory_percent >= thresholds.get("memory_warning", 85)
                elif "disk_usage_percent" in alert.metrics:
                    return self.current_metrics.disk_usage_percent >= thresholds.get("disk_warning", 90)
            
            # Check component alerts
            elif alert.component in self.components:
                component = self.components[alert.component]
                if "response_time" in alert.metrics:
                    return component.response_time >= thresholds.get("response_time_warning", 5.0)
                elif component.status in [ComponentStatus.ERROR, ComponentStatus.OFFLINE]:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check alert condition: {e}")
            return False
    
    def _attempt_auto_recovery(self, component: str, alert: HealthAlert):
        """Attempt automatic recovery"""
        try:
            recovery_config = self.config.get("recovery", {})
            max_attempts = recovery_config.get("max_recovery_attempts", 3)
            recovery_delay = recovery_config.get("recovery_delay", 30.0)
            
            self.logger.info(f"🔄 Attempting auto-recovery for {component}")
            
            # Component-specific recovery actions
            if component == "system":
                self._recover_system_resources()
            elif component in self.components:
                self._recover_component(component)
            
            # Wait before checking recovery
            time.sleep(recovery_delay)
            
            # Check if recovery was successful
            if not self._check_alert_condition(alert):
                alert.resolved = True
                alert.resolution_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                self.logger.info(f"✅ Auto-recovery successful for {component}")
            else:
                self.logger.warning(f"❌ Auto-recovery failed for {component}")
            
        except Exception as e:
            self.logger.error(f"Auto-recovery failed: {e}")
    
    def _recover_system_resources(self):
        """Recover system resources"""
        try:
            # Force garbage collection
            import gc
            gc.collect()
            
            # Clear caches if possible
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass
            
            self.logger.info("🧹 System resource recovery attempted")
            
        except Exception as e:
            self.logger.error(f"System resource recovery failed: {e}")
    
    def _recover_component(self, component_name: str):
        """Recover specific component"""
        try:
            # Try to restart component if possible
            if component_name in self.component_callbacks:
                # This would depend on component-specific recovery methods
                self.logger.info(f"🔄 Component recovery attempted: {component_name}")
            
        except Exception as e:
            self.logger.error(f"Component recovery failed: {e}")
    
    def _update_performance_baselines(self):
        """Update performance baselines based on recent metrics"""
        try:
            if len(self.metrics_history) < 100:  # Need enough data
                return
            
            # Calculate rolling averages for last 100 measurements
            recent_metrics = self.metrics_history[-100:]
            
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            
            # Update baselines with exponential smoothing
            alpha = 0.1  # Smoothing factor
            
            self.performance_baselines["cpu_baseline"] = (
                alpha * avg_cpu + (1 - alpha) * self.performance_baselines.get("cpu_baseline", avg_cpu)
            )
            
            self.performance_baselines["memory_baseline"] = (
                alpha * avg_memory + (1 - alpha) * self.performance_baselines.get("memory_baseline", avg_memory)
            )
            
            # Save baselines periodically
            if len(self.metrics_history) % 500 == 0:
                self._save_performance_baselines()
            
        except Exception as e:
            self.logger.error(f"Failed to update performance baselines: {e}")
    
    def _checkpoint_loop(self):
        """Checkpoint creation loop"""
        checkpoint_interval = self.config.get("checkpoint_interval", 300.0)
        
        while self.is_monitoring:
            try:
                time.sleep(checkpoint_interval)
                
                if self.is_monitoring:
                    self._create_checkpoint()
                
            except Exception as e:
                self.logger.error(f"Checkpoint loop error: {e}")
                time.sleep(60)
    
    def _create_checkpoint(self) -> Optional[str]:
        """Create system checkpoint"""
        try:
            if not self.current_metrics:
                return None
            
            checkpoint_id = f"checkpoint_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}"
            
            # Collect component states
            component_states = {}
            for name, component in self.components.items():
                component_states[name] = {
                    "status": component.status.value,
                    "last_check": component.last_check,
                    "response_time": component.response_time,
                    "error_count": component.error_count,
                    "memory_usage_mb": component.memory_usage_mb,
                    "cpu_usage_percent": component.cpu_usage_percent,
                    "custom_metrics": component.custom_metrics
                }
            
            # Get active processes
            active_processes = []
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    if 'mia' in proc.info['name'].lower():
                        active_processes.append(f"{proc.info['name']}:{proc.info['pid']}")
            except:
                pass
            
            # Create memory snapshot (simplified)
            memory_snapshot = pickle.dumps({
                "metrics_history_size": len(self.metrics_history),
                "active_alerts_count": len([a for a in self.active_alerts if not a.resolved]),
                "performance_baselines": self.performance_baselines
            })
            
            # Create checkpoint
            checkpoint = SystemCheckpoint(
                timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                checkpoint_id=checkpoint_id,
                system_metrics=self.current_metrics,
                component_states=component_states,
                active_processes=active_processes,
                memory_snapshot=memory_snapshot,
                config_snapshot=self.config.copy()
            )
            
            # Save checkpoint
            checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
            
            checkpoint_data = asdict(checkpoint)
            checkpoint_data["system_metrics"] = asdict(checkpoint.system_metrics)
            checkpoint_data["memory_snapshot"] = checkpoint_data["memory_snapshot"].hex()
            
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            # Add to checkpoints list
            self.checkpoints.append(checkpoint)
            
            # Trim checkpoints
            if len(self.checkpoints) > self.max_checkpoints:
                old_checkpoint = self.checkpoints.pop(0)
                old_file = self.checkpoints_dir / f"{old_checkpoint.checkpoint_id}.json"
                if old_file.exists():
                    old_file.unlink()
            
            self.logger.debug(f"📸 Created checkpoint: {checkpoint_id}")
            return checkpoint_id
            
        except Exception as e:
            self.logger.error(f"Failed to create checkpoint: {e}")
            return None
    
    def restore_from_checkpoint(self, checkpoint_id: str) -> bool:
        """Restore system from checkpoint"""
        try:
            checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
            
            if not checkpoint_file.exists():
                self.logger.error(f"Checkpoint not found: {checkpoint_id}")
                return False
            
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            # Restore performance baselines
            if "config_snapshot" in checkpoint_data:
                config_snapshot = checkpoint_data["config_snapshot"]
                # Selectively restore configuration
                self.config.update(config_snapshot)
            
            # Restore memory snapshot
            if "memory_snapshot" in checkpoint_data:
                memory_snapshot_hex = checkpoint_data["memory_snapshot"]
                memory_snapshot = bytes.fromhex(memory_snapshot_hex)
                snapshot_data = pickle.loads(memory_snapshot)
                
                self.performance_baselines = snapshot_data.get("performance_baselines", {})
            
            self.logger.info(f"✅ Restored from checkpoint: {checkpoint_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore from checkpoint: {e}")
            return False
    
    def register_component(self, name: str, health_callback: Callable) -> bool:
        """Register component for health monitoring"""
        try:
            self.component_callbacks[name] = health_callback
            
            if name not in self.components:
                self.components[name] = ComponentHealth(
                    name=name,
                    status=ComponentStatus.OFFLINE,
                    last_check=0.0,
                    response_time=0.0,
                    error_count=0,
                    uptime=0.0,
                    memory_usage_mb=0.0,
                    cpu_usage_percent=0.0,
                    custom_metrics={}
                )
            
            self.logger.info(f"📝 Registered component: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register component: {e}")
            return False
    
    def unregister_component(self, name: str) -> bool:
        """Unregister component from monitoring"""
        try:
            if name in self.component_callbacks:
                del self.component_callbacks[name]
            
            if name in self.components:
                del self.components[name]
            
            self.logger.info(f"🗑️ Unregistered component: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unregister component: {e}")
            return False
    
    def add_alert_callback(self, callback: Callable):
        """Add alert notification callback"""
        self.alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback: Callable):
        """Remove alert notification callback"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status"""
        try:
            if not self.current_metrics:
                return {"status": "unknown", "message": "No metrics available"}
            
            # Determine overall health status
            active_critical = len([a for a in self.active_alerts 
                                 if not a.resolved and a.severity == HealthStatus.CRITICAL])
            active_warnings = len([a for a in self.active_alerts 
                                 if not a.resolved and a.severity == HealthStatus.WARNING])
            
            if active_critical > 0:
                overall_status = HealthStatus.CRITICAL
            elif active_warnings > 2:
                overall_status = HealthStatus.WARNING
            elif self.current_metrics.cpu_percent > 70 or self.current_metrics.memory_percent > 80:
                overall_status = HealthStatus.WARNING
            else:
                overall_status = HealthStatus.GOOD
            
            return {
                "status": overall_status.value,
                "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                "system_metrics": asdict(self.current_metrics),
                "component_health": {
                    name: {
                        "status": comp.status.value,
                        "response_time": comp.response_time,
                        "error_count": comp.error_count,
                        "uptime": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - comp.last_check if comp.last_check > 0 else 0
                    }
                    for name, comp in self.components.items()
                },
                "active_alerts": len([a for a in self.active_alerts if not a.resolved]),
                "critical_alerts": active_critical,
                "warning_alerts": active_warnings,
                "checkpoints_available": len(self.checkpoints),
                "last_checkpoint": self.checkpoints[-1].checkpoint_id if self.checkpoints else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system health: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_metrics_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get metrics history for specified hours"""
        try:
            cutoff_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - (hours * 3600)
            
            recent_metrics = [
                asdict(metrics) for metrics in self.metrics_history
                if metrics.timestamp > cutoff_time
            ]
            
            return recent_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics history: {e}")
            return []
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts"""
        try:
            return [
                {
                    "timestamp": alert.timestamp,
                    "severity": alert.severity.value,
                    "component": alert.component,
                    "message": alert.message,
                    "metrics": alert.metrics,
                    "resolved": alert.resolved,
                    "resolution_time": alert.resolution_time
                }
                for alert in self.active_alerts
                if not alert.resolved
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get active alerts: {e}")
            return []
    
    def get_checkpoints(self) -> List[Dict[str, Any]]:
        """Get available checkpoints"""
        try:
            return [
                {
                    "checkpoint_id": cp.checkpoint_id,
                    "timestamp": cp.timestamp,
                    "system_metrics": asdict(cp.system_metrics),
                    "component_count": len(cp.component_states),
                    "process_count": len(cp.active_processes)
                }
                for cp in self.checkpoints
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get checkpoints: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get health monitor status"""
        return {
            "enabled": self.config.get("enabled", True),
            "is_monitoring": self.is_monitoring,
            "monitoring_interval": self.config.get("monitoring_interval", 5.0),
            "checkpoint_interval": self.config.get("checkpoint_interval", 300.0),
            "components_monitored": len(self.components),
            "metrics_history_size": len(self.metrics_history),
            "active_alerts": len([a for a in self.active_alerts if not a.resolved]),
            "checkpoints_available": len(self.checkpoints),
            "auto_recovery_enabled": self.config.get("recovery", {}).get("auto_recovery", True)
        }

# Global instance
health_monitor = HealthMonitor()