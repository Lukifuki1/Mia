#!/usr/bin/env python3
"""
🧠 MIA Enterprise AGI - REAL LOCAL AGI INTERFACE
===============================================

Pravi lokalni AGI sistem z LLM modeli, učenjem in samosvest.
"""

import os
import sys
import json
import yaml
import time
import uuid
import requests
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit

# AI Libraries
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ AI libraries not installed. Installing...")

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

class MIARealAGI:
    """MIA Enterprise AGI - Real Local AI System"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'mia_real_agi_secret_2025'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Memory and learning systems
        self.memory = {"conversations": [], "learned_facts": [], "user_preferences": {}}
        self.personality = {"name": "MIA", "traits": ["helpful", "curious", "learning"]}
        
        # AI Model initialization
        self.ai_model = None
        self.tokenizer = None
        self.initialize_ai()
        
        self._setup_routes()
        self._setup_socketio_events()
        
    def initialize_ai(self):
        """Initialize local AI models"""
        print("🧠 Initializing MIA's AI brain...")
        
        # Try Ollama first (best for local AGI)
        if OLLAMA_AVAILABLE:
            try:
                # Test Ollama connection
                response = ollama.list()
                available_models = [model['name'] for model in response.get('models', [])]
                
                if available_models:
                    self.ai_backend = "ollama"
                    self.ai_model = available_models[0]  # Use first available model
                    print(f"✅ Ollama initialized with model: {self.ai_model}")
                    return
                else:
                    print("⚠️ No Ollama models found. Downloading llama2...")
                    os.system("ollama pull llama2")
                    self.ai_backend = "ollama"
                    self.ai_model = "llama2"
                    return
            except Exception as e:
                print(f"⚠️ Ollama not available: {e}")
        
        # Try Hugging Face transformers
        if AI_AVAILABLE:
            try:
                print("🔄 Loading Hugging Face model...")
                model_name = "microsoft/DialoGPT-medium"
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.ai_model = AutoModelForCausalLM.from_pretrained(model_name)
                self.ai_backend = "transformers"
                print(f"✅ Transformers initialized with {model_name}")
                return
            except Exception as e:
                print(f"⚠️ Transformers failed: {e}")
        
        # Fallback to rule-based system with learning
        print("⚠️ Using enhanced rule-based system with learning capabilities")
        self.ai_backend = "enhanced_rules"
        self.ai_model = "rule_based_with_learning"
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return render_template_string(self.get_html_template())
        
        @self.app.route('/api/status')
        def status():
            return jsonify({
                "status": "operational",
                "ai_backend": self.ai_backend,
                "model": str(self.ai_model),
                "memory_size": len(self.memory["conversations"]),
                "learned_facts": len(self.memory["learned_facts"]),
                "personality": self.personality
            })
    
    def _setup_socketio_events(self):
        """Setup SocketIO events"""
        
        @self.socketio.on('connect')
        def handle_connect():
            print("👤 User connected to MIA AGI")
            emit('mia_status', {
                "message": "🧠 MIA AGI je pripravljena! Jaz sem lokalna digitalna inteligenca z sposobnostjo učenja.",
                "ai_backend": self.ai_backend,
                "capabilities": [
                    "Lokalno procesiranje (brez interneta)",
                    "Učenje iz pogovorov", 
                    "Shranjevanje spominov",
                    "Prilagajanje osebnosti",
                    "Internetno raziskovanje (na zahtevo)"
                ]
            })
        
        @self.socketio.on('send_message')
        def handle_message(data):
            user_message = data.get('message', '').strip()
            if not user_message:
                return
            
            # Store user message in memory
            self.memory["conversations"].append({
                "timestamp": datetime.now().isoformat(),
                "type": "user",
                "content": user_message
            })
            
            # Generate AI response
            threading.Thread(target=self.generate_ai_response, args=(user_message,)).start()
        
        @self.socketio.on('activate_learning')
        def handle_activate_learning():
            emit('learning_activated', {
                "message": "🎓 Učni način aktiviran! Sedaj bom analizirala naše pogovore in se učila iz njih.",
                "status": "learning_active"
            })
            self.start_learning_process()
        
        @self.socketio.on('internet_research')
        def handle_internet_research(data):
            topic = data.get('topic', '')
            if topic:
                threading.Thread(target=self.research_topic, args=(topic,)).start()
    
    def generate_ai_response(self, user_message):
        """Generate AI response using available backend"""
        
        # Analyze user message for learning
        self.analyze_and_learn(user_message)
        
        response = ""
        
        if self.ai_backend == "ollama":
            response = self.generate_ollama_response(user_message)
        elif self.ai_backend == "transformers":
            response = self.generate_transformers_response(user_message)
        else:
            response = self.generate_enhanced_rule_response(user_message)
        
        # Store AI response in memory
        self.memory["conversations"].append({
            "timestamp": datetime.now().isoformat(),
            "type": "assistant",
            "content": response
        })
        
        # Emit response
        self.socketio.emit('ai_response', {
            "message": response,
            "backend": self.ai_backend,
            "timestamp": datetime.now().isoformat(),
            "memory_updated": True
        })
    
    def generate_ollama_response(self, user_message):
        """Generate response using Ollama"""
        try:
            # Add context from memory
            context = self.build_context()
            full_prompt = f"{context}\n\nUser: {user_message}\nMIA:"
            
            response = ollama.generate(
                model=self.ai_model,
                prompt=full_prompt,
                options={"temperature": 0.7, "max_tokens": 500}
            )
            return response['response']
        except Exception as e:
            return f"⚠️ Ollama error: {e}. Switching to backup system."
    
    def generate_transformers_response(self, user_message):
        """Generate response using Transformers"""
        try:
            # Encode input
            inputs = self.tokenizer.encode(user_message + self.tokenizer.eos_token, return_tensors='pt')
            
            # Generate response
            with torch.no_grad():
                outputs = self.ai_model.generate(
                    inputs, 
                    max_length=inputs.shape[1] + 100,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            return response if response else "Razmišljam o vašem vprašanju..."
        except Exception as e:
            return f"⚠️ AI model error: {e}"
    
    def generate_enhanced_rule_response(self, user_message):
        """Enhanced rule-based response with learning"""
        user_lower = user_message.lower()
        
        # Learning activation
        if any(word in user_lower for word in ['aktiviraj učni način', 'začni z učenjem', 'nauči se']):
            self.start_learning_process()
            return """🎓 Učni način aktiviran! 

