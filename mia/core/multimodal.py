#!/usr/bin/env python3
"""
MIA Multimodal System
Basic multimodal capabilities including text-to-speech, image processing, and file handling
"""

import os
import json
import logging
import asyncio
import time
import base64
import hashlib
from typing import Dict, List, Any, Optional, Union, BinaryIO
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import mimetypes
import subprocess
import tempfile

class ModalityType(Enum):
    """Types of modalities"""
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"

class ProcessingStatus(Enum):
    """Processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class MultimodalContent:
    """Multimodal content item"""
    id: str
    modality: ModalityType
    content: Union[str, bytes]
    metadata: Dict[str, Any]
    timestamp: float
    status: ProcessingStatus = ProcessingStatus.PENDING
    processed_content: Optional[Any] = None
    error_message: Optional[str] = None

class MultimodalSystem:
    """Basic multimodal processing system"""
    
    def __init__(self, data_dir: str = "mia_data"):
        self.data_dir = Path(data_dir)
        self.multimodal_dir = self.data_dir / "multimodal"
        self.uploads_dir = self.multimodal_dir / "uploads"
        self.processed_dir = self.multimodal_dir / "processed"
        self.audio_dir = self.multimodal_dir / "audio"
        
        # Create directories
        for dir_path in [self.multimodal_dir, self.uploads_dir, self.processed_dir, self.audio_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.Multimodal")
        
        # Multimodal state
        self.content_items: Dict[str, MultimodalContent] = {}
        
        # Configuration
        self.config = {
            "max_file_size": 50 * 1024 * 1024,  # 50MB
            "supported_image_formats": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
            "supported_audio_formats": [".mp3", ".wav", ".ogg", ".m4a", ".flac"],
            "supported_video_formats": [".mp4", ".avi", ".mov", ".mkv", ".webm"],
            "tts_enabled": True,
            "image_processing_enabled": True,
            "audio_processing_enabled": True
        }
        
        # Check for available tools
        self._check_available_tools()
        
        self.logger.info("🎭 Multimodal system initialized")
    
    def _check_available_tools(self):
        """Check for available multimodal processing tools"""
        self.available_tools = {
            "espeak": self._check_command("espeak"),
            "ffmpeg": self._check_command("ffmpeg"),
            "convert": self._check_command("convert"),  # ImageMagick
            "python_pil": self._check_python_module("PIL"),
            "python_opencv": self._check_python_module("cv2"),
            "python_speech": self._check_python_module("speech_recognition")
        }
        
        available_count = sum(1 for available in self.available_tools.values() if available)
        self.logger.info(f"🔧 Available multimodal tools: {available_count}/{len(self.available_tools)}")
    
    def _check_command(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            subprocess.run([command, "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_python_module(self, module_name: str) -> bool:
        """Check if a Python module is available"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    async def process_text_to_speech(self, text: str, voice: str = "default") -> Optional[str]:
        """Convert text to speech"""
        if not self.config["tts_enabled"] or not self.available_tools["espeak"]:
            self.logger.warning("⚠️ Text-to-speech not available")
            return None
        
        try:
            # Create content item
            content_id = hashlib.md5(f"tts_{text}_{time.time()}".encode()).hexdigest()[:12]
            
            content_item = MultimodalContent(
                id=content_id,
                modality=ModalityType.AUDIO,
                content=text,
                metadata={"voice": voice, "type": "tts"},
                timestamp=time.time(),
                status=ProcessingStatus.PROCESSING
            )
            
            self.content_items[content_id] = content_item
            
            # Generate audio file
            audio_file = self.audio_dir / f"tts_{content_id}.wav"
            
            # Use espeak for TTS
            cmd = [
                "espeak",
                "-w", str(audio_file),
                "-s", "150",  # Speed
                "-p", "50",   # Pitch
                text
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and audio_file.exists():
                content_item.status = ProcessingStatus.COMPLETED
                content_item.processed_content = str(audio_file)
                
                self.logger.info(f"🔊 Generated TTS audio: {content_id}")
                return str(audio_file)
            else:
                content_item.status = ProcessingStatus.FAILED
                content_item.error_message = result.stderr
                self.logger.error(f"❌ TTS generation failed: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ TTS processing error: {e}")
            if content_id in self.content_items:
                self.content_items[content_id].status = ProcessingStatus.FAILED
                self.content_items[content_id].error_message = str(e)
            return None
    
    async def process_image(self, image_path: str, operations: List[str] = None) -> Optional[str]:
        """Process image with basic operations"""
        if not self.config["image_processing_enabled"]:
            self.logger.warning("⚠️ Image processing disabled")
            return None
        
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                self.logger.error(f"❌ Image file not found: {image_path}")
                return None
            
            # Create content item
            content_id = hashlib.md5(f"img_{image_path.name}_{time.time()}".encode()).hexdigest()[:12]
            
            content_item = MultimodalContent(
                id=content_id,
                modality=ModalityType.IMAGE,
                content=str(image_path),
                metadata={"operations": operations or [], "original_path": str(image_path)},
                timestamp=time.time(),
                status=ProcessingStatus.PROCESSING
            )
            
            self.content_items[content_id] = content_item
            
            # Process with PIL if available
            if self.available_tools["python_pil"]:
                processed_path = await self._process_image_with_pil(image_path, operations or [])
            elif self.available_tools["convert"]:
                processed_path = await self._process_image_with_imagemagick(image_path, operations or [])
            else:
                # Basic file copy as fallback
                processed_path = self.processed_dir / f"processed_{content_id}{image_path.suffix}"
                import shutil
                shutil.copy2(image_path, processed_path)
            
            if processed_path and processed_path.exists():
                content_item.status = ProcessingStatus.COMPLETED
                content_item.processed_content = str(processed_path)
                
                self.logger.info(f"🖼️ Processed image: {content_id}")
                return str(processed_path)
            else:
                content_item.status = ProcessingStatus.FAILED
                content_item.error_message = "Processing failed"
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Image processing error: {e}")
            if content_id in self.content_items:
                self.content_items[content_id].status = ProcessingStatus.FAILED
                self.content_items[content_id].error_message = str(e)
            return None
    
    async def _process_image_with_pil(self, image_path: Path, operations: List[str]) -> Optional[Path]:
        """Process image using PIL"""
        try:
            from PIL import Image, ImageEnhance, ImageFilter
            
            # Open image
            with Image.open(image_path) as img:
                # Apply operations
                for operation in operations:
                    if operation == "resize_small":
                        img = img.resize((300, 300), Image.Resampling.LANCZOS)
                    elif operation == "grayscale":
                        img = img.convert("L")
                    elif operation == "enhance_contrast":
                        enhancer = ImageEnhance.Contrast(img)
                        img = enhancer.enhance(1.5)
                    elif operation == "blur":
                        img = img.filter(ImageFilter.BLUR)
                    elif operation == "sharpen":
                        img = img.filter(ImageFilter.SHARPEN)
                
                # Save processed image
                output_path = self.processed_dir / f"pil_{int(time.time())}{image_path.suffix}"
                img.save(output_path)
                
                return output_path
                
        except Exception as e:
            self.logger.error(f"❌ PIL processing error: {e}")
            return None
    
    async def _process_image_with_imagemagick(self, image_path: Path, operations: List[str]) -> Optional[Path]:
        """Process image using ImageMagick"""
        try:
            output_path = self.processed_dir / f"im_{int(time.time())}{image_path.suffix}"
            
            cmd = ["convert", str(image_path)]
            
            # Apply operations
            for operation in operations:
                if operation == "resize_small":
                    cmd.extend(["-resize", "300x300"])
                elif operation == "grayscale":
                    cmd.extend(["-colorspace", "Gray"])
                elif operation == "enhance_contrast":
                    cmd.extend(["-contrast-stretch", "0"])
                elif operation == "blur":
                    cmd.extend(["-blur", "0x1"])
                elif operation == "sharpen":
                    cmd.extend(["-sharpen", "0x1"])
            
            cmd.append(str(output_path))
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and output_path.exists():
                return output_path
            else:
                self.logger.error(f"❌ ImageMagick error: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ ImageMagick processing error: {e}")
            return None
    
    async def handle_file_upload(self, file_content: bytes, filename: str, content_type: str = None) -> Optional[str]:
        """Handle file upload and basic processing"""
        try:
            # Validate file size
            if len(file_content) > self.config["max_file_size"]:
                self.logger.error(f"❌ File too large: {len(file_content)} bytes")
                return None
            
            # Determine file type
            file_path = Path(filename)
            file_extension = file_path.suffix.lower()
            
            # Determine modality
            if file_extension in self.config["supported_image_formats"]:
                modality = ModalityType.IMAGE
            elif file_extension in self.config["supported_audio_formats"]:
                modality = ModalityType.AUDIO
            elif file_extension in self.config["supported_video_formats"]:
                modality = ModalityType.VIDEO
            else:
                modality = ModalityType.FILE
            
            # Create content item
            content_id = hashlib.md5(f"upload_{filename}_{time.time()}".encode()).hexdigest()[:12]
            
            # Save file
            upload_path = self.uploads_dir / f"{content_id}_{filename}"
            with open(upload_path, 'wb') as f:
                f.write(file_content)
            
            content_item = MultimodalContent(
                id=content_id,
                modality=modality,
                content=str(upload_path),
                metadata={
                    "filename": filename,
                    "content_type": content_type,
                    "size": len(file_content),
                    "extension": file_extension
                },
                timestamp=time.time(),
                status=ProcessingStatus.COMPLETED
            )
            
            self.content_items[content_id] = content_item
            
            self.logger.info(f"📁 File uploaded: {filename} ({modality.value})")
            return content_id
            
        except Exception as e:
            self.logger.error(f"❌ File upload error: {e}")
            return None
    
    async def extract_text_from_image(self, image_path: str) -> Optional[str]:
        """Extract text from image using OCR (basic implementation)"""
        try:
            # This is a placeholder for OCR functionality
            # In a real implementation, you would use libraries like pytesseract
            
            self.logger.info(f"🔍 OCR requested for: {image_path}")
            
            # Simulate OCR processing
            await asyncio.sleep(1)
            
            # Return placeholder text
            return "OCR functionality not implemented. Install pytesseract for text extraction."
            
        except Exception as e:
            self.logger.error(f"❌ OCR error: {e}")
            return None
    
    async def convert_audio_format(self, audio_path: str, target_format: str = "wav") -> Optional[str]:
        """Convert audio to different format"""
        if not self.available_tools["ffmpeg"]:
            self.logger.warning("⚠️ FFmpeg not available for audio conversion")
            return None
        
        try:
            audio_path = Path(audio_path)
            if not audio_path.exists():
                self.logger.error(f"❌ Audio file not found: {audio_path}")
                return None
            
            # Create output path
            output_path = self.processed_dir / f"converted_{int(time.time())}.{target_format}"
            
            # Convert using FFmpeg
            cmd = [
                "ffmpeg",
                "-i", str(audio_path),
                "-y",  # Overwrite output file
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and output_path.exists():
                self.logger.info(f"🎵 Audio converted: {audio_path.name} -> {target_format}")
                return str(output_path)
            else:
                self.logger.error(f"❌ Audio conversion failed: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Audio conversion error: {e}")
            return None
    
    def get_content_item(self, content_id: str) -> Optional[MultimodalContent]:
        """Get content item by ID"""
        return self.content_items.get(content_id)
    
    def get_content_by_modality(self, modality: ModalityType) -> List[MultimodalContent]:
        """Get all content items of specified modality"""
        return [item for item in self.content_items.values() if item.modality == modality]
    
    def get_multimodal_stats(self) -> Dict[str, Any]:
        """Get multimodal system statistics"""
        stats = {
            "total_items": len(self.content_items),
            "by_modality": {},
            "by_status": {},
            "available_tools": self.available_tools,
            "config": self.config
        }
        
        # Count by modality
        for modality in ModalityType:
            count = len([item for item in self.content_items.values() if item.modality == modality])
            stats["by_modality"][modality.value] = count
        
        # Count by status
        for status in ProcessingStatus:
            count = len([item for item in self.content_items.values() if item.status == status])
            stats["by_status"][status.value] = count
        
        return stats
    
    def cleanup_old_content(self, days: int = 7):
        """Cleanup old multimodal content"""
        try:
            cutoff_time = time.time() - (days * 24 * 3600)
            
            removed_count = 0
            for content_id, item in list(self.content_items.items()):
                if item.timestamp < cutoff_time:
                    # Remove files
                    try:
                        if isinstance(item.content, str) and Path(item.content).exists():
                            Path(item.content).unlink()
                        if item.processed_content and Path(item.processed_content).exists():
                            Path(item.processed_content).unlink()
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to remove file: {e}")
                    
                    # Remove from memory
                    del self.content_items[content_id]
                    removed_count += 1
            
            self.logger.info(f"🗑️ Cleaned up {removed_count} old content items")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup error: {e}")

# Global multimodal system instance
multimodal_system = MultimodalSystem()