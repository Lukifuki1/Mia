#!/usr/bin/env python3
"""
✅ MIA Enterprise AGI - Final Production Validator
=================================================

Preveri determinističnost, izoliranost modulov brez side-effectov z dokumentacijo.
"""

import os
import sys
import json
import ast
import inspect
import importlib
from pathlib import Path
from typing import Dict, List, Any, Set, Optional
from datetime import datetime
import logging

class FinalProductionValidator:
    """Final production validator for deterministic, isolated modules"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.validation_results = {}
        self.logger = self._setup_logging()
        
        # Validation criteria
        self.deterministic_criteria = [
            "no_random_values",
            "no_timestamps",
            "no_system_dependent_calls",
            "consistent_output"
        ]
        
        self.isolation_criteria = [
            "no_global_state_modification",
            "no_file_system_writes",
            "no_network_calls",
            "no_external_dependencies"
        ]
        
        self.side_effect_criteria = [
            "pure_functions",
            "immutable_data_structures",
            "no_shared_mutable_state",
            "predictable_behavior"
        ]
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.FinalProductionValidator")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def validate_production_readiness(self) -> Dict[str, Any]:
        """Validate production readiness of all modules"""
        
        validation_result = {
            "validation_timestamp": datetime.now().isoformat(),
            "validator": "FinalProductionValidator",
            "module_validations": {},
            "overall_scores": {},
            "production_readiness": {},
            "documentation_coverage": {},
            "recommendations": []
        }
        
        self.logger.info("✅ Starting final production validation...")
        
        # Define modules to validate
        modules_to_validate = [
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
        
        # Validate each module
        for module_path in modules_to_validate:
            module_name = Path(module_path).name
            self.logger.info(f"🔍 Validating module: {module_name}")
            
            module_validation = self._validate_module(module_path)
            validation_result["module_validations"][module_name] = module_validation
        
        # Calculate overall scores
        validation_result["overall_scores"] = self._calculate_overall_scores(
            validation_result["module_validations"]
        )
        
        # Assess production readiness
        validation_result["production_readiness"] = self._assess_production_readiness(
            validation_result["module_validations"]
        )
        
        # Analyze documentation coverage
        validation_result["documentation_coverage"] = self._analyze_documentation_coverage(
            validation_result["module_validations"]
        )
        
        # Generate recommendations
        validation_result["recommendations"] = self._generate_production_recommendations(
            validation_result
        )
        
        self.logger.info("✅ Final production validation completed")
        
        return validation_result
    
    def _validate_module(self, module_path: str) -> Dict[str, Any]:
        """Validate a specific module"""
        
        module_validation = {
            "module_path": module_path,
            "deterministic_score": 0.0,
            "isolation_score": 0.0,
            "side_effect_score": 0.0,
            "documentation_score": 0.0,
            "overall_score": 0.0,
            "production_ready": False,
            "issues": [],
            "strengths": [],
            "files_analyzed": []
        }
        
        module_dir = self.project_root / module_path
        if not module_dir.exists():
            module_validation["issues"].append(f"Module directory {module_path} does not exist")
            return module_validation
        
        # Get all Python files in module
        py_files = list(module_dir.glob("*.py"))
        py_files = [f for f in py_files if not f.name.startswith("__")]
        
        if not py_files:
            module_validation["issues"].append("No Python files found in module")
            return module_validation
        
        # Analyze each file
        file_scores = {
            "deterministic": [],
            "isolation": [],
            "side_effect": [],
            "documentation": []
        }
        
        for py_file in py_files:
            file_analysis = self._analyze_file(py_file)
            module_validation["files_analyzed"].append({
                "file": py_file.name,
                "analysis": file_analysis
            })
            
            file_scores["deterministic"].append(file_analysis["deterministic_score"])
            file_scores["isolation"].append(file_analysis["isolation_score"])
            file_scores["side_effect"].append(file_analysis["side_effect_score"])
            file_scores["documentation"].append(file_analysis["documentation_score"])
            
            # Collect issues and strengths
            module_validation["issues"].extend(file_analysis["issues"])
            module_validation["strengths"].extend(file_analysis["strengths"])
        
        # Calculate module scores
        if file_scores["deterministic"]:
            module_validation["deterministic_score"] = sum(file_scores["deterministic"]) / len(file_scores["deterministic"])
        if file_scores["isolation"]:
            module_validation["isolation_score"] = sum(file_scores["isolation"]) / len(file_scores["isolation"])
        if file_scores["side_effect"]:
            module_validation["side_effect_score"] = sum(file_scores["side_effect"]) / len(file_scores["side_effect"])
        if file_scores["documentation"]:
            module_validation["documentation_score"] = sum(file_scores["documentation"]) / len(file_scores["documentation"])
        
        # Calculate overall score
        scores = [
            module_validation["deterministic_score"],
            module_validation["isolation_score"],
            module_validation["side_effect_score"],
            module_validation["documentation_score"]
        ]
        module_validation["overall_score"] = sum(scores) / len(scores)
        
        # Determine production readiness
        module_validation["production_ready"] = (
            module_validation["overall_score"] >= 80.0 and
            module_validation["deterministic_score"] >= 85.0 and
            module_validation["isolation_score"] >= 80.0
        )
        
        return module_validation
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a specific Python file"""
        
        file_analysis = {
            "file_path": str(file_path),
            "deterministic_score": 0.0,
            "isolation_score": 0.0,
            "side_effect_score": 0.0,
            "documentation_score": 0.0,
            "issues": [],
            "strengths": [],
            "metrics": {}
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Parse AST for analysis
            tree = ast.parse(content)
            
            # Analyze deterministic behavior
            file_analysis["deterministic_score"] = self._analyze_deterministic_behavior(content, tree)
            
            # Analyze isolation
            file_analysis["isolation_score"] = self._analyze_isolation(content, tree)
            
            # Analyze side effects
            file_analysis["side_effect_score"] = self._analyze_side_effects(content, tree)
            
            # Analyze documentation
            file_analysis["documentation_score"] = self._analyze_documentation(content, tree)
            
            # Collect metrics
            file_analysis["metrics"] = self._collect_file_metrics(content, tree)
            
        except Exception as e:
            file_analysis["issues"].append(f"Error analyzing file: {e}")
            self.logger.warning(f"Error analyzing {file_path}: {e}")
        
        return file_analysis
    
    def _analyze_deterministic_behavior(self, content: str, tree: ast.AST) -> float:
        """Analyze deterministic behavior of code"""
        
        score = 100.0
        issues = []
        
        # Check for non-deterministic patterns
        non_deterministic_patterns = [
            ('random', 'Random number generation'),
            ('time.time()', 'Current timestamp'),
            ('datetime.now()', 'Current datetime'),
            ('uuid', 'UUID generation'),
            ('os.getpid()', 'Process ID'),
            ('threading.current_thread()', 'Thread information')
        ]
        
        for pattern, description in non_deterministic_patterns:
            if pattern in content:
                score -= 15.0
                issues.append(f"Non-deterministic pattern: {description}")
        
        # Check for system-dependent calls
        system_calls = ['os.environ', 'sys.platform', 'platform.']
        for call in system_calls:
            if call in content:
                score -= 10.0
                issues.append(f"System-dependent call: {call}")
        
        # Check for file system operations
        fs_operations = ['open(', 'file(', 'Path(', '.read(', '.write(']
        fs_count = sum(1 for op in fs_operations if op in content)
        if fs_count > 0:
            score -= min(20.0, fs_count * 5.0)
            issues.append(f"File system operations: {fs_count}")
        
        return max(0.0, score)
    
    def _analyze_isolation(self, content: str, tree: ast.AST) -> float:
        """Analyze module isolation"""
        
        score = 100.0
        issues = []
        
        # Check for global variable modifications
        global_patterns = ['global ', 'globals()', 'setattr(']
        for pattern in global_patterns:
            if pattern in content:
                score -= 20.0
                issues.append(f"Global state modification: {pattern}")
        
        # Check for external network calls
        network_patterns = ['requests.', 'urllib.', 'http.', 'socket.']
        for pattern in network_patterns:
            if pattern in content:
                score -= 15.0
                issues.append(f"Network call: {pattern}")
        
        # Check for database operations
        db_patterns = ['sqlite3.', 'psycopg2.', 'pymongo.', 'sqlalchemy.']
        for pattern in db_patterns:
            if pattern in content:
                score -= 10.0
                issues.append(f"Database operation: {pattern}")
        
        # Check for subprocess calls
        subprocess_patterns = ['subprocess.', 'os.system(', 'os.popen(']
        for pattern in subprocess_patterns:
            if pattern in content:
                score -= 25.0
                issues.append(f"Subprocess call: {pattern}")
        
        return max(0.0, score)
    
    def _analyze_side_effects(self, content: str, tree: ast.AST) -> float:
        """Analyze side effects in code"""
        
        score = 100.0
        issues = []
        
        # Count function definitions
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        if functions:
            # Check for pure functions (no side effects)
            pure_function_indicators = 0
            
            for func in functions:
                func_source = ast.get_source_segment(content, func) if hasattr(ast, 'get_source_segment') else ""
                
                # Check for return statements
                returns = [node for node in ast.walk(func) if isinstance(node, ast.Return)]
                if returns:
                    pure_function_indicators += 1
                
                # Check for assignments to self or global
                assignments = [node for node in ast.walk(func) if isinstance(node, ast.Assign)]
                for assign in assignments:
                    for target in assign.targets:
                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                            score -= 5.0
                            issues.append(f"State modification in function: {func.name}")
            
            # Bonus for pure functions
            pure_ratio = pure_function_indicators / len(functions)
            score += pure_ratio * 20.0
        
        # Check for mutable default arguments
        for func in functions:
            for arg in func.args.defaults:
                if isinstance(arg, (ast.List, ast.Dict, ast.Set)):
                    score -= 10.0
                    issues.append(f"Mutable default argument in: {func.name}")
        
        return max(0.0, min(100.0, score))
    
    def _analyze_documentation(self, content: str, tree: ast.AST) -> float:
        """Analyze documentation coverage"""
        
        score = 0.0
        
        # Check for module docstring
        if ast.get_docstring(tree):
            score += 20.0
        
        # Check for class and function docstrings
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        documented_classes = sum(1 for cls in classes if ast.get_docstring(cls))
        documented_functions = sum(1 for func in functions if ast.get_docstring(func))
        
        total_items = len(classes) + len(functions)
        if total_items > 0:
            documentation_ratio = (documented_classes + documented_functions) / total_items
            score += documentation_ratio * 60.0
        
        # Check for type hints
        type_hint_count = content.count(': ') + content.count('-> ')
        if type_hint_count > 0:
            score += min(20.0, type_hint_count * 2.0)
        
        return min(100.0, score)
    
    def _collect_file_metrics(self, content: str, tree: ast.AST) -> Dict[str, Any]:
        """Collect file metrics"""
        
        metrics = {
            "lines_of_code": len(content.split('\n')),
            "classes": len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]),
            "functions": len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
            "imports": len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]),
            "complexity_score": 0.0
        }
        
        # Simple complexity calculation
        complexity_nodes = [
            ast.If, ast.For, ast.While, ast.Try, ast.With,
            ast.FunctionDef, ast.ClassDef
        ]
        
        complexity_count = sum(
            1 for node in ast.walk(tree)
            if any(isinstance(node, node_type) for node_type in complexity_nodes)
        )
        
        metrics["complexity_score"] = min(100.0, complexity_count * 2.0)
        
        return metrics
    
    def _calculate_overall_scores(self, module_validations: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall scores across all modules"""
        
        overall_scores = {
            "average_deterministic": 0.0,
            "average_isolation": 0.0,
            "average_side_effect": 0.0,
            "average_documentation": 0.0,
            "average_overall": 0.0,
            "production_ready_modules": 0,
            "total_modules": len(module_validations)
        }
        
        if not module_validations:
            return overall_scores
        
        # Calculate averages
        deterministic_scores = [m["deterministic_score"] for m in module_validations.values()]
        isolation_scores = [m["isolation_score"] for m in module_validations.values()]
        side_effect_scores = [m["side_effect_score"] for m in module_validations.values()]
        documentation_scores = [m["documentation_score"] for m in module_validations.values()]
        overall_scores_list = [m["overall_score"] for m in module_validations.values()]
        
        overall_scores["average_deterministic"] = sum(deterministic_scores) / len(deterministic_scores)
        overall_scores["average_isolation"] = sum(isolation_scores) / len(isolation_scores)
        overall_scores["average_side_effect"] = sum(side_effect_scores) / len(side_effect_scores)
        overall_scores["average_documentation"] = sum(documentation_scores) / len(documentation_scores)
        overall_scores["average_overall"] = sum(overall_scores_list) / len(overall_scores_list)
        
        # Count production ready modules
        overall_scores["production_ready_modules"] = sum(
            1 for m in module_validations.values() if m["production_ready"]
        )
        
        return overall_scores
    
    def _assess_production_readiness(self, module_validations: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall production readiness"""
        
        readiness = {
            "overall_status": "unknown",
            "readiness_percentage": 0.0,
            "ready_modules": [],
            "not_ready_modules": [],
            "critical_issues": [],
            "blocking_issues": []
        }
        
        if not module_validations:
            return readiness
        
        # Categorize modules
        for module_name, validation in module_validations.items():
            if validation["production_ready"]:
                readiness["ready_modules"].append(module_name)
            else:
                readiness["not_ready_modules"].append(module_name)
                
                # Identify critical issues
                if validation["deterministic_score"] < 70.0:
                    readiness["critical_issues"].append(f"{module_name}: Low deterministic score")
                
                if validation["isolation_score"] < 70.0:
                    readiness["critical_issues"].append(f"{module_name}: Poor isolation")
                
                if validation["overall_score"] < 60.0:
                    readiness["blocking_issues"].append(f"{module_name}: Overall score too low")
        
        # Calculate readiness percentage
        total_modules = len(module_validations)
        ready_count = len(readiness["ready_modules"])
        readiness["readiness_percentage"] = (ready_count / total_modules) * 100 if total_modules > 0 else 0
        
        # Determine overall status
        if readiness["readiness_percentage"] >= 90:
            readiness["overall_status"] = "PRODUCTION_READY"
        elif readiness["readiness_percentage"] >= 75:
            readiness["overall_status"] = "MOSTLY_READY"
        elif readiness["readiness_percentage"] >= 50:
            readiness["overall_status"] = "PARTIALLY_READY"
        else:
            readiness["overall_status"] = "NOT_READY"
        
        return readiness
    
    def _analyze_documentation_coverage(self, module_validations: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze documentation coverage across modules"""
        
        coverage = {
            "overall_coverage": 0.0,
            "well_documented_modules": [],
            "poorly_documented_modules": [],
            "documentation_grade": "unknown"
        }
        
        if not module_validations:
            return coverage
        
        # Calculate overall documentation coverage
        doc_scores = [m["documentation_score"] for m in module_validations.values()]
        coverage["overall_coverage"] = sum(doc_scores) / len(doc_scores)
        
        # Categorize modules by documentation quality
        for module_name, validation in module_validations.items():
            doc_score = validation["documentation_score"]
            
            if doc_score >= 80.0:
                coverage["well_documented_modules"].append(module_name)
            elif doc_score < 50.0:
                coverage["poorly_documented_modules"].append(module_name)
        
        # Determine documentation grade
        overall_coverage = coverage["overall_coverage"]
        if overall_coverage >= 90:
            coverage["documentation_grade"] = "A (Excellent)"
        elif overall_coverage >= 80:
            coverage["documentation_grade"] = "B (Good)"
        elif overall_coverage >= 70:
            coverage["documentation_grade"] = "C (Acceptable)"
        elif overall_coverage >= 60:
            coverage["documentation_grade"] = "D (Poor)"
        else:
            coverage["documentation_grade"] = "F (Failing)"
        
        return coverage
    
    def _generate_production_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate production readiness recommendations"""
        
        recommendations = []
        
        # Overall readiness recommendations
        readiness = validation_result.get("production_readiness", {})
        readiness_percentage = readiness.get("readiness_percentage", 0)
        
        if readiness_percentage < 75:
            recommendations.append(
                f"CRITICAL: Only {readiness_percentage:.1f}% of modules are production ready"
            )
        
        # Critical issues
        critical_issues = readiness.get("critical_issues", [])
        if critical_issues:
            recommendations.append(f"Address {len(critical_issues)} critical issues in modules")
        
        # Documentation recommendations
        doc_coverage = validation_result.get("documentation_coverage", {})
        if doc_coverage.get("overall_coverage", 0) < 80:
            recommendations.append("Improve documentation coverage across modules")
        
        # Module-specific recommendations
        not_ready_modules = readiness.get("not_ready_modules", [])
        if not_ready_modules:
            recommendations.append(
                f"Focus on improving {len(not_ready_modules)} modules: {', '.join(not_ready_modules[:3])}"
            )
        
        # Specific improvement areas
        overall_scores = validation_result.get("overall_scores", {})
        
        if overall_scores.get("average_deterministic", 0) < 85:
            recommendations.append("Improve deterministic behavior in modules")
        
        if overall_scores.get("average_isolation", 0) < 80:
            recommendations.append("Enhance module isolation and reduce dependencies")
        
        if overall_scores.get("average_side_effect", 0) < 85:
            recommendations.append("Reduce side effects and improve function purity")
        
        # General recommendations
        recommendations.extend([
            "Implement comprehensive unit tests for all modules",
            "Add type hints to improve code clarity and maintainability",
            "Consider code review process for production readiness",
            "Implement automated quality gates in CI/CD pipeline"
        ])
        
        return recommendations

def main():
    """Main function to run final production validation"""
    
    print("✅ MIA Enterprise AGI - Final Production Validation")
    print("=" * 55)
    
    validator = FinalProductionValidator()
    
    print("🔍 Validating production readiness of all modules...")
    validation_result = validator.validate_production_readiness()
    
    # Save results to JSON file
    output_file = "final_readiness_check.json"
    with open(output_file, 'w') as f:
        json.dump(validation_result, f, indent=2)
    
    print(f"📄 Validation results saved to: {output_file}")
    
    # Print summary
    print("\n📊 FINAL PRODUCTION VALIDATION SUMMARY:")
    
    overall_scores = validation_result.get("overall_scores", {})
    print(f"Average Overall Score: {overall_scores.get('average_overall', 0):.1f}%")
    print(f"Average Deterministic Score: {overall_scores.get('average_deterministic', 0):.1f}%")
    print(f"Average Isolation Score: {overall_scores.get('average_isolation', 0):.1f}%")
    print(f"Average Side Effect Score: {overall_scores.get('average_side_effect', 0):.1f}%")
    print(f"Average Documentation Score: {overall_scores.get('average_documentation', 0):.1f}%")
    
    readiness = validation_result.get("production_readiness", {})
    print(f"\nProduction Readiness: {readiness.get('readiness_percentage', 0):.1f}%")
    print(f"Overall Status: {readiness.get('overall_status', 'unknown')}")
    print(f"Ready Modules: {len(readiness.get('ready_modules', []))}/{overall_scores.get('total_modules', 0)}")
    
    doc_coverage = validation_result.get("documentation_coverage", {})
    print(f"Documentation Coverage: {doc_coverage.get('overall_coverage', 0):.1f}%")
    print(f"Documentation Grade: {doc_coverage.get('documentation_grade', 'unknown')}")
    
    print("\n📋 TOP RECOMMENDATIONS:")
    for i, recommendation in enumerate(validation_result.get("recommendations", [])[:5], 1):
        print(f"  {i}. {recommendation}")
    
    print(f"\n✅ Final production validation completed!")
    return validation_result

if __name__ == "__main__":
    main()