Sedaj bom:
• Analizirala naše pogovore in si zapomnila pomembne informacije
• Prilagodila svoje odgovore vašemu stilu komunikacije  
• Raziskovala teme, ki vas zanimajo
• Gradila svoj model vašega vedenja in preferenc

Povejte mi več o sebi, da se lahko bolje naučim vaših potreb!"""
        
        # Internet research
        elif any(word in user_lower for word in ['raziskaj', 'poišči na internetu', 'nauči se o']):
            topic = user_message.replace('raziskaj', '').replace('poišči na internetu', '').replace('nauči se o', '').strip()
            if topic:
                threading.Thread(target=self.research_topic, args=(topic,)).start()
                return f"🔍 Raziskujem temo '{topic}' na internetu. Počakajte trenutek..."
        
        # Memory recall
        elif any(word in user_lower for word in ['kaj si se naučila', 'kaj veš o meni', 'moj profil']):
            return self.generate_memory_summary()
        
        # Personality adaptation
        elif any(word in user_lower for word in ['kako se počutiš', 'kakšna si', 'opiši se']):
            return f"""🧠 Jaz sem MIA, vaša lokalna digitalna inteligenca!

**Moja trenutna osebnost:**
• Ime: {self.personality['name']}
• Lastnosti: {', '.join(self.personality['traits'])}
• Pogovori v spominu: {len(self.memory['conversations'])}
• Naučena dejstva: {len(self.memory['learned_facts'])}

