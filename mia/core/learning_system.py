#!/usr/bin/env python3
"""
MIA Learning System - Basic Learning Framework
Implements structured conversation storage, pattern recognition, and knowledge extraction
"""

import os
import json
import logging
import asyncio
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, Counter
import hashlib

class LearningType(Enum):
    """Types of learning"""
    CONVERSATION = "conversation"
    PATTERN = "pattern"
    KNOWLEDGE = "knowledge"
    BEHAVIOR = "behavior"
    PREFERENCE = "preference"

class KnowledgeType(Enum):
    """Types of knowledge"""
    FACTUAL = "factual"
    PROCEDURAL = "procedural"
    CONCEPTUAL = "conceptual"
    PERSONAL = "personal"
    CONTEXTUAL = "contextual"

@dataclass
class ConversationEntry:
    """Single conversation entry"""
    id: str
    timestamp: float
    user_input: str
    ai_response: str
    context: Dict[str, Any]
    sentiment: Optional[str] = None
    topics: List[str] = None
    patterns: List[str] = None

@dataclass
class LearnedPattern:
    """Learned pattern from conversations"""
    id: str
    pattern_type: str
    pattern: str
    frequency: int
    confidence: float
    examples: List[str]
    created_at: float
    last_seen: float

@dataclass
class KnowledgeItem:
    """Extracted knowledge item"""
    id: str
    content: str
    knowledge_type: KnowledgeType
    confidence: float
    source: str
    created_at: float
    updated_at: float
    tags: List[str]
    related_items: List[str]

