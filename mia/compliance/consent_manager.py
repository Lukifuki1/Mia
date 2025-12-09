import time
import platform
#!/usr/bin/env python3
"""
MIA Enterprise AGI - Consent Manager
===================================

LGPD consent management and tracking system.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum


class ConsentStatus(Enum):
    """Consent status types"""
    GIVEN = "given"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"


class ConsentManager:
    """LGPD consent management system"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = self._setup_logging()
        
        # Consent storage
        self.consent_records = {}
        self.consent_history = []
        
        # Configuration
        self.config = {
            "consent_expiry_days": 365,
            "require_explicit_consent": True,
            "allow_consent_withdrawal": True,
            "consent_granularity": "purpose_specific"
        }
        
        self.logger.info("📋 Consent Manager initialized")
    

    def process_consent(self, user_id: str, consent_type: str) -> Dict[str, Any]:
        """Process user consent"""
        try:
            consent_result = {
                "success": True,
                "user_id": user_id,
                "consent_type": consent_type,
                "consent_timestamp": datetime.now().isoformat(),
                "consent_status": "granted"
            }
            
            # Store consent record
            consent_record = {
                "user_id": user_id,
                "consent_type": consent_type,
                "timestamp": consent_result["consent_timestamp"],
                "status": "granted",
                "ip_address": "127.0.0.1",  # Simulated
                "user_agent": "MIA_System"
            }
            
            # Add to consent records
            # Consent records initialized in __init__
            
            self.consent_records.append(consent_record)
            
            self.logger.info(f"📋 Consent processed for user {user_id}: {consent_type}")
            return consent_result
            
        except Exception as e:
            self.logger.error(f"Consent processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_id": user_id,
                "consent_type": consent_type,
                "consent_timestamp": datetime.now().isoformat()
            }
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.Compliance.ConsentManager")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _get_deterministic_time(self) -> float:
        """Return deterministic time for testing"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC
    
    def initialize_consent_system(self) -> Dict[str, Any]:
        """Initialize consent management system"""
        try:
            self.logger.info("📋 Initializing consent management system...")
            
            # Create consent storage directory
            consent_dir = self.project_root / "mia_data" / "consent"
            consent_dir.mkdir(parents=True, exist_ok=True)
            
            # Load existing consent records
            self._load_consent_records()
            
            return {
                "success": True,
                "consent_records_loaded": len(self.consent_records),
                "storage_path": str(consent_dir)
            }
            
        except Exception as e:
            self.logger.error(f"Consent system initialization error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def record_consent(self, subject_id: str, purpose: str, data_categories: List[str],
                      legal_basis: str = "consent", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Record new consent"""
        try:
            consent_id = f"{subject_id}_{purpose}_{int(self._get_deterministic_time())}"
            
            consent_record = {
                "consent_id": consent_id,
                "subject_id": subject_id,
                "purpose": purpose,
                "data_categories": data_categories,
                "legal_basis": legal_basis,
                "status": ConsentStatus.GIVEN.value,
                "granted_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=self.config["consent_expiry_days"])).isoformat(),
                "metadata": metadata or {},
                "withdrawal_method": "email_request"
            }
            
            # Store consent record
            self.consent_records[consent_id] = consent_record
            
            # Add to history
            self.consent_history.append({
                "action": "consent_granted",
                "consent_id": consent_id,
                "timestamp": datetime.now().isoformat(),
                "details": consent_record
            })
            
            # Save to storage
            self._save_consent_records()
            
            self.logger.info(f"📋 Consent recorded: {consent_id}")
            
            return {
                "success": True,
                "consent_id": consent_id,
                "consent_record": consent_record
            }
            
        except Exception as e:
            self.logger.error(f"Consent recording error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_consent(self, subject_id: str, purpose: str, data_categories: List[str]) -> Dict[str, Any]:
        """Check if valid consent exists"""
        try:
            valid_consents = []
            
            for consent_id, consent_record in self.consent_records.items():
                if (consent_record["subject_id"] == subject_id and
                    consent_record["purpose"] == purpose and
                    consent_record["status"] == ConsentStatus.GIVEN.value):
                    
                    # Check if consent covers required data categories
                    if all(category in consent_record["data_categories"] for category in data_categories):
                        # Check if consent is not expired
                        expires_at = datetime.fromisoformat(consent_record["expires_at"])
                        if expires_at > datetime.now():
                            valid_consents.append(consent_record)
            
            if valid_consents:
                return {
                    "valid": True,
                    "consent_records": valid_consents,
                    "message": "Valid consent found"
                }
            else:
                return {
                    "valid": False,
                    "message": "No valid consent found",
                    "required_consent": {
                        "subject_id": subject_id,
                        "purpose": purpose,
                        "data_categories": data_categories
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Consent check error: {e}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    def withdraw_consent(self, consent_id: str, withdrawal_reason: Optional[str] = None) -> Dict[str, Any]:
        """Withdraw consent"""
        try:
            if consent_id not in self.consent_records:
                return {
                    "success": False,
                    "error": "Consent record not found"
                }
            
            consent_record = self.consent_records[consent_id]
            
            # Update consent status
            consent_record["status"] = ConsentStatus.WITHDRAWN.value
            consent_record["withdrawn_at"] = datetime.now().isoformat()
            consent_record["withdrawal_reason"] = withdrawal_reason
            
            # Add to history
            self.consent_history.append({
                "action": "consent_withdrawn",
                "consent_id": consent_id,
                "timestamp": datetime.now().isoformat(),
                "withdrawal_reason": withdrawal_reason
            })
            
            # Save to storage
            self._save_consent_records()
            
            self.logger.info(f"📋 Consent withdrawn: {consent_id}")
            
            return {
                "success": True,
                "consent_id": consent_id,
                "withdrawal_timestamp": consent_record["withdrawn_at"]
            }
            
        except Exception as e:
            self.logger.error(f"Consent withdrawal error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_consent(self, consent_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing consent"""
        try:
            if consent_id not in self.consent_records:
                return {
                    "success": False,
                    "error": "Consent record not found"
                }
            
            consent_record = self.consent_records[consent_id]
            
            # Update allowed fields
            allowed_updates = ["data_categories", "metadata", "expires_at"]
            for field, value in updates.items():
                if field in allowed_updates:
                    consent_record[field] = value
            
            consent_record["updated_at"] = datetime.now().isoformat()
            
            # Add to history
            self.consent_history.append({
                "action": "consent_updated",
                "consent_id": consent_id,
                "timestamp": datetime.now().isoformat(),
                "updates": updates
            })
            
            # Save to storage
            self._save_consent_records()
            
            self.logger.info(f"📋 Consent updated: {consent_id}")
            
            return {
                "success": True,
                "consent_id": consent_id,
                "updated_record": consent_record
            }
            
        except Exception as e:
            self.logger.error(f"Consent update error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_subject_consents(self, subject_id: str) -> Dict[str, Any]:
        """Get all consents for a subject"""
        try:
            subject_consents = []
            
            for consent_id, consent_record in self.consent_records.items():
                if consent_record["subject_id"] == subject_id:
                    subject_consents.append(consent_record)
            
            return {
                "subject_id": subject_id,
                "consents": subject_consents,
                "total_consents": len(subject_consents),
                "active_consents": len([c for c in subject_consents if c["status"] == ConsentStatus.GIVEN.value])
            }
            
        except Exception as e:
            self.logger.error(f"Subject consents retrieval error: {e}")
            return {
                "error": str(e)
            }
    
    def expire_old_consents(self) -> Dict[str, Any]:
        """Expire old consents based on expiry dates"""
        try:
            expired_count = 0
            current_time = datetime.now()
            
            for consent_id, consent_record in self.consent_records.items():
                if consent_record["status"] == ConsentStatus.GIVEN.value:
                    expires_at = datetime.fromisoformat(consent_record["expires_at"])
                    if expires_at <= current_time:
                        consent_record["status"] = ConsentStatus.EXPIRED.value
                        consent_record["expired_at"] = current_time.isoformat()
                        expired_count += 1
                        
                        # Add to history
                        self.consent_history.append({
                            "action": "consent_expired",
                            "consent_id": consent_id,
                            "timestamp": current_time.isoformat()
                        })
            
            if expired_count > 0:
                self._save_consent_records()
                self.logger.info(f"📋 Expired {expired_count} old consents")
            
            return {
                "success": True,
                "expired_consents": expired_count
            }
            
        except Exception as e:
            self.logger.error(f"Consent expiry error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _load_consent_records(self):
        """Load consent records from storage"""
        try:
            consent_file = self.project_root / "mia_data" / "consent" / "consent_records.json"
            if consent_file.exists():
                with open(consent_file, 'r') as f:
                    data = json.load(f)
                    self.consent_records = data.get("consent_records", {})
                    self.consent_history = data.get("consent_history", [])
                    
        except Exception as e:
            self.logger.warning(f"Failed to load consent records: {e}")
    
    def _save_consent_records(self):
        """Save consent records to storage"""
        try:
            consent_file = self.project_root / "mia_data" / "consent" / "consent_records.json"
            consent_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "consent_records": self.consent_records,
                "consent_history": self.consent_history,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(consent_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save consent records: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get consent manager status"""
        return {
            "total_consents": len(self.consent_records),
            "active_consents": len([c for c in self.consent_records.values() if c["status"] == ConsentStatus.GIVEN.value]),
            "withdrawn_consents": len([c for c in self.consent_records.values() if c["status"] == ConsentStatus.WITHDRAWN.value]),
            "expired_consents": len([c for c in self.consent_records.values() if c["status"] == ConsentStatus.EXPIRED.value]),
            "config": self.config
        }
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update consent manager configuration"""
        self.config.update(new_config)
        self.logger.info("📋 Consent manager configuration updated")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate consent management report"""
        try:
            status = self.get_status()
            
            return {
                "report_type": "consent_management",
                "timestamp": datetime.now().isoformat(),
                "statistics": status,
                "compliance_score": self._calculate_consent_compliance_score(),
                "recommendations": self.get_recommendations()
            }
            
        except Exception as e:
            self.logger.error(f"Consent report generation error: {e}")
            return {
                "error": str(e)
            }
    
    def _calculate_consent_compliance_score(self) -> float:
        """Calculate consent compliance score"""
        try:
            if not self.consent_records:
                return 100.0  # No data, no violations
            
            total_consents = len(self.consent_records)
            valid_consents = len([c for c in self.consent_records.values() if c["status"] == ConsentStatus.GIVEN.value])
            
            # Basic scoring - in practice, this would be more sophisticated
            score = (valid_consents / total_consents) * 100 if total_consents > 0 else 100.0
            
            return min(score, 100.0)
            
        except Exception:
            return 0.0
    
    def get_recommendations(self) -> List[str]:
        """Get consent management recommendations"""
        recommendations = []
        
        status = self.get_status()
        
        if status["expired_consents"] > 0:
            recommendations.append("Review and renew expired consents")
        
        if status["withdrawn_consents"] > status["active_consents"] * 0.1:
            recommendations.append("Investigate high consent withdrawal rate")
        
        recommendations.extend([
            "Implement automated consent renewal reminders",
            "Regular consent audit and cleanup",
            "Improve consent user experience",
            "Implement granular consent options"
        ])
        
        return recommendations