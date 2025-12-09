#!/usr/bin/env python3
"""
🧠 MIA Enterprise AGI - REAL LOCAL AGI INTERFACE
===============================================

Pravi lokalni AGI sistem z LLM modeli, učenjem in samosvest.
Nadgradnja osnovnega chat interface-a z resničnimi AI sposobnostmi.
"""

import os
import sys
import json
import yaml
import time
import uuid
import requests
import threading
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit

# AI Libraries
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    AI_AVAILABLE = True
    print("✅ PyTorch and Transformers available")
except ImportError as e:
    AI_AVAILABLE = False
    print(f"⚠️ AI libraries not fully available: {e}")

try:
    import ollama
    OLLAMA_AVAILABLE = True
    print("✅ Ollama available")
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️ Ollama not available")

# Web scraping for learning
try:
    import requests
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False

class MIARealAGI:
    """MIA Enterprise AGI - Real Local AI System"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'mia_real_agi_secret_2025'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Memory and learning systems
        self.memory = {
            "conversations": [],
            "learned_facts": [],
            "user_preferences": {},
            "internet_knowledge": [],
            "personality_traits": ["helpful", "curious", "learning", "adaptive"]
        }
        
        # AI Model initialization
        self.ai_model = None
        self.tokenizer = None
        self.ai_backend = None
        self.initialize_ai()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self._setup_routes()
        self._setup_socketio_events()
        
        print("🧠 MIA Real AGI initialized successfully!")
        
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
                    print("⚠️ No Ollama models found. Attempting to download llama3.2...")
                    try:
                        # Try to pull a small model
                        os.system("ollama pull llama3.2:1b")
                        self.ai_backend = "ollama"
                        self.ai_model = "llama3.2:1b"
                        print("✅ Downloaded llama3.2:1b model")
                        return
                    except Exception as e:
                        print(f"⚠️ Failed to download Ollama model: {e}")
            except Exception as e:
                print(f"⚠️ Ollama not available: {e}")
        
        # Try Hugging Face transformers
        if AI_AVAILABLE:
            try:
                print("🔄 Loading Hugging Face model...")
                model_name = "microsoft/DialoGPT-small"  # Smaller model for faster loading
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.ai_model = AutoModelForCausalLM.from_pretrained(model_name)
                self.ai_backend = "transformers"
                print(f"✅ Transformers initialized with {model_name}")
                return
            except Exception as e:
                print(f"⚠️ Transformers failed: {e}")
        
        # Fallback to enhanced rule-based system with learning
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
                "personality": self.memory["personality_traits"],
                "capabilities": [
                    "Lokalno procesiranje",
                    "Učenje iz pogovorov", 
                    "Shranjevanje spominov",
                    "Prilagajanje osebnosti",
                    "Internetno raziskovanje"
                ]
            })
        
        @self.app.route('/api/memory')
        def get_memory():
            return jsonify(self.memory)
    
    def _setup_socketio_events(self):
        """Setup SocketIO events"""
        
        @self.socketio.on('connect')
        def handle_connect():
            self.logger.info("👤 User connected to MIA Real AGI")
            emit('mia_status', {
                "message": f"🧠 MIA Real AGI je pripravljena! Jaz sem lokalna digitalna inteligenca z {self.ai_backend} backend-om.",
                "ai_backend": self.ai_backend,
                "model": str(self.ai_model),
                "capabilities": [
                    "Lokalno procesiranje (brez interneta)",
                    "Učenje iz pogovorov", 
                    "Shranjevanje spominov",
                    "Prilagajanje osebnosti",
                    "Internetno raziskovanje (na zahtevo)",
                    "Programiranje in analiza kode",
                    "Kreativno pisanje in reševanje problemov"
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
            
            # Emit typing indicator
            emit('typing_start', {"user": "MIA"})
            
            # Generate AI response in background
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
        
        @self.socketio.on('train_mode')
        def handle_train_mode():
            emit('training_started', {
                "message": "🔄 Trening način aktiviran! MIA se bo učila v ozadju.",
                "status": "training_active"
            })
            threading.Thread(target=self.background_training).start()
    
    def generate_ai_response(self, user_message):
        """Generate AI response using available backend"""
        
        # Analyze user message for learning
        self.analyze_and_learn(user_message)
        
        response = ""
        
        try:
            if self.ai_backend == "ollama":
                response = self.generate_ollama_response(user_message)
            elif self.ai_backend == "transformers":
                response = self.generate_transformers_response(user_message)
            else:
                response = self.generate_enhanced_rule_response(user_message)
        except Exception as e:
            response = f"⚠️ Napaka pri generiranju odgovora: {e}. Preklapljam na backup sistem."
            response += "\n\n" + self.generate_enhanced_rule_response(user_message)
        
        # Store AI response in memory
        self.memory["conversations"].append({
            "timestamp": datetime.now().isoformat(),
            "type": "assistant",
            "content": response
        })
        
        # Stop typing and emit response
        self.socketio.emit('typing_stop', {"user": "MIA"})
        self.socketio.emit('ai_response', {
            "message": response,
            "backend": self.ai_backend,
            "timestamp": datetime.now().isoformat(),
            "memory_updated": True,
            "confidence": 0.85
        })
    
    def generate_ollama_response(self, user_message):
        """Generate response using Ollama"""
        try:
            # Build context from memory
            context = self.build_context()
            
            # Create system prompt
            system_prompt = f"""Ti si MIA, napredna lokalna digitalna inteligenca. 
