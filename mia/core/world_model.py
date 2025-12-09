#!/usr/bin/env python3
"""
MIA Konceptualno-simbolni model sveta (KSM)
Interno semantično mrežo, ontološka konsistenca, notranja interpretacija realnosti
"""

import os
import json
import logging
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import networkx as nx

class EntityType(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Types of entities in the world model"""
    CONCEPT = "concept"
    OBJECT = "object"
    AGENT = "agent"
    PROCESS = "process"
    RELATION = "relation"
    STATE = "state"
    EVENT = "event"
    GOAL = "goal"

class RelationType(Enum):
    """Types of relations between entities"""
    IS_A = "is_a"
    PART_OF = "part_of"
    CAUSES = "causes"
    ENABLES = "enables"
    REQUIRES = "requires"
    SIMILAR_TO = "similar_to"
    OPPOSITE_OF = "opposite_of"
    TEMPORAL_BEFORE = "temporal_before"
    SPATIAL_NEAR = "spatial_near"
    FUNCTIONAL_ROLE = "functional_role"

class ConfidenceLevel(Enum):
    """Confidence levels for knowledge"""
    UNCERTAIN = 0.2
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    CERTAIN = 1.0

@dataclass
class Entity:
    """Entity in the world model"""
    entity_id: str
    entity_type: EntityType
    name: str
    description: str
    properties: Dict[str, Any]
    confidence: ConfidenceLevel
    created_at: float
    last_updated: float
    source: str

@dataclass
class Relation:
    """Relation between entities"""
    relation_id: str
    relation_type: RelationType
    source_entity: str
    target_entity: str
    strength: float
    confidence: ConfidenceLevel
    properties: Dict[str, Any]
    created_at: float
    last_updated: float

@dataclass
class OntologyRule:
    """Ontological consistency rule"""
    rule_id: str
    rule_type: str
    condition: str
    consequence: str
    confidence: ConfidenceLevel
    active: bool

class WorldModel:
    """Konceptualno-simbolni model sveta"""
    
    def __init__(self, config_path: str = "mia/data/world_model/config.json"):
        self.config_path = config_path
        self.world_model_dir = Path("mia/data/world_model")
        self.world_model_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.WorldModel")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # World model components
        self.entities: Dict[str, Entity] = {}
        self.relations: Dict[str, Relation] = {}
        self.ontology_rules: Dict[str, OntologyRule] = {}
        
        # Semantic network
        self.semantic_network = nx.DiGraph()
        
        # Ontological consistency
        self.ontology_version = "1.0"
        self.consistency_score = 1.0
        
        # Load existing world model
        self._load_world_model()
        
        # Initialize basic ontology
        self._initialize_basic_ontology()
        
        self.logger.info("🌍 World Model initialized")
    
    def _load_configuration(self) -> Dict:
        """Load world model configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load world model config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default world model configuration"""
        config = {
            "enabled": True,
            "auto_consistency_check": True,
            "consistency_check_interval": 300,  # 5 minutes
            "max_entities": 10000,
            "max_relations": 50000,
            "confidence_threshold": 0.3,
            "ontology_validation": True,
            "semantic_reasoning": True,
            "world_simulation": True,
            "knowledge_integration": {
                "auto_merge_similar": True,
                "conflict_resolution": "highest_confidence",
                "source_weighting": {
                    "direct_experience": 1.0,
                    "internet_learning": 0.7,
                    "model_inference": 0.5,
                    "user_input": 0.9
                }
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _load_world_model(self):
        """Load existing world model from storage"""
        try:
            # Load entities
            entities_file = self.world_model_dir / "entities.json"
            if entities_file.exists():
                with open(entities_file, 'r') as f:
                    entities_data = json.load(f)
                
                for entity_id, entity_data in entities_data.items():
                    entity = Entity(
                        entity_id=entity_data["entity_id"],
                        entity_type=EntityType(entity_data["entity_type"]),
                        name=entity_data["name"],
                        description=entity_data["description"],
                        properties=entity_data["properties"],
                        confidence=ConfidenceLevel(entity_data["confidence"]),
                        created_at=entity_data["created_at"],
                        last_updated=entity_data["last_updated"],
                        source=entity_data["source"]
                    )
                    self.entities[entity_id] = entity
            
            # Load relations
            relations_file = self.world_model_dir / "relations.json"
            if relations_file.exists():
                with open(relations_file, 'r') as f:
                    relations_data = json.load(f)
                
                for relation_id, relation_data in relations_data.items():
                    relation = Relation(
                        relation_id=relation_data["relation_id"],
                        relation_type=RelationType(relation_data["relation_type"]),
                        source_entity=relation_data["source_entity"],
                        target_entity=relation_data["target_entity"],
                        strength=relation_data["strength"],
                        confidence=ConfidenceLevel(relation_data["confidence"]),
                        properties=relation_data["properties"],
                        created_at=relation_data["created_at"],
                        last_updated=relation_data["last_updated"]
                    )
                    self.relations[relation_id] = relation
            
            # Load ontology rules
            ontology_file = self.world_model_dir / "ontology.json"
            if ontology_file.exists():
                with open(ontology_file, 'r') as f:
                    ontology_data = json.load(f)
                
                for rule_id, rule_data in ontology_data.items():
                    rule = OntologyRule(
                        rule_id=rule_data["rule_id"],
                        rule_type=rule_data["rule_type"],
                        condition=rule_data["condition"],
                        consequence=rule_data["consequence"],
                        confidence=ConfidenceLevel(rule_data["confidence"]),
                        active=rule_data["active"]
                    )
                    self.ontology_rules[rule_id] = rule
            
            # Rebuild semantic network
            self._rebuild_semantic_network()
            
            self.logger.info(f"✅ Loaded world model: {len(self.entities)} entities, {len(self.relations)} relations")
            
        except Exception as e:
            self.logger.error(f"Failed to load world model: {e}")
    
    def _save_world_model(self):
        """Save world model to storage"""
        try:
            # Save entities
            entities_data = {}
            for entity_id, entity in self.entities.items():
                entity_dict = asdict(entity)
                entity_dict["entity_type"] = entity.entity_type.value
                entity_dict["confidence"] = entity.confidence.value
                entities_data[entity_id] = entity_dict
            
            entities_file = self.world_model_dir / "entities.json"
            with open(entities_file, 'w') as f:
                json.dump(entities_data, f, indent=2)
            
            # Save relations
            relations_data = {}
            for relation_id, relation in self.relations.items():
                relation_dict = asdict(relation)
                relation_dict["relation_type"] = relation.relation_type.value
                relation_dict["confidence"] = relation.confidence.value
                relations_data[relation_id] = relation_dict
            
            relations_file = self.world_model_dir / "relations.json"
            with open(relations_file, 'w') as f:
                json.dump(relations_data, f, indent=2)
            
            # Save ontology rules
            ontology_data = {}
            for rule_id, rule in self.ontology_rules.items():
                rule_dict = asdict(rule)
                rule_dict["confidence"] = rule.confidence.value
                ontology_data[rule_id] = rule_dict
            
            ontology_file = self.world_model_dir / "ontology.json"
            with open(ontology_file, 'w') as f:
                json.dump(ontology_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save world model: {e}")
    
    def _initialize_basic_ontology(self):
        """Initialize basic ontological structure"""
        try:
            # Create fundamental concepts if they don't exist
            fundamental_concepts = [
                ("existence", EntityType.CONCEPT, "The state of being or existing"),
                ("time", EntityType.CONCEPT, "The indefinite continued progress of existence"),
                ("space", EntityType.CONCEPT, "The dimensions of height, depth, and width"),
                ("causality", EntityType.CONCEPT, "The relationship between cause and effect"),
                ("identity", EntityType.CONCEPT, "The fact of being who or what a person or thing is"),
                ("change", EntityType.CONCEPT, "The act or instance of making or becoming different"),
                ("knowledge", EntityType.CONCEPT, "Facts, information, and skills acquired through experience"),
                ("consciousness", EntityType.CONCEPT, "The state of being aware of and able to think"),
                ("intelligence", EntityType.CONCEPT, "The ability to acquire and apply knowledge and skills"),
                ("communication", EntityType.CONCEPT, "The imparting or exchanging of information")
            ]
            
            for concept_name, entity_type, description in fundamental_concepts:
                if not self._entity_exists(concept_name):
                    self.add_entity(
                        name=concept_name,
                        entity_type=entity_type,
                        description=description,
                        properties={},
                        confidence=ConfidenceLevel.CERTAIN,
                        source="basic_ontology"
                    )
            
            # Create basic ontological rules
            basic_rules = [
                ("existence_rule", "existence", "if entity exists then entity has identity", ConfidenceLevel.CERTAIN),
                ("causality_rule", "causality", "if event A causes event B then A occurs before B", ConfidenceLevel.CERTAIN),
                ("knowledge_rule", "knowledge", "if agent has knowledge then agent can reason", ConfidenceLevel.HIGH),
                ("consciousness_rule", "consciousness", "if agent is conscious then agent can experience", ConfidenceLevel.HIGH)
            ]
            
            for rule_name, rule_type, rule_condition, confidence in basic_rules:
                if rule_name not in self.ontology_rules:
                    self.add_ontology_rule(
                        rule_type=rule_type,
                        condition=rule_condition,
                        consequence="ontological_consistency",
                        confidence=confidence
                    )
            
            self.logger.info("✅ Basic ontology initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize basic ontology: {e}")
    
    def _entity_exists(self, name: str) -> bool:
        """Check if entity with given name exists"""
        return any(entity.name == name for entity in self.entities.values())
    
    def _rebuild_semantic_network(self):
        """Rebuild semantic network from entities and relations"""
        try:
            self.semantic_network.clear()
            
            # Add entities as nodes
            for entity_id, entity in self.entities.items():
                self.semantic_network.add_node(
                    entity_id,
                    name=entity.name,
                    type=entity.entity_type.value,
                    confidence=entity.confidence.value
                )
            
            # Add relations as edges
            for relation_id, relation in self.relations.items():
                if (relation.source_entity in self.entities and 
                    relation.target_entity in self.entities):
                    self.semantic_network.add_edge(
                        relation.source_entity,
                        relation.target_entity,
                        relation_type=relation.relation_type.value,
                        strength=relation.strength,
                        confidence=relation.confidence.value
                    )
            
            self.logger.debug(f"Semantic network rebuilt: {len(self.semantic_network.nodes)} nodes, {len(self.semantic_network.edges)} edges")
            
        except Exception as e:
            self.logger.error(f"Failed to rebuild semantic network: {e}")
    
    def add_entity(self, name: str, entity_type: EntityType, description: str,
                   properties: Dict[str, Any], confidence: ConfidenceLevel,
                   source: str) -> str:
        """Add new entity to world model"""
        try:
            # Generate entity ID
            entity_id = hashlib.sha256(f"{name}_{entity_type.value}_{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}".encode()).hexdigest()[:16]
            
            # Create entity
            entity = Entity(
                entity_id=entity_id,
                entity_type=entity_type,
                name=name,
                description=description,
                properties=properties,
                confidence=confidence,
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                last_updated=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                source=source
            )
            
            # Check for conflicts
            if self._check_entity_conflicts(entity):
                self.logger.warning(f"Entity conflict detected for: {name}")
                return ""
            
            # Add to world model
            self.entities[entity_id] = entity
            
            # Update semantic network
            self.semantic_network.add_node(
                entity_id,
                name=name,
                type=entity_type.value,
                confidence=confidence.value
            )
            
            # Save world model
            self._save_world_model()
            
            self.logger.info(f"✅ Added entity: {name} ({entity_type.value})")
            return entity_id
            
        except Exception as e:
            self.logger.error(f"Failed to add entity: {e}")
            return ""
    
    def add_relation(self, source_entity_id: str, target_entity_id: str,
                     relation_type: RelationType, strength: float,
                     confidence: ConfidenceLevel, properties: Dict[str, Any] = None) -> str:
        """Add new relation to world model"""
        try:
            # Validate entities exist
            if source_entity_id not in self.entities or target_entity_id not in self.entities:
                self.logger.error("Cannot create relation: one or both entities do not exist")
                return ""
            
            # Generate relation ID
            relation_id = hashlib.sha256(f"{source_entity_id}_{relation_type.value}_{target_entity_id}_{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}".encode()).hexdigest()[:16]
            
            # Create relation
            relation = Relation(
                relation_id=relation_id,
                relation_type=relation_type,
                source_entity=source_entity_id,
                target_entity=target_entity_id,
                strength=strength,
                confidence=confidence,
                properties=properties or {},
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                last_updated=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            )
            
            # Check ontological consistency
            if not self._check_relation_consistency(relation):
                self.logger.warning(f"Relation consistency check failed")
                return ""
            
            # Add to world model
            self.relations[relation_id] = relation
            
            # Update semantic network
            self.semantic_network.add_edge(
                source_entity_id,
                target_entity_id,
                relation_type=relation_type.value,
                strength=strength,
                confidence=confidence.value
            )
            
            # Save world model
            self._save_world_model()
            
            source_name = self.entities[source_entity_id].name
            target_name = self.entities[target_entity_id].name
            self.logger.info(f"✅ Added relation: {source_name} {relation_type.value} {target_name}")
            return relation_id
            
        except Exception as e:
            self.logger.error(f"Failed to add relation: {e}")
            return ""
    
    def add_ontology_rule(self, rule_type: str, condition: str, consequence: str,
                          confidence: ConfidenceLevel) -> str:
        """Add new ontology rule"""
        try:
            # Generate rule ID
            rule_id = hashlib.sha256(f"{rule_type}_{condition}_{self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}".encode()).hexdigest()[:16]
            
            # Create rule
            rule = OntologyRule(
                rule_id=rule_id,
                rule_type=rule_type,
                condition=condition,
                consequence=consequence,
                confidence=confidence,
                active=True
            )
            
            # Add to ontology
            self.ontology_rules[rule_id] = rule
            
            # Save world model
            self._save_world_model()
            
            self.logger.info(f"✅ Added ontology rule: {rule_type}")
            return rule_id
            
        except Exception as e:
            self.logger.error(f"Failed to add ontology rule: {e}")
            return ""
    
    def _check_entity_conflicts(self, entity: Entity) -> bool:
        """Check for entity conflicts"""
        try:
            # Check for duplicate names with different types
            for existing_entity in self.entities.values():
                if (existing_entity.name == entity.name and 
                    existing_entity.entity_type != entity.entity_type):
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check entity conflicts: {e}")
            return True
    
    def _check_relation_consistency(self, relation: Relation) -> bool:
        """Check relation consistency with ontology"""
        try:
            # Basic consistency checks
            source_entity = self.entities[relation.source_entity]
            target_entity = self.entities[relation.target_entity]
            
            # Check type compatibility
            if relation.relation_type == RelationType.IS_A:
                # IS_A relations should be between compatible types
                if source_entity.entity_type == target_entity.entity_type:
                    return True
            
            elif relation.relation_type == RelationType.PART_OF:
                # PART_OF relations should make sense
                if (source_entity.entity_type in [EntityType.OBJECT, EntityType.CONCEPT] and
                    target_entity.entity_type in [EntityType.OBJECT, EntityType.CONCEPT]):
                    return True
            
            elif relation.relation_type == RelationType.CAUSES:
                # CAUSES relations should be between events or processes
                if (source_entity.entity_type in [EntityType.EVENT, EntityType.PROCESS] and
                    target_entity.entity_type in [EntityType.EVENT, EntityType.PROCESS, EntityType.STATE]):
                    return True
            
            # Default to allowing relation if no specific rule applies
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check relation consistency: {e}")
            return False
    
    def query_entities(self, entity_type: Optional[EntityType] = None,
                       name_pattern: Optional[str] = None,
                       min_confidence: Optional[ConfidenceLevel] = None) -> List[Entity]:
        """Query entities based on criteria"""
        try:
            results = []
            
            for entity in self.entities.values():
                # Filter by type
                if entity_type and entity.entity_type != entity_type:
                    continue
                
                # Filter by name pattern
                if name_pattern and name_pattern.lower() not in entity.name.lower():
                    continue
                
                # Filter by confidence
                if min_confidence and entity.confidence.value < min_confidence.value:
                    continue
                
                results.append(entity)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to query entities: {e}")
            return []
    
    def find_related_entities(self, entity_id: str, relation_types: Optional[List[RelationType]] = None,
                              max_depth: int = 2) -> List[Tuple[str, str, float]]:
        """Find entities related to given entity"""
        try:
            if entity_id not in self.entities:
                return []
            
            related = []
            
            # Use semantic network for efficient traversal
            if entity_id in self.semantic_network:
                # Get direct neighbors
                for neighbor in self.semantic_network.neighbors(entity_id):
                    edge_data = self.semantic_network.get_edge_data(entity_id, neighbor)
                    if edge_data:
                        relation_type = edge_data.get('relation_type', '')
                        confidence = edge_data.get('confidence', 0.0)
                        
                        # Filter by relation type if specified
                        if relation_types:
                            if any(rt.value == relation_type for rt in relation_types):
                                related.append((neighbor, relation_type, confidence))
                        else:
                            related.append((neighbor, relation_type, confidence))
                
                # Get indirect neighbors if max_depth > 1
                if max_depth > 1:
                    for neighbor in list(related):
                        neighbor_id = neighbor[0]
                        for second_neighbor in self.semantic_network.neighbors(neighbor_id):
                            if second_neighbor != entity_id and second_neighbor not in [r[0] for r in related]:
                                edge_data = self.semantic_network.get_edge_data(neighbor_id, second_neighbor)
                                if edge_data:
                                    relation_type = edge_data.get('relation_type', '')
                                    confidence = edge_data.get('confidence', 0.0) * 0.8  # Reduce confidence for indirect relations
                                    related.append((second_neighbor, f"indirect_{relation_type}", confidence))
            
            return related
            
        except Exception as e:
            self.logger.error(f"Failed to find related entities: {e}")
            return []
    
    def check_ontological_consistency(self) -> Tuple[bool, List[str]]:
        """Check ontological consistency of the world model"""
        try:
            issues = []
            
            # Check for circular IS_A relations
            for relation in self.relations.values():
                if relation.relation_type == RelationType.IS_A:
                    if self._has_circular_isa(relation.source_entity, relation.target_entity):
                        issues.append(f"Circular IS_A relation detected: {relation.source_entity} -> {relation.target_entity}")
            
            # Check for contradictory relations
            for entity_id in self.entities:
                related = self.find_related_entities(entity_id, max_depth=1)
                for i, (related_id1, rel_type1, _) in enumerate(related):
                    for related_id2, rel_type2, _ in related[i+1:]:
                        if related_id1 == related_id2:
                            if self._are_contradictory_relations(rel_type1, rel_type2):
                                issues.append(f"Contradictory relations: {entity_id} has both {rel_type1} and {rel_type2} with {related_id1}")
            
            # Update consistency score
            total_checks = len(self.relations) + len(self.entities)
            if total_checks > 0:
                self.consistency_score = max(0.0, 1.0 - (len(issues) / total_checks))
            
            return len(issues) == 0, issues
            
        except Exception as e:
            self.logger.error(f"Failed to check ontological consistency: {e}")
            return False, [f"Consistency check error: {e}"]
    
    def _has_circular_isa(self, source_id: str, target_id: str, visited: Set[str] = None) -> bool:
        """Check for circular IS_A relations"""
        if visited is None:
            visited = set()
        
        if source_id in visited:
            return True
        
        visited.add(source_id)
        
        # Find all IS_A relations from target
        for relation in self.relations.values():
            if (relation.relation_type == RelationType.IS_A and 
                relation.source_entity == target_id):
                if self._has_circular_isa(source_id, relation.target_entity, visited.copy()):
                    return True
        
        return False
    
    def _are_contradictory_relations(self, rel_type1: str, rel_type2: str) -> bool:
        """Check if two relation types are contradictory"""
        contradictory_pairs = [
            ("similar_to", "opposite_of"),
            ("causes", "prevents"),
            ("enables", "disables")
        ]
        
        for pair in contradictory_pairs:
            if (rel_type1 in pair and rel_type2 in pair and rel_type1 != rel_type2):
                return True
        
        return False
    
    def integrate_knowledge(self, knowledge_item: Dict[str, Any], source: str) -> bool:
        """Integrate new knowledge into world model"""
        try:
            # Extract entities and relations from knowledge item
            if "entities" in knowledge_item:
                for entity_data in knowledge_item["entities"]:
                    self.add_entity(
                        name=entity_data["name"],
                        entity_type=EntityType(entity_data["type"]),
                        description=entity_data.get("description", ""),
                        properties=entity_data.get("properties", {}),
                        confidence=ConfidenceLevel(entity_data.get("confidence", 0.6)),
                        source=source
                    )
            
            if "relations" in knowledge_item:
                for relation_data in knowledge_item["relations"]:
                    # Find entity IDs by name
                    source_entity_id = self._find_entity_by_name(relation_data["source"])
                    target_entity_id = self._find_entity_by_name(relation_data["target"])
                    
                    if source_entity_id and target_entity_id:
                        self.add_relation(
                            source_entity_id=source_entity_id,
                            target_entity_id=target_entity_id,
                            relation_type=RelationType(relation_data["type"]),
                            strength=relation_data.get("strength", 0.7),
                            confidence=ConfidenceLevel(relation_data.get("confidence", 0.6)),
                            properties=relation_data.get("properties", {})
                        )
            
            self.logger.info(f"✅ Integrated knowledge from: {source}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to integrate knowledge: {e}")
            return False
    
    def _find_entity_by_name(self, name: str) -> Optional[str]:
        """Find entity ID by name"""
        for entity_id, entity in self.entities.items():
            if entity.name.lower() == name.lower():
                return entity_id
        return None
    
    def get_world_model_status(self) -> Dict[str, Any]:
        """Get world model status"""
        try:
            consistency_ok, issues = self.check_ontological_consistency()
            
            return {
                "enabled": self.config.get("enabled", True),
                "ontology_version": self.ontology_version,
                "entities_count": len(self.entities),
                "relations_count": len(self.relations),
                "ontology_rules_count": len(self.ontology_rules),
                "consistency_score": self.consistency_score,
                "consistency_ok": consistency_ok,
                "consistency_issues": len(issues),
                "semantic_network_nodes": len(self.semantic_network.nodes),
                "semantic_network_edges": len(self.semantic_network.edges)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get world model status: {e}")
            return {"error": str(e)}

# Global instance
world_model = WorldModel()