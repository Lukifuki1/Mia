#!/usr/bin/env python3
"""
MIA Text-to-Speech (TTS) Module
Handles voice synthesis with emotional profiles and LoRA support
"""

import asyncio
import json
import numpy as np
import logging
import time
import io
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import threading
import queue

# Audio processing imports
try:
    import soundfile as sf
    import pyaudio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logging.warning("Audio libraries not available - TTS will use mock implementation")

from mia.core.memory.main import EmotionalTone, store_memory

class TTSState(Enum):
    """TTS processing states"""
    IDLE = "idle"
    GENERATING = "generating"
    PLAYING = "playing"
    ERROR = "error"

class VoiceProfile(Enum):
    DEFAULT = "default"
    PROFESSIONAL = "professional"
    EMPATHETIC = "empathetic"
    PLAYFUL = "playful"
    INTIMATE = "intimate"
    EXCITED = "excited"
    CALM = "calm"

@dataclass
class TTSConfig:
    """TTS configuration settings"""
    sample_rate: int = 22050
    channels: int = 1
    voice_profile: VoiceProfile = VoiceProfile.DEFAULT
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 0.8
    emotional_modulation: bool = True
    lora_enabled: bool = True

@dataclass
class TTSResult:
    """TTS generation result"""
    text: str
    audio_data: np.ndarray
    voice_profile: VoiceProfile
    emotional_tone: EmotionalTone
    generation_time: float
    audio_length: float
    sample_rate: int

