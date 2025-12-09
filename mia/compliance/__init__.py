"""
MIA Enterprise AGI - Compliance Module
=====================================

LGPD and regulatory compliance management system.
"""

from .lgpd_manager import LGPDComplianceManager
from .consent_manager import ConsentManager
from .data_processor import DataProcessor
from .audit_system import ComplianceAuditSystem
from .privacy_manager import PrivacyManager

__all__ = [
    'LGPDComplianceManager',
    'ConsentManager',
    'DataProcessor',
    'ComplianceAuditSystem',
    'PrivacyManager'
]