#!/usr/bin/env python3
"""
Knowledge Bank Core - RDF/OWL Ontologija za MIA
===============================================

PRODUKCIJSKA IMPLEMENTACIJA hibridnega Knowledge Bank sistema.
Združuje simbolično znanje (RDF/OWL), semantično razumevanje in deterministično sklepanje.

KLJUČNE FUNKCIONALNOSTI:
- RDF/OWL ontologija z RDFLib
- SPARQL endpoint za poizvedovanje
- Concept management in validation
- Knowledge graph operations
- Persistent storage
- Integration z obstoječim MIA sistemom

ARHITEKTURA:
- Backward compatible z obstoječim persistent_knowledge_store
- Dodaja RDF/OWL layer nad obstoječe fact/relation storage
- Omogoča hibridno delovanje (classic + semantic)
"""

import logging
import json
import time
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import uuid

# Import existing MIA components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

try:
    from mia.core.persistent_knowledge_store import PersistentKnowledgeStore, Fact, Relation
    MIA_CORE_AVAILABLE = True
except ImportError:
    MIA_CORE_AVAILABLE = False

# RDF/OWL dependencies
try:
    from rdflib import Graph, Namespace, URIRef, Literal, BNode
    from rdflib.namespace import RDF, RDFS, OWL, XSD
    from rdflib.plugins.sparql import prepareQuery
    from rdflib.plugins.stores.memory import Memory
    RDF_AVAILABLE = True
except ImportError:
    RDF_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class ConceptDefinition:
    """Definicija koncepta v ontologiji"""
    uri: str
    label: str
    description: str
    parent_classes: List[str]
    properties: Dict[str, Any]
    constraints: Dict[str, Any]
    created_at: float

@dataclass
class RelationDefinition:
    """Definicija relacije v ontologiji"""
    uri: str
    label: str
    domain: str  # Source concept
    range: str   # Target concept
    properties: Dict[str, Any]
    inverse_of: Optional[str]
    created_at: float

