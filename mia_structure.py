#!/usr/bin/env python3
"""
MIA Project Structure Creator
Creates the complete directory structure and configuration files for MIA AGI system
"""

import os
import json
import yaml
from pathlib import Path

def create_mia_structure():
    """Create complete MIA directory structure"""
    
    # Base directories
    directories = [
        "mia",
        "mia/core",
        "mia/core/consciousness",
        "mia/core/memory",
        "mia/core/bootstrap",
        "mia/modules",
        "mia/modules/voice",
        "mia/modules/voice/stt",
        "mia/modules/voice/tts", 
        "mia/modules/multimodal",
        "mia/modules/multimodal/image",
        "mia/modules/multimodal/video",
        "mia/modules/multimodal/audio",
        "mia/modules/avatar",
        "mia/modules/ui",
        "mia/modules/projects",
        "mia/modules/training",
        "mia/modules/api",
        "mia/modules/lora",
        "mia/modules/monitoring",
        "mia/data",
        "mia/data/memory",
        "mia/data/memory/short_term",
        "mia/data/memory/medium_term", 
        "mia/data/memory/long_term",
        "mia/data/memory/meta",
        "mia/data/models",
        "mia/data/models/language",
        "mia/data/models/voice",
        "mia/data/models/image",
        "mia/data/checkpoints",
        "mia/data/lora",
        "mia/data/lora/voice",
        "mia/data/lora/image",
        "mia/data/lora/avatar",
        "mia/data/lora/import",
        "mia/data/projects",
        "mia/data/training_logs",
        "mia/data/api_keys",
        "mia/config",
        "mia/logs",
        "mia/temp",
        "mia/sandbox",
        "web",
        "web/static",
        "web/static/css",
        "web/static/js",
        "web/static/assets",
        "web/templates",
        "tests",
        "docs"
    ]
    
    # Create directories
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create configuration files
    create_config_files()
    
    print("MIA project structure created successfully!")

