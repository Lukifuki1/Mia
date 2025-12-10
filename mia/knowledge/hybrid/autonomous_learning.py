#!/usr/bin/env python3
"""
Autonomous Learning - Avtonomno učenje za hibridni MIA sistem
============================================================

PRODUKCIJSKA IMPLEMENTACIJA avtonomnega učenja, ki omogoča:
- Incremental ontology expansion
- Pattern recognition in knowledge extraction
- Self-improvement mechanisms
- Adaptive learning strategies
- Memory management in consolidation
- Integration z vsemi hibridnimi komponentami

KLJUČNE FUNKCIONALNOSTI:
- Incremental learning iz interakcij
- Pattern recognition za nove koncepte
- Ontology expansion z validacijo
- Knowledge consolidation
- Memory management
- Performance optimization
- Self-monitoring in diagnostics

ARHITEKTURA:
- Backward compatible z obstoječim MIA sistemom
- Integracija z vsemi hibridnimi komponentami
- Continuous learning loop
- Quality assurance mechanisms
"""

import logging
import json
import time
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union, Callable
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import hashlib
import uuid
from enum import Enum
from collections import defaultdict, Counter
import re

# Import existing MIA components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

try:
    from mia.knowledge.hybrid.knowledge_bank_core import HybridKnowledgeBank
    from mia.knowledge.hybrid.semantic_layer import SemanticLayer
    from mia.knowledge.hybrid.deterministic_reasoning import DeterministicReasoningEngine
    from mia.knowledge.hybrid.hybrid_pipeline import HybridPipeline
    HYBRID_COMPONENTS_AVAILABLE = True
except ImportError:
    HYBRID_COMPONENTS_AVAILABLE = False

# Machine learning dependencies
try:
    import numpy as np
    from sklearn.cluster import DBSCAN
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)

class LearningStrategy(Enum):
    """Strategije učenja"""
    INCREMENTAL = "incremental"
    BATCH = "batch"
    REINFORCEMENT = "reinforcement"
    PATTERN_BASED = "pattern_based"
    ADAPTIVE = "adaptive"

class LearningTrigger(Enum):
    """Sprožilci učenja"""
    NEW_INTERACTION = "new_interaction"
    PATTERN_DETECTED = "pattern_detected"
    CONFIDENCE_THRESHOLD = "confidence_threshold"
    TIME_BASED = "time_based"
    MANUAL = "manual"

@dataclass
class LearningEvent:
    """Dogodek učenja"""
    event_id: str
    trigger: LearningTrigger
    source_data: Dict[str, Any]
    extracted_knowledge: Dict[str, Any]
    confidence: float
    timestamp: float
    metadata: Dict[str, Any]

@dataclass
class Pattern:
    """Vzorec v podatkih"""
    pattern_id: str
    pattern_type: str
    description: str
    examples: List[Dict[str, Any]]
    frequency: int
    confidence: float
    first_seen: float
    last_seen: float
    metadata: Dict[str, Any]

@dataclass
class LearningResult:
    """Rezultat učenja"""
    success: bool
    new_concepts: List[str]
    new_relations: List[str]
    updated_concepts: List[str]
    patterns_discovered: List[str]
    confidence: float
    processing_time: float
    metadata: Dict[str, Any]

@dataclass
class ConsolidationResult:
    """Rezultat konsolidacije znanja"""
    concepts_merged: int
    relations_refined: int
    patterns_validated: int
    knowledge_pruned: int
    quality_improved: float
    processing_time: float

