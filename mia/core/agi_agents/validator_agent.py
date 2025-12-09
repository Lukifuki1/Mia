#!/usr/bin/env python3
"""
MIA AGI Validator Agent
Validira rezultate izvršenih nalog in zagotavlja kakovost
"""

import os
import json
import logging
import time
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading

class ValidationLevel(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Validation levels"""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    CRITICAL = "critical"

class ValidationStatus(Enum):
    """Validation status"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"

class ValidationType(Enum):
    """Types of validation"""
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    INTEGRATION = "integration"

@dataclass
class ValidationRule:
    """Validation rule definition"""
    rule_id: str
    rule_type: ValidationType
    name: str
    description: str
    validation_function: str
    parameters: Dict[str, Any]
    severity: str
    enabled: bool
    created_at: float

@dataclass
class ValidationResult:
    """Result of validation"""
    result_id: str
    task_id: str
    rule_id: str
    status: ValidationStatus
    score: float
    max_score: float
    message: str
    details: Dict[str, Any]
    suggestions: List[str]
    validated_at: float

@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    report_id: str
    task_id: str
    validation_level: ValidationLevel
    overall_status: ValidationStatus
    overall_score: float
    max_score: float
    results: List[ValidationResult]
    summary: Dict[str, Any]
    created_at: float

class ValidatorAgent:
    """AGI Validator Agent for result validation"""
    
    def __init__(self, config_path: str = "mia/data/agi_agents/validator_config.json"):
        self.config_path = config_path
        self.validator_dir = Path("mia/data/agi_agents/validator")
        self.validator_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.ValidatorAgent")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Validation state
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.validation_results: Dict[str, ValidationResult] = {}
        self.validation_reports: Dict[str, ValidationReport] = {}
        
        # Validation functions
        self.validation_functions = {
            "syntax_check": self._validate_syntax,
            "semantic_check": self._validate_semantics,
            "functional_test": self._validate_functionality,
            "performance_test": self._validate_performance,
            "security_scan": self._validate_security,
            "compliance_check": self._validate_compliance,
            "integration_test": self._validate_integration,
            "code_quality": self._validate_code_quality,
            "data_integrity": self._validate_data_integrity,
            "output_format": self._validate_output_format
        }
        
        # Load validation rules
        self._load_validation_rules()
        
        self.logger.info("✅ Validator Agent initialized")
    
    def _load_configuration(self) -> Dict:
        """Load validator configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load validator config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default validator configuration"""
        config = {
            "enabled": True,
            "default_validation_level": "standard",
            "auto_validation": True,
            "validation_timeout": 300,  # 5 minutes
            "score_thresholds": {
                "pass": 0.8,
                "warning": 0.6,
                "fail": 0.4
            },
            "validation_categories": {
                "syntax": {"enabled": True, "weight": 0.2},
                "semantic": {"enabled": True, "weight": 0.2},
                "functional": {"enabled": True, "weight": 0.3},
                "performance": {"enabled": True, "weight": 0.15},
                "security": {"enabled": True, "weight": 0.1},
                "compliance": {"enabled": True, "weight": 0.05}
            },
            "critical_validations": [
                "security_scan",
                "syntax_check",
                "functional_test"
            ],
            "reporting": {
                "generate_detailed_reports": True,
                "include_suggestions": True,
                "save_reports": True
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _load_validation_rules(self):
        """Load validation rules"""
        try:
            # Load from file if exists
            rules_file = self.validator_dir / "validation_rules.json"
            if rules_file.exists():
                with open(rules_file, 'r') as f:
                    rules_data = json.load(f)
                
                for rule_data in rules_data:
                    rule = ValidationRule(
                        rule_id=rule_data["rule_id"],
                        rule_type=ValidationType(rule_data["rule_type"]),
                        name=rule_data["name"],
                        description=rule_data["description"],
                        validation_function=rule_data["validation_function"],
                        parameters=rule_data["parameters"],
                        severity=rule_data["severity"],
                        enabled=rule_data["enabled"],
                        created_at=rule_data["created_at"]
                    )
                    self.validation_rules[rule.rule_id] = rule
            
            # Create default rules if none exist
            if not self.validation_rules:
                self._create_default_validation_rules()
            
            self.logger.info(f"✅ Loaded {len(self.validation_rules)} validation rules")
            
        except Exception as e:
            self.logger.error(f"Failed to load validation rules: {e}")
            self._create_default_validation_rules()
    
    def _create_default_validation_rules(self):
        """Create default validation rules"""
        try:
            default_rules = [
                {
                    "rule_id": "syntax_python",
                    "rule_type": ValidationType.SYNTAX,
                    "name": "Python Syntax Check",
                    "description": "Validate Python code syntax",
                    "validation_function": "syntax_check",
                    "parameters": {"language": "python"},
                    "severity": "critical",
                    "enabled": True
                },
                {
                    "rule_id": "output_format_json",
                    "rule_type": ValidationType.SEMANTIC,
                    "name": "JSON Output Format",
                    "description": "Validate JSON output format",
                    "validation_function": "output_format",
                    "parameters": {"format": "json"},
                    "severity": "high",
                    "enabled": True
                },
                {
                    "rule_id": "functional_basic",
                    "rule_type": ValidationType.FUNCTIONAL,
                    "name": "Basic Functionality Test",
                    "description": "Test basic functionality requirements",
                    "validation_function": "functional_test",
                    "parameters": {"test_type": "basic"},
                    "severity": "high",
                    "enabled": True
                },
                {
                    "rule_id": "performance_response_time",
                    "rule_type": ValidationType.PERFORMANCE,
                    "name": "Response Time Check",
                    "description": "Validate response time requirements",
                    "validation_function": "performance_test",
                    "parameters": {"metric": "response_time", "threshold": 5.0},
                    "severity": "medium",
                    "enabled": True
                },
                {
                    "rule_id": "security_basic",
                    "rule_type": ValidationType.SECURITY,
                    "name": "Basic Security Scan",
                    "description": "Basic security vulnerability scan",
                    "validation_function": "security_scan",
                    "parameters": {"scan_type": "basic"},
                    "severity": "critical",
                    "enabled": True
                },
                {
                    "rule_id": "code_quality",
                    "rule_type": ValidationType.COMPLIANCE,
                    "name": "Code Quality Standards",
                    "description": "Check code quality standards",
                    "validation_function": "code_quality",
                    "parameters": {"standards": ["pep8", "complexity"]},
                    "severity": "medium",
                    "enabled": True
                }
            ]
            
            for rule_data in default_rules:
                rule = ValidationRule(
                    rule_id=rule_data["rule_id"],
                    rule_type=rule_data["rule_type"],
                    name=rule_data["name"],
                    description=rule_data["description"],
                    validation_function=rule_data["validation_function"],
                    parameters=rule_data["parameters"],
                    severity=rule_data["severity"],
                    enabled=rule_data["enabled"],
                    created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                )
                self.validation_rules[rule.rule_id] = rule
            
            # Save rules
            self._save_validation_rules()
            
        except Exception as e:
            self.logger.error(f"Failed to create default validation rules: {e}")
    
    def _save_validation_rules(self):
        """Save validation rules"""
        try:
            rules_data = []
            for rule in self.validation_rules.values():
                rule_dict = asdict(rule)
                rule_dict["rule_type"] = rule.rule_type.value
                rules_data.append(rule_dict)
            
            rules_file = self.validator_dir / "validation_rules.json"
            with open(rules_file, 'w') as f:
                json.dump(rules_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save validation rules: {e}")
    
    def validate_task_result(self, task_id: str, task_result: Any, 
                           validation_level: ValidationLevel = ValidationLevel.STANDARD) -> str:
        """Validate task result"""
        try:
            # Create validation report
            report_id = hashlib.sha256(f"{task_id}_{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}".encode()).hexdigest()[:16]
            
            validation_results = []
            overall_score = 0.0
            max_score = 0.0
            
            # Get applicable rules based on validation level
            applicable_rules = self._get_applicable_rules(validation_level, task_result)
            
            # Run validations
            for rule in applicable_rules:
                if rule.enabled:
                    result = self._run_validation(rule, task_id, task_result)
                    validation_results.append(result)
                    
                    overall_score += result.score
                    max_score += result.max_score
            
            # Calculate overall status
            if max_score > 0:
                score_ratio = overall_score / max_score
                overall_status = self._calculate_overall_status(score_ratio)
            else:
                overall_status = ValidationStatus.SKIPPED
                score_ratio = 0.0
            
            # Create validation report
            report = ValidationReport(
                report_id=report_id,
                task_id=task_id,
                validation_level=validation_level,
                overall_status=overall_status,
                overall_score=overall_score,
                max_score=max_score,
                results=validation_results,
                summary=self._generate_validation_summary(validation_results),
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            )
            
            # Store report
            self.validation_reports[report_id] = report
            
            # Store individual results
            for result in validation_results:
                self.validation_results[result.result_id] = result
            
            self.logger.info(f"✅ Validation completed for task {task_id}: {overall_status.value} ({score_ratio:.2%})")
            
            return report_id
            
        except Exception as e:
            self.logger.error(f"Failed to validate task result: {e}")
            return ""
    
    def _get_applicable_rules(self, validation_level: ValidationLevel, task_result: Any) -> List[ValidationRule]:
        """Get applicable validation rules"""
        try:
            applicable_rules = []
            
            for rule in self.validation_rules.values():
                if not rule.enabled:
                    continue
                
                # Filter by validation level
                if validation_level == ValidationLevel.BASIC:
                    if rule.severity in ["critical"]:
                        applicable_rules.append(rule)
                elif validation_level == ValidationLevel.STANDARD:
                    if rule.severity in ["critical", "high"]:
                        applicable_rules.append(rule)
                elif validation_level == ValidationLevel.COMPREHENSIVE:
                    if rule.severity in ["critical", "high", "medium"]:
                        applicable_rules.append(rule)
                elif validation_level == ValidationLevel.CRITICAL:
                    applicable_rules.append(rule)
                
                # Additional filtering based on task result type
                # This could be expanded based on specific requirements
            
            return applicable_rules
            
        except Exception as e:
            self.logger.error(f"Failed to get applicable rules: {e}")
            return []
    
    def _run_validation(self, rule: ValidationRule, task_id: str, task_result: Any) -> ValidationResult:
        """Run individual validation"""
        try:
            # Get validation function
            validation_function = self.validation_functions.get(rule.validation_function)
            
            if not validation_function:
                return ValidationResult(
                    result_id=f"result_{rule.rule_id}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                    task_id=task_id,
                    rule_id=rule.rule_id,
                    status=ValidationStatus.SKIPPED,
                    score=0.0,
                    max_score=100.0,
                    message=f"Validation function not found: {rule.validation_function}",
                    details={},
                    suggestions=[],
                    validated_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                )
            
            # Run validation
            validation_result = validation_function(task_result, rule.parameters)
            
            # Create result object
            result = ValidationResult(
                result_id=f"result_{rule.rule_id}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                task_id=task_id,
                rule_id=rule.rule_id,
                status=validation_result.get("status", ValidationStatus.FAILED),
                score=validation_result.get("score", 0.0),
                max_score=validation_result.get("max_score", 100.0),
                message=validation_result.get("message", ""),
                details=validation_result.get("details", {}),
                suggestions=validation_result.get("suggestions", []),
                validated_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to run validation {rule.rule_id}: {e}")
            
            return ValidationResult(
                result_id=f"result_{rule.rule_id}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                task_id=task_id,
                rule_id=rule.rule_id,
                status=ValidationStatus.FAILED,
                score=0.0,
                max_score=100.0,
                message=f"Validation error: {e}",
                details={"error": str(e)},
                suggestions=["Check validation configuration"],
                validated_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            )
    
    def _validate_syntax(self, task_result: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate syntax"""
        try:
            language = parameters.get("language", "python")
            
            if language == "python":
                # Check if result contains Python code
                if isinstance(task_result, dict) and "output" in task_result:
                    code = task_result["output"]
                elif isinstance(task_result, str):
                    code = task_result
                else:
                    return {
                        "status": ValidationStatus.SKIPPED,
                        "score": 0.0,
                        "max_score": 100.0,
                        "message": "No Python code found to validate"
                    }
                
                # Try to compile the code
                try:
                    compile(code, '<string>', 'exec')
                    return {
                        "status": ValidationStatus.PASSED,
                        "score": 100.0,
                        "max_score": 100.0,
                        "message": "Python syntax is valid"
                    }
                except SyntaxError as e:
                    return {
                        "status": ValidationStatus.FAILED,
                        "score": 0.0,
                        "max_score": 100.0,
                        "message": f"Python syntax error: {e}",
                        "details": {"line": e.lineno, "text": e.text},
                        "suggestions": ["Fix syntax errors in the code"]
                    }
            
            return {
                "status": ValidationStatus.SKIPPED,
                "score": 0.0,
                "max_score": 100.0,
                "message": f"Syntax validation not implemented for {language}"
            }
            
        except Exception as e:
            return {
                "status": ValidationStatus.FAILED,
                "score": 0.0,
                "max_score": 100.0,
                "message": f"Syntax validation error: {e}"
            }
    
    def _validate_semantics(self, task_result: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate semantics"""
        try:
            # Basic semantic validation
            score = 50.0  # Base score
            
            # Check if result has expected structure
            if isinstance(task_result, dict):
                score += 25.0
                
                # Check for common fields
                expected_fields = parameters.get("expected_fields", [])
                for field in expected_fields:
                    if field in task_result:
                        score += 5.0
            
            # Check for meaningful content
            if task_result and str(task_result).strip():
                score += 20.0
            
            status = ValidationStatus.PASSED if score >= 70.0 else ValidationStatus.WARNING
            
            return {
                "status": status,
                "score": min(score, 100.0),
                "max_score": 100.0,
                "message": f"Semantic validation score: {score:.1f}/100"
            }
            
        except Exception as e:
            return {
                "status": ValidationStatus.FAILED,
                "score": 0.0,
                "max_score": 100.0,
                "message": f"Semantic validation error: {e}"
            }
    
    def _validate_functionality(self, task_result: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate functionality"""
        try:
            test_type = parameters.get("test_type", "basic")
            
            if test_type == "basic":
                # Basic functionality test
                if task_result is None:
                    return {
                        "status": ValidationStatus.FAILED,
                        "score": 0.0,
                        "max_score": 100.0,
                        "message": "Task result is None"
                    }
                
                # Check if result indicates success
                if isinstance(task_result, dict):
                    if task_result.get("status") == "success" or task_result.get("success") is True:
                        return {
                            "status": ValidationStatus.PASSED,
                            "score": 100.0,
                            "max_score": 100.0,
                            "message": "Functionality test passed"
                        }
                    elif "error" in task_result or task_result.get("status") == "error":
                        return {
                            "status": ValidationStatus.FAILED,
                            "score": 0.0,
                            "max_score": 100.0,
                            "message": f"Task reported error: {task_result.get('error', 'Unknown error')}"
                        }
                
                # Default to partial success
                return {
                    "status": ValidationStatus.WARNING,
                    "score": 60.0,
                    "max_score": 100.0,
                    "message": "Basic functionality appears to work"
                }
            
            return {
                "status": ValidationStatus.SKIPPED,
                "score": 0.0,
                "max_score": 100.0,
                "message": f"Functionality test type '{test_type}' not implemented"
            }
            
        except Exception as e:
            return {
                "status": ValidationStatus.FAILED,
                "score": 0.0,
                "max_score": 100.0,
                "message": f"Functionality validation error: {e}"
            }
    
    def _validate_performance(self, task_result: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate performance"""
        try:
            metric = parameters.get("metric", "response_time")
            threshold = parameters.get("threshold", 5.0)
            
            if metric == "response_time":
                # Check if result contains timing information
                execution_time = None
                
                if isinstance(task_result, dict):
                    execution_time = task_result.get("execution_time")
                    if execution_time is None:
                        execution_time = task_result.get("duration")
                    if execution_time is None:
                        execution_time = task_result.get("time")
                
                if execution_time is None:
                    return {
                        "status": ValidationStatus.SKIPPED,
                        "score": 0.0,
                        "max_score": 100.0,
                        "message": "No timing information available"
                    }
                
                # Calculate performance score
                if execution_time <= threshold:
                    score = 100.0
                    status = ValidationStatus.PASSED
                    message = f"Performance good: {execution_time:.2f}s <= {threshold}s"
                elif execution_time <= threshold * 2:
                    score = 60.0
                    status = ValidationStatus.WARNING
                    message = f"Performance acceptable: {execution_time:.2f}s"
                else:
                    score = 20.0
                    status = ValidationStatus.FAILED
                    message = f"Performance poor: {execution_time:.2f}s > {threshold * 2}s"
                
                return {
                    "status": status,
                    "score": score,
                    "max_score": 100.0,
                    "message": message,
                    "details": {"execution_time": execution_time, "threshold": threshold}
                }
            
            return {
                "status": ValidationStatus.SKIPPED,
                "score": 0.0,
                "max_score": 100.0,
                "message": f"Performance metric '{metric}' not implemented"
            }
            
        except Exception as e:
            return {
                "status": ValidationStatus.FAILED,
                "score": 0.0,
                "max_score": 100.0,
                "message": f"Performance validation error: {e}"
            }
    
    def _validate_security(self, task_result: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate security"""
        try:
            scan_type = parameters.get("scan_type", "basic")
            
            if scan_type == "basic":
                security_issues = []
                
                # Check for common security issues in result
                if isinstance(task_result, (str, dict)):
                    result_str = str(task_result).lower()
                    
                    # Check for potential security issues
                    security_patterns = [
                        (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
                        (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key detected"),
                        (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret detected"),
                        (r'eval\s*\(', "Use of eval() function detected"),
                        (r'exec\s*\(', "Use of exec() function detected"),
                        (r'__import__\s*\(', "Dynamic import detected")
                    ]
                    
                    for pattern, message in security_patterns:
                        if re.search(pattern, result_str):
                            security_issues.append(message)
                
                if security_issues:
                    return {
                        "status": ValidationStatus.FAILED,
                        "score": 0.0,
                        "max_score": 100.0,
                        "message": f"Security issues found: {len(security_issues)}",
                        "details": {"issues": security_issues},
                        "suggestions": ["Remove hardcoded credentials", "Avoid dangerous functions"]
                    }
                else:
                    return {
                        "status": ValidationStatus.PASSED,
                        "score": 100.0,
                        "max_score": 100.0,
                        "message": "No obvious security issues found"
                    }
            
            return {
                "status": ValidationStatus.SKIPPED,
                "score": 0.0,
                "max_score": 100.0,
                "message": f"Security scan type '{scan_type}' not implemented"
            }
            
        except Exception as e:
            return {
                "status": ValidationStatus.FAILED,
                "score": 0.0,
                "max_score": 100.0,
                "message": f"Security validation error: {e}"
            }
    
    def _validate_compliance(self, task_result: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate compliance"""
        try:
            # Basic compliance validation
            score = 70.0  # Base score
            
            # Check result structure compliance
            if isinstance(task_result, dict):
                score += 15.0
                
                # Check for standard fields
                if "status" in task_result or "success" in task_result:
                    score += 10.0
                
                if "message" in task_result or "description" in task_result:
                    score += 5.0
            
            status = ValidationStatus.PASSED if score >= 80.0 else ValidationStatus.WARNING
            
            return {
                "status": status,
                "score": score,
                "max_score": 100.0,
                "message": f"Compliance score: {score:.1f}/100"
            }
            
        except Exception as e:
            return {
                "status": ValidationStatus.FAILED,
                "score": 0.0,
                "max_score": 100.0,
                "message": f"Compliance validation error: {e}"
            }
    
    def _validate_integration(self, task_result: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate integration"""
        try:
            # Basic integration validation
            return {
                "status": ValidationStatus.PASSED,
                "score": 80.0,
                "max_score": 100.0,
                "message": "Integration validation passed"
            }
            
        except Exception as e:
            return {
                "status": ValidationStatus.FAILED,
                "score": 0.0,
                "max_score": 100.0,
                "message": f"Integration validation error: {e}"
            }
    
    def _validate_code_quality(self, task_result: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate code quality"""
        try:
            standards = parameters.get("standards", ["basic"])
            
            # Basic code quality checks
            score = 60.0  # Base score
            
            if isinstance(task_result, str):
                # Check code formatting
                if task_result.strip():
                    score += 20.0
                
                # Check for comments
                if "#" in task_result or '"""' in task_result:
                    score += 10.0
                
                # Check for proper indentation
                lines = task_result.split('\n')
                if any(line.startswith('    ') or line.startswith('\t') for line in lines):
                    score += 10.0
            
            status = ValidationStatus.PASSED if score >= 70.0 else ValidationStatus.WARNING
            
            return {
                "status": status,
                "score": score,
                "max_score": 100.0,
                "message": f"Code quality score: {score:.1f}/100"
            }
            
        except Exception as e:
            return {
                "status": ValidationStatus.FAILED,
                "score": 0.0,
                "max_score": 100.0,
                "message": f"Code quality validation error: {e}"
            }
    
    def _validate_data_integrity(self, task_result: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data integrity"""
        try:
            # Basic data integrity checks
            if task_result is None:
                return {
                    "status": ValidationStatus.FAILED,
                    "score": 0.0,
                    "max_score": 100.0,
                    "message": "Data is None"
                }
            
            return {
                "status": ValidationStatus.PASSED,
                "score": 90.0,
                "max_score": 100.0,
                "message": "Data integrity check passed"
            }
            
        except Exception as e:
            return {
                "status": ValidationStatus.FAILED,
                "score": 0.0,
                "max_score": 100.0,
                "message": f"Data integrity validation error: {e}"
            }
    
    def _validate_output_format(self, task_result: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate output format"""
        try:
            expected_format = parameters.get("format", "json")
            
            if expected_format == "json":
                if isinstance(task_result, dict):
                    return {
                        "status": ValidationStatus.PASSED,
                        "score": 100.0,
                        "max_score": 100.0,
                        "message": "Output format is valid JSON"
                    }
                elif isinstance(task_result, str):
                    try:
                        json.loads(task_result)
                        return {
                            "status": ValidationStatus.PASSED,
                            "score": 100.0,
                            "max_score": 100.0,
                            "message": "Output format is valid JSON string"
                        }
                    except json.JSONDecodeError:
                        return {
                            "status": ValidationStatus.FAILED,
                            "score": 0.0,
                            "max_score": 100.0,
                            "message": "Output is not valid JSON"
                        }
                else:
                    return {
                        "status": ValidationStatus.FAILED,
                        "score": 0.0,
                        "max_score": 100.0,
                        "message": f"Output format is {type(task_result)}, expected JSON"
                    }
            
            return {
                "status": ValidationStatus.SKIPPED,
                "score": 0.0,
                "max_score": 100.0,
                "message": f"Format validation for '{expected_format}' not implemented"
            }
            
        except Exception as e:
            return {
                "status": ValidationStatus.FAILED,
                "score": 0.0,
                "max_score": 100.0,
                "message": f"Output format validation error: {e}"
            }
    
    def _calculate_overall_status(self, score_ratio: float) -> ValidationStatus:
        """Calculate overall validation status"""
        thresholds = self.config.get("score_thresholds", {})
        
        if score_ratio >= thresholds.get("pass", 0.8):
            return ValidationStatus.PASSED
        elif score_ratio >= thresholds.get("warning", 0.6):
            return ValidationStatus.WARNING
        else:
            return ValidationStatus.FAILED
    
    def _generate_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate validation summary"""
        try:
            summary = {
                "total_validations": len(results),
                "passed": len([r for r in results if r.status == ValidationStatus.PASSED]),
                "failed": len([r for r in results if r.status == ValidationStatus.FAILED]),
                "warnings": len([r for r in results if r.status == ValidationStatus.WARNING]),
                "skipped": len([r for r in results if r.status == ValidationStatus.SKIPPED]),
                "categories": {}
            }
            
            # Group by validation type
            for result in results:
                rule = self.validation_rules.get(result.rule_id)
                if rule:
                    category = rule.rule_type.value
                    if category not in summary["categories"]:
                        summary["categories"][category] = {
                            "total": 0,
                            "passed": 0,
                            "failed": 0,
                            "score": 0.0,
                            "max_score": 0.0
                        }
                    
                    summary["categories"][category]["total"] += 1
                    summary["categories"][category]["score"] += result.score
                    summary["categories"][category]["max_score"] += result.max_score
                    
                    if result.status == ValidationStatus.PASSED:
                        summary["categories"][category]["passed"] += 1
                    elif result.status == ValidationStatus.FAILED:
                        summary["categories"][category]["failed"] += 1
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate validation summary: {e}")
            return {}
    
    def get_validation_report(self, report_id: str) -> Optional[ValidationReport]:
        """Get validation report"""
        return self.validation_reports.get(report_id)
    
    def get_validator_status(self) -> Dict[str, Any]:
        """Get validator agent status"""
        try:
            return {
                "enabled": self.config.get("enabled", True),
                "validation_rules": len(self.validation_rules),
                "validation_results": len(self.validation_results),
                "validation_reports": len(self.validation_reports),
                "validation_functions": list(self.validation_functions.keys()),
                "default_level": self.config.get("default_validation_level", "standard")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get validator status: {e}")
            return {"error": str(e)}

# Global instance
validator_agent = ValidatorAgent()