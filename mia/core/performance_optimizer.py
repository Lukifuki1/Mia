"""
Performance optimization module for MIA
"""

import os
import sys
import psutil
import gc
from typing import Dict, Any

class PerformanceOptimizer:
    """Performance optimization utilities"""
    
    def __init__(self):
        self.cpu_count = psutil.cpu_count()
        self.memory_gb = psutil.virtual_memory().total // (1024**3)
        
    def get_optimal_settings(self) -> Dict[str, Any]:
        """Get optimal settings based on hardware"""
        settings = {
            'max_workers': min(self.cpu_count, 8),
            'batch_size': 32 if self.memory_gb >= 16 else (16 if self.memory_gb >= 8 else 8),
            'cache_size_mb': min(1024, self.memory_gb * 64),
            'enable_gpu': self._check_gpu_available(),
            'memory_limit_gb': max(2, self.memory_gb // 2)
        }
        return settings
        
    def _check_gpu_available(self) -> bool:
        """Check if GPU is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
            
    def optimize_memory(self):
        """Optimize memory usage"""
        gc.collect()
        
    def optimize_startup(self):
        """Optimize startup performance"""
        # Set environment variables for better performance
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        os.environ['OMP_NUM_THREADS'] = str(min(4, self.cpu_count))
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        process = psutil.Process()
        return {
            'cpu_percent': process.cpu_percent(),
            'memory_mb': process.memory_info().rss // (1024 * 1024),
            'memory_percent': process.memory_percent(),
            'num_threads': process.num_threads()
        }

# Global optimizer instance
performance_optimizer = PerformanceOptimizer()
