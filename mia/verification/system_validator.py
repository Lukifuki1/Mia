#!/usr/bin/env python3
"""
MIA Enterprise AGI - System Validator
=====================================

System validation and environment verification.
"""

import logging
import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import psutil


class SystemValidator:
    """System validation and environment verification"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = self._setup_logging()
        
        # Validation configuration
        self.config = {
            "min_python_version": (3, 8),
            "min_memory_gb": 2,
            "min_disk_space_gb": 5,
            "min_cpu_cores": 2,
            "required_modules": ["json", "hashlib", "logging", "pathlib"],
            "validation_timeout": 60
        }
        
        # Validation results storage
        self.validation_results = {}
        
        self.logger.info("🔍 System Validator initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.Verification.SystemValidator")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _get_deterministic_time(self) -> float:
        """Return deterministic time for testing"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC
    
    def validate_python_environment(self) -> Dict[str, Any]:
        """Validate Python environment"""
        try:
            validation_result = {
                "validation_type": "python_environment",
                "validation_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "checks": [],
                "success": True
            }
            
            # Check Python version
            current_version = sys.version_info[:2]
            min_version = self.config["min_python_version"]
            
            if current_version >= min_version:
                validation_result["checks"].append({
                    "check": "python_version",
                    "status": "passed",
                    "current": f"{current_version[0]}.{current_version[1]}",
                    "required": f"{min_version[0]}.{min_version[1]}",
                    "message": f"Python version {current_version[0]}.{current_version[1]} meets requirement"
                })
            else:
                validation_result["checks"].append({
                    "check": "python_version",
                    "status": "failed",
                    "current": f"{current_version[0]}.{current_version[1]}",
                    "required": f"{min_version[0]}.{min_version[1]}",
                    "message": f"Python version {current_version[0]}.{current_version[1]} below requirement"
                })
                validation_result["success"] = False
            
            # Check required modules
            missing_modules = []
            for module in self.config["required_modules"]:
                try:
                    __import__(module)
                    validation_result["checks"].append({
                        "check": f"module_{module}",
                        "status": "passed",
                        "message": f"Module {module} is available"
                    })
                except ImportError:
                    missing_modules.append(module)
                    validation_result["checks"].append({
                        "check": f"module_{module}",
                        "status": "failed",
                        "message": f"Module {module} is missing"
                    })
                    validation_result["success"] = False
            
            # Check Python executable
            python_executable = sys.executable
            if os.path.exists(python_executable):
                validation_result["checks"].append({
                    "check": "python_executable",
                    "status": "passed",
                    "value": python_executable,
                    "message": f"Python executable found: {python_executable}"
                })
            else:
                validation_result["checks"].append({
                    "check": "python_executable",
                    "status": "failed",
                    "value": python_executable,
                    "message": f"Python executable not found: {python_executable}"
                })
                validation_result["success"] = False
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Python environment validation error: {e}")
            return {
                "validation_type": "python_environment",
                "success": False,
                "error": str(e),
                "validation_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
    
    def validate_system_resources(self) -> Dict[str, Any]:
        """Validate system resources"""
        try:
            validation_result = {
                "validation_type": "system_resources",
                "validation_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "checks": [],
                "success": True
            }
            
            # Check memory
            memory_gb = psutil.virtual_memory().total / (1024**3)
            min_memory = self.config["min_memory_gb"]
            
            if memory_gb >= min_memory:
                validation_result["checks"].append({
                    "check": "memory",
                    "status": "passed",
                    "current_gb": round(memory_gb, 2),
                    "required_gb": min_memory,
                    "message": f"Memory {memory_gb:.2f}GB meets requirement"
                })
            else:
                validation_result["checks"].append({
                    "check": "memory",
                    "status": "failed",
                    "current_gb": round(memory_gb, 2),
                    "required_gb": min_memory,
                    "message": f"Memory {memory_gb:.2f}GB below requirement"
                })
                validation_result["success"] = False
            
            # Check CPU cores
            cpu_cores = psutil.cpu_count()
            min_cores = self.config["min_cpu_cores"]
            
            if cpu_cores >= min_cores:
                validation_result["checks"].append({
                    "check": "cpu_cores",
                    "status": "passed",
                    "current": cpu_cores,
                    "required": min_cores,
                    "message": f"CPU cores {cpu_cores} meets requirement"
                })
            else:
                validation_result["checks"].append({
                    "check": "cpu_cores",
                    "status": "failed",
                    "current": cpu_cores,
                    "required": min_cores,
                    "message": f"CPU cores {cpu_cores} below requirement"
                })
                validation_result["success"] = False
            
            # Check disk space
            try:
                disk_usage = psutil.disk_usage(str(self.project_root))
                disk_free_gb = disk_usage.free / (1024**3)
                min_disk = self.config["min_disk_space_gb"]
                
                if disk_free_gb >= min_disk:
                    validation_result["checks"].append({
                        "check": "disk_space",
                        "status": "passed",
                        "current_gb": round(disk_free_gb, 2),
                        "required_gb": min_disk,
                        "message": f"Disk space {disk_free_gb:.2f}GB meets requirement"
                    })
                else:
                    validation_result["checks"].append({
                        "check": "disk_space",
                        "status": "failed",
                        "current_gb": round(disk_free_gb, 2),
                        "required_gb": min_disk,
                        "message": f"Disk space {disk_free_gb:.2f}GB below requirement"
                    })
                    validation_result["success"] = False
                    
            except Exception as e:
                validation_result["checks"].append({
                    "check": "disk_space",
                    "status": "error",
                    "message": f"Disk space check error: {e}"
                })
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"System resources validation error: {e}")
            return {
                "validation_type": "system_resources",
                "success": False,
                "error": str(e),
                "validation_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
    
    def validate_file_system_permissions(self) -> Dict[str, Any]:
        """Validate file system permissions"""
        try:
            validation_result = {
                "validation_type": "filesystem_permissions",
                "validation_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "checks": [],
                "success": True
            }
            
            # Check project root access
            if self.project_root.exists() and self.project_root.is_dir():
                validation_result["checks"].append({
                    "check": "project_root_access",
                    "status": "passed",
                    "path": str(self.project_root),
                    "message": "Project root is accessible"
                })
            else:
                validation_result["checks"].append({
                    "check": "project_root_access",
                    "status": "failed",
                    "path": str(self.project_root),
                    "message": "Project root is not accessible"
                })
                validation_result["success"] = False
            
            # Check write permissions
            test_file = self.project_root / "test_write_permission.tmp"
            try:
                test_file.write_text("test")
                test_file.unlink()
                validation_result["checks"].append({
                    "check": "write_permission",
                    "status": "passed",
                    "message": "Write permission available"
                })
            except Exception as e:
                validation_result["checks"].append({
                    "check": "write_permission",
                    "status": "failed",
                    "message": f"Write permission error: {e}"
                })
                validation_result["success"] = False
            
            # Check read permissions
            try:
                list(self.project_root.iterdir())
                validation_result["checks"].append({
                    "check": "read_permission",
                    "status": "passed",
                    "message": "Read permission available"
                })
            except Exception as e:
                validation_result["checks"].append({
                    "check": "read_permission",
                    "status": "failed",
                    "message": f"Read permission error: {e}"
                })
                validation_result["success"] = False
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"File system permissions validation error: {e}")
            return {
                "validation_type": "filesystem_permissions",
                "success": False,
                "error": str(e),
                "validation_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
    
    def validate_network_connectivity(self) -> Dict[str, Any]:
        """Validate network connectivity"""
        try:
            validation_result = {
                "validation_type": "network_connectivity",
                "validation_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "checks": [],
                "success": True
            }
            
            # Check DNS resolution
            try:
                import socket
                socket.gethostbyname("google.com")
                validation_result["checks"].append({
                    "check": "dns_resolution",
                    "status": "passed",
                    "message": "DNS resolution working"
                })
            except Exception as e:
                validation_result["checks"].append({
                    "check": "dns_resolution",
                    "status": "failed",
                    "message": f"DNS resolution error: {e}"
                })
                validation_result["success"] = False
            
            # Check internet connectivity (optional)
            try:
                import urllib.request
                urllib.request.urlopen("https://www.google.com", timeout=10)
                validation_result["checks"].append({
                    "check": "internet_connectivity",
                    "status": "passed",
                    "message": "Internet connectivity available"
                })
            except Exception as e:
                validation_result["checks"].append({
                    "check": "internet_connectivity",
                    "status": "warning",
                    "message": f"Internet connectivity limited: {e}"
                })
                # Don't fail validation for internet connectivity
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Network connectivity validation error: {e}")
            return {
                "validation_type": "network_connectivity",
                "success": False,
                "error": str(e),
                "validation_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
    
    def validate_dependencies(self) -> Dict[str, Any]:
        """Validate system dependencies"""
        try:
            validation_result = {
                "validation_type": "dependencies",
                "validation_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "checks": [],
                "success": True
            }
            
            # Check common system tools
            system_tools = ["git", "python", "pip"]
            
            for tool in system_tools:
                try:
                    result = subprocess.run(
                        [tool, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        validation_result["checks"].append({
                            "check": f"tool_{tool}",
                            "status": "passed",
                            "version": result.stdout.strip()[:100],  # Limit output
                            "message": f"Tool {tool} is available"
                        })
                    else:
                        validation_result["checks"].append({
                            "check": f"tool_{tool}",
                            "status": "failed",
                            "message": f"Tool {tool} returned error: {result.stderr.strip()[:100]}"
                        })
                        
                except subprocess.TimeoutExpired:
                    validation_result["checks"].append({
                        "check": f"tool_{tool}",
                        "status": "failed",
                        "message": f"Tool {tool} command timeout"
                    })
                except FileNotFoundError:
                    validation_result["checks"].append({
                        "check": f"tool_{tool}",
                        "status": "warning",
                        "message": f"Tool {tool} not found (optional)"
                    })
                except Exception as e:
                    validation_result["checks"].append({
                        "check": f"tool_{tool}",
                        "status": "error",
                        "message": f"Tool {tool} check error: {e}"
                    })
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Dependencies validation error: {e}")
            return {
                "validation_type": "dependencies",
                "success": False,
                "error": str(e),
                "validation_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive system validation"""
        try:
            self.logger.info("🔍 Running comprehensive system validation...")
            
            validation_id = f"validation_{int(self._get_deterministic_time())}"
            
            comprehensive_result = {
                "validation_id": validation_id,
                "validation_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "validation_phases": {},
                "overall_success": True,
                "summary": {}
            }
            
            # Phase 1: Python environment
            python_result = self.validate_python_environment()
            comprehensive_result["validation_phases"]["python_environment"] = python_result
            
            if not python_result.get("success", False):
                comprehensive_result["overall_success"] = False
            
            # Phase 2: System resources
            resources_result = self.validate_system_resources()
            comprehensive_result["validation_phases"]["system_resources"] = resources_result
            
            if not resources_result.get("success", False):
                comprehensive_result["overall_success"] = False
            
            # Phase 3: File system permissions
            permissions_result = self.validate_file_system_permissions()
            comprehensive_result["validation_phases"]["filesystem_permissions"] = permissions_result
            
            if not permissions_result.get("success", False):
                comprehensive_result["overall_success"] = False
            
            # Phase 4: Network connectivity
            network_result = self.validate_network_connectivity()
            comprehensive_result["validation_phases"]["network_connectivity"] = network_result
            
            if not network_result.get("success", False):
                comprehensive_result["overall_success"] = False
            
            # Phase 5: Dependencies
            dependencies_result = self.validate_dependencies()
            comprehensive_result["validation_phases"]["dependencies"] = dependencies_result
            
            if not dependencies_result.get("success", False):
                comprehensive_result["overall_success"] = False
            
            # Generate summary
            comprehensive_result["summary"] = self._generate_validation_summary(
                comprehensive_result["validation_phases"]
            )
            
            # Store results
            self.validation_results[validation_id] = comprehensive_result
            
            self.logger.info(f"🔍 Comprehensive system validation completed: {validation_id}")
            
            return comprehensive_result
            
        except Exception as e:
            self.logger.error(f"Comprehensive system validation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "validation_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
    
    def _generate_validation_summary(self, validation_phases: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation summary"""
        try:
            summary = {
                "total_phases": len(validation_phases),
                "successful_phases": 0,
                "failed_phases": 0,
                "total_checks": 0,
                "passed_checks": 0,
                "failed_checks": 0,
                "warning_checks": 0,
                "phase_details": {}
            }
            
            for phase_name, phase_result in validation_phases.items():
                if phase_result.get("success", False):
                    summary["successful_phases"] += 1
                    summary["phase_details"][phase_name] = "passed"
                else:
                    summary["failed_phases"] += 1
                    summary["phase_details"][phase_name] = "failed"
                
                # Count checks
                checks = phase_result.get("checks", [])
                summary["total_checks"] += len(checks)
                
                for check in checks:
                    status = check.get("status", "unknown")
                    if status == "passed":
                        summary["passed_checks"] += 1
                    elif status == "failed":
                        summary["failed_checks"] += 1
                    elif status == "warning":
                        summary["warning_checks"] += 1
            
            summary["success_rate"] = (
                summary["successful_phases"] / summary["total_phases"] * 100
                if summary["total_phases"] > 0 else 0
            )
            
            summary["check_success_rate"] = (
                summary["passed_checks"] / summary["total_checks"] * 100
                if summary["total_checks"] > 0 else 0
            )
            
            return summary
            
        except Exception as e:
            return {
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get system validator status"""
        return {
            "total_validations": len(self.validation_results),
            "config": self.config
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate system validation report"""
        try:
            status = self.get_status()
            
            return {
                "report_type": "system_validation",
                "timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "statistics": status,
                "recent_validations": list(self.validation_results.values())[-5:],  # Last 5
                "recommendations": self.get_recommendations()
            }
            
        except Exception as e:
            self.logger.error(f"System validation report generation error: {e}")
            return {
                "error": str(e)
            }
    
    def get_recommendations(self) -> List[str]:
        """Get system validation recommendations"""
        recommendations = []
        
        status = self.get_status()
        
        if status["total_validations"] == 0:
            recommendations.append("Run initial system validation")
        
        recommendations.extend([
            "Regular system health checks",
            "Monitor system resource usage",
            "Keep system dependencies updated",
            "Validate environment before deployments"
        ])
        
        return recommendations