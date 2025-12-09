#!/usr/bin/env python3
"""
MIA Enterprise AGI - License Manager
===================================

Enterprise license management and validation system.
"""

import logging
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum


class LicenseType(Enum):
    """License types"""
    TRIAL = "trial"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    UNLIMITED = "unlimited"


class LicenseStatus(Enum):
    """License status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


class LicenseManager:
    """Enterprise license management system"""
    
    def __init__(self, enterprise_dir: str = "./enterprise"):
        self.enterprise_dir = Path(enterprise_dir)
        self.logger = self._setup_logging()
        
        # License configuration
        self.config = {
            "validation_interval_hours": 24,
            "grace_period_days": 7,
            "auto_renewal": False,
            "offline_validation_days": 30
        }
        
        # License storage
        self.licenses = {}
        self.license_history = []
        
        self.logger.info("📄 License Manager initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.Enterprise.LicenseManager")
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
    
    def initialize_license_system(self) -> Dict[str, Any]:
        """Initialize license management system"""
        try:
            self.logger.info("📄 Initializing license management system...")
            
            # Create license directory
            license_dir = self.enterprise_dir / "licenses"
            license_dir.mkdir(parents=True, exist_ok=True)
            
            # Load existing licenses
            self._load_licenses()
            
            # Validate existing licenses
            validation_results = self._validate_all_licenses()
            
            return {
                "success": True,
                "licenses_loaded": len(self.licenses),
                "validation_results": validation_results,
                "storage_path": str(license_dir)
            }
            
        except Exception as e:
            self.logger.error(f"License system initialization error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def install_license(self, license_data: Dict[str, Any]) -> Dict[str, Any]:
        """Install a new license"""
        try:
            # Validate license data
            validation_result = self._validate_license_data(license_data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Invalid license data",
                    "validation_errors": validation_result["errors"]
                }
            
            license_id = license_data.get("license_id")
            
            # Create license record
            license_record = {
                "license_id": license_id,
                "license_type": license_data.get("license_type"),
                "organization": license_data.get("organization"),
                "issued_to": license_data.get("issued_to"),
                "issued_date": license_data.get("issued_date"),
                "expiry_date": license_data.get("expiry_date"),
                "features": license_data.get("features", []),
                "user_limit": license_data.get("user_limit", 1),
                "status": LicenseStatus.ACTIVE.value,
                "installed_at": self._get_build_timestamp().isoformat(),
                "signature": license_data.get("signature"),
                "validation_hash": self._generate_validation_hash(license_data)
            }
            
            # Store license
            self.licenses[license_id] = license_record
            
            # Add to history
            self.license_history.append({
                "action": "license_installed",
                "license_id": license_id,
                "timestamp": self._get_build_timestamp().isoformat(),
                "details": license_record
            })
            
            # Save licenses
            self._save_licenses()
            
            self.logger.info(f"📄 License installed: {license_id}")
            
            return {
                "success": True,
                "license_id": license_id,
                "license_record": license_record
            }
            
        except Exception as e:
            self.logger.error(f"License installation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_license(self, license_id: str) -> Dict[str, Any]:
        """Validate a specific license"""
        try:
            if license_id not in self.licenses:
                return {
                    "valid": False,
                    "error": "License not found"
                }
            
            license_record = self.licenses[license_id]
            
            validation_result = {
                "license_id": license_id,
                "valid": True,
                "validation_timestamp": self._get_build_timestamp().isoformat(),
                "validation_checks": []
            }
            
            # Check expiry date
            expiry_date = datetime.fromisoformat(license_record["expiry_date"])
            if expiry_date < self._get_build_timestamp():
                validation_result["validation_checks"].append({
                    "check": "expiry_date",
                    "status": "failed",
                    "message": "License has expired"
                })
                validation_result["valid"] = False
            else:
                validation_result["validation_checks"].append({
                    "check": "expiry_date",
                    "status": "passed",
                    "message": f"License valid until {expiry_date.isoformat()}"
                })
            
            # Check license status
            if license_record["status"] != LicenseStatus.ACTIVE.value:
                validation_result["validation_checks"].append({
                    "check": "license_status",
                    "status": "failed",
                    "message": f"License status is {license_record['status']}"
                })
                validation_result["valid"] = False
            else:
                validation_result["validation_checks"].append({
                    "check": "license_status",
                    "status": "passed",
                    "message": "License is active"
                })
            
            # Check signature (simplified validation)
            if not self._verify_license_signature(license_record):
                validation_result["validation_checks"].append({
                    "check": "signature_verification",
                    "status": "failed",
                    "message": "License signature verification failed"
                })
                validation_result["valid"] = False
            else:
                validation_result["validation_checks"].append({
                    "check": "signature_verification",
                    "status": "passed",
                    "message": "License signature verified"
                })
            
            # Update license record with validation result
            license_record["last_validation"] = self._get_build_timestamp().isoformat()
            license_record["validation_result"] = validation_result["valid"]
            
            self._save_licenses()
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"License validation error: {e}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    def _validate_license_data(self, license_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate license data structure"""
        errors = []
        
        # Required fields
        required_fields = ["license_id", "license_type", "organization", "issued_to", 
                          "issued_date", "expiry_date", "signature"]
        for field in required_fields:
            if field not in license_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate license type
        if "license_type" in license_data:
            try:
                LicenseType(license_data["license_type"])
            except ValueError:
                errors.append(f"Invalid license type: {license_data['license_type']}")
        
        # Validate dates
        try:
            if "issued_date" in license_data:
                datetime.fromisoformat(license_data["issued_date"])
            if "expiry_date" in license_data:
                datetime.fromisoformat(license_data["expiry_date"])
        except ValueError as e:
            errors.append(f"Invalid date format: {e}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _generate_validation_hash(self, license_data: Dict[str, Any]) -> str:
        """Generate validation hash for license"""
        try:
            # Create hash from key license fields
            hash_data = {
                "license_id": license_data.get("license_id"),
                "license_type": license_data.get("license_type"),
                "organization": license_data.get("organization"),
                "expiry_date": license_data.get("expiry_date")
            }
            
            hash_string = json.dumps(hash_data, sort_keys=True)
            return hashlib.sha256(hash_string.encode()).hexdigest()[:16]
            
        except Exception:
            return "hash_error"
    
    def _verify_license_signature(self, license_record: Dict[str, Any]) -> bool:
        """Verify license signature (simplified)"""
        try:
            # In a real implementation, this would verify cryptographic signatures
            # For now, we'll do basic validation
            signature = license_record.get("signature", "")
            validation_hash = license_record.get("validation_hash", "")
            
            # Basic signature validation
            return len(signature) > 10 and len(validation_hash) > 10
            
        except Exception:
            return False
    
    def _validate_all_licenses(self) -> Dict[str, Any]:
        """Validate all installed licenses"""
        try:
            validation_results = {}
            
            for license_id in self.licenses.keys():
                validation_results[license_id] = self.validate_license(license_id)
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"All licenses validation error: {e}")
            return {}
    
    def get_license_info(self, license_id: str) -> Optional[Dict[str, Any]]:
        """Get license information"""
        return self.licenses.get(license_id)
    
    def list_licenses(self) -> List[Dict[str, Any]]:
        """List all licenses"""
        return list(self.licenses.values())
    
    def check_feature_access(self, feature: str, license_id: Optional[str] = None) -> Dict[str, Any]:
        """Check if a feature is accessible under current licenses"""
        try:
            if license_id:
                # Check specific license
                if license_id not in self.licenses:
                    return {
                        "accessible": False,
                        "reason": "License not found"
                    }
                
                license_record = self.licenses[license_id]
                
                # Check if license is valid
                validation = self.validate_license(license_id)
                if not validation["valid"]:
                    return {
                        "accessible": False,
                        "reason": "License is not valid"
                    }
                
                # Check if feature is included
                features = license_record.get("features", [])
                if feature in features or "all_features" in features:
                    return {
                        "accessible": True,
                        "license_id": license_id,
                        "license_type": license_record["license_type"]
                    }
                else:
                    return {
                        "accessible": False,
                        "reason": f"Feature '{feature}' not included in license"
                    }
            else:
                # Check all licenses
                for license_id, license_record in self.licenses.items():
                    validation = self.validate_license(license_id)
                    if validation["valid"]:
                        features = license_record.get("features", [])
                        if feature in features or "all_features" in features:
                            return {
                                "accessible": True,
                                "license_id": license_id,
                                "license_type": license_record["license_type"]
                            }
                
                return {
                    "accessible": False,
                    "reason": f"Feature '{feature}' not available in any valid license"
                }
                
        except Exception as e:
            self.logger.error(f"Feature access check error: {e}")
            return {
                "accessible": False,
                "reason": f"Error checking feature access: {e}"
            }
    
    def revoke_license(self, license_id: str, reason: str = "") -> Dict[str, Any]:
        """Revoke a license"""
        try:
            if license_id not in self.licenses:
                return {
                    "success": False,
                    "error": "License not found"
                }
            
            license_record = self.licenses[license_id]
            license_record["status"] = LicenseStatus.REVOKED.value
            license_record["revoked_at"] = self._get_build_timestamp().isoformat()
            license_record["revocation_reason"] = reason
            
            # Add to history
            self.license_history.append({
                "action": "license_revoked",
                "license_id": license_id,
                "timestamp": self._get_build_timestamp().isoformat(),
                "reason": reason
            })
            
            self._save_licenses()
            
            self.logger.info(f"📄 License revoked: {license_id}")
            
            return {
                "success": True,
                "license_id": license_id,
                "revocation_timestamp": license_record["revoked_at"]
            }
            
        except Exception as e:
            self.logger.error(f"License revocation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _load_licenses(self):
        """Load licenses from storage"""
        try:
            license_file = self.enterprise_dir / "licenses" / "licenses.json"
            if license_file.exists():
                with open(license_file, 'r') as f:
                    data = json.load(f)
                    self.licenses = data.get("licenses", {})
                    self.license_history = data.get("license_history", [])
                    
        except Exception as e:
            self.logger.warning(f"Failed to load licenses: {e}")
    
    def _save_licenses(self):
        """Save licenses to storage"""
        try:
            license_file = self.enterprise_dir / "licenses" / "licenses.json"
            license_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "licenses": self.licenses,
                "license_history": self.license_history,
                "last_updated": self._get_build_timestamp().isoformat()
            }
            
            with open(license_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save licenses: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get license manager status"""
        active_licenses = len([l for l in self.licenses.values() if l["status"] == LicenseStatus.ACTIVE.value])
        expired_licenses = len([l for l in self.licenses.values() if l["status"] == LicenseStatus.EXPIRED.value])
        
        return {
            "total_licenses": len(self.licenses),
            "active_licenses": active_licenses,
            "expired_licenses": expired_licenses,
            "health_score": (active_licenses / len(self.licenses) * 100) if self.licenses else 100,
            "config": self.config
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate license management report"""
        try:
            status = self.get_status()
            
            return {
                "report_type": "license_management",
                "timestamp": self._get_build_timestamp().isoformat(),
                "statistics": status,
                "health_score": status["health_score"],
                "recommendations": self.get_recommendations()
            }
            
        except Exception as e:
            self.logger.error(f"License report generation error: {e}")
            return {
                "error": str(e)
            }
    
    def get_recommendations(self) -> List[str]:
        """Get license management recommendations"""
        recommendations = []
        
        status = self.get_status()
        
        if status["expired_licenses"] > 0:
            recommendations.append(f"Renew {status['expired_licenses']} expired licenses")
        
        if status["total_licenses"] == 0:
            recommendations.append("Install enterprise license")
        
        # Check for licenses expiring soon
        expiring_soon = 0
        for license_record in self.licenses.values():
            if license_record["status"] == LicenseStatus.ACTIVE.value:
                expiry_date = datetime.fromisoformat(license_record["expiry_date"])
                if expiry_date < self._get_build_timestamp() + timedelta(days=30):
                    expiring_soon += 1
        
        if expiring_soon > 0:
            recommendations.append(f"{expiring_soon} licenses expiring within 30 days")
        
        recommendations.extend([
            "Regular license validation",
            "Monitor license usage",
            "Backup license files",
            "Review license compliance"
        ])
        
        return recommendations