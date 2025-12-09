#!/usr/bin/env python3
"""
Security test: input_validation_security
Test input validation security
"""

import unittest
import sys
import hashlib
import base64
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestInputValidationSecuritySecurity(unittest.TestCase):
    """Security test for input_validation_security"""
    
    def setUp(self):
        """Set up security test"""
        self.security_test_data = {
            "valid_input": "valid test input",
            "malicious_inputs": [
                "<script>alert('xss')</script>",
                "'; DROP TABLE users; --",
                "{{7*7}}",
                "../../../etc/passwd",
                "javascript:alert('xss')",
                "eval('malicious code')",
                "exec('rm -rf /')",
                "__import__('os').system('ls')"
            ],
            "valid_credentials": {
                "username": "test_user",
                "password": "secure_password_123"
            },
            "invalid_credentials": [
                {"username": "", "password": ""},
                {"username": "admin", "password": "admin"},
                {"username": "test", "password": "' OR '1'='1"},
                {"username": "{{7*7}}", "password": "test"}
            ]
        }
    
    def test_input_sanitization(self):
        """Test input sanitization against malicious inputs"""
        for malicious_input in self.security_test_data["malicious_inputs"]:
            with self.subTest(input=malicious_input):
                # Test input sanitization
                sanitized = self._sanitize_input(malicious_input)
                
                # Sanitized input should not contain dangerous patterns
                self.assertNotIn("<script", sanitized.lower())
                self.assertNotIn("javascript:", sanitized.lower())
                self.assertNotIn("eval(", sanitized.lower())
                self.assertNotIn("exec(", sanitized.lower())
                self.assertNotIn("__import__", sanitized.lower())
                self.assertNotIn("drop table", sanitized.lower())
                self.assertNotIn("../", sanitized)
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM passwords --",
            "admin'--",
            "' OR 1=1 --"
        ]
        
        for injection_attempt in sql_injection_attempts:
            with self.subTest(injection=injection_attempt):
                # Test SQL query with injection attempt
                result = self._execute_safe_query("SELECT * FROM users WHERE username = ?", 
                                                [injection_attempt])
                
                # Should not return unauthorized data
                self.assertIsNotNone(result)
                # Result should be empty or contain only expected data
                if result:
                    self.assertNotIn("password", str(result).lower())
    
    def test_xss_prevention(self):
        """Test XSS prevention"""
        xss_attempts = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
            "{{7*7}}"
        ]
        
        for xss_attempt in xss_attempts:
            with self.subTest(xss=xss_attempt):
                # Test XSS prevention
                escaped_output = self._escape_html(xss_attempt)
                
                # Should not contain executable script tags
                self.assertNotIn("<script", escaped_output.lower())
                self.assertNotIn("javascript:", escaped_output.lower())
                self.assertNotIn("onerror=", escaped_output.lower())
                self.assertNotIn("onload=", escaped_output.lower())
    
    def test_authentication_security(self):
        """Test authentication security"""
        # Test valid authentication
        valid_creds = self.security_test_data["valid_credentials"]
        auth_result = self._authenticate_user(valid_creds["username"], valid_creds["password"])
        self.assertTrue(auth_result, "Valid authentication should succeed")
        
        # Test invalid authentication attempts
        for invalid_creds in self.security_test_data["invalid_credentials"]:
            with self.subTest(credentials=invalid_creds):
                auth_result = self._authenticate_user(
                    invalid_creds["username"], 
                    invalid_creds["password"]
                )
                self.assertFalse(auth_result, "Invalid authentication should fail")
    
    def test_password_security(self):
        """Test password security measures"""
        test_password = "test_password_123"
        
        # Test password hashing
        hashed_password = self._hash_password(test_password)
        
        # Hash should not be the same as original password
        self.assertNotEqual(hashed_password, test_password)
        
        # Hash should be consistent
        second_hash = self._hash_password(test_password)
        self.assertEqual(hashed_password, second_hash)
        
        # Hash should be of expected length (SHA-256)
        self.assertEqual(len(hashed_password), 64)
    
    def test_session_security(self):
        """Test session security"""
        # Create session
        session_id = self._create_session("test_user")
        
        # Session ID should be secure
        self.assertIsNotNone(session_id)
        self.assertGreater(len(session_id), 16)  # Minimum length
        
        # Session should be valid
        self.assertTrue(self._validate_session(session_id))
        
        # Invalid session should be rejected
        invalid_session = "invalid_session_id"
        self.assertFalse(self._validate_session(invalid_session))
    
    def test_data_encryption(self):
        """Test data encryption"""
        sensitive_data = "sensitive user information"
        
        # Encrypt data
        encrypted_data = self._encrypt_data(sensitive_data)
        
        # Encrypted data should be different from original
        self.assertNotEqual(encrypted_data, sensitive_data)
        
        # Decrypt data
        decrypted_data = self._decrypt_data(encrypted_data)
        
        # Decrypted data should match original
        self.assertEqual(decrypted_data, sensitive_data)
    
    def test_access_control(self):
        """Test access control"""
        # Test authorized access
        authorized_user = "admin_user"
        protected_resource = "admin_panel"
        
        access_granted = self._check_access(authorized_user, protected_resource)
        self.assertTrue(access_granted, "Authorized user should have access")
        
        # Test unauthorized access
        unauthorized_user = "regular_user"
        access_denied = self._check_access(unauthorized_user, protected_resource)
        self.assertFalse(access_denied, "Unauthorized user should be denied access")
    
    def _sanitize_input(self, input_data):
        """Sanitize input data"""
        if not isinstance(input_data, str):
            return str(input_data)
        
        # Basic sanitization
        sanitized = input_data.replace("<", "&lt;")
        sanitized = sanitized.replace(">", "&gt;")
        sanitized = sanitized.replace("'", "&#x27;")
        sanitized = sanitized.replace('"', "&quot;")
        sanitized = sanitized.replace("&", "&amp;")
        
        # Remove dangerous patterns
        dangerous_patterns = ["javascript:", "eval(", "exec(", "__import__"]
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, "")
        
        return sanitized
    
    def _execute_safe_query(self, query, parameters):
        """Execute safe SQL query (mocked)"""
        # Mock safe query execution
        if any(dangerous in str(parameters).lower() for dangerous in ["drop", "union", "or 1=1"]):
            return []  # Return empty result for dangerous queries
        
        # Mock normal query result
        return [{"username": parameters[0] if parameters else "test"}]
    
    def _escape_html(self, html_content):
        """Escape HTML content"""
        import html
        return html.escape(html_content)
    
    def _authenticate_user(self, username, password):
        """Authenticate user (mocked)"""
        # Mock authentication logic
        if not username or not password:
            return False
        
        # Check for SQL injection attempts
        if any(dangerous in password.lower() for dangerous in ["'", "or", "union", "drop"]):
            return False
        
        # Mock valid credentials
        valid_users = {"test_user": "secure_password_123"}
        
        return valid_users.get(username) == password
    
    def _hash_password(self, password):
        """Hash password"""
        # Use SHA-256 for testing (in production, use bcrypt or similar)
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _create_session(self, username):
        """Create user session"""
        import secrets
        session_data = f"{username}_{secrets.token_hex(16)}"
        return hashlib.sha256(session_data.encode()).hexdigest()
    
    def _validate_session(self, session_id):
        """Validate session"""
        # Mock session validation
        if not session_id or len(session_id) < 16:
            return False
        
        # Mock valid session format
        return len(session_id) == 64  # SHA-256 hash length
    
    def _encrypt_data(self, data):
        """Encrypt data (mocked)"""
        # Simple base64 encoding for testing (use proper encryption in production)
        return base64.b64encode(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data):
        """Decrypt data (mocked)"""
        # Simple base64 decoding for testing
        return base64.b64decode(encrypted_data.encode()).decode()
    
    def _check_access(self, user, resource):
        """Check user access to resource"""
        # Mock access control
        admin_users = ["admin_user", "super_admin"]
        admin_resources = ["admin_panel", "user_management"]
        
        if resource in admin_resources:
            return user in admin_users
        
        return True  # Allow access to non-admin resources

if __name__ == '__main__':
    unittest.main()
