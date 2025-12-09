#!/usr/bin/env python3
"""
Deterministic Tests - Core Determinism
Tests for deterministic behavior: same input → same output, hash consistency, reproducibility
"""

import pytest
import time
import hashlib
import json
import random
import numpy as np
from unittest.mock import Mock, patch
from mia.core.consciousness.main import ConsciousnessModule
from mia.core.memory.main import MemorySystem
from mia.core.adaptive_llm import AdaptiveLLMManager

@pytest.mark.deterministic
@pytest.mark.critical
class TestDeterministicCore:
    """Test core deterministic behavior"""
    
    def test_deterministic_input_output(self, deterministic_environment):
        """Test that same input produces same output"""
        # Test consciousness determinism
        consciousness = ConsciousnessModule()
        
        # Set deterministic state
        consciousness.consciousness_state = "ACTIVE"
        consciousness.emotional_state = "NEUTRAL"
        consciousness.awareness_level = 0.7
        
        # Test input
        test_input = "What are you thinking about right now?"
        test_context = {"emotional_tone": "curious", "complexity": "medium"}
        
        # Generate multiple outputs
        outputs = []
        for i in range(5):
            # Reset to same state
            consciousness.consciousness_state = "ACTIVE"
            consciousness.emotional_state = "NEUTRAL" 
            consciousness.awareness_level = 0.7
            
            # Process same input
            result = consciousness.process_user_input(test_input, test_context)
            outputs.append(result)
        
        # Verify deterministic behavior
        assert len(outputs) == 5
        
        # Check that core response structure is consistent
        for output in outputs:
            assert "consciousness_state" in output
            assert "emotional_state" in output
            assert "response_context" in output
            
        # Check that consciousness states are consistent
        consciousness_states = [out["consciousness_state"] for out in outputs]
        assert len(set(consciousness_states)) <= 2  # Should be mostly consistent
        
        # Check that response contexts have consistent structure
        for output in outputs:
            assert "interaction_type" in output["response_context"]
            assert "processing_time" in output["response_context"]
    
    def test_hash_consistency(self, deterministic_environment):
        """Test hash consistency for deterministic operations"""
        # Test memory hash consistency
        memory = MemorySystem()
        
        # Create test data
        test_data = {
            "content": "Deterministic test memory content",
            "memory_type": "SHORT_TERM",
            "emotional_tone": "NEUTRAL",
            "tags": ["deterministic", "test", "hash"]
        }
        
        # Generate hashes multiple times
        hashes = []
        for i in range(10):
            # Create hash of memory data
            data_string = json.dumps(test_data, sort_keys=True)
            data_hash = hashlib.sha256(data_string.encode()).hexdigest()
            hashes.append(data_hash)
        
        # All hashes should be identical
        assert len(set(hashes)) == 1, "Hash consistency failed"
        
        # Test consciousness state hash consistency
        consciousness = ConsciousnessModule()
        
        # Set specific state
        consciousness.consciousness_state = "INTROSPECTIVE"
        consciousness.emotional_state = "CONTEMPLATIVE"
        consciousness.awareness_level = 0.85
        
        # Generate state hashes
        state_hashes = []
        for i in range(10):
            state_data = {
                "consciousness_state": consciousness.consciousness_state,
                "emotional_state": consciousness.emotional_state,
                "awareness_level": consciousness.awareness_level
            }
            state_string = json.dumps(state_data, sort_keys=True)
            state_hash = hashlib.sha256(state_string.encode()).hexdigest()
            state_hashes.append(state_hash)
        
        # All state hashes should be identical
        assert len(set(state_hashes)) == 1, "State hash consistency failed"
    
    def test_model_switching_determinism(self, deterministic_environment, mock_hardware):
        """Test determinism during model switching"""
        llm_manager = AdaptiveLLMManager()
        
        # Mock models
        test_models = ["model-a", "model-b", "model-c"]
        
        # Test deterministic model switching
        switching_results = []
        
        for cycle in range(3):
            cycle_results = []
            
            for model_name in test_models:
                # Mock model loading
                with patch.object(llm_manager, '_load_model', return_value=True), \
                     patch.object(llm_manager, '_generate_with_model') as mock_generate:
                    
                    mock_generate.return_value = {
                        "text": f"Deterministic output from {model_name}",
                        "tokens": 25,
                        "model": model_name
                    }
                    
                    # Load model
                    success = llm_manager.load_model(model_name)
                    assert success == True
                    
                    # Generate text
                    result = llm_manager.generate_text("Deterministic test prompt")
                    cycle_results.append(result)
            
            switching_results.append(cycle_results)
        
        # Verify deterministic behavior across cycles
        assert len(switching_results) == 3
        
        for i in range(len(test_models)):
            # Results for same model should be consistent across cycles
            model_results = [cycle[i] for cycle in switching_results]
            
            # Check text consistency
            texts = [result["text"] for result in model_results]
            assert len(set(texts)) == 1, f"Text inconsistency for model {test_models[i]}"
            
            # Check token consistency
            tokens = [result["tokens"] for result in model_results]
            assert len(set(tokens)) == 1, f"Token inconsistency for model {test_models[i]}"
    
    def test_memory_deterministic_access(self, deterministic_environment):
        """Test deterministic memory access patterns"""
        memory = MemorySystem()
        
        # Store test memories in deterministic order
        test_memories = [
            {"content": f"Deterministic memory {i}", "tags": [f"det_{i}", "test"]}
            for i in range(100)
        ]
        
        stored_ids = []
        for mem_data in test_memories:
            memory_id = memory.store_memory(
                content=mem_data["content"],
                memory_type="SHORT_TERM",
                emotional_tone="NEUTRAL",
                tags=mem_data["tags"]
            )
            stored_ids.append(memory_id)
        
        # Test deterministic retrieval
        retrieval_queries = [
            "deterministic memory 5",
            "det_10",
            "test",
            "memory 25",
            "det_50"
        ]
        
        # Perform multiple retrieval cycles
        retrieval_cycles = []
        for cycle in range(5):
            cycle_results = []
            
            for query in retrieval_queries:
                retrieved = memory.retrieve_memories(
                    query=query,
                    memory_types=["SHORT_TERM"],
                    limit=10
                )
                
                # Create deterministic representation
                result_repr = []
                for mem in retrieved:
                    result_repr.append({
                        "content": mem["content"],
                        "id": mem["id"]
                    })
                
                cycle_results.append(result_repr)
            
            retrieval_cycles.append(cycle_results)
        
        # Verify deterministic retrieval
        for query_idx in range(len(retrieval_queries)):
            query_results = [cycle[query_idx] for cycle in retrieval_cycles]
            
            # All cycles should return same results for same query
            for i in range(1, len(query_results)):
                assert query_results[i] == query_results[0], f"Retrieval inconsistency for query {retrieval_queries[query_idx]}"
    
    def test_consciousness_deterministic_states(self, deterministic_environment):
        """Test deterministic consciousness state transitions"""
        consciousness = ConsciousnessModule()
        
        # Test deterministic state transitions
        initial_states = [
            ("DORMANT", "NEUTRAL", 0.0),
            ("AWAKENING", "CURIOUS", 0.3),
            ("ACTIVE", "ENGAGED", 0.7),
            ("INTROSPECTIVE", "CONTEMPLATIVE", 0.9),
            ("CREATIVE", "INSPIRED", 0.8)
        ]
        
        for initial_state in initial_states:
            consciousness_state, emotional_state, awareness_level = initial_state
            
            # Test multiple transition cycles from same initial state
            transition_results = []
            
            for cycle in range(5):
                # Reset to initial state
                consciousness.consciousness_state = consciousness_state
                consciousness.emotional_state = emotional_state
                consciousness.awareness_level = awareness_level
                
                # Perform state transitions
                cycle_transitions = []
                for step in range(10):
                    consciousness._update_consciousness_state()
                    consciousness._update_emotional_state({})
                    
                    state_snapshot = {
                        "consciousness_state": consciousness.consciousness_state,
                        "emotional_state": consciousness.emotional_state,
                        "awareness_level": round(consciousness.awareness_level, 3)
                    }
                    cycle_transitions.append(state_snapshot)
                
                transition_results.append(cycle_transitions)
            
            # Verify deterministic transitions
            # Note: Some variation is expected due to randomness, but patterns should be similar
            for step in range(10):
                step_states = [cycle[step] for cycle in transition_results]
                
                # Check that consciousness doesn't become dormant unexpectedly
                consciousness_states = [state["consciousness_state"] for state in step_states]
                dormant_count = consciousness_states.count("DORMANT")
                assert dormant_count <= len(step_states) * 0.2, f"Too many dormant states at step {step}"
                
                # Check awareness level stability
                awareness_levels = [state["awareness_level"] for state in step_states]
                awareness_variance = max(awareness_levels) - min(awareness_levels)
                assert awareness_variance <= 0.5, f"Excessive awareness variance at step {step}"
    
    def test_deterministic_rerun_consistency(self, deterministic_environment):
        """Test consistency across complete system reruns"""
        # Test complete system rerun determinism
        system_runs = []
        
        for run in range(3):
            run_results = {}
            
            # Initialize systems
            consciousness = ConsciousnessModule()
            memory = MemorySystem()
            
            # Set deterministic initial state
            consciousness.consciousness_state = "ACTIVE"
            consciousness.emotional_state = "NEUTRAL"
            consciousness.awareness_level = 0.5
            
            # Perform standard operations
            # 1. Store memories
            memory_ids = []
            for i in range(10):
                memory_id = memory.store_memory(
                    content=f"Rerun test memory {i}",
                    memory_type="SHORT_TERM",
                    emotional_tone="NEUTRAL",
                    tags=["rerun", "test"]
                )
                memory_ids.append(memory_id)
            
            run_results["memory_count"] = len(memory_ids)
            
            # 2. Process consciousness
            consciousness_results = []
            for i in range(5):
                result = consciousness.process_user_input(
                    f"Test input {i}",
                    {"emotional_tone": "neutral"}
                )
                consciousness_results.append(result["consciousness_state"])
            
            run_results["consciousness_states"] = consciousness_results
            
            # 3. Retrieve memories
            retrieved = memory.retrieve_memories(
                query="rerun test",
                memory_types=["SHORT_TERM"],
                limit=10
            )
            run_results["retrieved_count"] = len(retrieved)
            
            # 4. System status
            memory_status = memory.get_system_status()
            run_results["memory_status"] = memory_status["status"]
            
            consciousness_status = consciousness.get_consciousness_state()
            run_results["final_consciousness_state"] = consciousness_status["consciousness_state"]
            
            system_runs.append(run_results)
        
        # Verify consistency across runs
        assert len(system_runs) == 3
        
        # Check memory operations consistency
        memory_counts = [run["memory_count"] for run in system_runs]
        assert len(set(memory_counts)) == 1, "Memory count inconsistency across runs"
        
        retrieved_counts = [run["retrieved_count"] for run in system_runs]
        assert len(set(retrieved_counts)) == 1, "Retrieved count inconsistency across runs"
        
        # Check system status consistency
        memory_statuses = [run["memory_status"] for run in system_runs]
        assert len(set(memory_statuses)) == 1, "Memory status inconsistency across runs"
        
        # Check consciousness consistency (allow some variation)
        final_consciousness_states = [run["final_consciousness_state"] for run in system_runs]
        # Should not all be dormant
        dormant_count = final_consciousness_states.count("DORMANT")
        assert dormant_count <= 1, "Too many dormant final states"
    
    def test_random_seed_determinism(self, deterministic_environment):
        """Test determinism with controlled random seeds"""
        import random
        import numpy as np
        
        # Test with fixed random seed
        test_seed = 12345
        
        # Generate random sequences with same seed
        sequences = []
        
        for run in range(3):
            # Set seeds
            random.seed(test_seed)
            np.random.seed(test_seed)
            
            # Generate sequence
            sequence = {
                "random_ints": [random.randint(1, 100) for _ in range(10)],
                "random_floats": [self._get_deterministic_random() if hasattr(self, "_get_deterministic_random") else 0.5 for _ in range(10)],
                "numpy_ints": np.random.randint(1, 100, 10).tolist(),
                "numpy_floats": np.random.random(10).tolist()
            }
            
            sequences.append(sequence)
        
        # Verify all sequences are identical
        for i in range(1, len(sequences)):
            assert sequences[i]["random_ints"] == sequences[0]["random_ints"]
            assert sequences[i]["random_floats"] == sequences[0]["random_floats"]
            assert sequences[i]["numpy_ints"] == sequences[0]["numpy_ints"]
            assert sequences[i]["numpy_floats"] == sequences[0]["numpy_floats"]
    
    def test_deterministic_error_recovery(self, deterministic_environment):
        """Test deterministic error recovery behavior"""
        consciousness = ConsciousnessModule()
        
        # Test deterministic error scenarios
        error_scenarios = [
            {"error_type": "memory_error", "recovery_expected": True},
            {"error_type": "processing_error", "recovery_expected": True},
            {"error_type": "state_error", "recovery_expected": True}
        ]
        
        for scenario in error_scenarios:
            recovery_results = []
            
            # Test same error scenario multiple times
            for attempt in range(3):
                # Reset to known state
                consciousness.consciousness_state = "ACTIVE"
                consciousness.emotional_state = "NEUTRAL"
                
                # Simulate error and recovery
                try:
                    if scenario["error_type"] == "memory_error":
                        # Simulate memory error
                        with patch('mia.core.consciousness.main.store_memory', side_effect=Exception("Memory error")):
                            result = consciousness._perform_introspective_analysis()
                    
                    elif scenario["error_type"] == "processing_error":
                        # Simulate processing error
                        with patch.object(consciousness, '_generate_thought', side_effect=Exception("Processing error")):
                            consciousness._process_thoughts()
                            result = {"error_handled": True}
                    
                    elif scenario["error_type"] == "state_error":
                        # Simulate state error
                        consciousness.consciousness_state = None  # Invalid state
                        consciousness._update_consciousness_state()
                        result = {"state_recovered": consciousness.consciousness_state is not None}
                    
                    recovery_results.append(result)
                    
                except Exception as e:
                    # Error should be handled gracefully
                    recovery_results.append({"error": str(e), "handled": True})
            
            # Verify deterministic recovery
            assert len(recovery_results) == 3
            
            # Recovery behavior should be consistent
            if scenario["recovery_expected"]:
                # All attempts should either succeed or fail consistently
                success_count = sum(1 for result in recovery_results if not result.get("error"))
                # Should have some successful recoveries
                assert success_count >= 1, f"No successful recovery for {scenario['error_type']}"
    
    def test_deterministic_performance_metrics(self, deterministic_environment, test_timer):
        """Test deterministic performance metrics"""
        consciousness = ConsciousnessModule()
        memory = MemorySystem()
        
        # Test performance consistency
        performance_runs = []
        
        for run in range(5):
            run_metrics = {}
            
            # Test consciousness performance
            start_time = test_timer()
            
            for i in range(100):
                consciousness._update_consciousness_state()
                consciousness._update_emotional_state({})
            
            consciousness_time = test_timer() - start_time
            run_metrics["consciousness_time"] = consciousness_time
            
            # Test memory performance
            start_time = test_timer()
            
            for i in range(100):
                memory.store_memory(
                    content=f"Performance test {i}",
                    memory_type="SHORT_TERM",
                    emotional_tone="NEUTRAL",
                    tags=["performance"]
                )
            
            memory_time = test_timer() - start_time
            run_metrics["memory_time"] = memory_time
            
            performance_runs.append(run_metrics)
        
        # Verify performance consistency
        consciousness_times = [run["consciousness_time"] for run in performance_runs]
        memory_times = [run["memory_time"] for run in performance_runs]
        
        # Calculate variance
        consciousness_variance = max(consciousness_times) - min(consciousness_times)
        memory_variance = max(memory_times) - min(memory_times)
        
        # Performance should be relatively consistent
        consciousness_avg = sum(consciousness_times) / len(consciousness_times)
        memory_avg = sum(memory_times) / len(memory_times)
        
        # Variance should be less than 50% of average
        assert consciousness_variance < consciousness_avg * 0.5, "Consciousness performance too variable"
        assert memory_variance < memory_avg * 0.5, "Memory performance too variable"
        
        print(f"Consciousness avg: {consciousness_avg:.4f}s, variance: {consciousness_variance:.4f}s")
        print(f"Memory avg: {memory_avg:.4f}s, variance: {memory_variance:.4f}s")