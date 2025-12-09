#!/usr/bin/env python3
"""
QRD - Quality Regression Detector
Zazna regresije v kakovosti in zmogljivosti sistema
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

class RegressionType(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Types of regression"""
    PERFORMANCE = "performance"
    ACCURACY = "accuracy"
    RELIABILITY = "reliability"
    EFFICIENCY = "efficiency"
    QUALITY = "quality"
    STABILITY = "stability"

class RegressionSeverity(Enum):
    """Regression severity levels"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"

class DetectionMethod(Enum):
    """Regression detection methods"""
    STATISTICAL = "statistical"
    THRESHOLD = "threshold"
    TREND_ANALYSIS = "trend_analysis"
    CHANGE_POINT = "change_point"
    ANOMALY_DETECTION = "anomaly_detection"

@dataclass
class QualityMetric:
    """Quality metric data point"""
    timestamp: float
    metric_name: str
    component_id: str
    value: float
    baseline: float
    threshold_lower: Optional[float]
    threshold_upper: Optional[float]
    metadata: Dict[str, Any]

@dataclass
class RegressionEvent:
    """Quality regression event"""
    event_id: str
    regression_type: RegressionType
    component_id: str
    metric_name: str
    detection_method: DetectionMethod
    severity: RegressionSeverity
    regression_score: float
    baseline_value: float
    current_value: float
    change_percentage: float
    detected_at: float
    first_occurrence: float
    description: str
    root_cause_analysis: Dict[str, Any]
    recommended_actions: List[str]

@dataclass
class QualityBaseline:
    """Quality baseline for comparison"""
    baseline_id: str
    component_id: str
    metric_name: str
    baseline_value: float
    confidence_interval: Tuple[float, float]
    sample_size: int
    calculation_method: str
    created_at: float
    valid_until: Optional[float]

@dataclass
class RegressionReport:
    """Comprehensive regression analysis report"""
    report_id: str
    analysis_period: Tuple[float, float]
    total_regressions: int
    regressions_by_severity: Dict[str, int]
    regressions_by_type: Dict[str, int]
    affected_components: List[str]
    regression_events: List[RegressionEvent]
    trend_analysis: Dict[str, Any]
    recommendations: List[str]
    created_at: float

class QRD:
    """Quality Regression Detector"""
    
    def __init__(self, config_path: str = "mia/data/quality_control/qrd_config.json"):
        self.config_path = config_path
        self.qrd_dir = Path("mia/data/quality_control/qrd")
        self.qrd_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.QRD")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Quality tracking
        self.quality_metrics: Dict[str, deque] = {}  # component_id -> metrics
        self.quality_baselines: Dict[str, QualityBaseline] = {}
        self.regression_events: Dict[str, RegressionEvent] = {}
        self.regression_reports: Dict[str, RegressionReport] = {}
        
        # Detection state
        self.detection_active = False
        self.detection_thread: Optional[threading.Thread] = None
        self.detection_interval = self.config.get("detection_interval", 300)  # 5 minutes
        
        # Registered metrics
        self.registered_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Detection methods
        self.detection_methods = {
            DetectionMethod.STATISTICAL: self._statistical_detection,
            DetectionMethod.THRESHOLD: self._threshold_detection,
            DetectionMethod.TREND_ANALYSIS: self._trend_analysis_detection,
            DetectionMethod.CHANGE_POINT: self._change_point_detection,
            DetectionMethod.ANOMALY_DETECTION: self._anomaly_detection
        }
        
        self.logger.info("🔍 QRD (Quality Regression Detector) initialized")
    
    def _load_configuration(self) -> Dict:
        """Load QRD configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load QRD config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default QRD configuration"""
        config = {
            "enabled": True,
            "detection_interval": 300,  # 5 minutes
            "baseline_window": 7200,    # 2 hours for baseline calculation
            "detection_window": 1800,   # 30 minutes for regression detection
            "max_metrics_per_component": 1000,
            "regression_thresholds": {
                "minor": 0.05,      # 5% degradation
                "moderate": 0.15,   # 15% degradation
                "major": 0.30,      # 30% degradation
                "critical": 0.50    # 50% degradation
            },
            "detection_methods": {
                "statistical": {
                    "enabled": True,
                    "confidence_level": 0.95,
                    "min_samples": 10
                },
                "threshold": {
                    "enabled": True,
                    "dynamic_thresholds": True
                },
                "trend_analysis": {
                    "enabled": True,
                    "trend_window": 3600,  # 1 hour
                    "significance_threshold": 0.05
                },
                "change_point": {
                    "enabled": True,
                    "sensitivity": 2.0
                },
                "anomaly_detection": {
                    "enabled": True,
                    "anomaly_threshold": 2.5
                }
            },
            "metric_types": {
                "performance": {
                    "response_time": {"lower_is_better": True, "unit": "seconds"},
                    "throughput": {"lower_is_better": False, "unit": "ops/sec"},
                    "latency": {"lower_is_better": True, "unit": "ms"}
                },
                "accuracy": {
                    "precision": {"lower_is_better": False, "unit": "ratio"},
                    "recall": {"lower_is_better": False, "unit": "ratio"},
                    "f1_score": {"lower_is_better": False, "unit": "ratio"}
                },
                "reliability": {
                    "uptime": {"lower_is_better": False, "unit": "percentage"},
                    "error_rate": {"lower_is_better": True, "unit": "percentage"},
                    "success_rate": {"lower_is_better": False, "unit": "percentage"}
                },
                "efficiency": {
                    "cpu_usage": {"lower_is_better": True, "unit": "percentage"},
                    "memory_usage": {"lower_is_better": True, "unit": "percentage"},
                    "energy_consumption": {"lower_is_better": True, "unit": "watts"}
                }
            },
            "alerting": {
                "enabled": True,
                "alert_on_severity": ["major", "critical"],
                "notification_cooldown": 1800  # 30 minutes
            },
            "auto_baseline_update": {
                "enabled": True,
                "update_frequency": 86400,  # 24 hours
                "min_stable_period": 3600   # 1 hour of stable metrics
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def register_metric(self, component_id: str, metric_name: str, metric_type: RegressionType,
                       baseline_value: float = None, thresholds: Dict[str, float] = None):
        """Register quality metric for monitoring"""
        try:
            metric_key = f"{component_id}_{metric_name}"
            
            self.registered_metrics[metric_key] = {
                "component_id": component_id,
                "metric_name": metric_name,
                "metric_type": metric_type,
                "baseline_value": baseline_value,
                "thresholds": thresholds or {},
                "registered_at": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            }
            
            # Initialize metrics storage
            if component_id not in self.quality_metrics:
                max_metrics = self.config.get("max_metrics_per_component", 1000)
                self.quality_metrics[component_id] = deque(maxlen=max_metrics)
            
            # Create baseline if provided
            if baseline_value is not None:
                self._create_baseline(component_id, metric_name, baseline_value)
            
            self.logger.info(f"🔍 Registered quality metric: {component_id}.{metric_name} ({metric_type.value})")
            
        except Exception as e:
            self.logger.error(f"Failed to register metric: {e}")
    
    def record_quality_metric(self, component_id: str, metric_name: str, value: float,
                            metadata: Dict[str, Any] = None):
        """Record quality metric value"""
        try:
            metric_key = f"{component_id}_{metric_name}"
            
            if metric_key not in self.registered_metrics:
                self.logger.warning(f"Metric not registered: {metric_key}")
                return
            
            # Get baseline and thresholds
            baseline = self._get_baseline(component_id, metric_name)
            thresholds = self.registered_metrics[metric_key].get("thresholds", {})
            
            # Create quality metric
            quality_metric = QualityMetric(
                timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                metric_name=metric_name,
                component_id=component_id,
                value=value,
                baseline=baseline,
                threshold_lower=thresholds.get("lower"),
                threshold_upper=thresholds.get("upper"),
                metadata=metadata or {}
            )
            
            # Store metric
            if component_id not in self.quality_metrics:
                max_metrics = self.config.get("max_metrics_per_component", 1000)
                self.quality_metrics[component_id] = deque(maxlen=max_metrics)
            
            self.quality_metrics[component_id].append(quality_metric)
            
            # Immediate regression check
            self._check_immediate_regression(quality_metric)
            
        except Exception as e:
            self.logger.error(f"Failed to record quality metric: {e}")
    
    def start_detection(self):
        """Start regression detection"""
        try:
            if self.detection_active:
                return
            
            self.detection_active = True
            self.detection_thread = threading.Thread(
                target=self._detection_loop,
                daemon=True
            )
            self.detection_thread.start()
            
            self.logger.info("🔍 QRD detection started")
            
        except Exception as e:
            self.logger.error(f"Failed to start detection: {e}")
    
    def stop_detection(self):
        """Stop regression detection"""
        try:
            self.detection_active = False
            
            if self.detection_thread:
                self.detection_thread.join(timeout=5.0)
            
            self.logger.info("🔍 QRD detection stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop detection: {e}")
    
    def _detection_loop(self):
        """Main detection loop"""
        while self.detection_active:
            try:
                # Run regression detection for all components
                for component_id in self.quality_metrics:
                    self._detect_component_regressions(component_id)
                
                # Update baselines if enabled
                if self.config.get("auto_baseline_update", {}).get("enabled", True):
                    self._update_baselines()
                
                time.sleep(self.detection_interval)
                
            except Exception as e:
                self.logger.error(f"Error in detection loop: {e}")
                time.sleep(self.detection_interval)
    
    def _detect_component_regressions(self, component_id: str):
        """Detect regressions for component"""
        try:
            if component_id not in self.quality_metrics:
                return
            
            metrics = list(self.quality_metrics[component_id])
            if not metrics:
                return
            
            # Filter recent metrics
            current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            detection_window = self.config.get("detection_window", 1800)
            recent_metrics = [m for m in metrics if current_time - m.timestamp <= detection_window]
            
            if len(recent_metrics) < 3:  # Need minimum metrics
                return
            
            # Group by metric name
            metric_groups = {}
            for metric in recent_metrics:
                if metric.metric_name not in metric_groups:
                    metric_groups[metric.metric_name] = []
                metric_groups[metric.metric_name].append(metric)
            
            # Run detection methods for each metric
            for metric_name, metric_list in metric_groups.items():
                if len(metric_list) < 3:
                    continue
                
                # Run all enabled detection methods
                for method, detection_function in self.detection_methods.items():
                    method_config = self.config.get("detection_methods", {}).get(method.value, {})
                    if method_config.get("enabled", True):
                        regression = detection_function(component_id, metric_name, metric_list)
                        if regression:
                            self.regression_events[regression.event_id] = regression
                            self._handle_regression_event(regression)
            
        except Exception as e:
            self.logger.error(f"Failed to detect component regressions: {e}")
    
    def _statistical_detection(self, component_id: str, metric_name: str,
                             metrics: List[QualityMetric]) -> Optional[RegressionEvent]:
        """Statistical regression detection"""
        try:
            method_config = self.config.get("detection_methods", {}).get("statistical", {})
            confidence_level = method_config.get("confidence_level", 0.95)
            min_samples = method_config.get("min_samples", 10)
            
            if len(metrics) < min_samples:
                return None
            
            # Get baseline
            baseline = self._get_baseline(component_id, metric_name)
            if baseline is None:
                return None
            
            # Calculate current statistics
            current_values = [m.value for m in metrics]
            current_mean = statistics.mean(current_values)
            
            if len(current_values) > 1:
                current_std = statistics.stdev(current_values)
            else:
                return None
            
            # Statistical test (simplified t-test)
            if current_std > 0:
                t_statistic = abs(current_mean - baseline) / (current_std / (len(current_values) ** 0.5))
                
                # Critical value for 95% confidence (approximation)
                critical_value = 1.96
                
                if t_statistic > critical_value:
                    # Calculate regression metrics
                    change_percentage = ((current_mean - baseline) / baseline) * 100 if baseline != 0 else 0
                    regression_score = min(1.0, abs(change_percentage) / 100.0)
                    severity = self._calculate_severity(abs(change_percentage))
                    
                    # Determine regression type
                    metric_key = f"{component_id}_{metric_name}"
                    regression_type = self.registered_metrics.get(metric_key, {}).get("metric_type", RegressionType.QUALITY)
                    
                    return self._create_regression_event(
                        component_id, metric_name, regression_type,
                        DetectionMethod.STATISTICAL, severity,
                        regression_score, baseline, current_mean, change_percentage,
                        f"Statistical regression detected: {change_percentage:.1f}% change from baseline"
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Statistical detection failed: {e}")
            return None
    
    def _threshold_detection(self, component_id: str, metric_name: str,
                           metrics: List[QualityMetric]) -> Optional[RegressionEvent]:
        """Threshold-based regression detection"""
        try:
            if not metrics:
                return None
            
            latest_metric = metrics[-1]
            
            # Check against thresholds
            if latest_metric.threshold_lower is not None and latest_metric.value < latest_metric.threshold_lower:
                change_percentage = ((latest_metric.value - latest_metric.baseline) / latest_metric.baseline) * 100 if latest_metric.baseline != 0 else 0
                regression_score = abs(change_percentage) / 100.0
                severity = self._calculate_severity(abs(change_percentage))
                
                metric_key = f"{component_id}_{metric_name}"
                regression_type = self.registered_metrics.get(metric_key, {}).get("metric_type", RegressionType.QUALITY)
                
                return self._create_regression_event(
                    component_id, metric_name, regression_type,
                    DetectionMethod.THRESHOLD, severity,
                    regression_score, latest_metric.baseline, latest_metric.value, change_percentage,
                    f"Lower threshold violation: {latest_metric.value} < {latest_metric.threshold_lower}"
                )
            
            if latest_metric.threshold_upper is not None and latest_metric.value > latest_metric.threshold_upper:
                change_percentage = ((latest_metric.value - latest_metric.baseline) / latest_metric.baseline) * 100 if latest_metric.baseline != 0 else 0
                regression_score = abs(change_percentage) / 100.0
                severity = self._calculate_severity(abs(change_percentage))
                
                metric_key = f"{component_id}_{metric_name}"
                regression_type = self.registered_metrics.get(metric_key, {}).get("metric_type", RegressionType.QUALITY)
                
                return self._create_regression_event(
                    component_id, metric_name, regression_type,
                    DetectionMethod.THRESHOLD, severity,
                    regression_score, latest_metric.baseline, latest_metric.value, change_percentage,
                    f"Upper threshold violation: {latest_metric.value} > {latest_metric.threshold_upper}"
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Threshold detection failed: {e}")
            return None
    
    def _trend_analysis_detection(self, component_id: str, metric_name: str,
                                metrics: List[QualityMetric]) -> Optional[RegressionEvent]:
        """Trend analysis regression detection"""
        try:
            if len(metrics) < 5:  # Need minimum points for trend
                return None
            
            # Sort by timestamp
            sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
            values = [m.value for m in sorted_metrics]
            
            # Calculate linear trend
            n = len(values)
            x = list(range(n))
            
            # Simple linear regression
            sum_x = sum(x)
            sum_y = sum(values)
            sum_xy = sum(x[i] * values[i] for i in range(n))
            sum_x2 = sum(x[i] * x[i] for i in range(n))
            
            try:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            except ZeroDivisionError:
                return None
            
            # Check if trend indicates regression
            baseline = self._get_baseline(component_id, metric_name)
            if baseline is None:
                return None
            
            # Determine if metric should increase or decrease for better quality
            metric_key = f"{component_id}_{metric_name}"
            metric_info = self.registered_metrics.get(metric_key, {})
            
            # For now, assume negative slope is bad (can be configured per metric)
            if abs(slope) > 0.1:  # Significant trend
                current_value = values[-1]
                change_percentage = ((current_value - baseline) / baseline) * 100 if baseline != 0 else 0
                regression_score = min(1.0, abs(slope) * 10)  # Scale slope to score
                severity = self._calculate_severity(abs(change_percentage))
                
                regression_type = metric_info.get("metric_type", RegressionType.QUALITY)
                
                return self._create_regression_event(
                    component_id, metric_name, regression_type,
                    DetectionMethod.TREND_ANALYSIS, severity,
                    regression_score, baseline, current_value, change_percentage,
                    f"Negative trend detected: slope = {slope:.4f}"
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Trend analysis detection failed: {e}")
            return None
    
    def _change_point_detection(self, component_id: str, metric_name: str,
                              metrics: List[QualityMetric]) -> Optional[RegressionEvent]:
        """Change point regression detection"""
        try:
            if len(metrics) < 10:  # Need sufficient data
                return None
            
            values = [m.value for m in metrics]
            
            # Simple change point detection using variance
            mid_point = len(values) // 2
            first_half = values[:mid_point]
            second_half = values[mid_point:]
            
            if len(first_half) > 1 and len(second_half) > 1:
                first_mean = statistics.mean(first_half)
                second_mean = statistics.mean(second_half)
                
                # Check for significant change
                if first_mean != 0:
                    change_percentage = ((second_mean - first_mean) / first_mean) * 100
                    
                    if abs(change_percentage) > 20:  # 20% change threshold
                        baseline = self._get_baseline(component_id, metric_name)
                        regression_score = min(1.0, abs(change_percentage) / 100.0)
                        severity = self._calculate_severity(abs(change_percentage))
                        
                        metric_key = f"{component_id}_{metric_name}"
                        regression_type = self.registered_metrics.get(metric_key, {}).get("metric_type", RegressionType.QUALITY)
                        
                        return self._create_regression_event(
                            component_id, metric_name, regression_type,
                            DetectionMethod.CHANGE_POINT, severity,
                            regression_score, baseline or first_mean, second_mean, change_percentage,
                            f"Change point detected: {change_percentage:.1f}% change"
                        )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Change point detection failed: {e}")
            return None
    
    def _anomaly_detection(self, component_id: str, metric_name: str,
                         metrics: List[QualityMetric]) -> Optional[RegressionEvent]:
        """Anomaly-based regression detection"""
        try:
            if len(metrics) < 5:
                return None
            
            values = [m.value for m in metrics]
            
            # Calculate z-scores for anomaly detection
            mean_val = statistics.mean(values)
            
            if len(values) > 1:
                std_val = statistics.stdev(values)
            else:
                return None
            
            if std_val == 0:
                return None
            
            # Check latest values for anomalies
            anomaly_threshold = self.config.get("detection_methods", {}).get("anomaly_detection", {}).get("anomaly_threshold", 2.5)
            
            recent_values = values[-3:]  # Check last 3 values
            anomaly_count = 0
            
            for value in recent_values:
                z_score = abs(value - mean_val) / std_val
                if z_score > anomaly_threshold:
                    anomaly_count += 1
            
            # If multiple recent anomalies, consider it a regression
            if anomaly_count >= 2:
                baseline = self._get_baseline(component_id, metric_name)
                current_value = values[-1]
                change_percentage = ((current_value - baseline) / baseline) * 100 if baseline and baseline != 0 else 0
                regression_score = min(1.0, anomaly_count / 3.0)
                severity = self._calculate_severity(abs(change_percentage))
                
                metric_key = f"{component_id}_{metric_name}"
                regression_type = self.registered_metrics.get(metric_key, {}).get("metric_type", RegressionType.QUALITY)
                
                return self._create_regression_event(
                    component_id, metric_name, regression_type,
                    DetectionMethod.ANOMALY_DETECTION, severity,
                    regression_score, baseline or mean_val, current_value, change_percentage,
                    f"Multiple anomalies detected: {anomaly_count} out of 3 recent values"
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return None
    
    def _calculate_severity(self, change_percentage: float) -> RegressionSeverity:
        """Calculate regression severity based on change percentage"""
        try:
            thresholds = self.config.get("regression_thresholds", {})
            
            abs_change = abs(change_percentage)
            
            if abs_change >= thresholds.get("critical", 50.0):
                return RegressionSeverity.CRITICAL
            elif abs_change >= thresholds.get("major", 30.0):
                return RegressionSeverity.MAJOR
            elif abs_change >= thresholds.get("moderate", 15.0):
                return RegressionSeverity.MODERATE
            else:
                return RegressionSeverity.MINOR
            
        except Exception as e:
            self.logger.error(f"Failed to calculate severity: {e}")
            return RegressionSeverity.MINOR
    
    def _create_regression_event(self, component_id: str, metric_name: str,
                               regression_type: RegressionType, detection_method: DetectionMethod,
                               severity: RegressionSeverity, regression_score: float,
                               baseline_value: float, current_value: float,
                               change_percentage: float, description: str) -> RegressionEvent:
        """Create regression event"""
        try:
            event_id = f"regression_{component_id}_{metric_name}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}"
            
            # Generate root cause analysis
            root_cause_analysis = self._analyze_root_cause(
                component_id, metric_name, regression_type, current_value, baseline_value
            )
            
            # Generate recommended actions
            recommended_actions = self._generate_regression_recommendations(
                regression_type, severity, change_percentage
            )
            
            return RegressionEvent(
                event_id=event_id,
                regression_type=regression_type,
                component_id=component_id,
                metric_name=metric_name,
                detection_method=detection_method,
                severity=severity,
                regression_score=regression_score,
                baseline_value=baseline_value,
                current_value=current_value,
                change_percentage=change_percentage,
                detected_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                first_occurrence=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,  # Could be refined with historical analysis
                description=description,
                root_cause_analysis=root_cause_analysis,
                recommended_actions=recommended_actions
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create regression event: {e}")
            return None
    
    def _analyze_root_cause(self, component_id: str, metric_name: str,
                          regression_type: RegressionType, current_value: float,
                          baseline_value: float) -> Dict[str, Any]:
        """Analyze potential root causes of regression"""
        try:
            analysis = {
                "potential_causes": [],
                "correlation_analysis": {},
                "temporal_analysis": {},
                "confidence": 0.5
            }
            
            # Add potential causes based on regression type
            if regression_type == RegressionType.PERFORMANCE:
                analysis["potential_causes"].extend([
                    "Increased system load",
                    "Resource contention",
                    "Algorithm inefficiency",
                    "Network latency",
                    "Database performance issues"
                ])
            
            elif regression_type == RegressionType.ACCURACY:
                analysis["potential_causes"].extend([
                    "Model drift",
                    "Data quality issues",
                    "Feature distribution changes",
                    "Training data staleness",
                    "Hyperparameter degradation"
                ])
            
            elif regression_type == RegressionType.RELIABILITY:
                analysis["potential_causes"].extend([
                    "System instability",
                    "Hardware failures",
                    "Software bugs",
                    "Configuration changes",
                    "External dependencies"
                ])
            
            # Add severity-based analysis
            change_magnitude = abs(current_value - baseline_value)
            if change_magnitude > baseline_value * 0.5:  # >50% change
                analysis["potential_causes"].append("Catastrophic failure or major system change")
                analysis["confidence"] = 0.8
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze root cause: {e}")
            return {"error": str(e)}
    
    def _generate_regression_recommendations(self, regression_type: RegressionType,
                                           severity: RegressionSeverity,
                                           change_percentage: float) -> List[str]:
        """Generate recommendations for regression"""
        try:
            recommendations = []
            
            # Severity-based recommendations
            if severity == RegressionSeverity.CRITICAL:
                recommendations.extend([
                    "IMMEDIATE ACTION REQUIRED",
                    "Consider rolling back recent changes",
                    "Activate incident response procedures",
                    "Notify stakeholders immediately"
                ])
            
            elif severity == RegressionSeverity.MAJOR:
                recommendations.extend([
                    "High priority investigation required",
                    "Review recent deployments and changes",
                    "Consider temporary mitigation measures"
                ])
            
            # Type-based recommendations
            if regression_type == RegressionType.PERFORMANCE:
                recommendations.extend([
                    "Review system resource utilization",
                    "Check for performance bottlenecks",
                    "Analyze recent code changes for inefficiencies",
                    "Consider performance optimization strategies"
                ])
            
            elif regression_type == RegressionType.ACCURACY:
                recommendations.extend([
                    "Validate input data quality",
                    "Check for model drift",
                    "Review feature engineering pipeline",
                    "Consider model retraining"
                ])
            
            elif regression_type == RegressionType.RELIABILITY:
                recommendations.extend([
                    "Check system health and error logs",
                    "Verify external dependencies",
                    "Review recent configuration changes",
                    "Implement additional monitoring"
                ])
            
            # General recommendations
            recommendations.extend([
                "Document the regression for future reference",
                "Monitor closely for further degradation",
                "Update alerting thresholds if necessary"
            ])
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
            return ["Investigate regression and take appropriate action"]
    
    def _handle_regression_event(self, regression: RegressionEvent):
        """Handle detected regression event"""
        try:
            # Log regression
            severity_emoji = {
                RegressionSeverity.CRITICAL: "🚨",
                RegressionSeverity.MAJOR: "⚠️",
                RegressionSeverity.MODERATE: "⚡",
                RegressionSeverity.MINOR: "📊"
            }
            
            emoji = severity_emoji.get(regression.severity, "📊")
            
            log_message = (f"{emoji} Quality regression detected: "
                         f"{regression.component_id}.{regression.metric_name} "
                         f"({regression.severity.value}) - {regression.change_percentage:.1f}% change")
            
            if regression.severity == RegressionSeverity.CRITICAL:
                self.logger.critical(log_message)
            elif regression.severity == RegressionSeverity.MAJOR:
                self.logger.error(log_message)
            elif regression.severity == RegressionSeverity.MODERATE:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
            
            # Check alerting configuration
            alerting_config = self.config.get("alerting", {})
            if (alerting_config.get("enabled", True) and
                regression.severity.value in alerting_config.get("alert_on_severity", ["major", "critical"])):
                
                # Could integrate with external alerting system here
                self.logger.info(f"Alert triggered for regression: {regression.event_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to handle regression event: {e}")
    
    def _check_immediate_regression(self, metric: QualityMetric):
        """Check for immediate regression on new metric"""
        try:
            # Simple immediate check against baseline
            if metric.baseline is not None and metric.baseline != 0:
                change_percentage = ((metric.value - metric.baseline) / metric.baseline) * 100
                
                # Check for significant immediate regression
                if abs(change_percentage) > 25:  # 25% immediate change threshold
                    severity = self._calculate_severity(abs(change_percentage))
                    
                    if severity in [RegressionSeverity.MAJOR, RegressionSeverity.CRITICAL]:
                        metric_key = f"{metric.component_id}_{metric.metric_name}"
                        regression_type = self.registered_metrics.get(metric_key, {}).get("metric_type", RegressionType.QUALITY)
                        
                        regression = self._create_regression_event(
                            metric.component_id, metric.metric_name, regression_type,
                            DetectionMethod.THRESHOLD, severity,
                            abs(change_percentage) / 100.0, metric.baseline, metric.value,
                            change_percentage, f"Immediate regression detected: {change_percentage:.1f}% change"
                        )
                        
                        if regression:
                            self.regression_events[regression.event_id] = regression
                            self._handle_regression_event(regression)
            
        except Exception as e:
            self.logger.error(f"Failed to check immediate regression: {e}")
    
    def _get_baseline(self, component_id: str, metric_name: str) -> Optional[float]:
        """Get baseline value for metric"""
        try:
            baseline_key = f"{component_id}_{metric_name}"
            
            # Check if baseline exists
            for baseline in self.quality_baselines.values():
                if (baseline.component_id == component_id and
                    baseline.metric_name == metric_name and
                    (baseline.valid_until is None or baseline.valid_until > self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)):
                    return baseline.baseline_value
            
            # Check registered metric for baseline
            metric_key = f"{component_id}_{metric_name}"
            if metric_key in self.registered_metrics:
                return self.registered_metrics[metric_key].get("baseline_value")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get baseline: {e}")
            return None
    
    def _create_baseline(self, component_id: str, metric_name: str, baseline_value: float):
        """Create quality baseline"""
        try:
            baseline_id = f"baseline_{component_id}_{metric_name}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}"
            
            baseline = QualityBaseline(
                baseline_id=baseline_id,
                component_id=component_id,
                metric_name=metric_name,
                baseline_value=baseline_value,
                confidence_interval=(baseline_value * 0.95, baseline_value * 1.05),  # ±5%
                sample_size=1,
                calculation_method="manual",
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                valid_until=None
            )
            
            self.quality_baselines[baseline_id] = baseline
            
        except Exception as e:
            self.logger.error(f"Failed to create baseline: {e}")
    
    def _update_baselines(self):
        """Update baselines automatically"""
        try:
            update_frequency = self.config.get("auto_baseline_update", {}).get("update_frequency", 86400)
            min_stable_period = self.config.get("auto_baseline_update", {}).get("min_stable_period", 3600)
            
            current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # Check each registered metric for baseline updates
            for metric_key, metric_info in self.registered_metrics.items():
                component_id = metric_info["component_id"]
                metric_name = metric_info["metric_name"]
                
                # Check if baseline needs update
                last_baseline_time = 0
                for baseline in self.quality_baselines.values():
                    if (baseline.component_id == component_id and
                        baseline.metric_name == metric_name):
                        last_baseline_time = max(last_baseline_time, baseline.created_at)
                
                if current_time - last_baseline_time > update_frequency:
                    # Calculate new baseline from recent stable data
                    self._calculate_automatic_baseline(component_id, metric_name, min_stable_period)
            
        except Exception as e:
            self.logger.error(f"Failed to update baselines: {e}")
    
    def _calculate_automatic_baseline(self, component_id: str, metric_name: str, stable_period: float):
        """Calculate automatic baseline from stable data"""
        try:
            if component_id not in self.quality_metrics:
                return
            
            metrics = list(self.quality_metrics[component_id])
            current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # Get recent stable metrics
            stable_metrics = [
                m for m in metrics
                if (m.metric_name == metric_name and
                    current_time - m.timestamp <= stable_period)
            ]
            
            if len(stable_metrics) < 10:  # Need minimum data points
                return
            
            # Check for stability (low variance)
            values = [m.value for m in stable_metrics]
            mean_val = statistics.mean(values)
            
            if len(values) > 1:
                std_val = statistics.stdev(values)
                cv = std_val / mean_val if mean_val != 0 else float('inf')
                
                # Only update baseline if data is stable (CV < 10%)
                if cv < 0.1:
                    baseline_id = f"baseline_{component_id}_{metric_name}_{int(current_time)}"
                    
                    baseline = QualityBaseline(
                        baseline_id=baseline_id,
                        component_id=component_id,
                        metric_name=metric_name,
                        baseline_value=mean_val,
                        confidence_interval=(mean_val - 2*std_val, mean_val + 2*std_val),
                        sample_size=len(values),
                        calculation_method="automatic",
                        created_at=current_time,
                        valid_until=current_time + 86400  # Valid for 24 hours
                    )
                    
                    self.quality_baselines[baseline_id] = baseline
                    
                    self.logger.info(f"📊 Updated baseline for {component_id}.{metric_name}: {mean_val:.3f}")
            
        except Exception as e:
            self.logger.error(f"Failed to calculate automatic baseline: {e}")
    
    def generate_regression_report(self, start_time: float = None, end_time: float = None) -> str:
        """Generate comprehensive regression report"""
        try:
            if start_time is None:
                start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - 86400  # Last 24 hours
            if end_time is None:
                end_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # Filter regressions by time period
            period_regressions = [
                regression for regression in self.regression_events.values()
                if start_time <= regression.detected_at <= end_time
            ]
            
            # Analyze regressions
            total_regressions = len(period_regressions)
            
            regressions_by_severity = {}
            for severity in RegressionSeverity:
                regressions_by_severity[severity.value] = len([
                    r for r in period_regressions if r.severity == severity
                ])
            
            regressions_by_type = {}
            for reg_type in RegressionType:
                regressions_by_type[reg_type.value] = len([
                    r for r in period_regressions if r.regression_type == reg_type
                ])
            
            affected_components = list(set(r.component_id for r in period_regressions))
            
            # Generate trend analysis
            trend_analysis = self._analyze_regression_trends(period_regressions)
            
            # Generate recommendations
            recommendations = self._generate_report_recommendations(period_regressions)
            
            # Create report
            report = RegressionReport(
                report_id=f"regression_report_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                analysis_period=(start_time, end_time),
                total_regressions=total_regressions,
                regressions_by_severity=regressions_by_severity,
                regressions_by_type=regressions_by_type,
                affected_components=affected_components,
                regression_events=period_regressions,
                trend_analysis=trend_analysis,
                recommendations=recommendations,
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            )
            
            # Store report
            self.regression_reports[report.report_id] = report
            
            self.logger.info(f"📊 Generated regression report: {total_regressions} regressions in period")
            
            return report.report_id
            
        except Exception as e:
            self.logger.error(f"Failed to generate regression report: {e}")
            return ""
    
    def _analyze_regression_trends(self, regressions: List[RegressionEvent]) -> Dict[str, Any]:
        """Analyze trends in regressions"""
        try:
            if not regressions:
                return {}
            
            # Sort by detection time
            sorted_regressions = sorted(regressions, key=lambda r: r.detected_at)
            
            # Analyze temporal patterns
            detection_times = [r.detected_at for r in sorted_regressions]
            time_intervals = [detection_times[i+1] - detection_times[i] for i in range(len(detection_times)-1)]
            
            trend_analysis = {
                "temporal_pattern": {
                    "total_duration": detection_times[-1] - detection_times[0] if len(detection_times) > 1 else 0,
                    "average_interval": statistics.mean(time_intervals) if time_intervals else 0,
                    "regression_frequency": len(regressions) / max(1, (detection_times[-1] - detection_times[0]) / 3600)  # per hour
                },
                "severity_trend": {},
                "component_impact": {}
            }
            
            # Analyze severity trends
            severity_over_time = [(r.detected_at, r.severity.value) for r in sorted_regressions]
            trend_analysis["severity_trend"] = {
                "pattern": "increasing" if len(severity_over_time) > 1 else "stable",
                "most_common": max(set(s[1] for s in severity_over_time), key=lambda x: [s[1] for s in severity_over_time].count(x)) if severity_over_time else None
            }
            
            # Analyze component impact
            component_counts = {}
            for regression in regressions:
                component_counts[regression.component_id] = component_counts.get(regression.component_id, 0) + 1
            
            trend_analysis["component_impact"] = {
                "most_affected": max(component_counts.items(), key=lambda x: x[1]) if component_counts else None,
                "component_distribution": component_counts
            }
            
            return trend_analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze regression trends: {e}")
            return {}
    
    def _generate_report_recommendations(self, regressions: List[RegressionEvent]) -> List[str]:
        """Generate recommendations for regression report"""
        try:
            recommendations = []
            
            if not regressions:
                recommendations.append("No regressions detected in the analysis period")
                return recommendations
            
            # Count by severity
            critical_count = len([r for r in regressions if r.severity == RegressionSeverity.CRITICAL])
            major_count = len([r for r in regressions if r.severity == RegressionSeverity.MAJOR])
            
            if critical_count > 0:
                recommendations.append(f"URGENT: {critical_count} critical regressions require immediate attention")
            
            if major_count > 0:
                recommendations.append(f"HIGH PRIORITY: {major_count} major regressions need investigation")
            
            # Component-specific recommendations
            component_counts = {}
            for regression in regressions:
                component_counts[regression.component_id] = component_counts.get(regression.component_id, 0) + 1
            
            if component_counts:
                most_affected = max(component_counts.items(), key=lambda x: x[1])
                if most_affected[1] > 1:
                    recommendations.append(f"Focus investigation on component '{most_affected[0]}' with {most_affected[1]} regressions")
            
            # Type-specific recommendations
            type_counts = {}
            for regression in regressions:
                type_counts[regression.regression_type.value] = type_counts.get(regression.regression_type.value, 0) + 1
            
            if type_counts:
                most_common_type = max(type_counts.items(), key=lambda x: x[1])
                recommendations.append(f"Primary regression type: {most_common_type[0]} ({most_common_type[1]} occurrences)")
            
            # General recommendations
            recommendations.extend([
                "Review recent system changes and deployments",
                "Strengthen monitoring for affected components",
                "Consider implementing additional quality gates",
                "Update regression detection thresholds if necessary"
            ])
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate report recommendations: {e}")
            return ["Review regressions and take appropriate action"]
    
    def get_regression_events(self, component_id: str = None, severity: RegressionSeverity = None,
                            start_time: float = None) -> List[RegressionEvent]:
        """Get regression events with optional filtering"""
        try:
            events = []
            
            for event in self.regression_events.values():
                # Filter by component
                if component_id and event.component_id != component_id:
                    continue
                
                # Filter by severity
                if severity and event.severity != severity:
                    continue
                
                # Filter by time
                if start_time and event.detected_at < start_time:
                    continue
                
                events.append(event)
            
            # Sort by detection time (newest first)
            events.sort(key=lambda e: e.detected_at, reverse=True)
            
            return events
            
        except Exception as e:
            self.logger.error(f"Failed to get regression events: {e}")
            return []
    
    def get_qrd_status(self) -> Dict[str, Any]:
        """Get QRD status"""
        try:
            return {
                "enabled": self.config.get("enabled", True),
                "detection_active": self.detection_active,
                "detection_interval": self.detection_interval,
                "registered_metrics": len(self.registered_metrics),
                "quality_baselines": len(self.quality_baselines),
                "total_metrics": sum(len(metrics) for metrics in self.quality_metrics.values()),
                "regression_events": len(self.regression_events),
                "regression_reports": len(self.regression_reports),
                "detection_methods": list(self.detection_methods.keys())
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get QRD status: {e}")
            return {"error": str(e)}

# Global instance
qrd = QRD()