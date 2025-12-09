#!/usr/bin/env python3
"""
PAE - Performance Advisory Engine
Analizira metrike iz QPM in predlaga optimizacije
"""

import os
import json
import logging
import time
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading

class OptimizationType(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Types of optimizations"""
    BATCH_SIZE = "batch_size"
    PRECISION = "precision"
    MEMORY_LAYOUT = "memory_layout"
    CPU_AFFINITY = "cpu_affinity"
    GPU_UTILIZATION = "gpu_utilization"
    IO_OPTIMIZATION = "io_optimization"
    CACHE_OPTIMIZATION = "cache_optimization"
    THREADING = "threading"

class Priority(Enum):
    """Optimization priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class PerformanceRegression:
    """Performance regression detection"""
    metric_name: str
    baseline_value: float
    current_value: float
    regression_percentage: float
    detected_at: float
    severity: Priority

@dataclass
class OptimizationRecommendation:
    """Optimization recommendation"""
    recommendation_id: str
    optimization_type: OptimizationType
    target_component: str
    description: str
    expected_improvement: float
    implementation_effort: str
    priority: Priority
    parameters: Dict[str, Any]
    created_at: float
    applied: bool

class PAE:
    """Performance Advisory Engine"""
    
    def __init__(self, config_path: str = "mia/data/quality_control/pae_config.json"):
        self.config_path = config_path
        self.pae_dir = Path("mia/data/quality_control/pae")
        self.pae_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.PAE")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Performance analysis
        self.performance_baselines: Dict[str, float] = {}
        self.regressions: List[PerformanceRegression] = []
        self.recommendations: List[OptimizationRecommendation] = []
        
        # Analysis state
        self.analysis_active = False
        self.analysis_thread: Optional[threading.Thread] = None
        self.analysis_interval = self.config.get("analysis_interval", 300)  # 5 minutes
        
        # Load existing data
        self._load_baselines()
        self._load_recommendations()
        
        self.logger.info("🔍 PAE (Performance Advisory Engine) initialized")
    
    def _load_configuration(self) -> Dict:
        """Load PAE configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load PAE config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default PAE configuration"""
        config = {
            "enabled": True,
            "analysis_interval": 300,  # 5 minutes
            "regression_threshold": 0.1,  # 10% performance drop
            "baseline_window": 3600,  # 1 hour for baseline calculation
            "min_samples": 10,  # Minimum samples for analysis
            "optimization_targets": {
                "cpu_usage": {"target": 70.0, "critical": 90.0},
                "memory_usage": {"target": 80.0, "critical": 95.0},
                "response_time": {"target": 1.0, "critical": 5.0},
                "throughput": {"target": 100.0, "critical": 50.0}
            },
            "optimization_strategies": {
                "batch_size": {
                    "enabled": True,
                    "min_batch": 1,
                    "max_batch": 64,
                    "step": 2
                },
                "precision": {
                    "enabled": True,
                    "options": ["fp32", "fp16", "int8"]
                },
                "memory_layout": {
                    "enabled": True,
                    "strategies": ["contiguous", "chunked", "streaming"]
                }
            },
            "auto_apply": {
                "enabled": False,
                "priority_threshold": "medium",
                "require_approval": True
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _load_baselines(self):
        """Load performance baselines"""
        try:
            baselines_file = self.pae_dir / "baselines.json"
            if baselines_file.exists():
                with open(baselines_file, 'r') as f:
                    self.performance_baselines = json.load(f)
                
                self.logger.info(f"✅ Loaded {len(self.performance_baselines)} performance baselines")
            
        except Exception as e:
            self.logger.error(f"Failed to load baselines: {e}")
    
    def _save_baselines(self):
        """Save performance baselines"""
        try:
            baselines_file = self.pae_dir / "baselines.json"
            with open(baselines_file, 'w') as f:
                json.dump(self.performance_baselines, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save baselines: {e}")
    
    def _load_recommendations(self):
        """Load existing recommendations"""
        try:
            recommendations_file = self.pae_dir / "recommendations.json"
            if recommendations_file.exists():
                with open(recommendations_file, 'r') as f:
                    recommendations_data = json.load(f)
                
                for rec_data in recommendations_data:
                    recommendation = OptimizationRecommendation(
                        recommendation_id=rec_data["recommendation_id"],
                        optimization_type=OptimizationType(rec_data["optimization_type"]),
                        target_component=rec_data["target_component"],
                        description=rec_data["description"],
                        expected_improvement=rec_data["expected_improvement"],
                        implementation_effort=rec_data["implementation_effort"],
                        priority=Priority(rec_data["priority"]),
                        parameters=rec_data["parameters"],
                        created_at=rec_data["created_at"],
                        applied=rec_data["applied"]
                    )
                    self.recommendations.append(recommendation)
                
                self.logger.info(f"✅ Loaded {len(self.recommendations)} recommendations")
            
        except Exception as e:
            self.logger.error(f"Failed to load recommendations: {e}")
    
    def _save_recommendations(self):
        """Save recommendations"""
        try:
            recommendations_file = self.pae_dir / "recommendations.json"
            recommendations_data = []
            
            for rec in self.recommendations:
                rec_dict = asdict(rec)
                rec_dict["optimization_type"] = rec.optimization_type.value
                rec_dict["priority"] = rec.priority.value
                recommendations_data.append(rec_dict)
            
            with open(recommendations_file, 'w') as f:
                json.dump(recommendations_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save recommendations: {e}")
    
    def start_analysis(self):
        """Start performance analysis"""
        try:
            if self.analysis_active:
                self.logger.warning("Analysis already active")
                return
            
            self.analysis_active = True
            self.analysis_thread = threading.Thread(
                target=self._analysis_loop,
                daemon=True
            )
            self.analysis_thread.start()
            
            self.logger.info("🔍 PAE analysis started")
            
        except Exception as e:
            self.logger.error(f"Failed to start analysis: {e}")
    
    def stop_analysis(self):
        """Stop performance analysis"""
        try:
            self.analysis_active = False
            
            if self.analysis_thread:
                self.analysis_thread.join(timeout=5.0)
            
            self.logger.info("🔍 PAE analysis stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop analysis: {e}")
    
    def _analysis_loop(self):
        """Main analysis loop"""
        while self.analysis_active:
            try:
                # Get metrics from QPM
                metrics = self._get_qpm_metrics()
                
                if metrics:
                    # Update baselines
                    self._update_baselines(metrics)
                    
                    # Detect regressions
                    self._detect_regressions(metrics)
                    
                    # Generate recommendations
                    self._generate_recommendations(metrics)
                    
                    # Save data
                    self._save_baselines()
                    self._save_recommendations()
                
                time.sleep(self.analysis_interval)
                
            except Exception as e:
                self.logger.error(f"Error in analysis loop: {e}")
                time.sleep(self.analysis_interval)
    
    def _get_qpm_metrics(self) -> Optional[Dict[str, Any]]:
        """Get metrics from QPM"""
        try:
            
            # Get recent metrics summary
            metrics = qpm.get_metrics_summary(time_window=self.analysis_interval)
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get QPM metrics: {e}")
            return None
    
    def _update_baselines(self, metrics: Dict[str, Any]):
        """Update performance baselines"""
        try:
            performance_metrics = metrics.get("performance_metrics", {})
            
            for metric_name, metric_data in performance_metrics.items():
                if "mean" in metric_data:
                    # Update baseline with exponential moving average
                    current_baseline = self.performance_baselines.get(metric_name, metric_data["mean"])
                    alpha = 0.1  # Smoothing factor
                    
                    new_baseline = alpha * metric_data["mean"] + (1 - alpha) * current_baseline
                    self.performance_baselines[metric_name] = new_baseline
            
        except Exception as e:
            self.logger.error(f"Failed to update baselines: {e}")
    
    def _detect_regressions(self, metrics: Dict[str, Any]):
        """Detect performance regressions"""
        try:
            performance_metrics = metrics.get("performance_metrics", {})
            regression_threshold = self.config.get("regression_threshold", 0.1)
            
            for metric_name, metric_data in performance_metrics.items():
                if metric_name in self.performance_baselines and "latest" in metric_data:
                    baseline = self.performance_baselines[metric_name]
                    current = metric_data["latest"]
                    
                    # Calculate regression percentage
                    if baseline > 0:
                        regression = (current - baseline) / baseline
                        
                        # Check if regression exceeds threshold
                        if abs(regression) > regression_threshold:
                            severity = self._calculate_regression_severity(regression)
                            
                            regression_obj = PerformanceRegression(
                                metric_name=metric_name,
                                baseline_value=baseline,
                                current_value=current,
                                regression_percentage=regression,
                                detected_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                                severity=severity
                            )
                            
                            self.regressions.append(regression_obj)
                            
                            self.logger.warning(f"🚨 Performance regression detected: {metric_name} ({regression:.1%})")
            
        except Exception as e:
            self.logger.error(f"Failed to detect regressions: {e}")
    
    def _calculate_regression_severity(self, regression: float) -> Priority:
        """Calculate regression severity"""
        abs_regression = abs(regression)
        
        if abs_regression > 0.5:  # 50%
            return Priority.CRITICAL
        elif abs_regression > 0.3:  # 30%
            return Priority.HIGH
        elif abs_regression > 0.15:  # 15%
            return Priority.MEDIUM
        else:
            return Priority.LOW
    
    def _generate_recommendations(self, metrics: Dict[str, Any]):
        """Generate optimization recommendations"""
        try:
            performance_metrics = metrics.get("performance_metrics", {})
            
            # Analyze CPU usage
            if "cpu_usage" in performance_metrics:
                cpu_data = performance_metrics["cpu_usage"]
                if "mean" in cpu_data:
                    self._analyze_cpu_usage(cpu_data)
            
            # Analyze memory usage
            if "memory_usage" in performance_metrics:
                memory_data = performance_metrics["memory_usage"]
                if "mean" in memory_data:
                    self._analyze_memory_usage(memory_data)
            
            # Analyze response times
            response_time_metrics = [m for m in performance_metrics.keys() if "response_time" in m]
            for metric_name in response_time_metrics:
                self._analyze_response_time(performance_metrics[metric_name], metric_name)
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
    
    def _analyze_cpu_usage(self, cpu_data: Dict[str, Any]):
        """Analyze CPU usage and generate recommendations"""
        try:
            mean_usage = cpu_data["mean"]
            target = self.config.get("optimization_targets", {}).get("cpu_usage", {}).get("target", 70.0)
            
            if mean_usage > target:
                # High CPU usage - recommend optimizations
                
                # Batch size optimization
                if self.config.get("optimization_strategies", {}).get("batch_size", {}).get("enabled", True):
                    recommendation = OptimizationRecommendation(
                        recommendation_id=f"cpu_batch_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                        optimization_type=OptimizationType.BATCH_SIZE,
                        target_component="processing_pipeline",
                        description=f"Reduce batch size to lower CPU usage (current: {mean_usage:.1f}%)",
                        expected_improvement=15.0,
                        implementation_effort="low",
                        priority=Priority.MEDIUM if mean_usage > 85 else Priority.LOW,
                        parameters={"suggested_batch_size": max(1, int(cpu_data.get("latest", 32) * 0.7))},
                        created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                        applied=False
                    )
                    
                    if not self._recommendation_exists(recommendation):
                        self.recommendations.append(recommendation)
                        self.logger.info(f"💡 Generated CPU optimization recommendation: {recommendation.description}")
                
                # Threading optimization
                recommendation = OptimizationRecommendation(
                    recommendation_id=f"cpu_threading_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                    optimization_type=OptimizationType.THREADING,
                    target_component="processing_pipeline",
                    description=f"Optimize thread pool size for CPU usage (current: {mean_usage:.1f}%)",
                    expected_improvement=20.0,
                    implementation_effort="medium",
                    priority=Priority.HIGH if mean_usage > 90 else Priority.MEDIUM,
                    parameters={"suggested_threads": max(1, os.cpu_count() // 2)},
                    created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                    applied=False
                )
                
                if not self._recommendation_exists(recommendation):
                    self.recommendations.append(recommendation)
                    self.logger.info(f"💡 Generated threading optimization recommendation")
            
        except Exception as e:
            self.logger.error(f"Failed to analyze CPU usage: {e}")
    
    def _analyze_memory_usage(self, memory_data: Dict[str, Any]):
        """Analyze memory usage and generate recommendations"""
        try:
            mean_usage = memory_data["mean"]
            target = self.config.get("optimization_targets", {}).get("memory_usage", {}).get("target", 80.0)
            
            if mean_usage > target:
                # High memory usage - recommend optimizations
                
                # Memory layout optimization
                recommendation = OptimizationRecommendation(
                    recommendation_id=f"memory_layout_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                    optimization_type=OptimizationType.MEMORY_LAYOUT,
                    target_component="data_processing",
                    description=f"Optimize memory layout to reduce usage (current: {mean_usage:.1f}%)",
                    expected_improvement=25.0,
                    implementation_effort="medium",
                    priority=Priority.HIGH if mean_usage > 90 else Priority.MEDIUM,
                    parameters={"strategy": "streaming", "chunk_size": 1024},
                    created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                    applied=False
                )
                
                if not self._recommendation_exists(recommendation):
                    self.recommendations.append(recommendation)
                    self.logger.info(f"💡 Generated memory optimization recommendation")
                
                # Cache optimization
                recommendation = OptimizationRecommendation(
                    recommendation_id=f"cache_opt_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                    optimization_type=OptimizationType.CACHE_OPTIMIZATION,
                    target_component="caching_system",
                    description=f"Optimize cache size and eviction policy (memory: {mean_usage:.1f}%)",
                    expected_improvement=15.0,
                    implementation_effort="low",
                    priority=Priority.MEDIUM,
                    parameters={"cache_size_mb": 512, "eviction_policy": "lru"},
                    created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                    applied=False
                )
                
                if not self._recommendation_exists(recommendation):
                    self.recommendations.append(recommendation)
                    self.logger.info(f"💡 Generated cache optimization recommendation")
            
        except Exception as e:
            self.logger.error(f"Failed to analyze memory usage: {e}")
    
    def _analyze_response_time(self, response_data: Dict[str, Any], metric_name: str):
        """Analyze response time and generate recommendations"""
        try:
            mean_time = response_data["mean"]
            target = self.config.get("optimization_targets", {}).get("response_time", {}).get("target", 1.0)
            
            if mean_time > target:
                # High response time - recommend optimizations
                
                # Precision optimization
                if self.config.get("optimization_strategies", {}).get("precision", {}).get("enabled", True):
                    recommendation = OptimizationRecommendation(
                        recommendation_id=f"precision_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                        optimization_type=OptimizationType.PRECISION,
                        target_component="model_inference",
                        description=f"Use lower precision to improve response time (current: {mean_time:.2f}s)",
                        expected_improvement=30.0,
                        implementation_effort="low",
                        priority=Priority.HIGH if mean_time > 5.0 else Priority.MEDIUM,
                        parameters={"precision": "fp16", "fallback": "fp32"},
                        created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                        applied=False
                    )
                    
                    if not self._recommendation_exists(recommendation):
                        self.recommendations.append(recommendation)
                        self.logger.info(f"💡 Generated precision optimization recommendation")
                
                # GPU utilization optimization
                recommendation = OptimizationRecommendation(
                    recommendation_id=f"gpu_util_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                    optimization_type=OptimizationType.GPU_UTILIZATION,
                    target_component="gpu_processing",
                    description=f"Optimize GPU utilization for faster processing (response: {mean_time:.2f}s)",
                    expected_improvement=40.0,
                    implementation_effort="medium",
                    priority=Priority.HIGH,
                    parameters={"batch_processing": True, "memory_optimization": True},
                    created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                    applied=False
                )
                
                if not self._recommendation_exists(recommendation):
                    self.recommendations.append(recommendation)
                    self.logger.info(f"💡 Generated GPU optimization recommendation")
            
        except Exception as e:
            self.logger.error(f"Failed to analyze response time: {e}")
    
    def _recommendation_exists(self, new_recommendation: OptimizationRecommendation) -> bool:
        """Check if similar recommendation already exists"""
        try:
            for existing in self.recommendations:
                if (existing.optimization_type == new_recommendation.optimization_type and
                    existing.target_component == new_recommendation.target_component and
                    not existing.applied and
                    self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - existing.created_at < 3600):  # Within last hour
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check recommendation existence: {e}")
            return False
    
    def get_recommendations(self, priority_filter: Optional[Priority] = None,
                          applied_filter: Optional[bool] = None) -> List[OptimizationRecommendation]:
        """Get optimization recommendations"""
        try:
            filtered_recommendations = []
            
            for rec in self.recommendations:
                # Filter by priority
                if priority_filter and rec.priority != priority_filter:
                    continue
                
                # Filter by applied status
                if applied_filter is not None and rec.applied != applied_filter:
                    continue
                
                filtered_recommendations.append(rec)
            
            # Sort by priority and creation time
            filtered_recommendations.sort(key=lambda r: (r.priority.value, r.created_at), reverse=True)
            
            return filtered_recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to get recommendations: {e}")
            return []
    
    def apply_recommendation(self, recommendation_id: str) -> bool:
        """Apply optimization recommendation"""
        try:
            for rec in self.recommendations:
                if rec.recommendation_id == recommendation_id:
                    # Mark as applied
                    rec.applied = True
                    
                    # Apply the optimization based on type
                    success = self._apply_optimization(rec)
                    
                    if success:
                        self.logger.info(f"✅ Applied optimization: {rec.description}")
                        self._save_recommendations()
                        return True
                    else:
                        rec.applied = False
                        self.logger.error(f"❌ Failed to apply optimization: {rec.description}")
                        return False
            
            self.logger.error(f"Recommendation not found: {recommendation_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to apply recommendation: {e}")
            return False
    
    def _apply_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Apply specific optimization"""
        try:
            # This would integrate with actual system components
            # For now, just log the optimization
            
            self.logger.info(f"Applying {recommendation.optimization_type.value} optimization")
            self.logger.info(f"Target: {recommendation.target_component}")
            self.logger.info(f"Parameters: {recommendation.parameters}")
            
            # In a real implementation, this would:
            # 1. Update system configuration
            # 2. Restart affected components
            # 3. Monitor the impact
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply optimization: {e}")
            return False
    
    def get_pae_status(self) -> Dict[str, Any]:
        """Get PAE status"""
        try:
            active_recommendations = len([r for r in self.recommendations if not r.applied])
            applied_recommendations = len([r for r in self.recommendations if r.applied])
            
            return {
                "enabled": self.config.get("enabled", True),
                "analysis_active": self.analysis_active,
                "analysis_interval": self.analysis_interval,
                "baselines_count": len(self.performance_baselines),
                "regressions_count": len(self.regressions),
                "active_recommendations": active_recommendations,
                "applied_recommendations": applied_recommendations,
                "total_recommendations": len(self.recommendations)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get PAE status: {e}")
            return {"error": str(e)}

# Global instance
pae = PAE()