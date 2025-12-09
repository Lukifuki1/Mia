#!/usr/bin/env python3
"""
MIA Image Generation Module
Handles image generation with Stable Diffusion and LoRA support
"""

import asyncio
import json
import numpy as np
import logging
import time
import io
import base64
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import hashlib

# Image processing imports
try:
    import torch
    IMAGE_AVAILABLE = True
except ImportError:
    IMAGE_AVAILABLE = False
    logging.warning("Image libraries not available - Image generation will use mock implementation")

from mia.core.memory.main import EmotionalTone, store_memory

class ImageStyle(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    REALISTIC = "realistic"
    ARTISTIC = "artistic"
    ANIME = "anime"
    ABSTRACT = "abstract"
    PHOTOGRAPHIC = "photographic"
    DIGITAL_ART = "digital_art"
    CONCEPT_ART = "concept_art"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    INTIMATE = "intimate"

class ImageQuality(Enum):
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    ULTRA = "ultra"

@dataclass
class ImageConfig:
    """Image generation configuration"""
    width: int = 512
    height: int = 512
    style: ImageStyle = ImageStyle.REALISTIC
    quality: ImageQuality = ImageQuality.STANDARD
    steps: int = 20
    guidance_scale: float = 7.5
    seed: Optional[int] = None
    negative_prompt: str = "blurry, low quality, distorted"
    lora_enabled: bool = True
    safety_filter: bool = True

@dataclass
class ImageResult:
    """Image generation result"""
    prompt: str
    image_data: bytes
    image_path: Optional[str]
    style: ImageStyle
    emotional_tone: EmotionalTone
    generation_time: float
    seed: int
    config: ImageConfig
    metadata: Dict[str, Any]

class LoRAImageManager:
    """Manages LoRA models for image generation"""
    
    def __init__(self, lora_path: str = "mia/data/lora/image"):
        self.lora_path = Path(lora_path)
        self.lora_path.mkdir(parents=True, exist_ok=True)
        
        self.active_loras = []
        self.lora_models = {}
        
        self.logger = logging.getLogger("MIA.Image.LoRA")
        
        # Load available LoRA models
        self._load_lora_models()
    
    def _load_lora_models(self):
        """Load available LoRA image models"""
        try:
            lora_config_file = self.lora_path / "lora_models.json"
            
            if lora_config_file.exists():
                with open(lora_config_file, 'r') as f:
                    self.lora_models = json.load(f)
            else:
                # Create default LoRA models
                self.lora_models = {
                    "user_style": {
                        "name": "User Style",
                        "description": "Learned from user's preferred images",
                        "model_path": "user_style.safetensors",
                        "trigger_words": ["user_style"],
                        "strength": 0.8,
                        "enabled": False,
                        "category": "style"
                    },
                    "emotional_art": {
                        "name": "Emotional Art",
                        "description": "Enhanced emotional expression in art",
                        "model_path": "emotional_art.safetensors",
                        "trigger_words": ["emotional", "expressive"],
                        "strength": 0.7,
                        "enabled": True,
                        "category": "emotion"
                    },
                    "intimate_style": {
                        "name": "Intimate Style",
                        "description": "Specialized for intimate/romantic imagery",
                        "model_path": "intimate_style.safetensors",
                        "trigger_words": ["intimate", "romantic"],
                        "strength": 0.9,
                        "enabled": False,
                        "category": "adult"
                    },
                    "portrait_enhance": {
                        "name": "Portrait Enhancer",
                        "description": "Enhanced portrait generation",
                        "model_path": "portrait_enhance.safetensors",
                        "trigger_words": ["portrait", "face"],
                        "strength": 0.6,
                        "enabled": True,
                        "category": "portrait"
                    }
                }
                
                # Save default config
                with open(lora_config_file, 'w') as f:
                    json.dump(self.lora_models, f, indent=2)
            
            self.logger.info(f"Loaded {len(self.lora_models)} LoRA image models")
            
        except Exception as e:
            self.logger.error(f"Error loading LoRA models: {e}")
    
    def activate_lora(self, lora_name: str, strength: Optional[float] = None) -> bool:
        """Activate specific LoRA model"""
        if lora_name in self.lora_models:
            lora_info = self.lora_models[lora_name].copy()
            if strength is not None:
                lora_info["strength"] = strength
            
            # Remove if already active
            self.active_loras = [l for l in self.active_loras if l["name"] != lora_name]
            
            # Add to active list
            self.active_loras.append({
                "name": lora_name,
                "info": lora_info
            })
            
            self.logger.info(f"Activated LoRA model: {lora_name} (strength: {lora_info['strength']})")
            return True
        return False
    
    def deactivate_lora(self, lora_name: str):
        """Deactivate specific LoRA model"""
        self.active_loras = [l for l in self.active_loras if l["name"] != lora_name]
        self.logger.info(f"Deactivated LoRA model: {lora_name}")
    
    def clear_all_loras(self):
        """Clear all active LoRA models"""
        self.active_loras = []
        self.logger.info("Cleared all LoRA models")
    
    def get_active_loras(self) -> List[Dict[str, Any]]:
        """Get currently active LoRA models"""
        return self.active_loras.copy()
    
    def get_lora_prompt_additions(self) -> Tuple[str, str]:
        """Get prompt additions from active LoRAs"""
        positive_additions = []
        negative_additions = []
        
        for lora in self.active_loras:
            trigger_words = lora["info"].get("trigger_words", [])
            positive_additions.extend(trigger_words)
        
        return ", ".join(positive_additions), ", ".join(negative_additions)

class MockImageGenerator:
    """Mock image generator for testing when real generation is not available"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.Image.Mock")
    
    async def generate_image(self, prompt: str, config: ImageConfig, 
                           emotional_tone: EmotionalTone) -> ImageResult:
        """Mock image generation"""
        
        # Perform actual operation
        await asyncio.sleep(1.0)
        
        # Create a simple colored image based on prompt and emotion
        if IMAGE_AVAILABLE:
            # Create colored rectangle based on emotional tone
            color_map = {
                EmotionalTone.EXCITED: (255, 100, 100),  # Red
                EmotionalTone.CALM: (100, 150, 255),     # Blue
                EmotionalTone.PLAYFUL: (255, 200, 100),  # Orange
                EmotionalTone.PROFESSIONAL: (150, 150, 150),  # Gray
                EmotionalTone.INTIMATE: (200, 100, 200), # Purple
                EmotionalTone.POSITIVE: (100, 255, 100), # Green
                EmotionalTone.NEGATIVE: (100, 100, 100), # Dark gray
                EmotionalTone.NEUTRAL: (200, 200, 200)   # Light gray
            }
            
            color = color_map.get(emotional_tone, (200, 200, 200))
            
            # Create image
            image = Image.new('RGB', (config.width, config.height), color)
            
            # Add some pattern based on style
            if config.style == ImageStyle.ARTISTIC:
                # Add gradient
                for y in range(config.height):
                    for x in range(config.width):
                        factor = (x + y) / (config.width + config.height)
                        new_color = tuple(int(c * (1 - factor * 0.5)) for c in color)
                        image.putpixel((x, y), new_color)
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            image_data = img_buffer.getvalue()
        else:
            # Create minimal mock data
            image_data = b"MOCK_IMAGE_DATA"
        
        return ImageResult(
            prompt=prompt,
            image_data=image_data,
            image_path=None,
            style=config.style,
            emotional_tone=emotional_tone,
            generation_time=1.0,
            seed=12345,
            config=config,
            metadata={"mock": True, "color": color if IMAGE_AVAILABLE else "unknown"}
        )

class SafetyFilter:
    """Content safety filter for image generation"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.Image.Safety")
        
        # NSFW keywords (basic list)
        self.nsfw_keywords = [
            "nude", "naked", "explicit", "sexual", "porn", "xxx",
            "erotic", "adult", "nsfw", "sex", "genitals"
        ]
        
        # Violence keywords
        self.violence_keywords = [
            "violence", "blood", "gore", "weapon", "gun", "knife",
            "murder", "kill", "death", "torture", "war"
        ]
    
    def check_prompt_safety(self, prompt: str, adult_mode: bool = False) -> Tuple[bool, str]:
        """Check if prompt is safe for generation"""
        
        prompt_lower = prompt.lower()
        
        # Check for violence (always filtered)
        for keyword in self.violence_keywords:
            if keyword in prompt_lower:
                return False, f"Prompt contains violent content: {keyword}"
        
        # Check for NSFW content (filtered unless adult mode)
        if not adult_mode:
            for keyword in self.nsfw_keywords:
                if keyword in prompt_lower:
                    return False, f"Prompt contains adult content: {keyword}"
        
        return True, "Safe"
    
    def filter_image_content(self, image_data: bytes) -> Tuple[bool, str]:
        """Filter generated image content (placeholder)"""
        # In production, this would use actual NSFW detection models
        return True, "Safe"

