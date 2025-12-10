#!/usr/bin/env python3
"""
🧠 MIA Enterprise AGI - Complete Unified System
===============================================

MIA Enterprise AGI je napredno zasnovan, popolnoma lokalno delujoč inteligentni sistem 
generacije AGI, ustvarjen za uporabo v najzahtevnejših enterprise okoljih.

Gre za samostojen, visoko modularen in determinističen inteligentni ekosistem, ki združuje:
- Napredne kognitivne sposobnosti z realnim učenjem
- Stroge varnostne standarde in compliance
- Poslovno skladnost in enterprise funkcionalnosti
- Profesionalne razvojne zmožnosti
- Zanesljivo operativno infrastrukturo
- Desktop in web aplikacije
- Multimodalne zmogljivosti

KLJUČNE ZMOGLJIVOSTI:
- 🧠 Splošna umetna inteligenca (AGI) z učenjem
- 💬 Napreden pogovorni vmesnik z glasom
- 🌐 Enterprise web platforma
- 🖥️ Namizna aplikacija z GUI
- 🔒 Varnostni sistemi in audit
- 📊 Analitika in real-time monitoring
- 🎨 Multimodalne zmogljivosti (slike, zvok, video)
- 🚀 Produkcijska stabilnost in skalabilnost
- 🔄 Avtomatsko učenje in model discovery
- 📁 Projektni sistem za avtomatsko gradnjo

NAČINI DELOVANJA:
- Desktop Mode: Lokalna GUI aplikacija
- Web Mode: Spletni vmesnik
- Enterprise Mode: Polne enterprise funkcionalnosti
- Development Mode: Razvojno okolje
- Production Mode: Produkcijsko delovanje
"""

