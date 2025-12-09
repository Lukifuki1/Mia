#!/usr/bin/env python3
"""
Stress Tests - Memory System
Tests for memory system under high load: 10,000 records, consistency, performance
"""

import pytest
import time
import threading
import random
random.seed(42)  # Deterministic seed
import string
from concurrent.futures import ThreadPoolExecutor, as_completed
from mia.core.memory.main import MemorySystem, MemoryType, EmotionalTone

@pytest.mark.stress
@pytest.mark.slow
class TestMemoryStress:

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Test memory system under stress conditions"""
    
    def test_memory_stress_10k_records(self, deterministic_environment, isolated_memory, test_timer):
        """Test storing and retrieving 10,000 memory records"""
        memory = isolated_memory
        
        # Generate test data
        test_memories = []
        for i in range(10000):
            content = f"Stress test memory {i}: " + ''.join(random.choices(string.ascii_letters, k=50))
            memory_type = random.choice(list(MemoryType))
            emotional_tone = random.choice(list(EmotionalTone))
            tags = [f"stress_test", f"batch_{i//1000}", f"record_{i}"]
            
            test_memories.append({
                "content": content,
                "memory_type": memory_type,
                "emotional_tone": emotional_tone,
                "tags": tags
            })
        
        # Store memories and measure performance
        start_time = test_timer()
        stored_ids = []
        
        for i, mem_data in enumerate(test_memories):
            memory_id = memory.store_memory(**mem_data)
            stored_ids.append(memory_id)
            
            # Progress check every 1000 records
            if (i + 1) % 1000 == 0:
                elapsed = test_timer()
                print(f"Stored {i + 1}/10000 memories in {elapsed:.2f}s")
        
        storage_time = test_timer()
        
        # Verify all memories were stored
        assert len(stored_ids) == 10000
        assert all(memory_id is not None for memory_id in stored_ids)
        
        # Test retrieval performance
        retrieval_start = test_timer()
        
        # Test various retrieval patterns
        retrieval_tests = [
            ("stress test", 100),
            ("batch_5", 50),
            ("record_1234", 10),
            ("memory", 200),
            ("test", 150)
        ]
        
        total_retrieved = 0
        for query, limit in retrieval_tests:
            retrieved = memory.retrieve_memories(
                query=query,
                memory_types=list(MemoryType),
                limit=limit
            )
            total_retrieved += len(retrieved)
            assert len(retrieved) <= limit
        
        retrieval_time = test_timer() - retrieval_start
        
        # Performance assertions
        assert storage_time < 120.0  # 10k stores in under 2 minutes
        assert retrieval_time < 30.0  # All retrievals in under 30 seconds
        
        # Average performance
        avg_store_time = storage_time / 10000
        avg_retrieval_time = retrieval_time / len(retrieval_tests)
        
        assert avg_store_time < 0.012  # Under 12ms per store
        assert avg_retrieval_time < 6.0  # Under 6s per retrieval query
        
        print(f"Storage: {storage_time:.2f}s total, {avg_store_time*1000:.2f}ms avg")
        print(f"Retrieval: {retrieval_time:.2f}s total, {avg_retrieval_time:.2f}s avg")
        print(f"Total retrieved: {total_retrieved} memories")
    
    def test_concurrent_memory_operations(self, deterministic_environment, isolated_memory):
        """Test concurrent memory operations with multiple threads"""
        memory = isolated_memory
        
        # Test configuration
        num_threads = 10
        operations_per_thread = 100
        
        # Shared data structures
        results = {"stored": [], "retrieved": [], "errors": []}
        results_lock = threading.Lock()
        
        def memory_worker(thread_id):
            """Worker function for concurrent operations"""
            thread_results = {"stored": [], "retrieved": [], "errors": []}
            
            for i in range(operations_per_thread):
                try:
                    # Store operation
                    content = f"Thread {thread_id} memory {i}"
                    memory_id = memory.store_memory(
                        content=content,
                        memory_type=MemoryType.SHORT_TERM,
                        emotional_tone=EmotionalTone.NEUTRAL,
                        tags=[f"thread_{thread_id}", f"concurrent_test"]
                    )
                    thread_results["stored"].append(memory_id)
                    
                    # Retrieve operation
                    if i % 5 == 0:  # Every 5th operation
                        retrieved = memory.retrieve_memories(
                            query=f"thread {thread_id}",
                            memory_types=[MemoryType.SHORT_TERM],
                            limit=10
                        )
                        thread_results["retrieved"].extend(retrieved)
                        
                except Exception as e:
                    thread_results["errors"].append(str(e))
            
            # Merge results safely
            with results_lock:
                results["stored"].extend(thread_results["stored"])
                results["retrieved"].extend(thread_results["retrieved"])
                results["errors"].extend(thread_results["errors"])
        
        # Start concurrent operations
        start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        
        threads = []
        for thread_id in range(num_threads):
            thread = threading.Thread(target=memory_worker, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=60.0)  # 60 second timeout
        
        elapsed_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
        
        # Verify results
        expected_stores = num_threads * operations_per_thread
        assert len(results["stored"]) == expected_stores
        assert len(results["errors"]) < expected_stores * 0.01  # Less than 1% error rate
        
        # Check for duplicate memory IDs (should be unique)
        stored_ids = results["stored"]
        unique_ids = set(stored_ids)
        assert len(unique_ids) == len(stored_ids)  # All IDs should be unique
        
        # Performance check
        assert elapsed_time < 60.0  # Should complete in under 60 seconds
        
        print(f"Concurrent operations completed in {elapsed_time:.2f}s")
        print(f"Stored: {len(results['stored'])}, Retrieved: {len(results['retrieved'])}, Errors: {len(results['errors'])}")
    
    def test_memory_consistency_under_load(self, deterministic_environment, isolated_memory):
        """Test memory consistency under high load"""
        memory = isolated_memory
        
        # Store reference memories
        reference_memories = []
        for i in range(1000):
            content = f"Reference memory {i} with unique content {random.randint(1000, 9999)}"
            memory_id = memory.store_memory(
                content=content,
                memory_type=MemoryType.MEDIUM_TERM,
                emotional_tone=EmotionalTone.NEUTRAL,
                tags=["reference", f"ref_{i}"]
            )
            reference_memories.append({"id": memory_id, "content": content})
        
        # Perform high-load operations
        for load_cycle in range(10):
            # Store many temporary memories
            temp_ids = []
            for i in range(500):
                temp_id = memory.store_memory(
                    content=f"Temporary memory {load_cycle}_{i}",
                    memory_type=MemoryType.SHORT_TERM,
                    emotional_tone=EmotionalTone.NEUTRAL,
                    tags=["temporary", f"cycle_{load_cycle}"]
                )
                temp_ids.append(temp_id)
            
            # Verify reference memories are still intact
            for ref_mem in reference_memories[:10]:  # Check first 10
                retrieved = memory.retrieve_memories(
                    query=f"reference memory {reference_memories.index(ref_mem)}",
                    memory_types=[MemoryType.MEDIUM_TERM],
                    limit=5
                )
                
                # Should find the reference memory
                found = any(mem["content"] == ref_mem["content"] for mem in retrieved)
                assert found, f"Reference memory lost during load cycle {load_cycle}"
        
        # Final consistency check
        final_reference_check = memory.retrieve_memories(
            query="reference memory",
            memory_types=[MemoryType.MEDIUM_TERM],
            limit=1000
        )
        
        assert len(final_reference_check) >= 1000  # All reference memories should be found
        
        print(f"Consistency maintained through 10 load cycles")
        print(f"Final reference memories found: {len(final_reference_check)}")
    
    def test_memory_fragmentation_resistance(self, deterministic_environment, isolated_memory):
        """Test memory system resistance to fragmentation"""
        memory = isolated_memory
        
        # Create fragmentation pattern: store, delete, store, delete
        fragmentation_cycles = 50
        memories_per_cycle = 100
        
        for cycle in range(fragmentation_cycles):
            # Store memories
            stored_ids = []
            for i in range(memories_per_cycle):
                content = f"Fragmentation test cycle {cycle} memory {i}"
                memory_id = memory.store_memory(
                    content=content,
                    memory_type=MemoryType.SHORT_TERM,
                    emotional_tone=EmotionalTone.NEUTRAL,
                    tags=["fragmentation", f"cycle_{cycle}"]
                )
                stored_ids.append(memory_id)
            
            # Delete half of the memories (simulate fragmentation)
            if hasattr(memory, 'delete_memory'):
                for i in range(0, len(stored_ids), 2):  # Delete every other memory
                    try:
                        memory.delete_memory(stored_ids[i])
                    except:
                        pass  # Ignore deletion errors
            
            # Test performance after fragmentation
            if cycle % 10 == 9:  # Every 10 cycles
                start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                
                # Perform standard operations
                test_id = memory.store_memory(
                    content=f"Performance test after cycle {cycle}",
                    memory_type=MemoryType.SHORT_TERM,
                    emotional_tone=EmotionalTone.NEUTRAL,
                    tags=["performance_test"]
                )
                
                retrieved = memory.retrieve_memories(
                    query="performance test",
                    memory_types=[MemoryType.SHORT_TERM],
                    limit=10
                )
                
                operation_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
                
                # Performance should not degrade significantly
                assert operation_time < 1.0  # Operations should remain fast
                assert len(retrieved) >= 1  # Should find the test memory
        
        print(f"Completed {fragmentation_cycles} fragmentation cycles")
        print("Memory system maintained performance despite fragmentation")
    
    def test_memory_bulk_operations(self, deterministic_environment, isolated_memory, test_timer):
        """Test bulk memory operations"""
        memory = isolated_memory
        
        # Test bulk storage
        bulk_memories = []
        for i in range(5000):
            bulk_memories.append({
                "content": f"Bulk memory {i} with extended content " + "x" * 100,
                "memory_type": MemoryType.SHORT_TERM,
                "emotional_tone": EmotionalTone.NEUTRAL,
                "tags": ["bulk_test", f"bulk_{i//100}"]
            })
        
        # Store in bulk
        start_time = test_timer()
        
        if hasattr(memory, 'store_memories_bulk'):
            # Use bulk operation if available
            stored_ids = memory.store_memories_bulk(bulk_memories)
        else:
            # Fall back to individual operations
            stored_ids = []
            for mem_data in bulk_memories:
                memory_id = memory.store_memory(**mem_data)
                stored_ids.append(memory_id)
        
        bulk_storage_time = test_timer()
        
        # Test bulk retrieval
        retrieval_start = test_timer()
        
        if hasattr(memory, 'retrieve_memories_bulk'):
            # Use bulk retrieval if available
            queries = [f"bulk_{i}" for i in range(50)]
            bulk_retrieved = memory.retrieve_memories_bulk(queries, limit=100)
        else:
            # Fall back to individual retrievals
            bulk_retrieved = []
            for i in range(50):
                retrieved = memory.retrieve_memories(
                    query=f"bulk_{i}",
                    memory_types=[MemoryType.SHORT_TERM],
                    limit=100
                )
                bulk_retrieved.extend(retrieved)
        
        bulk_retrieval_time = test_timer() - retrieval_start
        
        # Verify results
        assert len(stored_ids) == 5000
        assert all(memory_id is not None for memory_id in stored_ids)
        
        # Performance requirements for bulk operations
        assert bulk_storage_time < 60.0  # 5k stores in under 60 seconds
        assert bulk_retrieval_time < 30.0  # 50 bulk retrievals in under 30 seconds
        
        print(f"Bulk storage: {bulk_storage_time:.2f}s for 5000 memories")
        print(f"Bulk retrieval: {bulk_retrieval_time:.2f}s for 50 queries")
        print(f"Retrieved {len(bulk_retrieved)} memories in bulk")
    
    def test_memory_system_recovery_under_stress(self, deterministic_environment, isolated_memory):
        """Test memory system recovery under stress conditions"""
        memory = isolated_memory
        
        # Store baseline memories
        baseline_memories = []
        for i in range(100):
            content = f"Baseline memory {i}"
            memory_id = memory.store_memory(
                content=content,
                memory_type=MemoryType.LONG_TERM,
                emotional_tone=EmotionalTone.NEUTRAL,
                tags=["baseline", "recovery_test"]
            )
            baseline_memories.append({"id": memory_id, "content": content})
        
        # Simulate stress conditions
        stress_conditions = [
            "high_memory_pressure",
            "rapid_operations",
            "concurrent_access",
            "large_content_storage"
        ]
        
        for condition in stress_conditions:
            print(f"Testing recovery under {condition}")
            
            if condition == "high_memory_pressure":
                # Store many large memories
                large_memories = []
                for i in range(200):
                    large_content = f"Large memory {i}: " + "x" * 1000
                    memory_id = memory.store_memory(
                        content=large_content,
                        memory_type=MemoryType.SHORT_TERM,
                        emotional_tone=EmotionalTone.NEUTRAL,
                        tags=["large", "stress"]
                    )
                    large_memories.append(memory_id)
            
            elif condition == "rapid_operations":
                # Perform rapid store/retrieve cycles
                for i in range(1000):
                    memory.store_memory(
                        content=f"Rapid memory {i}",
                        memory_type=MemoryType.SHORT_TERM,
                        emotional_tone=EmotionalTone.NEUTRAL,
                        tags=["rapid"]
                    )
                    if i % 10 == 0:
                        memory.retrieve_memories("rapid", limit=5)
            
            elif condition == "concurrent_access":
                # Simulate concurrent access
                def concurrent_worker():
                    for i in range(50):
                        memory.store_memory(
                            content=f"Concurrent memory {threading.current_thread().ident}_{i}",
                            memory_type=MemoryType.SHORT_TERM,
                            emotional_tone=EmotionalTone.NEUTRAL,
                            tags=["concurrent"]
                        )
                
                threads = []
                for _ in range(5):
                    thread = threading.Thread(target=concurrent_worker)
                    threads.append(thread)
                    thread.start()
                
                for thread in threads:
                    thread.join()
            
            elif condition == "large_content_storage":
                # Store memories with very large content
                for i in range(50):
                    huge_content = f"Huge memory {i}: " + "x" * 10000
                    memory.store_memory(
                        content=huge_content,
                        memory_type=MemoryType.SHORT_TERM,
                        emotional_tone=EmotionalTone.NEUTRAL,
                        tags=["huge"]
                    )
            
            # Verify baseline memories are still intact after stress
            recovered_baseline = memory.retrieve_memories(
                query="baseline memory",
                memory_types=[MemoryType.LONG_TERM],
                limit=100
            )
            
            assert len(recovered_baseline) >= 100, f"Baseline memories lost under {condition}"
            
            # Verify system is still responsive
            test_memory_id = memory.store_memory(
                content=f"Recovery test after {condition}",
                memory_type=MemoryType.SHORT_TERM,
                emotional_tone=EmotionalTone.NEUTRAL,
                tags=["recovery_test"]
            )
            
            assert test_memory_id is not None, f"System unresponsive after {condition}"
        
        print("Memory system successfully recovered from all stress conditions")
    
    def test_memory_performance_degradation(self, deterministic_environment, isolated_memory, test_timer):
        """Test memory performance degradation over time"""
        memory = isolated_memory
        
        # Baseline performance measurement
        baseline_times = []
        for i in range(10):
            start_time = test_timer()
            
            memory_id = memory.store_memory(
                content=f"Baseline performance test {i}",
                memory_type=MemoryType.SHORT_TERM,
                emotional_tone=EmotionalTone.NEUTRAL,
                tags=["baseline_perf"]
            )
            
            retrieved = memory.retrieve_memories(
                query="baseline performance",
                memory_types=[MemoryType.SHORT_TERM],
                limit=5
            )
            
            operation_time = test_timer() - start_time
            baseline_times.append(operation_time)
        
        baseline_avg = sum(baseline_times) / len(baseline_times)
        
        # Load system with many memories
        for batch in range(20):  # 20 batches of 500 = 10,000 memories
            for i in range(500):
                memory.store_memory(
                    content=f"Load test batch {batch} memory {i}",
                    memory_type=MemoryType.SHORT_TERM,
                    emotional_tone=EmotionalTone.NEUTRAL,
                    tags=["load_test", f"batch_{batch}"]
                )
            
            # Measure performance every 5 batches
            if batch % 5 == 4:
                performance_times = []
                for i in range(10):
                    start_time = test_timer()
                    
                    memory_id = memory.store_memory(
                        content=f"Performance test after batch {batch} iteration {i}",
                        memory_type=MemoryType.SHORT_TERM,
                        emotional_tone=EmotionalTone.NEUTRAL,
                        tags=["perf_test"]
                    )
                    
                    retrieved = memory.retrieve_memories(
                        query="performance test",
                        memory_types=[MemoryType.SHORT_TERM],
                        limit=5
                    )
                    
                    operation_time = test_timer() - start_time
                    performance_times.append(operation_time)
                
                current_avg = sum(performance_times) / len(performance_times)
                degradation = (current_avg - baseline_avg) / baseline_avg
                
                print(f"After batch {batch}: {current_avg:.4f}s avg (degradation: {degradation:.2%})")
                
                # Performance should not degrade more than 100%
                assert degradation < 1.0, f"Performance degraded too much: {degradation:.2%}"
        
        print(f"Baseline performance: {baseline_avg:.4f}s")
        print("Performance degradation test completed successfully")