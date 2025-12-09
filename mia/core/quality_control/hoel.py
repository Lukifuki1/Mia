#!/usr/bin/env python3
"""
HOEL - Human Oversight Enforcement Layer
Zagotavlja človeški nadzor nad kritičnimi operacijami in odločitvami
"""

import os
import json
import logging
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue

class OversightLevel(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Levels of human oversight"""
    NONE = "none"
    NOTIFICATION = "notification"
    APPROVAL_REQUIRED = "approval_required"
    MANDATORY_REVIEW = "mandatory_review"
    HUMAN_ONLY = "human_only"

class OperationType(Enum):
    """Types of operations requiring oversight"""
    SYSTEM_MODIFICATION = "system_modification"
    DATA_DELETION = "data_deletion"
    SECURITY_CHANGE = "security_change"
    MODEL_DEPLOYMENT = "model_deployment"
    CRITICAL_DECISION = "critical_decision"
    RESOURCE_ALLOCATION = "resource_allocation"
    USER_DATA_ACCESS = "user_data_access"
    EXTERNAL_COMMUNICATION = "external_communication"

class ApprovalStatus(Enum):
    """Approval status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    ESCALATED = "escalated"

@dataclass
class OversightRule:
    """Human oversight rule definition"""
    rule_id: str
    name: str
    description: str
    operation_type: OperationType
    oversight_level: OversightLevel
    conditions: Dict[str, Any]
    approvers: List[str]
    timeout_seconds: int
    escalation_rules: Dict[str, Any]
    enabled: bool
    created_at: float

@dataclass
class OversightRequest:
    """Request for human oversight"""
    request_id: str
    operation_type: OperationType
    operation_description: str
    oversight_level: OversightLevel
    requester: str
    operation_data: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    required_approvers: List[str]
    approval_status: ApprovalStatus
    approvals: List[Dict[str, Any]]
    rejections: List[Dict[str, Any]]
    created_at: float
    expires_at: float
    completed_at: Optional[float]
    execution_callback: Optional[str]

@dataclass
class HumanApproval:
    """Human approval record"""
    approval_id: str
    request_id: str
    approver: str
    decision: str  # "approve", "reject", "escalate"
    reasoning: str
    conditions: List[str]
    timestamp: float
    metadata: Dict[str, Any]

@dataclass
class OversightAuditLog:
    """Audit log entry for oversight activities"""
    log_id: str
    request_id: str
    action: str
    actor: str
    details: Dict[str, Any]
    timestamp: float

class HOEL:
    """Human Oversight Enforcement Layer"""
    
    def __init__(self, config_path: str = "mia/data/quality_control/hoel_config.json"):
        self.config_path = config_path
        self.hoel_dir = Path("mia/data/quality_control/hoel")
        self.hoel_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.HOEL")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Oversight state
        self.oversight_rules: Dict[str, OversightRule] = {}
        self.pending_requests: Dict[str, OversightRequest] = {}
        self.completed_requests: Dict[str, OversightRequest] = {}
        self.approvals: Dict[str, HumanApproval] = {}
        self.audit_logs: List[OversightAuditLog] = []
        
        # Request processing
        self.request_queue = queue.Queue()
        self.processing_active = False
        self.processing_thread: Optional[threading.Thread] = None
        
        # Registered callbacks
        self.execution_callbacks: Dict[str, Callable] = {}
        self.notification_callbacks: Dict[str, Callable] = {}
        
        # Load existing rules
        self._load_oversight_rules()
        
        self.logger.info("👁️ HOEL (Human Oversight Enforcement Layer) initialized")
    
    def _load_configuration(self) -> Dict:
        """Load HOEL configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load HOEL config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default HOEL configuration"""
        config = {
            "enabled": True,
            "default_timeout": 3600,  # 1 hour
            "escalation_timeout": 7200,  # 2 hours
            "max_pending_requests": 100,
            "audit_retention_days": 90,
            "default_approvers": ["admin", "supervisor"],
            "oversight_levels": {
                "none": {"description": "No oversight required"},
                "notification": {"description": "Notify humans but proceed"},
                "approval_required": {"description": "Require explicit approval"},
                "mandatory_review": {"description": "Require review and approval"},
                "human_only": {"description": "Only humans can perform this operation"}
            },
            "operation_types": {
                "system_modification": {
                    "default_level": "approval_required",
                    "default_approvers": ["admin"],
                    "timeout": 1800
                },
                "data_deletion": {
                    "default_level": "mandatory_review",
                    "default_approvers": ["admin", "data_protection_officer"],
                    "timeout": 3600
                },
                "security_change": {
                    "default_level": "mandatory_review",
                    "default_approvers": ["security_officer", "admin"],
                    "timeout": 1800
                },
                "model_deployment": {
                    "default_level": "approval_required",
                    "default_approvers": ["ml_engineer", "admin"],
                    "timeout": 3600
                },
                "critical_decision": {
                    "default_level": "human_only",
                    "default_approvers": ["human_supervisor"],
                    "timeout": 7200
                }
            },
            "risk_assessment": {
                "enabled": True,
                "factors": {
                    "data_sensitivity": {"weight": 0.3},
                    "system_impact": {"weight": 0.3},
                    "reversibility": {"weight": 0.2},
                    "user_impact": {"weight": 0.2}
                }
            },
            "escalation": {
                "enabled": True,
                "escalation_chain": ["supervisor", "manager", "director"],
                "auto_escalate_after": 3600  # 1 hour
            },
            "notifications": {
                "enabled": True,
                "channels": ["email", "slack", "dashboard"],
                "immediate_notification": ["critical_decision", "security_change"]
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _load_oversight_rules(self):
        """Load oversight rules"""
        try:
            rules_file = self.hoel_dir / "oversight_rules.json"
            if rules_file.exists():
                with open(rules_file, 'r') as f:
                    rules_data = json.load(f)
                
                for rule_data in rules_data:
                    rule = OversightRule(
                        rule_id=rule_data["rule_id"],
                        name=rule_data["name"],
                        description=rule_data["description"],
                        operation_type=OperationType(rule_data["operation_type"]),
                        oversight_level=OversightLevel(rule_data["oversight_level"]),
                        conditions=rule_data["conditions"],
                        approvers=rule_data["approvers"],
                        timeout_seconds=rule_data["timeout_seconds"],
                        escalation_rules=rule_data["escalation_rules"],
                        enabled=rule_data["enabled"],
                        created_at=rule_data["created_at"]
                    )
                    self.oversight_rules[rule.rule_id] = rule
            
            # Create default rules if none exist
            if not self.oversight_rules:
                self._create_default_rules()
            
            self.logger.info(f"✅ Loaded {len(self.oversight_rules)} oversight rules")
            
        except Exception as e:
            self.logger.error(f"Failed to load oversight rules: {e}")
            self._create_default_rules()
    
    def _create_default_rules(self):
        """Create default oversight rules"""
        try:
            default_rules = [
                {
                    "rule_id": "system_modification_critical",
                    "name": "Critical System Modifications",
                    "description": "Require approval for critical system modifications",
                    "operation_type": OperationType.SYSTEM_MODIFICATION,
                    "oversight_level": OversightLevel.MANDATORY_REVIEW,
                    "conditions": {"criticality": "high"},
                    "approvers": ["admin", "system_architect"],
                    "timeout_seconds": 1800,
                    "escalation_rules": {"auto_escalate": True, "escalate_to": "manager"},
                    "enabled": True
                },
                {
                    "rule_id": "data_deletion_any",
                    "name": "Data Deletion Operations",
                    "description": "Require approval for any data deletion",
                    "operation_type": OperationType.DATA_DELETION,
                    "oversight_level": OversightLevel.MANDATORY_REVIEW,
                    "conditions": {},
                    "approvers": ["admin", "data_protection_officer"],
                    "timeout_seconds": 3600,
                    "escalation_rules": {"auto_escalate": True, "escalate_to": "legal"},
                    "enabled": True
                },
                {
                    "rule_id": "security_changes",
                    "name": "Security Configuration Changes",
                    "description": "Require approval for security-related changes",
                    "operation_type": OperationType.SECURITY_CHANGE,
                    "oversight_level": OversightLevel.MANDATORY_REVIEW,
                    "conditions": {},
                    "approvers": ["security_officer", "admin"],
                    "timeout_seconds": 1800,
                    "escalation_rules": {"auto_escalate": True, "escalate_to": "ciso"},
                    "enabled": True
                },
                {
                    "rule_id": "model_deployment_production",
                    "name": "Production Model Deployment",
                    "description": "Require approval for production model deployments",
                    "operation_type": OperationType.MODEL_DEPLOYMENT,
                    "oversight_level": OversightLevel.APPROVAL_REQUIRED,
                    "conditions": {"environment": "production"},
                    "approvers": ["ml_engineer", "admin"],
                    "timeout_seconds": 3600,
                    "escalation_rules": {"auto_escalate": False},
                    "enabled": True
                },
                {
                    "rule_id": "critical_decisions",
                    "name": "Critical AI Decisions",
                    "description": "Human-only for critical decisions",
                    "operation_type": OperationType.CRITICAL_DECISION,
                    "oversight_level": OversightLevel.HUMAN_ONLY,
                    "conditions": {"impact": "high"},
                    "approvers": ["human_supervisor"],
                    "timeout_seconds": 7200,
                    "escalation_rules": {"auto_escalate": True, "escalate_to": "ethics_board"},
                    "enabled": True
                }
            ]
            
            for rule_data in default_rules:
                rule = OversightRule(
                    rule_id=rule_data["rule_id"],
                    name=rule_data["name"],
                    description=rule_data["description"],
                    operation_type=rule_data["operation_type"],
                    oversight_level=rule_data["oversight_level"],
                    conditions=rule_data["conditions"],
                    approvers=rule_data["approvers"],
                    timeout_seconds=rule_data["timeout_seconds"],
                    escalation_rules=rule_data["escalation_rules"],
                    enabled=rule_data["enabled"],
                    created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                )
                self.oversight_rules[rule.rule_id] = rule
            
            # Save rules
            self._save_oversight_rules()
            
        except Exception as e:
            self.logger.error(f"Failed to create default rules: {e}")
    
    def _save_oversight_rules(self):
        """Save oversight rules"""
        try:
            rules_data = []
            for rule in self.oversight_rules.values():
                rule_dict = asdict(rule)
                rule_dict["operation_type"] = rule.operation_type.value
                rule_dict["oversight_level"] = rule.oversight_level.value
                rules_data.append(rule_dict)
            
            rules_file = self.hoel_dir / "oversight_rules.json"
            with open(rules_file, 'w') as f:
                json.dump(rules_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save oversight rules: {e}")
    
    def start_processing(self):
        """Start request processing"""
        try:
            if self.processing_active:
                return
            
            self.processing_active = True
            self.processing_thread = threading.Thread(
                target=self._processing_loop,
                daemon=True
            )
            self.processing_thread.start()
            
            self.logger.info("👁️ HOEL processing started")
            
        except Exception as e:
            self.logger.error(f"Failed to start processing: {e}")
    
    def stop_processing(self):
        """Stop request processing"""
        try:
            self.processing_active = False
            
            if self.processing_thread:
                self.processing_thread.join(timeout=5.0)
            
            self.logger.info("👁️ HOEL processing stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop processing: {e}")
    
    def _processing_loop(self):
        """Main processing loop"""
        while self.processing_active:
            try:
                # Check for expired requests
                self._check_expired_requests()
                
                # Check for escalations
                self._check_escalations()
                
                # Process any queued requests
                try:
                    request = self.request_queue.get(timeout=1.0)
                    self._process_oversight_request(request)
                    self.request_queue.task_done()
                except queue.Empty:
                    pass
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                time.sleep(5)
    
    def request_oversight(self, operation_type: OperationType, operation_description: str,
                         requester: str, operation_data: Dict[str, Any] = None,
                         execution_callback: Callable = None) -> str:
        """Request human oversight for operation"""
        try:
            # Find applicable oversight rule
            applicable_rule = self._find_applicable_rule(operation_type, operation_data or {})
            
            if not applicable_rule:
                # No oversight required
                self.logger.info(f"No oversight required for {operation_type.value}")
                if execution_callback:
                    execution_callback(True, "No oversight required")
                return ""
            
            # Check if operation should be blocked entirely
            if applicable_rule.oversight_level == OversightLevel.HUMAN_ONLY:
                self.logger.warning(f"Operation {operation_type.value} requires human-only execution")
                if execution_callback:
                    execution_callback(False, "Human-only operation - AI execution not permitted")
                return ""
            
            # Create oversight request
            request_id = hashlib.sha256(f"{operation_type.value}_{requester}_{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}".encode()).hexdigest()[:16]
            
            # Perform risk assessment
            risk_assessment = self._assess_risk(operation_type, operation_data or {})
            
            # Determine required approvers
            required_approvers = applicable_rule.approvers.copy()
            
            # Calculate timeout
            timeout = applicable_rule.timeout_seconds
            expires_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 + timeout
            
            # Store execution callback
            callback_id = None
            if execution_callback:
                callback_id = f"callback_{request_id}"
                self.execution_callbacks[callback_id] = execution_callback
            
            # Create request
            request = OversightRequest(
                request_id=request_id,
                operation_type=operation_type,
                operation_description=operation_description,
                oversight_level=applicable_rule.oversight_level,
                requester=requester,
                operation_data=operation_data or {},
                risk_assessment=risk_assessment,
                required_approvers=required_approvers,
                approval_status=ApprovalStatus.PENDING,
                approvals=[],
                rejections=[],
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                expires_at=expires_at,
                completed_at=None,
                execution_callback=callback_id
            )
            
            # Store request
            self.pending_requests[request_id] = request
            
            # Add to processing queue
            self.request_queue.put(request)
            
            # Log audit entry
            self._log_audit_entry(request_id, "request_created", requester, {
                "operation_type": operation_type.value,
                "oversight_level": applicable_rule.oversight_level.value
            })
            
            self.logger.info(f"👁️ Oversight requested: {operation_description} (ID: {request_id})")
            
            return request_id
            
        except Exception as e:
            self.logger.error(f"Failed to request oversight: {e}")
            if execution_callback:
                execution_callback(False, f"Oversight request failed: {e}")
            return ""
    
    def _find_applicable_rule(self, operation_type: OperationType, operation_data: Dict[str, Any]) -> Optional[OversightRule]:
        """Find applicable oversight rule"""
        try:
            applicable_rules = []
            
            # Find rules matching operation type
            for rule in self.oversight_rules.values():
                if rule.operation_type == operation_type and rule.enabled:
                    # Check if conditions match
                    if self._check_rule_conditions(rule.conditions, operation_data):
                        applicable_rules.append(rule)
            
            if not applicable_rules:
                return None
            
            # Return rule with highest oversight level
            return max(applicable_rules, key=lambda r: list(OversightLevel).index(r.oversight_level))
            
        except Exception as e:
            self.logger.error(f"Failed to find applicable rule: {e}")
            return None
    
    def _check_rule_conditions(self, conditions: Dict[str, Any], operation_data: Dict[str, Any]) -> bool:
        """Check if rule conditions are met"""
        try:
            if not conditions:
                return True  # No conditions means rule applies
            
            for key, expected_value in conditions.items():
                if key not in operation_data:
                    return False
                
                actual_value = operation_data[key]
                
                # Simple equality check (could be extended for complex conditions)
                if actual_value != expected_value:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check rule conditions: {e}")
            return False
    
    def _assess_risk(self, operation_type: OperationType, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk of operation"""
        try:
            risk_config = self.config.get("risk_assessment", {})
            
            if not risk_config.get("enabled", True):
                return {"risk_score": 0.5, "factors": {}}
            
            factors = risk_config.get("factors", {})
            risk_scores = {}
            
            # Assess each risk factor
            for factor, config in factors.items():
                weight = config.get("weight", 0.25)
                
                if factor == "data_sensitivity":
                    score = self._assess_data_sensitivity(operation_data)
                elif factor == "system_impact":
                    score = self._assess_system_impact(operation_type, operation_data)
                elif factor == "reversibility":
                    score = self._assess_reversibility(operation_type, operation_data)
                elif factor == "user_impact":
                    score = self._assess_user_impact(operation_data)
                else:
                    score = 0.5  # Default moderate risk
                
                risk_scores[factor] = {"score": score, "weight": weight}
            
            # Calculate overall risk score
            total_weight = sum(factor["weight"] for factor in risk_scores.values())
            if total_weight > 0:
                overall_risk = sum(factor["score"] * factor["weight"] for factor in risk_scores.values()) / total_weight
            else:
                overall_risk = 0.5
            
            return {
                "risk_score": overall_risk,
                "factors": risk_scores,
                "risk_level": self._categorize_risk(overall_risk)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to assess risk: {e}")
            return {"risk_score": 0.5, "factors": {}, "error": str(e)}
    
    def _assess_data_sensitivity(self, operation_data: Dict[str, Any]) -> float:
        """Assess data sensitivity risk factor"""
        try:
            # Check for sensitive data indicators
            sensitive_indicators = ["personal", "financial", "medical", "confidential", "classified"]
            
            data_description = str(operation_data.get("data_description", "")).lower()
            data_type = str(operation_data.get("data_type", "")).lower()
            
            sensitivity_score = 0.0
            
            for indicator in sensitive_indicators:
                if indicator in data_description or indicator in data_type:
                    sensitivity_score += 0.2
            
            # Check for explicit sensitivity level
            sensitivity_level = operation_data.get("sensitivity_level", "").lower()
            if sensitivity_level in ["high", "critical"]:
                sensitivity_score += 0.5
            elif sensitivity_level in ["medium", "moderate"]:
                sensitivity_score += 0.3
            
            return min(1.0, sensitivity_score)
            
        except Exception as e:
            self.logger.error(f"Failed to assess data sensitivity: {e}")
            return 0.5
    
    def _assess_system_impact(self, operation_type: OperationType, operation_data: Dict[str, Any]) -> float:
        """Assess system impact risk factor"""
        try:
            # Base impact by operation type
            impact_scores = {
                OperationType.SYSTEM_MODIFICATION: 0.8,
                OperationType.DATA_DELETION: 0.9,
                OperationType.SECURITY_CHANGE: 0.9,
                OperationType.MODEL_DEPLOYMENT: 0.6,
                OperationType.CRITICAL_DECISION: 0.7,
                OperationType.RESOURCE_ALLOCATION: 0.5,
                OperationType.USER_DATA_ACCESS: 0.4,
                OperationType.EXTERNAL_COMMUNICATION: 0.3
            }
            
            base_impact = impact_scores.get(operation_type, 0.5)
            
            # Adjust based on scope
            scope = operation_data.get("scope", "").lower()
            if scope in ["global", "system-wide", "all"]:
                base_impact += 0.2
            elif scope in ["component", "module"]:
                base_impact += 0.1
            
            # Adjust based on criticality
            criticality = operation_data.get("criticality", "").lower()
            if criticality in ["critical", "high"]:
                base_impact += 0.2
            elif criticality == "medium":
                base_impact += 0.1
            
            return min(1.0, base_impact)
            
        except Exception as e:
            self.logger.error(f"Failed to assess system impact: {e}")
            return 0.5
    
    def _assess_reversibility(self, operation_type: OperationType, operation_data: Dict[str, Any]) -> float:
        """Assess reversibility risk factor"""
        try:
            # Operations that are hard to reverse have higher risk
            irreversible_operations = [
                OperationType.DATA_DELETION,
                OperationType.EXTERNAL_COMMUNICATION
            ]
            
            if operation_type in irreversible_operations:
                return 0.9
            
            # Check for explicit reversibility information
            reversible = operation_data.get("reversible", None)
            if reversible is False:
                return 0.8
            elif reversible is True:
                return 0.2
            
            # Check for backup availability
            has_backup = operation_data.get("has_backup", False)
            if has_backup:
                return 0.3
            
            return 0.5  # Default moderate risk
            
        except Exception as e:
            self.logger.error(f"Failed to assess reversibility: {e}")
            return 0.5
    
    def _assess_user_impact(self, operation_data: Dict[str, Any]) -> float:
        """Assess user impact risk factor"""
        try:
            # Check number of affected users
            affected_users = operation_data.get("affected_users", 0)
            
            if affected_users > 1000:
                return 0.9
            elif affected_users > 100:
                return 0.7
            elif affected_users > 10:
                return 0.5
            elif affected_users > 0:
                return 0.3
            else:
                return 0.1
            
        except Exception as e:
            self.logger.error(f"Failed to assess user impact: {e}")
            return 0.5
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk level"""
        if risk_score >= 0.8:
            return "high"
        elif risk_score >= 0.6:
            return "medium"
        elif risk_score >= 0.4:
            return "low"
        else:
            return "minimal"
    
    def _process_oversight_request(self, request: OversightRequest):
        """Process oversight request"""
        try:
            # Handle different oversight levels
            if request.oversight_level == OversightLevel.NOTIFICATION:
                # Just notify and proceed
                self._send_notification(request)
                self._approve_request(request, "system", "Notification-only operation")
                
            elif request.oversight_level in [OversightLevel.APPROVAL_REQUIRED, OversightLevel.MANDATORY_REVIEW]:
                # Send notifications to required approvers
                self._send_approval_notifications(request)
                
            # Log processing
            self._log_audit_entry(request.request_id, "request_processed", "system", {
                "oversight_level": request.oversight_level.value
            })
            
        except Exception as e:
            self.logger.error(f"Failed to process oversight request: {e}")
    
    def _send_notification(self, request: OversightRequest):
        """Send notification about operation"""
        try:
            notification_data = {
                "request_id": request.request_id,
                "operation_type": request.operation_type.value,
                "description": request.operation_description,
                "requester": request.requester,
                "risk_level": request.risk_assessment.get("risk_level", "unknown"),
                "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            }
            
            # Send to registered notification callbacks
            for callback_id, callback in self.notification_callbacks.items():
                try:
                    callback(notification_data)
                except Exception as e:
                    self.logger.error(f"Notification callback failed: {e}")
            
            self.logger.info(f"📢 Notification sent for operation: {request.operation_description}")
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
    
    def _send_approval_notifications(self, request: OversightRequest):
        """Send approval notifications to required approvers"""
        try:
            for approver in request.required_approvers:
                notification_data = {
                    "request_id": request.request_id,
                    "operation_type": request.operation_type.value,
                    "description": request.operation_description,
                    "requester": request.requester,
                    "risk_assessment": request.risk_assessment,
                    "expires_at": request.expires_at,
                    "approver": approver
                }
                
                # Send to registered notification callbacks
                for callback_id, callback in self.notification_callbacks.items():
                    try:
                        callback(notification_data)
                    except Exception as e:
                        self.logger.error(f"Approval notification callback failed: {e}")
            
            self.logger.info(f"📋 Approval notifications sent for: {request.operation_description}")
            
        except Exception as e:
            self.logger.error(f"Failed to send approval notifications: {e}")
    
    def provide_approval(self, request_id: str, approver: str, decision: str,
                        reasoning: str = "", conditions: List[str] = None) -> bool:
        """Provide human approval for request"""
        try:
            if request_id not in self.pending_requests:
                self.logger.error(f"Request not found: {request_id}")
                return False
            
            request = self.pending_requests[request_id]
            
            # Check if approver is authorized
            if approver not in request.required_approvers:
                self.logger.error(f"Unauthorized approver: {approver} for request {request_id}")
                return False
            
            # Check if request has expired
            if self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 > request.expires_at:
                self.logger.error(f"Request expired: {request_id}")
                return False
            
            # Create approval record
            approval_id = f"approval_{request_id}_{approver}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}"
            approval = HumanApproval(
                approval_id=approval_id,
                request_id=request_id,
                approver=approver,
                decision=decision,
                reasoning=reasoning,
                conditions=conditions or [],
                timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                metadata={}
            )
            
            # Store approval
            self.approvals[approval_id] = approval
            
            # Update request
            if decision == "approve":
                request.approvals.append(asdict(approval))
                
                # Check if all required approvals are received
                approved_by = set(a["approver"] for a in request.approvals)
                required_approvers = set(request.required_approvers)
                
                if approved_by.issuperset(required_approvers):
                    self._approve_request(request, approver, reasoning)
                
            elif decision == "reject":
                request.rejections.append(asdict(approval))
                self._reject_request(request, approver, reasoning)
                
            elif decision == "escalate":
                self._escalate_request(request, approver, reasoning)
            
            # Log audit entry
            self._log_audit_entry(request_id, f"approval_{decision}", approver, {
                "reasoning": reasoning,
                "conditions": conditions or []
            })
            
            self.logger.info(f"👤 Approval provided: {decision} by {approver} for {request_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to provide approval: {e}")
            return False
    
    def _approve_request(self, request: OversightRequest, approver: str, reasoning: str):
        """Approve oversight request"""
        try:
            request.approval_status = ApprovalStatus.APPROVED
            request.completed_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # Move to completed requests
            self.completed_requests[request.request_id] = request
            if request.request_id in self.pending_requests:
                del self.pending_requests[request.request_id]
            
            # Execute callback if provided
            if request.execution_callback and request.execution_callback in self.execution_callbacks:
                callback = self.execution_callbacks[request.execution_callback]
                try:
                    callback(True, f"Approved by {approver}: {reasoning}")
                except Exception as e:
                    self.logger.error(f"Execution callback failed: {e}")
                
                # Clean up callback
                del self.execution_callbacks[request.execution_callback]
            
            # Log audit entry
            self._log_audit_entry(request.request_id, "request_approved", approver, {
                "reasoning": reasoning
            })
            
            self.logger.info(f"✅ Request approved: {request.operation_description}")
            
        except Exception as e:
            self.logger.error(f"Failed to approve request: {e}")
    
    def _reject_request(self, request: OversightRequest, approver: str, reasoning: str):
        """Reject oversight request"""
        try:
            request.approval_status = ApprovalStatus.REJECTED
            request.completed_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # Move to completed requests
            self.completed_requests[request.request_id] = request
            if request.request_id in self.pending_requests:
                del self.pending_requests[request.request_id]
            
            # Execute callback if provided
            if request.execution_callback and request.execution_callback in self.execution_callbacks:
                callback = self.execution_callbacks[request.execution_callback]
                try:
                    callback(False, f"Rejected by {approver}: {reasoning}")
                except Exception as e:
                    self.logger.error(f"Execution callback failed: {e}")
                
                # Clean up callback
                del self.execution_callbacks[request.execution_callback]
            
            # Log audit entry
            self._log_audit_entry(request.request_id, "request_rejected", approver, {
                "reasoning": reasoning
            })
            
            self.logger.info(f"❌ Request rejected: {request.operation_description}")
            
        except Exception as e:
            self.logger.error(f"Failed to reject request: {e}")
    
    def _escalate_request(self, request: OversightRequest, escalator: str, reasoning: str):
        """Escalate oversight request"""
        try:
            request.approval_status = ApprovalStatus.ESCALATED
            
            # Add escalation approvers
            escalation_config = self.config.get("escalation", {})
            escalation_chain = escalation_config.get("escalation_chain", ["supervisor", "manager"])
            
            # Add next level approvers
            for escalation_approver in escalation_chain:
                if escalation_approver not in request.required_approvers:
                    request.required_approvers.append(escalation_approver)
            
            # Extend timeout
            request.expires_at += escalation_config.get("auto_escalate_after", 3600)
            
            # Send new notifications
            self._send_approval_notifications(request)
            
            # Log audit entry
            self._log_audit_entry(request.request_id, "request_escalated", escalator, {
                "reasoning": reasoning,
                "new_approvers": escalation_chain
            })
            
            self.logger.info(f"⬆️ Request escalated: {request.operation_description}")
            
        except Exception as e:
            self.logger.error(f"Failed to escalate request: {e}")
    
    def _check_expired_requests(self):
        """Check for expired requests"""
        try:
            current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            expired_requests = []
            
            for request_id, request in self.pending_requests.items():
                if current_time > request.expires_at:
                    expired_requests.append(request_id)
            
            for request_id in expired_requests:
                request = self.pending_requests[request_id]
                request.approval_status = ApprovalStatus.EXPIRED
                request.completed_at = current_time
                
                # Move to completed requests
                self.completed_requests[request_id] = request
                del self.pending_requests[request_id]
                
                # Execute callback with failure
                if request.execution_callback and request.execution_callback in self.execution_callbacks:
                    callback = self.execution_callbacks[request.execution_callback]
                    try:
                        callback(False, "Request expired - no approval received")
                    except Exception as e:
                        self.logger.error(f"Execution callback failed: {e}")
                    
                    # Clean up callback
                    del self.execution_callbacks[request.execution_callback]
                
                # Log audit entry
                self._log_audit_entry(request_id, "request_expired", "system", {})
                
                self.logger.warning(f"⏰ Request expired: {request.operation_description}")
            
        except Exception as e:
            self.logger.error(f"Failed to check expired requests: {e}")
    
    def _check_escalations(self):
        """Check for automatic escalations"""
        try:
            escalation_config = self.config.get("escalation", {})
            if not escalation_config.get("enabled", True):
                return
            
            auto_escalate_after = escalation_config.get("auto_escalate_after", 3600)
            current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            for request in self.pending_requests.values():
                if (request.approval_status == ApprovalStatus.PENDING and
                    current_time - request.created_at > auto_escalate_after):
                    
                    self._escalate_request(request, "system", "Automatic escalation due to timeout")
            
        except Exception as e:
            self.logger.error(f"Failed to check escalations: {e}")
    
    def _log_audit_entry(self, request_id: str, action: str, actor: str, details: Dict[str, Any]):
        """Log audit entry"""
        try:
            log_id = f"audit_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}_{len(self.audit_logs)}"
            
            audit_log = OversightAuditLog(
                log_id=log_id,
                request_id=request_id,
                action=action,
                actor=actor,
                details=details,
                timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            )
            
            self.audit_logs.append(audit_log)
            
            # Cleanup old audit logs
            retention_days = self.config.get("audit_retention_days", 90)
            cutoff_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - (retention_days * 86400)
            
            self.audit_logs = [log for log in self.audit_logs if log.timestamp > cutoff_time]
            
        except Exception as e:
            self.logger.error(f"Failed to log audit entry: {e}")
    
    def register_execution_callback(self, callback_id: str, callback: Callable):
        """Register execution callback"""
        self.execution_callbacks[callback_id] = callback
    
    def register_notification_callback(self, callback_id: str, callback: Callable):
        """Register notification callback"""
        self.notification_callbacks[callback_id] = callback
    
    def get_pending_requests(self, approver: str = None) -> List[OversightRequest]:
        """Get pending oversight requests"""
        try:
            requests = []
            
            for request in self.pending_requests.values():
                if approver and approver not in request.required_approvers:
                    continue
                
                requests.append(request)
            
            # Sort by creation time
            requests.sort(key=lambda r: r.created_at)
            
            return requests
            
        except Exception as e:
            self.logger.error(f"Failed to get pending requests: {e}")
            return []
    
    def get_request_details(self, request_id: str) -> Optional[OversightRequest]:
        """Get request details"""
        try:
            if request_id in self.pending_requests:
                return self.pending_requests[request_id]
            elif request_id in self.completed_requests:
                return self.completed_requests[request_id]
            else:
                return None
            
        except Exception as e:
            self.logger.error(f"Failed to get request details: {e}")
            return None
    
    def get_audit_logs(self, request_id: str = None, actor: str = None,
                      start_time: float = None, end_time: float = None) -> List[OversightAuditLog]:
        """Get audit logs with optional filtering"""
        try:
            logs = []
            
            for log in self.audit_logs:
                # Filter by request ID
                if request_id and log.request_id != request_id:
                    continue
                
                # Filter by actor
                if actor and log.actor != actor:
                    continue
                
                # Filter by time range
                if start_time and log.timestamp < start_time:
                    continue
                if end_time and log.timestamp > end_time:
                    continue
                
                logs.append(log)
            
            # Sort by timestamp (newest first)
            logs.sort(key=lambda l: l.timestamp, reverse=True)
            
            return logs
            
        except Exception as e:
            self.logger.error(f"Failed to get audit logs: {e}")
            return []
    
    def get_hoel_status(self) -> Dict[str, Any]:
        """Get HOEL status"""
        try:
            return {
                "enabled": self.config.get("enabled", True),
                "processing_active": self.processing_active,
                "oversight_rules": len(self.oversight_rules),
                "pending_requests": len(self.pending_requests),
                "completed_requests": len(self.completed_requests),
                "total_approvals": len(self.approvals),
                "audit_logs": len(self.audit_logs),
                "execution_callbacks": len(self.execution_callbacks),
                "notification_callbacks": len(self.notification_callbacks)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get HOEL status: {e}")
            return {"error": str(e)}

# Global instance
hoel = HOEL()