@dataclass
class ValidationResult:
    """Rezultat validacije"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]

@dataclass
class QueryResult:
    """Rezultat SPARQL poizvedbe"""
    success: bool
    results: List[Dict[str, Any]]
    query_time: float
    total_results: int
    error_message: Optional[str] = None

@dataclass
class KnowledgeStats:
    """Statistike Knowledge Bank"""
    total_concepts: int
    total_relations: int
    total_individuals: int
    total_triples: int
    ontology_size_mb: float
    last_updated: float
    validation_status: str

class HybridKnowledgeBank:
    """
    Hibridni Knowledge Bank sistem za MIA.
    
    Združuje:
    - Obstoječi MIA persistent storage (backward compatibility)
    - RDF/OWL ontologija (simbolično znanje)
    - SPARQL endpoint (poizvedovanje)
    - Concept management (hierarhije)
    - Validation system (konsistentnost)
    
    PRODUKCIJSKE FUNKCIONALNOSTI:
    ✅ RDF/OWL ontologija z RDFLib
    ✅ SPARQL endpoint za poizvedovanje
    ✅ Concept management in validation
    ✅ Integration z obstoječim MIA sistemom
    ✅ Async operations za performance
    ✅ Comprehensive error handling
    ✅ Persistent storage z backup
    ✅ Statistics in monitoring
    """
    
    def __init__(self, data_dir: str = "data/knowledge_bank", 
                 integrate_with_mia: bool = True):
        """
        Inicializiraj hibridni Knowledge Bank sistem.
        
        Args:
            data_dir: Direktorij za shranjevanje podatkov
            integrate_with_mia: Ali naj se integrira z obstoječim MIA sistemom
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Integration z obstoječim MIA sistemom
        self.mia_integration = integrate_with_mia and MIA_CORE_AVAILABLE
        self.mia_store = None
        
        if self.mia_integration:
            try:
                self.mia_store = PersistentKnowledgeStore(str(self.data_dir / "mia_classic"))
                logger.info("✅ MIA integration enabled - backward compatibility active")
            except Exception as e:
                logger.warning(f"⚠️ MIA integration failed: {e}")
                self.mia_integration = False
        
        # Initialize RDF graph
        self.rdf_available = RDF_AVAILABLE
        if self.rdf_available:
            self.graph = Graph()
            self._setup_namespaces()
            logger.info("✅ RDF/OWL ontologija inicializirana")
        else:
            self.graph = None
            logger.error("❌ RDFLib ni na voljo - Knowledge Bank ne bo deloval")
            raise RuntimeError("RDFLib is required for Knowledge Bank functionality")
            
        # Ontology storage
        self.concepts: Dict[str, ConceptDefinition] = {}
        self.relations: Dict[str, RelationDefinition] = {}
        self.individuals: Dict[str, Dict[str, Any]] = {}
        
        # Performance optimization
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.query_cache: Dict[str, QueryResult] = {}
        self.cache_max_size = 1000
        
        # Statistics
        self.stats = {
            'concepts_count': 0,
            'relations_count': 0,
            'individuals_count': 0,
            'triples_count': 0,
            'queries_executed': 0,
            'validations_performed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'last_backup': 0,
            'system_health': 'initializing'
        }
        
        # Load existing data
        self._load_ontology()
        
        # Update statistics
        self._update_statistics()
        
        logger.info(f"✅ Hibridni Knowledge Bank inicializiran")
        logger.info(f"   - RDF/OWL: {'✅' if self.rdf_available else '❌'}")
        logger.info(f"   - MIA Integration: {'✅' if self.mia_integration else '❌'}")
        logger.info(f"   - Concepts: {self.stats['concepts_count']}")
        logger.info(f"   - Relations: {self.stats['relations_count']}")
        logger.info(f"   - Triples: {self.stats['triples_count']}")
        
    def _setup_namespaces(self):
        """Nastavi RDF namespaces in osnovne ontologije"""
        if not self.graph:
            return
            
        # Define MIA ontology namespace
        self.MIA = Namespace("http://mia.ai/ontology#")
        self.MIADATA = Namespace("http://mia.ai/data#")
        
        # Bind namespaces
        self.graph.bind("mia", self.MIA)
        self.graph.bind("miadata", self.MIADATA)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)
        
        # Add basic ontology structure
        self.graph.add((self.MIA.Ontology, RDF.type, OWL.Ontology))
        self.graph.add((self.MIA.Ontology, RDFS.label, Literal("MIA Hybrid Knowledge Ontology")))
        self.graph.add((self.MIA.Ontology, RDFS.comment, 
                       Literal("Hibridna ontologija za MIA Enterprise AGI sistem")))
        
        # Add basic concept hierarchy
        self.graph.add((self.MIA.Entity, RDF.type, OWL.Class))
        self.graph.add((self.MIA.Entity, RDFS.label, Literal("Entity")))
        self.graph.add((self.MIA.Entity, RDFS.comment, Literal("Base class for all entities")))
        
        # Add basic properties
        self.graph.add((self.MIA.hasProperty, RDF.type, OWL.ObjectProperty))
        self.graph.add((self.MIA.hasProperty, RDFS.label, Literal("has property")))
        
        self.graph.add((self.MIA.hasValue, RDF.type, OWL.DatatypeProperty))
        self.graph.add((self.MIA.hasValue, RDFS.label, Literal("has value")))
        
        logger.debug("✅ RDF namespaces in osnovna ontologija nastavljena")
        
    def _update_statistics(self):
        """Posodobi statistike sistema"""
        try:
            self.stats['concepts_count'] = len(self.concepts)
            self.stats['relations_count'] = len(self.relations)
            self.stats['individuals_count'] = len(self.individuals)
            
            if self.graph:
                self.stats['triples_count'] = len(self.graph)
            
            self.stats['system_health'] = 'healthy'
            
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
            self.stats['system_health'] = 'error'
        
    async def create_concept(self, concept_id: str, label: str, description: str = "",
                            parent_classes: List[str] = None, properties: Dict[str, Any] = None,
                            sync_with_mia: bool = True) -> bool:
        """
        Ustvari nov koncept v hibridni ontologiji.
        
        Args:
            concept_id: Unique identifier
            label: Human-readable label
            description: Concept description
            parent_classes: List of parent class URIs
            properties: Additional properties
            sync_with_mia: Ali naj sinhronizira z obstoječim MIA sistemom
            
        Returns:
            True če je uspešno ustvarjen
        """
        try:
            # Generate concept URI
            concept_uri = f"http://mia.ai/ontology#{concept_id}"
            
            # Check if concept already exists
            if concept_uri in self.concepts:
                logger.warning(f"Concept {concept_id} already exists")
                return False
                
            # Validate parent classes
            for parent_uri in parent_classes or []:
                if parent_uri not in self.concepts and parent_uri != f"http://mia.ai/ontology#Entity":
                    logger.warning(f"Parent class {parent_uri} does not exist")
                    
            # Create concept definition
            concept = ConceptDefinition(
                uri=concept_uri,
                label=label,
                description=description,
                parent_classes=parent_classes or [f"http://mia.ai/ontology#Entity"],
                properties=properties or {},
                constraints={},
                created_at=time.time()
            )
            
            # Add to RDF graph
            if self.graph:
                concept_ref = URIRef(concept_uri)
                self.graph.add((concept_ref, RDF.type, OWL.Class))
                self.graph.add((concept_ref, RDFS.label, Literal(label)))
                
                if description:
                    self.graph.add((concept_ref, RDFS.comment, Literal(description)))
                    
                # Add parent classes
                for parent_uri in concept.parent_classes:
                    parent_ref = URIRef(parent_uri)
                    self.graph.add((concept_ref, RDFS.subClassOf, parent_ref))
                    
                # Add custom properties
                for prop_name, prop_value in (properties or {}).items():
                    prop_uri = URIRef(f"http://mia.ai/ontology#{prop_name}")
                    if isinstance(prop_value, str):
                        self.graph.add((concept_ref, prop_uri, Literal(prop_value)))
                    else:
                        self.graph.add((concept_ref, prop_uri, Literal(str(prop_value))))
                
            # Store concept
            self.concepts[concept_uri] = concept
            
            # Sync with MIA classic system
            if sync_with_mia and self.mia_integration and self.mia_store:
                try:
                    # Create corresponding fact in MIA system
                    fact = Fact(
                        entity=concept_id,
                        property="type",
                        value="concept",
                        source="knowledge_bank",
                        confidence=1.0,
                        timestamp=time.time()
                    )
                    await asyncio.get_event_loop().run_in_executor(
                        self.executor, self.mia_store.add_fact, fact
                    )
                    
                    # Add description fact
                    if description:
                        desc_fact = Fact(
                            entity=concept_id,
                            property="description",
                            value=description,
                            source="knowledge_bank",
                            confidence=1.0,
                            timestamp=time.time()
                        )
                        await asyncio.get_event_loop().run_in_executor(
                            self.executor, self.mia_store.add_fact, desc_fact
                        )
                        
                except Exception as e:
                    logger.warning(f"Failed to sync concept with MIA: {e}")
            
            # Update statistics
            self._update_statistics()
            
            logger.info(f"✅ Created concept: {concept_id} ({concept_uri})")
            return True
            
        except Exception as e:
            logger.error(f"Error creating concept {concept_id}: {e}")
            return False
            
    async def create_relation(self, relation_id: str, label: str, domain: str, range: str,
                             properties: Dict[str, Any] = None, inverse_of: str = None,
                             sync_with_mia: bool = True) -> bool:
        """
        Ustvari novo relacijo v hibridni ontologiji.
        
        Args:
            relation_id: Unique identifier
            label: Human-readable label
            domain: Source concept URI
            range: Target concept URI
            properties: Additional properties
            inverse_of: Inverse relation URI
            sync_with_mia: Ali naj sinhronizira z obstoječim MIA sistemom
            
        Returns:
            True če je uspešno ustvarjena
        """
        try:
            # Generate relation URI
            relation_uri = f"http://mia.ai/ontology#{relation_id}"
            
            # Check if relation already exists
            if relation_uri in self.relations:
                logger.warning(f"Relation {relation_id} already exists")
                return False
                
            # Validate domain and range concepts
            if domain not in self.concepts:
                logger.warning(f"Domain concept {domain} does not exist")
            if range not in self.concepts:
                logger.warning(f"Range concept {range} does not exist")
                
            # Create relation definition
            relation = RelationDefinition(
                uri=relation_uri,
                label=label,
                domain=domain,
                range=range,
                properties=properties or {},
                inverse_of=inverse_of,
                created_at=time.time()
            )
            
            # Add to RDF graph
            if self.graph:
                relation_ref = URIRef(relation_uri)
                self.graph.add((relation_ref, RDF.type, OWL.ObjectProperty))
                self.graph.add((relation_ref, RDFS.label, Literal(label)))
                self.graph.add((relation_ref, RDFS.domain, URIRef(domain)))
                self.graph.add((relation_ref, RDFS.range, URIRef(range)))
                
                if inverse_of:
                    self.graph.add((relation_ref, OWL.inverseOf, URIRef(inverse_of)))
                    
                # Add custom properties
                for prop_name, prop_value in (properties or {}).items():
                    prop_uri = URIRef(f"http://mia.ai/ontology#{prop_name}")
                    if isinstance(prop_value, str):
                        self.graph.add((relation_ref, prop_uri, Literal(prop_value)))
                    else:
                        self.graph.add((relation_ref, prop_uri, Literal(str(prop_value))))
                
            # Store relation
            self.relations[relation_uri] = relation
            
            # Sync with MIA classic system
            if sync_with_mia and self.mia_integration and self.mia_store:
                try:
                    # Create corresponding relation in MIA system
                    mia_relation = Relation(
                        subject=domain.split('#')[-1] if '#' in domain else domain,
                        predicate=relation_id,
                        object=range.split('#')[-1] if '#' in range else range,
                        source="knowledge_bank",
                        confidence=1.0,
                        timestamp=time.time()
                    )
                    await asyncio.get_event_loop().run_in_executor(
                        self.executor, self.mia_store.add_relation, mia_relation
                    )
                    
                except Exception as e:
                    logger.warning(f"Failed to sync relation with MIA: {e}")
            
            # Update statistics
            self._update_statistics()
            
            logger.info(f"✅ Created relation: {relation_id} ({relation_uri})")
            return True
            
        except Exception as e:
            logger.error(f"Error creating relation {relation_id}: {e}")
            return False
            
    async def add_individual(self, individual_id: str, concept_uri: str, 
                            properties: Dict[str, Any] = None, sync_with_mia: bool = True) -> bool:
        """
        Dodaj posameznik (individual) v hibridno ontologijo.
        
        Args:
            individual_id: Unique identifier
            concept_uri: URI of the concept this individual belongs to
            properties: Property values
            sync_with_mia: Ali naj sinhronizira z obstoječim MIA sistemom
            
        Returns:
            True če je uspešno dodan
        """
        try:
            # Generate individual URI
            individual_uri = f"http://mia.ai/data#{individual_id}"
            
            # Check if concept exists
            if concept_uri not in self.concepts:
                logger.warning(f"Concept {concept_uri} does not exist")
                
            # Add to RDF graph
            if self.graph:
                individual_ref = URIRef(individual_uri)
                concept_ref = URIRef(concept_uri)
                self.graph.add((individual_ref, RDF.type, concept_ref))
                
                # Add label
                self.graph.add((individual_ref, RDFS.label, Literal(individual_id)))
                
                # Add properties
                for prop_name, value in (properties or {}).items():
                    if prop_name.startswith('http://'):
                        prop_uri = URIRef(prop_name)
                    else:
                        prop_uri = URIRef(f"http://mia.ai/ontology#{prop_name}")
                        
                    if isinstance(value, str):
                        self.graph.add((individual_ref, prop_uri, Literal(value)))
                    elif isinstance(value, (int, float)):
                        self.graph.add((individual_ref, prop_uri, Literal(value)))
                    elif isinstance(value, bool):
                        self.graph.add((individual_ref, prop_uri, Literal(value)))
                    else:
                        # Assume it's a URI reference
                        self.graph.add((individual_ref, prop_uri, URIRef(str(value))))
                        
            # Store individual
            self.individuals[individual_uri] = {
                'id': individual_id,
                'concept_uri': concept_uri,
                'properties': properties or {},
                'created_at': time.time()
            }
            
            # Sync with MIA classic system
            if sync_with_mia and self.mia_integration and self.mia_store:
                try:
                    # Create facts for each property
                    for prop_name, value in (properties or {}).items():
                        fact = Fact(
                            entity=individual_id,
                            property=prop_name,
                            value=value,
                            source="knowledge_bank",
                            confidence=1.0,
                            timestamp=time.time()
                        )
                        await asyncio.get_event_loop().run_in_executor(
                            self.executor, self.mia_store.add_fact, fact
                        )
                        
                    # Add type fact
                    type_fact = Fact(
                        entity=individual_id,
                        property="rdf_type",
                        value=concept_uri,
                        source="knowledge_bank",
                        confidence=1.0,
                        timestamp=time.time()
                    )
                    await asyncio.get_event_loop().run_in_executor(
                        self.executor, self.mia_store.add_fact, type_fact
                    )
                    
                except Exception as e:
                    logger.warning(f"Failed to sync individual with MIA: {e}")
            
            # Update statistics
            self._update_statistics()
            
            logger.info(f"✅ Added individual: {individual_id} ({individual_uri})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding individual {individual_id}: {e}")
            return False
            
    async def query_sparql(self, query: str, use_cache: bool = True) -> QueryResult:
        """
        Izvedi SPARQL poizvedbo z optimizacijo in caching.
        
        Args:
            query: SPARQL query string
            use_cache: Ali naj uporabi cache za rezultate
            
        Returns:
            QueryResult objekt z rezultati
        """
        start_time = time.time()
        
        try:
            if not self.graph:
                return QueryResult(
                    success=False,
                    results=[],
                    query_time=0.0,
                    total_results=0,
                    error_message="RDF graph not available"
                )
            
            # Check cache
            query_hash = hashlib.md5(query.encode()).hexdigest()
            if use_cache and query_hash in self.query_cache:
                self.stats['cache_hits'] += 1
                cached_result = self.query_cache[query_hash]
                logger.debug(f"Cache hit for query: {query_hash[:8]}")
                return cached_result
            
            self.stats['cache_misses'] += 1
            self.stats['queries_executed'] += 1
            
            # Execute SPARQL query in thread pool
            def execute_query():
                results = []
                try:
                    for row in self.graph.query(query):
                        result_dict = {}
                        if hasattr(row, 'labels'):
                            # SELECT query
                            for i, var in enumerate(row.labels):
                                value = row[i]
                                if hasattr(value, 'toPython'):
                                    result_dict[str(var)] = value.toPython()
                                else:
                                    result_dict[str(var)] = str(value)
                        else:
                            # ASK query or other
                            result_dict['result'] = bool(row)
                        results.append(result_dict)
                    return results
                except Exception as e:
                    logger.error(f"SPARQL execution error: {e}")
                    raise
            
            # Run query in executor
            results = await asyncio.get_event_loop().run_in_executor(
                self.executor, execute_query
            )
            
            query_time = time.time() - start_time
            
            # Create result object
            query_result = QueryResult(
                success=True,
                results=results,
                query_time=query_time,
                total_results=len(results),
                error_message=None
            )
            
            # Cache result if cache is not full
            if use_cache and len(self.query_cache) < self.cache_max_size:
                self.query_cache[query_hash] = query_result
            elif use_cache and len(self.query_cache) >= self.cache_max_size:
                # Remove oldest entry
                oldest_key = next(iter(self.query_cache))
                del self.query_cache[oldest_key]
                self.query_cache[query_hash] = query_result
            
            logger.debug(f"SPARQL query executed in {query_time:.3f}s, {len(results)} results")
            return query_result
            
        except Exception as e:
            query_time = time.time() - start_time
            logger.error(f"Error executing SPARQL query: {e}")
            return QueryResult(
                success=False,
                results=[],
                query_time=query_time,
                total_results=0,
                error_message=str(e)
            )
            
    async def get_concept_hierarchy(self, concept_uri: str) -> Dict[str, Any]:
        """
        Pridobi hierarhijo koncepta z SPARQL poizvedbami.
        
        Args:
            concept_uri: URI koncepta
            
        Returns:
            Hierarhija koncepta
        """
        try:
            if concept_uri not in self.concepts:
                return {}
                
            concept = self.concepts[concept_uri]
            
            # SPARQL query za parent classes
            parents_query = f"""
            SELECT ?parent ?label WHERE {{
                <{concept_uri}> rdfs:subClassOf ?parent .
                OPTIONAL {{ ?parent rdfs:label ?label }}
            }}
            """
            
            # SPARQL query za child classes
            children_query = f"""
            SELECT ?child ?label WHERE {{
                ?child rdfs:subClassOf <{concept_uri}> .
                OPTIONAL {{ ?child rdfs:label ?label }}
            }}
            """
            
            # SPARQL query za individuals
            individuals_query = f"""
            SELECT ?individual ?label WHERE {{
                ?individual rdf:type <{concept_uri}> .
                OPTIONAL {{ ?individual rdfs:label ?label }}
            }}
            """
            
            # Execute queries
            parents_result = await self.query_sparql(parents_query)
            children_result = await self.query_sparql(children_query)
            individuals_result = await self.query_sparql(individuals_query)
            
            hierarchy = {
                'concept': asdict(concept),
                'parents': parents_result.results if parents_result.success else [],
                'children': children_result.results if children_result.success else [],
                'individuals': individuals_result.results if individuals_result.success else [],
                'statistics': {
                    'parent_count': len(parents_result.results) if parents_result.success else 0,
                    'children_count': len(children_result.results) if children_result.success else 0,
                    'individuals_count': len(individuals_result.results) if individuals_result.success else 0
                }
            }
            
            return hierarchy
            
        except Exception as e:
            logger.error(f"Error getting concept hierarchy: {e}")
            return {}
            
    async def validate_ontology(self) -> ValidationResult:
        """
        Validiraj hibridno ontologijo z naprednimi preverjanji.
        
        Returns:
            ValidationResult
        """
        try:
            self.stats['validations_performed'] += 1
            
            errors = []
            warnings = []
            
            # Check concept consistency
            for concept_uri, concept in self.concepts.items():
                # Check parent classes exist
                for parent_uri in concept.parent_classes:
                    if parent_uri not in self.concepts and parent_uri != "http://mia.ai/ontology#Entity":
                        errors.append(f"Concept {concept_uri} references non-existent parent {parent_uri}")
                        
                # Check for empty labels
                if not concept.label.strip():
                    warnings.append(f"Concept {concept_uri} has empty label")
                    
            # Check relation consistency
            for relation_uri, relation in self.relations.items():
                # Check domain and range exist
                if relation.domain not in self.concepts:
                    errors.append(f"Relation {relation_uri} references non-existent domain {relation.domain}")
                if relation.range not in self.concepts:
                    errors.append(f"Relation {relation_uri} references non-existent range {relation.range}")
                    
                # Check for empty labels
                if not relation.label.strip():
                    warnings.append(f"Relation {relation_uri} has empty label")
                    
            # Check individuals consistency
            for individual_uri, individual in self.individuals.items():
                concept_uri = individual.get('concept_uri')
                if concept_uri and concept_uri not in self.concepts:
                    errors.append(f"Individual {individual_uri} references non-existent concept {concept_uri}")
                    
            # Check for circular dependencies
            circular_deps = await self._check_circular_dependencies()
            if circular_deps:
                errors.extend([f"Circular dependency detected: {dep}" for dep in circular_deps])
                
            # RDF graph validation
            if self.graph:
                try:
                    # Check for basic RDF consistency
                    triples_count = len(self.graph)
                    if triples_count == 0:
                        warnings.append("RDF graph is empty")
                    elif triples_count > 100000:
                        warnings.append(f"Large RDF graph ({triples_count} triples) may impact performance")
                        
                except Exception as e:
                    errors.append(f"RDF graph validation error: {e}")
                    
            # Check MIA integration consistency
            if self.mia_integration and self.mia_store:
                try:
                    # Validate sync between systems
                    mia_facts_count = len(self.mia_store.facts)
                    kb_concepts_count = len(self.concepts)
                    
                    if abs(mia_facts_count - kb_concepts_count) > kb_concepts_count * 0.5:
                        warnings.append("Significant discrepancy between MIA facts and KB concepts")
                        
                except Exception as e:
                    warnings.append(f"MIA integration validation warning: {e}")
                    
            is_valid = len(errors) == 0
            
            result = ValidationResult(
                valid=is_valid,
                errors=errors,
                warnings=warnings,
                details={
                    'concepts_checked': len(self.concepts),
                    'relations_checked': len(self.relations),
                    'individuals_checked': len(self.individuals),
                    'circular_dependencies': len(circular_deps),
                    'rdf_triples': len(self.graph) if self.graph else 0,
                    'mia_integration': self.mia_integration,
                    'validation_timestamp': time.time()
                }
            )
            
            logger.info(f"Ontology validation: {'✅ Valid' if is_valid else '❌ Invalid'} ({len(errors)} errors, {len(warnings)} warnings)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating ontology: {e}")
            return ValidationResult(
                valid=False,
                errors=[f"Validation error: {e}"],
                warnings=[],
                details={'validation_timestamp': time.time()}
            )
            
    async def _check_circular_dependencies(self) -> List[str]:
        """Preveri krožne odvisnosti v hierarhiji z async optimizacijo"""
        
        def check_cycles():
            circular_deps = []
            
            def has_circular_path(concept_uri: str, visited: Set[str], path: List[str]) -> bool:
                if concept_uri in visited:
                    # Found circular dependency
                    if concept_uri in path:
                        cycle_start = path.index(concept_uri)
                        cycle = " -> ".join(path[cycle_start:] + [concept_uri])
                        if cycle not in circular_deps:
                            circular_deps.append(cycle)
                    return True
                    
                if concept_uri not in self.concepts:
                    return False
                    
                visited.add(concept_uri)
                path.append(concept_uri)
                
                concept = self.concepts[concept_uri]
                for parent_uri in concept.parent_classes:
                    if has_circular_path(parent_uri, visited.copy(), path.copy()):
                        return True
                        
                return False
                
            # Check each concept
            for concept_uri in self.concepts:
                has_circular_path(concept_uri, set(), [])
                
            return circular_deps
        
        # Run in executor for better performance
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, check_cycles
        )
        
    def get_statistics(self) -> KnowledgeStats:
        """Pridobi podrobne statistike hibridnega Knowledge Bank sistema"""
        try:
            # Update current statistics
            self._update_statistics()
            
            # Calculate ontology size
            ontology_size_mb = 0.0
            if self.graph:
                # Estimate size based on triples count
                ontology_size_mb = len(self.graph) * 0.0001  # Rough estimate
                
            return KnowledgeStats(
                total_concepts=len(self.concepts),
                total_relations=len(self.relations),
                total_individuals=len(self.individuals),
                total_triples=len(self.graph) if self.graph else 0,
                ontology_size_mb=ontology_size_mb,
                last_updated=time.time(),
                validation_status=self.stats.get('system_health', 'unknown')
            )
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return KnowledgeStats(
                total_concepts=0,
                total_relations=0,
                total_individuals=0,
                total_triples=0,
                ontology_size_mb=0.0,
                last_updated=time.time(),
                validation_status='error'
            )
            
    def get_detailed_statistics(self) -> Dict[str, Any]:
        """Pridobi podrobne statistike sistema"""
        basic_stats = self.get_statistics()
        
        return {
            'basic_stats': asdict(basic_stats),
            'performance_stats': {
                'queries_executed': self.stats.get('queries_executed', 0),
                'cache_hits': self.stats.get('cache_hits', 0),
                'cache_misses': self.stats.get('cache_misses', 0),
                'cache_hit_ratio': (
                    self.stats.get('cache_hits', 0) / 
                    max(self.stats.get('queries_executed', 1), 1)
                ),
                'validations_performed': self.stats.get('validations_performed', 0)
            },
            'system_info': {
                'rdf_available': self.rdf_available,
                'mia_integration': self.mia_integration,
                'storage_type': 'RDF Graph' if self.graph else 'No Storage',
                'cache_size': len(self.query_cache),
                'cache_max_size': self.cache_max_size,
                'executor_threads': self.executor._max_workers if self.executor else 0
            },
            'health_status': {
                'system_health': self.stats.get('system_health', 'unknown'),
                'last_backup': self.stats.get('last_backup', 0),
                'uptime': time.time() - self.stats.get('start_time', time.time())
            }
        }
        
    async def save_ontology(self, backup: bool = True) -> bool:
        """
        Shrani hibridno ontologijo na disk z backup funkcionalnostjo.
        
        Args:
            backup: Ali naj ustvari backup pred shranjevanjem
            
        Returns:
            True če je uspešno shranjeno
        """
        try:
            # Create backup if requested
            if backup:
                await self._create_backup()
                
            def save_data():
                # Save concepts
                concepts_file = self.data_dir / 'concepts.json'
                with open(concepts_file, 'w', encoding='utf-8') as f:
                    concepts_data = {uri: asdict(concept) for uri, concept in self.concepts.items()}
                    json.dump(concepts_data, f, indent=2, ensure_ascii=False)
                    
                # Save relations
                relations_file = self.data_dir / 'relations.json'
                with open(relations_file, 'w', encoding='utf-8') as f:
                    relations_data = {uri: asdict(relation) for uri, relation in self.relations.items()}
                    json.dump(relations_data, f, indent=2, ensure_ascii=False)
                    
                # Save individuals
                individuals_file = self.data_dir / 'individuals.json'
                with open(individuals_file, 'w', encoding='utf-8') as f:
                    json.dump(self.individuals, f, indent=2, ensure_ascii=False)
                    
                # Save RDF graph if available
                if self.graph:
                    rdf_file = self.data_dir / 'ontology.ttl'
                    self.graph.serialize(destination=str(rdf_file), format='turtle')
                    
                # Save statistics
                stats_file = self.data_dir / 'statistics.json'
                with open(stats_file, 'w', encoding='utf-8') as f:
                    current_stats = self.get_detailed_statistics()
                    json.dump(current_stats, f, indent=2, default=str)
                    
                return True
                
            # Run save operation in executor
            success = await asyncio.get_event_loop().run_in_executor(
                self.executor, save_data
            )
            
            if success:
                self.stats['last_backup'] = time.time()
                logger.info("✅ Hibridna ontologija uspešno shranjena")
                return True
            else:
                logger.error("❌ Napaka pri shranjevanju ontologije")
                return False
                
        except Exception as e:
            logger.error(f"Error saving ontology: {e}")
            return False
            
    def _load_ontology(self) -> bool:
        """Naloži ontologijo z diska"""
        try:
            # Load concepts
            concepts_file = self.data_dir / 'concepts.json'
            if concepts_file.exists():
                with open(concepts_file, 'r') as f:
                    concepts_data = json.load(f)
                    for uri, data in concepts_data.items():
                        self.concepts[uri] = ConceptDefinition(**data)
                        
            # Load relations
            relations_file = self.data_dir / 'relations.json'
            if relations_file.exists():
                with open(relations_file, 'r') as f:
                    relations_data = json.load(f)
                    for uri, data in relations_data.items():
                        self.relations[uri] = RelationDefinition(**data)
                        
            # Load RDF graph if available
            if self.graph:
                rdf_file = self.data_dir / 'ontology.ttl'
                if rdf_file.exists():
                    self.graph.parse(str(rdf_file), format='turtle')
            else:
                # Load fallback triples
                fallback_file = self.data_dir / 'fallback_triples.json'
                if fallback_file.exists():
                    with open(fallback_file, 'r') as f:
                        self.fallback_triples = json.load(f)
                        
            # Update statistics
            self.stats['concepts_count'] = len(self.concepts)
            self.stats['relations_count'] = len(self.relations)
            
            if self.concepts or self.relations:
                logger.info(f"✅ Loaded ontology: {len(self.concepts)} concepts, {len(self.relations)} relations")
                
            return True
            
        except Exception as e:
            logger.error(f"Error loading ontology: {e}")
            return False

    async def _create_backup(self) -> bool:
        """Ustvari backup trenutne ontologije"""
        try:
            import shutil
            from datetime import datetime
            
            # Create backup directory
            backup_dir = self.data_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            # Create timestamped backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_subdir = backup_dir / f"backup_{timestamp}"
            backup_subdir.mkdir(exist_ok=True)
            
            def create_backup():
                # Copy all ontology files
                for file_pattern in ['*.json', '*.ttl']:
                    for file_path in self.data_dir.glob(file_pattern):
                        if file_path.is_file():
                            shutil.copy2(file_path, backup_subdir)
                            
                # Create backup metadata
                metadata = {
                    'timestamp': timestamp,
                    'concepts_count': len(self.concepts),
                    'relations_count': len(self.relations),
                    'individuals_count': len(self.individuals),
                    'rdf_triples': len(self.graph) if self.graph else 0,
                    'backup_reason': 'pre_save_backup'
                }
                
                metadata_file = backup_subdir / 'backup_metadata.json'
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                    
                return True
                
            # Run backup in executor
            success = await asyncio.get_event_loop().run_in_executor(
                self.executor, create_backup
            )
            
            if success:
                logger.debug(f"Backup created: {backup_subdir}")
                return True
            else:
                logger.warning("Failed to create backup")
                return False
                
        except Exception as e:
            logger.warning(f"Error creating backup: {e}")
            return False
            
    async def shutdown(self):
        """Graceful shutdown hibridnega Knowledge Bank sistema"""
        try:
            logger.info("🔄 Shutting down Hybrid Knowledge Bank...")
            
            # Save current state
            await self.save_ontology(backup=True)
            
            # Shutdown executor
            if self.executor:
                self.executor.shutdown(wait=True)
                
            # Clear caches
            self.query_cache.clear()
            
            # Update final statistics
            self.stats['system_health'] = 'shutdown'
            
            logger.info("✅ Hybrid Knowledge Bank shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Convenience functions for easy usage
async def create_hybrid_knowledge_bank(data_dir: str = "data/knowledge_bank", 
                                      integrate_with_mia: bool = True) -> HybridKnowledgeBank:
    """
    Ustvari in inicializiraj hibridni Knowledge Bank sistem.
    
    Args:
        data_dir: Direktorij za podatke
        integrate_with_mia: Ali naj se integrira z MIA sistemom
        
    Returns:
        Inicializiran HybridKnowledgeBank
    """
    try:
        kb = HybridKnowledgeBank(data_dir=data_dir, integrate_with_mia=integrate_with_mia)
        
        # Validate system
        validation = await kb.validate_ontology()
        if not validation.valid:
            logger.warning(f"Knowledge Bank validation warnings: {validation.errors}")
            
        return kb
        
    except Exception as e:
        logger.error(f"Failed to create Hybrid Knowledge Bank: {e}")
        raise


if __name__ == "__main__":
    # Test implementation
    async def test_knowledge_bank():
        """Test hibridnega Knowledge Bank sistema"""
        try:
            logger.info("🧪 Testing Hybrid Knowledge Bank...")
            
            # Create knowledge bank
            kb = await create_hybrid_knowledge_bank()
            
            # Create test concepts
            await kb.create_concept("Person", "Person", "A human being")
            await kb.create_concept("Organization", "Organization", "A business or institution")
            
            # Create test relation
            await kb.create_relation("worksFor", "works for", 
                                   "http://mia.ai/ontology#Person", 
                                   "http://mia.ai/ontology#Organization")
            
            # Add test individual
            await kb.add_individual("john_doe", "http://mia.ai/ontology#Person", 
                                  {"name": "John Doe", "age": 30})
            
            # Test SPARQL query
            query = """
            SELECT ?person ?name WHERE {
                ?person rdf:type mia:Person .
                ?person mia:name ?name .
            }
            """
            result = await kb.query_sparql(query)
            logger.info(f"SPARQL query result: {result.results}")
            
            # Validate ontology
            validation = await kb.validate_ontology()
            logger.info(f"Validation result: {validation.valid}")
            
            # Get statistics
            stats = kb.get_detailed_statistics()
            logger.info(f"Statistics: {stats}")
            
            # Save ontology
            await kb.save_ontology()
            
            # Shutdown
            await kb.shutdown()
            
            logger.info("✅ Hybrid Knowledge Bank test completed successfully")
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise
    
    # Run test
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_knowledge_bank())