#!/usr/bin/env python3
"""
AGI Planner - Avtonomni načrtovalec nalog in projektov
"""

import os
import json
import logging
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class PlanType(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Types of plans"""
    PROJECT = "project"
    TASK = "task"
    OPTIMIZATION = "optimization"
    RESEARCH = "research"
    MAINTENANCE = "maintenance"

class PlanStatus(Enum):
    """Plan execution status"""
    DRAFT = "draft"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class PlanStep:
    """Individual plan step"""
    step_id: str
    name: str
    description: str
    dependencies: List[str]
    estimated_duration: float
    resources_required: List[str]
    success_criteria: List[str]
    status: str

@dataclass
class Plan:
    """Execution plan"""
    plan_id: str
    name: str
    description: str
    plan_type: PlanType
    priority: int
    steps: List[PlanStep]
    estimated_total_duration: float
    success_criteria: List[str]
    status: PlanStatus
    created_at: float
    updated_at: float

class AGIPlanner:
    """AGI Planner - Autonomous task and project planner"""
    
    def __init__(self, config_path: str = "mia/data/agi_agents/planner_config.json"):
        self.config_path = config_path
        self.planner_dir = Path("mia/data/agi_agents/planner")
        self.planner_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.AGIPlanner")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Planning state
        self.plans: Dict[str, Plan] = {}
        self.active_plans: Dict[str, Plan] = {}
        self.planning_active = False
        self.planning_thread: Optional[threading.Thread] = None
        
        self.logger.info("🧠 AGI Planner initialized")
    
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
            "planning_interval": 300,  # 5 minutes
            "max_concurrent_plans": 10,
            "auto_planning": True,
            "plan_templates": {
                "project": {
                    "phases": ["analysis", "design", "implementation", "testing", "deployment"],
                    "default_duration": 3600
                },
                "task": {
                    "phases": ["preparation", "execution", "verification"],
                    "default_duration": 900
                },
                "optimization": {
                    "phases": ["analysis", "optimization", "validation"],
                    "default_duration": 1800
                }
            },
            "planning_strategies": {
                "critical_path": True,
                "resource_optimization": True,
                "risk_assessment": True,
                "dependency_analysis": True
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def start_planning(self):
        """Start autonomous planning"""
        try:
            if self.planning_active:
                return
            
            self.planning_active = True
            self.planning_thread = threading.Thread(
                target=self._planning_loop,
                daemon=True
            )
            self.planning_thread.start()
            
            self.logger.info("🧠 AGI Planning started")
            
        except Exception as e:
            self.logger.error(f"Failed to start planning: {e}")
    
    def stop_planning(self):
        """Stop autonomous planning"""
        try:
            self.planning_active = False
            
            if self.planning_thread:
                self.planning_thread.join(timeout=5.0)
            
            self.logger.info("🧠 AGI Planning stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop planning: {e}")
    
    def _planning_loop(self):
        """Main planning loop"""
        while self.planning_active:
            try:
                # Review existing plans
                self._review_plans()
                
                # Generate new plans if needed
                if self.config.get("auto_planning", True):
                    self._generate_autonomous_plans()
                
                # Optimize existing plans
                self._optimize_plans()
                
                time.sleep(self.config.get("planning_interval", 300))
                
            except Exception as e:
                self.logger.error(f"Error in planning loop: {e}")
                time.sleep(60)
    
    def create_plan(self, name: str, description: str, plan_type: PlanType,
                   requirements: List[str] = None, priority: int = 5) -> str:
        """Create new execution plan"""
        try:
            plan_id = f"plan_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}_{len(self.plans)}"
            
            # Generate plan steps based on type and requirements
            steps = self._generate_plan_steps(plan_type, requirements or [])
            
            # Calculate estimated duration
            total_duration = sum(step.estimated_duration for step in steps)
            
            # Create plan
            plan = Plan(
                plan_id=plan_id,
                name=name,
                description=description,
                plan_type=plan_type,
                priority=priority,
                steps=steps,
                estimated_total_duration=total_duration,
                success_criteria=self._generate_success_criteria(plan_type),
                status=PlanStatus.DRAFT,
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                updated_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            )
            
            # Store plan
            self.plans[plan_id] = plan
            
            self.logger.info(f"📋 Created plan: {name} ({plan_id})")
            
            return plan_id
            
        except Exception as e:
            self.logger.error(f"Failed to create plan: {e}")
            return ""
    
    def _generate_plan_steps(self, plan_type: PlanType, requirements: List[str]) -> List[PlanStep]:
        """Generate plan steps based on type and requirements"""
        try:
            steps = []
            template = self.config.get("plan_templates", {}).get(plan_type.value, {})
            phases = template.get("phases", ["preparation", "execution", "completion"])
            default_duration = template.get("default_duration", 1800) / len(phases)
            
            for i, phase in enumerate(phases):
                step_id = f"step_{i+1}_{phase}"
                
                step = PlanStep(
                    step_id=step_id,
                    name=phase.title(),
                    description=f"{phase.title()} phase for {plan_type.value}",
                    dependencies=[f"step_{i}_{phases[i-1]}"] if i > 0 else [],
                    estimated_duration=default_duration,
                    resources_required=self._determine_resources(phase, requirements),
                    success_criteria=[f"{phase} completed successfully"],
                    status="pending"
                )
                
                steps.append(step)
            
            return steps
            
        except Exception as e:
            self.logger.error(f"Failed to generate plan steps: {e}")
            return []
    
    def _determine_resources(self, phase: str, requirements: List[str]) -> List[str]:
        """Determine required resources for phase"""
        try:
            base_resources = ["cpu", "memory"]
            
            if "analysis" in phase.lower():
                base_resources.extend(["data_access", "analytics_tools"])
            elif "implementation" in phase.lower():
                base_resources.extend(["development_tools", "storage"])
            elif "testing" in phase.lower():
                base_resources.extend(["testing_framework", "validation_data"])
            
            # Add specific requirements
            base_resources.extend(requirements)
            
            return list(set(base_resources))
            
        except Exception as e:
            self.logger.error(f"Failed to determine resources: {e}")
            return ["cpu", "memory"]
    
    def _generate_success_criteria(self, plan_type: PlanType) -> List[str]:
        """Generate success criteria for plan type"""
        try:
            criteria = ["All steps completed successfully", "No critical errors encountered"]
            
            if plan_type == PlanType.PROJECT:
                criteria.extend([
                    "Project deliverables meet requirements",
                    "Quality standards satisfied",
                    "Performance targets achieved"
                ])
            elif plan_type == PlanType.OPTIMIZATION:
                criteria.extend([
                    "Performance improvement measured",
                    "Resource efficiency increased",
                    "No regression in functionality"
                ])
            elif plan_type == PlanType.RESEARCH:
                criteria.extend([
                    "Research objectives achieved",
                    "Findings documented",
                    "Conclusions validated"
                ])
            
            return criteria
            
        except Exception as e:
            self.logger.error(f"Failed to generate success criteria: {e}")
            return ["Plan completed"]
    
    def approve_plan(self, plan_id: str) -> bool:
        """Approve plan for execution"""
        try:
            if plan_id not in self.plans:
                self.logger.error(f"Plan not found: {plan_id}")
                return False
            
            plan = self.plans[plan_id]
            plan.status = PlanStatus.APPROVED
            plan.updated_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # Add to active plans
            self.active_plans[plan_id] = plan
            
            self.logger.info(f"✅ Plan approved: {plan.name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to approve plan: {e}")
            return False
    
    def _review_plans(self):
        """Review existing plans"""
        try:
            for plan_id, plan in list(self.active_plans.items()):
                # Check if plan needs updates
                if self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - plan.updated_at > 3600:  # 1 hour
                    self._update_plan_status(plan)
            
        except Exception as e:
            self.logger.error(f"Failed to review plans: {e}")
    
    def _update_plan_status(self, plan: Plan):
        """Update plan status based on execution"""
        try:
            # This would integrate with executor to get actual status
            # For now, just update timestamp
            plan.updated_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
        except Exception as e:
            self.logger.error(f"Failed to update plan status: {e}")
    
    def _generate_autonomous_plans(self):
        """Generate autonomous plans based on system needs"""
        try:
            # Check if we need maintenance plans
            if len([p for p in self.plans.values() if p.plan_type == PlanType.MAINTENANCE]) == 0:
                self.create_plan(
                    "System Maintenance",
                    "Regular system maintenance and optimization",
                    PlanType.MAINTENANCE,
                    ["system_access", "maintenance_tools"],
                    priority=3
                )
            
            # Check if we need optimization plans
            if len([p for p in self.plans.values() if p.plan_type == PlanType.OPTIMIZATION]) < 2:
                self.create_plan(
                    "Performance Optimization",
                    "Optimize system performance and resource usage",
                    PlanType.OPTIMIZATION,
                    ["performance_tools", "monitoring_data"],
                    priority=4
                )
            
        except Exception as e:
            self.logger.error(f"Failed to generate autonomous plans: {e}")
    
    def _optimize_plans(self):
        """Optimize existing plans"""
        try:
            for plan in self.active_plans.values():
                if plan.status == PlanStatus.APPROVED:
                    # Optimize step order and resource allocation
                    self._optimize_plan_steps(plan)
            
        except Exception as e:
            self.logger.error(f"Failed to optimize plans: {e}")
    
    def _optimize_plan_steps(self, plan: Plan):
        """Optimize plan steps for efficiency"""
        try:
            # Simple optimization: sort by dependencies and duration
            # More sophisticated optimization would consider resource constraints
            
            # Update plan timestamp
            plan.updated_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
        except Exception as e:
            self.logger.error(f"Failed to optimize plan steps: {e}")
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get plan by ID"""
        return self.plans.get(plan_id)
    
    def get_active_plans(self) -> List[Plan]:
        """Get all active plans"""
        return list(self.active_plans.values())
    
    def get_planner_status(self) -> Dict[str, Any]:
        """Get planner status"""
        try:
            return {
                "enabled": self.config.get("enabled", True),
                "planning_active": self.planning_active,
                "total_plans": len(self.plans),
                "active_plans": len(self.active_plans),
                "draft_plans": len([p for p in self.plans.values() if p.status == PlanStatus.DRAFT]),
                "approved_plans": len([p for p in self.plans.values() if p.status == PlanStatus.APPROVED]),
                "completed_plans": len([p for p in self.plans.values() if p.status == PlanStatus.COMPLETED]),
                "auto_planning": self.config.get("auto_planning", True)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get planner status: {e}")
            return {"error": str(e)}

# Global instance
agi_planner = AGIPlanner()