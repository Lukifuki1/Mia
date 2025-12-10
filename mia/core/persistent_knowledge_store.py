#!/usr/bin/env python3
"""
Persistent Knowledge Store - PRIORITETA 1
==========================================

Osnovno jedro za shranjevanje in pridobivanje znanja.
To je PRVA komponenta, ki jo moramo implementirati za avtonomno učečo se MIA.
"""

import json
import logging
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class Fact:
    """Reprezentacija dejstva v bazi znanja"""
    entity: str
    property: str
    value: Any
    source: str
    confidence: float
    timestamp: float
    user_id: Optional[str] = None

@dataclass
class Relation:
    """Reprezentacija relacije med entitetami"""
    subject: str
    predicate: str
    object: str
    source: str
    confidence: float
    timestamp: float

@dataclass
class UserModel:
    """Model uporabnika za personalizacijo"""
    user_id: str
    communication_style: Dict[str, str]
    interests: List[str]
    knowledge_contributions: int
    interaction_count: int
    last_interaction: float
    created_at: float

class PersistentKnowledgeStore:
    """
    Osnovna baza znanja za MIA z persistentnim shranjevanjem.
    
    To je JEDRO avtonomnega učenja - brez tega ni mogoče shraniti naučenega znanja.
    """
    
    def __init__(self, data_dir: str = "data/knowledge"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Core data structures
        self.facts: Dict[str, Dict[str, Fact]] = defaultdict(dict)  # entity -> property -> Fact
        self.relations: List[Relation] = []
        self.user_models: Dict[str, UserModel] = {}
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Statistics
        self.stats = {
            'total_facts': 0,
            'total_relations': 0,
            'total_users': 0,
            'total_conversations': 0,
            'last_updated': time.time()
        }
        
        # Load existing data
        self.load_from_disk()
        
        logger.info(f"Initialized knowledge store with {self.stats['total_facts']} facts")
        
    def add_fact(self, entity: str, property: str, value: Any, 
                 source: str = "user", confidence: float = 0.8, user_id: str = None) -> bool:
        """
        Dodaj dejstvo v bazo znanja.
        
        Args:
            entity: Entiteta (npr. "aspirin")
            property: Lastnost (npr. "type", "use", "side_effects")
            value: Vrednost (npr. "medication", "pain relief")
            source: Vir informacije (npr. "user", "web", "wikipedia")
            confidence: Zanesljivost (0.0-1.0)
            user_id: ID uporabnika, ki je prispeval informacijo
            
        Returns:
            bool: True če je dejstvo dodano, False če že obstaja
        """
        try:
            # Normalize inputs
            entity = entity.strip().lower()
            property = property.strip().lower()
            
            if not entity or not property or not value:
                logger.warning(f"Invalid fact: entity='{entity}', property='{property}', value='{value}'")
                return False
                
            # Check if fact already exists
            if entity in self.facts and property in self.facts[entity]:
                existing_fact = self.facts[entity][property]
                # Update if new confidence is higher
                if confidence > existing_fact.confidence:
                    existing_fact.value = value
                    existing_fact.confidence = confidence
                    existing_fact.timestamp = time.time()
                    existing_fact.source = source
                    logger.info(f"Updated fact: {entity}.{property} = {value} (confidence: {confidence})")
                    self.save_to_disk()
                    return True
                else:
                    logger.debug(f"Fact already exists with higher confidence: {entity}.{property}")
                    return False
            
            # Create new fact
            fact = Fact(
                entity=entity,
                property=property,
                value=value,
                source=source,
                confidence=confidence,
                timestamp=time.time(),
                user_id=user_id
            )
            
            self.facts[entity][property] = fact
            self.stats['total_facts'] += 1
            self.stats['last_updated'] = time.time()
            
            # Update user contribution count
            if user_id:
                self.update_user_contribution(user_id)
                
            logger.info(f"Added fact: {entity}.{property} = {value} (source: {source}, confidence: {confidence})")
            
            # Auto-save after adding fact
            self.save_to_disk()
            return True
            
        except Exception as e:
            logger.error(f"Error adding fact: {e}")
            return False
            
    def query_knowledge(self, entity: str, property: str = None) -> Optional[Any]:
        """
        Poizveduj po znanju.
        
        Args:
            entity: Entiteta za iskanje
            property: Specifična lastnost (če None, vrni vse lastnosti)
            
        Returns:
            Dejstvo/a ali None če ni najdeno
        """
        try:
            entity = entity.strip().lower()
            
            if entity not in self.facts:
                return None
                
            if property:
                property = property.strip().lower()
                fact = self.facts[entity].get(property)
                return fact.value if fact else None
            else:
                # Return all properties for entity
                return {prop: fact.value for prop, fact in self.facts[entity].items()}
                
        except Exception as e:
            logger.error(f"Error querying knowledge: {e}")
            return None
            
    def search_entities(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Poišči entitete, ki se ujemajo z iskalno poizvedbo.
        
        Args:
            query: Iskalna poizvedba
            limit: Maksimalno število rezultatov
            
        Returns:
            Seznam ujemajočih se entitet z njihovimi lastnostmi
        """
        try:
            query = query.strip().lower()
            results = []
            
            for entity, properties in self.facts.items():
                # Check if query matches entity name
                if query in entity:
                    entity_data = {
                        'entity': entity,
                        'properties': {prop: fact.value for prop, fact in properties.items()},
                        'relevance': 1.0 if query == entity else 0.8
                    }
                    results.append(entity_data)
                    continue
                    
                # Check if query matches any property value
                for prop, fact in properties.items():
                    if isinstance(fact.value, str) and query in fact.value.lower():
                        entity_data = {
                            'entity': entity,
                            'properties': {prop: fact.value for prop, fact in properties.items()},
                            'relevance': 0.6
                        }
                        results.append(entity_data)
                        break
                        
            # Sort by relevance and limit results
            results.sort(key=lambda x: x['relevance'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching entities: {e}")
            return []
            
    def add_relation(self, subject: str, predicate: str, object: str,
                    source: str = "user", confidence: float = 0.8) -> bool:
        """
        Dodaj relacijo med entitetami.
        
        Args:
            subject: Subjekt relacije
            predicate: Predikat (vrsta relacije)
            object: Objekt relacije
            source: Vir informacije
            confidence: Zanesljivost
            
        Returns:
            bool: True če je relacija dodana
        """
        try:
            relation = Relation(
                subject=subject.strip().lower(),
                predicate=predicate.strip().lower(),
                object=object.strip().lower(),
                source=source,
                confidence=confidence,
                timestamp=time.time()
            )
            
            # Check for duplicates
            for existing in self.relations:
                if (existing.subject == relation.subject and 
                    existing.predicate == relation.predicate and
                    existing.object == relation.object):
                    logger.debug(f"Relation already exists: {subject} {predicate} {object}")
                    return False
                    
            self.relations.append(relation)
            self.stats['total_relations'] += 1
            self.stats['last_updated'] = time.time()
            
            logger.info(f"Added relation: {subject} {predicate} {object}")
            self.save_to_disk()
            return True
            
        except Exception as e:
            logger.error(f"Error adding relation: {e}")
            return False
            
    def get_related_entities(self, entity: str, predicate: str = None) -> List[str]:
        """
        Poišči entitete, povezane z dano entiteto.
        
        Args:
            entity: Entiteta za iskanje povezav
            predicate: Specifičen predikat (če None, vsi predikati)
            
        Returns:
            Seznam povezanih entitet
        """
        try:
            entity = entity.strip().lower()
            related = []
            
            for relation in self.relations:
                if relation.subject == entity:
                    if predicate is None or relation.predicate == predicate.strip().lower():
                        related.append(relation.object)
                elif relation.object == entity:
                    if predicate is None or relation.predicate == predicate.strip().lower():
                        related.append(relation.subject)
                        
            return list(set(related))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error getting related entities: {e}")
            return []
            
    def update_user_model(self, user_id: str, **kwargs) -> None:
        """
        Posodobi model uporabnika.
        
        Args:
            user_id: ID uporabnika
            **kwargs: Lastnosti za posodobitev
        """
        try:
            if user_id not in self.user_models:
                self.user_models[user_id] = UserModel(
                    user_id=user_id,
                    communication_style={},
                    interests=[],
                    knowledge_contributions=0,
                    interaction_count=0,
                    last_interaction=time.time(),
                    created_at=time.time()
                )
                self.stats['total_users'] += 1
                
            user_model = self.user_models[user_id]
            
            # Update provided attributes
            for key, value in kwargs.items():
                if hasattr(user_model, key):
                    if key == 'interests' and isinstance(value, list):
                        # Merge interests
                        user_model.interests = list(set(user_model.interests + value))
                    elif key == 'communication_style' and isinstance(value, dict):
                        # Merge communication style
                        user_model.communication_style.update(value)
                    else:
                        setattr(user_model, key, value)
                        
            user_model.last_interaction = time.time()
            user_model.interaction_count += 1
            
            logger.debug(f"Updated user model for {user_id}")
            self.save_to_disk()
            
        except Exception as e:
            logger.error(f"Error updating user model: {e}")
            
    def update_user_contribution(self, user_id: str) -> None:
        """Posodobi število prispevkov uporabnika."""
        if user_id in self.user_models:
            self.user_models[user_id].knowledge_contributions += 1
        else:
            self.update_user_model(user_id, knowledge_contributions=1)
            
    def add_conversation(self, user_id: str, user_input: str, mia_response: str, 
                        metadata: Dict[str, Any] = None) -> None:
        """
        Dodaj pogovor v zgodovino.
        
        Args:
            user_id: ID uporabnika
            user_input: Uporabniški vnos
            mia_response: MIA-in odgovor
            metadata: Dodatni metapodatki
        """
        try:
            conversation = {
                'user_id': user_id,
                'user_input': user_input,
                'mia_response': mia_response,
                'timestamp': time.time(),
                'metadata': metadata or {}
            }
            
            self.conversation_history.append(conversation)
            self.stats['total_conversations'] += 1
            
            # Keep only last 1000 conversations to prevent memory issues
            if len(self.conversation_history) > 1000:
                self.conversation_history = self.conversation_history[-1000:]
                
            # Update user model
            self.update_user_model(user_id)
            
            logger.debug(f"Added conversation for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error adding conversation: {e}")
            
    def get_user_conversations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Pridobi zadnje pogovore uporabnika."""
        try:
            user_conversations = [
                conv for conv in self.conversation_history 
                if conv['user_id'] == user_id
            ]
            return user_conversations[-limit:]  # Last N conversations
            
        except Exception as e:
            logger.error(f"Error getting user conversations: {e}")
            return []
            
    def get_statistics(self) -> Dict[str, Any]:
        """Pridobi statistike baze znanja."""
        return {
            **self.stats,
            'entities_count': len(self.facts),
            'avg_facts_per_entity': self.stats['total_facts'] / max(len(self.facts), 1),
            'active_users': len([u for u in self.user_models.values() 
                               if time.time() - u.last_interaction < 86400])  # Last 24h
        }
        
    def save_to_disk(self) -> bool:
        """Shrani bazo znanja na disk."""
        try:
            # Prepare data for serialization
            data = {
                'facts': {
                    entity: {prop: asdict(fact) for prop, fact in properties.items()}
                    for entity, properties in self.facts.items()
                },
                'relations': [asdict(relation) for relation in self.relations],
                'user_models': {uid: asdict(model) for uid, model in self.user_models.items()},
                'conversation_history': self.conversation_history[-1000:],  # Last 1000
                'stats': self.stats,
                'version': '1.0',
                'saved_at': time.time()
            }
            
            # Save to JSON file
            knowledge_file = self.data_dir / 'knowledge_base.json'
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            # Create backup
            backup_file = self.data_dir / f'knowledge_backup_{int(time.time())}.json'
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            # Keep only last 5 backups
            backup_files = sorted(self.data_dir.glob('knowledge_backup_*.json'))
            for old_backup in backup_files[:-5]:
                old_backup.unlink()
                
            logger.info(f"Saved knowledge base with {self.stats['total_facts']} facts")
            return True
            
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
            return False
            
    def load_from_disk(self) -> bool:
        """Naloži bazo znanja z diska."""
        try:
            knowledge_file = self.data_dir / 'knowledge_base.json'
            if not knowledge_file.exists():
                logger.info("No existing knowledge base found, starting fresh")
                return True
                
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Load facts
            for entity, properties in data.get('facts', {}).items():
                for prop, fact_data in properties.items():
                    fact = Fact(**fact_data)
                    self.facts[entity][prop] = fact
                    
            # Load relations
            for relation_data in data.get('relations', []):
                relation = Relation(**relation_data)
                self.relations.append(relation)
                
            # Load user models
            for uid, model_data in data.get('user_models', {}).items():
                model = UserModel(**model_data)
                self.user_models[uid] = model
                
            # Load conversation history
            self.conversation_history = data.get('conversation_history', [])
            
            # Load stats
            self.stats.update(data.get('stats', {}))
            
            logger.info(f"Loaded knowledge base: {len(self.facts)} entities, "
                       f"{self.stats['total_facts']} facts, {len(self.user_models)} users")
            return True
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            return False
            
    def clear_all_data(self) -> bool:
        """Počisti vso bazo znanja (PREVIDNO!)."""
        try:
            self.facts.clear()
            self.relations.clear()
            self.user_models.clear()
            self.conversation_history.clear()
            self.stats = {
                'total_facts': 0,
                'total_relations': 0,
                'total_users': 0,
                'total_conversations': 0,
                'last_updated': time.time()
            }
            
            self.save_to_disk()
            logger.warning("Cleared all knowledge base data")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            return False

# Example usage and testing
def main():
    """Primer uporabe PersistentKnowledgeStore"""
    
    # Initialize knowledge store
    kb = PersistentKnowledgeStore("data/test_knowledge")
    
    print("=== MIA Knowledge Store Test ===")
    
    # Add some facts
    print("\n1. Adding facts...")
    kb.add_fact("aspirin", "type", "medication", "user", 0.9, "user1")
    kb.add_fact("aspirin", "use", "pain relief", "user", 0.8, "user1")
    kb.add_fact("aspirin", "side_effects", "stomach irritation", "web", 0.7)
    kb.add_fact("diabetes", "type", "medical condition", "user", 0.9, "user2")
    kb.add_fact("diabetes", "symptoms", "increased thirst", "web", 0.8)
    
    # Add relations
    print("\n2. Adding relations...")
    kb.add_relation("aspirin", "treats", "headache", "user", 0.8)
    kb.add_relation("aspirin", "contraindicated_with", "bleeding_disorders", "web", 0.9)
    
    # Query knowledge
    print("\n3. Querying knowledge...")
    aspirin_info = kb.query_knowledge("aspirin")
    print(f"Aspirin info: {aspirin_info}")
    
    aspirin_type = kb.query_knowledge("aspirin", "type")
    print(f"Aspirin type: {aspirin_type}")
    
    # Search entities
    print("\n4. Searching entities...")
    search_results = kb.search_entities("pain")
    print(f"Search results for 'pain': {search_results}")
    
    # Get related entities
    print("\n5. Getting related entities...")
    related = kb.get_related_entities("aspirin")
    print(f"Entities related to aspirin: {related}")
    
    # Add conversation
    print("\n6. Adding conversation...")
    kb.add_conversation(
        "user1", 
        "What is aspirin?", 
        "Aspirin is a medication used for pain relief.",
        {"response_time": 1.2, "confidence": 0.8}
    )
    
    # Get statistics
    print("\n7. Statistics...")
    stats = kb.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
        
    print("\n=== Test completed ===")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()