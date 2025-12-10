#!/usr/bin/env python3
"""
MIA Enterprise Monitoring System
Advanced logging, monitoring, and analytics for enterprise deployment
"""

import os
import json
import logging
import asyncio
import time
import psutil
import threading
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import datetime

class MetricType(Enum):
    """Types of metrics"""
    PERFORMANCE = "performance"
    USAGE = "usage"
    ERROR = "error"
    SECURITY = "security"
    BUSINESS = "business"

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Metric:
    """System metric"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: float
    tags: Dict[str, str] = None
    metadata: Dict[str, Any] = None

@dataclass
class Alert:
    """System alert"""
    id: str
    level: AlertLevel
    message: str
    source: str
    timestamp: float
    resolved: bool = False
    resolved_at: Optional[float] = None
    metadata: Dict[str, Any] = None

class EnterpriseMonitoring:
    """Enterprise monitoring and logging system"""
    
    def __init__(self, data_dir: str = "mia_data"):
        self.data_dir = Path(data_dir)
        self.monitoring_dir = self.data_dir / "monitoring"
        self.logs_dir = self.monitoring_dir / "logs"
        self.metrics_dir = self.monitoring_dir / "metrics"
        self.alerts_dir = self.monitoring_dir / "alerts"
        
        # Create directories
        for dir_path in [self.monitoring_dir, self.logs_dir, self.metrics_dir, self.alerts_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_enterprise_logging()
        
        # Monitoring state
        self.metrics: deque = deque(maxlen=10000)  # Last 10k metrics
        self.alerts: List[Alert] = []
        self.system_stats = {}
        self.performance_stats = {}
        
        # Monitoring configuration
        self.config = {
            "metrics_retention_hours": 24,
            "alerts_retention_days": 7,
            "performance_monitoring": True,
            "security_monitoring": True,
            "auto_cleanup": True,
            "alert_thresholds": {
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "disk_usage": 90.0,
                "response_time": 5.0,
                "error_rate": 0.05
            }
        }
        
        # Start monitoring tasks
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("🔍 Enterprise monitoring system initialized")
    
    def _setup_enterprise_logging(self) -> logging.Logger:
        """Setup enterprise-grade logging"""
        logger = logging.getLogger("MIA.Enterprise.Monitoring")
        
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            # File handler
            log_file = self.logs_dir / f"mia_enterprise_{datetime.date.today().isoformat()}.log"
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
            logger.setLevel(logging.INFO)
        
        return logger
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Check alert conditions
                self._check_alert_conditions()
                
                # Cleanup old data
                if self.config["auto_cleanup"]:
                    self._cleanup_old_data()
                
                # Wait before next collection
                time.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                self.logger.error(f"❌ Monitoring loop error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            current_time = time.time()
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self._add_metric("system.cpu.usage", cpu_percent, MetricType.PERFORMANCE, 
                           tags={"unit": "percent"})
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self._add_metric("system.memory.usage", memory.percent, MetricType.PERFORMANCE,
                           tags={"unit": "percent"})
            self._add_metric("system.memory.available", memory.available / (1024**3), MetricType.PERFORMANCE,
                           tags={"unit": "GB"})
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self._add_metric("system.disk.usage", disk_percent, MetricType.PERFORMANCE,
                           tags={"unit": "percent"})
            
            # Network metrics (if available)
            try:
                network = psutil.net_io_counters()
                self._add_metric("system.network.bytes_sent", network.bytes_sent, MetricType.PERFORMANCE,
                               tags={"unit": "bytes"})
                self._add_metric("system.network.bytes_recv", network.bytes_recv, MetricType.PERFORMANCE,
                               tags={"unit": "bytes"})
            except:
                pass  # Network stats might not be available
            
            # Update system stats
            self.system_stats = {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_usage": disk_percent,
                "timestamp": current_time
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to collect system metrics: {e}")
    
    def _add_metric(self, name: str, value: float, metric_type: MetricType, 
                   tags: Dict[str, str] = None, metadata: Dict[str, Any] = None):
        """Add a metric to the collection"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=time.time(),
            tags=tags or {},
            metadata=metadata or {}
        )
        
        self.metrics.append(metric)
    
    def _check_alert_conditions(self):
        """Check for alert conditions"""
        try:
            current_time = time.time()
            thresholds = self.config["alert_thresholds"]
            
            # Check CPU usage
            if self.system_stats.get("cpu_usage", 0) > thresholds["cpu_usage"]:
                self._create_alert(
                    AlertLevel.WARNING,
                    f"High CPU usage: {self.system_stats['cpu_usage']:.1f}%",
                    "system_monitor",
                    {"metric": "cpu_usage", "value": self.system_stats["cpu_usage"]}
                )
            
            # Check memory usage
            if self.system_stats.get("memory_usage", 0) > thresholds["memory_usage"]:
                self._create_alert(
                    AlertLevel.WARNING,
                    f"High memory usage: {self.system_stats['memory_usage']:.1f}%",
                    "system_monitor",
                    {"metric": "memory_usage", "value": self.system_stats["memory_usage"]}
                )
            
            # Check disk usage
            if self.system_stats.get("disk_usage", 0) > thresholds["disk_usage"]:
                self._create_alert(
                    AlertLevel.ERROR,
                    f"High disk usage: {self.system_stats['disk_usage']:.1f}%",
                    "system_monitor",
                    {"metric": "disk_usage", "value": self.system_stats["disk_usage"]}
                )
                
        except Exception as e:
            self.logger.error(f"❌ Failed to check alert conditions: {e}")
    
    def _create_alert(self, level: AlertLevel, message: str, source: str, metadata: Dict[str, Any] = None):
        """Create a new alert"""
        alert_id = f"alert_{int(time.time() * 1000)}"
        
        alert = Alert(
            id=alert_id,
            level=level,
            message=message,
            source=source,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        
        self.alerts.append(alert)
        
        # Log alert
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL
        }[level]
        
        self.logger.log(log_level, f"🚨 ALERT [{level.value.upper()}] {message}")
    
    def _cleanup_old_data(self):
        """Cleanup old monitoring data"""
        try:
            current_time = time.time()
            
            # Cleanup old metrics (older than retention period)
            retention_seconds = self.config["metrics_retention_hours"] * 3600
            cutoff_time = current_time - retention_seconds
            
            # Filter metrics (deque doesn't support direct filtering, so we recreate)
            old_metrics = list(self.metrics)
            self.metrics.clear()
            for metric in old_metrics:
                if metric.timestamp > cutoff_time:
                    self.metrics.append(metric)
            
            # Cleanup old alerts
            alert_retention_seconds = self.config["alerts_retention_days"] * 24 * 3600
            alert_cutoff_time = current_time - alert_retention_seconds
            
            self.alerts = [alert for alert in self.alerts if alert.timestamp > alert_cutoff_time]
            
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup old data: {e}")
    
    def log_business_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Log a business metric"""
        self._add_metric(name, value, MetricType.BUSINESS, tags)
        self.logger.info(f"📊 Business metric: {name} = {value}")
    
    def log_performance_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Log a performance metric"""
        self._add_metric(name, value, MetricType.PERFORMANCE, tags)
    
    def log_security_event(self, event: str, severity: str = "info", metadata: Dict[str, Any] = None):
        """Log a security event"""
        self._add_metric(f"security.{event}", 1.0, MetricType.SECURITY, 
                        tags={"severity": severity}, metadata=metadata)
        
        if severity in ["warning", "error", "critical"]:
            alert_level = {
                "warning": AlertLevel.WARNING,
                "error": AlertLevel.ERROR,
                "critical": AlertLevel.CRITICAL
            }[severity]
            
            self._create_alert(alert_level, f"Security event: {event}", "security_monitor", metadata)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "system_stats": self.system_stats,
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "total_metrics": len(self.metrics),
            "monitoring_active": self.monitoring_active,
            "uptime_hours": (time.time() - self.monitoring_thread.ident) / 3600 if hasattr(self.monitoring_thread, 'ident') else 0
        }
    
    def get_metrics(self, metric_name: str = None, hours: int = 1) -> List[Dict[str, Any]]:
        """Get metrics for the specified time period"""
        cutoff_time = time.time() - (hours * 3600)
        
        filtered_metrics = []
        for metric in self.metrics:
            if metric.timestamp > cutoff_time:
                if metric_name is None or metric.name == metric_name:
                    filtered_metrics.append(asdict(metric))
        
        return filtered_metrics
    
    def get_alerts(self, resolved: bool = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alerts for the specified time period"""
        cutoff_time = time.time() - (hours * 3600)
        
        filtered_alerts = []
        for alert in self.alerts:
            if alert.timestamp > cutoff_time:
                if resolved is None or alert.resolved == resolved:
                    filtered_alerts.append(asdict(alert))
        
        return filtered_alerts
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = time.time()
                self.logger.info(f"✅ Alert resolved: {alert_id}")
                return True
        return False
    
    def shutdown(self):
        """Shutdown monitoring system"""
        self.monitoring_active = False
        if self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        self.logger.info("🔍 Enterprise monitoring system shutdown")

# Global monitoring instance
enterprise_monitoring = EnterpriseMonitoring()