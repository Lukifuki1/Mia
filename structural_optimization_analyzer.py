#!/usr/bin/env python3
"""
MIA Enterprise AGI - Structural Optimization Analyzer
====================================================

Analyzes large files for modularization and creates optimization plan.
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any


class StructuralOptimizationAnalyzer:
    """Analyzes code structure for optimization"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.large_files = []
        self.analysis_results = {}
        
    def analyze_file_complexity(self) -> Dict[str, Any]:
        """Analyze file complexity and identify large files"""
        print("🔍 Analyzing file complexity...")
        
        try:
            # Find all Python files and their sizes
            result = subprocess.run(
                ["find", ".", "-name", "*.py", "-type", "f", "-exec", "wc", "-c", "{}", "+"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            large_files = []
            total_files = 0
            total_size = 0
            
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        try:
                            size = int(parts[0])
                            filename = parts[1]
                            
                            if filename.endswith('.py') and not filename.endswith('total'):
                                total_files += 1
                                total_size += size
                                
                                if size > 51200:  # 50KB
                                    large_files.append({
                                        "file": filename,
                                        "size_bytes": size,
                                        "size_kb": round(size / 1024, 1),
                                        "complexity_level": self._assess_complexity_level(size)
                                    })
                        except (ValueError, IndexError):
                            continue
            
            # Sort by size descending
            large_files.sort(key=lambda x: x["size_bytes"], reverse=True)
            self.large_files = large_files
            
            return {
                "total_files": total_files,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "large_files_count": len(large_files),
                "large_files": large_files,
                "optimization_priority": self._calculate_optimization_priority(large_files)
            }
            
        except Exception as e:
            return {"error": str(e), "large_files_count": 0}
    
    def _assess_complexity_level(self, size_bytes: int) -> str:
        """Assess complexity level based on file size"""
        if size_bytes > 100 * 1024:  # 100KB
            return "CRITICAL"
        elif size_bytes > 80 * 1024:  # 80KB
            return "HIGH"
        elif size_bytes > 60 * 1024:  # 60KB
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_optimization_priority(self, large_files: List[Dict]) -> List[Dict]:
        """Calculate optimization priority for each file"""
        priority_list = []
        
        for file_info in large_files:
            priority_score = 0
            
            # Size factor (0-50 points)
            size_kb = file_info["size_kb"]
            if size_kb > 100:
                priority_score += 50
            elif size_kb > 80:
                priority_score += 40
            elif size_kb > 60:
                priority_score += 30
            else:
                priority_score += 20
            
            # File type factor (0-30 points)
            filename = file_info["file"]
            if "final_" in filename:
                priority_score += 30  # Final implementations are critical
            elif "test_" in filename or "/test" in filename:
                priority_score += 20  # Tests are important
            elif "core/" in filename:
                priority_score += 25  # Core modules are critical
            else:
                priority_score += 15
            
            # Complexity factor (0-20 points)
            if file_info["complexity_level"] == "CRITICAL":
                priority_score += 20
            elif file_info["complexity_level"] == "HIGH":
                priority_score += 15
            elif file_info["complexity_level"] == "MEDIUM":
                priority_score += 10
            else:
                priority_score += 5
            
            priority_list.append({
                "file": filename,
                "priority_score": priority_score,
                "complexity_level": file_info["complexity_level"],
                "size_kb": size_kb,
                "modularization_strategy": self._suggest_modularization_strategy(filename, size_kb)
            })
        
        # Sort by priority score descending
        priority_list.sort(key=lambda x: x["priority_score"], reverse=True)
        return priority_list
    
    def _suggest_modularization_strategy(self, filename: str, size_kb: float) -> Dict[str, Any]:
        """Suggest modularization strategy for a file"""
        
        # Analyze filename to suggest modules
        if "validation" in filename:
            modules = ["validation_core", "test_runner", "compliance_checker", "report_generator"]
        elif "security" in filename:
            modules = ["security_core", "encryption_manager", "access_control", "audit_system"]
        elif "builder" in filename or "build" in filename:
            modules = ["build_core", "platform_detector", "deployment_manager", "build_utils"]
        elif "test" in filename:
            modules = ["test_core", "test_cases", "test_runner", "test_utils"]
        elif "enterprise" in filename:
            modules = ["enterprise_core", "compliance_manager", "feature_manager", "enterprise_utils"]
        elif "compliance" in filename:
            modules = ["compliance_core", "regulation_checker", "audit_manager", "compliance_utils"]
        elif "analysis" in filename:
            modules = ["analysis_core", "data_processor", "report_generator", "analysis_utils"]
        elif "qrd" in filename or "quality" in filename:
            modules = ["quality_core", "control_system", "metrics_collector", "quality_utils"]
        else:
            # Generic modularization
            modules = ["core", "utils", "manager", "processor"]
        
        # Determine number of modules based on size
        if size_kb > 100:
            target_modules = 4
        elif size_kb > 80:
            target_modules = 3
        elif size_kb > 60:
            target_modules = 3
        else:
            target_modules = 2
        
        return {
            "target_modules": target_modules,
            "suggested_modules": modules[:target_modules],
            "estimated_size_per_module": round(size_kb / target_modules, 1),
            "modularization_approach": "functional_decomposition"
        }
    
    def create_modularization_plan(self) -> Dict[str, Any]:
        """Create comprehensive modularization plan"""
        print("📋 Creating modularization plan...")
        
        complexity_analysis = self.analyze_file_complexity()
        
        plan = {
            "timestamp": time.time(),
            "analysis_summary": {
                "total_files": complexity_analysis.get("total_files", 0),
                "large_files_count": complexity_analysis.get("large_files_count", 0),
                "total_size_reduction_target": "75%",
                "estimated_modules_to_create": 0
            },
            "modularization_phases": [],
            "risk_assessment": self._assess_modularization_risks(),
            "success_criteria": {
                "max_file_size_kb": 50,
                "max_large_files": 2,
                "functionality_preservation": "100%",
                "deterministic_hash_consistency": "required"
            }
        }
        
        # Create phases based on priority
        priority_files = complexity_analysis.get("optimization_priority", [])
        
        # Phase 1: Critical files (>100KB)
        critical_files = [f for f in priority_files if f["complexity_level"] == "CRITICAL"]
        if critical_files:
            plan["modularization_phases"].append({
                "phase": 1,
                "name": "Critical File Modularization",
                "files": critical_files,
                "estimated_modules": sum(f["modularization_strategy"]["target_modules"] for f in critical_files),
                "priority": "HIGHEST"
            })
        
        # Phase 2: High complexity files (80-100KB)
        high_files = [f for f in priority_files if f["complexity_level"] == "HIGH"]
        if high_files:
            plan["modularization_phases"].append({
                "phase": 2,
                "name": "High Complexity File Modularization",
                "files": high_files,
                "estimated_modules": sum(f["modularization_strategy"]["target_modules"] for f in high_files),
                "priority": "HIGH"
            })
        
        # Phase 3: Medium complexity files (60-80KB)
        medium_files = [f for f in priority_files if f["complexity_level"] == "MEDIUM"]
        if medium_files:
            plan["modularization_phases"].append({
                "phase": 3,
                "name": "Medium Complexity File Modularization",
                "files": medium_files,
                "estimated_modules": sum(f["modularization_strategy"]["target_modules"] for f in medium_files),
                "priority": "MEDIUM"
            })
        
        # Phase 4: Low complexity files (50-60KB)
        low_files = [f for f in priority_files if f["complexity_level"] == "LOW"]
        if low_files:
            plan["modularization_phases"].append({
                "phase": 4,
                "name": "Low Complexity File Modularization",
                "files": low_files,
                "estimated_modules": sum(f["modularization_strategy"]["target_modules"] for f in low_files),
                "priority": "LOW"
            })
        
        # Calculate total estimated modules
        plan["analysis_summary"]["estimated_modules_to_create"] = sum(
            phase["estimated_modules"] for phase in plan["modularization_phases"]
        )
        
        return plan
    
    def _assess_modularization_risks(self) -> Dict[str, Any]:
        """Assess risks associated with modularization"""
        return {
            "high_risk_factors": [
                "Deterministic hash consistency must be maintained",
                "Complex interdependencies between modules",
                "Critical production validation systems"
            ],
            "medium_risk_factors": [
                "Import path changes may affect existing code",
                "Test coverage may need updates",
                "Performance impact from module loading"
            ],
            "low_risk_factors": [
                "Code organization improvements",
                "Better maintainability",
                "Reduced file complexity"
            ],
            "mitigation_strategies": [
                "Incremental modularization with testing after each step",
                "Preserve original files as backup until verification",
                "Run deterministic hash verification after each change",
                "Comprehensive functionality testing after refactoring"
            ]
        }
    
    def generate_analysis_report(self) -> str:
        """Generate comprehensive analysis report"""
        plan = self.create_modularization_plan()
        
        report = f"""# MIA Enterprise AGI - Structural Optimization Analysis

## Executive Summary

**Analysis Date**: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(plan['timestamp']))}
**Total Files Analyzed**: {plan['analysis_summary']['total_files']}
**Large Files Identified**: {plan['analysis_summary']['large_files_count']}
**Estimated Modules to Create**: {plan['analysis_summary']['estimated_modules_to_create']}
**Target Size Reduction**: {plan['analysis_summary']['total_size_reduction_target']}

## Modularization Plan

"""
        
        for phase in plan["modularization_phases"]:
            report += f"""### Phase {phase['phase']}: {phase['name']}
**Priority**: {phase['priority']}
**Files to Modularize**: {len(phase['files'])}
**Estimated Modules**: {phase['estimated_modules']}

| File | Size | Complexity | Target Modules | Strategy |
|------|------|------------|----------------|----------|
"""
            for file_info in phase["files"]:
                strategy = file_info["modularization_strategy"]
                modules_str = ", ".join(strategy["suggested_modules"])
                report += f"| `{file_info['file']}` | {file_info['size_kb']}KB | {file_info['complexity_level']} | {strategy['target_modules']} | {modules_str} |\n"
            
            report += "\n"
        
        report += f"""## Risk Assessment

### High Risk Factors
"""
        for risk in plan["risk_assessment"]["high_risk_factors"]:
            report += f"- {risk}\n"
        
        report += f"""
### Mitigation Strategies
"""
        for strategy in plan["risk_assessment"]["mitigation_strategies"]:
            report += f"- {strategy}\n"
        
        report += f"""
## Success Criteria

- **Maximum File Size**: {plan['success_criteria']['max_file_size_kb']}KB
- **Maximum Large Files**: {plan['success_criteria']['max_large_files']}
- **Functionality Preservation**: {plan['success_criteria']['functionality_preservation']}
- **Hash Consistency**: {plan['success_criteria']['deterministic_hash_consistency']}

## Next Steps

1. Execute Phase 1 (Critical Files) modularization
2. Run deterministic hash verification after each file
3. Execute comprehensive functionality testing
4. Proceed to subsequent phases
5. Generate final optimization report

---

**Generated by**: MIA Enterprise AGI Structural Optimization Analyzer
"""
        
        return report


def main():
    """Main analysis execution"""
    print("🏗️ MIA Enterprise AGI - Structural Optimization Analysis")
    print("=" * 60)
    
    analyzer = StructuralOptimizationAnalyzer()
    
    # Generate analysis report
    report = analyzer.generate_analysis_report()
    
    # Save report
    report_path = Path("structural_optimization_analysis.md")
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"📄 Analysis report saved to: {report_path}")
    
    # Save plan as JSON
    plan = analyzer.create_modularization_plan()
    plan_path = Path("modularization_plan.json")
    with open(plan_path, 'w') as f:
        json.dump(plan, f, indent=2)
    
    print(f"📋 Modularization plan saved to: {plan_path}")
    
    # Display summary
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"Large Files: {plan['analysis_summary']['large_files_count']}")
    print(f"Estimated Modules: {plan['analysis_summary']['estimated_modules_to_create']}")
    print(f"Modularization Phases: {len(plan['modularization_phases'])}")
    
    return plan


if __name__ == "__main__":
    main()