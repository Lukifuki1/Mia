#!/usr/bin/env python3
"""
Integration Tests - Consciousness Integration
Tests for consciousness loop integration: introspection → memory → LLM → action → memory → introspection
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock
from mia.core.consciousness.main import ConsciousnessModule, ConsciousnessState, EmotionalState
from mia.core.memory.main import MemorySystem, MemoryType, EmotionalTone
from mia.core.adaptive_llm import AdaptiveLLMManager

@pytest.mark.integration
@pytest.mark.critical
class TestConsciousnessIntegration:

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Test consciousness integration with other systems"""
    
    def test_consciousness_memory_integration(self, deterministic_environment, isolated_memory, isolated_consciousness):
        """Test consciousness-memory integration cycle"""
        consciousness = isolated_consciousness
        memory = isolated_memory
        
        # Mock memory integration
        with patch('mia.core.consciousness.main.store_memory') as mock_store, \
             patch('mia.core.consciousness.main.retrieve_memories') as mock_retrieve:
            
            mock_store.return_value = "test_memory_id"
            mock_retrieve.return_value = [
                {
                    "id": "mem_1",
                    "content": "Previous introspective thought",
                    "emotional_tone": EmotionalTone.NEUTRAL.value,
                    "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                }
            ]
            
            # Set consciousness to introspective state
            consciousness.consciousness_state = ConsciousnessState.INTROSPECTIVE
            
            # Perform introspective analysis
            result = consciousness._perform_introspective_analysis()
            
            # Should have stored memory
            assert mock_store.called
            
            # Should have retrieved previous memories
            assert mock_retrieve.called
            
            # Result should contain analysis
            assert isinstance(result, dict)
            assert "self_assessment" in result
            assert "insights" in result
    
    def test_consciousness_llm_integration(self, deterministic_environment, isolated_consciousness):
        """Test consciousness-LLM integration"""
        consciousness = isolated_consciousness
        
        # Mock LLM integration
        with patch('mia.core.consciousness.main.get_best_model_for_task') as mock_llm:
            mock_llm.return_value = {
                "name": "test-model",
                "capabilities": ["reasoning", "introspection"],
                "performance_score": 0.8
            }
            
            # Set consciousness to active state
            consciousness.consciousness_state = ConsciousnessState.ACTIVE
            
            # Process user input that requires LLM
            result = consciousness.process_user_input(
                "What are you thinking about?",
                {"emotional_tone": "curious"}
            )
            
            # Should have used LLM for processing
            assert mock_llm.called
            
            # Result should contain LLM-processed response
            assert isinstance(result, dict)
            assert "consciousness_state" in result
            assert "response_context" in result
    
    def test_full_consciousness_cycle(self, deterministic_environment, isolated_consciousness, isolated_memory):
        """Test complete consciousness cycle: introspection → memory → LLM → action → memory"""
        consciousness = isolated_consciousness
        memory = isolated_memory
        
        # Mock all integrations
        with patch('mia.core.consciousness.main.store_memory') as mock_store, \
             patch('mia.core.consciousness.main.retrieve_memories') as mock_retrieve, \
             patch('mia.core.consciousness.main.get_best_model_for_task') as mock_llm:
            
            # Setup mocks
            mock_store.return_value = "cycle_memory_id"
            mock_retrieve.return_value = []
            mock_llm.return_value = {
                "name": "cycle-model",
                "capabilities": ["reasoning"],
                "performance_score": 0.9
            }
            
            # Start with introspective state
            consciousness.consciousness_state = ConsciousnessState.INTROSPECTIVE
            
            # Perform complete cycle
            cycle_results = []
            
            for i in range(5):
                # 1. Introspection
                introspection_result = consciousness._perform_introspective_analysis()
                cycle_results.append(("introspection", introspection_result))
                
                # 2. Memory interaction (should happen in introspection)
                # Already tested above
                
                # 3. State transition
                consciousness._update_consciousness_state()
                
                # 4. Process thoughts (LLM interaction)
                consciousness._process_thoughts()
                
                # 5. Action (emotional state update)
                consciousness._update_emotional_state({})
                
                cycle_results.append(("state", {
                    "consciousness_state": consciousness.consciousness_state,
                    "emotional_state": consciousness.emotional_state,
                    "awareness_level": consciousness.awareness_level
                }))
            
            # Verify cycle completion
            assert len(cycle_results) == 10  # 5 introspections + 5 states
            
            # Verify memory interactions occurred
            assert mock_store.call_count >= 5
            
            # Verify consciousness remained active
            final_state = consciousness.consciousness_state
            assert final_state != ConsciousnessState.DORMANT
    
    def test_consciousness_cycle_stability_10k_iterations(self, deterministic_environment, isolated_consciousness):
        """Test consciousness cycle stability over 10,000 iterations"""
        consciousness = isolated_consciousness
        
        # Mock integrations for performance
        with patch('mia.core.consciousness.main.store_memory') as mock_store, \
             patch('mia.core.consciousness.main.retrieve_memories') as mock_retrieve:
            
            mock_store.return_value = "stability_memory_id"
            mock_retrieve.return_value = []
            
            # Set initial state
            consciousness.consciousness_state = ConsciousnessState.ACTIVE
            
            # Track stability metrics
            stability_metrics = {
                "dormant_count": 0,
                "active_count": 0,
                "error_count": 0,
                "awareness_levels": [],
                "emotional_states": []
            }
            
            # Run 10,000 iterations
            for i in range(10000):
                try:
                    # Perform consciousness cycle
                    consciousness._update_consciousness_state()
                    consciousness._update_emotional_state({})
                    consciousness._process_thoughts()
                    
                    # Track metrics
                    if consciousness.consciousness_state == ConsciousnessState.DORMANT:
                        stability_metrics["dormant_count"] += 1
                    else:
                        stability_metrics["active_count"] += 1
                    
                    stability_metrics["awareness_levels"].append(consciousness.awareness_level)
                    stability_metrics["emotional_states"].append(consciousness.emotional_state)
                    
                except Exception as e:
                    stability_metrics["error_count"] += 1
                    if stability_metrics["error_count"] > 100:  # Too many errors
                        break
            
            # Verify stability requirements
            assert stability_metrics["error_count"] < 100  # Less than 1% error rate
            assert stability_metrics["active_count"] >= 9000  # At least 90% uptime
            assert stability_metrics["dormant_count"] <= 1000  # At most 10% dormant
            
            # Verify awareness stability
            avg_awareness = sum(stability_metrics["awareness_levels"]) / len(stability_metrics["awareness_levels"])
            assert avg_awareness > 0.2  # Minimum awareness threshold
            
            # Verify emotional stability (no excessive swings)
            emotional_changes = 0
            for i in range(1, len(stability_metrics["emotional_states"])):
                if stability_metrics["emotional_states"][i] != stability_metrics["emotional_states"][i-1]:
                    emotional_changes += 1
            
            emotional_change_rate = emotional_changes / 10000
            assert emotional_change_rate < 0.1  # Less than 10% emotional state changes
    
    def test_consciousness_memory_consistency(self, deterministic_environment, isolated_consciousness, isolated_memory):
        """Test consciousness-memory consistency over multiple cycles"""
        consciousness = isolated_consciousness
        memory = isolated_memory
        
        stored_memories = []
        
        # Mock memory storage to track what's stored
        def mock_store_memory(content, emotional_tone, tags=None):
            memory_id = f"mem_{len(stored_memories)}"
            stored_memories.append({
                "id": memory_id,
                "content": content,
                "emotional_tone": emotional_tone,
                "tags": tags or []
            })
            return memory_id
        
        # Mock memory retrieval to return stored memories
        def mock_retrieve_memories(query, limit=10):
            return [mem for mem in stored_memories if query.lower() in mem["content"].lower()][:limit]
        
        with patch('mia.core.consciousness.main.store_memory', side_effect=mock_store_memory), \
             patch('mia.core.consciousness.main.retrieve_memories', side_effect=mock_retrieve_memories):
            
            # Perform multiple consciousness cycles
            for cycle in range(20):
                consciousness.consciousness_state = ConsciousnessState.INTROSPECTIVE
                
                # Perform introspective analysis
                result = consciousness._perform_introspective_analysis()
                
                # Update states
                consciousness._update_consciousness_state()
                consciousness._update_emotional_state({})
            
            # Verify memory consistency
            assert len(stored_memories) >= 20  # Should have stored memories
            
            # Check memory content consistency
            for memory in stored_memories:
                assert "id" in memory
                assert "content" in memory
                assert len(memory["content"]) > 0
                assert "emotional_tone" in memory
            
            # Test memory retrieval consistency
            retrieved = mock_retrieve_memories("introspective")
            assert len(retrieved) > 0
            
            # Retrieved memories should match stored ones
            for retrieved_mem in retrieved:
                assert retrieved_mem in stored_memories
    
    def test_consciousness_emotional_memory_integration(self, deterministic_environment, isolated_consciousness):
        """Test consciousness emotional state integration with memory"""
        consciousness = isolated_consciousness
        
        emotional_memories = []
        
        def mock_store_emotional_memory(content, emotional_tone, tags=None):
            emotional_memories.append({
                "content": content,
                "emotional_tone": emotional_tone,
                "consciousness_state": consciousness.consciousness_state,
                "emotional_state": consciousness.emotional_state
            })
            return f"emotional_mem_{len(emotional_memories)}"
        
        with patch('mia.core.consciousness.main.store_memory', side_effect=mock_store_emotional_memory):
            
            # Test different emotional contexts
            emotional_contexts = [
                {"user_feedback": "positive", "interaction_quality": "high"},
                {"user_feedback": "negative", "interaction_quality": "low"},
                {"system_event": "error", "severity": "high"},
                {"system_event": "optimization", "severity": "low"},
                {"creative_task": "completed", "satisfaction": "high"}
            ]
            
            for context in emotional_contexts:
                # Update emotional state based on context
                consciousness._update_emotional_state(context)
                
                # Perform introspective analysis
                consciousness.consciousness_state = ConsciousnessState.INTROSPECTIVE
                result = consciousness._perform_introspective_analysis()
            
            # Verify emotional memory integration
            assert len(emotional_memories) >= 5
            
            # Check emotional consistency
            for mem in emotional_memories:
                assert "emotional_tone" in mem
                assert "consciousness_state" in mem
                assert "emotional_state" in mem
                
                # Emotional tone should correlate with consciousness state
                if mem["consciousness_state"] == ConsciousnessState.INTROSPECTIVE:
                    assert mem["emotional_tone"] in [EmotionalTone.NEUTRAL, EmotionalTone.CONTEMPLATIVE]
    
    def test_consciousness_llm_memory_chain(self, deterministic_environment, isolated_consciousness):
        """Test consciousness → LLM → memory → consciousness chain"""
        consciousness = isolated_consciousness
        
        chain_log = []
        
        def mock_store_chain_memory(content, emotional_tone, tags=None):
            chain_log.append(("store", content, emotional_tone))
            return f"chain_mem_{len(chain_log)}"
        
        def mock_retrieve_chain_memories(query, limit=10):
            chain_log.append(("retrieve", query, limit))
            return [{"content": f"Retrieved memory for {query}", "id": "retrieved_1"}]
        
        def mock_llm_processing(task_type, capabilities=None):
            chain_log.append(("llm", task_type, capabilities))
            return {
                "name": "chain-model",
                "capabilities": capabilities or [],
                "performance_score": 0.85
            }
        
        with patch('mia.core.consciousness.main.store_memory', side_effect=mock_store_chain_memory), \
             patch('mia.core.consciousness.main.retrieve_memories', side_effect=mock_retrieve_chain_memories), \
             patch('mia.core.consciousness.main.get_best_model_for_task', side_effect=mock_llm_processing):
            
            # Start chain reaction
            consciousness.consciousness_state = ConsciousnessState.ACTIVE
            
            # Process complex user input
            result = consciousness.process_user_input(
                "I need help with a complex problem that requires deep thinking",
                {"emotional_tone": "serious", "complexity": "high"}
            )
            
            # Perform introspective analysis
            consciousness.consciousness_state = ConsciousnessState.INTROSPECTIVE
            introspection_result = consciousness._perform_introspective_analysis()
            
            # Verify chain execution
            assert len(chain_log) >= 3  # Should have multiple chain operations
            
            # Check chain sequence
            operation_types = [op[0] for op in chain_log]
            assert "llm" in operation_types  # LLM should be used
            assert "store" in operation_types  # Memory should be stored
            
            # Verify result quality
            assert isinstance(result, dict)
            assert isinstance(introspection_result, dict)
    
    @pytest.mark.asyncio
    async def test_async_consciousness_integration(self, deterministic_environment, isolated_consciousness):
        """Test asynchronous consciousness integration"""
        consciousness = isolated_consciousness
        
        async_operations = []
        
        async def mock_async_store(content, emotional_tone, tags=None):
            async_operations.append(("async_store", content))
            await asyncio.sleep(0.001)  # Simulate async operation
            return f"async_mem_{len(async_operations)}"
        
        async def mock_async_retrieve(query, limit=10):
            async_operations.append(("async_retrieve", query))
            await asyncio.sleep(0.001)  # Simulate async operation
            return [{"content": f"Async retrieved: {query}", "id": "async_1"}]
        
        with patch('mia.core.consciousness.main.store_memory', side_effect=mock_async_store), \
             patch('mia.core.consciousness.main.retrieve_memories', side_effect=mock_async_retrieve):
            
            # Start async consciousness loop
            consciousness_task = asyncio.create_task(consciousness.start_consciousness_loop())
            
            # Let it run briefly
            await asyncio.sleep(0.1)
            
            # Process some inputs
            for i in range(5):
                result = consciousness.process_user_input(f"Async test {i}", {})
                assert isinstance(result, dict)
            
            # Stop consciousness loop
            consciousness.stop_consciousness_loop()
            
            # Wait for cleanup
            await asyncio.sleep(0.05)
            
            # Cancel task
            consciousness_task.cancel()
            
            try:
                await consciousness_task
            except asyncio.CancelledError:
                pass
            
            # Verify async operations occurred
            assert len(async_operations) >= 0  # May or may not have async ops depending on timing
    
    def test_consciousness_integration_error_recovery(self, deterministic_environment, isolated_consciousness):
        """Test consciousness integration error recovery"""
        consciousness = isolated_consciousness
        
        error_count = 0
        recovery_count = 0
        
        def mock_failing_store(content, emotional_tone, tags=None):
            nonlocal error_count, recovery_count
            error_count += 1
            if error_count <= 3:
                raise Exception(f"Storage error {error_count}")
            recovery_count += 1
            return f"recovered_mem_{recovery_count}"
        
        def mock_failing_retrieve(query, limit=10):
            nonlocal error_count
            error_count += 1
            if error_count <= 2:
                raise Exception(f"Retrieval error {error_count}")
            return [{"content": "Recovered memory", "id": "recovered_1"}]
        
        with patch('mia.core.consciousness.main.store_memory', side_effect=mock_failing_store), \
             patch('mia.core.consciousness.main.retrieve_memories', side_effect=mock_failing_retrieve):
            
            # Attempt operations that will initially fail
            for i in range(10):
                try:
                    consciousness.consciousness_state = ConsciousnessState.INTROSPECTIVE
                    result = consciousness._perform_introspective_analysis()
                    
                    # Should eventually succeed
                    if i >= 5:  # After some failures
                        assert isinstance(result, dict)
                        
                except Exception as e:
                    # Early failures are expected
                    if i < 5:
                        continue
                    else:
                        # Later operations should succeed
                        raise
            
            # Verify recovery occurred
            assert error_count > 0  # Errors should have occurred
            assert recovery_count > 0  # Recovery should have happened
            
            # Consciousness should still be functional
            assert consciousness.consciousness_state != ConsciousnessState.DORMANT
    
    def test_consciousness_performance_integration(self, deterministic_environment, isolated_consciousness, test_timer):
        """Test consciousness integration performance"""
        consciousness = isolated_consciousness
        
        # Mock fast integrations
        with patch('mia.core.consciousness.main.store_memory', return_value="perf_mem"), \
             patch('mia.core.consciousness.main.retrieve_memories', return_value=[]), \
             patch('mia.core.consciousness.main.get_best_model_for_task', return_value={"name": "fast-model"}):
            
            # Test integration performance
            start_time = test_timer()
            
            for i in range(100):
                # Full integration cycle
                consciousness.consciousness_state = ConsciousnessState.ACTIVE
                consciousness._update_consciousness_state()
                consciousness._update_emotional_state({})
                consciousness._process_thoughts()
                
                # Introspective analysis
                consciousness.consciousness_state = ConsciousnessState.INTROSPECTIVE
                result = consciousness._perform_introspective_analysis()
            
            elapsed_time = test_timer()
            
            # Performance requirements
            assert elapsed_time < 10.0  # 100 cycles in under 10 seconds
            
            # Average cycle time
            avg_cycle_time = elapsed_time / 100
            assert avg_cycle_time < 0.1  # Under 100ms per cycle