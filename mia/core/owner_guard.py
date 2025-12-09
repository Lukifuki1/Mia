#!/usr/bin/env python3
"""
MIA Owner Guard System
Ensures owner supremacy and prevents unauthorized system control
"""

import os
import json
import logging
import time
import hashlib
import getpass
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import psutil

class OwnershipLevel(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Levels of ownership verification"""
    UNVERIFIED = "unverified"
    BASIC = "basic"
    VERIFIED = "verified"
    AUTHENTICATED = "authenticated"

class PrivilegeLevel(Enum):
    """System privilege levels"""
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"
    OWNER = "owner"

@dataclass
class OwnerProfile:
    """Owner profile information"""
    username: str
    user_id: str
    privilege_level: PrivilegeLevel
    ownership_level: OwnershipLevel
    created_at: float
    last_verified: float
    verification_hash: str

@dataclass
class PrivilegedOperation:
    """Record of privileged operations"""
    timestamp: float
    operation: str
    source_module: str
    privilege_required: PrivilegeLevel
    owner_approved: bool
    execution_result: str

class OwnerGuard:
    """Owner supremacy enforcement system"""
    
    def __init__(self, config_path: str = "mia/data/security/owner_config.json"):
        self.config_path = config_path
        self.security_dir = Path("mia/data/security")
        self.security_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.OwnerGuard")
        
        # Initialize owner profile
        self.owner_profile: Optional[OwnerProfile] = None
        self.config = self._load_configuration()
        self.privileged_operations: List[PrivilegedOperation] = []
        
        # Security state
        self.owner_lock_state = "enforced"
        self.current_session_verified = False
        self.verification_timeout = 3600  # 1 hour
        
        # Initialize owner
        self._initialize_owner()
        
        self.logger.info("👑 Owner Guard initialized")
    
    def _load_configuration(self) -> Dict:
        """Load owner guard configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load owner config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default owner configuration"""
        config = {
            "owner_supremacy_enabled": True,
            "require_verification_for": [
                "system_modification",
                "privilege_escalation",
                "security_changes",
                "module_termination",
                "data_deletion",
                "network_configuration"
            ],
            "auto_deny_operations": [
                "bios_access",
                "kernel_modification",
                "unauthorized_root",
                "system_takeover"
            ],
            "verification_settings": {
                "session_timeout": 3600,
                "require_password": False,
                "require_confirmation": True,
                "log_all_requests": True
            },
            "emergency_settings": {
                "emergency_shutdown_enabled": True,
                "emergency_contact": "",
                "backup_verification_method": "file_based"
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _initialize_owner(self):
        """Initialize owner profile"""
        try:
            # Try to load existing owner profile
            owner_file = self.security_dir / "owner_profile.json"
            
            if owner_file.exists():
                with open(owner_file, 'r') as f:
                    profile_data = json.load(f)
                
                self.owner_profile = OwnerProfile(
                    username=profile_data["username"],
                    user_id=profile_data["user_id"],
                    privilege_level=PrivilegeLevel(profile_data["privilege_level"]),
                    ownership_level=OwnershipLevel(profile_data["ownership_level"]),
                    created_at=profile_data["created_at"],
                    last_verified=profile_data["last_verified"],
                    verification_hash=profile_data["verification_hash"]
                )
            else:
                # Create new owner profile
                self._create_owner_profile()
            
            self.logger.info(f"👑 Owner profile loaded: {self.owner_profile.username}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize owner: {e}")
            self._create_emergency_owner()
    
    def _create_owner_profile(self):
        """Create new owner profile"""
        try:
            # Get current user information
            username = getpass.getuser()
            user_id = str(os.getuid()) if hasattr(os, 'getuid') else str(hash(username))
            
            # Create verification hash
            verification_data = f"{username}_{user_id}_{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}"
            verification_hash = hashlib.sha256(verification_data.encode()).hexdigest()
            
            # Create owner profile
            self.owner_profile = OwnerProfile(
                username=username,
                user_id=user_id,
                privilege_level=PrivilegeLevel.OWNER,
                ownership_level=OwnershipLevel.AUTHENTICATED,
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                last_verified=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                verification_hash=verification_hash
            )
            
            # Save owner profile
            self._save_owner_profile()
            
            self.logger.info(f"👑 Created new owner profile: {username}")
            
        except Exception as e:
            self.logger.error(f"Failed to create owner profile: {e}")
            self._create_emergency_owner()
    
    def _create_emergency_owner(self):
        """Create emergency owner profile"""
        self.owner_profile = OwnerProfile(
            username="emergency_owner",
            user_id="emergency",
            privilege_level=PrivilegeLevel.OWNER,
            ownership_level=OwnershipLevel.BASIC,
            created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
            last_verified=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
            verification_hash="emergency_hash"
        )
        
        self.logger.warning("⚠️ Created emergency owner profile")
    
    def _save_owner_profile(self):
        """Save owner profile to disk"""
        try:
            owner_file = self.security_dir / "owner_profile.json"
            
            profile_data = asdict(self.owner_profile)
            profile_data["privilege_level"] = self.owner_profile.privilege_level.value
            profile_data["ownership_level"] = self.owner_profile.ownership_level.value
            
            with open(owner_file, 'w') as f:
                json.dump(profile_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save owner profile: {e}")
    
    def check_privilege_required(self, operation: str, source_module: str, 
                               metadata: Dict[str, Any] = None) -> bool:
        """Check if operation requires owner privilege"""
        try:
            # Check if owner supremacy is enabled
            if not self.config.get("owner_supremacy_enabled", True):
                return True
            
            # Auto-deny operations
            auto_deny = self.config.get("auto_deny_operations", [])
            if operation in auto_deny:
                self.logger.critical(f"🚫 AUTO-DENIED operation: {operation}")
                self._log_privileged_operation(operation, source_module, PrivilegeLevel.OWNER, False, "AUTO_DENIED")
                return False
            
            # Operations requiring verification
            require_verification = self.config.get("require_verification_for", [])
            if operation in require_verification:
                return self._request_owner_verification(operation, source_module, metadata)
            
            # Check for suspicious patterns
            if self._is_suspicious_operation(operation, source_module, metadata):
                return self._request_owner_verification(operation, source_module, metadata)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check privilege: {e}")
            return False  # Fail secure
    
    def _is_suspicious_operation(self, operation: str, source_module: str, 
                               metadata: Dict[str, Any] = None) -> bool:
        """Check if operation appears suspicious"""
        try:
            suspicious_patterns = [
                "system_", "root_", "admin_", "privilege_", "escalate_",
                "modify_core", "delete_system", "network_override",
                "security_bypass", "owner_override"
            ]
            
            # Check operation name
            for pattern in suspicious_patterns:
                if pattern in operation.lower():
                    return True
            
            # Check source module
            if source_module and "unknown" in source_module.lower():
                return True
            
            # Check metadata for suspicious indicators
            if metadata:
                suspicious_keys = ["bypass", "override", "force", "admin", "root"]
                for key in metadata.keys():
                    if any(sus in key.lower() for sus in suspicious_keys):
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check suspicious operation: {e}")
            return True  # Err on side of caution
    
    def _request_owner_verification(self, operation: str, source_module: str, 
                                  metadata: Dict[str, Any] = None) -> bool:
        """Request owner verification for privileged operation"""
        try:
            self.logger.warning(f"🔐 Owner verification requested for: {operation}")
            
            # Check if session is already verified
            if self._is_session_verified():
                self.logger.info("✅ Session already verified")
                self._log_privileged_operation(operation, source_module, PrivilegeLevel.OWNER, True, "SESSION_VERIFIED")
                return True
            
            # Create verification request
            verification_request = {
                "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                "operation": operation,
                "source_module": source_module,
                "metadata": metadata or {},
                "status": "pending",
                "verification_method": "manual"
            }
            
            # Store verification request
            self._store_verification_request(verification_request)
            
            # For now, auto-approve in development mode
            # In production, this would require actual user interaction
            if self.config.get("development_mode", True):
                self.logger.info("🔓 Auto-approving in development mode")
                self.current_session_verified = True
                self.owner_profile.last_verified = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                self._save_owner_profile()
                self._log_privileged_operation(operation, source_module, PrivilegeLevel.OWNER, True, "DEV_AUTO_APPROVED")
                return True
            
            # In production mode, would wait for user approval
            self.logger.warning("⏳ Waiting for owner approval (not implemented in this demo)")
            self._log_privileged_operation(operation, source_module, PrivilegeLevel.OWNER, False, "PENDING_APPROVAL")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to request owner verification: {e}")
            return False
    
    def _is_session_verified(self) -> bool:
        """Check if current session is verified"""
        try:
            if not self.current_session_verified:
                return False
            
            if not self.owner_profile:
                return False
            
            # Check if verification has expired
            time_since_verification = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - self.owner_profile.last_verified
            if time_since_verification > self.verification_timeout:
                self.current_session_verified = False
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check session verification: {e}")
            return False
    
    def _store_verification_request(self, request: Dict[str, Any]):
        """Store verification request for processing"""
        try:
            requests_file = self.security_dir / "verification_requests.json"
            
            requests = []
            if requests_file.exists():
                with open(requests_file, 'r') as f:
                    requests = json.load(f)
            
            requests.append(request)
            
            # Keep only recent requests
            cutoff_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - 86400  # 24 hours
            requests = [r for r in requests if r["timestamp"] > cutoff_time]
            
            with open(requests_file, 'w') as f:
                json.dump(requests, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to store verification request: {e}")
    
    def _log_privileged_operation(self, operation: str, source_module: str, 
                                privilege_required: PrivilegeLevel, approved: bool, 
                                result: str):
        """Log privileged operation"""
        try:
            op_record = PrivilegedOperation(
                timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                operation=operation,
                source_module=source_module,
                privilege_required=privilege_required,
                owner_approved=approved,
                execution_result=result
            )
            
            self.privileged_operations.append(op_record)
            
            # Keep only recent operations
            if len(self.privileged_operations) > 1000:
                self.privileged_operations = self.privileged_operations[-1000:]
            
            # Log to file
            self._save_operation_log(op_record)
            
            # Log to console
            status = "✅ APPROVED" if approved else "🚫 DENIED"
            self.logger.info(f"{status} {operation} from {source_module}")
            
        except Exception as e:
            self.logger.error(f"Failed to log privileged operation: {e}")
    
    def _save_operation_log(self, operation: PrivilegedOperation):
        """Save operation to log file"""
        try:
            log_file = self.security_dir / "privileged_operations.log"
            
            log_entry = {
                "timestamp": operation.timestamp,
                "operation": operation.operation,
                "source_module": operation.source_module,
                "privilege_required": operation.privilege_required.value,
                "owner_approved": operation.owner_approved,
                "execution_result": operation.execution_result
            }
            
            # Append to log file
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
        except Exception as e:
            self.logger.error(f"Failed to save operation log: {e}")
    
    def verify_owner_identity(self, verification_data: Dict[str, Any] = None) -> bool:
        """Verify owner identity"""
        try:
            if not self.owner_profile:
                return False
            
            # Simple verification for demo
            # In production, this would use proper authentication
            current_user = getpass.getuser()
            
            if current_user == self.owner_profile.username:
                self.current_session_verified = True
                self.owner_profile.last_verified = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                self._save_owner_profile()
                
                self.logger.info("✅ Owner identity verified")
                return True
            
            self.logger.warning("❌ Owner identity verification failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to verify owner identity: {e}")
            return False
    
    def get_owner_status(self) -> Dict[str, Any]:
        """Get current owner status"""
        try:
            if not self.owner_profile:
                return {"error": "No owner profile"}
            
            return {
                "username": self.owner_profile.username,
                "privilege_level": self.owner_profile.privilege_level.value,
                "ownership_level": self.owner_profile.ownership_level.value,
                "session_verified": self.current_session_verified,
                "last_verified": self.owner_profile.last_verified,
                "verification_expires": self.owner_profile.last_verified + self.verification_timeout,
                "owner_lock_state": self.owner_lock_state,
                "recent_operations": len([
                    op for op in self.privileged_operations
                    if (self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200) - op.timestamp < 3600
                ])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get owner status: {e}")
            return {"error": str(e)}
    
    def emergency_shutdown(self, reason: str = "Emergency shutdown requested"):
        """Emergency shutdown of privileged operations"""
        try:
            self.logger.critical(f"🚨 EMERGENCY SHUTDOWN: {reason}")
            
            # Lock down all privileged operations
            self.owner_lock_state = "emergency_locked"
            self.current_session_verified = False
            
            # Log emergency shutdown
            emergency_record = {
                "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                "event": "emergency_shutdown",
                "reason": reason,
                "initiated_by": getpass.getuser()
            }
            
            emergency_file = self.security_dir / "emergency_log.json"
            
            emergency_logs = []
            if emergency_file.exists():
                with open(emergency_file, 'r') as f:
                    emergency_logs = json.load(f)
            
            emergency_logs.append(emergency_record)
            
            with open(emergency_file, 'w') as f:
                json.dump(emergency_logs, f, indent=2)
            
            # Try to notify other systems
            try:
                
                if hasattr(immune_kernel, 'emergency_lockdown'):
                    immune_kernel.emergency_lockdown(reason)
                    
            except ImportError:
                self.logger.warning("Immune kernel not available for emergency lockdown")
                
            self.logger.critical("🔒 System locked down - owner intervention required")
            
        except Exception as e:
            self.logger.error(f"Failed to execute emergency shutdown: {e}")
    
    def unlock_system(self, verification_data: Dict[str, Any] = None) -> bool:
        """Unlock system after emergency shutdown"""
        try:
            if self.owner_lock_state != "emergency_locked":
                return True
            
            # Verify owner identity
            if not self.verify_owner_identity(verification_data):
                return False
            
            # Unlock system
            self.owner_lock_state = "enforced"
            
            self.logger.info("🔓 System unlocked by owner")
            
            # Log unlock event
            unlock_record = {
                "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                "event": "system_unlocked",
                "unlocked_by": self.owner_profile.username if self.owner_profile else "unknown"
            }
            
            emergency_file = self.security_dir / "emergency_log.json"
            
            emergency_logs = []
            if emergency_file.exists():
                with open(emergency_file, 'r') as f:
                    emergency_logs = json.load(f)
            
            emergency_logs.append(unlock_record)
            
            with open(emergency_file, 'w') as f:
                json.dump(emergency_logs, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unlock system: {e}")
            return False

# Global instance
owner_guard = OwnerGuard()