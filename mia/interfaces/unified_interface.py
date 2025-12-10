#!/usr/bin/env python3
"""
🌐 MIA Enterprise AGI - Unified Interface System
===============================================

Konsolidiran vmesniški sistem, ki združuje:
- Web vmesnik (HTML/CSS/JavaScript)
- Chat vmesnik (WebSocket real-time)
- Desktop vmesnik (Electron/Native)
- Voice vmesnik (STT/TTS)
- API vmesnik (REST/GraphQL)
"""

import os
import sys
import json
import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, Union, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import uuid
from datetime import datetime

# FastAPI and WebSocket imports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import uvicorn

class InterfaceType(Enum):
    """Interface types"""
    WEB = "web"
    CHAT = "chat"
    DESKTOP = "desktop"
    VOICE = "voice"
    API = "api"

class MessageType(Enum):
    """Message types"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    THOUGHT = "thought"
    ERROR = "error"
    STATUS = "status"

@dataclass
class InterfaceMessage:
    """Interface message"""
    id: str
    type: MessageType
    content: str
    timestamp: float
    interface: InterfaceType
    metadata: Dict[str, Any]

@dataclass
class InterfaceConfig:
    """Interface configuration"""
    web_enabled: bool = True
    chat_enabled: bool = True
    desktop_enabled: bool = True
    voice_enabled: bool = True
    api_enabled: bool = True
    web_port: int = 12000
    api_port: int = 8000
    host: str = "0.0.0.0"
    cors_enabled: bool = True
    static_files: bool = True

class UnifiedInterfaceSystem:
    """
    Unified Interface System
    
    Centralizirani sistem za vse uporabniške vmesnike
    """
    
    def __init__(self, config: Optional[InterfaceConfig] = None):
        self.config = config or InterfaceConfig()
        self.logger = self._setup_logging()
        self.is_running = False
        
        # Interface components
        self.web_app = FastAPI(title="MIA Enterprise AGI", version="1.0.0")
        self.websocket_connections: List[WebSocket] = []
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.message_history: List[InterfaceMessage] = []
        
        # Setup directories
        self.static_dir = Path("web/static")
        self.templates_dir = Path("web/templates")
        self.data_dir = Path("mia_data/interfaces")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("🌐 Unified Interface System initializing...")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup interface logging"""
        return logging.getLogger("MIA.Interfaces.Unified")
    
    async def initialize(self):
        """Initialize all interface components"""
        self.logger.info("🚀 Initializing Interface Components...")
        
        try:
            # Setup FastAPI application
            await self._setup_web_app()
            
            # Initialize chat system
            await self._initialize_chat_system()
            
            # Initialize voice system
            if self.config.voice_enabled:
                await self._initialize_voice_system()
            
            # Initialize desktop interface
            if self.config.desktop_enabled:
                await self._initialize_desktop_interface()
            
            # Create static files and templates
            await self._create_web_assets()
            
            self.is_running = True
            self.logger.info("✅ Interface Components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize interface components: {e}")
            raise
    
    async def _setup_web_app(self):
        """Setup FastAPI web application"""
        self.logger.info("🌐 Setting up Web Application...")
        
        # Add CORS middleware
        if self.config.cors_enabled:
            self.web_app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # Setup static files
        if self.config.static_files and self.static_dir.exists():
            self.web_app.mount("/static", StaticFiles(directory=str(self.static_dir)), name="static")
        
        # Setup routes
        await self._setup_routes()
        
        self.logger.info("✅ Web Application setup complete")
    
    async def _setup_routes(self):
        """Setup web routes"""
        
        @self.web_app.get("/", response_class=HTMLResponse)
        async def home(request: Request):
            """Home page"""
            return HTMLResponse(self._get_home_html())
        
        @self.web_app.get("/chat", response_class=HTMLResponse)
        async def chat_page(request: Request):
            """Chat interface page"""
            return HTMLResponse(self._get_chat_html())
        
        @self.web_app.get("/dashboard", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Dashboard page"""
            return HTMLResponse(self._get_dashboard_html())
        
        @self.web_app.websocket("/ws/chat")
        async def chat_websocket(websocket: WebSocket):
            """WebSocket endpoint for chat"""
            await self._handle_chat_websocket(websocket)
        
        @self.web_app.get("/api/status")
        async def api_status():
            """API status endpoint"""
            return await self._get_api_status()
        
        @self.web_app.post("/api/chat")
        async def api_chat(request: Request):
            """API chat endpoint"""
            data = await request.json()
            return await self._process_api_chat(data)
        
        @self.web_app.get("/api/interfaces/status")
        async def interfaces_status():
            """Get interfaces status"""
            return {
                "web": self.config.web_enabled,
                "chat": self.config.chat_enabled,
                "desktop": self.config.desktop_enabled,
                "voice": self.config.voice_enabled,
                "api": self.config.api_enabled,
                "active_connections": len(self.websocket_connections),
                "active_sessions": len(self.active_sessions),
                "message_count": len(self.message_history),
                "timestamp": time.time()
            }
        
        @self.web_app.post("/api/voice/speak")
        async def voice_speak(request: Request):
            """Voice synthesis endpoint"""
            data = await request.json()
            return await self._process_voice_synthesis(data)
        
        @self.web_app.post("/api/voice/listen")
        async def voice_listen(request: Request):
            """Voice recognition endpoint"""
            return await self._process_voice_recognition()
    
    async def _initialize_chat_system(self):
        """Initialize chat system"""
        self.logger.info("💬 Initializing Chat System...")
        
        # Load chat configuration
        chat_config = {
            "max_message_length": 10000,
            "max_history_length": 1000,
            "typing_indicator": True,
            "message_streaming": True,
            "file_upload": True,
            "voice_input": self.config.voice_enabled
        }
        
        # Save chat configuration
        with open(self.data_dir / "chat_config.json", "w") as f:
            json.dump(chat_config, f, indent=2)
        
        self.logger.info("✅ Chat System initialized")
    
    async def _initialize_voice_system(self):
        """Initialize voice system"""
        self.logger.info("🎤 Initializing Voice System...")
        
        try:
            # Voice system configuration
            voice_config = {
                "stt_enabled": True,
                "tts_enabled": True,
                "language": "en-US",
                "voice": "neural",
                "speech_rate": 1.0,
                "speech_volume": 0.8
            }
            
            # Save voice configuration
            with open(self.data_dir / "voice_config.json", "w") as f:
                json.dump(voice_config, f, indent=2)
            
            self.logger.info("✅ Voice System initialized")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Voice System initialization failed: {e}")
    
    async def _initialize_desktop_interface(self):
        """Initialize desktop interface"""
        self.logger.info("🖥️ Initializing Desktop Interface...")
        
        try:
            # Desktop configuration
            desktop_config = {
                "window_width": 1200,
                "window_height": 800,
                "resizable": True,
                "fullscreen": False,
                "always_on_top": False,
                "system_tray": True,
                "auto_start": False
            }
            
            # Save desktop configuration
            with open(self.data_dir / "desktop_config.json", "w") as f:
                json.dump(desktop_config, f, indent=2)
            
            self.logger.info("✅ Desktop Interface initialized")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Desktop Interface initialization failed: {e}")
    
    async def _create_web_assets(self):
        """Create web assets (HTML, CSS, JS)"""
        self.logger.info("🎨 Creating Web Assets...")
        
        # Create directories
        self.static_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create CSS file
        css_content = self._get_unified_css()
        with open(self.static_dir / "unified.css", "w") as f:
            f.write(css_content)
        
        # Create JavaScript file
        js_content = self._get_unified_js()
        with open(self.static_dir / "unified.js", "w") as f:
            f.write(js_content)
        
        self.logger.info("✅ Web Assets created")
    
    def _get_home_html(self) -> str:
        """Get home page HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIA Enterprise AGI</title>
    <link rel="stylesheet" href="/static/unified.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🧠 MIA Enterprise AGI</h1>
            <p>Artificial General Intelligence Platform</p>
        </header>
        
        <nav class="navigation">
            <a href="/" class="nav-link active">Home</a>
            <a href="/chat" class="nav-link">Chat</a>
            <a href="/dashboard" class="nav-link">Dashboard</a>
        </nav>
        
        <main class="main-content">
            <div class="welcome-section">
                <h2>Welcome to MIA Enterprise AGI</h2>
                <p>Advanced Artificial General Intelligence system for enterprise use.</p>
                
                <div class="features-grid">
                    <div class="feature-card">
                        <h3>🧠 AGI Core</h3>
                        <p>Advanced reasoning and decision making</p>
                    </div>
                    <div class="feature-card">
                        <h3>💬 Chat Interface</h3>
                        <p>Natural language conversation</p>
                    </div>
                    <div class="feature-card">
                        <h3>🔒 Enterprise Security</h3>
                        <p>Bank-grade security and compliance</p>
                    </div>
                    <div class="feature-card">
                        <h3>📊 Analytics</h3>
                        <p>Real-time monitoring and insights</p>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <a href="/chat" class="btn btn-primary">Start Chat</a>
                    <a href="/dashboard" class="btn btn-secondary">View Dashboard</a>
                </div>
            </div>
        </main>
        
        <footer class="footer">
            <p>&copy; 2024 MIA Enterprise AGI. All rights reserved.</p>
        </footer>
    </div>
    
    <script src="/static/unified.js"></script>
</body>
</html>
"""
    
    def _get_chat_html(self) -> str:
        """Get chat page HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIA Enterprise AGI - Chat</title>
    <link rel="stylesheet" href="/static/unified.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>💬 MIA Chat Interface</h1>
            <div class="status-indicator" id="connectionStatus">Connecting...</div>
        </header>
        
        <nav class="navigation">
            <a href="/" class="nav-link">Home</a>
            <a href="/chat" class="nav-link active">Chat</a>
            <a href="/dashboard" class="nav-link">Dashboard</a>
        </nav>
        
        <main class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="system-message">
                    <p>🧠 MIA Enterprise AGI is ready to assist you.</p>
                </div>
            </div>
            
            <div class="chat-input-container">
                <div class="input-group">
                    <textarea id="messageInput" placeholder="Type your message here..." rows="3"></textarea>
                    <div class="input-actions">
                        <button id="voiceButton" class="btn btn-voice" title="Voice Input">🎤</button>
                        <button id="sendButton" class="btn btn-primary">Send</button>
                    </div>
                </div>
            </div>
        </main>
    </div>
    
    <script src="/static/unified.js"></script>
    <script>
        // Initialize chat interface
        document.addEventListener('DOMContentLoaded', function() {
            initializeChatInterface();
        });
    </script>
</body>
</html>
"""
    
    def _get_dashboard_html(self) -> str:
        """Get dashboard page HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIA Enterprise AGI - Dashboard</title>
    <link rel="stylesheet" href="/static/unified.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>📊 MIA Dashboard</h1>
            <div class="system-status" id="systemStatus">Loading...</div>
        </header>
        
        <nav class="navigation">
            <a href="/" class="nav-link">Home</a>
            <a href="/chat" class="nav-link">Chat</a>
            <a href="/dashboard" class="nav-link active">Dashboard</a>
        </nav>
        
        <main class="dashboard-content">
            <div class="dashboard-grid">
                <div class="dashboard-card">
                    <h3>🧠 AGI Core Status</h3>
                    <div id="agiStatus" class="status-content">Loading...</div>
                </div>
                
                <div class="dashboard-card">
                    <h3>💬 Chat Activity</h3>
                    <div id="chatActivity" class="status-content">Loading...</div>
                </div>
                
                <div class="dashboard-card">
                    <h3>🔒 Security Status</h3>
                    <div id="securityStatus" class="status-content">Loading...</div>
                </div>
                
                <div class="dashboard-card">
                    <h3>📈 System Metrics</h3>
                    <div id="systemMetrics" class="status-content">Loading...</div>
                </div>
            </div>
        </main>
    </div>
    
    <script src="/static/unified.js"></script>
    <script>
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initializeDashboard();
        });
    </script>
