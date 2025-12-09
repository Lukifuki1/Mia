#!/usr/bin/env python3
"""
MIA Immune System Kernel
Central orchestrator for system security and integrity
"""

import os
import json
import logging
import time
import hashlib
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import asyncio

class ThreatLevel(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Threat severity levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ActionType(Enum):
    """Types of actions that can be taken"""
    ALLOW = "allow"
    SANDBOX = "sandbox"
    QUARANTINE = "quarantine"
    BLOCK = "block"
    TERMINATE = "terminate"

@dataclass
class SecurityEvent:
    """Security event record"""
    timestamp: float
    event_type: str
    threat_level: ThreatLevel
    source_module: str
    description: str
    action_taken: ActionType
    metadata: Dict[str, Any]

@dataclass
class SystemState:
    """Current system security state"""
    overall_threat_level: ThreatLevel
    active_threats: int
    quarantined_items: int
    blocked_operations: int
    last_scan_time: float
    system_integrity_score: float

class ImmuneKernel:
    """Central immune system orchestrator"""
    
    def __init__(self, config_path: str = "mia/data/immune/config.json"):
        self.config_path = config_path
        self.immune_dir = Path("mia/data/immune")
        self.immune_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.ImmuneKernel")
        
        # Initialize components
        self.config = self._load_configuration()
        self.security_events: List[SecurityEvent] = []
        self.system_state = SystemState(
            overall_threat_level=ThreatLevel.NONE,
            active_threats=0,
            quarantined_items=0,
            blocked_operations=0,
            last_scan_time=0,
            system_integrity_score=1.0
        )
        
        # Runtime state
        self.running = False
        self.scan_interval = self.config.get("scan_interval", 60)  # seconds
        
        self.logger.info("🛡️ Immune Kernel initialized")
    
    def _load_configuration(self) -> Dict:
        """Load immune system configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load immune config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default immune system configuration"""
        config = {
            "enabled": True,
            "scan_interval": 60,
            "threat_thresholds": {
                "integrity_warning": 0.8,
                "integrity_critical": 0.6,
                "behavior_anomaly_threshold": 0.7,
                "cognitive_drift_threshold": 0.5
            },
            "protection_levels": {
                "filesystem_protection": True,
                "memory_protection": True,
                "network_protection": True,
                "cognitive_protection": True,
                "training_protection": True
            },
            "response_settings": {
                "auto_quarantine": True,
                "auto_block_threats": True,
                "require_human_approval": ["terminate", "major_changes"],
                "log_all_events": True
            },
            "critical_paths": [
                "mia/core/immune/",
                "mia/core/owner_guard.py",
                "mia/core/root_policy.py",
                "mia/core/consciousness/",
                "mia/core/memory/"
            ]
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def check_operation_allowed(self, operation: str, source_module: str, 
                              metadata: Dict[str, Any] = None) -> bool:
        """Check if an operation is allowed by the immune system"""
        try:
            # Quick security check for operations
            
            # Check for high-risk operations
            high_risk_operations = [
                "file_delete", "system_modify", "network_access", 
                "memory_write", "process_spawn"
            ]
            
            if operation in high_risk_operations:
                # Additional checks for high-risk operations
                if self.system_state.overall_threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                    self.logger.warning(f"🚫 High-risk operation blocked during threat condition: {operation}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check operation permission: {e}")
            return True  # Fail open for safety
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current immune system status"""
        try:
            return {
                "enabled": self.config.get("enabled", True),
                "running": self.running,
                "system_state": asdict(self.system_state),
                "recent_events": len([
                    e for e in self.security_events
                    if (self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200) - e.timestamp < 3600
                ])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {"error": str(e)}

# Global instance
immune_kernel = ImmuneKernel()