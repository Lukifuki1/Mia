#!/usr/bin/env python3
"""
Deterministic Memory Manager
"""

import json
import hashlib
from typing import Dict, Any, List
from collections import OrderedDict

class DeterministicMemoryManager:
    """Deterministični memory manager"""
    
    def __init__(self, deterministic_seed: int = 42):
        self.deterministic_seed = deterministic_seed
        self.memory_store = OrderedDict()  # Deterministični vrstni red
        self.access_counter = 0
        
    def store_memory(self, key: str, data: Any) -> str:
        """Shrani spomin deterministično"""
        # Deterministični ključ
        deterministic_key = self._generate_deterministic_key(key)
        
        # Deterministična serializacija
        serialized_data = self._serialize_deterministic(data)
        
        # Shrani v deterministični vrstni red
        self.memory_store[deterministic_key] = {
            "data": serialized_data,
            "access_count": 0,
            "storage_order": len(self.memory_store),
            "hash": self._hash_data(serialized_data)
        }
        
        return deterministic_key
    
    def retrieve_memory(self, key: str) -> Any:
        """Pridobi spomin deterministično"""
        deterministic_key = self._generate_deterministic_key(key)
        
        if deterministic_key in self.memory_store:
            memory_item = self.memory_store[deterministic_key]
            memory_item["access_count"] += 1
            return self._deserialize_deterministic(memory_item["data"])
        
        return None
    
    def _generate_deterministic_key(self, key: str) -> str:
        """Generiraj deterministični ključ"""
        key_data = f"{key}_{self.deterministic_seed}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
    
    def _serialize_deterministic(self, data: Any) -> str:
        """Deterministična serializacija"""
        if isinstance(data, dict):
            # Sortiraj ključe za konsistenco
            sorted_data = {k: data[k] for k in sorted(data.keys())}
            return json.dumps(sorted_data, sort_keys=True, separators=(',', ':'))
        else:
            return json.dumps(data, sort_keys=True, separators=(',', ':'))
    
    def _deserialize_deterministic(self, serialized: str) -> Any:
        """Deterministična deserializacija"""
        return json.loads(serialized)
    
    def _hash_data(self, data: str) -> str:
        """Hash podatkov"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def get_memory_state_hash(self) -> str:
        """Pridobi hash celotnega memory state"""
        state_data = {
            "memory_count": len(self.memory_store),
            "memory_hashes": [item["hash"] for item in self.memory_store.values()],
            "seed": self.deterministic_seed
        }
        
        state_str = json.dumps(state_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(state_str.encode()).hexdigest()
