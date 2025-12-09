#!/usr/bin/env python3
"""
🔍 MIA Enterprise AGI - Končna Produkcijska Validacija
=====================================================

Modularized production validation system using dedicated modules.
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import modularized components
from mia.production import (
    ProductionValidationCore,
    ProductionTestRunner,
    ProductionComplianceChecker,
    ProductionReportGenerator
)


class ProductionValidator:
    """Modularized production validator"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = self._setup_logging()
        
        # Initialize modular components
        self.validation_core = ProductionValidationCore(project_root)
        self.test_runner = ProductionTestRunner(project_root)
        self.compliance_checker = ProductionComplianceChecker(project_root)
        self.report_generator = ProductionReportGenerator(project_root)
        
        # Results storage
        self.validation_results = {}
        self.test_results = {}
        self.compliance_results = {}
        
        self.logger.info("🔍 Modularized Production Validator inicializiran")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("MIA.ProductionValidator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def run_complete_validation(self) -> Dict[str, Any]:
        """Run complete production validation using modular components"""
        try:
            start_time = time.time()
            self.logger.info("🚀 Starting modularized production validation...")
            
            # 1. Core system validation
            self.logger.info("1️⃣ Running core system validation...")
            self.validation_results = self.validation_core.run_comprehensive_validation()
            
            # 2. Test execution
            self.logger.info("2️⃣ Running production tests...")
            self.test_results = self.test_runner.run_all_tests()
            
            # 3. Compliance validation
            self.logger.info("3️⃣ Running compliance validation...")
            self.compliance_results = self.compliance_checker.run_comprehensive_compliance_check()
            
            # 4. Generate comprehensive reports
            self.logger.info("4️⃣ Generating comprehensive reports...")
            report_files = self.report_generator.generate_comprehensive_report(
                self.validation_results,
                self.test_results,
                self.compliance_results
            )
            
            # Calculate overall results
            execution_time = time.time() - start_time
            final_report = self._generate_final_validation_report(execution_time, report_files)
            
            self.logger.info("✅ Modularized production validation completed")
            return final_report
            
        except Exception as e:
            self.logger.error(f"Production validation error: {e}")
            return {"status": "FAILED", "error": str(e)}
    
    def _generate_final_validation_report(self, execution_time: float, report_files: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final validation report"""
        try:
            # Calculate overall scores
            validation_score = self.validation_results.get('overall_score', 0.0)
            test_score = self.test_results.get('overall_score', 0.0)
            compliance_score = self.compliance_results.get('overall_compliance_score', 0.0)
            
            overall_score = (validation_score + test_score + compliance_score) / 3
            
            # Determine production readiness
            production_ready = (
                self.validation_results.get('production_ready', False) and
                self.test_results.get('all_tests_passed', False) and
                compliance_score >= 0.8
            )
            
            return {
                "status": "COMPLETED",
                "overall_score": overall_score,
                "production_ready": production_ready,
                "execution_time": execution_time,
                "component_scores": {
                    "validation": validation_score,
                    "testing": test_score,
                    "compliance": compliance_score
                },
                "detailed_results": {
                    "validation": self.validation_results,
                    "testing": self.test_results,
                    "compliance": self.compliance_results
                },
                "report_files": report_files,
                "grade": "A" if overall_score >= 0.9 else "B" if overall_score >= 0.8 else "C",
                "recommendation": "APPROVED FOR PRODUCTION" if production_ready else "REQUIRES ADDITIONAL WORK",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate final report: {e}")
            return {
                "status": "ERROR",
                "error": str(e),
                "partial_results": {
                    "validation": self.validation_results,
                    "testing": self.test_results,
                    "compliance": self.compliance_results
                }
            }


def main():
    """Main execution function"""
    print("🔍 MIA Enterprise AGI - Final Production Validation")
    print("=" * 60)
    
    validator = ProductionValidator()
    result = validator.run_complete_validation()
    
    # Display results
    print(f"\n📊 VALIDATION RESULTS:")
    print(f"Status: {result.get('status', 'Unknown')}")
    print(f"Overall Score: {result.get('overall_score', 0.0):.1%}")
    print(f"Production Ready: {'✅ YES' if result.get('production_ready', False) else '❌ NO'}")
    print(f"Grade: {result.get('grade', 'N/A')}")
    print(f"Recommendation: {result.get('recommendation', 'Unknown')}")
    
    if 'report_files' in result:
        print(f"\n📄 Generated Reports:")
        for report_type, report_path in result['report_files'].items():
            print(f"  - {report_type}: {report_path}")
    
    return result


if __name__ == "__main__":
    main()
