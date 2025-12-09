#!/usr/bin/env python3
"""
🌐 MIA Web Interface - FastAPI Web Server
Web interface za MIA AGI sistem z avatarjem
"""

import os
import sys
import json
import time
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Import MIA systems
from mia_production_core import MIACore
from mia_voice_system import MIAVoiceSystem
from mia_multimodal_system import MIAMultimodalSystem
from mia_project_system import MIAProjectSystem


class ChatMessage(BaseModel):
    """Chat message model"""
    message: str
    user_id: str = "user"
    timestamp: Optional[str] = None


class GenerationRequest(BaseModel):
    """Content generation request"""
    prompt: str
    modality: str
    style: str = "default"
    quality: str = "medium"
    adult_mode: bool = False


class ProjectRequest(BaseModel):
    """Project creation request"""
    name: str
    description: str
    project_type: str
    requirements: List[str]
    features: List[str]
    technologies: List[str] = []


class MIAWebInterface:
    """MIA Web Interface Server"""
    
    def __init__(self, data_path: str = "mia_data"):
        self.data_path = Path(data_path)
        self.logger = self._setup_logging()
        
        # Initialize MIA systems
        self.mia_core = MIACore(str(self.data_path))
        self.voice_system = MIAVoiceSystem(self.data_path)
        self.multimodal_system = MIAMultimodalSystem(self.data_path)
        self.project_system = MIAProjectSystem(self.data_path)
        
        # FastAPI app
        self.app = FastAPI(
            title="MIA - Lokalna Digitalna Inteligentna Entiteta",
            description="Web interface za MIA AGI sistem",
            version="1.0.0"
        )
        
        # Setup static files and templates
        self._setup_static_files()
        self._setup_routes()
        
        # WebSocket connections
        self.active_connections: List[WebSocket] = []
        
        self.logger.info("🌐 MIA Web Interface initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup web interface logging"""
        logger = logging.getLogger("MIA.WebInterface")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - MIA.WebInterface - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _setup_static_files(self):
        """Setup static files and templates"""
        # Create static and templates directories
        static_dir = Path("static")
        templates_dir = Path("templates")
        static_dir.mkdir(exist_ok=True)
        templates_dir.mkdir(exist_ok=True)
        
        # Create HTML template
        self._create_html_template(templates_dir)
        self._create_css_styles(static_dir)
        self._create_javascript(static_dir)
        
        # Mount static files
        self.app.mount("/static", StaticFiles(directory="static"), name="static")
        self.templates = Jinja2Templates(directory="templates")
    
    def _create_html_template(self, templates_dir: Path):
        """Create main HTML template"""
        html_content = '''<!DOCTYPE html>
<html lang="sl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIA - Lokalna Digitalna Inteligentna Entiteta</title>
    <link href="/static/styles.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div id="app">
        <!-- Header -->
        <header class="header">
            <div class="header-content">
                <h1><i class="fas fa-brain"></i> MIA</h1>
                <div class="status-indicator">
                    <span id="status-dot" class="status-dot online"></span>
                    <span id="status-text">Online</span>
                </div>
            </div>
        </header>

        <!-- Main Container -->
        <div class="main-container">
            <!-- Sidebar -->
            <aside class="sidebar">
                <nav class="nav-menu">
                    <button class="nav-item active" data-tab="chat">
                        <i class="fas fa-comments"></i> Chat
                    </button>
                    <button class="nav-item" data-tab="avatar">
                        <i class="fas fa-user-circle"></i> Avatar
                    </button>
                    <button class="nav-item" data-tab="multimodal">
                        <i class="fas fa-magic"></i> Generacija
                    </button>
                    <button class="nav-item" data-tab="projects">
                        <i class="fas fa-project-diagram"></i> Projekti
                    </button>
                    <button class="nav-item" data-tab="memory">
                        <i class="fas fa-database"></i> Spomin
                    </button>
                    <button class="nav-item" data-tab="settings">
                        <i class="fas fa-cog"></i> Nastavitve
                    </button>
                </nav>
                
                <!-- Mode Switcher -->
                <div class="mode-switcher">
                    <button id="developer-mode" class="mode-btn">
                        <i class="fas fa-code"></i> Razvijalec
                    </button>
                    <button id="adult-mode" class="mode-btn adult">
                        <i class="fas fa-unlock"></i> 18+
                    </button>
                    <button id="training-mode" class="mode-btn">
                        <i class="fas fa-graduation-cap"></i> Trening
                    </button>
                </div>
            </aside>

            <!-- Content Area -->
            <main class="content">
                <!-- Chat Tab -->
                <div id="chat-tab" class="tab-content active">
                    <div class="chat-container">
                        <div id="chat-messages" class="chat-messages"></div>
                        <div class="chat-input-container">
                            <input type="text" id="chat-input" placeholder="Pogovorite se z MIA..." />
                            <button id="send-btn"><i class="fas fa-paper-plane"></i></button>
                            <button id="voice-btn"><i class="fas fa-microphone"></i></button>
                        </div>
                    </div>
                </div>

                <!-- Avatar Tab -->
                <div id="avatar-tab" class="tab-content">
                    <div class="avatar-container">
                        <div id="avatar-display" class="avatar-display">
                            <div class="avatar-placeholder">
                                <i class="fas fa-user-circle"></i>
                                <p>MIA Avatar</p>
                            </div>
                        </div>
                        <div class="avatar-controls">
                            <button class="avatar-btn" data-emotion="neutral">😐 Nevtralno</button>
                            <button class="avatar-btn" data-emotion="happy">😊 Veselo</button>
                            <button class="avatar-btn" data-emotion="sad">😢 Žalostno</button>
                            <button class="avatar-btn" data-emotion="excited">🤩 Vznemirjeno</button>
                        </div>
                    </div>
                </div>

                <!-- Multimodal Tab -->
                <div id="multimodal-tab" class="tab-content">
                    <div class="generation-container">
                        <div class="generation-form">
                            <h3>Generacija vsebine</h3>
                            <input type="text" id="generation-prompt" placeholder="Opišite kaj želite generirati..." />
                            <div class="generation-options">
                                <select id="generation-modality">
                                    <option value="image">🎨 Slika</option>
                                    <option value="video">🎬 Video</option>
                                    <option value="audio">🎵 Zvok</option>
                                </select>
                                <select id="generation-style">
                                    <option value="default">Privzeto</option>
                                    <option value="artistic">Umetniško</option>
                                    <option value="photorealistic">Fotorealistično</option>
                                    <option value="anime">Anime</option>
                                </select>
                                <select id="generation-quality">
                                    <option value="medium">Srednja</option>
                                    <option value="low">Nizka</option>
                                    <option value="high">Visoka</option>
                                </select>
                            </div>
                            <button id="generate-btn">Generiraj</button>
                        </div>
                        <div id="generation-results" class="generation-results"></div>
                    </div>
                </div>

                <!-- Projects Tab -->
                <div id="projects-tab" class="tab-content">
                    <div class="projects-container">
                        <div class="project-form">
                            <h3>Ustvari nov projekt</h3>
                            <input type="text" id="project-name" placeholder="Ime projekta" />
                            <textarea id="project-description" placeholder="Opis projekta"></textarea>
                            <select id="project-type">
                                <option value="web_app">Spletna aplikacija</option>
                                <option value="api_service">API storitev</option>
                                <option value="desktop_app">Namizna aplikacija</option>
                                <option value="cli_tool">CLI orodje</option>
                                <option value="library">Knjižnica</option>
                            </select>
                            <textarea id="project-features" placeholder="Funkcionalnosti (ena na vrstico)"></textarea>
                            <button id="create-project-btn">Ustvari projekt</button>
                        </div>
                        <div id="projects-list" class="projects-list"></div>
                    </div>
                </div>

                <!-- Memory Tab -->
                <div id="memory-tab" class="tab-content">
                    <div class="memory-container">
                        <div class="memory-stats" id="memory-stats"></div>
                        <div class="memory-search">
                            <input type="text" id="memory-search" placeholder="Iskanje po spominu..." />
                            <button id="search-memory-btn">Išči</button>
                        </div>
                        <div id="memory-results" class="memory-results"></div>
                    </div>
                </div>

                <!-- Settings Tab -->
                <div id="settings-tab" class="tab-content">
                    <div class="settings-container">
                        <h3>Nastavitve</h3>
                        <div class="setting-group">
                            <label>Glasovni profil:</label>
                            <select id="voice-profile">
                                <option value="default">Privzeti</option>
                                <option value="professional">Profesionalni</option>
                                <option value="empathetic">Empatičen</option>
                                <option value="playful">Igriv</option>
                            </select>
                        </div>
                        <div class="setting-group">
                            <label>Hitrost govora:</label>
                            <input type="range" id="speech-speed" min="0.5" max="2" step="0.1" value="1" />
                        </div>
                        <div class="setting-group">
                            <label>Glasnost:</label>
                            <input type="range" id="speech-volume" min="0" max="1" step="0.1" value="0.8" />
                        </div>
                        <button id="save-settings-btn">Shrani nastavitve</button>
                    </div>
                </div>
            </main>
        </div>

        <!-- System Status -->
        <div class="system-status">
            <div id="consciousness-level" class="status-item">
                <span>Zavest: </span><span id="consciousness-value">100%</span>
            </div>
            <div id="emotional-state" class="status-item">
                <span>Čustva: </span><span id="emotion-value">nevtralno</span>
            </div>
            <div id="memory-usage" class="status-item">
                <span>Spomin: </span><span id="memory-value">0 MB</span>
            </div>
        </div>
    </div>

    <script src="/static/app.js"></script>
</body>
</html>'''
        
        template_file = templates_dir / "index.html"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _create_css_styles(self, static_dir: Path):
        """Create CSS styles"""
        css_content = '''/* MIA Web Interface Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #333;
    height: 100vh;
    overflow: hidden;
}

#app {
    display: flex;
    flex-direction: column;
    height: 100vh;
}

/* Header */
.header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    padding: 1rem 2rem;
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header h1 {
    color: #667eea;
    font-size: 2rem;
    font-weight: bold;
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #4CAF50;
    animation: pulse 2s infinite;
}

.status-dot.offline {
    background: #f44336;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

/* Main Container */
.main-container {
    display: flex;
    flex: 1;
    overflow: hidden;
}

/* Sidebar */
.sidebar {
    width: 250px;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.nav-menu {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.nav-item {
    padding: 1rem;
    border: none;
    background: transparent;
    text-align: left;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 1rem;
    color: #666;
}

.nav-item:hover {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
}

.nav-item.active {
    background: #667eea;
    color: white;
}

.nav-item i {
    margin-right: 0.5rem;
    width: 20px;
}

/* Mode Switcher */
.mode-switcher {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-top: auto;
}

.mode-btn {
    padding: 0.75rem;
    border: 2px solid #667eea;
    background: transparent;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    color: #667eea;
    font-weight: bold;
}

.mode-btn:hover {
    background: #667eea;
    color: white;
}

.mode-btn.adult {
    border-color: #e91e63;
    color: #e91e63;
}

.mode-btn.adult:hover {
    background: #e91e63;
    color: white;
}

.mode-btn.active {
    background: #667eea;
    color: white;
}

/* Content Area */
.content {
    flex: 1;
    padding: 2rem;
    overflow-y: auto;
}

.tab-content {
    display: none;
    height: 100%;
}

.tab-content.active {
    display: block;
}

/* Chat */
.chat-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    overflow: hidden;
}

.chat-messages {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.message {
    max-width: 70%;
    padding: 1rem;
    border-radius: 15px;
    word-wrap: break-word;
}

.message.user {
    align-self: flex-end;
    background: #667eea;
    color: white;
}

.message.mia {
    align-self: flex-start;
    background: #f5f5f5;
    color: #333;
}

.chat-input-container {
    display: flex;
    padding: 1rem;
    gap: 0.5rem;
    background: rgba(255, 255, 255, 0.5);
}

#chat-input {
    flex: 1;
    padding: 1rem;
    border: 2px solid #ddd;
    border-radius: 25px;
    outline: none;
    font-size: 1rem;
}

#chat-input:focus {
    border-color: #667eea;
}

#send-btn, #voice-btn {
    width: 50px;
    height: 50px;
    border: none;
    border-radius: 50%;
    background: #667eea;
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;
}

#send-btn:hover, #voice-btn:hover {
    background: #5a6fd8;
    transform: scale(1.1);
}

/* Avatar */
.avatar-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
    height: 100%;
}

.avatar-display {
    width: 300px;
    height: 300px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.avatar-placeholder {
    text-align: center;
    color: #667eea;
}

.avatar-placeholder i {
    font-size: 4rem;
    margin-bottom: 1rem;
}

.avatar-controls {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.avatar-btn {
    padding: 0.75rem 1.5rem;
    border: 2px solid #667eea;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 25px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 1rem;
}

.avatar-btn:hover {
    background: #667eea;
    color: white;
}

/* Generation */
.generation-container {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    height: 100%;
}

.generation-form {
    background: rgba(255, 255, 255, 0.9);
    padding: 2rem;
    border-radius: 15px;
}

.generation-form h3 {
    margin-bottom: 1rem;
    color: #667eea;
}

#generation-prompt {
    width: 100%;
    padding: 1rem;
    border: 2px solid #ddd;
    border-radius: 10px;
    margin-bottom: 1rem;
    font-size: 1rem;
}

.generation-options {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
}

.generation-options select {
    flex: 1;
    padding: 0.75rem;
    border: 2px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
}

#generate-btn {
    width: 100%;
    padding: 1rem;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 1.1rem;
    cursor: pointer;
    transition: all 0.3s ease;
}

#generate-btn:hover {
    background: #5a6fd8;
}

.generation-results {
    flex: 1;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    padding: 1rem;
    overflow-y: auto;
}

/* Projects */
.projects-container {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    height: 100%;
}

.project-form {
    background: rgba(255, 255, 255, 0.9);
    padding: 2rem;
    border-radius: 15px;
}

.project-form h3 {
    margin-bottom: 1rem;
    color: #667eea;
}

.project-form input,
.project-form textarea,
.project-form select {
    width: 100%;
    padding: 1rem;
    border: 2px solid #ddd;
    border-radius: 8px;
    margin-bottom: 1rem;
    font-size: 1rem;
    font-family: inherit;
}

.project-form textarea {
    height: 100px;
    resize: vertical;
}

#create-project-btn {
    width: 100%;
    padding: 1rem;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 1.1rem;
    cursor: pointer;
    transition: all 0.3s ease;
}

#create-project-btn:hover {
    background: #5a6fd8;
}

.projects-list {
    flex: 1;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    padding: 1rem;
    overflow-y: auto;
}

/* Memory */
.memory-container {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    height: 100%;
}

.memory-stats {
    background: rgba(255, 255, 255, 0.9);
    padding: 2rem;
    border-radius: 15px;
    display: flex;
    justify-content: space-around;
    text-align: center;
}

.memory-search {
    display: flex;
    gap: 1rem;
}

#memory-search {
    flex: 1;
    padding: 1rem;
    border: 2px solid #ddd;
    border-radius: 10px;
    font-size: 1rem;
}

#search-memory-btn {
    padding: 1rem 2rem;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s ease;
}

#search-memory-btn:hover {
    background: #5a6fd8;
}

.memory-results {
    flex: 1;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    padding: 1rem;
    overflow-y: auto;
}

/* Settings */
.settings-container {
    background: rgba(255, 255, 255, 0.9);
    padding: 2rem;
    border-radius: 15px;
    max-width: 600px;
}

.settings-container h3 {
    margin-bottom: 2rem;
    color: #667eea;
}

.setting-group {
    margin-bottom: 2rem;
}

.setting-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: bold;
    color: #333;
}

.setting-group select,
.setting-group input {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
}

#save-settings-btn {
    width: 100%;
    padding: 1rem;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 1.1rem;
    cursor: pointer;
    transition: all 0.3s ease;
}

#save-settings-btn:hover {
    background: #5a6fd8;
}

/* System Status */
.system-status {
    background: rgba(255, 255, 255, 0.9);
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-around;
    font-size: 0.9rem;
}

.status-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
    .main-container {
        flex-direction: column;
    }
    
    .sidebar {
        width: 100%;
        height: auto;
        flex-direction: row;
        overflow-x: auto;
    }
    
    .nav-menu {
        flex-direction: row;
        gap: 1rem;
    }
    
    .mode-switcher {
        flex-direction: row;
        margin-top: 0;
        margin-left: auto;
    }
}

/* Loading Animation */
.loading {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(102, 126, 234, 0.3);
    border-radius: 50%;
    border-top-color: #667eea;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Notification */
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 2rem;
    background: #4CAF50;
    color: white;
    border-radius: 10px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    animation: slideIn 0.3s ease;
}

.notification.error {
    background: #f44336;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}'''
        
        css_file = static_dir / "styles.css"
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css_content)
    
    def _create_javascript(self, static_dir: Path):
        """Create JavaScript application"""
        js_content = '''// MIA Web Interface JavaScript
class MIAWebApp {
    constructor() {
        this.ws = null;
        this.currentTab = 'chat';
        this.isListening = false;
        this.init();
    }

    init() {
        this.setupWebSocket();
        this.setupEventListeners();
        this.setupTabs();
        this.loadSystemStatus();
        
        // Load initial data
        this.loadMemoryStats();
        this.loadProjects();
    }

    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.updateStatus('online');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.updateStatus('offline');
            // Reconnect after 3 seconds
            setTimeout(() => this.setupWebSocket(), 3000);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateStatus('offline');
        };
    }

    setupEventListeners() {
        // Chat
        document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        document.getElementById('send-btn').addEventListener('click', () => {
            this.sendMessage();
        });
        
        document.getElementById('voice-btn').addEventListener('click', () => {
            this.toggleVoiceInput();
        });

        // Mode buttons
        document.getElementById('developer-mode').addEventListener('click', () => {
            this.setMode('developer');
        });
        
        document.getElementById('adult-mode').addEventListener('click', () => {
            this.setMode('adult_18plus');
        });
        
        document.getElementById('training-mode').addEventListener('click', () => {
            this.setMode('training');
        });

        // Generation
        document.getElementById('generate-btn').addEventListener('click', () => {
            this.generateContent();
        });

        // Projects
        document.getElementById('create-project-btn').addEventListener('click', () => {
            this.createProject();
        });

        // Memory
        document.getElementById('search-memory-btn').addEventListener('click', () => {
            this.searchMemory();
        });

        // Settings
        document.getElementById('save-settings-btn').addEventListener('click', () => {
            this.saveSettings();
        });

        // Avatar emotions
        document.querySelectorAll('.avatar-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const emotion = e.target.dataset.emotion;
                this.setAvatarEmotion(emotion);
            });
        });
    }

    setupTabs() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }

    switchTab(tabName) {
        // Update nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        this.currentTab = tabName;
    }

    updateStatus(status) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        if (status === 'online') {
            statusDot.classList.remove('offline');
            statusText.textContent = 'Online';
        } else {
            statusDot.classList.add('offline');
            statusText.textContent = 'Offline';
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'chat_response':
                this.addMessage(data.message, 'mia');
                break;
            case 'system_status':
                this.updateSystemStatus(data.status);
                break;
            case 'generation_result':
                this.displayGenerationResult(data.result);
                break;
            case 'project_update':
                this.updateProjectStatus(data.project);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        this.addMessage(message, 'user');
        input.value = '';
        
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'chat',
                message: message
            }));
        }
    }

    addMessage(message, sender) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        messageDiv.textContent = message;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    toggleVoiceInput() {
        const voiceBtn = document.getElementById('voice-btn');
        
        if (this.isListening) {
            this.stopListening();
            voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceBtn.style.background = '#667eea';
        } else {
            this.startListening();
            voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
            voiceBtn.style.background = '#f44336';
        }
        
        this.isListening = !this.isListening;
    }

    startListening() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'start_voice_input'
            }));
        }
    }

    stopListening() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'stop_voice_input'
            }));
        }
    }

    setMode(mode) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'set_mode',
                mode: mode
            }));
        }
        
        // Update UI
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        if (mode === 'developer') {
            document.getElementById('developer-mode').classList.add('active');
        } else if (mode === 'adult_18plus') {
            document.getElementById('adult-mode').classList.add('active');
        } else if (mode === 'training') {
            document.getElementById('training-mode').classList.add('active');
        }
        
        this.showNotification(`Aktiviran ${mode} način`, 'success');
    }

    generateContent() {
        const prompt = document.getElementById('generation-prompt').value.trim();
        const modality = document.getElementById('generation-modality').value;
        const style = document.getElementById('generation-style').value;
        const quality = document.getElementById('generation-quality').value;
        
        if (!prompt) {
            this.showNotification('Vnesite opis za generacijo', 'error');
            return;
        }
        
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'generate_content',
                prompt: prompt,
                modality: modality,
                style: style,
                quality: quality
            }));
        }
        
        // Show loading
        const resultsDiv = document.getElementById('generation-results');
        resultsDiv.innerHTML = '<div class="loading"></div> Generiranje...';
    }

    displayGenerationResult(result) {
        const resultsDiv = document.getElementById('generation-results');
        
        if (result.success) {
            const resultPath = result.path;
            const modality = result.modality;
            
            let content = '';
            if (modality === 'image') {
                content = `<img src="/generated/images/${resultPath}" alt="Generated image" style="max-width: 100%; border-radius: 10px;">`;
            } else if (modality === 'video') {
                content = `<video controls style="max-width: 100%; border-radius: 10px;"><source src="/generated/videos/${resultPath}" type="video/mp4"></video>`;
            } else if (modality === 'audio') {
                content = `<audio controls style="width: 100%;"><source src="/generated/audio/${resultPath}" type="audio/wav"></audio>`;
            }
            
            resultsDiv.innerHTML = content;
        } else {
            resultsDiv.innerHTML = `<p style="color: #f44336;">Napaka: ${result.error}</p>`;
        }
    }

    createProject() {
        const name = document.getElementById('project-name').value.trim();
        const description = document.getElementById('project-description').value.trim();
        const projectType = document.getElementById('project-type').value;
        const features = document.getElementById('project-features').value.trim().split('\\n').filter(f => f.trim());
        
        if (!name || !description || features.length === 0) {
            this.showNotification('Izpolnite vsa polja', 'error');
            return;
        }
        
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'create_project',
                name: name,
                description: description,
                project_type: projectType,
                features: features,
                requirements: ['Basic functionality'],
                technologies: []
            }));
        }
        
        // Clear form
        document.getElementById('project-name').value = '';
        document.getElementById('project-description').value = '';
        document.getElementById('project-features').value = '';
    }

    updateProjectStatus(project) {
        this.loadProjects(); // Reload projects list
        this.showNotification(`Projekt ${project.name}: ${project.status}`, 'success');
    }

    async loadProjects() {
        try {
            const response = await fetch('/api/projects');
            const projects = await response.json();
            
            const projectsList = document.getElementById('projects-list');
            projectsList.innerHTML = '';
            
            projects.forEach(project => {
                const projectDiv = document.createElement('div');
                projectDiv.style.cssText = 'background: #f5f5f5; padding: 1rem; margin-bottom: 1rem; border-radius: 10px;';
                projectDiv.innerHTML = `
                    <h4>${project.name}</h4>
                    <p>Status: ${project.status}</p>
                    <p>Naloge: ${project.tasks_completed}/${project.tasks_total}</p>
                    <small>Ustvarjen: ${new Date(project.created_at * 1000).toLocaleString()}</small>
                `;
                projectsList.appendChild(projectDiv);
            });
        } catch (error) {
            console.error('Error loading projects:', error);
        }
    }

    searchMemory() {
        const query = document.getElementById('memory-search').value.trim();
        
        if (!query) {
            this.showNotification('Vnesite iskalni pojem', 'error');
            return;
        }
        
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'search_memory',
                query: query
            }));
        }
    }

    async loadMemoryStats() {
        try {
            const response = await fetch('/api/memory/stats');
            const stats = await response.json();
            
            const statsDiv = document.getElementById('memory-stats');
            statsDiv.innerHTML = `
                <div>
                    <h4>${stats.short_term_count}</h4>
                    <p>Kratkoročni</p>
                </div>
                <div>
                    <h4>${stats.medium_term_count}</h4>
                    <p>Srednjeročni</p>
                </div>
                <div>
                    <h4>${stats.long_term_count}</h4>
                    <p>Dolgoročni</p>
                </div>
                <div>
                    <h4>${stats.permanent_count}</h4>
                    <p>Trajni</p>
                </div>
            `;
        } catch (error) {
            console.error('Error loading memory stats:', error);
        }
    }

    async loadSystemStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            this.updateSystemStatus(status);
        } catch (error) {
            console.error('Error loading system status:', error);
        }
    }

    updateSystemStatus(status) {
        document.getElementById('consciousness-value').textContent = 
            Math.round(status.consciousness.consciousness_level * 100) + '%';
        document.getElementById('emotion-value').textContent = 
            status.consciousness.emotional_state;
        document.getElementById('memory-value').textContent = 
            Math.round(status.memory_stats.short_term_count * 0.1) + ' MB';
    }

    setAvatarEmotion(emotion) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'set_avatar_emotion',
                emotion: emotion
            }));
        }
        
        this.showNotification(`Avatar čustvo: ${emotion}`, 'success');
    }

    saveSettings() {
        const voiceProfile = document.getElementById('voice-profile').value;
        const speechSpeed = document.getElementById('speech-speed').value;
        const speechVolume = document.getElementById('speech-volume').value;
        
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'save_settings',
                settings: {
                    voice_profile: voiceProfile,
                    speech_speed: parseFloat(speechSpeed),
                    speech_volume: parseFloat(speechVolume)
                }
            }));
        }
        
        this.showNotification('Nastavitve shranjene', 'success');
    }

    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.classList.add('notification');
        if (type === 'error') {
            notification.classList.add('error');
        }
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MIAWebApp();
});'''
        
        js_file = static_dir / "app.js"
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            return self.templates.TemplateResponse("index.html", {"request": request})
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.handle_websocket(websocket)
        
        @self.app.post("/api/chat")
        async def chat_endpoint(message: ChatMessage):
            return await self.handle_chat(message)
        
        @self.app.post("/api/generate")
        async def generate_endpoint(request: GenerationRequest):
            return await self.handle_generation(request)
        
        @self.app.post("/api/projects")
        async def create_project_endpoint(request: ProjectRequest):
            return await self.handle_project_creation(request)
        
        @self.app.get("/api/projects")
        async def list_projects_endpoint():
            return self.project_system.list_projects()
        
        @self.app.get("/api/memory/stats")
        async def memory_stats_endpoint():
            return self.mia_core.memory.get_memory_stats()
        
        @self.app.get("/api/status")
        async def status_endpoint():
            return self.mia_core.get_system_status()
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    
    async def handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connections"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await self.process_websocket_message(websocket, message)
                
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
    
    async def process_websocket_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Process WebSocket message"""
        message_type = message.get("type")
        
        if message_type == "chat":
            response = self.mia_core.interact(message["message"])
            await websocket.send_text(json.dumps({
                "type": "chat_response",
                "message": response
            }))
        
        elif message_type == "set_mode":
            mode = message["mode"]
            if mode == "developer":
                self.mia_core.interact("razvijalec mia")
            elif mode == "adult_18plus":
                self.mia_core.interact("mia 18+")
            elif mode == "training":
                self.mia_core.interact("mia, treniraj")
        
        elif message_type == "generate_content":
            result = self.multimodal_system.generate(
                message["prompt"],
                message["modality"],
                message["style"],
                message["quality"]
            )
            
            await websocket.send_text(json.dumps({
                "type": "generation_result",
                "result": {
                    "success": result is not None,
                    "path": result if result else None,
                    "modality": message["modality"],
                    "error": "Generation failed" if not result else None
                }
            }))
        
        elif message_type == "create_project":
            project_id = self.project_system.create_project(
                message["name"],
                message["description"],
                message["project_type"],
                message["requirements"],
                message["features"],
                message["technologies"]
            )
            
            # Start building project in background
            asyncio.create_task(self.build_project_async(project_id, websocket))
        
        elif message_type == "search_memory":
            results = self.mia_core.memory.search_memories(message["query"])
            await websocket.send_text(json.dumps({
                "type": "memory_results",
                "results": results
            }))
    
    async def build_project_async(self, project_id: str, websocket: WebSocket):
        """Build project asynchronously"""
        try:
            result = self.project_system.build_project(project_id)
            
            await websocket.send_text(json.dumps({
                "type": "project_update",
                "project": {
                    "id": project_id,
                    "name": result.get("name", "Unknown"),
                    "status": "completed" if result["success"] else "failed"
                }
            }))
        except Exception as e:
            self.logger.error(f"Project build error: {e}")
            await websocket.send_text(json.dumps({
                "type": "project_update",
                "project": {
                    "id": project_id,
                    "status": "failed",
                    "error": str(e)
                }
            }))
    
    async def handle_chat(self, message: ChatMessage) -> Dict[str, Any]:
        """Handle chat API endpoint"""
        try:
            response = self.mia_core.interact(message.message, message.user_id)
            return {"success": True, "response": response}
        except Exception as e:
            self.logger.error(f"Chat error: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_generation(self, request: GenerationRequest) -> Dict[str, Any]:
        """Handle generation API endpoint"""
        try:
            result = self.multimodal_system.generate(
                request.prompt,
                request.modality,
                request.style,
                request.quality,
                request.adult_mode
            )
            
            return {
                "success": result is not None,
                "path": result,
                "modality": request.modality
            }
        except Exception as e:
            self.logger.error(f"Generation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_project_creation(self, request: ProjectRequest) -> Dict[str, Any]:
        """Handle project creation API endpoint"""
        try:
            project_id = self.project_system.create_project(
                request.name,
                request.description,
                request.project_type,
                request.requirements,
                request.features,
                request.technologies
            )
            
            return {"success": True, "project_id": project_id}
        except Exception as e:
            self.logger.error(f"Project creation error: {e}")
            return {"success": False, "error": str(e)}
    
    def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the web server"""
        # Start MIA core
        self.mia_core.start()
        
        self.logger.info(f"🌐 Starting MIA Web Interface on http://{host}:{port}")
        
        # Run server
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )


def main():
    """Main function"""
    print("🌐 MIA Web Interface")
    print("=" * 25)
    
    # Initialize web interface
    web_interface = MIAWebInterface()
    
    try:
        # Start server
        web_interface.start_server()
    except KeyboardInterrupt:
        print("\n👋 MIA Web Interface stopped")
    finally:
        web_interface.mia_core.stop()


if __name__ == "__main__":
    main()