#!/usr/bin/env python3
"""
MIA Enterprise Security System
Authentication, access control, data encryption, and secure configuration
"""

import os
import json
import logging
import asyncio
import time
import hashlib
import secrets
import jwt
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from datetime import datetime, timedelta
import base64

class UserRole(Enum):
    """User roles"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    API = "api"

class PermissionType(Enum):
    """Permission types"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"

class SecurityEventType(Enum):
    """Security event types"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    ACCESS_DENIED = "access_denied"
    PERMISSION_GRANTED = "permission_granted"
    CONFIG_CHANGE = "config_change"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

@dataclass
class User:
    """User account"""
    id: str
    username: str
    password_hash: str
    role: UserRole
    permissions: List[str]
    created_at: float
    last_login: Optional[float] = None
    login_attempts: int = 0
    locked_until: Optional[float] = None
    metadata: Dict[str, Any] = None

@dataclass
class Session:
    """User session"""
    id: str
    user_id: str
    token: str
    created_at: float
    expires_at: float
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    active: bool = True

@dataclass
class SecurityEvent:
    """Security event"""
    id: str
    event_type: SecurityEventType
    user_id: Optional[str]
    ip_address: Optional[str]
    timestamp: float
    details: Dict[str, Any]
    severity: str = "info"

class SecuritySystem:
    """Enterprise security system"""
    
    def __init__(self, data_dir: str = "mia_data"):
        self.data_dir = Path(data_dir)
        self.security_dir = self.data_dir / "security"
        self.users_file = self.security_dir / "users.json"
        self.sessions_file = self.security_dir / "sessions.json"
        self.events_file = self.security_dir / "security_events.json"
        
        # Create directories
        self.security_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.Enterprise.Security")
        
        # Security state
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.security_events: List[SecurityEvent] = []
        
        # Security configuration
        self.config = {
            "session_timeout": 3600,  # 1 hour
            "max_login_attempts": 5,
            "lockout_duration": 900,  # 15 minutes
            "password_min_length": 8,
            "require_strong_passwords": True,
            "jwt_secret": self._generate_jwt_secret(),
            "encryption_enabled": True,
            "audit_logging": True,
            "rate_limiting": True,
            "max_requests_per_minute": 60
        }
        
        # Rate limiting
        self.rate_limits: Dict[str, List[float]] = {}
        
        # Load security data
        self._load_security_data()
        
        # Create default admin user if none exists
        if not self.users:
            self._create_default_admin()
        
        # Start security maintenance tasks
        self.security_active = True
        self.security_thread = threading.Thread(target=self._security_maintenance_loop, daemon=True)
        self.security_thread.start()
        
        self.logger.info("🔐 Security system initialized")
    
    def _generate_jwt_secret(self) -> str:
        """Generate JWT secret key"""
        secret_file = self.security_dir / "jwt_secret.key"
        
        if secret_file.exists():
            try:
                with open(secret_file, 'r') as f:
                    return f.read().strip()
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to load JWT secret: {e}")
        
        # Generate new secret
        secret = secrets.token_urlsafe(32)
        
        try:
            with open(secret_file, 'w') as f:
                f.write(secret)
            os.chmod(secret_file, 0o600)  # Restrict permissions
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to save JWT secret: {e}")
        
        return secret
    
    def _load_security_data(self):
        """Load security data from files"""
        try:
            # Load users
            if self.users_file.exists():
                with open(self.users_file, 'r') as f:
                    users_data = json.load(f)
                    self.users = {}
                    for k, v in users_data.items():
                        v['role'] = UserRole(v['role'])  # Convert string back to enum
                        self.users[k] = User(**v)
                self.logger.info(f"👥 Loaded {len(self.users)} users")
            
            # Load sessions
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r') as f:
                    sessions_data = json.load(f)
                    self.sessions = {k: Session(**v) for k, v in sessions_data.items()}
                # Clean expired sessions
                self._cleanup_expired_sessions()
                self.logger.info(f"🎫 Loaded {len(self.sessions)} active sessions")
            
            # Load security events
            if self.events_file.exists():
                with open(self.events_file, 'r') as f:
                    events_data = json.load(f)
                    self.security_events = []
                    for event_data in events_data:
                        event_data['event_type'] = SecurityEventType(event_data['event_type'])  # Convert string back to enum
                        self.security_events.append(SecurityEvent(**event_data))
                self.logger.info(f"📋 Loaded {len(self.security_events)} security events")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to load security data: {e}")
    
    def _save_security_data(self):
        """Save security data to files"""
        try:
            # Save users
            with open(self.users_file, 'w') as f:
                users_data = {}
                for k, v in self.users.items():
                    user_dict = asdict(v)
                    user_dict['role'] = v.role.value  # Convert enum to string
                    users_data[k] = user_dict
                json.dump(users_data, f, indent=2)
            
            # Save sessions
            with open(self.sessions_file, 'w') as f:
                json.dump({k: asdict(v) for k, v in self.sessions.items()}, f, indent=2)
            
            # Save security events (last 1000 events)
            with open(self.events_file, 'w') as f:
                recent_events = self.security_events[-1000:] if len(self.security_events) > 1000 else self.security_events
                events_data = []
                for event in recent_events:
                    event_dict = asdict(event)
                    event_dict['event_type'] = event.event_type.value  # Convert enum to string
                    events_data.append(event_dict)
                json.dump(events_data, f, indent=2)
            
            # Set secure permissions
            for file_path in [self.users_file, self.sessions_file, self.events_file]:
                os.chmod(file_path, 0o600)
                
        except Exception as e:
            self.logger.error(f"❌ Failed to save security data: {e}")
    
    def _create_default_admin(self):
        """Create default admin user"""
        admin_password = secrets.token_urlsafe(12)
        
        admin_user = User(
            id="admin_001",
            username="admin",
            password_hash=self._hash_password(admin_password),
            role=UserRole.ADMIN,
            permissions=["*"],  # All permissions
            created_at=time.time(),
            metadata={"created_by": "system", "default_admin": True}
        )
        
        self.users[admin_user.id] = admin_user
        self._save_security_data()
        
        # Log admin credentials (in production, this should be done securely)
        self.logger.warning(f"🔑 Default admin created - Username: admin, Password: {admin_password}")
        
        # Log security event
        self._log_security_event(
            SecurityEventType.CONFIG_CHANGE,
            None,
            None,
            {"action": "default_admin_created", "username": "admin"}
        )
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_hex = password_hash.split(':')
            password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash_check.hex() == hash_hex
        except Exception:
            return False
    
    def _validate_password_strength(self, password: str) -> Tuple[bool, List[str]]:
        """Validate password strength"""
        errors = []
        
        if len(password) < self.config["password_min_length"]:
            errors.append(f"Password must be at least {self.config['password_min_length']} characters")
        
        if self.config["require_strong_passwords"]:
            if not any(c.isupper() for c in password):
                errors.append("Password must contain at least one uppercase letter")
            if not any(c.islower() for c in password):
                errors.append("Password must contain at least one lowercase letter")
            if not any(c.isdigit() for c in password):
                errors.append("Password must contain at least one digit")
            if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
                errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors
    
    def _check_rate_limit(self, identifier: str) -> bool:
        """Check rate limiting"""
        if not self.config["rate_limiting"]:
            return True
        
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        # Clean old requests
        if identifier in self.rate_limits:
            self.rate_limits[identifier] = [
                req_time for req_time in self.rate_limits[identifier] 
                if req_time > window_start
            ]
        else:
            self.rate_limits[identifier] = []
        
        # Check limit
        if len(self.rate_limits[identifier]) >= self.config["max_requests_per_minute"]:
            return False
        
        # Add current request
        self.rate_limits[identifier].append(current_time)
        return True
    
    def _log_security_event(self, event_type: SecurityEventType, user_id: Optional[str], 
                           ip_address: Optional[str], details: Dict[str, Any], severity: str = "info"):
        """Log security event"""
        event = SecurityEvent(
            id=f"sec_{int(time.time() * 1000)}",
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            timestamp=time.time(),
            details=details,
            severity=severity
        )
        
        self.security_events.append(event)
        
        # Log to system logger
        log_level = {
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }.get(severity, logging.INFO)
        
        self.logger.log(log_level, f"🔐 Security Event: {event_type.value} - {details}")
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if session.expires_at < current_time:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            self.logger.info(f"🗑️ Cleaned up {len(expired_sessions)} expired sessions")
    
    def _security_maintenance_loop(self):
        """Security maintenance tasks"""
        while self.security_active:
            try:
                # Cleanup expired sessions
                self._cleanup_expired_sessions()
                
                # Unlock locked accounts
                current_time = time.time()
                for user in self.users.values():
                    if user.locked_until and user.locked_until < current_time:
                        user.locked_until = None
                        user.login_attempts = 0
                        self.logger.info(f"🔓 Account unlocked: {user.username}")
                
                # Save security data periodically
                self._save_security_data()
                
                # Wait before next maintenance cycle
                time.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error(f"❌ Security maintenance error: {e}")
                time.sleep(60)
    
    async def authenticate_user(self, username: str, password: str, ip_address: str = None) -> Optional[str]:
        """Authenticate user and create session"""
        try:
            # Rate limiting
            if not self._check_rate_limit(ip_address or "unknown"):
                self._log_security_event(
                    SecurityEventType.SUSPICIOUS_ACTIVITY,
                    None,
                    ip_address,
                    {"reason": "rate_limit_exceeded", "username": username},
                    "warning"
                )
                return None
            
            # Find user
            user = None
            for u in self.users.values():
                if u.username == username:
                    user = u
                    break
            
            if not user:
                self._log_security_event(
                    SecurityEventType.LOGIN_FAILURE,
                    None,
                    ip_address,
                    {"reason": "user_not_found", "username": username},
                    "warning"
                )
                return None
            
            # Check if account is locked
            if user.locked_until and user.locked_until > time.time():
                self._log_security_event(
                    SecurityEventType.LOGIN_FAILURE,
                    user.id,
                    ip_address,
                    {"reason": "account_locked", "username": username},
                    "warning"
                )
                return None
            
            # Verify password
            if not self._verify_password(password, user.password_hash):
                user.login_attempts += 1
                
                # Lock account if too many attempts
                if user.login_attempts >= self.config["max_login_attempts"]:
                    user.locked_until = time.time() + self.config["lockout_duration"]
                    self.logger.warning(f"🔒 Account locked: {username}")
                
                self._log_security_event(
                    SecurityEventType.LOGIN_FAILURE,
                    user.id,
                    ip_address,
                    {"reason": "invalid_password", "username": username, "attempts": user.login_attempts},
                    "warning"
                )
                return None
            
            # Successful authentication
            user.login_attempts = 0
            user.last_login = time.time()
            
            # Create session
            session_id = secrets.token_urlsafe(32)
            session_token = self._create_jwt_token(user.id, session_id)
            
            session = Session(
                id=session_id,
                user_id=user.id,
                token=session_token,
                created_at=time.time(),
                expires_at=time.time() + self.config["session_timeout"],
                ip_address=ip_address,
                active=True
            )
            
            self.sessions[session_id] = session
            
            self._log_security_event(
                SecurityEventType.LOGIN_SUCCESS,
                user.id,
                ip_address,
                {"username": username, "session_id": session_id}
            )
            
            self.logger.info(f"✅ User authenticated: {username}")
            return session_token
            
        except Exception as e:
            self.logger.error(f"❌ Authentication error: {e}")
            return None
    
    def _create_jwt_token(self, user_id: str, session_id: str) -> str:
        """Create JWT token"""
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "iat": time.time(),
            "exp": time.time() + self.config["session_timeout"]
        }
        
        return jwt.encode(payload, self.config["jwt_secret"], algorithm="HS256")
    
    async def validate_token(self, token: str) -> Optional[User]:
        """Validate JWT token and return user"""
        try:
            # Decode token
            payload = jwt.decode(token, self.config["jwt_secret"], algorithms=["HS256"])
            
            user_id = payload.get("user_id")
            session_id = payload.get("session_id")
            
            # Check session
            session = self.sessions.get(session_id)
            if not session or not session.active or session.expires_at < time.time():
                return None
            
            # Get user
            user = self.users.get(user_id)
            if not user:
                return None
            
            # Update session expiry
            session.expires_at = time.time() + self.config["session_timeout"]
            
            return user
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("⚠️ Token expired")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("⚠️ Invalid token")
            return None
        except Exception as e:
            self.logger.error(f"❌ Token validation error: {e}")
            return None
    
    async def logout_user(self, token: str, ip_address: str = None) -> bool:
        """Logout user and invalidate session"""
        try:
            # Decode token to get session
            payload = jwt.decode(token, self.config["jwt_secret"], algorithms=["HS256"])
            session_id = payload.get("session_id")
            user_id = payload.get("user_id")
            
            # Invalidate session
            if session_id in self.sessions:
                self.sessions[session_id].active = False
                del self.sessions[session_id]
            
            self._log_security_event(
                SecurityEventType.LOGOUT,
                user_id,
                ip_address,
                {"session_id": session_id}
            )
            
            self.logger.info(f"👋 User logged out: {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Logout error: {e}")
            return False
    
    def check_permission(self, user: User, permission: str, resource: str = None) -> bool:
        """Check if user has permission"""
        try:
            # Admin has all permissions
            if user.role == UserRole.ADMIN or "*" in user.permissions:
                return True
            
            # Check specific permission
            if permission in user.permissions:
                return True
            
            # Check resource-specific permission
            if resource and f"{permission}:{resource}" in user.permissions:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Permission check error: {e}")
            return False
    
    def create_user(self, username: str, password: str, role: UserRole, permissions: List[str] = None) -> Optional[str]:
        """Create new user"""
        try:
            # Check if username exists
            for user in self.users.values():
                if user.username == username:
                    self.logger.error(f"❌ Username already exists: {username}")
                    return None
            
            # Validate password
            is_valid, errors = self._validate_password_strength(password)
            if not is_valid:
                self.logger.error(f"❌ Password validation failed: {'; '.join(errors)}")
                return None
            
            # Create user
            user_id = f"user_{int(time.time() * 1000)}"
            user = User(
                id=user_id,
                username=username,
                password_hash=self._hash_password(password),
                role=role,
                permissions=permissions or [],
                created_at=time.time()
            )
            
            self.users[user_id] = user
            self._save_security_data()
            
            self._log_security_event(
                SecurityEventType.CONFIG_CHANGE,
                None,
                None,
                {"action": "user_created", "username": username, "role": role.value}
            )
            
            self.logger.info(f"👤 User created: {username}")
            return user_id
            
        except Exception as e:
            self.logger.error(f"❌ User creation error: {e}")
            return None
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics"""
        current_time = time.time()
        
        # Count events by type (last 24 hours)
        recent_events = [e for e in self.security_events if e.timestamp > current_time - 86400]
        event_counts = {}
        for event_type in SecurityEventType:
            event_counts[event_type.value] = len([e for e in recent_events if e.event_type == event_type])
        
        return {
            "total_users": len(self.users),
            "active_sessions": len(self.sessions),
            "security_events_24h": len(recent_events),
            "event_counts": event_counts,
            "locked_accounts": len([u for u in self.users.values() if u.locked_until and u.locked_until > current_time]),
            "config": {
                "session_timeout": self.config["session_timeout"],
                "max_login_attempts": self.config["max_login_attempts"],
                "rate_limiting": self.config["rate_limiting"]
            }
        }
    
    def shutdown(self):
        """Shutdown security system"""
        self.security_active = False
        if self.security_thread.is_alive():
            self.security_thread.join(timeout=5)
        self._save_security_data()
        self.logger.info("🔐 Security system shutdown")

# Global security system instance
security_system = SecuritySystem()