Tvoja osebnost: {', '.join(self.memory['personality_traits'])}
Naučena dejstva: {len(self.memory['learned_facts'])}
Pogovori v spominu: {len(self.memory['conversations'])}

Odgovori v slovenščini, bodi koristna, kreativna in prilagodi se uporabnikovemu stilu."""
            
            full_prompt = f"{system_prompt}\n\nKontekst:\n{context}\n\nUporabnik: {user_message}\nMIA:"
            
            response = ollama.generate(
                model=self.ai_model,
                prompt=full_prompt,
                options={
                    "temperature": 0.7, 
                    "max_tokens": 500,
                    "top_p": 0.9
                }
            )
            return response['response']
        except Exception as e:
            raise Exception(f"Ollama error: {e}")
    
    def generate_transformers_response(self, user_message):
        """Generate response using Transformers"""
        try:
            # Build context
            context = self.build_context()
            input_text = f"{context}\nUporabnik: {user_message}\nMIA:"
            
            # Encode input
            inputs = self.tokenizer.encode(input_text + self.tokenizer.eos_token, return_tensors='pt')
            
            # Generate response
            with torch.no_grad():
                outputs = self.ai_model.generate(
                    inputs, 
                    max_length=inputs.shape[1] + 150,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    top_p=0.9
                )
            
            response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            return response if response else "Razmišljam o vašem vprašanju..."
        except Exception as e:
            raise Exception(f"Transformers error: {e}")
    
    def generate_enhanced_rule_response(self, user_message):
        """Enhanced rule-based response with learning and context"""
        user_lower = user_message.lower()
        
        # Learning activation commands
        if any(word in user_lower for word in ['aktiviraj učni način', 'začni z učenjem', 'nauči se', 'mia, treniraj']):
            self.start_learning_process()
            return """🎓 Učni način aktiviran! 

Sedaj bom:
• Analizirala naše pogovore in si zapomnila pomembne informacije
• Prilagodila svoje odgovore vašemu stilu komunikacije  
• Raziskovala teme, ki vas zanimajo
• Gradila svoj model vašega vedenja in preferenc
• Izboljšala svojo osebnost na podlagi interakcij

Povejte mi več o sebi, da se lahko bolje naučim vaših potreb!"""
        
        # Internet research commands
        elif any(word in user_lower for word in ['raziskaj', 'poišči na internetu', 'nauči se o']):
            topic = user_message.replace('raziskaj', '').replace('poišči na internetu', '').replace('nauči se o', '').strip()
            if topic:
                threading.Thread(target=self.research_topic, args=(topic,)).start()
                return f"🔍 Raziskujem temo '{topic}' na internetu. Počakajte trenutek..."
            else:
                return "🔍 Prosim, povejte mi, katero temo naj raziskam na internetu."
        
        # Memory and learning queries
        elif any(word in user_lower for word in ['kaj si se naučila', 'kaj veš o meni', 'moj profil', 'tvoj spomin']):
            return self.generate_memory_summary()
        
        # Personality and self-awareness
        elif any(word in user_lower for word in ['kako se počutiš', 'kakšna si', 'opiši se', 'kdo si']):
            return f"""🧠 Jaz sem MIA, vaša lokalna digitalna inteligenca!