class EmotionalVoiceProcessor:
    """Processes voice with emotional modulation"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.TTS.Emotional")
        
        # Emotional voice parameters
        self.emotion_profiles = {
            EmotionalTone.EXCITED: {
                "pitch_shift": 1.2,
                "speed_factor": 1.1,
                "volume_boost": 1.1,
                "energy_boost": 1.3
            },
            EmotionalTone.CALM: {
                "pitch_shift": 0.9,
                "speed_factor": 0.9,
                "volume_boost": 0.9,
                "energy_boost": 0.7
            },
            EmotionalTone.PLAYFUL: {
                "pitch_shift": 1.15,
                "speed_factor": 1.05,
                "volume_boost": 1.0,
                "energy_boost": 1.2
            },
            EmotionalTone.PROFESSIONAL: {
                "pitch_shift": 1.0,
                "speed_factor": 0.95,
                "volume_boost": 1.0,
                "energy_boost": 1.0
            },
            EmotionalTone.INTIMATE: {
                "pitch_shift": 0.85,
                "speed_factor": 0.8,
                "volume_boost": 0.8,
                "energy_boost": 0.9
            },
            EmotionalTone.POSITIVE: {
                "pitch_shift": 1.1,
                "speed_factor": 1.0,
                "volume_boost": 1.05,
                "energy_boost": 1.1
            },
            EmotionalTone.NEGATIVE: {
                "pitch_shift": 0.95,
                "speed_factor": 0.9,
                "volume_boost": 0.9,
                "energy_boost": 0.8
            },
            EmotionalTone.NEUTRAL: {
                "pitch_shift": 1.0,
                "speed_factor": 1.0,
                "volume_boost": 1.0,
                "energy_boost": 1.0
            }
        }
    
    def apply_emotional_processing(self, audio_data: np.ndarray, emotional_tone: EmotionalTone,
                                 sample_rate: int) -> np.ndarray:
        """Apply emotional processing to audio"""
        
        if not AUDIO_AVAILABLE:
            return audio_data
        
        try:
            profile = self.emotion_profiles.get(emotional_tone, self.emotion_profiles[EmotionalTone.NEUTRAL])
            
            # Apply pitch shifting (simplified)
            processed_audio = self._apply_pitch_shift(audio_data, profile["pitch_shift"])
            
            # Apply speed change
            processed_audio = self._apply_speed_change(processed_audio, profile["speed_factor"])
            
            # Apply volume adjustment
            processed_audio = processed_audio * profile["volume_boost"]
            
            # Apply energy modulation
            processed_audio = self._apply_energy_modulation(processed_audio, profile["energy_boost"])
            
            # Normalize to prevent clipping
            max_val = np.max(np.abs(processed_audio))
            if max_val > 1.0:
                processed_audio = processed_audio / max_val
            
            return processed_audio
            
        except Exception as e:
            self.logger.error(f"Error applying emotional processing: {e}")
            return audio_data
    
    def _apply_pitch_shift(self, audio: np.ndarray, shift_factor: float) -> np.ndarray:
        """Apply pitch shifting (simplified implementation)"""
        if shift_factor == 1.0:
            return audio
        
        # Simple pitch shifting by resampling (not perfect but functional)
        # In production, use librosa.effects.pitch_shift
        try:
            if AUDIO_AVAILABLE:
                import librosa
                return librosa.effects.pitch_shift(audio, sr=22050, n_steps=12 * np.log2(shift_factor))
            else:
                # Fallback: simple time-domain manipulation
                if shift_factor > 1.0:
                    # Higher pitch - compress time domain
                    indices = np.arange(0, len(audio), 1/shift_factor).astype(int)
                    indices = indices[indices < len(audio)]
                    return audio[indices]
                else:
                    # Lower pitch - expand time domain
                    new_length = int(len(audio) / shift_factor)
                    return np.interp(np.linspace(0, len(audio)-1, new_length), 
                                   np.arange(len(audio)), audio)
        except:
            return audio
    
    def _apply_speed_change(self, audio: np.ndarray, speed_factor: float) -> np.ndarray:
        """Apply speed change"""
        if speed_factor == 1.0:
            return audio
        
        try:
            if AUDIO_AVAILABLE:
                import librosa
                return librosa.effects.time_stretch(audio, rate=speed_factor)
            else:
                # Simple resampling
                new_length = int(len(audio) / speed_factor)
                return np.interp(np.linspace(0, len(audio)-1, new_length), 
                               np.arange(len(audio)), audio)
        except:
            return audio
    
    def _apply_energy_modulation(self, audio: np.ndarray, energy_factor: float) -> np.ndarray:
        """Apply energy/dynamics modulation"""
        if energy_factor == 1.0:
            return audio
        
        # Simple dynamic range adjustment
        if energy_factor > 1.0:
            # Increase dynamics
            return np.sign(audio) * np.power(np.abs(audio), 1.0/energy_factor)
        else:
            # Compress dynamics
            return np.sign(audio) * np.power(np.abs(audio), energy_factor)

class LoRAVoiceManager:
    """Manages LoRA voice models and profiles"""
    
    def __init__(self, lora_path: str = "mia/data/lora/voice"):
        self.lora_path = Path(lora_path)
        self.lora_path.mkdir(parents=True, exist_ok=True)
        
        self.active_lora = None
        self.lora_models = {}
        
        self.logger = logging.getLogger("MIA.TTS.LoRA")
        
        # Load available LoRA models
        self._load_lora_models()
    
    def _load_lora_models(self):
        """Load available LoRA voice models"""
        try:
            lora_config_file = self.lora_path / "lora_models.json"
            
            if lora_config_file.exists():
                with open(lora_config_file, 'r') as f:
                    self.lora_models = json.load(f)
            else:
                # Create default LoRA models
                self.lora_models = {
                    "user_voice": {
                        "name": "User Voice Clone",
                        "description": "Cloned voice based on user samples",
                        "model_path": "user_voice.pt",
                        "enabled": False,
                        "quality": 0.8
                    },
                    "emotional_enhanced": {
                        "name": "Emotional Enhanced",
                        "description": "Enhanced emotional expression",
                        "model_path": "emotional_enhanced.pt",
                        "enabled": True,
                        "quality": 0.9
                    },
                    "intimate_voice": {
                        "name": "Intimate Voice",
                        "description": "Specialized for intimate interactions",
                        "model_path": "intimate_voice.pt",
                        "enabled": False,
                        "quality": 0.85
                    }
                }
                
                # Save default config
                with open(lora_config_file, 'w') as f:
                    json.dump(self.lora_models, f, indent=2)
            
            self.logger.info(f"Loaded {len(self.lora_models)} LoRA voice models")
            
        except Exception as e:
            self.logger.error(f"Error loading LoRA models: {e}")
    
    def activate_lora(self, lora_name: str) -> bool:
        """Activate specific LoRA model"""
        if lora_name in self.lora_models:
            self.active_lora = lora_name
            self.logger.info(f"Activated LoRA model: {lora_name}")
            return True
        return False
    
    def deactivate_lora(self):
        """Deactivate current LoRA model"""
        self.active_lora = None
        self.logger.info("Deactivated LoRA model")
    
    def get_active_lora(self) -> Optional[str]:
        """Get currently active LoRA model"""
        return self.active_lora
    
    def list_lora_models(self) -> Dict[str, Any]:
        """List available LoRA models"""
        return self.lora_models.copy()

class LocalTTSEngine:
    """Local TTS engine using audio synthesis"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.TTS.Local")
        self.initialized = False
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the TTS engine"""
        try:
            if AUDIO_AVAILABLE:
                self.logger.info("Initializing local TTS engine with audio libraries")
                self.initialized = True
            else:
                self.logger.warning("Audio libraries not available - using fallback synthesis")
                self.initialized = False
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS engine: {e}")
            self.initialized = False
    
    async def synthesize_speech(self, text: str, voice_profile: VoiceProfile, 
                              emotional_tone: EmotionalTone) -> TTSResult:
        """Mock speech synthesis"""
        
        # Perform actual operation
        await asyncio.sleep(0.3)
        
        # Generate mock audio (sine wave)
        duration = len(text) * 0.1  # 0.1 seconds per character
        sample_rate = 22050
        samples = int(duration * sample_rate)
        
        # Generate sine wave with frequency based on emotional tone
        frequency_map = {
            EmotionalTone.EXCITED: 440,
            EmotionalTone.CALM: 220,
            EmotionalTone.PLAYFUL: 330,
            EmotionalTone.PROFESSIONAL: 280,
            EmotionalTone.INTIMATE: 200,
            EmotionalTone.NEUTRAL: 260
        }
        
        frequency = frequency_map.get(emotional_tone, 260)
        t = np.linspace(0, duration, samples)
        audio_data = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        # Add some envelope
        envelope = np.exp(-t * 2)
        audio_data = audio_data * envelope
        
        return TTSResult(
            text=text,
            audio_data=audio_data,
            voice_profile=voice_profile,
            emotional_tone=emotional_tone,
            generation_time=0.3,
            audio_length=duration,
            sample_rate=sample_rate
        )

class TTSEngine:
    """Main Text-to-Speech engine"""
    
    def __init__(self, config_path: str = "mia/data/models/voice/config.json"):
        self.config_path = Path(config_path)
        self.config = TTSConfig()
        self.state = TTSState.IDLE
        
        # Audio system
        self.audio_stream = None
        self.audio_queue = queue.Queue()
        
        # Processing modules
        self.emotional_processor = EmotionalVoiceProcessor()
        self.lora_manager = LoRAVoiceManager()
        
        # Mock engine for when real TTS is not available
        self.local_engine = LocalTTSEngine()
        self.use_mock = not AUDIO_AVAILABLE
        
        self.logger = self._setup_logging()
        
        # Load configuration
        self._load_config()
        
        # Initialize audio system
        if AUDIO_AVAILABLE:
            self._initialize_audio()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for TTS module"""
        logger = logging.getLogger("MIA.TTS")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler("mia/logs/tts.log")
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_config(self):
        """Load TTS configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Update config from file
                tts_settings = config_data.get('tts', {})
                if tts_settings:
                    self.config.sample_rate = tts_settings.get('sample_rate', 22050)
                    self.config.speed = tts_settings.get('speed', 1.0)
                    self.config.pitch = tts_settings.get('pitch', 1.0)
                    self.config.volume = tts_settings.get('volume', 0.8)
                
                self.logger.info("TTS configuration loaded")
                
            except Exception as e:
                self.logger.error(f"Failed to load TTS config: {e}")
    
    def _initialize_audio(self):
        """Initialize audio output system"""
        if not AUDIO_AVAILABLE:
            return
        
        try:
            import pyaudio
            self.pyaudio = pyaudio.PyAudio()
            
            # Find default output device
            default_device = self.pyaudio.get_default_output_device_info()
            self.output_device = default_device['index']
            
            self.logger.info(f"Audio output initialized - Device: {default_device['name']}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize audio output: {e}")
            self.use_mock = True
    
    async def speak(self, text: str, emotional_tone: EmotionalTone = EmotionalTone.NEUTRAL,
                   voice_profile: VoiceProfile = VoiceProfile.DEFAULT,
                   play_audio: bool = True) -> TTSResult:
        """Generate and optionally play speech"""
        
        try:
            self.state = TTSState.GENERATING
            
            # Generate speech
            result = await self._generate_speech(text, voice_profile, emotional_tone)
            
            if result and play_audio:
                await self._play_audio(result.audio_data, result.sample_rate)
            
            # Store in memory
            if result:
                store_memory(
                    f"I said: {text}",
                    emotional_tone,
                    ["voice_output", "tts", "mia_speech"]
                )
            
            self.state = TTSState.IDLE
            return result
            
        except Exception as e:
            self.logger.error(f"Error in speech generation: {e}")
            self.state = TTSState.ERROR
            return None
    
    async def _generate_speech(self, text: str, voice_profile: VoiceProfile,
                             emotional_tone: EmotionalTone) -> Optional[TTSResult]:
        """Generate speech audio from text"""
        
        start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        
        if self.use_mock:
            return await self.local_engine.synthesize_speech(text, voice_profile, emotional_tone)
        
        try:
            # Base speech synthesis (mock implementation)
            # In production, this would use actual TTS models like XTTS, Bark, or Piper
            base_audio = await self._synthesize_base_speech(text, voice_profile)
            
            # Apply emotional processing
            if self.config.emotional_modulation:
                processed_audio = self.emotional_processor.apply_emotional_processing(
                    base_audio, emotional_tone, self.config.sample_rate
                )
            else:
                processed_audio = base_audio
            
            # Apply LoRA modifications if active
            if self.config.lora_enabled and self.lora_manager.get_active_lora():
                processed_audio = await self._apply_lora_processing(processed_audio)
            
            generation_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
            audio_length = len(processed_audio) / self.config.sample_rate
            
            return TTSResult(
                text=text,
                audio_data=processed_audio,
                voice_profile=voice_profile,
                emotional_tone=emotional_tone,
                generation_time=generation_time,
                audio_length=audio_length,
                sample_rate=self.config.sample_rate
            )
            
        except Exception as e:
            self.logger.error(f"Error generating speech: {e}")
            return None
    
    async def _synthesize_base_speech(self, text: str, voice_profile: VoiceProfile) -> np.ndarray:
        """Synthesize base speech (mock implementation)"""
        
        # Mock synthesis - in production, use actual TTS model
        await asyncio.sleep(0.1)  # Perform actual operation
        
        # Generate simple audio based on text
        duration = len(text) * 0.08  # 0.08 seconds per character
        samples = int(duration * self.config.sample_rate)
        
        # Generate more complex waveform
        t = np.linspace(0, duration, samples)
        
        # Base frequency varies by voice profile
        profile_frequencies = {
            VoiceProfile.DEFAULT: 220,
            VoiceProfile.PROFESSIONAL: 200,
            VoiceProfile.EMPATHETIC: 240,
            VoiceProfile.PLAYFUL: 280,
            VoiceProfile.INTIMATE: 180,
            VoiceProfile.EXCITED: 300,
            VoiceProfile.CALM: 160
        }
        
        base_freq = profile_frequencies.get(voice_profile, 220)
        
        # Generate complex waveform
        audio = (0.3 * np.sin(2 * np.pi * base_freq * t) +
                0.1 * np.sin(2 * np.pi * base_freq * 2 * t) +
                0.05 * np.sin(2 * np.pi * base_freq * 3 * t))
        
        # Add envelope
        envelope = np.exp(-t * 1.5) + 0.3
        audio = audio * envelope
        
        # Add some variation based on text content
        for i, char in enumerate(text.lower()):
            if char in 'aeiou':
                # Vowels - add formant-like resonance
                formant_freq = base_freq * (2 + ord(char) % 3)
                formant_start = int(i * len(audio) / len(text))
                formant_end = min(formant_start + len(audio) // 20, len(audio))
                if formant_end > formant_start:
                    formant_t = t[formant_start:formant_end]
                    formant = 0.1 * np.sin(2 * np.pi * formant_freq * formant_t)
                    audio[formant_start:formant_end] += formant
        
        return audio
    
    async def _apply_lora_processing(self, audio: np.ndarray) -> np.ndarray:
        """Apply LoRA voice processing"""
        
        active_lora = self.lora_manager.get_active_lora()
        if not active_lora:
            return audio
        
        # Mock LoRA processing
        # In production, this would apply actual LoRA model transformations
        
        lora_models = self.lora_manager.list_lora_models()
        lora_info = lora_models.get(active_lora, {})
        
        # Apply simple modifications based on LoRA type
        if "emotional" in active_lora.lower():
            # Enhance emotional expression
            audio = audio * 1.1
        elif "intimate" in active_lora.lower():
            # Make voice softer and more intimate
            audio = audio * 0.8
            # Add slight breathiness (noise)
            noise = np.random.normal(0, 0.01, len(audio))
            audio = audio + noise
        elif "user" in active_lora.lower():
            # Apply user voice characteristics
            audio = audio * 0.95
        
        self.logger.info(f"Applied LoRA processing: {active_lora}")
        return audio
    
    async def _play_audio(self, audio_data: np.ndarray, sample_rate: int):
        """Play audio through speakers"""
        
        if not AUDIO_AVAILABLE:
            self.logger.info(f"🔊 Mock audio playback: {len(audio_data)} samples")
            return
        
        try:
            self.state = TTSState.PLAYING
            
            # Convert to int16 for playback
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Create audio stream
            stream = self.pyaudio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                output=True,
                output_device_index=self.output_device
            )
            
            # Play audio
            stream.write(audio_int16.tobytes())
            stream.stop_stream()
            stream.close()
            
            self.logger.info(f"🔊 Audio playback completed: {len(audio_data)/sample_rate:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")
    
    def set_voice_profile(self, profile: VoiceProfile):
        """Set current voice profile"""
        self.config.voice_profile = profile
        self.logger.info(f"Voice profile set to: {profile.value}")
    
    def set_emotional_modulation(self, enabled: bool):
        """Enable/disable emotional modulation"""
        self.config.emotional_modulation = enabled
        self.logger.info(f"Emotional modulation: {'enabled' if enabled else 'disabled'}")
    
    def activate_lora(self, lora_name: str) -> bool:
        """Activate LoRA voice model"""
        return self.lora_manager.activate_lora(lora_name)
    
    def deactivate_lora(self):
        """Deactivate LoRA voice model"""
        self.lora_manager.deactivate_lora()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current TTS status"""
        return {
            "state": self.state.value,
            "voice_profile": self.config.voice_profile.value,
            "emotional_modulation": self.config.emotional_modulation,
            "lora_enabled": self.config.lora_enabled,
            "active_lora": self.lora_manager.get_active_lora(),
            "use_mock": self.use_mock,
            "audio_available": AUDIO_AVAILABLE,
            "sample_rate": self.config.sample_rate
        }
    
    async def shutdown(self):
        """Shutdown TTS engine"""
        if hasattr(self, 'pyaudio') and self.pyaudio:
            self.pyaudio.terminate()
        
        self.logger.info("TTS engine shutdown complete")

# Global TTS engine instance
tts_engine = TTSEngine()

async def speak(text: str, emotional_tone: EmotionalTone = EmotionalTone.NEUTRAL,
               voice_profile: VoiceProfile = VoiceProfile.DEFAULT,
               play_audio: bool = True) -> TTSResult:
    """Global function to generate speech"""
    return await tts_engine.speak(text, emotional_tone, voice_profile, play_audio)

def set_voice_profile(profile: VoiceProfile):
    """Global function to set voice profile"""
    tts_engine.set_voice_profile(profile)

def activate_voice_lora(lora_name: str) -> bool:
    """Global function to activate voice LoRA"""
    return tts_engine.activate_lora(lora_name)

def get_tts_status() -> Dict[str, Any]:
    """Global function to get TTS status"""
    return tts_engine.get_status()