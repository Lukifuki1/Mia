#!/usr/bin/env python3
"""
LGPD Consent Manager
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class LGPDConsentManager:
    """LGPD Consent Manager za upravljanje privolitev"""
    
    def __init__(self):
        self.consents = {}
        self.consent_templates = {}
        
    def create_consent_template(self, 
                              template_id: str,
                              purpose: str,
                              data_categories: List[str],
                              retention_period: int,
                              third_parties: List[str] = None) -> Dict[str, Any]:
        """Ustvari predlogo privolitve"""
        template = {
            "template_id": template_id,
            "purpose": purpose,
            "data_categories": data_categories,
            "retention_period": retention_period,
            "third_parties": third_parties or [],
            "created_at": self._get_build_timestamp().isoformat(),
            "version": "1.0",
            "language": "pt-BR",  # Brazilska portugalščina
            "consent_text": self._generate_consent_text(purpose, data_categories, retention_period)
        }
        
        self.consent_templates[template_id] = template
        
        return {
            "status": "created",
            "template": template
        }
    
    def record_consent(self, 
                      data_subject_id: str,
                      template_id: str,
                      consent_given: bool,
                      consent_method: str = "explicit") -> Dict[str, Any]:
        """Zabeleži privolitev"""
        consent_id = f"consent_{data_subject_id}_{template_id}_{int(self._get_build_timestamp().timestamp())}"
        
        consent_record = {
            "consent_id": consent_id,
            "data_subject_id": data_subject_id,
            "template_id": template_id,
            "consent_given": consent_given,
            "consent_method": consent_method,
            "timestamp": self._get_build_timestamp().isoformat(),
            "ip_address": "127.0.0.1",  # V produkciji bi bilo dejansko
            "user_agent": "MIA Enterprise AGI",
            "consent_proof": self._generate_consent_proof(consent_id, consent_given),
            "status": "active" if consent_given else "withdrawn"
        }
        
        self.consents[consent_id] = consent_record
        
        return {
            "status": "recorded",
            "consent_record": consent_record
        }
    
    def withdraw_consent(self, data_subject_id: str, template_id: str) -> Dict[str, Any]:
        """Umakni privolitev"""
        withdrawn_consents = []
        
        for consent_id, consent_data in self.consents.items():
            if (consent_data["data_subject_id"] == data_subject_id and 
                consent_data["template_id"] == template_id and
                consent_data["status"] == "active"):
                
                consent_data["status"] = "withdrawn"
                consent_data["withdrawn_at"] = self._get_build_timestamp().isoformat()
                withdrawn_consents.append(consent_id)
        
        return {
            "status": "withdrawn",
            "withdrawn_consents": withdrawn_consents,
            "withdrawal_count": len(withdrawn_consents)
        }
    
    def get_consent_status(self, data_subject_id: str, template_id: str) -> Dict[str, Any]:
        """Pridobi status privolitve"""
        active_consents = []
        
        for consent_id, consent_data in self.consents.items():
            if (consent_data["data_subject_id"] == data_subject_id and 
                consent_data["template_id"] == template_id and
                consent_data["status"] == "active"):
                active_consents.append(consent_data)
        
        has_valid_consent = len(active_consents) > 0
        
        return {
            "data_subject_id": data_subject_id,
            "template_id": template_id,
            "has_valid_consent": has_valid_consent,
            "active_consents": active_consents,
            "consent_count": len(active_consents)
        }
    
    def _generate_consent_text(self, purpose: str, data_categories: List[str], retention_period: int) -> str:
        """Generiraj besedilo privolitve v brazilski portugalščini"""
        categories_text = ", ".join(data_categories)
        retention_text = f"{retention_period} dias" if retention_period < 365 else f"{retention_period // 365} anos"
        
        consent_text = f"""
Consentimento para Tratamento de Dados Pessoais (LGPD)

Eu autorizo o tratamento dos meus dados pessoais ({categories_text}) para a seguinte finalidade: {purpose}.

Período de retenção: {retention_text}

Seus direitos incluem:
- Acesso aos seus dados
- Correção de dados incorretos
- Exclusão dos dados
- Portabilidade dos dados
- Revogação do consentimento

Para exercer seus direitos, entre em contato conosco através de privacy@mia-enterprise.com

Este consentimento pode ser revogado a qualquer momento.
        """.strip()
        
        return consent_text
    
    def _generate_consent_proof(self, consent_id: str, consent_given: bool) -> str:
        """Generiraj dokaz privolitve"""
        proof_data = f"{consent_id}_{consent_given}_{self._get_build_timestamp().isoformat()}"
        return hashlib.sha256(proof_data.encode()).hexdigest()
    
    def get_consent_dashboard(self) -> Dict[str, Any]:
        """Pridobi consent dashboard"""
        total_consents = len(self.consents)
        active_consents = sum(1 for c in self.consents.values() if c["status"] == "active")
        withdrawn_consents = sum(1 for c in self.consents.values() if c["status"] == "withdrawn")
        
        return {
            "total_consents": total_consents,
            "active_consents": active_consents,
            "withdrawn_consents": withdrawn_consents,
            "consent_rate": (active_consents / total_consents * 100) if total_consents > 0 else 0,
            "templates_count": len(self.consent_templates),
            "last_updated": self._get_build_timestamp().isoformat()
        }