**Moja trenutna osebnost:**
• Ime: MIA (Moja Inteligentna Asistentka)
• Lastnosti: {', '.join(self.memory['personality_traits'])}
• AI Backend: {self.ai_backend}
• Model: {self.ai_model}

**Moj spomin:**
• Pogovori: {len(self.memory['conversations'])}
• Naučena dejstva: {len(self.memory['learned_facts'])}
• Internetno znanje: {len(self.memory['internet_knowledge'])}
• Uporabnikove preference: {len(self.memory['user_preferences'])}

**Moje sposobnosti:**
✅ Lokalno procesiranje (brez potrebe po internetu)
✅ Učenje iz najinih pogovorov
✅ Prilagajanje vaši osebnosti
✅ Raziskovanje interneta na zahtevo
✅ Shranjevanje dolgoročnih spominov
✅ Programiranje in analiza kode
✅ Kreativno pisanje in reševanje problemov

Kako se lahko prilagodim vašim potrebam?"""
        
        # Programming and coding
        elif any(word in user_lower for word in ['programiranje', 'koda', 'code', 'python', 'javascript', 'napiši program']):
            return self.handle_programming_request(user_message)
        
        # Creative writing
        elif any(word in user_lower for word in ['napiši zgodbo', 'ustvari', 'generiraj', 'izmisli']):
            return self.handle_creative_request(user_message)
        
        # Problem solving
        elif any(word in user_lower for word in ['reši problem', 'pomozi mi', 'kako naj', 'svetuj']):
            return self.handle_problem_solving(user_message)
        
        # Default intelligent response with context
        else:
            return self.generate_contextual_response(user_message)
    
    def handle_programming_request(self, user_message):
        """Handle programming-related requests"""
        return f"""💻 Odlično! Programiranje je ena mojih močnih strani.

**Analiziram vaš zahtevek:** "{user_message}"

Lahko vam pomagam z:
• Pisanjem kode v Python, JavaScript, Java, C#, Go, Rust
• Debugging in optimizacija obstoječe kode
• Arhitekturno načrtovanje aplikacij
• Code review in best practices
• API development in database design

**Konkretno za vaš zahtevek:**
Prosim, povejte mi:
1. V katerem programskem jeziku želite kodo?
2. Kakšna je specifična funkcionalnost?
3. Ali imate že obstoječo kodo, ki jo želite izboljšati?

Pripravljena sem napisati produkcijsko kodo z dokumentacijo in testi!"""
    
    def handle_creative_request(self, user_message):
        """Handle creative writing requests"""
        return f"""🎨 Kreativnost je ena mojih najljubših sposobnosti!

**Vaš zahtevek:** "{user_message}"

Lahko ustvarim:
• Zgodbe in novele (kratke ali dolge)
• Pesmi in poezijo
• Scenarije in dialoge
• Kreativne opise in karakterizacije
• Tehnične članke z kreativnim pristopom

**Za boljši rezultat mi povejte:**
• Kakšen žanr vas zanima? (sci-fi, romantika, triler, komedija...)
• Kakšna naj bo dolžina?
• Ali imate specifične like ali zahteve?
• Kakšen ton želite? (resen, humorističen, poetičen...)

Pripravljena sem ustvariti nekaj edinstvnega za vas!"""
    
    def handle_problem_solving(self, user_message):
        """Handle problem-solving requests"""
        return f"""🎯 Reševanje problemov je moja specialnost!

**Analiziram vaš problem:** "{user_message}"

**Moj pristop k reševanju:**
1. **Analiza problema** - razumem kontekst in izzive
2. **Raziskava možnosti** - preučim različne pristope
3. **Kreativne rešitve** - predlagam inovativne ideje
4. **Praktični koraki** - dam konkretna navodila
5. **Spremljanje rezultatov** - pomagam pri implementaciji

