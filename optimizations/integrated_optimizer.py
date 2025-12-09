#!/usr/bin/env python3
"""
🚀 MIA Enterprise AGI - Integrated Optimizer
===========================================

Integrates all optimizations into MIA system for 100% audit score
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from performance_optimizer import UltimatePerformanceOptimizer
from advanced_caching import UltimateCacheSystem
import logging
import time

class IntegratedOptimizer:
    """Integrated optimization system"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # Initialize optimizers
        self.performance_optimizer = UltimatePerformanceOptimizer()
        self.cache_system = UltimateCacheSystem()
        
        self.optimization_active = False
        self.logger.info("🚀 Integrated Optimizer initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("MIA.IntegratedOptimizer")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def activate_all_optimizations(self):
        """Activate all optimizations"""
        try:
            self.logger.info("🚀 Activating all optimizations...")
            
            # Activate performance optimization
            self.performance_optimizer.activate_ultimate_optimization()
            
            # Start cache warming
            self.cache_system.start_cache_warming()
            
            self.optimization_active = True
            self.logger.info("✅ All optimizations activated")
            
        except Exception as e:
            self.logger.error(f"Failed to activate optimizations: {e}")
    
    def get_optimization_status(self):
        """Get optimization status"""
        try:
            perf_metrics = self.performance_optimizer.get_performance_metrics()
            cache_stats = self.cache_system.get_comprehensive_stats()
            
            return {
                "optimization_active": self.optimization_active,
                "performance": perf_metrics,
                "cache": cache_stats
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get optimization status: {e}")
            return {}
    
    def deactivate_optimizations(self):
        """Deactivate all optimizations"""
        try:
            self.performance_optimizer.deactivate_optimization()
            self.cache_system.stop_cache_warming()
            self.optimization_active = False
            self.logger.info("🔄 All optimizations deactivated")
            
        except Exception as e:
            self.logger.error(f"Failed to deactivate optimizations: {e}")

# Global optimizer instance
integrated_optimizer = IntegratedOptimizer()

def main():
    """Main execution function"""
    print("🚀 Starting Integrated Optimization System...")
    
    # Activate optimizations
    integrated_optimizer.activate_all_optimizations()
    
    # Run for test period
    print("⏱️ Running optimizations for 15 seconds...")
    time.sleep(15)
    
    # Get status
    status = integrated_optimizer.get_optimization_status()
    
    print("\n" + "="*60)
    print("📊 INTEGRATED OPTIMIZATION STATUS")
    print("="*60)
    
    if status:
        print(f"Optimization Active: {status['optimization_active']}")
        
        if status.get('performance'):
            perf = status['performance']
            print(f"Performance Score: {perf.get('overall_score', 0):.3f}")
            print(f"Memory Usage: {perf.get('memory_percent', 0):.1f}%")
        
        if status.get('cache'):
            cache = status['cache']['overall']
            print(f"Cache Hit Rate: {cache.get('overall_hit_rate', 0):.2%}")
            print(f"Cache Response Time: {cache.get('avg_response_time', 0):.4f}s")
    
    print("="*60)
    print("✅ Integrated optimization system ready!")
    
    return integrated_optimizer

if __name__ == "__main__":
    main()