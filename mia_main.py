#!/usr/bin/env python3
"""
MIA Enterprise AGI - Desktop Application Launcher
Complete local AI system with model discovery and learning
"""

import os
import sys
import json
import logging
import asyncio
import time
import signal
import threading
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import MIA core systems
try:
    from mia.core.agi_core import agi_core, initialize_agi, shutdown_agi
    from mia.core.model_discovery import model_discovery, discover_models
    from mia.core.model_learning import model_learning, start_learning_from_models
    from mia.interfaces.chat import chat_interface
    from mia.enterprise.security import security_manager
    from mia.enterprise.analytics import analytics
    from mia.enterprise.api_gateway import api_gateway
    from mia.modules.ui.web import MIAWebUI
except ImportError as e:
    print(f"❌ Critical import error: {e}")
    print("Ensure all MIA modules are properly installed")
    sys.exit(1)

class MIADesktopApp:
    """MIA Desktop Application"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.is_running = False
        self.web_ui = None
        self.shutdown_event = threading.Event()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _setup_logging(self) -> logging.Logger:
        """Setup application logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('mia_desktop.log')
            ]
        )
        return logging.getLogger("MIA.Desktop")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
    
    async def start(self):
        """Start the MIA desktop application"""
        try:
            self.logger.info("🚀 Starting MIA Enterprise AGI Desktop Application")
            self.is_running = True
            
            # Display startup banner
            self._display_banner()
            
            # Initialize core systems
            await self._initialize_systems()
            
            # Start model discovery
            self._start_model_discovery()
            
            # Start model learning
            self._start_model_learning()
            
            # Start web interface
            await self._start_web_interface()
            
            # Start API gateway
            await self._start_api_gateway()
            
            self.logger.info("✅ MIA Desktop Application started successfully")
            self.logger.info("🌐 Web interface: http://localhost:12000")
            self.logger.info("🔌 API gateway: http://localhost:8000")
            
            # Keep application running
            await self._run_main_loop()
            
        except Exception as e:
            self.logger.error(f"Failed to start MIA Desktop: {e}")
            raise
    
    def _display_banner(self):
        """Display startup banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🤖 MIA Enterprise AGI                     ║
║                  Desktop Application v1.0.0                 ║
║                                                              ║
║  🧠 Local Digital Intelligence System                       ║
║  🔍 Automatic Model Discovery                               ║
║  📚 Self-Learning from Local Models                         ║
║  🔒 Enterprise Security & Analytics                         ║
║  🌐 Web Interface & API Gateway                             ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    async def _initialize_systems(self):
        """Initialize core MIA systems"""
        self.logger.info("🔧 Initializing core systems...")
        
        # Create data directories
        data_dirs = [
            "mia/data/models",
            "mia/data/learning",
            "mia/data/analytics",
            "mia/data/security",
            "mia/logs"
        ]
        
        for dir_path in data_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize AGI Core
        self.logger.info("🧠 Initializing AGI Core...")
        await initialize_agi()
        
        # Initialize security manager
        self.logger.info("🔒 Initializing security system...")
        # Security manager is already initialized globally
        
        # Initialize analytics
        self.logger.info("📊 Initializing analytics system...")
        # Analytics is already initialized globally
        
        self.logger.info("✅ Core systems initialized")
    
    def _start_model_discovery(self):
        """Start automatic model discovery"""
        self.logger.info("🔍 Starting model discovery...")
        
        try:
            # Load existing model cache
            model_discovery.load_model_cache()
            
            # Start continuous discovery
            discover_models(continuous=True)
            
            # Display initial stats
            stats = model_discovery.get_discovery_stats()
            self.logger.info(f"📊 Model discovery stats: {stats['total_models']} models found")
            
        except Exception as e:
            self.logger.error(f"Failed to start model discovery: {e}")
    
    def _start_model_learning(self):
        """Start model learning system"""
        self.logger.info("📚 Starting model learning...")
        
        try:
            # Wait a bit for model discovery to find some models
            def delayed_learning():
                time.sleep(30)  # Wait 30 seconds
                start_learning_from_models()
                self.logger.info("🧠 Model learning started")
            
            learning_thread = threading.Thread(target=delayed_learning, daemon=True)
            learning_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start model learning: {e}")
    
    async def _start_web_interface(self):
        """Start web interface"""
        self.logger.info("🌐 Starting web interface...")
        
        try:
            self.web_ui = MIAWebUI(host="0.0.0.0", port=12000)
            
            # Start web UI in background
            def start_web_ui():
                import uvicorn
                uvicorn.run(
                    self.web_ui.app,
                    host=self.web_ui.host,
                    port=self.web_ui.port,
                    log_level="info"
                )
            
            web_thread = threading.Thread(target=start_web_ui, daemon=True)
            web_thread.start()
            
            # Wait a bit for web server to start
            await asyncio.sleep(2)
            
            self.logger.info("✅ Web interface started on http://localhost:12000")
            
        except Exception as e:
            self.logger.error(f"Failed to start web interface: {e}")
    
    async def _start_api_gateway(self):
        """Start API gateway"""
        self.logger.info("🔌 Starting API gateway...")
        
        try:
            # Start API gateway in background
            def start_api():
                import uvicorn
                uvicorn.run(
                    api_gateway.app,
                    host="0.0.0.0",
                    port=8000,
                    log_level="info"
                )
            
            api_thread = threading.Thread(target=start_api, daemon=True)
            api_thread.start()
            
            # Wait a bit for API server to start
            await asyncio.sleep(2)
            
            self.logger.info("✅ API gateway started on http://localhost:8000")
            
        except Exception as e:
            self.logger.error(f"Failed to start API gateway: {e}")
    
    async def _run_main_loop(self):
        """Main application loop"""
        self.logger.info("🔄 Entering main application loop")
        
        try:
            while self.is_running and not self.shutdown_event.is_set():
                # Display periodic status
                await self._display_status()
                
                # Wait for shutdown or next status update
                try:
                    await asyncio.wait_for(
                        asyncio.create_task(self._wait_for_shutdown()),
                        timeout=60.0  # Update status every minute
                    )
                    break  # Shutdown requested
                except asyncio.TimeoutError:
                    continue  # Continue main loop
                    
        except KeyboardInterrupt:
            self.logger.info("🛑 Application interrupted by user")
        except Exception as e:
            self.logger.error(f"Main loop error: {e}")
        finally:
            await self._cleanup()
    
    async def _wait_for_shutdown(self):
        """Wait for shutdown event"""
        while not self.shutdown_event.is_set():
            await asyncio.sleep(1)
    
    async def _display_status(self):
        """Display current system status"""
        try:
            # Get model discovery stats
            discovery_stats = model_discovery.get_discovery_stats()
            
            # Get learning stats
            learning_stats = model_learning.get_learning_stats()
            
            # Get analytics stats
            analytics_stats = analytics.get_real_time_metrics()
            
            status = f"""
