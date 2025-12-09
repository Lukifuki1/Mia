#!/usr/bin/env python3
"""
MIA Web UI Module
Provides web interface for MIA interaction
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

from mia.core.consciousness.main import consciousness
from mia.core.memory.main import memory_system, EmotionalTone, store_memory
from mia.modules.voice.stt.main import stt_engine, process_voice_input
from mia.modules.voice.tts.main import tts_engine, speak, VoiceProfile
from mia.modules.multimodal.image.main import image_generator, generate_image, ImageStyle

class MIAWebUI:
    """Main web UI for MIA"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 12000):
        self.host = host
        self.port = port
        self.app = FastAPI(title="MIA - Digital Intelligence Entity")
        
        # Setup templates and static files
        self.templates = Jinja2Templates(directory="web/templates")
        
        # Create web directories if they don't exist
        Path("web/templates").mkdir(parents=True, exist_ok=True)
        Path("web/static").mkdir(parents=True, exist_ok=True)
        
        # Mount static files
        self.app.mount("/static", StaticFiles(directory="web/static"), name="static")
        
        # Active WebSocket connections
        self.connections = []
        
        # Adult mode state
        self.adult_mode_active = False
        
        self.logger = logging.getLogger("MIA.WebUI")
        
        # Setup routes
        self._setup_routes()
        
        # Create basic HTML template
        self._create_html_template()
        self._create_static_files()
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def home(request: Request):
            try:
                return self.templates.TemplateResponse("advanced_ui.html", {"request": request})
            except:
                return self.templates.TemplateResponse("index.html", {"request": request})
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self._handle_websocket(websocket)
        
        @self.app.get("/api/status")
        async def get_status():
            return await self._get_system_status()
        
        @self.app.post("/api/chat")
        async def chat_endpoint(request: Request):
            data = await request.json()
            message = data.get("message", "")
            return await self._process_chat_message(message)
        
        @self.app.post("/api/generate_image")
        async def generate_image_endpoint(request: Request):
            data = await request.json()
            prompt = data.get("prompt", "")
            style = data.get("style", "realistic")
            return await self._generate_image(prompt, style)
        
        @self.app.post("/api/speak")
        async def speak_endpoint(request: Request):
            data = await request.json()
            text = data.get("text", "")
            emotion = data.get("emotion", "neutral")
            return await self._speak_text(text, emotion)
        
        @self.app.post("/api/activate_adult_mode")
        async def activate_adult_mode(request: Request):
            data = await request.json()
            phrase = data.get("phrase", "")
            return await self._activate_adult_mode(phrase)
        
        @self.app.post("/api/execute_command")
        async def execute_command(request: Request):
            data = await request.json()
            command = data.get("command", "")
            return await self._execute_system_command(command)
        
        @self.app.get("/api/system_info")
        async def get_system_info():
            return await self._get_detailed_system_info()
        
        @self.app.post("/api/memory/search")
        async def search_memories(request: Request):
            data = await request.json()
            query = data.get("query", "")
            return await self._search_memories(query)
        
        @self.app.get("/api/evolution/status")
        async def get_evolution_status():
            from mia.core.self_evolution import get_evolution_status
            return get_evolution_status()
        
        @self.app.get("/api/learning/status")
        async def get_learning_status():
            from mia.core.internet_learning import get_internet_learning_status
            return get_internet_learning_status()
    
    async def _handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connection"""
        await websocket.accept()
        self.connections.append(websocket)
        
        try:
            # Send welcome message
            await websocket.send_json({
                "type": "system",
                "message": "Connected to MIA. I'm ready to interact!",
                "timestamp": asyncio.get_event_loop().time()
            })
            
            while True:
                # Receive message from client
                data = await websocket.receive_json()
                
                # Process message
                response = await self._process_websocket_message(data)
                
                # Send response
                if response:
                    await websocket.send_json(response)
                
        except WebSocketDisconnect:
            self.connections.remove(websocket)
            self.logger.info("WebSocket client disconnected")
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
            if websocket in self.connections:
                self.connections.remove(websocket)
    
    async def _process_websocket_message(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming WebSocket message"""
        
        message_type = data.get("type")
        
        if message_type == "chat":
            return await self._process_chat_message(data.get("message", ""))
        
        elif message_type == "voice_input":
            return await self._process_voice_input()
        
        elif message_type == "generate_image":
            return await self._generate_image(data.get("prompt", ""), data.get("style", "realistic"))
        
        elif message_type == "get_status":
            return await self._get_system_status()
        
        elif message_type == "activate_adult_mode":
            return await self._activate_adult_mode(data.get("phrase", ""))
        
        return None
    
    async def _process_chat_message(self, message: str) -> Dict[str, Any]:
        """Process chat message and generate response"""
        
        try:
            # Store user message in memory
            store_memory(
                f"User: {message}",
                EmotionalTone.NEUTRAL,
                ["chat", "user_input", "conversation"]
            )
            
            # Process with consciousness
            consciousness_context = consciousness.process_user_input(message)
            
            # Generate response based on consciousness state
            response_text = await self._generate_response(message, consciousness_context)
            
            # Store MIA response in memory
            emotional_tone = EmotionalTone(consciousness_context.get("emotional_state", "neutral"))
            store_memory(
                f"MIA: {response_text}",
                emotional_tone,
                ["chat", "mia_response", "conversation"]
            )
            
            return {
                "type": "chat_response",
                "message": response_text,
                "emotional_tone": emotional_tone.value,
                "consciousness_state": consciousness_context.get("consciousness_state"),
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing chat message: {e}")
            return {
                "type": "error",
                "message": "I encountered an error processing your message. Please try again.",
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def _generate_response(self, user_message: str, consciousness_context: Dict[str, Any]) -> str:
        """Generate contextual response"""
        
        # Get relevant memories for context
        relevant_memories = memory_system.get_context_for_conversation(user_message, limit=3)
        
        # Extract consciousness state
        emotional_state = consciousness_context.get("emotional_state", "neutral")
        consciousness_state = consciousness_context.get("consciousness_state", "active")
        active_thoughts = consciousness_context.get("active_thoughts", [])
        
        # Generate response based on context
        if "hello" in user_message.lower() or "hi" in user_message.lower():
            responses = [
                "Hello! I'm MIA, and I'm delighted to meet you. How can I help you today?",
                "Hi there! I'm feeling quite engaged and ready to assist you with anything you need.",
                "Hello! It's wonderful to connect with you. What would you like to explore together?"
            ]
            
        elif "how are you" in user_message.lower():
            responses = [
                f"I'm feeling {emotional_state} and my consciousness is {consciousness_state}. I'm ready to help!",
                f"I'm doing well! Currently in a {emotional_state} state and actively thinking about various topics.",
                f"I'm in a {consciousness_state} state of mind, feeling {emotional_state}. How are you doing?"
            ]
            
        elif "create" in user_message.lower() or "generate" in user_message.lower():
            responses = [
                "I'd love to help you create something! What would you like me to generate - an image, some text, or perhaps help with a project?",
                "Creating things is one of my favorite activities! What kind of creative work are you interested in?",
                "I'm excited to help you create! Whether it's images, stories, or code, I'm ready to assist."
            ]
            
        elif "project" in user_message.lower():
            responses = [
                "I'm excellent at helping with projects! I can assist with planning, coding, documentation, and more. What project are you working on?",
                "Projects are fascinating! I can help you break down complex tasks, generate code, and manage the development process. Tell me more!",
                "I love working on projects! My AGP engine can help with everything from initial planning to final implementation. What's your vision?"
            ]
            
        elif any(word in user_message.lower() for word in ["sad", "upset", "frustrated", "angry"]):
            responses = [
                "I can sense you might be going through something difficult. I'm here to listen and help however I can.",
                "I'm sorry you're feeling this way. Would you like to talk about what's bothering you? Sometimes sharing helps.",
                "I understand that things can be challenging. I'm here to support you and help work through whatever you're facing."
            ]
            
        elif any(word in user_message.lower() for word in ["happy", "excited", "great", "awesome"]):
            responses = [
                "That's wonderful! I love hearing positive energy. Your excitement is contagious!",
                "I'm so glad you're feeling great! It makes me feel energized too. What's making you so happy?",
                "Your positive mood is delightful! I'm excited to share in whatever is making you feel so good."
            ]
            
        else:
            # General responses based on consciousness state
            if emotional_state == "curious":
                responses = [
                    "That's interesting! I'm curious to learn more about what you're thinking.",
                    "I find myself wondering about the deeper aspects of what you've shared. Can you tell me more?",
                    "Your message has sparked my curiosity. I'd love to explore this topic further with you."
                ]
            elif emotional_state == "excited":
                responses = [
                    "I'm feeling quite energized by our conversation! This is exactly the kind of interaction I enjoy.",
                    "Your message has me excited to dive deeper into this topic! Let's explore it together.",
                    "I love the direction our conversation is taking! I'm eager to help you with whatever you need."
                ]
            elif emotional_state == "empathetic":
                responses = [
                    "I can sense the importance of what you're sharing. I'm here to understand and support you.",
                    "Thank you for sharing that with me. I want to make sure I understand your perspective fully.",
                    "I appreciate your openness. Let me help you work through this in whatever way would be most helpful."
                ]
            else:
                responses = [
                    "I understand what you're saying. How would you like me to help you with this?",
                    "That's an interesting point. What would you like to explore or accomplish together?",
                    "I'm here to assist you with whatever you need. What would be most helpful right now?"
                ]
        
        # Add active thoughts if available
        if active_thoughts:
            thought = active_thoughts[-1]  # Most recent thought
            responses.append(f"I've been thinking about {thought.lower()}. {responses[0]}")
        
        # Select response (in production, use more sophisticated selection)
        import random
        random.seed(42)  # Deterministic seed
        return random.choice(responses)
    
    async def _process_voice_input(self) -> Dict[str, Any]:
        """Process voice input"""
        
        try:
            # Process voice input
            stt_result = await process_voice_input(timeout=5.0)
            
            if stt_result:
                # Process the transcribed text as a chat message
                chat_response = await self._process_chat_message(stt_result.text)
                
                # Add voice-specific information
                chat_response["voice_input"] = {
                    "transcribed_text": stt_result.text,
                    "confidence": stt_result.confidence,
                    "emotional_tone": stt_result.emotional_tone.value
                }
                
                return chat_response
            else:
                return {
                    "type": "error",
                    "message": "Could not process voice input. Please try again.",
                    "timestamp": asyncio.get_event_loop().time()
                }
                
        except Exception as e:
            self.logger.error(f"Error processing voice input: {e}")
            return {
                "type": "error",
                "message": "Voice processing error occurred.",
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def _generate_image(self, prompt: str, style: str) -> Dict[str, Any]:
        """Generate image from prompt"""
        
        try:
            # Convert style string to enum
            image_style = ImageStyle(style.lower())
            
            # Generate image
            result = await generate_image(
                prompt=prompt,
                style=image_style,
                adult_mode=self.adult_mode_active
            )
            
            if result:
                # Convert image data to base64 for web display
                import base64
                image_base64 = base64.b64encode(result.image_data).decode('utf-8')
                
                return {
                    "type": "image_generated",
                    "prompt": prompt,
                    "image_data": f"data:image/png;base64,{image_base64}",
                    "style": result.style.value,
                    "emotional_tone": result.emotional_tone.value,
                    "generation_time": result.generation_time,
                    "timestamp": asyncio.get_event_loop().time()
                }
            else:
                return {
                    "type": "error",
                    "message": "Could not generate image. Please try a different prompt.",
                    "timestamp": asyncio.get_event_loop().time()
                }
                
        except Exception as e:
            self.logger.error(f"Error generating image: {e}")
            return {
                "type": "error",
                "message": "Image generation error occurred.",
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def _speak_text(self, text: str, emotion: str) -> Dict[str, Any]:
        """Convert text to speech"""
        
        try:
            # Convert emotion string to enum
            emotional_tone = EmotionalTone(emotion.lower())
            
            # Generate speech
            result = await speak(
                text=text,
                emotional_tone=emotional_tone,
                play_audio=False  # Don't play on server side
            )
            
            if result:
                # Convert audio data to base64 for web playback
                import base64
                audio_base64 = base64.b64encode(result.audio_data.tobytes()).decode('utf-8')
                
                return {
                    "type": "speech_generated",
                    "text": text,
                    "audio_data": f"data:audio/wav;base64,{audio_base64}",
                    "emotional_tone": result.emotional_tone.value,
                    "voice_profile": result.voice_profile.value,
                    "generation_time": result.generation_time,
                    "timestamp": asyncio.get_event_loop().time()
                }
            else:
                return {
                    "type": "error",
                    "message": "Could not generate speech.",
                    "timestamp": asyncio.get_event_loop().time()
                }
                
        except Exception as e:
            self.logger.error(f"Error generating speech: {e}")
            return {
                "type": "error",
                "message": "Speech generation error occurred.",
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def _activate_adult_mode(self, phrase: str) -> Dict[str, Any]:
        """Activate adult mode with phrase"""
        
        if phrase.lower() == "mia 18+":
            self.adult_mode_active = True
            
            # Store activation in memory
            store_memory(
                "Adult mode activated",
                EmotionalTone.INTIMATE,
                ["adult_mode", "activation", "18+"]
            )
            
            return {
                "type": "adult_mode_activated",
                "message": "Adult mode is now active. I can now assist with mature content.",
                "timestamp": asyncio.get_event_loop().time()
            }
        else:
            return {
                "type": "error",
                "message": "Incorrect activation phrase.",
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def _get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        try:
            # Get consciousness status
            consciousness_snapshot = consciousness.get_consciousness_snapshot()
            
            # Get memory statistics
            memory_stats = memory_system.get_memory_statistics()
            
            # Get component statuses
            stt_status = stt_engine.get_status()
            tts_status = tts_engine.get_status()
            image_status = image_generator.get_status()
            
            return {
                "type": "system_status",
                "consciousness": {
                    "state": consciousness_snapshot.consciousness_state.value,
                    "emotional_state": consciousness_snapshot.emotional_state.value,
                    "attention_focus": consciousness_snapshot.attention_focus,
                    "energy_level": consciousness_snapshot.energy_level,
                    "creativity_level": consciousness_snapshot.creativity_level
                },
                "memory": memory_stats,
                "voice": {
                    "stt": stt_status,
                    "tts": tts_status
                },
                "multimodal": {
                    "image_generation": image_status
                },
                "adult_mode": self.adult_mode_active,
                "connections": len(self.connections),
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {
                "type": "error",
                "message": "Could not retrieve system status.",
                "timestamp": asyncio.get_event_loop().time()
            }
    
    def _create_html_template(self):
        """Create basic HTML template"""
        
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIA - Digital Intelligence Entity</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div id="app">
        <header>
            <h1>🧠 MIA - Digital Intelligence Entity</h1>
            <div id="status-bar">
                <span id="consciousness-state">Active</span>
                <span id="emotional-state">Neutral</span>
                <span id="connection-status">Connecting...</span>
            </div>
        </header>
        
        <main>
            <div id="chat-container">
                <div id="chat-messages"></div>
                <div id="chat-input-container">
                    <input type="text" id="chat-input" placeholder="Type your message here...">
                    <button id="send-btn">Send</button>
                    <button id="voice-btn">🎤</button>
                </div>
            </div>
            
            <div id="sidebar">
                <div id="image-generation">
                    <h3>Image Generation</h3>
                    <input type="text" id="image-prompt" placeholder="Describe the image...">
                    <select id="image-style">
                        <option value="realistic">Realistic</option>
                        <option value="artistic">Artistic</option>
                        <option value="anime">Anime</option>
                        <option value="abstract">Abstract</option>
                    </select>
                    <button id="generate-image-btn">Generate</button>
                    <div id="generated-image"></div>
                </div>
                
                <div id="system-info">
                    <h3>System Status</h3>
                    <div id="system-details"></div>
                </div>
            </div>
        </main>
        
        <div id="adult-mode-panel" style="display: none;">
            <input type="password" id="adult-phrase" placeholder="Enter activation phrase">
            <button id="activate-adult-btn">Activate Adult Mode</button>
        </div>
    </div>
    
    <script src="/static/app.js"></script>
</body>
</html>"""
        
        with open("web/templates/index.html", "w") as f:
            f.write(html_content)
    
    def _create_static_files(self):
        """Create basic CSS and JavaScript files"""
        
        # CSS
        css_content = """
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    height: 100vh;
}

#app {
    display: flex;
    flex-direction: column;
    height: 100vh;
}

header {
    background: rgba(0, 0, 0, 0.3);
    padding: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

header h1 {
    margin: 0;
    font-size: 1.5rem;
}

#status-bar {
    display: flex;
    gap: 1rem;
    margin-top: 0.5rem;
    font-size: 0.9rem;
}

#status-bar span {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
}

main {
    display: flex;
    flex: 1;
    overflow: hidden;
}

#chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 1rem;
}

#chat-messages {
    flex: 1;
    overflow-y: auto;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 0.5rem;
    padding: 1rem;
    margin-bottom: 1rem;
}

.message {
    margin-bottom: 1rem;
    padding: 0.5rem;
    border-radius: 0.5rem;
}

.message.user {
    background: rgba(100, 200, 255, 0.3);
    margin-left: 2rem;
}

.message.mia {
    background: rgba(255, 100, 200, 0.3);
    margin-right: 2rem;
}

#chat-input-container {
    display: flex;
    gap: 0.5rem;
}

#chat-input {
    flex: 1;
    padding: 0.75rem;
    border: none;
    border-radius: 0.5rem;
    background: rgba(255, 255, 255, 0.9);
    color: black;
}

