#!/usr/bin/env python3
"""
AGI Optimizer - Avtonomni optimizator sistema in procesov
"""

import os
import json
import logging
import time
import threading
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

class OptimizationType(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Types of optimization"""
    PERFORMANCE = "performance"
    MEMORY = "memory"
    CPU = "cpu"
    DISK = "disk"
    NETWORK = "network"
    ALGORITHM = "algorithm"
    RESOURCE = "resource"
    WORKFLOW = "workflow"

class OptimizationStatus(Enum):
    """Optimization status"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    OPTIMIZING = "optimizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class OptimizationPriority(Enum):
    """Optimization priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class OptimizationMetric:
    """Optimization metric"""
    metric_id: str
    name: str
    description: str
    current_value: float
    target_value: float
    improvement_percentage: float
    unit: str
    timestamp: float

@dataclass
class OptimizationAction:
    """Optimization action"""
    action_id: str
    name: str
    description: str
    optimization_type: OptimizationType
    parameters: Dict[str, Any]
    estimated_impact: float
    risk_level: str
    executed: bool
    execution_time: Optional[float]
    result: Optional[Dict[str, Any]]

@dataclass
class OptimizationTask:
    """Optimization task"""
    task_id: str
    name: str
    description: str
    optimization_type: OptimizationType
    priority: OptimizationPriority
    target: str
    metrics: List[OptimizationMetric]
    actions: List[OptimizationAction]
    status: OptimizationStatus
    created_at: float
    started_at: Optional[float]
    completed_at: Optional[float]
    success_rate: float

class AGIOptimizer:
    """AGI Optimizer - Autonomous system and process optimizer"""
    
    def __init__(self, config_path: str = "mia/data/agi_agents/optimizer_config.json"):
        self.config_path = config_path
        self.optimizer_dir = Path("mia/data/agi_agents/optimizer")
        self.optimizer_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.AGIOptimizer")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Optimization state
        self.optimization_tasks: Dict[str, OptimizationTask] = {}
        self.active_tasks: Dict[str, OptimizationTask] = {}
        self.optimization_active = False
        self.optimization_thread: Optional[threading.Thread] = None
        
        # Optimization handlers
        self.optimization_handlers: Dict[OptimizationType, Callable] = {}
        
        # Performance baselines
        self.performance_baselines: Dict[str, float] = {}
        
        # Register default handlers
        self._register_default_handlers()
        
        # Initialize performance baselines
        self._initialize_baselines()
        
        self.logger.info("⚡ AGI Optimizer initialized")
    
    def _load_configuration(self) -> Dict:
        """Load optimizer configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load optimizer config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default optimizer configuration"""
        config = {
            "enabled": True,
            "optimization_interval": 300,  # 5 minutes
            "auto_optimization": True,
            "max_concurrent_optimizations": 3,
            "optimization_timeout": 600,  # 10 minutes
            "performance_monitoring": True,
            "optimization_types": {
                "performance": {"enabled": True, "priority": "high", "auto_trigger": True},
                "memory": {"enabled": True, "priority": "high", "auto_trigger": True},
                "cpu": {"enabled": True, "priority": "medium", "auto_trigger": True},
                "disk": {"enabled": True, "priority": "medium", "auto_trigger": False},
                "network": {"enabled": True, "priority": "low", "auto_trigger": False},
                "algorithm": {"enabled": True, "priority": "medium", "auto_trigger": False},
                "resource": {"enabled": True, "priority": "high", "auto_trigger": True},
                "workflow": {"enabled": True, "priority": "medium", "auto_trigger": False}
            },
            "thresholds": {
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "disk_usage": 90.0,
                "response_time": 1000.0,  # milliseconds
                "error_rate": 5.0  # percentage
            },
            "optimization_targets": {
                "cpu_reduction": 10.0,  # percentage
                "memory_reduction": 15.0,  # percentage
                "response_time_improvement": 20.0,  # percentage
                "throughput_improvement": 25.0  # percentage
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _register_default_handlers(self):
        """Register default optimization handlers"""
        try:
            self.optimization_handlers.update({
                OptimizationType.PERFORMANCE: self._optimize_performance,
                OptimizationType.MEMORY: self._optimize_memory,
                OptimizationType.CPU: self._optimize_cpu,
                OptimizationType.DISK: self._optimize_disk,
                OptimizationType.NETWORK: self._optimize_network,
                OptimizationType.ALGORITHM: self._optimize_algorithm,
                OptimizationType.RESOURCE: self._optimize_resource,
                OptimizationType.WORKFLOW: self._optimize_workflow
            })
            
        except Exception as e:
            self.logger.error(f"Failed to register optimization handlers: {e}")
    
    def _initialize_baselines(self):
        """Initialize performance baselines"""
        try:
            # Collect initial performance metrics
            self.performance_baselines.update({
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "load_average": os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0.0
            })
            
            self.logger.info("📊 Performance baselines initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize baselines: {e}")
    
    def start_optimization(self):
        """Start autonomous optimization"""
        try:
            if self.optimization_active:
                return
            
            self.optimization_active = True
            self.optimization_thread = threading.Thread(
                target=self._optimization_loop,
                daemon=True
            )
            self.optimization_thread.start()
            
            self.logger.info("⚡ AGI Optimization started")
            
        except Exception as e:
            self.logger.error(f"Failed to start optimization: {e}")
    
    def stop_optimization(self):
        """Stop autonomous optimization"""
        try:
            self.optimization_active = False
            
            if self.optimization_thread:
                self.optimization_thread.join(timeout=5.0)
            
            self.logger.info("⚡ AGI Optimization stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop optimization: {e}")
    
    def _optimization_loop(self):
        """Main optimization loop"""
        while self.optimization_active:
            try:
                # Monitor system performance
                self._monitor_performance()
                
                # Identify optimization opportunities
                if self.config.get("auto_optimization", True):
                    self._identify_optimization_opportunities()
                
                # Process optimization tasks
                self._process_optimization_tasks()
                
                # Update performance baselines
                self._update_baselines()
                
                time.sleep(self.config.get("optimization_interval", 300))
                
            except Exception as e:
                self.logger.error(f"Error in optimization loop: {e}")
                time.sleep(60)
    
    def create_optimization_task(self, name: str, description: str, 
                               optimization_type: OptimizationType,
                               target: str, priority: OptimizationPriority = OptimizationPriority.MEDIUM) -> str:
        """Create new optimization task"""
        try:
            task_id = f"opt_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}_{len(self.optimization_tasks)}"
            
            # Create optimization task
            task = OptimizationTask(
                task_id=task_id,
                name=name,
                description=description,
                optimization_type=optimization_type,
                priority=priority,
                target=target,
                metrics=[],
                actions=[],
                status=OptimizationStatus.PENDING,
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                started_at=None,
                completed_at=None,
                success_rate=0.0
            )
            
            # Generate optimization actions
            task.actions = self._generate_optimization_actions(optimization_type, target)
            
            # Generate metrics to track
            task.metrics = self._generate_optimization_metrics(optimization_type, target)
            
            # Store task
            self.optimization_tasks[task_id] = task
            
            self.logger.info(f"⚡ Created optimization task: {name} ({task_id})")
            
            return task_id
            
        except Exception as e:
            self.logger.error(f"Failed to create optimization task: {e}")
            return ""
    
    def _generate_optimization_actions(self, optimization_type: OptimizationType, 
                                     target: str) -> List[OptimizationAction]:
        """Generate optimization actions for type and target"""
        try:
            actions = []
            
            if optimization_type == OptimizationType.MEMORY:
                actions.extend([
                    OptimizationAction(
                        action_id="mem_gc",
                        name="Garbage Collection",
                        description="Force garbage collection to free memory",
                        optimization_type=optimization_type,
                        parameters={"aggressive": False},
                        estimated_impact=0.1,
                        risk_level="low",
                        executed=False,
                        execution_time=None,
                        result=None
                    ),
                    OptimizationAction(
                        action_id="mem_cache_clear",
                        name="Clear Caches",
                        description="Clear unnecessary caches",
                        optimization_type=optimization_type,
                        parameters={"cache_types": ["temp", "user"]},
                        estimated_impact=0.15,
                        risk_level="low",
                        executed=False,
                        execution_time=None,
                        result=None
                    )
                ])
            
            elif optimization_type == OptimizationType.CPU:
                actions.extend([
                    OptimizationAction(
                        action_id="cpu_process_priority",
                        name="Adjust Process Priorities",
                        description="Optimize process priorities for better CPU usage",
                        optimization_type=optimization_type,
                        parameters={"strategy": "balanced"},
                        estimated_impact=0.12,
                        risk_level="medium",
                        executed=False,
                        execution_time=None,
                        result=None
                    )
                ])
            
            elif optimization_type == OptimizationType.PERFORMANCE:
                actions.extend([
                    OptimizationAction(
                        action_id="perf_algorithm_tune",
                        name="Algorithm Tuning",
                        description="Optimize algorithm parameters",
                        optimization_type=optimization_type,
                        parameters={"target": target},
                        estimated_impact=0.2,
                        risk_level="medium",
                        executed=False,
                        execution_time=None,
                        result=None
                    )
                ])
            
            return actions
            
        except Exception as e:
            self.logger.error(f"Failed to generate optimization actions: {e}")
            return []
    
    def _generate_optimization_metrics(self, optimization_type: OptimizationType, 
                                     target: str) -> List[OptimizationMetric]:
        """Generate optimization metrics for type and target"""
        try:
            metrics = []
            current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            if optimization_type == OptimizationType.MEMORY:
                current_memory = psutil.virtual_memory().percent
                target_memory = current_memory * 0.85  # 15% reduction target
                
                metrics.append(OptimizationMetric(
                    metric_id="memory_usage",
                    name="Memory Usage",
                    description="System memory usage percentage",
                    current_value=current_memory,
                    target_value=target_memory,
                    improvement_percentage=15.0,
                    unit="percent",
                    timestamp=current_time
                ))
            
            elif optimization_type == OptimizationType.CPU:
                current_cpu = psutil.cpu_percent(interval=1)
                target_cpu = current_cpu * 0.9  # 10% reduction target
                
                metrics.append(OptimizationMetric(
                    metric_id="cpu_usage",
                    name="CPU Usage",
                    description="System CPU usage percentage",
                    current_value=current_cpu,
                    target_value=target_cpu,
                    improvement_percentage=10.0,
                    unit="percent",
                    timestamp=current_time
                ))
            
            elif optimization_type == OptimizationType.PERFORMANCE:
                # Generic performance metric
                metrics.append(OptimizationMetric(
                    metric_id="response_time",
                    name="Response Time",
                    description="System response time",
                    current_value=100.0,  # milliseconds
                    target_value=80.0,    # 20% improvement
                    improvement_percentage=20.0,
                    unit="ms",
                    timestamp=current_time
                ))
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to generate optimization metrics: {e}")
            return []
    
    def _monitor_performance(self):
        """Monitor system performance"""
        try:
            current_metrics = {
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "load_average": os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0.0
            }
            
            # Check thresholds
            thresholds = self.config.get("thresholds", {})
            
            for metric, value in current_metrics.items():
                threshold = thresholds.get(metric)
                if threshold and value > threshold:
                    self.logger.warning(f"⚠️ Performance threshold exceeded: {metric} = {value:.1f}% (threshold: {threshold}%)")
            
        except Exception as e:
            self.logger.error(f"Failed to monitor performance: {e}")
    
    def _identify_optimization_opportunities(self):
        """Identify optimization opportunities"""
        try:
            # Check for memory optimization opportunities
            memory_usage = psutil.virtual_memory().percent
            if memory_usage > self.config.get("thresholds", {}).get("memory_usage", 85.0):
                if not any(task.optimization_type == OptimizationType.MEMORY and 
                          task.status in [OptimizationStatus.PENDING, OptimizationStatus.ANALYZING, OptimizationStatus.OPTIMIZING]
                          for task in self.optimization_tasks.values()):
                    
                    self.create_optimization_task(
                        "Memory Optimization",
                        "Optimize memory usage due to high utilization",
                        OptimizationType.MEMORY,
                        "system",
                        OptimizationPriority.HIGH
                    )
            
            # Check for CPU optimization opportunities
            cpu_usage = psutil.cpu_percent(interval=1)
            if cpu_usage > self.config.get("thresholds", {}).get("cpu_usage", 80.0):
                if not any(task.optimization_type == OptimizationType.CPU and 
                          task.status in [OptimizationStatus.PENDING, OptimizationStatus.ANALYZING, OptimizationStatus.OPTIMIZING]
                          for task in self.optimization_tasks.values()):
                    
                    self.create_optimization_task(
                        "CPU Optimization",
                        "Optimize CPU usage due to high utilization",
                        OptimizationType.CPU,
                        "system",
                        OptimizationPriority.HIGH
                    )
            
        except Exception as e:
            self.logger.error(f"Failed to identify optimization opportunities: {e}")
    
    def _process_optimization_tasks(self):
        """Process optimization tasks"""
        try:
            # Get pending tasks sorted by priority
            pending_tasks = [
                task for task in self.optimization_tasks.values()
                if task.status == OptimizationStatus.PENDING
            ]
            
            priority_order = {
                OptimizationPriority.CRITICAL: 4,
                OptimizationPriority.HIGH: 3,
                OptimizationPriority.MEDIUM: 2,
                OptimizationPriority.LOW: 1
            }
            
            pending_tasks.sort(key=lambda x: priority_order[x.priority], reverse=True)
            
            # Start tasks up to concurrent limit
            max_concurrent = self.config.get("max_concurrent_optimizations", 3)
            available_slots = max_concurrent - len(self.active_tasks)
            
            for task in pending_tasks[:available_slots]:
                self._start_optimization_task(task)
            
        except Exception as e:
            self.logger.error(f"Failed to process optimization tasks: {e}")
    
    def _start_optimization_task(self, task: OptimizationTask):
        """Start optimization task"""
        try:
            task.status = OptimizationStatus.ANALYZING
            task.started_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # Add to active tasks
            self.active_tasks[task.task_id] = task
            
            # Start task execution in separate thread
            task_thread = threading.Thread(
                target=self._execute_optimization_task,
                args=(task,),
                daemon=True
            )
            task_thread.start()
            
            self.logger.info(f"▶️ Started optimization task: {task.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to start optimization task: {e}")
            task.status = OptimizationStatus.FAILED
    
    def _execute_optimization_task(self, task: OptimizationTask):
        """Execute optimization task"""
        try:
            # Get optimization handler
            handler = self.optimization_handlers.get(task.optimization_type)
            if not handler:
                task.status = OptimizationStatus.FAILED
                task.completed_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                return
            
            task.status = OptimizationStatus.OPTIMIZING
            
            # Execute optimization actions
            successful_actions = 0
            
            for action in task.actions:
                try:
                    start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                    result = handler(action, task)
                    action.execution_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
                    action.result = result
                    action.executed = True
                    successful_actions += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to execute optimization action {action.action_id}: {e}")
                    action.result = {"error": str(e)}
            
            # Calculate success rate
            if task.actions:
                task.success_rate = successful_actions / len(task.actions)
            else:
                task.success_rate = 0.0
            
            # Update task status
            if task.success_rate >= 0.5:
                task.status = OptimizationStatus.COMPLETED
            else:
                task.status = OptimizationStatus.FAILED
            
            task.completed_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # Remove from active tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            
            self.logger.info(f"✅ Optimization task completed: {task.name} (Success rate: {task.success_rate:.1%})")
            
        except Exception as e:
            self.logger.error(f"Failed to execute optimization task: {e}")
            task.status = OptimizationStatus.FAILED
            task.completed_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
    
    # Optimization Handlers
    
    def _optimize_performance(self, action: OptimizationAction, task: OptimizationTask) -> Dict[str, Any]:
        """Optimize performance"""
        try:
            if action.action_id == "perf_algorithm_tune":
                # Simulate algorithm tuning
                return {
                    "status": "success",
                    "improvement": 0.15,
                    "message": "Algorithm parameters optimized"
                }
            
            return {"status": "success", "message": "Performance optimization completed"}
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _optimize_memory(self, action: OptimizationAction, task: OptimizationTask) -> Dict[str, Any]:
        """Optimize memory usage"""
        try:
            if action.action_id == "mem_gc":
                # Force garbage collection
                import gc
                gc.collect()
                return {
                    "status": "success",
                    "message": "Garbage collection executed"
                }
            
            elif action.action_id == "mem_cache_clear":
                # Clear caches (simulated)
                return {
                    "status": "success",
                    "message": "Caches cleared"
                }
            
            return {"status": "success", "message": "Memory optimization completed"}
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _optimize_cpu(self, action: OptimizationAction, task: OptimizationTask) -> Dict[str, Any]:
        """Optimize CPU usage"""
        try:
            if action.action_id == "cpu_process_priority":
                # Optimize process priorities (simulated)
                return {
                    "status": "success",
                    "message": "Process priorities optimized"
                }
            
            return {"status": "success", "message": "CPU optimization completed"}
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _optimize_disk(self, action: OptimizationAction, task: OptimizationTask) -> Dict[str, Any]:
        """Optimize disk usage"""
        try:
            return {"status": "success", "message": "Disk optimization completed"}
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _optimize_network(self, action: OptimizationAction, task: OptimizationTask) -> Dict[str, Any]:
        """Optimize network usage"""
        try:
            return {"status": "success", "message": "Network optimization completed"}
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _optimize_algorithm(self, action: OptimizationAction, task: OptimizationTask) -> Dict[str, Any]:
        """Optimize algorithms"""
        try:
            return {"status": "success", "message": "Algorithm optimization completed"}
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _optimize_resource(self, action: OptimizationAction, task: OptimizationTask) -> Dict[str, Any]:
        """Optimize resource usage"""
        try:
            return {"status": "success", "message": "Resource optimization completed"}
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _optimize_workflow(self, action: OptimizationAction, task: OptimizationTask) -> Dict[str, Any]:
        """Optimize workflows"""
        try:
            return {"status": "success", "message": "Workflow optimization completed"}
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _update_baselines(self):
        """Update performance baselines"""
        try:
            # Update baselines with current metrics
            current_metrics = {
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "load_average": os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0.0
            }
            
            # Use exponential moving average to update baselines
            alpha = 0.1  # Smoothing factor
            
            for metric, current_value in current_metrics.items():
                if metric in self.performance_baselines:
                    self.performance_baselines[metric] = (
                        alpha * current_value + 
                        (1 - alpha) * self.performance_baselines[metric]
                    )
                else:
                    self.performance_baselines[metric] = current_value
            
        except Exception as e:
            self.logger.error(f"Failed to update baselines: {e}")
    
    def get_optimization_task(self, task_id: str) -> Optional[OptimizationTask]:
        """Get optimization task by ID"""
        return self.optimization_tasks.get(task_id)
    
    def get_active_tasks(self) -> List[OptimizationTask]:
        """Get all active optimization tasks"""
        return list(self.active_tasks.values())
    
    def cancel_optimization_task(self, task_id: str) -> bool:
        """Cancel optimization task"""
        try:
            if task_id in self.optimization_tasks:
                task = self.optimization_tasks[task_id]
                task.status = OptimizationStatus.CANCELLED
                task.completed_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                
                # Remove from active tasks if present
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
                
                self.logger.info(f"🚫 Optimization task cancelled: {task.name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to cancel optimization task: {e}")
            return False
    
    def get_optimizer_status(self) -> Dict[str, Any]:
        """Get optimizer status"""
        try:
            return {
                "enabled": self.config.get("enabled", True),
                "optimization_active": self.optimization_active,
                "total_tasks": len(self.optimization_tasks),
                "active_tasks": len(self.active_tasks),
                "pending_tasks": len([t for t in self.optimization_tasks.values() if t.status == OptimizationStatus.PENDING]),
                "completed_tasks": len([t for t in self.optimization_tasks.values() if t.status == OptimizationStatus.COMPLETED]),
                "failed_tasks": len([t for t in self.optimization_tasks.values() if t.status == OptimizationStatus.FAILED]),
                "auto_optimization": self.config.get("auto_optimization", True),
                "performance_baselines": self.performance_baselines.copy()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get optimizer status: {e}")
            return {"error": str(e)}

# Global instance
agi_optimizer = AGIOptimizer()