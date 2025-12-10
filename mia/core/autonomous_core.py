#!/usr/bin/env python3
"""
MIA Autonomous Learning Core
============================

Centralno jedro za avtonomno učenje iz interneta in interakcij z uporabnikom.
Implementira world model, knowledge graph in kontinuirano učenje.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
import networkx as nx
from datetime import datetime

# AI/ML imports
try:
    import torch
    import transformers
    from sentence_transformers import SentenceTransformer
    ADVANCED_AI_AVAILABLE = True
except ImportError:
    ADVANCED_AI_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class Concept:
    """Reprezentacija koncepta v world model"""
    name: str
    type: str
    properties: Dict[str, Any]
    confidence: float
    created_at: float
    updated_at: float

@dataclass
class Relation:
    """Reprezentacija relacije med koncepti"""
    subject: str
    predicate: str
    object: str
    confidence: float
    source: str
    timestamp: float

@dataclass
class UserInteraction:
    """Reprezentacija interakcije z uporabnikom"""
    user_id: str
    query: str
    response: str
    context: Dict[str, Any]
    feedback: Optional[str]
    timestamp: float

class WorldModel:
    """Interna reprezentacija sveta in znanja"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.concepts: Dict[str, Concept] = {}
        self.relations: List[Relation] = []
        self.graph = nx.MultiDiGraph()
        
        # Load existing data
        self.load_world_model()
        
    def add_concept(self, name: str, concept_type: str, properties: Dict[str, Any], confidence: float = 0.8):
        """Dodaj nov koncept v world model"""
        concept = Concept(
            name=name,
            type=concept_type,
            properties=properties,
            confidence=confidence,
            created_at=time.time(),
            updated_at=time.time()
        )
        
        self.concepts[name] = concept
        self.graph.add_node(name, **asdict(concept))
        
        logger.info(f"Added concept: {name} ({concept_type})")
        
    def add_relation(self, subject: str, predicate: str, obj: str, confidence: float = 0.8, source: str = "unknown"):
        """Dodaj relacijo med koncepti"""
        relation = Relation(
            subject=subject,
            predicate=predicate,
            object=obj,
            confidence=confidence,
            source=source,
            timestamp=time.time()
        )
        
        self.relations.append(relation)
        self.graph.add_edge(subject, obj, 
                           relation=predicate, 
                           confidence=confidence,
                           source=source,
                           timestamp=time.time())
        
        logger.info(f"Added relation: {subject} --{predicate}--> {obj}")
        
    def query_related_concepts(self, concept: str, max_depth: int = 2) -> List[str]:
        """Poišči povezane koncepte"""
        if concept not in self.graph:
            return []
            
        related = []
        for depth in range(1, max_depth + 1):
            for node in nx.single_source_shortest_path_length(self.graph, concept, cutoff=depth):
                if node != concept and node not in related:
                    related.append(node)
                    
        return related
        
    def get_concept_info(self, concept: str) -> Optional[Dict[str, Any]]:
        """Pridobi informacije o konceptu"""
        if concept in self.concepts:
            return asdict(self.concepts[concept])
        return None
        
    def save_world_model(self):
        """Shrani world model na disk"""
        world_data = {
            'concepts': {name: asdict(concept) for name, concept in self.concepts.items()},
            'relations': [asdict(relation) for relation in self.relations]
        }
        
        world_file = self.data_dir / 'world_model.json'
        with open(world_file, 'w', encoding='utf-8') as f:
            json.dump(world_data, f, indent=2, ensure_ascii=False)
            
    def load_world_model(self):
        """Naloži world model z diska"""
        world_file = self.data_dir / 'world_model.json'
        if not world_file.exists():
            return
            
        try:
            with open(world_file, 'r', encoding='utf-8') as f:
                world_data = json.load(f)
                
            # Load concepts
            for name, concept_data in world_data.get('concepts', {}).items():
                concept = Concept(**concept_data)
                self.concepts[name] = concept
                self.graph.add_node(name, **concept_data)
                
            # Load relations
            for relation_data in world_data.get('relations', []):
                relation = Relation(**relation_data)
                self.relations.append(relation)
                self.graph.add_edge(relation.subject, relation.object,
                                   relation=relation.predicate,
                                   confidence=relation.confidence,
                                   source=relation.source,
                                   timestamp=relation.timestamp)
                                   
            logger.info(f"Loaded world model: {len(self.concepts)} concepts, {len(self.relations)} relations")
            
        except Exception as e:
            logger.error(f"Error loading world model: {e}")

