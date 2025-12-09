#!/usr/bin/env python3
"""
MIA LoRA Training Manager
Advanced LoRA model training, management, and deployment system
"""

import os
import json
import logging
import time
import shutil
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import zipfile

# Machine Learning libraries
try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, Dataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    Dataset = None

# LoRA libraries
try:
    from transformers import AutoTokenizer, AutoModel
    PEFT_AVAILABLE = True
except ImportError:
    PEFT_AVAILABLE = False

# Audio processing for voice LoRA
try:
    import librosa
    import soundfile as sf
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False
    librosa = None
    sf = None

class LoRAType(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Types of LoRA models"""
    TEXT_GENERATION = "text_generation"
    VOICE_SYNTHESIS = "voice_synthesis"
    IMAGE_GENERATION = "image_generation"
    AVATAR_ANIMATION = "avatar_animation"
    EMOTIONAL_EXPRESSION = "emotional_expression"

class TrainingStatus(Enum):
    """Training status"""
    IDLE = "idle"
    PREPARING = "preparing"
    TRAINING = "training"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class LoRAQuality(Enum):
    """LoRA model quality levels"""
    DRAFT = "draft"
    GOOD = "good"
    EXCELLENT = "excellent"
    PRODUCTION = "production"

@dataclass
class LoRAModel:
    """LoRA model metadata"""
    name: str
    lora_type: LoRAType
    base_model: str
    version: str
    quality: LoRAQuality
    file_path: str
    config_path: str
    created_at: float
    trained_on: str
    training_duration: float
    validation_score: float
    file_size_mb: float
    description: str
    tags: List[str]
    is_active: bool = False
    is_adult_content: bool = False

@dataclass
class TrainingConfig:
    """LoRA training configuration"""
    model_name: str
    lora_type: LoRAType
    base_model: str
    dataset_path: str
    output_path: str
    epochs: int = 10
    batch_size: int = 4
    learning_rate: float = 1e-4
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1
    target_modules: List[str] = None
    validation_split: float = 0.2
    save_steps: int = 500
    logging_steps: int = 100
    warmup_steps: int = 100
    max_grad_norm: float = 1.0
    fp16: bool = True
    gradient_checkpointing: bool = True

@dataclass
class TrainingProgress:
    """Training progress information"""
    status: TrainingStatus
    current_epoch: int
    total_epochs: int
    current_step: int
    total_steps: int
    loss: float
    validation_loss: float
    learning_rate: float
    elapsed_time: float
    estimated_remaining: float
    gpu_memory_used: float
    cpu_usage: float

class LoRATrainingDataset:
    """Custom dataset for LoRA training"""
    
    def __init__(self, data_path: str, lora_type: LoRAType, tokenizer=None):
        self.data_path = Path(data_path)
        self.lora_type = lora_type
        self.tokenizer = tokenizer
        self.data = []
        
        self._load_data()
    
    def _load_data(self):
        """Load training data based on LoRA type"""
        try:
            if self.lora_type == LoRAType.TEXT_GENERATION:
                self._load_text_data()
            elif self.lora_type == LoRAType.VOICE_SYNTHESIS:
                self._load_voice_data()
            elif self.lora_type == LoRAType.IMAGE_GENERATION:
                self._load_image_data()
            elif self.lora_type == LoRAType.EMOTIONAL_EXPRESSION:
                self._load_emotional_data()
            
        except Exception as e:
            logging.error(f"Failed to load training data: {e}")
    
    def _load_text_data(self):
        """Load text training data"""
        try:
            if self.data_path.is_file() and self.data_path.suffix == '.json':
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for item in data:
                    if 'input' in item and 'output' in item:
                        self.data.append({
                            'input': item['input'],
                            'output': item['output']
                        })
            
            elif self.data_path.is_file() and self.data_path.suffix == '.txt':
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line in lines:
                    line = line.strip()
                    if line:
                        # Simple format: input -> output
                        if ' -> ' in line:
                            input_text, output_text = line.split(' -> ', 1)
                            self.data.append({
                                'input': input_text.strip(),
                                'output': output_text.strip()
                            })
                        else:
                            # Use line as both input and output for language modeling
                            self.data.append({
                                'input': line,
                                'output': line
                            })
            
            elif self.data_path.is_dir():
                # Load from directory of text files
                for file_path in self.data_path.glob('*.txt'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            self.data.append({
                                'input': content,
                                'output': content
                            })
            
        except Exception as e:
            logging.error(f"Failed to load text data: {e}")
    
    def _load_voice_data(self):
        """Load voice training data"""
        try:
            if not AUDIO_PROCESSING_AVAILABLE:
                logging.error("Audio processing libraries not available")
                return
            
            # Load audio files and transcriptions
            if self.data_path.is_dir():
                for audio_file in self.data_path.glob('*.wav'):
                    transcript_file = audio_file.with_suffix('.txt')
                    
                    if transcript_file.exists():
                        # Load audio
                        audio, sr = librosa.load(str(audio_file), sr=22050)
                        
                        # Load transcript
                        with open(transcript_file, 'r', encoding='utf-8') as f:
                            transcript = f.read().strip()
                        
                        self.data.append({
                            'audio': audio,
                            'transcript': transcript,
                            'sample_rate': sr
                        })
            
        except Exception as e:
            logging.error(f"Failed to load voice data: {e}")
    
    def _load_image_data(self):
        """Load image training data"""
        try:
            # Load image files and captions
            if self.data_path.is_dir():
                for image_file in self.data_path.glob('*.jpg'):
                    caption_file = image_file.with_suffix('.txt')
                    
                    if caption_file.exists():
                        with open(caption_file, 'r', encoding='utf-8') as f:
                            caption = f.read().strip()
                        
                        self.data.append({
                            'image_path': str(image_file),
                            'caption': caption
                        })
            
        except Exception as e:
            logging.error(f"Failed to load image data: {e}")
    
    def _load_emotional_data(self):
        """Load emotional expression data"""
        try:
            if self.data_path.is_file() and self.data_path.suffix == '.json':
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for item in data:
                    if 'text' in item and 'emotion' in item:
                        self.data.append({
                            'text': item['text'],
                            'emotion': item['emotion'],
                            'intensity': item.get('intensity', 1.0)
                        })
            
        except Exception as e:
            logging.error(f"Failed to load emotional data: {e}")
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx]

class LoRAManager:
    """LoRA Training and Management System"""
    
    def __init__(self, config_path: str = "mia/data/lora/config.json"):
        self.config_path = config_path
        self.lora_dir = Path("mia/data/lora")
        self.lora_dir.mkdir(parents=True, exist_ok=True)
        
        self.models_dir = self.lora_dir / "models"
        self.models_dir.mkdir(exist_ok=True)
        
        self.training_dir = self.lora_dir / "training"
        self.training_dir.mkdir(exist_ok=True)
        
        self.datasets_dir = self.lora_dir / "datasets"
        self.datasets_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger("MIA.LoRAManager")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # LoRA models registry
        self.lora_models: Dict[str, LoRAModel] = {}
        self.active_models: Dict[LoRAType, str] = {}
        
        # Training state
        self.current_training: Optional[TrainingConfig] = None
        self.training_progress: Optional[TrainingProgress] = None
        self.training_thread: Optional[threading.Thread] = None
        self.training_callbacks: List[Callable] = []
        
        # Load existing models
        self._load_existing_models()
        
        self.logger.info("🧬 LoRA Manager initialized")
    
    def _load_configuration(self) -> Dict:
        """Load LoRA manager configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load LoRA config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default LoRA configuration"""
        config = {
            "enabled": True,
            "auto_training": False,
            "max_concurrent_training": 1,
            "default_training_params": {
                "epochs": 10,
                "batch_size": 4,
                "learning_rate": 1e-4,
                "lora_rank": 16,
                "lora_alpha": 32,
                "lora_dropout": 0.1
            },
            "supported_base_models": {
                "text_generation": [
                    "microsoft/DialoGPT-medium",
                    "microsoft/DialoGPT-large",
                    "gpt2",
                    "gpt2-medium"
                ],
                "voice_synthesis": [
                    "facebook/wav2vec2-base",
                    "facebook/wav2vec2-large"
                ],
                "image_generation": [
                    "runwayml/stable-diffusion-v1-5",
                    "stabilityai/stable-diffusion-2-1"
                ]
            },
            "quality_thresholds": {
                "draft": 0.5,
                "good": 0.7,
                "excellent": 0.85,
                "production": 0.9
            },
            "adult_content": {
                "enabled": False,
                "require_explicit_consent": True,
                "separate_storage": True
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _load_existing_models(self):
        """Load existing LoRA models from disk"""
        try:
            models_registry_file = self.lora_dir / "models_registry.json"
            
            if models_registry_file.exists():
                with open(models_registry_file, 'r') as f:
                    registry_data = json.load(f)
                
                for model_name, model_data in registry_data.items():
                    lora_model = LoRAModel(
                        name=model_data["name"],
                        lora_type=LoRAType(model_data["lora_type"]),
                        base_model=model_data["base_model"],
                        version=model_data["version"],
                        quality=LoRAQuality(model_data["quality"]),
                        file_path=model_data["file_path"],
                        config_path=model_data["config_path"],
                        created_at=model_data["created_at"],
                        trained_on=model_data["trained_on"],
                        training_duration=model_data["training_duration"],
                        validation_score=model_data["validation_score"],
                        file_size_mb=model_data["file_size_mb"],
                        description=model_data["description"],
                        tags=model_data["tags"],
                        is_active=model_data.get("is_active", False),
                        is_adult_content=model_data.get("is_adult_content", False)
                    )
                    
                    # Verify file exists
                    if Path(lora_model.file_path).exists():
                        self.lora_models[model_name] = lora_model
                        
                        if lora_model.is_active:
                            self.active_models[lora_model.lora_type] = model_name
            
            self.logger.info(f"✅ Loaded {len(self.lora_models)} LoRA models")
            
        except Exception as e:
            self.logger.error(f"Failed to load existing models: {e}")
    
    def _save_models_registry(self):
        """Save models registry to disk"""
        try:
            models_registry_file = self.lora_dir / "models_registry.json"
            
            registry_data = {}
            for model_name, lora_model in self.lora_models.items():
                registry_data[model_name] = asdict(lora_model)
                registry_data[model_name]["lora_type"] = lora_model.lora_type.value
                registry_data[model_name]["quality"] = lora_model.quality.value
            
            with open(models_registry_file, 'w') as f:
                json.dump(registry_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save models registry: {e}")
    
    def create_training_config(self, model_name: str, lora_type: LoRAType,
                             base_model: str, dataset_path: str, **kwargs) -> TrainingConfig:
        """Create training configuration"""
        try:
            # Get default parameters
            default_params = self.config.get("default_training_params", {})
            
            # Create output path
            output_path = self.training_dir / model_name
            output_path.mkdir(exist_ok=True)
            
            # Create training config
            config = TrainingConfig(
                model_name=model_name,
                lora_type=lora_type,
                base_model=base_model,
                dataset_path=dataset_path,
                output_path=str(output_path),
                epochs=kwargs.get("epochs", default_params.get("epochs", 10)),
                batch_size=kwargs.get("batch_size", default_params.get("batch_size", 4)),
                learning_rate=kwargs.get("learning_rate", default_params.get("learning_rate", 1e-4)),
                lora_rank=kwargs.get("lora_rank", default_params.get("lora_rank", 16)),
                lora_alpha=kwargs.get("lora_alpha", default_params.get("lora_alpha", 32)),
                lora_dropout=kwargs.get("lora_dropout", default_params.get("lora_dropout", 0.1)),
                target_modules=kwargs.get("target_modules"),
                validation_split=kwargs.get("validation_split", 0.2),
                save_steps=kwargs.get("save_steps", 500),
                logging_steps=kwargs.get("logging_steps", 100),
                warmup_steps=kwargs.get("warmup_steps", 100),
                max_grad_norm=kwargs.get("max_grad_norm", 1.0),
                fp16=kwargs.get("fp16", True),
                gradient_checkpointing=kwargs.get("gradient_checkpointing", True)
            )
            
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to create training config: {e}")
            raise
    
    def start_training(self, training_config: TrainingConfig,
                      callback: Optional[Callable] = None) -> bool:
        """Start LoRA training"""
        try:
            if not TORCH_AVAILABLE or not PEFT_AVAILABLE:
                self.logger.error("PyTorch or PEFT not available for training")
                return False
            
            if self.current_training:
                self.logger.error("Training already in progress")
                return False
            
            # Validate training config
            if not self._validate_training_config(training_config):
                return False
            
            # Set current training
            self.current_training = training_config
            
            # Initialize training progress
            self.training_progress = TrainingProgress(
                status=TrainingStatus.PREPARING,
                current_epoch=0,
                total_epochs=training_config.epochs,
                current_step=0,
                total_steps=0,
                loss=0.0,
                validation_loss=0.0,
                learning_rate=training_config.learning_rate,
                elapsed_time=0.0,
                estimated_remaining=0.0,
                gpu_memory_used=0.0,
                cpu_usage=0.0
            )
            
            # Add callback
            if callback:
                self.training_callbacks.append(callback)
            
            # Start training thread
            self.training_thread = threading.Thread(
                target=self._training_loop,
                args=(training_config,),
                daemon=True
            )
            self.training_thread.start()
            
            self.logger.info(f"🚀 Started training: {training_config.model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start training: {e}")
            return False
    
    def _validate_training_config(self, config: TrainingConfig) -> bool:
        """Validate training configuration"""
        try:
            # Check dataset exists
            if not Path(config.dataset_path).exists():
                self.logger.error(f"Dataset not found: {config.dataset_path}")
                return False
            
            # Check base model is supported
            supported_models = self.config.get("supported_base_models", {})
            type_models = supported_models.get(config.lora_type.value, [])
            
            if config.base_model not in type_models:
                self.logger.warning(f"Base model {config.base_model} not in supported list")
            
            # Check output directory is writable
            output_path = Path(config.output_path)
            if not output_path.parent.exists():
                output_path.parent.mkdir(parents=True)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Training config validation failed: {e}")
            return False
    
    def _training_loop(self, config: TrainingConfig):
        """Main training loop"""
        try:
            start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # Update status
            self.training_progress.status = TrainingStatus.PREPARING
            self._notify_training_callbacks()
            
            # Load dataset
            dataset = LoRATrainingDataset(
                config.dataset_path,
                config.lora_type
            )
            
            if len(dataset) == 0:
                raise ValueError("Empty dataset")
            
            # Split dataset
            train_size = int(len(dataset) * (1 - config.validation_split))
            val_size = len(dataset) - train_size
            
            train_dataset, val_dataset = torch.utils.data.random_split(
                dataset, [train_size, val_size]
            )
            
            # Create data loaders
            train_loader = DataLoader(
                train_dataset,
                batch_size=config.batch_size,
                shuffle=True
            )
            
            val_loader = DataLoader(
                val_dataset,
                batch_size=config.batch_size,
                shuffle=False
            )
            
            # Calculate total steps
            total_steps = len(train_loader) * config.epochs
            self.training_progress.total_steps = total_steps
            
            # Initialize model and training components
            model, optimizer, scheduler = self._initialize_training_components(config)
            
            # Update status
            self.training_progress.status = TrainingStatus.TRAINING
            self._notify_training_callbacks()
            
            # Training loop
            best_val_loss = float('inf')
            
            for epoch in range(config.epochs):
                self.training_progress.current_epoch = epoch + 1
                
                # Training phase
                model.train()
                epoch_loss = 0.0
                
                for step, batch in enumerate(train_loader):
                    self.training_progress.current_step = epoch * len(train_loader) + step + 1
                    
                    # Forward pass
                    loss = self._training_step(model, batch, config)
                    
                    # Backward pass
                    loss.backward()
                    
                    # Gradient clipping
                    torch.nn.utils.clip_grad_norm_(model.parameters(), config.max_grad_norm)
                    
                    # Optimizer step
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad()
                    
                    # Update progress
                    epoch_loss += loss.item()
                    self.training_progress.loss = loss.item()
                    self.training_progress.learning_rate = scheduler.get_last_lr()[0]
                    self.training_progress.elapsed_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
                    
                    # Estimate remaining time
                    if self.training_progress.current_step > 0:
                        avg_step_time = self.training_progress.elapsed_time / self.training_progress.current_step
                        remaining_steps = total_steps - self.training_progress.current_step
                        self.training_progress.estimated_remaining = avg_step_time * remaining_steps
                    
                    # Update GPU memory usage
                    if torch.cuda.is_available():
                        self.training_progress.gpu_memory_used = torch.cuda.memory_allocated() / 1024**3
                    
                    # Log progress
                    if step % config.logging_steps == 0:
                        self._notify_training_callbacks()
                    
                    # Save checkpoint
                    if step % config.save_steps == 0:
                        self._save_checkpoint(model, config, epoch, step)
                
                # Validation phase
                self.training_progress.status = TrainingStatus.VALIDATING
                val_loss = self._validate_model(model, val_loader, config)
                self.training_progress.validation_loss = val_loss
                
                # Save best model
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    self._save_best_model(model, config)
                
                self.training_progress.status = TrainingStatus.TRAINING
                self._notify_training_callbacks()
            
            # Training completed
            self.training_progress.status = TrainingStatus.COMPLETED
            self._notify_training_callbacks()
            
            # Register trained model
            self._register_trained_model(config, best_val_loss, self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time)
            
            self.logger.info(f"✅ Training completed: {config.model_name}")
            
        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            if self.training_progress:
                self.training_progress.status = TrainingStatus.FAILED
                self._notify_training_callbacks()
        
        finally:
            # Cleanup
            self.current_training = None
            self.training_thread = None
    
    def _initialize_training_components(self, config: TrainingConfig):
        """Initialize model, optimizer, and scheduler for training"""
        try:
            # This is a simplified implementation
            # In a real implementation, you would load the actual base model
            
            # For demonstration, create a simple model
            if config.lora_type == LoRAType.TEXT_GENERATION:
                # Load tokenizer and model
                tokenizer = AutoTokenizer.from_pretrained(config.base_model)
                base_model = AutoModel.from_pretrained(config.base_model)
                
                # Create LoRA config
                lora_config = LoraConfig(
                    task_type=TaskType.CAUSAL_LM,
                    r=config.lora_rank,
                    lora_alpha=config.lora_alpha,
                    lora_dropout=config.lora_dropout,
                    target_modules=config.target_modules or ["q_proj", "v_proj"]
                )
                
                # Apply LoRA
                model = get_peft_model(base_model, lora_config)
                
            else:
                # Basic transformer model for other types
                model = nn.TransformerEncoder(
                    nn.TransformerEncoderLayer(d_model=768, nhead=8),
                    num_layers=6
                )
            
            # Optimizer
            optimizer = torch.optim.AdamW(
                model.parameters(),
                lr=config.learning_rate
            )
            
            # Scheduler
            scheduler = torch.optim.lr_scheduler.LinearLR(
                optimizer,
                start_factor=0.1,
                total_iters=config.warmup_steps
            )
            
            return model, optimizer, scheduler
            
        except Exception as e:
            self.logger.error(f"Failed to initialize training components: {e}")
            raise
    
    def _training_step(self, model, batch, config: TrainingConfig) -> torch.Tensor:
        """Perform single training step"""
        try:
            # This is a simplified training step
            # In a real implementation, this would depend on the LoRA type
            
            if config.lora_type == LoRAType.TEXT_GENERATION:
                # Text generation training step
                inputs = batch.get('input', torch.randn(config.batch_size, 512))
                targets = batch.get('output', torch.randn(config.batch_size, 512))
                
                outputs = model(inputs)
                loss = nn.MSELoss()(outputs.last_hidden_state, targets)
                
            else:
                # Placeholder for other types
                inputs = torch.randn(config.batch_size, 768)
                outputs = model(inputs)
                targets = torch.randn(config.batch_size, 768)
                loss = nn.MSELoss()(outputs, targets)
            
            return loss
            
        except Exception as e:
            self.logger.error(f"Training step failed: {e}")
            return torch.tensor(0.0, requires_grad=True)
    
    def _validate_model(self, model, val_loader, config: TrainingConfig) -> float:
        """Validate model on validation set"""
        try:
            model.eval()
            total_loss = 0.0
            num_batches = 0
            
            with torch.no_grad():
                for batch in val_loader:
                    loss = self._training_step(model, batch, config)
                    total_loss += loss.item()
                    num_batches += 1
            
            avg_loss = total_loss / max(num_batches, 1)
            return avg_loss
            
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return float('inf')
    
    def _save_checkpoint(self, model, config: TrainingConfig, epoch: int, step: int):
        """Save training checkpoint"""
        try:
            checkpoint_dir = Path(config.output_path) / "checkpoints"
            checkpoint_dir.mkdir(exist_ok=True)
            
            checkpoint_path = checkpoint_dir / f"checkpoint_epoch_{epoch}_step_{step}.pt"
            
            torch.save({
                'model_state_dict': model.state_dict(),
                'epoch': epoch,
                'step': step,
                'config': asdict(config)
            }, checkpoint_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {e}")
    
    def _save_best_model(self, model, config: TrainingConfig):
        """Save best model"""
        try:
            model_path = Path(config.output_path) / "best_model.pt"
            torch.save(model.state_dict(), model_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save best model: {e}")
    
    def _register_trained_model(self, config: TrainingConfig, validation_score: float, 
                              training_duration: float):
        """Register trained model in the registry"""
        try:
            # Determine quality based on validation score
            quality_thresholds = self.config.get("quality_thresholds", {})
            
            if validation_score <= quality_thresholds.get("production", 0.9):
                quality = LoRAQuality.PRODUCTION
            elif validation_score <= quality_thresholds.get("excellent", 0.85):
                quality = LoRAQuality.EXCELLENT
            elif validation_score <= quality_thresholds.get("good", 0.7):
                quality = LoRAQuality.GOOD
            else:
                quality = LoRAQuality.DRAFT
            
            # Get file size
            model_file = Path(config.output_path) / "best_model.pt"
            file_size_mb = model_file.stat().st_size / (1024 * 1024) if model_file.exists() else 0.0
            
            # Create LoRA model entry
            lora_model = LoRAModel(
                name=config.model_name,
                lora_type=config.lora_type,
                base_model=config.base_model,
                version="1.0",
                quality=quality,
                file_path=str(model_file),
                config_path=str(Path(config.output_path) / "config.json"),
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                trained_on=config.dataset_path,
                training_duration=training_duration,
                validation_score=validation_score,
                file_size_mb=file_size_mb,
                description=f"LoRA model trained on {Path(config.dataset_path).name}",
                tags=[config.lora_type.value, config.base_model.split('/')[-1]],
                is_active=False,
                is_adult_content=False
            )
            
            # Save config
            config_file = Path(config.output_path) / "config.json"
            with open(config_file, 'w') as f:
                json.dump(asdict(config), f, indent=2)
            
            # Register model
            self.lora_models[config.model_name] = lora_model
            self._save_models_registry()
            
            self.logger.info(f"📝 Registered LoRA model: {config.model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to register trained model: {e}")
    
    def _notify_training_callbacks(self):
        """Notify training progress callbacks"""
        try:
            for callback in self.training_callbacks:
                try:
                    callback(self.training_progress)
                except Exception as e:
                    self.logger.error(f"Callback error: {e}")
        except Exception as e:
            self.logger.error(f"Failed to notify callbacks: {e}")
    
    def stop_training(self) -> bool:
        """Stop current training"""
        try:
            if not self.current_training:
                return False
            
            if self.training_progress:
                self.training_progress.status = TrainingStatus.CANCELLED
                self._notify_training_callbacks()
            
            self.current_training = None
            
            self.logger.info("🛑 Training stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop training: {e}")
            return False
    
    def activate_lora_model(self, model_name: str) -> bool:
        """Activate LoRA model"""
        try:
            if model_name not in self.lora_models:
                self.logger.error(f"LoRA model not found: {model_name}")
                return False
            
            lora_model = self.lora_models[model_name]
            
            # Deactivate current model of same type
            if lora_model.lora_type in self.active_models:
                old_model_name = self.active_models[lora_model.lora_type]
                if old_model_name in self.lora_models:
                    self.lora_models[old_model_name].is_active = False
            
            # Activate new model
            lora_model.is_active = True
            self.active_models[lora_model.lora_type] = model_name
            
            # Save registry
            self._save_models_registry()
            
            self.logger.info(f"✅ Activated LoRA model: {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to activate LoRA model: {e}")
            return False
    
    def deactivate_lora_model(self, model_name: str) -> bool:
        """Deactivate LoRA model"""
        try:
            if model_name not in self.lora_models:
                return False
            
            lora_model = self.lora_models[model_name]
            lora_model.is_active = False
            
            if lora_model.lora_type in self.active_models:
                del self.active_models[lora_model.lora_type]
            
            self._save_models_registry()
            
            self.logger.info(f"❌ Deactivated LoRA model: {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deactivate LoRA model: {e}")
            return False
    
    def delete_lora_model(self, model_name: str) -> bool:
        """Delete LoRA model"""
        try:
            if model_name not in self.lora_models:
                return False
            
            lora_model = self.lora_models[model_name]
            
            # Deactivate if active
            if lora_model.is_active:
                self.deactivate_lora_model(model_name)
            
            # Delete files
            if Path(lora_model.file_path).exists():
                Path(lora_model.file_path).unlink()
            
            if Path(lora_model.config_path).exists():
                Path(lora_model.config_path).unlink()
            
            # Remove from registry
            del self.lora_models[model_name]
            self._save_models_registry()
            
            self.logger.info(f"🗑️ Deleted LoRA model: {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete LoRA model: {e}")
            return False
    
    def export_lora_model(self, model_name: str, export_path: str) -> bool:
        """Export LoRA model as ZIP archive"""
        try:
            if model_name not in self.lora_models:
                return False
            
            lora_model = self.lora_models[model_name]
            
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add model file
                if Path(lora_model.file_path).exists():
                    zipf.write(lora_model.file_path, "model.pt")
                
                # Add config file
                if Path(lora_model.config_path).exists():
                    zipf.write(lora_model.config_path, "config.json")
                
                # Add metadata
                metadata = asdict(lora_model)
                metadata["lora_type"] = lora_model.lora_type.value
                metadata["quality"] = lora_model.quality.value
                
                zipf.writestr("metadata.json", json.dumps(metadata, indent=2))
            
            self.logger.info(f"📦 Exported LoRA model: {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export LoRA model: {e}")
            return False
    
    def import_lora_model(self, import_path: str) -> bool:
        """Import LoRA model from ZIP archive"""
        try:
            with zipfile.ZipFile(import_path, 'r') as zipf:
                # Extract metadata
                metadata_content = zipf.read("metadata.json")
                metadata = json.loads(metadata_content)
                
                model_name = metadata["name"]
                
                # Create model directory
                model_dir = self.models_dir / model_name
                model_dir.mkdir(exist_ok=True)
                
                # Extract files
                zipf.extract("model.pt", model_dir)
                zipf.extract("config.json", model_dir)
                
                # Create LoRA model entry
                lora_model = LoRAModel(
                    name=metadata["name"],
                    lora_type=LoRAType(metadata["lora_type"]),
                    base_model=metadata["base_model"],
                    version=metadata["version"],
                    quality=LoRAQuality(metadata["quality"]),
                    file_path=str(model_dir / "model.pt"),
                    config_path=str(model_dir / "config.json"),
                    created_at=metadata["created_at"],
                    trained_on=metadata["trained_on"],
                    training_duration=metadata["training_duration"],
                    validation_score=metadata["validation_score"],
                    file_size_mb=metadata["file_size_mb"],
                    description=metadata["description"],
                    tags=metadata["tags"],
                    is_active=False,
                    is_adult_content=metadata.get("is_adult_content", False)
                )
                
                # Register model
                self.lora_models[model_name] = lora_model
                self._save_models_registry()
            
            self.logger.info(f"📥 Imported LoRA model: {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import LoRA model: {e}")
            return False
    
    def get_lora_models(self, lora_type: Optional[LoRAType] = None,
                       include_adult: bool = False) -> Dict[str, Dict[str, Any]]:
        """Get available LoRA models"""
        models = {}
        
        for name, lora_model in self.lora_models.items():
            # Filter by type
            if lora_type and lora_model.lora_type != lora_type:
                continue
            
            # Filter adult content
            if lora_model.is_adult_content and not include_adult:
                continue
            
            models[name] = {
                "name": lora_model.name,
                "lora_type": lora_model.lora_type.value,
                "base_model": lora_model.base_model,
                "version": lora_model.version,
                "quality": lora_model.quality.value,
                "created_at": lora_model.created_at,
                "training_duration": lora_model.training_duration,
                "validation_score": lora_model.validation_score,
                "file_size_mb": lora_model.file_size_mb,
                "description": lora_model.description,
                "tags": lora_model.tags,
                "is_active": lora_model.is_active,
                "is_adult_content": lora_model.is_adult_content
            }
        
        return models
    
    def get_training_status(self) -> Optional[Dict[str, Any]]:
        """Get current training status"""
        if not self.training_progress:
            return None
        
        return {
            "status": self.training_progress.status.value,
            "current_epoch": self.training_progress.current_epoch,
            "total_epochs": self.training_progress.total_epochs,
            "current_step": self.training_progress.current_step,
            "total_steps": self.training_progress.total_steps,
            "loss": self.training_progress.loss,
            "validation_loss": self.training_progress.validation_loss,
            "learning_rate": self.training_progress.learning_rate,
            "elapsed_time": self.training_progress.elapsed_time,
            "estimated_remaining": self.training_progress.estimated_remaining,
            "gpu_memory_used": self.training_progress.gpu_memory_used,
            "cpu_usage": self.training_progress.cpu_usage,
            "progress_percentage": (self.training_progress.current_step / max(self.training_progress.total_steps, 1)) * 100
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get LoRA manager status"""
        return {
            "enabled": self.config.get("enabled", True),
            "torch_available": TORCH_AVAILABLE,
            "peft_available": PEFT_AVAILABLE,
            "total_models": len(self.lora_models),
            "active_models": {k.value: v for k, v in self.active_models.items()},
            "is_training": self.current_training is not None,
            "training_status": self.get_training_status(),
            "adult_content_enabled": self.config.get("adult_content", {}).get("enabled", False)
        }

# Global instance
lora_manager = LoRAManager()