"""
MIA Core Identity Module
Deterministična osebnostna matrika z introspektivno integracijo
"""

from .self_model import (
    SelfIdentityModel,
    PhysicalAttributes,
    BehavioralTraits,
    PersonalityCore,
    get_self_identity,
    get_self_description,
    perform_self_reflection,
    get_introspective_thoughts
)

__all__ = [
    'SelfIdentityModel',
    'PhysicalAttributes', 
    'BehavioralTraits',
    'PersonalityCore',
    'get_self_identity',
    'get_self_description',
    'perform_self_reflection',
    'get_introspective_thoughts'
]