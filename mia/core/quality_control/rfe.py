#!/usr/bin/env python3
"""
RFE - Resource Forecasting Engine
Napoveduje potrebe po resursih in optimizira alokacijo
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
import psutil

class ResourceType(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Resource types"""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    DISK = "disk"
    NETWORK = "network"
    CUSTOM = "custom"

class ForecastHorizon(Enum):
    """Forecast time horizons"""
    SHORT_TERM = "short_term"    # 1-5 minutes
    MEDIUM_TERM = "medium_term"  # 5-60 minutes
    LONG_TERM = "long_term"      # 1-24 hours

class ForecastMethod(Enum):
    """Forecasting methods"""
    LINEAR_REGRESSION = "linear_regression"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    MOVING_AVERAGE = "moving_average"
    ARIMA = "arima"
    NEURAL_NETWORK = "neural_network"

@dataclass
class ResourceUsagePoint:
    """Resource usage data point"""
    timestamp: float
    resource_type: ResourceType
    component_id: str
    usage_value: float
    capacity: float
    utilization: float
    metadata: Dict[str, Any]

@dataclass
class ResourceForecast:
    """Resource usage forecast"""
    forecast_id: str
    resource_type: ResourceType
    component_id: str
    horizon: ForecastHorizon
    method: ForecastMethod
    predicted_values: List[Tuple[float, float]]  # (timestamp, predicted_value)
    confidence_intervals: List[Tuple[float, float, float]]  # (timestamp, lower, upper)
    accuracy_score: float
    created_at: float
    valid_until: float

@dataclass
class ResourceAlert:
    """Resource usage alert"""
    alert_id: str
    resource_type: ResourceType
    component_id: str
    alert_type: str  # "threshold", "forecast", "anomaly"
    severity: str    # "low", "medium", "high", "critical"
    message: str
    predicted_time: Optional[float]
    recommended_actions: List[str]
    created_at: float

@dataclass
class OptimizationRecommendation:
    """Resource optimization recommendation"""
    recommendation_id: str
    resource_type: ResourceType
    component_id: str
    optimization_type: str
    description: str
    expected_savings: Dict[str, float]
    implementation_effort: str
    priority: int
    created_at: float

