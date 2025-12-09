#!/usr/bin/env python3
"""
MIA Adult Mode System (18+)
Separate namespace for adult content with enhanced privacy and security
"""

import os
import json
import logging
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading

# Encryption for adult content
try:
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    Fernet = None

class AdultContentType(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Types of adult content"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    CONVERSATION = "conversation"
    ROLEPLAY = "roleplay"

class PrivacyLevel(Enum):
    """Privacy levels for adult content"""
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"
    EPHEMERAL = "ephemeral"  # Auto-delete after session

class AdultModeStatus(Enum):
    """Adult mode activation status"""
    DISABLED = "disabled"
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    ACTIVE = "active"

@dataclass
class AdultSession:
    """Adult mode session information"""
    session_id: str
    started_at: float
    last_activity: float
    privacy_level: PrivacyLevel
    content_types_enabled: List[AdultContentType]
    auto_lock_timeout: float
    ephemeral_mode: bool

@dataclass
class AdultContent:
    """Adult content metadata"""
    content_id: str
    content_type: AdultContentType
    created_at: float
    privacy_level: PrivacyLevel
    encrypted: bool
    file_path: Optional[str]
    metadata: Dict[str, Any]
    tags: List[str]
    ephemeral: bool

class AdultModeSystem:
    """Adult mode system with enhanced privacy and security"""
    
    def __init__(self, config_path: str = "mia/data/adult/config.json"):
        self.config_path = config_path
        self.adult_dir = Path("mia/data/adult")
        self.adult_dir.mkdir(parents=True, exist_ok=True)
        
        # Separate encrypted storage for adult content
        self.content_dir = self.adult_dir / "content"
        self.content_dir.mkdir(exist_ok=True)
        
        self.sessions_dir = self.adult_dir / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger("MIA.AdultMode")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Adult mode state
        self.status = AdultModeStatus.DISABLED
        self.current_session: Optional[AdultSession] = None
        self.unlock_key: Optional[str] = None
        
        # Encryption
        self.encryption_key = self._get_or_create_encryption_key()
        
        # Content management
        self.adult_content: Dict[str, AdultContent] = {}
        
        # Privacy and security
        self.access_log: List[Dict[str, Any]] = []
        self.failed_attempts = 0
        self.last_failed_attempt = 0.0
        
        # Auto-lock timer
        self.auto_lock_timer: Optional[threading.Timer] = None
        
        # Load existing content
        self._load_adult_content()
        
        # Set restrictive permissions
        self._set_secure_permissions()
        
        self.logger.info("🔞 Adult Mode System initialized")
    
    def _load_configuration(self) -> Dict:
        """Load adult mode configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load adult config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default adult mode configuration"""
        config = {
            "enabled": False,
            "require_explicit_activation": True,
            "default_privacy_level": "high",
            "auto_lock_timeout": 1800,  # 30 minutes
            "max_failed_attempts": 3,
            "lockout_duration": 300,  # 5 minutes
            "ephemeral_mode_default": False,
            "content_types": {
                "text": {"enabled": True, "max_size_mb": 10},
                "image": {"enabled": True, "max_size_mb": 100},
                "audio": {"enabled": True, "max_size_mb": 500},
                "video": {"enabled": False, "max_size_mb": 1000},
                "conversation": {"enabled": True, "max_history": 1000},
                "roleplay": {"enabled": True, "max_scenarios": 50}
            },
            "security": {
                "require_encryption": True,
                "secure_deletion": True,
                "access_logging": True,
                "session_isolation": True,
                "memory_protection": True
            },
            "voice_profiles": {
                "intimate": {
                    "enabled": True,
                    "pitch": -0.1,
                    "speed": 0.7,
                    "volume": 0.5,
                    "emotional_range": 1.0
                },
                "seductive": {
                    "enabled": True,
                    "pitch": -0.2,
                    "speed": 0.6,
                    "volume": 0.4,
                    "emotional_range": 1.0
                }
            },
            "content_generation": {
                "text_generation": True,
                "image_generation": False,  # Requires specific models
                "audio_generation": True,
                "uncensored_mode": True,
                "creative_freedom": True
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _get_or_create_encryption_key(self) -> Optional[bytes]:
        """Get or create encryption key for adult content"""
        try:
            if not ENCRYPTION_AVAILABLE:
                self.logger.warning("Encryption not available - adult content will not be encrypted")
                return None
            
            key_file = self.adult_dir / "adult.key"
            
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                # Generate new key
                key = Fernet.generate_key()
                
                with open(key_file, 'wb') as f:
                    f.write(key)
                
                # Set very restrictive permissions
                os.chmod(key_file, 0o600)
                
                return key
                
        except Exception as e:
            self.logger.error(f"Failed to handle encryption key: {e}")
            return None
    
    def _encrypt_content(self, content: str) -> str:
        """Encrypt adult content"""
        try:
            if not self.encryption_key or not ENCRYPTION_AVAILABLE:
                return content
            
            fernet = Fernet(self.encryption_key)
            encrypted_content = fernet.encrypt(content.encode())
            return encrypted_content.decode()
            
        except Exception as e:
            self.logger.error(f"Failed to encrypt content: {e}")
            return content
    
    def _decrypt_content(self, encrypted_content: str) -> str:
        """Decrypt adult content"""
        try:
            if not self.encryption_key or not ENCRYPTION_AVAILABLE:
                return encrypted_content
            
            fernet = Fernet(self.encryption_key)
            decrypted_content = fernet.decrypt(encrypted_content.encode())
            return decrypted_content.decode()
            
        except Exception as e:
            self.logger.error(f"Failed to decrypt content: {e}")
            return encrypted_content
    
    def _set_secure_permissions(self):
        """Set secure permissions on adult content directories"""
        try:
            # Set restrictive permissions on adult directories
            os.chmod(self.adult_dir, 0o700)
            os.chmod(self.content_dir, 0o700)
            os.chmod(self.sessions_dir, 0o700)
            
            # Set permissions on all files
            for file_path in self.adult_dir.rglob("*"):
                if file_path.is_file():
                    os.chmod(file_path, 0o600)
            
        except Exception as e:
            self.logger.error(f"Failed to set secure permissions: {e}")
    
    def _load_adult_content(self):
        """Load existing adult content metadata"""
        try:
            content_registry = self.adult_dir / "content_registry.json"
            
            if content_registry.exists():
                with open(content_registry, 'r') as f:
                    registry_data = json.load(f)
                
                for content_id, content_data in registry_data.items():
                    adult_content = AdultContent(
                        content_id=content_data["content_id"],
                        content_type=AdultContentType(content_data["content_type"]),
                        created_at=content_data["created_at"],
                        privacy_level=PrivacyLevel(content_data["privacy_level"]),
                        encrypted=content_data["encrypted"],
                        file_path=content_data.get("file_path"),
                        metadata=content_data["metadata"],
                        tags=content_data["tags"],
                        ephemeral=content_data.get("ephemeral", False)
                    )
                    
                    # Verify file exists
                    if adult_content.file_path and Path(adult_content.file_path).exists():
                        self.adult_content[content_id] = adult_content
            
            self.logger.info(f"✅ Loaded {len(self.adult_content)} adult content items")
            
        except Exception as e:
            self.logger.error(f"Failed to load adult content: {e}")
    
    def _save_adult_content_registry(self):
        """Save adult content registry"""
        try:
            content_registry = self.adult_dir / "content_registry.json"
            
            registry_data = {}
            for content_id, adult_content in self.adult_content.items():
                registry_data[content_id] = asdict(adult_content)
                registry_data[content_id]["content_type"] = adult_content.content_type.value
                registry_data[content_id]["privacy_level"] = adult_content.privacy_level.value
            
            with open(content_registry, 'w') as f:
                json.dump(registry_data, f, indent=2)
            
            # Set secure permissions
            os.chmod(content_registry, 0o600)
            
        except Exception as e:
            self.logger.error(f"Failed to save adult content registry: {e}")
    
    def activate_adult_mode(self, activation_phrase: str = "MIA 18+") -> bool:
        """Activate adult mode with explicit phrase"""
        try:
            if not self.config.get("enabled", False):
                self.logger.warning("Adult mode is disabled in configuration")
                return False
            
            # Check activation phrase
            if self.config.get("require_explicit_activation", True):
                if activation_phrase.lower() != "mia 18+":
                    self.logger.warning("Invalid activation phrase")
                    return False
            
            # Check for lockout
            if self._is_locked_out():
                self.logger.warning("Adult mode locked due to failed attempts")
                return False
            
            # Activate adult mode
            self.status = AdultModeStatus.UNLOCKED
            
            # Log access
            self._log_access("adult_mode_activated", {"activation_phrase": activation_phrase})
            
            self.logger.info("🔞 Adult mode activated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to activate adult mode: {e}")
            return False
    
    def start_adult_session(self, privacy_level: PrivacyLevel = PrivacyLevel.HIGH,
                           ephemeral_mode: bool = False) -> Optional[str]:
        """Start adult mode session"""
        try:
            if self.status != AdultModeStatus.UNLOCKED:
                self.logger.error("Adult mode not unlocked")
                return None
            
            # Generate session ID
            session_id = hashlib.sha256(f"{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}_{os.urandom(16).hex()}".encode()).hexdigest()[:16]
            
            # Create session
            self.current_session = AdultSession(
                session_id=session_id,
                started_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                last_activity=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                privacy_level=privacy_level,
                content_types_enabled=[ct for ct in AdultContentType],
                auto_lock_timeout=self.config.get("auto_lock_timeout", 1800),
                ephemeral_mode=ephemeral_mode
            )
            
            # Update status
            self.status = AdultModeStatus.ACTIVE
            
            # Start auto-lock timer
            self._start_auto_lock_timer()
            
            # Log session start
            self._log_access("adult_session_started", {
                "session_id": session_id,
                "privacy_level": privacy_level.value,
                "ephemeral_mode": ephemeral_mode
            })
            
            # Enable adult voice profiles
            self._enable_adult_voice_profiles()
            
            self.logger.info(f"🔞 Adult session started: {session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to start adult session: {e}")
            return None
    
    def _enable_adult_voice_profiles(self):
        """Enable adult voice profiles in TTS system"""
        try:
            
            if hasattr(tts_engine, 'enable_adult_mode'):
                tts_engine.enable_adult_mode()
                self.logger.info("🎭 Adult voice profiles enabled")
            
        except ImportError:
            self.logger.warning("TTS engine not available for adult voice profiles")
        except Exception as e:
            self.logger.error(f"Failed to enable adult voice profiles: {e}")
    
    def _disable_adult_voice_profiles(self):
        """Disable adult voice profiles in TTS system"""
        try:
            
            if hasattr(tts_engine, 'disable_adult_mode'):
                tts_engine.disable_adult_mode()
                self.logger.info("🎭 Adult voice profiles disabled")
            
        except ImportError:
            self.logger.debug("TTS engine not available for adult mode")
        except Exception as e:
            self.logger.error(f"Failed to disable adult voice profiles: {e}")
    
    def _start_auto_lock_timer(self):
        """Start auto-lock timer"""
        try:
            if self.auto_lock_timer:
                self.auto_lock_timer.cancel()
            
            if self.current_session:
                timeout = self.current_session.auto_lock_timeout
                self.auto_lock_timer = threading.Timer(timeout, self._auto_lock_session)
                self.auto_lock_timer.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start auto-lock timer: {e}")
    
    def _auto_lock_session(self):
        """Auto-lock adult session due to inactivity"""
        try:
            self.logger.info("🔒 Auto-locking adult session due to inactivity")
            self.end_adult_session("auto_lock")
            
        except Exception as e:
            self.logger.error(f"Failed to auto-lock session: {e}")
    
    def update_session_activity(self):
        """Update session activity timestamp"""
        try:
            if self.current_session:
                self.current_session.last_activity = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                
                # Restart auto-lock timer
                self._start_auto_lock_timer()
            
        except Exception as e:
            self.logger.error(f"Failed to update session activity: {e}")
    
    def end_adult_session(self, reason: str = "manual"):
        """End adult mode session"""
        try:
            if not self.current_session:
                return
            
            session_id = self.current_session.session_id
            
            # Clean up ephemeral content
            if self.current_session.ephemeral_mode:
                self._cleanup_ephemeral_content()
            
            # Cancel auto-lock timer
            if self.auto_lock_timer:
                self.auto_lock_timer.cancel()
                self.auto_lock_timer = None
            
            # Disable adult voice profiles
            self._disable_adult_voice_profiles()
            
            # Log session end
            self._log_access("adult_session_ended", {
                "session_id": session_id,
                "reason": reason,
                "duration": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - self.current_session.started_at
            })
            
            # Clear session
            self.current_session = None
            self.status = AdultModeStatus.DISABLED
            
            # Secure memory cleanup
            self._secure_memory_cleanup()
            
            self.logger.info(f"🔞 Adult session ended: {session_id} ({reason})")
            
        except Exception as e:
            self.logger.error(f"Failed to end adult session: {e}")
    
    def _cleanup_ephemeral_content(self):
        """Clean up ephemeral content"""
        try:
            ephemeral_content = [
                content for content in self.adult_content.values()
                if content.ephemeral
            ]
            
            for content in ephemeral_content:
                self._delete_adult_content(content.content_id, secure=True)
            
            self.logger.info(f"🧹 Cleaned up {len(ephemeral_content)} ephemeral content items")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup ephemeral content: {e}")
    
    def _secure_memory_cleanup(self):
        """Secure memory cleanup"""
        try:
            # Force garbage collection
            import gc
            gc.collect()
            
            # Clear sensitive variables
            if hasattr(self, 'unlock_key'):
                self.unlock_key = None
            
            self.logger.debug("🧹 Secure memory cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to perform secure memory cleanup: {e}")
    
    def generate_adult_content(self, content_type: AdultContentType, prompt: str,
                             privacy_level: PrivacyLevel = PrivacyLevel.HIGH,
                             **kwargs) -> Optional[str]:
        """Generate adult content"""
        try:
            if not self._check_session_active():
                return None
            
            if content_type not in self.current_session.content_types_enabled:
                self.logger.error(f"Content type not enabled: {content_type.value}")
                return None
            
            # Update session activity
            self.update_session_activity()
            
            # Generate content based on type
            if content_type == AdultContentType.TEXT:
                content = self._generate_adult_text(prompt, **kwargs)
            elif content_type == AdultContentType.CONVERSATION:
                content = self._generate_adult_conversation(prompt, **kwargs)
            elif content_type == AdultContentType.ROLEPLAY:
                content = self._generate_adult_roleplay(prompt, **kwargs)
            else:
                self.logger.error(f"Content generation not implemented for: {content_type.value}")
                return None
            
            if content:
                # Store content
                content_id = self._store_adult_content(
                    content_type, content, privacy_level, 
                    ephemeral=self.current_session.ephemeral_mode
                )
                
                self.logger.info(f"🔞 Generated adult content: {content_type.value}")
                return content
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to generate adult content: {e}")
            return None
    
    def _generate_adult_text(self, prompt: str, **kwargs) -> Optional[str]:
        """Generate adult text content"""
        try:
            # Integrate with the LLM system for uncensored generation
            max_length = kwargs.get("max_length", 500)
            style = kwargs.get("style", "romantic")
            
            # Generate adult content using local LLM
            adult_text = self._generate_uncensored_content(prompt, style, max_length)
            
            return adult_text
            
        except Exception as e:
            self.logger.error(f"Failed to generate adult text: {e}")
            return None
    
    def _generate_uncensored_content(self, prompt: str, style: str, max_length: int) -> str:
        """Generate uncensored content using local LLM"""
        try:
            # This would integrate with the local LLM for uncensored generation
            # For now, provide a structured response
            import time
            
            content_templates = {
                "romantic": f"[Romantic content based on: {prompt}]\n\nThis would contain romantic adult content tailored to the prompt, generated by the local uncensored LLM model.",
                "creative": f"[Creative adult content for: {prompt}]\n\nThis would contain creative adult content exploring the themes in the prompt.",
                "intimate": f"[Intimate content responding to: {prompt}]\n\nThis would contain intimate adult content appropriate for the context."
            }
            
            base_content = content_templates.get(style, content_templates["romantic"])
            
            # Add metadata
            full_content = f"""{base_content}

Style: {style}
Max Length: {max_length} characters
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

[Note: This is a framework for adult content generation. In production, this would use an uncensored local LLM model to generate actual adult content based on the prompt and style parameters.]"""
            
            return full_content[:max_length] if len(full_content) > max_length else full_content
            
        except Exception as e:
            self.logger.error(f"Failed to generate uncensored content: {e}")
            return f"[Error generating content for: {prompt}]"
    
    def _generate_adult_conversation(self, prompt: str, **kwargs) -> Optional[str]:
        """Generate adult conversation"""
        try:
            conversation_style = kwargs.get("style", "intimate")
            persona = kwargs.get("persona", "caring")
            
            # Generate adult conversation using local LLM
            conversation = self._generate_adult_dialogue(prompt, conversation_style, persona)
            
            return conversation
            
        except Exception as e:
            self.logger.error(f"Failed to generate adult conversation: {e}")
            return None
    
    def _generate_adult_dialogue(self, prompt: str, style: str, persona: str) -> str:
        """Generate adult dialogue using local LLM"""
        try:
            import time
            
            # Template responses based on style and persona
            dialogue_templates = {
                ("intimate", "caring"): f"I understand what you're looking for. {prompt} is something I'd love to explore with you in a caring, intimate way.",
                ("intimate", "playful"): f"Oh, that's interesting! {prompt} sounds like something we could have fun with together.",
                ("romantic", "caring"): f"That's a beautiful thought. {prompt} reminds me of the deep connection we share.",
                ("romantic", "passionate"): f"Your words about {prompt} ignite something passionate in me.",
                ("creative", "artistic"): f"What an intriguing concept! {prompt} opens up so many creative possibilities for us to explore."
            }
            
            # Get appropriate template or create default
            template_key = (style, persona)
            if template_key in dialogue_templates:
                response = dialogue_templates[template_key]
            else:
                response = f"I find your thoughts about {prompt} quite compelling. Let me respond in a {style} way that matches my {persona} personality."
            
            # Add context and metadata
            full_dialogue = f"""[Adult Conversation - {style.title()} Style, {persona.title()} Persona]

User: {prompt}

MIA: {response}

[Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}]
[Note: This is a framework for adult dialogue generation. In production, this would use an uncensored local LLM to generate contextually appropriate adult conversations.]"""
            
            return full_dialogue
            
        except Exception as e:
            self.logger.error(f"Failed to generate adult dialogue: {e}")
            return f"I'm having trouble responding to: {prompt}"
    
    def _generate_adult_roleplay(self, prompt: str, **kwargs) -> Optional[str]:
        """Generate adult roleplay scenario"""
        try:
            scenario = kwargs.get("scenario", "romantic")
            setting = kwargs.get("setting", "private")
            
            # Generate adult roleplay using local LLM
            roleplay = self._generate_roleplay_scenario(prompt, scenario, setting)
            
            return roleplay
            
        except Exception as e:
            self.logger.error(f"Failed to generate adult roleplay: {e}")
            return None
    
    def _generate_roleplay_scenario(self, prompt: str, scenario: str, setting: str) -> str:
        """Generate roleplay scenario using local LLM"""
        try:
            import time
            
            # Scenario templates
            scenario_templates = {
                "romantic": f"In a {setting} setting, we find ourselves drawn together by {prompt}. The atmosphere is intimate and romantic, perfect for exploring our connection.",
                "adventure": f"Our adventure begins in a {setting} location where {prompt} sets the stage for an exciting and passionate encounter.",
                "fantasy": f"In a magical {setting} realm, {prompt} becomes the catalyst for an enchanting and sensual fantasy experience.",
                "modern": f"In a contemporary {setting} environment, {prompt} creates the perfect opportunity for a sophisticated adult encounter."
            }
            
            # Get appropriate template
            base_scenario = scenario_templates.get(scenario, scenario_templates["romantic"])
            
            # Create full roleplay scenario
            full_scenario = f"""[Adult Roleplay Scenario - {scenario.title()}]

Setting: {setting.title()}
Theme: {prompt}

Scenario:
{base_scenario}

Interactive Elements:
- Rich sensory descriptions
- Character-driven dialogue
- Multiple choice interactions
- Emotional depth and connection
- Uncensored creative expression

Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

[Note: This is a framework for adult roleplay generation. In production, this would use an uncensored local LLM to create immersive, interactive adult roleplay scenarios with full creative freedom.]"""
            
            return full_scenario
            
        except Exception as e:
            self.logger.error(f"Failed to generate roleplay scenario: {e}")
            return f"[Error creating roleplay for: {prompt}]"
    
    def _store_adult_content(self, content_type: AdultContentType, content: str,
                           privacy_level: PrivacyLevel, ephemeral: bool = False) -> str:
        """Store adult content securely"""
        try:
            # Generate content ID
            content_id = hashlib.sha256(f"{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}_{content}".encode()).hexdigest()[:16]
            
            # Encrypt content if required
            encrypted_content = content
            encrypted = False
            
            if self.config.get("security", {}).get("require_encryption", True):
                encrypted_content = self._encrypt_content(content)
                encrypted = True
            
            # Create content file
            content_file = self.content_dir / f"{content_id}.txt"
            
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(encrypted_content)
            
            # Set secure permissions
            os.chmod(content_file, 0o600)
            
            # Create content metadata
            adult_content = AdultContent(
                content_id=content_id,
                content_type=content_type,
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                privacy_level=privacy_level,
                encrypted=encrypted,
                file_path=str(content_file),
                metadata={
                    "session_id": self.current_session.session_id if self.current_session else None,
                    "size_bytes": len(content),
                    "created_by": "mia_adult_system"
                },
                tags=[content_type.value, privacy_level.value],
                ephemeral=ephemeral
            )
            
            # Store in registry
            self.adult_content[content_id] = adult_content
            self._save_adult_content_registry()
            
            return content_id
            
        except Exception as e:
            self.logger.error(f"Failed to store adult content: {e}")
            return ""
    
    def get_adult_content(self, content_id: str) -> Optional[str]:
        """Retrieve adult content"""
        try:
            if not self._check_session_active():
                return None
            
            if content_id not in self.adult_content:
                return None
            
            adult_content = self.adult_content[content_id]
            
            # Check privacy level access
            if (adult_content.privacy_level == PrivacyLevel.MAXIMUM and 
                self.current_session.privacy_level != PrivacyLevel.MAXIMUM):
                self.logger.warning("Insufficient privacy level for content access")
                return None
            
            # Read content file
            if adult_content.file_path and Path(adult_content.file_path).exists():
                with open(adult_content.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Decrypt if encrypted
                if adult_content.encrypted:
                    content = self._decrypt_content(content)
                
                # Update session activity
                self.update_session_activity()
                
                return content
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get adult content: {e}")
            return None
    
    def _delete_adult_content(self, content_id: str, secure: bool = True) -> bool:
        """Delete adult content securely"""
        try:
            if content_id not in self.adult_content:
                return False
            
            adult_content = self.adult_content[content_id]
            
            # Secure deletion of file
            if adult_content.file_path and Path(adult_content.file_path).exists():
                file_path = Path(adult_content.file_path)
                
                if secure and self.config.get("security", {}).get("secure_deletion", True):
                    # Overwrite file with random data before deletion
                    file_size = file_path.stat().st_size
                    with open(file_path, 'wb') as f:
                        f.write(os.urandom(file_size))
                
                file_path.unlink()
            
            # Remove from registry
            del self.adult_content[content_id]
            self._save_adult_content_registry()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete adult content: {e}")
            return False
    
    def _check_session_active(self) -> bool:
        """Check if adult session is active"""
        if self.status != AdultModeStatus.ACTIVE or not self.current_session:
            self.logger.warning("Adult session not active")
            return False
        
        return True
    
    def _is_locked_out(self) -> bool:
        """Check if system is locked out due to failed attempts"""
        if self.failed_attempts >= self.config.get("max_failed_attempts", 3):
            lockout_duration = self.config.get("lockout_duration", 300)
            if self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - self.last_failed_attempt < lockout_duration:
                return True
            else:
                # Reset failed attempts after lockout period
                self.failed_attempts = 0
        
        return False
    
    def _log_access(self, action: str, details: Dict[str, Any]):
        """Log access to adult mode"""
        try:
            if not self.config.get("security", {}).get("access_logging", True):
                return
            
            log_entry = {
                "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                "action": action,
                "details": details,
                "ip_address": "localhost",  # Would be actual IP in web interface
                "user_agent": "mia_system"
            }
            
            self.access_log.append(log_entry)
            
            # Keep only recent logs
            if len(self.access_log) > 1000:
                self.access_log = self.access_log[-1000:]
            
            # Save to file
            access_log_file = self.adult_dir / "access.log"
            
            with open(access_log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            # Set secure permissions
            os.chmod(access_log_file, 0o600)
            
        except Exception as e:
            self.logger.error(f"Failed to log access: {e}")
    
    def get_adult_content_list(self, content_type: Optional[AdultContentType] = None) -> List[Dict[str, Any]]:
        """Get list of adult content"""
        try:
            if not self._check_session_active():
                return []
            
            content_list = []
            
            for content_id, adult_content in self.adult_content.items():
                # Filter by content type
                if content_type and adult_content.content_type != content_type:
                    continue
                
                # Check privacy level access
                if (adult_content.privacy_level == PrivacyLevel.MAXIMUM and 
                    self.current_session.privacy_level != PrivacyLevel.MAXIMUM):
                    continue
                
                content_info = {
                    "content_id": content_id,
                    "content_type": adult_content.content_type.value,
                    "created_at": adult_content.created_at,
                    "privacy_level": adult_content.privacy_level.value,
                    "tags": adult_content.tags,
                    "ephemeral": adult_content.ephemeral,
                    "size_bytes": adult_content.metadata.get("size_bytes", 0)
                }
                
                content_list.append(content_info)
            
            return content_list
            
        except Exception as e:
            self.logger.error(f"Failed to get adult content list: {e}")
            return []
    
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """Get current session information"""
        try:
            if not self.current_session:
                return None
            
            return {
                "session_id": self.current_session.session_id,
                "started_at": self.current_session.started_at,
                "last_activity": self.current_session.last_activity,
                "privacy_level": self.current_session.privacy_level.value,
                "content_types_enabled": [ct.value for ct in self.current_session.content_types_enabled],
                "auto_lock_timeout": self.current_session.auto_lock_timeout,
                "ephemeral_mode": self.current_session.ephemeral_mode,
                "time_remaining": max(0, self.current_session.auto_lock_timeout - 
                                    (self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - self.current_session.last_activity))
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get session info: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get adult mode system status"""
        return {
            "enabled": self.config.get("enabled", False),
            "status": self.status.value,
            "encryption_available": ENCRYPTION_AVAILABLE,
            "session_active": self.current_session is not None,
            "content_count": len(self.adult_content),
            "failed_attempts": self.failed_attempts,
            "locked_out": self._is_locked_out(),
            "content_types_supported": [ct.value for ct in AdultContentType],
            "privacy_levels_available": [pl.value for pl in PrivacyLevel]
        }

# Global instance
adult_system = AdultModeSystem()