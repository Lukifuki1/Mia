#!/usr/bin/env python3
"""
📊 MIA Enterprise AGI - Enterprise Analytics Dashboard
=====================================================

Advanced analytics and business intelligence dashboard:
- Real-time performance metrics
- Predictive analytics and insights
- Business intelligence reporting
- Custom dashboards and visualizations
- Data aggregation and analysis
"""

import asyncio
import time
import logging
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from datetime import datetime, timedelta
import statistics
import math

class MetricType(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class Metric:
    metric_id: str
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    tags: Dict[str, str]
    unit: str

@dataclass
class Alert:
    alert_id: str
    metric_name: str
    level: AlertLevel
    message: str
    threshold: float
    current_value: float
    timestamp: datetime
    resolved: bool

@dataclass
class Dashboard:
    dashboard_id: str
    name: str
    description: str
    widgets: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    owner: str
    shared: bool

class MetricsCollector:
    """Advanced metrics collection system"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = Path(db_path)
        self.logger = self._setup_logging()
        
        self.metrics_buffer: List[Metric] = []
        self.buffer_lock = threading.Lock()
        self.collection_active = False
        
        self._init_database()
        
        self.logger.info("📊 Metrics Collector initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("MIA.MetricsCollector")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    tags TEXT,
                    unit TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    threshold REAL NOT NULL,
                    current_value REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    resolved INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_name_timestamp 
                ON metrics(name, timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_timestamp 
                ON alerts(timestamp)
            """)
    
    def record_metric(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE,
                     tags: Optional[Dict[str, str]] = None, unit: str = "") -> bool:
        """Record a metric"""
        try:
            metric = Metric(
                metric_id=f"{name}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 * 1000)}",
                name=name,
                metric_type=metric_type,
                value=value,
                timestamp=datetime.now(),
                tags=tags or {},
                unit=unit
            )
            
            with self.buffer_lock:
                self.metrics_buffer.append(metric)
                
                # Flush buffer if it gets too large
                if len(self.metrics_buffer) > 1000:
                    self._flush_metrics()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record metric: {e}")
            return False
    
    def _flush_metrics(self):
        """Flush metrics buffer to database"""
        try:
            if not self.metrics_buffer:
                return
            
            with sqlite3.connect(self.db_path) as conn:
                for metric in self.metrics_buffer:
                    conn.execute("""
                        INSERT INTO metrics 
                        (metric_id, name, metric_type, value, timestamp, tags, unit)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        metric.metric_id,
                        metric.name,
                        metric.metric_type.value,
                        metric.value,
                        metric.timestamp.isoformat(),
                        json.dumps(metric.tags),
                        metric.unit
                    ))
            
            self.metrics_buffer.clear()
            self.logger.debug(f"Flushed {len(self.metrics_buffer)} metrics to database")
            
        except Exception as e:
            self.logger.error(f"Failed to flush metrics: {e}")
    
    def start_collection(self):
        """Start automatic metrics collection"""
        self.collection_active = True
        
        def collection_loop():
            while self.collection_active:
                try:
                    # Collect system metrics
                    self._collect_system_metrics()
                    
                    # Flush metrics buffer periodically
                    with self.buffer_lock:
                        if self.metrics_buffer:
                            self._flush_metrics()
                    
                    time.sleep(30)  # Collect every 30 seconds
                    
                except Exception as e:
                    self.logger.error(f"Collection loop error: {e}")
                    time.sleep(60)
        
        collection_thread = threading.Thread(target=collection_loop, daemon=True)
        collection_thread.start()
        
        self.logger.info("📊 Metrics collection started")
    
    def stop_collection(self):
        """Stop metrics collection"""
        self.collection_active = False
        
        # Flush remaining metrics
        with self.buffer_lock:
            if self.metrics_buffer:
                self._flush_metrics()
        
        self.logger.info("📊 Metrics collection stopped")
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            import psutil
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric("system.cpu.usage", cpu_percent, MetricType.GAUGE, unit="%")
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.record_metric("system.memory.usage", memory.percent, MetricType.GAUGE, unit="%")
            self.record_metric("system.memory.available", memory.available / 1024 / 1024, MetricType.GAUGE, unit="MB")
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.record_metric("system.disk.usage", disk_percent, MetricType.GAUGE, unit="%")
            
            # Process metrics
            process = psutil.Process()
            self.record_metric("process.memory.rss", process.memory_info().rss / 1024 / 1024, MetricType.GAUGE, unit="MB")
            self.record_metric("process.cpu.percent", process.cpu_percent(), MetricType.GAUGE, unit="%")
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
    
    def get_metrics(self, name: str, start_time: Optional[datetime] = None, 
                   end_time: Optional[datetime] = None, limit: int = 1000) -> List[Metric]:
        """Get metrics by name and time range"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM metrics WHERE name = ?"
                params = [name]
                
                if start_time:
                    query += " AND timestamp >= ?"
                    params.append(start_time.isoformat())
                
                if end_time:
                    query += " AND timestamp <= ?"
                    params.append(end_time.isoformat())
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                metrics = []
                for row in rows:
                    metric = Metric(
                        metric_id=row[1],
                        name=row[2],
                        metric_type=MetricType(row[3]),
                        value=row[4],
                        timestamp=datetime.fromisoformat(row[5]),
                        tags=json.loads(row[6]) if row[6] else {},
                        unit=row[7] or ""
                    )
                    metrics.append(metric)
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {e}")
            return []

class AlertManager:
    """Advanced alerting system"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.logger = self._setup_logging()
        
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_callbacks: List[Callable] = []
        
        self.monitoring_active = False
        
        self.logger.info("🚨 Alert Manager initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("MIA.AlertManager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def add_alert_rule(self, rule_id: str, metric_name: str, threshold: float,
                      condition: str = "greater", level: AlertLevel = AlertLevel.WARNING,
                      message: str = "") -> bool:
        """Add alert rule"""
        try:
            self.alert_rules[rule_id] = {
                "metric_name": metric_name,
                "threshold": threshold,
                "condition": condition,  # greater, less, equal
                "level": level,
                "message": message or f"{metric_name} {condition} {threshold}"
            }
            
            self.logger.info(f"🚨 Alert rule added: {rule_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add alert rule: {e}")
            return False
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add alert callback function"""
        self.alert_callbacks.append(callback)
    
    def start_monitoring(self):
        """Start alert monitoring"""
        self.monitoring_active = True
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    self._check_alert_rules()
                    time.sleep(60)  # Check every minute
                    
                except Exception as e:
                    self.logger.error(f"Alert monitoring error: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitor_thread.start()
        
        self.logger.info("🚨 Alert monitoring started")
    
    def stop_monitoring(self):
        """Stop alert monitoring"""
        self.monitoring_active = False
        self.logger.info("🚨 Alert monitoring stopped")
    
    def _check_alert_rules(self):
        """Check all alert rules"""
        try:
            for rule_id, rule in self.alert_rules.items():
                metric_name = rule["metric_name"]
                threshold = rule["threshold"]
                condition = rule["condition"]
                level = rule["level"]
                message = rule["message"]
                
                # Get recent metrics
                recent_metrics = self.metrics_collector.get_metrics(
                    metric_name,
                    start_time=datetime.now() - timedelta(minutes=5),
                    limit=10
                )
                
                if not recent_metrics:
                    continue
                
                # Check latest value
                latest_metric = recent_metrics[0]
                current_value = latest_metric.value
                
                # Evaluate condition
                alert_triggered = False
                if condition == "greater" and current_value > threshold:
                    alert_triggered = True
                elif condition == "less" and current_value < threshold:
                    alert_triggered = True
                elif condition == "equal" and abs(current_value - threshold) < 0.001:
                    alert_triggered = True
                
                if alert_triggered:
                    # Create or update alert
                    alert_id = f"{rule_id}_{metric_name}"
                    
                    if alert_id not in self.active_alerts:
                        alert = Alert(
                            alert_id=alert_id,
                            metric_name=metric_name,
                            level=level,
                            message=message,
                            threshold=threshold,
                            current_value=current_value,
                            timestamp=datetime.now(),
                            resolved=False
                        )
                        
                        self.active_alerts[alert_id] = alert
                        self._trigger_alert(alert)
                        
                        # Store in database
                        self._store_alert(alert)
                else:
                    # Resolve alert if it exists
                    alert_id = f"{rule_id}_{metric_name}"
                    if alert_id in self.active_alerts:
                        alert = self.active_alerts[alert_id]
                        alert.resolved = True
                        self._resolve_alert(alert)
                        del self.active_alerts[alert_id]
                
        except Exception as e:
            self.logger.error(f"Failed to check alert rules: {e}")
    
    def _trigger_alert(self, alert: Alert):
        """Trigger alert"""
        try:
            self.logger.warning(f"🚨 ALERT: {alert.message} (Current: {alert.current_value}, Threshold: {alert.threshold})")
            
            # Call alert callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"Alert callback error: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to trigger alert: {e}")
    
    def _resolve_alert(self, alert: Alert):
        """Resolve alert"""
        try:
            self.logger.info(f"✅ RESOLVED: {alert.message}")
            
        except Exception as e:
            self.logger.error(f"Failed to resolve alert: {e}")
    
    def _store_alert(self, alert: Alert):
        """Store alert in database"""
        try:
            with sqlite3.connect(self.metrics_collector.db_path) as conn:
                conn.execute("""
                    INSERT INTO alerts 
                    (alert_id, metric_name, level, message, threshold, current_value, timestamp, resolved)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.alert_id,
                    alert.metric_name,
                    alert.level.value,
                    alert.message,
                    alert.threshold,
                    alert.current_value,
                    alert.timestamp.isoformat(),
                    0 if not alert.resolved else 1
                ))
                
        except Exception as e:
            self.logger.error(f"Failed to store alert: {e}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())

class AnalyticsEngine:
    """Advanced analytics and insights engine"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.logger = self._setup_logging()
        
        self.logger.info("🔍 Analytics Engine initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("MIA.AnalyticsEngine")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def calculate_statistics(self, metric_name: str, hours: int = 24) -> Dict[str, float]:
        """Calculate statistical metrics"""
        try:
            start_time = datetime.now() - timedelta(hours=hours)
            metrics = self.metrics_collector.get_metrics(metric_name, start_time=start_time)
            
            if not metrics:
                return {}
            
            values = [m.value for m in metrics]
            
            stats = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "percentile_95": self._percentile(values, 95),
                "percentile_99": self._percentile(values, 99)
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to calculate statistics: {e}")
            return {}
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile"""
        try:
            sorted_values = sorted(values)
            index = (percentile / 100) * (len(sorted_values) - 1)
            
            if index.is_integer():
                return sorted_values[int(index)]
            else:
                lower = sorted_values[int(index)]
                upper = sorted_values[int(index) + 1]
                return lower + (upper - lower) * (index - int(index))
                
        except Exception as e:
            return 0.0
    
    def detect_anomalies(self, metric_name: str, hours: int = 24, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalies using statistical methods"""
        try:
            start_time = datetime.now() - timedelta(hours=hours)
            metrics = self.metrics_collector.get_metrics(metric_name, start_time=start_time)
            
            if len(metrics) < 10:
                return []
            
            values = [m.value for m in metrics]
            mean = statistics.mean(values)
            std_dev = statistics.stdev(values) if len(values) > 1 else 0
            
            anomalies = []
            for metric in metrics:
                if std_dev > 0:
                    z_score = abs(metric.value - mean) / std_dev
                    if z_score > threshold:
                        anomalies.append({
                            "timestamp": metric.timestamp.isoformat(),
                            "value": metric.value,
                            "z_score": z_score,
                            "deviation": metric.value - mean
                        })
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Failed to detect anomalies: {e}")
            return []
    
    def predict_trend(self, metric_name: str, hours: int = 24, forecast_hours: int = 6) -> Dict[str, Any]:
        """Simple trend prediction using linear regression"""
        try:
            start_time = datetime.now() - timedelta(hours=hours)
            metrics = self.metrics_collector.get_metrics(metric_name, start_time=start_time)
            
            if len(metrics) < 5:
                return {}
            
            # Prepare data for linear regression
            timestamps = [(m.timestamp - metrics[-1].timestamp).total_seconds() for m in metrics]
            values = [m.value for m in metrics]
            
            # Simple linear regression
            n = len(timestamps)
            sum_x = sum(timestamps)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(timestamps, values))
            sum_x2 = sum(x * x for x in timestamps)
            
            # Calculate slope and intercept
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Predict future values
            future_time = forecast_hours * 3600  # Convert to seconds
            predicted_value = slope * future_time + intercept
            
            # Calculate confidence (R-squared)
            y_mean = sum_y / n
            ss_tot = sum((y - y_mean) ** 2 for y in values)
            ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(timestamps, values))
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            return {
                "current_value": values[0],
                "predicted_value": predicted_value,
                "trend": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
                "slope": slope,
                "confidence": r_squared,
                "forecast_hours": forecast_hours
            }
            
        except Exception as e:
            self.logger.error(f"Failed to predict trend: {e}")
            return {}

class DashboardManager:
    """Dashboard management system"""
    
    def __init__(self, metrics_collector: MetricsCollector, analytics_engine: AnalyticsEngine):
        self.metrics_collector = metrics_collector
        self.analytics_engine = analytics_engine
        self.logger = self._setup_logging()
        
        self.dashboards: Dict[str, Dashboard] = {}
        
        # Create default dashboards
        self._create_default_dashboards()
        
        self.logger.info("📊 Dashboard Manager initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("MIA.DashboardManager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _create_default_dashboards(self):
        """Create default dashboards"""
        try:
            # System Performance Dashboard
            system_dashboard = Dashboard(
                dashboard_id="system_performance",
                name="System Performance",
                description="Real-time system performance metrics",
                widgets=[
                    {
                        "type": "gauge",
                        "title": "CPU Usage",
                        "metric": "system.cpu.usage",
                        "unit": "%",
                        "thresholds": {"warning": 70, "critical": 90}
                    },
                    {
                        "type": "gauge",
                        "title": "Memory Usage",
                        "metric": "system.memory.usage",
                        "unit": "%",
                        "thresholds": {"warning": 80, "critical": 95}
                    },
                    {
                        "type": "line_chart",
                        "title": "CPU Usage Over Time",
                        "metric": "system.cpu.usage",
                        "time_range": "1h"
                    },
                    {
                        "type": "line_chart",
                        "title": "Memory Usage Over Time",
                        "metric": "system.memory.usage",
                        "time_range": "1h"
                    }
                ],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                owner="system",
                shared=True
            )
            
            self.dashboards["system_performance"] = system_dashboard
            
            # Application Metrics Dashboard
            app_dashboard = Dashboard(
                dashboard_id="application_metrics",
                name="Application Metrics",
                description="MIA Enterprise AGI application metrics",
                widgets=[
                    {
                        "type": "counter",
                        "title": "Total Requests",
                        "metric": "app.requests.total"
                    },
                    {
                        "type": "gauge",
                        "title": "Response Time",
                        "metric": "app.response.time",
                        "unit": "ms"
                    },
                    {
                        "type": "line_chart",
                        "title": "Request Rate",
                        "metric": "app.requests.rate",
                        "time_range": "1h"
                    },
                    {
                        "type": "bar_chart",
                        "title": "Error Rate by Type",
                        "metric": "app.errors.by_type",
                        "time_range": "24h"
                    }
                ],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                owner="system",
                shared=True
            )
            
            self.dashboards["application_metrics"] = app_dashboard
            
        except Exception as e:
            self.logger.error(f"Failed to create default dashboards: {e}")
    
    def create_dashboard(self, dashboard_id: str, name: str, description: str,
                        widgets: List[Dict[str, Any]], owner: str = "user") -> bool:
        """Create custom dashboard"""
        try:
            dashboard = Dashboard(
                dashboard_id=dashboard_id,
                name=name,
                description=description,
                widgets=widgets,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                owner=owner,
                shared=False
            )
            
            self.dashboards[dashboard_id] = dashboard
            
            self.logger.info(f"📊 Dashboard created: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create dashboard: {e}")
            return False
    
    def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get dashboard data with real-time metrics"""
        try:
            if dashboard_id not in self.dashboards:
                return {}
            
            dashboard = self.dashboards[dashboard_id]
            dashboard_data = {
                "dashboard": asdict(dashboard),
                "widgets_data": []
            }
            
            for widget in dashboard.widgets:
                widget_data = self._get_widget_data(widget)
                dashboard_data["widgets_data"].append(widget_data)
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Failed to get dashboard data: {e}")
            return {}
    
    def _get_widget_data(self, widget: Dict[str, Any]) -> Dict[str, Any]:
        """Get data for specific widget"""
        try:
            widget_type = widget.get("type")
            metric_name = widget.get("metric")
            time_range = widget.get("time_range", "1h")
            
            if not metric_name:
                return {"error": "No metric specified"}
            
            # Parse time range
            hours = self._parse_time_range(time_range)
            
            # Get metrics
            start_time = datetime.now() - timedelta(hours=hours)
            metrics = self.metrics_collector.get_metrics(metric_name, start_time=start_time)
            
            if widget_type == "gauge":
                # Latest value for gauge
                latest_value = metrics[0].value if metrics else 0
                return {
                    "type": "gauge",
                    "value": latest_value,
                    "unit": widget.get("unit", ""),
                    "thresholds": widget.get("thresholds", {})
                }
            
            elif widget_type == "counter":
                # Sum for counter
                total_value = sum(m.value for m in metrics)
                return {
                    "type": "counter",
                    "value": total_value
                }
            
            elif widget_type == "line_chart":
                # Time series data
                data_points = [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "value": m.value
                    } for m in reversed(metrics)
                ]
                return {
                    "type": "line_chart",
                    "data": data_points
                }
            
            elif widget_type == "bar_chart":
                # Aggregated data (simplified)
                if metrics:
                    stats = self.analytics_engine.calculate_statistics(metric_name, hours)
                    return {
                        "type": "bar_chart",
                        "data": [
                            {"label": "Min", "value": stats.get("min", 0)},
                            {"label": "Mean", "value": stats.get("mean", 0)},
                            {"label": "Max", "value": stats.get("max", 0)}
                        ]
                    }
                else:
                    return {"type": "bar_chart", "data": []}
            
            else:
                return {"error": f"Unknown widget type: {widget_type}"}
                
        except Exception as e:
            self.logger.error(f"Failed to get widget data: {e}")
            return {"error": str(e)}
    
    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to hours"""
        try:
            if time_range.endswith("h"):
                return int(time_range[:-1])
            elif time_range.endswith("d"):
                return int(time_range[:-1]) * 24
            elif time_range.endswith("m"):
                return int(time_range[:-1]) / 60
            else:
                return 1  # Default to 1 hour
                
        except:
            return 1
    
    def list_dashboards(self) -> List[Dict[str, Any]]:
        """List all dashboards"""
        return [
            {
                "dashboard_id": dashboard.dashboard_id,
                "name": dashboard.name,
                "description": dashboard.description,
                "owner": dashboard.owner,
                "shared": dashboard.shared,
                "widget_count": len(dashboard.widgets)
            } for dashboard in self.dashboards.values()
        ]

class UltimateAnalyticsDashboard:
    """Ultimate Enterprise Analytics Dashboard"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.logger = self._setup_logging()
        
        # Initialize components
        self.metrics_collector = MetricsCollector(db_path)
        self.analytics_engine = AnalyticsEngine(self.metrics_collector)
        self.alert_manager = AlertManager(self.metrics_collector)
        self.dashboard_manager = DashboardManager(self.metrics_collector, self.analytics_engine)
        
        # Setup default alert rules
        self._setup_default_alerts()
        
        self.logger.info("📊 Ultimate Analytics Dashboard initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("MIA.UltimateAnalytics")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_default_alerts(self):
        """Setup default alert rules"""
        try:
            # CPU usage alert
            self.alert_manager.add_alert_rule(
                "high_cpu",
                "system.cpu.usage",
                80.0,
                "greater",
                AlertLevel.WARNING,
                "High CPU usage detected"
            )
            
            # Memory usage alert
            self.alert_manager.add_alert_rule(
                "high_memory",
                "system.memory.usage",
                90.0,
                "greater",
                AlertLevel.CRITICAL,
                "High memory usage detected"
            )
            
            # Disk usage alert
            self.alert_manager.add_alert_rule(
                "high_disk",
                "system.disk.usage",
                85.0,
                "greater",
                AlertLevel.WARNING,
                "High disk usage detected"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to setup default alerts: {e}")
    
    def start_analytics_system(self):
        """Start the analytics system"""
        try:
            self.logger.info("🚀 Starting Ultimate Analytics Dashboard...")
            
            # Start metrics collection
            self.metrics_collector.start_collection()
            
            # Start alert monitoring
            self.alert_manager.start_monitoring()
            
            self.logger.info("✅ Analytics system started")
            
        except Exception as e:
            self.logger.error(f"Failed to start analytics system: {e}")
    
    def stop_analytics_system(self):
        """Stop the analytics system"""
        try:
            self.metrics_collector.stop_collection()
            self.alert_manager.stop_monitoring()
            
            self.logger.info("🛑 Analytics system stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop analytics system: {e}")
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        try:
            # Get recent metrics
            cpu_stats = self.analytics_engine.calculate_statistics("system.cpu.usage", 1)
            memory_stats = self.analytics_engine.calculate_statistics("system.memory.usage", 1)
            
            # Get active alerts
            active_alerts = self.alert_manager.get_active_alerts()
            
            # Get dashboards
            dashboards = self.dashboard_manager.list_dashboards()
            
            return {
                "system_health": {
                    "cpu_usage": cpu_stats.get("mean", 0),
                    "memory_usage": memory_stats.get("mean", 0),
                    "status": "healthy" if len(active_alerts) == 0 else "warning"
                },
                "alerts": {
                    "active_count": len(active_alerts),
                    "critical_count": len([a for a in active_alerts if a.level == AlertLevel.CRITICAL]),
                    "warning_count": len([a for a in active_alerts if a.level == AlertLevel.WARNING])
                },
                "dashboards": {
                    "total_count": len(dashboards),
                    "shared_count": len([d for d in dashboards if d["shared"]])
                },
                "metrics": {
                    "collection_active": self.metrics_collector.collection_active,
                    "monitoring_active": self.alert_manager.monitoring_active
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system overview: {e}")
            return {}

def main():
    """Main execution function"""
    print("📊 Initializing Ultimate Enterprise Analytics Dashboard...")
    
    # Initialize analytics dashboard
    analytics_dashboard = UltimateAnalyticsDashboard()
    
    # Start analytics system
    analytics_dashboard.start_analytics_system()
    
    # Record some sample metrics
    metrics_collector = analytics_dashboard.metrics_collector
    
    # Simulate application metrics
    for i in range(10):
        metrics_collector.record_metric("app.requests.total", i * 10, MetricType.COUNTER)
        metrics_collector.record_metric("app.response.time", 50 + i * 5, MetricType.GAUGE, unit="ms")
        metrics_collector.record_metric("app.errors.rate", 0.01 + i * 0.001, MetricType.GAUGE, unit="%")
        time.sleep(0.1)
    
    # Wait for some data collection
    print("⏱️ Collecting analytics data...")
    time.sleep(3)
    
    # Get system overview
    overview = analytics_dashboard.get_system_overview()
    
    # Get dashboard data
    system_dashboard = analytics_dashboard.dashboard_manager.get_dashboard_data("system_performance")
    app_dashboard = analytics_dashboard.dashboard_manager.get_dashboard_data("application_metrics")
    
    print("\n" + "="*60)
    print("📊 ULTIMATE ENTERPRISE ANALYTICS DASHBOARD")
    print("="*60)
    
    if overview:
        health = overview.get("system_health", {})
        print(f"System Status: {health.get('status', 'unknown').upper()}")
        print(f"CPU Usage: {health.get('cpu_usage', 0):.1f}%")
        print(f"Memory Usage: {health.get('memory_usage', 0):.1f}%")
        
        alerts = overview.get("alerts", {})
        print(f"\nAlerts:")
        print(f"  Active: {alerts.get('active_count', 0)}")
        print(f"  Critical: {alerts.get('critical_count', 0)}")
        print(f"  Warning: {alerts.get('warning_count', 0)}")
        
        dashboards = overview.get("dashboards", {})
        print(f"\nDashboards:")
        print(f"  Total: {dashboards.get('total_count', 0)}")
        print(f"  Shared: {dashboards.get('shared_count', 0)}")
        
        metrics = overview.get("metrics", {})
        print(f"\nMetrics Collection:")
        print(f"  Active: {metrics.get('collection_active', False)}")
        print(f"  Monitoring: {metrics.get('monitoring_active', False)}")
    
    print(f"\nAvailable Dashboards:")
    dashboard_list = analytics_dashboard.dashboard_manager.list_dashboards()
    for dashboard in dashboard_list:
        print(f"  - {dashboard['name']}: {dashboard['widget_count']} widgets")
    
    print("="*60)
    print("✅ Ultimate Enterprise Analytics Dashboard operational!")
    
    # Stop analytics system
    analytics_dashboard.stop_analytics_system()

if __name__ == "__main__":
    main()