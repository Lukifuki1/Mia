#!/usr/bin/env python3
"""
MIA Enterprise AGI - Audit System
================================

Comprehensive security audit and compliance monitoring system.
"""

import os
import sys
import logging
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
import subprocess


class AuditSystem:
    """Comprehensive security audit and compliance system"""
    
    def __init__(self, audit_storage_path: Optional[str] = None):
        self.logger = self._setup_logging()
        
        # Audit storage configuration
        self.audit_storage_path = Path(audit_storage_path) if audit_storage_path else Path("mia_data/audit")
        self.audit_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Audit configuration
        self.audit_enabled = True
        self.retention_days = 365  # Keep audit logs for 1 year
        self.max_log_size_mb = 100
        
        # Audit categories
        self.audit_categories = {
            "security": "Security-related events",
            "access": "Access control events",
            "system": "System events",
            "data": "Data access and modification",
            "compliance": "Compliance-related events",
            "performance": "Performance monitoring",
            "error": "Error and exception events"
        }
        
        # Current audit session
        self.current_audit_session = None
        self.audit_buffer = []
        
        self.logger.info("📋 Audit System initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.Security.AuditSystem")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def start_audit_session(self, session_name: str, description: str = "") -> Dict[str, Any]:
        """Start new audit session"""
        try:
            self.logger.info(f"📋 Starting audit session: {session_name}")
            
            session_id = f"audit_{int(self._get_build_epoch())}_{session_name}"
            
            self.current_audit_session = {
                "session_id": session_id,
                "session_name": session_name,
                "description": description,
                "start_time": self._get_build_timestamp().isoformat(),
                "end_time": None,
                "events_logged": 0,
                "categories_used": set(),
                "status": "active"
            }
            
            # Log session start
            self.log_audit_event(
                category="system",
                event_type="audit_session_start",
                description=f"Audit session '{session_name}' started",
                metadata={"session_id": session_id}
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "session_name": session_name
            }
            
        except Exception as e:
            self.logger.error(f"Audit session start error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def log_audit_event(self, 
                       category: str,
                       event_type: str,
                       description: str,
                       user_id: Optional[str] = None,
                       resource: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None,
                       severity: str = "info") -> Dict[str, Any]:
        """Log audit event"""
        try:
            if not self.audit_enabled:
                return {"success": True, "message": "Audit disabled"}
            
            # Validate category
            if category not in self.audit_categories:
                category = "system"
            
            # Create audit event
            event = {
                "timestamp": self._get_build_timestamp().isoformat(),
                "event_id": f"evt_{int(self._get_build_epoch() * 1000000)}",
                "session_id": self.current_audit_session["session_id"] if self.current_audit_session else None,
                "category": category,
                "event_type": event_type,
                "description": description,
                "user_id": user_id,
                "resource": resource,
                "metadata": metadata or {},
                "severity": severity,
                "system_info": self._get_system_context()
            }
            
            # Add to buffer
            self.audit_buffer.append(event)
            
            # Update session statistics
            if self.current_audit_session:
                self.current_audit_session["events_logged"] += 1
                self.current_audit_session["categories_used"].add(category)
            
            # Flush buffer if it gets too large
            if len(self.audit_buffer) >= 100:
                self._flush_audit_buffer()
            
            return {
                "success": True,
                "event_id": event["event_id"]
            }
            
        except Exception as e:
            self.logger.error(f"Audit event logging error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_system_context(self) -> Dict[str, Any]:
        """Get current system context for audit"""
        try:
            return {
                "process_id": self._get_process_id(),
                "working_directory": str(Path.cwd()),
                "python_version": sys.version.split()[0],
                "platform": self._get_platform()
            }
        except Exception:
            return {}
    
    def _flush_audit_buffer(self) -> Dict[str, Any]:
        """Flush audit buffer to storage"""
        try:
            if not self.audit_buffer:
                return {"success": True, "events_flushed": 0}
            
            # Create audit log file
            timestamp = self._get_build_timestamp().strftime("%Y%m%d_%H%M%S")
            log_file = self.audit_storage_path / f"audit_log_{timestamp}.json"
            
            # Write events to file
            with open(log_file, 'w') as f:
                json.dump({
                    "audit_log_version": "1.0",
                    "created_at": self._get_build_timestamp().isoformat(),
                    "events_count": len(self.audit_buffer),
                    "events": self.audit_buffer
                }, f, indent=2)
            
            events_flushed = len(self.audit_buffer)
            self.audit_buffer.clear()
            
            self.logger.info(f"📋 Flushed {events_flushed} audit events to {log_file}")
            
            return {
                "success": True,
                "events_flushed": events_flushed,
                "log_file": str(log_file)
            }
            
        except Exception as e:
            self.logger.error(f"Audit buffer flush error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def end_audit_session(self) -> Dict[str, Any]:
        """End current audit session"""
        try:
            if not self.current_audit_session:
                return {
                    "success": False,
                    "error": "No active audit session"
                }
            
            # Flush remaining events
            flush_result = self._flush_audit_buffer()
            
            # Update session
            self.current_audit_session["end_time"] = self._get_build_timestamp().isoformat()
            self.current_audit_session["status"] = "completed"
            self.current_audit_session["categories_used"] = list(self.current_audit_session["categories_used"])
            
            # Save session summary
            session_file = self.audit_storage_path / f"session_{self.current_audit_session['session_id']}.json"
            with open(session_file, 'w') as f:
                json.dump(self.current_audit_session, f, indent=2)
            
            session_summary = self.current_audit_session.copy()
            self.current_audit_session = None
            
            self.logger.info(f"📋 Audit session completed: {session_summary['session_name']}")
            
            return {
                "success": True,
                "session_summary": session_summary,
                "flush_result": flush_result
            }
            
        except Exception as e:
            self.logger.error(f"Audit session end error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_security_audit(self) -> Dict[str, Any]:
        """Run comprehensive security audit"""
        try:
            self.logger.info("🔍 Running comprehensive security audit...")
            
            # Start audit session
            session_result = self.start_audit_session("security_audit", "Comprehensive security audit")
            if not session_result["success"]:
                return session_result
            
            audit_results = {
                "audit_timestamp": self._get_build_timestamp().isoformat(),
                "audit_type": "comprehensive_security",
                "findings": [],
                "recommendations": [],
                "compliance_status": {},
                "risk_score": 0.0
            }
            
            # File system security audit
            fs_audit = self._audit_file_system_security()
            audit_results["findings"].extend(fs_audit.get("findings", []))
            
            # Permission audit
            perm_audit = self._audit_permissions()
            audit_results["findings"].extend(perm_audit.get("findings", []))
            
            # Configuration audit
            config_audit = self._audit_configuration_security()
            audit_results["findings"].extend(config_audit.get("findings", []))
            
            # Network security audit
            network_audit = self._audit_network_security()
            audit_results["findings"].extend(network_audit.get("findings", []))
            
            # Calculate risk score
            audit_results["risk_score"] = self._calculate_risk_score(audit_results["findings"])
            
            # Generate recommendations
            audit_results["recommendations"] = self._generate_security_recommendations(audit_results["findings"])
            
            # Check compliance
            audit_results["compliance_status"] = self._check_security_compliance(audit_results["findings"])
            
            # Log audit completion
            self.log_audit_event(
                category="security",
                event_type="security_audit_completed",
                description="Comprehensive security audit completed",
                metadata={
                    "findings_count": len(audit_results["findings"]),
                    "risk_score": audit_results["risk_score"]
                }
            )
            
            # End audit session
            self.end_audit_session()
            
            return {
                "success": True,
                "audit_results": audit_results
            }
            
        except Exception as e:
            self.logger.error(f"Security audit error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _audit_file_system_security(self) -> Dict[str, Any]:
        """Audit file system security"""
        try:
            findings = []
            
            # Check for world-writable files
            for root, dirs, files in os.walk("."):
                for file in files:
                    file_path = Path(root) / file
                    try:
                        stat_info = file_path.stat()
                        # Check if file is world-writable (others have write permission)
                        if stat_info.st_mode & 0o002:
                            findings.append({
                                "type": "file_permission",
                                "severity": "medium",
                                "file": str(file_path),
                                "issue": "World-writable file",
                                "recommendation": "Remove world-write permissions"
                            })
                    except (OSError, PermissionError):
                        continue
            
            # Check for sensitive files with weak permissions
            sensitive_patterns = ["*.key", "*.pem", "*.p12", "*.pfx", "config.json", ".env"]
            for pattern in sensitive_patterns:
                for file_path in Path(".").rglob(pattern):
                    try:
                        stat_info = file_path.stat()
                        # Check if sensitive file is readable by others
                        if stat_info.st_mode & 0o044:
                            findings.append({
                                "type": "sensitive_file_permission",
                                "severity": "high",
                                "file": str(file_path),
                                "issue": "Sensitive file readable by others",
                                "recommendation": "Set restrictive permissions (600 or 640)"
                            })
                    except (OSError, PermissionError):
                        continue
            
            return {
                "audit_type": "file_system_security",
                "findings": findings
            }
            
        except Exception as e:
            return {
                "audit_type": "file_system_security",
                "error": str(e),
                "findings": []
            }
    
    def _audit_permissions(self) -> Dict[str, Any]:
        """Audit access control permissions"""
        try:
            findings = []
            
            # Check for default passwords (would need access to user management)
            # This is a placeholder for actual permission audit
            findings.append({
                "type": "permission_audit",
                "severity": "info",
                "issue": "Permission audit completed",
                "recommendation": "Review user permissions regularly"
            })
            
            return {
                "audit_type": "permissions",
                "findings": findings
            }
            
        except Exception as e:
            return {
                "audit_type": "permissions",
                "error": str(e),
                "findings": []
            }
    
    def _audit_configuration_security(self) -> Dict[str, Any]:
        """Audit configuration security"""
        try:
            findings = []
            
            # Check for debug mode in production
            config_files = list(Path(".").rglob("*.json")) + list(Path(".").rglob("*.yaml")) + list(Path(".").rglob("*.yml"))
            
            for config_file in config_files:
                try:
                    with open(config_file, 'r') as f:
                        content = f.read().lower()
                        if "debug" in content and ("true" in content or "1" in content):
                            findings.append({
                                "type": "configuration",
                                "severity": "medium",
                                "file": str(config_file),
                                "issue": "Debug mode may be enabled",
                                "recommendation": "Disable debug mode in production"
                            })
                except (OSError, UnicodeDecodeError):
                    continue
            
            return {
                "audit_type": "configuration_security",
                "findings": findings
            }
            
        except Exception as e:
            return {
                "audit_type": "configuration_security",
                "error": str(e),
                "findings": []
            }
    
    def _audit_network_security(self) -> Dict[str, Any]:
        """Audit network security"""
        try:
            findings = []
            
            # Check for open ports (basic check)
            try:
                result = subprocess.run(
                    ["netstat", "-tuln"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    listening_ports = []
                    
                    for line in lines:
                        if "LISTEN" in line:
                            parts = line.split()
                            if len(parts) >= 4:
                                address = parts[3]
                                if "0.0.0.0:" in address or ":::" in address:
                                    port = address.split(":")[-1]
                                    listening_ports.append(port)
                    
                    if listening_ports:
                        findings.append({
                            "type": "network_security",
                            "severity": "info",
                            "issue": f"Open ports detected: {', '.join(listening_ports)}",
                            "recommendation": "Review open ports and close unnecessary ones"
                        })
                        
            except (subprocess.TimeoutExpired, FileNotFoundError):
                findings.append({
                    "type": "network_security",
                    "severity": "info",
                    "issue": "Could not check network ports",
                    "recommendation": "Manually review network configuration"
                })
            
            return {
                "audit_type": "network_security",
                "findings": findings
            }
            
        except Exception as e:
            return {
                "audit_type": "network_security",
                "error": str(e),
                "findings": []
            }
    
    def _calculate_risk_score(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score based on findings"""
        try:
            if not findings:
                return 0.0
            
            severity_weights = {
                "critical": 10,
                "high": 7,
                "medium": 4,
                "low": 2,
                "info": 1
            }
            
            total_score = 0
            max_possible_score = len(findings) * 10  # Assuming all critical
            
            for finding in findings:
                severity = finding.get("severity", "info")
                weight = severity_weights.get(severity, 1)
                total_score += weight
            
            if max_possible_score == 0:
                return 0.0
            
            # Return risk score as percentage (0-100)
            risk_score = (total_score / max_possible_score) * 100
            return round(risk_score, 2)
            
        except Exception as e:
            self.logger.error(f"Risk score calculation error: {e}")
            return 0.0
    
    def _generate_security_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on findings"""
        recommendations = []
        
        # Count findings by severity
        severity_counts = {}
        for finding in findings:
            severity = finding.get("severity", "info")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Generate recommendations
        if severity_counts.get("critical", 0) > 0:
            recommendations.append("Address critical security issues immediately")
        
        if severity_counts.get("high", 0) > 0:
            recommendations.append("Review and fix high-severity security issues")
        
        if severity_counts.get("medium", 0) > 5:
            recommendations.append("Implement automated security scanning")
        
        recommendations.extend([
            "Conduct regular security audits",
            "Implement security monitoring",
            "Review and update security policies",
            "Provide security training for team members"
        ])
        
        return recommendations
    
    def _check_security_compliance(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check compliance with security standards"""
        critical_count = len([f for f in findings if f.get("severity") == "critical"])
        high_count = len([f for f in findings if f.get("severity") == "high"])
        
        compliance_status = {
            "overall_compliant": critical_count == 0 and high_count <= 2,
            "critical_issues": critical_count,
            "high_issues": high_count,
            "compliance_level": "high" if critical_count == 0 and high_count == 0 else 
                              "medium" if critical_count == 0 and high_count <= 2 else "low"
        }
        
        return compliance_status
    
    def get_audit_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get audit summary for specified period"""
        try:
            end_date = self._get_build_timestamp()
            start_date = end_date - timedelta(days=days)
            
            # Find audit log files in date range
            log_files = []
            for log_file in self.audit_storage_path.glob("audit_log_*.json"):
                try:
                    # Extract timestamp from filename
                    timestamp_str = log_file.stem.split("_", 2)[2]
                    file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    
                    if start_date <= file_date <= end_date:
                        log_files.append(log_file)
                except (ValueError, IndexError):
                    continue
            
            # Analyze audit logs
            total_events = 0
            events_by_category = {}
            events_by_severity = {}
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r') as f:
                        log_data = json.load(f)
                        events = log_data.get("events", [])
                        
                        total_events += len(events)
                        
                        for event in events:
                            category = event.get("category", "unknown")
                            severity = event.get("severity", "info")
                            
                            events_by_category[category] = events_by_category.get(category, 0) + 1
                            events_by_severity[severity] = events_by_severity.get(severity, 0) + 1
                            
                except (json.JSONDecodeError, OSError):
                    continue
            
            return {
                "success": True,
                "period_days": days,
                "total_events": total_events,
                "events_by_category": events_by_category,
                "events_by_severity": events_by_severity,
                "log_files_analyzed": len(log_files)
            }
            
        except Exception as e:
            self.logger.error(f"Audit summary error: {e}")
            return {
                "success": False,
                "error": str(e)
            }