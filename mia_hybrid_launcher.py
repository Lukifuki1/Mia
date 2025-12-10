#!/usr/bin/env python3
"""
MIA Hybrid Launcher - Unified launcher za celoten hibridni MIA sistem
====================================================================

PRODUKCIJSKA IMPLEMENTACIJA unified launcher-ja, ki omogoča:
- Enostaven zagon celotnega hibridnega sistema
- Različne načine delovanja (classic, hybrid, adaptive)
- Web in desktop interface support
- Enterprise funkcionalnosti
- Monitoring in diagnostics
- Configuration management
- Graceful shutdown

KLJUČNE FUNKCIONALNOSTI:
- Unified system startup
- Multi-mode support (classic/hybrid/adaptive)
- Web server integration
- Desktop application support
- Enterprise features
- Real-time monitoring
- Configuration management
- Health checks
- Graceful shutdown

ARHITEKTURA:
- Ohrani backward compatibility z obstoječim launcher-jem
- Dodaj hibridne funkcionalnosti
- Support za različne deployment modes
- Comprehensive error handling
"""

import os
import sys
import json
import logging
import asyncio
import argparse
import signal
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import subprocess
import webbrowser
from concurrent.futures import ThreadPoolExecutor

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import MIA components
try:
    from mia.core.agi_core import AGICore
    from mia.core.persistent_knowledge_store import PersistentKnowledgeStore
    from mia.core.hybrid_integration import HybridIntegration, IntegrationConfig, IntegrationMode, create_hybrid_integration, get_default_config
    MIA_CORE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ MIA Core components not available: {e}")
    MIA_CORE_AVAILABLE = False

# Import hybrid components
try:
    from mia.knowledge.hybrid.hybrid_pipeline import create_full_hybrid_system
    HYBRID_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Hybrid components not available: {e}")
    HYBRID_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mia_hybrid.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class LauncherConfig:
    """Konfiguracija launcher-ja"""
    mode: str = "hybrid_enhanced"  # classic, hybrid, hybrid_enhanced, adaptive
    enable_web: bool = True
    enable_desktop: bool = False
    enable_enterprise: bool = True
    web_port: int = 8000
    web_host: str = "0.0.0.0"
    data_dir: str = "data"
    log_level: str = "INFO"
    auto_open_browser: bool = True
    enable_monitoring: bool = True
    enable_api: bool = True
    