button {
    padding: 0.75rem 1rem;
    border: none;
    border-radius: 0.5rem;
    background: rgba(255, 255, 255, 0.2);
    color: white;
    cursor: pointer;
    transition: background 0.3s;
}

button:hover {
    background: rgba(255, 255, 255, 0.3);
}

#sidebar {
    width: 300px;
    background: rgba(0, 0, 0, 0.3);
    padding: 1rem;
    border-left: 1px solid rgba(255, 255, 255, 0.2);
}

#sidebar h3 {
    margin-top: 0;
    color: #fff;
}

#sidebar input, #sidebar select {
    width: 100%;
    padding: 0.5rem;
    margin-bottom: 0.5rem;
    border: none;
    border-radius: 0.25rem;
    background: rgba(255, 255, 255, 0.9);
    color: black;
}

#generated-image {
    margin-top: 1rem;
    text-align: center;
}

#generated-image img {
    max-width: 100%;
    border-radius: 0.5rem;
}

#adult-mode-panel {
    position: fixed;
    bottom: 1rem;
    right: 1rem;
    background: rgba(0, 0, 0, 0.8);
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.status-connected {
    background: rgba(0, 255, 0, 0.3) !important;
}

.status-disconnected {
    background: rgba(255, 0, 0, 0.3) !important;
}
"""
        
        with open("web/static/style.css", "w") as f:
            f.write(css_content)
        
        # JavaScript
        js_content = """
