#!/usr/bin/env python3
"""
MIA Speech-to-Text (STT) Module
Handles voice recognition with emotional tone analysis
"""

import asyncio
import json
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import time
import threading
import queue

# Audio processing imports (will be installed via requirements)
try:
    import librosa
    import soundfile as sf
    import pyaudio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logging.warning("Audio libraries not available - STT will use mock implementation")

from mia.core.memory.main import EmotionalTone, store_memory

class STTState(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    ERROR = "error"

@dataclass
class AudioConfig:
    """Audio configuration settings"""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    format: int = None  # Will be set based on pyaudio availability
    input_device: Optional[int] = None
    noise_threshold: float = 0.01
    silence_timeout: float = 2.0

@dataclass
class STTResult:
    """Speech-to-text result with metadata"""
    text: str
    confidence: float
    emotional_tone: EmotionalTone
    audio_features: Dict[str, float]
    processing_time: float
    timestamp: float

class EmotionalAnalyzer:
    """Analyzes emotional content from audio features"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.STT.Emotional")
    
    def analyze_audio_emotion(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[EmotionalTone, Dict[str, float]]:
        """Analyze emotional tone from audio features"""
        
        if not AUDIO_AVAILABLE:
            return EmotionalTone.NEUTRAL, {}
        
        try:
            # Extract audio features
            features = self._extract_audio_features(audio_data, sample_rate)
            
            # Classify emotion based on features
            emotion = self._classify_emotion(features)
            
            return emotion, features
            
        except Exception as e:
            self.logger.error(f"Error analyzing emotion: {e}")
            return EmotionalTone.NEUTRAL, {}
    
    def _extract_audio_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Extract relevant audio features for emotion analysis"""
        
        features = {}
        
        try:
            # Fundamental frequency (pitch)
            pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sample_rate)
            pitch_mean = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0
            features['pitch_mean'] = float(pitch_mean)
            
            # Energy/intensity
            rms = librosa.feature.rms(y=audio_data)[0]
            features['energy_mean'] = float(np.mean(rms))
            features['energy_std'] = float(np.std(rms))
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            
            # Zero crossing rate (speech rhythm)
            zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
            features['zcr_mean'] = float(np.mean(zcr))
            
            # MFCC features (first few coefficients)
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=5)
            for i in range(5):
                features[f'mfcc_{i}'] = float(np.mean(mfccs[i]))
            
            # Tempo
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            features['tempo'] = float(tempo)
            
        except Exception as e:
            self.logger.error(f"Error extracting audio features: {e}")
        
        return features
    
    def _classify_emotion(self, features: Dict[str, float]) -> EmotionalTone:
        """Classify emotion based on audio features"""
        
        if not features:
            return EmotionalTone.NEUTRAL
        
        # Simple rule-based emotion classification
        # In production, this would use a trained ML model
        
        pitch_mean = features.get('pitch_mean', 0)
        energy_mean = features.get('energy_mean', 0)
        energy_std = features.get('energy_std', 0)
        tempo = features.get('tempo', 120)
        
        # High energy + high pitch = excited
        if energy_mean > 0.1 and pitch_mean > 200:
            return EmotionalTone.EXCITED
        
        # Low energy + low pitch = calm
        elif energy_mean < 0.05 and pitch_mean < 150:
            return EmotionalTone.CALM
        
        # High energy variation = emotional
        elif energy_std > 0.05:
            if pitch_mean > 180:
                return EmotionalTone.POSITIVE
            else:
                return EmotionalTone.NEGATIVE
        
        # Fast tempo = playful
        elif tempo > 140:
            return EmotionalTone.PLAYFUL
        
        # Slow tempo = professional
        elif tempo < 100:
            return EmotionalTone.PROFESSIONAL
        
        return EmotionalTone.NEUTRAL

