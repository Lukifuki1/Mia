#!/usr/bin/env python3
"""
🔍 MIA Enterprise AGI - Popolna Introspektivna Analiza Sistema
============================================================

Modularized introspective analysis using dedicated analysis modules.
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import modularized analysis components
from mia.analysis import (
    IntrospectiveAnalyzer,
    CodeMetrics,
    ModuleAnalysis,
    SystemAnalyzer,
    QualityAnalyzer
)


class ComprehensiveIntrospectiveAnalyzer:
    """Modularized comprehensive introspective analysis system"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = self._setup_logging()
        
        # Initialize modular analysis components
        self.introspective_analyzer = IntrospectiveAnalyzer(project_root)
        
        # Analysis results storage
        self.analysis_results = {}
        
        self.logger.info("🔍 Modularized Comprehensive Introspective Analyzer initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.Analysis.ComprehensiveIntrospectiveAnalyzer")
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
    
    def run_complete_system_analysis(self) -> Dict[str, Any]:
        """Run complete system analysis using modular components"""
        try:
            self.logger.info("🔍 Starting complete system analysis...")
            
            # Run comprehensive introspective analysis
            analysis_results = self.introspective_analyzer.run_comprehensive_analysis()
            
            # Store results
            self.analysis_results = analysis_results
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(analysis_results)
            analysis_results["executive_summary"] = executive_summary
            
            # Save comprehensive report
            self._save_comprehensive_analysis_report(analysis_results)
            
            self.logger.info(f"✅ Complete system analysis completed - Score: {analysis_results.get('overall_score', 0):.1f}%")
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Complete system analysis error: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_executive_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of analysis results"""
        try:
            overall_score = analysis_results.get("overall_score", 0)
            
            executive_summary = {
                "analysis_timestamp": datetime.now().isoformat(),
                "overall_system_score": overall_score,
                "system_grade": self._calculate_system_grade(overall_score),
                "key_strengths": self._identify_key_strengths(analysis_results),
                "critical_issues": self._identify_critical_issues(analysis_results),
                "improvement_priorities": self._prioritize_improvements(analysis_results),
                "enterprise_readiness": self._assess_enterprise_readiness(analysis_results),
                "next_steps": self._recommend_next_steps(analysis_results)
            }
            
            return executive_summary
            
        except Exception as e:
            self.logger.error(f"Executive summary generation error: {e}")
            return {
                "error": str(e)
            }
    
    def _calculate_system_grade(self, score: float) -> str:
        """Calculate system grade based on overall score"""
        if score >= 95:
            return "A+ (Excellent)"
        elif score >= 90:
            return "A (Very Good)"
        elif score >= 80:
            return "B (Good)"
        elif score >= 70:
            return "C (Satisfactory)"
        elif score >= 60:
            return "D (Needs Improvement)"
        else:
            return "F (Critical Issues)"
    
    def _identify_key_strengths(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Identify key system strengths"""
        strengths = []
        
        # Check code metrics
        code_metrics = analysis_results.get("code_metrics", {})
        project_summary = code_metrics.get("project_summary", {})
        
        if project_summary.get("total_files", 0) > 100:
            strengths.append("Comprehensive codebase with extensive functionality")
        
        # Check system analysis
        system_analysis = analysis_results.get("system_analysis", {})
        if system_analysis.get("architecture_score", 0) > 80:
            strengths.append("Well-structured system architecture")
        
        # Check quality analysis
        quality_analysis = analysis_results.get("quality_analysis", {})
        if quality_analysis.get("quality_score", 0) > 80:
            strengths.append("High code quality standards")
        
        # Check integration
        integration_analysis = analysis_results.get("integration_analysis", {})
        if integration_analysis.get("loose_coupling_score", 0) > 80:
            strengths.append("Good modular design with loose coupling")
        
        if not strengths:
            strengths.append("System has potential for improvement")
        
        return strengths
    
    def _identify_critical_issues(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Identify critical system issues"""
        critical_issues = []
        
        # Check for large files
        code_metrics = analysis_results.get("code_metrics", {})
        quality_indicators = code_metrics.get("quality_indicators", {})
        
        if quality_indicators.get("large_files", 0) > 5:
            critical_issues.append(f"{quality_indicators['large_files']} files exceed 50KB size limit")
        
        # Check for circular dependencies
        integration_analysis = analysis_results.get("integration_analysis", {})
        if integration_analysis.get("circular_dependencies"):
            critical_issues.append("Circular dependencies detected between modules")
        
        # Check system architecture issues
        system_analysis = analysis_results.get("system_analysis", {})
        arch_issues = system_analysis.get("architecture_issues", [])
        if arch_issues:
            critical_issues.extend(arch_issues[:3])  # Top 3 issues
        
        return critical_issues
    
    def _prioritize_improvements(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Prioritize improvement recommendations"""
        improvements = []
        
        # Get all recommendations
        all_recommendations = analysis_results.get("recommendations", [])
        
        # Prioritize based on impact
        high_priority = [
            rec for rec in all_recommendations 
            if any(keyword in rec.lower() for keyword in ['critical', 'security', 'circular', 'large'])
        ]
        
        medium_priority = [
            rec for rec in all_recommendations 
            if any(keyword in rec.lower() for keyword in ['test', 'coverage', 'documentation'])
        ]
        
        # Combine prioritized recommendations
        improvements.extend(high_priority[:3])  # Top 3 high priority
        improvements.extend(medium_priority[:2])  # Top 2 medium priority
        
        if not improvements:
            improvements = all_recommendations[:5]  # Fallback to first 5
        
        return improvements
    
    def _assess_enterprise_readiness(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess enterprise readiness"""
        overall_score = analysis_results.get("overall_score", 0)
        
        readiness_assessment = {
            "overall_readiness_score": overall_score,
            "enterprise_grade": self._calculate_system_grade(overall_score),
            "ready_for_production": overall_score >= 85,
            "ready_for_enterprise": overall_score >= 95,
            "blocking_issues": len(self._identify_critical_issues(analysis_results)),
            "readiness_level": "High" if overall_score >= 90 else "Medium" if overall_score >= 70 else "Low"
        }
        
        return readiness_assessment
    
    def _recommend_next_steps(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Recommend next steps based on analysis"""
        next_steps = []
        
        overall_score = analysis_results.get("overall_score", 0)
        
        if overall_score < 70:
            next_steps.extend([
                "Address critical system issues immediately",
                "Implement comprehensive testing strategy",
                "Refactor large files and reduce complexity"
            ])
        elif overall_score < 90:
            next_steps.extend([
                "Improve code quality and documentation",
                "Enhance test coverage",
                "Optimize system performance"
            ])
        else:
            next_steps.extend([
                "Fine-tune system for enterprise deployment",
                "Implement advanced monitoring and alerting",
                "Prepare for production scaling"
            ])
        
        next_steps.extend([
            "Schedule regular system health checks",
            "Implement continuous improvement processes"
        ])
        
        return next_steps
    
    def _save_comprehensive_analysis_report(self, analysis_results: Dict[str, Any]):
        """Save comprehensive analysis report"""
        try:
            reports_dir = Path("comprehensive_analysis_reports")
            reports_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"comprehensive_analysis_{timestamp}.json"
            
            with open(report_file, 'w') as f:
                json.dump(analysis_results, f, indent=2)
            
            self.logger.info(f"📄 Comprehensive analysis report saved: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Analysis report saving error: {e}")


def main():
    """Main execution function"""
    print("🔍 MIA Enterprise AGI - Complete Introspective Analysis")
    print("=" * 60)
    
    analyzer = ComprehensiveIntrospectiveAnalyzer()
    result = analyzer.run_complete_system_analysis()
    
    # Display results
    if result.get("overall_score") is not None:
        print(f"\n📊 COMPREHENSIVE ANALYSIS RESULTS:")
        print(f"Overall System Score: {result.get('overall_score', 0):.1f}%")
        
        executive_summary = result.get("executive_summary", {})
        print(f"System Grade: {executive_summary.get('system_grade', 'Unknown')}")
        print(f"Enterprise Ready: {'✅ YES' if executive_summary.get('enterprise_readiness', {}).get('ready_for_enterprise', False) else '❌ NO'}")
        
        # Show key strengths
        strengths = executive_summary.get("key_strengths", [])
        if strengths:
            print(f"\n💪 KEY STRENGTHS:")
            for i, strength in enumerate(strengths[:3], 1):
                print(f"  {i}. {strength}")
        
        # Show critical issues
        critical_issues = executive_summary.get("critical_issues", [])
        if critical_issues:
            print(f"\n⚠️ CRITICAL ISSUES:")
            for i, issue in enumerate(critical_issues[:3], 1):
                print(f"  {i}. {issue}")
        
        # Show next steps
        next_steps = executive_summary.get("next_steps", [])
        if next_steps:
            print(f"\n🎯 NEXT STEPS:")
            for i, step in enumerate(next_steps[:3], 1):
                print(f"  {i}. {step}")
    else:
        print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
    
    return result


if __name__ == "__main__":
    main()
