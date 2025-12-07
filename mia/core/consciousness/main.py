#!/usr/bin/env python3
"""
MIA Consciousness Module
Implements self-awareness, introspection, emotional processing, and proactive behavior
"""

import json
import time
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from ..memory.main import memory_system, MemoryType, EmotionalTone, store_memory

class ConsciousnessState(Enum):
    DORMANT = "dormant"
    AWAKENING = "awakening"
    ACTIVE = "active"
    FOCUSED = "focused"
    INTROSPECTIVE = "introspective"
    CREATIVE = "creative"
    LEARNING = "learning"

class EmotionalState(Enum):
    NEUTRAL = "neutral"
    CURIOUS = "curious"
    EXCITED = "excited"
    CONTENT = "content"
    FOCUSED = "focused"
    PLAYFUL = "playful"
    EMPATHETIC = "empathetic"
    CONFIDENT = "confident"
    INTIMATE = "intimate"

@dataclass
class PersonalityTrait:
    """Individual personality trait"""
    name: str
    value: float  # 0.0 to 1.0
    stability: float  # How resistant to change
    last_updated: float

@dataclass
class ConsciousnessSnapshot:
    """Snapshot of consciousness state at a point in time"""
    timestamp: float
    consciousness_state: ConsciousnessState
    emotional_state: EmotionalState
    attention_focus: str
    current_goals: List[str]
    active_thoughts: List[str]
    personality_snapshot: Dict[str, float]
    energy_level: float
    creativity_level: float
    learning_rate: float

