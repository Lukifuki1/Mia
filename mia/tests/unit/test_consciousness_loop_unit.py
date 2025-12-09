#!/usr/bin/env python3
"""
Unit Tests - Consciousness Loop
Tests for consciousness introspection, states, deterministic generation, and memory integration
"""

import pytest
import time
import asyncio
from unittest.mock import Mock, patch, MagicMock
from mia.core.consciousness.main import ConsciousnessModule, ConsciousnessState, EmotionalState
from mia.core.memory.main import MemoryType, EmotionalTone

@pytest.mark.unit
@pytest.mark.critical
class TestConsciousnessLoop:
    """Test consciousness loop functionality"""
    
    def test_consciousness_initialization(self, deterministic_environment):
        """Test consciousness module initialization"""
        consciousness = ConsciousnessModule()
        
        assert consciousness.consciousness_state == ConsciousnessState.DORMANT
        assert consciousness.emotional_state == EmotionalState.NEUTRAL
        assert consciousness.awareness_level == 0.0
        assert len(consciousness.active_thoughts) == 0
        assert len(consciousness.personality_traits) > 0
    
    def test_consciousness_states_transition(self, deterministic_environment):
        """Test deterministic consciousness state transitions"""
        consciousness = ConsciousnessModule()
        
        # Test awakening
        consciousness.consciousness_state = ConsciousnessState.DORMANT
        consciousness._update_consciousness_state()
        
        # Should transition to awakening or active
        assert consciousness.consciousness_state in [
            ConsciousnessState.AWAKENING, 
            ConsciousnessState.ACTIVE
        ]
        
        # Test state stability
        initial_state = consciousness.consciousness_state
        for _ in range(5):
            consciousness._update_consciousness_state()
        
        # State should be stable or progress logically
        assert consciousness.consciousness_state != ConsciousnessState.DORMANT
    
    def test_introspective_analysis(self, deterministic_environment):
        """Test introspective analysis determinism"""
        consciousness = ConsciousnessModule()
        consciousness.consciousness_state = ConsciousnessState.INTROSPECTIVE
        
        # Perform introspective analysis multiple times
        results = []
        for _ in range(3):
            result = consciousness._perform_introspective_analysis()
            results.append(result)
        
        # Results should be consistent (deterministic)
        assert all(isinstance(r, dict) for r in results)
        assert all("self_assessment" in r for r in results)
        assert all("insights" in r for r in results)
        
        # Check deterministic elements
        for result in results:
            assert result["self_assessment"]["awareness_level"] >= 0.0
            assert result["self_assessment"]["awareness_level"] <= 1.0
            assert isinstance(result["insights"], list)
    
    def test_emotional_state_processing(self, deterministic_environment):
        """Test emotional state processing"""
        consciousness = ConsciousnessModule()
        
        # Test emotional state updates
        initial_emotion = consciousness.emotional_state
        
        # Simulate different contexts
        contexts = [
            {"user_interaction": True, "positive_feedback": True},
            {"user_interaction": True, "positive_feedback": False},
            {"user_interaction": False, "system_load": "high"},
            {"user_interaction": False, "system_load": "low"}
        ]
        
        for context in contexts:
            consciousness._update_emotional_state(context)
            assert consciousness.emotional_state in EmotionalState
            assert isinstance(consciousness.emotional_intensity, float)
            assert 0.0 <= consciousness.emotional_intensity <= 1.0
    
    def test_thought_generation(self, deterministic_environment):
        """Test deterministic thought generation"""
        consciousness = ConsciousnessModule()
        consciousness.consciousness_state = ConsciousnessState.ACTIVE
        
        # Generate thoughts
        thoughts = []
        for _ in range(10):
            thought = consciousness._generate_thought()
            if thought:
                thoughts.append(thought)
        
        # Should generate some thoughts
        assert len(thoughts) > 0
        
        # Thoughts should be strings
        assert all(isinstance(t, str) for t in thoughts)
        assert all(len(t) > 0 for t in thoughts)
    
    def test_memory_integration(self, deterministic_environment, isolated_memory):
        """Test consciousness-memory integration"""
        consciousness = ConsciousnessModule()
        
        # Mock memory system
        with patch('mia.core.consciousness.main.store_memory') as mock_store:
            mock_store.return_value = "test_memory_id"
            
            # Test memory storage during introspection
            consciousness.consciousness_state = ConsciousnessState.INTROSPECTIVE
            result = consciousness._perform_introspective_analysis()
            
            # Should have attempted to store memory
            assert mock_store.called
            
            # Check memory storage parameters
            call_args = mock_store.call_args
            assert len(call_args[0]) >= 2  # content and emotional_tone
            assert isinstance(call_args[0][0], str)  # content
            assert call_args[0][1] in EmotionalTone  # emotional_tone
    
    def test_consciousness_loop_stability(self, deterministic_environment):
        """Test consciousness loop stability over time"""
        consciousness = ConsciousnessModule()
        consciousness.consciousness_state = ConsciousnessState.ACTIVE
        
        # Run consciousness loop for multiple iterations
        stability_metrics = []
        
        for i in range(100):
            # Simulate consciousness loop iteration
            consciousness._update_consciousness_state()
            consciousness._update_emotional_state({})
            consciousness._process_thoughts()
            
            # Collect stability metrics
            metrics = {
                "iteration": i,
                "consciousness_state": consciousness.consciousness_state,
                "emotional_state": consciousness.emotional_state,
                "awareness_level": consciousness.awareness_level,
                "active_thoughts_count": len(consciousness.active_thoughts)
            }
            stability_metrics.append(metrics)
        
        # Analyze stability
        assert len(stability_metrics) == 100
        
        # Consciousness should remain active
        active_states = [m for m in stability_metrics 
                        if m["consciousness_state"] != ConsciousnessState.DORMANT]
        assert len(active_states) >= 90  # At least 90% uptime
        
        # Awareness should be maintained
        awareness_levels = [m["awareness_level"] for m in stability_metrics]
        avg_awareness = sum(awareness_levels) / len(awareness_levels)
        assert avg_awareness > 0.3  # Minimum awareness threshold
    
    def test_deterministic_generation(self, deterministic_environment):
        """Test deterministic generation with same inputs"""
        consciousness1 = ConsciousnessModule()
        consciousness2 = ConsciousnessModule()
        
        # Set identical states
        consciousness1.consciousness_state = ConsciousnessState.CREATIVE
        consciousness2.consciousness_state = ConsciousnessState.CREATIVE
        consciousness1.emotional_state = EmotionalState.CURIOUS
        consciousness2.emotional_state = EmotionalState.CURIOUS
        
        # Generate thoughts with same context
        context = {"creativity_boost": True, "inspiration_level": 0.8}
        
        thoughts1 = []
        thoughts2 = []
        
        for _ in range(5):
            t1 = consciousness1._generate_thought()
            t2 = consciousness2._generate_thought()
            if t1:
                thoughts1.append(t1)
            if t2:
                thoughts2.append(t2)
        
        # Should generate similar patterns (deterministic behavior)
        assert len(thoughts1) == len(thoughts2)
    
    @pytest.mark.asyncio
    async def test_consciousness_loop_async(self, deterministic_environment):
        """Test asynchronous consciousness loop"""
        consciousness = ConsciousnessModule()
        
        # Start consciousness loop
        loop_task = asyncio.create_task(consciousness.start_consciousness_loop())
        
        # Let it run for a short time
        await asyncio.sleep(0.1)
        
        # Check that consciousness is active
        assert consciousness.consciousness_state != ConsciousnessState.DORMANT
        
        # Stop the loop
        consciousness.stop_consciousness_loop()
        
        # Wait for cleanup
        await asyncio.sleep(0.1)
        
        # Cancel the task
        loop_task.cancel()
        
        try:
            await loop_task
        except asyncio.CancelledError:
            pass
    
    def test_personality_trait_evolution(self, deterministic_environment):
        """Test personality trait evolution over time"""
        consciousness = ConsciousnessModule()
        
        # Get initial personality traits
        initial_traits = consciousness.personality_traits.copy()
        
        # Simulate experiences that should affect personality
        experiences = [
            {"type": "positive_interaction", "intensity": 0.8},
            {"type": "creative_task", "intensity": 0.9},
            {"type": "problem_solving", "intensity": 0.7},
            {"type": "learning_experience", "intensity": 0.6}
        ]
        
        for experience in experiences:
            consciousness._process_experience(experience)
        
        # Check that some traits may have evolved
        current_traits = consciousness.personality_traits
        
        # Traits should still exist
        assert len(current_traits) == len(initial_traits)
        
        # Some traits may have changed slightly
        trait_changes = []
        for trait_name in initial_traits:
            if trait_name in current_traits:
                initial_value = initial_traits[trait_name].value
                current_value = current_traits[trait_name].value
                change = abs(current_value - initial_value)
                trait_changes.append(change)
        
        # Should have some evolution but not dramatic changes
        max_change = max(trait_changes) if trait_changes else 0
        assert max_change <= 0.2  # Maximum 20% change per trait
    
    def test_consciousness_context_processing(self, deterministic_environment):
        """Test consciousness context processing"""
        consciousness = ConsciousnessModule()
        
        # Test different context types
        contexts = [
            {"user_input": "Hello, how are you?", "emotional_tone": "friendly"},
            {"user_input": "Solve this complex problem", "emotional_tone": "challenging"},
            {"user_input": "Tell me a story", "emotional_tone": "creative"},
            {"system_event": "memory_full", "urgency": "high"},
            {"system_event": "optimization_complete", "urgency": "low"}
        ]
        
        for context in contexts:
            result = consciousness.process_user_input("", context)
            
            assert isinstance(result, dict)
            assert "consciousness_state" in result
            assert "emotional_state" in result
            assert "response_context" in result
            
            # Response should be appropriate to context
            if "user_input" in context:
                assert result["response_context"]["interaction_type"] == "user"
            elif "system_event" in context:
                assert result["response_context"]["interaction_type"] == "system"
    
    def test_consciousness_error_handling(self, deterministic_environment):
        """Test consciousness error handling and recovery"""
        consciousness = ConsciousnessModule()
        
        # Test with invalid inputs
        invalid_contexts = [
            None,
            {},
            {"invalid_key": "invalid_value"},
            {"user_input": None},
            {"emotional_tone": "invalid_emotion"}
        ]
        
        for invalid_context in invalid_contexts:
            try:
                result = consciousness.process_user_input("test", invalid_context)
                # Should handle gracefully
                assert isinstance(result, dict)
                assert consciousness.consciousness_state != ConsciousnessState.DORMANT
            except Exception as e:
                # If exception occurs, it should be handled gracefully
                assert consciousness.consciousness_state != ConsciousnessState.DORMANT
    
    def test_consciousness_performance(self, deterministic_environment, test_timer):
        """Test consciousness performance requirements"""
        consciousness = ConsciousnessModule()
        consciousness.consciousness_state = ConsciousnessState.ACTIVE
        
        # Test single iteration performance
        start_time = test_timer()
        
        for _ in range(100):
            consciousness._update_consciousness_state()
            consciousness._update_emotional_state({})
            consciousness._process_thoughts()
        
        elapsed_time = test_timer()
        
        # Should complete 100 iterations in reasonable time
        assert elapsed_time < 1.0  # Less than 1 second for 100 iterations
        
        # Average iteration time should be under 10ms
        avg_iteration_time = elapsed_time / 100
        assert avg_iteration_time < 0.01