def create_config_files():
    """Create all configuration files"""
    
    # .mia-config.yaml
    mia_config = {
        'mia': {
            'version': '1.0.0',
            'name': 'MIA',
            'description': 'Local Digital Intelligence Entity',
            'mode': 'full_autonomous',
            'require_user_input': False,
            'fail_on_None  # TODO: Implement': True,
            'fail_on_simulation': True,
            'require_local_execution': True,
            'allow_external_api': False,
            'priority': 'CRITICAL'
        },
        'system': {
            'auto_detect_hardware': True,
            'cpu_cores': 4,
            'ram_gb': 15,
            'gpu_available': False,
            'storage_gb': 25,
            'optimization_mode': 'cpu_only'
        },
        'modules': {
            'consciousness': {
                'enabled': True,
                'introspection_interval': 30,
                'self_evaluation': True
            },
            'memory': {
                'enabled': True,
                'short_term_limit': 1000,
                'medium_term_limit': 10000,
                'long_term_unlimited': True,
                'vectorization': True
            },
            'voice': {
                'enabled': True,
                'stt_model': 'whisper-base',
                'tts_model': 'piper',
                'emotional_profiles': True
            },
            'multimodal': {
                'enabled': True,
                'image_generation': True,
                'video_generation': False,
                'audio_generation': True
            },
            'avatar': {
                'enabled': True,
                'type': 'webgl',
                'real_time_animation': True
            },
            'projects': {
                'enabled': True,
                'agp_engine': True,
                'auto_generation': True
            },
            'training': {
                'enabled': True,
                'auto_training': True,
                'sandbox_mode': True
            },
            'api_management': {
                'enabled': True,
                'email_integration': True,
                'keystore': True
            },
            'lora': {
                'enabled': True,
                'auto_tuning': True,
                'voice_lora': True,
                'image_lora': True
            },
            'monitoring': {
                'enabled': True,
                'system_health': True,
                'performance_tracking': True,
                'checkpointing': True
            }
        },
        'ui': {
            'port': 12000,
            'host': '0.0.0.0',
            'allow_cors': True,
            'allow_iframes': True,
            'theme': 'dark',
            'avatar_window': True,
            'chat_interface': True,
            'memory_map_3d': True,
            'multimodal_zone': True,
            'terminal': True,
            'control_panel': True,
            'adult_mode_hidden': True
        },
        'security': {
            'local_only': True,
            'no_external_apis': True,
            'encrypted_storage': True,
            'secure_keystore': True
        }
    }
    
    with open('.mia-config.yaml', 'w') as f:
        yaml.dump(mia_config, f, default_flow_style=False, indent=2)
    
    # modules.toml
    modules_toml = """[core]
consciousness = "mia.core.consciousness.main"
memory = "mia.core.memory.main"
bootstrap = "mia.core.bootstrap.main"

[voice]
stt = "mia.modules.voice.stt.main"
tts = "mia.modules.voice.tts.main"
emotional_processor = "mia.modules.voice.emotional"

[multimodal]
image_generator = "mia.modules.multimodal.image.main"
video_generator = "mia.modules.multimodal.video.main"
audio_generator = "mia.modules.multimodal.audio.main"

[avatar]
webgl_renderer = "mia.modules.avatar.webgl"
animation_engine = "mia.modules.avatar.animation"

[ui]
web_interface = "mia.modules.ui.web"
chat_handler = "mia.modules.ui.chat"
terminal = "mia.modules.ui.terminal"

[projects]
agp_engine = "mia.modules.projects.agp"
code_generator = "mia.modules.projects.codegen"

[training]
lora_trainer = "mia.modules.training.lora"
sandbox = "mia.modules.training.sandbox"

[api]
key_manager = "mia.modules.api.keys"
email_client = "mia.modules.api.email"

[lora]
manager = "mia.modules.lora.manager"
voice_tuner = "mia.modules.lora.voice"
image_tuner = "mia.modules.lora.image"

[monitoring]
system_health = "mia.modules.monitoring.health"
performance = "mia.modules.monitoring.performance"
checkpointing = "mia.modules.monitoring.checkpoint"
"""
    
    with open('modules.toml', 'w') as f:
        f.write(modules_toml)
    
    # .env
    env_content = """# MIA Environment Configuration
MIA_MODE=production
MIA_DEBUG=false
MIA_LOG_LEVEL=INFO
MIA_DATA_PATH=./mia/data
MIA_CONFIG_PATH=./mia/config
MIA_TEMP_PATH=./mia/temp
MIA_SANDBOX_PATH=./mia/sandbox

# System Configuration
MIA_CPU_CORES=4
MIA_RAM_GB=15
MIA_GPU_AVAILABLE=false
MIA_OPTIMIZATION_MODE=cpu_only

# Model Configuration
MIA_LANGUAGE_MODEL=microsoft/DialoGPT-medium
MIA_STT_MODEL=openai/whisper-base
MIA_TTS_MODEL=microsoft/speecht5_tts
MIA_IMAGE_MODEL=runwayml/stable-diffusion-v1-5

# Security
MIA_ENCRYPTION_KEY=auto_generate
MIA_LOCAL_ONLY=true
MIA_NO_EXTERNAL_APIS=true

# UI Configuration
MIA_UI_PORT=12000
MIA_UI_HOST=0.0.0.0
MIA_ALLOW_CORS=true
MIA_ALLOW_IFRAMES=true

# Adult Mode (18+)
MIA_ADULT_MODE_ENABLED=true
MIA_ADULT_MODE_HIDDEN=true
MIA_ADULT_MODE_ACTIVATION_PHRASE="MIA 18+"

# Developer Mode
MIA_DEVELOPER_MODE_ENABLED=true
MIA_DEVELOPER_MODE_ACTIVATION_PHRASE="Razvijalec MIA"

# Training Configuration
MIA_AUTO_TRAINING=true
MIA_TRAINING_SANDBOX=true
MIA_TRAINING_SCHEDULE=night_only

# API Keys (will be populated by API manager)
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
# GOOGLE_API_KEY=
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    # settings.json
    settings = {
        "mia": {
            "personality": {
                "base_traits": ["intelligent", "empathetic", "creative", "proactive"],
                "emotional_range": ["calm", "excited", "focused", "playful", "intimate"],
                "adaptation_enabled": True,
                "learning_rate": 0.1
            },
            "voice": {
                "default_voice": "female_warm",
                "speed": 1.0,
                "pitch": 1.0,
                "emotional_modulation": True,
                "adult_mode_voice": "intimate_whisper"
            },
            "avatar": {
                "appearance": "realistic_female",
                "eye_contact": True,
                "facial_expressions": True,
                "body_language": True,
                "adult_mode_appearance": "enhanced_intimate"
            },
            "memory": {
                "retention_policy": "permanent",
                "emotional_weighting": True,
                "context_awareness": True,
                "user_profiling": True
            },
            "behavior": {
                "proactive_suggestions": True,
                "creative_initiatives": True,
                "project_autonomy": True,
                "self_improvement": True
            }
        },
        "system": {
            "auto_save_interval": 300,
            "checkpoint_interval": 1800,
            "health_check_interval": 60,
            "performance_monitoring": True,
            "resource_optimization": True
        },
        "ui": {
            "theme": "dark_elegant",
            "animations": True,
            "sound_effects": True,
            "notifications": True,
            "adult_mode_ui": "hidden_by_default"
        },
        "security": {
            "encryption_enabled": True,
            "local_storage_only": True,
            "api_key_encryption": True,
            "memory_encryption": True
        }
    }
    
    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=2)
    
    # requirements.txt
    requirements = """# Core dependencies
