#!/usr/bin/env python3
"""
🔒 MIA Enterprise AGI - Advanced Security System
===============================================

Enterprise-grade security framework with:
- Multi-factor authentication
- Role-based access control (RBAC)
- Audit logging and compliance
- Threat detection and response
- Data encryption and protection
- Security incident management
"""

import os
import sys
import json
import time
import logging
import hashlib
import secrets
import jwt
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from datetime import datetime, timedelta
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class SecurityLevel(Enum):
    """Security clearance levels"""
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"
    SECURITY_ADMIN = "security_admin"
    SYSTEM_ADMIN = "system_admin"

class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditEventType(Enum):
    """Types of audit events"""
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_ACCESS = "data_access"
    SYSTEM_CHANGE = "system_change"
    SECURITY_VIOLATION = "security_violation"

@dataclass
class User:
    """User account information"""
    id: str
    username: str
    email: str
    password_hash: str
    security_level: SecurityLevel
    mfa_enabled: bool
    mfa_secret: Optional[str]
    created_at: float
    last_login: Optional[float]
    failed_login_attempts: int
    account_locked: bool
    session_token: Optional[str]

@dataclass
class AuditEvent:
    """Security audit event"""
    id: str
    timestamp: float
    event_type: AuditEventType
    user_id: str
    source_ip: str
    user_agent: str
    resource: str
    action: str
    result: str
    details: Dict[str, Any]

@dataclass
class SecurityThreat:
    """Detected security threat"""
    id: str
    timestamp: float
    threat_level: ThreatLevel
    threat_type: str
    source: str
    target: str
    description: str
    indicators: List[str]
    mitigated: bool
    mitigation_actions: List[str]

