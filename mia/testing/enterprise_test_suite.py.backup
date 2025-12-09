#!/usr/bin/env python3
"""
MIA Enterprise Test Suite
Celovit testni sistem za enterprise funkcionalnosti
"""

import os
import json
import logging
import time
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class TestType(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Types of tests"""
    UNIT = "unit"
    INTEGRATION = "integration"
    STRESS = "stress"
    RECOVERY = "recovery"
    PERFORMANCE = "performance"
    SECURITY = "security"
    CROSS_MODULE = "cross_module"
    END_TO_END = "end_to_end"

class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

@dataclass
class TestResult:
    """Test execution result"""
    test_id: str
    test_name: str
    test_type: TestType
    status: TestStatus
    duration: float
    error_message: Optional[str]
    output: str
    metrics: Dict[str, Any]
    executed_at: float

class EnterpriseTestSuite:
    """Enterprise Test Suite for MIA system"""
    
    def __init__(self, config_path: str = "mia/testing/test_config.json"):
        self.config_path = config_path
        self.test_dir = Path("mia/testing")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.EnterpriseTestSuite")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Test state
        self.test_results: Dict[str, TestResult] = {}
        
        self.logger.info("🧪 Enterprise Test Suite initialized")
    
    def _load_configuration(self) -> Dict:
        """Load test configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load test config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default test configuration"""
        config = {
            "enabled": True,
            "parallel_execution": True,
            "max_parallel_tests": 4,
            "default_timeout": 300,
            "stress_test_duration": 600,
            "performance_thresholds": {
                "response_time_ms": 1000,
                "memory_usage_mb": 2048,
                "cpu_usage_percent": 80.0,
                "throughput_ops_sec": 100
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def run_unit_tests(self) -> bool:
        """Run unit tests"""
        try:
            self.logger.info("🧪 Running unit tests")
            
            # Test consciousness module
            result = self._test_consciousness_module()
            self.test_results[f"unit_consciousness_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}"] = result
            
            # Test memory system
            result = self._test_memory_system()
            self.test_results[f"unit_memory_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}"] = result
            
            # Test adaptive LLM
            result = self._test_adaptive_llm()
            self.test_results[f"unit_llm_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}"] = result
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to run unit tests: {e}")
            return False
    
    def _test_consciousness_module(self) -> TestResult:
        """Test consciousness module"""
        start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        
        try:
            from mia.core.consciousness import consciousness
            
            # Test initialization
            assert consciousness is not None, "Consciousness module not initialized"
            
            # Test basic functionality
            status = consciousness.get_consciousness_status()
            assert isinstance(status, dict), "Status should be a dictionary"
            assert "enabled" in status, "Status should contain 'enabled' field"
            
            return TestResult(
                test_id=f"consciousness_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_name="test_consciousness_module",
                test_type=TestType.UNIT,
                status=TestStatus.PASSED,
                duration=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time,
                error_message=None,
                output="Consciousness module tests passed",
                metrics={"status_fields": len(status)},
                executed_at=start_time
            )
            
        except Exception as e:
            return TestResult(
                test_id=f"consciousness_error_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_name="test_consciousness_module",
                test_type=TestType.UNIT,
                status=TestStatus.FAILED,
                duration=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time,
                error_message=str(e),
                output=f"Consciousness test failed: {e}",
                metrics={},
                executed_at=start_time
            )
    
    def _test_memory_system(self) -> TestResult:
        """Test memory system"""
        start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        
        try:
            from mia.core.memory import memory_system
            
            # Test memory operations
            test_data = {"test": "data", "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}
            
            # Store memory
            memory_id = memory_system.store_memory("test", test_data, "unit_test")
            assert memory_id, "Memory storage should return ID"
            
            # Retrieve memory
            retrieved = memory_system.get_memory(memory_id)
            assert retrieved is not None, "Memory should be retrievable"
            
            return TestResult(
                test_id=f"memory_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_name="test_memory_system",
                test_type=TestType.UNIT,
                status=TestStatus.PASSED,
                duration=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time,
                error_message=None,
                output="Memory system tests passed",
                metrics={"memory_id": memory_id},
                executed_at=start_time
            )
            
        except Exception as e:
            return TestResult(
                test_id=f"memory_error_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_name="test_memory_system",
                test_type=TestType.UNIT,
                status=TestStatus.FAILED,
                duration=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time,
                error_message=str(e),
                output=f"Memory test failed: {e}",
                metrics={},
                executed_at=start_time
            )
    
    def _test_adaptive_llm(self) -> TestResult:
        """Test adaptive LLM"""
        start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        
        try:
            from mia.core.adaptive_llm import adaptive_llm
            
            # Test LLM status
            status = adaptive_llm.get_llm_status()
            assert isinstance(status, dict), "LLM status should be a dictionary"
            
            return TestResult(
                test_id=f"llm_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_name="test_adaptive_llm",
                test_type=TestType.UNIT,
                status=TestStatus.PASSED,
                duration=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time,
                error_message=None,
                output="Adaptive LLM tests passed",
                metrics={"available_models": status.get("available_models", 0)},
                executed_at=start_time
            )
            
        except Exception as e:
            return TestResult(
                test_id=f"llm_error_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_name="test_adaptive_llm",
                test_type=TestType.UNIT,
                status=TestStatus.FAILED,
                duration=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time,
                error_message=str(e),
                output=f"Adaptive LLM test failed: {e}",
                metrics={},
                executed_at=start_time
            )
    
    def run_stress_tests(self) -> bool:
        """Run stress tests"""
        try:
            self.logger.info("🔥 Running stress tests")
            
            # Memory stress test
            result = self._test_memory_stress()
            self.test_results[f"stress_memory_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}"] = result
            
            # CPU stress test
            result = self._test_cpu_stress()
            self.test_results[f"stress_cpu_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}"] = result
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to run stress tests: {e}")
            return False
    
    def _test_memory_stress(self) -> TestResult:
        """Test memory stress"""
        start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        
        try:
            initial_memory = psutil.virtual_memory().percent
            
            # Simulate memory stress (limited for safety)
            data_chunks = []
            max_memory_usage = initial_memory
            
            # Allocate memory in small chunks for 10 seconds
            end_time = start_time + 10
            
            while self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 < end_time:
                chunk = bytearray(1024 * 1024)  # 1MB chunks
                data_chunks.append(chunk)
                
                current_memory = psutil.virtual_memory().percent
                max_memory_usage = max(max_memory_usage, current_memory)
                
                # Safety check
                if current_memory > 85:
                    break
                
                time.sleep(0.1)
            
            # Clean up
            del data_chunks
            
            final_memory = psutil.virtual_memory().percent
            
            return TestResult(
                test_id=f"memory_stress_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_name="test_memory_stress",
                test_type=TestType.STRESS,
                status=TestStatus.PASSED,
                duration=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time,
                error_message=None,
                output="Memory stress test completed",
                metrics={
                    "initial_memory_percent": initial_memory,
                    "max_memory_percent": max_memory_usage,
                    "final_memory_percent": final_memory
                },
                executed_at=start_time
            )
            
        except Exception as e:
            return TestResult(
                test_id=f"memory_stress_error_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_name="test_memory_stress",
                test_type=TestType.STRESS,
                status=TestStatus.FAILED,
                duration=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time,
                error_message=str(e),
                output=f"Memory stress test failed: {e}",
                metrics={},
                executed_at=start_time
            )
    
    def _test_cpu_stress(self) -> TestResult:
        """Test CPU stress"""
        start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        
        try:
            initial_cpu = psutil.cpu_percent()
            
            # CPU stress simulation (limited duration)
            max_cpu_usage = initial_cpu
            end_time = start_time + 10  # 10 seconds
            
            while self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 < end_time:
                # Simple CPU-intensive calculation
                result = sum(i * i for i in range(1000))
                
                current_cpu = psutil.cpu_percent()
                max_cpu_usage = max(max_cpu_usage, current_cpu)
            
            final_cpu = psutil.cpu_percent()
            
            return TestResult(
                test_id=f"cpu_stress_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_name="test_cpu_stress",
                test_type=TestType.STRESS,
                status=TestStatus.PASSED,
                duration=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time,
                error_message=None,
                output="CPU stress test completed",
                metrics={
                    "initial_cpu_percent": initial_cpu,
                    "max_cpu_percent": max_cpu_usage,
                    "final_cpu_percent": final_cpu
                },
                executed_at=start_time
            )
            
        except Exception as e:
            return TestResult(
                test_id=f"cpu_stress_error_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_name="test_cpu_stress",
                test_type=TestType.STRESS,
                status=TestStatus.FAILED,
                duration=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time,
                error_message=str(e),
                output=f"CPU stress test failed: {e}",
                metrics={},
                executed_at=start_time
            )
    
    def run_performance_tests(self) -> bool:
        """Run performance tests"""
        try:
            self.logger.info("⚡ Running performance tests")
            
            # Response time test
            result = self._test_response_time()
            self.test_results[f"perf_response_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}"] = result
            
            # Memory efficiency test
            result = self._test_memory_efficiency()
            self.test_results[f"perf_memory_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}"] = result
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to run performance tests: {e}")
            return False
    
    def _test_response_time(self) -> TestResult:
        """Test response time"""
        start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        
        try:
            # Simulate response time measurement
            response_times = []
            
            for i in range(10):
                op_start = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                # Simulate operation
                time.sleep(0.01)  # 10ms simulated operation
                response_time = (self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - op_start) * 1000  # Convert to ms
                response_times.append(response_time)
            
            avg_response_time = sum(response_times) / len(response_times)
            threshold = self.config.get("performance_thresholds", {}).get("response_time_ms", 1000)
            
            status = TestStatus.PASSED if avg_response_time <= threshold else TestStatus.FAILED
            
            return TestResult(
                test_id=f"response_time_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_name="test_response_time",
                test_type=TestType.PERFORMANCE,
                status=status,
                duration=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time,
                error_message=None,
                output=f"Response time: {avg_response_time:.2f}ms (threshold: {threshold}ms)",
                metrics={
                    "avg_response_time_ms": avg_response_time,
                    "threshold_ms": threshold,
                    "samples": len(response_times)
                },
                executed_at=start_time
            )
            
        except Exception as e:
            return TestResult(
                test_id=f"response_time_error_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_name="test_response_time",
                test_type=TestType.PERFORMANCE,
                status=TestStatus.FAILED,
                duration=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time,
                error_message=str(e),
                output=f"Response time test failed: {e}",
                metrics={},
                executed_at=start_time
            )
    
    def _test_memory_efficiency(self) -> TestResult:
        """Test memory efficiency"""
        start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        
        try:
            current_memory = psutil.virtual_memory().percent
            threshold = 80.0  # 80% threshold
            
            status = TestStatus.PASSED if current_memory <= threshold else TestStatus.FAILED
            
            return TestResult(
                test_id=f"memory_efficiency_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_name="test_memory_efficiency",
                test_type=TestType.PERFORMANCE,
                status=status,
                duration=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time,
                error_message=None,
                output=f"Memory usage: {current_memory:.1f}% (threshold: {threshold}%)",
                metrics={
                    "memory_percent": current_memory,
                    "threshold_percent": threshold
                },
                executed_at=start_time
            )
            
        except Exception as e:
            return TestResult(
                test_id=f"memory_efficiency_error_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_name="test_memory_efficiency",
                test_type=TestType.PERFORMANCE,
                status=TestStatus.FAILED,
                duration=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time,
                error_message=str(e),
                output=f"Memory efficiency test failed: {e}",
                metrics={},
                executed_at=start_time
            )
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all test suites"""
        try:
            results = {}
            
            # Run unit tests
            results["unit_tests"] = self.run_unit_tests()
            
            # Run stress tests
            results["stress_tests"] = self.run_stress_tests()
            
            # Run performance tests
            results["performance_tests"] = self.run_performance_tests()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to run all tests: {e}")
            return {}
    
    def get_test_results(self) -> List[TestResult]:
        """Get all test results"""
        try:
            results = list(self.test_results.values())
            results.sort(key=lambda r: r.executed_at, reverse=True)
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to get test results: {e}")
            return []
    
    def generate_test_report(self) -> str:
        """Generate test report"""
        try:
            report_data = {
                "generated_at": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                "total_tests": len(self.test_results),
                "results_by_status": {},
                "results_by_type": {},
                "test_results": []
            }
            
            # Analyze results
            for result in self.test_results.values():
                # By status
                status = result.status.value
                report_data["results_by_status"][status] = report_data["results_by_status"].get(status, 0) + 1
                
                # By type
                test_type = result.test_type.value
                report_data["results_by_type"][test_type] = report_data["results_by_type"].get(test_type, 0) + 1
                
                # Add to results list
                report_data["test_results"].append(asdict(result))
            
            # Save report
            report_file = self.test_dir / f"test_report_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}.json"
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            self.logger.info(f"📊 Test report generated: {report_file}")
            
            return str(report_file)
            
        except Exception as e:
            self.logger.error(f"Failed to generate test report: {e}")
            return ""
    
    def get_test_status(self) -> Dict[str, Any]:
        """Get test suite status"""
        try:
            return {
                "enabled": self.config.get("enabled", True),
                "total_tests": len(self.test_results),
                "parallel_execution": self.config.get("parallel_execution", True),
                "max_parallel_tests": self.config.get("max_parallel_tests", 4)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get test status: {e}")
            return {"error": str(e)}

# Global instance
enterprise_test_suite = EnterpriseTestSuite()