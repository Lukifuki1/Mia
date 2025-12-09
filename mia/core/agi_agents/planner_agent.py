#!/usr/bin/env python3
"""
MIA AGI Planner Agent
Strategic planning and task decomposition
"""

import os
import json
import logging
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import asyncio

class PlanType(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Types of plans"""
    PROJECT = "project"
    TASK = "task"
    LEARNING = "learning"
    OPTIMIZATION = "optimization"
    EMERGENCY = "emergency"
    MAINTENANCE = "maintenance"

class PlanStatus(Enum):
    """Plan execution status"""
    DRAFT = "draft"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Priority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class Task:
    """Individual task in a plan"""
    task_id: str
    name: str
    description: str
    priority: Priority
    estimated_duration: float
    dependencies: List[str]
    resources_required: Dict[str, Any]
    success_criteria: List[str]
    status: str
    assigned_agent: Optional[str]
    created_at: float
    deadline: Optional[float]

@dataclass
class Plan:
    """Strategic plan"""
    plan_id: str
    name: str
    description: str
    plan_type: PlanType
    priority: Priority
    tasks: List[Task]
    status: PlanStatus
    created_at: float
    updated_at: float
    estimated_completion: float
    success_metrics: Dict[str, Any]
    risk_assessment: Dict[str, Any]

class PlannerAgent:
    """AGI Planner Agent for strategic planning"""
    
    def __init__(self, config_path: str = "mia/data/agi_agents/planner_config.json"):
        self.config_path = config_path
        self.planner_dir = Path("mia/data/agi_agents/planner")
        self.planner_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.PlannerAgent")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Planning state
        self.active_plans: Dict[str, Plan] = {}
        self.completed_plans: Dict[str, Plan] = {}
        self.planning_history: List[Dict[str, Any]] = []
        
        # Planning capabilities
        self.planning_strategies = {
            "hierarchical": self._hierarchical_planning,
            "temporal": self._temporal_planning,
            "resource_based": self._resource_based_planning,
            "risk_aware": self._risk_aware_planning
        }
        
        # Load existing plans
        self._load_plans()
        
        self.logger.info("🧠 Planner Agent initialized")
    
    def _load_configuration(self) -> Dict:
        """Load planner configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load planner config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default planner configuration"""
        config = {
            "enabled": True,
            "max_active_plans": 10,
            "max_tasks_per_plan": 50,
            "default_planning_strategy": "hierarchical",
            "auto_optimization": True,
            "risk_assessment": True,
            "resource_tracking": True,
            "planning_horizon_days": 30,
            "task_estimation": {
                "use_historical_data": True,
                "confidence_factor": 0.8,
                "buffer_percentage": 20
            },
            "priority_weights": {
                "user_requests": 1.0,
                "system_maintenance": 0.7,
                "optimization": 0.5,
                "learning": 0.6,
                "emergency": 2.0
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _load_plans(self):
        """Load existing plans from storage"""
        try:
            plans_file = self.planner_dir / "plans.json"
            if plans_file.exists():
                with open(plans_file, 'r') as f:
                    plans_data = json.load(f)
                
                for plan_id, plan_data in plans_data.items():
                    # Reconstruct tasks
                    tasks = []
                    for task_data in plan_data["tasks"]:
                        task = Task(
                            task_id=task_data["task_id"],
                            name=task_data["name"],
                            description=task_data["description"],
                            priority=Priority(task_data["priority"]),
                            estimated_duration=task_data["estimated_duration"],
                            dependencies=task_data["dependencies"],
                            resources_required=task_data["resources_required"],
                            success_criteria=task_data["success_criteria"],
                            status=task_data["status"],
                            assigned_agent=task_data.get("assigned_agent"),
                            created_at=task_data["created_at"],
                            deadline=task_data.get("deadline")
                        )
                        tasks.append(task)
                    
                    # Reconstruct plan
                    plan = Plan(
                        plan_id=plan_data["plan_id"],
                        name=plan_data["name"],
                        description=plan_data["description"],
                        plan_type=PlanType(plan_data["plan_type"]),
                        priority=Priority(plan_data["priority"]),
                        tasks=tasks,
                        status=PlanStatus(plan_data["status"]),
                        created_at=plan_data["created_at"],
                        updated_at=plan_data["updated_at"],
                        estimated_completion=plan_data["estimated_completion"],
                        success_metrics=plan_data["success_metrics"],
                        risk_assessment=plan_data["risk_assessment"]
                    )
                    
                    if plan.status in [PlanStatus.COMPLETED, PlanStatus.FAILED, PlanStatus.CANCELLED]:
                        self.completed_plans[plan_id] = plan
                    else:
                        self.active_plans[plan_id] = plan
            
            self.logger.info(f"✅ Loaded {len(self.active_plans)} active plans, {len(self.completed_plans)} completed plans")
            
        except Exception as e:
            self.logger.error(f"Failed to load plans: {e}")
    
    def _save_plans(self):
        """Save plans to storage"""
        try:
            all_plans = {**self.active_plans, **self.completed_plans}
            plans_data = {}
            
            for plan_id, plan in all_plans.items():
                # Convert tasks to dict
                tasks_data = []
                for task in plan.tasks:
                    task_dict = asdict(task)
                    task_dict["priority"] = task.priority.value
                    tasks_data.append(task_dict)
                
                # Convert plan to dict
                plan_dict = asdict(plan)
                plan_dict["plan_type"] = plan.plan_type.value
                plan_dict["priority"] = plan.priority.value
                plan_dict["status"] = plan.status.value
                plan_dict["tasks"] = tasks_data
                
                plans_data[plan_id] = plan_dict
            
            plans_file = self.planner_dir / "plans.json"
            with open(plans_file, 'w') as f:
                json.dump(plans_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save plans: {e}")
    
    def create_plan(self, name: str, description: str, plan_type: PlanType,
                    priority: Priority, objectives: List[str],
                    constraints: Dict[str, Any] = None,
                    deadline: Optional[float] = None) -> str:
        """Create new strategic plan"""
        try:
            # Generate plan ID
            plan_id = hashlib.sha256(f"{name}_{plan_type.value}_{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}".encode()).hexdigest()[:16]
            
            # Decompose objectives into tasks
            tasks = self._decompose_objectives(objectives, constraints or {})
            
            # Estimate completion time
            estimated_completion = self._estimate_plan_completion(tasks)
            
            # Perform risk assessment
            risk_assessment = self._assess_plan_risks(tasks, constraints or {})
            
            # Create plan
            plan = Plan(
                plan_id=plan_id,
                name=name,
                description=description,
                plan_type=plan_type,
                priority=priority,
                tasks=tasks,
                status=PlanStatus.DRAFT,
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                updated_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                estimated_completion=estimated_completion,
                success_metrics=self._define_success_metrics(objectives),
                risk_assessment=risk_assessment
            )
            
            # Add to active plans
            self.active_plans[plan_id] = plan
            
            # Save plans
            self._save_plans()
            
            self.logger.info(f"✅ Created plan: {name} ({plan_type.value}) with {len(tasks)} tasks")
            return plan_id
            
        except Exception as e:
            self.logger.error(f"Failed to create plan: {e}")
            return ""
    
    def _decompose_objectives(self, objectives: List[str], constraints: Dict[str, Any]) -> List[Task]:
        """Decompose objectives into actionable tasks"""
        try:
            tasks = []
            
            for i, objective in enumerate(objectives):
                # Analyze objective complexity
                complexity = self._analyze_objective_complexity(objective)
                
                if complexity == "simple":
                    # Create single task
                    task = self._create_task_from_objective(objective, i)
                    tasks.append(task)
                
                elif complexity == "moderate":
                    # Break into 2-3 subtasks
                    subtasks = self._break_into_subtasks(objective, 3)
                    for j, subtask in enumerate(subtasks):
                        task = self._create_task_from_objective(subtask, f"{i}_{j}")
                        tasks.append(task)
                
                elif complexity == "complex":
                    # Break into multiple phases
                    phases = self._break_into_phases(objective)
                    for j, phase in enumerate(phases):
                        task = self._create_task_from_objective(phase, f"{i}_{j}")
                        tasks.append(task)
            
            # Establish dependencies
            tasks = self._establish_task_dependencies(tasks)
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Failed to decompose objectives: {e}")
            return []
    
    def _analyze_objective_complexity(self, objective: str) -> str:
        """Analyze objective complexity"""
        try:
            # Simple heuristics for complexity analysis
            complexity_indicators = {
                "simple": ["update", "fix", "check", "verify", "test"],
                "moderate": ["implement", "create", "build", "develop", "design"],
                "complex": ["system", "architecture", "integration", "optimization", "enterprise"]
            }
            
            objective_lower = objective.lower()
            
            for complexity, indicators in complexity_indicators.items():
                if any(indicator in objective_lower for indicator in indicators):
                    return complexity
            
            # Default to moderate if no indicators found
            return "moderate"
            
        except Exception as e:
            self.logger.error(f"Failed to analyze objective complexity: {e}")
            return "moderate"
    
    def _create_task_from_objective(self, objective: str, task_index: Any) -> Task:
        """Create task from objective"""
        try:
            task_id = hashlib.sha256(f"{objective}_{task_index}_{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}".encode()).hexdigest()[:12]
            
            # Estimate duration based on objective
            estimated_duration = self._estimate_task_duration(objective)
            
            # Determine priority
            priority = self._determine_task_priority(objective)
            
            # Define success criteria
            success_criteria = self._define_task_success_criteria(objective)
            
            # Identify required resources
            resources_required = self._identify_required_resources(objective)
            
            task = Task(
                task_id=task_id,
                name=objective,
                description=f"Task: {objective}",
                priority=priority,
                estimated_duration=estimated_duration,
                dependencies=[],
                resources_required=resources_required,
                success_criteria=success_criteria,
                status="pending",
                assigned_agent=None,
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                deadline=None
            )
            
            return task
            
        except Exception as e:
            self.logger.error(f"Failed to create task from objective: {e}")
            return None
    
    def _break_into_subtasks(self, objective: str, max_subtasks: int) -> List[str]:
        """Break objective into subtasks"""
        try:
            # Simple subtask generation
            if "implement" in objective.lower():
                return [
                    f"Design {objective}",
                    f"Develop {objective}",
                    f"Test {objective}"
                ]
            elif "build" in objective.lower():
                return [
                    f"Plan {objective}",
                    f"Construct {objective}",
                    f"Validate {objective}"
                ]
            elif "create" in objective.lower():
                return [
                    f"Specify {objective}",
                    f"Implement {objective}",
                    f"Review {objective}"
                ]
            else:
                return [
                    f"Prepare for {objective}",
                    f"Execute {objective}",
                    f"Verify {objective}"
                ]
            
        except Exception as e:
            self.logger.error(f"Failed to break into subtasks: {e}")
            return [objective]
    
    def _break_into_phases(self, objective: str) -> List[str]:
        """Break complex objective into phases"""
        try:
            phases = [
                f"Phase 1: Analysis and Planning for {objective}",
                f"Phase 2: Design and Architecture for {objective}",
                f"Phase 3: Implementation of {objective}",
                f"Phase 4: Testing and Validation of {objective}",
                f"Phase 5: Deployment and Monitoring of {objective}"
            ]
            return phases
            
        except Exception as e:
            self.logger.error(f"Failed to break into phases: {e}")
            return [objective]
    
    def _establish_task_dependencies(self, tasks: List[Task]) -> List[Task]:
        """Establish dependencies between tasks"""
        try:
            # Simple dependency logic
            for i, task in enumerate(tasks):
                if i > 0:
                    # Each task depends on the previous one
                    task.dependencies.append(tasks[i-1].task_id)
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Failed to establish task dependencies: {e}")
            return tasks
    
    def _estimate_task_duration(self, objective: str) -> float:
        """Estimate task duration in hours"""
        try:
            # Simple duration estimation
            duration_map = {
                "simple": 2.0,
                "moderate": 8.0,
                "complex": 24.0
            }
            
            complexity = self._analyze_objective_complexity(objective)
            base_duration = duration_map.get(complexity, 8.0)
            
            # Add buffer
            buffer_percentage = self.config.get("task_estimation", {}).get("buffer_percentage", 20)
            return base_duration * (1 + buffer_percentage / 100)
            
        except Exception as e:
            self.logger.error(f"Failed to estimate task duration: {e}")
            return 8.0
    
    def _determine_task_priority(self, objective: str) -> Priority:
        """Determine task priority"""
        try:
            objective_lower = objective.lower()
            
            if any(word in objective_lower for word in ["critical", "urgent", "emergency"]):
                return Priority.CRITICAL
            elif any(word in objective_lower for word in ["important", "high"]):
                return Priority.HIGH
            elif any(word in objective_lower for word in ["low", "minor"]):
                return Priority.LOW
            else:
                return Priority.MEDIUM
            
        except Exception as e:
            self.logger.error(f"Failed to determine task priority: {e}")
            return Priority.MEDIUM
    
    def _define_task_success_criteria(self, objective: str) -> List[str]:
        """Define success criteria for task"""
        try:
            return [
                f"Task '{objective}' completed successfully",
                "No errors or issues reported",
                "Quality standards met",
                "Documentation updated"
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to define success criteria: {e}")
            return ["Task completed"]
    
    def _identify_required_resources(self, objective: str) -> Dict[str, Any]:
        """Identify required resources for task"""
        try:
            resources = {
                "cpu_hours": 1.0,
                "memory_gb": 2.0,
                "storage_gb": 1.0,
                "network_access": False,
                "external_apis": [],
                "human_approval": False
            }
            
            objective_lower = objective.lower()
            
            if any(word in objective_lower for word in ["build", "compile", "train"]):
                resources["cpu_hours"] = 4.0
                resources["memory_gb"] = 8.0
            
            if any(word in objective_lower for word in ["download", "internet", "web"]):
                resources["network_access"] = True
            
            if any(word in objective_lower for word in ["critical", "system", "security"]):
                resources["human_approval"] = True
            
            return resources
            
        except Exception as e:
            self.logger.error(f"Failed to identify required resources: {e}")
            return {}
    
    def _estimate_plan_completion(self, tasks: List[Task]) -> float:
        """Estimate plan completion time"""
        try:
            total_duration = sum(task.estimated_duration for task in tasks)
            
            # Account for parallelization
            parallelization_factor = 0.7  # Assume 30% time savings from parallel execution
            
            return self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 + (total_duration * 3600 * parallelization_factor)  # Convert hours to seconds
            
        except Exception as e:
            self.logger.error(f"Failed to estimate plan completion: {e}")
            return self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 + 86400  # Default to 1 day
    
    def _assess_plan_risks(self, tasks: List[Task], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Assess plan risks"""
        try:
            risks = {
                "resource_availability": 0.2,
                "technical_complexity": 0.3,
                "dependency_failures": 0.1,
                "external_factors": 0.1,
                "overall_risk_score": 0.0
            }
            
            # Calculate overall risk
            risks["overall_risk_score"] = sum(risks.values()) / len(risks)
            
            return risks
            
        except Exception as e:
            self.logger.error(f"Failed to assess plan risks: {e}")
            return {"overall_risk_score": 0.5}
    
    def _define_success_metrics(self, objectives: List[str]) -> Dict[str, Any]:
        """Define success metrics for plan"""
        try:
            return {
                "objectives_completed": 0,
                "total_objectives": len(objectives),
                "completion_percentage": 0.0,
                "quality_score": 0.0,
                "time_efficiency": 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to define success metrics: {e}")
            return {}
    
    def _hierarchical_planning(self, objectives: List[str], constraints: Dict[str, Any]) -> List[Task]:
        """Hierarchical planning strategy"""
        return self._decompose_objectives(objectives, constraints)
    
    def _temporal_planning(self, objectives: List[str], constraints: Dict[str, Any]) -> List[Task]:
        """Temporal planning strategy"""
        tasks = self._decompose_objectives(objectives, constraints)
        # Sort by priority and dependencies
        return sorted(tasks, key=lambda t: (t.priority.value, len(t.dependencies)))
    
    def _resource_based_planning(self, objectives: List[str], constraints: Dict[str, Any]) -> List[Task]:
        """Resource-based planning strategy"""
        tasks = self._decompose_objectives(objectives, constraints)
        # Sort by resource requirements
        return sorted(tasks, key=lambda t: sum(t.resources_required.values()) if isinstance(list(t.resources_required.values())[0], (int, float)) else 0)
    
    def _risk_aware_planning(self, objectives: List[str], constraints: Dict[str, Any]) -> List[Task]:
        """Risk-aware planning strategy"""
        tasks = self._decompose_objectives(objectives, constraints)
        # Prioritize low-risk tasks first
        return sorted(tasks, key=lambda t: t.priority.value)
    
    def get_plan_status(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get plan status"""
        try:
            plan = self.active_plans.get(plan_id) or self.completed_plans.get(plan_id)
            if not plan:
                return None
            
            completed_tasks = len([t for t in plan.tasks if t.status == "completed"])
            total_tasks = len(plan.tasks)
            
            return {
                "plan_id": plan_id,
                "name": plan.name,
                "status": plan.status.value,
                "progress": completed_tasks / total_tasks if total_tasks > 0 else 0,
                "completed_tasks": completed_tasks,
                "total_tasks": total_tasks,
                "estimated_completion": plan.estimated_completion,
                "risk_score": plan.risk_assessment.get("overall_risk_score", 0.0)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get plan status: {e}")
            return None
    
    def get_planner_status(self) -> Dict[str, Any]:
        """Get planner agent status"""
        try:
            return {
                "enabled": self.config.get("enabled", True),
                "active_plans": len(self.active_plans),
                "completed_plans": len(self.completed_plans),
                "total_tasks": sum(len(plan.tasks) for plan in self.active_plans.values()),
                "planning_strategies": list(self.planning_strategies.keys()),
                "default_strategy": self.config.get("default_planning_strategy", "hierarchical")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get planner status: {e}")
            return {"error": str(e)}

# Global instance
planner_agent = PlannerAgent()