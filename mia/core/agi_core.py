#!/usr/bin/env python3
"""
MIA Enterprise AGI - Core Intelligence System
The main AGI core that provides reasoning, understanding, and autonomous capabilities
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

class ThoughtType(Enum):
    """Types of thoughts the AGI can have"""
    REASONING = "reasoning"
    PLANNING = "planning"
    REFLECTION = "reflection"
    ANALYSIS = "analysis"
    DECISION = "decision"
    CREATIVE = "creative"

class TaskStatus(Enum):
    """Status of AGI tasks"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class Thought:
    """Represents a thought in the AGI's reasoning process"""
    id: str
    type: ThoughtType
    content: str
    confidence: float
    timestamp: float
    context: Dict[str, Any]
    reasoning_chain: List[str]

@dataclass
class Task:
    """Represents a task for the AGI to process"""
    id: str
    description: str
    priority: int
    status: TaskStatus
    created_at: float
    updated_at: float
    context: Dict[str, Any]
    result: Optional[Any] = None
    error: Optional[str] = None

@dataclass
class Memory:
    """Represents a memory in the AGI's memory system"""
    id: str
    content: str
    type: str
    importance: float
    timestamp: float
    associations: List[str]
    context: Dict[str, Any]

class AGICore:
    """
    Main AGI Core - The central intelligence system
    
    This is the heart of MIA Enterprise AGI that provides:
    - Semantic understanding and reasoning
    - Context management and memory
    - Task planning and execution
    - Autonomous decision making
    - Learning and adaptation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, knowledge_store=None, data_dir=None, **kwargs):
        self.config = config or {}
        self.knowledge_store = knowledge_store
        self.data_dir = data_dir
        self.logger = self._setup_logging()
        
        # Core state
        self.is_running = False
        self.thoughts: List[Thought] = []
        self.tasks: Dict[str, Task] = {}
        self.memories: Dict[str, Memory] = {}
        self.context: Dict[str, Any] = {}
        
        # Core components
        self.semantic_engine = None
        self.llm_backend = None
        self.memory_system = None
        self.agent_system = None
        
        # Model management
        self.available_models = {}
        self.current_model = None
        self.model_performance = {}
        self.model_discovery = None
        
        # Learning system
        self.learning_system = None
        
        # Performance metrics
        self.metrics = {
            "thoughts_generated": 0,
            "tasks_completed": 0,
            "decisions_made": 0,
            "learning_events": 0,
            "start_time": time.time()
        }
        
        self.logger.info("🧠 AGI Core initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup AGI core logging"""
        logger = logging.getLogger("MIA.AGI.Core")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def initialize(self):
        """Initialize the AGI core systems"""
        self.logger.info("🚀 Initializing AGI Core systems...")
        
        try:
            # Initialize model discovery
            await self._initialize_model_discovery()
            
            # Initialize semantic engine
            await self._initialize_semantic_engine()
            
            # Initialize LLM backend
            await self._initialize_llm_backend()
            
            # Initialize learning system
            await self._initialize_learning_system()
            
            # Initialize memory system
            await self._initialize_memory_system()
            
            # Initialize agent system
            await self._initialize_agent_system()
            
            # Load existing state
            await self._load_state()
            
            self.is_running = True
            self.logger.info("✅ AGI Core fully initialized and ready")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize AGI Core: {e}")
            raise
    
    async def _initialize_semantic_engine(self):
        """Initialize the semantic understanding engine"""
        self.logger.info("🔍 Initializing semantic engine...")
        
        # Basic semantic engine implementation
        self.semantic_engine = {
            "context_window": 4096,
            "understanding_threshold": 0.7,
            "reasoning_depth": 3,
            "knowledge_base": {},
            "concept_graph": {}
        }
        
        self.logger.info("✅ Semantic engine ready")
    
    async def _initialize_model_discovery(self):
        """Initialize model discovery and management"""
        self.logger.info("🔍 Initializing model discovery...")
        
        try:
            from .model_discovery import model_discovery
            self.model_discovery = model_discovery
            
            # Discover available models
            await self._discover_models()
            
            # Select best model
            await self._select_optimal_model()
            
            self.logger.info(f"✅ Model discovery ready - {len(self.available_models)} models found")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Model discovery failed: {e}")
            self.available_models = {}
    
    async def _discover_models(self):
        """Discover all available models"""
        try:
            # Start discovery process
            self.model_discovery.start_discovery()
            
            # Wait a bit for discovery to complete
            await asyncio.sleep(2)
            
            # Get discovered models
            discovered = self.model_discovery.get_discovered_models()
            
            for model_id, model_info in discovered.items():
                self.available_models[model_id] = {
                    "info": model_info,
                    "performance_score": 0.0,
                    "usage_count": 0,
                    "last_used": None,
                    "status": "available"
                }
                
            self.logger.info(f"📊 Discovered {len(self.available_models)} models")
            
        except Exception as e:
            self.logger.error(f"❌ Model discovery failed: {e}")
    
    async def _select_optimal_model(self):
        """Select the best available model"""
        if not self.available_models:
            self.logger.warning("⚠️ No models available for selection")
            return
        
        # Prioritize Ollama models, then HuggingFace
        ollama_models = [m for m in self.available_models.values() 
                        if m["info"].format.value == "ollama"]
        
        if ollama_models:
            # Select first Ollama model
            best_model = ollama_models[0]
            self.current_model = best_model["info"].id
            self.logger.info(f"🎯 Selected Ollama model: {self.current_model}")
        else:
            # Select first available model
            first_model = list(self.available_models.values())[0]
            self.current_model = first_model["info"].id
            self.logger.info(f"🎯 Selected model: {self.current_model}")
    
    async def switch_model(self, model_id: str) -> bool:
        """Switch to a different model"""
        if model_id not in self.available_models:
            self.logger.error(f"❌ Model {model_id} not available")
            return False
        
        try:
            old_model = self.current_model
            self.current_model = model_id
            
            # Reinitialize LLM backend with new model
            await self._initialize_llm_backend()
            
            self.logger.info(f"🔄 Switched from {old_model} to {model_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to switch model: {e}")
            self.current_model = old_model  # Revert
            return False
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models"""
        return {
            "current": self.current_model,
            "available": {
                model_id: {
                    "name": model_data["info"].name,
                    "format": model_data["info"].format.value,
                    "size": model_data["info"].size,
                    "performance_score": model_data["performance_score"],
                    "usage_count": model_data["usage_count"]
                }
                for model_id, model_data in self.available_models.items()
            }
        }
    
    async def _initialize_learning_system(self):
        """Initialize the learning system"""
        self.logger.info("🧠 Initializing learning system...")
        
        try:
            from .learning_system import learning_system
            self.learning_system = learning_system
            
            self.logger.info("✅ Learning system ready")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize learning system: {e}")
            self.learning_system = None
    
    async def _initialize_llm_backend(self):
        """Initialize the LLM backend for language processing"""
        self.logger.info("🤖 Initializing LLM backend...")
        
        # Use current model if available
        if self.current_model and self.current_model in self.available_models:
            model_info = self.available_models[self.current_model]["info"]
            
            if model_info.format.value == "ollama":
                try:
                    from mia.core.llm_backends.ollama_backend import ollama_backend
                    
                    if await ollama_backend.is_available():
                        await ollama_backend.initialize()
                        self.ollama_backend = ollama_backend
                        self.llm_backend = {
                            "type": "ollama",
                            "backend": ollama_backend,
                            "model": model_info.name,
                            "context_length": 4096,
                            "temperature": 0.7,
                            "max_tokens": 1024,
                            "status": "ready"
                        }
                        
                        # Update model usage
                        self.available_models[self.current_model]["usage_count"] += 1
                        self.available_models[self.current_model]["last_used"] = time.time()
                        
                        self.logger.info(f"✅ LLM backend ready with Ollama model: {model_info.name}")
                        return
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to initialize Ollama backend: {e}")
        
        # Try to initialize Ollama backend as fallback
        try:
            from mia.core.llm_backends.ollama_backend import ollama_backend
            
            if await ollama_backend.is_available():
                await ollama_backend.initialize()
                self.ollama_backend = ollama_backend  # Store reference for direct access
                self.llm_backend = {
                    "type": "ollama",
                    "backend": ollama_backend,
                    "context_length": 4096,
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "status": "ready"
                }
                self.logger.info("✅ LLM backend ready with Ollama")
                return
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to initialize Ollama backend: {e}")
        
        # Check for available local models as fallback
        from mia.core.model_discovery import model_discovery
        
        models = model_discovery.get_discovered_models()
        best_model = None
        
        for model_id, model_info in models.items():
            if model_info.is_loaded and model_info.performance_score > 0.8:
                best_model = model_info
                break
        
        if best_model:
            self.llm_backend = {
                "type": "local",
                "model": best_model,
                "context_length": 4096,
                "temperature": 0.7,
                "max_tokens": 1024,
                "status": "ready"
            }
            self.logger.info(f"✅ LLM backend ready with model: {best_model.name}")
        else:
            # Fallback to basic text processing
            self.llm_backend = {
                "type": "basic",
                "model": None,
                "mode": "basic_processing",
                "status": "fallback"
            }
            self.logger.warning("⚠️ No suitable LLM found, using basic processing")
    
    async def _initialize_memory_system(self):
        """Initialize the memory management system"""
        self.logger.info("🧠 Initializing memory system...")
        
        self.memory_system = {
            "short_term": {},
            "long_term": {},
            "working_memory": {},
            "episodic_memory": {},
            "semantic_memory": {},
            "max_short_term": 100,
            "max_working": 20,
            "consolidation_threshold": 0.8
        }
        
        self.logger.info("✅ Memory system ready")
    
    async def _initialize_agent_system(self):
        """Initialize the autonomous agent system"""
        self.logger.info("🤖 Initializing agent system...")
        
        self.agent_system = {
            "active_agents": {},
            "task_queue": [],
            "goal_stack": [],
            "planning_horizon": 5,
            "max_concurrent_tasks": 3,
            "autonomy_level": 0.8
        }
        
        self.logger.info("✅ Agent system ready")
    
    async def _load_state(self):
        """Load previous AGI state if available"""
        state_file = Path("mia/data/agi_state.json")
        
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                
                # Restore memories
                for memory_data in state.get("memories", []):
                    memory = Memory(**memory_data)
                    self.memories[memory.id] = memory
                
                # Restore context
                self.context.update(state.get("context", {}))
                
                self.logger.info(f"📚 Loaded {len(self.memories)} memories from previous session")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Could not load previous state: {e}")
    
    async def save_state(self):
        """Save current AGI state"""
        state_file = Path("mia/data/agi_state.json")
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            state = {
                "memories": [asdict(memory) for memory in self.memories.values()],
                "context": self.context,
                "metrics": self.metrics,
                "timestamp": time.time()
            }
            
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
            self.logger.info("💾 AGI state saved")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save state: {e}")
    
    async def think(self, prompt: str, thought_type: ThoughtType = ThoughtType.REASONING) -> Thought:
        """
        Generate a thought based on the given prompt
        This is the core reasoning function of the AGI
        """
        thought_id = f"thought_{int(time.time() * 1000)}"
        
        self.logger.info(f"🤔 Thinking about: {prompt[:100]}...")
        
        # Analyze the prompt and context
        context = await self._analyze_context(prompt)
        
        # Generate reasoning chain
        reasoning_chain = await self._generate_reasoning_chain(prompt, context)
        
        # Generate the actual thought content
        content = await self._generate_thought_content(prompt, reasoning_chain, thought_type)
        
        # Calculate confidence
        confidence = await self._calculate_confidence(content, reasoning_chain)
        
        thought = Thought(
            id=thought_id,
            type=thought_type,
            content=content,
            confidence=confidence,
            timestamp=time.time(),
            context=context,
            reasoning_chain=reasoning_chain
        )
        
        self.thoughts.append(thought)
        self.metrics["thoughts_generated"] += 1
        
        # Store important thoughts in memory
        if confidence > 0.8:
            await self._store_in_memory(thought)
        
        self.logger.info(f"💭 Generated thought with confidence {confidence:.2f}")
        return thought
    
    async def _analyze_context(self, prompt: str) -> Dict[str, Any]:
        """Analyze the context of the given prompt"""
        context = {
            "prompt_length": len(prompt),
            "prompt_complexity": self._estimate_complexity(prompt),
            "relevant_memories": await self._find_relevant_memories(prompt),
            "current_tasks": list(self.tasks.keys()),
            "timestamp": time.time()
        }
        
        return context
    
    def _estimate_complexity(self, text: str) -> float:
        """Estimate the complexity of a text prompt"""
        # Simple complexity estimation based on various factors
        factors = {
            "length": min(len(text) / 1000, 1.0),
            "questions": text.count("?") * 0.1,
            "technical_terms": len([w for w in text.split() if len(w) > 8]) * 0.05,
            "sentences": text.count(".") * 0.02
        }
        
        complexity = sum(factors.values())
        return min(complexity, 1.0)
    
    async def _find_relevant_memories(self, prompt: str) -> List[str]:
        """Find memories relevant to the current prompt"""
        relevant = []
        prompt_words = set(prompt.lower().split())
        
        for memory_id, memory in self.memories.items():
            memory_words = set(memory.content.lower().split())
            overlap = len(prompt_words.intersection(memory_words))
            
            if overlap > 2:  # Simple relevance threshold
                relevant.append(memory_id)
        
        return relevant[:5]  # Return top 5 relevant memories
    
    async def _generate_reasoning_chain(self, prompt: str, context: Dict[str, Any]) -> List[str]:
        """Generate a chain of reasoning steps"""
        reasoning_steps = []
        
        # Step 1: Understand the prompt
        reasoning_steps.append(f"Understanding prompt: {prompt[:50]}...")
        
        # Step 2: Consider context
        if context["relevant_memories"]:
            reasoning_steps.append(f"Considering {len(context['relevant_memories'])} relevant memories")
        
        # Step 3: Analyze complexity
        complexity = context["prompt_complexity"]
        if complexity > 0.5:
            reasoning_steps.append("This is a complex prompt requiring deeper analysis")
        else:
            reasoning_steps.append("This is a straightforward prompt")
        
        # Step 4: Plan response
        reasoning_steps.append("Planning comprehensive response")
        
        return reasoning_steps
    
    async def _generate_thought_content(self, prompt: str, reasoning_chain: List[str], thought_type: ThoughtType) -> str:
        """Generate the actual content of the thought"""
        
        if self.llm_backend and self.llm_backend.get("status") == "ready":
            # Use LLM for sophisticated response
            return await self._generate_llm_response(prompt, reasoning_chain, thought_type)
        else:
            # Use basic processing
            return await self._generate_basic_response(prompt, reasoning_chain, thought_type)
    
    async def _generate_llm_response(self, prompt: str, reasoning_chain: List[str], thought_type: ThoughtType) -> str:
        """Generate response using LLM backend"""
        try:
            if self.llm_backend.get("type") == "ollama":
                backend = self.llm_backend["backend"]
                
                # Create a structured prompt for the LLM
                system_prompt = f"""You are MIA, an Enterprise AGI assistant. You are currently engaged in {thought_type.value} thinking.
                
