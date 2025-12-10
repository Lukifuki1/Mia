"""
Fixed concurrent processing module for MIA
"""

import asyncio
import concurrent.futures
import threading
import multiprocessing
from typing import Any, Callable, List, Optional

class FixedConcurrentProcessor:
    """Fixed concurrent processing implementation"""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or min(4, multiprocessing.cpu_count())
        
    def cpu_intensive_task(self, x: int) -> int:
        """CPU intensive task - proper function definition"""
        return sum(i * i for i in range(x * 1000))
        
    async def process_parallel_tasks(self, tasks: List[int]) -> List[int]:
        """Process tasks in parallel"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.cpu_intensive_task, task) for task in tasks]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        return results
        
    async def process_async_tasks(self, tasks: List[int]) -> List[int]:
        """Process tasks asynchronously"""
        async def async_task(x: int) -> int:
            await asyncio.sleep(0.01)  # Simulate async work
            return self.cpu_intensive_task(x)
            
        results = await asyncio.gather(*[async_task(task) for task in tasks])
        return results
        
    def test_concurrent_processing(self) -> bool:
        """Test concurrent processing functionality"""
        try:
            # Test thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(self.cpu_intensive_task, i) for i in range(3)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
                
            return len(results) == 3
        except Exception as e:
            print(f"Concurrent processing test failed: {e}")
            return False

# Global instance
concurrent_processor = FixedConcurrentProcessor()
