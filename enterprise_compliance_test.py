#!/usr/bin/env python3
"""
MIA Enterprise AGI - Enterprise Compliance Test
==============================================

Test script to verify enterprise compliance improvements.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mia.enterprise import ComplianceManager


def main():
    """Main enterprise compliance test"""
    print("🏢 MIA Enterprise AGI - Enterprise Compliance Test")
    print("=" * 60)
    
    # Initialize compliance manager
    compliance_manager = ComplianceManager(".")
    
    # Evaluate compliance
    print("📋 Evaluating enterprise compliance...")
    compliance_results = compliance_manager.evaluate_enterprise_compliance()
    
    # Display results
    print("\n📊 COMPLIANCE RESULTS:")
    print(f"Overall Score: {compliance_results['overall_score']:.1%}")
    print(f"Compliance Level: {compliance_results['compliance_level']}")
    
    print("\n📋 STANDARDS COMPLIANCE:")
    for standard, result in compliance_results["standards"].items():
        status_icon = "✅" if result["status"] == "COMPLIANT" else "❌"
        required_text = "(Required)" if result["required"] else "(Optional)"
        print(f"{status_icon} {standard}: {result['score']:.1%} {required_text}")
    
    # Generate compliance report
    print("\n📄 Generating compliance report...")
    compliance_report = compliance_manager.generate_compliance_report()
    
    print("\n💡 RECOMMENDATIONS:")
    for recommendation in compliance_report["recommendations"]:
        print(f"• {recommendation}")
    
    print("\n📝 ACTION ITEMS:")
    for action_item in compliance_report["action_items"]:
        print(f"• {action_item}")
    
    # Final assessment
    is_compliant = compliance_results["overall_score"] >= 0.80
    
    print("\n🎯 FINAL ASSESSMENT:")
    if is_compliant:
        print("✅ ENTERPRISE COMPLIANCE ACHIEVED")
        print("✅ READY FOR ENTERPRISE DEPLOYMENT")
    else:
        print("⚠️ ENTERPRISE COMPLIANCE NEEDS IMPROVEMENT")
        print("⚠️ ADDITIONAL COMPLIANCE WORK REQUIRED")
    
    return {
        "compliance_results": compliance_results,
        "compliance_report": compliance_report,
        "is_compliant": is_compliant
    }


if __name__ == "__main__":
    main()