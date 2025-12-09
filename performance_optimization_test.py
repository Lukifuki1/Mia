#!/usr/bin/env python3
"""
MIA Enterprise AGI - Performance Optimization Test
=================================================

Test script to verify memory and consciousness optimization targets.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mia.performance import MemoryOptimizer, ConsciousnessOptimizer, PerformanceBenchmarker


async def main():
    """Main performance optimization test"""
    print("🚀 MIA Enterprise AGI - Performance Optimization Test")
    print("=" * 60)
    
    # Initialize benchmarker
    benchmarker = PerformanceBenchmarker()
    
    # Run comprehensive benchmark
    print("📊 Running comprehensive performance benchmark...")
    results = await benchmarker.run_comprehensive_benchmark(duration_seconds=15)
    
    # Display results
    print("\n📈 BENCHMARK RESULTS:")
    print(f"Memory Performance: {results['memory_benchmark']['benchmark_ops_per_second']:.1f} ops/sec")
    print(f"Memory Target (≥1000): {'✅ ACHIEVED' if results['memory_benchmark']['target_achieved'] else '❌ NOT ACHIEVED'}")
    
    print(f"Consciousness Response: {results['consciousness_benchmark']['avg_response_time']:.3f}s")
    print(f"Consciousness Target (<0.1s): {'✅ ACHIEVED' if results['consciousness_benchmark']['target_achieved'] else '❌ NOT ACHIEVED'}")
    
    print(f"Overall Performance Grade: {results['overall_performance']['performance_grade']}")
    print(f"All Targets Achieved: {'✅ YES' if results['overall_performance']['all_targets_achieved'] else '❌ NO'}")
    
    # Run stress test
    print("\n💪 Running stability stress test...")
    stress_results = await benchmarker.run_stress_test(duration_seconds=10)
    
    print(f"Error Rate: {stress_results['error_rate_per_second']:.3f} errors/sec")
    print(f"Stability Target (≤0.01): {'✅ ACHIEVED' if stress_results['target_achieved'] else '❌ NOT ACHIEVED'}")
    print(f"System Stability: {stress_results['stability_status']}")
    
    # Final assessment
    all_optimized = (
        results['overall_performance']['all_targets_achieved'] and
        stress_results['target_achieved']
    )
    
    print("\n🎯 FINAL ASSESSMENT:")
    if all_optimized:
        print("✅ ALL OPTIMIZATION TARGETS ACHIEVED")
        print("✅ SYSTEM READY FOR PRODUCTION")
    else:
        print("⚠️ OPTIMIZATION TARGETS NOT FULLY ACHIEVED")
        print("⚠️ ADDITIONAL OPTIMIZATION REQUIRED")
    
    return {
        "benchmark_results": results,
        "stress_results": stress_results,
        "all_optimized": all_optimized
    }


if __name__ == "__main__":
    asyncio.run(main())