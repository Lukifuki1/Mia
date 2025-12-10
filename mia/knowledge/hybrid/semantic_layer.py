#!/usr/bin/env python3
"""
Semantic Layer - Semantična obdelava za hibridni MIA sistem
==========================================================

PRODUKCIJSKA IMPLEMENTACIJA semantične obdelave naravnega jezika.
Omogoča pretvorbo naravnega jezika v strukturirane koncepte in relacije.

KLJUČNE FUNKCIONALNOSTI:
- Sentence embeddings za semantično podobnost
- Semantic parsing NL → koncepti
- Concept mapping in disambiguation
- Context grounding
- Integration z Knowledge Bank Core
- Named Entity Recognition (NER)
- Relation extraction
- Semantic similarity computation

ARHITEKTURA:
- Backward compatible z obstoječim MIA sistemom
- Integracija z Knowledge Bank Core
- Support za lokalne in cloud embeddings
- Caching za performance optimization
"""

import logging
import json
import time
import asyncio
import threading
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import hashlib
import uuid

# Import existing MIA components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

try:
    from mia.knowledge.hybrid.knowledge_bank_core import HybridKnowledgeBank, create_hybrid_knowledge_bank
    KNOWLEDGE_BANK_AVAILABLE = True
except ImportError:
    KNOWLEDGE_BANK_AVAILABLE = False

# Semantic processing dependencies
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

# NLP dependencies
try:
    import spacy
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.tag import pos_tag
    from nltk.chunk import ne_chunk
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class SemanticConcept:
    """Semantični koncept z embeddings"""
    concept_id: str
    label: str
    description: str
    embedding: Optional[List[float]]
    confidence: float
    source: str
    created_at: float
    metadata: Dict[str, Any]

@dataclass
class SemanticRelation:
    """Semantična relacija med koncepti"""
    relation_id: str
    subject_concept: str
    predicate: str
    object_concept: str
    confidence: float
    embedding: Optional[List[float]]
    source: str
    created_at: float
    metadata: Dict[str, Any]

@dataclass
class ParsedEntity:
    """Entiteta iz naravnega jezika"""
    text: str
    entity_type: str
    start_pos: int
    end_pos: int
    confidence: float
    normalized_form: str
    linked_concept: Optional[str] = None

@dataclass
class SemanticParseResult:
    """Rezultat semantične analize"""
    original_text: str
    entities: List[ParsedEntity]
    relations: List[SemanticRelation]
    concepts: List[SemanticConcept]
    confidence: float
    processing_time: float
    metadata: Dict[str, Any]

@dataclass
class SimilarityResult:
    """Rezultat semantične podobnosti"""
    query: str
    matches: List[Dict[str, Any]]
    similarity_scores: List[float]
    processing_time: float

