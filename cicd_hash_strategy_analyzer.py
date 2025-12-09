#!/usr/bin/env python3
"""
🔄 MIA Enterprise AGI - CI/CD Hash Strategy Analyzer
===================================================

Ugotovi run_id vključenost v hash in predlagaj refaktorirano strategijo.
"""

import os
import sys
import json
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime
import logging

class CICDHashStrategyAnalyzer:
    """Analyzer for CI/CD hash strategy and reproducibility"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.analysis_results = {}
        self.logger = self._setup_logging()
        
        # Hash strategy configuration
        self.non_deterministic_patterns = [
            r'run_id',
            r'timestamp',
            r'datetime\.now\(\)',
            r'time\.time\(\)',
            r'uuid\.',
            r'random\.',
            r'os\.getpid\(\)',
            r'threading\.current_thread\(\)',
            r'__file__',
            r'__name__'
        ]
        
        self.deterministic_alternatives = {
            'run_id': 'build_hash',
            'timestamp': 'build_version',
            'datetime.now()': 'build_timestamp',
            'time.time()': 'build_epoch',
            'uuid.': 'deterministic_id',
            'random.': 'seeded_random',
            'os.getpid()': 'process_identifier',
            'threading.current_thread()': 'thread_identifier'
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.CICDHashStrategyAnalyzer")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def analyze_hash_strategy(self) -> Dict[str, Any]:
        """Analyze current hash strategy and reproducibility"""
        
        analysis_result = {
            "analysis_timestamp": datetime.now().isoformat(),
            "analyzer": "CICDHashStrategyAnalyzer",
            "current_strategy": {},
            "reproducibility_issues": {},
            "recommended_strategy": {},
            "implementation_plan": {},
            "validation_tests": {}
        }
        
        self.logger.info("🔄 Starting CI/CD hash strategy analysis...")
        
        # Analyze current hash strategy
        analysis_result["current_strategy"] = self._analyze_current_strategy()
        
        # Identify reproducibility issues
        analysis_result["reproducibility_issues"] = self._identify_reproducibility_issues()
        
        # Generate recommended strategy
        analysis_result["recommended_strategy"] = self._generate_recommended_strategy()
        
        # Create implementation plan
        analysis_result["implementation_plan"] = self._create_implementation_plan()
        
        # Design validation tests
        analysis_result["validation_tests"] = self._design_validation_tests()
        
        self.logger.info("✅ CI/CD hash strategy analysis completed")
        
        return analysis_result
    
    def _analyze_current_strategy(self) -> Dict[str, Any]:
        """Analyze current hash strategy implementation"""
        
        current_strategy = {
            "hash_sources": [],
            "deterministic_elements": [],
            "non_deterministic_elements": [],
            "hash_algorithms": [],
            "reproducibility_score": 0.0
        }
        
        # Find all Python files that might contain hashing logic
        hash_files = []
        for pattern in ["*hash*.py", "*validation*.py", "*build*.py", "*deploy*.py"]:
            hash_files.extend(self.project_root.rglob(pattern))
        
        # Analyze each file for hash-related code
        for file_path in hash_files:
            if file_path.is_file():
                file_analysis = self._analyze_file_for_hashing(file_path)
                if file_analysis["contains_hashing"]:
                    current_strategy["hash_sources"].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "analysis": file_analysis
                    })
        
        # Analyze deterministic vs non-deterministic elements
        all_elements = []
        for source in current_strategy["hash_sources"]:
            all_elements.extend(source["analysis"]["hash_elements"])
        
        for element in all_elements:
            if self._is_deterministic_element(element):
                current_strategy["deterministic_elements"].append(element)
            else:
                current_strategy["non_deterministic_elements"].append(element)
        
        # Calculate reproducibility score
        total_elements = len(all_elements)
        deterministic_count = len(current_strategy["deterministic_elements"])
        
        if total_elements > 0:
            current_strategy["reproducibility_score"] = (deterministic_count / total_elements) * 100
        
        return current_strategy
    
    def _analyze_file_for_hashing(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a file for hashing-related code"""
        
        file_analysis = {
            "contains_hashing": False,
            "hash_algorithms": [],
            "hash_elements": [],
            "non_deterministic_patterns": [],
            "line_numbers": {}
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check for hash algorithms
            hash_algorithms = ['hashlib', 'sha256', 'md5', 'sha1', 'blake2b']
            for algorithm in hash_algorithms:
                if algorithm in content:
                    file_analysis["hash_algorithms"].append(algorithm)
                    file_analysis["contains_hashing"] = True
            
            # Check for hash-related methods
            hash_methods = ['hash', 'digest', 'hexdigest', 'update']
            for method in hash_methods:
                if f'.{method}(' in content:
                    file_analysis["contains_hashing"] = True
            
            # Find hash elements and non-deterministic patterns
            for i, line in enumerate(lines, 1):
                # Look for hash input elements
                if any(keyword in line.lower() for keyword in ['hash', 'digest', 'checksum']):
                    file_analysis["hash_elements"].append(line.strip())
                    file_analysis["line_numbers"][i] = line.strip()
                
                # Check for non-deterministic patterns
                for pattern in self.non_deterministic_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        file_analysis["non_deterministic_patterns"].append({
                            "pattern": pattern,
                            "line": i,
                            "content": line.strip()
                        })
        
        except Exception as e:
            self.logger.warning(f"Error analyzing file {file_path}: {e}")
        
        return file_analysis
    
    def _is_deterministic_element(self, element: str) -> bool:
        """Check if an element is deterministic"""
        
        element_lower = element.lower()
        
        # Check for non-deterministic patterns
        for pattern in self.non_deterministic_patterns:
            if re.search(pattern, element_lower, re.IGNORECASE):
                return False
        
        # Deterministic elements
        deterministic_keywords = [
            'version', 'config', 'content', 'source', 'module',
            'class', 'function', 'constant', 'static'
        ]
        
        return any(keyword in element_lower for keyword in deterministic_keywords)
    
    def _identify_reproducibility_issues(self) -> Dict[str, Any]:
        """Identify reproducibility issues in current implementation"""
        
        issues = {
            "critical_issues": [],
            "medium_issues": [],
            "minor_issues": [],
            "overall_risk": "unknown",
            "impact_assessment": {}
        }
        
        # Analyze current strategy for issues
        current_strategy = self._analyze_current_strategy()
        
        # Critical issues
        non_deterministic_count = len(current_strategy["non_deterministic_elements"])
        if non_deterministic_count > 0:
            issues["critical_issues"].append({
                "issue": "Non-deterministic elements in hash calculation",
                "count": non_deterministic_count,
                "elements": current_strategy["non_deterministic_elements"][:5],  # Show first 5
                "impact": "Builds will produce different hashes for identical code"
            })
        
        # Check for run_id specifically
        run_id_found = False
        for source in current_strategy.get("hash_sources", []):
            for pattern in source["analysis"]["non_deterministic_patterns"]:
                if "run_id" in pattern["pattern"].lower():
                    run_id_found = True
                    break
        
        if run_id_found:
            issues["critical_issues"].append({
                "issue": "run_id included in hash calculation",
                "impact": "Each CI/CD run produces unique hash regardless of code changes",
                "recommendation": "Replace run_id with deterministic build identifier"
            })
        
        # Medium issues
        reproducibility_score = current_strategy.get("reproducibility_score", 0)
        if reproducibility_score < 90:
            issues["medium_issues"].append({
                "issue": f"Low reproducibility score ({reproducibility_score:.1f}%)",
                "impact": "Builds may not be fully reproducible",
                "recommendation": "Increase deterministic elements in hash calculation"
            })
        
        # Minor issues
        if len(current_strategy.get("hash_algorithms", [])) > 1:
            issues["minor_issues"].append({
                "issue": "Multiple hash algorithms used",
                "impact": "Inconsistent hashing across different components",
                "recommendation": "Standardize on single hash algorithm (SHA-256)"
            })
        
        # Determine overall risk
        if len(issues["critical_issues"]) > 0:
            issues["overall_risk"] = "HIGH"
        elif len(issues["medium_issues"]) > 0:
            issues["overall_risk"] = "MEDIUM"
        elif len(issues["minor_issues"]) > 0:
            issues["overall_risk"] = "LOW"
        else:
            issues["overall_risk"] = "MINIMAL"
        
        # Impact assessment
        issues["impact_assessment"] = {
            "build_reproducibility": "COMPROMISED" if run_id_found else "PARTIAL",
            "ci_cd_reliability": "AFFECTED" if len(issues["critical_issues"]) > 0 else "STABLE",
            "deployment_consistency": "INCONSISTENT" if reproducibility_score < 80 else "CONSISTENT"
        }
        
        return issues
    
    def _generate_recommended_strategy(self) -> Dict[str, Any]:
        """Generate recommended hash strategy"""
        
        recommended_strategy = {
            "strategy_name": "Deterministic Build Hash Strategy",
            "core_principles": [
                "Use only deterministic inputs for hash calculation",
                "Exclude runtime-specific identifiers (run_id, timestamps)",
                "Include semantic version and build configuration",
                "Normalize content before hashing",
                "Use consistent hash algorithm (SHA-256)"
            ],
            "hash_inputs": {
                "included": [
                    "source_code_content",
                    "configuration_files",
                    "dependency_versions",
                    "build_configuration",
                    "semantic_version"
                ],
                "excluded": [
                    "run_id",
                    "build_timestamp",
                    "random_values",
                    "process_ids",
                    "temporary_files"
                ]
            },
            "implementation_details": {
                "hash_algorithm": "SHA-256",
                "content_normalization": True,
                "version_scheme": "semantic_versioning",
                "build_identifier": "content_based_hash"
            },
            "validation_approach": {
                "reproducibility_tests": True,
                "cross_platform_validation": True,
                "regression_testing": True
            }
        }
        
        return recommended_strategy
    
    def _create_implementation_plan(self) -> Dict[str, Any]:
        """Create implementation plan for new hash strategy"""
        
        implementation_plan = {
            "phases": [
                {
                    "phase": 1,
                    "name": "Analysis and Preparation",
                    "duration": "1-2 days",
                    "tasks": [
                        "Audit all hash-related code",
                        "Identify non-deterministic elements",
                        "Create deterministic alternatives mapping",
                        "Design new hash calculation logic"
                    ]
                },
                {
                    "phase": 2,
                    "name": "Implementation",
                    "duration": "2-3 days",
                    "tasks": [
                        "Implement deterministic hash calculator",
                        "Replace non-deterministic elements",
                        "Add content normalization",
                        "Update build scripts"
                    ]
                },
                {
                    "phase": 3,
                    "name": "Testing and Validation",
                    "duration": "1-2 days",
                    "tasks": [
                        "Run reproducibility tests",
                        "Validate cross-platform consistency",
                        "Test CI/CD pipeline integration",
                        "Performance impact assessment"
                    ]
                },
                {
                    "phase": 4,
                    "name": "Deployment and Monitoring",
                    "duration": "1 day",
                    "tasks": [
                        "Deploy to CI/CD pipeline",
                        "Monitor hash consistency",
                        "Update documentation",
                        "Train development team"
                    ]
                }
            ],
            "code_changes": {
                "new_files": [
                    "mia/build/deterministic_hasher.py",
                    "mia/build/content_normalizer.py",
                    "tests/test_hash_reproducibility.py"
                ],
                "modified_files": [
                    "All files containing hash calculations",
                    "CI/CD configuration files",
                    "Build scripts"
                ]
            },
            "risk_mitigation": [
                "Maintain backward compatibility during transition",
                "Implement gradual rollout with feature flags",
                "Create rollback procedures",
                "Monitor hash consistency metrics"
            ]
        }
        
        return implementation_plan
    
    def _design_validation_tests(self) -> Dict[str, Any]:
        """Design validation tests for new hash strategy"""
        
        validation_tests = {
            "reproducibility_tests": [
                {
                    "test_name": "identical_builds_same_hash",
                    "description": "Verify identical builds produce same hash",
                    "steps": [
                        "Build project twice with identical inputs",
                        "Compare generated hashes",
                        "Assert hashes are identical"
                    ]
                },
                {
                    "test_name": "cross_platform_consistency",
                    "description": "Verify hash consistency across platforms",
                    "steps": [
                        "Build on Linux, Windows, macOS",
                        "Compare hashes across platforms",
                        "Assert platform-independent hashes"
                    ]
                },
                {
                    "test_name": "temporal_consistency",
                    "description": "Verify hash consistency over time",
                    "steps": [
                        "Build same code at different times",
                        "Compare hashes from different builds",
                        "Assert time-independent hashes"
                    ]
                }
            ],
            "regression_tests": [
                {
                    "test_name": "code_change_detection",
                    "description": "Verify hash changes when code changes",
                    "steps": [
                        "Build project with original code",
                        "Make minor code change",
                        "Build project again",
                        "Assert hashes are different"
                    ]
                },
                {
                    "test_name": "config_change_detection",
                    "description": "Verify hash changes when config changes",
                    "steps": [
                        "Build with original configuration",
                        "Modify configuration",
                        "Build again",
                        "Assert hashes are different"
                    ]
                }
            ],
            "performance_tests": [
                {
                    "test_name": "hash_calculation_performance",
                    "description": "Measure hash calculation performance",
                    "metrics": [
                        "Hash calculation time",
                        "Memory usage during hashing",
                        "CPU utilization"
                    ]
                }
            ],
            "integration_tests": [
                {
                    "test_name": "ci_cd_pipeline_integration",
                    "description": "Test integration with CI/CD pipeline",
                    "steps": [
                        "Trigger CI/CD build",
                        "Verify hash generation",
                        "Check hash storage and retrieval",
                        "Validate deployment process"
                    ]
                }
            ]
        }
        
        return validation_tests

def main():
    """Main function to run CI/CD hash strategy analysis"""
    
    print("🔄 MIA Enterprise AGI - CI/CD Hash Strategy Analysis")
    print("=" * 55)
    
    analyzer = CICDHashStrategyAnalyzer()
    
    print("🔍 Analyzing current CI/CD hash strategy...")
    analysis_result = analyzer.analyze_hash_strategy()
    
    # Save results to markdown file
    output_file = "cicd_hash_strategy_recommendation.md"
    
    # Generate markdown content
    markdown_content = f"""# 🔄 MIA Enterprise AGI - CI/CD Hash Strategy Recommendation

## 📊 ANALYSIS SUMMARY

**Analysis Date**: {analysis_result['analysis_timestamp']}  
**Analyzer**: {analysis_result['analyzer']}

## 🔍 CURRENT STRATEGY ANALYSIS

### Hash Sources
"""
    
    current_strategy = analysis_result.get("current_strategy", {})
    for source in current_strategy.get("hash_sources", []):
        markdown_content += f"- **{source['file']}**: Contains hashing logic\n"
    
    markdown_content += f"""
### Reproducibility Metrics
- **Reproducibility Score**: {current_strategy.get('reproducibility_score', 0):.1f}%
- **Deterministic Elements**: {len(current_strategy.get('deterministic_elements', []))}
- **Non-Deterministic Elements**: {len(current_strategy.get('non_deterministic_elements', []))}

## ⚠️ REPRODUCIBILITY ISSUES

"""
    
    issues = analysis_result.get("reproducibility_issues", {})
    markdown_content += f"**Overall Risk Level**: {issues.get('overall_risk', 'unknown')}\n\n"
    
    # Critical issues
    critical_issues = issues.get("critical_issues", [])
    if critical_issues:
        markdown_content += "### 🚨 Critical Issues\n"
        for issue in critical_issues:
            markdown_content += f"- **{issue['issue']}**\n"
            markdown_content += f"  - Impact: {issue['impact']}\n"
            if 'recommendation' in issue:
                markdown_content += f"  - Recommendation: {issue['recommendation']}\n"
        markdown_content += "\n"
    
    # Medium issues
    medium_issues = issues.get("medium_issues", [])
    if medium_issues:
        markdown_content += "### ⚠️ Medium Issues\n"
        for issue in medium_issues:
            markdown_content += f"- **{issue['issue']}**\n"
            markdown_content += f"  - Impact: {issue['impact']}\n"
            markdown_content += f"  - Recommendation: {issue['recommendation']}\n"
        markdown_content += "\n"
    
    # Recommended strategy
    recommended = analysis_result.get("recommended_strategy", {})
    markdown_content += f"""## 🎯 RECOMMENDED STRATEGY

### {recommended.get('strategy_name', 'New Hash Strategy')}

#### Core Principles
"""
    
    for principle in recommended.get("core_principles", []):
        markdown_content += f"- {principle}\n"
    
    markdown_content += """
#### Hash Inputs

**Included:**
"""
    
    for input_item in recommended.get("hash_inputs", {}).get("included", []):
        markdown_content += f"- {input_item}\n"
    
    markdown_content += """
**Excluded:**
"""
    
    for excluded_item in recommended.get("hash_inputs", {}).get("excluded", []):
        markdown_content += f"- {excluded_item}\n"
    
    # Implementation plan
    implementation = analysis_result.get("implementation_plan", {})
    markdown_content += """
## 🚀 IMPLEMENTATION PLAN

"""
    
    for phase in implementation.get("phases", []):
        markdown_content += f"### Phase {phase['phase']}: {phase['name']}\n"
        markdown_content += f"**Duration**: {phase['duration']}\n\n"
        markdown_content += "**Tasks:**\n"
        for task in phase.get("tasks", []):
            markdown_content += f"- {task}\n"
        markdown_content += "\n"
    
    # Validation tests
    validation = analysis_result.get("validation_tests", {})
    markdown_content += """## 🧪 VALIDATION TESTS

### Reproducibility Tests
"""
    
    for test in validation.get("reproducibility_tests", []):
        markdown_content += f"- **{test['test_name']}**: {test['description']}\n"
    
    markdown_content += """
### Regression Tests
"""
    
    for test in validation.get("regression_tests", []):
        markdown_content += f"- **{test['test_name']}**: {test['description']}\n"
    
    markdown_content += """
## ✅ NEXT STEPS

1. **Review and approve** the recommended hash strategy
2. **Implement Phase 1** tasks (Analysis and Preparation)
3. **Create deterministic hash calculator** module
4. **Run validation tests** to ensure reproducibility
5. **Deploy to CI/CD pipeline** with monitoring

---

*Generated by MIA Enterprise AGI CI/CD Hash Strategy Analyzer*
"""
    
    # Save markdown file
    with open(output_file, 'w') as f:
        f.write(markdown_content)
    
    # Also save JSON results
    json_output_file = "cicd_hash_strategy_analysis.json"
    with open(json_output_file, 'w') as f:
        json.dump(analysis_result, f, indent=2)
    
    print(f"📄 Analysis results saved to: {output_file}")
    print(f"📄 JSON data saved to: {json_output_file}")
    
    # Print summary
    print("\n📊 CI/CD HASH STRATEGY ANALYSIS SUMMARY:")
    print(f"Reproducibility Score: {current_strategy.get('reproducibility_score', 0):.1f}%")
    print(f"Overall Risk Level: {issues.get('overall_risk', 'unknown')}")
    print(f"Critical Issues: {len(critical_issues)}")
    print(f"Medium Issues: {len(medium_issues)}")
    
    print("\n🎯 RECOMMENDED ACTIONS:")
    if critical_issues:
        print("  1. URGENT: Address critical reproducibility issues")
    if medium_issues:
        print("  2. HIGH: Improve reproducibility score")
    print("  3. MEDIUM: Implement deterministic hash strategy")
    print("  4. LOW: Run validation tests and monitor")
    
    print(f"\n✅ CI/CD hash strategy analysis completed!")
    return analysis_result

if __name__ == "__main__":
    main()