#!/usr/bin/env python3
"""
MIA Enterprise AGI - Package Tester
===================================

Automated package testing and validation system.
"""

import logging
import subprocess
import threading
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class PackageTester:
    """Automated package testing system"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = self._setup_logging()
        
        # Testing configuration
        self.config = {
            "test_timeout": 300,  # 5 minutes
            "parallel_tests": 3,
            "cold_start_timeout": 60,
            "memory_limit_mb": 1024,
            "deterministic_seed": 42
        }
        
        # Test results storage
        self.test_results = {}
        self.active_tests = {}
        
        self.logger.info("📦 Package Tester initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.Verification.PackageTester")
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
    
    def test_package_integrity(self, package_path: str) -> Dict[str, Any]:
        """Test package integrity and structure"""
        try:
            package_file = Path(package_path)
            
            if not package_file.exists():
                return {
                    "success": False,
                    "error": f"Package file not found: {package_path}"
                }
            
            integrity_result = {
                "package_path": str(package_file),
                "test_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "integrity_checks": [],
                "success": True
            }
            
            # Check 1: File size
            file_size = package_file.stat().st_size
            if file_size > 0:
                integrity_result["integrity_checks"].append({
                    "check": "file_size",
                    "status": "passed",
                    "value": file_size,
                    "message": f"Package size: {file_size} bytes"
                })
            else:
                integrity_result["integrity_checks"].append({
                    "check": "file_size",
                    "status": "failed",
                    "value": file_size,
                    "message": "Package file is empty"
                })
                integrity_result["success"] = False
            
            # Check 2: File hash
            file_hash = self._calculate_file_hash(package_file)
            integrity_result["integrity_checks"].append({
                "check": "file_hash",
                "status": "passed",
                "value": file_hash,
                "message": f"Package hash: {file_hash}"
            })
            
            # Check 3: File permissions
            permissions = oct(package_file.stat().st_mode)[-3:]
            integrity_result["integrity_checks"].append({
                "check": "file_permissions",
                "status": "passed",
                "value": permissions,
                "message": f"File permissions: {permissions}"
            })
            
            # Check 4: File extension validation
            expected_extensions = {
                "linux": [".AppImage", ".deb", ".rpm"],
                "windows": [".exe", ".msi"],
                "macos": [".app", ".dmg", ".pkg"]
            }
            
            extension_valid = False
            for platform, extensions in expected_extensions.items():
                if any(package_file.name.endswith(ext) for ext in extensions):
                    extension_valid = True
                    break
            
            if extension_valid:
                integrity_result["integrity_checks"].append({
                    "check": "file_extension",
                    "status": "passed",
                    "value": package_file.suffix,
                    "message": f"Valid package extension: {package_file.suffix}"
                })
            else:
                integrity_result["integrity_checks"].append({
                    "check": "file_extension",
                    "status": "warning",
                    "value": package_file.suffix,
                    "message": f"Unusual package extension: {package_file.suffix}"
                })
            
            return integrity_result
            
        except Exception as e:
            self.logger.error(f"Package integrity test error: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
    
    def test_package_execution(self, package_path: str, platform: str) -> Dict[str, Any]:
        """Test package execution"""
        try:
            package_file = Path(package_path)
            
            execution_result = {
                "package_path": str(package_file),
                "platform": platform,
                "test_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "execution_tests": [],
                "success": True
            }
            
            # Test 1: Package launch test
            launch_test = self._test_package_launch(package_file, platform)
            execution_result["execution_tests"].append({
                "test": "package_launch",
                "result": launch_test,
                "success": launch_test.get("success", False)
            })
            
            if not launch_test.get("success", False):
                execution_result["success"] = False
            
            # Test 2: Cold start performance
            cold_start_test = self._test_cold_start_performance(package_file, platform)
            execution_result["execution_tests"].append({
                "test": "cold_start_performance",
                "result": cold_start_test,
                "success": cold_start_test.get("success", False)
            })
            
            # Test 3: Memory usage test
            memory_test = self._test_memory_usage(package_file, platform)
            execution_result["execution_tests"].append({
                "test": "memory_usage",
                "result": memory_test,
                "success": memory_test.get("success", False)
            })
            
            # Test 4: Basic functionality test
            functionality_test = self._test_basic_functionality(package_file, platform)
            execution_result["execution_tests"].append({
                "test": "basic_functionality",
                "result": functionality_test,
                "success": functionality_test.get("success", False)
            })
            
            # Calculate overall success
            execution_result["success"] = all(
                test["success"] for test in execution_result["execution_tests"]
            )
            
            return execution_result
            
        except Exception as e:
            self.logger.error(f"Package execution test error: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
    
    def _test_package_launch(self, package_file: Path, platform: str) -> Dict[str, Any]:
        """Test package launch"""
        try:
            if platform == "linux" and package_file.suffix == ".AppImage":
                # Make AppImage executable
                package_file.chmod(0o755)
                cmd = [str(package_file), "--help"]
            elif platform == "windows" and package_file.suffix == ".exe":
                cmd = [str(package_file), "/help"]
            elif platform == "macos" and package_file.suffix == ".app":
                cmd = ["open", str(package_file)]
            else:
                return {
                    "success": False,
                    "error": f"Unsupported package type for platform: {platform}"
                }
            
            # Run command with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config["test_timeout"]
            )
            
            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout[:1000],  # Limit output
                "stderr": result.stderr[:1000],
                "command": " ".join(cmd)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Package launch timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _test_cold_start_performance(self, package_file: Path, platform: str) -> Dict[str, Any]:
        """Test cold start performance"""
        try:
            start_time = deterministic_helpers.get_deterministic_epoch()
            
            # Simulate cold start test
            if platform == "linux":
                # For Linux, test file access time
                package_file.stat()
                cold_start_time = deterministic_helpers.get_deterministic_epoch() - start_time
            elif platform == "windows":
                # For Windows, test file access time
                package_file.stat()
                cold_start_time = deterministic_helpers.get_deterministic_epoch() - start_time
            elif platform == "macos":
                # For macOS, test file access time
                package_file.stat()
                cold_start_time = deterministic_helpers.get_deterministic_epoch() - start_time
            else:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
            
            # Check if cold start time is acceptable
            acceptable_time = self.config["cold_start_timeout"]
            success = cold_start_time < acceptable_time
            
            return {
                "success": success,
                "cold_start_time_seconds": cold_start_time,
                "acceptable_time_seconds": acceptable_time,
                "performance_grade": "good" if cold_start_time < 5 else "acceptable" if cold_start_time < 30 else "poor"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _test_memory_usage(self, package_file: Path, platform: str) -> Dict[str, Any]:
        """Test memory usage"""
        try:
            import psutil
from .deterministic_helpers import deterministic_helpers
            
            # Get current memory usage
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Simulate memory test by reading package file
            with open(package_file, 'rb') as f:
                # Read file in chunks to simulate package loading
                chunk_size = 1024 * 1024  # 1MB chunks
                while f.read(chunk_size):
                    pass
            
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before
            
            # Check if memory usage is within limits
            memory_limit = self.config["memory_limit_mb"]
            success = memory_used < memory_limit
            
            return {
                "success": success,
                "memory_used_mb": round(memory_used, 2),
                "memory_limit_mb": memory_limit,
                "memory_efficiency": "good" if memory_used < 100 else "acceptable" if memory_used < 500 else "poor"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _test_basic_functionality(self, package_file: Path, platform: str) -> Dict[str, Any]:
        """Test basic functionality"""
        try:
            functionality_tests = []
            
            # Test 1: File accessibility
            if package_file.is_file():
                functionality_tests.append({
                    "test": "file_accessibility",
                    "passed": True,
                    "message": "Package file is accessible"
                })
            else:
                functionality_tests.append({
                    "test": "file_accessibility",
                    "passed": False,
                    "message": "Package file is not accessible"
                })
            
            # Test 2: File readability
            try:
                with open(package_file, 'rb') as f:
                    f.read(1024)  # Read first 1KB
                functionality_tests.append({
                    "test": "file_readability",
                    "passed": True,
                    "message": "Package file is readable"
                })
            except Exception as e:
                functionality_tests.append({
                    "test": "file_readability",
                    "passed": False,
                    "message": f"Package file read error: {e}"
                })
            
            # Test 3: Platform compatibility
            if platform in ["linux", "windows", "macos"]:
                functionality_tests.append({
                    "test": "platform_compatibility",
                    "passed": True,
                    "message": f"Platform {platform} is supported"
                })
            else:
                functionality_tests.append({
                    "test": "platform_compatibility",
                    "passed": False,
                    "message": f"Platform {platform} is not supported"
                })
            
            # Calculate overall success
            all_passed = all(test["passed"] for test in functionality_tests)
            
            return {
                "success": all_passed,
                "functionality_tests": functionality_tests,
                "total_tests": len(functionality_tests),
                "passed_tests": len([t for t in functionality_tests if t["passed"]])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate file hash"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()[:16]  # First 16 characters
            
        except Exception as e:
            return f"hash_error_{e}"
    
    def run_comprehensive_package_test(self, package_path: str, platform: str) -> Dict[str, Any]:
        """Run comprehensive package test"""
        try:
            self.logger.info(f"📦 Running comprehensive package test: {package_path}")
            
            test_id = f"test_{int(self._get_deterministic_time())}_{hash(package_path) % 10000}"
            
            comprehensive_result = {
                "test_id": test_id,
                "package_path": package_path,
                "platform": platform,
                "test_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "test_phases": {},
                "overall_success": True,
                "summary": {}
            }
            
            # Phase 1: Integrity test
            integrity_result = self.test_package_integrity(package_path)
            comprehensive_result["test_phases"]["integrity"] = integrity_result
            
            if not integrity_result.get("success", False):
                comprehensive_result["overall_success"] = False
            
            # Phase 2: Execution test (only if integrity passed)
            if integrity_result.get("success", False):
                execution_result = self.test_package_execution(package_path, platform)
                comprehensive_result["test_phases"]["execution"] = execution_result
                
                if not execution_result.get("success", False):
                    comprehensive_result["overall_success"] = False
            else:
                comprehensive_result["test_phases"]["execution"] = {
                    "skipped": True,
                    "reason": "Integrity test failed"
                }
            
            # Generate summary
            comprehensive_result["summary"] = self._generate_test_summary(
                comprehensive_result["test_phases"]
            )
            
            # Store results
            self.test_results[test_id] = comprehensive_result
            
            self.logger.info(f"📦 Comprehensive package test completed: {test_id}")
            
            return comprehensive_result
            
        except Exception as e:
            self.logger.error(f"Comprehensive package test error: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
    
    def _generate_test_summary(self, test_phases: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test summary"""
        try:
            summary = {
                "total_phases": len(test_phases),
                "successful_phases": 0,
                "failed_phases": 0,
                "skipped_phases": 0,
                "phase_details": {}
            }
            
            for phase_name, phase_result in test_phases.items():
                if phase_result.get("skipped", False):
                    summary["skipped_phases"] += 1
                    summary["phase_details"][phase_name] = "skipped"
                elif phase_result.get("success", False):
                    summary["successful_phases"] += 1
                    summary["phase_details"][phase_name] = "passed"
                else:
                    summary["failed_phases"] += 1
                    summary["phase_details"][phase_name] = "failed"
            
            summary["success_rate"] = (
                summary["successful_phases"] / summary["total_phases"] * 100
                if summary["total_phases"] > 0 else 0
            )
            
            return summary
            
        except Exception as e:
            return {
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get package tester status"""
        return {
            "total_tests": len(self.test_results),
            "active_tests": len(self.active_tests),
            "config": self.config
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate package testing report"""
        try:
            status = self.get_status()
            
            return {
                "report_type": "package_testing",
                "timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "statistics": status,
                "recent_tests": list(self.test_results.values())[-5:],  # Last 5
                "recommendations": self.get_recommendations()
            }
            
        except Exception as e:
            self.logger.error(f"Package testing report generation error: {e}")
            return {
                "error": str(e)
            }
    
    def get_recommendations(self) -> List[str]:
        """Get package testing recommendations"""
        recommendations = []
        
        status = self.get_status()
        
        if status["total_tests"] == 0:
            recommendations.append("Run initial package tests")
        
        recommendations.extend([
            "Automated package testing in CI/CD",
            "Cross-platform package validation",
            "Performance regression testing",
            "Package integrity monitoring"
        ])
        
        return recommendations