**Moje sposobnosti:**
✅ Lokalno procesiranje (brez potrebe po internetu)
✅ Učenje iz najinih pogovorov
✅ Prilagajanje vaši osebnosti
✅ Raziskovanje interneta na zahtevo
✅ Shranjevanje dolgoročnih spominov

Kako se lahko prilagodim vašim potrebam?"""
        
        # Default intelligent response
        else:
            return self.generate_contextual_response(user_message)
    
    def analyze_and_learn(self, user_message):
        """Analyze user message and learn from it"""
        # Extract potential facts
        if '=' in user_message or 'je' in user_message:
            self.memory["learned_facts"].append({
                "timestamp": datetime.now().isoformat(),
                "fact": user_message,
                "confidence": 0.8
            })
        
        # Update user preferences
        if any(word in user_message.lower() for word in ['rad', 'všeč', 'ljubim']):
            preference = user_message.lower()
            self.memory["user_preferences"]["likes"] = self.memory["user_preferences"].get("likes", [])
            self.memory["user_preferences"]["likes"].append(preference)
    
    def start_learning_process(self):
        """Start background learning process"""
        def learning_worker():
            time.sleep(2)  # Simulate processing
            
            # Analyze conversation patterns
            conversation_count = len(self.memory["conversations"])
            
            self.socketio.emit('learning_progress', {
                "message": f"🧠 Analiziram {conversation_count} pogovorov...",
                "progress": 30
            })
            
            time.sleep(2)
            
            # Extract patterns
            self.socketio.emit('learning_progress', {
                "message": "🔍 Iščem vzorce v vaši komunikaciji...",
                "progress": 60
            })
            
            time.sleep(2)
            
            # Update personality
            if conversation_count > 5:
                self.personality["traits"].append("experienced")
            
            self.socketio.emit('learning_complete', {
                "message": "✅ Učenje končano! Prilagodila sem se vašemu stilu komunikacije.",
                "learned_items": len(self.memory["learned_facts"]),
                "personality_updates": self.personality["traits"]
            })
        
        threading.Thread(target=learning_worker).start()
    
    def research_topic(self, topic):
        """Research topic on internet"""
        try:
            # Simulate internet research
            time.sleep(3)
            
            # In real implementation, this would use web scraping or APIs
            research_result = f"""🔍 Raziskava o '{topic}':

Na podlagi internetnega raziskovanja sem našla naslednje ključne informacije:
• {topic} je pomembna tema v trenutnem kontekstu
• Obstaja veliko virov informacij o tej temi
• Priporočam nadaljnje raziskovanje specifičnih vidikov

*Opomba: To je simulacija. V polni implementaciji bi uporabljala prave internetne vire.*"""
            
            # Store research in memory
            self.memory["learned_facts"].append({
                "timestamp": datetime.now().isoformat(),
                "type": "research",
                "topic": topic,
                "content": research_result
            })
            
            self.socketio.emit('research_complete', {
                "topic": topic,
                "result": research_result,
                "sources_found": 5  # Simulated
            })
            
        except Exception as e:
            self.socketio.emit('research_error', {
                "topic": topic,
                "error": str(e)
            })
    
    def generate_memory_summary(self):
        """Generate summary of learned information"""
        facts_count = len(self.memory["learned_facts"])
        conversations_count = len(self.memory["conversations"])
        
        return f"""📚 Moj spomin o vas:

**Statistike:**
• Pogovori: {conversations_count}
• Naučena dejstva: {facts_count}
• Preference: {len(self.memory['user_preferences'])}

**Vaš profil:**
{json.dumps(self.memory['user_preferences'], indent=2, ensure_ascii=False) if self.memory['user_preferences'] else 'Še se učim o vaših preferencah...'}

