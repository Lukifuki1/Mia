#!/usr/bin/env python3
"""
MIA Speech-to-Text Engine
Real-time speech recognition with emotional tone analysis
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

# Audio processing
try:
    import pyaudio
    import webrtcvad
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    pyaudio = None
    webrtcvad = None

# Whisper for STT
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None

class EmotionalTone(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Emotional tones detected in speech"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "excited"
    CALM = "calm"
    FRUSTRATED = "frustrated"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"

class SpeechQuality(Enum):
    """Speech recognition quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

@dataclass
class SpeechResult:
    """Speech recognition result"""
    text: str
    confidence: float
    emotional_tone: EmotionalTone
    quality: SpeechQuality
    duration: float
    timestamp: float
    language: str
    speaker_id: Optional[str] = None

@dataclass
class AudioConfig:
    """Audio configuration"""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    format: int = None  # Will be set based on pyaudio availability
    vad_aggressiveness: int = 2
    silence_threshold: float = 0.5

class STTEngine:
    """Speech-to-Text Engine with emotional analysis"""
    
    def __init__(self, config_path: str = "mia/data/voice/stt_config.json"):
        self.config_path = config_path
        self.voice_dir = Path("mia/data/voice")
        self.voice_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.STTEngine")
        
        # Initialize configuration
        self.config = self._load_configuration()
        self.audio_config = AudioConfig()
        
        # Audio components
        self.audio = None
        self.vad = None
        self.whisper_model = None
        
        # Runtime state
        self.is_listening = False
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.result_callbacks: List[Callable] = []
        
        # Initialize components
        self._initialize_audio()
        self._initialize_whisper()
        self._initialize_vad()
        
        self.logger.info("🎤 STT Engine initialized")
    
    def _load_configuration(self) -> Dict:
        """Load STT configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load STT config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default STT configuration"""
        config = {
            "enabled": True,
            "whisper_model": "base",  # tiny, base, small, medium, large
            "language": "auto",  # auto-detect or specific language
            "emotional_analysis": True,
            "real_time_processing": True,
            "voice_activity_detection": True,
            "noise_reduction": True,
            "speaker_identification": False,
            "confidence_threshold": 0.7,
            "audio_settings": {
                "sample_rate": 16000,
                "channels": 1,
                "chunk_size": 1024,
                "vad_aggressiveness": 2,
                "silence_threshold": 0.5
            },
            "emotional_keywords": {
                "happy": ["great", "awesome", "wonderful", "fantastic", "love", "excited"],
                "sad": ["sad", "disappointed", "upset", "depressed", "terrible"],
                "angry": ["angry", "furious", "mad", "annoyed", "frustrated"],
                "confident": ["sure", "certain", "confident", "definitely", "absolutely"],
                "uncertain": ["maybe", "perhaps", "not sure", "uncertain", "possibly"]
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _initialize_audio(self):
        """Initialize audio system"""
        try:
            if not AUDIO_AVAILABLE:
                self.logger.warning("PyAudio not available - STT will work with file input only")
                return
            
            self.audio = pyaudio.PyAudio()
            self.audio_config.format = pyaudio.paInt16
            
            # Update audio config from settings
            audio_settings = self.config.get("audio_settings", {})
            self.audio_config.sample_rate = audio_settings.get("sample_rate", 16000)
            self.audio_config.channels = audio_settings.get("channels", 1)
            self.audio_config.chunk_size = audio_settings.get("chunk_size", 1024)
            self.audio_config.vad_aggressiveness = audio_settings.get("vad_aggressiveness", 2)
            self.audio_config.silence_threshold = audio_settings.get("silence_threshold", 0.5)
            
            self.logger.info("✅ Audio system initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize audio: {e}")
            self.audio = None
    
    def _initialize_whisper(self):
        """Initialize Whisper model"""
        try:
            if not WHISPER_AVAILABLE:
                self.logger.warning("Whisper not available - using fallback STT")
                return
            
            model_name = self.config.get("whisper_model", "base")
            self.logger.info(f"Loading Whisper model: {model_name}")
            
            self.whisper_model = whisper.load_model(model_name)
            
            self.logger.info("✅ Whisper model loaded")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Whisper: {e}")
            self.whisper_model = None
    
    def _initialize_vad(self):
        """Initialize Voice Activity Detection"""
        try:
            if not AUDIO_AVAILABLE or not webrtcvad:
                self.logger.warning("WebRTC VAD not available")
                return
            
            self.vad = webrtcvad.Vad(self.audio_config.vad_aggressiveness)
            
            self.logger.info("✅ Voice Activity Detection initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize VAD: {e}")
            self.vad = None
    
    def start_listening(self, callback: Optional[Callable] = None):
        """Start real-time speech recognition"""
        if not self.audio or not AUDIO_AVAILABLE:
            self.logger.error("Audio system not available")
            return False
        
        if self.is_listening:
            self.logger.warning("Already listening")
            return True
        
        try:
            if callback:
                self.result_callbacks.append(callback)
            
            self.is_listening = True
            
            # Start audio capture thread
            audio_thread = threading.Thread(target=self._audio_capture_loop, daemon=True)
            audio_thread.start()
            
            # Start processing thread
            processing_thread = threading.Thread(target=self._audio_processing_loop, daemon=True)
            processing_thread.start()
            
            self.logger.info("🎤 Started listening")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start listening: {e}")
            self.is_listening = False
            return False
    
    def stop_listening(self):
        """Stop real-time speech recognition"""
        self.is_listening = False
        self.is_recording = False
        self.logger.info("🔇 Stopped listening")
    
    def _audio_capture_loop(self):
        """Audio capture loop"""
        try:
            stream = self.audio.open(
                format=self.audio_config.format,
                channels=self.audio_config.channels,
                rate=self.audio_config.sample_rate,
                input=True,
                frames_per_buffer=self.audio_config.chunk_size
            )
            
            self.logger.info("🎙️ Audio capture started")
            
            while self.is_listening:
                try:
                    data = stream.read(self.audio_config.chunk_size, exception_on_overflow=False)
                    
                    # Voice activity detection
                    if self.vad and self._is_speech(data):
                        if not self.is_recording:
                            self.is_recording = True
                            self.logger.debug("🗣️ Speech detected - starting recording")
                        
                        self.audio_queue.put(data)
                    else:
                        if self.is_recording:
                            # Add silence marker to indicate end of speech
                            self.audio_queue.put(None)
                            self.is_recording = False
                            self.logger.debug("🤫 Silence detected - stopping recording")
                
                except Exception as e:
                    self.logger.error(f"Audio capture error: {e}")
                    break
            
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            self.logger.error(f"Audio capture loop failed: {e}")
    
    def _is_speech(self, audio_data: bytes) -> bool:
        """Check if audio data contains speech"""
        try:
            if not self.vad:
                # Fallback: simple volume-based detection
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                volume = np.sqrt(np.mean(audio_array**2))
                return volume > 1000  # Threshold for speech
            
            # Use WebRTC VAD
            return self.vad.is_speech(audio_data, self.audio_config.sample_rate)
            
        except Exception as e:
            self.logger.error(f"Speech detection error: {e}")
            return False
    
    def _audio_processing_loop(self):
        """Audio processing and recognition loop"""
        audio_buffer = []
        
        while self.is_listening:
            try:
                # Get audio data from queue
                try:
                    data = self.audio_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                if data is None:
                    # End of speech - process accumulated audio
                    if audio_buffer:
                        self._process_audio_buffer(audio_buffer)
                        audio_buffer = []
                else:
                    # Accumulate audio data
                    audio_buffer.append(data)
                
            except Exception as e:
                self.logger.error(f"Audio processing error: {e}")
    
    def _process_audio_buffer(self, audio_buffer: List[bytes]):
        """Process accumulated audio buffer"""
        try:
            if not audio_buffer:
                return
            
            # Combine audio chunks
            audio_data = b''.join(audio_buffer)
            
            # Save to temporary file for Whisper
            temp_file = self.voice_dir / f"temp_audio_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}.wav"
            
            with wave.open(str(temp_file), 'wb') as wf:
                wf.setnchannels(self.audio_config.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.audio_config.format))
                wf.setframerate(self.audio_config.sample_rate)
                wf.writeframes(audio_data)
            
            # Recognize speech
            result = self.recognize_file(str(temp_file))
            
            # Clean up temp file
            temp_file.unlink()
            
            # Call callbacks
            if result and result.text.strip():
                for callback in self.result_callbacks:
                    try:
                        callback(result)
                    except Exception as e:
                        self.logger.error(f"Callback error: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to process audio buffer: {e}")
    
    def recognize_file(self, audio_file: str) -> Optional[SpeechResult]:
        """Recognize speech from audio file"""
        try:
            if not self.whisper_model:
                return self._fallback_recognition(audio_file)
            
            start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(
                audio_file,
                language=None if self.config.get("language") == "auto" else self.config.get("language")
            )
            
            duration = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
            
            # Extract text and confidence
            text = result["text"].strip()
            
            # Estimate confidence (Whisper doesn't provide direct confidence)
            confidence = self._estimate_confidence(result)
            
            # Analyze emotional tone
            emotional_tone = self._analyze_emotional_tone(text)
            
            # Determine quality
            quality = self._determine_quality(confidence, duration, len(text))
            
            # Detect language
            language = result.get("language", "unknown")
            
            speech_result = SpeechResult(
                text=text,
                confidence=confidence,
                emotional_tone=emotional_tone,
                quality=quality,
                duration=duration,
                timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                language=language
            )
            
            self.logger.info(f"🗣️ Recognized: '{text}' (confidence: {confidence:.2f})")
            
            return speech_result
            
        except Exception as e:
            self.logger.error(f"Failed to recognize speech: {e}")
            return None
    
    def _fallback_recognition(self, audio_file: str) -> Optional[SpeechResult]:
        """Fallback recognition when Whisper is not available"""
        try:
            # Basic audio analysis fallback
            self.logger.warning("Using fallback STT - basic audio analysis")
            
            # Analyze audio file properties for basic feedback
            import os
            audio_size = os.path.getsize(audio_file) if os.path.exists(audio_file) else 0
            estimated_duration = max(0.1, audio_size / (16000 * 2))  # Rough estimate
            
            return SpeechResult(
                text="[Audio detected - Please install Whisper for full STT functionality]",
                confidence=0.5,
                emotional_tone=EmotionalTone.NEUTRAL,
                quality=SpeechQuality.FAIR,
                duration=estimated_duration,
                timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                language="unknown"
            )
            
        except Exception as e:
            self.logger.error(f"Fallback recognition failed: {e}")
            return None
    
    def _estimate_confidence(self, whisper_result: Dict) -> float:
        """Estimate confidence from Whisper result"""
        try:
            # Use segments information if available
            if "segments" in whisper_result:
                segments = whisper_result["segments"]
                if segments:
                    # Average confidence from segments
                    confidences = []
                    for segment in segments:
                        if "avg_logprob" in segment:
                            # Convert log probability to confidence (0-1)
                            confidence = min(1.0, max(0.0, (segment["avg_logprob"] + 1.0)))
                            confidences.append(confidence)
                    
                    if confidences:
                        return sum(confidences) / len(confidences)
            
            # Fallback: estimate based on text length and other factors
            text = whisper_result.get("text", "")
            if len(text) > 10:
                return 0.8
            elif len(text) > 3:
                return 0.6
            else:
                return 0.4
                
        except Exception as e:
            self.logger.error(f"Failed to estimate confidence: {e}")
            return 0.5
    
    def _analyze_emotional_tone(self, text: str) -> EmotionalTone:
        """Analyze emotional tone from text"""
        try:
            if not self.config.get("emotional_analysis", True):
                return EmotionalTone.NEUTRAL
            
            text_lower = text.lower()
            emotional_keywords = self.config.get("emotional_keywords", {})
            
            # Count emotional keywords
            emotion_scores = {}
            
            for emotion, keywords in emotional_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                if score > 0:
                    emotion_scores[emotion] = score
            
            # Return emotion with highest score
            if emotion_scores:
                best_emotion = max(emotion_scores, key=emotion_scores.get)
                return EmotionalTone(best_emotion)
            
            # Analyze text patterns for additional emotions
            if any(word in text_lower for word in ["!", "wow", "amazing"]):
                return EmotionalTone.EXCITED
            elif any(word in text_lower for word in ["calm", "peaceful", "relaxed"]):
                return EmotionalTone.CALM
            elif "?" in text and any(word in text_lower for word in ["what", "how", "why"]):
                return EmotionalTone.UNCERTAIN
            
            return EmotionalTone.NEUTRAL
            
        except Exception as e:
            self.logger.error(f"Failed to analyze emotional tone: {e}")
            return EmotionalTone.NEUTRAL
    
    def _determine_quality(self, confidence: float, duration: float, text_length: int) -> SpeechQuality:
        """Determine speech recognition quality"""
        try:
            # Quality based on multiple factors
            quality_score = 0
            
            # Confidence factor
            if confidence >= 0.9:
                quality_score += 3
            elif confidence >= 0.7:
                quality_score += 2
            elif confidence >= 0.5:
                quality_score += 1
            
            # Text length factor
            if text_length >= 20:
                quality_score += 2
            elif text_length >= 5:
                quality_score += 1
            
            # Duration factor (not too fast, not too slow)
            if 0.5 <= duration <= 3.0:
                quality_score += 1
            
            # Determine quality level
            if quality_score >= 5:
                return SpeechQuality.EXCELLENT
            elif quality_score >= 3:
                return SpeechQuality.GOOD
            elif quality_score >= 1:
                return SpeechQuality.FAIR
            else:
                return SpeechQuality.POOR
                
        except Exception as e:
            self.logger.error(f"Failed to determine quality: {e}")
            return SpeechQuality.FAIR
    
    def add_result_callback(self, callback: Callable):
        """Add callback for speech recognition results"""
        self.result_callbacks.append(callback)
    
    def remove_result_callback(self, callback: Callable):
        """Remove callback for speech recognition results"""
        if callback in self.result_callbacks:
            self.result_callbacks.remove(callback)
    
    def get_status(self) -> Dict[str, Any]:
        """Get STT engine status"""
        return {
            "enabled": self.config.get("enabled", True),
            "is_listening": self.is_listening,
            "is_recording": self.is_recording,
            "whisper_available": WHISPER_AVAILABLE,
            "audio_available": AUDIO_AVAILABLE,
            "whisper_model": self.config.get("whisper_model", "base"),
            "language": self.config.get("language", "auto"),
            "emotional_analysis": self.config.get("emotional_analysis", True),
            "callbacks_count": len(self.result_callbacks)
        }
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.stop_listening()
            
            if self.audio:
                self.audio.terminate()
            
            self.logger.info("🧹 STT Engine cleaned up")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

# Global instance
stt_engine = STTEngine()