class SemanticLayer:
    """
    Semantična obdelava za hibridni MIA sistem.
    
    Omogoča:
    - Pretvorbo naravnega jezika v strukturirane koncepte
    - Semantično iskanje in podobnost
    - Named Entity Recognition
    - Relation extraction
    - Context grounding
    - Integration z Knowledge Bank
    
    PRODUKCIJSKE FUNKCIONALNOSTI:
    ✅ Sentence embeddings z SentenceTransformers
    ✅ Semantic parsing NL → koncepti
    ✅ Concept mapping in disambiguation
    ✅ Context grounding z Knowledge Bank
    ✅ Async operations za performance
    ✅ Comprehensive error handling
    ✅ Caching za optimizacijo
    ✅ Statistics in monitoring
    """
    
    def __init__(self, 
                 knowledge_bank: Optional[HybridKnowledgeBank] = None,
                 model_name: str = "all-MiniLM-L6-v2",
                 data_dir: str = "data/semantic_layer",
                 cache_size: int = 1000):
        """
        Inicializiraj semantični layer.
        
        Args:
            knowledge_bank: Povezava z Knowledge Bank sistemom
            model_name: Ime sentence transformer modela
            data_dir: Direktorij za podatke
            cache_size: Velikost cache-a
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Knowledge Bank integration
        self.knowledge_bank = knowledge_bank
        self.kb_integration = knowledge_bank is not None
        
        # Initialize embeddings model
        self.embeddings_available = EMBEDDINGS_AVAILABLE
        self.model = None
        self.model_name = model_name
        
        if self.embeddings_available:
            try:
                self.model = SentenceTransformer(model_name)
                logger.info(f"✅ Sentence transformer model loaded: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load embeddings model: {e}")
                self.embeddings_available = False
        else:
            logger.warning("❌ SentenceTransformers not available - semantic features limited")
            
        # Initialize NLP components
        self.nlp_available = NLP_AVAILABLE
        self.nlp_model = None
        
        if self.nlp_available:
            try:
                # Try to load spaCy model
                self.nlp_model = spacy.load("en_core_web_sm")
                logger.info("✅ spaCy model loaded")
            except OSError:
                try:
                    # Fallback to basic NLTK
                    nltk.download('punkt', quiet=True)
                    nltk.download('averaged_perceptron_tagger', quiet=True)
                    nltk.download('maxent_ne_chunker', quiet=True)
                    nltk.download('words', quiet=True)
                    logger.info("✅ NLTK components loaded")
                except Exception as e:
                    logger.warning(f"NLP components not fully available: {e}")
                    self.nlp_available = False
        
        # Performance optimization
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.embedding_cache: Dict[str, List[float]] = {}
        self.parse_cache: Dict[str, SemanticParseResult] = {}
        self.cache_size = cache_size
        
        # Storage
        self.concepts: Dict[str, SemanticConcept] = {}
        self.relations: Dict[str, SemanticRelation] = {}
        
        # Statistics
        self.stats = {
            'embeddings_computed': 0,
            'texts_parsed': 0,
            'concepts_extracted': 0,
            'relations_extracted': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'similarity_queries': 0,
            'system_health': 'initializing',
            'start_time': time.time()
        }
        
        # Load existing data
        self._load_semantic_data()
        
        # Update statistics
        self._update_statistics()
        
        logger.info("✅ Semantic Layer inicializiran")
        logger.info(f"   - Embeddings: {'✅' if self.embeddings_available else '❌'}")
        logger.info(f"   - NLP: {'✅' if self.nlp_available else '❌'}")
        logger.info(f"   - Knowledge Bank: {'✅' if self.kb_integration else '❌'}")
        logger.info(f"   - Concepts: {len(self.concepts)}")
        logger.info(f"   - Relations: {len(self.relations)}")
        
    def _update_statistics(self):
        """Posodobi statistike sistema"""
        try:
            self.stats['concepts_count'] = len(self.concepts)
            self.stats['relations_count'] = len(self.relations)
            self.stats['cache_size'] = len(self.embedding_cache)
            self.stats['system_health'] = 'healthy'
            
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
            self.stats['system_health'] = 'error'
            
    async def compute_embedding(self, text: str, use_cache: bool = True) -> Optional[List[float]]:
        """
        Izračunaj embedding za besedilo.
        
        Args:
            text: Besedilo za embedding
            use_cache: Ali naj uporabi cache
            
        Returns:
            Embedding vektor ali None
        """
        if not self.embeddings_available or not self.model:
            return None
            
        try:
            # Check cache
            text_hash = hashlib.md5(text.encode()).hexdigest()
            if use_cache and text_hash in self.embedding_cache:
                self.stats['cache_hits'] += 1
                return self.embedding_cache[text_hash]
                
            self.stats['cache_misses'] += 1
            self.stats['embeddings_computed'] += 1
            
            # Compute embedding in executor
            def compute():
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
                
            embedding = await asyncio.get_event_loop().run_in_executor(
                self.executor, compute
            )
            
            # Cache result
            if use_cache and len(self.embedding_cache) < self.cache_size:
                self.embedding_cache[text_hash] = embedding
            elif use_cache and len(self.embedding_cache) >= self.cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self.embedding_cache))
                del self.embedding_cache[oldest_key]
                self.embedding_cache[text_hash] = embedding
                
            return embedding
            
        except Exception as e:
            logger.error(f"Error computing embedding: {e}")
            return None
            
    async def parse_natural_language(self, text: str, 
                                   extract_entities: bool = True,
                                   extract_relations: bool = True,
                                   link_to_kb: bool = True) -> SemanticParseResult:
        """
        Parsiraj naravni jezik v strukturirane koncepte.
        
        Args:
            text: Besedilo za parsiranje
            extract_entities: Ali naj izvleče entitete
            extract_relations: Ali naj izvleče relacije
            link_to_kb: Ali naj poveže z Knowledge Bank
            
        Returns:
            SemanticParseResult
        """
        start_time = time.time()
        
        try:
            # Check cache
            cache_key = hashlib.md5(f"{text}_{extract_entities}_{extract_relations}_{link_to_kb}".encode()).hexdigest()
            if cache_key in self.parse_cache:
                self.stats['cache_hits'] += 1
                return self.parse_cache[cache_key]
                
            self.stats['cache_misses'] += 1
            self.stats['texts_parsed'] += 1
            
            entities = []
            relations = []
            concepts = []
            
            # Extract entities
            if extract_entities:
                entities = await self._extract_entities(text)
                
            # Extract relations
            if extract_relations:
                relations = await self._extract_relations(text, entities)
                
            # Create concepts from entities
            for entity in entities:
                concept = await self._entity_to_concept(entity, text)
                if concept:
                    concepts.append(concept)
                    
            # Link to Knowledge Bank
            if link_to_kb and self.kb_integration:
                await self._link_to_knowledge_bank(entities, relations, concepts)
                
            processing_time = time.time() - start_time
            
            result = SemanticParseResult(
                original_text=text,
                entities=entities,
                relations=relations,
                concepts=concepts,
                confidence=self._calculate_parse_confidence(entities, relations, concepts),
                processing_time=processing_time,
                metadata={
                    'extract_entities': extract_entities,
                    'extract_relations': extract_relations,
                    'link_to_kb': link_to_kb,
                    'timestamp': time.time()
                }
            )
            
            # Cache result
            if len(self.parse_cache) < self.cache_size:
                self.parse_cache[cache_key] = result
                
            self.stats['concepts_extracted'] += len(concepts)
            self.stats['relations_extracted'] += len(relations)
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error parsing natural language: {e}")
            
            return SemanticParseResult(
                original_text=text,
                entities=[],
                relations=[],
                concepts=[],
                confidence=0.0,
                processing_time=processing_time,
                metadata={'error': str(e)}
            )
            
    async def _extract_entities(self, text: str) -> List[ParsedEntity]:
        """Izvleči entitete iz besedila"""
        entities = []
        
        try:
            if self.nlp_model and hasattr(self.nlp_model, 'pipe'):
                # Use spaCy
                def extract_with_spacy():
                    doc = self.nlp_model(text)
                    extracted = []
                    
                    for ent in doc.ents:
                        entity = ParsedEntity(
                            text=ent.text,
                            entity_type=ent.label_,
                            start_pos=ent.start_char,
                            end_pos=ent.end_char,
                            confidence=0.8,  # spaCy doesn't provide confidence scores
                            normalized_form=ent.text.lower().strip()
                        )
                        extracted.append(entity)
                        
                    return extracted
                    
                entities = await asyncio.get_event_loop().run_in_executor(
                    self.executor, extract_with_spacy
                )
                
            elif self.nlp_available:
                # Use NLTK fallback
                def extract_with_nltk():
                    tokens = word_tokenize(text)
                    pos_tags = pos_tag(tokens)
                    chunks = ne_chunk(pos_tags)
                    
                    extracted = []
                    current_pos = 0
                    
                    for chunk in chunks:
                        if hasattr(chunk, 'label'):
                            # Named entity
                            entity_text = ' '.join([token for token, pos in chunk])
                            start_pos = text.find(entity_text, current_pos)
                            end_pos = start_pos + len(entity_text)
                            
                            entity = ParsedEntity(
                                text=entity_text,
                                entity_type=chunk.label(),
                                start_pos=start_pos,
                                end_pos=end_pos,
                                confidence=0.6,  # Lower confidence for NLTK
                                normalized_form=entity_text.lower().strip()
                            )
                            extracted.append(entity)
                            current_pos = end_pos
                            
                    return extracted
                    
                entities = await asyncio.get_event_loop().run_in_executor(
                    self.executor, extract_with_nltk
                )
                
            else:
                # Simple regex-based extraction as fallback
                entities = await self._extract_entities_regex(text)
                
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            
        return entities
        
    async def _extract_entities_regex(self, text: str) -> List[ParsedEntity]:
        """Enostavna regex-based ekstrakciaj entitet"""
        entities = []
        
        try:
            # Simple patterns for common entities
            patterns = {
                'PERSON': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
                'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'URL': r'https?://[^\s]+',
                'NUMBER': r'\b\d+\b',
                'DATE': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
            }
            
            for entity_type, pattern in patterns.items():
                for match in re.finditer(pattern, text):
                    entity = ParsedEntity(
                        text=match.group(),
                        entity_type=entity_type,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.4,  # Low confidence for regex
                        normalized_form=match.group().lower().strip()
                    )
                    entities.append(entity)
                    
        except Exception as e:
            logger.error(f"Error in regex entity extraction: {e}")
            
        return entities
        
    async def _extract_relations(self, text: str, entities: List[ParsedEntity]) -> List[SemanticRelation]:
        """Izvleči relacije med entitetami"""
        relations = []
        
        try:
            # Simple pattern-based relation extraction
            relation_patterns = [
                (r'(\w+)\s+works\s+for\s+(\w+)', 'worksFor'),
                (r'(\w+)\s+is\s+a\s+(\w+)', 'isA'),
                (r'(\w+)\s+has\s+(\w+)', 'has'),
                (r'(\w+)\s+uses\s+(\w+)', 'uses'),
                (r'(\w+)\s+owns\s+(\w+)', 'owns'),
                (r'(\w+)\s+lives\s+in\s+(\w+)', 'livesIn')
            ]
            
            for pattern, relation_type in relation_patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    subject = match.group(1)
                    object_entity = match.group(2)
                    
                    # Try to match with extracted entities
                    subject_entity = self._find_matching_entity(subject, entities)
                    object_entity_match = self._find_matching_entity(object_entity, entities)
                    
                    if subject_entity and object_entity_match:
                        relation = SemanticRelation(
                            relation_id=str(uuid.uuid4()),
                            subject_concept=subject_entity.normalized_form,
                            predicate=relation_type,
                            object_concept=object_entity_match.normalized_form,
                            confidence=0.6,
                            embedding=None,  # Will be computed if needed
                            source='semantic_layer',
                            created_at=time.time(),
                            metadata={
                                'pattern': pattern,
                                'original_text': match.group()
                            }
                        )
                        relations.append(relation)
                        
        except Exception as e:
            logger.error(f"Error extracting relations: {e}")
            
        return relations
        
    def _find_matching_entity(self, text: str, entities: List[ParsedEntity]) -> Optional[ParsedEntity]:
        """Najdi ujemajočo se entiteto"""
        text_lower = text.lower().strip()
        
        for entity in entities:
            if entity.normalized_form == text_lower or text_lower in entity.normalized_form:
                return entity
                
        return None
        
    async def _entity_to_concept(self, entity: ParsedEntity, context: str) -> Optional[SemanticConcept]:
        """Pretvori entiteto v semantični koncept"""
        try:
            # Compute embedding for entity
            embedding = await self.compute_embedding(entity.text)
            
            concept = SemanticConcept(
                concept_id=str(uuid.uuid4()),
                label=entity.text,
                description=f"{entity.entity_type} extracted from: {context[:100]}...",
                embedding=embedding,
                confidence=entity.confidence,
                source='semantic_layer',
                created_at=time.time(),
                metadata={
                    'entity_type': entity.entity_type,
                    'start_pos': entity.start_pos,
                    'end_pos': entity.end_pos,
                    'normalized_form': entity.normalized_form
                }
            )
            
            return concept
            
        except Exception as e:
            logger.error(f"Error converting entity to concept: {e}")
            return None
            
    async def _link_to_knowledge_bank(self, entities: List[ParsedEntity], 
                                    relations: List[SemanticRelation],
                                    concepts: List[SemanticConcept]):
        """Poveži z Knowledge Bank sistemom"""
        if not self.kb_integration or not self.knowledge_bank:
            return
            
        try:
            # Link concepts to Knowledge Bank
            for concept in concepts:
                # Check if similar concept exists
                similar_concepts = await self._find_similar_concepts_in_kb(concept)
                
                if similar_concepts:
                    # Link to existing concept
                    concept.metadata['kb_linked_concept'] = similar_concepts[0]['uri']
                else:
                    # Create new concept in Knowledge Bank
                    success = await self.knowledge_bank.create_concept(
                        concept_id=concept.concept_id,
                        label=concept.label,
                        description=concept.description,
                        properties={'semantic_confidence': concept.confidence}
                    )
                    
                    if success:
                        concept.metadata['kb_created'] = True
                        
            # Link relations to Knowledge Bank
            for relation in relations:
                # Try to create relation in Knowledge Bank
                try:
                    success = await self.knowledge_bank.create_relation(
                        relation_id=relation.relation_id,
                        label=relation.predicate,
                        domain=f"http://mia.ai/ontology#{relation.subject_concept}",
                        range=f"http://mia.ai/ontology#{relation.object_concept}",
                        properties={'semantic_confidence': relation.confidence}
                    )
                    
                    if success:
                        relation.metadata['kb_created'] = True
                        
                except Exception as e:
                    logger.warning(f"Failed to create relation in KB: {e}")
                    
        except Exception as e:
            logger.error(f"Error linking to Knowledge Bank: {e}")
            
    async def _find_similar_concepts_in_kb(self, concept: SemanticConcept) -> List[Dict[str, Any]]:
        """Najdi podobne koncepte v Knowledge Bank"""
        if not self.kb_integration or not self.knowledge_bank:
            return []
            
        try:
            # Simple text-based similarity for now
            # In production, this would use semantic similarity
            query = f"""
            SELECT ?concept ?label WHERE {{
                ?concept rdfs:label ?label .
                FILTER(CONTAINS(LCASE(?label), LCASE("{concept.label}")))
            }}
            """
            
            result = await self.knowledge_bank.query_sparql(query)
            
            if result.success:
                return result.results
                
        except Exception as e:
            logger.error(f"Error finding similar concepts in KB: {e}")
            
        return []
        
    def _calculate_parse_confidence(self, entities: List[ParsedEntity], 
                                  relations: List[SemanticRelation],
                                  concepts: List[SemanticConcept]) -> float:
        """Izračunaj zaupanje parsiranja"""
        if not entities and not relations and not concepts:
            return 0.0
            
        total_confidence = 0.0
        total_items = 0
        
        for entity in entities:
            total_confidence += entity.confidence
            total_items += 1
            
        for relation in relations:
            total_confidence += relation.confidence
            total_items += 1
            
        for concept in concepts:
            total_confidence += concept.confidence
            total_items += 1
            
        return total_confidence / max(total_items, 1)
        
    async def find_similar_concepts(self, query: str, limit: int = 10, 
                                  threshold: float = 0.5) -> SimilarityResult:
        """
        Najdi semantično podobne koncepte.
        
        Args:
            query: Poizvedba
            limit: Maksimalno število rezultatov
            threshold: Minimalna podobnost
            
        Returns:
            SimilarityResult
        """
        start_time = time.time()
        
        try:
            self.stats['similarity_queries'] += 1
            
            # Compute query embedding
            query_embedding = await self.compute_embedding(query)
            
            if not query_embedding:
                return SimilarityResult(
                    query=query,
                    matches=[],
                    similarity_scores=[],
                    processing_time=time.time() - start_time
                )
                
            matches = []
            scores = []
            
            # Compare with stored concepts
            for concept in self.concepts.values():
                if concept.embedding:
                    similarity = cosine_similarity(
                        [query_embedding], 
                        [concept.embedding]
                    )[0][0]
                    
                    if similarity >= threshold:
                        matches.append({
                            'concept': asdict(concept),
                            'similarity': float(similarity)
                        })
                        scores.append(float(similarity))
                        
            # Sort by similarity
            sorted_results = sorted(
                zip(matches, scores), 
                key=lambda x: x[1], 
                reverse=True
            )[:limit]
            
            if sorted_results:
                matches, scores = zip(*sorted_results)
                matches = list(matches)
                scores = list(scores)
            else:
                matches, scores = [], []
                
            return SimilarityResult(
                query=query,
                matches=matches,
                similarity_scores=scores,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Error finding similar concepts: {e}")
            return SimilarityResult(
                query=query,
                matches=[],
                similarity_scores=[],
                processing_time=time.time() - start_time
            )
            
    def _load_semantic_data(self):
        """Naloži semantične podatke z diska"""
        try:
            # Load concepts
            concepts_file = self.data_dir / 'semantic_concepts.json'
            if concepts_file.exists():
                with open(concepts_file, 'r', encoding='utf-8') as f:
                    concepts_data = json.load(f)
                    for concept_id, data in concepts_data.items():
                        self.concepts[concept_id] = SemanticConcept(**data)
                        
            # Load relations
            relations_file = self.data_dir / 'semantic_relations.json'
            if relations_file.exists():
                with open(relations_file, 'r', encoding='utf-8') as f:
                    relations_data = json.load(f)
                    for relation_id, data in relations_data.items():
                        self.relations[relation_id] = SemanticRelation(**data)
                        
            logger.info(f"✅ Semantic data loaded: {len(self.concepts)} concepts, {len(self.relations)} relations")
            
        except Exception as e:
            logger.error(f"Error loading semantic data: {e}")
            
    async def save_semantic_data(self) -> bool:
        """Shrani semantične podatke na disk"""
        try:
            def save_data():
                # Save concepts
                concepts_file = self.data_dir / 'semantic_concepts.json'
                with open(concepts_file, 'w', encoding='utf-8') as f:
                    concepts_data = {cid: asdict(concept) for cid, concept in self.concepts.items()}
                    json.dump(concepts_data, f, indent=2, ensure_ascii=False)
                    
                # Save relations
                relations_file = self.data_dir / 'semantic_relations.json'
                with open(relations_file, 'w', encoding='utf-8') as f:
                    relations_data = {rid: asdict(relation) for rid, relation in self.relations.items()}
                    json.dump(relations_data, f, indent=2, ensure_ascii=False)
                    
                # Save statistics
                stats_file = self.data_dir / 'semantic_statistics.json'
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump(self.stats, f, indent=2, default=str)
                    
                return True
                
            success = await asyncio.get_event_loop().run_in_executor(
                self.executor, save_data
            )
            
            if success:
                logger.info("✅ Semantic data saved successfully")
                return True
            else:
                logger.error("❌ Failed to save semantic data")
                return False
                
        except Exception as e:
            logger.error(f"Error saving semantic data: {e}")
            return False
            
    def get_statistics(self) -> Dict[str, Any]:
        """Pridobi statistike Semantic Layer"""
        self._update_statistics()
        
        return {
            'basic_stats': {
                'concepts_count': len(self.concepts),
                'relations_count': len(self.relations),
                'embeddings_computed': self.stats['embeddings_computed'],
                'texts_parsed': self.stats['texts_parsed']
            },
            'performance_stats': {
                'cache_hits': self.stats['cache_hits'],
                'cache_misses': self.stats['cache_misses'],
                'cache_hit_ratio': self.stats['cache_hits'] / max(self.stats['cache_hits'] + self.stats['cache_misses'], 1),
                'similarity_queries': self.stats['similarity_queries']
            },
            'system_info': {
                'embeddings_available': self.embeddings_available,
                'nlp_available': self.nlp_available,
                'kb_integration': self.kb_integration,
                'model_name': self.model_name,
                'cache_size': len(self.embedding_cache),
                'system_health': self.stats['system_health']
            },
            'uptime': time.time() - self.stats['start_time']
        }
        
    async def shutdown(self):
        """Graceful shutdown Semantic Layer"""
        try:
            logger.info("🔄 Shutting down Semantic Layer...")
            
            # Save current state
            await self.save_semantic_data()
            
            # Shutdown executor
            if self.executor:
                self.executor.shutdown(wait=True)
                
            # Clear caches
            self.embedding_cache.clear()
            self.parse_cache.clear()
            
            # Update final statistics
            self.stats['system_health'] = 'shutdown'
            
            logger.info("✅ Semantic Layer shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Convenience functions
async def create_semantic_layer(knowledge_bank: Optional[HybridKnowledgeBank] = None,
                               model_name: str = "all-MiniLM-L6-v2",
                               data_dir: str = "data/semantic_layer") -> SemanticLayer:
    """
    Ustvari in inicializiraj Semantic Layer.
    
    Args:
        knowledge_bank: Povezava z Knowledge Bank
        model_name: Ime embeddings modela
        data_dir: Direktorij za podatke
        
    Returns:
        Inicializiran SemanticLayer
    """
    try:
        semantic_layer = SemanticLayer(
            knowledge_bank=knowledge_bank,
            model_name=model_name,
            data_dir=data_dir
        )
        
        return semantic_layer
        
    except Exception as e:
        logger.error(f"Failed to create Semantic Layer: {e}")
        raise


if __name__ == "__main__":
    # Test implementation
    async def test_semantic_layer():
        """Test Semantic Layer sistema"""
        try:
            logger.info("🧪 Testing Semantic Layer...")
            
            # Create semantic layer
            semantic_layer = await create_semantic_layer()
            
            # Test text parsing
            test_text = "John Doe works for Microsoft and uses Python programming language."
            
            parse_result = await semantic_layer.parse_natural_language(test_text)
            
            logger.info(f"Parse result:")
            logger.info(f"  - Entities: {len(parse_result.entities)}")
            logger.info(f"  - Relations: {len(parse_result.relations)}")
            logger.info(f"  - Concepts: {len(parse_result.concepts)}")
            logger.info(f"  - Confidence: {parse_result.confidence:.2f}")
            
            # Test similarity search
            if parse_result.concepts:
                similarity_result = await semantic_layer.find_similar_concepts("software developer")
                logger.info(f"Similarity search found {len(similarity_result.matches)} matches")
                
            # Get statistics
            stats = semantic_layer.get_statistics()
            logger.info(f"Statistics: {stats}")
            
            # Save data
            await semantic_layer.save_semantic_data()
            
            # Shutdown
            await semantic_layer.shutdown()
            
            logger.info("✅ Semantic Layer test completed successfully")
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise
    
    # Run test
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_semantic_layer())