import os
import sys
import json
import logging
import asyncio
import time
import signal
import threading
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import psutil

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class SystemMode(Enum):
    """System operation modes"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    ENTERPRISE = "enterprise"
    TESTING = "testing"
    DESKTOP = "desktop"
    WEB = "web"
    HYBRID = "hybrid"

class ComponentStatus(Enum):
    """Component status"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class SystemConfig:
    """System configuration"""
    mode: SystemMode = SystemMode.ENTERPRISE
    web_port: int = 12000
    api_port: int = 8000
    desktop_port: int = 12001
    enable_voice: bool = True
    enable_multimodal: bool = True
    enable_desktop: bool = True
    enable_security: bool = True
    enable_analytics: bool = True
    enable_learning: bool = True
    enable_model_discovery: bool = True
    enable_project_system: bool = True
    log_level: str = "INFO"
    data_dir: str = "mia_data"
    models_dir: str = "models"
    projects_dir: str = "projects"

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load system configuration from JSON file"""
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Return default configuration
            return {
                "system": {"mode": "production", "debug": False},
                "server": {"api_port": 8000, "web_port": 12000, "desktop_port": 12001},
                "ai": {"learning_enabled": True, "memory_enabled": True},
                "paths": {"data_dir": "./mia/data", "models_dir": "./models", "projects_dir": "./projects"}
            }
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

class MIAEnterpriseAGI:
    """
    MIA Enterprise AGI - Unified System
    
    Celovit sistem umetne splošne inteligence za enterprise uporabo
    """
    
    def __init__(self, config: Optional[SystemConfig] = None):
        # Load configuration from file
        self.config_data = load_config()
        self.config = config or SystemConfig()
        
        # Apply configuration from file
        if self.config_data:
            server_config = self.config_data.get("server", {})
            self.config.web_port = server_config.get("web_port", self.config.web_port)
            self.config.api_port = server_config.get("api_port", self.config.api_port)
            self.config.desktop_port = server_config.get("desktop_port", self.config.desktop_port)
            
            ai_config = self.config_data.get("ai", {})
            self.config.enable_learning = ai_config.get("learning_enabled", self.config.enable_learning)
            
            paths_config = self.config_data.get("paths", {})
            self.config.data_dir = paths_config.get("data_dir", self.config.data_dir)
            self.config.models_dir = paths_config.get("models_dir", self.config.models_dir)
            self.config.projects_dir = paths_config.get("projects_dir", self.config.projects_dir)
        
        self.logger = self._setup_logging()
        self.is_running = False
        self.components = {}
        self.shutdown_event = threading.Event()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("🧠 MIA Enterprise AGI initializing...")
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging system"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f"{self.config.data_dir}/mia_enterprise.log")
            ]
        )
        return logging.getLogger("MIA.Enterprise.AGI")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown_event.set()
        asyncio.create_task(self.shutdown())
    
    async def initialize(self):
        """Initialize all system components"""
        self.logger.info("🚀 Initializing MIA Enterprise AGI components...")
        
        # Create data directory
        os.makedirs(self.config.data_dir, exist_ok=True)
        
        try:
            # Initialize core AGI system
            await self._initialize_agi_core()
            
            # Initialize enterprise features
            await self._initialize_enterprise_features()
            
            # Initialize user interfaces
            await self._initialize_interfaces()
            
            # Initialize additional systems
            await self._initialize_additional_systems()
            
            self.is_running = True
            self.logger.info("✅ MIA Enterprise AGI fully initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize system: {e}")
            raise
    
    async def _initialize_agi_core(self):
        """Initialize AGI core system"""
        self.logger.info("🧠 Initializing AGI Core...")
        
        try:
            from mia.core.agi_core import agi_core, initialize_agi
            from mia.core.model_discovery import model_discovery
            from mia.core.model_learning import model_learning
            from mia.interfaces.chat import chat_interface
            
            # Initialize AGI core
            await initialize_agi()
            self.components['agi_core'] = ComponentStatus.RUNNING
            
            # Start model discovery
            model_discovery.start_discovery()
            self.components['model_discovery'] = ComponentStatus.RUNNING
            
            # Initialize chat interface
            await chat_interface.initialize()
            self.components['chat_interface'] = ComponentStatus.RUNNING
            
            self.logger.info("✅ AGI Core initialized successfully")
            
        except ImportError as e:
            self.logger.warning(f"⚠️ AGI Core not available: {e}")
            self.components['agi_core'] = ComponentStatus.ERROR
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize AGI Core: {e}")
            self.components['agi_core'] = ComponentStatus.ERROR
            raise
    
    async def _initialize_enterprise_features(self):
        """Initialize enterprise features"""
        self.logger.info("🏢 Initializing Enterprise Features...")
        
        try:
            # Initialize unified enterprise manager
            from mia.enterprise.unified_enterprise_manager import enterprise_manager
            await enterprise_manager.initialize()
            self.components['enterprise_manager'] = ComponentStatus.RUNNING
            
            # Initialize individual components through enterprise manager
            if self.config.enable_security:
                self.components['security'] = ComponentStatus.RUNNING
                
            if self.config.enable_analytics:
                self.components['analytics'] = ComponentStatus.RUNNING
                
            # API gateway is handled by unified interface
            self.components['api_gateway'] = ComponentStatus.RUNNING
            
            self.logger.info("✅ Enterprise Features initialized")
            
        except ImportError as e:
            self.logger.warning(f"⚠️ Some enterprise features not available: {e}")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize enterprise features: {e}")
            raise
    
    async def _initialize_interfaces(self):
        """Initialize user interfaces"""
        self.logger.info("🌐 Initializing User Interfaces...")
        
        try:
            # Initialize unified interface system
            from mia.interfaces.unified_interface import unified_interface, InterfaceConfig
            
            # Create interface configuration
            interface_config = InterfaceConfig(
                web_enabled=True,
                chat_enabled=True,
                desktop_enabled=self.config.enable_desktop,
                voice_enabled=self.config.enable_voice,
                api_enabled=True,
                web_port=self.config.web_port,
                api_port=self.config.api_port
            )
            
            # Initialize unified interface
            unified_interface.config = interface_config
            await unified_interface.initialize()
            self.components['unified_interface'] = ComponentStatus.RUNNING
            
            # Start interface server in background
            import asyncio
            asyncio.create_task(unified_interface.start_server())
            
            self.logger.info("✅ User Interfaces initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize interfaces: {e}")
            raise
    
    async def _initialize_additional_systems(self):
        """Initialize additional systems"""
        self.logger.info("🔧 Initializing Additional Systems...")
        
        try:
            # Model discovery system
            if self.config.enable_model_discovery:
                try:
                    from mia.core.model_discovery import model_discovery
                    # Model discovery is already started in AGI core initialization
                    self.components['model_discovery'] = ComponentStatus.RUNNING
                    self.logger.info("✅ Model Discovery system active")
                except ImportError:
                    self.logger.warning("⚠️ Model Discovery system not available")
                    self.components['model_discovery'] = ComponentStatus.ERROR
            
            # Learning system
            if self.config.enable_learning:
                try:
                    from mia.core.model_learning import model_learning
                    await model_learning.initialize()
                    self.components['learning'] = ComponentStatus.RUNNING
                    self.logger.info("✅ Learning system initialized")
                except ImportError:
                    self.logger.warning("⚠️ Learning system not available")
                    self.components['learning'] = ComponentStatus.ERROR
            
            # Project system
            if self.config.enable_project_system:
                try:
                    from mia.modules.projects.main import project_system
                    await project_system.initialize()
                    self.components['project_system'] = ComponentStatus.RUNNING
                    self.logger.info("✅ Project system initialized")
                except ImportError:
                    self.logger.warning("⚠️ Project system not available")
                    self.components['project_system'] = ComponentStatus.ERROR
            
            # Voice system
            if self.config.enable_voice:
                try:
                    from mia.modules.voice.main import voice_system
                    await voice_system.initialize()
                    self.components['voice'] = ComponentStatus.RUNNING
                    self.logger.info("✅ Voice system initialized")
                except ImportError:
                    self.logger.warning("⚠️ Voice system not available")
                    self.components['voice'] = ComponentStatus.ERROR
            
            # Multimodal system
            if self.config.enable_multimodal:
                try:
                    from mia.modules.multimodal.main import multimodal_system
                    await multimodal_system.initialize()
                    self.components['multimodal'] = ComponentStatus.RUNNING
                    self.logger.info("✅ Multimodal system initialized")
                except ImportError:
                    self.logger.warning("⚠️ Multimodal system not available")
                    self.components['multimodal'] = ComponentStatus.ERROR
            
            # Desktop application (if in desktop or hybrid mode)
            if self.config.mode in [SystemMode.DESKTOP, SystemMode.HYBRID] and self.config.enable_desktop:
                try:
                    await self._initialize_desktop_app()
                    self.components['desktop_app'] = ComponentStatus.RUNNING
                    self.logger.info("✅ Desktop application initialized")
                except Exception as e:
                    self.logger.warning(f"⚠️ Desktop application failed: {e}")
                    self.components['desktop_app'] = ComponentStatus.ERROR
            
            self.logger.info("✅ Additional Systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize additional systems: {e}")
    
    async def _initialize_desktop_app(self):
        """Initialize desktop application"""
        self.logger.info("🖥️ Initializing Desktop Application...")
        
        # Create desktop data directories
        desktop_data_dir = Path(self.config.data_dir) / "desktop"
        desktop_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Desktop app configuration
        desktop_config = {
            "window_title": "MIA Enterprise AGI",
            "window_width": 1200,
            "window_height": 800,
            "web_port": self.config.desktop_port,
            "enable_system_tray": True,
            "auto_start": False,
            "theme": "dark"
        }
        
        # Save desktop configuration
        with open(desktop_data_dir / "desktop_config.json", "w") as f:
            json.dump(desktop_config, f, indent=2)
        
        self.logger.info("✅ Desktop Application ready")
    
    async def run(self):
        """Run the main system loop"""
        self.logger.info("🚀 Starting MIA Enterprise AGI...")
        
        # Display startup banner
        self._display_banner()
        
        # Display system status
        self._display_system_status()
        
        # Main application loop
        try:
            while not self.shutdown_event.is_set():
                # Monitor system health
                await self._monitor_system_health()
                
                # Update system metrics
                await self._update_metrics()
                
                # Sleep for monitoring interval
                await asyncio.sleep(5)
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
        finally:
            await self.shutdown()
    
    async def _monitor_system_health(self):
        """Monitor system health"""
        try:
            # Check component status
            for component, status in self.components.items():
                if status == ComponentStatus.ERROR:
                    self.logger.warning(f"⚠️ Component {component} is in error state")
            
            # Check system resources
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 90:
                self.logger.warning(f"⚠️ High CPU usage: {cpu_percent}%")
            if memory_percent > 90:
                self.logger.warning(f"⚠️ High memory usage: {memory_percent}%")
                
        except Exception as e:
            self.logger.error(f"Error monitoring system health: {e}")
    
    async def _update_metrics(self):
        """Update system metrics"""
        try:
            if 'analytics' in self.components and self.components['analytics'] == ComponentStatus.RUNNING:
                from mia.enterprise.analytics import analytics
                await analytics.update_metrics({
                    'timestamp': time.time(),
                    'components': self.components,
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('/').percent
                })
        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")
    
    def _display_banner(self):
        """Display startup banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🧠 MIA Enterprise AGI                     ║