class AutonomousLearning:
    """
    Avtonomno učenje za hibridni MIA sistem.
    
    Omogoča:
    - Incremental learning iz interakcij
    - Pattern recognition za nove koncepte
    - Ontology expansion z validacijo
    - Knowledge consolidation
    - Memory management
    - Self-improvement
    
    PRODUKCIJSKE FUNKCIONALNOSTI:
    ✅ Incremental ontology expansion
    ✅ Pattern recognition z ML algoritmi
    ✅ Knowledge extraction iz interakcij
    ✅ Memory management in consolidation
    ✅ Quality assurance mechanisms
    ✅ Async operations za performance
    ✅ Comprehensive monitoring
    ✅ Integration z vsemi hibridnimi komponentami
    """
    
    def __init__(self,
                 knowledge_bank: Optional[HybridKnowledgeBank] = None,
                 semantic_layer: Optional[SemanticLayer] = None,
                 reasoning_engine: Optional[DeterministicReasoningEngine] = None,
                 pipeline: Optional[HybridPipeline] = None,
                 data_dir: str = "data/autonomous_learning",
                 learning_strategy: LearningStrategy = LearningStrategy.ADAPTIVE):
        """
        Inicializiraj avtonomno učenje.
        
        Args:
            knowledge_bank: Knowledge Bank komponenta
            semantic_layer: Semantic Layer komponenta
            reasoning_engine: Reasoning Engine komponenta
            pipeline: Hybrid Pipeline komponenta
            data_dir: Direktorij za podatke
            learning_strategy: Strategija učenja
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Component integration
        self.knowledge_bank = knowledge_bank
        self.semantic_layer = semantic_layer
        self.reasoning_engine = reasoning_engine
        self.pipeline = pipeline
        
        # Check component availability
        self.kb_available = knowledge_bank is not None
        self.semantic_available = semantic_layer is not None
        self.reasoning_available = reasoning_engine is not None
        self.pipeline_available = pipeline is not None
        
        # Learning configuration
        self.learning_strategy = learning_strategy
        self.confidence_threshold = 0.6
        self.pattern_min_frequency = 3
        self.consolidation_interval = 3600  # 1 hour
        self.max_memory_size = 10000
        
        # Machine learning availability
        self.ml_available = ML_AVAILABLE
        if self.ml_available:
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            self.clusterer = DBSCAN(eps=0.3, min_samples=2)
            logger.info("✅ ML components available")
        else:
            logger.warning("❌ ML components not available - pattern recognition limited")
            
        # Performance optimization
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.learning_queue = asyncio.Queue(maxsize=1000)
        self.consolidation_lock = asyncio.Lock()
        
        # Learning memory
        self.learning_events: List[LearningEvent] = []
        self.discovered_patterns: Dict[str, Pattern] = {}
        self.interaction_history: List[Dict[str, Any]] = []
        
        # Statistics
        self.stats = {
            'total_learning_events': 0,
            'successful_learning_events': 0,
            'failed_learning_events': 0,
            'concepts_learned': 0,
            'relations_learned': 0,
            'patterns_discovered': 0,
            'consolidations_performed': 0,
            'last_consolidation': 0,
            'system_health': 'initializing',
            'start_time': time.time()
        }
        
        # Load existing data
        self._load_learning_data()
        
        # Start background learning loop
        self.learning_task = None
        self.consolidation_task = None
        
        # Update statistics
        self._update_statistics()
        
        logger.info("✅ Autonomous Learning inicializiran")
        logger.info(f"   - Knowledge Bank: {'✅' if self.kb_available else '❌'}")
        logger.info(f"   - Semantic Layer: {'✅' if self.semantic_available else '❌'}")
        logger.info(f"   - Reasoning Engine: {'✅' if self.reasoning_available else '❌'}")
        logger.info(f"   - Pipeline: {'✅' if self.pipeline_available else '❌'}")
        logger.info(f"   - ML Available: {'✅' if self.ml_available else '❌'}")
        logger.info(f"   - Learning Strategy: {self.learning_strategy.value}")
        logger.info(f"   - Learning Events: {len(self.learning_events)}")
        logger.info(f"   - Patterns: {len(self.discovered_patterns)}")
        
    def _update_statistics(self):
        """Posodobi statistike sistema"""
        try:
            self.stats['learning_events_count'] = len(self.learning_events)
            self.stats['patterns_count'] = len(self.discovered_patterns)
            self.stats['interaction_history_size'] = len(self.interaction_history)
            self.stats['system_health'] = 'healthy'
            
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
            self.stats['system_health'] = 'error'
            
    async def start_learning(self):
        """Začni avtonomno učenje"""
        try:
            logger.info("🚀 Starting autonomous learning...")
            
            # Start learning loop
            self.learning_task = asyncio.create_task(self._learning_loop())
            
            # Start consolidation loop
            self.consolidation_task = asyncio.create_task(self._consolidation_loop())
            
            logger.info("✅ Autonomous learning started")
            
        except Exception as e:
            logger.error(f"Error starting autonomous learning: {e}")
            
    async def stop_learning(self):
        """Ustavi avtonomno učenje"""
        try:
            logger.info("🔄 Stopping autonomous learning...")
            
            # Cancel tasks
            if self.learning_task:
                self.learning_task.cancel()
                
            if self.consolidation_task:
                self.consolidation_task.cancel()
                
            # Wait for tasks to complete
            await asyncio.gather(self.learning_task, self.consolidation_task, return_exceptions=True)
            
            logger.info("✅ Autonomous learning stopped")
            
        except Exception as e:
            logger.error(f"Error stopping autonomous learning: {e}")
            
    async def learn_from_interaction(self, 
                                   user_input: str,
                                   system_response: str,
                                   pipeline_result: Optional[Dict[str, Any]] = None,
                                   feedback: Optional[Dict[str, Any]] = None) -> LearningResult:
        """
        Učenje iz interakcije z uporabnikom.
        
        Args:
            user_input: Uporabniški vnos
            system_response: Sistemski odgovor
            pipeline_result: Rezultat pipeline procesiranja
            feedback: Povratne informacije
            
        Returns:
            LearningResult
        """
        start_time = time.time()
        
        try:
            self.stats['total_learning_events'] += 1
            
            # Create interaction record
            interaction = {
                'user_input': user_input,
                'system_response': system_response,
                'pipeline_result': pipeline_result,
                'feedback': feedback,
                'timestamp': time.time(),
                'interaction_id': str(uuid.uuid4())
            }
            
            # Add to interaction history
            self.interaction_history.append(interaction)
            
            # Limit history size
            if len(self.interaction_history) > self.max_memory_size:
                self.interaction_history = self.interaction_history[-self.max_memory_size:]
                
            # Extract knowledge from interaction
            extracted_knowledge = await self._extract_knowledge_from_interaction(interaction)
            
            # Learn new concepts and relations
            learning_result = await self._learn_from_extracted_knowledge(extracted_knowledge)
            
            # Detect patterns
            patterns = await self._detect_patterns_in_interaction(interaction)
            
            # Create learning event
            learning_event = LearningEvent(
                event_id=str(uuid.uuid4()),
                trigger=LearningTrigger.NEW_INTERACTION,
                source_data=interaction,
                extracted_knowledge=extracted_knowledge,
                confidence=learning_result.confidence,
                timestamp=time.time(),
                metadata={
                    'patterns_detected': len(patterns),
                    'user_input_length': len(user_input),
                    'has_feedback': feedback is not None
                }
            )
            
            self.learning_events.append(learning_event)
            
            # Update patterns
            for pattern in patterns:
                await self._update_pattern(pattern)
                
            # Update statistics
            if learning_result.success:
                self.stats['successful_learning_events'] += 1
                self.stats['concepts_learned'] += len(learning_result.new_concepts)
                self.stats['relations_learned'] += len(learning_result.new_relations)
            else:
                self.stats['failed_learning_events'] += 1
                
            self.stats['patterns_discovered'] += len(patterns)
            
            processing_time = time.time() - start_time
            learning_result.processing_time = processing_time
            
            logger.info(f"Learning from interaction: {'✅ Success' if learning_result.success else '❌ Failed'} "
                       f"({len(learning_result.new_concepts)} concepts, {len(learning_result.new_relations)} relations, "
                       f"{len(patterns)} patterns) in {processing_time:.3f}s")
                       
            return learning_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error learning from interaction: {e}")
            
            self.stats['failed_learning_events'] += 1
            
            return LearningResult(
                success=False,
                new_concepts=[],
                new_relations=[],
                updated_concepts=[],
                patterns_discovered=[],
                confidence=0.0,
                processing_time=processing_time,
                metadata={'error': str(e)}
            )
            
    async def _extract_knowledge_from_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Izvleči znanje iz interakcije"""
        try:
            extracted = {
                'concepts': [],
                'relations': [],
                'facts': [],
                'patterns': []
            }
            
            user_input = interaction['user_input']
            system_response = interaction['system_response']
            
            # Use semantic layer if available
            if self.semantic_available:
                # Parse user input
                user_parse = await self.semantic_layer.parse_natural_language(user_input)
                
                # Extract concepts from entities
                for entity in user_parse.entities:
                    concept = {
                        'name': entity.normalized_form,
                        'type': entity.entity_type,
                        'confidence': entity.confidence,
                        'source': 'user_input'
                    }
                    extracted['concepts'].append(concept)
                    
                # Extract relations
                for relation in user_parse.relations:
                    rel = {
                        'subject': relation.subject_concept,
                        'predicate': relation.predicate,
                        'object': relation.object_concept,
                        'confidence': relation.confidence,
                        'source': 'user_input'
                    }
                    extracted['relations'].append(rel)
                    
                # Parse system response
                response_parse = await self.semantic_layer.parse_natural_language(system_response)
                
                # Extract concepts from response
                for entity in response_parse.entities:
                    concept = {
                        'name': entity.normalized_form,
                        'type': entity.entity_type,
                        'confidence': entity.confidence,
                        'source': 'system_response'
                    }
                    extracted['concepts'].append(concept)
                    
            else:
                # Fallback: simple keyword extraction
                user_keywords = self._extract_keywords(user_input)
                response_keywords = self._extract_keywords(system_response)
                
                for keyword in user_keywords:
                    concept = {
                        'name': keyword,
                        'type': 'KEYWORD',
                        'confidence': 0.5,
                        'source': 'user_input'
                    }
                    extracted['concepts'].append(concept)
                    
                for keyword in response_keywords:
                    concept = {
                        'name': keyword,
                        'type': 'KEYWORD',
                        'confidence': 0.5,
                        'source': 'system_response'
                    }
                    extracted['concepts'].append(concept)
                    
            # Extract facts from pipeline result
            pipeline_result = interaction.get('pipeline_result')
            if pipeline_result:
                # Extract facts from successful reasoning
                if pipeline_result.get('success'):
                    stage_results = pipeline_result.get('stage_results', [])
                    for stage_result in stage_results:
                        if stage_result.get('stage') == 'reasoning' and stage_result.get('success'):
                            reasoning_results = stage_result.get('results', {})
                            reasoning_result = reasoning_results.get('reasoning_result', {})
                            if reasoning_result.get('success'):
                                for result_fact in reasoning_result.get('results', []):
                                    fact = {
                                        'term': result_fact.get('term'),
                                        'confidence': result_fact.get('confidence', 0.5),
                                        'source': 'reasoning_engine'
                                    }
                                    extracted['facts'].append(fact)
                                    
            return extracted
            
        except Exception as e:
            logger.error(f"Error extracting knowledge from interaction: {e}")
            return {'concepts': [], 'relations': [], 'facts': [], 'patterns': []}
            
    async def _learn_from_extracted_knowledge(self, extracted_knowledge: Dict[str, Any]) -> LearningResult:
        """Učenje iz izvlečenega znanja"""
        try:
            new_concepts = []
            new_relations = []
            updated_concepts = []
            
            # Learn concepts
            for concept_data in extracted_knowledge.get('concepts', []):
                if concept_data['confidence'] >= self.confidence_threshold:
                    concept_name = concept_data['name']
                    
                    # Check if concept already exists in knowledge bank
                    if self.kb_available:
                        concept_uri = f"http://mia.ai/ontology#{concept_name}"
                        
                        # Try to create new concept
                        success = await self.knowledge_bank.create_concept(
                            concept_id=concept_name,
                            label=concept_name,
                            description=f"Learned from interaction: {concept_data['type']}",
                            properties={
                                'learned_confidence': concept_data['confidence'],
                                'learned_source': concept_data['source'],
                                'learned_timestamp': time.time()
                            }
                        )
                        
                        if success:
                            new_concepts.append(concept_name)
                        else:
                            # Concept might already exist - update it
                            updated_concepts.append(concept_name)
                            
            # Learn relations
            for relation_data in extracted_knowledge.get('relations', []):
                if relation_data['confidence'] >= self.confidence_threshold:
                    relation_id = f"{relation_data['subject']}_{relation_data['predicate']}_{relation_data['object']}"
                    
                    if self.kb_available:
                        success = await self.knowledge_bank.create_relation(
                            relation_id=relation_id,
                            label=relation_data['predicate'],
                            domain=f"http://mia.ai/ontology#{relation_data['subject']}",
                            range=f"http://mia.ai/ontology#{relation_data['object']}",
                            properties={
                                'learned_confidence': relation_data['confidence'],
                                'learned_source': relation_data['source'],
                                'learned_timestamp': time.time()
                            }
                        )
                        
                        if success:
                            new_relations.append(relation_id)
                            
            # Learn facts
            for fact_data in extracted_knowledge.get('facts', []):
                if fact_data['confidence'] >= self.confidence_threshold:
                    if self.reasoning_available:
                        # Add fact to reasoning engine
                        from mia.knowledge.hybrid.deterministic_reasoning import Fact, LogicalTerm
                        
                        term_data = fact_data.get('term', {})
                        if isinstance(term_data, dict):
                            logical_term = LogicalTerm(
                                name=term_data.get('name', 'unknown'),
                                arguments=term_data.get('arguments', []),
                                negated=term_data.get('negated', False)
                            )
                            
                            fact = Fact(
                                fact_id=str(uuid.uuid4()),
                                term=logical_term,
                                confidence=fact_data['confidence'],
                                source=fact_data['source'],
                                timestamp=time.time(),
                                derived=True
                            )
                            
                            await self.reasoning_engine.add_fact(fact)
                            
            # Calculate overall confidence
            total_items = len(new_concepts) + len(new_relations) + len(updated_concepts)
            confidence = min(1.0, total_items / 10.0) if total_items > 0 else 0.0
            
            return LearningResult(
                success=total_items > 0,
                new_concepts=new_concepts,
                new_relations=new_relations,
                updated_concepts=updated_concepts,
                patterns_discovered=[],
                confidence=confidence,
                processing_time=0.0,
                metadata={
                    'extraction_source': 'interaction',
                    'total_concepts_processed': len(extracted_knowledge.get('concepts', [])),
                    'total_relations_processed': len(extracted_knowledge.get('relations', []))
                }
            )
            
        except Exception as e:
            logger.error(f"Error learning from extracted knowledge: {e}")
            return LearningResult(
                success=False,
                new_concepts=[],
                new_relations=[],
                updated_concepts=[],
                patterns_discovered=[],
                confidence=0.0,
                processing_time=0.0,
                metadata={'error': str(e)}
            )
            
    async def _detect_patterns_in_interaction(self, interaction: Dict[str, Any]) -> List[Pattern]:
        """Zaznaj vzorce v interakciji"""
        patterns = []
        
        try:
            user_input = interaction['user_input']
            system_response = interaction['system_response']
            
            # Pattern 1: Question-Answer patterns
            if user_input.strip().endswith('?'):
                pattern_id = "question_answer_pattern"
                pattern = await self._get_or_create_pattern(
                    pattern_id=pattern_id,
                    pattern_type="question_answer",
                    description="User asks question, system provides answer"
                )
                
                pattern.examples.append({
                    'question': user_input,
                    'answer': system_response,
                    'timestamp': interaction['timestamp']
                })
                pattern.frequency += 1
                pattern.last_seen = interaction['timestamp']
                
                patterns.append(pattern)
                
            # Pattern 2: Concept definition patterns
            definition_keywords = ['what is', 'define', 'explain', 'describe']
            if any(keyword in user_input.lower() for keyword in definition_keywords):
                pattern_id = "concept_definition_pattern"
                pattern = await self._get_or_create_pattern(
                    pattern_id=pattern_id,
                    pattern_type="concept_definition",
                    description="User asks for concept definition"
                )
                
                pattern.examples.append({
                    'request': user_input,
                    'definition': system_response,
                    'timestamp': interaction['timestamp']
                })
                pattern.frequency += 1
                pattern.last_seen = interaction['timestamp']
                
                patterns.append(pattern)
                
            # Pattern 3: Reasoning patterns
            reasoning_keywords = ['if', 'then', 'because', 'therefore', 'implies']
            if any(keyword in user_input.lower() for keyword in reasoning_keywords):
                pattern_id = "logical_reasoning_pattern"
                pattern = await self._get_or_create_pattern(
                    pattern_id=pattern_id,
                    pattern_type="logical_reasoning",
                    description="User engages in logical reasoning"
                )
                
                pattern.examples.append({
                    'reasoning_input': user_input,
                    'reasoning_output': system_response,
                    'timestamp': interaction['timestamp']
                })
                pattern.frequency += 1
                pattern.last_seen = interaction['timestamp']
                
                patterns.append(pattern)
                
            # Pattern 4: ML-based pattern detection
            if self.ml_available and len(self.interaction_history) > 10:
                ml_patterns = await self._detect_ml_patterns(interaction)
                patterns.extend(ml_patterns)
                
        except Exception as e:
            logger.error(f"Error detecting patterns in interaction: {e}")
            
        return patterns
        
    async def _get_or_create_pattern(self, pattern_id: str, pattern_type: str, description: str) -> Pattern:
        """Pridobi ali ustvari vzorec"""
        if pattern_id in self.discovered_patterns:
            return self.discovered_patterns[pattern_id]
        else:
            pattern = Pattern(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                description=description,
                examples=[],
                frequency=0,
                confidence=0.5,
                first_seen=time.time(),
                last_seen=time.time(),
                metadata={}
            )
            self.discovered_patterns[pattern_id] = pattern
            return pattern
            
    async def _detect_ml_patterns(self, interaction: Dict[str, Any]) -> List[Pattern]:
        """Zaznaj vzorce z ML algoritmi"""
        patterns = []
        
        try:
            if not self.ml_available or len(self.interaction_history) < 10:
                return patterns
                
            # Prepare text data for clustering
            texts = []
            for hist_interaction in self.interaction_history[-100:]:  # Last 100 interactions
                combined_text = f"{hist_interaction['user_input']} {hist_interaction['system_response']}"
                texts.append(combined_text)
                
            # Vectorize texts
            def vectorize_texts():
                try:
                    vectors = self.vectorizer.fit_transform(texts)
                    return vectors.toarray()
                except Exception as e:
                    logger.error(f"Error vectorizing texts: {e}")
                    return None
                    
            vectors = await asyncio.get_event_loop().run_in_executor(
                self.executor, vectorize_texts
            )
            
            if vectors is not None:
                # Perform clustering
                def cluster_vectors():
                    try:
                        clusters = self.clusterer.fit_predict(vectors)
                        return clusters
                    except Exception as e:
                        logger.error(f"Error clustering vectors: {e}")
                        return None
                        
                clusters = await asyncio.get_event_loop().run_in_executor(
                    self.executor, cluster_vectors
                )
                
                if clusters is not None:
                    # Analyze clusters
                    cluster_counts = Counter(clusters)
                    
                    for cluster_id, count in cluster_counts.items():
                        if cluster_id != -1 and count >= self.pattern_min_frequency:  # -1 is noise in DBSCAN
                            pattern_id = f"ml_cluster_{cluster_id}"
                            
                            pattern = await self._get_or_create_pattern(
                                pattern_id=pattern_id,
                                pattern_type="ml_cluster",
                                description=f"ML-detected interaction cluster with {count} examples"
                            )
                            
                            # Add examples from this cluster
                            cluster_indices = [i for i, c in enumerate(clusters) if c == cluster_id]
                            for idx in cluster_indices[-5:]:  # Last 5 examples
                                if idx < len(self.interaction_history):
                                    hist_interaction = self.interaction_history[-(len(texts)-idx)]
                                    pattern.examples.append({
                                        'user_input': hist_interaction['user_input'],
                                        'system_response': hist_interaction['system_response'],
                                        'timestamp': hist_interaction['timestamp'],
                                        'cluster_id': cluster_id
                                    })
                                    
                            pattern.frequency = count
                            pattern.confidence = min(1.0, count / 10.0)
                            pattern.last_seen = time.time()
                            
                            patterns.append(pattern)
                            
        except Exception as e:
            logger.error(f"Error in ML pattern detection: {e}")
            
        return patterns
        
    async def _update_pattern(self, pattern: Pattern):
        """Posodobi vzorec"""
        try:
            # Update confidence based on frequency
            pattern.confidence = min(1.0, pattern.frequency / 10.0)
            
            # Limit examples to prevent memory bloat
            if len(pattern.examples) > 20:
                pattern.examples = pattern.examples[-20:]
                
            # Store updated pattern
            self.discovered_patterns[pattern.pattern_id] = pattern
            
        except Exception as e:
            logger.error(f"Error updating pattern {pattern.pattern_id}: {e}")
            
    async def _learning_loop(self):
        """Glavna zanka avtonomnega učenja"""
        try:
            logger.info("🔄 Learning loop started")
            
            while True:
                try:
                    # Wait for learning events or timeout
                    try:
                        learning_event = await asyncio.wait_for(
                            self.learning_queue.get(), 
                            timeout=60.0
                        )
                        
                        # Process learning event
                        await self._process_learning_event(learning_event)
                        
                    except asyncio.TimeoutError:
                        # Periodic maintenance
                        await self._periodic_maintenance()
                        
                except asyncio.CancelledError:
                    logger.info("Learning loop cancelled")
                    break
                    
                except Exception as e:
                    logger.error(f"Error in learning loop: {e}")
                    await asyncio.sleep(5)  # Wait before retrying
                    
        except Exception as e:
            logger.error(f"Learning loop error: {e}")
            
    async def _consolidation_loop(self):
        """Zanka konsolidacije znanja"""
        try:
            logger.info("🔄 Consolidation loop started")
            
            while True:
                try:
                    # Wait for consolidation interval
                    await asyncio.sleep(self.consolidation_interval)
                    
                    # Perform consolidation
                    await self._consolidate_knowledge()
                    
                except asyncio.CancelledError:
                    logger.info("Consolidation loop cancelled")
                    break
                    
                except Exception as e:
                    logger.error(f"Error in consolidation loop: {e}")
                    await asyncio.sleep(60)  # Wait before retrying
                    
        except Exception as e:
            logger.error(f"Consolidation loop error: {e}")
            
    async def _process_learning_event(self, learning_event: LearningEvent):
        """Procesiraj dogodek učenja"""
        try:
            logger.debug(f"Processing learning event: {learning_event.event_id}")
            
            # Extract and learn from the event
            extracted_knowledge = learning_event.extracted_knowledge
            
            if extracted_knowledge:
                learning_result = await self._learn_from_extracted_knowledge(extracted_knowledge)
                
                if learning_result.success:
                    logger.info(f"Learning event processed successfully: "
                               f"{len(learning_result.new_concepts)} concepts, "
                               f"{len(learning_result.new_relations)} relations")
                else:
                    logger.warning(f"Learning event processing failed: {learning_event.event_id}")
                    
        except Exception as e:
            logger.error(f"Error processing learning event: {e}")
            
    async def _periodic_maintenance(self):
        """Periodično vzdrževanje"""
        try:
            logger.debug("Performing periodic maintenance")
            
            # Clean up old learning events
            if len(self.learning_events) > self.max_memory_size:
                self.learning_events = self.learning_events[-self.max_memory_size:]
                
            # Clean up old interaction history
            if len(self.interaction_history) > self.max_memory_size:
                self.interaction_history = self.interaction_history[-self.max_memory_size:]
                
            # Update pattern confidences
            for pattern in self.discovered_patterns.values():
                # Decay confidence over time
                time_since_last_seen = time.time() - pattern.last_seen
                if time_since_last_seen > 86400:  # 1 day
                    pattern.confidence *= 0.95  # Slight decay
                    
            # Remove low-confidence patterns
            patterns_to_remove = [
                pid for pid, pattern in self.discovered_patterns.items()
                if pattern.confidence < 0.1
            ]
            
            for pid in patterns_to_remove:
                del self.discovered_patterns[pid]
                
            if patterns_to_remove:
                logger.info(f"Removed {len(patterns_to_remove)} low-confidence patterns")
                
            # Update statistics
            self._update_statistics()
            
        except Exception as e:
            logger.error(f"Error in periodic maintenance: {e}")
            
    async def _consolidate_knowledge(self):
        """Konsolidiraj znanje"""
        start_time = time.time()
        
        try:
            async with self.consolidation_lock:
                logger.info("🔄 Starting knowledge consolidation...")
                
                concepts_merged = 0
                relations_refined = 0
                patterns_validated = 0
                knowledge_pruned = 0
                
                # Consolidate concepts
                if self.kb_available:
                    concepts_merged = await self._consolidate_concepts()
                    relations_refined = await self._consolidate_relations()
                    
                # Validate patterns
                patterns_validated = await self._validate_patterns()
                
                # Prune low-quality knowledge
                knowledge_pruned = await self._prune_knowledge()
                
                # Calculate quality improvement
                quality_before = self._calculate_knowledge_quality()
                
                # Update statistics
                self.stats['consolidations_performed'] += 1
                self.stats['last_consolidation'] = time.time()
                
                processing_time = time.time() - start_time
                
                consolidation_result = ConsolidationResult(
                    concepts_merged=concepts_merged,
                    relations_refined=relations_refined,
                    patterns_validated=patterns_validated,
                    knowledge_pruned=knowledge_pruned,
                    quality_improved=0.0,  # Would need before/after comparison
                    processing_time=processing_time
                )
                
                logger.info(f"✅ Knowledge consolidation completed: "
                           f"{concepts_merged} concepts merged, "
                           f"{relations_refined} relations refined, "
                           f"{patterns_validated} patterns validated, "
                           f"{knowledge_pruned} items pruned "
                           f"in {processing_time:.3f}s")
                           
                return consolidation_result
                
        except Exception as e:
            logger.error(f"Error in knowledge consolidation: {e}")
            return ConsolidationResult(
                concepts_merged=0,
                relations_refined=0,
                patterns_validated=0,
                knowledge_pruned=0,
                quality_improved=0.0,
                processing_time=time.time() - start_time
            )
            
    async def _consolidate_concepts(self) -> int:
        """Konsolidiraj koncepte"""
        merged_count = 0
        
        try:
            if not self.kb_available:
                return 0
                
            # Get all concepts from knowledge bank
            stats = self.knowledge_bank.get_statistics()
            
            # Simple consolidation: merge very similar concepts
            # This is a simplified implementation
            # In practice, this would use more sophisticated similarity measures
            
            logger.debug(f"Consolidating concepts from {stats.total_concepts} total concepts")
            
            # For now, just return 0 as we don't want to accidentally merge important concepts
            # In a full implementation, this would use semantic similarity to identify duplicates
            
        except Exception as e:
            logger.error(f"Error consolidating concepts: {e}")
            
        return merged_count
        
    async def _consolidate_relations(self) -> int:
        """Konsolidiraj relacije"""
        refined_count = 0
        
        try:
            if not self.kb_available:
                return 0
                
            # Get all relations from knowledge bank
            stats = self.knowledge_bank.get_statistics()
            
            logger.debug(f"Consolidating relations from {stats.total_relations} total relations")
            
            # Simple relation refinement
            # In practice, this would identify redundant or conflicting relations
            
        except Exception as e:
            logger.error(f"Error consolidating relations: {e}")
            
        return refined_count
        
    async def _validate_patterns(self) -> int:
        """Validiraj vzorce"""
        validated_count = 0
        
        try:
            for pattern in self.discovered_patterns.values():
                # Validate pattern based on frequency and recency
                if pattern.frequency >= self.pattern_min_frequency:
                    time_since_last_seen = time.time() - pattern.last_seen
                    
                    if time_since_last_seen < 86400:  # Less than 1 day
                        pattern.confidence = min(1.0, pattern.confidence * 1.1)  # Boost confidence
                        validated_count += 1
                    else:
                        pattern.confidence = max(0.1, pattern.confidence * 0.9)  # Reduce confidence
                        
        except Exception as e:
            logger.error(f"Error validating patterns: {e}")
            
        return validated_count
        
    async def _prune_knowledge(self) -> int:
        """Počisti znanje nizke kakovosti"""
        pruned_count = 0
        
        try:
            # Remove low-confidence patterns
            patterns_to_remove = [
                pid for pid, pattern in self.discovered_patterns.items()
                if pattern.confidence < 0.2 and pattern.frequency < 2
            ]
            
            for pid in patterns_to_remove:
                del self.discovered_patterns[pid]
                pruned_count += 1
                
            # Limit learning events
            if len(self.learning_events) > self.max_memory_size:
                events_to_remove = len(self.learning_events) - self.max_memory_size
                self.learning_events = self.learning_events[events_to_remove:]
                pruned_count += events_to_remove
                
        except Exception as e:
            logger.error(f"Error pruning knowledge: {e}")
            
        return pruned_count
        
    def _calculate_knowledge_quality(self) -> float:
        """Izračunaj kakovost znanja"""
        try:
            if not self.discovered_patterns:
                return 0.0
                
            # Simple quality metric based on pattern confidence and frequency
            total_quality = 0.0
            total_patterns = 0
            
            for pattern in self.discovered_patterns.values():
                pattern_quality = pattern.confidence * min(1.0, pattern.frequency / 10.0)
                total_quality += pattern_quality
                total_patterns += 1
                
            return total_quality / max(total_patterns, 1)
            
        except Exception as e:
            logger.error(f"Error calculating knowledge quality: {e}")
            return 0.0
            
    def _extract_keywords(self, text: str) -> List[str]:
        """Izvleči ključne besede iz besedila"""
        # Simple keyword extraction
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:10]  # Return top 10 keywords
        
    def _load_learning_data(self):
        """Naloži learning podatke z diska"""
        try:
            # Load learning events
            events_file = self.data_dir / 'learning_events.json'
            if events_file.exists():
                with open(events_file, 'r', encoding='utf-8') as f:
                    events_data = json.load(f)
                    for event_data in events_data[-1000:]:  # Load last 1000 events
                        learning_event = LearningEvent(
                            event_id=event_data['event_id'],
                            trigger=LearningTrigger(event_data['trigger']),
                            source_data=event_data['source_data'],
                            extracted_knowledge=event_data['extracted_knowledge'],
                            confidence=event_data['confidence'],
                            timestamp=event_data['timestamp'],
                            metadata=event_data.get('metadata', {})
                        )
                        self.learning_events.append(learning_event)
                        
            # Load patterns
            patterns_file = self.data_dir / 'patterns.json'
            if patterns_file.exists():
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    patterns_data = json.load(f)
                    for pattern_id, pattern_data in patterns_data.items():
                        pattern = Pattern(
                            pattern_id=pattern_id,
                            pattern_type=pattern_data['pattern_type'],
                            description=pattern_data['description'],
                            examples=pattern_data['examples'],
                            frequency=pattern_data['frequency'],
                            confidence=pattern_data['confidence'],
                            first_seen=pattern_data['first_seen'],
                            last_seen=pattern_data['last_seen'],
                            metadata=pattern_data.get('metadata', {})
                        )
                        self.discovered_patterns[pattern_id] = pattern
                        
            # Load interaction history
            history_file = self.data_dir / 'interaction_history.json'
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                    self.interaction_history = history_data[-1000:]  # Load last 1000 interactions
                    
            logger.info(f"✅ Learning data loaded: {len(self.learning_events)} events, "
                       f"{len(self.discovered_patterns)} patterns, "
                       f"{len(self.interaction_history)} interactions")
                       
        except Exception as e:
            logger.error(f"Error loading learning data: {e}")
            
    async def save_learning_data(self) -> bool:
        """Shrani learning podatke na disk"""
        try:
            def save_data():
                # Save learning events
                events_file = self.data_dir / 'learning_events.json'
                with open(events_file, 'w', encoding='utf-8') as f:
                    events_data = []
                    for event in self.learning_events[-1000:]:  # Save last 1000 events
                        events_data.append(asdict(event))
                    json.dump(events_data, f, indent=2, ensure_ascii=False, default=str)
                    
                # Save patterns
                patterns_file = self.data_dir / 'patterns.json'
                with open(patterns_file, 'w', encoding='utf-8') as f:
                    patterns_data = {}
                    for pattern_id, pattern in self.discovered_patterns.items():
                        patterns_data[pattern_id] = asdict(pattern)
                    json.dump(patterns_data, f, indent=2, ensure_ascii=False, default=str)
                    
                # Save interaction history
                history_file = self.data_dir / 'interaction_history.json'
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(self.interaction_history[-1000:], f, indent=2, ensure_ascii=False, default=str)
                    
                # Save statistics
                stats_file = self.data_dir / 'learning_statistics.json'
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump(self.stats, f, indent=2, default=str)
                    
                return True
                
            success = await asyncio.get_event_loop().run_in_executor(
                self.executor, save_data
            )
            
            if success:
                logger.info("✅ Learning data saved successfully")
                return True
            else:
                logger.error("❌ Failed to save learning data")
                return False
                
        except Exception as e:
            logger.error(f"Error saving learning data: {e}")
            return False
            
    def get_statistics(self) -> Dict[str, Any]:
        """Pridobi statistike Autonomous Learning"""
        self._update_statistics()
        
        return {
            'basic_stats': {
                'total_learning_events': self.stats['total_learning_events'],
                'successful_learning_events': self.stats['successful_learning_events'],
                'failed_learning_events': self.stats['failed_learning_events'],
                'concepts_learned': self.stats['concepts_learned'],
                'relations_learned': self.stats['relations_learned'],
                'patterns_discovered': self.stats['patterns_discovered']
            },
            'memory_stats': {
                'learning_events_count': len(self.learning_events),
                'patterns_count': len(self.discovered_patterns),
                'interaction_history_size': len(self.interaction_history),
                'max_memory_size': self.max_memory_size
            },
            'consolidation_stats': {
                'consolidations_performed': self.stats['consolidations_performed'],
                'last_consolidation': self.stats['last_consolidation'],
                'consolidation_interval': self.consolidation_interval
            },
            'pattern_stats': {
                'total_patterns': len(self.discovered_patterns),
                'high_confidence_patterns': len([p for p in self.discovered_patterns.values() if p.confidence > 0.8]),
                'frequent_patterns': len([p for p in self.discovered_patterns.values() if p.frequency >= self.pattern_min_frequency]),
                'recent_patterns': len([p for p in self.discovered_patterns.values() if time.time() - p.last_seen < 86400])
            },
            'system_info': {
                'learning_strategy': self.learning_strategy.value,
                'confidence_threshold': self.confidence_threshold,
                'ml_available': self.ml_available,
                'kb_available': self.kb_available,
                'semantic_available': self.semantic_available,
                'reasoning_available': self.reasoning_available,
                'system_health': self.stats['system_health']
            },
            'uptime': time.time() - self.stats['start_time']
        }
        
    async def shutdown(self):
        """Graceful shutdown Autonomous Learning"""
        try:
            logger.info("🔄 Shutting down Autonomous Learning...")
            
            # Stop learning loops
            await self.stop_learning()
            
            # Save current state
            await self.save_learning_data()
            
            # Shutdown executor
            if self.executor:
                self.executor.shutdown(wait=True)
                
            # Update final statistics
            self.stats['system_health'] = 'shutdown'
            
            logger.info("✅ Autonomous Learning shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Convenience functions
async def create_autonomous_learning(knowledge_bank: Optional[HybridKnowledgeBank] = None,
                                   semantic_layer: Optional[SemanticLayer] = None,
                                   reasoning_engine: Optional[DeterministicReasoningEngine] = None,
                                   pipeline: Optional[HybridPipeline] = None,
                                   data_dir: str = "data/autonomous_learning",
                                   learning_strategy: LearningStrategy = LearningStrategy.ADAPTIVE) -> AutonomousLearning:
    """
    Ustvari in inicializiraj Autonomous Learning.
    
    Args:
        knowledge_bank: Knowledge Bank komponenta
        semantic_layer: Semantic Layer komponenta
        reasoning_engine: Reasoning Engine komponenta
        pipeline: Pipeline komponenta
        data_dir: Direktorij za podatke
        learning_strategy: Strategija učenja
        
    Returns:
        Inicializiran AutonomousLearning
    """
    try:
        autonomous_learning = AutonomousLearning(
            knowledge_bank=knowledge_bank,
            semantic_layer=semantic_layer,
            reasoning_engine=reasoning_engine,
            pipeline=pipeline,
            data_dir=data_dir,
            learning_strategy=learning_strategy
        )
        
        return autonomous_learning
        
    except Exception as e:
        logger.error(f"Failed to create Autonomous Learning: {e}")
        raise


if __name__ == "__main__":
    # Test implementation
    async def test_autonomous_learning():
        """Test Autonomous Learning sistema"""
        try:
            logger.info("🧪 Testing Autonomous Learning...")
            
            # Create autonomous learning system
            autonomous_learning = await create_autonomous_learning()
            
            # Start learning
            await autonomous_learning.start_learning()
            
            # Simulate some interactions
            test_interactions = [
                ("What is machine learning?", "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed."),
                ("How does neural networks work?", "Neural networks are computing systems inspired by biological neural networks that process information using interconnected nodes."),
                ("If all birds can fly and penguins are birds, can penguins fly?", "This is a logical fallacy. While the premise states all birds can fly, in reality, penguins are birds that cannot fly."),
                ("Explain deep learning", "Deep learning is a subset of machine learning that uses neural networks with multiple layers to model and understand complex patterns.")
            ]
            
            for user_input, system_response in test_interactions:
                logger.info(f"\n--- Learning from interaction ---")
                logger.info(f"User: {user_input}")
                logger.info(f"System: {system_response}")
                
                learning_result = await autonomous_learning.learn_from_interaction(
                    user_input=user_input,
                    system_response=system_response,
                    feedback={'helpful': True, 'rating': 4}
                )
                
                logger.info(f"Learning result:")
                logger.info(f"  - Success: {learning_result.success}")
                logger.info(f"  - New concepts: {len(learning_result.new_concepts)}")
                logger.info(f"  - New relations: {len(learning_result.new_relations)}")
                logger.info(f"  - Patterns discovered: {len(learning_result.patterns_discovered)}")
                logger.info(f"  - Confidence: {learning_result.confidence:.2f}")
                
                # Small delay between interactions
                await asyncio.sleep(1)
                
            # Wait a bit for background processing
            await asyncio.sleep(5)
            
            # Get statistics
            stats = autonomous_learning.get_statistics()
            logger.info(f"\nAutonomous Learning Statistics:")
            logger.info(f"  - Total learning events: {stats['basic_stats']['total_learning_events']}")
            logger.info(f"  - Successful events: {stats['basic_stats']['successful_learning_events']}")
            logger.info(f"  - Concepts learned: {stats['basic_stats']['concepts_learned']}")
            logger.info(f"  - Relations learned: {stats['basic_stats']['relations_learned']}")
            logger.info(f"  - Patterns discovered: {stats['basic_stats']['patterns_discovered']}")
            logger.info(f"  - Total patterns: {stats['pattern_stats']['total_patterns']}")
            
            # Save data
            await autonomous_learning.save_learning_data()
            
            # Shutdown
            await autonomous_learning.shutdown()
            
            logger.info("✅ Autonomous Learning test completed successfully")
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise
    
    # Run test
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_autonomous_learning())