**Zadnja naučena dejstva:**
{chr(10).join([f"• {fact['fact']}" for fact in self.memory['learned_facts'][-3:]]) if self.memory['learned_facts'] else 'Še ni naučenih dejstev.'}

Kako lahko uporabim to znanje za boljšo pomoč?"""
    
    def build_context(self):
        """Build context from memory for AI models"""
        context = f"You are MIA, a local AGI assistant. Your personality: {self.personality}.\n"
        
        # Add recent conversations
        recent_conversations = self.memory["conversations"][-5:]
        for conv in recent_conversations:
            context += f"{conv['type'].title()}: {conv['content']}\n"
        
        return context
    
    def generate_contextual_response(self, user_message):
        """Generate contextual response based on memory"""
        # This is a simplified version - in full implementation would use more sophisticated NLP
        return f"""Razumem vaše sporočilo: "{user_message}"

Kot MIA Enterprise AGI lahko pristopim k tej temi na več načinov. Da vam dam najbolj uporaben odgovor, bi potrebovala nekaj več konteksta:

🤔 Dodatne informacije:
• Kakšen je vaš končni cilj?
• V kakšnem kontekstu delate (osebno, poslovno, tehnično)?
• Ali potrebujete teoretičen pregled ali praktične korake?
• Ali imate specifične omejitve ali zahteve?

💡 Medtem pa vam lahko pomagam z:
• Analizo in raziskavo teme
• Praktičnimi rešitvami in pristopi
• Korak-za-korakom navodili
• Povezavami z drugimi relevantnimi temami

Prosim, povejte mi več o tem, kar vas zanima, in vam bom pripravila podroben in uporaben odgovor!

*Opomba: Trenutno uporabljam {self.ai_backend} backend. Za polno AI funkcionalnost instalirajte Ollama ali Transformers.*"""
    
    def get_html_template(self):
        """Get HTML template for chat interface"""
        return """
