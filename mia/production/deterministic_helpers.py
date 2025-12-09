#!/usr/bin/env python3
"""
🔧 MIA Enterprise AGI - Deterministic Helpers
=============================================

Provides deterministic utilities for consistent behavior.
"""

import hashlib
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

class DeterministicHelpers:
    """Helpers for deterministic behavior"""
    
    def __init__(self):
        self.build_config = {
            "build_timestamp": "2025-12-09T14:00:00Z",
            "build_version": "1.0.0",
            "build_epoch": 1733752800
        }
    
    def get_deterministic_timestamp(self) -> str:
        """Get deterministic timestamp"""
        return self.build_config["build_timestamp"]
    
    def get_deterministic_epoch(self) -> float:
        """Get deterministic epoch"""
        return float(self.build_config["build_epoch"])
    
    def generate_deterministic_id(self, seed: str = "default") -> str:
        """Generate deterministic ID"""
        hasher = hashlib.sha256()
        hasher.update(f"{seed}_{self.build_config['build_version']}".encode('utf-8'))
        return hasher.hexdigest()[:32]
    
    def get_seeded_random(self, seed: int = 42):
        """Get seeded random generator"""
        import random
        deterministic_helpers.get_seeded_random().seed(seed)
        return random
    
    def normalize_data(self, data: Any) -> str:
        """Normalize data for consistent processing"""
        if isinstance(data, dict):
            return json.dumps(data, sort_keys=True, separators=(',', ':'))
        elif isinstance(data, (list, tuple)):
            return json.dumps(sorted(data) if all(isinstance(x, (str, int, float)) for x in data) else list(data))
        else:
            return str(data)
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate deterministic content hash"""
        hasher = hashlib.sha256()
        hasher.update(content.encode('utf-8'))
        return hasher.hexdigest()

# Global instance
deterministic_helpers = DeterministicHelpers()