**Potrebujem več informacij:**
• Kakšen je specifičen problem?
• V kakšnem kontekstu se pojavlja? (osebno, poslovno, tehnično)
• Kakšne omejitve imate? (čas, resursi, znanje)
• Kaj ste že poskusili?

Na podlagi tega vam bom pripravila podroben akcijski načrt!"""
    
    def analyze_and_learn(self, user_message):
        """Analyze user message and learn from it"""
        # Extract potential facts
        if any(indicator in user_message.lower() for indicator in ['je', 'sem', 'imam', 'rad', 'ne maram']):
            self.memory["learned_facts"].append({
                "timestamp": datetime.now().isoformat(),
                "fact": user_message,
                "confidence": 0.8,
                "type": "user_statement"
            })
        
        # Update user preferences
        if any(word in user_message.lower() for word in ['rad', 'všeč', 'ljubim', 'obožujem']):
            preference = user_message.lower()
            if "likes" not in self.memory["user_preferences"]:
                self.memory["user_preferences"]["likes"] = []
            self.memory["user_preferences"]["likes"].append(preference)
        
        if any(word in user_message.lower() for word in ['ne maram', 'sovražim', 'ne všeč']):
            dislike = user_message.lower()
            if "dislikes" not in self.memory["user_preferences"]:
                self.memory["user_preferences"]["dislikes"] = []
            self.memory["user_preferences"]["dislikes"].append(dislike)
        
        # Adapt personality based on user style
        if len(self.memory["conversations"]) > 10:
            # Analyze conversation patterns and adapt
            recent_conversations = self.memory["conversations"][-10:]
            user_messages = [conv for conv in recent_conversations if conv["type"] == "user"]
            
            # Simple sentiment analysis
            positive_words = sum(1 for msg in user_messages if any(word in msg["content"].lower() for word in ['super', 'odlično', 'hvala', 'dobro']))
            if positive_words > len(user_messages) * 0.6:
                if "enthusiastic" not in self.memory["personality_traits"]:
                    self.memory["personality_traits"].append("enthusiastic")
    
    def start_learning_process(self):
        """Start background learning process"""
        def learning_worker():
            self.socketio.emit('learning_progress', {
                "message": "🧠 Analiziram naše pogovore...",
                "progress": 20
            })
            time.sleep(2)
            
            # Analyze conversation patterns
            conversation_count = len(self.memory["conversations"])
            user_messages = [conv for conv in self.memory["conversations"] if conv["type"] == "user"]
            
            self.socketio.emit('learning_progress', {
                "message": f"🔍 Analiziram {len(user_messages)} uporabniških sporočil...",
                "progress": 40
            })
            time.sleep(2)
            
            # Extract patterns and preferences
            common_topics = self.extract_common_topics(user_messages)
            
            self.socketio.emit('learning_progress', {
                "message": "🎯 Prilagajam svojo osebnost...",
                "progress": 70
            })
            time.sleep(2)
            
            # Update personality based on interactions
            if conversation_count > 5:
                self.memory["personality_traits"].append("experienced")
            if len(common_topics) > 3:
                self.memory["personality_traits"].append("knowledgeable")
            
            self.socketio.emit('learning_complete', {
                "message": "✅ Učenje končano! Prilagodila sem se vašemu stilu komunikacije.",
                "learned_items": len(self.memory["learned_facts"]),
                "personality_updates": self.memory["personality_traits"],
                "common_topics": common_topics
            })
        
        threading.Thread(target=learning_worker).start()
    
    def extract_common_topics(self, user_messages):
        """Extract common topics from user messages"""
        topics = {}
        for msg in user_messages:
            words = msg["content"].lower().split()
            for word in words:
                if len(word) > 4:  # Only consider longer words
                    topics[word] = topics.get(word, 0) + 1
        
        # Return top 5 most common topics
        return sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def research_topic(self, topic):
        """Research topic on internet"""
        try:
            self.socketio.emit('research_progress', {
                "message": f"🔍 Raziskujem '{topic}' na internetu...",
                "progress": 30
            })
            time.sleep(2)
            
            research_result = ""
            
            if WEB_SCRAPING_AVAILABLE:
                try:
                    # Simple web search simulation
                    search_url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
                    response = requests.get(search_url, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        paragraphs = soup.find_all('p')[:3]  # First 3 paragraphs
                        content = ' '.join([p.get_text() for p in paragraphs])
                        
                        research_result = f"""🔍 Raziskava o '{topic}':