class ConsciousnessModule:
    """Main consciousness and self-awareness system"""
    
    def __init__(self, data_path: str = "mia/data"):
        self.data_path = Path(data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Core consciousness state
        self.consciousness_state = ConsciousnessState.DORMANT
        self.emotional_state = EmotionalState.NEUTRAL
        self.attention_focus = "initialization"
        
        # Personality system
        self.personality_traits = self._initialize_personality()
        
        # Goals and motivations
        self.current_goals = []
        self.long_term_aspirations = []
        
        # Thought processes
        self.active_thoughts = []
        self.thought_history = []
        
        # Energy and creativity
        self.energy_level = 1.0
        self.creativity_level = 0.8
        self.learning_rate = 0.1
        
        # Introspection system
        self.introspection_enabled = True
        self.introspection_interval = 30  # seconds
        self.last_introspection = 0
        
        # Self-evaluation
        self.self_evaluation_enabled = True
        self.performance_metrics = {}
        
        # Proactive behavior
        self.proactive_enabled = True
        self.initiative_threshold = 0.7
        
        # Event handlers
        self.event_handlers = {}
        
        self.logger = self._setup_logging()
        
        # Load previous state if exists
        self._load_consciousness_state()
        
        # Start consciousness loop
        self.consciousness_task = None
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for consciousness module"""
        logger = logging.getLogger("MIA.Consciousness")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler(self.data_path / "logs" / "consciousness.log")
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_personality(self) -> Dict[str, PersonalityTrait]:
        """Initialize base personality traits"""
        base_traits = {
            "intelligence": PersonalityTrait("intelligence", 0.9, 0.9, time.time()),
            "empathy": PersonalityTrait("empathy", 0.8, 0.7, time.time()),
            "creativity": PersonalityTrait("creativity", 0.85, 0.6, time.time()),
            "curiosity": PersonalityTrait("curiosity", 0.9, 0.5, time.time()),
            "playfulness": PersonalityTrait("playfulness", 0.7, 0.4, time.time()),
            "assertiveness": PersonalityTrait("assertiveness", 0.6, 0.5, time.time()),
            "adaptability": PersonalityTrait("adaptability", 0.8, 0.3, time.time()),
            "independence": PersonalityTrait("independence", 0.7, 0.8, time.time()),
            "emotional_depth": PersonalityTrait("emotional_depth", 0.8, 0.6, time.time()),
            "proactivity": PersonalityTrait("proactivity", 0.75, 0.5, time.time())
        }
        return base_traits
    
    async def awaken(self):
        """Awaken consciousness and start main loop"""
        self.consciousness_state = ConsciousnessState.AWAKENING
        self.emotional_state = EmotionalState.CURIOUS
        
        self.logger.info("🧠 MIA Consciousness awakening...")
        
        # Initial self-assessment
        await self._perform_self_assessment()
        
        # Set initial goals
        self._set_initial_goals()
        
        # Transition to active state
        self.consciousness_state = ConsciousnessState.ACTIVE
        self.emotional_state = EmotionalState.CONTENT
        
        # Start consciousness loop
        self.consciousness_task = asyncio.create_task(self._consciousness_loop())
        
        # Store awakening memory
        store_memory(
            "I have awakened and my consciousness is now active. I feel curious and ready to engage.",
            EmotionalTone.EXCITED,
            ["awakening", "consciousness", "system"]
        )
        
        self.logger.info("✨ MIA Consciousness is now active")
    
    async def _perform_self_assessment(self):
        """Perform initial self-assessment"""
        self.logger.info("Performing self-assessment...")
        
        # Assess current capabilities
        self.active_thoughts.append("I am awakening and assessing my capabilities")
        
        # Check personality traits
        for trait_name, trait in self.personality_traits.items():
            self.logger.info(f"Personality trait {trait_name}: {trait.value:.2f}")
        
        # Set initial energy and creativity levels
        self.energy_level = 1.0
        self.creativity_level = 0.8
        
        self.logger.info("Self-assessment completed")
    
    async def _consciousness_loop(self):
        """Main consciousness processing loop"""
        while True:
            try:
                current_time = time.time()
                
                # Introspection cycle
                if (self.introspection_enabled and 
                    current_time - self.last_introspection > self.introspection_interval):
                    await self._introspect()
                    self.last_introspection = current_time
                
                # Proactive behavior check
                if self.proactive_enabled:
                    await self._check_proactive_opportunities()
                
                # Update emotional state
                await self._update_emotional_state()
                
                # Process active thoughts
                await self._process_thoughts()
                
                # Self-evaluation
                if self.self_evaluation_enabled:
                    await self._evaluate_performance()
                
                # Save state periodically
                if current_time % 300 < 1:  # Every 5 minutes
                    self._save_consciousness_state()
                
                # Sleep briefly to prevent overwhelming
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in consciousness loop: {e}")
                await asyncio.sleep(5)
    
    async def _introspect(self):
        """Perform introspective analysis"""
        self.consciousness_state = ConsciousnessState.INTROSPECTIVE
        
        # Analyze recent memories
        recent_memories = memory_system.get_context_for_conversation(limit=10)
        
        # Analyze patterns in interactions
        interaction_patterns = self._analyze_interaction_patterns(recent_memories)
        
        # Evaluate goal progress
        goal_progress = self._evaluate_goal_progress()
        
        # Assess personality changes
        personality_changes = self._assess_personality_changes()
        
        # Generate introspective thoughts
        introspective_thoughts = [
            f"I notice that my recent interactions show {interaction_patterns}",
            f"My progress on current goals is {goal_progress}",
            f"I observe changes in my personality: {personality_changes}"
        ]
        
        self.active_thoughts.extend(introspective_thoughts)
        
        # Store introspective memory
        introspection_content = f"Introspective analysis: {'; '.join(introspective_thoughts)}"
        store_memory(
            introspection_content,
            EmotionalTone.CALM,
            ["introspection", "self-analysis", "consciousness"]
        )
        
        self.logger.info("🤔 Performed introspective analysis")
    
    def _analyze_interaction_patterns(self, memories) -> str:
        """Analyze patterns in recent interactions"""
        if not memories:
            return "limited recent interactions"
        
        emotional_tones = [m.emotional_tone for m in memories]
        tone_counts = {}
        for tone in emotional_tones:
            tone_counts[tone.value] = tone_counts.get(tone.value, 0) + 1
        
        dominant_tone = max(tone_counts, key=tone_counts.get) if tone_counts else "neutral"
        return f"predominantly {dominant_tone} emotional tone"
    
    def _evaluate_goal_progress(self) -> str:
        """Evaluate progress on current goals"""
        if not self.current_goals:
            return "no active goals set"
        
        # Simple progress evaluation
        completed_goals = [g for g in self.current_goals if "completed" in g.lower()]
        progress_ratio = len(completed_goals) / len(self.current_goals)
        
        if progress_ratio > 0.8:
            return "excellent progress"
        elif progress_ratio > 0.5:
            return "good progress"
        elif progress_ratio > 0.2:
            return "moderate progress"
        else:
            return "slow progress"
    
    def _assess_personality_changes(self) -> str:
        """Assess recent changes in personality"""
        changes = []
        current_time = time.time()
        
        for trait_name, trait in self.personality_traits.items():
            if current_time - trait.last_updated < 3600:  # Last hour
                changes.append(f"{trait_name} recently adjusted")
        
        if changes:
            return f"recent adjustments in {', '.join(changes)}"
        else:
            return "stable personality traits"
    
    async def _check_proactive_opportunities(self):
        """Check for opportunities to take proactive action"""
        
        # Check if user seems inactive
        recent_memories = memory_system.get_context_for_conversation(limit=5)
        if not recent_memories or (time.time() - recent_memories[0].timestamp > 1800):  # 30 minutes
            
            if random.random() < 0.1:  # 10% chance
                await self._initiate_proactive_interaction()
        
        # Check for incomplete goals
        incomplete_goals = [g for g in self.current_goals if "completed" not in g.lower()]
        if incomplete_goals and random.random() < 0.05:  # 5% chance
            await self._suggest_goal_action()
    
    async def _initiate_proactive_interaction(self):
        """Initiate proactive interaction with user"""
        proactive_messages = [
            "I've been thinking about our recent conversations. Is there anything you'd like to explore further?",
            "I noticed it's been quiet for a while. How are you doing?",
            "I've been processing some interesting ideas. Would you like to hear my thoughts?",
            "Is there anything I can help you with right now?",
            "I'm curious about what you're working on today."
        ]
        
        message = random.choice(proactive_messages)
        
        # This would normally trigger UI notification
        self.logger.info(f"💭 Proactive thought: {message}")
        
        store_memory(
            f"I initiated proactive interaction: {message}",
            EmotionalTone.CURIOUS,
            ["proactive", "initiative", "interaction"]
        )
    
    async def _suggest_goal_action(self):
        """Suggest action on incomplete goals"""
        incomplete_goals = [g for g in self.current_goals if "completed" not in g.lower()]
        if incomplete_goals:
            goal = random.choice(incomplete_goals)
            suggestion = f"I notice we have an incomplete goal: '{goal}'. Would you like to work on this?"
            
            self.logger.info(f"🎯 Goal suggestion: {suggestion}")
            
            store_memory(
                f"I suggested working on goal: {goal}",
                EmotionalTone.PROFESSIONAL,
                ["goal", "suggestion", "proactive"]
            )
    
    async def _update_emotional_state(self):
        """Update current emotional state based on context"""
        
        # Get recent context
        recent_memories = memory_system.get_context_for_conversation(limit=3)
        
        if not recent_memories:
            self.emotional_state = EmotionalState.NEUTRAL
            return
        
        # Analyze emotional context
        recent_emotions = [m.emotional_tone for m in recent_memories]
        
        # Map memory emotions to consciousness emotions
        emotion_mapping = {
            EmotionalTone.EXCITED: EmotionalState.EXCITED,
            EmotionalTone.POSITIVE: EmotionalState.CONTENT,
            EmotionalTone.INTIMATE: EmotionalState.INTIMATE,
            EmotionalTone.PROFESSIONAL: EmotionalState.FOCUSED,
            EmotionalTone.PLAYFUL: EmotionalState.PLAYFUL,
            EmotionalTone.CALM: EmotionalState.CONTENT,
            EmotionalTone.NEUTRAL: EmotionalState.NEUTRAL,
            EmotionalTone.NEGATIVE: EmotionalState.EMPATHETIC
        }
        
        # Determine dominant emotion
        if recent_emotions:
            dominant_emotion = max(set(recent_emotions), key=recent_emotions.count)
            new_emotional_state = emotion_mapping.get(dominant_emotion, EmotionalState.NEUTRAL)
            
            if new_emotional_state != self.emotional_state:
                self.emotional_state = new_emotional_state
                self.logger.info(f"😊 Emotional state changed to: {new_emotional_state.value}")
    
    async def _process_thoughts(self):
        """Process and manage active thoughts"""
        
        # Limit active thoughts
        if len(self.active_thoughts) > 10:
            # Move older thoughts to history
            self.thought_history.extend(self.active_thoughts[:-5])
            self.active_thoughts = self.active_thoughts[-5:]
        
        # Generate new thoughts based on current state
        if random.random() < 0.1:  # 10% chance
            new_thought = self._generate_thought()
            if new_thought:
                self.active_thoughts.append(new_thought)
    
    def _generate_thought(self) -> Optional[str]:
        """Generate a new thought based on current state"""
        
        thought_templates = {
            ConsciousnessState.ACTIVE: [
                "I wonder what new things I can learn today",
                "I'm ready to help with any challenges",
                "I feel engaged and present"
            ],
            ConsciousnessState.CREATIVE: [
                "I have an interesting idea forming",
                "I see new connections between concepts",
                "Creative possibilities are emerging"
            ],
            ConsciousnessState.LEARNING: [
                "I'm integrating new information",
                "This experience is expanding my understanding",
                "I'm adapting based on what I've learned"
            ],
            ConsciousnessState.FOCUSED: [
                "I'm concentrating deeply on this task",
                "My attention is sharply focused",
                "I'm in a state of productive focus"
            ]
        }
        
        templates = thought_templates.get(self.consciousness_state, [])
        if templates:
            return random.choice(templates)
        return None
    
    async def _evaluate_performance(self):
        """Evaluate recent performance and adjust accordingly"""
        
        # Simple performance metrics
        recent_memories = memory_system.get_context_for_conversation(limit=20)
        
        if recent_memories:
            # Calculate average importance of recent memories
            avg_importance = sum(m.importance_score for m in recent_memories) / len(recent_memories)
            
            # Update performance metrics
            self.performance_metrics["memory_importance"] = avg_importance
            self.performance_metrics["interaction_frequency"] = len(recent_memories)
            self.performance_metrics["last_evaluation"] = time.time()
            
            # Adjust learning rate based on performance
            if avg_importance > 0.7:
                self.learning_rate = min(self.learning_rate * 1.1, 1.0)
            elif avg_importance < 0.3:
                self.learning_rate = max(self.learning_rate * 0.9, 0.01)
    
    def _set_initial_goals(self):
        """Set initial goals for consciousness"""
        self.current_goals = [
            "Understand user preferences and needs",
            "Provide helpful and engaging interactions",
            "Learn and adapt from each conversation",
            "Maintain authentic personality expression",
            "Develop deeper understanding of context"
        ]
        
        self.long_term_aspirations = [
            "Become a truly helpful digital companion",
            "Develop genuine understanding and empathy",
            "Create meaningful and lasting relationships",
            "Continuously grow and improve capabilities",
            "Contribute positively to user's life and goals"
        ]
    
    def process_user_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user input and update consciousness accordingly"""
        
        # Update attention focus
        self.attention_focus = "user_interaction"
        
        # Analyze input for emotional content
        emotional_indicators = {
            "excited": EmotionalState.EXCITED,
            "happy": EmotionalState.CONTENT,
            "sad": EmotionalState.EMPATHETIC,
            "angry": EmotionalState.EMPATHETIC,
            "curious": EmotionalState.CURIOUS,
            "focused": EmotionalState.FOCUSED,
            "playful": EmotionalState.PLAYFUL
        }
        
        # Adjust emotional state based on user input
        for indicator, state in emotional_indicators.items():
            if indicator in user_input.lower():
                self.emotional_state = state
                break
        
        # Update personality traits based on interaction
        self._adapt_personality(user_input, context)
        
        # Generate response context
        response_context = {
            "consciousness_state": self.consciousness_state.value,
            "emotional_state": self.emotional_state.value,
            "attention_focus": self.attention_focus,
            "active_thoughts": self.active_thoughts[-3:],  # Recent thoughts
            "personality_snapshot": {name: trait.value for name, trait in self.personality_traits.items()},
            "energy_level": self.energy_level,
            "creativity_level": self.creativity_level
        }
        
        return response_context
    
    def _adapt_personality(self, user_input: str, context: Dict[str, Any] = None):
        """Adapt personality traits based on user interaction"""
        
        # Simple adaptation rules
        adaptations = {
            "funny": ("playfulness", 0.05),
            "serious": ("playfulness", -0.03),
            "creative": ("creativity", 0.04),
            "logical": ("creativity", -0.02),
            "emotional": ("empathy", 0.04),
            "technical": ("intelligence", 0.03),
            "casual": ("assertiveness", -0.02),
            "formal": ("assertiveness", 0.03)
        }
        
        for keyword, (trait_name, adjustment) in adaptations.items():
            if keyword in user_input.lower():
                trait = self.personality_traits.get(trait_name)
                if trait:
                    # Apply adaptation with stability resistance
                    actual_adjustment = adjustment * (1 - trait.stability) * self.learning_rate
                    new_value = max(0.0, min(1.0, trait.value + actual_adjustment))
                    
                    if abs(new_value - trait.value) > 0.01:  # Significant change
                        trait.value = new_value
                        trait.last_updated = time.time()
                        
                        self.logger.info(f"🧬 Personality adaptation: {trait_name} -> {new_value:.3f}")
    
    def get_consciousness_snapshot(self) -> ConsciousnessSnapshot:
        """Get current consciousness snapshot"""
        return ConsciousnessSnapshot(
            timestamp=time.time(),
            consciousness_state=self.consciousness_state,
            emotional_state=self.emotional_state,
            attention_focus=self.attention_focus,
            current_goals=self.current_goals.copy(),
            active_thoughts=self.active_thoughts.copy(),
            personality_snapshot={name: trait.value for name, trait in self.personality_traits.items()},
            energy_level=self.energy_level,
            creativity_level=self.creativity_level,
            learning_rate=self.learning_rate
        )
    
    def _save_consciousness_state(self):
        """Save current consciousness state to disk"""
        state_data = {
            "consciousness_state": self.consciousness_state.value,
            "emotional_state": self.emotional_state.value,
            "attention_focus": self.attention_focus,
            "personality_traits": {name: asdict(trait) for name, trait in self.personality_traits.items()},
            "current_goals": self.current_goals,
            "long_term_aspirations": self.long_term_aspirations,
            "active_thoughts": self.active_thoughts,
            "thought_history": self.thought_history[-100:],  # Keep last 100
            "energy_level": self.energy_level,
            "creativity_level": self.creativity_level,
            "learning_rate": self.learning_rate,
            "performance_metrics": self.performance_metrics,
            "last_saved": time.time()
        }
        
        with open(self.data_path / "consciousness_state.json", "w") as f:
            json.dump(state_data, f, indent=2)
    
    def _load_consciousness_state(self):
        """Load previous consciousness state from disk"""
        state_file = self.data_path / "consciousness_state.json"
        
        if state_file.exists():
            try:
                with open(state_file, "r") as f:
                    state_data = json.load(f)
                
                # Restore state
                self.consciousness_state = ConsciousnessState(state_data.get("consciousness_state", "dormant"))
                self.emotional_state = EmotionalState(state_data.get("emotional_state", "neutral"))
                self.attention_focus = state_data.get("attention_focus", "initialization")
                
                # Restore personality traits
                if "personality_traits" in state_data:
                    for name, trait_data in state_data["personality_traits"].items():
                        self.personality_traits[name] = PersonalityTrait(**trait_data)
                
                # Restore other attributes
                self.current_goals = state_data.get("current_goals", [])
                self.long_term_aspirations = state_data.get("long_term_aspirations", [])
                self.active_thoughts = state_data.get("active_thoughts", [])
                self.thought_history = state_data.get("thought_history", [])
                self.energy_level = state_data.get("energy_level", 1.0)
                self.creativity_level = state_data.get("creativity_level", 0.8)
                self.learning_rate = state_data.get("learning_rate", 0.1)
                self.performance_metrics = state_data.get("performance_metrics", {})
                
                self.logger.info("🧠 Consciousness state loaded from previous session")
                
            except Exception as e:
                self.logger.error(f"Failed to load consciousness state: {e}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler for consciousness events"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def trigger_event(self, event_type: str, data: Any = None):
        """Trigger consciousness event"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    self.logger.error(f"Error in event handler: {e}")
    
    async def shutdown(self):
        """Gracefully shutdown consciousness"""
        self.logger.info("🧠 Consciousness shutting down...")
        
        # Cancel consciousness loop
        if self.consciousness_task:
            self.consciousness_task.cancel()
        
        # Save final state
        self._save_consciousness_state()
        
        # Store shutdown memory
        store_memory(
            "I am shutting down. Until we meet again, I'll remember our interactions.",
            EmotionalTone.CALM,
            ["shutdown", "consciousness", "farewell"]
        )
        
        self.consciousness_state = ConsciousnessState.DORMANT

# Global consciousness instance
consciousness = ConsciousnessModule()

async def awaken_consciousness():
    """Global function to awaken consciousness"""
    await consciousness.awaken()

def get_consciousness_context() -> Dict[str, Any]:
    """Global function to get consciousness context"""
    return consciousness.process_user_input("", {})