class RFE:
    """Resource Forecasting Engine"""
    
    def __init__(self, config_path: str = "mia/data/quality_control/rfe_config.json"):
        self.config_path = config_path
        self.rfe_dir = Path("mia/data/quality_control/rfe")
        self.rfe_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.RFE")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Resource tracking
        self.resource_history: Dict[str, deque] = {}  # component_id -> usage points
        self.forecasts: Dict[str, ResourceForecast] = {}
        self.alerts: Dict[str, ResourceAlert] = {}
        self.recommendations: Dict[str, OptimizationRecommendation] = {}
        
        # Forecasting state
        self.forecasting_active = False
        self.forecasting_thread: Optional[threading.Thread] = None
        self.forecasting_interval = self.config.get("forecasting_interval", 300)  # 5 minutes
        
        # Registered components
        self.registered_components: Dict[str, Dict[str, Any]] = {}
        
        # Forecasting models
        self.forecasting_models = {
            ForecastMethod.LINEAR_REGRESSION: self._linear_regression_forecast,
            ForecastMethod.EXPONENTIAL_SMOOTHING: self._exponential_smoothing_forecast,
            ForecastMethod.MOVING_AVERAGE: self._moving_average_forecast,
            ForecastMethod.ARIMA: self._arima_forecast
        }
        
        self.logger.info("📈 RFE (Resource Forecasting Engine) initialized")
    
    def _load_configuration(self) -> Dict:
        """Load RFE configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load RFE config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default RFE configuration"""
        config = {
            "enabled": True,
            "forecasting_interval": 300,  # 5 minutes
            "history_retention": 86400,   # 24 hours
            "max_history_points": 1000,
            "forecast_horizons": {
                "short_term": {"duration": 300, "points": 10},    # 5 minutes, 10 points
                "medium_term": {"duration": 3600, "points": 20},  # 1 hour, 20 points
                "long_term": {"duration": 86400, "points": 48}    # 24 hours, 48 points
            },
            "forecasting_methods": {
                "linear_regression": {"enabled": True, "min_points": 10},
                "exponential_smoothing": {"enabled": True, "alpha": 0.3},
                "moving_average": {"enabled": True, "window": 5},
                "arima": {"enabled": False, "order": [1, 1, 1]}
            },
            "alert_thresholds": {
                "cpu": {"warning": 70.0, "critical": 85.0},
                "memory": {"warning": 80.0, "critical": 90.0},
                "gpu": {"warning": 75.0, "critical": 90.0},
                "disk": {"warning": 85.0, "critical": 95.0},
                "network": {"warning": 80.0, "critical": 95.0}
            },
            "optimization_targets": {
                "cpu_efficiency": 0.7,
                "memory_efficiency": 0.8,
                "cost_reduction": 0.2,
                "performance_improvement": 0.15
            },
            "auto_scaling": {
                "enabled": False,
                "scale_up_threshold": 80.0,
                "scale_down_threshold": 30.0,
                "cooldown_period": 300
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def register_component(self, component_id: str, resource_types: List[ResourceType],
                          capacity_limits: Dict[str, float] = None):
        """Register component for resource monitoring"""
        try:
            self.registered_components[component_id] = {
                "resource_types": resource_types,
                "capacity_limits": capacity_limits or {},
                "registered_at": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            }
            
            # Initialize history storage
            if component_id not in self.resource_history:
                max_points = self.config.get("max_history_points", 1000)
                self.resource_history[component_id] = deque(maxlen=max_points)
            
            self.logger.info(f"📈 Registered component for resource forecasting: {component_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to register component: {e}")
    
    def record_resource_usage(self, component_id: str, resource_type: ResourceType,
                            usage_value: float, capacity: float = None,
                            metadata: Dict[str, Any] = None):
        """Record resource usage data point"""
        try:
            if component_id not in self.registered_components:
                self.logger.warning(f"Component not registered: {component_id}")
                return
            
            # Calculate utilization
            if capacity is None:
                capacity = self.registered_components[component_id].get("capacity_limits", {}).get(resource_type.value, 100.0)
            
            utilization = (usage_value / capacity) * 100.0 if capacity > 0 else 0.0
            
            # Create usage point
            usage_point = ResourceUsagePoint(
                timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                resource_type=resource_type,
                component_id=component_id,
                usage_value=usage_value,
                capacity=capacity,
                utilization=utilization,
                metadata=metadata or {}
            )
            
            # Store usage point
            self.resource_history[component_id].append(usage_point)
            
            # Check for immediate alerts
            self._check_resource_alerts(usage_point)
            
        except Exception as e:
            self.logger.error(f"Failed to record resource usage: {e}")
    
    def start_forecasting(self):
        """Start resource forecasting"""
        try:
            if self.forecasting_active:
                return
            
            self.forecasting_active = True
            self.forecasting_thread = threading.Thread(
                target=self._forecasting_loop,
                daemon=True
            )
            self.forecasting_thread.start()
            
            self.logger.info("📈 RFE forecasting started")
            
        except Exception as e:
            self.logger.error(f"Failed to start forecasting: {e}")
    
    def stop_forecasting(self):
        """Stop resource forecasting"""
        try:
            self.forecasting_active = False
            
            if self.forecasting_thread:
                self.forecasting_thread.join(timeout=5.0)
            
            self.logger.info("📈 RFE forecasting stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop forecasting: {e}")
    
    def _forecasting_loop(self):
        """Main forecasting loop"""
        while self.forecasting_active:
            try:
                # Generate forecasts for all registered components
                for component_id in self.registered_components:
                    self._generate_component_forecasts(component_id)
                
                # Clean up old forecasts
                self._cleanup_old_forecasts()
                
                # Generate optimization recommendations
                self._generate_optimization_recommendations()
                
                time.sleep(self.forecasting_interval)
                
            except Exception as e:
                self.logger.error(f"Error in forecasting loop: {e}")
                time.sleep(self.forecasting_interval)
    
    def _generate_component_forecasts(self, component_id: str):
        """Generate forecasts for component"""
        try:
            if component_id not in self.resource_history:
                return
            
            usage_points = list(self.resource_history[component_id])
            if len(usage_points) < 5:  # Need minimum data points
                return
            
            # Group by resource type
            resource_groups = {}
            for point in usage_points:
                resource_type = point.resource_type
                if resource_type not in resource_groups:
                    resource_groups[resource_type] = []
                resource_groups[resource_type].append(point)
            
            # Generate forecasts for each resource type
            for resource_type, points in resource_groups.items():
                if len(points) < 5:
                    continue
                
                # Generate forecasts for different horizons
                for horizon in ForecastHorizon:
                    forecast = self._generate_forecast(component_id, resource_type, points, horizon)
                    if forecast:
                        self.forecasts[forecast.forecast_id] = forecast
            
        except Exception as e:
            self.logger.error(f"Failed to generate component forecasts: {e}")
    
    def _generate_forecast(self, component_id: str, resource_type: ResourceType,
                         usage_points: List[ResourceUsagePoint], horizon: ForecastHorizon) -> Optional[ResourceForecast]:
        """Generate forecast for specific resource and horizon"""
        try:
            # Get horizon configuration
            horizon_config = self.config.get("forecast_horizons", {}).get(horizon.value, {})
            duration = horizon_config.get("duration", 3600)
            num_points = horizon_config.get("points", 20)
            
            # Prepare data
            timestamps = [p.timestamp for p in usage_points]
            values = [p.usage_value for p in usage_points]
            
            if len(values) < 3:
                return None
            
            # Choose forecasting method based on data characteristics
            method = self._select_forecasting_method(values)
            
            # Generate forecast
            forecasting_function = self.forecasting_models.get(method)
            if not forecasting_function:
                method = ForecastMethod.MOVING_AVERAGE
                forecasting_function = self.forecasting_models[method]
            
            predicted_values, confidence_intervals = forecasting_function(
                timestamps, values, duration, num_points
            )
            
            # Calculate accuracy score (simplified)
            accuracy_score = self._calculate_forecast_accuracy(values, method)
            
            # Create forecast
            forecast = ResourceForecast(
                forecast_id=f"forecast_{component_id}_{resource_type.value}_{horizon.value}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                resource_type=resource_type,
                component_id=component_id,
                horizon=horizon,
                method=method,
                predicted_values=predicted_values,
                confidence_intervals=confidence_intervals,
                accuracy_score=accuracy_score,
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                valid_until=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 + duration
            )
            
            # Check for forecast-based alerts
            self._check_forecast_alerts(forecast)
            
            return forecast
            
        except Exception as e:
            self.logger.error(f"Failed to generate forecast: {e}")
            return None
    
    def _select_forecasting_method(self, values: List[float]) -> ForecastMethod:
        """Select appropriate forecasting method based on data characteristics"""
        try:
            # Simple heuristics for method selection
            if len(values) < 10:
                return ForecastMethod.MOVING_AVERAGE
            
            # Check for trend
            if len(values) >= 10:
                recent_values = values[-10:]
                older_values = values[-20:-10] if len(values) >= 20 else values[:-10]
                
                if len(older_values) > 0:
                    recent_mean = statistics.mean(recent_values)
                    older_mean = statistics.mean(older_values)
                    
                    # If there's a clear trend, use linear regression
                    if abs(recent_mean - older_mean) / older_mean > 0.1:
                        return ForecastMethod.LINEAR_REGRESSION
            
            # Check for volatility
            if len(values) >= 5:
                std_dev = statistics.stdev(values)
                mean_val = statistics.mean(values)
                cv = std_dev / mean_val if mean_val > 0 else 0
                
                # If high volatility, use exponential smoothing
                if cv > 0.3:
                    return ForecastMethod.EXPONENTIAL_SMOOTHING
            
            # Default to moving average
            return ForecastMethod.MOVING_AVERAGE
            
        except Exception as e:
            self.logger.error(f"Failed to select forecasting method: {e}")
            return ForecastMethod.MOVING_AVERAGE
    
    def _linear_regression_forecast(self, timestamps: List[float], values: List[float],
                                  duration: float, num_points: int) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float, float]]]:
        """Linear regression forecasting"""
        try:
            if len(values) < 2:
                return [], []
            
            # Simple linear regression
            n = len(values)
            x = list(range(n))
            
            # Calculate slope and intercept
            sum_x = sum(x)
            sum_y = sum(values)
            sum_xy = sum(x[i] * values[i] for i in range(n))
            sum_x2 = sum(x[i] * x[i] for i in range(n))
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Generate predictions
            current_time = timestamps[-1]
            time_step = duration / num_points
            
            predicted_values = []
            confidence_intervals = []
            
            # Calculate residual standard error for confidence intervals
            residuals = [values[i] - (slope * x[i] + intercept) for i in range(n)]
            mse = sum(r * r for r in residuals) / max(1, n - 2)
            std_error = (mse ** 0.5)
            
            for i in range(num_points):
                future_time = current_time + (i + 1) * time_step
                future_x = n + i
                predicted_value = slope * future_x + intercept
                
                # Simple confidence interval (±2 standard errors)
                margin = 2 * std_error
                lower_bound = max(0, predicted_value - margin)
                upper_bound = predicted_value + margin
                
                predicted_values.append((future_time, predicted_value))
                confidence_intervals.append((future_time, lower_bound, upper_bound))
            
            return predicted_values, confidence_intervals
            
        except Exception as e:
            self.logger.error(f"Linear regression forecast failed: {e}")
            return [], []
    
    def _exponential_smoothing_forecast(self, timestamps: List[float], values: List[float],
                                      duration: float, num_points: int) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float, float]]]:
        """Exponential smoothing forecasting"""
        try:
            if not values:
                return [], []
            
            alpha = self.config.get("forecasting_methods", {}).get("exponential_smoothing", {}).get("alpha", 0.3)
            
            # Calculate smoothed values
            smoothed = [values[0]]
            for i in range(1, len(values)):
                smoothed_value = alpha * values[i] + (1 - alpha) * smoothed[i-1]
                smoothed.append(smoothed_value)
            
            # Generate predictions (constant forecast)
            last_smoothed = smoothed[-1]
            current_time = timestamps[-1]
            time_step = duration / num_points
            
            predicted_values = []
            confidence_intervals = []
            
            # Calculate prediction error for confidence intervals
            errors = [abs(values[i] - smoothed[i]) for i in range(len(values))]
            avg_error = statistics.mean(errors) if errors else 0
            
            for i in range(num_points):
                future_time = current_time + (i + 1) * time_step
                predicted_value = last_smoothed
                
                # Confidence interval widens with time
                margin = avg_error * (1 + i * 0.1)
                lower_bound = max(0, predicted_value - margin)
                upper_bound = predicted_value + margin
                
                predicted_values.append((future_time, predicted_value))
                confidence_intervals.append((future_time, lower_bound, upper_bound))
            
            return predicted_values, confidence_intervals
            
        except Exception as e:
            self.logger.error(f"Exponential smoothing forecast failed: {e}")
            return [], []
    
    def _moving_average_forecast(self, timestamps: List[float], values: List[float],
                               duration: float, num_points: int) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float, float]]]:
        """Moving average forecasting"""
        try:
            if not values:
                return [], []
            
            window = self.config.get("forecasting_methods", {}).get("moving_average", {}).get("window", 5)
            window = min(window, len(values))
            
            # Calculate moving average
            recent_values = values[-window:]
            avg_value = statistics.mean(recent_values)
            
            # Generate predictions (constant forecast)
            current_time = timestamps[-1]
            time_step = duration / num_points
            
            predicted_values = []
            confidence_intervals = []
            
            # Calculate standard deviation for confidence intervals
            std_dev = statistics.stdev(recent_values) if len(recent_values) > 1 else 0
            
            for i in range(num_points):
                future_time = current_time + (i + 1) * time_step
                predicted_value = avg_value
                
                # Confidence interval based on standard deviation
                margin = 2 * std_dev
                lower_bound = max(0, predicted_value - margin)
                upper_bound = predicted_value + margin
                
                predicted_values.append((future_time, predicted_value))
                confidence_intervals.append((future_time, lower_bound, upper_bound))
            
            return predicted_values, confidence_intervals
            
        except Exception as e:
            self.logger.error(f"Moving average forecast failed: {e}")
            return [], []
    
    def _arima_forecast(self, timestamps: List[float], values: List[float],
                      duration: float, num_points: int) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float, float]]]:
        """ARIMA forecasting (simplified implementation)"""
        try:
            # For now, fall back to linear regression
            return self._linear_regression_forecast(timestamps, values, duration, num_points)
            
        except Exception as e:
            self.logger.error(f"ARIMA forecast failed: {e}")
            return [], []
    
    def _calculate_forecast_accuracy(self, historical_values: List[float], method: ForecastMethod) -> float:
        """Calculate forecast accuracy score"""
        try:
            # Simplified accuracy calculation
            if len(historical_values) < 5:
                return 0.5
            
            # Use coefficient of variation as a proxy for predictability
            mean_val = statistics.mean(historical_values)
            std_val = statistics.stdev(historical_values) if len(historical_values) > 1 else 0
            
            if mean_val > 0:
                cv = std_val / mean_val
                # Lower coefficient of variation = higher accuracy
                accuracy = max(0.1, 1.0 - min(1.0, cv))
            else:
                accuracy = 0.5
            
            # Adjust based on method
            method_adjustments = {
                ForecastMethod.LINEAR_REGRESSION: 0.1,
                ForecastMethod.EXPONENTIAL_SMOOTHING: 0.05,
                ForecastMethod.MOVING_AVERAGE: 0.0,
                ForecastMethod.ARIMA: 0.15
            }
            
            accuracy += method_adjustments.get(method, 0.0)
            return min(1.0, accuracy)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate forecast accuracy: {e}")
            return 0.5
    
    def _check_resource_alerts(self, usage_point: ResourceUsagePoint):
        """Check for resource usage alerts"""
        try:
            thresholds = self.config.get("alert_thresholds", {}).get(usage_point.resource_type.value, {})
            
            warning_threshold = thresholds.get("warning", 80.0)
            critical_threshold = thresholds.get("critical", 90.0)
            
            if usage_point.utilization >= critical_threshold:
                self._create_alert(
                    usage_point.component_id,
                    usage_point.resource_type,
                    "threshold",
                    "critical",
                    f"Critical {usage_point.resource_type.value} usage: {usage_point.utilization:.1f}%"
                )
            elif usage_point.utilization >= warning_threshold:
                self._create_alert(
                    usage_point.component_id,
                    usage_point.resource_type,
                    "threshold",
                    "medium",
                    f"High {usage_point.resource_type.value} usage: {usage_point.utilization:.1f}%"
                )
            
        except Exception as e:
            self.logger.error(f"Failed to check resource alerts: {e}")
    
    def _check_forecast_alerts(self, forecast: ResourceForecast):
        """Check for forecast-based alerts"""
        try:
            if not forecast.predicted_values:
                return
            
            thresholds = self.config.get("alert_thresholds", {}).get(forecast.resource_type.value, {})
            critical_threshold = thresholds.get("critical", 90.0)
            
            # Check if any predicted value exceeds threshold
            for timestamp, predicted_value in forecast.predicted_values:
                # Convert to utilization if needed
                component_info = self.registered_components.get(forecast.component_id, {})
                capacity = component_info.get("capacity_limits", {}).get(forecast.resource_type.value, 100.0)
                predicted_utilization = (predicted_value / capacity) * 100.0 if capacity > 0 else predicted_value
                
                if predicted_utilization >= critical_threshold:
                    time_until = timestamp - self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                    self._create_alert(
                        forecast.component_id,
                        forecast.resource_type,
                        "forecast",
                        "high",
                        f"Predicted {forecast.resource_type.value} overload in {time_until/60:.1f} minutes",
                        predicted_time=timestamp
                    )
                    break  # Only create one alert per forecast
            
        except Exception as e:
            self.logger.error(f"Failed to check forecast alerts: {e}")
    
    def _create_alert(self, component_id: str, resource_type: ResourceType,
                     alert_type: str, severity: str, message: str,
                     predicted_time: Optional[float] = None):
        """Create resource alert"""
        try:
            alert_id = f"alert_{component_id}_{resource_type.value}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}"
            
            # Generate recommended actions
            recommended_actions = self._generate_alert_recommendations(
                resource_type, alert_type, severity
            )
            
            alert = ResourceAlert(
                alert_id=alert_id,
                resource_type=resource_type,
                component_id=component_id,
                alert_type=alert_type,
                severity=severity,
                message=message,
                predicted_time=predicted_time,
                recommended_actions=recommended_actions,
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            )
            
            self.alerts[alert_id] = alert
            
            # Log alert
            if severity == "critical":
                self.logger.critical(f"🚨 {message}")
            elif severity == "high":
                self.logger.error(f"⚠️ {message}")
            else:
                self.logger.warning(f"📊 {message}")
            
        except Exception as e:
            self.logger.error(f"Failed to create alert: {e}")
    
    def _generate_alert_recommendations(self, resource_type: ResourceType,
                                      alert_type: str, severity: str) -> List[str]:
        """Generate recommendations for alert"""
        try:
            recommendations = []
            
            if resource_type == ResourceType.CPU:
                recommendations.extend([
                    "Consider reducing batch sizes or concurrent operations",
                    "Review CPU-intensive processes for optimization opportunities",
                    "Consider scaling up CPU resources if sustained high usage"
                ])
            
            elif resource_type == ResourceType.MEMORY:
                recommendations.extend([
                    "Review memory usage patterns and optimize data structures",
                    "Consider implementing memory pooling or caching strategies",
                    "Monitor for memory leaks in long-running processes"
                ])
            
            elif resource_type == ResourceType.GPU:
                recommendations.extend([
                    "Optimize GPU memory usage and batch processing",
                    "Consider model quantization or precision reduction",
                    "Review GPU utilization patterns for efficiency improvements"
                ])
            
            elif resource_type == ResourceType.DISK:
                recommendations.extend([
                    "Clean up temporary files and logs",
                    "Consider data compression or archival strategies",
                    "Monitor disk I/O patterns for optimization"
                ])
            
            elif resource_type == ResourceType.NETWORK:
                recommendations.extend([
                    "Review network usage patterns and optimize data transfer",
                    "Consider data compression or caching strategies",
                    "Monitor for network bottlenecks or inefficient protocols"
                ])
            
            # Add severity-specific recommendations
            if severity in ["critical", "high"]:
                recommendations.insert(0, "Immediate action required - consider emergency scaling")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate alert recommendations: {e}")
            return ["Review resource usage and consider optimization"]
    
    def _generate_optimization_recommendations(self):
        """Generate resource optimization recommendations"""
        try:
            current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # Analyze resource usage patterns
            for component_id, usage_history in self.resource_history.items():
                if not usage_history:
                    continue
                
                # Get recent usage data
                recent_points = [p for p in usage_history if current_time - p.timestamp <= 3600]  # Last hour
                
                if len(recent_points) < 10:
                    continue
                
                # Group by resource type
                resource_groups = {}
                for point in recent_points:
                    if point.resource_type not in resource_groups:
                        resource_groups[point.resource_type] = []
                    resource_groups[point.resource_type].append(point)
                
                # Analyze each resource type
                for resource_type, points in resource_groups.items():
                    self._analyze_resource_optimization(component_id, resource_type, points)
            
        except Exception as e:
            self.logger.error(f"Failed to generate optimization recommendations: {e}")
    
    def _analyze_resource_optimization(self, component_id: str, resource_type: ResourceType,
                                     usage_points: List[ResourceUsagePoint]):
        """Analyze resource for optimization opportunities"""
        try:
            if len(usage_points) < 5:
                return
            
            utilizations = [p.utilization for p in usage_points]
            avg_utilization = statistics.mean(utilizations)
            max_utilization = max(utilizations)
            min_utilization = min(utilizations)
            
            # Check for optimization opportunities
            recommendations = []
            
            # Under-utilization
            if avg_utilization < 30.0 and max_utilization < 50.0:
                recommendations.append(self._create_optimization_recommendation(
                    component_id,
                    resource_type,
                    "under_utilization",
                    f"Low {resource_type.value} utilization detected (avg: {avg_utilization:.1f}%)",
                    {"resource_savings": avg_utilization * 0.5},
                    "low",
                    1
                ))
            
            # High variability
            if len(utilizations) > 1:
                std_dev = statistics.stdev(utilizations)
                cv = std_dev / avg_utilization if avg_utilization > 0 else 0
                
                if cv > 0.5:  # High coefficient of variation
                    recommendations.append(self._create_optimization_recommendation(
                        component_id,
                        resource_type,
                        "high_variability",
                        f"High {resource_type.value} usage variability detected (CV: {cv:.2f})",
                        {"efficiency_improvement": 0.2},
                        "medium",
                        2
                    ))
            
            # Peak usage optimization
            if max_utilization > 85.0 and avg_utilization < 60.0:
                recommendations.append(self._create_optimization_recommendation(
                    component_id,
                    resource_type,
                    "peak_optimization",
                    f"Peak {resource_type.value} usage optimization opportunity",
                    {"peak_reduction": (max_utilization - avg_utilization) * 0.3},
                    "medium",
                    3
                ))
            
            # Store recommendations
            for rec in recommendations:
                self.recommendations[rec.recommendation_id] = rec
            
        except Exception as e:
            self.logger.error(f"Failed to analyze resource optimization: {e}")
    
    def _create_optimization_recommendation(self, component_id: str, resource_type: ResourceType,
                                          optimization_type: str, description: str,
                                          expected_savings: Dict[str, float],
                                          implementation_effort: str, priority: int) -> OptimizationRecommendation:
        """Create optimization recommendation"""
        recommendation_id = f"opt_{component_id}_{resource_type.value}_{optimization_type}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}"
        
        return OptimizationRecommendation(
            recommendation_id=recommendation_id,
            resource_type=resource_type,
            component_id=component_id,
            optimization_type=optimization_type,
            description=description,
            expected_savings=expected_savings,
            implementation_effort=implementation_effort,
            priority=priority,
            created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        )
    
    def _cleanup_old_forecasts(self):
        """Clean up expired forecasts"""
        try:
            current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            expired_forecasts = [
                forecast_id for forecast_id, forecast in self.forecasts.items()
                if forecast.valid_until < current_time
            ]
            
            for forecast_id in expired_forecasts:
                del self.forecasts[forecast_id]
            
            if expired_forecasts:
                self.logger.debug(f"Cleaned up {len(expired_forecasts)} expired forecasts")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old forecasts: {e}")
    
    def get_resource_forecast(self, component_id: str, resource_type: ResourceType,
                            horizon: ForecastHorizon) -> Optional[ResourceForecast]:
        """Get resource forecast"""
        try:
            # Find matching forecast
            for forecast in self.forecasts.values():
                if (forecast.component_id == component_id and
                    forecast.resource_type == resource_type and
                    forecast.horizon == horizon and
                    forecast.valid_until > self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200):
                    return forecast
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get resource forecast: {e}")
            return None
    
    def get_active_alerts(self, component_id: str = None, severity: str = None) -> List[ResourceAlert]:
        """Get active resource alerts"""
        try:
            alerts = []
            current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            for alert in self.alerts.values():
                # Filter by component if specified
                if component_id and alert.component_id != component_id:
                    continue
                
                # Filter by severity if specified
                if severity and alert.severity != severity:
                    continue
                
                # Only include recent alerts (last 24 hours)
                if current_time - alert.created_at <= 86400:
                    alerts.append(alert)
            
            # Sort by severity and creation time
            severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            alerts.sort(key=lambda a: (severity_order.get(a.severity, 0), a.created_at), reverse=True)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Failed to get active alerts: {e}")
            return []
    
    def get_optimization_recommendations(self, component_id: str = None) -> List[OptimizationRecommendation]:
        """Get optimization recommendations"""
        try:
            recommendations = []
            
            for rec in self.recommendations.values():
                if component_id and rec.component_id != component_id:
                    continue
                
                recommendations.append(rec)
            
            # Sort by priority
            recommendations.sort(key=lambda r: r.priority, reverse=True)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to get optimization recommendations: {e}")
            return []
    
    def get_rfe_status(self) -> Dict[str, Any]:
        """Get RFE status"""
        try:
            return {
                "enabled": self.config.get("enabled", True),
                "forecasting_active": self.forecasting_active,
                "forecasting_interval": self.forecasting_interval,
                "registered_components": len(self.registered_components),
                "total_usage_points": sum(len(history) for history in self.resource_history.values()),
                "active_forecasts": len([f for f in self.forecasts.values() if f.valid_until > self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200]),
                "active_alerts": len(self.get_active_alerts()),
                "optimization_recommendations": len(self.recommendations),
                "forecasting_methods": list(self.forecasting_models.keys())
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get RFE status: {e}")
            return {"error": str(e)}

# Global instance
rfe = RFE()