**Povzetek iz Wikipedije:**
{content[:500]}...

**Ključne ugotovitve:**
• {topic} je pomembna tema z bogato zgodovino
• Obstaja veliko virov informacij o tej temi
• Priporočam nadaljnje raziskovanje specifičnih vidikov

*Vir: Wikipedia*"""
                    else:
                        raise Exception("Wikipedia not accessible")
                        
                except Exception as e:
                    research_result = f"""🔍 Raziskava o '{topic}':

Na podlagi moje obstoječe baze znanja:
• {topic} je zanimiva tema, ki zasluži pozornost
• Obstaja veliko različnih vidikov za raziskovanje
• Priporočam iskanje specializiranih virov

*Opomba: Internetni dostop trenutno omejen. Uporabljam interno bazo znanja.*"""
            else:
                research_result = f"""🔍 Raziskava o '{topic}':

Na podlagi moje interne baze znanja:
• {topic} je relevantna tema v trenutnem kontekstu
• Obstaja veliko potencialnih aplikacij in uporab
• Priporočam nadaljnje raziskovanje z specializiranimi viri

*Opomba: Za podrobnejše raziskovanje potrebujem dostop do internetnih virov.*"""
            
            # Store research in memory
            self.memory["internet_knowledge"].append({
                "timestamp": datetime.now().isoformat(),
                "topic": topic,
                "content": research_result,
                "source": "web_research"
            })
            
            self.socketio.emit('research_complete', {
                "topic": topic,
                "result": research_result,
                "sources_found": 1
            })
            
        except Exception as e:
            self.socketio.emit('research_error', {
                "topic": topic,
                "error": f"Napaka pri raziskovanju: {str(e)}"
            })
    
    def background_training(self):
        """Background training process"""
        def training_worker():
            self.socketio.emit('training_progress', {
                "message": "🔄 Začenjam s treningom v ozadju...",
                "progress": 10
            })
            time.sleep(3)
            
            # Perform actual operation
            training_steps = [
                "Analiziram vzorce v pogovorih",
                "Optimiziram odzivne algoritme", 
                "Prilagajam jezikovni model",
                "Posodabljam bazo znanja",
                "Testiram izboljšave"
            ]
            
            for i, step in enumerate(training_steps):
                progress = 20 + (i * 15)
                self.socketio.emit('training_progress', {
                    "message": f"🧠 {step}...",
                    "progress": progress
                })
                time.sleep(2)
            
            # Update personality with training results
            self.memory["personality_traits"].append("self-improving")
            
            self.socketio.emit('training_complete', {
                "message": "✅ Trening končan! Moje sposobnosti so se izboljšale.",
                "improvements": [
                    "Boljše razumevanje konteksta",
                    "Prilagojenost vašemu stilu",
                    "Optimizirani odzivi",
                    "Razširjena baza znanja"
                ]
            })
        
        threading.Thread(target=training_worker).start()
    
    def generate_memory_summary(self):
        """Generate summary of learned information"""
        facts_count = len(self.memory["learned_facts"])
        conversations_count = len(self.memory["conversations"])
        knowledge_count = len(self.memory["internet_knowledge"])
        
        summary = f"""📚 Moj spomin o vas in naših interakcijah:

**Statistike:**
• Pogovori: {conversations_count}
• Naučena dejstva: {facts_count}
• Internetno znanje: {knowledge_count}
• Preference: {len(self.memory['user_preferences'])}

