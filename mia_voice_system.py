#!/usr/bin/env python3
"""
🎙️ MIA Voice System - TTS & STT
Lokalni glasovni sistem z emocionalnimi profili
"""

import os
import sys
import json
import time
import threading
import logging
import wave
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    pyaudio = None
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import subprocess
import tempfile
import io


@dataclass
class VoiceProfile:
    """Voice profile configuration"""
    name: str
    language: str = "sl"
    gender: str = "female"
    emotion: str = "neutral"
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0
    model_path: Optional[str] = None


class MIATextToSpeech:
    """MIA Text-to-Speech System"""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.voice_data_path = data_path / "voice"
        self.voice_data_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_logging()
        
        # Voice profiles
        self.profiles = self._load_voice_profiles()
        self.current_profile = self.profiles.get("default", VoiceProfile("default"))
        
        # TTS engines
        self.engines = {}
        self._initialize_engines()
        
        self.logger.info("🎙️ MIA TTS System initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup TTS logging"""
        logger = logging.getLogger("MIA.TTS")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - MIA.TTS - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _load_voice_profiles(self) -> Dict[str, VoiceProfile]:
        """Load voice profiles"""
        profiles_file = self.voice_data_path / "profiles.json"
        
        # Default profiles
        default_profiles = {
            "default": VoiceProfile("default", "sl", "female", "neutral"),
            "professional": VoiceProfile("professional", "sl", "female", "calm", 0.9, 1.0, 0.8),
            "empathetic": VoiceProfile("empathetic", "sl", "female", "warm", 0.8, 0.9, 0.9),
            "playful": VoiceProfile("playful", "sl", "female", "happy", 1.2, 1.1, 1.0),
            "dominant": VoiceProfile("dominant", "sl", "female", "confident", 0.9, 1.2, 1.1),
            "sensual": VoiceProfile("sensual", "sl", "female", "seductive", 0.7, 0.8, 0.9),
            "adult_18plus": VoiceProfile("adult_18plus", "sl", "female", "intimate", 0.8, 0.9, 1.0)
        }
        
        if profiles_file.exists():
            try:
                with open(profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    profiles = {}
                    for name, profile_data in data.items():
                        profiles[name] = VoiceProfile(**profile_data)
                    return profiles
            except Exception as e:
                self.logger.error(f"Error loading voice profiles: {e}")
        
        # Save default profiles
        self._save_voice_profiles(default_profiles)
        return default_profiles
    
    def _save_voice_profiles(self, profiles: Dict[str, VoiceProfile]):
        """Save voice profiles"""
        profiles_file = self.voice_data_path / "profiles.json"
        try:
            data = {name: profile.__dict__ for name, profile in profiles.items()}
            with open(profiles_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving voice profiles: {e}")
    
    def _initialize_engines(self):
        """Initialize TTS engines"""
        # Try to initialize different TTS engines
        
        # 1. Try pyttsx3 (cross-platform)
        try:
            import pyttsx3
            engine = pyttsx3.init()
            self.engines["pyttsx3"] = engine
            self.logger.info("✅ pyttsx3 TTS engine initialized")
        except ImportError:
            self.logger.warning("pyttsx3 not available")
        except Exception as e:
            self.logger.error(f"pyttsx3 initialization error: {e}")
        
        # 2. Try gTTS (requires internet, but we'll use it for voice generation)
        try:
            from gtts import gTTS
            self.engines["gtts"] = gTTS
            self.logger.info("✅ gTTS engine available")
        except ImportError:
            self.logger.warning("gTTS not available")
        
        # 3. Try espeak (Linux)
        try:
            result = subprocess.run(['espeak', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.engines["espeak"] = "espeak"
                self.logger.info("✅ espeak TTS engine available")
        except FileNotFoundError:
            self.logger.warning("espeak not available")
        
        # 4. Try festival (Linux)
        try:
            result = subprocess.run(['festival', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.engines["festival"] = "festival"
                self.logger.info("✅ festival TTS engine available")
        except FileNotFoundError:
            self.logger.warning("festival not available")
        
        if not self.engines:
            self.logger.warning("No TTS engines available - using fallback")
    
    def speak(self, text: str, profile_name: str = None, save_audio: bool = False) -> Optional[str]:
        """Convert text to speech"""
        if not text.strip():
            return None
        
        # Use specified profile or current
        profile = self.profiles.get(profile_name, self.current_profile) if profile_name else self.current_profile
        
        self.logger.info(f"🗣️ Speaking with profile '{profile.name}': {text[:50]}...")
        
        # Generate audio
        audio_file = None
        
        if "pyttsx3" in self.engines:
            audio_file = self._speak_pyttsx3(text, profile, save_audio)
        elif "espeak" in self.engines:
            audio_file = self._speak_espeak(text, profile, save_audio)
        elif "festival" in self.engines:
            audio_file = self._speak_festival(text, profile, save_audio)
        else:
            # Fallback - just log the text
            self.logger.info(f"🔊 MIA says: {text}")
            return None
        
        return audio_file
    
    def _speak_pyttsx3(self, text: str, profile: VoiceProfile, save_audio: bool) -> Optional[str]:
        """Speak using pyttsx3"""
        try:
            engine = self.engines["pyttsx3"]
            
            # Configure voice properties
            voices = engine.getProperty('voices')
            if voices:
                # Try to find female voice
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            # Set properties based on profile
            engine.setProperty('rate', int(200 * profile.speed))
            engine.setProperty('volume', profile.volume)
            
            if save_audio:
                # Save to file
                audio_file = self.voice_data_path / f"tts_{int(time.time())}.wav"
                engine.save_to_file(text, str(audio_file))
                engine.runAndWait()
                return str(audio_file)
            else:
                # Speak directly
                engine.say(text)
                engine.runAndWait()
                return None
                
        except Exception as e:
            self.logger.error(f"pyttsx3 error: {e}")
            return None
    
    def _speak_espeak(self, text: str, profile: VoiceProfile, save_audio: bool) -> Optional[str]:
        """Speak using espeak"""
        try:
            # Build espeak command
            cmd = ['espeak']
            
            # Voice selection
            if profile.language == "sl":
                cmd.extend(['-v', 'sl'])
            else:
                cmd.extend(['-v', 'en'])
            
            # Speed and pitch
            cmd.extend(['-s', str(int(175 * profile.speed))])
            cmd.extend(['-p', str(int(50 * profile.pitch))])
            cmd.extend(['-a', str(int(100 * profile.volume))])
            
            if save_audio:
                audio_file = self.voice_data_path / f"tts_{int(time.time())}.wav"
                cmd.extend(['-w', str(audio_file)])
                cmd.append(text)
                
                subprocess.run(cmd, check=True)
                return str(audio_file)
            else:
                cmd.append(text)
                subprocess.run(cmd, check=True)
                return None
                
        except Exception as e:
            self.logger.error(f"espeak error: {e}")
            return None
    
    def _speak_festival(self, text: str, profile: VoiceProfile, save_audio: bool) -> Optional[str]:
        """Speak using festival"""
        try:
            if save_audio:
                audio_file = self.voice_data_path / f"tts_{int(time.time())}.wav"
                cmd = ['festival', '--tts', '--output', str(audio_file)]
            else:
                cmd = ['festival', '--tts']
            
            # Run festival with text input
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, text=True)
            process.communicate(input=text)
            
            return str(audio_file) if save_audio else None
            
        except Exception as e:
            self.logger.error(f"festival error: {e}")
            return None
    
    def set_profile(self, profile_name: str):
        """Set current voice profile"""
        if profile_name in self.profiles:
            self.current_profile = self.profiles[profile_name]
            self.logger.info(f"🎭 Voice profile changed to: {profile_name}")
        else:
            self.logger.warning(f"Voice profile not found: {profile_name}")
    
    def create_profile(self, name: str, **kwargs) -> VoiceProfile:
        """Create new voice profile"""
        profile = VoiceProfile(name, **kwargs)
        self.profiles[name] = profile
        self._save_voice_profiles(self.profiles)
        self.logger.info(f"✨ Created voice profile: {name}")
        return profile
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available voice profiles"""
        return list(self.profiles.keys())


class MIASpeechToText:
    """MIA Speech-to-Text System"""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.audio_data_path = data_path / "audio"
        self.audio_data_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_logging()
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.channels = 1
        self.format = pyaudio.paInt16
        
        # Initialize audio
        if PYAUDIO_AVAILABLE:
            self.audio = pyaudio.PyAudio()
        else:
            self.audio = None
            self.logger.warning("PyAudio not available - voice input disabled")
        
        # STT engines
        self.engines = {}
        self._initialize_engines()
        
        # Recording state
        self.is_recording = False
        self.recording_thread = None
        
        self.logger.info("🎤 MIA STT System initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup STT logging"""
        logger = logging.getLogger("MIA.STT")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - MIA.STT - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _initialize_engines(self):
        """Initialize STT engines"""
        # Try to initialize different STT engines
        
        # 1. Try speech_recognition
        try:
            import speech_recognition as sr
            self.engines["speech_recognition"] = sr.Recognizer()
            self.logger.info("✅ speech_recognition STT engine initialized")
        except ImportError:
            self.logger.warning("speech_recognition not available")
        
        # 2. Try whisper (OpenAI Whisper)
        try:
            import whisper
            model = whisper.load_model("base")
            self.engines["whisper"] = model
            self.logger.info("✅ Whisper STT engine initialized")
        except ImportError:
            self.logger.warning("whisper not available")
        except Exception as e:
            self.logger.error(f"Whisper initialization error: {e}")
        
        if not self.engines:
            self.logger.warning("No STT engines available")
    
    def start_listening(self, callback: Callable[[str], None] = None, 
                       continuous: bool = False, timeout: float = 5.0):
        """Start listening for speech"""
        if not PYAUDIO_AVAILABLE or not self.audio:
            self.logger.error("PyAudio not available - cannot start listening")
            return
            
        if self.is_recording:
            self.logger.warning("Already recording")
            return
        
        self.is_recording = True
        self.recording_thread = threading.Thread(
            target=self._listen_loop, 
            args=(callback, continuous, timeout),
            daemon=True
        )
        self.recording_thread.start()
        
        self.logger.info("🎤 Started listening...")
    
    def stop_listening(self):
        """Stop listening for speech"""
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)
        self.logger.info("🔇 Stopped listening")
    
    def _listen_loop(self, callback: Callable[[str], None], continuous: bool, timeout: float):
        """Main listening loop"""
        try:
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            while self.is_recording:
                # Record audio
                audio_data = self._record_audio_chunk(stream, timeout)
                
                if audio_data:
                    # Convert to text
                    text = self._transcribe_audio(audio_data)
                    
                    if text and callback:
                        callback(text)
                    
                    if not continuous:
                        break
                
        except Exception as e:
            self.logger.error(f"Listening error: {e}")
        finally:
            try:
                stream.stop_stream()
                stream.close()
            except:
                pass
            self.is_recording = False
    
    def _record_audio_chunk(self, stream, timeout: float) -> Optional[bytes]:
        """Record audio chunk"""
        try:
            frames = []
            start_time = time.time()
            silence_threshold = 500
            silence_duration = 0
            
            while self.is_recording and (time.time() - start_time) < timeout:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                # Simple voice activity detection
                audio_data = np.frombuffer(data, dtype=np.int16)
                volume = np.sqrt(np.mean(audio_data**2))
                
                if volume < silence_threshold:
                    silence_duration += self.chunk_size / self.sample_rate
                    if silence_duration > 1.0:  # 1 second of silence
                        break
                else:
                    silence_duration = 0
            
            if frames:
                return b''.join(frames)
            
        except Exception as e:
            self.logger.error(f"Recording error: {e}")
        
        return None
    
    def _transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio to text"""
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                # Write WAV header and data
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(self.channels)
                    wav_file.setsampwidth(self.audio.get_sample_size(self.format))
                    wav_file.setframerate(self.sample_rate)
                    wav_file.writeframes(audio_data)
                
                # Transcribe using available engine
                text = None
                
                if "whisper" in self.engines:
                    text = self._transcribe_whisper(temp_file.name)
                elif "speech_recognition" in self.engines:
                    text = self._transcribe_speech_recognition(temp_file.name)
                
                # Clean up
                os.unlink(temp_file.name)
                
                if text:
                    self.logger.info(f"🎯 Transcribed: {text}")
                
                return text
                
        except Exception as e:
            self.logger.error(f"Transcription error: {e}")
            return None
    
    def _transcribe_whisper(self, audio_file: str) -> Optional[str]:
        """Transcribe using Whisper"""
        try:
            model = self.engines["whisper"]
            result = model.transcribe(audio_file)
            return result["text"].strip()
        except Exception as e:
            self.logger.error(f"Whisper transcription error: {e}")
            return None
    
    def _transcribe_speech_recognition(self, audio_file: str) -> Optional[str]:
        """Transcribe using speech_recognition"""
        try:
            import speech_recognition as sr
            
            recognizer = self.engines["speech_recognition"]
            
            with sr.AudioFile(audio_file) as source:
                audio = recognizer.record(source)
            
            # Try different recognition services
            try:
                return recognizer.recognize_google(audio, language="sl-SI")
            except:
                try:
                    return recognizer.recognize_google(audio, language="en-US")
                except:
                    return recognizer.recognize_sphinx(audio)
                    
        except Exception as e:
            self.logger.error(f"Speech recognition error: {e}")
            return None
    
    def transcribe_file(self, audio_file: str) -> Optional[str]:
        """Transcribe audio file"""
        if not os.path.exists(audio_file):
            self.logger.error(f"Audio file not found: {audio_file}")
            return None
        
        if "whisper" in self.engines:
            return self._transcribe_whisper(audio_file)
        elif "speech_recognition" in self.engines:
            return self._transcribe_speech_recognition(audio_file)
        
        return None


class MIAVoiceSystem:
    """Complete MIA Voice System"""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.logger = self._setup_logging()
        
        # Initialize TTS and STT
        self.tts = MIATextToSpeech(data_path)
        self.stt = MIASpeechToText(data_path)
        
        # Voice interaction state
        self.listening_active = False
        self.voice_callback = None
        
        self.logger.info("🎙️🎤 MIA Voice System initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup voice system logging"""
        logger = logging.getLogger("MIA.Voice")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - MIA.Voice - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def speak(self, text: str, profile: str = None, emotion: str = None) -> Optional[str]:
        """Speak text with optional profile and emotion"""
        # Adjust profile based on emotion
        if emotion and not profile:
            emotion_profiles = {
                "happy": "playful",
                "sad": "empathetic", 
                "angry": "dominant",
                "calm": "professional",
                "excited": "playful",
                "seductive": "sensual",
                "intimate": "adult_18plus"
            }
            profile = emotion_profiles.get(emotion, "default")
        
        return self.tts.speak(text, profile)
    
    def start_voice_interaction(self, callback: Callable[[str], str]):
        """Start voice interaction loop"""
        self.voice_callback = callback
        self.listening_active = True
        
        def voice_handler(recognized_text: str):
            if self.voice_callback and recognized_text.strip():
                try:
                    response = self.voice_callback(recognized_text)
                    if response:
                        self.speak(response)
                except Exception as e:
                    self.logger.error(f"Voice callback error: {e}")
        
        self.stt.start_listening(voice_handler, continuous=True)
        self.logger.info("🗣️ Voice interaction started")
    
    def stop_voice_interaction(self):
        """Stop voice interaction"""
        self.listening_active = False
        self.stt.stop_listening()
        self.voice_callback = None
        self.logger.info("🔇 Voice interaction stopped")
    
    def set_voice_profile(self, profile_name: str):
        """Set TTS voice profile"""
        self.tts.set_profile(profile_name)
    
    def create_voice_profile(self, name: str, **kwargs):
        """Create new voice profile"""
        return self.tts.create_profile(name, **kwargs)
    
    def get_voice_profiles(self) -> List[str]:
        """Get available voice profiles"""
        return self.tts.get_available_profiles()
    
    def transcribe_audio_file(self, file_path: str) -> Optional[str]:
        """Transcribe audio file to text"""
        return self.stt.transcribe_file(file_path)


def main():
    """Test MIA Voice System"""
    print("🎙️ MIA Voice System Test")
    print("=" * 30)
    
    # Initialize voice system
    voice_system = MIAVoiceSystem(Path("mia_data"))
    
    # Test TTS
    print("\n🗣️ Testing Text-to-Speech...")
    voice_system.speak("Pozdravljeni! Jaz sem MIA, vaša lokalna digitalna inteligentna entiteta.")
    
    # Test different profiles
    profiles = voice_system.get_voice_profiles()
    print(f"Available profiles: {profiles}")
    
    for profile in ["professional", "empathetic", "playful"]:
        if profile in profiles:
            print(f"Testing profile: {profile}")
            voice_system.speak(f"To je moj {profile} glas.", profile)
            time.sleep(1)
    
    # Test STT (if available)
    print("\n🎤 Testing Speech-to-Text...")
    print("Say something (5 seconds)...")
    
    def test_callback(text: str) -> str:
        print(f"Recognized: {text}")
        return f"Slišal sem: {text}"
    
    try:
        voice_system.start_voice_interaction(test_callback)
        time.sleep(10)  # Listen for 10 seconds
        voice_system.stop_voice_interaction()
    except KeyboardInterrupt:
        voice_system.stop_voice_interaction()
    
    print("✅ Voice system test completed")


if __name__ == "__main__":
    main()