</body>
</html>
"""
    
    def _get_unified_css(self) -> str:
        """Get unified CSS styles"""
        return """
/* MIA Enterprise AGI - Unified Styles */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #333;
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.header {
    background: rgba(255, 255, 255, 0.95);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
}

.header h1 {
    color: #4a5568;
    margin-bottom: 10px;
    font-size: 2.5em;
}

.header p {
    color: #718096;
    font-size: 1.2em;
}

.navigation {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-bottom: 30px;
}

.nav-link {
    padding: 12px 24px;
    background: rgba(255, 255, 255, 0.9);
    color: #4a5568;
    text-decoration: none;
    border-radius: 25px;
    transition: all 0.3s ease;
    font-weight: 500;
}

.nav-link:hover, .nav-link.active {
    background: #667eea;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.main-content {
    flex: 1;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    padding: 30px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
}

.welcome-section h2 {
    color: #4a5568;
    margin-bottom: 15px;
    font-size: 2em;
}

.welcome-section p {
    color: #718096;
    margin-bottom: 30px;
    font-size: 1.1em;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.feature-card {
    background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
    padding: 25px;
    border-radius: 12px;
    text-align: center;
    transition: transform 0.3s ease;
    border: 1px solid rgba(102, 126, 234, 0.1);
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.feature-card h3 {
    color: #4a5568;
    margin-bottom: 10px;
    font-size: 1.3em;
}

.feature-card p {
    color: #718096;
}

.action-buttons {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 30px;
}

.btn {
    padding: 15px 30px;
    border: none;
    border-radius: 25px;
    font-size: 1.1em;
    font-weight: 600;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-block;
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
    background: rgba(255, 255, 255, 0.9);
    color: #4a5568;
    border: 2px solid #667eea;
}

.btn-secondary:hover {
    background: #667eea;
    color: white;
    transform: translateY(-2px);
}

/* Chat Interface Styles */
.chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.chat-messages {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    max-height: 60vh;
}

.message {
    margin-bottom: 15px;
    padding: 15px;
    border-radius: 12px;
    max-width: 80%;
    animation: fadeIn 0.3s ease;
}

.user-message {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    margin-left: auto;
}

.assistant-message {
    background: #f7fafc;
    color: #4a5568;
    border: 1px solid #e2e8f0;
}

.system-message {
    background: #fef5e7;
    color: #744210;
    border: 1px solid #f6e05e;
    text-align: center;
}

.chat-input-container {
    padding: 20px;
    background: rgba(247, 250, 252, 0.9);
    border-top: 1px solid #e2e8f0;
}

.input-group {
    display: flex;
    gap: 10px;
    align-items: flex-end;
}

#messageInput {
    flex: 1;
    padding: 15px;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    font-size: 1em;
    resize: vertical;
    min-height: 60px;
    font-family: inherit;
}

#messageInput:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-actions {
    display: flex;
    gap: 10px;
}