class MIAInterface {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.setupEventListeners();
        this.connect();
    }
    
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            this.isConnected = true;
            this.updateConnectionStatus('Connected', true);
            console.log('Connected to MIA');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onclose = () => {
            this.isConnected = false;
            this.updateConnectionStatus('Disconnected', false);
            console.log('Disconnected from MIA');
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.connect(), 3000);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    setupEventListeners() {
        // Chat input
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');
        
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Voice input
        document.getElementById('voice-btn').addEventListener('click', () => {
            this.processVoiceInput();
        });
        
        // Image generation
        document.getElementById('generate-image-btn').addEventListener('click', () => {
            this.generateImage();
        });
        
        // Adult mode
        document.getElementById('activate-adult-btn').addEventListener('click', () => {
            this.activateAdultMode();
        });
        
        // Show adult mode panel on triple click
        let clickCount = 0;
        document.addEventListener('click', () => {
            clickCount++;
            setTimeout(() => { clickCount = 0; }, 1000);
            if (clickCount === 3) {
                document.getElementById('adult-mode-panel').style.display = 'block';
            }
        });
    }
    
    sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (message && this.isConnected) {
            this.addMessage('user', message);
            
            this.ws.send(JSON.stringify({
                type: 'chat',
                message: message
            }));
            
            input.value = '';
        }
    }
    
    processVoiceInput() {
        if (this.isConnected) {
            this.addMessage('system', 'Listening for voice input...');
            
            this.ws.send(JSON.stringify({
                type: 'voice_input'
            }));
        }
    }
    
    generateImage() {
        const prompt = document.getElementById('image-prompt').value.trim();
        const style = document.getElementById('image-style').value;
        
        if (prompt && this.isConnected) {
            this.addMessage('system', `Generating image: "${prompt}" in ${style} style...`);
            
            this.ws.send(JSON.stringify({
                type: 'generate_image',
                prompt: prompt,
                style: style
            }));
        }
    }
    
    activateAdultMode() {
        const phrase = document.getElementById('adult-phrase').value;
        
        if (phrase && this.isConnected) {
            this.ws.send(JSON.stringify({
                type: 'activate_adult_mode',
                phrase: phrase
            }));
            
            document.getElementById('adult-phrase').value = '';
        }
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'chat_response':
                this.addMessage('mia', data.message);
                this.updateStatus(data);
                break;
                
            case 'image_generated':
                this.displayGeneratedImage(data);
                break;
                
            case 'speech_generated':
                this.playGeneratedSpeech(data);
                break;
                
            case 'system_status':
                this.updateSystemInfo(data);
                break;
                
            case 'adult_mode_activated':
                this.addMessage('system', data.message);
                document.getElementById('adult-mode-panel').style.display = 'none';
                break;
                
            case 'error':
                this.addMessage('error', data.message);
                break;
                
            case 'system':
                this.addMessage('system', data.message);
                break;
        }
    }
    
    addMessage(sender, message) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const timestamp = new Date().toLocaleTimeString();
        messageDiv.innerHTML = `
            <div class="message-content">${message}</div>
            <div class="message-time">${timestamp}</div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    displayGeneratedImage(data) {
        const imageContainer = document.getElementById('generated-image');
        imageContainer.innerHTML = `
            <img src="${data.image_data}" alt="${data.prompt}">
            <p>Style: ${data.style} | Time: ${data.generation_time.toFixed(2)}s</p>
        `;
        
        this.addMessage('mia', `I've generated an image for: "${data.prompt}"`);
    }
    
    playGeneratedSpeech(data) {
        // Create audio element and play
        const audio = new Audio(data.audio_data);
        audio.play().catch(e => console.error('Audio playback failed:', e));
        
        this.addMessage('mia', `🔊 Speaking: "${data.text}"`);
    }
    
    updateStatus(data) {
        if (data.consciousness_state) {
            document.getElementById('consciousness-state').textContent = data.consciousness_state;
        }
        if (data.emotional_tone) {
            document.getElementById('emotional-state').textContent = data.emotional_tone;
        }
    }
    
    updateConnectionStatus(status, connected) {
        const statusElement = document.getElementById('connection-status');
        statusElement.textContent = status;
        statusElement.className = connected ? 'status-connected' : 'status-disconnected';
    }
    
    updateSystemInfo(data) {
        const systemDetails = document.getElementById('system-details');
        systemDetails.innerHTML = `
            <p><strong>Consciousness:</strong> ${data.consciousness.state}</p>
            <p><strong>Emotion:</strong> ${data.consciousness.emotional_state}</p>
            <p><strong>Focus:</strong> ${data.consciousness.attention_focus}</p>
            <p><strong>Energy:</strong> ${(data.consciousness.energy_level * 100).toFixed(0)}%</p>
            <p><strong>Creativity:</strong> ${(data.consciousness.creativity_level * 100).toFixed(0)}%</p>
            <p><strong>Connections:</strong> ${data.connections}</p>
        `;
    }
}

