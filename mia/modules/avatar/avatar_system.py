#!/usr/bin/env python3
"""
MIA Avatar System
Vizualni avatar z emocionalno mimiko in real-time animacijo
"""

import os
import json
import logging
import time
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import asyncio

class AvatarMode(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Avatar display modes"""
    NORMAL = "normal"
    ADULT = "adult"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    EXPRESSIVE = "expressive"

class EmotionalState(Enum):
    """Emotional states for avatar"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    FOCUSED = "focused"
    CONFUSED = "confused"
    CONFIDENT = "confident"
    CARING = "caring"
    PLAYFUL = "playful"
    SEDUCTIVE = "seductive"  # For adult mode

class AnimationType(Enum):
    """Types of animations"""
    IDLE = "idle"
    SPEAKING = "speaking"
    LISTENING = "listening"
    THINKING = "thinking"
    REACTING = "reacting"
    GESTURE = "gesture"

@dataclass
class AvatarState:
    """Current avatar state"""
    emotional_state: EmotionalState
    animation_type: AnimationType
    mode: AvatarMode
    eye_contact: bool
    speaking: bool
    attention_level: float
    expression_intensity: float

@dataclass
class AnimationFrame:
    """Single animation frame"""
    frame_id: str
    timestamp: float
    facial_expression: Dict[str, float]
    eye_position: Tuple[float, float]
    mouth_shape: str
    gesture_data: Dict[str, Any]
    metadata: Dict[str, Any]

class AvatarSystem:
    """MIA Avatar System with emotional rendering"""
    
    def __init__(self, config_path: str = "mia/data/avatar/config.json"):
        self.config_path = config_path
        self.avatar_dir = Path("mia/data/avatar")
        self.avatar_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.AvatarSystem")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Avatar state
        self.current_state = AvatarState(
            emotional_state=EmotionalState.NEUTRAL,
            animation_type=AnimationType.IDLE,
            mode=AvatarMode.NORMAL,
            eye_contact=True,
            speaking=False,
            attention_level=0.8,
            expression_intensity=0.5
        )
        
        # Animation system
        self.animation_queue: List[AnimationFrame] = []
        self.current_animation: Optional[AnimationFrame] = None
        self.animation_thread: Optional[threading.Thread] = None
        self.animation_active = False
        
        # Emotional expressions
        self.expression_templates = self._load_expression_templates()
        
        # Avatar assets
        self.avatar_assets = self._load_avatar_assets()
        
        # WebGL/Canvas integration
        self.canvas_context = None
        self.webgl_renderer = None
        
        self.logger.info("👤 Avatar System initialized")
    
    def _load_configuration(self) -> Dict:
        """Load avatar configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load avatar config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default avatar configuration"""
        config = {
            "enabled": True,
            "rendering_engine": "webgl",  # webgl, canvas, live2d
            "frame_rate": 30,
            "animation_smoothing": True,
            "eye_tracking": True,
            "lip_sync": True,
            "gesture_recognition": True,
            "emotional_responsiveness": 0.8,
            "avatar_styles": {
                "normal": {
                    "base_model": "default_female",
                    "clothing": "casual",
                    "hair_style": "medium_length",
                    "eye_color": "brown",
                    "expression_range": "full"
                },
                "professional": {
                    "base_model": "default_female",
                    "clothing": "business",
                    "hair_style": "professional",
                    "eye_color": "brown",
                    "expression_range": "moderate"
                },
                "adult": {
                    "base_model": "adult_female",
                    "clothing": "intimate",
                    "hair_style": "flowing",
                    "eye_color": "seductive",
                    "expression_range": "enhanced"
                }
            },
            "animation_settings": {
                "idle_frequency": 3.0,  # seconds
                "blink_frequency": 2.5,
                "micro_expressions": True,
                "breathing_animation": True,
                "subtle_movements": True
            },
            "adult_mode": {
                "enabled": False,
                "enhanced_expressions": True,
                "intimate_gestures": True,
                "seductive_animations": True,
                "adult_voice_sync": True
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _load_expression_templates(self) -> Dict[str, Dict[str, float]]:
        """Load facial expression templates"""
        try:
            expressions = {
                EmotionalState.NEUTRAL: {
                    "eyebrow_left": 0.0,
                    "eyebrow_right": 0.0,
                    "eye_left_open": 0.8,
                    "eye_right_open": 0.8,
                    "mouth_smile": 0.1,
                    "mouth_open": 0.0,
                    "cheek_lift": 0.0
                },
                EmotionalState.HAPPY: {
                    "eyebrow_left": 0.2,
                    "eyebrow_right": 0.2,
                    "eye_left_open": 0.7,
                    "eye_right_open": 0.7,
                    "mouth_smile": 0.8,
                    "mouth_open": 0.1,
                    "cheek_lift": 0.6
                },
                EmotionalState.SAD: {
                    "eyebrow_left": -0.3,
                    "eyebrow_right": -0.3,
                    "eye_left_open": 0.6,
                    "eye_right_open": 0.6,
                    "mouth_smile": -0.4,
                    "mouth_open": 0.0,
                    "cheek_lift": -0.2
                },
                EmotionalState.EXCITED: {
                    "eyebrow_left": 0.4,
                    "eyebrow_right": 0.4,
                    "eye_left_open": 0.9,
                    "eye_right_open": 0.9,
                    "mouth_smile": 0.9,
                    "mouth_open": 0.3,
                    "cheek_lift": 0.8
                },
                EmotionalState.FOCUSED: {
                    "eyebrow_left": -0.1,
                    "eyebrow_right": -0.1,
                    "eye_left_open": 0.9,
                    "eye_right_open": 0.9,
                    "mouth_smile": 0.0,
                    "mouth_open": 0.0,
                    "cheek_lift": 0.0
                },
                EmotionalState.CONFUSED: {
                    "eyebrow_left": 0.3,
                    "eyebrow_right": -0.2,
                    "eye_left_open": 0.8,
                    "eye_right_open": 0.7,
                    "mouth_smile": -0.1,
                    "mouth_open": 0.1,
                    "cheek_lift": 0.0
                },
                EmotionalState.CONFIDENT: {
                    "eyebrow_left": 0.1,
                    "eyebrow_right": 0.1,
                    "eye_left_open": 0.8,
                    "eye_right_open": 0.8,
                    "mouth_smile": 0.4,
                    "mouth_open": 0.0,
                    "cheek_lift": 0.3
                },
                EmotionalState.CARING: {
                    "eyebrow_left": 0.2,
                    "eyebrow_right": 0.2,
                    "eye_left_open": 0.7,
                    "eye_right_open": 0.7,
                    "mouth_smile": 0.5,
                    "mouth_open": 0.0,
                    "cheek_lift": 0.4
                },
                EmotionalState.PLAYFUL: {
                    "eyebrow_left": 0.3,
                    "eyebrow_right": 0.1,
                    "eye_left_open": 0.8,
                    "eye_right_open": 0.6,
                    "mouth_smile": 0.7,
                    "mouth_open": 0.1,
                    "cheek_lift": 0.5
                },
                EmotionalState.SEDUCTIVE: {
                    "eyebrow_left": 0.1,
                    "eyebrow_right": 0.1,
                    "eye_left_open": 0.6,
                    "eye_right_open": 0.6,
                    "mouth_smile": 0.3,
                    "mouth_open": 0.2,
                    "cheek_lift": 0.2
                }
            }
            
            return expressions
            
        except Exception as e:
            self.logger.error(f"Failed to load expression templates: {e}")
            return {}
    
    def _load_avatar_assets(self) -> Dict[str, Any]:
        """Load avatar assets and models"""
        try:
            assets = {
                "models": {
                    "default_female": "assets/models/female_base.json",
                    "adult_female": "assets/models/female_adult.json"
                },
                "textures": {
                    "skin": "assets/textures/skin_default.png",
                    "eyes": "assets/textures/eyes_brown.png",
                    "hair": "assets/textures/hair_brown.png"
                },
                "animations": {
                    "idle": "assets/animations/idle.json",
                    "speaking": "assets/animations/speaking.json",
                    "gestures": "assets/animations/gestures.json"
                },
                "clothing": {
                    "casual": "assets/clothing/casual.json",
                    "business": "assets/clothing/business.json",
                    "intimate": "assets/clothing/intimate.json"
                }
            }
            
            # Create default assets if they don't exist
            self._create_default_assets(assets)
            
            return assets
            
        except Exception as e:
            self.logger.error(f"Failed to load avatar assets: {e}")
            return {}
    
    def _create_default_assets(self, assets: Dict[str, Any]):
        """Create default assets for avatar system"""
        try:
            assets_dir = self.avatar_dir / "assets"
            assets_dir.mkdir(exist_ok=True)
            
            # Create default model files
            models_dir = assets_dir / "models"
            models_dir.mkdir(exist_ok=True)
            
            default_model = {
                "name": "MIA Avatar",
                "version": "1.0",
                "type": "basic_avatar",
                "vertices": [
                    {"x": 0, "y": 0, "z": 0},
                    {"x": 1, "y": 0, "z": 0},
                    {"x": 0, "y": 1, "z": 0}
                ],
                "faces": [{"v1": 0, "v2": 1, "v3": 2}],
                "bones": [{"name": "root", "position": [0, 0, 0]}],
                "animations": [{"name": "idle", "frames": []}]
            }
            
            for model_name in ["female_base.json", "female_adult.json"]:
                model_file = models_dir / model_name
                if not model_file.exists():
                    with open(model_file, 'w') as f:
                        json.dump(default_model, f, indent=2)
            
            self.logger.info("✅ Default avatar assets created")
            
        except Exception as e:
            self.logger.error(f"Failed to create default assets: {e}")
    
    def set_emotional_state(self, emotional_state: EmotionalState, intensity: float = 1.0):
        """Set avatar emotional state"""
        try:
            self.current_state.emotional_state = emotional_state
            self.current_state.expression_intensity = intensity
            
            # Generate animation frame for new emotional state
            self._generate_emotional_animation(emotional_state, intensity)
            
            self.logger.info(f"👤 Avatar emotional state: {emotional_state.value} (intensity: {intensity})")
            
        except Exception as e:
            self.logger.error(f"Failed to set emotional state: {e}")
    
    def set_avatar_mode(self, mode: AvatarMode):
        """Set avatar display mode"""
        try:
            self.current_state.mode = mode
            
            # Apply mode-specific styling
            self._apply_mode_styling(mode)
            
            self.logger.info(f"👤 Avatar mode: {mode.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to set avatar mode: {e}")
    
    def start_speaking_animation(self, text: str, voice_data: Optional[bytes] = None):
        """Start speaking animation with lip sync"""
        try:
            self.current_state.speaking = True
            self.current_state.animation_type = AnimationType.SPEAKING
            
            # Generate lip sync animation
            lip_sync_frames = self._generate_lip_sync_animation(text, voice_data)
            
            # Add frames to animation queue
            for frame in lip_sync_frames:
                self.animation_queue.append(frame)
            
            self.logger.info(f"👤 Started speaking animation for: {text[:50]}...")
            
        except Exception as e:
            self.logger.error(f"Failed to start speaking animation: {e}")
    
    def stop_speaking_animation(self):
        """Stop speaking animation"""
        try:
            self.current_state.speaking = False
            self.current_state.animation_type = AnimationType.IDLE
            
            # Clear speaking animations from queue
            self.animation_queue = [f for f in self.animation_queue if f.metadata.get("type") != "speaking"]
            
            self.logger.info("👤 Stopped speaking animation")
            
        except Exception as e:
            self.logger.error(f"Failed to stop speaking animation: {e}")
    
    def set_eye_contact(self, enabled: bool, target_position: Optional[Tuple[float, float]] = None):
        """Set eye contact and gaze direction"""
        try:
            self.current_state.eye_contact = enabled
            
            if enabled and target_position:
                # Generate eye movement animation
                eye_frame = self._generate_eye_movement_frame(target_position)
                self.animation_queue.append(eye_frame)
            
            self.logger.debug(f"👤 Eye contact: {enabled}")
            
        except Exception as e:
            self.logger.error(f"Failed to set eye contact: {e}")
    
    def add_gesture(self, gesture_type: str, intensity: float = 1.0):
        """Add gesture animation"""
        try:
            gesture_frames = self._generate_gesture_animation(gesture_type, intensity)
            
            for frame in gesture_frames:
                self.animation_queue.append(frame)
            
            self.logger.info(f"👤 Added gesture: {gesture_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to add gesture: {e}")
    
    def _generate_emotional_animation(self, emotional_state: EmotionalState, intensity: float):
        """Generate animation for emotional state"""
        try:
            if emotional_state not in self.expression_templates:
                return
            
            expression = self.expression_templates[emotional_state]
            
            # Apply intensity scaling
            scaled_expression = {}
            for key, value in expression.items():
                scaled_expression[key] = value * intensity
            
            # Create animation frame
            frame = AnimationFrame(
                frame_id=f"emotion_{emotional_state.value}_{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}",
                timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                facial_expression=scaled_expression,
                eye_position=(0.0, 0.0),
                mouth_shape="neutral",
                gesture_data={},
                metadata={"type": "emotional", "state": emotional_state.value}
            )
            
            self.animation_queue.append(frame)
            
        except Exception as e:
            self.logger.error(f"Failed to generate emotional animation: {e}")
    
    def _apply_mode_styling(self, mode: AvatarMode):
        """Apply mode-specific styling"""
        try:
            style_config = self.config.get("avatar_styles", {}).get(mode.value, {})
            
            # Apply styling changes
            # This would modify the avatar's appearance based on the mode
            
            self.logger.debug(f"Applied styling for mode: {mode.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to apply mode styling: {e}")
    
    def _generate_lip_sync_animation(self, text: str, voice_data: Optional[bytes] = None) -> List[AnimationFrame]:
        """Generate lip sync animation frames"""
        try:
            frames = []
            
            # Simple phoneme-based lip sync
            phoneme_map = {
                'a': 'open',
                'e': 'wide',
                'i': 'smile',
                'o': 'round',
                'u': 'pucker',
                'm': 'closed',
                'p': 'closed',
                'b': 'closed',
                'f': 'narrow',
                'v': 'narrow'
            }
            
            # Generate frames based on text
            frame_duration = 1.0 / self.config.get("frame_rate", 30)
            current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            for i, char in enumerate(text.lower()):
                if char in phoneme_map:
                    mouth_shape = phoneme_map[char]
                    
                    frame = AnimationFrame(
                        frame_id=f"lipsync_{i}_{current_time}",
                        timestamp=current_time + (i * frame_duration),
                        facial_expression=self.expression_templates.get(self.current_state.emotional_state, {}),
                        eye_position=(0.0, 0.0),
                        mouth_shape=mouth_shape,
                        gesture_data={},
                        metadata={"type": "speaking", "phoneme": char}
                    )
                    
                    frames.append(frame)
            
            return frames
            
        except Exception as e:
            self.logger.error(f"Failed to generate lip sync animation: {e}")
            return []
    
    def _generate_eye_movement_frame(self, target_position: Tuple[float, float]) -> AnimationFrame:
        """Generate eye movement frame"""
        try:
            frame = AnimationFrame(
                frame_id=f"eye_movement_{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}",
                timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                facial_expression=self.expression_templates.get(self.current_state.emotional_state, {}),
                eye_position=target_position,
                mouth_shape="neutral",
                gesture_data={},
                metadata={"type": "eye_movement"}
            )
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Failed to generate eye movement frame: {e}")
            return None
    
    def _generate_gesture_animation(self, gesture_type: str, intensity: float) -> List[AnimationFrame]:
        """Generate gesture animation frames"""
        try:
            frames = []
            
            # Simple gesture animations
            gesture_data = {
                "nod": {"head_rotation": (10 * intensity, 0, 0)},
                "shake": {"head_rotation": (0, 15 * intensity, 0)},
                "wave": {"hand_position": (50 * intensity, 0, 0)},
                "point": {"hand_position": (30 * intensity, -20, 0)}
            }
            
            if gesture_type in gesture_data:
                frame = AnimationFrame(
                    frame_id=f"gesture_{gesture_type}_{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}",
                    timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                    facial_expression=self.expression_templates.get(self.current_state.emotional_state, {}),
                    eye_position=(0.0, 0.0),
                    mouth_shape="neutral",
                    gesture_data=gesture_data[gesture_type],
                    metadata={"type": "gesture", "gesture": gesture_type}
                )
                
                frames.append(frame)
            
            return frames
            
        except Exception as e:
            self.logger.error(f"Failed to generate gesture animation: {e}")
            return []
    
    def start_animation_system(self):
        """Start animation processing system"""
        try:
            if self.animation_active:
                return
            
            self.animation_active = True
            self.animation_thread = threading.Thread(
                target=self._animation_loop,
                daemon=True
            )
            self.animation_thread.start()
            
            self.logger.info("👤 Avatar animation system started")
            
        except Exception as e:
            self.logger.error(f"Failed to start animation system: {e}")
    
    def stop_animation_system(self):
        """Stop animation processing system"""
        try:
            self.animation_active = False
            
            if self.animation_thread:
                self.animation_thread.join(timeout=5.0)
            
            self.logger.info("👤 Avatar animation system stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop animation system: {e}")
    
    def _animation_loop(self):
        """Main animation processing loop"""
        frame_duration = 1.0 / self.config.get("frame_rate", 30)
        
        while self.animation_active:
            try:
                current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                
                # Process animation queue
                if self.animation_queue:
                    # Get next frame
                    next_frame = self.animation_queue.pop(0)
                    
                    if next_frame.timestamp <= current_time:
                        self.current_animation = next_frame
                        self._render_frame(next_frame)
                    else:
                        # Put frame back if not ready
                        self.animation_queue.insert(0, next_frame)
                
                # Generate idle animation if no other animations
                if not self.animation_queue and not self.current_state.speaking:
                    self._generate_idle_animation()
                
                time.sleep(frame_duration)
                
            except Exception as e:
                self.logger.error(f"Error in animation loop: {e}")
                time.sleep(frame_duration)
    
    def _generate_idle_animation(self):
        """Generate idle animation frames"""
        try:
            current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            idle_frequency = self.config.get("animation_settings", {}).get("idle_frequency", 3.0)
            
            # Generate subtle idle movements
            if hasattr(self, '_last_idle_time'):
                if current_time - self._last_idle_time < idle_frequency:
                    return
            
            self._last_idle_time = current_time
            
            # Subtle breathing animation
            breathing_frame = AnimationFrame(
                frame_id=f"idle_breathing_{current_time}",
                timestamp=current_time,
                facial_expression=self.expression_templates.get(self.current_state.emotional_state, {}),
                eye_position=(0.0, 0.0),
                mouth_shape="neutral",
                gesture_data={"breathing": 0.1},
                metadata={"type": "idle", "subtype": "breathing"}
            )
            
            self.animation_queue.append(breathing_frame)
            
        except Exception as e:
            self.logger.error(f"Failed to generate idle animation: {e}")
    
    def _render_frame(self, frame: AnimationFrame):
        """Render animation frame"""
        try:
            # This would render the frame to the UI
            # For now, just log the frame data
            
            self.logger.debug(f"👤 Rendering frame: {frame.frame_id}")
            
            # In a real implementation, this would:
            # 1. Update WebGL/Canvas rendering
            # 2. Apply facial expressions
            # 3. Update eye positions
            # 4. Apply gestures
            # 5. Sync with audio if speaking
            
        except Exception as e:
            self.logger.error(f"Failed to render frame: {e}")
    
    def get_avatar_status(self) -> Dict[str, Any]:
        """Get avatar system status"""
        try:
            return {
                "enabled": self.config.get("enabled", True),
                "animation_active": self.animation_active,
                "current_state": asdict(self.current_state),
                "animation_queue_length": len(self.animation_queue),
                "current_animation": asdict(self.current_animation) if self.current_animation else None,
                "frame_rate": self.config.get("frame_rate", 30),
                "rendering_engine": self.config.get("rendering_engine", "webgl")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get avatar status: {e}")
            return {"error": str(e)}

# Global instance
avatar_system = AvatarSystem()