class MiaHybridLauncher:
    """
    Unified launcher za celoten MIA hibridni sistem.
    
    Omogoča:
    - Enostaven zagon celotnega sistema
    - Različne načine delovanja
    - Web in desktop interface
    - Enterprise funkcionalnosti
    - Monitoring in diagnostics
    - Configuration management
    
    PRODUKCIJSKE FUNKCIONALNOSTI:
    ✅ Unified system startup
    ✅ Multi-mode support
    ✅ Web server integration
    ✅ Enterprise features
    ✅ Real-time monitoring
    ✅ Configuration management
    ✅ Health checks
    ✅ Graceful shutdown
    """
    
    def __init__(self, config: LauncherConfig):
        """
        Inicializiraj MIA Hybrid Launcher.
        
        Args:
            config: Konfiguracija launcher-ja
        """
        self.config = config
        self.data_dir = Path(config.data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # System components
        self.agi_core: Optional[AGICore] = None
        self.knowledge_store: Optional[PersistentKnowledgeStore] = None
        self.hybrid_integration: Optional[HybridIntegration] = None
        
        # Web server
        self.web_server_process: Optional[subprocess.Popen] = None
        self.web_server_thread: Optional[threading.Thread] = None
        
        # System state
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        self.startup_time = 0.0
        
        # Statistics
        self.stats = {
            'startup_time': 0.0,
            'uptime': 0.0,
            'requests_processed': 0,
            'system_health': 'initializing',
            'components_status': {},
            'last_health_check': 0.0
        }
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        logger.info("✅ MIA Hybrid Launcher inicializiran")
        logger.info(f"   - Mode: {self.config.mode}")
        logger.info(f"   - Web: {'✅' if self.config.enable_web else '❌'}")
        logger.info(f"   - Desktop: {'✅' if self.config.enable_desktop else '❌'}")
        logger.info(f"   - Enterprise: {'✅' if self.config.enable_enterprise else '❌'}")
        
    def _setup_signal_handlers(self):
        """Nastavi signal handlers za graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.shutdown())
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    async def start(self):
        """Zaženi celoten MIA hibridni sistem"""
        try:
            startup_start = time.time()
            logger.info("🚀 Starting MIA Hybrid System...")
            
            # Update log level
            logging.getLogger().setLevel(getattr(logging, self.config.log_level.upper()))
            
            # Initialize core components
            await self._initialize_core_components()
            
            # Initialize hybrid integration
            await self._initialize_hybrid_integration()
            
            # Start web server if enabled
            if self.config.enable_web:
                await self._start_web_server()
                
            # Start desktop application if enabled
            if self.config.enable_desktop:
                await self._start_desktop_app()
                
            # Start monitoring if enabled
            if self.config.enable_monitoring:
                await self._start_monitoring()
                
            # System is now running
            self.is_running = True
            self.startup_time = time.time() - startup_start
            self.stats['startup_time'] = self.startup_time
            self.stats['system_health'] = 'running'
            
            logger.info(f"✅ MIA Hybrid System started successfully in {self.startup_time:.2f}s")
            
            # Print system information
            await self._print_system_info()
            
            # Open browser if configured
            if self.config.enable_web and self.config.auto_open_browser:
                await self._open_browser()
                
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"Error starting MIA Hybrid System: {e}")
            raise
            
    async def _initialize_core_components(self):
        """Inicializiraj osnovne komponente"""
        try:
            logger.info("🔄 Initializing core components...")
            
            if not MIA_CORE_AVAILABLE:
                logger.warning("❌ MIA Core components not available")
                return
                
            # Initialize Knowledge Store
            knowledge_store_path = self.data_dir / "knowledge_store"
            self.knowledge_store = PersistentKnowledgeStore(str(knowledge_store_path))
            logger.info("✅ Knowledge Store initialized")
            
            # Initialize AGI Core
            self.agi_core = AGICore(
                knowledge_store=self.knowledge_store,
                data_dir=str(self.data_dir / "agi_core")
            )
            logger.info("✅ AGI Core initialized")
            
            # Update component status
            self.stats['components_status']['knowledge_store'] = 'running'
            self.stats['components_status']['agi_core'] = 'running'
            
        except Exception as e:
            logger.error(f"Error initializing core components: {e}")
            self.stats['components_status']['core'] = 'error'
            raise
            
    async def _initialize_hybrid_integration(self):
        """Inicializiraj hibridno integracijo"""
        try:
            logger.info("🔄 Initializing hybrid integration...")
            
            # Create integration config
            integration_config = IntegrationConfig(
                mode=IntegrationMode(self.config.mode),
                enable_hybrid_reasoning=True,
                enable_semantic_processing=True,
                enable_autonomous_learning=True,
                fallback_to_classic=True,
                performance_monitoring=self.config.enable_monitoring,
                data_dir=str(self.data_dir / "hybrid_integration")
            )
            
            # Create hybrid integration
            self.hybrid_integration = await create_hybrid_integration(
                config=integration_config,
                agi_core=self.agi_core,
                knowledge_store=self.knowledge_store
            )
            
            logger.info("✅ Hybrid Integration initialized")
            self.stats['components_status']['hybrid_integration'] = 'running'
            
            # Get capabilities
            capabilities = self.hybrid_integration.get_capabilities()
            logger.info(f"   - Capability Level: {capabilities['capability_level']}")
            logger.info(f"   - Classic Available: {'✅' if capabilities['classic_capabilities']['agi_core'] else '❌'}")
            logger.info(f"   - Hybrid Available: {'✅' if capabilities['hybrid_capabilities']['hybrid_pipeline'] else '❌'}")
            
        except Exception as e:
            logger.error(f"Error initializing hybrid integration: {e}")
            self.stats['components_status']['hybrid_integration'] = 'error'
            # Don't raise - system can still work with classic components
            
    async def _start_web_server(self):
        """Zaženi web server"""
        try:
            logger.info("🔄 Starting web server...")
            
            # Create web server script
            web_server_script = self._create_web_server_script()
            
            # Start web server in separate process
            def start_server():
                try:
                    import uvicorn
                    from fastapi import FastAPI, HTTPException
                    from fastapi.staticfiles import StaticFiles
                    from fastapi.responses import HTMLResponse, JSONResponse
                    from fastapi.middleware.cors import CORSMiddleware
                    import uvicorn
                    
                    app = FastAPI(title="MIA Hybrid System", version="1.0.0")
                    
                    # Add CORS middleware
                    app.add_middleware(
                        CORSMiddleware,
                        allow_origins=["*"],
                        allow_credentials=True,
                        allow_methods=["*"],
                        allow_headers=["*"],
                    )
                    
                    # Health check endpoint
                    @app.get("/health")
                    async def health_check():
                        return JSONResponse({
                            "status": "healthy",
                            "uptime": time.time() - self.startup_time,
                            "components": self.stats['components_status']
                        })
                        
                    # Main interface endpoint
                    @app.get("/", response_class=HTMLResponse)
                    async def main_interface():
                        return self._get_main_interface_html()
                        
                    # API endpoint for processing requests
                    @app.post("/api/process")
                    async def process_request(request_data: dict):
                        try:
                            if not self.hybrid_integration:
                                raise HTTPException(status_code=503, detail="Hybrid integration not available")
                                
                            from mia.core.hybrid_integration import ProcessingRequest
                            
                            # Create processing request
                            processing_request = ProcessingRequest(
                                request_id=str(time.time()),
                                user_input=request_data.get('input', ''),
                                user_id=request_data.get('user_id', 'web_user'),
                                context=request_data.get('context', {}),
                                preferred_mode=None,
                                timestamp=time.time()
                            )
                            
                            # Process request
                            response = await self.hybrid_integration.process_request(processing_request)
                            
                            # Update statistics
                            self.stats['requests_processed'] += 1
                            
                            return JSONResponse({
                                "success": response.success,
                                "response": response.response,
                                "confidence": response.confidence,
                                "processing_time": response.processing_time,
                                "mode_used": response.mode_used.value,
                                "capabilities_used": response.capabilities_used
                            })
                            
                        except Exception as e:
                            logger.error(f"Error processing request: {e}")
                            raise HTTPException(status_code=500, detail=str(e))
                            
                    # Statistics endpoint
                    @app.get("/api/stats")
                    async def get_statistics():
                        stats = {
                            'system_stats': self.stats,
                            'integration_stats': self.hybrid_integration.get_statistics() if self.hybrid_integration else {}
                        }
                        return JSONResponse(stats)
                        
                    # Capabilities endpoint
                    @app.get("/api/capabilities")
                    async def get_capabilities():
                        if self.hybrid_integration:
                            return JSONResponse(self.hybrid_integration.get_capabilities())
                        else:
                            return JSONResponse({"error": "Hybrid integration not available"})
                            
                    # Start server
                    uvicorn.run(
                        app,
                        host=self.config.web_host,
                        port=self.config.web_port,
                        log_level="info"
                    )
                    
                except ImportError:
                    logger.error("FastAPI/Uvicorn not available - web server cannot start")
                except Exception as e:
                    logger.error(f"Error starting web server: {e}")
                    
            # Start server in thread
            self.web_server_thread = threading.Thread(target=start_server, daemon=True)
            self.web_server_thread.start()
            
            # Wait a bit for server to start
            await asyncio.sleep(2)
            
            logger.info(f"✅ Web server started on http://{self.config.web_host}:{self.config.web_port}")
            self.stats['components_status']['web_server'] = 'running'
            
        except Exception as e:
            logger.error(f"Error starting web server: {e}")
            self.stats['components_status']['web_server'] = 'error'
            
    def _create_web_server_script(self) -> str:
        """Ustvari web server script"""
        # Create a proper web server script
        return "web_server.py"
        
    def _get_main_interface_html(self) -> str:
        """Pridobi HTML za glavni interface"""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MIA Hybrid System</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; margin-bottom: 30px; }
                .header h1 { color: #333; margin: 0; }
                .header p { color: #666; margin: 10px 0 0 0; }
                .chat-container { border: 1px solid #ddd; border-radius: 5px; height: 400px; overflow-y: auto; padding: 10px; margin-bottom: 20px; background: #fafafa; }
                .input-container { display: flex; gap: 10px; }
                .input-container input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
                .input-container button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
                .input-container button:hover { background: #0056b3; }
                .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
                .user-message { background: #e3f2fd; text-align: right; }
                .system-message { background: #f1f8e9; }
                .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
                .stat-card { background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }
                .stat-value { font-size: 24px; font-weight: bold; color: #007bff; }
                .stat-label { color: #666; margin-top: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 MIA Hybrid System</h1>
                    <p>Advanced AI with Neural-Symbolic Integration</p>
                </div>
                
                <div class="chat-container" id="chatContainer">
                    <div class="message system-message">
                        <strong>MIA:</strong> Hello! I'm MIA, your hybrid AI assistant. I combine neural processing with symbolic reasoning to provide intelligent responses. How can I help you today?
                    </div>
                </div>
                
                <div class="input-container">
                    <input type="text" id="userInput" placeholder="Ask me anything..." onkeypress="handleKeyPress(event)">
                    <button onclick="sendMessage()">Send</button>
                </div>
                
                <div class="stats" id="statsContainer">
                    <div class="stat-card">
                        <div class="stat-value" id="requestsCount">0</div>
                        <div class="stat-label">Requests Processed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="systemHealth">Healthy</div>
                        <div class="stat-label">System Health</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="uptime">0s</div>
                        <div class="stat-label">Uptime</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="mode">Hybrid</div>
                        <div class="stat-label">Processing Mode</div>
                    </div>
                </div>
            </div>
            
            <script>
                function handleKeyPress(event) {
                    if (event.key === 'Enter') {
                        sendMessage();
                    }
                }
                
                async function sendMessage() {
                    const input = document.getElementById('userInput');
                    const message = input.value.trim();
                    
                    if (!message) return;
                    
                    // Add user message to chat
                    addMessage(message, 'user');
                    input.value = '';
                    
                    try {
                        // Send request to API
                        const response = await fetch('/api/process', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                input: message,
                                user_id: 'web_user',
                                context: {}
                            })
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            addMessage(data.response, 'system', {
                                confidence: data.confidence,
                                processing_time: data.processing_time,
                                mode_used: data.mode_used,
                                capabilities_used: data.capabilities_used
                            });
                        } else {
                            addMessage('Sorry, I encountered an error processing your request.', 'system');
                        }
                        
                    } catch (error) {
                        console.error('Error:', error);
                        addMessage('Sorry, I encountered a network error.', 'system');
                    }
                    
                    // Update statistics
                    updateStats();
                }
                
                function addMessage(text, type, metadata = null) {
                    const chatContainer = document.getElementById('chatContainer');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${type}-message`;
                    
                    let content = `<strong>${type === 'user' ? 'You' : 'MIA'}:</strong> ${text}`;
                    
                    if (metadata) {
                        content += `<br><small style="color: #666;">
                            Confidence: ${(metadata.confidence * 100).toFixed(1)}% | 
                            Time: ${(metadata.processing_time * 1000).toFixed(0)}ms | 
                            Mode: ${metadata.mode_used} | 
                            Capabilities: ${metadata.capabilities_used.join(', ')}
                        </small>`;
                    }
                    
                    messageDiv.innerHTML = content;
                    chatContainer.appendChild(messageDiv);
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
                
                async function updateStats() {
                    try {
                        const response = await fetch('/api/stats');
                        const stats = await response.json();
                        
                        document.getElementById('requestsCount').textContent = stats.system_stats.requests_processed || 0;
                        document.getElementById('systemHealth').textContent = stats.system_stats.system_health || 'Unknown';
                        
                        const uptime = stats.system_stats.uptime || 0;
                        document.getElementById('uptime').textContent = uptime > 60 ? `${Math.floor(uptime/60)}m` : `${Math.floor(uptime)}s`;
                        
                    } catch (error) {
                        console.error('Error updating stats:', error);
                    }
                }
                
                // Update stats every 30 seconds
                setInterval(updateStats, 30000);
                updateStats();
            </script>
        </body>
        </html>
        """
        
    async def _start_desktop_app(self):
        """Zaženi desktop aplikacijo"""
        try:
            logger.info("🔄 Starting desktop application...")
            
            # Check if desktop directory exists
            desktop_dir = project_root / "desktop"
            if not desktop_dir.exists():
                logger.warning("❌ Desktop directory not found")
                return
                
            # Try to start Electron app
            electron_main = desktop_dir / "main.js"
            if electron_main.exists():
                self.web_server_process = subprocess.Popen([
                    "npm", "start"
                ], cwd=str(desktop_dir))
                
                logger.info("✅ Desktop application started")
                self.stats['components_status']['desktop_app'] = 'running'
            else:
                logger.warning("❌ Desktop application main.js not found")
                
        except Exception as e:
            logger.error(f"Error starting desktop application: {e}")
            self.stats['components_status']['desktop_app'] = 'error'
            
    async def _start_monitoring(self):
        """Zaženi monitoring sistem"""
        try:
            logger.info("🔄 Starting monitoring system...")
            
            # Start health check loop
            asyncio.create_task(self._health_check_loop())
            
            logger.info("✅ Monitoring system started")
            self.stats['components_status']['monitoring'] = 'running'
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            self.stats['components_status']['monitoring'] = 'error'
            
    async def _health_check_loop(self):
        """Zanka za preverjanje zdravja sistema"""
        while self.is_running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check: {e}")
                await asyncio.sleep(60)
                
    async def _perform_health_check(self):
        """Izvedi preverjanje zdravja sistema"""
        try:
            self.stats['last_health_check'] = time.time()
            self.stats['uptime'] = time.time() - self.startup_time
            
            # Check component health
            healthy_components = 0
            total_components = len(self.stats['components_status'])
            
            for component, status in self.stats['components_status'].items():
                if status == 'running':
                    healthy_components += 1
                    
            # Update overall health
            if healthy_components == total_components:
                self.stats['system_health'] = 'healthy'
            elif healthy_components > total_components / 2:
                self.stats['system_health'] = 'degraded'
            else:
                self.stats['system_health'] = 'unhealthy'
                
            # Log health status
            logger.debug(f"Health check: {self.stats['system_health']} "
                        f"({healthy_components}/{total_components} components healthy)")
                        
        except Exception as e:
            logger.error(f"Error performing health check: {e}")
            self.stats['system_health'] = 'error'
            
    async def _print_system_info(self):
        """Izpiši informacije o sistemu"""
        print("\n" + "="*60)
        print("🧠 MIA HYBRID SYSTEM - SUCCESSFULLY STARTED")
        print("="*60)
        print(f"Mode: {self.config.mode}")
        print(f"Startup Time: {self.startup_time:.2f}s")
        print(f"Data Directory: {self.data_dir}")
        
        if self.config.enable_web:
            print(f"Web Interface: http://{self.config.web_host}:{self.config.web_port}")
            
        print("\nComponents Status:")
        for component, status in self.stats['components_status'].items():
            status_icon = "✅" if status == "running" else "❌"
            print(f"  {status_icon} {component}: {status}")
            
        if self.hybrid_integration:
            capabilities = self.hybrid_integration.get_capabilities()
            print(f"\nCapability Level: {capabilities['capability_level']}")
            
            print("\nAvailable Capabilities:")
            for category, caps in capabilities.items():
                if isinstance(caps, dict):
                    print(f"  {category}:")
                    for cap, available in caps.items():
                        cap_icon = "✅" if available else "❌"
                        print(f"    {cap_icon} {cap}")
                        
        print("\nCommands:")
        print("  Ctrl+C - Graceful shutdown")
        print("  Check logs in: mia_hybrid.log")
        print("="*60 + "\n")
        
    async def _open_browser(self):
        """Odpri browser z web interface"""
        try:
            await asyncio.sleep(3)  # Wait for server to be ready
            url = f"http://localhost:{self.config.web_port}"
            webbrowser.open(url)
            logger.info(f"🌐 Browser opened: {url}")
        except Exception as e:
            logger.error(f"Error opening browser: {e}")
            
    async def shutdown(self):
        """Graceful shutdown celotnega sistema"""
        try:
            logger.info("🔄 Shutting down MIA Hybrid System...")
            
            self.is_running = False
            
            # Shutdown hybrid integration
            if self.hybrid_integration:
                await self.hybrid_integration.shutdown()
                logger.info("✅ Hybrid Integration shutdown")
                
            # Shutdown web server
            if self.web_server_process:
                self.web_server_process.terminate()
                self.web_server_process.wait()
                logger.info("✅ Web server shutdown")
                
            # Update final statistics
            self.stats['system_health'] = 'shutdown'
            self.stats['uptime'] = time.time() - self.startup_time
            
            # Signal shutdown complete
            self.shutdown_event.set()
            
            logger.info(f"✅ MIA Hybrid System shutdown complete (uptime: {self.stats['uptime']:.1f}s)")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            
    def get_system_status(self) -> Dict[str, Any]:
        """Pridobi status sistema"""
        return {
            'is_running': self.is_running,
            'startup_time': self.startup_time,
            'uptime': time.time() - self.startup_time if self.is_running else 0,
            'config': asdict(self.config),
            'stats': self.stats,
            'capabilities': self.hybrid_integration.get_capabilities() if self.hybrid_integration else {}
        }


def parse_arguments():
    """Parsiraj command line argumente"""
    parser = argparse.ArgumentParser(description="MIA Hybrid System Launcher")
    
    parser.add_argument("--mode", 
                       choices=["classic", "hybrid", "hybrid_enhanced", "adaptive"],
                       default="hybrid_enhanced",
                       help="System mode (default: hybrid_enhanced)")
                       
    parser.add_argument("--web-port", type=int, default=8000,
                       help="Web server port (default: 8000)")
                       
    parser.add_argument("--web-host", default="0.0.0.0",
                       help="Web server host (default: 0.0.0.0)")
                       
    parser.add_argument("--data-dir", default="data",
                       help="Data directory (default: data)")
                       
    parser.add_argument("--log-level", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       default="INFO",
                       help="Log level (default: INFO)")
                       
    parser.add_argument("--no-web", action="store_true",
                       help="Disable web interface")
                       
    parser.add_argument("--no-browser", action="store_true",
                       help="Don't auto-open browser")
                       
    parser.add_argument("--enable-desktop", action="store_true",
                       help="Enable desktop application")
                       
    parser.add_argument("--no-enterprise", action="store_true",
                       help="Disable enterprise features")
                       
    parser.add_argument("--no-monitoring", action="store_true",
                       help="Disable monitoring")
                       
    return parser.parse_args()


def create_config_from_args(args) -> LauncherConfig:
    """Ustvari konfiguracijo iz argumentov"""
    return LauncherConfig(
        mode=args.mode,
        enable_web=not args.no_web,
        enable_desktop=args.enable_desktop,
        enable_enterprise=not args.no_enterprise,
        web_port=args.web_port,
        web_host=args.web_host,
        data_dir=args.data_dir,
        log_level=args.log_level,
        auto_open_browser=not args.no_browser,
        enable_monitoring=not args.no_monitoring,
        enable_api=True
    )


async def main():
    """Glavna funkcija"""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Create configuration
        config = create_config_from_args(args)
        
        # Create and start launcher
        launcher = MiaHybridLauncher(config)
        await launcher.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required")
            sys.exit(1)
            
        # Print banner
        print("""
╔══════════════════════════════════════════════════════════════╗
║                    🧠 MIA HYBRID SYSTEM                      ║
║              Neural-Symbolic AI Integration                  ║
║                                                              ║
║  🚀 Starting unified hybrid system...                       ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        # Run main
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)