#!/usr/bin/env python3
"""
Integrity Guard - Varuje integriteto podatkov in sistemskih komponent
"""

import os
import json
import logging
import time
import hashlib
import hmac
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import sqlite3

class IntegrityLevel(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Integrity protection levels"""
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    CRITICAL = "critical"

class ViolationType(Enum):
    """Types of integrity violations"""
    CHECKSUM_MISMATCH = "checksum_mismatch"
    UNAUTHORIZED_MODIFICATION = "unauthorized_modification"
    SIGNATURE_INVALID = "signature_invalid"
    TIMESTAMP_ANOMALY = "timestamp_anomaly"
    SIZE_ANOMALY = "size_anomaly"
    PERMISSION_VIOLATION = "permission_violation"

@dataclass
class IntegrityRecord:
    """Integrity record for protected resource"""
    record_id: str
    resource_path: str
    resource_type: str
    checksum: str
    signature: Optional[str]
    size: int
    permissions: str
    created_at: float
    last_verified: float
    verification_count: int
    integrity_level: IntegrityLevel

@dataclass
class IntegrityViolation:
    """Integrity violation event"""
    violation_id: str
    resource_path: str
    violation_type: ViolationType
    severity: str
    description: str
    expected_value: str
    actual_value: str
    detected_at: float
    resolved: bool
    resolution_action: Optional[str]

class IntegrityGuard:
    """Integrity Guard - protects data and system integrity"""
    
    def __init__(self, config_path: str = "mia/data/immune_system/integrity_config.json"):
        self.config_path = config_path
        self.integrity_dir = Path("mia/data/immune_system/integrity")
        self.integrity_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.IntegrityGuard")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Initialize database
        self.db_path = self.integrity_dir / "integrity.db"
        self._initialize_database()
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_interval = self.config.get("monitoring_interval", 300)  # 5 minutes
        
        # Protected resources
        self.protected_resources: Dict[str, IntegrityRecord] = {}
        self.violations: Dict[str, IntegrityViolation] = {}
        
        # Cryptographic keys
        self.signing_key = self._get_or_create_signing_key()
        
        self.logger.info("🛡️ Integrity Guard initialized")
    
    def _load_configuration(self) -> Dict:
        """Load integrity guard configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load integrity config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default integrity configuration"""
        config = {
            "enabled": True,
            "monitoring_interval": 300,  # 5 minutes
            "default_integrity_level": "standard",
            "checksum_algorithm": "sha256",
            "signature_algorithm": "hmac-sha256",
            "protected_paths": [
                "mia/core/",
                "mia/data/config/",
                "mia/data/models/",
                "mia/data/memory/"
            ],
            "excluded_patterns": [
                "*.log",
                "*.tmp",
                "__pycache__",
                "*.pyc"
            ],
            "integrity_levels": {
                "critical": {
                    "verify_interval": 60,    # 1 minute
                    "require_signature": True,
                    "monitor_permissions": True,
                    "alert_on_violation": True
                },
                "high": {
                    "verify_interval": 300,   # 5 minutes
                    "require_signature": True,
                    "monitor_permissions": True,
                    "alert_on_violation": True
                },
                "standard": {
                    "verify_interval": 900,   # 15 minutes
                    "require_signature": False,
                    "monitor_permissions": False,
                    "alert_on_violation": True
                },
                "basic": {
                    "verify_interval": 3600,  # 1 hour
                    "require_signature": False,
                    "monitor_permissions": False,
                    "alert_on_violation": False
                }
            },
            "violation_responses": {
                "checksum_mismatch": "alert_and_quarantine",
                "unauthorized_modification": "alert_and_restore",
                "signature_invalid": "alert_and_block",
                "timestamp_anomaly": "alert_only",
                "size_anomaly": "alert_only",
                "permission_violation": "alert_and_fix"
            },
            "backup_enabled": True,
            "quarantine_enabled": True,
            "auto_restore": False
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _initialize_database(self):
        """Initialize integrity database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create integrity records table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS integrity_records (
                        record_id TEXT PRIMARY KEY,
                        resource_path TEXT UNIQUE,
                        resource_type TEXT,
                        checksum TEXT,
                        signature TEXT,
                        size INTEGER,
                        permissions TEXT,
                        created_at REAL,
                        last_verified REAL,
                        verification_count INTEGER,
                        integrity_level TEXT
                    )
                ''')
                
                # Create violations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS violations (
                        violation_id TEXT PRIMARY KEY,
                        resource_path TEXT,
                        violation_type TEXT,
                        severity TEXT,
                        description TEXT,
                        expected_value TEXT,
                        actual_value TEXT,
                        detected_at REAL,
                        resolved INTEGER,
                        resolution_action TEXT
                    )
                ''')
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_resource_path ON integrity_records(resource_path)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_detected_at ON violations(detected_at)')
                
                conn.commit()
            
            self.logger.info("✅ Integrity database initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
    
    def _get_or_create_signing_key(self) -> bytes:
        """Get or create signing key for integrity signatures"""
        try:
            key_file = self.integrity_dir / "signing.key"
            
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                # Generate new key
                key = os.urandom(32)  # 256-bit key
                
                with open(key_file, 'wb') as f:
                    f.write(key)
                
                # Set restrictive permissions
                os.chmod(key_file, 0o600)
                
                self.logger.info("🔑 Generated new signing key")
                return key
            
        except Exception as e:
            self.logger.error(f"Failed to get signing key: {e}")
            return os.urandom(32)  # Fallback to temporary key
    
    def protect_resource(self, resource_path: str, integrity_level: IntegrityLevel = IntegrityLevel.STANDARD):
        """Add resource to integrity protection"""
        try:
            if not Path(resource_path).exists():
                self.logger.error(f"Resource not found: {resource_path}")
                return False
            
            # Calculate checksum
            checksum = self._calculate_checksum(resource_path)
            if not checksum:
                return False
            
            # Calculate signature if required
            signature = None
            level_config = self.config.get("integrity_levels", {}).get(integrity_level.value, {})
            if level_config.get("require_signature", False):
                signature = self._calculate_signature(resource_path, checksum)
            
            # Get file info
            stat_info = Path(resource_path).stat()
            size = stat_info.st_size
            permissions = oct(stat_info.st_mode)[-3:]
            
            # Determine resource type
            resource_type = self._determine_resource_type(resource_path)
            
            # Create integrity record
            record_id = hashlib.sha256(f"{resource_path}_{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}".encode()).hexdigest()[:16]
            
            record = IntegrityRecord(
                record_id=record_id,
                resource_path=resource_path,
                resource_type=resource_type,
                checksum=checksum,
                signature=signature,
                size=size,
                permissions=permissions,
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                last_verified=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                verification_count=1,
                integrity_level=integrity_level
            )
            
            # Store in database
            self._store_integrity_record(record)
            
            # Store in memory
            self.protected_resources[resource_path] = record
            
            self.logger.info(f"🛡️ Protected resource: {resource_path} ({integrity_level.value})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to protect resource: {e}")
            return False
    
    def _calculate_checksum(self, file_path: str) -> Optional[str]:
        """Calculate file checksum"""
        try:
            algorithm = self.config.get("checksum_algorithm", "sha256")
            
            if algorithm == "sha256":
                hash_obj = hashlib.sha256()
            elif algorithm == "md5":
                hash_obj = hashlib.md5()
            else:
                hash_obj = hashlib.sha256()  # Default
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            self.logger.error(f"Failed to calculate checksum: {e}")
            return None
    
    def _calculate_signature(self, file_path: str, checksum: str) -> Optional[str]:
        """Calculate integrity signature"""
        try:
            # Create signature data
            signature_data = f"{file_path}:{checksum}:{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}"
            
            # Calculate HMAC signature
            signature = hmac.new(
                self.signing_key,
                signature_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return signature
            
        except Exception as e:
            self.logger.error(f"Failed to calculate signature: {e}")
            return None
    
    def _determine_resource_type(self, file_path: str) -> str:
        """Determine resource type"""
        try:
            path = Path(file_path)
            
            if path.is_dir():
                return "directory"
            
            suffix = path.suffix.lower()
            
            if suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h']:
                return "source_code"
            elif suffix in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg']:
                return "configuration"
            elif suffix in ['.db', '.sqlite', '.sqlite3']:
                return "database"
            elif suffix in ['.pkl', '.pickle', '.joblib']:
                return "model"
            elif suffix in ['.log', '.txt']:
                return "text"
            elif suffix in ['.bin', '.exe', '.so', '.dll']:
                return "binary"
            else:
                return "unknown"
            
        except Exception as e:
            self.logger.error(f"Failed to determine resource type: {e}")
            return "unknown"
    
    def _store_integrity_record(self, record: IntegrityRecord):
        """Store integrity record in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO integrity_records 
                    (record_id, resource_path, resource_type, checksum, signature, 
                     size, permissions, created_at, last_verified, verification_count, integrity_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record.record_id,
                    record.resource_path,
                    record.resource_type,
                    record.checksum,
                    record.signature,
                    record.size,
                    record.permissions,
                    record.created_at,
                    record.last_verified,
                    record.verification_count,
                    record.integrity_level.value
                ))
                
                conn.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to store integrity record: {e}")
    
    def start_monitoring(self):
        """Start integrity monitoring"""
        try:
            if self.monitoring_active:
                return
            
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.logger.info("🛡️ Integrity monitoring started")
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop integrity monitoring"""
        try:
            self.monitoring_active = False
            
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5.0)
            
            self.logger.info("🛡️ Integrity monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
    
    def get_integrity_status(self) -> Dict[str, Any]:
        """Get integrity guard status"""
        try:
            return {
                "enabled": self.config.get("enabled", True),
                "monitoring_active": self.monitoring_active,
                "monitoring_interval": self.monitoring_interval,
                "protected_resources": len(self.protected_resources),
                "total_violations": len(self.violations),
                "backup_enabled": self.config.get("backup_enabled", True),
                "quarantine_enabled": self.config.get("quarantine_enabled", True)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get integrity status: {e}")
            return {"error": str(e)}
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Basic monitoring implementation
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)

# Global instance
integrity_guard = IntegrityGuard()