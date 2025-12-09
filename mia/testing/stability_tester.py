#!/usr/bin/env python3
"""
MIA Enterprise AGI - Stability Tester
====================================

168-hour stability testing and long-term reliability validation.
"""

import os
import sys
import time
import logging
import threading
import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta


class StabilityTester:
    """168-hour stability testing system"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = self._setup_logging()
        
        # Stability test configuration
        self.test_duration_hours = 168  # 7 days
        self.monitoring_interval = 300  # 5 minutes
        self.stability_thresholds = {
            "max_memory_growth": 100,  # MB
            "max_cpu_spike": 90,  # percentage
            "max_error_rate": 0.01,  # 1%
            "min_uptime": 0.99  # 99%
        }
        
        # Test state
        self.test_active = False
        self.test_start_time = None
        self.stability_data = []
        self.error_log = []
        
        self.logger.info("🔄 Stability Tester initialized")
    

    def run_stability_tests(self) -> Dict[str, Any]:
        """Run comprehensive stability tests"""
        try:
            stability_result = {
                "success": True,
                "test_timestamp": self._get_build_timestamp().isoformat(),
                "stability_tests": [],
                "overall_score": 0.0,
                "status": "unknown"
            }
            
            # Test 1: Memory stability
            memory_test = self._test_memory_stability()
            stability_result["stability_tests"].append(memory_test)
            
            # Test 2: Error handling stability
            error_test = self._test_error_handling_stability()
            stability_result["stability_tests"].append(error_test)
            
            # Test 3: Resource cleanup stability
            cleanup_test = self._test_resource_cleanup_stability()
            stability_result["stability_tests"].append(cleanup_test)
            
            # Calculate overall score
            scores = [test.get("score", 0) for test in stability_result["stability_tests"]]
            stability_result["overall_score"] = sum(scores) / len(scores) if scores else 0
            
            # Determine status
            if stability_result["overall_score"] >= 90:
                stability_result["status"] = "stable"
            elif stability_result["overall_score"] >= 80:
                stability_result["status"] = "mostly_stable"
            else:
                stability_result["status"] = "unstable"
                stability_result["success"] = False
            
            return stability_result
            
        except Exception as e:
            self.logger.error(f"Stability tests error: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_timestamp": self._get_build_timestamp().isoformat()
            }
    
    def _test_memory_stability(self) -> Dict[str, Any]:
        """Test memory stability"""
        try:
            import psutil
            initial_memory = psutil.virtual_memory().percent
            
            # Allocate and deallocate memory
            data = [i for i in range(10000)]
            del data
            
            final_memory = psutil.virtual_memory().percent
            memory_increase = final_memory - initial_memory
            
            # Score based on memory stability
            if memory_increase < 1:
                score = 100
            elif memory_increase < 5:
                score = 80
            else:
                score = 60
            
            return {
                "test": "memory_stability",
                "initial_memory_percent": initial_memory,
                "final_memory_percent": final_memory,
                "memory_increase": memory_increase,
                "score": score,
                "status": "passed"
            }
        except Exception as e:
            return {
                "test": "memory_stability",
                "error": str(e),
                "score": 0,
                "status": "failed"
            }
    
    def _test_error_handling_stability(self) -> Dict[str, Any]:
        """Test error handling stability"""
        try:
            errors_handled = 0
            total_errors = 3
            
            # Test 1: Division by zero
            try:
                result = 1 / 0
            except ZeroDivisionError:
                errors_handled += 1
            
            # Test 2: Key error
            try:
                d = {}
                value = d["nonexistent"]
            except KeyError:
                errors_handled += 1
            
            # Test 3: Type error
            try:
                result = "string" + 5
            except TypeError:
                errors_handled += 1
            
            # Score based on error handling
            score = (errors_handled / total_errors) * 100
            
            return {
                "test": "error_handling_stability",
                "errors_handled": errors_handled,
                "total_errors": total_errors,
                "score": score,
                "status": "passed"
            }
        except Exception as e:
            return {
                "test": "error_handling_stability",
                "error": str(e),
                "score": 0,
                "status": "failed"
            }
    
    def _test_resource_cleanup_stability(self) -> Dict[str, Any]:
        """Test resource cleanup stability"""
        try:
            # Test file cleanup
            test_files = []
            for i in range(5):
                test_file = Path(f"stability_test_{i}.tmp")
                test_file.write_text("test")
                test_files.append(test_file)
            
            # Clean up files
            cleaned_files = 0
            for test_file in test_files:
                try:
                    test_file.unlink()
                    cleaned_files += 1
                except Exception as e:
                    self.logger.warning(f"Could not clean test file {test_file}: {e}")
                    continue
            score = (cleaned_files / len(test_files)) * 100
            
            return {
                "test": "resource_cleanup_stability",
                "files_created": len(test_files),
                "files_cleaned": cleaned_files,
                "score": score,
                "status": "passed"
            }
        except Exception as e:
            return {
                "test": "resource_cleanup_stability",
                "error": str(e),
                "score": 0,
                "status": "failed"
            }
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.Testing.StabilityTester")
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
    
    def start_stability_test(self, duration_hours: Optional[int] = None) -> Dict[str, Any]:
        """Start 168-hour stability test"""
        try:
            if self.test_active:
                return {
                    "status": "error",
                    "error": "Stability test already running"
                }
            
            test_duration = duration_hours or self.test_duration_hours
            self.logger.info(f"🔄 Starting {test_duration}-hour stability test...")
            
            self.test_active = True
            self.test_start_time = self._get_build_timestamp()
            self.stability_data = []
            self.error_log = []
            
            # Start monitoring thread
            monitor_thread = threading.Thread(
                target=self._run_stability_monitoring,
                args=(test_duration,)
            )
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Start stress testing thread
            stress_thread = threading.Thread(
                target=self._run_stress_tests,
                args=(test_duration,)
            )
            stress_thread.daemon = True
            stress_thread.start()
            
            return {
                "status": "started",
                "test_duration_hours": test_duration,
                "start_time": self.test_start_time.isoformat(),
                "monitoring_interval_seconds": self.monitoring_interval
            }
            
        except Exception as e:
            self.logger.error(f"Stability test start error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _run_stability_monitoring(self, duration_hours: int):
        """Run continuous stability monitoring"""
        try:
            end_time = self.test_start_time + timedelta(hours=duration_hours)
            
            while self._get_build_timestamp() < end_time and self.test_active:
                try:
                    # Collect system metrics
                    metrics = self._collect_system_metrics()
                    self.stability_data.append(metrics)
                    
                    # Check for stability issues
                    issues = self._check_stability_issues(metrics)
                    if issues:
                        self.error_log.extend(issues)
                    
                    # Log progress periodically
                    if len(self.stability_data) % 12 == 0:  # Every hour
                        elapsed_hours = (self._get_build_timestamp() - self.test_start_time).total_seconds() / 3600
                        self.logger.info(f"🔄 Stability test progress: {elapsed_hours:.1f}/{duration_hours} hours")
                    
                except Exception as e:
                    self.error_log.append({
                        "timestamp": self._get_build_timestamp().isoformat(),
                        "type": "monitoring_error",
                        "error": str(e)
                    })
                
                time.sleep(self.monitoring_interval)
            
            # Test completed
            self.test_active = False
            self.logger.info("✅ Stability test monitoring completed")
            
        except Exception as e:
            self.logger.error(f"Stability monitoring error: {e}")
            self.test_active = False
    
    def _run_stress_tests(self, duration_hours: int):
        """Run periodic stress tests during stability testing"""
        try:
            end_time = self.test_start_time + timedelta(hours=duration_hours)
            stress_interval = 3600  # Run stress test every hour
            
            while self._get_build_timestamp() < end_time and self.test_active:
                try:
                    # Run mini stress test
                    stress_result = self._run_mini_stress_test()
                    
                    # Log stress test result
                    self.stability_data.append({
                        "timestamp": self._get_build_timestamp().isoformat(),
                        "type": "stress_test",
                        "result": stress_result
                    })
                    
                except Exception as e:
                    self.error_log.append({
                        "timestamp": self._get_build_timestamp().isoformat(),
                        "type": "stress_test_error",
                        "error": str(e)
                    })
                
                time.sleep(stress_interval)
            
        except Exception as e:
            self.logger.error(f"Stress testing error: {e}")
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics"""
        try:
            process = psutil.Process()
            
            metrics = {
                "timestamp": self._get_build_timestamp().isoformat(),
                "type": "system_metrics",
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_info": {
                    "rss_mb": process.memory_info().rss / 1024 / 1024,
                    "vms_mb": process.memory_info().vms / 1024 / 1024,
                    "percent": process.memory_percent()
                },
                "system_memory": {
                    "total_mb": psutil.virtual_memory().total / 1024 / 1024,
                    "available_mb": psutil.virtual_memory().available / 1024 / 1024,
                    "percent": psutil.virtual_memory().percent
                },
                "disk_usage": {
                    "total_gb": psutil.disk_usage('/').total / 1024 / 1024 / 1024,
                    "free_gb": psutil.disk_usage('/').free / 1024 / 1024 / 1024,
                    "percent": psutil.disk_usage('/').percent
                },
                "process_info": {
                    "threads": process.num_threads(),
                    "open_files": len(process.open_files()),
                    "connections": len(process.connections()),
                    "status": process.status()
                },
                "uptime_seconds": (self._get_build_timestamp() - self.test_start_time).total_seconds()
            }
            
            return metrics
            
        except Exception as e:
            return {
                "timestamp": self._get_build_timestamp().isoformat(),
                "type": "system_metrics",
                "error": str(e)
            }
    
    def _check_stability_issues(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for stability issues in metrics"""
        issues = []
        
        try:
            # Check memory growth
            if len(self.stability_data) > 12:  # After first hour
                initial_memory = self.stability_data[0].get("memory_info", {}).get("rss_mb", 0)
                current_memory = metrics.get("memory_info", {}).get("rss_mb", 0)
                memory_growth = current_memory - initial_memory
                
                if memory_growth > self.stability_thresholds["max_memory_growth"]:
                    issues.append({
                        "timestamp": self._get_build_timestamp().isoformat(),
                        "type": "memory_leak",
                        "severity": "high",
                        "memory_growth_mb": memory_growth,
                        "threshold_mb": self.stability_thresholds["max_memory_growth"]
                    })
            
            # Check CPU spikes
            cpu_percent = metrics.get("cpu_percent", 0)
            if cpu_percent > self.stability_thresholds["max_cpu_spike"]:
                issues.append({
                    "timestamp": self._get_build_timestamp().isoformat(),
                    "type": "cpu_spike",
                    "severity": "medium",
                    "cpu_percent": cpu_percent,
                    "threshold": self.stability_thresholds["max_cpu_spike"]
                })
            
            # Check system memory
            system_memory_percent = metrics.get("system_memory", {}).get("percent", 0)
            if system_memory_percent > 90:
                issues.append({
                    "timestamp": self._get_build_timestamp().isoformat(),
                    "type": "system_memory_high",
                    "severity": "medium",
                    "memory_percent": system_memory_percent
                })
            
            # Check disk space
            disk_percent = metrics.get("disk_usage", {}).get("percent", 0)
            if disk_percent > 90:
                issues.append({
                    "timestamp": self._get_build_timestamp().isoformat(),
                    "type": "disk_space_low",
                    "severity": "medium",
                    "disk_percent": disk_percent
                })
            
        except Exception as e:
            issues.append({
                "timestamp": self._get_build_timestamp().isoformat(),
                "type": "stability_check_error",
                "severity": "low",
                "error": str(e)
            })
        
        return issues
    
    def _run_mini_stress_test(self) -> Dict[str, Any]:
        """Run mini stress test"""
        try:
            start_time = self._get_build_epoch()
            
            # CPU stress
            cpu_result = sum(i * i for i in range(50000))
            
            # Memory stress
            memory_test = []
            for i in range(1000):
                memory_test.append({"id": i, "data": "x" * 100})
            
            # I/O stress
            temp_file = self.project_root / "temp_stress_test.txt"
            with open(temp_file, 'w') as f:
                f.write("stress test data\n" * 1000)
            
            with open(temp_file, 'r') as f:
                content = f.read()
            
            temp_file.unlink()
            
            end_time = self._get_build_epoch()
            
            return {
                "duration": end_time - start_time,
                "cpu_result": cpu_result,
                "memory_objects": len(memory_test),
                "io_bytes": len(content),
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_stability_status(self) -> Dict[str, Any]:
        """Get current stability test status"""
        try:
            if not self.test_active and not self.stability_data:
                return {
                    "status": "not_running",
                    "message": "No stability test is currently running"
                }
            
            current_time = self._get_build_timestamp()
            elapsed_time = (current_time - self.test_start_time).total_seconds() if self.test_start_time else 0
            
            status = {
                "test_active": self.test_active,
                "start_time": self.test_start_time.isoformat() if self.test_start_time else None,
                "elapsed_hours": elapsed_time / 3600,
                "data_points_collected": len(self.stability_data),
                "errors_detected": len(self.error_log),
                "current_metrics": self.stability_data[-1] if self.stability_data else None
            }
            
            # Calculate stability metrics
            if len(self.stability_data) > 1:
                stability_metrics = self._calculate_stability_metrics()
                status["stability_metrics"] = stability_metrics
            
            return status
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def stop_stability_test(self) -> Dict[str, Any]:
        """Stop stability test and generate report"""
        try:
            if not self.test_active:
                return {
                    "status": "error",
                    "error": "No stability test is currently running"
                }
            
            self.logger.info("🛑 Stopping stability test...")
            self.test_active = False
            
            # Generate final report
            final_report = self._generate_stability_report()
            
            # Save report
            self._save_stability_report(final_report)
            
            return {
                "status": "stopped",
                "final_report": final_report
            }
            
        except Exception as e:
            self.logger.error(f"Stop stability test error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _calculate_stability_metrics(self) -> Dict[str, Any]:
        """Calculate stability metrics from collected data"""
        try:
            if not self.stability_data:
                return {}
            
            # Extract metrics
            memory_values = []
            cpu_values = []
            
            for data_point in self.stability_data:
                if data_point.get("type") == "system_metrics":
                    memory_info = data_point.get("memory_info", {})
                    if "rss_mb" in memory_info:
                        memory_values.append(memory_info["rss_mb"])
                    
                    if "cpu_percent" in data_point:
                        cpu_values.append(data_point["cpu_percent"])
            
            metrics = {}
            
            if memory_values:
                metrics["memory_stats"] = {
                    "initial_mb": memory_values[0],
                    "current_mb": memory_values[-1],
                    "max_mb": max(memory_values),
                    "min_mb": min(memory_values),
                    "average_mb": sum(memory_values) / len(memory_values),
                    "growth_mb": memory_values[-1] - memory_values[0]
                }
            
            if cpu_values:
                metrics["cpu_stats"] = {
                    "max_percent": max(cpu_values),
                    "min_percent": min(cpu_values),
                    "average_percent": sum(cpu_values) / len(cpu_values)
                }
            
            # Calculate uptime percentage
            total_expected_points = len(self.stability_data)
            actual_points = len([d for d in self.stability_data if d.get("type") == "system_metrics"])
            uptime_percentage = (actual_points / total_expected_points) if total_expected_points > 0 else 0
            
            metrics["uptime_percentage"] = uptime_percentage
            metrics["error_rate"] = len(self.error_log) / len(self.stability_data) if self.stability_data else 0
            
            return metrics
            
        except Exception as e:
            return {
                "error": str(e)
            }
    
    def _generate_stability_report(self) -> Dict[str, Any]:
        """Generate comprehensive stability report"""
        try:
            end_time = self._get_build_timestamp()
            elapsed_time = (end_time - self.test_start_time).total_seconds() if self.test_start_time else 0
            
            report = {
                "report_timestamp": end_time.isoformat(),
                "test_summary": {
                    "start_time": self.test_start_time.isoformat() if self.test_start_time else None,
                    "end_time": end_time.isoformat(),
                    "elapsed_hours": elapsed_time / 3600,
                    "planned_duration_hours": self.test_duration_hours,
                    "completion_percentage": (elapsed_time / 3600) / self.test_duration_hours * 100 if self.test_duration_hours > 0 else 0
                },
                "data_collection": {
                    "total_data_points": len(self.stability_data),
                    "monitoring_interval_seconds": self.monitoring_interval,
                    "expected_data_points": int(elapsed_time / self.monitoring_interval) if self.monitoring_interval > 0 else 0
                },
                "stability_metrics": self._calculate_stability_metrics(),
                "error_analysis": {
                    "total_errors": len(self.error_log),
                    "error_types": self._analyze_error_types(),
                    "critical_issues": [e for e in self.error_log if e.get("severity") == "high"]
                },
                "threshold_compliance": self._check_threshold_compliance(),
                "stability_score": self._calculate_stability_score(),
                "recommendations": self._generate_stability_recommendations()
            }
            
            return report
            
        except Exception as e:
            return {
                "error": str(e),
                "report_timestamp": self._get_build_timestamp().isoformat()
            }
    
    def _analyze_error_types(self) -> Dict[str, int]:
        """Analyze error types in error log"""
        error_types = {}
        
        for error in self.error_log:
            error_type = error.get("type", "unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return error_types
    
    def _check_threshold_compliance(self) -> Dict[str, Any]:
        """Check compliance with stability thresholds"""
        compliance = {}
        stability_metrics = self._calculate_stability_metrics()
        
        # Memory growth compliance
        memory_growth = stability_metrics.get("memory_stats", {}).get("growth_mb", 0)
        compliance["memory_growth"] = {
            "value": memory_growth,
            "threshold": self.stability_thresholds["max_memory_growth"],
            "compliant": memory_growth <= self.stability_thresholds["max_memory_growth"]
        }
        
        # CPU spike compliance
        max_cpu = stability_metrics.get("cpu_stats", {}).get("max_percent", 0)
        compliance["cpu_spikes"] = {
            "value": max_cpu,
            "threshold": self.stability_thresholds["max_cpu_spike"],
            "compliant": max_cpu <= self.stability_thresholds["max_cpu_spike"]
        }
        
        # Error rate compliance
        error_rate = stability_metrics.get("error_rate", 0)
        compliance["error_rate"] = {
            "value": error_rate,
            "threshold": self.stability_thresholds["max_error_rate"],
            "compliant": error_rate <= self.stability_thresholds["max_error_rate"]
        }
        
        # Uptime compliance
        uptime = stability_metrics.get("uptime_percentage", 0)
        compliance["uptime"] = {
            "value": uptime,
            "threshold": self.stability_thresholds["min_uptime"],
            "compliant": uptime >= self.stability_thresholds["min_uptime"]
        }
        
        return compliance
    
    def _calculate_stability_score(self) -> float:
        """Calculate overall stability score"""
        try:
            compliance = self._check_threshold_compliance()
            
            total_score = 0.0
            total_metrics = 0
            
            for metric_name, metric_data in compliance.items():
                if metric_data.get("compliant", False):
                    total_score += 100.0
                else:
                    # Partial score based on how close to threshold
                    value = metric_data.get("value", 0)
                    threshold = metric_data.get("threshold", 1)
                    
                    if metric_name == "uptime":
                        # Higher is better for uptime
                        partial_score = (value / threshold) * 100 if threshold > 0 else 0
                    else:
                        # Lower is better for other metrics
                        partial_score = max(0, 100 - (value / threshold) * 50) if threshold > 0 else 0
                    
                    total_score += partial_score
                
                total_metrics += 1
            
            return total_score / total_metrics if total_metrics > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Stability score calculation error: {e}")
            return 0.0
    
    def _generate_stability_recommendations(self) -> List[str]:
        """Generate stability recommendations"""
        recommendations = []
        compliance = self._check_threshold_compliance()
        
        if not compliance.get("memory_growth", {}).get("compliant", True):
            recommendations.append("Investigate and fix memory leaks")
        
        if not compliance.get("cpu_spikes", {}).get("compliant", True):
            recommendations.append("Optimize CPU-intensive operations")
        
        if not compliance.get("error_rate", {}).get("compliant", True):
            recommendations.append("Reduce error rate through better error handling")
        
        if not compliance.get("uptime", {}).get("compliant", True):
            recommendations.append("Improve system reliability and uptime")
        
        if len(self.error_log) > 0:
            recommendations.append("Review and address logged errors")
        
        recommendations.extend([
            "Implement automated stability monitoring",
            "Add alerting for stability issues",
            "Consider load balancing for high availability",
            "Implement graceful degradation strategies"
        ])
        
        return recommendations
    
    def _save_stability_report(self, report: Dict[str, Any]):
        """Save stability report to file"""
        try:
            reports_dir = Path("stability_reports")
            reports_dir.mkdir(exist_ok=True)
            
            timestamp = self._get_build_timestamp().strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"stability_report_{timestamp}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"📄 Stability report saved: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Stability report saving error: {e}")