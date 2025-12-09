#!/usr/bin/env python3
"""
LGPD Retention Policies
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class LGPDRetentionManager:
    """LGPD Retention Manager za upravljanje obdobij hrambe"""
    
    def __init__(self):
        self.retention_policies = {
            "personal": 365 * 2,      # 2 leti
            "sensitive": 365 * 1,     # 1 leto
            "children": 365 * 1,      # 1 leto
            "biometric": 365 * 5,     # 5 let
            "health": 365 * 10        # 10 let
        }
        self.data_records = {}
        
    def set_retention_policy(self, data_category: str, retention_days: int) -> Dict[str, Any]:
        """Nastavi retention policy"""
        self.retention_policies[data_category] = retention_days
        
        return {
            "status": "set",
            "data_category": data_category,
            "retention_days": retention_days,
            "retention_years": retention_days / 365
        }
    
    def register_data_for_retention(self, 
                                  data_id: str,
                                  data_category: str,
                                  data_subject_id: str,
                                  created_at: Optional[str] = None) -> Dict[str, Any]:
        """Registriraj podatke za retention management"""
        if created_at is None:
            created_at = self._get_build_timestamp().isoformat()
        
        retention_days = self.retention_policies.get(data_category, 365)
        created_dt = datetime.fromisoformat(created_at)
        expiry_dt = created_dt + timedelta(days=retention_days)
        
        record = {
            "data_id": data_id,
            "data_category": data_category,
            "data_subject_id": data_subject_id,
            "created_at": created_at,
            "expiry_date": expiry_dt.isoformat(),
            "retention_days": retention_days,
            "status": "active"
        }
        
        self.data_records[data_id] = record
        
        return {
            "status": "registered",
            "record": record
        }
    
    def check_expired_data(self) -> Dict[str, Any]:
        """Preveri podatke, ki so presegali retention period"""
        current_time = self._get_build_timestamp()
        expired_records = []
        
        for data_id, record in self.data_records.items():
            expiry_dt = datetime.fromisoformat(record["expiry_date"])
            if current_time > expiry_dt and record["status"] == "active":
                expired_records.append(data_id)
        
        return {
            "expired_count": len(expired_records),
            "expired_records": expired_records,
            "check_timestamp": current_time.isoformat()
        }
    
    def delete_expired_data(self) -> Dict[str, Any]:
        """Izbriši podatke, ki so presegali retention period"""
        expired_check = self.check_expired_data()
        deleted_records = []
        
        for data_id in expired_check["expired_records"]:
            if data_id in self.data_records:
                self.data_records[data_id]["status"] = "deleted"
                self.data_records[data_id]["deleted_at"] = self._get_build_timestamp().isoformat()
                deleted_records.append(data_id)
        
        return {
            "deleted_count": len(deleted_records),
            "deleted_records": deleted_records,
            "deletion_timestamp": self._get_build_timestamp().isoformat()
        }
    
    def get_retention_dashboard(self) -> Dict[str, Any]:
        """Pridobi retention dashboard"""
        total_records = len(self.data_records)
        active_records = sum(1 for r in self.data_records.values() if r["status"] == "active")
        deleted_records = sum(1 for r in self.data_records.values() if r["status"] == "deleted")
        
        expired_check = self.check_expired_data()
        
        return {
            "total_records": total_records,
            "active_records": active_records,
            "deleted_records": deleted_records,
            "expired_pending_deletion": expired_check["expired_count"],
            "retention_policies": self.retention_policies,
            "last_updated": self._get_build_timestamp().isoformat()
        }
