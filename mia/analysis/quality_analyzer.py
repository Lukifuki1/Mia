#!/usr/bin/env python3
"""
MIA Enterprise AGI - Quality Analyzer
====================================

Code quality analysis and assessment system.
"""

import os
import ast
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import json
from datetime import datetime
class QualityAnalyzer:
    """Code quality analysis system"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = self._setup_logging()
        
        # Quality metrics
        self.quality_issues = []
        self.quality_metrics = {}
        
        self.logger.info("✅ Quality Analyzer initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.Analysis.QualityAnalyzer")
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
    
    def analyze_code_quality(self) -> Dict[str, Any]:
        """Analyze code quality across the project"""
        try:
            self.logger.info("✅ Analyzing code quality...")
            
            quality_analysis = {
                "timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "code_style_analysis": self._analyze_code_style(),
                "documentation_analysis": self._analyze_documentation(),
                "maintainability_analysis": self._analyze_maintainability(),
                "reliability_analysis": self._analyze_reliability(),
                "performance_analysis": self._analyze_performance_patterns(),
                "security_analysis": self._analyze_security_patterns(),
                "quality_score": 0.0,
                "quality_grade": "F",
                "improvement_suggestions": []
            }
            
            # Calculate overall quality score
            quality_analysis["quality_score"] = self._calculate_quality_score(quality_analysis)
            quality_analysis["quality_grade"] = self._calculate_quality_grade(quality_analysis["quality_score"])
            
            # Generate improvement suggestions
            quality_analysis["improvement_suggestions"] = self._generate_improvement_suggestions(quality_analysis)
            
            return quality_analysis
            
        except Exception as e:
            self.logger.error(f"Code quality analysis error: {e}")
            return {
                "error": str(e),
                "timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
    
    def _analyze_code_style(self) -> Dict[str, Any]:
        """Analyze code style and formatting"""
        try:
            style_analysis = {
                "pep8_compliance": 0.0,
                "naming_conventions": 0.0,
                "line_length_issues": 0,
                "import_organization": 0.0,
                "style_issues": []
            }
            
            python_files = list(self.project_root.rglob("*.py"))
            total_files = len(python_files)
            
            if total_files == 0:
                return style_analysis
            
            compliant_files = 0
            total_line_length_issues = 0
            proper_naming_files = 0
            proper_import_files = 0
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.splitlines()
                    
                    # Check line length
                    long_lines = [i for i, line in enumerate(lines, 1) if len(line) > 120]
                    total_line_length_issues += len(long_lines)
                    
                    if len(long_lines) == 0:
                        compliant_files += 1
                    
                    # Check naming conventions
                    if self._check_naming_conventions(content):
                        proper_naming_files += 1
                    
                    # Check import organization
                    if self._check_import_organization(lines):
                        proper_import_files += 1
                        
                except Exception as e:
                    self.logger.warning(f"Style analysis error for {py_file}: {e}")
            
            # Calculate scores
            style_analysis["pep8_compliance"] = (compliant_files / total_files) * 100
            style_analysis["naming_conventions"] = (proper_naming_files / total_files) * 100
            style_analysis["import_organization"] = (proper_import_files / total_files) * 100
            style_analysis["line_length_issues"] = total_line_length_issues
            
            return style_analysis
            
        except Exception as e:
            self.logger.error(f"Code style analysis error: {e}")
            return {}
    
    def _check_naming_conventions(self, content: str) -> bool:
        """Check if naming conventions are followed"""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Class names should be PascalCase
                    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                        return False
                elif isinstance(node, ast.FunctionDef):
                    # Function names should be snake_case
                    if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                        return False
            
            return True
            
        except SyntaxError:
            return False
        except Exception:
            return False
    
    def _check_import_organization(self, lines: List[str]) -> bool:
        """Check if imports are properly organized"""
        try:
            import_lines = []
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith(('import ', 'from ')) and not stripped.startswith('#'):
                    import_lines.append((i, stripped))
            
            if not import_lines:
                return True
            
            # Check if imports are at the top (after docstring/comments)
            first_import_line = import_lines[0][0]
            
            # Allow for module docstring and comments at the top
            non_import_before = 0
            for i in range(first_import_line):
                line = lines[i].strip()
                if line and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                    non_import_before += 1
            
            return non_import_before <= 2  # Allow some flexibility
            
        except Exception:
            return False
    
    def _analyze_documentation(self) -> Dict[str, Any]:
        """Analyze documentation quality"""
        try:
            doc_analysis = {
                "docstring_coverage": 0.0,
                "readme_quality": 0.0,
                "inline_comments": 0.0,
                "documentation_files": 0,
                "api_documentation": False
            }
            
            python_files = list(self.project_root.rglob("*.py"))
            total_functions_classes = 0
            documented_functions_classes = 0
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                            total_functions_classes += 1
                            
                            # Check for docstring
                            if (node.body and 
                                isinstance(node.body[0], ast.Expr) and
                                isinstance(node.body[0].value, ast.Constant) and
                                isinstance(node.body[0].value.value, str)):
                                documented_functions_classes += 1
                                
                except Exception as e:
                    self.logger.warning(f"Documentation analysis error for {py_file}: {e}")
            
            # Calculate docstring coverage
            if total_functions_classes > 0:
                doc_analysis["docstring_coverage"] = (documented_functions_classes / total_functions_classes) * 100
            
            # Check for README
            readme_files = ["README.md", "README.rst", "README.txt"]
            readme_exists = any((self.project_root / readme).exists() for readme in readme_files)
            doc_analysis["readme_quality"] = 100.0 if readme_exists else 0.0
            
            # Count documentation files
            doc_files = list(self.project_root.rglob("*.md")) + list(self.project_root.rglob("*.rst"))
            doc_analysis["documentation_files"] = len(doc_files)
            
            return doc_analysis
            
        except Exception as e:
            self.logger.error(f"Documentation analysis error: {e}")
            return {}
    
    def _analyze_maintainability(self) -> Dict[str, Any]:
        """Analyze code maintainability"""
        try:
            maintainability_analysis = {
                "cyclomatic_complexity": 0.0,
                "code_duplication": 0.0,
                "function_length": 0.0,
                "class_size": 0.0,
                "maintainability_index": 0.0
            }
            
            python_files = list(self.project_root.rglob("*.py"))
            total_complexity = 0
            total_functions = 0
            function_lengths = []
            class_sizes = []
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            total_functions += 1
                            complexity = self._calculate_cyclomatic_complexity(node)
                            total_complexity += complexity
                            
                            # Calculate function length
                            func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 10
                            function_lengths.append(func_lines)
                            
                        elif isinstance(node, ast.ClassDef):
                            # Calculate class size (number of methods)
                            methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                            class_sizes.append(len(methods))
                            
                except Exception as e:
                    self.logger.warning(f"Maintainability analysis error for {py_file}: {e}")
            
            # Calculate metrics
            if total_functions > 0:
                maintainability_analysis["cyclomatic_complexity"] = total_complexity / total_functions
            
            if function_lengths:
                avg_function_length = sum(function_lengths) / len(function_lengths)
                maintainability_analysis["function_length"] = avg_function_length
            
            if class_sizes:
                avg_class_size = sum(class_sizes) / len(class_sizes)
                maintainability_analysis["class_size"] = avg_class_size
            
            # Calculate maintainability index (simplified)
            complexity_score = max(0, 100 - maintainability_analysis["cyclomatic_complexity"] * 5)
            length_score = max(0, 100 - (maintainability_analysis["function_length"] - 20) * 2)
            maintainability_analysis["maintainability_index"] = (complexity_score + length_score) / 2
            
            return maintainability_analysis
            
        except Exception as e:
            self.logger.error(f"Maintainability analysis error: {e}")
            return {}
    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _analyze_reliability(self) -> Dict[str, Any]:
        """Analyze code reliability patterns"""
        try:
            reliability_analysis = {
                "error_handling_coverage": 0.0,
                "defensive_programming": 0.0,
                "input_validation": 0.0,
                "resource_management": 0.0
            }
            
            python_files = list(self.project_root.rglob("*.py"))
            total_functions = 0
            functions_with_error_handling = 0
            functions_with_validation = 0
            functions_with_resource_mgmt = 0
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            total_functions += 1
                            
                            # Check for error handling
                            if self._has_error_handling(node):
                                functions_with_error_handling += 1
                            
                            # Check for input validation
                            if self._has_input_validation(node):
                                functions_with_validation += 1
                            
                            # Check for resource management
                            if self._has_resource_management(node):
                                functions_with_resource_mgmt += 1
                                
                except Exception as e:
                    self.logger.warning(f"Reliability analysis error for {py_file}: {e}")
            
            # Calculate scores
            if total_functions > 0:
                reliability_analysis["error_handling_coverage"] = (functions_with_error_handling / total_functions) * 100
                reliability_analysis["input_validation"] = (functions_with_validation / total_functions) * 100
                reliability_analysis["resource_management"] = (functions_with_resource_mgmt / total_functions) * 100
            
            return reliability_analysis
            
        except Exception as e:
            self.logger.error(f"Reliability analysis error: {e}")
            return {}
    
    def _has_error_handling(self, node: ast.FunctionDef) -> bool:
        """Check if function has error handling"""
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                return True
        return False
    
    def _has_input_validation(self, node: ast.FunctionDef) -> bool:
        """Check if function has input validation"""
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                # Simple heuristic: look for isinstance, len, or None checks
                if hasattr(child, 'test') and isinstance(child.test, ast.Call):
                    if hasattr(child.test.func, 'id') and child.test.func.id in ['isinstance', 'len']:
                        return True
        return False
    
    def _has_resource_management(self, node: ast.FunctionDef) -> bool:
        """Check if function has proper resource management"""
        for child in ast.walk(node):
            if isinstance(child, ast.With):
                return True
        return False
    
    def _analyze_performance_patterns(self) -> Dict[str, Any]:
        """Analyze performance-related patterns"""
        try:
            performance_analysis = {
                "efficient_algorithms": 0.0,
                "memory_efficiency": 0.0,
                "io_optimization": 0.0,
                "caching_usage": 0.0
            }
            
            python_files = list(self.project_root.rglob("*.py"))
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Simple pattern matching for performance indicators
                    if 'cache' in content.lower() or 'lru_cache' in content:
                        performance_analysis["caching_usage"] += 1
                    
                    if 'with open' in content:
                        performance_analysis["io_optimization"] += 1
                    
                    if 'generator' in content or 'yield' in content:
                        performance_analysis["memory_efficiency"] += 1
                        
                except Exception as e:
                    self.logger.warning(f"Performance analysis error for {py_file}: {e}")
            
            # Normalize scores
            total_files = len(python_files) if python_files else 1
            for key in performance_analysis:
                performance_analysis[key] = (performance_analysis[key] / total_files) * 100
            
            return performance_analysis
            
        except Exception as e:
            self.logger.error(f"Performance analysis error: {e}")
            return {}
    
    def _analyze_security_patterns(self) -> Dict[str, Any]:
        """Analyze security-related patterns"""
        try:
            security_analysis = {
                "input_sanitization": 0.0,
                "secure_coding": 0.0,
                "credential_management": 0.0,
                "security_issues": []
            }
            
            python_files = list(self.project_root.rglob("*.py"))
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Check for security patterns
                    if 'sanitize' in content.lower() or 'escape' in content.lower():
                        security_analysis["input_sanitization"] += 1
                    
                    if 'os.environ' in content or 'getenv' in content:
                        security_analysis["credential_management"] += 1
                    
                    # Check for potential security issues
                    if 'eval(' in content:
                        security_analysis["security_issues"].append(f"eval() usage in {py_file}")
                    
                    if 'exec(' in content:
                        security_analysis["security_issues"].append(f"exec() usage in {py_file}")
                        
                except Exception as e:
                    self.logger.warning(f"Security analysis error for {py_file}: {e}")
            
            # Normalize scores
            total_files = len(python_files) if python_files else 1
            security_analysis["input_sanitization"] = (security_analysis["input_sanitization"] / total_files) * 100
            security_analysis["credential_management"] = (security_analysis["credential_management"] / total_files) * 100
            
            return security_analysis
            
        except Exception as e:
            self.logger.error(f"Security analysis error: {e}")
            return {}
    
    def _calculate_quality_score(self, quality_analysis: Dict[str, Any]) -> float:
        """Calculate overall quality score"""
        try:
            scores = []
            
            # Code style score
            style_analysis = quality_analysis.get("code_style_analysis", {})
            style_score = (
                style_analysis.get("pep8_compliance", 0) * 0.4 +
                style_analysis.get("naming_conventions", 0) * 0.3 +
                style_analysis.get("import_organization", 0) * 0.3
            )
            scores.append(style_score)
            
            # Documentation score
            doc_analysis = quality_analysis.get("documentation_analysis", {})
            doc_score = (
                doc_analysis.get("docstring_coverage", 0) * 0.6 +
                doc_analysis.get("readme_quality", 0) * 0.4
            )
            scores.append(doc_score)
            
            # Maintainability score
            maint_analysis = quality_analysis.get("maintainability_analysis", {})
            maint_score = maint_analysis.get("maintainability_index", 0)
            scores.append(maint_score)
            
            # Reliability score
            rel_analysis = quality_analysis.get("reliability_analysis", {})
            rel_score = (
                rel_analysis.get("error_handling_coverage", 0) * 0.4 +
                rel_analysis.get("input_validation", 0) * 0.3 +
                rel_analysis.get("resource_management", 0) * 0.3
            )
            scores.append(rel_score)
            
            # Calculate weighted average
            overall_score = sum(scores) / len(scores) if scores else 0
            
            return round(overall_score, 2)
            
        except Exception as e:
            self.logger.error(f"Quality score calculation error: {e}")
            return 0.0
    
    def _calculate_quality_grade(self, score: float) -> str:
        """Calculate quality grade based on score"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_improvement_suggestions(self, quality_analysis: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        # Style improvements
        style_analysis = quality_analysis.get("code_style_analysis", {})
        if style_analysis.get("pep8_compliance", 100) < 80:
            suggestions.append("Improve PEP 8 compliance")
        
        if style_analysis.get("line_length_issues", 0) > 0:
            suggestions.append(f"Fix {style_analysis['line_length_issues']} line length issues")
        
        # Documentation improvements
        doc_analysis = quality_analysis.get("documentation_analysis", {})
        if doc_analysis.get("docstring_coverage", 100) < 70:
            suggestions.append("Add more docstrings to functions and classes")
        
        if doc_analysis.get("readme_quality", 100) < 50:
            suggestions.append("Create or improve README documentation")
        
        # Maintainability improvements
        maint_analysis = quality_analysis.get("maintainability_analysis", {})
        if maint_analysis.get("cyclomatic_complexity", 0) > 10:
            suggestions.append("Reduce cyclomatic complexity in functions")
        
        # Reliability improvements
        rel_analysis = quality_analysis.get("reliability_analysis", {})
        if rel_analysis.get("error_handling_coverage", 100) < 60:
            suggestions.append("Add more error handling to functions")
        
        # Security improvements
        security_analysis = quality_analysis.get("security_analysis", {})
        if security_analysis.get("security_issues"):
            suggestions.append("Address identified security issues")
        
        return suggestions