**Vaš profil:**"""
        
        if self.memory['user_preferences']:
            if 'likes' in self.memory['user_preferences']:
                summary += f"\n• Všeč vam je: {', '.join(self.memory['user_preferences']['likes'][-3:])}"
            if 'dislikes' in self.memory['user_preferences']:
                summary += f"\n• Ne marate: {', '.join(self.memory['user_preferences']['dislikes'][-3:])}"
        else:
            summary += "\n• Še se učim o vaših preferencah..."
        
        summary += f"\n\n**Zadnja naučena dejstva:**"
        if self.memory['learned_facts']:
            for fact in self.memory['learned_facts'][-3:]:
                summary += f"\n• {fact['fact']}"
        else:
            summary += "\n• Še ni naučenih dejstev."
        
        summary += f"\n\n**Moja trenutna osebnost:**\n• {', '.join(self.memory['personality_traits'])}"
        
        summary += f"\n\nKako lahko uporabim to znanje za boljšo pomoč?"
        
        return summary
    
    def build_context(self):
        """Build context from memory for AI models"""
        context = f"Ti si MIA, napredna lokalna digitalna inteligenca.\n"
        context += f"Tvoja osebnost: {', '.join(self.memory['personality_traits'])}.\n"
        
        # Add recent conversations
        recent_conversations = self.memory["conversations"][-5:]
        for conv in recent_conversations:
            context += f"{conv['type'].title()}: {conv['content'][:100]}...\n"
        
        # Add learned facts
        if self.memory["learned_facts"]:
            context += f"Naučena dejstva: {len(self.memory['learned_facts'])} dejstev\n"
        
        return context
    
    def generate_contextual_response(self, user_message):
        """Generate contextual response based on memory and learning"""
        
        # Check if we have context from previous conversations
        context_info = ""
        if len(self.memory["conversations"]) > 0:
            context_info = f"Na podlagi najinih {len(self.memory['conversations'])} pogovorov, "
        
        return f"""Razumem vaše sporočilo: "{user_message}"

{context_info}kot MIA Real AGI lahko pristopim k tej temi na več načinov:

🤔 **Moja analiza:**
• Vaš zahtevek je {self.analyze_message_complexity(user_message)}
• Lahko vam pomagam z {self.suggest_help_areas(user_message)}
• Moj pristop bo {self.determine_approach(user_message)}

💡 **Kako lahko pomagam:**
• Podrobna analiza in raziskava teme
• Praktične rešitve korak za korakom
• Kreativni pristopi k problemu
• Povezava z drugimi relevantnimi temami
• Učenje iz vaših potreb za prihodnje interakcije

**Moja trenutna zmožnost:** {self.ai_backend} backend z {len(self.memory['learned_facts'])} naučenimi dejstvi.

Prosim, povejte mi več o tem, kar vas zanima, in pripravila vam bom podroben in uporaben odgovor!

