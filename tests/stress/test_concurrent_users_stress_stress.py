#!/usr/bin/env python3
"""
Stress test: concurrent_users_stress
Test with many concurrent users
"""

import unittest
import sys
import time
import threading
import psutil
import gc
from pathlib import Path
from unittest.mock import Mock
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestConcurrentUsersStressStress(unittest.TestCase):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Stress test for concurrent_users_stress"""
    
    def setUp(self):
        """Set up stress test"""
        self.stress_start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        self.initial_memory = psutil.virtual_memory().percent
        self.initial_cpu = psutil.cpu_percent()
        
        # Stress test parameters
        self.stress_duration = 30  # seconds
        self.concurrent_threads = 10
        self.operations_per_thread = 100
        
        print(f"Starting stress test: concurrent_users_stress")
        print(f"Initial memory usage: {self.initial_memory:.1f}%")
        print(f"Initial CPU usage: {self.initial_cpu:.1f}%")
    
    def tearDown(self):
        """Clean up stress test"""
        # Force garbage collection
        gc.collect()
        
        final_memory = psutil.virtual_memory().percent
        final_cpu = psutil.cpu_percent()
        stress_duration = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - self.stress_start_time
        
        print(f"Stress test completed in {stress_duration:.2f}s")
        print(f"Final memory usage: {final_memory:.1f}%")
        print(f"Final CPU usage: {final_cpu:.1f}%")
        
        # Check for memory leaks
        memory_increase = final_memory - self.initial_memory
        if memory_increase > 10:  # More than 10% increase
            print(f"WARNING: Possible memory leak detected (+{memory_increase:.1f}%)")
    
    def test_high_load_performance(self):
        """Test performance under high load"""
        results = []
        
        def stress_operation(thread_id):
            """Single stress operation"""
            thread_results = []
            
            for i in range(self.operations_per_thread):
                start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                
                # Simulate intensive operation
                result = self._simulate_intensive_operation(thread_id, i)
                
                operation_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
                thread_results.append({
                    "thread_id": thread_id,
                    "operation_id": i,
                    "duration": operation_time,
                    "result": result
                })
                
                # Small delay to prevent overwhelming
                time.sleep(0.001)
            
            return thread_results
        
        # Execute stress test with multiple threads
        with ThreadPoolExecutor(max_workers=self.concurrent_threads) as executor:
            futures = [
                executor.submit(stress_operation, thread_id)
                for thread_id in range(self.concurrent_threads)
            ]
            
            for future in as_completed(futures):
                try:
                    thread_results = future.result(timeout=60)
                    results.extend(thread_results)
                except Exception as e:
                    print(f"Thread execution error: {e}")
        
        # Analyze results
        total_operations = len(results)
        successful_operations = len([r for r in results if r["result"] is not None])
        avg_duration = sum(r["duration"] for r in results) / len(results) if results else 0
        
        print(f"Total operations: {total_operations}")
        print(f"Successful operations: {successful_operations}")
        print(f"Success rate: {successful_operations/total_operations*100:.1f}%")
        print(f"Average operation duration: {avg_duration:.4f}s")
        
        # Assertions
        self.assertGreater(total_operations, 0)
        self.assertGreaterEqual(successful_operations / total_operations, 0.95)  # 95% success rate
        self.assertLess(avg_duration, 1.0)  # Average operation under 1 second
    
    def test_memory_pressure_handling(self):
        """Test handling of memory pressure"""
        memory_allocations = []
        
        try:
            # Gradually increase memory usage
            for i in range(100):
                # Allocate memory (1MB chunks)
                data = bytearray(1024 * 1024)  # 1MB
                memory_allocations.append(data)
                
                current_memory = psutil.virtual_memory().percent
                
                # Stop if memory usage gets too high
                if current_memory > 80:
                    print(f"Stopping memory allocation at {current_memory:.1f}% usage")
                    break
                
                # Check system responsiveness
                start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                self._simulate_system_operation()
                response_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
                
                # System should remain responsive
                self.assertLess(response_time, 2.0, 
                               f"System unresponsive under memory pressure: {response_time:.2f}s")
                
                time.sleep(0.1)
        
        finally:
            # Clean up memory allocations
            memory_allocations.clear()
            gc.collect()
    
    def test_concurrent_access_safety(self):
        """Test thread safety under concurrent access"""
        shared_resource = {"counter": 0, "data": []}
        lock = threading.Lock()
        errors = []
        
        def concurrent_access(thread_id):
            """Concurrent access operation"""
            try:
                for i in range(50):
                    with lock:
                        # Simulate shared resource access
                        current_value = shared_resource["counter"]
                        time.sleep(0.001)  # Simulate processing
                        shared_resource["counter"] = current_value + 1
                        shared_resource["data"].append(f"thread_{thread_id}_op_{i}")
                    
                    # Simulate some work outside lock
                    self._simulate_work()
                    
            except Exception as e:
                errors.append(f"Thread {thread_id} error: {e}")
        
        # Start concurrent threads
        threads = []
        for thread_id in range(self.concurrent_threads):
            thread = threading.Thread(target=concurrent_access, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)
        
        # Verify results
        expected_counter = self.concurrent_threads * 50
        actual_counter = shared_resource["counter"]
        
        print(f"Expected counter: {expected_counter}")
        print(f"Actual counter: {actual_counter}")
        print(f"Data entries: {len(shared_resource['data'])}")
        print(f"Errors: {len(errors)}")
        
        # Assertions
        self.assertEqual(actual_counter, expected_counter, "Counter mismatch indicates race condition")
        self.assertEqual(len(shared_resource["data"]), expected_counter, "Data count mismatch")
        self.assertEqual(len(errors), 0, f"Concurrent access errors: {errors}")
    
    def _simulate_intensive_operation(self, thread_id, operation_id):
        """Simulate intensive operation"""
        try:
            # CPU intensive task
            result = sum(i * i for i in range(1000))
            
            # Memory allocation
            temp_data = [i for i in range(100)]
            
            # Simulate processing
            processed_result = {
                "thread_id": thread_id,
                "operation_id": operation_id,
                "result": result,
                "data_size": len(temp_data)
            }
            
            return processed_result
            
        except Exception as e:
            return None
    
    def _simulate_system_operation(self):
        """Simulate basic system operation"""
        # Simple operation to test system responsiveness
        data = {"test": "data", "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}
        processed = json.dumps(data)
        return len(processed)
    
    def _simulate_work(self):
        """Simulate some work"""
        time.sleep(0.001)
        return sum(i for i in range(10))
    
    def test_resource_cleanup(self):
        """Test proper resource cleanup under stress"""
        initial_handles = len(psutil.Process().open_files())
        
        # Perform operations that create resources
        for i in range(100):
            try:
                # Simulate resource creation and cleanup
                with open(f"/tmp/stress_test_{i}.tmp", "w") as f:
                    f.write(f"test data {i}")
                
                # Immediately clean up
                os.unlink(f"/tmp/stress_test_{i}.tmp")
                
            except Exception as e:
                print(f"Resource operation error: {e}")
        
        # Check for resource leaks
        final_handles = len(psutil.Process().open_files())
        handle_increase = final_handles - initial_handles
        
        print(f"Initial file handles: {initial_handles}")
        print(f"Final file handles: {final_handles}")
        
        # Should not have significant handle leaks
        self.assertLess(handle_increase, 10, "Possible file handle leak detected")

if __name__ == '__main__':
    unittest.main()
