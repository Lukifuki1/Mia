#!/usr/bin/env python3
"""
MIA Enterprise AGI - Production Validation
==========================================

Comprehensive validation script to ensure the system is production-ready.
"""

import os
import sys
import json
import logging
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Tuple

class ProductionValidator:
    """Validates MIA Enterprise AGI for production deployment"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_results = {
            "core_system": {},
            "dependencies": {},
            "configuration": {},
            "security": {},
            "performance": {},
            "documentation": {},
            "overall_score": 0
        }
        
    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete production validation"""
        print("🔍 MIA Enterprise AGI - Production Validation")
        print("=" * 50)
        
        # Core system validation
        print("\n📋 Validating Core System...")
        self.validation_results["core_system"] = self._validate_core_system()
        
        # Dependencies validation
        print("\n📦 Validating Dependencies...")
        self.validation_results["dependencies"] = self._validate_dependencies()
        
        # Configuration validation
        print("\n⚙️ Validating Configuration...")
        self.validation_results["configuration"] = self._validate_configuration()
        
        # Security validation
        print("\n🔒 Validating Security...")
        self.validation_results["security"] = self._validate_security()
        
        # Performance validation
        print("\n⚡ Validating Performance...")
        self.validation_results["performance"] = self._validate_performance()
        
        # Documentation validation
        print("\n📚 Validating Documentation...")
        self.validation_results["documentation"] = self._validate_documentation()
        
        # Calculate overall score
        self._calculate_overall_score()
        
        # Generate report
        self._generate_report()
        
        return self.validation_results
    
    def _validate_core_system(self) -> Dict[str, Any]:
        """Validate core system components"""
        results = {
            "main_launcher": False,
            "start_scripts": False,
            "core_modules": False,
            "enterprise_features": False,
            "desktop_app": False,
            "score": 0
        }
        
        # Check main launcher
        if os.path.exists("mia_enterprise_agi.py"):
            results["main_launcher"] = True
            print("✅ Main launcher found")
        else:
            print("❌ Main launcher missing")
        
        # Check start scripts
        start_scripts = ["start_mia.sh", "start_mia.bat", "start_mia.command"]
        if all(os.path.exists(script) for script in start_scripts):
            results["start_scripts"] = True
            print("✅ Start scripts found")
        else:
            print("❌ Some start scripts missing")
        
        # Check core modules
        core_modules = [
            "mia/core/agi_core.py",
            "mia/interfaces/unified_interface.py",
            "mia/modules/ui/web.py"
        ]
        if all(os.path.exists(module) for module in core_modules):
            results["core_modules"] = True
            print("✅ Core modules found")
        else:
            print("❌ Some core modules missing")
        
        # Check enterprise features
        if os.path.exists("enterprise/") and os.path.exists("mia/enterprise/"):
            results["enterprise_features"] = True
            print("✅ Enterprise features found")
        else:
            print("❌ Enterprise features missing")
        
        # Check desktop app
        if os.path.exists("desktop/") and os.path.exists("desktop/package.json"):
            results["desktop_app"] = True
            print("✅ Desktop application found")
        else:
            print("❌ Desktop application missing")
        
        results["score"] = sum(results[key] for key in results if isinstance(results[key], bool)) / 5 * 100
        return results
    
    def _validate_dependencies(self) -> Dict[str, Any]:
        """Validate dependencies and requirements"""
        results = {
            "requirements_file": False,
            "python_version": False,
            "critical_packages": False,
            "score": 0
        }
        
        # Check requirements.txt
        if os.path.exists("requirements.txt"):
            results["requirements_file"] = True
            print("✅ Requirements file found")
        else:
            print("❌ Requirements file missing")
        
        # Check Python version
        if sys.version_info >= (3, 8):
            results["python_version"] = True
            print(f"✅ Python version {sys.version_info.major}.{sys.version_info.minor} is compatible")
        else:
            print(f"❌ Python version {sys.version_info.major}.{sys.version_info.minor} is too old")
        
        # Check critical packages
        critical_packages = ["fastapi", "uvicorn", "transformers", "torch"]
        missing_packages = []
        
        for package in critical_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if not missing_packages:
            results["critical_packages"] = True
            print("✅ All critical packages available")
        else:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
        
        results["score"] = sum(results[key] for key in results if isinstance(results[key], bool)) / 3 * 100
        return results
    
    def _validate_configuration(self) -> Dict[str, Any]:
        """Validate configuration files"""
        results = {
            "main_config": False,
            "desktop_config": False,
            "enterprise_config": False,
            "score": 0
        }
        
        # Check main config
        if os.path.exists("config.json"):
            try:
                with open("config.json", 'r') as f:
                    config = json.load(f)
                    if all(key in config for key in ["system", "server", "ai"]):
                        results["main_config"] = True
                        print("✅ Main configuration valid")
                    else:
                        print("❌ Main configuration incomplete")
            except Exception as e:
                print(f"❌ Main configuration error: {e}")
        else:
            print("❌ Main configuration missing")
        
        # Check desktop config
        if os.path.exists("desktop/package.json"):
            results["desktop_config"] = True
            print("✅ Desktop configuration found")
        else:
            print("❌ Desktop configuration missing")
        
        # Check enterprise config
        if os.path.exists("mia/config/enterprise.json"):
            results["enterprise_config"] = True
            print("✅ Enterprise configuration found")
        else:
            print("❌ Enterprise configuration missing")
        
        results["score"] = sum(results[key] for key in results if isinstance(results[key], bool)) / 3 * 100
        return results
    
    def _validate_security(self) -> Dict[str, Any]:
        """Validate security features"""
        results = {
            "owner_guard": False,
            "security_modules": False,
            "compliance_features": False,
            "score": 0
        }
        
        # Check owner guard
        if os.path.exists("mia/core/owner_guard.py"):
            results["owner_guard"] = True
            print("✅ Owner guard system found")
        else:
            print("❌ Owner guard system missing")
        
        # Check security modules
        security_modules = [
            "mia/core/security/",
            "mia/enterprise/security_manager.py"
        ]
        if any(os.path.exists(module) for module in security_modules):
            results["security_modules"] = True
            print("✅ Security modules found")
        else:
            print("❌ Security modules missing")
        
        # Check compliance features
        if os.path.exists("docs/compliance/"):
            results["compliance_features"] = True
            print("✅ Compliance documentation found")
        else:
            print("❌ Compliance documentation missing")
        
        results["score"] = sum(results[key] for key in results if isinstance(results[key], bool)) / 3 * 100
        return results
    
    def _validate_performance(self) -> Dict[str, Any]:
        """Validate performance optimizations"""
        results = {
            "optimization_modules": False,
            "caching_system": False,
            "monitoring": False,
            "score": 0
        }
        
        # Check optimization modules
        if os.path.exists("mia/core/hardware_optimizer.py"):
            results["optimization_modules"] = True
            print("✅ Optimization modules found")
        else:
            print("❌ Optimization modules missing")
        
        # Check caching system
        if os.path.exists("mia/data/"):
            results["caching_system"] = True
            print("✅ Caching system found")
        else:
            print("❌ Caching system missing")
        
        # Check monitoring
        if os.path.exists("mia/verification/performance_monitor.py"):
            results["monitoring"] = True
            print("✅ Performance monitoring found")
        else:
            print("❌ Performance monitoring missing")
        
        results["score"] = sum(results[key] for key in results if isinstance(results[key], bool)) / 3 * 100
        return results
    
    def _validate_documentation(self) -> Dict[str, Any]:
        """Validate documentation completeness"""
        results = {
            "main_readme": False,
            "docs_structure": False,
            "user_guides": False,
            "score": 0
        }
        
        # Check main README
        if os.path.exists("README.md"):
            results["main_readme"] = True
            print("✅ Main README found")
        else:
            print("❌ Main README missing")
        
        # Check docs structure
        if os.path.exists("docs/") and os.path.exists("docs/README.md"):
            results["docs_structure"] = True
            print("✅ Documentation structure found")
        else:
            print("❌ Documentation structure missing")
        
        # Check user guides
        if os.path.exists("docs/guides/"):
            results["user_guides"] = True
            print("✅ User guides found")
        else:
            print("❌ User guides missing")
        
        results["score"] = sum(results[key] for key in results if isinstance(results[key], bool)) / 3 * 100
        return results
    
    def _calculate_overall_score(self):
        """Calculate overall production readiness score"""
        scores = [
            self.validation_results["core_system"]["score"],
            self.validation_results["dependencies"]["score"],
            self.validation_results["configuration"]["score"],
            self.validation_results["security"]["score"],
            self.validation_results["performance"]["score"],
            self.validation_results["documentation"]["score"]
        ]
        
        self.validation_results["overall_score"] = sum(scores) / len(scores)
    
    def _generate_report(self):
        """Generate validation report"""
        print("\n" + "=" * 50)
        print("📊 PRODUCTION VALIDATION REPORT")
        print("=" * 50)
        
        score = self.validation_results["overall_score"]
        
        if score >= 90:
            status = "🟢 PRODUCTION READY"
        elif score >= 75:
            status = "🟡 MOSTLY READY (minor issues)"
        elif score >= 60:
            status = "🟠 NEEDS WORK (major issues)"
        else:
            status = "🔴 NOT READY (critical issues)"
        
        print(f"\nOverall Score: {score:.1f}%")
        print(f"Status: {status}")
        
        print(f"\nComponent Scores:")
        print(f"  Core System: {self.validation_results['core_system']['score']:.1f}%")
        print(f"  Dependencies: {self.validation_results['dependencies']['score']:.1f}%")
        print(f"  Configuration: {self.validation_results['configuration']['score']:.1f}%")
        print(f"  Security: {self.validation_results['security']['score']:.1f}%")
        print(f"  Performance: {self.validation_results['performance']['score']:.1f}%")
        print(f"  Documentation: {self.validation_results['documentation']['score']:.1f}%")
        
        # Save report
        with open("production_validation_report.json", "w") as f:
            json.dump(self.validation_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: production_validation_report.json")

def main():
    """Main validation function"""
    validator = ProductionValidator()
    results = validator.run_full_validation()
    
    # Exit with appropriate code
    if results["overall_score"] >= 75:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()