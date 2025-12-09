"""
MIA Enterprise AGI - Desktop Builder Module
==========================================

Modularized cross-platform desktop application builder.
"""

from .platform_detector import PlatformDetector
from .build_system import BuildSystem
from .deployment_manager import DeploymentManager
from .cross_platform_utils import CrossPlatformUtils

__all__ = [
    'PlatformDetector',
    'BuildSystem',
    'DeploymentManager',
    'CrossPlatformUtils'
]