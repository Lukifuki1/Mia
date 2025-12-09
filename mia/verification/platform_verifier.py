#!/usr/bin/env python3
"""
MIA Enterprise AGI - Platform Verifier
======================================

Core platform verification and testing system.
"""

import os
import sys
import logging
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import psutil


class PlatformVerifier:
    """Core platform verification system"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = self._setup_logging()
        
        # Verification configuration
        self.verification_config = {
            "platforms": ["linux", "windows", "macos"],
            "introspective_cycles": 100,
            "parallel_instances": 3,
            "cold_start_timeout": 60,  # seconds
            "max_memory_gb": 5,
            "deterministic_seed": 42,
            "test_timeout": 300  # 5 minutes per test
        }
        
        # Platform packages
        self.platform_packages = {
            "linux": "mia_enterprise_linux.AppImage",
            "windows": "mia_enterprise_windows.exe", 
            "macos": "mia_enterprise_macos.app"
        }
        
        # Verification state
        self.verification_results = {}
        self.active_verifications = {}
        
        self.logger.info("🔧 Platform Verifier initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.Verification.PlatformVerifier")
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
    
    def detect_current_platform(self) -> Dict[str, Any]:
        """Detect current platform and system information"""
        try:
            platform_info = {
                "platform": sys.platform,
                "architecture": os.uname().machine if hasattr(os, 'uname') else 'unknown',
                "python_version": sys.version,
                "cpu_count": psutil.cpu_count(),
                "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "disk_space_gb": round(psutil.disk_usage('/').total / (1024**3), 2) if os.path.exists('/') else 0,
                "detection_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
            
            # Normalize platform name
            if platform_info["platform"].startswith("linux"):
                platform_info["normalized_platform"] = "linux"
            elif platform_info["platform"].startswith("win"):
                platform_info["normalized_platform"] = "windows"
            elif platform_info["platform"].startswith("darwin"):
                platform_info["normalized_platform"] = "macos"
            else:
                platform_info["normalized_platform"] = "unknown"
            
            self.logger.info(f"🔧 Platform detected: {platform_info['normalized_platform']}")
            
            return platform_info
            
        except Exception as e:
            self.logger.error(f"Platform detection error: {e}")
            return {
                "platform": "unknown",
                "error": str(e),
                "detection_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
    
    def verify_platform_compatibility(self, target_platform: str) -> Dict[str, Any]:
        """Verify platform compatibility"""
        try:
            current_platform = self.detect_current_platform()
            
            compatibility_result = {
                "target_platform": target_platform,
                "current_platform": current_platform["normalized_platform"],
                "compatible": False,
                "compatibility_checks": [],
                "verification_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
            
            # Check platform compatibility
            if current_platform["normalized_platform"] == target_platform:
                compatibility_result["compatibility_checks"].append({
                    "check": "platform_match",
                    "status": "passed",
                    "message": f"Platform matches: {target_platform}"
                })
                compatibility_result["compatible"] = True
            else:
                compatibility_result["compatibility_checks"].append({
                    "check": "platform_match",
                    "status": "failed",
                    "message": f"Platform mismatch: {current_platform['normalized_platform']} != {target_platform}"
                })
            
            # Check system requirements
            memory_gb = current_platform.get("memory_gb", 0)
            if memory_gb >= 2:
                compatibility_result["compatibility_checks"].append({
                    "check": "memory_requirement",
                    "status": "passed",
                    "message": f"Memory sufficient: {memory_gb}GB >= 2GB"
                })
            else:
                compatibility_result["compatibility_checks"].append({
                    "check": "memory_requirement",
                    "status": "failed",
                    "message": f"Insufficient memory: {memory_gb}GB < 2GB"
                })
                compatibility_result["compatible"] = False
            
            # Check CPU requirements
            cpu_count = current_platform.get("cpu_count", 0)
            if cpu_count >= 2:
                compatibility_result["compatibility_checks"].append({
                    "check": "cpu_requirement",
                    "status": "passed",
                    "message": f"CPU sufficient: {cpu_count} cores >= 2 cores"
                })
            else:
                compatibility_result["compatibility_checks"].append({
                    "check": "cpu_requirement",
                    "status": "failed",
                    "message": f"Insufficient CPU: {cpu_count} cores < 2 cores"
                })
                compatibility_result["compatible"] = False
            
            return compatibility_result
            
        except Exception as e:
            self.logger.error(f"Platform compatibility verification error: {e}")
            return {
                "target_platform": target_platform,
                "compatible": False,
                "error": str(e),
                "verification_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
    
    def run_platform_verification(self, platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run comprehensive platform verification"""
        try:
            if platforms is None:
                platforms = self.verification_config["platforms"]
            
            self.logger.info(f"🔧 Running platform verification for: {platforms}")
            
            verification_id = f"verification_{int(self._get_deterministic_time())}"
            
            verification_result = {
                "verification_id": verification_id,
                "verification_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "target_platforms": platforms,
                "platform_results": {},
                "overall_success": True,
                "summary": {}
            }
            
            # Verify each platform
            for platform in platforms:
                platform_result = self._verify_single_platform(platform)
                verification_result["platform_results"][platform] = platform_result
                
                if not platform_result.get("success", False):
                    verification_result["overall_success"] = False
            
            # Generate summary
            verification_result["summary"] = self._generate_verification_summary(
                verification_result["platform_results"]
            )
            
            # Store results
            self.verification_results[verification_id] = verification_result
            
            self.logger.info(f"🔧 Platform verification completed: {verification_id}")
            
            return verification_result
            
        except Exception as e:
            self.logger.error(f"Platform verification error: {e}")
            return {
                "success": False,
                "error": str(e),
                "verification_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
    
    def _verify_single_platform(self, platform: str) -> Dict[str, Any]:
        """Verify a single platform"""
        try:
            self.logger.info(f"🔧 Verifying platform: {platform}")
            
            platform_result = {
                "platform": platform,
                "verification_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "verification_steps": [],
                "success": True
            }
            
            # Step 1: Check platform compatibility
            compatibility_result = self.verify_platform_compatibility(platform)
            platform_result["verification_steps"].append({
                "step": "compatibility_check",
                "result": compatibility_result,
                "success": compatibility_result.get("compatible", False)
            })
            
            if not compatibility_result.get("compatible", False):
                platform_result["success"] = False
                return platform_result
            
            # Step 2: Check package availability
            package_check = self._check_package_availability(platform)
            platform_result["verification_steps"].append({
                "step": "package_availability",
                "result": package_check,
                "success": package_check.get("available", False)
            })
            
            # Step 3: Verify system dependencies
            dependency_check = self._verify_system_dependencies(platform)
            platform_result["verification_steps"].append({
                "step": "dependency_verification",
                "result": dependency_check,
                "success": dependency_check.get("all_satisfied", False)
            })
            
            # Step 4: Run platform-specific tests
            platform_tests = self._run_platform_tests(platform)
            platform_result["verification_steps"].append({
                "step": "platform_tests",
                "result": platform_tests,
                "success": platform_tests.get("all_passed", False)
            })
            
            # Check overall success
            platform_result["success"] = all(
                step["success"] for step in platform_result["verification_steps"]
            )
            
            return platform_result
            
        except Exception as e:
            self.logger.error(f"Single platform verification error: {e}")
            return {
                "platform": platform,
                "success": False,
                "error": str(e),
                "verification_timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
    
    def _check_package_availability(self, platform: str) -> Dict[str, Any]:
        """Check if platform package is available"""
        try:
            package_name = self.platform_packages.get(platform)
            if not package_name:
                return {
                    "available": False,
                    "error": f"No package defined for platform: {platform}"
                }
            
            # Check if package exists in build directory
            build_dir = self.project_root / "build" / "packages"
            package_path = build_dir / package_name
            
            if package_path.exists():
                package_size = package_path.stat().st_size
                return {
                    "available": True,
                    "package_name": package_name,
                    "package_path": str(package_path),
                    "package_size_mb": round(package_size / (1024*1024), 2)
                }
            else:
                return {
                    "available": False,
                    "package_name": package_name,
                    "expected_path": str(package_path),
                    "error": "Package file not found"
                }
                
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }
    
    def _verify_system_dependencies(self, platform: str) -> Dict[str, Any]:
        """Verify system dependencies for platform"""
        try:
            dependencies = {
                "linux": ["python3", "pip3", "git"],
                "windows": ["python", "pip", "git"],
                "macos": ["python3", "pip3", "git"]
            }
            
            platform_deps = dependencies.get(platform, [])
            dependency_results = []
            
            for dep in platform_deps:
                try:
                    # Check if dependency is available
                    result = subprocess.run(
                        [dep, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        dependency_results.append({
                            "dependency": dep,
                            "satisfied": True,
                            "version": result.stdout.strip()
                        })
                    else:
                        dependency_results.append({
                            "dependency": dep,
                            "satisfied": False,
                            "error": result.stderr.strip()
                        })
                        
                except subprocess.TimeoutExpired:
                    dependency_results.append({
                        "dependency": dep,
                        "satisfied": False,
                        "error": "Command timeout"
                    })
                except FileNotFoundError:
                    dependency_results.append({
                        "dependency": dep,
                        "satisfied": False,
                        "error": "Command not found"
                    })
            
            all_satisfied = all(dep["satisfied"] for dep in dependency_results)
            
            return {
                "all_satisfied": all_satisfied,
                "dependency_results": dependency_results,
                "total_dependencies": len(platform_deps),
                "satisfied_dependencies": len([d for d in dependency_results if d["satisfied"]])
            }
            
        except Exception as e:
            return {
                "all_satisfied": False,
                "error": str(e)
            }
    
    def _run_platform_tests(self, platform: str) -> Dict[str, Any]:
        """Run platform-specific tests"""
        try:
            test_results = []
            
            # Test 1: Python environment
            python_test = self._test_python_environment()
            test_results.append({
                "test": "python_environment",
                "passed": python_test.get("success", False),
                "result": python_test
            })
            
            # Test 2: File system access
            filesystem_test = self._test_filesystem_access()
            test_results.append({
                "test": "filesystem_access",
                "passed": filesystem_test.get("success", False),
                "result": filesystem_test
            })
            
            # Test 3: Network connectivity
            network_test = self._test_network_connectivity()
            test_results.append({
                "test": "network_connectivity",
                "passed": network_test.get("success", False),
                "result": network_test
            })
            
            # Test 4: Memory allocation
            memory_test = self._test_memory_allocation()
            test_results.append({
                "test": "memory_allocation",
                "passed": memory_test.get("success", False),
                "result": memory_test
            })
            
            all_passed = all(test["passed"] for test in test_results)
            
            return {
                "all_passed": all_passed,
                "test_results": test_results,
                "total_tests": len(test_results),
                "passed_tests": len([t for t in test_results if t["passed"]])
            }
            
        except Exception as e:
            return {
                "all_passed": False,
                "error": str(e)
            }
    
    def _test_python_environment(self) -> Dict[str, Any]:
        """Test Python environment"""
        try:
            import sys
            import json
            import hashlib
            
            return {
                "success": True,
                "python_version": sys.version,
                "modules_imported": ["sys", "json", "hashlib"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _test_filesystem_access(self) -> Dict[str, Any]:
        """Test filesystem access"""
        try:
            test_dir = self.project_root / "test_filesystem"
            test_dir.mkdir(exist_ok=True)
            
            test_file = test_dir / "test_file.txt"
            test_file.write_text("test content")
            
            content = test_file.read_text()
            test_file.unlink()
            test_dir.rmdir()
            
            return {
                "success": True,
                "operations": ["create_directory", "write_file", "read_file", "delete_file", "delete_directory"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _test_network_connectivity(self) -> Dict[str, Any]:
        """Test network connectivity"""
        try:
            import socket
from .deterministic_helpers import deterministic_helpers
            
            # Test DNS resolution
            socket.gethostbyname("google.com")
            
            return {
                "success": True,
                "dns_resolution": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _test_memory_allocation(self) -> Dict[str, Any]:
        """Test memory allocation"""
        try:
            # Allocate 100MB of memory
            test_data = bytearray(100 * 1024 * 1024)
            test_data[0] = 1
            test_data[-1] = 1
            
            del test_data
            
            return {
                "success": True,
                "allocated_mb": 100
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_verification_summary(self, platform_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate verification summary"""
        try:
            total_platforms = len(platform_results)
            successful_platforms = len([p for p in platform_results.values() if p.get("success", False)])
            
            summary = {
                "total_platforms": total_platforms,
                "successful_platforms": successful_platforms,
                "success_rate": (successful_platforms / total_platforms * 100) if total_platforms > 0 else 0,
                "failed_platforms": [
                    platform for platform, result in platform_results.items()
                    if not result.get("success", False)
                ]
            }
            
            return summary
            
        except Exception as e:
            return {
                "error": str(e)
            }
    
    def get_verification_status(self) -> Dict[str, Any]:
        """Get platform verifier status"""
        return {
            "total_verifications": len(self.verification_results),
            "active_verifications": len(self.active_verifications),
            "supported_platforms": self.verification_config["platforms"],
            "config": self.verification_config
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate platform verification report"""
        try:
            status = self.get_verification_status()
            
            return {
                "report_type": "platform_verification",
                "timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "statistics": status,
                "recent_verifications": list(self.verification_results.values())[-5:],  # Last 5
                "recommendations": self.get_recommendations()
            }
            
        except Exception as e:
            self.logger.error(f"Platform verification report generation error: {e}")
            return {
                "error": str(e)
            }
    
    def get_recommendations(self) -> List[str]:
        """Get platform verification recommendations"""
        recommendations = []
        
        status = self.get_verification_status()
        
        if status["total_verifications"] == 0:
            recommendations.append("Run initial platform verification")
        
        recommendations.extend([
            "Regular platform compatibility testing",
            "Automated verification in CI/CD pipeline",
            "Cross-platform package validation",
            "Performance benchmarking across platforms"
        ])
        
        return recommendations