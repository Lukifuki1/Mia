#!/usr/bin/env python3
"""
🔍 MIA Enterprise AGI - Advanced Monitoring System
==================================================

Comprehensive monitoring, alerting, and analytics for enterprise deployment:
- Real-time performance monitoring
- Predictive analytics
- Automated alerting
- Compliance reporting
- Security monitoring
- Resource optimization
"""

import os
import sys
import json
import time
import logging
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class MetricType(Enum):
    """Types of metrics"""
    SYSTEM = "system"
    APPLICATION = "application"
    SECURITY = "security"
    BUSINESS = "business"

@dataclass
class SystemMetric:
    """System performance metric"""
    timestamp: float
    metric_type: MetricType
    name: str
    value: float
    unit: str
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}

@dataclass
class Alert:
    """System alert"""
    id: str
    timestamp: float
    level: AlertLevel
    title: str
    description: str
    source: str
    metric_name: str
    metric_value: float
    threshold: float
    resolved: bool = False
    resolved_at: Optional[float] = None

class MIAEnterpriseMonitor:
    """Enterprise monitoring system for MIA AGI"""
    
    def __init__(self, config_path: str = "mia_data/config/monitoring.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = self._setup_logging()
        
        # Database for metrics storage
        self.db_path = Path("mia_data/monitoring/metrics.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Monitoring state
        self.running = False
        self.metrics_buffer = []
        self.active_alerts = {}
        self.last_cleanup = time.time()
        
        # Thresholds
        self.thresholds = self.config.get("thresholds", {
            "cpu_usage": {"warning": 80, "critical": 95},
            "memory_usage": {"warning": 85, "critical": 95},
            "disk_usage": {"warning": 85, "critical": 95},
            "response_time": {"warning": 2000, "critical": 5000},  # ms
            "error_rate": {"warning": 5, "critical": 10}  # %
        })
        
        self.logger.info("🔍 MIA Enterprise Monitor initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration"""
        if Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load config: {e}")
        
        # Default configuration
        default_config = {
            "monitoring": {
                "interval_seconds": 30,
                "retention_days": 30,
                "batch_size": 100
            },
            "alerting": {
                "enabled": True,
                "email_enabled": False,
                "webhook_enabled": False,
                "smtp_server": "localhost",
                "smtp_port": 587,
                "email_from": "mia-monitor@company.com",
                "email_to": ["admin@company.com"],
                "webhook_url": ""
            },
            "thresholds": {
                "cpu_usage": {"warning": 80, "critical": 95},
                "memory_usage": {"warning": 85, "critical": 95},
                "disk_usage": {"warning": 85, "critical": 95},
                "gpu_usage": {"warning": 90, "critical": 98},
                "response_time": {"warning": 2000, "critical": 5000},
                "error_rate": {"warning": 5, "critical": 10}
            },
            "compliance": {
                "soc2_enabled": True,
                "gdpr_enabled": True,
                "audit_logging": True,
                "data_retention_days": 2555  # 7 years
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """Setup monitoring logging"""
        log_dir = Path("mia_data/logs/monitoring")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logger = logging.getLogger("MIA.Monitor")
        if not logger.handlers:
            handler = logging.FileHandler(log_dir / "monitor.log")
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        
        return logger
    
    def _init_database(self):
        """Initialize metrics database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    metric_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    tags TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    level TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    source TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    threshold REAL NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)')
            
            conn.commit()
    
    async def start(self):
        """Start monitoring system"""
        if self.running:
            return
        
        self.running = True
        self.logger.info("🔍 Starting enterprise monitoring...")
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._system_monitoring_loop()),
            asyncio.create_task(self._application_monitoring_loop()),
            asyncio.create_task(self._security_monitoring_loop()),
            asyncio.create_task(self._metrics_processor_loop()),
            asyncio.create_task(self._alert_processor_loop()),
            asyncio.create_task(self._cleanup_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}")
        finally:
            self.running = False
    
    async def stop(self):
        """Stop monitoring system"""
        self.running = False
        self.logger.info("🛑 Stopping enterprise monitoring...")
        
        # Flush remaining metrics
        if self.metrics_buffer:
            self._flush_metrics()
    
    async def _system_monitoring_loop(self):
        """System resource monitoring loop"""
        while self.running:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.config["monitoring"]["interval_seconds"])
            except Exception as e:
                self.logger.error(f"System monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        timestamp = time.time()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        self._add_metric(SystemMetric(
            timestamp=timestamp,
            metric_type=MetricType.SYSTEM,
            name="cpu_usage",
            value=cpu_percent,
            unit="percent"
        ))
        
        # Memory metrics
        memory = psutil.virtual_memory()
        self._add_metric(SystemMetric(
            timestamp=timestamp,
            metric_type=MetricType.SYSTEM,
            name="memory_usage",
            value=memory.percent,
            unit="percent"
        ))
        
        self._add_metric(SystemMetric(
            timestamp=timestamp,
            metric_type=MetricType.SYSTEM,
            name="memory_available",
            value=memory.available / (1024**3),  # GB
            unit="GB"
        ))
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        self._add_metric(SystemMetric(
            timestamp=timestamp,
            metric_type=MetricType.SYSTEM,
            name="disk_usage",
            value=disk_percent,
            unit="percent"
        ))
        
        # Network metrics
        network = psutil.net_io_counters()
        if network:
            self._add_metric(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.SYSTEM,
                name="network_bytes_sent",
                value=network.bytes_sent,
                unit="bytes"
            ))
            
            self._add_metric(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.SYSTEM,
                name="network_bytes_recv",
                value=network.bytes_recv,
                unit="bytes"
            ))
        
        # GPU metrics (if available)
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            for i, gpu in enumerate(gpus):
                self._add_metric(SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.SYSTEM,
                    name="gpu_usage",
                    value=gpu.load * 100,
                    unit="percent",
                    tags={"gpu_id": str(i)}
                ))
                
                self._add_metric(SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.SYSTEM,
                    name="gpu_memory_usage",
                    value=(gpu.memoryUsed / gpu.memoryTotal) * 100,
                    unit="percent",
                    tags={"gpu_id": str(i)}
                ))
        except ImportError:
            self.logger.debug("GPU monitoring not available - pynvml not installed")
        
        # Check thresholds and generate alerts
        self._check_thresholds(timestamp, {
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "disk_usage": disk_percent
        })
    
    async def _application_monitoring_loop(self):
        """Application-specific monitoring loop"""
        while self.running:
            try:
                await self._collect_application_metrics()
                await asyncio.sleep(self.config["monitoring"]["interval_seconds"] * 2)
            except Exception as e:
                self.logger.error(f"Application monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _collect_application_metrics(self):
        """Collect MIA application metrics"""
        timestamp = time.time()
        
        # Check if MIA services are running
        mia_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if any('mia' in str(cmd).lower() for cmd in proc.info['cmdline'] or []):
                    mia_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        self._add_metric(SystemMetric(
            timestamp=timestamp,
            metric_type=MetricType.APPLICATION,
            name="mia_processes_count",
            value=len(mia_processes),
            unit="count"
        ))
        
        # Collect process-specific metrics
        total_cpu = 0
        total_memory = 0
        
        for proc in mia_processes:
            try:
                cpu_percent = proc.cpu_percent()
                memory_percent = proc.memory_percent()
                
                total_cpu += cpu_percent
                total_memory += memory_percent
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if mia_processes:
            self._add_metric(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.APPLICATION,
                name="mia_cpu_usage",
                value=total_cpu,
                unit="percent"
            ))
            
            self._add_metric(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.APPLICATION,
                name="mia_memory_usage",
                value=total_memory,
                unit="percent"
            ))
        
        # Check application health endpoints
        await self._check_health_endpoints(timestamp)
    
    async def _check_health_endpoints(self, timestamp: float):
        """Check application health endpoints"""
        import aiohttp
        
        endpoints = [
            ("http://localhost:12000/health", "web_interface"),
            ("http://localhost:8000/health", "core_api")
        ]
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for url, service_name in endpoints:
                try:
                    start_time = time.time()
                    async with session.get(url) as response:
                        response_time = (time.time() - start_time) * 1000  # ms
                        
                        self._add_metric(SystemMetric(
                            timestamp=timestamp,
                            metric_type=MetricType.APPLICATION,
                            name="response_time",
                            value=response_time,
                            unit="ms",
                            tags={"service": service_name}
                        ))
                        
                        self._add_metric(SystemMetric(
                            timestamp=timestamp,
                            metric_type=MetricType.APPLICATION,
                            name="service_status",
                            value=1 if response.status == 200 else 0,
                            unit="boolean",
                            tags={"service": service_name}
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"Health check failed for {service_name}: {e}")
                    self._add_metric(SystemMetric(
                        timestamp=timestamp,
                        metric_type=MetricType.APPLICATION,
                        name="service_status",
                        value=0,
                        unit="boolean",
                        tags={"service": service_name}
                    ))
    
    async def _security_monitoring_loop(self):
        """Security monitoring loop"""
        while self.running:
            try:
                await self._collect_security_metrics()
                await asyncio.sleep(self.config["monitoring"]["interval_seconds"] * 4)
            except Exception as e:
                self.logger.error(f"Security monitoring error: {e}")
                await asyncio.sleep(120)
    
    async def _collect_security_metrics(self):
        """Collect security-related metrics"""
        timestamp = time.time()
        
        # Check for suspicious processes
        suspicious_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if proc.info['cpu_percent'] > 90:  # High CPU usage
                    suspicious_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        self._add_metric(SystemMetric(
            timestamp=timestamp,
            metric_type=MetricType.SECURITY,
            name="suspicious_processes",
            value=suspicious_count,
            unit="count"
        ))
        
        # Check network connections
        connections = psutil.net_connections()
        external_connections = len([c for c in connections if c.status == 'ESTABLISHED'])
        
        self._add_metric(SystemMetric(
            timestamp=timestamp,
            metric_type=MetricType.SECURITY,
            name="network_connections",
            value=external_connections,
            unit="count"
        ))
        
        # Check file system integrity (basic)
        critical_files = [
            "mia_production_core.py",
            "mia_enterprise_launcher.py",
            "requirements.txt"
        ]
        
        missing_files = 0
        for file_path in critical_files:
            if not Path(file_path).exists():
                missing_files += 1
        
        self._add_metric(SystemMetric(
            timestamp=timestamp,
            metric_type=MetricType.SECURITY,
            name="missing_critical_files",
            value=missing_files,
            unit="count"
        ))
    
    def _add_metric(self, metric: SystemMetric):
        """Add metric to buffer"""
        self.metrics_buffer.append(metric)
        
        # Flush buffer if it's getting large
        if len(self.metrics_buffer) >= self.config["monitoring"]["batch_size"]:
            self._flush_metrics()
    
    def _flush_metrics(self):
        """Flush metrics buffer to database"""
        if not self.metrics_buffer:
            return
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                for metric in self.metrics_buffer:
                    conn.execute('''
                        INSERT INTO metrics (timestamp, metric_type, name, value, unit, tags)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        metric.timestamp,
                        metric.metric_type.value,
                        metric.name,
                        metric.value,
                        metric.unit,
                        json.dumps(metric.tags) if metric.tags else None
                    ))
                conn.commit()
            
            self.logger.debug(f"Flushed {len(self.metrics_buffer)} metrics to database")
            self.metrics_buffer.clear()
            
        except Exception as e:
            self.logger.error(f"Failed to flush metrics: {e}")
    
    def _check_thresholds(self, timestamp: float, metrics: Dict[str, float]):
        """Check metrics against thresholds and generate alerts"""
        for metric_name, value in metrics.items():
            if metric_name not in self.thresholds:
                continue
            
            thresholds = self.thresholds[metric_name]
            
            # Check critical threshold
            if value >= thresholds.get("critical", 100):
                self._create_alert(
                    timestamp=timestamp,
                    level=AlertLevel.CRITICAL,
                    title=f"Critical {metric_name}",
                    description=f"{metric_name} is at {value:.1f}%, exceeding critical threshold of {thresholds['critical']}%",
                    source="system_monitor",
                    metric_name=metric_name,
                    metric_value=value,
                    threshold=thresholds["critical"]
                )
            
            # Check warning threshold
            elif value >= thresholds.get("warning", 80):
                self._create_alert(
                    timestamp=timestamp,
                    level=AlertLevel.WARNING,
                    title=f"High {metric_name}",
                    description=f"{metric_name} is at {value:.1f}%, exceeding warning threshold of {thresholds['warning']}%",
                    source="system_monitor",
                    metric_name=metric_name,
                    metric_value=value,
                    threshold=thresholds["warning"]
                )
    
    def _create_alert(self, timestamp: float, level: AlertLevel, title: str,
                     description: str, source: str, metric_name: str,
                     metric_value: float, threshold: float):
        """Create and process alert"""
        alert_id = f"{metric_name}_{level.value}_{int(timestamp)}"
        
        # Check if similar alert already exists
        if alert_id in self.active_alerts:
            return
        
        alert = Alert(
            id=alert_id,
            timestamp=timestamp,
            level=level,
            title=title,
            description=description,
            source=source,
            metric_name=metric_name,
            metric_value=metric_value,
            threshold=threshold
        )
        
        self.active_alerts[alert_id] = alert
        
        # Store alert in database
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO alerts 
                    (id, timestamp, level, title, description, source, 
                     metric_name, metric_value, threshold, resolved, resolved_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.id, alert.timestamp, alert.level.value, alert.title,
                    alert.description, alert.source, alert.metric_name,
                    alert.metric_value, alert.threshold, alert.resolved,
                    alert.resolved_at
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to store alert: {e}")
        
        # Send alert notifications
        asyncio.create_task(self._send_alert_notification(alert))
        
        self.logger.warning(f"Alert created: {alert.title} - {alert.description}")
    
    async def _send_alert_notification(self, alert: Alert):
        """Send alert notification"""
        if not self.config["alerting"]["enabled"]:
            return
        
        try:
            # Email notification
            if self.config["alerting"]["email_enabled"]:
                await self._send_email_alert(alert)
            
            # Webhook notification
            if self.config["alerting"]["webhook_enabled"]:
                await self._send_webhook_alert(alert)
                
        except Exception as e:
            self.logger.error(f"Failed to send alert notification: {e}")
    
    async def _send_email_alert(self, alert: Alert):
        """Send email alert notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config["alerting"]["email_from"]
            msg['To'] = ", ".join(self.config["alerting"]["email_to"])
            msg['Subject'] = f"MIA Alert: {alert.title}"
            
            body = f"""
MIA Enterprise AGI Alert

Level: {alert.level.value.upper()}
Title: {alert.title}
Description: {alert.description}
Source: {alert.source}
Metric: {alert.metric_name}
Value: {alert.metric_value}
Threshold: {alert.threshold}
Time: {datetime.fromtimestamp(alert.timestamp)}

Please investigate and take appropriate action.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(
                self.config["alerting"]["smtp_server"],
                self.config["alerting"]["smtp_port"]
            )
            server.starttls()
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email alert sent for: {alert.title}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    async def _send_webhook_alert(self, alert: Alert):
        """Send webhook alert notification"""
        import aiohttp
        
        try:
            webhook_url = self.config["alerting"]["webhook_url"]
            if not webhook_url:
                return
            
            payload = {
                "alert_id": alert.id,
                "timestamp": alert.timestamp,
                "level": alert.level.value,
                "title": alert.title,
                "description": alert.description,
                "source": alert.source,
                "metric_name": alert.metric_name,
                "metric_value": alert.metric_value,
                "threshold": alert.threshold
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        self.logger.info(f"Webhook alert sent for: {alert.title}")
                    else:
                        self.logger.error(f"Webhook alert failed: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Failed to send webhook alert: {e}")
    
    async def _metrics_processor_loop(self):
        """Process and analyze metrics"""
        while self.running:
            try:
                # Flush metrics buffer periodically
                if self.metrics_buffer:
                    self._flush_metrics()
                
                await asyncio.sleep(60)  # Process every minute
                
            except Exception as e:
                self.logger.error(f"Metrics processor error: {e}")
                await asyncio.sleep(60)
    
    async def _alert_processor_loop(self):
        """Process and manage alerts"""
        while self.running:
            try:
                # Auto-resolve alerts that are no longer active
                current_time = time.time()
                resolved_alerts = []
                
                for alert_id, alert in self.active_alerts.items():
                    # Auto-resolve alerts older than 1 hour if conditions improved
                    if current_time - alert.timestamp > 3600:  # 1 hour
                        alert.resolved = True
                        alert.resolved_at = current_time
                        resolved_alerts.append(alert_id)
                
                # Remove resolved alerts
                for alert_id in resolved_alerts:
                    del self.active_alerts[alert_id]
                    self.logger.info(f"Auto-resolved alert: {alert_id}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Alert processor error: {e}")
                await asyncio.sleep(300)
    
    async def _cleanup_loop(self):
        """Cleanup old data"""
        while self.running:
            try:
                current_time = time.time()
                
                # Cleanup every 24 hours
                if current_time - self.last_cleanup > 86400:
                    await self._cleanup_old_data()
                    self.last_cleanup = current_time
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_data(self):
        """Cleanup old metrics and alerts"""
        try:
            retention_days = self.config["monitoring"]["retention_days"]
            cutoff_time = time.time() - (retention_days * 86400)
            
            with sqlite3.connect(self.db_path) as conn:
                # Cleanup old metrics
                result = conn.execute(
                    'DELETE FROM metrics WHERE timestamp < ?',
                    (cutoff_time,)
                )
                metrics_deleted = result.rowcount
                
                # Cleanup old resolved alerts
                result = conn.execute(
                    'DELETE FROM alerts WHERE resolved = 1 AND timestamp < ?',
                    (cutoff_time,)
                )
                alerts_deleted = result.rowcount
                
                conn.commit()
            
            self.logger.info(f"Cleanup completed: {metrics_deleted} metrics, {alerts_deleted} alerts deleted")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the last N hours"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            
            with sqlite3.connect(self.db_path) as conn:
                # Get metric counts by type
                cursor = conn.execute('''
                    SELECT metric_type, COUNT(*) as count
                    FROM metrics 
                    WHERE timestamp > ?
                    GROUP BY metric_type
                ''', (cutoff_time,))
                
                metric_counts = dict(cursor.fetchall())
                
                # Get recent alerts
                cursor = conn.execute('''
                    SELECT level, COUNT(*) as count
                    FROM alerts 
                    WHERE timestamp > ?
                    GROUP BY level
                ''', (cutoff_time,))
                
                alert_counts = dict(cursor.fetchall())
                
                return {
                    "period_hours": hours,
                    "metric_counts": metric_counts,
                    "alert_counts": alert_counts,
                    "active_alerts": len(self.active_alerts),
                    "last_updated": time.time()
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get metrics summary: {e}")
            return {}


async def main():
    """Main entry point for monitoring system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MIA Enterprise Monitor")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    
    args = parser.parse_args()
    
    # Create monitor
    config_path = args.config or "mia_data/config/monitoring.json"
    monitor = MIAEnterpriseMonitor(config_path)
    
    try:
        print("🔍 Starting MIA Enterprise Monitor...")
        await monitor.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested")
    except Exception as e:
        print(f"❌ Monitor error: {e}")
    finally:
        await monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())