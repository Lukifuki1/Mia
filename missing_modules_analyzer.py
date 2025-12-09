#!/usr/bin/env python3
"""
🔍 MIA Enterprise AGI - Missing Modules Analyzer
===============================================

Analizira manjkajoče metode in funkcionalnosti v modulariziranih modulih.
"""

import os
import sys
import json
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime

class MissingModulesAnalyzer:
    """Analyzer for missing methods and functionalities in modularized modules"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.analysis_results = {}
        self.reference_methods = {}
        self.current_methods = {}
        
    def analyze_missing_modules(self) -> Dict[str, Any]:
        """Analyze missing methods in all modularized modules"""
        
        analysis_result = {
            "analysis_timestamp": datetime.now().isoformat(),
            "analyzer": "MissingModulesAnalyzer",
            "modules_analyzed": {},
            "missing_methods_summary": {},
            "recommendations": [],
            "overall_completeness": 0.0
        }
        
        # Define module mappings (original -> modularized)
        module_mappings = {
            "final_production_validation.py": "mia/production/",
            "final_security_implementation.py": "mia/security/",
            "final_testing_implementation.py": "mia/testing/",
            "lgpd_compliance_implementation.py": "mia/compliance/",
            "desktop/enterprise_features.py": "mia/enterprise/",
            "desktop/cross_platform_builder.py": "mia/desktop/",
            "automated_platform_verification.py": "mia/verification/",
            "introspective_analysis.py": "mia/analysis/",
            "mia/modules/project_builder/main.py": "mia/project_builder/"
        }
        
        # Analyze each module mapping
        for original_file, modular_dir in module_mappings.items():
            module_analysis = self._analyze_module_mapping(original_file, modular_dir)
            analysis_result["modules_analyzed"][original_file] = module_analysis
        
        # Generate summary
        analysis_result["missing_methods_summary"] = self._generate_missing_methods_summary(
            analysis_result["modules_analyzed"]
        )
        
        # Calculate overall completeness
        analysis_result["overall_completeness"] = self._calculate_overall_completeness(
            analysis_result["modules_analyzed"]
        )
        
        # Generate recommendations
        analysis_result["recommendations"] = self._generate_recommendations(
            analysis_result["missing_methods_summary"]
        )
        
        return analysis_result
    
    def _analyze_module_mapping(self, original_file: str, modular_dir: str) -> Dict[str, Any]:
        """Analyze mapping between original file and modularized directory"""
        
        module_analysis = {
            "original_file": original_file,
            "modular_directory": modular_dir,
            "original_methods": [],
            "modular_methods": [],
            "missing_methods": [],
            "extra_methods": [],
            "completeness_percentage": 0.0,
            "status": "unknown"
        }
        
        # Get methods from original file
        original_methods = self._extract_methods_from_file(original_file)
        module_analysis["original_methods"] = original_methods
        
        # Get methods from modular directory
        modular_methods = self._extract_methods_from_directory(modular_dir)
        module_analysis["modular_methods"] = modular_methods
        
        # Find missing and extra methods
        original_set = set(original_methods)
        modular_set = set(modular_methods)
        
        module_analysis["missing_methods"] = list(original_set - modular_set)
        module_analysis["extra_methods"] = list(modular_set - original_set)
        
        # Calculate completeness
        if original_methods:
            found_methods = len(original_set & modular_set)
            module_analysis["completeness_percentage"] = (found_methods / len(original_methods)) * 100
        
        # Determine status
        if module_analysis["completeness_percentage"] >= 95:
            module_analysis["status"] = "complete"
        elif module_analysis["completeness_percentage"] >= 80:
            module_analysis["status"] = "mostly_complete"
        elif module_analysis["completeness_percentage"] >= 60:
            module_analysis["status"] = "partially_complete"
        else:
            module_analysis["status"] = "incomplete"
        
        return module_analysis
    
    def _extract_methods_from_file(self, file_path: str) -> List[str]:
        """Extract method names from a Python file"""
        methods = []
        
        try:
            file_full_path = self.project_root / file_path
            if not file_full_path.exists():
                return methods
            
            content = file_full_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    methods.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append(f"{node.name}.{item.name}")
        
        except Exception as e:
            print(f"Error extracting methods from {file_path}: {e}")
        
        return methods
    
    def _extract_methods_from_directory(self, dir_path: str) -> List[str]:
        """Extract method names from all Python files in a directory"""
        methods = []
        
        try:
            dir_full_path = self.project_root / dir_path
            if not dir_full_path.exists():
                return methods
            
            for py_file in dir_full_path.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue
                
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        methods.append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                methods.append(f"{node.name}.{item.name}")
        
        except Exception as e:
            print(f"Error extracting methods from {dir_path}: {e}")
        
        return methods
    
    def _generate_missing_methods_summary(self, modules_analyzed: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of missing methods across all modules"""
        
        summary = {
            "total_modules": len(modules_analyzed),
            "complete_modules": 0,
            "incomplete_modules": 0,
            "total_missing_methods": 0,
            "critical_missing_methods": [],
            "modules_by_status": {
                "complete": [],
                "mostly_complete": [],
                "partially_complete": [],
                "incomplete": []
            }
        }
        
        for original_file, analysis in modules_analyzed.items():
            status = analysis.get("status", "unknown")
            summary["modules_by_status"][status].append(original_file)
            
            if status == "complete":
                summary["complete_modules"] += 1
            else:
                summary["incomplete_modules"] += 1
            
            missing_methods = analysis.get("missing_methods", [])
            summary["total_missing_methods"] += len(missing_methods)
            
            # Identify critical missing methods
            for method in missing_methods:
                if any(keyword in method.lower() for keyword in [
                    "validate", "authenticate", "encrypt", "audit", "compliance",
                    "security", "test", "deploy", "generate", "process"
                ]):
                    summary["critical_missing_methods"].append({
                        "method": method,
                        "module": original_file,
                        "modular_dir": analysis.get("modular_directory", "")
                    })
        
        return summary
    
    def _calculate_overall_completeness(self, modules_analyzed: Dict[str, Any]) -> float:
        """Calculate overall completeness percentage"""
        
        if not modules_analyzed:
            return 0.0
        
        total_completeness = sum(
            analysis.get("completeness_percentage", 0)
            for analysis in modules_analyzed.values()
        )
        
        return total_completeness / len(modules_analyzed)
    
    def _generate_recommendations(self, missing_summary: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on missing methods analysis"""
        
        recommendations = []
        
        # Overall recommendations
        if missing_summary["total_missing_methods"] > 0:
            recommendations.append(
                f"Implement {missing_summary['total_missing_methods']} missing methods "
                f"across {missing_summary['incomplete_modules']} modules"
            )
        
        # Critical methods recommendations
        critical_methods = missing_summary.get("critical_missing_methods", [])
        if critical_methods:
            recommendations.append(
                f"Priority: Implement {len(critical_methods)} critical missing methods "
                f"for security, validation, and compliance"
            )
        
        # Module-specific recommendations
        incomplete_modules = missing_summary["modules_by_status"].get("incomplete", [])
        if incomplete_modules:
            recommendations.append(
                f"Focus on completing {len(incomplete_modules)} incomplete modules: "
                f"{', '.join(incomplete_modules[:3])}{'...' if len(incomplete_modules) > 3 else ''}"
            )
        
        # Testing recommendations
        recommendations.append(
            "Add comprehensive unit tests for all implemented methods"
        )
        
        # Documentation recommendations
        recommendations.append(
            "Update module documentation to reflect current implementation status"
        )
        
        return recommendations

def main():
    """Main function to run missing modules analysis"""
    
    print("🔍 MIA Enterprise AGI - Missing Modules Analysis")
    print("=" * 55)
    
    analyzer = MissingModulesAnalyzer()
    
    print("🔍 Analyzing missing methods in modularized modules...")
    analysis_result = analyzer.analyze_missing_modules()
    
    # Save results to JSON file
    output_file = "missing_modules_report.json"
    with open(output_file, 'w') as f:
        json.dump(analysis_result, f, indent=2)
    
    print(f"📄 Analysis results saved to: {output_file}")
    
    # Print summary
    print("\n📊 MISSING MODULES ANALYSIS SUMMARY:")
    print(f"Overall Completeness: {analysis_result['overall_completeness']:.1f}%")
    
    summary = analysis_result["missing_methods_summary"]
    print(f"Total Modules Analyzed: {summary['total_modules']}")
    print(f"Complete Modules: {summary['complete_modules']}")
    print(f"Incomplete Modules: {summary['incomplete_modules']}")
    print(f"Total Missing Methods: {summary['total_missing_methods']}")
    print(f"Critical Missing Methods: {len(summary['critical_missing_methods'])}")
    
    print("\n📋 RECOMMENDATIONS:")
    for i, recommendation in enumerate(analysis_result["recommendations"], 1):
        print(f"  {i}. {recommendation}")
    
    print(f"\n✅ Missing modules analysis completed!")
    return analysis_result

if __name__ == "__main__":
    main()