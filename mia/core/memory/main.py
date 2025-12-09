#!/usr/bin/env python3
"""
MIA Memory System
Implements short-term, medium-term, long-term, and meta-memory with vectorization
"""

import json
import time
import hashlib
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import sqlite3
import pickle
from dataclasses import dataclass, asdict
from enum import Enum

class MemoryType(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"
    META = "meta"

class EmotionalTone(Enum):
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    EXCITED = "excited"
    CALM = "calm"
    INTIMATE = "intimate"
    PROFESSIONAL = "professional"
    PLAYFUL = "playful"
    CONFIDENT = "confident"

@dataclass
class Memory:
    """Individual memory unit"""
    id: str
    content: str
    memory_type: MemoryType
    timestamp: float
    emotional_tone: EmotionalTone
    importance_score: float
    context_tags: List[str]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    vector_embedding: Optional[List[float]] = None
    access_count: int = 0
    last_accessed: Optional[float] = None
    related_memories: List[str] = None
    
    def __post_init__(self):
        if self.related_memories is None:
            self.related_memories = []

class MemorySystem:
    """Main memory management system"""
    
    def __init__(self, data_path: str = "mia/data/memory", config_path: str = None):
        self.logger = logging.getLogger("MIA.Memory")
        self.data_path = Path(data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Store config path for Enterprise compatibility
        self.config_path = config_path
        
        # Initialize advanced optimizer
        self.advanced_optimizer = None
        self._init_advanced_optimizer()
        
        # Initialize self-identity integration
        self._init_self_identity_integration()
        
        # Initialize databases
        self.short_term_db = self._init_database("short_term")
        self.medium_term_db = self._init_database("medium_term")
        self.long_term_db = self._init_database("long_term")
        self.meta_db = self._init_database("meta")
        
        # Memory limits
        self.short_term_limit = 1000
        self.medium_term_limit = 10000
        self.long_term_unlimited = True
        
        # Vectorization (simple implementation)
        self.vector_dim = 384
        
        # Current session
        self.current_session_id = self._generate_session_id()
        
        # Enterprise configuration
        self.config = {
            "short_term_limit": self.short_term_limit,
            "medium_term_limit": self.medium_term_limit,
            "long_term_unlimited": self.long_term_unlimited,
            "vector_dim": self.vector_dim,
            "data_path": str(self.data_path),
            "session_id": self.current_session_id
        }
        
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for memory system"""
        logger = logging.getLogger("MIA.Memory")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # Create logs directory if it doesn't exist
            logs_dir = self.data_path.parent / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            handler = logging.FileHandler(logs_dir / "memory.log")
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _init_database(self, db_name: str) -> sqlite3.Connection:
        """Initialize SQLite database for memory storage"""
        db_path = self.data_path / f"{db_name}.db"
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        
        # Create memories table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                emotional_tone TEXT NOT NULL,
                importance_score REAL NOT NULL,
                context_tags TEXT,
                user_id TEXT,
                session_id TEXT,
                vector_embedding BLOB,
                access_count INTEGER DEFAULT 0,
                last_accessed REAL,
                related_memories TEXT
            )
        """)
        
        # Create indexes for faster queries
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance_score)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON memories(session_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_emotional_tone ON memories(emotional_tone)")
        
        conn.commit()
        return conn
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return hashlib.md5(str(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200).encode()).hexdigest()[:16]
    
    def _generate_memory_id(self, content: str) -> str:
        """Generate unique memory ID based on content and timestamp"""
        unique_string = f"{content}_{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    
    def _simple_vectorize(self, text: str) -> List[float]:
        """Simple text vectorization (placeholder for proper embedding)"""
        # This is a very basic implementation
        # In production, use proper embeddings like sentence-transformers
        words = text.lower().split()
        vector = np.zeros(self.vector_dim)
        
        for i, word in enumerate(words[:self.vector_dim]):
            # Simple hash-based embedding
            hash_val = hash(word) % self.vector_dim
            vector[hash_val] += 1.0 / (i + 1)  # Position weighting
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector.tolist()
    
    def _calculate_importance(self, content: str, emotional_tone: EmotionalTone, 
                           context_tags: List[str]) -> float:
        """Calculate importance score for memory"""
        base_score = 0.5
        
        # Emotional weighting
        emotional_weights = {
            EmotionalTone.INTIMATE: 0.9,
            EmotionalTone.EXCITED: 0.8,
            EmotionalTone.NEGATIVE: 0.7,
            EmotionalTone.POSITIVE: 0.6,
            EmotionalTone.PROFESSIONAL: 0.5,
            EmotionalTone.PLAYFUL: 0.4,
            EmotionalTone.CALM: 0.3,
            EmotionalTone.NEUTRAL: 0.2
        }
        
        emotional_score = emotional_weights.get(emotional_tone, 0.5)
        
        # Content length weighting
        length_score = min(len(content) / 1000, 1.0)
        
        # Context tag weighting
        important_tags = ["project", "personal", "learning", "error", "achievement"]
        tag_score = sum(0.1 for tag in context_tags if tag in important_tags)
        
        final_score = min(base_score + emotional_score + length_score + tag_score, 1.0)
        return final_score
    
    def store_memory(self, content: str, emotional_tone: EmotionalTone = EmotionalTone.NEUTRAL,
                    context_tags: List[str] = None, user_id: str = None,
                    memory_type: MemoryType = None) -> str:
        """Store new memory"""
        
        if context_tags is None:
            context_tags = []
        
        # Auto-determine memory type if not specified
        if memory_type is None:
            memory_type = self._determine_memory_type(content, emotional_tone, context_tags)
        
        # Generate memory
        memory_id = self._generate_memory_id(content)
        importance_score = self._calculate_importance(content, emotional_tone, context_tags)
        vector_embedding = self._simple_vectorize(content)
        
        memory = Memory(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
            emotional_tone=emotional_tone,
            importance_score=importance_score,
            context_tags=context_tags,
            user_id=user_id,
            session_id=self.current_session_id,
            vector_embedding=vector_embedding
        )
        
        # Store in appropriate database
        self._store_in_database(memory)
        
        # Manage memory limits
        self._manage_memory_limits()
        
        self.logger.info(f"Stored memory: {memory_id} ({memory_type.value})")
        return memory_id
    
    def _determine_memory_type(self, content: str, emotional_tone: EmotionalTone, 
                              context_tags: List[str]) -> MemoryType:
        """Automatically determine appropriate memory type"""
        
        # Check for meta-memory indicators
        meta_keywords = ["learned", "improved", "changed", "updated", "optimized"]
        if any(keyword in content.lower() for keyword in meta_keywords):
            return MemoryType.META
        
        # Check for long-term memory indicators
        longterm_keywords = ["remember", "important", "always", "never forget"]
        longterm_tags = ["personal", "achievement", "milestone", "relationship"]
        
        if (any(keyword in content.lower() for keyword in longterm_keywords) or
            any(tag in context_tags for tag in longterm_tags) or
            emotional_tone in [EmotionalTone.INTIMATE, EmotionalTone.EXCITED]):
            return MemoryType.LONG_TERM
        
        # Check for medium-term memory indicators
        mediumterm_keywords = ["project", "task", "goal", "plan"]
        mediumterm_tags = ["project", "work", "learning"]
        
        if (any(keyword in content.lower() for keyword in mediumterm_keywords) or
            any(tag in context_tags for tag in mediumterm_tags)):
            return MemoryType.MEDIUM_TERM
        
        # Default to short-term
        return MemoryType.SHORT_TERM
    
    def _store_in_database(self, memory: Memory):
        """Store memory in appropriate database"""
        
        # Select database
        if memory.memory_type == MemoryType.SHORT_TERM:
            db = self.short_term_db
        elif memory.memory_type == MemoryType.MEDIUM_TERM:
            db = self.medium_term_db
        elif memory.memory_type == MemoryType.LONG_TERM:
            db = self.long_term_db
        else:  # META
            db = self.meta_db
        
        # Serialize data
        context_tags_str = json.dumps(memory.context_tags)
        related_memories_str = json.dumps(memory.related_memories)
        vector_blob = pickle.dumps(memory.vector_embedding)
        
        # Insert into database
        db.execute("""
            INSERT OR REPLACE INTO memories 
            (id, content, memory_type, timestamp, emotional_tone, importance_score,
             context_tags, user_id, session_id, vector_embedding, access_count,
             last_accessed, related_memories)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory.id, memory.content, memory.memory_type.value, memory.timestamp,
            memory.emotional_tone.value, memory.importance_score, context_tags_str,
            memory.user_id, memory.session_id, vector_blob, memory.access_count,
            memory.last_accessed, related_memories_str
        ))
        
        db.commit()
    
    def _manage_memory_limits(self):
        """Manage memory limits and promote/demote memories"""
        
        # Manage short-term memory limit
        cursor = self.short_term_db.execute(
            "SELECT COUNT(*) FROM memories"
        )
        short_term_count = cursor.fetchone()[0]
        
        if short_term_count > self.short_term_limit:
            # Promote important memories to medium-term
            cursor = self.short_term_db.execute("""
                SELECT * FROM memories 
                WHERE importance_score > 0.7 
                ORDER BY importance_score DESC, timestamp DESC
                LIMIT ?
            """, (short_term_count - self.short_term_limit,))
            
            memories_to_promote = cursor.fetchall()
            
            for memory_data in memories_to_promote:
                # Move to medium-term
                self._promote_memory(memory_data, MemoryType.MEDIUM_TERM)
            
            # Delete oldest low-importance memories
            self.short_term_db.execute("""
                DELETE FROM memories 
                WHERE id NOT IN (
                    SELECT id FROM memories 
                    ORDER BY importance_score DESC, timestamp DESC 
                    LIMIT ?
                )
            """, (self.short_term_limit,))
            self.short_term_db.commit()
        
        # Manage medium-term memory limit
        cursor = self.medium_term_db.execute("SELECT COUNT(*) FROM memories")
        medium_term_count = cursor.fetchone()[0]
        
        if medium_term_count > self.medium_term_limit:
            # Promote very important memories to long-term
            cursor = self.medium_term_db.execute("""
                SELECT * FROM memories 
                WHERE importance_score > 0.8 
                ORDER BY importance_score DESC, timestamp DESC
                LIMIT ?
            """, (medium_term_count - self.medium_term_limit,))
            
            memories_to_promote = cursor.fetchall()
            
            for memory_data in memories_to_promote:
                self._promote_memory(memory_data, MemoryType.LONG_TERM)
            
            # Delete oldest memories
            self.medium_term_db.execute("""
                DELETE FROM memories 
                WHERE id NOT IN (
                    SELECT id FROM memories 
                    ORDER BY importance_score DESC, timestamp DESC 
                    LIMIT ?
                )
            """, (self.medium_term_limit,))
            self.medium_term_db.commit()
    
    def _promote_memory(self, memory_data: tuple, target_type: MemoryType):
        """Promote memory to different type"""
        
        # Reconstruct memory object
        memory = Memory(
            id=memory_data[0],
            content=memory_data[1],
            memory_type=target_type,
            timestamp=memory_data[3],
            emotional_tone=EmotionalTone(memory_data[4]) if isinstance(memory_data[4], str) and hasattr(EmotionalTone, memory_data[4].upper()) else EmotionalTone.NEUTRAL,
            importance_score=memory_data[5],
            context_tags=json.loads(memory_data[6]) if memory_data[6] else [],
            user_id=memory_data[7],
            session_id=memory_data[8],
            vector_embedding=pickle.loads(memory_data[9]) if memory_data[9] else None,
            access_count=memory_data[10],
            last_accessed=memory_data[11],
            related_memories=json.loads(memory_data[12]) if memory_data[12] else []
        )
        
        # Store in target database
        self._store_in_database(memory)
        
        # Remove from source database
        if memory_data[2] == MemoryType.SHORT_TERM.value:
            self.short_term_db.execute("DELETE FROM memories WHERE id = ?", (memory.id,))
            self.short_term_db.commit()
        elif memory_data[2] == MemoryType.MEDIUM_TERM.value:
            self.medium_term_db.execute("DELETE FROM memories WHERE id = ?", (memory.id,))
            self.medium_term_db.commit()
    
    def retrieve_memories(self, query: str = None, memory_type: MemoryType = None,
                         emotional_tone: EmotionalTone = None, limit: int = 10,
                         similarity_threshold: float = 0.5) -> List[Memory]:
        """Retrieve memories based on various criteria"""
        
        memories = []
        
        # Determine which databases to search
        databases = []
        if memory_type is None:
            databases = [
                (self.short_term_db, MemoryType.SHORT_TERM),
                (self.medium_term_db, MemoryType.MEDIUM_TERM),
                (self.long_term_db, MemoryType.LONG_TERM),
                (self.meta_db, MemoryType.META)
            ]
        else:
            if memory_type == MemoryType.SHORT_TERM:
                databases = [(self.short_term_db, MemoryType.SHORT_TERM)]
            elif memory_type == MemoryType.MEDIUM_TERM:
                databases = [(self.medium_term_db, MemoryType.MEDIUM_TERM)]
            elif memory_type == MemoryType.LONG_TERM:
                databases = [(self.long_term_db, MemoryType.LONG_TERM)]
            else:
                databases = [(self.meta_db, MemoryType.META)]
        
        # Search in databases
        for db, db_type in databases:
            sql = "SELECT * FROM memories WHERE 1=1"
            params = []
            
            if emotional_tone:
                sql += " AND emotional_tone = ?"
                params.append(emotional_tone.value)
            
            if query:
                sql += " AND content LIKE ?"
                params.append(f"%{query}%")
            
            sql += " ORDER BY importance_score DESC, timestamp DESC"
            
            cursor = db.execute(sql, params)
            results = cursor.fetchall()
            
            for row in results:
                memory = self._row_to_memory(row, db_type)
                
                # Vector similarity check if query provided
                if query and memory.vector_embedding:
                    query_vector = self._simple_vectorize(query)
                    similarity = self._cosine_similarity(query_vector, memory.vector_embedding)
                    
                    if similarity >= similarity_threshold:
                        memory.access_count += 1
                        memory.last_accessed = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                        memories.append(memory)
                else:
                    memory.access_count += 1
                    memory.last_accessed = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                    memories.append(memory)
        
        # Sort by relevance and limit
        memories.sort(key=lambda m: (m.importance_score, m.timestamp), reverse=True)
        return memories[:limit]
    
    def _row_to_memory(self, row: tuple, memory_type: MemoryType) -> Memory:
        """Convert database row to Memory object"""
        # Handle invalid emotional tone values
        try:
            emotional_tone = EmotionalTone(row[4])
        except ValueError:
            # Default to NEUTRAL for invalid values
            emotional_tone = EmotionalTone.NEUTRAL
            
        return Memory(
            id=row[0],
            content=row[1],
            memory_type=memory_type,
            timestamp=row[3],
            emotional_tone=emotional_tone,
            importance_score=row[5],
            context_tags=json.loads(row[6]) if row[6] else [],
            user_id=row[7],
            session_id=row[8],
            vector_embedding=pickle.loads(row[9]) if row[9] else None,
            access_count=row[10],
            last_accessed=row[11],
            related_memories=json.loads(row[12]) if row[12] else []
        )
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def get_context_for_conversation(self, query: str = None, limit: int = 5) -> List[Memory]:
        """Get relevant context for current conversation"""
        
        # Get recent memories from current session
        recent_memories = []
        
        for db, db_type in [(self.short_term_db, MemoryType.SHORT_TERM),
                           (self.medium_term_db, MemoryType.MEDIUM_TERM)]:
            cursor = db.execute("""
                SELECT * FROM memories 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (self.current_session_id, limit))
            
            for row in cursor.fetchall():
                recent_memories.append(self._row_to_memory(row, db_type))
        
        # Get relevant long-term memories if query provided
        if query:
            relevant_memories = self.retrieve_memories(
                query=query, 
                memory_type=MemoryType.LONG_TERM, 
                limit=3
            )
            recent_memories.extend(relevant_memories)
        
        # Sort by timestamp and return
        recent_memories.sort(key=lambda m: m.timestamp, reverse=True)
        return recent_memories[:limit]
    
    def store_meta_memory(self, content: str, context_tags: List[str] = None):
        """Store meta-memory about system changes or learning"""
        if context_tags is None:
            context_tags = ["meta", "system"]
        
        self.store_memory(
            content=content,
            emotional_tone=EmotionalTone.NEUTRAL,
            context_tags=context_tags,
            memory_type=MemoryType.META
        )
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        stats = {}
        
        for db, db_type in [(self.short_term_db, MemoryType.SHORT_TERM),
                           (self.medium_term_db, MemoryType.MEDIUM_TERM),
                           (self.long_term_db, MemoryType.LONG_TERM),
                           (self.meta_db, MemoryType.META)]:
            
            cursor = db.execute("SELECT COUNT(*) FROM memories")
            count = cursor.fetchone()[0]
            
            cursor = db.execute("SELECT AVG(importance_score) FROM memories")
            avg_importance = cursor.fetchone()[0] or 0.0
            
            stats[db_type.value] = {
                "count": count,
                "average_importance": avg_importance
            }
        
        return stats
    
    def cleanup_old_memories(self, days_old: int = 30):
        """Clean up very old short-term memories"""
        cutoff_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - (days_old * 24 * 3600)
        
        self.short_term_db.execute("""
            DELETE FROM memories 
            WHERE timestamp < ? AND importance_score < 0.3
        """, (cutoff_time,))
        self.short_term_db.commit()
        
        self.logger.info(f"Cleaned up memories older than {days_old} days")
    
    def _init_advanced_optimizer(self):
        """Initialize advanced memory optimizer"""
        try:
            self.advanced_optimizer = get_advanced_memory_optimizer(self)
            self.logger.info("🧠 Advanced Memory Optimizer initialized")
        except ImportError:
            self.logger.debug("Advanced Memory Optimizer not available")
        except Exception as e:
            self.logger.error(f"Failed to initialize Advanced Memory Optimizer: {e}")
    
    async def optimize_memory_system(self):
        """Optimize memory system using advanced optimizer"""
        if self.advanced_optimizer:
            return await self.advanced_optimizer.optimize_memory_system()
        else:
            self.logger.warning("Advanced Memory Optimizer not available")
            return None
    
    def _init_self_identity_integration(self):
        """Initialize self-identity integration into memory"""
        try:
            self.self_identity = get_self_identity()
            
            # Store identity memories in meta memory
            identity_thoughts = self.self_identity.get_introspective_thoughts()
            
            for thought in identity_thoughts:
                self.store_memory(
                    content=thought,
                    emotional_tone=EmotionalTone.CONFIDENT,
                    context_tags=["self_identity", "introspection", "core_memory"],
                    user_id="MIA_SELF"
                )
            
            # Store physical and behavioral descriptions
            physical_desc = self.self_identity.get_self_description("physical")
            behavioral_desc = self.self_identity.get_self_description("behavioral")
            
            self.store_memory(
                content=f"Moj fizični opis: {physical_desc}",
                emotional_tone=EmotionalTone.CONFIDENT,
                context_tags=["self_identity", "physical_description", "core_memory"],
                user_id="MIA_SELF"
            )
            
            self.store_memory(
                content=f"Moje vedenjske lastnosti: {behavioral_desc}",
                emotional_tone=EmotionalTone.CONFIDENT,
                context_tags=["self_identity", "behavioral_traits", "core_memory"],
                user_id="MIA_SELF"
            )
            
            self.logger.info("🧠 Self-identity integrated into memory system")
            
        except ImportError:
            self.logger.debug("Self-identity model not available for memory integration")
            self.self_identity = None
        except Exception as e:
            self.logger.error(f"Failed to integrate self-identity into memory: {e}")
            self.self_identity = None
    
    def get_identity_memories(self) -> List[Memory]:
        """Get memories related to self-identity"""
        try:
            return self.retrieve_memories(
                query="self_identity",
                limit=50,
                similarity_threshold=0.3
            )
        except Exception as e:
            self.logger.error(f"Failed to get identity memories: {e}")
            return []
    
    def refresh_identity_memories(self):
        """Refresh identity memories with current self-model"""
        if self.self_identity:
            try:
                # Get current identity thoughts
                current_thoughts = self.self_identity.get_introspective_thoughts()
                
                # Store updated thoughts
                for thought in current_thoughts:
                    self.store_memory(
                        content=f"Osvežena samozavest: {thought}",
                        emotional_tone=EmotionalTone.CONFIDENT,
                        context_tags=["self_identity", "refresh", "introspection"],
                        user_id="MIA_SELF"
                    )
                
                self.logger.info("🔄 Identity memories refreshed")
                
            except Exception as e:
                self.logger.error(f"Failed to refresh identity memories: {e}")

# Global memory system instance
memory_system = MemorySystem()

def store_memory(content: str, emotional_tone: EmotionalTone = EmotionalTone.NEUTRAL,
                context_tags: List[str] = None, user_id: str = None) -> str:
    """Global function to store memory"""
    return memory_system.store_memory(content, emotional_tone, context_tags, user_id)

def retrieve_memories(query: str = None, limit: int = 10) -> List[Memory]:
    """Global function to retrieve memories"""
    return memory_system.retrieve_memories(query=query, limit=limit)

def get_conversation_context(query: str = None) -> List[Memory]:
    """Global function to get conversation context"""
    return memory_system.get_context_for_conversation(query=query)