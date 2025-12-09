#!/usr/bin/env python3
"""
🔍 MIA Enterprise AGI - Introspective Hash Validator
===================================================

Izvede introspektivni test s 5000 cikli za hash konsistenco.
"""

import os
import sys
import json
import time
import hashlib
import threading
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime
import logging

class IntrospectiveHashValidator:
    """Introspective hash validator for 5000-cycle consistency testing"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.validation_results = {}
        self.hash_history = []
        self.cycle_count = 5000
        self.logger = self._setup_logging()
        
        # Hash consistency tracking
        self.consistent_hashes = set()
        self.inconsistent_hashes = set()
        self.hash_variations = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.IntrospectiveHashValidator")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def run_introspective_validation(self) -> Dict[str, Any]:
        """Run 5000-cycle introspective hash validation"""
        
        validation_result = {
            "validation_timestamp": datetime.now().isoformat(),
            "validator": "IntrospectiveHashValidator",
            "total_cycles": self.cycle_count,
            "hash_consistency": {},
            "module_stability": {},
            "performance_metrics": {},
            "deterministic_analysis": {},
            "recommendations": []
        }
        
        self.logger.info(f"🔍 Starting {self.cycle_count}-cycle introspective hash validation...")
        
        start_time = time.time()
        
        # Run validation cycles
        for cycle in range(self.cycle_count):
            if cycle % 500 == 0:
                self.logger.info(f"🔄 Cycle {cycle}/{self.cycle_count} ({(cycle/self.cycle_count)*100:.1f}%)")
            
            cycle_result = self._run_validation_cycle(cycle)
            self.hash_history.append(cycle_result)
            
            # Early termination if major inconsistency detected
            if cycle > 100 and self._detect_major_inconsistency():
                self.logger.warning(f"⚠️ Major inconsistency detected at cycle {cycle}")
                break
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        validation_result["hash_consistency"] = self._analyze_hash_consistency()
        validation_result["module_stability"] = self._analyze_module_stability()
        validation_result["performance_metrics"] = self._analyze_performance_metrics(total_time)
        validation_result["deterministic_analysis"] = self._analyze_deterministic_behavior()
        validation_result["recommendations"] = self._generate_validation_recommendations()
        
        self.logger.info(f"✅ Introspective validation completed in {total_time:.2f}s")
        
        return validation_result
    
    def _run_validation_cycle(self, cycle: int) -> Dict[str, Any]:
        """Run a single validation cycle"""
        
        cycle_start = time.time()
        
        cycle_result = {
            "cycle": cycle,
            "timestamp": datetime.now().isoformat(),
            "module_hashes": {},
            "system_state": {},
            "execution_time": 0.0,
            "errors": []
        }
        
        try:
            # Calculate hashes for all modules
            cycle_result["module_hashes"] = self._calculate_module_hashes()
            
            # Capture system state
            cycle_result["system_state"] = self._capture_system_state()
            
            # Perform introspective analysis
            introspective_data = self._perform_introspective_analysis()
            cycle_result["introspective_hash"] = self._hash_data(introspective_data)
            
        except Exception as e:
            cycle_result["errors"].append(str(e))
            self.logger.error(f"Error in cycle {cycle}: {e}")
        
        cycle_result["execution_time"] = time.time() - cycle_start
        
        return cycle_result
    
    def _calculate_module_hashes(self) -> Dict[str, str]:
        """Calculate hashes for all modules"""
        
        module_hashes = {}
        
        # Define module directories to hash
        module_dirs = [
            "mia/security",
            "mia/production", 
            "mia/testing",
            "mia/compliance",
            "mia/enterprise",
            "mia/verification",
            "mia/analysis",
            "mia/project_builder",
            "mia/desktop"
        ]
        
        for module_dir in module_dirs:
            module_path = self.project_root / module_dir
            if module_path.exists():
                module_hash = self._hash_directory(module_path)
                module_hashes[module_dir] = module_hash
        
        return module_hashes
    
    def _hash_directory(self, directory: Path) -> str:
        """Calculate hash for a directory"""
        
        hasher = hashlib.sha256()
        
        # Get all Python files in directory
        py_files = sorted(directory.glob("*.py"))
        
        for py_file in py_files:
            if py_file.name.startswith("__"):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                # Normalize content (remove timestamps, random values)
                normalized_content = self._normalize_content(content)
                hasher.update(normalized_content.encode('utf-8'))
            except Exception as e:
                self.logger.warning(f"Could not hash {py_file}: {e}")
        
        return hasher.hexdigest()
    
    def _normalize_content(self, content: str) -> str:
        """Normalize content for consistent hashing"""
        
        # Remove common non-deterministic elements
        lines = content.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Skip timestamp lines
            if any(keyword in line.lower() for keyword in ['timestamp', 'datetime.now()', 'time.time()']):
                continue
            
            # Skip random or UUID lines
            if any(keyword in line.lower() for keyword in ['random', 'uuid', 'randint']):
                continue
            
            # Skip version or build info
            if any(keyword in line.lower() for keyword in ['version =', 'build =', '__version__']):
                continue
            
            normalized_lines.append(line.strip())
        
        return '\n'.join(normalized_lines)
    
    def _capture_system_state(self) -> Dict[str, Any]:
        """Capture current system state"""
        
        system_state = {
            "module_count": 0,
            "file_count": 0,
            "total_size": 0,
            "python_version": sys.version_info[:2]
        }
        
        try:
            # Count modules and files
            for module_dir in ["mia/security", "mia/production", "mia/testing", "mia/compliance", "mia/enterprise"]:
                module_path = self.project_root / module_dir
                if module_path.exists():
                    system_state["module_count"] += 1
                    
                    py_files = list(module_path.glob("*.py"))
                    system_state["file_count"] += len(py_files)
                    
                    for py_file in py_files:
                        try:
                            system_state["total_size"] += py_file.stat().st_size
                        except:
                            pass
        
        except Exception as e:
            self.logger.warning(f"Error capturing system state: {e}")
        
        return system_state
    
    def _perform_introspective_analysis(self) -> Dict[str, Any]:
        """Perform introspective analysis of the system"""
        
        introspective_data = {
            "analysis_type": "introspective_validation",
            "system_components": [],
            "module_relationships": {},
            "stability_indicators": {}
        }
        
        # Analyze system components
        module_dirs = ["mia/security", "mia/production", "mia/testing", "mia/compliance", "mia/enterprise"]
        
        for module_dir in module_dirs:
            module_path = self.project_root / module_dir
            if module_path.exists():
                component_analysis = self._analyze_component(module_path)
                introspective_data["system_components"].append(component_analysis)
        
        # Analyze module relationships
        introspective_data["module_relationships"] = self._analyze_module_relationships()
        
        # Calculate stability indicators
        introspective_data["stability_indicators"] = self._calculate_stability_indicators()
        
        return introspective_data
    
    def _analyze_component(self, component_path: Path) -> Dict[str, Any]:
        """Analyze a single component"""
        
        component_analysis = {
            "component": component_path.name,
            "file_count": 0,
            "class_count": 0,
            "function_count": 0,
            "import_count": 0
        }
        
        try:
            py_files = list(component_path.glob("*.py"))
            component_analysis["file_count"] = len(py_files)
            
            for py_file in py_files:
                if py_file.name.startswith("__"):
                    continue
                
                try:
                    content = py_file.read_text(encoding='utf-8')
                    
                    # Count classes and functions
                    component_analysis["class_count"] += content.count("class ")
                    component_analysis["function_count"] += content.count("def ")
                    component_analysis["import_count"] += content.count("import ") + content.count("from ")
                
                except Exception:
                    pass
        
        except Exception as e:
            self.logger.warning(f"Error analyzing component {component_path}: {e}")
        
        return component_analysis
    
    def _analyze_module_relationships(self) -> Dict[str, List[str]]:
        """Analyze relationships between modules"""
        
        relationships = {}
        
        module_dirs = ["mia/security", "mia/production", "mia/testing", "mia/compliance", "mia/enterprise"]
        
        for module_dir in module_dirs:
            module_path = self.project_root / module_dir
            if not module_path.exists():
                continue
            
            module_name = module_path.name
            relationships[module_name] = []
            
            # Find imports to other modules
            py_files = list(module_path.glob("*.py"))
            
            for py_file in py_files:
                if py_file.name.startswith("__"):
                    continue
                
                try:
                    content = py_file.read_text(encoding='utf-8')
                    
                    for other_module in module_dirs:
                        other_name = Path(other_module).name
                        if other_name != module_name and f"mia.{other_name}" in content:
                            if other_name not in relationships[module_name]:
                                relationships[module_name].append(other_name)
                
                except Exception:
                    pass
        
        return relationships
    
    def _calculate_stability_indicators(self) -> Dict[str, float]:
        """Calculate system stability indicators"""
        
        indicators = {
            "module_consistency": 1.0,
            "import_stability": 1.0,
            "structure_stability": 1.0
        }
        
        # Calculate based on historical data if available
        if len(self.hash_history) > 10:
            recent_hashes = self.hash_history[-10:]
            
            # Check module hash consistency
            module_hashes = [cycle.get("module_hashes", {}) for cycle in recent_hashes]
            if module_hashes:
                consistency_scores = []
                
                for module_dir in ["mia/security", "mia/production", "mia/testing"]:
                    module_hash_values = [mh.get(module_dir, "") for mh in module_hashes]
                    unique_hashes = set(module_hash_values)
                    
                    if len(unique_hashes) <= 1:
                        consistency_scores.append(1.0)
                    else:
                        consistency_scores.append(0.8)  # Some variation detected
                
                if consistency_scores:
                    indicators["module_consistency"] = sum(consistency_scores) / len(consistency_scores)
        
        return indicators
    
    def _hash_data(self, data: Any) -> str:
        """Hash arbitrary data structure"""
        
        hasher = hashlib.sha256()
        
        # Convert data to JSON string for consistent hashing
        try:
            json_str = json.dumps(data, sort_keys=True, default=str)
            hasher.update(json_str.encode('utf-8'))
        except Exception as e:
            # Fallback to string representation
            hasher.update(str(data).encode('utf-8'))
        
        return hasher.hexdigest()
    
    def _detect_major_inconsistency(self) -> bool:
        """Detect major inconsistency in recent cycles"""
        
        if len(self.hash_history) < 10:
            return False
        
        # Check last 10 cycles for major variations
        recent_cycles = self.hash_history[-10:]
        
        # Check module hash consistency
        for module_dir in ["mia/security", "mia/production", "mia/testing"]:
            module_hashes = [
                cycle.get("module_hashes", {}).get(module_dir, "")
                for cycle in recent_cycles
            ]
            
            unique_hashes = set(module_hashes)
            if len(unique_hashes) > 3:  # Too many variations
                return True
        
        return False
    
    def _analyze_hash_consistency(self) -> Dict[str, Any]:
        """Analyze hash consistency across all cycles"""
        
        consistency_analysis = {
            "total_cycles_analyzed": len(self.hash_history),
            "module_consistency": {},
            "overall_consistency": 0.0,
            "consistency_grade": "unknown",
            "inconsistent_cycles": []
        }
        
        if not self.hash_history:
            return consistency_analysis
        
        # Analyze each module's hash consistency
        module_dirs = ["mia/security", "mia/production", "mia/testing", "mia/compliance", "mia/enterprise"]
        
        for module_dir in module_dirs:
            module_hashes = [
                cycle.get("module_hashes", {}).get(module_dir, "")
                for cycle in self.hash_history
            ]
            
            unique_hashes = set(module_hashes)
            consistency_percentage = (1 - (len(unique_hashes) - 1) / len(module_hashes)) * 100
            
            consistency_analysis["module_consistency"][module_dir] = {
                "unique_hashes": len(unique_hashes),
                "consistency_percentage": consistency_percentage,
                "most_common_hash": max(set(module_hashes), key=module_hashes.count) if module_hashes else ""
            }
        
        # Calculate overall consistency
        module_consistencies = [
            data["consistency_percentage"]
            for data in consistency_analysis["module_consistency"].values()
        ]
        
        if module_consistencies:
            consistency_analysis["overall_consistency"] = sum(module_consistencies) / len(module_consistencies)
        
        # Determine grade
        overall = consistency_analysis["overall_consistency"]
        if overall >= 99.5:
            consistency_analysis["consistency_grade"] = "A+ (Excellent)"
        elif overall >= 99.0:
            consistency_analysis["consistency_grade"] = "A (Very Good)"
        elif overall >= 98.0:
            consistency_analysis["consistency_grade"] = "B (Good)"
        elif overall >= 95.0:
            consistency_analysis["consistency_grade"] = "C (Acceptable)"
        else:
            consistency_analysis["consistency_grade"] = "D (Poor)"
        
        return consistency_analysis
    
    def _analyze_module_stability(self) -> Dict[str, Any]:
        """Analyze module stability across cycles"""
        
        stability_analysis = {
            "stable_modules": [],
            "unstable_modules": [],
            "stability_metrics": {},
            "overall_stability": 0.0
        }
        
        if not self.hash_history:
            return stability_analysis
        
        module_dirs = ["mia/security", "mia/production", "mia/testing", "mia/compliance", "mia/enterprise"]
        
        for module_dir in module_dirs:
            # Analyze stability indicators for each module
            stability_score = self._calculate_module_stability_score(module_dir)
            
            stability_analysis["stability_metrics"][module_dir] = stability_score
            
            if stability_score >= 95.0:
                stability_analysis["stable_modules"].append(module_dir)
            else:
                stability_analysis["unstable_modules"].append(module_dir)
        
        # Calculate overall stability
        if stability_analysis["stability_metrics"]:
            stability_scores = list(stability_analysis["stability_metrics"].values())
            stability_analysis["overall_stability"] = sum(stability_scores) / len(stability_scores)
        
        return stability_analysis
    
    def _calculate_module_stability_score(self, module_dir: str) -> float:
        """Calculate stability score for a specific module"""
        
        if not self.hash_history:
            return 0.0
        
        # Get module hashes across all cycles
        module_hashes = [
            cycle.get("module_hashes", {}).get(module_dir, "")
            for cycle in self.hash_history
        ]
        
        if not module_hashes:
            return 0.0
        
        # Calculate stability based on hash consistency
        unique_hashes = set(module_hashes)
        
        if len(unique_hashes) == 1:
            return 100.0  # Perfect stability
        elif len(unique_hashes) <= 2:
            return 95.0   # Very stable
        elif len(unique_hashes) <= 3:
            return 85.0   # Mostly stable
        else:
            return 60.0   # Unstable
    
    def _analyze_performance_metrics(self, total_time: float) -> Dict[str, Any]:
        """Analyze performance metrics"""
        
        performance_metrics = {
            "total_execution_time": total_time,
            "average_cycle_time": 0.0,
            "cycles_per_second": 0.0,
            "performance_grade": "unknown",
            "execution_consistency": 0.0
        }
        
        if self.hash_history:
            # Calculate average cycle time
            cycle_times = [cycle.get("execution_time", 0) for cycle in self.hash_history]
            valid_times = [t for t in cycle_times if t > 0]
            
            if valid_times:
                performance_metrics["average_cycle_time"] = sum(valid_times) / len(valid_times)
                performance_metrics["cycles_per_second"] = len(self.hash_history) / total_time
                
                # Calculate execution consistency
                import statistics
                if len(valid_times) > 1:
                    mean_time = statistics.mean(valid_times)
                    std_dev = statistics.stdev(valid_times)
                    cv = (std_dev / mean_time) * 100 if mean_time > 0 else 100
                    performance_metrics["execution_consistency"] = max(0, 100 - cv)
        
        # Determine performance grade
        cps = performance_metrics["cycles_per_second"]
        if cps >= 1000:
            performance_metrics["performance_grade"] = "A+ (Excellent)"
        elif cps >= 500:
            performance_metrics["performance_grade"] = "A (Very Good)"
        elif cps >= 100:
            performance_metrics["performance_grade"] = "B (Good)"
        elif cps >= 50:
            performance_metrics["performance_grade"] = "C (Acceptable)"
        else:
            performance_metrics["performance_grade"] = "D (Poor)"
        
        return performance_metrics
    
    def _analyze_deterministic_behavior(self) -> Dict[str, Any]:
        """Analyze deterministic behavior of the system"""
        
        deterministic_analysis = {
            "deterministic_score": 0.0,
            "deterministic_grade": "unknown",
            "non_deterministic_elements": [],
            "deterministic_modules": [],
            "recommendations": []
        }
        
        if not self.hash_history:
            return deterministic_analysis
        
        # Analyze deterministic behavior based on hash consistency
        module_dirs = ["mia/security", "mia/production", "mia/testing", "mia/compliance", "mia/enterprise"]
        deterministic_scores = []
        
        for module_dir in module_dirs:
            module_hashes = [
                cycle.get("module_hashes", {}).get(module_dir, "")
                for cycle in self.hash_history
            ]
            
            unique_hashes = set(module_hashes)
            
            if len(unique_hashes) == 1:
                deterministic_scores.append(100.0)
                deterministic_analysis["deterministic_modules"].append(module_dir)
            else:
                score = max(0, 100 - (len(unique_hashes) - 1) * 10)
                deterministic_scores.append(score)
                deterministic_analysis["non_deterministic_elements"].append({
                    "module": module_dir,
                    "unique_hashes": len(unique_hashes),
                    "score": score
                })
        
        # Calculate overall deterministic score
        if deterministic_scores:
            deterministic_analysis["deterministic_score"] = sum(deterministic_scores) / len(deterministic_scores)
        
        # Determine grade
        score = deterministic_analysis["deterministic_score"]
        if score >= 99.5:
            deterministic_analysis["deterministic_grade"] = "A+ (Fully Deterministic)"
        elif score >= 98.0:
            deterministic_analysis["deterministic_grade"] = "A (Highly Deterministic)"
        elif score >= 95.0:
            deterministic_analysis["deterministic_grade"] = "B (Mostly Deterministic)"
        elif score >= 90.0:
            deterministic_analysis["deterministic_grade"] = "C (Partially Deterministic)"
        else:
            deterministic_analysis["deterministic_grade"] = "D (Non-Deterministic)"
        
        # Generate recommendations
        if deterministic_analysis["non_deterministic_elements"]:
            deterministic_analysis["recommendations"].append(
                "Remove non-deterministic elements from modules with hash variations"
            )
        
        if score < 95.0:
            deterministic_analysis["recommendations"].append(
                "Implement deterministic content normalization for consistent hashing"
            )
        
        return deterministic_analysis
    
    def _generate_validation_recommendations(self) -> List[str]:
        """Generate validation recommendations"""
        
        recommendations = []
        
        # Based on hash consistency
        if self.hash_history:
            consistency_data = self._analyze_hash_consistency()
            overall_consistency = consistency_data.get("overall_consistency", 0)
            
            if overall_consistency < 95.0:
                recommendations.append(
                    f"Improve hash consistency (currently {overall_consistency:.1f}%) by removing non-deterministic elements"
                )
            
            if overall_consistency >= 99.0:
                recommendations.append(
                    "Excellent hash consistency achieved - maintain current practices"
                )
        
        # Performance recommendations
        recommendations.append("Continue regular introspective validation cycles")
        recommendations.append("Monitor hash consistency in production environment")
        recommendations.append("Implement automated hash validation in CI/CD pipeline")
        
        return recommendations

def main():
    """Main function to run introspective hash validation"""
    
    print("🔍 MIA Enterprise AGI - Introspective Hash Validation")
    print("=" * 55)
    
    validator = IntrospectiveHashValidator()
    
    print("🔄 Running 5000-cycle introspective hash validation...")
    validation_result = validator.run_introspective_validation()
    
    # Save results to log file
    output_file = "introspective_hash_validation.log"
    with open(output_file, 'w') as f:
        json.dump(validation_result, f, indent=2)
    
    print(f"📄 Validation results saved to: {output_file}")
    
    # Print summary
    print("\n📊 INTROSPECTIVE HASH VALIDATION SUMMARY:")
    
    consistency = validation_result.get("hash_consistency", {})
    print(f"Overall Consistency: {consistency.get('overall_consistency', 0):.2f}%")
    print(f"Consistency Grade: {consistency.get('consistency_grade', 'unknown')}")
    
    stability = validation_result.get("module_stability", {})
    print(f"Overall Stability: {stability.get('overall_stability', 0):.2f}%")
    print(f"Stable Modules: {len(stability.get('stable_modules', []))}")
    print(f"Unstable Modules: {len(stability.get('unstable_modules', []))}")
    
    performance = validation_result.get("performance_metrics", {})
    print(f"Cycles per Second: {performance.get('cycles_per_second', 0):.1f}")
    print(f"Performance Grade: {performance.get('performance_grade', 'unknown')}")
    
    deterministic = validation_result.get("deterministic_analysis", {})
    print(f"Deterministic Score: {deterministic.get('deterministic_score', 0):.2f}%")
    print(f"Deterministic Grade: {deterministic.get('deterministic_grade', 'unknown')}")
    
    print("\n📋 RECOMMENDATIONS:")
    for i, recommendation in enumerate(validation_result.get("recommendations", []), 1):
        print(f"  {i}. {recommendation}")
    
    print(f"\n✅ Introspective hash validation completed!")
    return validation_result

if __name__ == "__main__":
    main()