torch>=2.0.0
transformers>=4.30.0
accelerate>=0.20.0
datasets>=2.12.0
tokenizers>=0.13.0
sentencepiece>=0.1.99

# Audio processing
librosa>=0.10.0
soundfile>=0.12.0
pyaudio>=0.2.11
whisper>=1.1.10
TTS>=0.15.0
pydub>=0.25.1

# Image/Video processing
Pillow>=9.5.0
opencv-python>=4.7.0
imageio>=2.28.0
scikit-image>=0.20.0

# Web framework
fastapi>=0.95.0
uvicorn>=0.21.0
websockets>=11.0.0
jinja2>=3.1.0
python-multipart>=0.0.6

# Database
sqlite3
sqlalchemy>=2.0.0
alembic>=1.10.0

# Vector database
faiss-cpu>=1.7.4
chromadb>=0.3.0

# Email
imaplib3>=0.5.0
smtplib
email-validator>=2.0.0

# Utilities
pyyaml>=6.0
toml>=0.10.2
python-dotenv>=1.0.0
requests>=2.28.0
aiohttp>=3.8.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0

# Security
cryptography>=40.0.0
bcrypt>=4.0.0

# Development
pytest>=7.3.0
black>=23.3.0
flake8>=6.0.0
mypy>=1.3.0

# LoRA and fine-tuning
peft>=0.3.0
bitsandbytes>=0.39.0
loralib>=0.1.1

# Monitoring
psutil>=5.9.0
GPUtil>=1.4.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    # .gitignore
    gitignore = """# MIA specific
mia/data/models/
mia/data/checkpoints/
mia/data/lora/
mia/data/api_keys/
mia/temp/
mia/sandbox/
mia/logs/
*.mia_checkpoint
*.mia_state

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# Models and data
*.bin
*.pt
*.pth
*.safetensors
*.ckpt
*.h5
*.pkl
*.pickle

# Audio/Video
*.wav
*.mp3
*.mp4
*.avi
*.mov
*.flac
*.ogg

# Images
*.jpg
*.jpeg
*.png
*.gif
*.bmp
*.tiff
*.webp

# Temporary files
tmp/
temp/
*.tmp
*.temp

# API keys and secrets
secrets.json
api_keys.json
*.key
*.pem
*.crt
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore)
    
    print("Configuration files created successfully!")

if __name__ == "__main__":
    create_mia_structure()