class UserModel:
    """Model uporabnika za personalizacijo"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.preferences: Dict[str, Any] = {}
        self.interests: List[str] = []
        self.communication_style: Dict[str, str] = {
            'formality': 'neutral',
            'detail_level': 'medium',
            'language': 'sl'
        }
        self.interaction_history: List[UserInteraction] = []
        
    def update_from_interaction(self, interaction: UserInteraction):
        """Posodobi model iz interakcije"""
        self.interaction_history.append(interaction)
        
        # Analiziraj komunikacijski stil
        if len(interaction.query.split()) > 20:
            self.communication_style['detail_level'] = 'high'
        elif len(interaction.query.split()) < 5:
            self.communication_style['detail_level'] = 'low'
            
        # Analiziraj formalnost
        if any(word in interaction.query.lower() for word in ['prosim', 'hvala', 'oprostite']):
            self.communication_style['formality'] = 'formal'
        elif any(word in interaction.query.lower() for word in ['ej', 'hej', 'kul']):
            self.communication_style['formality'] = 'informal'
            
        logger.debug(f"Updated user model for {self.user_id}")
        
    def get_response_style(self) -> Dict[str, str]:
        """Vrni prilagojeni stil odgovarjanja"""
        return self.communication_style.copy()

class WebLearner:
    """Komponenta za učenje iz interneta"""
    
    def __init__(self, world_model: WorldModel):
        self.world_model = world_model
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def learn_from_url(self, url: str) -> bool:
        """Učenje iz spletne strani"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    await self.process_content(content, url)
                    return True
                    
        except Exception as e:
            logger.error(f"Error learning from {url}: {e}")
            
        return False
        
    async def process_content(self, content: str, source: str):
        """Procesiraj vsebino in ekstraktiraj znanje"""
        # Osnovni ekstrakcijon znanja (lahko bi uporabili NLP)
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 200:
                # Poskusi ekstraktirati preproste dejstva
                if ' je ' in line or ' is ' in line:
                    await self.extract_simple_fact(line, source)
                    
    async def extract_simple_fact(self, sentence: str, source: str):
        """Ekstraktiraj preprosto dejstvo iz stavka"""
        try:
            # Preprosta hevristika za ekstrakcijon dejstev
            if ' je ' in sentence:
                parts = sentence.split(' je ', 1)
                if len(parts) == 2:
                    subject = parts[0].strip()
                    predicate_object = parts[1].strip()
                    
                    # Dodaj v world model
                    self.world_model.add_concept(subject, "entity", {"description": predicate_object}, confidence=0.6)
                    self.world_model.add_relation(subject, "je", predicate_object, confidence=0.6, source=source)
                    
        except Exception as e:
            logger.debug(f"Error extracting fact from '{sentence}': {e}")