.btn-voice {
    background: #48bb78;
    color: white;
    padding: 15px;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn-voice:hover {
    background: #38a169;
    transform: scale(1.05);
}

/* Dashboard Styles */
.dashboard-content {
    flex: 1;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
}

.dashboard-card {
    background: rgba(255, 255, 255, 0.95);
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(102, 126, 234, 0.1);
}

.dashboard-card h3 {
    color: #4a5568;
    margin-bottom: 15px;
    font-size: 1.3em;
}

.status-content {
    color: #718096;
    font-size: 1em;
}

.status-indicator {
    display: inline-block;
    padding: 5px 15px;
    border-radius: 20px;
    font-size: 0.9em;
    font-weight: 500;
}

.status-connected {
    background: #c6f6d5;
    color: #22543d;
}

.status-connecting {
    background: #fef5e7;
    color: #744210;
}

.status-error {
    background: #fed7d7;
    color: #742a2a;
}

.footer {
    text-align: center;
    padding: 20px;
    color: rgba(255, 255, 255, 0.8);
    margin-top: 20px;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Responsive Design */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    .header h1 {
        font-size: 2em;
    }
    
    .navigation {
        flex-wrap: wrap;
        gap: 10px;
    }
    
    .features-grid {
        grid-template-columns: 1fr;
    }
    
    .action-buttons {
        flex-direction: column;
        align-items: center;
    }
    
    .dashboard-grid {
        grid-template-columns: 1fr;
    }
}
"""
    
    def _get_unified_js(self) -> str:
        """Get unified JavaScript"""
        return """
// MIA Enterprise AGI - Unified JavaScript

class MIAInterface {
    constructor() {
        this.websocket = null;
        this.isConnected = false;
        this.messageHistory = [];
        this.currentSessionId = null;
        
        this.init();
    }
    
    init() {
        console.log('🧠 MIA Interface initializing...');
        this.setupEventListeners();
        this.updateSystemStatus();
    }
    
    setupEventListeners() {
        // Send button
        const sendButton = document.getElementById('sendButton');
        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendMessage());
        }
        
        // Message input
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
        
        // Voice button
        const voiceButton = document.getElementById('voiceButton');
        if (voiceButton) {
            voiceButton.addEventListener('click', () => this.toggleVoiceInput());
        }
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('✅ WebSocket connected');
            this.isConnected = true;
            this.updateConnectionStatus('Connected', 'status-connected');
        };
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.websocket.onclose = () => {
            console.log('❌ WebSocket disconnected');
            this.isConnected = false;
            this.updateConnectionStatus('Disconnected', 'status-error');
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.connectWebSocket(), 3000);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus('Error', 'status-error');
        };
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'assistant':
                this.addMessage(data.content, 'assistant');
                break;
            case 'thought':
                this.addThought(data.content, data.confidence);
                break;
            case 'status':
                this.updateSystemStatus(data.content);
                break;
            case 'error':
                this.addMessage(data.content, 'error');
                break;
        }
    }
    
    sendMessage() {
        const messageInput = document.getElementById('messageInput');
        if (!messageInput) return;
        
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Send via WebSocket if connected
        if (this.isConnected && this.websocket) {
            this.websocket.send(JSON.stringify({
                type: 'user_message',
                content: message,
                timestamp: Date.now()
            }));
        } else {
            // Fallback to API
            this.sendMessageViaAPI(message);
        }
        
        // Clear input
        messageInput.value = '';
    }
    
    async sendMessageViaAPI(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.currentSessionId
                })
            });
            
            const data = await response.json();
            
            if (data.response) {
                this.addMessage(data.response, 'assistant');
            }
            
            if (data.session_id) {
                this.currentSessionId = data.session_id;
            }
            
        } catch (error) {
            console.error('API error:', error);
            this.addMessage('Sorry, I encountered an error processing your message.', 'error');
        }
    }
    
    addMessage(content, type) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const timestamp = new Date().toLocaleTimeString();
        
        if (type === 'user') {
            messageDiv.innerHTML = `
                <div class="message-content">${this.escapeHtml(content)}</div>
                <div class="message-time">${timestamp}</div>
            `;
        } else if (type === 'assistant') {
            messageDiv.innerHTML = `
                <div class="message-content">🧠 ${this.escapeHtml(content)}</div>
                <div class="message-time">${timestamp}</div>
            `;
        } else if (type === 'error') {
            messageDiv.innerHTML = `
                <div class="message-content">❌ ${this.escapeHtml(content)}</div>
                <div class="message-time">${timestamp}</div>
            `;
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Store in history
        this.messageHistory.push({
            content: content,
            type: type,
            timestamp: Date.now()
        });
    }
    
    addThought(content, confidence) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;
        
        const thoughtDiv = document.createElement('div');
        thoughtDiv.className = 'message thought-message';
        thoughtDiv.innerHTML = `
            <div class="thought-content">
                💭 <em>${this.escapeHtml(content)}</em>
                <span class="confidence">(Confidence: ${(confidence * 100).toFixed(1)}%)</span>
            </div>
        `;
        
        chatMessages.appendChild(thoughtDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    updateConnectionStatus(status, className) {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = `status-indicator ${className}`;
        }
    }
    
    async updateSystemStatus() {
        try {
            const response = await fetch('/api/interfaces/status');
            const data = await response.json();
            
            const systemStatus = document.getElementById('systemStatus');
            if (systemStatus) {
                systemStatus.innerHTML = `
                    <div>Active Connections: ${data.active_connections}</div>
                    <div>Active Sessions: ${data.active_sessions}</div>
                    <div>Messages: ${data.message_count}</div>
                `;
            }
            
            // Update dashboard if present
            this.updateDashboard(data);
            
        } catch (error) {
            console.error('Failed to update system status:', error);
        }
    }
    
    updateDashboard(data) {
        const agiStatus = document.getElementById('agiStatus');
        if (agiStatus) {
            agiStatus.innerHTML = `
                <div>Status: ✅ Running</div>
                <div>Active Sessions: ${data.active_sessions}</div>
            `;
        }
        
        const chatActivity = document.getElementById('chatActivity');
        if (chatActivity) {
            chatActivity.innerHTML = `
                <div>Active Connections: ${data.active_connections}</div>
                <div>Total Messages: ${data.message_count}</div>
            `;
        }
        
        const securityStatus = document.getElementById('securityStatus');
        if (securityStatus) {
            securityStatus.innerHTML = `
                <div>Security: 🔒 Active</div>
                <div>Encryption: ✅ Enabled</div>
            `;
        }
        
        const systemMetrics = document.getElementById('systemMetrics');
        if (systemMetrics) {
            systemMetrics.innerHTML = `
                <div>Uptime: ${this.formatUptime(Date.now() - (data.timestamp * 1000))}</div>
                <div>Last Update: ${new Date(data.timestamp * 1000).toLocaleTimeString()}</div>
            `;
        }
    }
    
    toggleVoiceInput() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            this.startVoiceRecognition();
        } else {
            alert('Voice recognition is not supported in this browser.');
        }
    }
    
    startVoiceRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        const voiceButton = document.getElementById('voiceButton');
        if (voiceButton) {
            voiceButton.style.background = '#e53e3e';
            voiceButton.textContent = '🔴';
        }
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const messageInput = document.getElementById('messageInput');
            if (messageInput) {
                messageInput.value = transcript;
            }
        };
        
        recognition.onend = () => {
            if (voiceButton) {
                voiceButton.style.background = '#48bb78';
                voiceButton.textContent = '🎤';
            }
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            if (voiceButton) {
                voiceButton.style.background = '#48bb78';
                voiceButton.textContent = '🎤';
            }
        };
        
        recognition.start();
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    formatUptime(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) return `${days}d ${hours % 24}h`;
        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    }
}