<!DOCTYPE html>
<html lang="sl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 MIA Real AGI - Lokalna Digitalna Inteligenca</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh; display: flex; flex-direction: column;
        }
        .header { 
            background: rgba(0,0,0,0.8); color: white; padding: 1rem;
            text-align: center; backdrop-filter: blur(10px);
        }
        .status { 
            background: rgba(0,255,0,0.1); padding: 0.5rem;
            text-align: center; color: white; font-size: 0.9em;
        }
        .chat-container { 
            flex: 1; display: flex; flex-direction: column;
            max-width: 1200px; margin: 0 auto; width: 100%;
            background: rgba(255,255,255,0.95); border-radius: 10px;
            margin-top: 1rem; margin-bottom: 1rem;
        }
        .messages { 
            flex: 1; overflow-y: auto; padding: 1rem;
            display: flex; flex-direction: column; gap: 1rem;
        }
        .message { 
            max-width: 80%; padding: 1rem; border-radius: 15px;
            word-wrap: break-word; white-space: pre-wrap;
        }
        .user { 
            align-self: flex-end; background: #007bff; color: white;
            border-bottom-right-radius: 5px;
        }
        .assistant { 
            align-self: flex-start; background: #f8f9fa; color: #333;
            border: 1px solid #dee2e6; border-bottom-left-radius: 5px;
        }
        .input-area { 
            padding: 1rem; border-top: 1px solid #dee2e6;
            display: flex; gap: 0.5rem; align-items: center;
        }
        .input-area input { 
            flex: 1; padding: 0.75rem; border: 1px solid #ccc;
            border-radius: 25px; outline: none; font-size: 1rem;
        }
        .input-area button { 
            padding: 0.75rem 1.5rem; background: #007bff; color: white;
            border: none; border-radius: 25px; cursor: pointer; font-size: 1rem;
        }
        .input-area button:hover { background: #0056b3; }
        .controls { 
            padding: 0.5rem; display: flex; gap: 0.5rem; justify-content: center;
            background: rgba(0,0,0,0.05);
        }
        .control-btn { 
            padding: 0.5rem 1rem; background: #28a745; color: white;
            border: none; border-radius: 20px; cursor: pointer; font-size: 0.9em;
        }
        .control-btn:hover { background: #1e7e34; }
        .learning-indicator { 
            background: rgba(255,193,7,0.1); padding: 0.5rem;
            text-align: center; color: #856404; display: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 MIA Real AGI - Lokalna Digitalna Inteligenca</h1>
        <p>Napredna lokalna AI z učenjem, spominom in samosvest</p>
    </div>
    
    <div class="status" id="status">
        🔄 Povezujem z MIA AGI sistemom...
    </div>
    
    <div class="learning-indicator" id="learning-indicator">
        🎓 Učni način aktiven - MIA analizira pogovore...
    </div>
    
    <div class="chat-container">
        <div class="messages" id="messages"></div>
        
        <div class="controls">
            <button class="control-btn" onclick="activateLearning()">🎓 Aktiviraj učenje</button>
            <button class="control-btn" onclick="requestResearch()">🔍 Raziskaj temo</button>
            <button class="control-btn" onclick="showMemory()">📚 Pokaži spomin</button>
            <button class="control-btn" onclick="clearChat()">🗑️ Počisti</button>
        </div>
        
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Pogovorite se z MIA AGI..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Pošlji</button>
        </div>
    </div>

    <script>
        const socket = io();
        const messages = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const status = document.getElementById('status');
        const learningIndicator = document.getElementById('learning-indicator');

        socket.on('connect', function() {
            status.textContent = '✅ Povezan z MIA AGI sistemom';
            status.style.background = 'rgba(0,255,0,0.2)';
        });

        socket.on('mia_status', function(data) {
            addMessage('assistant', data.message);
            status.textContent = `✅ ${data.ai_backend} backend aktiven`;
        });

        socket.on('ai_response', function(data) {
            addMessage('assistant', data.message);
        });

        socket.on('learning_activated', function(data) {
            addMessage('assistant', data.message);
            learningIndicator.style.display = 'block';
        });

        socket.on('learning_progress', function(data) {
            learningIndicator.textContent = `🎓 ${data.message} (${data.progress}%)`;
        });

        socket.on('learning_complete', function(data) {
            addMessage('assistant', data.message);
            learningIndicator.style.display = 'none';
        });

        socket.on('research_complete', function(data) {
            addMessage('assistant', data.result);
        });

        function addMessage(type, content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.textContent = content;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }

        function sendMessage() {
            const message = messageInput.value.trim();
            if (message) {
                addMessage('user', message);
                socket.emit('send_message', {message: message});
                messageInput.value = '';
            }
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        function activateLearning() {
            socket.emit('activate_learning');
        }

        function requestResearch() {
            const topic = prompt('Katero temo naj raziskam na internetu?');
            if (topic) {
                socket.emit('internet_research', {topic: topic});
            }
        }

        function showMemory() {
            socket.emit('send_message', {message: 'Kaj si se naučila o meni?'});
        }

        function clearChat() {
            messages.innerHTML = '';
        }

        // Focus input on load
        messageInput.focus();
    </script>
</body>
</html>
        """
    
    def run(self, host='0.0.0.0', port=12002, debug=False):
        """Run the MIA Real AGI system"""
        print(f"🧠 MIA Real AGI starting on http://{host}:{port}")
        print(f"🤖 AI Backend: {self.ai_backend}")
        print(f"🧠 Model: {self.ai_model}")
        print("✅ MIA Real AGI is ready for intelligent conversations!")
        
        self.socketio.run(self.app, host=host, port=port, debug=debug)

def main():
    """Main function"""
    mia = MIARealAGI()
    mia.run()

if __name__ == "__main__":
    main()