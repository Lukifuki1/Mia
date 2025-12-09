#!/usr/bin/env python3
"""
🔧 MIA Enterprise AGI - Core Verification Methods
Enterprise Production Implementation
"""

import os
import sys
import json
import hashlib
import logging
import sqlite3
import pickle
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time


class EnterpriseVerificationCore:
    """Enterprise-grade core verification methods"""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.logger = self._setup_logging()
        self.storage_path = Path(storage_path) if storage_path else Path("mia_data/verification")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.db_path = self.storage_path / "verification.db"
        self._init_database()
        
        # Cache for performance
        self._cache = {}
        self._cache_lock = threading.RLock()
        self._cache_ttl = 300  # 5 minutes
        
        # Verification metrics
        self.metrics = {
            "total_verifications": 0,
            "successful_verifications": 0,
            "failed_verifications": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Setup enterprise logging"""
        logger = logging.getLogger(f"MIA.Enterprise.{self.__class__.__name__}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _init_database(self):
        """Initialize SQLite database for verification data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create verification data table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS verification_data (
                        id TEXT PRIMARY KEY,
                        data_hash TEXT NOT NULL,
                        content BLOB,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        access_count INTEGER DEFAULT 0
                    )
                ''')
                
                # Create verification logs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS verification_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        operation TEXT NOT NULL,
                        identifier TEXT,
                        result TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        execution_time REAL
                    )
                ''')
                
                # Create indexes for performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_data_hash ON verification_data(data_hash)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON verification_data(created_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_operation ON verification_logs(operation)')
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Database initialization error: {e}")
            raise
    
    def verify_data_integrity(self, identifier: str, expected_hash: Optional[str] = None) -> Dict[str, Any]:
        """Verify data integrity with enterprise-grade checks"""
        start_time = time.time()
        self.metrics["total_verifications"] += 1
        
        try:
            # Check cache first
            cache_key = f"integrity_{identifier}"
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                self.metrics["cache_hits"] += 1
                return cached_result
            
            self.metrics["cache_misses"] += 1
            
            # Retrieve data from database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT data_hash, content, metadata FROM verification_data WHERE id = ?',
                    (identifier,)
                )
                result = cursor.fetchone()
                
                if not result:
                    verification_result = {
                        "success": False,
                        "identifier": identifier,
                        "error": "Data not found",
                        "integrity_score": 0.0,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    stored_hash, content, metadata = result
                    
                    # Verify hash integrity
                    if content:
                        calculated_hash = hashlib.sha256(content).hexdigest()
                        hash_match = calculated_hash == stored_hash
                    else:
                        hash_match = False
                    
                    # Additional integrity checks
                    metadata_valid = self._validate_metadata(metadata)
                    content_valid = self._validate_content(content)
                    
                    # Calculate integrity score
                    integrity_score = self._calculate_integrity_score(
                        hash_match, metadata_valid, content_valid
                    )
                    
                    verification_result = {
                        "success": hash_match and metadata_valid and content_valid,
                        "identifier": identifier,
                        "hash_match": hash_match,
                        "metadata_valid": metadata_valid,
                        "content_valid": content_valid,
                        "integrity_score": integrity_score,
                        "stored_hash": stored_hash,
                        "calculated_hash": calculated_hash if content else None,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Update access count
                    cursor.execute(
                        'UPDATE verification_data SET access_count = access_count + 1 WHERE id = ?',
                        (identifier,)
                    )
                    conn.commit()
            
            # Cache result
            self._set_cache(cache_key, verification_result)
            
            # Log operation
            execution_time = time.time() - start_time
            self._log_operation("verify_integrity", identifier, verification_result["success"], execution_time)
            
            if verification_result["success"]:
                self.metrics["successful_verifications"] += 1
            else:
                self.metrics["failed_verifications"] += 1
            
            return verification_result
            
        except Exception as e:
            self.logger.error(f"Data integrity verification error: {e}")
            self.metrics["failed_verifications"] += 1
            return {
                "success": False,
                "identifier": identifier,
                "error": str(e),
                "integrity_score": 0.0,
                "timestamp": datetime.now().isoformat()
            }
    
    def store_verification_data(self, identifier: str, content: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Store data with verification metadata"""
        try:
            # Calculate hash
            data_hash = hashlib.sha256(content).hexdigest()
            metadata_json = json.dumps(metadata, sort_keys=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert or update data
                cursor.execute('''
                    INSERT OR REPLACE INTO verification_data 
                    (id, data_hash, content, metadata, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (identifier, data_hash, content, metadata_json))
                
                conn.commit()
            
            # Clear cache for this identifier
            self._clear_cache_for_identifier(identifier)
            
            self.logger.info(f"Stored verification data: {identifier}")
            
            return {
                "success": True,
                "identifier": identifier,
                "data_hash": data_hash,
                "size": len(content),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Store verification data error: {e}")
            return {
                "success": False,
                "identifier": identifier,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def retrieve_verification_data(self, identifier: str) -> Dict[str, Any]:
        """Retrieve verification data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT data_hash, content, metadata, created_at, access_count
                    FROM verification_data WHERE id = ?
                ''', (identifier,))
                
                result = cursor.fetchone()
                
                if not result:
                    return {
                        "success": False,
                        "identifier": identifier,
                        "error": "Data not found",
                        "timestamp": datetime.now().isoformat()
                    }
                
                data_hash, content, metadata_json, created_at, access_count = result
                
                try:
                    metadata = json.loads(metadata_json) if metadata_json else {}
                except json.JSONDecodeError:
                    metadata = {}
                
                return {
                    "success": True,
                    "identifier": identifier,
                    "data_hash": data_hash,
                    "content": content,
                    "metadata": metadata,
                    "created_at": created_at,
                    "access_count": access_count,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Retrieve verification data error: {e}")
            return {
                "success": False,
                "identifier": identifier,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def batch_verify_integrity(self, identifiers: List[str]) -> Dict[str, Any]:
        """Batch verify multiple data items"""
        results = {}
        failed_count = 0
        
        for identifier in identifiers:
            result = self.verify_data_integrity(identifier)
            results[identifier] = result
            if not result["success"]:
                failed_count += 1
        
        return {
            "success": failed_count == 0,
            "total_items": len(identifiers),
            "failed_items": failed_count,
            "success_rate": ((len(identifiers) - failed_count) / len(identifiers)) * 100 if identifiers else 100,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_verification_metrics(self) -> Dict[str, Any]:
        """Get verification system metrics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get database statistics
                cursor.execute('SELECT COUNT(*) FROM verification_data')
                total_records = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM verification_logs')
                total_operations = cursor.fetchone()[0]
                
                cursor.execute('''
                    SELECT AVG(execution_time) FROM verification_logs 
                    WHERE timestamp > datetime('now', '-1 hour')
                ''')
                avg_execution_time = cursor.fetchone()[0] or 0
                
            cache_hit_rate = (self.metrics["cache_hits"] / 
                            (self.metrics["cache_hits"] + self.metrics["cache_misses"])) * 100 if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0
            
            success_rate = (self.metrics["successful_verifications"] / 
                          self.metrics["total_verifications"]) * 100 if self.metrics["total_verifications"] > 0 else 0
            
            return {
                "database_records": total_records,
                "total_operations": total_operations,
                "cache_hit_rate": round(cache_hit_rate, 2),
                "success_rate": round(success_rate, 2),
                "avg_execution_time": round(avg_execution_time, 4),
                "metrics": self.metrics.copy(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Get metrics error: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def cleanup_old_data(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up old verification data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count records to be deleted
                cursor.execute(
                    'SELECT COUNT(*) FROM verification_data WHERE created_at < ?',
                    (cutoff_date.isoformat(),)
                )
                records_to_delete = cursor.fetchone()[0]
                
                # Delete old records
                cursor.execute(
                    'DELETE FROM verification_data WHERE created_at < ?',
                    (cutoff_date.isoformat(),)
                )
                
                # Delete old logs
                cursor.execute(
                    'DELETE FROM verification_logs WHERE timestamp < ?',
                    (cutoff_date.isoformat(),)
                )
                
                conn.commit()
            
            # Clear cache
            self._clear_cache()
            
            self.logger.info(f"Cleaned up {records_to_delete} old verification records")
            
            return {
                "success": True,
                "records_deleted": records_to_delete,
                "cutoff_date": cutoff_date.isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _validate_metadata(self, metadata_json: str) -> bool:
        """Validate metadata structure"""
        try:
            if not metadata_json:
                return False
            
            metadata = json.loads(metadata_json)
            
            # Check required fields
            required_fields = ["created", "version"]
            for field in required_fields:
                if field not in metadata:
                    return False
            
            # Validate timestamp format
            try:
                datetime.fromisoformat(metadata["created"].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return False
            
            return True
            
        except (json.JSONDecodeError, TypeError):
            return False
    
    def _validate_content(self, content: bytes) -> bool:
        """Validate content structure"""
        if not content:
            return False
        
        # Basic content validation
        if len(content) == 0:
            return False
        
        # Check for common corruption patterns
        if content == b'\x00' * len(content):  # All null bytes
            return False
        
        return True
    
    def _calculate_integrity_score(self, hash_match: bool, metadata_valid: bool, content_valid: bool) -> float:
        """Calculate integrity score"""
        score = 0.0
        
        if hash_match:
            score += 50.0
        if metadata_valid:
            score += 25.0
        if content_valid:
            score += 25.0
        
        return score
    
    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get item from cache"""
        with self._cache_lock:
            if key in self._cache:
                item, timestamp = self._cache[key]
                if time.time() - timestamp < self._cache_ttl:
                    return item
                else:
                    del self._cache[key]
        return None
    
    def _set_cache(self, key: str, value: Dict[str, Any]):
        """Set item in cache"""
        with self._cache_lock:
            self._cache[key] = (value, time.time())
    
    def _clear_cache_for_identifier(self, identifier: str):
        """Clear cache entries for specific identifier"""
        with self._cache_lock:
            keys_to_remove = [k for k in self._cache.keys() if identifier in k]
            for key in keys_to_remove:
                del self._cache[key]
    
    def _clear_cache(self):
        """Clear entire cache"""
        with self._cache_lock:
            self._cache.clear()
    
    def _log_operation(self, operation: str, identifier: str, success: bool, execution_time: float):
        """Log verification operation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO verification_logs (operation, identifier, result, execution_time)
                    VALUES (?, ?, ?, ?)
                ''', (operation, identifier, "success" if success else "failure", execution_time))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Log operation error: {e}")


# Backward compatibility
CoreHandler = EnterpriseVerificationCore