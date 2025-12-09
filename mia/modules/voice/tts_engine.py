#!/usr/bin/env python3
"""
MIA Text-to-Speech Engine
Advanced TTS with emotional expression and voice cloning
"""

import os
import json
import logging
import time
import threading
import queue
import wave
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import tempfile

# Audio playback
try:
    import pyaudio
    import pygame
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    pyaudio = None
    pygame = None

# TTS engines
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    pyttsx3 = None

class VoiceGender(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Voice gender options"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

class EmotionalExpression(Enum):
    """Emotional expressions for TTS"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CALM = "calm"
    CONFIDENT = "confident"
    GENTLE = "gentle"
    PROFESSIONAL = "professional"
    INTIMATE = "intimate"  # For 18+ mode
    SEDUCTIVE = "seductive"  # For 18+ mode

class SpeechSpeed(Enum):
    """Speech speed options"""
    VERY_SLOW = "very_slow"
    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"
    VERY_FAST = "very_fast"

@dataclass
class VoiceProfile:
    """Voice profile configuration"""
    name: str
    gender: VoiceGender
    language: str
    pitch: float  # -1.0 to 1.0
    speed: float  # 0.5 to 2.0
    volume: float  # 0.0 to 1.0
    emotional_range: float  # 0.0 to 1.0
    voice_id: Optional[str] = None
    lora_model: Optional[str] = None

@dataclass
class SpeechRequest:
    """Speech synthesis request"""
    text: str
    voice_profile: VoiceProfile
    emotional_expression: EmotionalExpression
    speed_override: Optional[float] = None
    pitch_override: Optional[float] = None
    volume_override: Optional[float] = None
    callback: Optional[Callable] = None

@dataclass
class SpeechResult:
    """Speech synthesis result"""
    success: bool
    audio_file: Optional[str]
    duration: float
    text: str
    voice_profile: str
    emotional_expression: str
    error_message: Optional[str] = None

class TTSEngine:
    """Text-to-Speech Engine with emotional expression"""
    
    def __init__(self, config_path: str = "mia/data/voice/tts_config.json"):
        self.config_path = config_path
        self.voice_dir = Path("mia/data/voice")
        self.voice_dir.mkdir(parents=True, exist_ok=True)
        
        self.audio_output_dir = self.voice_dir / "output"
        self.audio_output_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger("MIA.TTSEngine")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Voice profiles
        self.voice_profiles: Dict[str, VoiceProfile] = {}
        self.current_voice_profile: Optional[VoiceProfile] = None
        
        # TTS engines
        self.pyttsx3_engine = None
        self.xtts_engine = None
        
        # Audio system
        self.audio_system = None
        
        # Speech queue
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.speech_thread = None
        
        # Initialize components
        self._initialize_voice_profiles()
        self._initialize_tts_engines()
        self._initialize_audio_system()
        self._start_speech_thread()
        
        self.logger.info("🔊 TTS Engine initialized")
    
    def _load_configuration(self) -> Dict:
        """Load TTS configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load TTS config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default TTS configuration"""
        config = {
            "enabled": True,
            "default_voice": "mia_female",
            "audio_format": "wav",
            "sample_rate": 22050,
            "emotional_synthesis": True,
            "voice_cloning": False,
            "real_time_synthesis": True,
            "audio_effects": True,
            "adult_mode_voices": False,
            "engines": {
                "pyttsx3": {
                    "enabled": True,
                    "rate": 200,
                    "volume": 0.8
                },
                "xtts": {
                    "enabled": False,
                    "model_path": "models/xtts",
                    "speaker_wav": "voices/reference.wav"
                }
            },
            "voice_profiles": {
                "mia_female": {
                    "name": "MIA Female",
                    "gender": "female",
                    "language": "en",
                    "pitch": 0.1,
                    "speed": 1.0,
                    "volume": 0.8,
                    "emotional_range": 0.7
                },
                "mia_male": {
                    "name": "MIA Male",
                    "gender": "male",
                    "language": "en",
                    "pitch": -0.2,
                    "speed": 1.0,
                    "volume": 0.8,
                    "emotional_range": 0.6
                },
                "mia_professional": {
                    "name": "MIA Professional",
                    "gender": "neutral",
                    "language": "en",
                    "pitch": 0.0,
                    "speed": 0.9,
                    "volume": 0.7,
                    "emotional_range": 0.3
                }
            },
            "emotional_modifiers": {
                "happy": {"pitch": 0.2, "speed": 1.1, "volume": 0.9},
                "sad": {"pitch": -0.2, "speed": 0.8, "volume": 0.6},
                "excited": {"pitch": 0.3, "speed": 1.3, "volume": 1.0},
                "calm": {"pitch": -0.1, "speed": 0.9, "volume": 0.7},
                "confident": {"pitch": 0.1, "speed": 1.0, "volume": 0.9},
                "gentle": {"pitch": 0.0, "speed": 0.8, "volume": 0.6},
                "professional": {"pitch": 0.0, "speed": 0.9, "volume": 0.8},
                "intimate": {"pitch": -0.1, "speed": 0.7, "volume": 0.5},
                "seductive": {"pitch": -0.2, "speed": 0.6, "volume": 0.4}
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _initialize_voice_profiles(self):
        """Initialize voice profiles"""
        try:
            profiles_config = self.config.get("voice_profiles", {})
            
            for profile_name, profile_data in profiles_config.items():
                voice_profile = VoiceProfile(
                    name=profile_data["name"],
                    gender=VoiceGender(profile_data["gender"]),
                    language=profile_data["language"],
                    pitch=profile_data["pitch"],
                    speed=profile_data["speed"],
                    volume=profile_data["volume"],
                    emotional_range=profile_data["emotional_range"],
                    voice_id=profile_data.get("voice_id"),
                    lora_model=profile_data.get("lora_model")
                )
                
                self.voice_profiles[profile_name] = voice_profile
            
            # Set default voice
            default_voice = self.config.get("default_voice", "mia_female")
            if default_voice in self.voice_profiles:
                self.current_voice_profile = self.voice_profiles[default_voice]
            
            self.logger.info(f"✅ Loaded {len(self.voice_profiles)} voice profiles")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize voice profiles: {e}")
    
    def _initialize_tts_engines(self):
        """Initialize TTS engines"""
        try:
            # Initialize pyttsx3
            if PYTTSX3_AVAILABLE and self.config["engines"]["pyttsx3"]["enabled"]:
                self.pyttsx3_engine = pyttsx3.init()
                
                # Configure pyttsx3
                pyttsx3_config = self.config["engines"]["pyttsx3"]
                self.pyttsx3_engine.setProperty('rate', pyttsx3_config["rate"])
                self.pyttsx3_engine.setProperty('volume', pyttsx3_config["volume"])
                
                self.logger.info("✅ pyttsx3 engine initialized")
            
            # Initialize XTTS engine
            if self.config["engines"]["xtts"]["enabled"]:
                try:
                    self._initialize_xtts_engine()
                    self.logger.info("✅ XTTS engine initialized")
                except Exception as e:
                    self.logger.warning(f"XTTS engine initialization failed: {e}")
                    self.logger.info("Continuing with available engines")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS engines: {e}")
    
    def _initialize_xtts_engine(self):
        """Initialize XTTS (Coqui TTS) engine"""
        try:
            # Try to import XTTS dependencies
            try:
                import torch
                from TTS.api import TTS
                self.xtts_available = True
            except ImportError as e:
                self.logger.warning(f"XTTS dependencies not available: {e}")
                self.xtts_available = False
                return
            
            # Initialize XTTS model
            xtts_config = self.config["engines"]["xtts"]
            model_name = xtts_config.get("model", "tts_models/multilingual/multi-dataset/xtts_v2")
            
            self.xtts_engine = TTS(model_name=model_name)
            
            # Set device (GPU if available, CPU otherwise)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.xtts_engine.to(device)
            
            self.logger.info(f"XTTS engine initialized on {device}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize XTTS engine: {e}")
            self.xtts_available = False
            raise
    
    def _initialize_audio_system(self):
        """Initialize audio playback system"""
        try:
            if AUDIO_AVAILABLE:
                pygame.mixer.init(
                    frequency=self.config.get("sample_rate", 22050),
                    size=-16,
                    channels=2,
                    buffer=1024
                )
                self.audio_system = "pygame"
                self.logger.info("✅ Audio system initialized (pygame)")
            else:
                self.logger.warning("Audio system not available")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize audio system: {e}")
    
    def _start_speech_thread(self):
        """Start speech processing thread"""
        try:
            self.speech_thread = threading.Thread(target=self._speech_processing_loop, daemon=True)
            self.speech_thread.start()
            
            self.logger.info("✅ Speech processing thread started")
            
        except Exception as e:
            self.logger.error(f"Failed to start speech thread: {e}")
    
    def _speech_processing_loop(self):
        """Speech processing loop"""
        while True:
            try:
                # Get speech request from queue
                try:
                    request = self.speech_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process speech request
                result = self._synthesize_speech(request)
                
                # Play audio if synthesis was successful
                if result.success and result.audio_file:
                    self._play_audio_file(result.audio_file)
                
                # Call callback if provided
                if request.callback:
                    try:
                        request.callback(result)
                    except Exception as e:
                        self.logger.error(f"Callback error: {e}")
                
                # Mark task as done
                self.speech_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Speech processing error: {e}")
    
    def speak(self, text: str, voice_profile: Optional[str] = None,
              emotional_expression: EmotionalExpression = EmotionalExpression.NEUTRAL,
              callback: Optional[Callable] = None, **kwargs) -> bool:
        """Queue text for speech synthesis"""
        try:
            if not self.config.get("enabled", True):
                self.logger.warning("TTS is disabled")
                return False
            
            # Get voice profile
            if voice_profile and voice_profile in self.voice_profiles:
                profile = self.voice_profiles[voice_profile]
            else:
                profile = self.current_voice_profile or list(self.voice_profiles.values())[0]
            
            # Create speech request
            request = SpeechRequest(
                text=text,
                voice_profile=profile,
                emotional_expression=emotional_expression,
                speed_override=kwargs.get("speed"),
                pitch_override=kwargs.get("pitch"),
                volume_override=kwargs.get("volume"),
                callback=callback
            )
            
            # Queue request
            self.speech_queue.put(request)
            
            self.logger.info(f"🔊 Queued speech: '{text[:50]}...'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to queue speech: {e}")
            return False
    
    def speak_immediately(self, text: str, **kwargs) -> SpeechResult:
        """Synthesize and play speech immediately (blocking)"""
        try:
            # Get voice profile
            voice_profile = kwargs.get("voice_profile")
            if voice_profile and voice_profile in self.voice_profiles:
                profile = self.voice_profiles[voice_profile]
            else:
                profile = self.current_voice_profile or list(self.voice_profiles.values())[0]
            
            # Create speech request
            request = SpeechRequest(
                text=text,
                voice_profile=profile,
                emotional_expression=kwargs.get("emotional_expression", EmotionalExpression.NEUTRAL),
                speed_override=kwargs.get("speed"),
                pitch_override=kwargs.get("pitch"),
                volume_override=kwargs.get("volume")
            )
            
            # Synthesize speech
            result = self._synthesize_speech(request)
            
            # Play audio if synthesis was successful
            if result.success and result.audio_file:
                self._play_audio_file(result.audio_file)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to speak immediately: {e}")
            return SpeechResult(
                success=False,
                audio_file=None,
                duration=0.0,
                text=text,
                voice_profile="unknown",
                emotional_expression="neutral",
                error_message=str(e)
            )
    
    def _synthesize_speech(self, request: SpeechRequest) -> SpeechResult:
        """Synthesize speech from request"""
        try:
            start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # Apply emotional modifiers
            modified_profile = self._apply_emotional_modifiers(
                request.voice_profile, 
                request.emotional_expression
            )
            
            # Apply overrides
            if request.speed_override:
                modified_profile.speed = request.speed_override
            if request.pitch_override:
                modified_profile.pitch = request.pitch_override
            if request.volume_override:
                modified_profile.volume = request.volume_override
            
            # Generate audio file
            audio_file = self._generate_audio(request.text, modified_profile)
            
            duration = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
            
            if audio_file:
                return SpeechResult(
                    success=True,
                    audio_file=audio_file,
                    duration=duration,
                    text=request.text,
                    voice_profile=request.voice_profile.name,
                    emotional_expression=request.emotional_expression.value
                )
            else:
                return SpeechResult(
                    success=False,
                    audio_file=None,
                    duration=duration,
                    text=request.text,
                    voice_profile=request.voice_profile.name,
                    emotional_expression=request.emotional_expression.value,
                    error_message="Failed to generate audio"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to synthesize speech: {e}")
            return SpeechResult(
                success=False,
                audio_file=None,
                duration=0.0,
                text=request.text,
                voice_profile=request.voice_profile.name,
                emotional_expression=request.emotional_expression.value,
                error_message=str(e)
            )
    
    def _apply_emotional_modifiers(self, voice_profile: VoiceProfile, 
                                 emotional_expression: EmotionalExpression) -> VoiceProfile:
        """Apply emotional modifiers to voice profile"""
        try:
            # Create a copy of the voice profile
            modified_profile = VoiceProfile(
                name=voice_profile.name,
                gender=voice_profile.gender,
                language=voice_profile.language,
                pitch=voice_profile.pitch,
                speed=voice_profile.speed,
                volume=voice_profile.volume,
                emotional_range=voice_profile.emotional_range,
                voice_id=voice_profile.voice_id,
                lora_model=voice_profile.lora_model
            )
            
            # Get emotional modifiers
            emotional_modifiers = self.config.get("emotional_modifiers", {})
            modifiers = emotional_modifiers.get(emotional_expression.value, {})
            
            # Apply modifiers with emotional range scaling
            emotional_scale = voice_profile.emotional_range
            
            if "pitch" in modifiers:
                pitch_modifier = modifiers["pitch"] * emotional_scale
                modified_profile.pitch = max(-1.0, min(1.0, voice_profile.pitch + pitch_modifier))
            
            if "speed" in modifiers:
                speed_modifier = (modifiers["speed"] - 1.0) * emotional_scale
                modified_profile.speed = max(0.5, min(2.0, voice_profile.speed + speed_modifier))
            
            if "volume" in modifiers:
                volume_modifier = (modifiers["volume"] - voice_profile.volume) * emotional_scale
                modified_profile.volume = max(0.0, min(1.0, voice_profile.volume + volume_modifier))
            
            return modified_profile
            
        except Exception as e:
            self.logger.error(f"Failed to apply emotional modifiers: {e}")
            return voice_profile
    
    def _generate_audio(self, text: str, voice_profile: VoiceProfile) -> Optional[str]:
        """Generate audio file from text and voice profile"""
        try:
            # Generate unique filename
            timestamp = int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 * 1000)
            audio_file = self.audio_output_dir / f"speech_{timestamp}.wav"
            
            # Use pyttsx3 for now
            if self.pyttsx3_engine:
                return self._generate_audio_pyttsx3(text, voice_profile, str(audio_file))
            
            # Fallback: create silent audio file
            return self._generate_silent_audio(str(audio_file), duration=len(text) * 0.1)
            
        except Exception as e:
            self.logger.error(f"Failed to generate audio: {e}")
            return None
    
    def _generate_audio_pyttsx3(self, text: str, voice_profile: VoiceProfile, 
                               audio_file: str) -> Optional[str]:
        """Generate audio using pyttsx3"""
        try:
            # Configure pyttsx3 engine
            self.pyttsx3_engine.setProperty('rate', int(200 * voice_profile.speed))
            self.pyttsx3_engine.setProperty('volume', voice_profile.volume)
            
            # Try to set voice based on gender
            voices = self.pyttsx3_engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if voice_profile.gender == VoiceGender.FEMALE and 'female' in voice.name.lower():
                        self.pyttsx3_engine.setProperty('voice', voice.id)
                        break
                    elif voice_profile.gender == VoiceGender.MALE and 'male' in voice.name.lower():
                        self.pyttsx3_engine.setProperty('voice', voice.id)
                        break
            
            # Save to file
            self.pyttsx3_engine.save_to_file(text, audio_file)
            self.pyttsx3_engine.runAndWait()
            
            # Check if file was created
            if Path(audio_file).exists():
                return audio_file
            else:
                self.logger.error("pyttsx3 failed to create audio file")
                return None
                
        except Exception as e:
            self.logger.error(f"pyttsx3 generation failed: {e}")
            return None
    
    def _generate_silent_audio(self, audio_file: str, duration: float = 1.0) -> str:
        """Generate silent audio file as fallback"""
        try:
            sample_rate = self.config.get("sample_rate", 22050)
            samples = int(sample_rate * duration)
            
            # Create silent audio
            audio_data = np.zeros(samples, dtype=np.int16)
            
            # Save as WAV file
            with wave.open(audio_file, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.tobytes())
            
            return audio_file
            
        except Exception as e:
            self.logger.error(f"Failed to generate silent audio: {e}")
            return audio_file
    
    def _play_audio_file(self, audio_file: str):
        """Play audio file"""
        try:
            if not self.audio_system:
                self.logger.warning("No audio system available")
                return
            
            if self.audio_system == "pygame":
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            
            self.logger.debug(f"🔊 Played audio: {audio_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to play audio: {e}")
    
    def set_voice_profile(self, profile_name: str) -> bool:
        """Set current voice profile"""
        try:
            if profile_name in self.voice_profiles:
                self.current_voice_profile = self.voice_profiles[profile_name]
                self.logger.info(f"🎭 Voice profile set to: {profile_name}")
                return True
            else:
                self.logger.error(f"Voice profile not found: {profile_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to set voice profile: {e}")
            return False
    
    def add_voice_profile(self, profile_name: str, voice_profile: VoiceProfile) -> bool:
        """Add new voice profile"""
        try:
            self.voice_profiles[profile_name] = voice_profile
            
            # Save to config
            self.config["voice_profiles"][profile_name] = {
                "name": voice_profile.name,
                "gender": voice_profile.gender.value,
                "language": voice_profile.language,
                "pitch": voice_profile.pitch,
                "speed": voice_profile.speed,
                "volume": voice_profile.volume,
                "emotional_range": voice_profile.emotional_range,
                "voice_id": voice_profile.voice_id,
                "lora_model": voice_profile.lora_model
            }
            
            # Save config to file
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            self.logger.info(f"➕ Added voice profile: {profile_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add voice profile: {e}")
            return False
    
    def enable_adult_mode(self) -> bool:
        """Enable adult mode voices"""
        try:
            self.config["adult_mode_voices"] = True
            
            # Add adult mode voice profiles if not present
            if "mia_intimate" not in self.voice_profiles:
                intimate_profile = VoiceProfile(
                    name="MIA Intimate",
                    gender=VoiceGender.FEMALE,
                    language="en",
                    pitch=-0.1,
                    speed=0.7,
                    volume=0.5,
                    emotional_range=1.0
                )
                self.add_voice_profile("mia_intimate", intimate_profile)
            
            if "mia_seductive" not in self.voice_profiles:
                seductive_profile = VoiceProfile(
                    name="MIA Seductive",
                    gender=VoiceGender.FEMALE,
                    language="en",
                    pitch=-0.2,
                    speed=0.6,
                    volume=0.4,
                    emotional_range=1.0
                )
                self.add_voice_profile("mia_seductive", seductive_profile)
            
            self.logger.info("🔓 Adult mode voices enabled")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enable adult mode: {e}")
            return False
    
    def disable_adult_mode(self) -> bool:
        """Disable adult mode voices"""
        try:
            self.config["adult_mode_voices"] = False
            self.logger.info("🔒 Adult mode voices disabled")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to disable adult mode: {e}")
            return False
    
    def stop_speaking(self):
        """Stop current speech"""
        try:
            if self.audio_system == "pygame":
                pygame.mixer.music.stop()
            
            # Clear speech queue
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()
                except queue.Empty:
                    break
            
            self.logger.info("🔇 Stopped speaking")
            
        except Exception as e:
            self.logger.error(f"Failed to stop speaking: {e}")
    
    def is_speaking(self) -> bool:
        """Check if currently speaking"""
        try:
            if self.audio_system == "pygame":
                return pygame.mixer.music.get_busy()
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check speaking status: {e}")
            return False
    
    def get_voice_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get available voice profiles"""
        profiles = {}
        
        for name, profile in self.voice_profiles.items():
            # Filter adult mode profiles if not enabled
            if not self.config.get("adult_mode_voices", False):
                if name in ["mia_intimate", "mia_seductive"]:
                    continue
            
            profiles[name] = {
                "name": profile.name,
                "gender": profile.gender.value,
                "language": profile.language,
                "pitch": profile.pitch,
                "speed": profile.speed,
                "volume": profile.volume,
                "emotional_range": profile.emotional_range
            }
        
        return profiles
    
    def get_status(self) -> Dict[str, Any]:
        """Get TTS engine status"""
        return {
            "enabled": self.config.get("enabled", True),
            "is_speaking": self.is_speaking(),
            "current_voice": self.current_voice_profile.name if self.current_voice_profile else None,
            "voice_profiles_count": len(self.voice_profiles),
            "adult_mode_enabled": self.config.get("adult_mode_voices", False),
            "pyttsx3_available": PYTTSX3_AVAILABLE,
            "audio_available": AUDIO_AVAILABLE,
            "queue_size": self.speech_queue.qsize(),
            "engines": {
                "pyttsx3": self.pyttsx3_engine is not None,
                "xtts": self.xtts_engine is not None
            }
        }
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.stop_speaking()
            
            if self.pyttsx3_engine:
                self.pyttsx3_engine.stop()
            
            if AUDIO_AVAILABLE and pygame.mixer.get_init():
                pygame.mixer.quit()
            
            self.logger.info("🧹 TTS Engine cleaned up")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

# Global instance
tts_engine = TTSEngine()