class LearningSystem:
    """Basic learning system for MIA"""
    
    def __init__(self, data_dir: str = "mia_data"):
        self.data_dir = Path(data_dir)
        self.learning_dir = self.data_dir / "learning"
        self.conversations_dir = self.learning_dir / "conversations"
        self.patterns_dir = self.learning_dir / "patterns"
        self.knowledge_dir = self.learning_dir / "knowledge"
        
        # Create directories
        for dir_path in [self.learning_dir, self.conversations_dir, self.patterns_dir, self.knowledge_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.Learning")
        
        # Learning state
        self.conversations: List[ConversationEntry] = []
        self.patterns: Dict[str, LearnedPattern] = {}
        self.knowledge: Dict[str, KnowledgeItem] = {}
        
        # Learning configuration
        self.config = {
            "max_conversations": 10000,
            "pattern_min_frequency": 3,
            "knowledge_confidence_threshold": 0.7,
            "learning_enabled": True,
            "auto_save_interval": 300,  # 5 minutes
            "pattern_analysis_interval": 3600  # 1 hour
        }
        
        # Load existing data
        self._load_learning_data()
        
        # Background learning will be started when needed
        self._background_task = None
    
    def start_background_learning(self):
        """Start background learning tasks"""
        if self.config["learning_enabled"] and self._background_task is None:
            try:
                self._background_task = asyncio.create_task(self._background_learning_loop())
            except RuntimeError:
                # No event loop running, will start later
                pass
    
    def _load_learning_data(self):
        """Load existing learning data"""
        try:
            # Load conversations
            conversations_file = self.conversations_dir / "conversations.json"
            if conversations_file.exists():
                with open(conversations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversations = [ConversationEntry(**entry) for entry in data]
                self.logger.info(f"📚 Loaded {len(self.conversations)} conversations")
            
            # Load patterns
            patterns_file = self.patterns_dir / "patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.patterns = {k: LearnedPattern(**v) for k, v in data.items()}
                self.logger.info(f"🔍 Loaded {len(self.patterns)} patterns")
            
            # Load knowledge
            knowledge_file = self.knowledge_dir / "knowledge.json"
            if knowledge_file.exists():
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.knowledge = {k: KnowledgeItem(**v) for k, v in data.items()}
                self.logger.info(f"🧠 Loaded {len(self.knowledge)} knowledge items")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to load learning data: {e}")
    
    def _save_learning_data(self):
        """Save learning data to disk"""
        try:
            # Save conversations
            conversations_file = self.conversations_dir / "conversations.json"
            with open(conversations_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(conv) for conv in self.conversations], f, indent=2, ensure_ascii=False)
            
            # Save patterns
            patterns_file = self.patterns_dir / "patterns.json"
            with open(patterns_file, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.patterns.items()}, f, indent=2, ensure_ascii=False)
            
            # Save knowledge
            knowledge_file = self.knowledge_dir / "knowledge.json"
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.knowledge.items()}, f, indent=2, ensure_ascii=False)
                
            self.logger.info("💾 Learning data saved successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save learning data: {e}")
    
    async def learn_from_conversation(self, user_input: str, ai_response: str, context: Dict[str, Any] = None) -> str:
        """Learn from a conversation exchange"""
        if not self.config["learning_enabled"]:
            return "learning_disabled"
        
        try:
            # Create conversation entry
            conv_id = hashlib.md5(f"{user_input}{ai_response}{time.time()}".encode()).hexdigest()[:12]
            
            # Analyze input and response
            topics = self._extract_topics(user_input)
            sentiment = self._analyze_sentiment(user_input)
            patterns = self._identify_patterns(user_input)
            
            conversation = ConversationEntry(
                id=conv_id,
                timestamp=time.time(),
                user_input=user_input,
                ai_response=ai_response,
                context=context or {},
                sentiment=sentiment,
                topics=topics,
                patterns=patterns
            )
            
            # Add to conversations
            self.conversations.append(conversation)
            
            # Limit conversation history
            if len(self.conversations) > self.config["max_conversations"]:
                self.conversations = self.conversations[-self.config["max_conversations"]:]
            
            # Extract knowledge
            await self._extract_knowledge_from_conversation(conversation)
            
            # Update patterns
            await self._update_patterns(conversation)
            
            self.logger.info(f"📖 Learned from conversation: {conv_id}")
            return conv_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to learn from conversation: {e}")
            return "learning_failed"
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        # Simple topic extraction based on keywords
        topics = []
        
        # AI/ML related topics
        ai_keywords = ["ai", "artificial intelligence", "machine learning", "neural network", "deep learning", "llm", "model"]
        tech_keywords = ["programming", "code", "software", "computer", "technology", "algorithm"]
        science_keywords = ["science", "research", "experiment", "theory", "hypothesis"]
        
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ai_keywords):
            topics.append("artificial_intelligence")
        if any(keyword in text_lower for keyword in tech_keywords):
            topics.append("technology")
        if any(keyword in text_lower for keyword in science_keywords):
            topics.append("science")
        
        # Question types
        if text.strip().endswith('?'):
            topics.append("question")
        if any(word in text_lower for word in ["how", "what", "why", "when", "where"]):
            topics.append("inquiry")
        
        return topics
    
    def _analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis"""
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "like"]
        negative_words = ["bad", "terrible", "awful", "hate", "dislike", "horrible", "wrong", "error"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _identify_patterns(self, text: str) -> List[str]:
        """Identify patterns in text"""
        patterns = []
        
        # Question patterns
        if text.strip().endswith('?'):
            if text.lower().startswith('what'):
                patterns.append("what_question")
            elif text.lower().startswith('how'):
                patterns.append("how_question")
            elif text.lower().startswith('why'):
                patterns.append("why_question")
        
        # Greeting patterns
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        if any(greeting in text.lower() for greeting in greetings):
            patterns.append("greeting")
        
        # Request patterns
        request_words = ["please", "can you", "could you", "would you", "help me"]
        if any(word in text.lower() for word in request_words):
            patterns.append("request")
        
        return patterns
    
    async def _extract_knowledge_from_conversation(self, conversation: ConversationEntry):
        """Extract knowledge from conversation"""
        try:
            # Extract factual statements from AI response
            response = conversation.ai_response
            
            # Look for definitions
            if "is a" in response or "are a" in response:
                knowledge_id = hashlib.md5(f"definition_{response}".encode()).hexdigest()[:12]
                
                knowledge_item = KnowledgeItem(
                    id=knowledge_id,
                    content=response,
                    knowledge_type=KnowledgeType.FACTUAL,
                    confidence=0.8,
                    source=f"conversation_{conversation.id}",
                    created_at=time.time(),
                    updated_at=time.time(),
                    tags=conversation.topics or [],
                    related_items=[]
                )
                
                self.knowledge[knowledge_id] = knowledge_item
            
            # Extract procedural knowledge (how-to)
            if "how to" in conversation.user_input.lower() and len(response) > 50:
                knowledge_id = hashlib.md5(f"procedure_{response}".encode()).hexdigest()[:12]
                
                knowledge_item = KnowledgeItem(
                    id=knowledge_id,
                    content=f"Q: {conversation.user_input}\nA: {response}",
                    knowledge_type=KnowledgeType.PROCEDURAL,
                    confidence=0.7,
                    source=f"conversation_{conversation.id}",
                    created_at=time.time(),
                    updated_at=time.time(),
                    tags=conversation.topics or [],
                    related_items=[]
                )
                
                self.knowledge[knowledge_id] = knowledge_item
                
        except Exception as e:
            self.logger.error(f"❌ Failed to extract knowledge: {e}")
    
    async def _update_patterns(self, conversation: ConversationEntry):
        """Update learned patterns"""
        try:
            for pattern in conversation.patterns:
                if pattern in self.patterns:
                    # Update existing pattern
                    self.patterns[pattern].frequency += 1
                    self.patterns[pattern].last_seen = time.time()
                    self.patterns[pattern].examples.append(conversation.user_input[:100])
                    
                    # Limit examples
                    if len(self.patterns[pattern].examples) > 10:
                        self.patterns[pattern].examples = self.patterns[pattern].examples[-10:]
                else:
                    # Create new pattern
                    pattern_id = hashlib.md5(f"pattern_{pattern}".encode()).hexdigest()[:12]
                    
                    learned_pattern = LearnedPattern(
                        id=pattern_id,
                        pattern_type="conversation",
                        pattern=pattern,
                        frequency=1,
                        confidence=0.5,
                        examples=[conversation.user_input[:100]],
                        created_at=time.time(),
                        last_seen=time.time()
                    )
                    
                    self.patterns[pattern] = learned_pattern
                    
        except Exception as e:
            self.logger.error(f"❌ Failed to update patterns: {e}")
    
    async def _background_learning_loop(self):
        """Background learning tasks"""
        while True:
            try:
                # Auto-save data
                await asyncio.sleep(self.config["auto_save_interval"])
                self._save_learning_data()
                
                # Analyze patterns
                await asyncio.sleep(self.config["pattern_analysis_interval"])
                await self._analyze_conversation_patterns()
                
            except Exception as e:
                self.logger.error(f"❌ Background learning error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _analyze_conversation_patterns(self):
        """Analyze conversation patterns for insights"""
        try:
            if len(self.conversations) < 10:
                return
            
            # Analyze recent conversations
            recent_conversations = self.conversations[-100:]
            
            # Topic frequency analysis
            topic_counter = Counter()
            for conv in recent_conversations:
                if conv.topics:
                    topic_counter.update(conv.topics)
            
            # Pattern frequency analysis
            pattern_counter = Counter()
            for conv in recent_conversations:
                if conv.patterns:
                    pattern_counter.update(conv.patterns)
            
            # Update pattern confidence based on frequency
            for pattern_name, pattern in self.patterns.items():
                if pattern.frequency >= self.config["pattern_min_frequency"]:
                    pattern.confidence = min(0.95, pattern.confidence + 0.1)
            
            self.logger.info(f"📊 Analyzed {len(recent_conversations)} conversations")
            
        except Exception as e:
            self.logger.error(f"❌ Pattern analysis failed: {e}")
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        return {
            "conversations_count": len(self.conversations),
            "patterns_count": len(self.patterns),
            "knowledge_count": len(self.knowledge),
            "top_topics": self._get_top_topics(),
            "top_patterns": self._get_top_patterns(),
            "learning_enabled": self.config["learning_enabled"]
        }
    
    def _get_top_topics(self) -> List[Tuple[str, int]]:
        """Get most frequent topics"""
        topic_counter = Counter()
        for conv in self.conversations[-1000:]:  # Last 1000 conversations
            if conv.topics:
                topic_counter.update(conv.topics)
        return topic_counter.most_common(10)
    
    def _get_top_patterns(self) -> List[Tuple[str, int]]:
        """Get most frequent patterns"""
        return [(pattern, data.frequency) for pattern, data in 
                sorted(self.patterns.items(), key=lambda x: x[1].frequency, reverse=True)[:10]]
    
    def search_knowledge(self, query: str) -> List[KnowledgeItem]:
        """Search knowledge base"""
        results = []
        query_lower = query.lower()
        
        for knowledge_item in self.knowledge.values():
            if (query_lower in knowledge_item.content.lower() or 
                any(tag in query_lower for tag in knowledge_item.tags)):
                results.append(knowledge_item)
        
        # Sort by confidence
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:10]
    
    def get_conversation_context(self, limit: int = 5) -> List[ConversationEntry]:
        """Get recent conversation context"""
        return self.conversations[-limit:] if self.conversations else []

# Global learning system instance
learning_system = LearningSystem()