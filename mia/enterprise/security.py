#!/usr/bin/env python3
"""
MIA Enterprise Security Module
Provides enterprise-grade security features
"""

import os
import json
import hashlib
import logging
import secrets
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class SecurityLevel(Enum):
    """Security levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuthenticationMethod(Enum):
    """Authentication methods"""
    PASSWORD = "password"
    TOKEN = "token"
    BIOMETRIC = "biometric"
    MULTI_FACTOR = "multi_factor"

@dataclass
class SecurityConfig:
    """Security configuration"""
    encryption_enabled: bool = True
    audit_logging: bool = True
    session_timeout: int = 3600
    max_login_attempts: int = 3
    password_complexity: bool = True
    two_factor_auth: bool = False

class EnterpriseSecurityManager:
    """Enterprise security manager"""
    
    def __init__(self, config_path: str = "mia/data/security/config.json"):
        self.config_path = Path(config_path)
        self.logger = self._setup_logging()
        self.config = self._load_config()
        self.encryption_key = self._generate_encryption_key()
        self.active_sessions = {}
        self.failed_attempts = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Setup security logging"""
        logger = logging.getLogger("MIA.Security")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _load_config(self) -> SecurityConfig:
        """Load security configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                return SecurityConfig(**data)
            except Exception as e:
                self.logger.warning(f"Failed to load security config: {e}")
        
        return SecurityConfig()
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key"""
        password = b"mia_enterprise_key"
        salt = b"mia_salt_2025"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not self.config.encryption_enabled:
            return data
            
        try:
            f = Fernet(self.encryption_key)
            encrypted_data = f.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not self.config.encryption_enabled:
            return encrypted_data
            
        try:
            f = Fernet(self.encryption_key)
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = f.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            return encrypted_data
    
    def authenticate_user(self, username: str, password: str, 
                         method: AuthenticationMethod = AuthenticationMethod.PASSWORD) -> Optional[str]:
        """Authenticate user and return session token"""
        
        # Check failed attempts
        if username in self.failed_attempts:
            if self.failed_attempts[username] >= self.config.max_login_attempts:
                self.logger.warning(f"Account locked for user: {username}")
                return None
        
        # Validate credentials (in production, check against secure database)
        if self._validate_credentials(username, password, method):
            # Generate session token
            token = self._generate_session_token(username)
            self.active_sessions[token] = {
                "username": username,
                "created_at": time.time(),
                "last_activity": time.time()
            }
            
            # Reset failed attempts
            if username in self.failed_attempts:
                del self.failed_attempts[username]
            
            self.logger.info(f"User authenticated: {username}")
            return token
        else:
            # Track failed attempt
            self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
            self.logger.warning(f"Authentication failed for user: {username}")
            return None
    
    def _validate_credentials(self, username: str, password: str, 
                            method: AuthenticationMethod) -> bool:
        """Validate user credentials"""
        # In production, this would check against secure database
        # For now, use basic validation
        if method == AuthenticationMethod.PASSWORD:
            # Basic password validation
            if len(password) < 8:
                return False
            if self.config.password_complexity:
                if not any(c.isupper() for c in password):
                    return False
                if not any(c.islower() for c in password):
                    return False
                if not any(c.isdigit() for c in password):
                    return False
        
        # Demo credentials for testing
        demo_users = {
            "admin": "AdminPass123",
            "user": "UserPass123",
            "enterprise": "EnterprisePass123"
        }
        
        return demo_users.get(username) == password
    
    def _generate_session_token(self, username: str) -> str:
        """Generate secure session token"""
        payload = {
            "username": username,
            "created_at": time.time(),
            "expires_at": time.time() + self.config.session_timeout
        }
        
        # Use JWT for token generation
        secret_key = hashlib.sha256(self.encryption_key).hexdigest()
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        return token
    
    def validate_session(self, token: str) -> Optional[str]:
        """Validate session token"""
        if token not in self.active_sessions:
            return None
        
        session = self.active_sessions[token]
        current_time = time.time()
        
        # Check session timeout
        if current_time - session["created_at"] > self.config.session_timeout:
            del self.active_sessions[token]
            return None
        
        # Update last activity
        session["last_activity"] = current_time
        return session["username"]
    
    def logout_user(self, token: str) -> bool:
        """Logout user and invalidate session"""
        if token in self.active_sessions:
            username = self.active_sessions[token]["username"]
            del self.active_sessions[token]
            self.logger.info(f"User logged out: {username}")
            return True
        return False
    
    def audit_log(self, action: str, user: str, details: Dict[str, Any] = None):
        """Log security events for audit"""
        if not self.config.audit_logging:
            return
        
        log_entry = {
            "timestamp": time.time(),
            "action": action,
            "user": user,
            "details": details or {}
        }
        
        # In production, this would write to secure audit log
        self.logger.info(f"AUDIT: {json.dumps(log_entry)}")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        return {
            "active_sessions": len(self.active_sessions),
            "failed_attempts": len(self.failed_attempts),
            "encryption_enabled": self.config.encryption_enabled,
            "audit_logging": self.config.audit_logging,
            "session_timeout": self.config.session_timeout
        }

# Global security manager instance
security_manager = EnterpriseSecurityManager()

def authenticate(username: str, password: str) -> Optional[str]:
    """Authenticate user"""
    return security_manager.authenticate_user(username, password)

def validate_session(token: str) -> Optional[str]:
    """Validate session token"""
    return security_manager.validate_session(token)

def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data"""
    return security_manager.encrypt_data(data)

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    return security_manager.decrypt_data(encrypted_data)