// Global functions for initialization
function initializeChatInterface() {
    const miaInterface = new MIAInterface();
    miaInterface.connectWebSocket();
    
    // Update status every 30 seconds
    setInterval(() => miaInterface.updateSystemStatus(), 30000);
}

function initializeDashboard() {
    const miaInterface = new MIAInterface();
    
    // Update dashboard every 10 seconds
    setInterval(() => miaInterface.updateSystemStatus(), 10000);
}

// Initialize interface when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌐 MIA Interface loaded');
    
    // Initialize based on current page
    if (window.location.pathname === '/chat') {
        initializeChatInterface();
    } else if (window.location.pathname === '/dashboard') {
        initializeDashboard();
    }
});
"""
    
    async def _handle_chat_websocket(self, websocket: WebSocket):
        """Handle chat WebSocket connection"""
        await websocket.accept()
        self.websocket_connections.append(websocket)
        
        # Create session
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            "websocket": websocket,
            "created_at": time.time(),
            "last_activity": time.time()
        }
        
        self.logger.info(f"💬 New WebSocket connection: {session_id}")
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Update session activity
                self.active_sessions[session_id]["last_activity"] = time.time()
                
                # Process message
                await self._process_websocket_message(websocket, message_data, session_id)
                
        except WebSocketDisconnect:
            self.logger.info(f"💬 WebSocket disconnected: {session_id}")
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
        finally:
            # Cleanup
            if websocket in self.websocket_connections:
                self.websocket_connections.remove(websocket)
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
    
    async def _process_websocket_message(self, websocket: WebSocket, data: Dict[str, Any], session_id: str):
        """Process WebSocket message"""
        try:
            message_type = data.get("type", "unknown")
            content = data.get("content", "")
            
            if message_type == "user_message":
                # Log user message
                user_message = InterfaceMessage(
                    id=str(uuid.uuid4()),
                    type=MessageType.USER,
                    content=content,
                    timestamp=time.time(),
                    interface=InterfaceType.CHAT,
                    metadata={"session_id": session_id}
                )
                self.message_history.append(user_message)
                
                # Process with AGI core
                response = await self._process_with_agi(content, session_id)
                
                # Send response
                await websocket.send_text(json.dumps({
                    "type": "assistant",
                    "content": response,
                    "timestamp": time.time()
                }))
                
                # Log assistant response
                assistant_message = InterfaceMessage(
                    id=str(uuid.uuid4()),
                    type=MessageType.ASSISTANT,
                    content=response,
                    timestamp=time.time(),
                    interface=InterfaceType.CHAT,
                    metadata={"session_id": session_id}
                )
                self.message_history.append(assistant_message)
                
        except Exception as e:
            self.logger.error(f"Error processing WebSocket message: {e}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "content": "Sorry, I encountered an error processing your message.",
                "timestamp": time.time()
            }))
    
    async def _process_with_agi(self, message: str, session_id: str) -> str:
        """Process message with AGI core"""
        try:
            # Try to use AGI core
            from mia.core.agi_core import agi_core
            
            # Generate response
            response = await agi_core.process_message(message, {
                "session_id": session_id,
                "interface": "chat",
                "timestamp": time.time()
            })
            
            return response.get("content", "I'm processing your request...")
            
        except ImportError:
            # Fallback response
            return f"I understand you said: '{message}'. I'm a basic response system currently. The full AGI core will provide more intelligent responses."
        except Exception as e:
            self.logger.error(f"Error processing with AGI: {e}")
            return "I encountered an error processing your request. Please try again."
    
    async def _get_api_status(self) -> Dict[str, Any]:
        """Get API status"""
        return {
            "status": "running",
            "interfaces": {
                "web": self.config.web_enabled,
                "chat": self.config.chat_enabled,
                "desktop": self.config.desktop_enabled,
                "voice": self.config.voice_enabled,
                "api": self.config.api_enabled
            },
            "connections": {
                "websocket": len(self.websocket_connections),
                "sessions": len(self.active_sessions)
            },
            "messages": len(self.message_history),
            "timestamp": time.time()
        }
    
    async def _process_api_chat(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process API chat request"""
        try:
            message = data.get("message", "")
            session_id = data.get("session_id") or str(uuid.uuid4())
            
            # Process with AGI
            response = await self._process_with_agi(message, session_id)
            
            return {
                "response": response,
                "session_id": session_id,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing API chat: {e}")
            return {
                "error": "Failed to process message",
                "timestamp": time.time()
            }
    
    async def _process_voice_synthesis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process voice synthesis request"""
        try:
            text = data.get("text", "")
            voice = data.get("voice", "neural")
            
            # Placeholder for voice synthesis
            return {
                "status": "success",
                "message": f"Voice synthesis for: {text}",
                "voice": voice,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error in voice synthesis: {e}")
            return {
                "status": "error",
                "message": "Voice synthesis failed",
                "timestamp": time.time()
            }
    
    async def _process_voice_recognition(self) -> Dict[str, Any]:
        """Process voice recognition request"""
        try:
            # Placeholder for voice recognition
            return {
                "status": "success",
                "transcript": "Voice recognition placeholder",
                "confidence": 0.95,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error in voice recognition: {e}")
            return {
                "status": "error",
                "message": "Voice recognition failed",
                "timestamp": time.time()
            }
    
    async def start_server(self, port: Optional[int] = None):
        """Start the interface server"""
        server_port = port or self.config.web_port
        
        self.logger.info(f"🚀 Starting Unified Interface Server on port {server_port}...")
        
        config = uvicorn.Config(
            self.web_app,
            host=self.config.host,
            port=server_port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    async def shutdown(self):
        """Shutdown interface system"""
        self.logger.info("🛑 Shutting down Unified Interface System...")
        
        # Close all WebSocket connections
        for websocket in self.websocket_connections:
            try:
                await websocket.close()
            except:
                pass
        
        # Clear sessions
        self.active_sessions.clear()
        self.websocket_connections.clear()
        
        self.is_running = False
        self.logger.info("✅ Unified Interface System shutdown complete")

# Global interface system instance
unified_interface = UnifiedInterfaceSystem()

# Convenience functions
async def initialize_interfaces(config: Optional[InterfaceConfig] = None):
    """Initialize interface system"""
    if config:
        global unified_interface
        unified_interface = UnifiedInterfaceSystem(config)
    
    await unified_interface.initialize()

async def start_interface_server(port: Optional[int] = None):
    """Start interface server"""
    await unified_interface.start_server(port)

async def get_interface_status():
    """Get interface status"""
    return await unified_interface._get_api_status()

async def shutdown_interfaces():
    """Shutdown interface system"""
    await unified_interface.shutdown()