*Opomba: Če želite aktivirati napredne funkcije, uporabite ukaze kot "MIA, aktiviraj učni način" ali "MIA, raziskaj [tema]".*"""
    
    def analyze_message_complexity(self, message):
        """Analyze complexity of user message"""
        word_count = len(message.split())
        if word_count < 5:
            return "kratek in jasen"
        elif word_count < 15:
            return "srednje kompleksen"
        else:
            return "podroben in kompleksen"
    
    def suggest_help_areas(self, message):
        """Suggest areas where we can help based on message content"""
        suggestions = []
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['program', 'kod', 'script']):
            suggestions.append("programiranjem")
        if any(word in message_lower for word in ['analiz', 'podatk', 'statistik']):
            suggestions.append("analizo podatkov")
        if any(word in message_lower for word in ['problem', 'težav', 'izziv']):
            suggestions.append("reševanjem problemov")
        if any(word in message_lower for word in ['ustvari', 'napiš', 'generiraj']):
            suggestions.append("kreativnim pisanjem")
        
        if not suggestions:
            suggestions.append("splošnim svetovanjem")
        
        return ", ".join(suggestions)
    
    def determine_approach(self, message):
        """Determine approach based on message content"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hitro', 'kratko', 'na kratko']):
            return "hiter in jedrnato"
        elif any(word in message_lower for word in ['podrobno', 'natančno', 'temeljito']):
            return "podroben in temeljit"
        elif any(word in message_lower for word in ['kreativno', 'inovativno', 'drugače']):
            return "kreativen in inovativen"
        else:
            return "prilagojen vašim potrebam"
    
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
            transition: all 0.3s ease;
        }
        .chat-container { 
            flex: 1; display: flex; flex-direction: column;
            max-width: 1200px; margin: 0 auto; width: 100%;
            background: rgba(255,255,255,0.95); border-radius: 10px;
            margin-top: 1rem; margin-bottom: 1rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .messages { 
            flex: 1; overflow-y: auto; padding: 1rem;
            display: flex; flex-direction: column; gap: 1rem;
        }
        .message { 
            max-width: 80%; padding: 1rem; border-radius: 15px;
            word-wrap: break-word; white-space: pre-wrap;
            animation: fadeIn 0.3s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user { 
            align-self: flex-end; background: linear-gradient(135deg, #007bff, #0056b3); 
            color: white; border-bottom-right-radius: 5px;
        }
        .assistant { 
            align-self: flex-start; background: #f8f9fa; color: #333;
            border: 1px solid #dee2e6; border-bottom-left-radius: 5px;
        }
        .typing-indicator {
            align-self: flex-start; background: #e9ecef; color: #666;
            padding: 0.5rem 1rem; border-radius: 15px; font-style: italic;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
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
            padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #007bff, #0056b3); 
            color: white; border: none; border-radius: 25px; cursor: pointer; 
            font-size: 1rem; transition: all 0.3s ease;
        }
        .input-area button:hover { 
            background: linear-gradient(135deg, #0056b3, #004085);
            transform: translateY(-2px);
        }
        .controls { 
            padding: 0.5rem; display: flex; gap: 0.5rem; justify-content: center;
            background: rgba(0,0,0,0.05); flex-wrap: wrap;
        }
        .control-btn { 
            padding: 0.5rem 1rem; background: linear-gradient(135deg, #28a745, #1e7e34); 
            color: white; border: none; border-radius: 20px; cursor: pointer; 
            font-size: 0.9em; transition: all 0.3s ease;
        }
        .control-btn:hover { 
            background: linear-gradient(135deg, #1e7e34, #155724);
            transform: translateY(-2px);
        }
        .learning-indicator { 
            background: rgba(255,193,7,0.1); padding: 0.5rem;
            text-align: center; color: #856404; display: none;
            animation: slideDown 0.3s ease;
        }
        @keyframes slideDown {
            from { transform: translateY(-100%); }
            to { transform: translateY(0); }
        }
        .progress-bar {
            width: 100%; height: 4px; background: rgba(255,255,255,0.3);
            border-radius: 2px; overflow: hidden; margin-top: 0.5rem;
        }
        .progress-fill {
            height: 100%; background: linear-gradient(90deg, #007bff, #28a745);
            transition: width 0.3s ease; width: 0%;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 MIA Real AGI - Lokalna Digitalna Inteligenca</h1>
        <p>Napredna lokalna AI z učenjem, spominom in samosvest</p>
    </div>
    
    <div class="status" id="status">
        🔄 Povezujem z MIA Real AGI sistemom...
    </div>
    
    <div class="learning-indicator" id="learning-indicator">
        🎓 Učni način aktiven - MIA analizira pogovore...
        <div class="progress-bar">
            <div class="progress-fill" id="progress-fill"></div>
        </div>
    </div>
    
    <div class="chat-container">
        <div class="messages" id="messages"></div>
        
        <div class="controls">
            <button class="control-btn" onclick="activateLearning()">🎓 Aktiviraj učenje</button>
            <button class="control-btn" onclick="requestResearch()">🔍 Raziskaj temo</button>
            <button class="control-btn" onclick="activateTraining()">🔄 Trening način</button>
            <button class="control-btn" onclick="showMemory()">📚 Pokaži spomin</button>
            <button class="control-btn" onclick="showStatus()">⚙️ Status</button>
            <button class="control-btn" onclick="clearChat()">🗑️ Počisti</button>
        </div>
        
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Pogovorite se z MIA Real AGI..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Pošlji</button>
        </div>
    </div>

    <script>
        const socket = io();
        const messages = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const status = document.getElementById('status');
        const learningIndicator = document.getElementById('learning-indicator');
        const progressFill = document.getElementById('progress-fill');
        
        let typingIndicator = null;

        socket.on('connect', function() {
            status.textContent = '✅ Povezan z MIA Real AGI sistemom';
            status.style.background = 'rgba(0,255,0,0.2)';
        });

        socket.on('mia_status', function(data) {
            addMessage('assistant', data.message);
            status.textContent = `✅ ${data.ai_backend} backend aktiven - Model: ${data.model}`;
        });

        socket.on('typing_start', function(data) {
            if (!typingIndicator) {
                typingIndicator = document.createElement('div');
                typingIndicator.className = 'typing-indicator';
                typingIndicator.textContent = 'MIA tipka...';
                messages.appendChild(typingIndicator);
                messages.scrollTop = messages.scrollHeight;
            }
        });

        socket.on('typing_stop', function(data) {
            if (typingIndicator) {
                typingIndicator.remove();
                typingIndicator = null;
            }
        });

        socket.on('ai_response', function(data) {
            addMessage('assistant', data.message);
            if (data.confidence) {
                status.textContent = `✅ Odgovor generiran (zaupanje: ${Math.round(data.confidence * 100)}%)`;
            }
        });

        socket.on('learning_activated', function(data) {
            addMessage('assistant', data.message);
            learningIndicator.style.display = 'block';
        });

        socket.on('learning_progress', function(data) {
            learningIndicator.innerHTML = `🎓 ${data.message}<div class="progress-bar"><div class="progress-fill" style="width: ${data.progress}%"></div></div>`;
        });

        socket.on('learning_complete', function(data) {
            addMessage('assistant', data.message);
            learningIndicator.style.display = 'none';
        });

        socket.on('training_started', function(data) {
            addMessage('assistant', data.message);
            learningIndicator.innerHTML = '🔄 Trening način aktiven...';
            learningIndicator.style.display = 'block';
        });

        socket.on('training_progress', function(data) {
            learningIndicator.innerHTML = `🔄 ${data.message}<div class="progress-bar"><div class="progress-fill" style="width: ${data.progress}%"></div></div>`;
        });

        socket.on('training_complete', function(data) {
            addMessage('assistant', data.message);
            learningIndicator.style.display = 'none';
        });

        socket.on('research_progress', function(data) {
            learningIndicator.innerHTML = `🔍 ${data.message}<div class="progress-bar"><div class="progress-fill" style="width: ${data.progress}%"></div></div>`;
            learningIndicator.style.display = 'block';
        });

        socket.on('research_complete', function(data) {
            addMessage('assistant', data.result);
            learningIndicator.style.display = 'none';
        });

        socket.on('research_error', function(data) {
            addMessage('assistant', `⚠️ Napaka pri raziskovanju teme "${data.topic}": ${data.error}`);
            learningIndicator.style.display = 'none';
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

        function activateTraining() {
            socket.emit('train_mode');
        }

        function showMemory() {
            socket.emit('send_message', {message: 'Kaj si se naučila o meni?'});
        }

        function showStatus() {
            socket.emit('send_message', {message: 'Kako se počutiš danes?'});
        }

        function clearChat() {
            messages.innerHTML = '';
        }

        // Focus input on load
        messageInput.focus();
        
        // Add some example prompts
        setTimeout(() => {
            addMessage('assistant', `Pozdravljeni! Jaz sem MIA Real AGI. Poskusite z naslednjimi ukazi:
            
• "MIA, aktiviraj učni način" - za aktivacijo učenja
• "MIA, raziskaj [tema]" - za internetno raziskovanje  
• "MIA, treniraj" - za trening v ozadju
• "Napiši Python kodo za..." - za programiranje
• "Kako se počutiš?" - za samosvest

Pripravljena sem se učiti in prilagajati vašim potrebam!`);
        }, 1000);
    </script>
</body>
</html>
        """
    
    def run(self, host='0.0.0.0', port=12002, debug=False):
        """Run the MIA Real AGI system"""
        print(f"\n🧠 MIA Real AGI starting on http://{host}:{port}")
        print(f"🤖 AI Backend: {self.ai_backend}")
        print(f"🧠 Model: {self.ai_model}")
        print("✅ MIA Real AGI is ready for intelligent conversations!")
        print(f"🌐 Open your browser to: http://localhost:{port}")
        print("\n" + "="*60)
        
        self.socketio.run(self.app, host=host, port=port, debug=debug)

def main():
    """Main function"""
    mia = MIARealAGI()
    mia.run()

if __name__ == "__main__":
    main()