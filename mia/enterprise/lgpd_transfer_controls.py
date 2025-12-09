#!/usr/bin/env python3
"""
LGPD Cross-Border Transfer Controls
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class LGPDTransferManager:
    """LGPD Cross-Border Transfer Manager"""
    
    def __init__(self):
        self.transfer_records = {}
        self.approved_countries = [
            "Argentina", "Uruguay", "Canada", "Switzerland", 
            "United Kingdom", "Japan", "South Korea"
        ]  # Države z ustrezno ravnjo varstva
        
    def assess_transfer_legality(self, 
                               destination_country: str,
                               data_categories: List[str],
                               transfer_mechanism: str,
                               recipient_info: Dict[str, Any]) -> Dict[str, Any]:
        """Oceni zakonitost prenosa podatkov"""
        
        # Preveri, če je država na seznamu odobrenih
        adequate_protection = destination_country in self.approved_countries
        
        # Oceni transfer mechanism
        valid_mechanisms = [
            "adequacy_decision",
            "standard_contractual_clauses", 
            "binding_corporate_rules",
            "certification",
            "consent",
            "contract_performance",
            "legal_claims"
        ]
        
        mechanism_valid = transfer_mechanism in valid_mechanisms
        
        # Posebne zahteve za občutljive podatke
        sensitive_data_restrictions = "sensitive" in data_categories or "health" in data_categories
        
        # Določi zakonitost
        transfer_legal = True
        requirements = []
        
        if not adequate_protection and not mechanism_valid:
            transfer_legal = False
            requirements.append("Valid transfer mechanism required")
        
        if sensitive_data_restrictions and transfer_mechanism == "consent":
            requirements.append("Explicit consent required for sensitive data")
        
        if not adequate_protection:
            requirements.append("Additional safeguards required")
        
        assessment = {
            "destination_country": destination_country,
            "adequate_protection": adequate_protection,
            "transfer_mechanism": transfer_mechanism,
            "mechanism_valid": mechanism_valid,
            "transfer_legal": transfer_legal,
            "requirements": requirements,
            "risk_level": self._assess_transfer_risk(destination_country, data_categories),
            "assessed_at": self._get_build_timestamp().isoformat()
        }
        
        return assessment
    
    def register_international_transfer(self, 
                                      transfer_id: str,
                                      data_subject_ids: List[str],
                                      destination_country: str,
                                      recipient_info: Dict[str, Any],
                                      data_categories: List[str],
                                      transfer_mechanism: str,
                                      purpose: str) -> Dict[str, Any]:
        """Registriraj mednarodni prenos podatkov"""
        
        # Oceni zakonitost
        legality_assessment = self.assess_transfer_legality(
            destination_country, data_categories, transfer_mechanism, recipient_info
        )
        
        if not legality_assessment["transfer_legal"]:
            return {
                "status": "rejected",
                "reason": "Transfer not legally compliant",
                "assessment": legality_assessment
            }
        
        # Registriraj prenos
        transfer_record = {
            "transfer_id": transfer_id,
            "data_subject_ids": data_subject_ids,
            "destination_country": destination_country,
            "recipient_info": recipient_info,
            "data_categories": data_categories,
            "transfer_mechanism": transfer_mechanism,
            "purpose": purpose,
            "legality_assessment": legality_assessment,
            "registered_at": self._get_build_timestamp().isoformat(),
            "status": "approved",
            "monitoring": {
                "next_review_date": (self._get_build_timestamp().replace(year=self._get_build_timestamp().year + 1)).isoformat(),
                "compliance_checks": []
            }
        }
        
        self.transfer_records[transfer_id] = transfer_record
        
        return {
            "status": "approved",
            "transfer_record": transfer_record
        }
    
    def monitor_ongoing_transfers(self) -> Dict[str, Any]:
        """Spremljaj tekoče prenose"""
        current_time = self._get_build_timestamp()
        
        active_transfers = []
        review_required = []
        
        for transfer_id, record in self.transfer_records.items():
            if record["status"] == "approved":
                active_transfers.append(transfer_id)
                
                # Preveri, če je potreben pregled
                review_date = datetime.fromisoformat(record["monitoring"]["next_review_date"])
                if current_time >= review_date:
                    review_required.append(transfer_id)
        
        return {
            "active_transfers": len(active_transfers),
            "transfers_requiring_review": len(review_required),
            "review_required_transfers": review_required,
            "monitoring_timestamp": current_time.isoformat()
        }
    
    def _assess_transfer_risk(self, destination_country: str, data_categories: List[str]) -> str:
        """Oceni tveganje prenosa"""
        risk_score = 0
        
        # Tveganje glede na državo
        if destination_country not in self.approved_countries:
            risk_score += 2
        
        # Tveganje glede na kategorije podatkov
        if "sensitive" in data_categories:
            risk_score += 3
        if "health" in data_categories:
            risk_score += 3
        if "biometric" in data_categories:
            risk_score += 3
        if "children" in data_categories:
            risk_score += 2
        
        if risk_score >= 5:
            return "high"
        elif risk_score >= 3:
            return "medium"
        else:
            return "low"
    
    def get_transfer_dashboard(self) -> Dict[str, Any]:
        """Pridobi transfer dashboard"""
        total_transfers = len(self.transfer_records)
        active_transfers = sum(1 for t in self.transfer_records.values() if t["status"] == "approved")
        high_risk_transfers = sum(1 for t in self.transfer_records.values() 
                                if t["legality_assessment"]["risk_level"] == "high")
        
        return {
            "total_transfers": total_transfers,
            "active_transfers": active_transfers,
            "high_risk_transfers": high_risk_transfers,
            "approved_countries": len(self.approved_countries),
            "compliance_rate": 98.5,  # Simulirano
            "last_updated": self._get_build_timestamp().isoformat()
        }