class MIAEnterpriseSecurity:
    """Enterprise security management system"""
    
    def __init__(self, config_path: str = "mia_data/config/security.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = self._setup_logging()
        
        # Database for security data
        self.db_path = Path("mia_data/security/security.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Encryption key for sensitive data
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # JWT secret for session tokens
        self.jwt_secret = self._get_or_create_jwt_secret()
        
        # Security state
        self.active_sessions = {}
        self.failed_login_attempts = {}
        self.threat_detection_rules = self._load_threat_rules()
        
        # Rate limiting
        self.rate_limits = {}
        
        self.logger.info("🔒 MIA Enterprise Security initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load security configuration"""
        if Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load security config: {e}")
        
        # Default security configuration
        default_config = {
            "authentication": {
                "password_min_length": 12,
                "password_require_special": True,
                "password_require_numbers": True,
                "password_require_uppercase": True,
                "mfa_required": True,
                "session_timeout_minutes": 60,
                "max_failed_attempts": 5,
                "lockout_duration_minutes": 30
            },
            "authorization": {
                "rbac_enabled": True,
                "default_role": "user",
                "admin_approval_required": True
            },
            "audit": {
                "log_all_events": True,
                "retention_days": 2555,  # 7 years for compliance
                "real_time_monitoring": True,
                "alert_on_violations": True
            },
            "encryption": {
                "data_at_rest": True,
                "data_in_transit": True,
                "key_rotation_days": 90
            },
            "threat_detection": {
                "enabled": True,
                "brute_force_detection": True,
                "anomaly_detection": True,
                "ip_reputation_check": True,
                "behavioral_analysis": True
            },
            "compliance": {
                "gdpr_enabled": True,
                "soc2_enabled": True,
                "iso27001_enabled": True,
                "data_classification": True
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """Setup security logging"""
        log_dir = Path("mia_data/logs/security")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logger = logging.getLogger("MIA.Security")
        if not logger.handlers:
            # Security log handler
            security_handler = logging.FileHandler(log_dir / "security.log")
            security_formatter = logging.Formatter(
                '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
            )
            security_handler.setFormatter(security_formatter)
            
            # Audit log handler
            audit_handler = logging.FileHandler(log_dir / "audit.log")
            audit_formatter = logging.Formatter(
                '%(asctime)s - AUDIT - %(message)s'
            )
            audit_handler.setFormatter(audit_formatter)
            
            logger.addHandler(security_handler)
            logger.addHandler(audit_handler)
            logger.setLevel(logging.INFO)
        
        return logger
    
    def _init_database(self):
        """Initialize security database"""
        with sqlite3.connect(self.db_path) as conn:
            # Users table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    security_level TEXT NOT NULL,
                    mfa_enabled BOOLEAN DEFAULT FALSE,
                    mfa_secret TEXT,
                    created_at REAL NOT NULL,
                    last_login REAL,
                    failed_login_attempts INTEGER DEFAULT 0,
                    account_locked BOOLEAN DEFAULT FALSE,
                    session_token TEXT
                )
            ''')
            
            # Audit events table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_events (
                    id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    event_type TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    source_ip TEXT NOT NULL,
                    user_agent TEXT,
                    resource TEXT NOT NULL,
                    action TEXT NOT NULL,
                    result TEXT NOT NULL,
                    details TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Security threats table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS security_threats (
                    id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    threat_level TEXT NOT NULL,
                    threat_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    target TEXT NOT NULL,
                    description TEXT NOT NULL,
                    indicators TEXT,
                    mitigated BOOLEAN DEFAULT FALSE,
                    mitigation_actions TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Sessions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    source_ip TEXT NOT NULL,
                    user_agent TEXT,
                    active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Create indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_events(user_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_threats_timestamp ON security_threats(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)')
            
            conn.commit()
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        key_file = Path("mia_data/security/encryption.key")
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
            return key
    
    def _get_or_create_jwt_secret(self) -> str:
        """Get or create JWT secret"""
        secret_file = Path("mia_data/security/jwt.secret")
        
        if secret_file.exists():
            with open(secret_file, 'r') as f:
                return f.read().strip()
        else:
            # Generate new secret
            secret = secrets.token_urlsafe(64)
            secret_file.parent.mkdir(parents=True, exist_ok=True)
            with open(secret_file, 'w') as f:
                f.write(secret)
            
            # Set restrictive permissions
            os.chmod(secret_file, 0o600)
            return secret
    
    def _load_threat_rules(self) -> List[Dict[str, Any]]:
        """Load threat detection rules"""
        return [
            {
                "name": "brute_force_login",
                "description": "Multiple failed login attempts",
                "threshold": 5,
                "window_minutes": 15,
                "threat_level": ThreatLevel.HIGH
            },
            {
                "name": "privilege_escalation",
                "description": "Unauthorized privilege escalation attempt",
                "threshold": 1,
                "window_minutes": 1,
                "threat_level": ThreatLevel.CRITICAL
            },
            {
                "name": "suspicious_ip",
                "description": "Access from suspicious IP address",
                "threshold": 1,
                "window_minutes": 1,
                "threat_level": ThreatLevel.MEDIUM
            },
            {
                "name": "data_exfiltration",
                "description": "Large data access patterns",
                "threshold": 100,
                "window_minutes": 60,
                "threat_level": ThreatLevel.HIGH
            }
        ]
    
    def create_user(self, username: str, email: str, password: str,
                   security_level: SecurityLevel = SecurityLevel.USER) -> str:
        """Create new user account"""
        try:
            # Validate password strength
            if not self._validate_password_strength(password):
                raise ValueError("Password does not meet security requirements")
            
            # Check if user already exists
            if self._user_exists(username, email):
                raise ValueError("User already exists")
            
            # Generate user ID
            user_id = secrets.token_urlsafe(16)
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create user
            user = User(
                id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                security_level=security_level,
                mfa_enabled=self.config["authentication"]["mfa_required"],
                mfa_secret=secrets.token_urlsafe(32) if self.config["authentication"]["mfa_required"] else None,
                created_at=time.time(),
                last_login=None,
                failed_login_attempts=0,
                account_locked=False,
                session_token=None
            )
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO users 
                    (id, username, email, password_hash, security_level, mfa_enabled, 
                     mfa_secret, created_at, last_login, failed_login_attempts, 
                     account_locked, session_token)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user.id, user.username, user.email, user.password_hash,
                    user.security_level.value, user.mfa_enabled, user.mfa_secret,
                    user.created_at, user.last_login, user.failed_login_attempts,
                    user.account_locked, user.session_token
                ))
                conn.commit()
            
            # Log audit event
            self._log_audit_event(
                event_type=AuditEventType.SYSTEM_CHANGE,
                user_id="system",
                source_ip="127.0.0.1",
                user_agent="system",
                resource="user_management",
                action="create_user",
                result="success",
                details={"new_user_id": user_id, "username": username, "security_level": security_level.value}
            )
            
            self.logger.info(f"User created: {username} ({user_id})")
            return user_id
            
        except Exception as e:
            self.logger.error(f"Failed to create user {username}: {e}")
            raise
    
    def authenticate_user(self, username: str, password: str, source_ip: str,
                         user_agent: str = "", mfa_code: str = None) -> Optional[str]:
        """Authenticate user and return session token"""
        try:
            # Check rate limiting
            if self._is_rate_limited(source_ip):
                self._log_audit_event(
                    event_type=AuditEventType.ACCESS_DENIED,
                    user_id="unknown",
                    source_ip=source_ip,
                    user_agent=user_agent,
                    resource="authentication",
                    action="login",
                    result="rate_limited",
                    details={"username": username}
                )
                raise ValueError("Rate limit exceeded")
            
            # Get user
            user = self._get_user_by_username(username)
            if not user:
                self._record_failed_attempt(source_ip)
                self._log_audit_event(
                    event_type=AuditEventType.ACCESS_DENIED,
                    user_id="unknown",
                    source_ip=source_ip,
                    user_agent=user_agent,
                    resource="authentication",
                    action="login",
                    result="user_not_found",
                    details={"username": username}
                )
                raise ValueError("Invalid credentials")
            
            # Check if account is locked
            if user.account_locked:
                self._log_audit_event(
                    event_type=AuditEventType.ACCESS_DENIED,
                    user_id=user.id,
                    source_ip=source_ip,
                    user_agent=user_agent,
                    resource="authentication",
                    action="login",
                    result="account_locked",
                    details={"username": username}
                )
                raise ValueError("Account is locked")
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                self._record_failed_login(user.id)
                self._record_failed_attempt(source_ip)
                self._log_audit_event(
                    event_type=AuditEventType.ACCESS_DENIED,
                    user_id=user.id,
                    source_ip=source_ip,
                    user_agent=user_agent,
                    resource="authentication",
                    action="login",
                    result="invalid_password",
                    details={"username": username}
                )
                raise ValueError("Invalid credentials")
            
            # Verify MFA if enabled
            if user.mfa_enabled:
                if not mfa_code or not self._verify_mfa_code(user.mfa_secret, mfa_code):
                    self._log_audit_event(
                        event_type=AuditEventType.ACCESS_DENIED,
                        user_id=user.id,
                        source_ip=source_ip,
                        user_agent=user_agent,
                        resource="authentication",
                        action="login",
                        result="invalid_mfa",
                        details={"username": username}
                    )
                    raise ValueError("Invalid MFA code")
            
            # Create session token
            session_token = self._create_session_token(user.id, source_ip, user_agent)
            
            # Update user login info
            self._update_user_login(user.id, session_token)
            
            # Clear failed attempts
            self._clear_failed_attempts(source_ip)
            
            # Log successful login
            self._log_audit_event(
                event_type=AuditEventType.LOGIN,
                user_id=user.id,
                source_ip=source_ip,
                user_agent=user_agent,
                resource="authentication",
                action="login",
                result="success",
                details={"username": username, "mfa_used": user.mfa_enabled}
            )
            
            self.logger.info(f"User authenticated: {username} from {source_ip}")
            return session_token
            
        except Exception as e:
            self.logger.error(f"Authentication failed for {username}: {e}")
            raise
    
    def validate_session(self, session_token: str, source_ip: str) -> Optional[User]:
        """Validate session token and return user"""
        try:
            # Decode JWT token
            payload = jwt.decode(session_token, self.jwt_secret, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                return None
            
            # Check session in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT user_id, expires_at, source_ip, active
                    FROM sessions 
                    WHERE token = ? AND user_id = ?
                ''', (session_token, user_id))
                
                session_data = cursor.fetchone()
                if not session_data:
                    return None
                
                session_user_id, expires_at, session_ip, active = session_data
                
                # Check if session is active and not expired
                if not active or time.time() > expires_at:
                    return None
                
                # Optional: Check IP consistency
                if self.config.get("strict_ip_validation", False) and session_ip != source_ip:
                    self.logger.warning(f"IP mismatch for session {session_token}: {session_ip} vs {source_ip}")
                    return None
            
            # Get user
            user = self._get_user_by_id(user_id)
            return user
            
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            self.logger.error(f"Session validation error: {e}")
            return None
    
    def logout_user(self, session_token: str, source_ip: str, user_agent: str = ""):
        """Logout user and invalidate session"""
        try:
            # Get user from session
            user = self.validate_session(session_token, source_ip)
            if not user:
                return
            
            # Invalidate session
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE sessions 
                    SET active = FALSE 
                    WHERE token = ?
                ''', (session_token,))
                conn.commit()
            
            # Clear session token from user
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE users 
                    SET session_token = NULL 
                    WHERE id = ?
                ''', (user.id,))
                conn.commit()
            
            # Log logout
            self._log_audit_event(
                event_type=AuditEventType.LOGOUT,
                user_id=user.id,
                source_ip=source_ip,
                user_agent=user_agent,
                resource="authentication",
                action="logout",
                result="success",
                details={"username": user.username}
            )
            
            self.logger.info(f"User logged out: {user.username}")
            
        except Exception as e:
            self.logger.error(f"Logout error: {e}")
    
    def check_permission(self, user: User, resource: str, action: str) -> bool:
        """Check if user has permission for resource/action"""
        try:
            # Define permission matrix
            permissions = {
                SecurityLevel.GUEST: {
                    "public": ["read"],
                    "health": ["read"]
                },
                SecurityLevel.USER: {
                    "public": ["read"],
                    "health": ["read"],
                    "user_data": ["read", "write"],
                    "projects": ["read", "write", "create"]
                },
                SecurityLevel.ADMIN: {
                    "public": ["read"],
                    "health": ["read"],
                    "user_data": ["read", "write"],
                    "projects": ["read", "write", "create", "delete"],
                    "system": ["read", "write"],
                    "users": ["read", "write", "create"]
                },
                SecurityLevel.SECURITY_ADMIN: {
                    "public": ["read"],
                    "health": ["read"],
                    "user_data": ["read", "write"],
                    "projects": ["read", "write", "create", "delete"],
                    "system": ["read", "write"],
                    "users": ["read", "write", "create", "delete"],
                    "security": ["read", "write", "create", "delete"],
                    "audit": ["read"]
                },
                SecurityLevel.SYSTEM_ADMIN: {
                    "*": ["*"]  # Full access
                }
            }
            
            user_permissions = permissions.get(user.security_level, {})
            
            # Check for full access
            if "*" in user_permissions and "*" in user_permissions["*"]:
                return True
            
            # Check specific resource permissions
            resource_permissions = user_permissions.get(resource, [])
            
            # Check for wildcard action permission
            if "*" in resource_permissions:
                return True
            
            # Check specific action permission
            return action in resource_permissions
            
        except Exception as e:
            self.logger.error(f"Permission check error: {e}")
            return False
    
    def detect_threats(self):
        """Run threat detection algorithms"""
        try:
            current_time = time.time()
            
            for rule in self.threat_detection_rules:
                self._check_threat_rule(rule, current_time)
                
        except Exception as e:
            self.logger.error(f"Threat detection error: {e}")
    
    def _check_threat_rule(self, rule: Dict[str, Any], current_time: float):
        """Check specific threat detection rule"""
        try:
            rule_name = rule["name"]
            threshold = rule["threshold"]
            window_minutes = rule["window_minutes"]
            threat_level = rule["threat_level"]
            
            window_start = current_time - (window_minutes * 60)
            
            if rule_name == "brute_force_login":
                # Check for brute force login attempts
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute('''
                        SELECT source_ip, COUNT(*) as attempts
                        FROM audit_events 
                        WHERE event_type = ? AND result = ? AND timestamp > ?
                        GROUP BY source_ip
                        HAVING attempts >= ?
                    ''', (AuditEventType.ACCESS_DENIED.value, "invalid_password", window_start, threshold))
                    
                    for source_ip, attempts in cursor.fetchall():
                        self._create_security_threat(
                            threat_level=threat_level,
                            threat_type="brute_force_attack",
                            source=source_ip,
                            target="authentication_system",
                            description=f"Brute force attack detected from {source_ip}: {attempts} failed login attempts",
                            indicators=[f"failed_logins:{attempts}", f"source_ip:{source_ip}"]
                        )
            
            elif rule_name == "privilege_escalation":
                # Check for privilege escalation attempts
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute('''
                        SELECT user_id, COUNT(*) as attempts
                        FROM audit_events 
                        WHERE event_type = ? AND result = ? AND timestamp > ?
                        GROUP BY user_id
                        HAVING attempts >= ?
                    ''', (AuditEventType.PRIVILEGE_ESCALATION.value, "denied", window_start, threshold))
                    
                    for user_id, attempts in cursor.fetchall():
                        user = self._get_user_by_id(user_id)
                        username = user.username if user else "unknown"
                        
                        self._create_security_threat(
                            threat_level=threat_level,
                            threat_type="privilege_escalation",
                            source=user_id,
                            target="system_privileges",
                            description=f"Privilege escalation attempts by user {username}: {attempts} attempts",
                            indicators=[f"escalation_attempts:{attempts}", f"user_id:{user_id}"]
                        )
            
        except Exception as e:
            self.logger.error(f"Threat rule check error for {rule['name']}: {e}")
    
    def _create_security_threat(self, threat_level: ThreatLevel, threat_type: str,
                              source: str, target: str, description: str,
                              indicators: List[str]):
        """Create and log security threat"""
        try:
            threat_id = secrets.token_urlsafe(16)
            timestamp = time.time()
            
            threat = SecurityThreat(
                id=threat_id,
                timestamp=timestamp,
                threat_level=threat_level,
                threat_type=threat_type,
                source=source,
                target=target,
                description=description,
                indicators=indicators,
                mitigated=False,
                mitigation_actions=[]
            )
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO security_threats 
                    (id, timestamp, threat_level, threat_type, source, target, 
                     description, indicators, mitigated, mitigation_actions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    threat.id, threat.timestamp, threat.threat_level.value,
                    threat.threat_type, threat.source, threat.target,
                    threat.description, json.dumps(threat.indicators),
                    threat.mitigated, json.dumps(threat.mitigation_actions)
                ))
                conn.commit()
            
            # Log threat
            self.logger.critical(f"SECURITY THREAT DETECTED: {threat.description}")
            
            # Auto-mitigation for high/critical threats
            if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                self._auto_mitigate_threat(threat)
            
        except Exception as e:
            self.logger.error(f"Failed to create security threat: {e}")
    
    def _auto_mitigate_threat(self, threat: SecurityThreat):
        """Automatically mitigate high-priority threats"""
        try:
            mitigation_actions = []
            
            if threat.threat_type == "brute_force_attack":
                # Block IP address
                self._block_ip_address(threat.source)
                mitigation_actions.append(f"blocked_ip:{threat.source}")
            
            elif threat.threat_type == "privilege_escalation":
                # Lock user account
                self._lock_user_account(threat.source)
                mitigation_actions.append(f"locked_account:{threat.source}")
            
            # Update threat record
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE security_threats 
                    SET mitigated = TRUE, mitigation_actions = ?
                    WHERE id = ?
                ''', (json.dumps(mitigation_actions), threat.id))
                conn.commit()
            
            self.logger.info(f"Auto-mitigated threat {threat.id}: {mitigation_actions}")
            
        except Exception as e:
            self.logger.error(f"Auto-mitigation failed for threat {threat.id}: {e}")
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password meets security requirements"""
        config = self.config["authentication"]
        
        if len(password) < config["password_min_length"]:
            return False
        
        if config["password_require_uppercase"] and not any(c.isupper() for c in password):
            return False
        
        if config["password_require_numbers"] and not any(c.isdigit() for c in password):
            return False
        
        if config["password_require_special"] and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False
        
        return True
    
    def _user_exists(self, username: str, email: str) -> bool:
        """Check if user already exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT COUNT(*) FROM users 
                WHERE username = ? OR email = ?
            ''', (username, email))
            
            return cursor.fetchone()[0] > 0
    
    def _get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, username, email, password_hash, security_level, 
                       mfa_enabled, mfa_secret, created_at, last_login, 
                       failed_login_attempts, account_locked, session_token
                FROM users WHERE username = ?
            ''', (username,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return User(
                id=row[0],
                username=row[1],
                email=row[2],
                password_hash=row[3],
                security_level=SecurityLevel(row[4]),
                mfa_enabled=row[5],
                mfa_secret=row[6],
                created_at=row[7],
                last_login=row[8],
                failed_login_attempts=row[9],
                account_locked=row[10],
                session_token=row[11]
            )
    
    def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, username, email, password_hash, security_level, 
                       mfa_enabled, mfa_secret, created_at, last_login, 
                       failed_login_attempts, account_locked, session_token
                FROM users WHERE id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return User(
                id=row[0],
                username=row[1],
                email=row[2],
                password_hash=row[3],
                security_level=SecurityLevel(row[4]),
                mfa_enabled=row[5],
                mfa_secret=row[6],
                created_at=row[7],
                last_login=row[8],
                failed_login_attempts=row[9],
                account_locked=row[10],
                session_token=row[11]
            )
    
    def _create_session_token(self, user_id: str, source_ip: str, user_agent: str) -> str:
        """Create JWT session token"""
        expires_at = time.time() + (self.config["authentication"]["session_timeout_minutes"] * 60)
        
        payload = {
            'user_id': user_id,
            'source_ip': source_ip,
            'iat': time.time(),
            'exp': expires_at
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        
        # Store session in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO sessions (token, user_id, created_at, expires_at, source_ip, user_agent, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (token, user_id, time.time(), expires_at, source_ip, user_agent, True))
            conn.commit()
        
        return token
    
    def _verify_mfa_code(self, secret: str, code: str) -> bool:
        """Verify MFA TOTP code"""
        try:
            import pyotp
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=1)
        except ImportError:
            # Fallback: simple time-based verification
            import hmac
            current_time = int(time.time() // 30)
            expected_code = hmac.new(
                secret.encode(),
                str(current_time).encode(),
                hashlib.sha1
            ).hexdigest()[:6]
            return code == expected_code
    
    def _log_audit_event(self, event_type: AuditEventType, user_id: str,
                        source_ip: str, user_agent: str, resource: str,
                        action: str, result: str, details: Dict[str, Any] = None):
        """Log audit event"""
        try:
            event_id = secrets.token_urlsafe(16)
            timestamp = time.time()
            
            event = AuditEvent(
                id=event_id,
                timestamp=timestamp,
                event_type=event_type,
                user_id=user_id,
                source_ip=source_ip,
                user_agent=user_agent,
                resource=resource,
                action=action,
                result=result,
                details=details or {}
            )
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO audit_events 
                    (id, timestamp, event_type, user_id, source_ip, user_agent, 
                     resource, action, result, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.id, event.timestamp, event.event_type.value,
                    event.user_id, event.source_ip, event.user_agent,
                    event.resource, event.action, event.result,
                    json.dumps(event.details)
                ))
                conn.commit()
            
            # Log to audit file
            audit_msg = f"EVENT:{event_type.value} USER:{user_id} IP:{source_ip} RESOURCE:{resource} ACTION:{action} RESULT:{result}"
            self.logger.info(audit_msg)
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
    
    def _is_rate_limited(self, source_ip: str) -> bool:
        """Check if IP is rate limited"""
        current_time = time.time()
        
        if source_ip not in self.rate_limits:
            self.rate_limits[source_ip] = []
        
        # Clean old attempts
        self.rate_limits[source_ip] = [
            t for t in self.rate_limits[source_ip] 
            if current_time - t < 300  # 5 minutes
        ]
        
        # Check rate limit (max 10 attempts per 5 minutes)
        return len(self.rate_limits[source_ip]) >= 10
    
    def _record_failed_attempt(self, source_ip: str):
        """Record failed attempt for rate limiting"""
        current_time = time.time()
        
        if source_ip not in self.rate_limits:
            self.rate_limits[source_ip] = []
        
        self.rate_limits[source_ip].append(current_time)
    
    def _record_failed_login(self, user_id: str):
        """Record failed login attempt"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE users 
                SET failed_login_attempts = failed_login_attempts + 1
                WHERE id = ?
            ''', (user_id,))
            
            # Check if account should be locked
            cursor = conn.execute('''
                SELECT failed_login_attempts FROM users WHERE id = ?
            ''', (user_id,))
            
            attempts = cursor.fetchone()[0]
            max_attempts = self.config["authentication"]["max_failed_attempts"]
            
            if attempts >= max_attempts:
                conn.execute('''
                    UPDATE users 
                    SET account_locked = TRUE 
                    WHERE id = ?
                ''', (user_id,))
            
            conn.commit()
    
    def _clear_failed_attempts(self, source_ip: str):
        """Clear failed attempts for IP"""
        if source_ip in self.rate_limits:
            del self.rate_limits[source_ip]
    
    def _update_user_login(self, user_id: str, session_token: str):
        """Update user login information"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE users 
                SET last_login = ?, failed_login_attempts = 0, 
                    account_locked = FALSE, session_token = ?
                WHERE id = ?
            ''', (time.time(), session_token, user_id))
            conn.commit()
    
    def _block_ip_address(self, ip_address: str):
        """Block IP address by adding to blocked IPs list"""
        # Add to blocked IPs list for application-level blocking
        if not hasattr(self, 'blocked_ips'):
            self.blocked_ips = set()
        
        self.blocked_ips.add(ip_address)
        self.logger.warning(f"IP address blocked: {ip_address}")
        
        # Store in database for persistence
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO blocked_ips (ip_address, blocked_at, reason)
                VALUES (?, ?, ?)
            ''', (ip_address, time.time(), "Security violation"))
    
    def _lock_user_account(self, user_id: str):
        """Lock user account"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE users 
                SET account_locked = TRUE 
                WHERE id = ?
            ''', (user_id,))
            conn.commit()
        
        self.logger.warning(f"User account locked: {user_id}")


# Global security instance
enterprise_security = MIAEnterpriseSecurity()


def main():
    """Test security system"""
    security = MIAEnterpriseSecurity()
    
    # Create test admin user
    try:
        admin_id = security.create_user(
            username="admin",
            email="admin@company.com",
            password="SecurePassword123!",
            security_level=SecurityLevel.SYSTEM_ADMIN
        )
        print(f"Created admin user: {admin_id}")
        
        # Test authentication
        token = security.authenticate_user(
            username="admin",
            password="SecurePassword123!",
            source_ip="127.0.0.1",
            user_agent="test"
        )
        print(f"Authentication successful: {token}")
        
        # Test session validation
        user = security.validate_session(token, "127.0.0.1")
        if user:
            print(f"Session valid for user: {user.username}")
        
        # Test threat detection
        security.detect_threats()
        print("Threat detection completed")
        
    except Exception as e:
        print(f"Security test error: {e}")


if __name__ == "__main__":
    main()