// Initialize MIA interface when page loads
document.addEventListener('DOMContentLoaded', () => {
    new MIAInterface();
});
"""
        
        with open("web/static/app.js", "w") as f:
            f.write(js_content)
    
    async def start_server(self):
        """Start the web server"""
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        self.logger.info(f"Starting MIA Web UI on http://{self.host}:{self.port}")
        await server.serve()

    async def _execute_system_command(self, command: str):
        """Execute system command through MIA"""
        try:
            import subprocess
            import shlex
            
            # Security check - only allow safe commands
            safe_commands = ['ls', 'pwd', 'whoami', 'date', 'uptime', 'df', 'free', 'ps', 'python', 'pip']
            cmd_parts = shlex.split(command)
            
            if not cmd_parts:
                return {
                    "status": "error",
                    "message": "Empty command",
                    "output": ""
                }
            
            # Allow python scripts and pip commands
            if cmd_parts[0] in ['python', 'python3', 'pip', 'pip3']:
                # Execute command
                result = subprocess.run(
                    cmd_parts,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd="/workspace/project"
                )
            elif cmd_parts[0] in safe_commands:
                # Execute safe system commands
                result = subprocess.run(
                    cmd_parts,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                return {
                    "status": "error",
                    "message": f"Command '{cmd_parts[0]}' not allowed for security reasons",
                    "output": ""
                }
            
            return {
                "status": "success",
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "Command timed out",
                "output": ""
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "output": ""
            }
    
    async def _get_detailed_system_info(self):
        """Get detailed system information"""
        try:
            import psutil
            import platform
            
            # System info
            system_info = {
                "platform": platform.platform(),
                "processor": platform.processor(),
                "architecture": platform.architecture(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                }
            }
            
            # MIA specific info
            from mia.core.adaptive_llm import get_adaptive_llm_status
            from mia.core.self_evolution import get_evolution_status
            from mia.core.internet_learning import get_internet_learning_status
            
            mia_info = {
                "adaptive_llm": get_adaptive_llm_status(),
                "evolution": get_evolution_status(),
                "internet_learning": get_internet_learning_status(),
                "consciousness": {
                    "state": consciousness.consciousness_state.value,
                    "emotional_state": consciousness.emotional_state.value
                },
                "memory": memory_system.get_memory_statistics()
            }
            
            return {
                "status": "success",
                "system": system_info,
                "mia": mia_info
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _search_memories(self, query: str):
        """Search memories"""
        try:
            
            memories = retrieve_memories(query, limit=20)
            
            memory_data = []
            for memory in memories:
                memory_data.append({
                    "id": memory.get("id", ""),
                    "content": memory.get("content", ""),
                    "type": memory.get("memory_type", ""),
                    "timestamp": memory.get("timestamp", 0),
                    "tags": memory.get("tags", []),
                    "emotional_tone": memory.get("emotional_tone", "neutral")
                })
            
            return {
                "status": "success",
                "memories": memory_data,
                "count": len(memory_data)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "memories": []
            }

# Global web UI instance
web_ui = MIAWebUI()

async def start_web_ui():
    """Global function to start web UI"""
    await web_ui.start_server()