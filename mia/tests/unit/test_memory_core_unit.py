#!/usr/bin/env python3
"""
Unit Tests - Memory Core
Tests for short/medium/long/meta memory operations, consistency, and deterministic access
"""

import pytest
import time
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from mia.core.memory.main import MemorySystem, MemoryType, EmotionalTone, store_memory, retrieve_memories

@pytest.mark.unit
@pytest.mark.critical
class TestMemoryCore:
    """Test memory system core functionality"""
    
    def test_memory_system_initialization(self, deterministic_environment, temp_workspace):
        """Test memory system initialization"""
        memory = MemorySystem()
        
        assert memory.config is not None
        assert memory.storage_path.exists()
        assert memory.vector_store is not None
        assert memory.memory_index is not None
        assert len(memory.active_memories) == 0
    
    def test_short_term_memory_operations(self, deterministic_environment, isolated_memory):
        """Test short-term memory storage and retrieval"""
        memory = isolated_memory
        
        # Store short-term memories
        test_memories = [
            "User asked about the weather",
            "System performed calculation",
            "User expressed satisfaction",
            "Error occurred in module X",
            "User requested file operation"
        ]
        
        memory_ids = []
        for content in test_memories:
            memory_id = memory.store_memory(
                content=content,
                memory_type=MemoryType.SHORT_TERM,
                emotional_tone=EmotionalTone.NEUTRAL,
                tags=["test", "short_term"]
            )
            memory_ids.append(memory_id)
            assert memory_id is not None
            assert len(memory_id) > 0
        
        # Retrieve memories
        retrieved = memory.retrieve_memories(
            query="user",
            memory_types=[MemoryType.SHORT_TERM],
            limit=10
        )
        
        assert len(retrieved) >= 3  # Should find user-related memories
        
        # Check memory structure
        for mem in retrieved:
            assert "id" in mem
            assert "content" in mem
            assert "memory_type" in mem
            assert "emotional_tone" in mem
            assert "timestamp" in mem
            assert "tags" in mem
    
    def test_medium_term_memory_operations(self, deterministic_environment, isolated_memory):
        """Test medium-term memory storage and retrieval"""
        memory = isolated_memory
        
        # Store medium-term memories
        behavioral_patterns = [
            "User prefers detailed explanations",
            "User works primarily in the evening",
            "User frequently asks about programming",
            "User shows interest in AI topics",
            "User uses formal communication style"
        ]
        
        for pattern in behavioral_patterns:
            memory_id = memory.store_memory(
                content=pattern,
                memory_type=MemoryType.MEDIUM_TERM,
                emotional_tone=EmotionalTone.NEUTRAL,
                tags=["behavior", "pattern", "user_preference"]
            )
            assert memory_id is not None
        
        # Retrieve behavioral patterns
        patterns = memory.retrieve_memories(
            query="user prefers",
            memory_types=[MemoryType.MEDIUM_TERM],
            limit=5
        )
        
        assert len(patterns) >= 1
        
        # Test pattern recognition
        user_patterns = memory.get_user_patterns()
        assert isinstance(user_patterns, dict)
        assert "communication_style" in user_patterns or "preferences" in user_patterns
    
    def test_long_term_memory_operations(self, deterministic_environment, isolated_memory):
        """Test long-term memory storage and retrieval"""
        memory = isolated_memory
        
        # Store long-term memories (core experiences)
        core_experiences = [
            "First interaction with user established trust",
            "Successfully completed complex project together",
            "User taught me about their domain expertise",
            "Developed understanding of user's goals",
            "Established collaborative working relationship"
        ]
        
        for experience in core_experiences:
            memory_id = memory.store_memory(
                content=experience,
                memory_type=MemoryType.LONG_TERM,
                emotional_tone=EmotionalTone.POSITIVE,
                tags=["relationship", "core_experience", "milestone"]
            )
            assert memory_id is not None
        
        # Retrieve core experiences
        experiences = memory.retrieve_memories(
            query="relationship",
            memory_types=[MemoryType.LONG_TERM],
            limit=10
        )
        
        assert len(experiences) >= 1
        
        # Test relationship context
        relationship_context = memory.get_relationship_context()
        assert isinstance(relationship_context, dict)
        assert "trust_level" in relationship_context
        assert "interaction_history" in relationship_context
    
    def test_meta_memory_operations(self, deterministic_environment, isolated_memory):
        """Test meta-memory storage and retrieval"""
        memory = isolated_memory
        
        # Store meta-memories (system changes)
        system_changes = [
            "Updated consciousness module to version 2.1",
            "Optimized memory retrieval algorithm",
            "Added new emotional processing capability",
            "Integrated advanced reasoning module",
            "Enhanced security protocols"
        ]
        
        for change in system_changes:
            memory_id = memory.store_memory(
                content=change,
                memory_type=MemoryType.META,
                emotional_tone=EmotionalTone.NEUTRAL,
                tags=["system_change", "upgrade", "meta"]
            )
            assert memory_id is not None
        
        # Retrieve system changes
        changes = memory.retrieve_memories(
            query="module",
            memory_types=[MemoryType.META],
            limit=10
        )
        
        assert len(changes) >= 1
        
        # Test system evolution tracking
        evolution_history = memory.get_system_evolution()
        assert isinstance(evolution_history, list)
        assert len(evolution_history) >= 0
    
    def test_memory_consistency_across_cycles(self, deterministic_environment, isolated_memory):
        """Test memory consistency across multiple read/write cycles"""
        memory = isolated_memory
        
        # Store test data
        test_data = {
            "content": "Consistency test memory",
            "memory_type": MemoryType.SHORT_TERM,
            "emotional_tone": EmotionalTone.NEUTRAL,
            "tags": ["consistency", "test"]
        }
        
        # Store memory
        memory_id = memory.store_memory(**test_data)
        
        # Retrieve multiple times
        retrievals = []
        for _ in range(10):
            retrieved = memory.retrieve_memories(
                query="consistency test",
                memory_types=[MemoryType.SHORT_TERM],
                limit=1
            )
            retrievals.append(retrieved)
        
        # All retrievals should be consistent
        assert all(len(r) == 1 for r in retrievals)
        
        # Content should be identical
        contents = [r[0]["content"] for r in retrievals]
        assert all(c == contents[0] for c in contents)
        
        # Memory ID should be consistent
        ids = [r[0]["id"] for r in retrievals]
        assert all(i == ids[0] for i in ids)
    
    def test_deterministic_memory_access(self, deterministic_environment, isolated_memory):
        """Test deterministic memory access patterns"""
        memory = isolated_memory
        
        # Store memories with specific patterns
        memories = [
            ("Pattern A memory 1", ["pattern_a", "test_1"]),
            ("Pattern A memory 2", ["pattern_a", "test_2"]),
            ("Pattern B memory 1", ["pattern_b", "test_1"]),
            ("Pattern B memory 2", ["pattern_b", "test_2"]),
            ("Pattern C memory 1", ["pattern_c", "test_1"])
        ]
        
        for content, tags in memories:
            memory.store_memory(
                content=content,
                memory_type=MemoryType.SHORT_TERM,
                emotional_tone=EmotionalTone.NEUTRAL,
                tags=tags
            )
        
        # Test deterministic retrieval
        queries = ["pattern_a", "pattern_b", "pattern_c", "test_1", "test_2"]
        
        for query in queries:
            # Retrieve multiple times
            results = []
            for _ in range(5):
                retrieved = memory.retrieve_memories(
                    query=query,
                    memory_types=[MemoryType.SHORT_TERM],
                    limit=10
                )
                results.append(retrieved)
            
            # Results should be deterministic
            assert all(len(r) == len(results[0]) for r in results)
            
            # Order should be consistent
            for i, result_set in enumerate(results[1:], 1):
                for j, mem in enumerate(result_set):
                    assert mem["id"] == results[0][j]["id"]
    
    def test_memory_emotional_processing(self, deterministic_environment, isolated_memory):
        """Test emotional tone processing in memory"""
        memory = isolated_memory
        
        # Store memories with different emotional tones
        emotional_memories = [
            ("Happy interaction with user", EmotionalTone.POSITIVE),
            ("Frustrating error occurred", EmotionalTone.NEGATIVE),
            ("Routine system operation", EmotionalTone.NEUTRAL),
            ("Exciting discovery made", EmotionalTone.POSITIVE),
            ("Concerning security issue", EmotionalTone.NEGATIVE)
        ]
        
        for content, tone in emotional_memories:
            memory_id = memory.store_memory(
                content=content,
                memory_type=MemoryType.SHORT_TERM,
                emotional_tone=tone,
                tags=["emotional_test"]
            )
            assert memory_id is not None
        
        # Retrieve by emotional tone
        positive_memories = memory.retrieve_memories_by_emotion(EmotionalTone.POSITIVE)
        negative_memories = memory.retrieve_memories_by_emotion(EmotionalTone.NEGATIVE)
        neutral_memories = memory.retrieve_memories_by_emotion(EmotionalTone.NEUTRAL)
        
        assert len(positive_memories) >= 2
        assert len(negative_memories) >= 2
        assert len(neutral_memories) >= 1
        
        # Check emotional consistency
        for mem in positive_memories:
            assert mem["emotional_tone"] == EmotionalTone.POSITIVE.value
        for mem in negative_memories:
            assert mem["emotional_tone"] == EmotionalTone.NEGATIVE.value
    
    def test_memory_vector_operations(self, deterministic_environment, isolated_memory):
        """Test vector-based memory operations"""
        memory = isolated_memory
        
        # Store semantically related memories
        related_memories = [
            "Python programming language",
            "JavaScript development",
            "Software engineering practices",
            "Machine learning algorithms",
            "Data science techniques"
        ]
        
        for content in related_memories:
            memory.store_memory(
                content=content,
                memory_type=MemoryType.SHORT_TERM,
                emotional_tone=EmotionalTone.NEUTRAL,
                tags=["programming", "technology"]
            )
        
        # Test semantic similarity search
        similar_memories = memory.find_similar_memories(
            "coding and programming",
            similarity_threshold=0.3,
            limit=5
        )
        
        assert len(similar_memories) >= 2
        
        # Check similarity scores
        for mem in similar_memories:
            assert "similarity_score" in mem
            assert 0.0 <= mem["similarity_score"] <= 1.0
    
    def test_memory_compression_and_consolidation(self, deterministic_environment, isolated_memory):
        """Test memory compression and consolidation"""
        memory = isolated_memory
        
        # Store many similar memories
        for i in range(50):
            memory.store_memory(
                content=f"Similar memory {i} about the same topic",
                memory_type=MemoryType.SHORT_TERM,
                emotional_tone=EmotionalTone.NEUTRAL,
                tags=["similar", "consolidation_test"]
            )
        
        # Check initial count
        initial_count = len(memory.retrieve_memories(
            query="similar memory",
            memory_types=[MemoryType.SHORT_TERM],
            limit=100
        ))
        
        assert initial_count >= 50
        
        # Perform consolidation
        memory.consolidate_memories()
        
        # Check if consolidation occurred
        final_count = len(memory.retrieve_memories(
            query="similar memory",
            memory_types=[MemoryType.SHORT_TERM, MemoryType.MEDIUM_TERM],
            limit=100
        ))
        
        # Should have some consolidation effect
        assert final_count <= initial_count
    
    def test_memory_persistence(self, deterministic_environment, temp_workspace):
        """Test memory persistence across system restarts"""
        storage_path = temp_workspace / "test_memory"
        
        # Create first memory instance
        memory1 = MemorySystem()
        memory1.storage_path = storage_path
        memory1._initialize_storage()
        
        # Store test memories
        test_memories = [
            "Persistent memory test 1",
            "Persistent memory test 2",
            "Persistent memory test 3"
        ]
        
        stored_ids = []
        for content in test_memories:
            memory_id = memory1.store_memory(
                content=content,
                memory_type=MemoryType.LONG_TERM,
                emotional_tone=EmotionalTone.NEUTRAL,
                tags=["persistence_test"]
            )
            stored_ids.append(memory_id)
        
        # Save state
        memory1.save_state()
        
        # Create second memory instance (simulating restart)
        memory2 = MemorySystem()
        memory2.storage_path = storage_path
        memory2._initialize_storage()
        memory2.load_state()
        
        # Retrieve memories from second instance
        retrieved = memory2.retrieve_memories(
            query="persistent memory test",
            memory_types=[MemoryType.LONG_TERM],
            limit=10
        )
        
        assert len(retrieved) >= 3
        
        # Check that IDs match
        retrieved_ids = [mem["id"] for mem in retrieved]
        for stored_id in stored_ids:
            assert stored_id in retrieved_ids
    
    def test_memory_performance(self, deterministic_environment, isolated_memory, test_timer):
        """Test memory performance requirements"""
        memory = isolated_memory
        
        # Test storage performance
        start_time = test_timer()
        
        for i in range(100):
            memory.store_memory(
                content=f"Performance test memory {i}",
                memory_type=MemoryType.SHORT_TERM,
                emotional_tone=EmotionalTone.NEUTRAL,
                tags=["performance", "test"]
            )
        
        storage_time = test_timer()
        
        # Test retrieval performance
        retrieval_start = test_timer()
        
        for i in range(100):
            memory.retrieve_memories(
                query=f"performance test {i % 10}",
                memory_types=[MemoryType.SHORT_TERM],
                limit=5
            )
        
        retrieval_time = test_timer() - retrieval_start
        
        # Performance requirements
        assert storage_time < 5.0  # 100 stores in under 5 seconds
        assert retrieval_time < 2.0  # 100 retrievals in under 2 seconds
        
        # Average operation times
        avg_store_time = storage_time / 100
        avg_retrieval_time = retrieval_time / 100
        
        assert avg_store_time < 0.05  # Under 50ms per store
        assert avg_retrieval_time < 0.02  # Under 20ms per retrieval
    
    def test_memory_error_handling(self, deterministic_environment, isolated_memory):
        """Test memory error handling and recovery"""
        memory = isolated_memory
        
        # Test with invalid inputs
        invalid_inputs = [
            {"content": None, "memory_type": MemoryType.SHORT_TERM},
            {"content": "", "memory_type": MemoryType.SHORT_TERM},
            {"content": "test", "memory_type": None},
            {"content": "test", "memory_type": "invalid_type"},
            {"content": "test", "emotional_tone": "invalid_tone"}
        ]
        
        for invalid_input in invalid_inputs:
            try:
                result = memory.store_memory(
                    content=invalid_input.get("content", "test"),
                    memory_type=invalid_input.get("memory_type", MemoryType.SHORT_TERM),
                    emotional_tone=invalid_input.get("emotional_tone", EmotionalTone.NEUTRAL),
                    tags=["error_test"]
                )
                # If no exception, result should be None or handled gracefully
                if result is not None:
                    assert isinstance(result, str)
            except Exception as e:
                # Exception should be handled gracefully
                assert memory.get_system_status()["status"] == "active"
    
    def test_global_memory_functions(self, deterministic_environment):
        """Test global memory functions"""
        # Test store_memory function
        memory_id = store_memory(
            "Global function test",
            EmotionalTone.NEUTRAL,
            ["global", "test"]
        )
        
        assert memory_id is not None
        assert isinstance(memory_id, str)
        
        # Test retrieve_memories function
        memories = retrieve_memories("global function", limit=5)
        
        assert isinstance(memories, list)
        assert len(memories) >= 0
        
        # If memories found, check structure
        if memories:
            for mem in memories:
                assert "id" in mem
                assert "content" in mem
                assert "timestamp" in mem