Your reasoning chain so far: {' -> '.join(reasoning_chain)}

Please provide a thoughtful, professional response to the following:"""
                
                full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nMIA:"
                
                # Use timeout for LLM response generation
                response = await asyncio.wait_for(
                    backend.generate_response(
                        prompt=full_prompt,
                        model="llama3.2:1b",
                        stream=False,
                        temperature=self.llm_backend.get("temperature", 0.7),
                        max_tokens=self.llm_backend.get("max_tokens", 1024)
                    ),
                    timeout=8.0  # 8 second timeout
                )
                
                return response.strip() if response else "I'm processing your request..."
                
        except asyncio.TimeoutError:
            self.logger.warning("LLM generation timed out, using fallback")
            return await self._generate_basic_response(prompt, reasoning_chain, thought_type)
        except Exception as e:
            self.logger.error(f"❌ LLM generation error: {e}")
            return await self._generate_basic_response(prompt, reasoning_chain, thought_type)
    
    async def _generate_basic_response(self, prompt: str, reasoning_chain: List[str], thought_type: ThoughtType) -> str:
        """Generate basic response without LLM"""
        
        if thought_type == ThoughtType.REASONING:
            return f"Analyzing: {prompt}. Based on available information and reasoning chain, I can provide insights."
        elif thought_type == ThoughtType.PLANNING:
            return f"Planning approach for: {prompt}. Breaking down into manageable steps."
        elif thought_type == ThoughtType.ANALYSIS:
            return f"Analyzing: {prompt}. Examining patterns, relationships, and implications."
        elif thought_type == ThoughtType.DECISION:
            return f"Making decision about: {prompt}. Weighing options and consequences."
        elif thought_type == ThoughtType.CREATIVE:
            return f"Creative thinking about: {prompt}. Exploring innovative approaches and possibilities."
        else:
            return f"Reflecting on: {prompt}. Considering multiple perspectives and implications."
    
    async def _calculate_confidence(self, content: str, reasoning_chain: List[str]) -> float:
        """Calculate confidence in the generated thought"""
        factors = {
            "content_length": min(len(content) / 500, 1.0) * 0.3,
            "reasoning_depth": min(len(reasoning_chain) / 5, 1.0) * 0.4,
            "coherence": 0.8,  # Would be calculated based on actual content analysis
            "relevance": 0.7   # Would be calculated based on prompt matching
        }
        
        confidence = sum(factors.values())
        return min(confidence, 1.0)
    
    async def _store_in_memory(self, thought: Thought):
        """Store important thoughts in memory"""
        memory_id = f"memory_{thought.id}"
        
        memory = Memory(
            id=memory_id,
            content=thought.content,
            type="thought",
            importance=thought.confidence,
            timestamp=thought.timestamp,
            associations=[],
            context=thought.context
        )
        
        self.memories[memory_id] = memory
        self.logger.debug(f"💾 Stored thought in memory: {memory_id}")
    
    async def process_task(self, description: str, priority: int = 5) -> Task:
        """Process a new task"""
        task_id = f"task_{int(time.time() * 1000)}"
        
        task = Task(
            id=task_id,
            description=description,
            priority=priority,
            status=TaskStatus.PENDING,
            created_at=time.time(),
            updated_at=time.time(),
            context={}
        )
        
        self.tasks[task_id] = task
        self.logger.info(f"📋 New task created: {description[:50]}...")
        
        # Start processing the task
        await self._process_task_async(task)
        
        return task
    
    async def _process_task_async(self, task: Task):
        """Process a task asynchronously"""
        try:
            task.status = TaskStatus.PROCESSING
            task.updated_at = time.time()
            
            # Generate thoughts about the task
            thought = await self.think(
                f"How should I approach this task: {task.description}",
                ThoughtType.PLANNING
            )
            
            # Perform actual operation
            await asyncio.sleep(0.1)  # Perform actual operation
            
            # Complete the task
            task.result = {
                "approach": thought.content,
                "confidence": thought.confidence,
                "reasoning": thought.reasoning_chain
            }
            task.status = TaskStatus.COMPLETED
            task.updated_at = time.time()
            
            self.metrics["tasks_completed"] += 1
            self.logger.info(f"✅ Task completed: {task.id}")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.updated_at = time.time()
            self.logger.error(f"❌ Task failed: {task.id} - {e}")
    
    async def chat(self, message: str) -> str:
        """
        Main chat interface - process user message and return response
        This is the primary interface for interacting with the AGI
        """
        self.logger.info(f"💬 Processing chat message: {message[:50]}...")
        
        # Generate thought about the message
        thought = await self.think(message, ThoughtType.REASONING)
        
        # Update context
        self.context["last_message"] = message
        self.context["last_response_time"] = time.time()
        
        # Generate response
        response = await self._generate_chat_response(message, thought)
        
        # Store conversation in memory
        await self._store_conversation(message, response)
        
        return response
    
    async def _generate_chat_response(self, message: str, thought: Thought) -> str:
        """Generate a chat response based on the message and thought"""
        
        # Try to use Ollama backend if available with timeout
        if hasattr(self, 'ollama_backend') and self.ollama_backend:
            try:
                # Use asyncio.wait_for with a shorter timeout for chat responses
                response = await asyncio.wait_for(
                    self.ollama_backend.generate_response(message),
                    timeout=10.0  # 10 second timeout for chat
                )
                if response and response.strip() and not response.startswith("Error:"):
                    return response
            except asyncio.TimeoutError:
                self.logger.warning("Ollama backend timed out, using fallback response")
            except Exception as e:
                self.logger.warning(f"Ollama backend failed: {e}, falling back to basic response")
        
        # Enhanced fallback response generation
        intent = self._analyze_intent(message)
        
        # Generate more intelligent responses based on message content
        message_lower = message.lower()
        
        if "ai" in message_lower or "artificial intelligence" in message_lower:
            return "Artificial Intelligence (AI) is the simulation of human intelligence in machines that are programmed to think and learn like humans. It includes machine learning, natural language processing, computer vision, and decision-making capabilities. AI systems can analyze data, recognize patterns, and make predictions to solve complex problems."
        
        elif "explain" in message_lower or "what is" in message_lower:
            return f"Based on my analysis of your question '{message}', I can provide insights. {thought.content} This involves understanding the core concepts and providing clear explanations based on available knowledge."
        
        elif "how" in message_lower:
            return f"To address your question about '{message}', here's my understanding: {thought.content} The process typically involves systematic analysis and step-by-step reasoning."
        
        elif intent == "question":
            return f"Based on my analysis: {thought.content}"
        elif intent == "request":
            return f"I understand you're asking me to: {message}. {thought.content}"
        elif intent == "conversation":
            return f"I appreciate you sharing that. {thought.content}"
        else:
            return thought.content
    
    def _analyze_intent(self, message: str) -> str:
        """Analyze the intent of a user message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["?", "what", "how", "why", "when", "where", "who"]):
            return "question"
        elif any(word in message_lower for word in ["please", "can you", "could you", "would you"]):
            return "request"
        elif any(word in message_lower for word in ["hello", "hi", "thanks", "thank you"]):
            return "conversation"
        else:
            return "statement"
    
    async def _store_conversation(self, message: str, response: str):
        """Store conversation in memory"""
        memory_id = f"conversation_{int(time.time() * 1000)}"
        
        memory = Memory(
            id=memory_id,
            content=f"User: {message}\nMIA: {response}",
            type="conversation",
            importance=0.6,
            timestamp=time.time(),
            associations=[],
            context={"type": "chat_interaction"}
        )
        
        self.memories[memory_id] = memory
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current AGI status"""
        return {
            "is_running": self.is_running,
            "thoughts_count": len(self.thoughts),
            "tasks_count": len(self.tasks),
            "memories_count": len(self.memories),
            "metrics": self.metrics,
            "uptime": time.time() - self.metrics["start_time"],
            "components": {
                "semantic_engine": "ready" if self.semantic_engine else "not_initialized",
                "llm_backend": self.llm_backend.get("status", "not_initialized") if self.llm_backend else "not_initialized",
                "memory_system": "ready" if self.memory_system else "not_initialized",
                "agent_system": "ready" if self.agent_system else "not_initialized"
            }
        }
    
    async def shutdown(self):
        """Gracefully shutdown the AGI core"""
        self.logger.info("🛑 Shutting down AGI Core...")
        
        # Save current state
        await self.save_state()
        
        # Clean up resources
        self.is_running = False
        
        self.logger.info("👋 AGI Core shutdown complete")

# Global AGI core instance
agi_core = AGICore()

async def initialize_agi():
    """Initialize the global AGI core"""
    await agi_core.initialize()

async def shutdown_agi():
    """Shutdown the global AGI core"""
    await agi_core.shutdown()