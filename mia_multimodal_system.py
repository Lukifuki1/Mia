#!/usr/bin/env python3
"""
🎨 MIA Multimodal System - Image, Video, Audio Generation
Lokalna generacija vseh modalnosti brez zunanjih API-jev
"""

import os
import sys
import json
import time
import threading
import logging
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
import tempfile
import base64
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = ImageDraw = ImageFont = ImageFilter = ImageEnhance = None
import numpy as np
import io


@dataclass
class GenerationRequest:
    """Request for content generation"""
    prompt: str
    modality: str  # "image", "video", "audio", "text"
    style: str = "default"
    quality: str = "medium"  # "low", "medium", "high"
    adult_mode: bool = False
    custom_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_params is None:
            self.custom_params = {}


class MIAImageGenerator:
    """MIA Image Generation System"""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.images_path = data_path / "generated" / "images"
        self.images_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_logging()
        
        # Available generators
        self.generators = {}
        self._initialize_generators()
        
        # Style presets
        self.styles = self._load_style_presets()
        
        self.logger.info("🎨 MIA Image Generator initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup image generator logging"""
        logger = logging.getLogger("MIA.ImageGen")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - MIA.ImageGen - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _initialize_generators(self):
        """Initialize image generation engines"""
        # 1. Try Stable Diffusion (diffusers)
        try:
            from diffusers import StableDiffusionPipeline
            import torch
            
            # Check if CUDA is available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Load a small model for testing
            model_id = "runwayml/stable-diffusion-v1-5"
            pipe = StableDiffusionPipeline.from_pretrained(
                model_id, 
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                safety_checker=None,  # Disable safety checker for 18+ mode
                requires_safety_checker=False
            )
            pipe = pipe.to(device)
            
            self.generators["stable_diffusion"] = pipe
            self.logger.info(f"✅ Stable Diffusion initialized on {device}")
            
        except ImportError:
            self.logger.warning("Stable Diffusion (diffusers) not available")
        except Exception as e:
            self.logger.error(f"Stable Diffusion initialization error: {e}")
        
        # 2. Fallback: Procedural generation
        self.generators["procedural"] = self._procedural_generator
        self.logger.info("✅ Procedural image generator available")
    
    def _load_style_presets(self) -> Dict[str, Dict[str, Any]]:
        """Load style presets"""
        return {
            "default": {
                "guidance_scale": 7.5,
                "num_inference_steps": 20,
                "width": 512,
                "height": 512
            },
            "artistic": {
                "guidance_scale": 10.0,
                "num_inference_steps": 30,
                "width": 512,
                "height": 512,
                "prompt_suffix": ", artistic, masterpiece, detailed"
            },
            "photorealistic": {
                "guidance_scale": 8.0,
                "num_inference_steps": 25,
                "width": 768,
                "height": 768,
                "prompt_suffix": ", photorealistic, high quality, detailed"
            },
            "anime": {
                "guidance_scale": 9.0,
                "num_inference_steps": 25,
                "width": 512,
                "height": 512,
                "prompt_suffix": ", anime style, manga, detailed"
            },
            "adult_18plus": {
                "guidance_scale": 8.0,
                "num_inference_steps": 30,
                "width": 768,
                "height": 768,
                "prompt_suffix": ", artistic, sensual, detailed"
            }
        }
    
    def generate_image(self, request: GenerationRequest) -> Optional[str]:
        """Generate image from prompt"""
        self.logger.info(f"🎨 Generating image: {request.prompt[:50]}...")
        
        try:
            # Choose generator
            if "stable_diffusion" in self.generators and request.quality in ["medium", "high"]:
                return self._generate_stable_diffusion(request)
            else:
                return self._generate_procedural(request)
                
        except Exception as e:
            self.logger.error(f"Image generation error: {e}")
            return None
    
    def _generate_stable_diffusion(self, request: GenerationRequest) -> Optional[str]:
        """Generate image using Stable Diffusion"""
        try:
            pipe = self.generators["stable_diffusion"]
            style_config = self.styles.get(request.style, self.styles["default"])
            
            # Prepare prompt
            prompt = request.prompt
            if "prompt_suffix" in style_config:
                prompt += style_config["prompt_suffix"]
            
            # Generate image
            with torch.no_grad():
                result = pipe(
                    prompt,
                    guidance_scale=style_config.get("guidance_scale", 7.5),
                    num_inference_steps=style_config.get("num_inference_steps", 20),
                    width=style_config.get("width", 512),
                    height=style_config.get("height", 512),
                    **request.custom_params
                )
            
            # Save image
            image = result.images[0]
            timestamp = int(time.time())
            filename = f"sd_{timestamp}_{hashlib.md5(request.prompt.encode()).hexdigest()[:8]}.png"
            filepath = self.images_path / filename
            
            image.save(filepath)
            
            self.logger.info(f"✅ Generated image: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Stable Diffusion generation error: {e}")
            return None
    
    def _generate_procedural(self, request: GenerationRequest) -> Optional[str]:
        """Generate image using procedural methods"""
        return self._procedural_generator(request)
    
    def _procedural_generator(self, request: GenerationRequest) -> Optional[str]:
        """Procedural image generator (fallback)"""
        if not PIL_AVAILABLE:
            self.logger.error("PIL not available - cannot generate images")
            return None
            
        try:
            # Create base image
            width, height = 512, 512
            if request.quality == "high":
                width, height = 1024, 1024
            elif request.quality == "low":
                width, height = 256, 256
            
            # Generate based on prompt keywords
            prompt_lower = request.prompt.lower()
            
            if "landscape" in prompt_lower or "nature" in prompt_lower:
                image = self._generate_landscape(width, height)
            elif "portrait" in prompt_lower or "person" in prompt_lower:
                image = self._generate_portrait(width, height)
            elif "abstract" in prompt_lower or "art" in prompt_lower:
                image = self._generate_abstract(width, height)
            else:
                image = self._generate_pattern(width, height, request.prompt)
            
            # Apply style effects
            if request.style == "artistic":
                image = image.filter(ImageFilter.SMOOTH)
                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(1.3)
            elif request.style == "photorealistic":
                image = image.filter(ImageFilter.SHARPEN)
            
            # Save image
            timestamp = int(time.time())
            filename = f"proc_{timestamp}_{hashlib.md5(request.prompt.encode()).hexdigest()[:8]}.png"
            filepath = self.images_path / filename
            
            image.save(filepath)
            
            self.logger.info(f"✅ Generated procedural image: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Procedural generation error: {e}")
            return None
    
    def _generate_landscape(self, width: int, height: int):
        """Generate landscape image"""
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        # Sky gradient
        for y in range(height // 2):
            color_intensity = int(135 + (120 * y / (height // 2)))
            color = (color_intensity, color_intensity + 20, 255)
            draw.line([(0, y), (width, y)], fill=color)
        
        # Ground
        for y in range(height // 2, height):
            color_intensity = int(100 - (50 * (y - height // 2) / (height // 2)))
            color = (color_intensity, color_intensity + 30, color_intensity // 2)
            draw.line([(0, y), (width, y)], fill=color)
        
        # Add some hills
        points = [(0, height // 2 + 50), (width // 4, height // 2 - 30), 
                 (width // 2, height // 2 + 20), (3 * width // 4, height // 2 - 40), 
                 (width, height // 2 + 30), (width, height), (0, height)]
        draw.polygon(points, fill=(60, 120, 40))
        
        return image
    
    def _generate_portrait(self, width: int, height: int):
        """Generate portrait placeholder"""
        image = Image.new('RGB', (width, height), color=(240, 230, 220))
        draw = ImageDraw.Draw(image)
        
        # Face oval
        face_width = width // 3
        face_height = height // 2
        face_x = width // 2 - face_width // 2
        face_y = height // 3 - face_height // 2
        
        draw.ellipse([face_x, face_y, face_x + face_width, face_y + face_height], 
                    fill=(255, 220, 177), outline=(200, 180, 140))
        
        # Eyes
        eye_y = face_y + face_height // 3
        draw.ellipse([face_x + face_width // 4 - 10, eye_y - 5, 
                     face_x + face_width // 4 + 10, eye_y + 5], fill=(50, 50, 50))
        draw.ellipse([face_x + 3 * face_width // 4 - 10, eye_y - 5, 
                     face_x + 3 * face_width // 4 + 10, eye_y + 5], fill=(50, 50, 50))
        
        # Mouth
        mouth_y = face_y + 2 * face_height // 3
        draw.arc([face_x + face_width // 4, mouth_y - 10, 
                 face_x + 3 * face_width // 4, mouth_y + 10], 0, 180, fill=(150, 100, 100))
        
        return image
    
    def _generate_abstract(self, width: int, height: int):
        """Generate abstract art"""
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        # Random colored shapes
        import random
        for _ in range(20):
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            
            shape_type = random.choice(['rectangle', 'ellipse', 'line'])
            if shape_type == 'rectangle':
                draw.rectangle([min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)], 
                             fill=color, outline=color)
            elif shape_type == 'ellipse':
                draw.ellipse([min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)], 
                           fill=color, outline=color)
            else:
                draw.line([x1, y1, x2, y2], fill=color, width=random.randint(1, 5))
        
        return image
    
    def _generate_pattern(self, width: int, height: int, prompt: str):
        """Generate pattern based on prompt"""
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Simple text-based pattern
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw prompt as pattern
        if font:
            text_width, text_height = draw.textsize(prompt[:20], font=font)
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            draw.text((x, y), prompt[:20], fill=(100, 100, 100), font=font)
        
        # Add decorative elements
        for i in range(0, width, 50):
            for j in range(0, height, 50):
                draw.rectangle([i, j, i + 20, j + 20], outline=(200, 200, 200))
        
        return image


class MIAVideoGenerator:
    """MIA Video Generation System"""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.videos_path = data_path / "generated" / "videos"
        self.videos_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_logging()
        
        # Video generation tools
        self.generators = {}
        self._initialize_generators()
        
        self.logger.info("🎬 MIA Video Generator initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup video generator logging"""
        logger = logging.getLogger("MIA.VideoGen")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - MIA.VideoGen - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _initialize_generators(self):
        """Initialize video generation tools"""
        # Check for FFmpeg
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.generators["ffmpeg"] = "ffmpeg"
                self.logger.info("✅ FFmpeg available for video generation")
        except FileNotFoundError:
            self.logger.warning("FFmpeg not available")
        
        # Fallback: Image sequence generator
        self.generators["image_sequence"] = self._generate_image_sequence
        self.logger.info("✅ Image sequence generator available")
    
    def generate_video(self, request: GenerationRequest) -> Optional[str]:
        """Generate video from prompt"""
        self.logger.info(f"🎬 Generating video: {request.prompt[:50]}...")
        
        try:
            if "ffmpeg" in self.generators:
                return self._generate_with_ffmpeg(request)
            else:
                return self._generate_image_sequence(request)
                
        except Exception as e:
            self.logger.error(f"Video generation error: {e}")
            return None
    
    def _generate_with_ffmpeg(self, request: GenerationRequest) -> Optional[str]:
        """Generate video using FFmpeg"""
        try:
            # Create temporary directory for frames
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Generate frames (simple animation)
                frame_count = 30  # 1 second at 30fps
                for i in range(frame_count):
                    frame_request = GenerationRequest(
                        prompt=f"{request.prompt} frame {i}",
                        modality="image",
                        style=request.style,
                        quality="medium"
                    )
                    
                    # Generate frame using image generator
                    from mia_multimodal_system import MIAImageGenerator
                    img_gen = MIAImageGenerator(self.data_path)
                    frame_path = img_gen.generate_image(frame_request)
                    
                    if frame_path:
                        # Copy to temp directory with sequential naming
                        frame_name = f"frame_{i:04d}.png"
                        subprocess.run(['cp', frame_path, str(temp_path / frame_name)])
                
                # Create video with FFmpeg
                timestamp = int(time.time())
                video_filename = f"video_{timestamp}_{hashlib.md5(request.prompt.encode()).hexdigest()[:8]}.mp4"
                video_path = self.videos_path / video_filename
                
                cmd = [
                    'ffmpeg', '-y',
                    '-framerate', '30',
                    '-i', str(temp_path / 'frame_%04d.png'),
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    str(video_path)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.logger.info(f"✅ Generated video: {video_path}")
                    return str(video_path)
                else:
                    self.logger.error(f"FFmpeg error: {result.stderr}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"FFmpeg video generation error: {e}")
            return None
    
    def _generate_image_sequence(self, request: GenerationRequest) -> Optional[str]:
        """Generate video as image sequence (fallback)"""
        try:
            # Create directory for sequence
            timestamp = int(time.time())
            sequence_name = f"sequence_{timestamp}_{hashlib.md5(request.prompt.encode()).hexdigest()[:8]}"
            sequence_path = self.videos_path / sequence_name
            sequence_path.mkdir(exist_ok=True)
            
            # Generate multiple frames
            frame_count = 10
            for i in range(frame_count):
                frame_request = GenerationRequest(
                    prompt=f"{request.prompt} variation {i}",
                    modality="image",
                    style=request.style,
                    quality="medium"
                )
                
                # Generate frame
                from mia_multimodal_system import MIAImageGenerator
                img_gen = MIAImageGenerator(self.data_path)
                frame_path = img_gen.generate_image(frame_request)
                
                if frame_path:
                    # Copy to sequence directory
                    frame_name = f"frame_{i:04d}.png"
                    subprocess.run(['cp', frame_path, str(sequence_path / frame_name)])
            
            # Create info file
            info_file = sequence_path / "info.json"
            with open(info_file, 'w') as f:
                json.dump({
                    "prompt": request.prompt,
                    "frame_count": frame_count,
                    "type": "image_sequence",
                    "created": time.time()
                }, f, indent=2)
            
            self.logger.info(f"✅ Generated image sequence: {sequence_path}")
            return str(sequence_path)
            
        except Exception as e:
            self.logger.error(f"Image sequence generation error: {e}")
            return None


class MIAAudioGenerator:
    """MIA Audio Generation System"""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.audio_path = data_path / "generated" / "audio"
        self.audio_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_logging()
        
        # Audio generation tools
        self.generators = {}
        self._initialize_generators()
        
        self.logger.info("🎵 MIA Audio Generator initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup audio generator logging"""
        logger = logging.getLogger("MIA.AudioGen")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - MIA.AudioGen - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _initialize_generators(self):
        """Initialize audio generation tools"""
        # Check for SoX (Sound eXchange)
        try:
            result = subprocess.run(['sox', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.generators["sox"] = "sox"
                self.logger.info("✅ SoX available for audio generation")
        except FileNotFoundError:
            self.logger.warning("SoX not available")
        
        # Fallback: Procedural audio generation
        self.generators["procedural"] = self._generate_procedural_audio
        self.logger.info("✅ Procedural audio generator available")
    
    def generate_audio(self, request: GenerationRequest) -> Optional[str]:
        """Generate audio from prompt"""
        self.logger.info(f"🎵 Generating audio: {request.prompt[:50]}...")
        
        try:
            if "sox" in self.generators:
                return self._generate_with_sox(request)
            else:
                return self._generate_procedural_audio(request)
                
        except Exception as e:
            self.logger.error(f"Audio generation error: {e}")
            return None
    
    def _generate_with_sox(self, request: GenerationRequest) -> Optional[str]:
        """Generate audio using SoX"""
        try:
            timestamp = int(time.time())
            audio_filename = f"audio_{timestamp}_{hashlib.md5(request.prompt.encode()).hexdigest()[:8]}.wav"
            audio_path = self.audio_path / audio_filename
            
            # Generate different types of audio based on prompt
            prompt_lower = request.prompt.lower()
            
            if "music" in prompt_lower or "melody" in prompt_lower:
                # Generate simple melody
                cmd = [
                    'sox', '-n', str(audio_path),
                    'synth', '5', 'pluck', 'C4', 'E4', 'G4', 'C5'
                ]
            elif "noise" in prompt_lower or "ambient" in prompt_lower:
                # Generate ambient noise
                cmd = [
                    'sox', '-n', str(audio_path),
                    'synth', '10', 'brownnoise', 'vol', '0.3'
                ]
            elif "tone" in prompt_lower or "beep" in prompt_lower:
                # Generate tone
                cmd = [
                    'sox', '-n', str(audio_path),
                    'synth', '3', 'sine', '440'
                ]
            else:
                # Default: simple chord
                cmd = [
                    'sox', '-n', str(audio_path),
                    'synth', '4', 'pluck', 'A4', 'C5', 'E5'
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"✅ Generated audio: {audio_path}")
                return str(audio_path)
            else:
                self.logger.error(f"SoX error: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"SoX audio generation error: {e}")
            return None
    
    def _generate_procedural_audio(self, request: GenerationRequest) -> Optional[str]:
        """Generate audio procedurally (fallback)"""
        try:
            import wave
            import struct
            
            # Audio parameters
            sample_rate = 44100
            duration = 5.0  # seconds
            frequency = 440.0  # A4
            
            # Adjust based on prompt
            prompt_lower = request.prompt.lower()
            if "high" in prompt_lower:
                frequency = 880.0
            elif "low" in prompt_lower:
                frequency = 220.0
            elif "music" in prompt_lower:
                frequency = 523.25  # C5
            
            # Generate waveform
            frames = []
            for i in range(int(sample_rate * duration)):
                t = i / sample_rate
                # Simple sine wave with fade in/out
                amplitude = 0.3
                if t < 0.1:  # Fade in
                    amplitude *= t / 0.1
                elif t > duration - 0.1:  # Fade out
                    amplitude *= (duration - t) / 0.1
                
                value = amplitude * np.sin(2 * np.pi * frequency * t)
                frames.append(struct.pack('<h', int(value * 32767)))
            
            # Save to file
            timestamp = int(time.time())
            audio_filename = f"proc_audio_{timestamp}_{hashlib.md5(request.prompt.encode()).hexdigest()[:8]}.wav"
            audio_path = self.audio_path / audio_filename
            
            with wave.open(str(audio_path), 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(b''.join(frames))
            
            self.logger.info(f"✅ Generated procedural audio: {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            self.logger.error(f"Procedural audio generation error: {e}")
            return None


class MIAMultimodalSystem:
    """Complete MIA Multimodal Generation System"""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.logger = self._setup_logging()
        
        # Initialize generators
        self.image_generator = MIAImageGenerator(data_path)
        self.video_generator = MIAVideoGenerator(data_path)
        self.audio_generator = MIAAudioGenerator(data_path)
        
        # Generation history
        self.generation_history = []
        
        self.logger.info("🎨🎬🎵 MIA Multimodal System initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup multimodal system logging"""
        logger = logging.getLogger("MIA.Multimodal")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - MIA.Multimodal - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def generate(self, prompt: str, modality: str, style: str = "default", 
                quality: str = "medium", adult_mode: bool = False, **kwargs) -> Optional[str]:
        """Generate content in specified modality"""
        request = GenerationRequest(
            prompt=prompt,
            modality=modality,
            style=style,
            quality=quality,
            adult_mode=adult_mode,
            custom_params=kwargs
        )
        
        self.logger.info(f"🎯 Generating {modality}: {prompt[:50]}...")
        
        result = None
        
        if modality == "image":
            result = self.image_generator.generate_image(request)
        elif modality == "video":
            result = self.video_generator.generate_video(request)
        elif modality == "audio":
            result = self.audio_generator.generate_audio(request)
        else:
            self.logger.error(f"Unknown modality: {modality}")
            return None
        
        # Store in history
        if result:
            self.generation_history.append({
                "prompt": prompt,
                "modality": modality,
                "style": style,
                "quality": quality,
                "adult_mode": adult_mode,
                "result": result,
                "timestamp": time.time()
            })
        
        return result
    
    def generate_image(self, prompt: str, style: str = "default", quality: str = "medium", 
                      adult_mode: bool = False, **kwargs) -> Optional[str]:
        """Generate image"""
        return self.generate(prompt, "image", style, quality, adult_mode, **kwargs)
    
    def generate_video(self, prompt: str, style: str = "default", quality: str = "medium", 
                      adult_mode: bool = False, **kwargs) -> Optional[str]:
        """Generate video"""
        return self.generate(prompt, "video", style, quality, adult_mode, **kwargs)
    
    def generate_audio(self, prompt: str, style: str = "default", quality: str = "medium", 
                      adult_mode: bool = False, **kwargs) -> Optional[str]:
        """Generate audio"""
        return self.generate(prompt, "audio", style, quality, adult_mode, **kwargs)
    
    def get_generation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent generation history"""
        return self.generation_history[-limit:]
    
    def get_available_styles(self, modality: str) -> List[str]:
        """Get available styles for modality"""
        if modality == "image":
            return list(self.image_generator.styles.keys())
        else:
            return ["default", "artistic", "ambient", "energetic"]
    
    def clear_history(self):
        """Clear generation history"""
        self.generation_history.clear()
        self.logger.info("🧹 Generation history cleared")


def main():
    """Test MIA Multimodal System"""
    print("🎨 MIA Multimodal System Test")
    print("=" * 35)
    
    # Initialize multimodal system
    multimodal = MIAMultimodalSystem(Path("mia_data"))
    
    # Test image generation
    print("\n🎨 Testing Image Generation...")
    image_path = multimodal.generate_image("beautiful landscape with mountains and lake", "artistic", "medium")
    if image_path:
        print(f"✅ Generated image: {image_path}")
    
    # Test different styles
    styles = multimodal.get_available_styles("image")
    print(f"Available image styles: {styles}")
    
    # Test video generation
    print("\n🎬 Testing Video Generation...")
    video_path = multimodal.generate_video("animated sunset over ocean", "default", "medium")
    if video_path:
        print(f"✅ Generated video: {video_path}")
    
    # Test audio generation
    print("\n🎵 Testing Audio Generation...")
    audio_path = multimodal.generate_audio("peaceful ambient music", "ambient", "medium")
    if audio_path:
        print(f"✅ Generated audio: {audio_path}")
    
    # Show history
    print("\n📜 Generation History:")
    history = multimodal.get_generation_history()
    for item in history:
        print(f"- {item['modality']}: {item['prompt'][:30]}... -> {item['result']}")
    
    print("\n✅ Multimodal system test completed")


if __name__ == "__main__":
    main()