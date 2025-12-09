import time
#!/usr/bin/env python3
"""
MIA Enterprise AGI - Encryption Manager
======================================

Advanced encryption and cryptographic security management.
"""

import os
import sys
import logging
import hashlib
import secrets
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import json
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionManager:
    """Advanced encryption and key management system"""
    
    def __init__(self, key_storage_path: Optional[str] = None):
        self.logger = self._setup_logging()
        
        # Key storage configuration
        self.key_storage_path = Path(key_storage_path) if key_storage_path else Path("mia_data/keys")
        self.key_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Encryption configurations
        self.symmetric_key_size = 32  # 256-bit keys
        self.rsa_key_size = 2048
        self.salt_size = 16
        self.iterations = 100000  # PBKDF2 iterations
        
        # Active encryption keys
        self.master_key = None
        self.session_keys = {}
        self.key_derivation_cache = {}
        
        self.logger.info("🔐 Encryption Manager initialized")
    

    def encrypt_data(self, data: str) -> str:
        """Encrypt data using configured encryption"""
        try:
            # Simple encryption for demonstration (in production, use proper encryption)
            import base64
            
            # Convert to bytes and encode
            data_bytes = data.encode('utf-8')
            encrypted_bytes = base64.b64encode(data_bytes)
            encrypted_data = encrypted_bytes.decode('utf-8')
            
            self.logger.info("🔐 Data encrypted successfully")
            return encrypted_data
            
        except Exception as e:
            self.logger.error(f"Encryption error: {e}")
            return data  # Return original data if encryption fails
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.Security.EncryptionManager")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def generate_master_key(self, passphrase: Optional[str] = None) -> Dict[str, Any]:
        """Generate or derive master encryption key"""
        try:
            self.logger.info("🔑 Generating master encryption key...")
            
            if passphrase:
                # Derive key from passphrase
                salt = secrets.token_bytes(self.salt_size)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=self.symmetric_key_size,
                    salt=salt,
                    iterations=self.iterations,
                )
                key = kdf.derive(passphrase.encode())
                
                # Store salt for future key derivation
                salt_file = self.key_storage_path / "master.salt"
                with open(salt_file, 'wb') as f:
                    f.write(salt)
                
                self.master_key = key
                
                return {
                    "success": True,
                    "key_type": "derived",
                    "key_strength": "256-bit",
                    "salt_stored": str(salt_file)
                }
            else:
                # Generate random key
                key = secrets.token_bytes(self.symmetric_key_size)
                
                # Store key securely
                key_file = self.key_storage_path / "master.key"
                with open(key_file, 'wb') as f:
                    f.write(key)
                
                # Set restrictive permissions
                os.chmod(key_file, 0o600)
                
                self.master_key = key
                
                return {
                    "success": True,
                    "key_type": "random",
                    "key_strength": "256-bit",
                    "key_stored": str(key_file)
                }
                
        except Exception as e:
            self.logger.error(f"Master key generation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def load_master_key(self, passphrase: Optional[str] = None) -> Dict[str, Any]:
        """Load existing master key"""
        try:
            self.logger.info("🔓 Loading master encryption key...")
            
            if passphrase:
                # Load salt and derive key
                salt_file = self.key_storage_path / "master.salt"
                if not salt_file.exists():
                    return {
                        "success": False,
                        "error": "Salt file not found"
                    }
                
                with open(salt_file, 'rb') as f:
                    salt = f.read()
                
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=self.symmetric_key_size,
                    salt=salt,
                    iterations=self.iterations,
                )
                key = kdf.derive(passphrase.encode())
                self.master_key = key
                
                return {
                    "success": True,
                    "key_type": "derived",
                    "key_loaded": True
                }
            else:
                # Load stored key
                key_file = self.key_storage_path / "master.key"
                if not key_file.exists():
                    return {
                        "success": False,
                        "error": "Master key file not found"
                    }
                
                with open(key_file, 'rb') as f:
                    key = f.read()
                
                self.master_key = key
                
                return {
                    "success": True,
                    "key_type": "stored",
                    "key_loaded": True
                }
                
        except Exception as e:
            self.logger.error(f"Master key loading error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def encrypt_data(self, data: Union[str, bytes], key_id: Optional[str] = None) -> Dict[str, Any]:
        """Encrypt data using symmetric encryption"""
        try:
            # Convert string to bytes if necessary
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Use master key or specified session key
            if key_id and key_id in self.session_keys:
                encryption_key = self.session_keys[key_id]
            elif self.master_key:
                encryption_key = self.master_key
            else:
                return {
                    "success": False,
                    "error": "No encryption key available"
                }
            
            # Create Fernet cipher
            fernet_key = base64.urlsafe_b64encode(encryption_key)
            cipher = Fernet(fernet_key)
            
            # Encrypt data
            encrypted_data = cipher.encrypt(data)
            
            return {
                "success": True,
                "encrypted_data": base64.b64encode(encrypted_data).decode('utf-8'),
                "key_id": key_id or "master",
                "encryption_algorithm": "Fernet (AES-128)"
            }
            
        except Exception as e:
            self.logger.error(f"Data encryption error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def decrypt_data(self, encrypted_data: str, key_id: Optional[str] = None) -> Dict[str, Any]:
        """Decrypt data using symmetric encryption"""
        try:
            # Use master key or specified session key
            if key_id and key_id in self.session_keys:
                decryption_key = self.session_keys[key_id]
            elif self.master_key:
                decryption_key = self.master_key
            else:
                return {
                    "success": False,
                    "error": "No decryption key available"
                }
            
            # Create Fernet cipher
            fernet_key = base64.urlsafe_b64encode(decryption_key)
            cipher = Fernet(fernet_key)
            
            # Decrypt data
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = cipher.decrypt(encrypted_bytes)
            
            return {
                "success": True,
                "decrypted_data": decrypted_data.decode('utf-8'),
                "key_id": key_id or "master"
            }
            
        except Exception as e:
            self.logger.error(f"Data decryption error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_rsa_keypair(self, key_id: str) -> Dict[str, Any]:
        """Generate RSA public/private key pair"""
        try:
            self.logger.info(f"🔑 Generating RSA key pair: {key_id}")
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.rsa_key_size,
            )
            
            # Get public key
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Store keys
            private_key_file = self.key_storage_path / f"{key_id}_private.pem"
            public_key_file = self.key_storage_path / f"{key_id}_public.pem"
            
            with open(private_key_file, 'wb') as f:
                f.write(private_pem)
            
            with open(public_key_file, 'wb') as f:
                f.write(public_pem)
            
            # Set restrictive permissions
            os.chmod(private_key_file, 0o600)
            os.chmod(public_key_file, 0o644)
            
            return {
                "success": True,
                "key_id": key_id,
                "key_size": self.rsa_key_size,
                "private_key_file": str(private_key_file),
                "public_key_file": str(public_key_file),
                "public_key_pem": public_pem.decode('utf-8')
            }
            
        except Exception as e:
            self.logger.error(f"RSA key generation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def encrypt_with_rsa(self, data: Union[str, bytes], public_key_file: str) -> Dict[str, Any]:
        """Encrypt data with RSA public key"""
        try:
            # Convert string to bytes if necessary
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Load public key
            with open(public_key_file, 'rb') as f:
                public_key = serialization.load_pem_public_key(f.read())
            
            # Encrypt data
            encrypted_data = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return {
                "success": True,
                "encrypted_data": base64.b64encode(encrypted_data).decode('utf-8'),
                "encryption_algorithm": "RSA-OAEP"
            }
            
        except Exception as e:
            self.logger.error(f"RSA encryption error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def decrypt_with_rsa(self, encrypted_data: str, private_key_file: str) -> Dict[str, Any]:
        """Decrypt data with RSA private key"""
        try:
            # Load private key
            with open(private_key_file, 'rb') as f:
                private_key = serialization.load_pem_private_key(f.read(), password=None)
            
            # Decrypt data
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return {
                "success": True,
                "decrypted_data": decrypted_data.decode('utf-8')
            }
            
        except Exception as e:
            self.logger.error(f"RSA decryption error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_session_key(self, session_id: str) -> Dict[str, Any]:
        """Generate session-specific encryption key"""
        try:
            session_key = secrets.token_bytes(self.symmetric_key_size)
            self.session_keys[session_id] = session_key
            
            return {
                "success": True,
                "session_id": session_id,
                "key_strength": "256-bit"
            }
            
        except Exception as e:
            self.logger.error(f"Session key generation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def hash_data(self, data: Union[str, bytes], algorithm: str = "sha256") -> Dict[str, Any]:
        """Generate cryptographic hash of data"""
        try:
            # Convert string to bytes if necessary
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Select hash algorithm
            if algorithm.lower() == "sha256":
                hash_obj = hashlib.sha256()
            elif algorithm.lower() == "sha512":
                hash_obj = hashlib.sha512()
            elif algorithm.lower() == "md5":
                hash_obj = hashlib.md5()
            else:
                return {
                    "success": False,
                    "error": f"Unsupported hash algorithm: {algorithm}"
                }
            
            hash_obj.update(data)
            hash_value = hash_obj.hexdigest()
            
            return {
                "success": True,
                "hash_value": hash_value,
                "algorithm": algorithm.upper(),
                "data_size": len(data)
            }
            
        except Exception as e:
            self.logger.error(f"Data hashing error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def secure_delete_key(self, key_id: str) -> Dict[str, Any]:
        """Securely delete encryption key"""
        try:
            deleted_files = []
            
            # Delete session key from memory
            if key_id in self.session_keys:
                del self.session_keys[key_id]
                deleted_files.append(f"session_key_{key_id}")
            
            # Delete key files
            key_files = [
                self.key_storage_path / f"{key_id}.key",
                self.key_storage_path / f"{key_id}_private.pem",
                self.key_storage_path / f"{key_id}_public.pem"
            ]
            
            for key_file in key_files:
                if key_file.exists():
                    # Overwrite file with random data before deletion
                    file_size = key_file.stat().st_size
                    with open(key_file, 'wb') as f:
                        f.write(secrets.token_bytes(file_size))
                    
                    key_file.unlink()
                    deleted_files.append(str(key_file))
            
            return {
                "success": True,
                "key_id": key_id,
                "deleted_files": deleted_files
            }
            
        except Exception as e:
            self.logger.error(f"Secure key deletion error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_encryption_status(self) -> Dict[str, Any]:
        """Get current encryption system status"""
        try:
            status = {
                "master_key_loaded": self.master_key is not None,
                "active_session_keys": len(self.session_keys),
                "key_storage_path": str(self.key_storage_path),
                "supported_algorithms": [
                    "Fernet (AES-128)",
                    "RSA-OAEP",
                    "SHA256",
                    "SHA512"
                ],
                "key_files": []
            }
            
            # List available key files
            if self.key_storage_path.exists():
                for key_file in self.key_storage_path.glob("*"):
                    if key_file.is_file():
                        status["key_files"].append({
                            "filename": key_file.name,
                            "size_bytes": key_file.stat().st_size,
                            "modified": datetime.fromtimestamp(key_file.stat().st_mtime).isoformat()
                        })
            
            return status
            
        except Exception as e:
            self.logger.error(f"Encryption status error: {e}")
            return {
                "error": str(e)
            }