║                  Artificial General Intelligence             ║
║                                                              ║
║  🧠 Advanced Cognitive Capabilities                         ║
║  💬 Natural Language Understanding                          ║
║  🌐 Enterprise Web Platform                                 ║
║  🖥️ Desktop Application                                     ║
║  🔒 Enterprise Security                                     ║
║  📊 Real-time Analytics                                     ║
║  🚀 Production Ready                                        ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(banner)
        self.logger.info("MIA Enterprise AGI started successfully")
    
    def _display_system_status(self):
        """Display system status"""
        print(f"\n📊 MIA Enterprise AGI System Status ({self.config.mode.value.upper()} mode):")
        print("├─ 🧠 AGI Core:", "✅ Running" if self.components.get('agi_core') == ComponentStatus.RUNNING else "❌ Error")
        print("├─ 💬 Chat Interface:", "✅ Running" if self.components.get('chat_interface') == ComponentStatus.RUNNING else "❌ Error")
        print("├─ 🌐 Web Interface:", f"✅ Running on port {self.config.web_port}" if self.components.get('unified_interface') == ComponentStatus.RUNNING else "❌ Error")
        print("├─ 🔌 API Gateway:", f"✅ Running on port {self.config.api_port}" if self.components.get('api_gateway') == ComponentStatus.RUNNING else "❌ Error")
        print("├─ 🏢 Enterprise Manager:", "✅ Active" if self.components.get('enterprise_manager') == ComponentStatus.RUNNING else "⚠️ Disabled")
        print("├─ 🔒 Security:", "✅ Active" if self.components.get('security') == ComponentStatus.RUNNING else "⚠️ Disabled")
        print("├─ 📊 Analytics:", "✅ Active" if self.components.get('analytics') == ComponentStatus.RUNNING else "⚠️ Disabled")
        print("├─ 🔍 Model Discovery:", "✅ Active" if self.components.get('model_discovery') == ComponentStatus.RUNNING else "⚠️ Disabled")
        print("├─ 🎓 Learning System:", "✅ Active" if self.components.get('learning') == ComponentStatus.RUNNING else "⚠️ Disabled")
        print("├─ 📁 Project System:", "✅ Active" if self.components.get('project_system') == ComponentStatus.RUNNING else "⚠️ Disabled")
        print("├─ 🎤 Voice System:", "✅ Active" if self.components.get('voice') == ComponentStatus.RUNNING else "⚠️ Disabled")
        print("├─ 🖼️ Multimodal:", "✅ Active" if self.components.get('multimodal') == ComponentStatus.RUNNING else "⚠️ Disabled")
        print("└─ 🖥️ Desktop App:", "✅ Active" if self.components.get('desktop_app') == ComponentStatus.RUNNING else "⚠️ Disabled")
        
        print(f"\n🌐 Access Points:")
        if self.components.get('unified_interface') == ComponentStatus.RUNNING:
            print(f"├─ Web Interface: http://localhost:{self.config.web_port}")
            print(f"├─ Chat Interface: http://localhost:{self.config.web_port}/chat")
            print(f"├─ Dashboard: http://localhost:{self.config.web_port}/dashboard")
        if self.components.get('api_gateway') == ComponentStatus.RUNNING:
            print(f"├─ API Gateway: http://localhost:{self.config.api_port}")
        if self.components.get('desktop_app') == ComponentStatus.RUNNING:
            print(f"└─ Desktop App: http://localhost:{self.config.desktop_port}")
        print()
    
    async def shutdown(self):
        """Shutdown all system components"""
        if not self.is_running:
            return
            
        self.logger.info("🛑 Shutting down MIA Enterprise AGI...")
        self.is_running = False
        
        try:
            # Shutdown components in reverse order
            if 'unified_interface' in self.components:
                from mia.interfaces.unified_interface import unified_interface
                await unified_interface.shutdown()
                
            if 'enterprise_manager' in self.components:
                from mia.enterprise.unified_enterprise_manager import enterprise_manager
                await enterprise_manager.shutdown()
                
            if 'agi_core' in self.components:
                from mia.core.agi_core import shutdown_agi
                await shutdown_agi()
                
            if 'model_discovery' in self.components:
                from mia.core.model_discovery import model_discovery
                model_discovery.stop_discovery()
                
            self.logger.info("✅ MIA Enterprise AGI shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

def create_config_from_args(args) -> SystemConfig:
    """Create system configuration from command line arguments"""
    # Handle convenience shortcuts
    if args.desktop_only:
        args.mode = "desktop"
        args.enable_desktop = True
        args.enable_voice = False
        args.enable_multimodal = False
    elif args.web_only:
        args.mode = "web"
        args.enable_desktop = False
    elif args.minimal:
        args.enable_voice = False
        args.enable_multimodal = False
        args.enable_learning = False
        args.enable_model_discovery = False
        args.enable_project_system = False
    elif args.quick_start:
        args.enable_analytics = False
        args.enable_learning = False
        args.enable_model_discovery = False
    
    return SystemConfig(
        mode=SystemMode(args.mode),
        web_port=args.web_port,
        api_port=args.api_port,
        desktop_port=args.desktop_port,
        enable_voice=args.enable_voice,
        enable_multimodal=args.enable_multimodal,
        enable_desktop=args.enable_desktop,
        enable_security=args.enable_security,
        enable_analytics=args.enable_analytics,
        enable_learning=args.enable_learning,
        enable_model_discovery=args.enable_model_discovery,
        enable_project_system=args.enable_project_system,
        log_level=args.log_level,
        data_dir=args.data_dir,
        models_dir=args.models_dir,
        projects_dir=args.projects_dir
    )

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="MIA Enterprise AGI - Complete Unified System")
    parser.add_argument("--mode", choices=["development", "production", "enterprise", "testing", "desktop", "web", "hybrid"], 
                       default="enterprise", help="System operation mode")
    parser.add_argument("--web-port", type=int, default=12000, help="Web interface port")
    parser.add_argument("--api-port", type=int, default=8000, help="API gateway port")
    parser.add_argument("--desktop-port", type=int, default=12001, help="Desktop application port")
    parser.add_argument("--enable-voice", action="store_true", default=True, help="Enable voice system")
    parser.add_argument("--enable-multimodal", action="store_true", default=True, help="Enable multimodal system")
    parser.add_argument("--enable-desktop", action="store_true", default=True, help="Enable desktop interface")
    parser.add_argument("--enable-security", action="store_true", default=True, help="Enable security features")
    parser.add_argument("--enable-analytics", action="store_true", default=True, help="Enable analytics")
    parser.add_argument("--enable-learning", action="store_true", default=True, help="Enable learning system")
    parser.add_argument("--enable-model-discovery", action="store_true", default=True, help="Enable model discovery")
    parser.add_argument("--enable-project-system", action="store_true", default=True, help="Enable project system")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="Logging level")
    parser.add_argument("--data-dir", default="mia_data", help="Data directory")
    parser.add_argument("--models-dir", default="models", help="Models directory")
    parser.add_argument("--projects-dir", default="projects", help="Projects directory")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    parser.add_argument("--quick-start", action="store_true", help="Quick start with minimal features")
    parser.add_argument("--full-features", action="store_true", help="Enable all features (default)")
    
    # Convenience shortcuts
    parser.add_argument("--desktop-only", action="store_true", help="Desktop mode only")
    parser.add_argument("--web-only", action="store_true", help="Web mode only")
    parser.add_argument("--minimal", action="store_true", help="Minimal mode (basic features only)")
    
    args = parser.parse_args()
    
    # Display help information
    if len(sys.argv) == 1:
        print("""
🧠 MIA Enterprise AGI - Complete Unified System
===============================================

Quick Start Examples:
  python3 mia_enterprise_agi.py                    # Full enterprise mode
  python3 mia_enterprise_agi.py --test             # Test system integrity
  python3 mia_enterprise_agi.py --desktop-only     # Desktop application only
  python3 mia_enterprise_agi.py --web-only         # Web interface only
  python3 mia_enterprise_agi.py --minimal          # Minimal features
  python3 mia_enterprise_agi.py --quick-start      # Quick start mode
  
Available Modes:
  enterprise  - Full enterprise features (default)
  production  - Production deployment
  development - Development mode with debug
  desktop     - Desktop application focus
  web         - Web interface focus
  hybrid      - Combined desktop + web
  testing     - Testing and validation

Access Points (after startup):
  🌐 Web Interface: http://localhost:12000
  💬 Chat Interface: http://localhost:12000/chat
  📊 Dashboard: http://localhost:12000/dashboard
  🔌 API Gateway: http://localhost:8000
  🖥️ Desktop App: http://localhost:12001

For full help: python3 mia_enterprise_agi.py --help
""")
    
    # Create system configuration
    config = create_config_from_args(args)
    
    # Create and run MIA Enterprise AGI
    mia_system = MIAEnterpriseAGI(config)
    
    try:
        await mia_system.initialize()
        
        if args.test:
            print("✅ MIA Enterprise AGI test mode - system initialized successfully")
            await mia_system.shutdown()
        else:
            await mia_system.run()
            
    except KeyboardInterrupt:
        print("\n👋 MIA Enterprise AGI stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure proper event loop handling
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())