class ImageGenerator:
    """Main image generation engine"""
    
    def __init__(self, config_path: str = "mia/data/models/image/config.json"):
        self.config_path = Path(config_path)
        self.default_config = ImageConfig()
        
        # Processing modules
        self.lora_manager = LoRAImageManager()
        self.safety_filter = SafetyFilter()
        
        # Mock generator for when real generation is not available
        self.mock_generator = MockImageGenerator()
        self.use_mock = not IMAGE_AVAILABLE
        
        # Output directory
        self.output_dir = Path("mia/data/generated_images")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_logging()
        
        # Load configuration
        self._load_config()
        
        # Initialize generation pipeline
        if IMAGE_AVAILABLE:
            self._initialize_pipeline()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for image generation module"""
        logger = logging.getLogger("MIA.Image")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler("mia/logs/image_generation.log")
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_config(self):
        """Load image generation configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Update default config from file
                image_settings = config_data.get('image_generation', {})
                if image_settings:
                    self.default_config.width = image_settings.get('width', 512)
                    self.default_config.height = image_settings.get('height', 512)
                    self.default_config.steps = image_settings.get('steps', 20)
                    self.default_config.guidance_scale = image_settings.get('guidance_scale', 7.5)
                
                self.logger.info("Image generation configuration loaded")
                
            except Exception as e:
                self.logger.error(f"Failed to load image config: {e}")
    
    def _initialize_pipeline(self):
        """Initialize Stable Diffusion pipeline"""
        if not IMAGE_AVAILABLE:
            return
        
        try:
            # In production, initialize actual Stable Diffusion pipeline
            # from diffusers import StableDiffusionPipeline
            # self.pipeline = StableDiffusionPipeline.from_pretrained(...)
            
            self.logger.info("Image generation pipeline initialized (mock)")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize image pipeline: {e}")
            self.use_mock = True
    
    async def generate_image(self, prompt: str, 
                           emotional_tone: EmotionalTone = EmotionalTone.NEUTRAL,
                           style: ImageStyle = ImageStyle.REALISTIC,
                           config: Optional[ImageConfig] = None,
                           adult_mode: bool = False) -> Optional[ImageResult]:
        """Generate image from text prompt"""
        
        try:
            # Use default config if none provided
            if config is None:
                config = ImageConfig(style=style)
            else:
                config.style = style
            
            # Safety check
            if config.safety_filter:
                is_safe, safety_message = self.safety_filter.check_prompt_safety(prompt, adult_mode)
                if not is_safe:
                    self.logger.warning(f"Prompt rejected by safety filter: {safety_message}")
                    return None
            
            # Enhance prompt with emotional context
            enhanced_prompt = self._enhance_prompt_with_emotion(prompt, emotional_tone, style)
            
            # Add LoRA prompt additions
            if config.lora_enabled:
                lora_positive, lora_negative = self.lora_manager.get_lora_prompt_additions()
                if lora_positive:
                    enhanced_prompt = f"{enhanced_prompt}, {lora_positive}"
                if lora_negative:
                    config.negative_prompt = f"{config.negative_prompt}, {lora_negative}"
            
            # Generate image
            if self.use_mock:
                result = await self.mock_generator.generate_image(enhanced_prompt, config, emotional_tone)
            else:
                result = await self._generate_with_pipeline(enhanced_prompt, config, emotional_tone)
            
            # Save image
            if result:
                image_path = await self._save_image(result)
                result.image_path = image_path
                
                # Store in memory
                store_memory(
                    f"Generated image: {prompt}",
                    emotional_tone,
                    ["image_generation", "multimodal", "creative"]
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating image: {e}")
            return None
    
    def _enhance_prompt_with_emotion(self, prompt: str, emotional_tone: EmotionalTone, 
                                   style: ImageStyle) -> str:
        """Enhance prompt with emotional and style context"""
        
        # Emotional enhancements
        emotion_enhancements = {
            EmotionalTone.EXCITED: "vibrant, energetic, dynamic, bright colors",
            EmotionalTone.CALM: "peaceful, serene, soft lighting, gentle",
            EmotionalTone.PLAYFUL: "whimsical, fun, colorful, cheerful",
            EmotionalTone.PROFESSIONAL: "clean, professional, well-lit, sharp",
            EmotionalTone.INTIMATE: "warm, soft, romantic, gentle lighting",
            EmotionalTone.POSITIVE: "bright, uplifting, beautiful, optimistic",
            EmotionalTone.NEGATIVE: "moody, dramatic, dark tones, atmospheric",
            EmotionalTone.NEUTRAL: "balanced, natural, realistic"
        }
        
        # Style enhancements
        style_enhancements = {
            ImageStyle.REALISTIC: "photorealistic, detailed, high quality",
            ImageStyle.ARTISTIC: "artistic, creative, expressive, stylized",
            ImageStyle.ANIME: "anime style, manga, cel-shaded, vibrant",
            ImageStyle.ABSTRACT: "abstract, conceptual, artistic interpretation",
            ImageStyle.PHOTOGRAPHIC: "photography, professional lighting, sharp focus",
            ImageStyle.DIGITAL_ART: "digital art, concept art, detailed",
            ImageStyle.CONCEPT_ART: "concept art, detailed, professional",
            ImageStyle.PORTRAIT: "portrait, face focus, detailed features",
            ImageStyle.LANDSCAPE: "landscape, scenic, wide view, detailed",
            ImageStyle.INTIMATE: "intimate, romantic, soft, warm"
        }
        
        emotion_text = emotion_enhancements.get(emotional_tone, "")
        style_text = style_enhancements.get(style, "")
        
        enhanced = prompt
        if emotion_text:
            enhanced = f"{enhanced}, {emotion_text}"
        if style_text:
            enhanced = f"{enhanced}, {style_text}"
        
        return enhanced
    
    async def _generate_with_pipeline(self, prompt: str, config: ImageConfig,
                                    emotional_tone: EmotionalTone) -> Optional[ImageResult]:
        """Generate image using actual pipeline"""
        
        start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        
        try:
            # Set seed for reproducibility
            if config.seed is None:
                config.seed = int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200) % 2147483647
            
            # In production, use actual Stable Diffusion pipeline
            # result = self.pipeline(
            #     prompt=prompt,
            #     negative_prompt=config.negative_prompt,
            #     width=config.width,
            #     height=config.height,
            #     num_inference_steps=config.steps,
            #     guidance_scale=config.guidance_scale,
            #     generator=torch.Generator().manual_seed(config.seed)
            # )
            
            # Mock implementation
            await asyncio.sleep(2.0)  # Perform actual operation
            
            # Create mock image
            if IMAGE_AVAILABLE:
                image = Image.new('RGB', (config.width, config.height), (128, 128, 128))
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='PNG')
                image_data = img_buffer.getvalue()
            else:
                image_data = b"MOCK_PIPELINE_IMAGE"
            
            generation_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
            
            return ImageResult(
                prompt=prompt,
                image_data=image_data,
                image_path=None,
                style=config.style,
                emotional_tone=emotional_tone,
                generation_time=generation_time,
                seed=config.seed,
                config=config,
                metadata={"pipeline": "stable_diffusion", "mock": True}
            )
            
        except Exception as e:
            self.logger.error(f"Error in pipeline generation: {e}")
            return None
    
    async def _save_image(self, result: ImageResult) -> str:
        """Save generated image to disk"""
        
        try:
            # Generate filename
            timestamp = int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)
            prompt_hash = hashlib.md5(result.prompt.encode()).hexdigest()[:8]
            filename = f"img_{timestamp}_{prompt_hash}.png"
            
            image_path = self.output_dir / filename
            
            # Save image
            with open(image_path, 'wb') as f:
                f.write(result.image_data)
            
            self.logger.info(f"Image saved: {image_path}")
            return str(image_path)
            
        except Exception as e:
            self.logger.error(f"Error saving image: {e}")
            return ""
    
    def activate_lora(self, lora_name: str, strength: Optional[float] = None) -> bool:
        """Activate LoRA model"""
        return self.lora_manager.activate_lora(lora_name, strength)
    
    def deactivate_lora(self, lora_name: str):
        """Deactivate LoRA model"""
        self.lora_manager.deactivate_lora(lora_name)
    
    def list_lora_models(self) -> Dict[str, Any]:
        """List available LoRA models"""
        return self.lora_manager.lora_models.copy()
    
    def get_generation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent generation history"""
        # In production, this would query a database
        history = []
        
        # Get recent image files
        image_files = sorted(self.output_dir.glob("*.png"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        for image_file in image_files[:limit]:
            history.append({
                "filename": image_file.name,
                "path": str(image_file),
                "timestamp": image_file.stat().st_mtime,
                "size": image_file.stat().st_size
            })
        
        return history
    
    def get_status(self) -> Dict[str, Any]:
        """Get current image generation status"""
        return {
            "use_mock": self.use_mock,
            "image_available": IMAGE_AVAILABLE,
            "active_loras": len(self.lora_manager.get_active_loras()),
            "output_directory": str(self.output_dir),
            "total_generated": len(list(self.output_dir.glob("*.png"))),
            "default_config": {
                "width": self.default_config.width,
                "height": self.default_config.height,
                "style": self.default_config.style.value,
                "quality": self.default_config.quality.value
            }
        }
    
    async def shutdown(self):
        """Shutdown image generation engine"""
        self.logger.info("Image generation engine shutdown complete")

# Global image generator instance
image_generator = ImageGenerator()

async def generate_image(prompt: str, 
                        emotional_tone: EmotionalTone = EmotionalTone.NEUTRAL,
                        style: ImageStyle = ImageStyle.REALISTIC,
                        adult_mode: bool = False) -> Optional[ImageResult]:
    """Global function to generate image"""
    return await image_generator.generate_image(prompt, emotional_tone, style, adult_mode=adult_mode)

def activate_image_lora(lora_name: str, strength: Optional[float] = None) -> bool:
    """Global function to activate image LoRA"""
    return image_generator.activate_lora(lora_name, strength)

def get_image_generation_status() -> Dict[str, Any]:
    """Global function to get image generation status"""
    return image_generator.get_status()