#!/usr/bin/env python3
"""
QPM - Quality & Performance Monitor
Neprekinjeno meri in zapisuje sistemske metrike
"""

import os
import json
import logging
import time
import psutil
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import deque
import statistics

@dataclass
class PerformanceMetric:

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Performance metric data point"""
    timestamp: float
    metric_name: str
    value: float
    unit: str
    source_module: str
    metadata: Dict[str, Any]

@dataclass
class QualityMetric:
    """Quality metric data point"""
    timestamp: float
    metric_name: str
    score: float
    max_score: float
    source_module: str
    details: Dict[str, Any]

class QPM:
    """Quality & Performance Monitor"""
    
    def __init__(self, config_path: str = "mia/data/quality_control/qpm_config.json"):
        self.config_path = config_path
        self.qpm_dir = Path("mia/data/quality_control/qpm")
        self.qpm_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.QPM")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Metrics storage
        self.performance_metrics: deque = deque(maxlen=self.config.get("max_metrics", 10000))
        self.quality_metrics: deque = deque(maxlen=self.config.get("max_metrics", 10000))
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_interval = self.config.get("monitoring_interval", 5.0)
        
        # Registered modules for monitoring
        self.registered_modules: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("📊 QPM (Quality & Performance Monitor) initialized")
    
    def _load_configuration(self) -> Dict:
        """Load QPM configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load QPM config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default QPM configuration"""
        config = {
            "enabled": True,
            "monitoring_interval": 5.0,
            "max_metrics": 10000,
            "auto_save_interval": 300,  # 5 minutes
            "performance_thresholds": {
                "cpu_usage_warning": 80.0,
                "cpu_usage_critical": 95.0,
                "memory_usage_warning": 85.0,
                "memory_usage_critical": 95.0,
                "response_time_warning": 2.0,
                "response_time_critical": 5.0
            },
            "quality_thresholds": {
                "accuracy_minimum": 0.8,
                "consistency_minimum": 0.9,
                "reliability_minimum": 0.95
            },
            "metrics_to_monitor": {
                "system_metrics": True,
                "process_metrics": True,
                "module_metrics": True,
                "quality_metrics": True,
                "custom_metrics": True
            },
            "anomaly_detection": {
                "enabled": True,
                "sensitivity": 0.8,
                "window_size": 100
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        try:
            if self.monitoring_active:
                self.logger.warning("Monitoring already active")
                return
            
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.logger.info("📊 QPM monitoring started")
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        try:
            self.monitoring_active = False
            
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5.0)
            
            self.logger.info("📊 QPM monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        last_save_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        save_interval = self.config.get("auto_save_interval", 300)
        
        while self.monitoring_active:
            try:
                # Collect system metrics
                if self.config.get("metrics_to_monitor", {}).get("system_metrics", True):
                    self._collect_system_metrics()
                
                # Collect process metrics
                if self.config.get("metrics_to_monitor", {}).get("process_metrics", True):
                    self._collect_process_metrics()
                
                # Collect module metrics
                if self.config.get("metrics_to_monitor", {}).get("module_metrics", True):
                    self._collect_module_metrics()
                
                # Check for anomalies
                if self.config.get("anomaly_detection", {}).get("enabled", True):
                    self._detect_anomalies()
                
                # Auto-save metrics
                current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                if current_time - last_save_time >= save_interval:
                    self._save_metrics()
                    last_save_time = current_time
                
                # Wait for next cycle
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            self.record_performance_metric(
                "cpu_usage",
                cpu_percent,
                "percent",
                "system",
                {"cores": psutil.cpu_count()}
            )
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.record_performance_metric(
                "memory_usage",
                memory.percent,
                "percent",
                "system",
                {"total_gb": memory.total / (1024**3), "available_gb": memory.available / (1024**3)}
            )
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            self.record_performance_metric(
                "disk_usage",
                (disk.used / disk.total) * 100,
                "percent",
                "system",
                {"total_gb": disk.total / (1024**3), "free_gb": disk.free / (1024**3)}
            )
            
            # Network metrics
            network = psutil.net_io_counters()
            self.record_performance_metric(
                "network_bytes_sent",
                network.bytes_sent,
                "bytes",
                "system",
                {"packets_sent": network.packets_sent}
            )
            
            self.record_performance_metric(
                "network_bytes_recv",
                network.bytes_recv,
                "bytes",
                "system",
                {"packets_recv": network.packets_recv}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
    
    def _collect_process_metrics(self):
        """Collect process-level metrics"""
        try:
            current_process = psutil.Process()
            
            # Process CPU usage
            cpu_percent = current_process.cpu_percent()
            self.record_performance_metric(
                "process_cpu_usage",
                cpu_percent,
                "percent",
                "process",
                {"pid": current_process.pid}
            )
            
            # Process memory usage
            memory_info = current_process.memory_info()
            self.record_performance_metric(
                "process_memory_rss",
                memory_info.rss / (1024**2),  # MB
                "MB",
                "process",
                {"vms_mb": memory_info.vms / (1024**2)}
            )
            
            # Process thread count
            num_threads = current_process.num_threads()
            self.record_performance_metric(
                "process_threads",
                num_threads,
                "count",
                "process",
                {}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect process metrics: {e}")
    
    def _collect_module_metrics(self):
        """Collect metrics from registered modules"""
        try:
            for module_name, module_info in self.registered_modules.items():
                try:
                    # Call module's metric collection function
                    if "metric_collector" in module_info:
                        metrics = module_info["metric_collector"]()
                        
                        if isinstance(metrics, dict):
                            for metric_name, metric_value in metrics.items():
                                if isinstance(metric_value, (int, float)):
                                    self.record_performance_metric(
                                        f"{module_name}_{metric_name}",
                                        metric_value,
                                        "unit",
                                        module_name,
                                        {}
                                    )
                
                except Exception as e:
                    self.logger.error(f"Failed to collect metrics from {module_name}: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to collect module metrics: {e}")
    
    def _detect_anomalies(self):
        """Detect anomalies in metrics"""
        try:
            if len(self.performance_metrics) < self.config.get("anomaly_detection", {}).get("window_size", 100):
                return
            
            # Simple anomaly detection based on standard deviation
            recent_metrics = {}
            window_size = self.config.get("anomaly_detection", {}).get("window_size", 100)
            
            # Group recent metrics by name
            for metric in list(self.performance_metrics)[-window_size:]:
                if metric.metric_name not in recent_metrics:
                    recent_metrics[metric.metric_name] = []
                recent_metrics[metric.metric_name].append(metric.value)
            
            # Check for anomalies
            for metric_name, values in recent_metrics.items():
                if len(values) >= 10:  # Need sufficient data
                    mean_val = statistics.mean(values)
                    stdev_val = statistics.stdev(values) if len(values) > 1 else 0
                    
                    latest_value = values[-1]
                    
                    # Check if latest value is anomalous
                    if stdev_val > 0:
                        z_score = abs(latest_value - mean_val) / stdev_val
                        sensitivity = self.config.get("anomaly_detection", {}).get("sensitivity", 0.8)
                        
                        if z_score > (3.0 * sensitivity):  # Anomaly threshold
                            self.logger.warning(f"🚨 Anomaly detected in {metric_name}: {latest_value} (z-score: {z_score:.2f})")
            
        except Exception as e:
            self.logger.error(f"Failed to detect anomalies: {e}")
    
    def record_performance_metric(self, metric_name: str, value: float, unit: str,
                                  source_module: str, metadata: Dict[str, Any] = None):
        """Record a performance metric"""
        try:
            metric = PerformanceMetric(
                timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                metric_name=metric_name,
                value=value,
                unit=unit,
                source_module=source_module,
                metadata=metadata or {}
            )
            
            self.performance_metrics.append(metric)
            
            # Check thresholds
            self._check_performance_thresholds(metric)
            
        except Exception as e:
            self.logger.error(f"Failed to record performance metric: {e}")
    
    def record_quality_metric(self, metric_name: str, score: float, max_score: float,
                              source_module: str, details: Dict[str, Any] = None):
        """Record a quality metric"""
        try:
            metric = QualityMetric(
                timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                metric_name=metric_name,
                score=score,
                max_score=max_score,
                source_module=source_module,
                details=details or {}
            )
            
            self.quality_metrics.append(metric)
            
            # Check quality thresholds
            self._check_quality_thresholds(metric)
            
        except Exception as e:
            self.logger.error(f"Failed to record quality metric: {e}")
    
    def _check_performance_thresholds(self, metric: PerformanceMetric):
        """Check performance thresholds"""
        try:
            thresholds = self.config.get("performance_thresholds", {})
            
            warning_key = f"{metric.metric_name}_warning"
            critical_key = f"{metric.metric_name}_critical"
            
            if critical_key in thresholds and metric.value >= thresholds[critical_key]:
                self.logger.critical(f"🚨 CRITICAL: {metric.metric_name} = {metric.value} {metric.unit}")
            elif warning_key in thresholds and metric.value >= thresholds[warning_key]:
                self.logger.warning(f"⚠️ WARNING: {metric.metric_name} = {metric.value} {metric.unit}")
            
        except Exception as e:
            self.logger.error(f"Failed to check performance thresholds: {e}")
    
    def _check_quality_thresholds(self, metric: QualityMetric):
        """Check quality thresholds"""
        try:
            thresholds = self.config.get("quality_thresholds", {})
            
            # Calculate normalized score
            normalized_score = metric.score / metric.max_score if metric.max_score > 0 else 0
            
            threshold_key = f"{metric.metric_name}_minimum"
            if threshold_key in thresholds and normalized_score < thresholds[threshold_key]:
                self.logger.warning(f"⚠️ QUALITY: {metric.metric_name} below threshold: {normalized_score:.2f}")
            
        except Exception as e:
            self.logger.error(f"Failed to check quality thresholds: {e}")
    
    def register_module(self, module_name: str, metric_collector: callable = None):
        """Register module for monitoring"""
        try:
            self.registered_modules[module_name] = {
                "registered_at": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                "metric_collector": metric_collector
            }
            
            self.logger.info(f"📊 Registered module for monitoring: {module_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to register module: {e}")
    
    def get_metrics_summary(self, time_window: float = 3600) -> Dict[str, Any]:
        """Get metrics summary for specified time window"""
        try:
            current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            cutoff_time = current_time - time_window
            
            # Filter recent metrics
            recent_performance = [m for m in self.performance_metrics if m.timestamp >= cutoff_time]
            recent_quality = [m for m in self.quality_metrics if m.timestamp >= cutoff_time]
            
            # Calculate summaries
            performance_summary = {}
            quality_summary = {}
            
            # Performance metrics summary
            for metric in recent_performance:
                if metric.metric_name not in performance_summary:
                    performance_summary[metric.metric_name] = {
                        "values": [],
                        "unit": metric.unit,
                        "source": metric.source_module
                    }
                performance_summary[metric.metric_name]["values"].append(metric.value)
            
            # Calculate statistics for performance metrics
            for metric_name, data in performance_summary.items():
                values = data["values"]
                if values:
                    data["count"] = len(values)
                    data["mean"] = statistics.mean(values)
                    data["min"] = min(values)
                    data["max"] = max(values)
                    data["latest"] = values[-1]
                    if len(values) > 1:
                        data["stdev"] = statistics.stdev(values)
                    else:
                        data["stdev"] = 0.0
                    del data["values"]  # Remove raw values to save space
            
            # Quality metrics summary
            for metric in recent_quality:
                if metric.metric_name not in quality_summary:
                    quality_summary[metric.metric_name] = {
                        "scores": [],
                        "max_scores": [],
                        "source": metric.source_module
                    }
                quality_summary[metric.metric_name]["scores"].append(metric.score)
                quality_summary[metric.metric_name]["max_scores"].append(metric.max_score)
            
            # Calculate statistics for quality metrics
            for metric_name, data in quality_summary.items():
                scores = data["scores"]
                max_scores = data["max_scores"]
                if scores and max_scores:
                    normalized_scores = [s/ms if ms > 0 else 0 for s, ms in zip(scores, max_scores)]
                    data["count"] = len(scores)
                    data["mean_score"] = statistics.mean(normalized_scores)
                    data["min_score"] = min(normalized_scores)
                    data["max_score"] = max(normalized_scores)
                    data["latest_score"] = normalized_scores[-1]
                    del data["scores"]  # Remove raw values
                    del data["max_scores"]
            
            return {
                "time_window_hours": time_window / 3600,
                "performance_metrics": performance_summary,
                "quality_metrics": quality_summary,
                "total_performance_points": len(recent_performance),
                "total_quality_points": len(recent_quality)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics summary: {e}")
            return {}
    
    def _save_metrics(self):
        """Save metrics to storage"""
        try:
            # Save performance metrics
            performance_file = self.qpm_dir / "performance_metrics.json"
            performance_data = [asdict(m) for m in self.performance_metrics]
            
            with open(performance_file, 'w') as f:
                json.dump(performance_data, f, indent=2)
            
            # Save quality metrics
            quality_file = self.qpm_dir / "quality_metrics.json"
            quality_data = [asdict(m) for m in self.quality_metrics]
            
            with open(quality_file, 'w') as f:
                json.dump(quality_data, f, indent=2)
            
            self.logger.debug("📊 Metrics saved to storage")
            
        except Exception as e:
            self.logger.error(f"Failed to save metrics: {e}")
    
    def get_qpm_status(self) -> Dict[str, Any]:
        """Get QPM status"""
        try:
            return {
                "enabled": self.config.get("enabled", True),
                "monitoring_active": self.monitoring_active,
                "monitoring_interval": self.monitoring_interval,
                "performance_metrics_count": len(self.performance_metrics),
                "quality_metrics_count": len(self.quality_metrics),
                "registered_modules": list(self.registered_modules.keys()),
                "anomaly_detection_enabled": self.config.get("anomaly_detection", {}).get("enabled", True)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get QPM status: {e}")
            return {"error": str(e)}
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get current quality metrics"""
        try:
            # Calculate overall quality score
            if self.quality_metrics:
                recent_metrics = list(self.quality_metrics.values())[-10:]  # Last 10 metrics
                avg_score = sum(m.get("score", 0) for m in recent_metrics) / len(recent_metrics)
            else:
                avg_score = 0.0
            
            # Calculate performance score
            if self.performance_metrics:
                recent_perf = list(self.performance_metrics.values())[-10:]
                avg_perf = sum(m.get("value", 0) for m in recent_perf) / len(recent_perf)
            else:
                avg_perf = 0.0
            
            return {
                "overall_quality_score": avg_score,
                "performance_score": avg_perf,
                "total_quality_metrics": len(self.quality_metrics),
                "total_performance_metrics": len(self.performance_metrics),
                "monitoring_active": self.monitoring_active,
                "registered_modules": list(self.registered_modules.keys()),
                "last_update": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get quality metrics: {e}")
            return {
                "error": str(e),
                "overall_quality_score": 0.0,
                "performance_score": 0.0
            }

# Global instance
qpm = QPM()