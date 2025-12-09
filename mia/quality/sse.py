#!/usr/bin/env python3
"""
SSE - Stability Score Evaluator
Ocenjuje stabilnost sistemskih komponent in procesov
"""

import os
import json
import logging
import time
import statistics
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import deque

class StabilityLevel(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Stability levels"""
    CRITICAL = "critical"
    UNSTABLE = "unstable"
    MODERATE = "moderate"
    STABLE = "stable"
    HIGHLY_STABLE = "highly_stable"

class ComponentType(Enum):
    """Component types for stability evaluation"""
    SYSTEM = "system"
    MODULE = "module"
    PROCESS = "process"
    SERVICE = "service"
    MEMORY = "memory"
    NETWORK = "network"
    STORAGE = "storage"

@dataclass
class StabilityMetric:
    """Stability metric data point"""
    timestamp: float
    component_id: str
    component_type: ComponentType
    metric_name: str
    value: float
    baseline: float
    deviation: float
    stability_score: float

@dataclass
class StabilityReport:
    """Stability evaluation report"""
    report_id: str
    component_id: str
    component_type: ComponentType
    evaluation_period: float
    overall_stability: StabilityLevel
    stability_score: float
    metrics: List[StabilityMetric]
    anomalies: List[Dict[str, Any]]
    trends: Dict[str, Any]
    recommendations: List[str]
    created_at: float

class SSE:
    """Stability Score Evaluator"""
    
    def __init__(self, config_path: str = "mia/data/quality_control/sse_config.json"):
        self.config_path = config_path
        self.sse_dir = Path("mia/data/quality_control/sse")
        self.sse_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.SSE")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Stability tracking
        self.component_metrics: Dict[str, deque] = {}
        self.component_baselines: Dict[str, Dict[str, float]] = {}
        self.stability_reports: Dict[str, StabilityReport] = {}
        
        # Evaluation state
        self.evaluation_active = False
        self.evaluation_thread: Optional[threading.Thread] = None
        self.evaluation_interval = self.config.get("evaluation_interval", 60)  # 1 minute
        
        # Registered components
        self.registered_components: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("📊 SSE (Stability Score Evaluator) initialized")
    
    def _load_configuration(self) -> Dict:
        """Load SSE configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load SSE config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default SSE configuration"""
        config = {
            "enabled": True,
            "evaluation_interval": 60,  # seconds
            "baseline_window": 3600,  # 1 hour for baseline calculation
            "stability_window": 1800,  # 30 minutes for stability evaluation
            "max_metrics_per_component": 1000,
            "stability_thresholds": {
                "highly_stable": 0.95,
                "stable": 0.85,
                "moderate": 0.70,
                "unstable": 0.50,
                "critical": 0.30
            },
            "deviation_thresholds": {
                "low": 0.05,    # 5%
                "medium": 0.15, # 15%
                "high": 0.30,   # 30%
                "critical": 0.50 # 50%
            },
            "anomaly_detection": {
                "enabled": True,
                "sensitivity": 2.0,  # Standard deviations
                "min_samples": 10
            },
            "trend_analysis": {
                "enabled": True,
                "trend_window": 3600,  # 1 hour
                "significance_threshold": 0.05
            },
            "component_weights": {
                "system": 1.0,
                "module": 0.8,
                "process": 0.6,
                "service": 0.7,
                "memory": 0.9,
                "network": 0.8,
                "storage": 0.7
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def register_component(self, component_id: str, component_type: ComponentType,
                          metrics: List[str], baseline_values: Dict[str, float] = None):
        """Register component for stability monitoring"""
        try:
            self.registered_components[component_id] = {
                "type": component_type,
                "metrics": metrics,
                "registered_at": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                "baseline_values": baseline_values or {}
            }
            
            # Initialize metrics storage
            if component_id not in self.component_metrics:
                max_metrics = self.config.get("max_metrics_per_component", 1000)
                self.component_metrics[component_id] = deque(maxlen=max_metrics)
            
            # Initialize baselines
            if component_id not in self.component_baselines:
                self.component_baselines[component_id] = baseline_values or {}
            
            self.logger.info(f"📊 Registered component for stability monitoring: {component_id} ({component_type.value})")
            
        except Exception as e:
            self.logger.error(f"Failed to register component: {e}")
    
    def record_metric(self, component_id: str, metric_name: str, value: float):
        """Record stability metric for component"""
        try:
            if component_id not in self.registered_components:
                self.logger.warning(f"Component not registered: {component_id}")
                return
            
            component_info = self.registered_components[component_id]
            component_type = component_info["type"]
            
            # Get or calculate baseline
            baseline = self._get_baseline(component_id, metric_name, value)
            
            # Calculate deviation
            if baseline > 0:
                deviation = abs(value - baseline) / baseline
            else:
                deviation = 0.0
            
            # Calculate stability score for this metric
            stability_score = self._calculate_metric_stability_score(deviation)
            
            # Create metric object
            metric = StabilityMetric(
                timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                component_id=component_id,
                component_type=component_type,
                metric_name=metric_name,
                value=value,
                baseline=baseline,
                deviation=deviation,
                stability_score=stability_score
            )
            
            # Store metric
            self.component_metrics[component_id].append(metric)
            
            # Update baseline if needed
            self._update_baseline(component_id, metric_name, value)
            
        except Exception as e:
            self.logger.error(f"Failed to record metric: {e}")
    
    def start_evaluation(self):
        """Start stability evaluation"""
        try:
            if self.evaluation_active:
                return
            
            self.evaluation_active = True
            self.evaluation_thread = threading.Thread(
                target=self._evaluation_loop,
                daemon=True
            )
            self.evaluation_thread.start()
            
            self.logger.info("📊 SSE evaluation started")
            
        except Exception as e:
            self.logger.error(f"Failed to start evaluation: {e}")
    
    def stop_evaluation(self):
        """Stop stability evaluation"""
        try:
            self.evaluation_active = False
            
            if self.evaluation_thread:
                self.evaluation_thread.join(timeout=5.0)
            
            self.logger.info("📊 SSE evaluation stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop evaluation: {e}")
    
    def _evaluation_loop(self):
        """Main evaluation loop"""
        while self.evaluation_active:
            try:
                # Evaluate all registered components
                for component_id in self.registered_components:
                    self._evaluate_component_stability(component_id)
                
                time.sleep(self.evaluation_interval)
                
            except Exception as e:
                self.logger.error(f"Error in evaluation loop: {e}")
                time.sleep(self.evaluation_interval)
    
    def _evaluate_component_stability(self, component_id: str):
        """Evaluate stability of a component"""
        try:
            if component_id not in self.component_metrics:
                return
            
            metrics = list(self.component_metrics[component_id])
            if not metrics:
                return
            
            # Filter recent metrics
            current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            stability_window = self.config.get("stability_window", 1800)
            recent_metrics = [m for m in metrics if current_time - m.timestamp <= stability_window]
            
            if len(recent_metrics) < 3:  # Need minimum metrics
                return
            
            # Calculate overall stability score
            stability_scores = [m.stability_score for m in recent_metrics]
            overall_score = statistics.mean(stability_scores)
            
            # Determine stability level
            stability_level = self._determine_stability_level(overall_score)
            
            # Detect anomalies
            anomalies = self._detect_anomalies(recent_metrics)
            
            # Analyze trends
            trends = self._analyze_trends(recent_metrics)
            
            # Generate recommendations
            recommendations = self._generate_stability_recommendations(
                component_id, stability_level, anomalies, trends
            )
            
            # Create stability report
            report = StabilityReport(
                report_id=f"stability_{component_id}_{int(current_time)}",
                component_id=component_id,
                component_type=self.registered_components[component_id]["type"],
                evaluation_period=stability_window,
                overall_stability=stability_level,
                stability_score=overall_score,
                metrics=recent_metrics,
                anomalies=anomalies,
                trends=trends,
                recommendations=recommendations,
                created_at=current_time
            )
            
            # Store report
            self.stability_reports[report.report_id] = report
            
            # Log significant stability changes
            if stability_level in [StabilityLevel.CRITICAL, StabilityLevel.UNSTABLE]:
                self.logger.warning(f"🚨 Stability issue detected: {component_id} - {stability_level.value} ({overall_score:.3f})")
            elif stability_level == StabilityLevel.HIGHLY_STABLE:
                self.logger.debug(f"✅ High stability: {component_id} ({overall_score:.3f})")
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate component stability: {e}")
    
    def _get_baseline(self, component_id: str, metric_name: str, current_value: float) -> float:
        """Get baseline value for metric"""
        try:
            # Check if baseline exists
            if (component_id in self.component_baselines and 
                metric_name in self.component_baselines[component_id]):
                return self.component_baselines[component_id][metric_name]
            
            # Calculate baseline from historical data
            if component_id in self.component_metrics:
                metrics = list(self.component_metrics[component_id])
                metric_values = [m.value for m in metrics if m.metric_name == metric_name]
                
                if len(metric_values) >= 10:
                    # Use median as baseline (more robust than mean)
                    baseline = statistics.median(metric_values)
                    
                    # Store baseline
                    if component_id not in self.component_baselines:
                        self.component_baselines[component_id] = {}
                    self.component_baselines[component_id][metric_name] = baseline
                    
                    return baseline
            
            # Use current value as initial baseline
            return current_value
            
        except Exception as e:
            self.logger.error(f"Failed to get baseline: {e}")
            return current_value
    
    def _update_baseline(self, component_id: str, metric_name: str, new_value: float):
        """Update baseline with exponential moving average"""
        try:
            if component_id not in self.component_baselines:
                self.component_baselines[component_id] = {}
            
            current_baseline = self.component_baselines[component_id].get(metric_name, new_value)
            
            # Exponential moving average with alpha = 0.1
            alpha = 0.1
            updated_baseline = alpha * new_value + (1 - alpha) * current_baseline
            
            self.component_baselines[component_id][metric_name] = updated_baseline
            
        except Exception as e:
            self.logger.error(f"Failed to update baseline: {e}")
    
    def _calculate_metric_stability_score(self, deviation: float) -> float:
        """Calculate stability score based on deviation"""
        try:
            thresholds = self.config.get("deviation_thresholds", {})
            
            if deviation <= thresholds.get("low", 0.05):
                return 1.0  # Highly stable
            elif deviation <= thresholds.get("medium", 0.15):
                return 0.8  # Stable
            elif deviation <= thresholds.get("high", 0.30):
                return 0.6  # Moderate
            elif deviation <= thresholds.get("critical", 0.50):
                return 0.3  # Unstable
            else:
                return 0.1  # Critical
            
        except Exception as e:
            self.logger.error(f"Failed to calculate stability score: {e}")
            return 0.5
    
    def _determine_stability_level(self, stability_score: float) -> StabilityLevel:
        """Determine stability level from score"""
        try:
            thresholds = self.config.get("stability_thresholds", {})
            
            if stability_score >= thresholds.get("highly_stable", 0.95):
                return StabilityLevel.HIGHLY_STABLE
            elif stability_score >= thresholds.get("stable", 0.85):
                return StabilityLevel.STABLE
            elif stability_score >= thresholds.get("moderate", 0.70):
                return StabilityLevel.MODERATE
            elif stability_score >= thresholds.get("unstable", 0.50):
                return StabilityLevel.UNSTABLE
            else:
                return StabilityLevel.CRITICAL
            
        except Exception as e:
            self.logger.error(f"Failed to determine stability level: {e}")
            return StabilityLevel.MODERATE
    
    def _detect_anomalies(self, metrics: List[StabilityMetric]) -> List[Dict[str, Any]]:
        """Detect anomalies in metrics"""
        try:
            if not self.config.get("anomaly_detection", {}).get("enabled", True):
                return []
            
            anomalies = []
            sensitivity = self.config.get("anomaly_detection", {}).get("sensitivity", 2.0)
            min_samples = self.config.get("anomaly_detection", {}).get("min_samples", 10)
            
            # Group metrics by name
            metric_groups = {}
            for metric in metrics:
                if metric.metric_name not in metric_groups:
                    metric_groups[metric.metric_name] = []
                metric_groups[metric.metric_name].append(metric)
            
            # Detect anomalies in each metric group
            for metric_name, metric_list in metric_groups.items():
                if len(metric_list) < min_samples:
                    continue
                
                values = [m.value for m in metric_list]
                mean_val = statistics.mean(values)
                
                if len(values) > 1:
                    stdev_val = statistics.stdev(values)
                    
                    # Find outliers
                    for metric in metric_list:
                        if stdev_val > 0:
                            z_score = abs(metric.value - mean_val) / stdev_val
                            
                            if z_score > sensitivity:
                                anomalies.append({
                                    "timestamp": metric.timestamp,
                                    "metric_name": metric_name,
                                    "value": metric.value,
                                    "expected": mean_val,
                                    "z_score": z_score,
                                    "severity": "high" if z_score > sensitivity * 1.5 else "medium"
                                })
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Failed to detect anomalies: {e}")
            return []
    
    def _analyze_trends(self, metrics: List[StabilityMetric]) -> Dict[str, Any]:
        """Analyze trends in metrics"""
        try:
            if not self.config.get("trend_analysis", {}).get("enabled", True):
                return {}
            
            trends = {}
            
            # Group metrics by name
            metric_groups = {}
            for metric in metrics:
                if metric.metric_name not in metric_groups:
                    metric_groups[metric.metric_name] = []
                metric_groups[metric.metric_name].append(metric)
            
            # Analyze trend for each metric
            for metric_name, metric_list in metric_groups.items():
                if len(metric_list) < 5:  # Need minimum points for trend
                    continue
                
                # Sort by timestamp
                metric_list.sort(key=lambda m: m.timestamp)
                
                # Extract values and timestamps
                timestamps = [m.timestamp for m in metric_list]
                values = [m.value for m in metric_list]
                
                # Calculate linear trend
                try:
                    # Simple linear regression
                    n = len(values)
                    sum_x = sum(range(n))
                    sum_y = sum(values)
                    sum_xy = sum(i * values[i] for i in range(n))
                    sum_x2 = sum(i * i for i in range(n))
                    
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                    
                    # Determine trend direction
                    if abs(slope) < 0.001:
                        trend_direction = "stable"
                    elif slope > 0:
                        trend_direction = "increasing"
                    else:
                        trend_direction = "decreasing"
                    
                    trends[metric_name] = {
                        "direction": trend_direction,
                        "slope": slope,
                        "strength": min(1.0, abs(slope) * 1000),  # Normalize strength
                        "data_points": n
                    }
                    
                except ZeroDivisionError:
                    trends[metric_name] = {
                        "direction": "stable",
                        "slope": 0.0,
                        "strength": 0.0,
                        "data_points": n
                    }
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Failed to analyze trends: {e}")
            return {}
    
    def _generate_stability_recommendations(self, component_id: str, stability_level: StabilityLevel,
                                          anomalies: List[Dict[str, Any]], trends: Dict[str, Any]) -> List[str]:
        """Generate stability recommendations"""
        try:
            recommendations = []
            
            # Recommendations based on stability level
            if stability_level == StabilityLevel.CRITICAL:
                recommendations.append(f"CRITICAL: Component {component_id} requires immediate attention")
                recommendations.append("Consider restarting the component or checking for resource issues")
                recommendations.append("Review recent changes that might have affected stability")
            
            elif stability_level == StabilityLevel.UNSTABLE:
                recommendations.append(f"Component {component_id} shows instability")
                recommendations.append("Monitor closely and consider preventive measures")
                recommendations.append("Check for resource constraints or configuration issues")
            
            elif stability_level == StabilityLevel.MODERATE:
                recommendations.append(f"Component {component_id} stability is moderate")
                recommendations.append("Consider optimization to improve stability")
            
            # Recommendations based on anomalies
            if anomalies:
                high_severity_anomalies = [a for a in anomalies if a.get("severity") == "high"]
                if high_severity_anomalies:
                    recommendations.append(f"High-severity anomalies detected in {len(high_severity_anomalies)} metrics")
                    recommendations.append("Investigate root cause of anomalous behavior")
                
                recommendations.append(f"Total anomalies detected: {len(anomalies)}")
            
            # Recommendations based on trends
            for metric_name, trend_info in trends.items():
                if trend_info["direction"] == "increasing" and trend_info["strength"] > 0.5:
                    recommendations.append(f"Increasing trend detected in {metric_name} - monitor for potential issues")
                elif trend_info["direction"] == "decreasing" and trend_info["strength"] > 0.5:
                    recommendations.append(f"Decreasing trend detected in {metric_name} - investigate cause")
            
            # General recommendations
            if not recommendations:
                if stability_level in [StabilityLevel.STABLE, StabilityLevel.HIGHLY_STABLE]:
                    recommendations.append(f"Component {component_id} is operating stably")
                    recommendations.append("Continue current monitoring practices")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
            return [f"Error generating recommendations for {component_id}"]
    
    def get_component_stability(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Get current stability status for component"""
        try:
            if component_id not in self.registered_components:
                return None
            
            # Get recent metrics
            if component_id not in self.component_metrics:
                return None
            
            metrics = list(self.component_metrics[component_id])
            if not metrics:
                return None
            
            # Calculate current stability
            recent_metrics = metrics[-10:]  # Last 10 metrics
            stability_scores = [m.stability_score for m in recent_metrics]
            current_score = statistics.mean(stability_scores)
            stability_level = self._determine_stability_level(current_score)
            
            return {
                "component_id": component_id,
                "component_type": self.registered_components[component_id]["type"].value,
                "stability_level": stability_level.value,
                "stability_score": current_score,
                "metrics_count": len(metrics),
                "last_updated": metrics[-1].timestamp if metrics else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get component stability: {e}")
            return None
    
    def get_stability_report(self, report_id: str) -> Optional[StabilityReport]:
        """Get stability report"""
        return self.stability_reports.get(report_id)
    
    def get_sse_status(self) -> Dict[str, Any]:
        """Get SSE status"""
        try:
            return {
                "enabled": self.config.get("enabled", True),
                "evaluation_active": self.evaluation_active,
                "evaluation_interval": self.evaluation_interval,
                "registered_components": len(self.registered_components),
                "total_metrics": sum(len(metrics) for metrics in self.component_metrics.values()),
                "stability_reports": len(self.stability_reports),
                "component_types": list(set(
                    comp["type"].value for comp in self.registered_components.values()
                ))
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get SSE status: {e}")
            return {"error": str(e)}
    
    def evaluate_stability(self) -> Dict[str, Any]:
        """Evaluate system stability"""
        try:
            # Calculate overall stability score
            if self.stability_reports:
                recent_reports = list(self.stability_reports.values())[-10:]  # Last 10 reports
                avg_stability = sum(r.get("stability_score", 0) for r in recent_reports) / len(recent_reports)
            else:
                avg_stability = 0.0
            
            # Calculate component stability
            component_stability = {}
            for comp_id, metrics in self.component_metrics.items():
                if metrics:
                    recent_metrics = metrics[-5:]  # Last 5 metrics
                    comp_stability = sum(m.get("stability_score", 0) for m in recent_metrics) / len(recent_metrics)
                    component_stability[comp_id] = comp_stability
                else:
                    component_stability[comp_id] = 0.0
            
            # Determine stability level
            if avg_stability >= 0.9:
                stability_level = "excellent"
            elif avg_stability >= 0.7:
                stability_level = "good"
            elif avg_stability >= 0.5:
                stability_level = "fair"
            else:
                stability_level = "poor"
            
            return {
                "overall_stability_score": avg_stability,
                "stability_level": stability_level,
                "component_stability": component_stability,
                "total_reports": len(self.stability_reports),
                "evaluation_active": self.evaluation_active,
                "last_evaluation": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            }
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate stability: {e}")
            return {
                "error": str(e),
                "overall_stability_score": 0.0,
                "stability_level": "unknown"
            }

# Global instance
sse = SSE()