📊 MIA System Status:
├─ 🔍 Model Discovery: {discovery_stats['total_models']} models found
├─ 📚 Learning: {learning_stats['completed_tasks']}/{learning_stats['total_tasks']} tasks completed
├─ 🔒 Security: Active sessions, encryption enabled
├─ 📈 Analytics: Real-time monitoring active
├─ 🌐 Web UI: Running on port 12000
└─ 🔌 API Gateway: Running on port 8000
            """
            
            self.logger.info(status)
            
        except Exception as e:
            self.logger.warning(f"Failed to display status: {e}")
    
    def shutdown(self):
        """Shutdown the application"""
        self.logger.info("🛑 Shutting down MIA Desktop Application...")
        self.is_running = False
        self.shutdown_event.set()
    
    async def _cleanup(self):
        """Cleanup resources"""
        try:
            self.logger.info("🧹 Cleaning up resources...")
            
            # Stop model discovery
            model_discovery.stop_discovery()
            
            # Stop model learning
            model_learning.stop_learning()
            
            # Save learning results
            model_learning.save_learning_results()
            
            # Flush analytics
            analytics._flush_metrics()
            
            self.logger.info("✅ Cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

def main():
    """Main entry point"""
    app = MIADesktopApp()
    
    try:
        # Run the application
        asyncio.run(app.start())
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)
    finally:
        print("👋 MIA Desktop Application stopped")

if __name__ == "__main__":
    main()