class AutonomousCore:
    """Glavno avtonomno jedro MIA"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        
        # Komponente
        self.world_model = WorldModel(data_dir)
        self.user_models: Dict[str, UserModel] = {}
        self.web_learner = WebLearner(self.world_model)
        
        # AI modeli (če so na voljo)
        self.language_model = None
        self.embedding_model = None
        
        if ADVANCED_AI_AVAILABLE:
            self.initialize_ai_models()
            
        # Učenje v ozadju
        self.learning_task = None
        self.is_learning = False
        
    def initialize_ai_models(self):
        """Inicializiraj AI modele"""
        try:
            # Embedding model za semantic search
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Initialized embedding model")
            
        except Exception as e:
            logger.error(f"Error initializing AI models: {e}")
            
    def get_user_model(self, user_id: str) -> UserModel:
        """Pridobi ali ustvari model uporabnika"""
        if user_id not in self.user_models:
            self.user_models[user_id] = UserModel(user_id)
        return self.user_models[user_id]
        
    async def process_query(self, query: str, user_id: str, context: Dict[str, Any] = None) -> str:
        """Glavna funkcija za procesiranje poizvedb"""
        context = context or {}
        user_model = self.get_user_model(user_id)
        
        # 1. Poišči relevantno znanje
        relevant_concepts = self.find_relevant_knowledge(query)
        
        # 2. Generiraj odgovor
        response = await self.generate_response(query, relevant_concepts, user_model)
        
        # 3. Shrani interakcijo za učenje
        interaction = UserInteraction(
            user_id=user_id,
            query=query,
            response=response,
            context=context,
            feedback=None,
            timestamp=time.time()
        )
        
        user_model.update_from_interaction(interaction)
        
        return response
        
    def find_relevant_knowledge(self, query: str) -> List[str]:
        """Poišči relevantno znanje za poizvedbo"""
        relevant = []
        
        # Preprosto iskanje po ključnih besedah
        query_words = query.lower().split()
        
        for concept_name in self.world_model.concepts:
            if any(word in concept_name.lower() for word in query_words):
                relevant.append(concept_name)
                # Dodaj povezane koncepte
                related = self.world_model.query_related_concepts(concept_name, max_depth=1)
                relevant.extend(related[:3])  # Omeji na 3 povezane
                
        return list(set(relevant))[:10]  # Omeji na 10 konceptov
        
    async def generate_response(self, query: str, relevant_concepts: List[str], user_model: UserModel) -> str:
        """Generiraj odgovor na podlagi znanja in uporabniškega modela"""
        style = user_model.get_response_style()
        
        if not relevant_concepts:
            return self.generate_default_response(query, style)
            
        # Zberi informacije o relevantnih konceptih
        knowledge_info = []
        for concept in relevant_concepts:
            info = self.world_model.get_concept_info(concept)
            if info:
                knowledge_info.append(f"{concept}: {info.get('properties', {}).get('description', 'Ni opisa')}")
                
        # Generiraj odgovor na podlagi znanja
        if knowledge_info:
            response = f"Na podlagi mojega znanja:\n\n"
            response += "\n".join(knowledge_info[:3])  # Omeji na 3 informacije
            
            if style['detail_level'] == 'high':
                response += f"\n\nTo znanje temelji na {len(relevant_concepts)} povezanih konceptih v moji bazi znanja."
                
        else:
            response = self.generate_default_response(query, style)
            
        return response
        
    def generate_default_response(self, query: str, style: Dict[str, str]) -> str:
        """Generiraj privzeti odgovor"""
        if style['formality'] == 'formal':
            return f"Oprostite, trenutno nimam dovolj informacij o tem, kar sprašujete. Lahko poskusite preformulirati vprašanje ali pa se bom poskusil naučiti več o tej temi."
        else:
            return f"Hmm, o tem še ne vem dovolj. Lahko poskusiš drugače vprašati ali pa se bom poskusil naučiti več o tem."
            
    async def start_autonomous_learning(self):
        """Začni avtonomno učenje v ozadju"""
        if self.is_learning:
            return
            
        self.is_learning = True
        self.learning_task = asyncio.create_task(self._learning_loop())
        logger.info("Started autonomous learning")
        
    async def stop_autonomous_learning(self):
        """Ustavi avtonomno učenje"""
        self.is_learning = False
        if self.learning_task:
            self.learning_task.cancel()
            try:
                await self.learning_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped autonomous learning")
        
    async def _learning_loop(self):
        """Glavna zanka za avtonomno učenje"""
        while self.is_learning:
            try:
                # Identificiraj knowledge gaps
                gaps = self.identify_knowledge_gaps()
                
                if gaps:
                    # Poišči vire za učenje
                    await self.learn_about_topics(gaps[:3])  # Omeji na 3 teme
                    
                # Shrani world model
                self.world_model.save_world_model()
                
                # Počakaj pred naslednjim ciklom
                await asyncio.sleep(3600)  # Učenje vsako uro
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in learning loop: {e}")
                await asyncio.sleep(300)  # Počakaj 5 minut ob napaki
                
    def identify_knowledge_gaps(self) -> List[str]:
        """Identificiraj pomanjkljivosti v znanju"""
        gaps = []
        
        # Analiziraj nedavne poizvedbe uporabnikov
        for user_model in self.user_models.values():
            for interaction in user_model.interaction_history[-10:]:  # Zadnjih 10 interakcij
                query_words = interaction.query.lower().split()
                for word in query_words:
                    if len(word) > 3 and word not in self.world_model.concepts:
                        gaps.append(word)
                        
        return list(set(gaps))[:5]  # Vrni do 5 gaps
        
    async def learn_about_topics(self, topics: List[str]):
        """Učenje o določenih temah"""
        async with self.web_learner as learner:
            for topic in topics:
                # Preprosto iskanje (v resnici bi uporabili search API)
                search_urls = [
                    f"https://sl.wikipedia.org/wiki/{topic}",
                    f"https://en.wikipedia.org/wiki/{topic}"
                ]
                
                for url in search_urls:
                    success = await learner.learn_from_url(url)
                    if success:
                        logger.info(f"Learned about {topic} from {url}")
                        break
                        
                # Počakaj med poizvedbami
                await asyncio.sleep(1)
                
    def get_statistics(self) -> Dict[str, Any]:
        """Pridobi statistike o jedru"""
        return {
            'concepts': len(self.world_model.concepts),
            'relations': len(self.world_model.relations),
            'users': len(self.user_models),
            'total_interactions': sum(len(um.interaction_history) for um in self.user_models.values()),
            'is_learning': self.is_learning,
            'ai_models_available': ADVANCED_AI_AVAILABLE
        }

# Primer uporabe
async def main():
    """Primer uporabe avtonomnega jedra"""
    core = AutonomousCore(Path("data/autonomous"))
    
    # Dodaj nekaj osnovnega znanja
    core.world_model.add_concept("Python", "programming_language", {"description": "Programski jezik"})
    core.world_model.add_concept("AI", "technology", {"description": "Umetna inteligenca"})
    core.world_model.add_relation("Python", "se_uporablja_za", "AI", confidence=0.9)
    
    # Začni avtonomno učenje
    await core.start_autonomous_learning()
    
    # Simuliraj nekaj poizvedb
    response1 = await core.process_query("Kaj je Python?", "user1")
    print(f"Odgovor 1: {response1}")
    
    response2 = await core.process_query("Povej mi o umetni inteligenci", "user2")
    print(f"Odgovor 2: {response2}")
    
    # Prikaži statistike
    stats = core.get_statistics()
    print(f"Statistike: {stats}")
    
    # Ustavi učenje
    await core.stop_autonomous_learning()

if __name__ == "__main__":
    asyncio.run(main())