#!/usr/bin/env python3
"""
🛡️ MIA Enterprise AGI - Finalna Varnostna Implementacija
=======================================================

Modularized security implementation using dedicated security modules.
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import modularized security components
from mia.security import (
    SecurityCore,
    EncryptionManager,
    AccessControl,
    AuditSystem
)


class SecurityVulnerabilityScanner:
    """Modularized security vulnerability scanner"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = self._setup_logging()
        
        # Initialize modular security components
        self.security_core = SecurityCore(project_root)
        self.encryption_manager = EncryptionManager()
        self.access_control = AccessControl()
        self.audit_system = AuditSystem()
        
        # Results storage
        self.scan_results = {}
        self.security_report = {}
        
        self.logger.info("🛡️ Modularized Security Scanner initialized")
        
        self.vulnerabilities_found = []
        self.fixes_applied = []
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("MIA.SecurityScanner")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def scan_and_fix_vulnerabilities(self) -> Dict[str, Any]:
        """Run comprehensive security scan using modular components"""
        try:
            self.logger.info("🔍 Starting comprehensive security scan...")
            
            # 1. Start audit session
            audit_session = self.audit_system.start_audit_session(
                "security_scan", 
                "Comprehensive security vulnerability scan"
            )
            
            # 2. Run core vulnerability scan
            self.logger.info("🔍 Running core vulnerability scan...")
            self.scan_results = self.security_core.scan_vulnerabilities()
            
            # 3. Run security audit
            self.logger.info("🔍 Running security audit...")
            audit_results = self.audit_system.run_security_audit()
            
            # 4. Check encryption status
            self.logger.info("🔐 Checking encryption status...")
            encryption_status = self.encryption_manager.get_encryption_status()
            
            # 5. Check access control status
            self.logger.info("🔐 Checking access control status...")
            access_control_status = self.access_control.get_system_status()
            
            # 6. Generate comprehensive security report
            comprehensive_report = self._generate_comprehensive_security_report(
                self.scan_results,
                audit_results,
                encryption_status,
                access_control_status
            )
            
            # 7. End audit session
            self.audit_system.end_audit_session()
            
            self.logger.info("✅ Comprehensive security scan completed")
            
            return comprehensive_report
            
        except Exception as e:
            self.logger.error(f"Security scan error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_comprehensive_security_report(self,
                                              scan_results: Dict[str, Any],
                                              audit_results: Dict[str, Any],
                                              encryption_status: Dict[str, Any],
                                              access_control_status: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        try:
            # Calculate overall security score
            vulnerability_score = scan_results.get("security_score", 0.0)
            audit_score = 1.0 - (audit_results.get("audit_results", {}).get("risk_score", 0.0) / 100.0)
            encryption_score = 1.0 if encryption_status.get("master_key_loaded", False) else 0.5
            access_control_score = 0.9 if access_control_status.get("total_users", 0) > 0 else 0.3
            
            overall_score = (vulnerability_score + audit_score + encryption_score + access_control_score) / 4
            
            comprehensive_report = {
                "timestamp": datetime.now().isoformat(),
                "scan_type": "comprehensive_security",
                "overall_security_score": round(overall_score, 3),
                "component_scores": {
                    "vulnerability_scan": vulnerability_score,
                    "security_audit": audit_score,
                    "encryption": encryption_score,
                    "access_control": access_control_score
                },
                "vulnerability_scan_results": scan_results,
                "security_audit_results": audit_results,
                "encryption_status": encryption_status,
                "access_control_status": access_control_status,
                "security_grade": self._calculate_security_grade(overall_score),
                "recommendations": self._generate_security_recommendations(overall_score, scan_results, audit_results),
                "compliance_status": self._check_overall_compliance(overall_score, scan_results, audit_results)
            }
            
            # Save report
            self._save_security_report(comprehensive_report)
            
            return comprehensive_report
            
        except Exception as e:
            self.logger.error(f"Security report generation error: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_security_grade(self, score: float) -> str:
        """Calculate security grade based on score"""
        if score >= 0.95:
            return "A+"
        elif score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
    
    def _generate_security_recommendations(self, 
                                         overall_score: float,
                                         scan_results: Dict[str, Any],
                                         audit_results: Dict[str, Any]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if overall_score < 0.8:
            recommendations.append("Improve overall security posture")
        
        if scan_results.get("vulnerabilities_found", 0) > 0:
            recommendations.append("Address identified vulnerabilities")
        
        critical_issues = len(scan_results.get("critical_issues", []))
        if critical_issues > 0:
            recommendations.append(f"Immediately fix {critical_issues} critical security issues")
        
        audit_risk = audit_results.get("audit_results", {}).get("risk_score", 0.0)
        if audit_risk > 30:
            recommendations.append("Review and improve security configuration")
        
        recommendations.extend([
            "Implement regular security scans",
            "Enable comprehensive audit logging",
            "Review access control policies",
            "Ensure encryption is properly configured"
        ])
        
        return recommendations
    
    def _check_overall_compliance(self, 
                                overall_score: float,
                                scan_results: Dict[str, Any],
                                audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Check overall security compliance"""
        critical_issues = len(scan_results.get("critical_issues", []))
        high_issues = len(scan_results.get("high_issues", []))
        
        compliance_status = {
            "overall_compliant": overall_score >= 0.9 and critical_issues == 0,
            "security_score": overall_score,
            "critical_issues_count": critical_issues,
            "high_issues_count": high_issues,
            "compliance_level": "high" if overall_score >= 0.9 else "medium" if overall_score >= 0.7 else "low",
            "enterprise_ready": overall_score >= 0.95 and critical_issues == 0 and high_issues <= 1
        }
        
        return compliance_status
    
    def _save_security_report(self, report: Dict[str, Any]):
        """Save security report to file"""
        try:
            reports_dir = Path("security_reports")
            reports_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"security_report_{timestamp}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"📄 Security report saved: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Report saving error: {e}")


def main():
    """Main execution function"""
    print("🛡️ MIA Enterprise AGI - Final Security Implementation")
    print("=" * 60)
    
    scanner = SecurityVulnerabilityScanner()
    result = scanner.scan_and_fix_vulnerabilities()
    
    # Display results
    if result.get("success", True):  # Default to True for backward compatibility
        print(f"\n📊 SECURITY SCAN RESULTS:")
        print(f"Overall Security Score: {result.get('overall_security_score', 0.0):.1%}")
        print(f"Security Grade: {result.get('security_grade', 'Unknown')}")
        
        compliance = result.get("compliance_status", {})
        print(f"Enterprise Ready: {'✅ YES' if compliance.get('enterprise_ready', False) else '❌ NO'}")
        print(f"Compliance Level: {compliance.get('compliance_level', 'unknown').upper()}")
        
        # Show component scores
        component_scores = result.get("component_scores", {})
        print(f"\n📈 COMPONENT SCORES:")
        for component, score in component_scores.items():
            print(f"  {component.replace('_', ' ').title()}: {score:.1%}")
        
        # Show recommendations
        recommendations = result.get("recommendations", [])
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. {rec}")
    else:
        print(f"❌ Security scan failed: {result.get('error', 'Unknown error')}")
    
    return result


if __name__ == "__main__":
    main()
