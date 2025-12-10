#!/usr/bin/env python3
"""
MIA Enterprise Analytics Module
Provides advanced analytics and reporting capabilities
"""

import os
import json
import logging
import time
import statistics
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import sqlite3
import numpy as np

class MetricType(Enum):
    """Types of metrics"""
    PERFORMANCE = "performance"
    USAGE = "usage"
    ERROR = "error"
    SECURITY = "security"
    BUSINESS = "business"
    SYSTEM = "system"

class AggregationType(Enum):
    """Aggregation types"""
    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"

@dataclass
class Metric:
    """Analytics metric"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: float
    tags: Dict[str, str] = None
    metadata: Dict[str, Any] = None

@dataclass
class Report:
    """Analytics report"""
    title: str
    description: str
    metrics: List[Metric]
    generated_at: float
    time_range: Tuple[float, float]
    summary: Dict[str, Any] = None

class EnterpriseAnalytics:
    """Enterprise analytics engine"""
    
    def __init__(self, db_path: str = "mia/data/analytics/metrics.db"):
        self.db_path = Path(db_path)
        self.logger = self._setup_logging()
        self._initialize_database()
        self.metric_buffer = []
        self.buffer_size = 1000
        
    def _setup_logging(self) -> logging.Logger:
        """Setup analytics logging"""
        logger = logging.getLogger("MIA.Analytics")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _initialize_database(self):
        """Initialize analytics database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    metric_type TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    tags TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
                ON metrics(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_name 
                ON metrics(name)
            """)
    
    def record_metric(self, name: str, value: float, metric_type: MetricType,
                     tags: Dict[str, str] = None, metadata: Dict[str, Any] = None):
        """Record a metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=time.time(),
            tags=tags or {},
            metadata=metadata or {}
        )
        
        self.metric_buffer.append(metric)
        
        # Flush buffer if full
        if len(self.metric_buffer) >= self.buffer_size:
            self._flush_metrics()
    
    def _flush_metrics(self):
        """Flush metrics buffer to database"""
        if not self.metric_buffer:
            return
        
        with sqlite3.connect(self.db_path) as conn:
            for metric in self.metric_buffer:
                conn.execute("""
                    INSERT INTO metrics (name, value, metric_type, timestamp, tags, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    metric.name,
                    metric.value,
                    metric.metric_type.value,
                    metric.timestamp,
                    json.dumps(metric.tags),
                    json.dumps(metric.metadata)
                ))
        
        self.logger.info(f"Flushed {len(self.metric_buffer)} metrics to database")
        self.metric_buffer.clear()
    
    def get_metrics(self, name: str = None, metric_type: MetricType = None,
                   start_time: float = None, end_time: float = None,
                   limit: int = 1000) -> List[Metric]:
        """Get metrics from database"""
        query = "SELECT * FROM metrics WHERE 1=1"
        params = []
        
        if name:
            query += " AND name = ?"
            params.append(name)
        
        if metric_type:
            query += " AND metric_type = ?"
            params.append(metric_type.value)
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        metrics = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            for row in cursor.fetchall():
                metric = Metric(
                    name=row[1],
                    value=row[2],
                    metric_type=MetricType(row[3]),
                    timestamp=row[4],
                    tags=json.loads(row[5]) if row[5] else {},
                    metadata=json.loads(row[6]) if row[6] else {}
                )
                metrics.append(metric)
        
        return metrics
    
    def aggregate_metrics(self, name: str, aggregation: AggregationType,
                         start_time: float = None, end_time: float = None) -> float:
        """Aggregate metrics"""
        metrics = self.get_metrics(name=name, start_time=start_time, end_time=end_time)
        
        if not metrics:
            return 0.0
        
        values = [m.value for m in metrics]
        
        if aggregation == AggregationType.SUM:
            return sum(values)
        elif aggregation == AggregationType.AVERAGE:
            return statistics.mean(values)
        elif aggregation == AggregationType.COUNT:
            return len(values)
        elif aggregation == AggregationType.MIN:
            return min(values)
        elif aggregation == AggregationType.MAX:
            return max(values)
        elif aggregation == AggregationType.MEDIAN:
            return statistics.median(values)
        else:
            return 0.0
    
    def generate_performance_report(self, hours: int = 24) -> Report:
        """Generate performance report"""
        end_time = time.time()
        start_time = end_time - (hours * 3600)
        
        # Get performance metrics
        response_times = self.get_metrics(
            name="response_time",
            metric_type=MetricType.PERFORMANCE,
            start_time=start_time,
            end_time=end_time
        )
        
        cpu_usage = self.get_metrics(
            name="cpu_usage",
            metric_type=MetricType.SYSTEM,
            start_time=start_time,
            end_time=end_time
        )
        
        memory_usage = self.get_metrics(
            name="memory_usage",
            metric_type=MetricType.SYSTEM,
            start_time=start_time,
            end_time=end_time
        )
        
        # Calculate summary statistics
        summary = {
            "avg_response_time": self.aggregate_metrics("response_time", AggregationType.AVERAGE, start_time, end_time),
            "max_response_time": self.aggregate_metrics("response_time", AggregationType.MAX, start_time, end_time),
            "avg_cpu_usage": self.aggregate_metrics("cpu_usage", AggregationType.AVERAGE, start_time, end_time),
            "max_cpu_usage": self.aggregate_metrics("cpu_usage", AggregationType.MAX, start_time, end_time),
            "avg_memory_usage": self.aggregate_metrics("memory_usage", AggregationType.AVERAGE, start_time, end_time),
            "max_memory_usage": self.aggregate_metrics("memory_usage", AggregationType.MAX, start_time, end_time),
            "total_requests": len(response_times)
        }
        
        all_metrics = response_times + cpu_usage + memory_usage
        
        return Report(
            title=f"Performance Report - Last {hours} Hours",
            description=f"System performance metrics for the last {hours} hours",
            metrics=all_metrics,
            generated_at=time.time(),
            time_range=(start_time, end_time),
            summary=summary
        )
    
    def generate_usage_report(self, days: int = 7) -> Report:
        """Generate usage report"""
        end_time = time.time()
        start_time = end_time - (days * 24 * 3600)
        
        # Get usage metrics
        user_sessions = self.get_metrics(
            name="user_session",
            metric_type=MetricType.USAGE,
            start_time=start_time,
            end_time=end_time
        )
        
        api_calls = self.get_metrics(
            name="api_call",
            metric_type=MetricType.USAGE,
            start_time=start_time,
            end_time=end_time
        )
        
        # Calculate summary
        summary = {
            "total_sessions": len(user_sessions),
            "total_api_calls": len(api_calls),
            "avg_sessions_per_day": len(user_sessions) / days,
            "avg_api_calls_per_day": len(api_calls) / days
        }
        
        all_metrics = user_sessions + api_calls
        
        return Report(
            title=f"Usage Report - Last {days} Days",
            description=f"System usage metrics for the last {days} days",
            metrics=all_metrics,
            generated_at=time.time(),
            time_range=(start_time, end_time),
            summary=summary
        )
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        current_time = time.time()
        last_hour = current_time - 3600
        
        return {
            "current_timestamp": current_time,
            "active_sessions": self.aggregate_metrics("active_sessions", AggregationType.MAX, last_hour),
            "requests_per_minute": self.aggregate_metrics("requests", AggregationType.COUNT, current_time - 60),
            "avg_response_time": self.aggregate_metrics("response_time", AggregationType.AVERAGE, last_hour),
            "error_rate": self.aggregate_metrics("errors", AggregationType.COUNT, last_hour),
            "cpu_usage": self.aggregate_metrics("cpu_usage", AggregationType.AVERAGE, current_time - 300),
            "memory_usage": self.aggregate_metrics("memory_usage", AggregationType.AVERAGE, current_time - 300)
        }
    
    def export_report(self, report: Report, format: str = "json") -> str:
        """Export report to specified format"""
        if format == "json":
            return json.dumps(asdict(report), indent=2, default=str)
        elif format == "csv":
            # Simple CSV export
            lines = ["name,value,type,timestamp"]
            for metric in report.metrics:
                lines.append(f"{metric.name},{metric.value},{metric.metric_type.value},{metric.timestamp}")
            return "\n".join(lines)
        else:
            return str(report)
    
    def cleanup_old_metrics(self, days: int = 30):
        """Clean up old metrics"""
        cutoff_time = time.time() - (days * 24 * 3600)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM metrics WHERE timestamp < ?", (cutoff_time,))
            deleted_count = cursor.rowcount
        
        self.logger.info(f"Cleaned up {deleted_count} old metrics")
        return deleted_count

# Global analytics instance
analytics = EnterpriseAnalytics()

def record_performance_metric(name: str, value: float, tags: Dict[str, str] = None):
    """Record performance metric"""
    analytics.record_metric(name, value, MetricType.PERFORMANCE, tags)

def record_usage_metric(name: str, value: float, tags: Dict[str, str] = None):
    """Record usage metric"""
    analytics.record_metric(name, value, MetricType.USAGE, tags)

def record_system_metric(name: str, value: float, tags: Dict[str, str] = None):
    """Record system metric"""
    analytics.record_metric(name, value, MetricType.SYSTEM, tags)

def get_performance_report(hours: int = 24) -> Report:
    """Get performance report"""
    return analytics.generate_performance_report(hours)

def get_usage_report(days: int = 7) -> Report:
    """Get usage report"""
    return analytics.generate_usage_report(days)