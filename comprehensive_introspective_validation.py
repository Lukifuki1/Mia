#!/usr/bin/env python3
"""
🔍 MIA Enterprise AGI - Comprehensive Introspective Validation
=============================================================

MODULARIZED VERSION - Main functionality moved to mia.validation module
This file now serves as a lightweight entry point.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mia.validation import ComprehensiveIntrospectiveValidator


def main():
    """Main entry point for comprehensive introspective validation"""
    validator = ComprehensiveIntrospectiveValidator(".")
    results = validator.execute_comprehensive_validation()
    
    print("🔍 MIA Enterprise AGI - Comprehensive Introspective Validation")
    print("=" * 60)
    print(f"Status: {results.get('status', 'unknown')}")
    print(f"Overall Score: {results.get('overall_score', 0.0):.2%}")
    print(f"Execution Time: {results.get('execution_time', 0.0):.2f}s")
    print(f"Tests Passed: {results.get('passed_tests', 0)}/{results.get('total_tests', 0)}")
    
    if results.get('is_fully_validated', False):
        print("✅ System is fully validated and ready for production")
    else:
        print("⚠️ System requires optimization before production deployment")
    
    return results


if __name__ == "__main__":
    main()