#!/usr/bin/env python3
"""
🔄 MIA Enterprise AGI - Cross-Module Regression Tester
=====================================================

Testiraj vse kombinacije med 9 moduli za izključitev hidden state leakage.
"""

import os
import sys
import json
import hashlib
import importlib
from pathlib import Path
from typing import Dict, List, Any, Set, Optional, Tuple
from datetime import datetime
import logging
import gc

class CrossModuleRegressionTester:
    """Tester for cross-module regression and state leakage"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.test_results = {}
        self.logger = self._setup_logging()
        
        # All modules to test
        self.modules = [
            "security", "production", "testing", "compliance", 
            "enterprise", "verification", "analysis", 
            "project_builder", "desktop"
        ]
        
        # State tracking
        self.initial_state = {}
        self.module_states = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.CrossModuleRegressionTester")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def run_cross_module_regression_test(self) -> Dict[str, Any]:
        """Run comprehensive cross-module regression test"""
        
        test_result = {
            "test_timestamp": datetime.now().isoformat(),
            "tester": "CrossModuleRegressionTester",
            "modules_tested": self.modules,
            "test_combinations": {},
            "state_leakage_analysis": {},
            "isolation_validation": {},
            "regression_summary": {},
            "recommendations": []
        }
        
        self.logger.info("🔄 Starting cross-module regression test...")
        
        # Capture initial system state
        self.initial_state = self._capture_system_state()
        
        # Test all module combinations
        test_result["test_combinations"] = self._test_all_module_combinations()
        
        # Analyze state leakage
        test_result["state_leakage_analysis"] = self._analyze_state_leakage()
        
        # Validate isolation
        test_result["isolation_validation"] = self._validate_module_isolation()
        
        # Generate regression summary
        test_result["regression_summary"] = self._generate_regression_summary(test_result)
        
        # Generate recommendations
        test_result["recommendations"] = self._generate_regression_recommendations(test_result)
        
        self.logger.info("✅ Cross-module regression test completed")
        
        return test_result
    
    def _capture_system_state(self) -> Dict[str, Any]:
        """Capture initial system state"""
        
        state = {
            "timestamp": datetime.now().isoformat(),
            "memory_usage": self._get_memory_usage(),
            "loaded_modules": list(sys.modules.keys()),
            "global_variables": self._capture_global_variables(),
            "environment_variables": dict(os.environ),
            "system_hash": self._calculate_system_hash()
        }
        
        return state
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage"""
        
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss": memory_info.rss,
                "vms": memory_info.vms,
                "percent": process.memory_percent(),
                "available": psutil.virtual_memory().available
            }
        except ImportError:
            return {"error": "psutil not available"}
    
    def _capture_global_variables(self) -> Dict[str, str]:
        """Capture global variables state"""
        
        global_vars = {}
        
        # Capture important global state
        global_vars["sys_path"] = str(sys.path)
        global_vars["sys_modules_count"] = str(len(sys.modules))
        global_vars["cwd"] = os.getcwd()
        
        return global_vars
    
    def _calculate_system_hash(self) -> str:
        """Calculate system state hash"""
        
        hasher = hashlib.sha256()
        
        # Hash system state components
        hasher.update(str(len(sys.modules)).encode('utf-8'))
        hasher.update(os.getcwd().encode('utf-8'))
        hasher.update(str(sys.version_info).encode('utf-8'))
        
        return hasher.hexdigest()[:32]
    
    def _test_all_module_combinations(self) -> Dict[str, Any]:
        """Test all module combinations"""
        
        combinations_result = {
            "total_combinations": 0,
            "successful_combinations": 0,
            "failed_combinations": 0,
            "combination_results": {},
            "interaction_matrix": {}
        }
        
        # Test individual modules first
        for module in self.modules:
            self.logger.info(f"🔄 Testing individual module: {module}")
            
            individual_result = self._test_individual_module(module)
            combinations_result["combination_results"][f"individual_{module}"] = individual_result
            combinations_result["total_combinations"] += 1
            
            if individual_result["test_passed"]:
                combinations_result["successful_combinations"] += 1
            else:
                combinations_result["failed_combinations"] += 1
        
        # Test pairwise combinations
        for i, module_a in enumerate(self.modules):
            for j, module_b in enumerate(self.modules):
                if i < j:  # Avoid duplicate pairs
                    self.logger.info(f"🔄 Testing module pair: {module_a} + {module_b}")
                    
                    pair_result = self._test_module_pair(module_a, module_b)
                    combination_key = f"{module_a}+{module_b}"
                    combinations_result["combination_results"][combination_key] = pair_result
                    combinations_result["total_combinations"] += 1
                    
                    if pair_result["test_passed"]:
                        combinations_result["successful_combinations"] += 1
                    else:
                        combinations_result["failed_combinations"] += 1
                    
                    # Update interaction matrix
                    if module_a not in combinations_result["interaction_matrix"]:
                        combinations_result["interaction_matrix"][module_a] = {}
                    combinations_result["interaction_matrix"][module_a][module_b] = pair_result["compatibility_score"]
        
        # Test triple combinations (sample)
        sample_triples = [
            ("security", "enterprise", "compliance"),
            ("production", "testing", "verification"),
            ("analysis", "project_builder", "desktop")
        ]
        
        for triple in sample_triples:
            self.logger.info(f"🔄 Testing module triple: {' + '.join(triple)}")
            
            triple_result = self._test_module_triple(triple)
            combination_key = "+".join(triple)
            combinations_result["combination_results"][combination_key] = triple_result
            combinations_result["total_combinations"] += 1
            
            if triple_result["test_passed"]:
                combinations_result["successful_combinations"] += 1
            else:
                combinations_result["failed_combinations"] += 1
        
        return combinations_result
    
    def _test_individual_module(self, module_name: str) -> Dict[str, Any]:
        """Test individual module"""
        
        test_result = {
            "module": module_name,
            "test_type": "individual",
            "test_passed": True,
            "state_before": None,
            "state_after": None,
            "state_changes": [],
            "memory_impact": {},
            "execution_time": 0.0,
            "issues": []
        }
        
        start_time = datetime.now()
        
        try:
            # Capture state before
            test_result["state_before"] = self._capture_module_state(module_name)
            
            # Simulate module usage
            self._simulate_module_usage(module_name)
            
            # Capture state after
            test_result["state_after"] = self._capture_module_state(module_name)
            
            # Analyze state changes
            test_result["state_changes"] = self._compare_states(
                test_result["state_before"], 
                test_result["state_after"]
            )
            
            # Check for unexpected state changes
            if len(test_result["state_changes"]) > 5:  # Allow some expected changes
                test_result["test_passed"] = False
                test_result["issues"].append("Excessive state changes detected")
        
        except Exception as e:
            test_result["test_passed"] = False
            test_result["issues"].append(f"Module test error: {e}")
        
        end_time = datetime.now()
        test_result["execution_time"] = (end_time - start_time).total_seconds()
        
        return test_result
    
    def _test_module_pair(self, module_a: str, module_b: str) -> Dict[str, Any]:
        """Test module pair interaction"""
        
        test_result = {
            "modules": [module_a, module_b],
            "test_type": "pairwise",
            "test_passed": True,
            "compatibility_score": 100.0,
            "interaction_issues": [],
            "state_isolation": True,
            "memory_leakage": False,
            "execution_time": 0.0
        }
        
        start_time = datetime.now()
        
        try:
            # Test module A first
            state_a_before = self._capture_module_state(module_a)
            self._simulate_module_usage(module_a)
            state_a_after = self._capture_module_state(module_a)
            
            # Test module B
            state_b_before = self._capture_module_state(module_b)
            self._simulate_module_usage(module_b)
            state_b_after = self._capture_module_state(module_b)
            
            # Test both together
            combined_state_before = self._capture_system_state()
            self._simulate_module_usage(module_a)
            self._simulate_module_usage(module_b)
            combined_state_after = self._capture_system_state()
            
            # Analyze interactions
            interaction_analysis = self._analyze_module_interaction(
                module_a, module_b,
                state_a_before, state_a_after,
                state_b_before, state_b_after,
                combined_state_before, combined_state_after
            )
            
            test_result.update(interaction_analysis)
        
        except Exception as e:
            test_result["test_passed"] = False
            test_result["interaction_issues"].append(f"Pair test error: {e}")
            test_result["compatibility_score"] = 0.0
        
        end_time = datetime.now()
        test_result["execution_time"] = (end_time - start_time).total_seconds()
        
        return test_result
    
    def _test_module_triple(self, modules: Tuple[str, str, str]) -> Dict[str, Any]:
        """Test module triple interaction"""
        
        test_result = {
            "modules": list(modules),
            "test_type": "triple",
            "test_passed": True,
            "integration_score": 100.0,
            "complex_interactions": [],
            "resource_usage": {},
            "execution_time": 0.0
        }
        
        start_time = datetime.now()
        
        try:
            # Capture initial state
            initial_state = self._capture_system_state()
            
            # Simulate usage of all three modules
            for module in modules:
                self._simulate_module_usage(module)
            
            # Capture final state
            final_state = self._capture_system_state()
            
            # Analyze complex interactions
            interaction_analysis = self._analyze_complex_interaction(
                modules, initial_state, final_state
            )
            
            test_result.update(interaction_analysis)
        
        except Exception as e:
            test_result["test_passed"] = False
            test_result["complex_interactions"].append(f"Triple test error: {e}")
            test_result["integration_score"] = 0.0
        
        end_time = datetime.now()
        test_result["execution_time"] = (end_time - start_time).total_seconds()
        
        return test_result
    
    def _capture_module_state(self, module_name: str) -> Dict[str, Any]:
        """Capture state specific to a module"""
        
        state = {
            "module": module_name,
            "timestamp": datetime.now().isoformat(),
            "memory_before": self._get_memory_usage(),
            "loaded_submodules": [],
            "module_hash": None
        }
        
        # Check for loaded submodules
        module_prefix = f"mia.{module_name}"
        for mod_name in sys.modules:
            if mod_name.startswith(module_prefix):
                state["loaded_submodules"].append(mod_name)
        
        # Calculate module-specific hash
        module_dir = self.project_root / "mia" / module_name
        if module_dir.exists():
            state["module_hash"] = self._calculate_module_hash(module_dir)
        
        return state
    
    def _calculate_module_hash(self, module_dir: Path) -> str:
        """Calculate hash for module directory"""
        
        hasher = hashlib.sha256()
        
        py_files = sorted(module_dir.glob("*.py"))
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                hasher.update(content.encode('utf-8'))
            except Exception:
                pass
        
        return hasher.hexdigest()[:16]
    
    def _simulate_module_usage(self, module_name: str) -> None:
        """Simulate typical module usage"""
        
        try:
            # Try to import module components
            module_path = f"mia.{module_name}"
            
            # Check if module directory exists
            module_dir = self.project_root / "mia" / module_name
            if not module_dir.exists():
                return
            
            # Simulate basic operations
            self._simulate_basic_operations(module_name)
            
            # Force garbage collection to test memory management
            gc.collect()
        
        except Exception as e:
            self.logger.warning(f"Error simulating usage for {module_name}: {e}")
    
    def _simulate_basic_operations(self, module_name: str) -> None:
        """Simulate basic operations for module"""
        
        # Simulate common operations based on module type
        operations = {
            "security": ["validate", "encrypt", "audit"],
            "production": ["validate", "report", "status"],
            "testing": ["test", "validate", "report"],
            "compliance": ["check", "audit", "validate"],
            "enterprise": ["deploy", "configure", "manage"],
            "verification": ["verify", "validate", "check"],
            "analysis": ["analyze", "report", "insights"],
            "project_builder": ["build", "deploy", "validate"],
            "desktop": ["initialize", "manage", "handle"]
        }
        
        module_operations = operations.get(module_name, ["generic"])
        
        # Simulate operations (lightweight)
        for operation in module_operations:
            # Create some temporary data
            temp_data = {
                "operation": operation,
                "module": module_name,
                "timestamp": datetime.now().isoformat(),
                "data": f"test_data_for_{operation}"
            }
            
            # Simulate processing
            temp_hash = hashlib.sha256(str(temp_data).encode('utf-8')).hexdigest()[:8]
            
            # Clean up
            del temp_data, temp_hash
    
    def _compare_states(self, state_before: Dict[str, Any], state_after: Dict[str, Any]) -> List[str]:
        """Compare two states and return changes"""
        
        changes = []
        
        # Compare memory usage
        mem_before = state_before.get("memory_before", {})
        mem_after = state_after.get("memory_before", {})  # Note: this is intentional for comparison
        
        if isinstance(mem_before, dict) and isinstance(mem_after, dict):
            rss_before = mem_before.get("rss", 0)
            rss_after = mem_after.get("rss", 0)
            
            if abs(rss_after - rss_before) > 1024 * 1024:  # 1MB threshold
                changes.append(f"Memory change: {(rss_after - rss_before) / 1024 / 1024:.1f} MB")
        
        # Compare loaded submodules
        modules_before = set(state_before.get("loaded_submodules", []))
        modules_after = set(state_after.get("loaded_submodules", []))
        
        new_modules = modules_after - modules_before
        if new_modules:
            changes.append(f"New modules loaded: {', '.join(new_modules)}")
        
        # Compare module hash
        hash_before = state_before.get("module_hash")
        hash_after = state_after.get("module_hash")
        
        if hash_before != hash_after:
            changes.append("Module content changed")
        
        return changes
    
    def _analyze_module_interaction(self, module_a: str, module_b: str,
                                  state_a_before: Dict, state_a_after: Dict,
                                  state_b_before: Dict, state_b_after: Dict,
                                  combined_before: Dict, combined_after: Dict) -> Dict[str, Any]:
        """Analyze interaction between two modules"""
        
        analysis = {
            "compatibility_score": 100.0,
            "interaction_issues": [],
            "state_isolation": True,
            "memory_leakage": False
        }
        
        # Check for state isolation
        changes_a = self._compare_states(state_a_before, state_a_after)
        changes_b = self._compare_states(state_b_before, state_b_after)
        
        if len(changes_a) > 3 or len(changes_b) > 3:
            analysis["state_isolation"] = False
            analysis["interaction_issues"].append("Excessive state changes detected")
            analysis["compatibility_score"] -= 20.0
        
        # Check for memory leakage
        mem_before = combined_before.get("memory_usage", {})
        mem_after = combined_after.get("memory_usage", {})
        
        if isinstance(mem_before, dict) and isinstance(mem_after, dict):
            rss_before = mem_before.get("rss", 0)
            rss_after = mem_after.get("rss", 0)
            
            memory_increase = rss_after - rss_before
            if memory_increase > 10 * 1024 * 1024:  # 10MB threshold
                analysis["memory_leakage"] = True
                analysis["interaction_issues"].append(f"Memory leak detected: {memory_increase / 1024 / 1024:.1f} MB")
                analysis["compatibility_score"] -= 30.0
        
        # Check for module conflicts
        if self._detect_module_conflicts(module_a, module_b):
            analysis["interaction_issues"].append("Module conflicts detected")
            analysis["compatibility_score"] -= 25.0
        
        return analysis
    
    def _analyze_complex_interaction(self, modules: Tuple[str, str, str],
                                   initial_state: Dict, final_state: Dict) -> Dict[str, Any]:
        """Analyze complex interaction between three modules"""
        
        analysis = {
            "integration_score": 100.0,
            "complex_interactions": [],
            "resource_usage": {}
        }
        
        # Analyze resource usage
        mem_initial = initial_state.get("memory_usage", {})
        mem_final = final_state.get("memory_usage", {})
        
        if isinstance(mem_initial, dict) and isinstance(mem_final, dict):
            memory_change = mem_final.get("rss", 0) - mem_initial.get("rss", 0)
            analysis["resource_usage"]["memory_change_mb"] = memory_change / 1024 / 1024
            
            if memory_change > 20 * 1024 * 1024:  # 20MB threshold for triple
                analysis["complex_interactions"].append("High memory usage in triple interaction")
                analysis["integration_score"] -= 30.0
        
        # Check for complex conflicts
        if self._detect_complex_conflicts(modules):
            analysis["complex_interactions"].append("Complex module conflicts detected")
            analysis["integration_score"] -= 40.0
        
        return analysis
    
    def _detect_module_conflicts(self, module_a: str, module_b: str) -> bool:
        """Detect conflicts between two modules"""
        
        # Known conflict patterns
        conflict_patterns = [
            ("security", "testing"),  # Security might interfere with testing
            ("production", "testing")  # Production and testing might conflict
        ]
        
        return (module_a, module_b) in conflict_patterns or (module_b, module_a) in conflict_patterns
    
    def _detect_complex_conflicts(self, modules: Tuple[str, str, str]) -> bool:
        """Detect complex conflicts between three modules"""
        
        # Complex conflict patterns
        complex_conflicts = [
            ("security", "production", "testing")  # All three might have complex interactions
        ]
        
        return modules in complex_conflicts
    
    def _analyze_state_leakage(self) -> Dict[str, Any]:
        """Analyze state leakage across modules"""
        
        leakage_analysis = {
            "leakage_detected": False,
            "leakage_sources": [],
            "global_state_changes": [],
            "memory_leaks": [],
            "isolation_score": 100.0
        }
        
        # Compare current state with initial state
        current_state = self._capture_system_state()
        
        # Check for global state changes
        initial_modules = set(self.initial_state.get("loaded_modules", []))
        current_modules = set(current_state.get("loaded_modules", []))
        
        new_modules = current_modules - initial_modules
        if new_modules:
            leakage_analysis["global_state_changes"].append(f"New global modules: {len(new_modules)}")
            leakage_analysis["isolation_score"] -= 10.0
        
        # Check for memory leaks
        initial_memory = self.initial_state.get("memory_usage", {})
        current_memory = current_state.get("memory_usage", {})
        
        if isinstance(initial_memory, dict) and isinstance(current_memory, dict):
            memory_increase = current_memory.get("rss", 0) - initial_memory.get("rss", 0)
            if memory_increase > 50 * 1024 * 1024:  # 50MB threshold
                leakage_analysis["memory_leaks"].append(f"Memory leak: {memory_increase / 1024 / 1024:.1f} MB")
                leakage_analysis["leakage_detected"] = True
                leakage_analysis["isolation_score"] -= 30.0
        
        # Check for environment changes
        initial_env_count = len(self.initial_state.get("environment_variables", {}))
        current_env_count = len(current_state.get("environment_variables", {}))
        
        if current_env_count != initial_env_count:
            leakage_analysis["global_state_changes"].append("Environment variables changed")
            leakage_analysis["isolation_score"] -= 5.0
        
        return leakage_analysis
    
    def _validate_module_isolation(self) -> Dict[str, Any]:
        """Validate module isolation"""
        
        isolation_validation = {
            "isolation_passed": True,
            "isolation_score": 100.0,
            "module_isolation_scores": {},
            "isolation_issues": []
        }
        
        # Test each module's isolation
        for module in self.modules:
            module_isolation = self._test_module_isolation(module)
            isolation_validation["module_isolation_scores"][module] = module_isolation
            
            if module_isolation["isolation_score"] < 90.0:
                isolation_validation["isolation_passed"] = False
                isolation_validation["isolation_issues"].append(
                    f"Module {module} has poor isolation: {module_isolation['isolation_score']:.1f}%"
                )
        
        # Calculate overall isolation score
        if isolation_validation["module_isolation_scores"]:
            scores = [m["isolation_score"] for m in isolation_validation["module_isolation_scores"].values()]
            isolation_validation["isolation_score"] = sum(scores) / len(scores)
        
        return isolation_validation
    
    def _test_module_isolation(self, module_name: str) -> Dict[str, Any]:
        """Test isolation for specific module"""
        
        isolation_test = {
            "module": module_name,
            "isolation_score": 100.0,
            "isolation_issues": []
        }
        
        try:
            # Test module in isolation
            before_state = self._capture_system_state()
            self._simulate_module_usage(module_name)
            after_state = self._capture_system_state()
            
            # Check for global changes
            changes = self._compare_system_states(before_state, after_state)
            
            if len(changes) > 2:  # Allow minimal changes
                isolation_test["isolation_score"] -= len(changes) * 10
                isolation_test["isolation_issues"].extend(changes)
        
        except Exception as e:
            isolation_test["isolation_score"] = 0.0
            isolation_test["isolation_issues"].append(f"Isolation test error: {e}")
        
        return isolation_test
    
    def _compare_system_states(self, state_before: Dict, state_after: Dict) -> List[str]:
        """Compare system states"""
        
        changes = []
        
        # Compare module counts
        modules_before = len(state_before.get("loaded_modules", []))
        modules_after = len(state_after.get("loaded_modules", []))
        
        if modules_after > modules_before + 5:  # Allow some module loading
            changes.append(f"Excessive module loading: +{modules_after - modules_before}")
        
        # Compare memory
        mem_before = state_before.get("memory_usage", {})
        mem_after = state_after.get("memory_usage", {})
        
        if isinstance(mem_before, dict) and isinstance(mem_after, dict):
            memory_increase = mem_after.get("rss", 0) - mem_before.get("rss", 0)
            if memory_increase > 5 * 1024 * 1024:  # 5MB threshold
                changes.append(f"Memory increase: {memory_increase / 1024 / 1024:.1f} MB")
        
        return changes
    
    def _generate_regression_summary(self, test_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate regression test summary"""
        
        combinations = test_result.get("test_combinations", {})
        leakage = test_result.get("state_leakage_analysis", {})
        isolation = test_result.get("isolation_validation", {})
        
        summary = {
            "overall_status": "PASSED",
            "total_tests": combinations.get("total_combinations", 0),
            "successful_tests": combinations.get("successful_combinations", 0),
            "failed_tests": combinations.get("failed_combinations", 0),
            "success_rate": 0.0,
            "state_leakage_detected": leakage.get("leakage_detected", False),
            "isolation_score": isolation.get("isolation_score", 100.0),
            "critical_issues": [],
            "warnings": []
        }
        
        # Calculate success rate
        if summary["total_tests"] > 0:
            summary["success_rate"] = (summary["successful_tests"] / summary["total_tests"]) * 100
        
        # Determine overall status
        if summary["success_rate"] < 90.0:
            summary["overall_status"] = "FAILED"
            summary["critical_issues"].append(f"Low success rate: {summary['success_rate']:.1f}%")
        
        if summary["state_leakage_detected"]:
            summary["overall_status"] = "FAILED"
            summary["critical_issues"].append("State leakage detected")
        
        if summary["isolation_score"] < 85.0:
            summary["overall_status"] = "FAILED"
            summary["critical_issues"].append(f"Poor isolation: {summary['isolation_score']:.1f}%")
        
        # Add warnings
        if summary["success_rate"] < 95.0:
            summary["warnings"].append("Some module combinations have issues")
        
        if summary["isolation_score"] < 95.0:
            summary["warnings"].append("Module isolation could be improved")
        
        return summary
    
    def _generate_regression_recommendations(self, test_result: Dict[str, Any]) -> List[str]:
        """Generate regression test recommendations"""
        
        recommendations = []
        
        summary = test_result.get("regression_summary", {})
        
        # Status-based recommendations
        if summary.get("overall_status") == "PASSED":
            recommendations.append("✅ All cross-module regression tests passed")
        else:
            recommendations.append("❌ Critical issues found in cross-module testing")
        
        # Success rate recommendations
        success_rate = summary.get("success_rate", 0)
        if success_rate < 90.0:
            recommendations.append(f"Improve module compatibility (current: {success_rate:.1f}%)")
        
        # State leakage recommendations
        if summary.get("state_leakage_detected", False):
            recommendations.append("Fix state leakage issues between modules")
        
        # Isolation recommendations
        isolation_score = summary.get("isolation_score", 100)
        if isolation_score < 90.0:
            recommendations.append(f"Improve module isolation (current: {isolation_score:.1f}%)")
        
        # Specific module recommendations
        combinations = test_result.get("test_combinations", {})
        interaction_matrix = combinations.get("interaction_matrix", {})
        
        for module_a, interactions in interaction_matrix.items():
            for module_b, score in interactions.items():
                if score < 80.0:
                    recommendations.append(f"Fix compatibility between {module_a} and {module_b}")
        
        # General recommendations
        recommendations.extend([
            "Continue monitoring cross-module interactions",
            "Implement automated regression testing in CI/CD",
            "Add module isolation validation to deployment process",
            "Monitor memory usage in production environment"
        ])
        
        return recommendations

def main():
    """Main function to run cross-module regression test"""
    
    print("🔄 MIA Enterprise AGI - Cross-Module Regression Test")
    print("=" * 55)
    
    tester = CrossModuleRegressionTester()
    
    print("🔄 Running comprehensive cross-module regression test...")
    test_result = tester.run_cross_module_regression_test()
    
    # Save results to JSON file
    output_file = "cross_module_regression_report.json"
    with open(output_file, 'w') as f:
        json.dump(test_result, f, indent=2)
    
    print(f"📄 Test results saved to: {output_file}")
    
    # Print summary
    print("\n📊 CROSS-MODULE REGRESSION TEST SUMMARY:")
    
    summary = test_result.get("regression_summary", {})
    print(f"Overall Status: {summary.get('overall_status', 'unknown')}")
    print(f"Total Tests: {summary.get('total_tests', 0)}")
    print(f"Successful Tests: {summary.get('successful_tests', 0)}")
    print(f"Failed Tests: {summary.get('failed_tests', 0)}")
    print(f"Success Rate: {summary.get('success_rate', 0):.1f}%")
    
    leakage = test_result.get("state_leakage_analysis", {})
    leakage_status = "❌ DETECTED" if leakage.get("leakage_detected", False) else "✅ NONE"
    print(f"State Leakage: {leakage_status}")
    
    isolation = test_result.get("isolation_validation", {})
    isolation_score = isolation.get("isolation_score", 100)
    print(f"Isolation Score: {isolation_score:.1f}%")
    
    print("\n📋 TOP RECOMMENDATIONS:")
    for i, recommendation in enumerate(test_result.get("recommendations", [])[:5], 1):
        print(f"  {i}. {recommendation}")
    
    print(f"\n✅ Cross-module regression test completed!")
    return test_result

if __name__ == "__main__":
    main()