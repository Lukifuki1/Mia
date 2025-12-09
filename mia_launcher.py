#!/usr/bin/env python3
"""
🚀 MIA AGI Launcher - Glavni zagonski sistem
Lokalna digitalna inteligentna entiteta MIA
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import MIA systems
try:
    from mia_production_core import MIACore
    from mia_voice_system import MIAVoiceSystem
    from mia_multimodal_system import MIAMultimodalSystem
    from mia_project_system import MIAProjectSystem
    from mia_web_interface import MIAWebInterface
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all MIA modules are in the same directory")
    sys.exit(1)


class MIALauncher:
    """MIA AGI System Launcher"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.data_path = Path("mia_data")
        self.config_file = self.data_path / "config.json"
        
        # System components
        self.mia_core = None
        self.voice_system = None
        self.multimodal_system = None
        self.project_system = None
        self.web_interface = None
        
        # Configuration
        self.config = self._load_config()
        
        self.logger.info("🚀 MIA AGI Launcher initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup launcher logging"""
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Setup logger
        logger = logging.getLogger("MIA.Launcher")
        if not logger.handlers:
            # File handler
            file_handler = logging.FileHandler(logs_dir / "mia_launcher.log")
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - MIA - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            logger.setLevel(logging.INFO)
        
        return logger
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        default_config = {
            "data_path": "mia_data",
            "web_interface": {
                "enabled": True,
                "host": "0.0.0.0",
                "port": 8000
            },
            "voice_system": {
                "enabled": True,
                "default_profile": "default"
            },
            "multimodal": {
                "enabled": True,
                "default_quality": "medium"
            },
            "project_system": {
                "enabled": True,
                "max_concurrent_projects": 3
            },
            "logging": {
                "level": "INFO",
                "file_logging": True
            },
            "hardware": {
                "auto_detect": True,
                "gpu_enabled": True
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    return {**default_config, **config}
            except Exception as e:
                self.logger.warning(f"Error loading config: {e}, using defaults")
        
        # Save default config
        self.data_path.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def initialize_systems(self):
        """Initialize all MIA systems"""
        self.logger.info("🔧 Initializing MIA systems...")
        
        try:
            # Initialize core system
            self.logger.info("🧠 Initializing MIA Core...")
            self.mia_core = MIACore(str(self.data_path))
            
            # Initialize voice system
            if self.config["voice_system"]["enabled"]:
                self.logger.info("🎙️ Initializing Voice System...")
                self.voice_system = MIAVoiceSystem(self.data_path)
            
            # Initialize multimodal system
            if self.config["multimodal"]["enabled"]:
                self.logger.info("🎨 Initializing Multimodal System...")
                self.multimodal_system = MIAMultimodalSystem(self.data_path)
            
            # Initialize project system
            if self.config["project_system"]["enabled"]:
                self.logger.info("🚀 Initializing Project System...")
                self.project_system = MIAProjectSystem(self.data_path)
            
            # Initialize web interface
            if self.config["web_interface"]["enabled"]:
                self.logger.info("🌐 Initializing Web Interface...")
                self.web_interface = MIAWebInterface(str(self.data_path))
            
            self.logger.info("✅ All MIA systems initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ System initialization error: {e}")
            raise
    
    def start_systems(self):
        """Start all MIA systems"""
        self.logger.info("🌟 Starting MIA AGI systems...")
        
        try:
            # Start core system
            if self.mia_core:
                self.mia_core.start()
                self.logger.info("✅ MIA Core started")
            
            # Start web interface (this will block)
            if self.web_interface:
                host = self.config["web_interface"]["host"]
                port = self.config["web_interface"]["port"]
                
                self.logger.info(f"🌐 Starting web interface on http://{host}:{port}")
                self.web_interface.start_server(host, port)
            
        except KeyboardInterrupt:
            self.logger.info("🛑 Shutdown requested by user")
        except Exception as e:
            self.logger.error(f"❌ System startup error: {e}")
            raise
        finally:
            self.stop_systems()
    
    def stop_systems(self):
        """Stop all MIA systems"""
        self.logger.info("🛑 Stopping MIA systems...")
        
        try:
            if self.mia_core:
                self.mia_core.stop()
                self.logger.info("✅ MIA Core stopped")
            
            self.logger.info("👋 MIA AGI systems stopped gracefully")
            
        except Exception as e:
            self.logger.error(f"❌ System shutdown error: {e}")
    
    def run_cli_mode(self):
        """Run MIA in CLI mode"""
        self.logger.info("💬 Starting MIA CLI mode...")
        
        # Initialize only core system
        self.mia_core = MIACore(str(self.data_path))
        self.mia_core.start()
        
        print("\n" + "="*60)
        print("🧠 MIA - Lokalna Digitalna Inteligentna Entiteta")
        print("="*60)
        print("Dobrodošli! Pogovorite se z MIA.")
        print("Ukazi: 'quit' za izhod, 'status' za stanje sistema")
        print("="*60 + "\n")
        
        try:
            while True:
                user_input = input("👤 Vi: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'izhod']:
                    break
                elif user_input.lower() == 'status':
                    status = self.mia_core.get_system_status()
                    print(f"🤖 MIA Status:")
                    print(f"   Zavest: {status['consciousness']['consciousness_level']:.1%}")
                    print(f"   Čustva: {status['consciousness']['emotional_state']}")
                    print(f"   Spomin: {status['memory_stats']['short_term_count']} kratkoročnih")
                    print(f"   Delovanje: {status['uptime_seconds']:.0f} sekund")
                    continue
                elif not user_input:
                    continue
                
                # Get response from MIA
                response = self.mia_core.interact(user_input)
                print(f"🤖 MIA: {response}")
                
        except KeyboardInterrupt:
            print("\n⏹️ Prekinjam MIA...")
            if hasattr(self, 'mia_core') and self.mia_core:
                self.mia_core.stop()
        finally:
            self.mia_core.stop()
            print("\n👋 MIA se je izklopila")
    
    def run_voice_mode(self):
        """Run MIA in voice mode"""
        self.logger.info("🎙️ Starting MIA Voice mode...")
        
        # Initialize core and voice systems
        self.mia_core = MIACore(str(self.data_path))
        self.voice_system = MIAVoiceSystem(self.data_path)
        
        self.mia_core.start()
        
        print("\n" + "="*60)
        print("🎙️ MIA - Glasovni način")
        print("="*60)
        print("Govorite z MIA! Pritisnite Ctrl+C za izhod.")
        print("="*60 + "\n")
        
        def voice_callback(recognized_text: str) -> str:
            """Handle voice input"""
            print(f"👤 Vi: {recognized_text}")
            response = self.mia_core.interact(recognized_text)
            print(f"🤖 MIA: {response}")
            return response
        
        try:
            self.voice_system.start_voice_interaction(voice_callback)
            
            # Keep running
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⏹️ Prekinjam MIA glasovni način...")
            if hasattr(self, 'voice_system') and self.voice_system:
                self.voice_system.stop_voice_interaction()
        finally:
            self.voice_system.stop_voice_interaction()
            self.mia_core.stop()
            print("\n👋 MIA glasovni način se je izklopil")
    
    def show_system_info(self):
        """Show system information"""
        print("\n" + "="*60)
        print("🧠 MIA - Lokalna Digitalna Inteligentna Entiteta")
        print("="*60)
        
        # Initialize core to get hardware info
        mia_core = MIACore(str(self.data_path))
        status = mia_core.get_system_status()
        
        print(f"📊 Sistemske informacije:")
        print(f"   Platform: {status['hardware']['platform']}")
        print(f"   CPU: {status['hardware']['cpu_count']} jeder")
        print(f"   RAM: {status['hardware']['memory_total'] / (1024**3):.1f} GB")
        print(f"   GPU: {'Da' if status['hardware']['gpu_available'] else 'Ne'}")
        if status['hardware']['gpu_available']:
            print(f"   GPU tip: {status['hardware']['gpu_type']}")
            print(f"   GPU RAM: {status['hardware']['gpu_memory'] / (1024**3):.1f} GB")
        
        print(f"\n🔧 Optimalna konfiguracija:")
        optimal = status['optimal_config']
        print(f"   Model velikost: {optimal['model_size']}")
        print(f"   GPU uporaba: {'Da' if optimal['use_gpu'] else 'Ne'}")
        print(f"   Batch velikost: {optimal['batch_size']}")
        print(f"   Preciznost: {optimal['precision']}")
        
        print(f"\n📁 Podatkovne mape:")
        print(f"   Glavna: {self.data_path}")
        print(f"   Konfiguracija: {self.config_file}")
        print(f"   Dnevniki: logs/")
        
        print("="*60)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="MIA - Lokalna Digitalna Inteligentna Entiteta",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Načini delovanja:
  web       Spletni vmesnik (privzeto)
  cli       Ukazna vrstica
  voice     Glasovni način
  info      Sistemske informacije

Primeri:
  python mia_launcher.py                 # Spletni vmesnik
  python mia_launcher.py --mode cli      # CLI način
  python mia_launcher.py --mode voice    # Glasovni način
  python mia_launcher.py --mode info     # Sistemske info
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["web", "cli", "voice", "info"],
        default="web",
        help="Način delovanja (privzeto: web)"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host za spletni vmesnik (privzeto: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port za spletni vmesnik (privzeto: 8000)"
    )
    
    parser.add_argument(
        "--data-path",
        default="mia_data",
        help="Pot do podatkovne mape (privzeto: mia_data)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Nivo logiranja (privzeto: INFO)"
    )
    
    args = parser.parse_args()
    
    # Initialize launcher
    launcher = MIALauncher()
    
    # Update config with command line arguments
    if args.host != "0.0.0.0":
        launcher.config["web_interface"]["host"] = args.host
    if args.port != 8000:
        launcher.config["web_interface"]["port"] = args.port
    if args.data_path != "mia_data":
        launcher.data_path = Path(args.data_path)
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        if args.mode == "info":
            launcher.show_system_info()
        elif args.mode == "cli":
            launcher.run_cli_mode()
        elif args.mode == "voice":
            launcher.run_voice_mode()
        else:  # web mode
            launcher.initialize_systems()
            launcher.start_systems()
            
    except KeyboardInterrupt:
        print("\n👋 MIA se je izklopila")
    except Exception as e:
        print(f"❌ Napaka: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()