class MockSTTEngine:
    """Mock STT engine for testing when real STT is not available"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.STT.Mock")
        self.mock_responses = [
            "Hello MIA, how are you today?",
            "Can you help me with a project?",
            "I'm feeling excited about this!",
            "Let's work on something creative.",
            "MIA, what do you think about this?",
            "I need some assistance please.",
            "This is really interesting!",
            "Can we try something different?",
        ]
        self.response_index = 0
    
    async def transcribe_audio(self, audio_data: np.ndarray, sample_rate: int) -> STTResult:
        """Mock transcription"""
        
        # Perform actual operation
        await asyncio.sleep(0.5)
        
        # Get mock response
        text = self.mock_responses[self.response_index % len(self.mock_responses)]
        self.response_index += 1
        
        # Mock emotional analysis
        if "excited" in text.lower():
            emotion = EmotionalTone.EXCITED
        elif "help" in text.lower() or "assist" in text.lower():
            emotion = EmotionalTone.PROFESSIONAL
        elif "creative" in text.lower() or "interesting" in text.lower():
            emotion = EmotionalTone.PLAYFUL
        else:
            emotion = EmotionalTone.NEUTRAL
        
        return STTResult(
            text=text,
            confidence=0.95,
            emotional_tone=emotion,
            audio_features={},
            processing_time=0.5,
            timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        )

class STTEngine:
    """Main Speech-to-Text engine"""
    
    def __init__(self, config_path: str = "mia/data/models/voice/config.json"):
        self.config_path = Path(config_path)
        self.audio_config = AudioConfig()
        self.emotional_analyzer = EmotionalAnalyzer()
        self.state = STTState.IDLE
        
        # Audio stream
        self.audio_stream = None
        self.audio_queue = queue.Queue()
        self.is_listening = False
        
        # Mock engine for when real STT is not available
        self.mock_engine = MockSTTEngine()
        self.use_mock = not AUDIO_AVAILABLE
        
        self.logger = self._setup_logging()
        
        # Load configuration
        self._load_config()
        
        # Initialize audio system
        if AUDIO_AVAILABLE:
            self._initialize_audio()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for STT module"""
        logger = logging.getLogger("MIA.STT")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler("mia/logs/stt.log")
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_config(self):
        """Load STT configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                # Update audio config from file
                audio_settings = config.get('audio', {})
                if audio_settings:
                    self.audio_config.sample_rate = audio_settings.get('sample_rate', 16000)
                    self.audio_config.channels = audio_settings.get('channels', 1)
                    self.audio_config.chunk_size = audio_settings.get('chunk_size', 1024)
                
                self.logger.info("STT configuration loaded")
                
            except Exception as e:
                self.logger.error(f"Failed to load STT config: {e}")
    
    def _initialize_audio(self):
        """Initialize audio system"""
        if not AUDIO_AVAILABLE:
            return
        
        try:
            import pyaudio
            self.audio_config.format = pyaudio.paInt16
            
            # Initialize PyAudio
            self.pyaudio = pyaudio.PyAudio()
            
            # Find default input device
            default_device = self.pyaudio.get_default_input_device_info()
            self.audio_config.input_device = default_device['index']
            
            self.logger.info(f"Audio initialized - Device: {default_device['name']}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize audio: {e}")
            self.use_mock = True
    
    async def start_listening(self) -> bool:
        """Start listening for voice input"""
        
        if self.use_mock:
            self.logger.info("🎤 Mock STT listening started")
            self.state = STTState.LISTENING
            return True
        
        if not AUDIO_AVAILABLE:
            return False
        
        try:
            self.state = STTState.LISTENING
            self.is_listening = True
            
            # Start audio stream
            self.audio_stream = self.pyaudio.open(
                format=self.audio_config.format,
                channels=self.audio_config.channels,
                rate=self.audio_config.sample_rate,
                input=True,
                input_device_index=self.audio_config.input_device,
                frames_per_buffer=self.audio_config.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.audio_stream.start_stream()
            
            self.logger.info("🎤 STT listening started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start listening: {e}")
            self.state = STTState.ERROR
            return False
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Audio stream callback"""
        if self.is_listening:
            self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue if AUDIO_AVAILABLE else 0)
    
    async def stop_listening(self):
        """Stop listening for voice input"""
        
        self.is_listening = False
        self.state = STTState.IDLE
        
        if self.audio_stream and AUDIO_AVAILABLE:
            try:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
            except Exception as e:
                self.logger.error(f"Error stopping audio stream: {e}")
        
        self.logger.info("🎤 STT listening stopped")
    
    async def process_voice_input(self, timeout: float = 5.0) -> Optional[STTResult]:
        """Process voice input and return transcription"""
        
        if self.use_mock:
            return await self._process_mock_input()
        
        if not self.is_listening:
            await self.start_listening()
        
        try:
            self.state = STTState.PROCESSING
            
            # Collect audio data
            audio_data = await self._collect_audio_data(timeout)
            
            if audio_data is None:
                return None
            
            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Transcribe audio (mock implementation)
            result = await self._transcribe_audio(audio_array)
            
            # Store in memory
            if result and result.text:
                store_memory(
                    f"User said: {result.text}",
                    result.emotional_tone,
                    ["voice_input", "stt", "user_speech"]
                )
            
            self.state = STTState.LISTENING
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing voice input: {e}")
            self.state = STTState.ERROR
            return None
    
    async def _process_mock_input(self) -> STTResult:
        """Process mock voice input"""
        return await self.mock_engine.transcribe_audio(np.array([]), 16000)
    
    async def _collect_audio_data(self, timeout: float) -> Optional[bytes]:
        """Collect audio data from stream"""
        
        audio_chunks = []
        start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        silence_start = None
        
        while self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time < timeout:
            try:
                # Get audio chunk with timeout
                chunk = self.audio_queue.get(timeout=0.1)
                audio_chunks.append(chunk)
                
                # Check for silence
                audio_array = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0
                energy = np.mean(np.abs(audio_array))
                
                if energy < self.audio_config.noise_threshold:
                    if silence_start is None:
                        silence_start = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                    elif self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - silence_start > self.audio_config.silence_timeout:
                        break  # End of speech detected
                else:
                    silence_start = None
                
            except queue.Empty:
                continue
        
        if audio_chunks:
            return b''.join(audio_chunks)
        return None
    
    async def _transcribe_audio(self, audio_data: np.ndarray) -> Optional[STTResult]:
        """Transcribe audio data to text"""
        
        start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        
        try:
            # Analyze emotional tone
            emotional_tone, audio_features = self.emotional_analyzer.analyze_audio_emotion(
                audio_data, self.audio_config.sample_rate
            )
            
            # Mock transcription (in production, use Whisper or similar)
            text = await self._mock_transcribe(audio_data)
            
            processing_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
            
            return STTResult(
                text=text,
                confidence=0.85,  # Mock confidence
                emotional_tone=emotional_tone,
                audio_features=audio_features,
                processing_time=processing_time,
                timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            )
            
        except Exception as e:
            self.logger.error(f"Error transcribing audio: {e}")
            return None
    
    async def _mock_transcribe(self, audio_data: np.ndarray) -> str:
        """Mock transcription for testing"""
        
        # Perform actual operation
        await asyncio.sleep(0.2)
        
        # Return mock text based on audio characteristics
        if len(audio_data) > 16000:  # Longer audio
            return "This is a longer speech input that I'm processing."
        else:
            return "Short voice input detected."
    
    def get_status(self) -> Dict[str, Any]:
        """Get current STT status"""
        return {
            "state": self.state.value,
            "is_listening": self.is_listening,
            "use_mock": self.use_mock,
            "audio_available": AUDIO_AVAILABLE,
            "sample_rate": self.audio_config.sample_rate,
            "channels": self.audio_config.channels
        }
    
    async def shutdown(self):
        """Shutdown STT engine"""
        await self.stop_listening()
        
        if hasattr(self, 'pyaudio') and self.pyaudio:
            self.pyaudio.terminate()
        
        self.logger.info("STT engine shutdown complete")

# Global STT engine instance
stt_engine = STTEngine()

async def start_voice_listening():
    """Global function to start voice listening"""
    return await stt_engine.start_listening()

async def process_voice_input(timeout: float = 5.0) -> Optional[STTResult]:
    """Global function to process voice input"""
    return await stt_engine.process_voice_input(timeout)

async def stop_voice_listening():
    """Global function to stop voice listening"""
    await stt_engine.stop_listening()

def get_stt_status() -> Dict[str, Any]:
    """Global function to get STT status"""
    return stt_engine.get_status()