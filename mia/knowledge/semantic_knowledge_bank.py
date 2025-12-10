#!/usr/bin/env python3
"""
Semantic Knowledge Bank for MIA
===============================

Implementacija semantične in deterministične baze znanja z logičnim sklepanjem.
Kombinira simbolično AI (ontologije, pravila) z nevronskim AI (embeddings, LLM).
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import networkx as nx
from collections import defaultdict
import re

# Semantic web imports (optional)
try:
    import rdflib
    from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal, URIRef
    from rdflib.plugins.sparql import prepareQuery
    SEMANTIC_WEB_AVAILABLE = True
except ImportError:
    SEMANTIC_WEB_AVAILABLE = False

# AI/ML imports
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class SemanticConcept:
    """Semantični koncept z ontološkimi lastnostmi"""
    uri: str
    label: str
    concept_type: str
    domain: str
    properties: Dict[str, Any]
    relations: List[Dict[str, str]]
    confidence: float
    created_at: float
    updated_at: float

@dataclass
class LogicalRule:
    """Logično pravilo za deterministično sklepanje"""
    rule_id: str
    condition: str
    conclusion: str
    domain: str
    confidence: float
    explanation: str
    created_at: float

@dataclass
class SemanticQuery:
    """Semantična poizvedba"""
    query_text: str
    semantic_structure: Dict[str, Any]
    entities: List[str]
    relations: List[str]
    intent: str
    domain: Optional[str]

class OntologyManager:
    """Upravljanje ontologij in konceptnih hierarhij"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.ontologies: Dict[str, Dict] = {}
        self.concept_hierarchy = nx.DiGraph()
        self.load_ontologies()
        
    def add_domain_ontology(self, domain: str, ontology_data: Dict[str, Any]):
        """Dodaj ontologijo za specifično domeno"""
        self.ontologies[domain] = ontology_data
        
        # Build concept hierarchy
        for concept, properties in ontology_data.items():
            self.concept_hierarchy.add_node(concept, domain=domain, **properties)
            
            # Add hierarchical relations
            if 'parent' in properties:
                self.concept_hierarchy.add_edge(properties['parent'], concept, relation='subclass')
            if 'children' in properties:
                for child in properties['children']:
                    self.concept_hierarchy.add_edge(concept, child, relation='subclass')
                    
        logger.info(f"Added ontology for domain: {domain} with {len(ontology_data)} concepts")
        
    def get_concept_hierarchy(self, concept: str) -> Dict[str, List[str]]:
        """Pridobi hierarhijo koncepta"""
        if concept not in self.concept_hierarchy:
            return {'parents': [], 'children': [], 'siblings': []}
            
        parents = list(self.concept_hierarchy.predecessors(concept))
        children = list(self.concept_hierarchy.successors(concept))
        
        # Find siblings (concepts with same parent)
        siblings = []
        for parent in parents:
            siblings.extend([
                child for child in self.concept_hierarchy.successors(parent)
                if child != concept
            ])
            
        return {
            'parents': parents,
            'children': children,
            'siblings': list(set(siblings))
        }
        
    def classify_concept(self, concept: str, context: str = None) -> str:
        """Klasificiraj koncept v ontološko kategorijo"""
        if concept in self.concept_hierarchy:
            node_data = self.concept_hierarchy.nodes[concept]
            return node_data.get('type', 'Entity')
            
        # Simple heuristic classification
        if any(word in concept.lower() for word in ['disease', 'illness', 'syndrome']):
            return 'MedicalCondition'
        elif any(word in concept.lower() for word in ['drug', 'medication', 'medicine']):
            return 'Medication'
        elif any(word in concept.lower() for word in ['law', 'regulation', 'statute']):
            return 'LegalConcept'
        else:
            return 'Entity'
            
    def load_ontologies(self):
        """Naloži obstoječe ontologije"""
        ontology_file = self.data_dir / 'ontologies.json'
        if ontology_file.exists():
            try:
                with open(ontology_file, 'r', encoding='utf-8') as f:
                    self.ontologies = json.load(f)
                logger.info(f"Loaded {len(self.ontologies)} ontologies")
            except Exception as e:
                logger.error(f"Error loading ontologies: {e}")

class LogicalRuleEngine:
    """Engine za deterministično logično sklepanje"""
    
    def __init__(self):
        self.rules: List[LogicalRule] = []
        self.facts: Set[str] = set()
        
    def add_rule(self, condition: str, conclusion: str, domain: str, confidence: float = 1.0, explanation: str = ""):
        """Dodaj logično pravilo"""
        rule = LogicalRule(
            rule_id=f"rule_{len(self.rules)}",
            condition=condition,
            conclusion=conclusion,
            domain=domain,
            confidence=confidence,
            explanation=explanation,
            created_at=time.time()
        )
        self.rules.append(rule)
        logger.debug(f"Added rule: {condition} -> {conclusion}")
        
    def add_domain_rules(self, domain: str):
        """Dodaj pravila za specifično domeno"""
        if domain == "medicine":
            self._add_medical_rules()
        elif domain == "law":
            self._add_legal_rules()
        elif domain == "science":
            self._add_scientific_rules()
        elif domain == "general":
            self._add_general_rules()
            
    def _add_medical_rules(self):
        """Medicinska pravila"""
        medical_rules = [
            ("symptom(fever) AND symptom(cough)", "possible_condition(flu)", "Gripa ima značilne simptome"),
            ("age > 65 AND medication(aspirin)", "bleeding_risk(increased)", "Aspirin povečuje tveganje pri starejših"),
            ("condition(diabetes) AND age > 50", "risk_category(high)", "Diabetes pri starejših je visoko tveganje"),
            ("medication(warfarin) AND medication(aspirin)", "interaction(dangerous)", "Nevarna kombinacija antikoagulantov"),
            ("symptom(chest_pain) AND age > 40", "emergency_assessment(required)", "Bolečina v prsih zahteva nujno obravnavo")
        ]
        
        for condition, conclusion, explanation in medical_rules:
            self.add_rule(condition, conclusion, "medicine", 0.9, explanation)
            
    def _add_legal_rules(self):
        """Pravna pravila"""
        legal_rules = [
            ("contract_element(offer) AND contract_element(acceptance) AND contract_element(consideration)", 
             "contract(valid)", "Veljavna pogodba potrebuje ponudbo, sprejem in nadomestilo"),
            ("age < 18", "legal_capacity(limited)", "Mladoletniki imajo omejeno poslovno sposobnost"),
            ("document(signed) AND witness(present)", "document(legally_binding)", "Podpisan dokument z pričo je pravno zavezujoč"),
            ("crime(committed) AND evidence(sufficient)", "prosecution(possible)", "Zadostni dokazi omogočajo pregon")
        ]
        
        for condition, conclusion, explanation in legal_rules:
            self.add_rule(condition, conclusion, "law", 0.95, explanation)
            
    def _add_scientific_rules(self):
        """Znanstvena pravila"""
        scientific_rules = [
            ("temperature < 0", "water_state(ice)", "Voda pod 0°C je led"),
            ("pressure_increase AND volume_constant", "temperature_increase", "Gay-Lussacov zakon"),
            ("mass AND acceleration", "force", "Newtonov drugi zakon: F = ma"),
            ("acid AND base", "neutralization_reaction", "Kislina in baza se nevtralizirata")
        ]
        
        for condition, conclusion, explanation in scientific_rules:
            self.add_rule(condition, conclusion, "science", 1.0, explanation)
            
    def _add_general_rules(self):
        """Splošna pravila"""
        general_rules = [
            ("animal(X) AND mammal(X)", "warm_blooded(X)", "Sesalci so toplokrvni"),
            ("bird(X)", "can_fly(X)", "Ptice lahko letijo (z izjemami)"),
            ("metal(X) AND heat(applied)", "expansion(X)", "Kovine se pri segrevanju raztezajo"),
            ("plant(X) AND sunlight(present)", "photosynthesis(X)", "Rastline izvajajo fotosintezo")
        ]
        
        for condition, conclusion, explanation in general_rules:
            self.add_rule(condition, conclusion, "general", 0.8, explanation)
    
    def forward_chaining(self, initial_facts: Set[str], max_iterations: int = 10) -> Dict[str, Any]:
        """Forward chaining za deterministično sklepanje"""
        facts = initial_facts.copy()
        new_conclusions = []
        reasoning_steps = []
        
        for iteration in range(max_iterations):
            iteration_conclusions = []
            
            for rule in self.rules:
                if self._rule_applies(rule.condition, facts):
                    conclusion = self._extract_conclusion(rule.conclusion, facts)
                    if conclusion and conclusion not in facts:
                        facts.add(conclusion)
                        iteration_conclusions.append(conclusion)
                        new_conclusions.append(conclusion)
                        
                        reasoning_steps.append({
                            'step': len(reasoning_steps) + 1,
                            'rule_id': rule.rule_id,
                            'condition': rule.condition,
                            'conclusion': conclusion,
                            'explanation': rule.explanation,
                            'confidence': rule.confidence
                        })
                        
            if not iteration_conclusions:
                break  # No new conclusions
                
        return {
            'final_facts': facts,
            'new_conclusions': new_conclusions,
            'reasoning_steps': reasoning_steps,
            'iterations': iteration + 1,
            'deterministic': True
        }
        
    def _rule_applies(self, condition: str, facts: Set[str]) -> bool:
        """Preveri, ali se pravilo lahko uporabi"""
        # Simple pattern matching for conditions
        # In real implementation, this would be more sophisticated
        
        if " AND " in condition:
            conditions = condition.split(" AND ")
            return all(self._check_condition(cond.strip(), facts) for cond in conditions)
        elif " OR " in condition:
            conditions = condition.split(" OR ")
            return any(self._check_condition(cond.strip(), facts) for cond in conditions)
        else:
            return self._check_condition(condition, facts)
            
    def _check_condition(self, condition: str, facts: Set[str]) -> bool:
        """Preveri posamezno kondico"""
        # Handle comparison operators
        if ">" in condition or "<" in condition or "=" in condition:
            return self._evaluate_comparison(condition, facts)
            
        # Handle function calls like symptom(fever)
        if "(" in condition and ")" in condition:
            return condition in facts
            
        # Simple fact matching
        return condition in facts
        
    def _evaluate_comparison(self, condition: str, facts: Set[str]) -> bool:
        """Evalviraj primerjalne operatorje"""
        # Simplified evaluation - in real implementation would be more robust
        for fact in facts:
            if "age" in condition and "age" in fact:
                try:
                    # Extract age value from facts
                    age_match = re.search(r'age\((\d+)\)', fact)
                    if age_match:
                        age = int(age_match.group(1))
                        if "> 65" in condition and age > 65:
                            return True
                        elif "< 18" in condition and age < 18:
                            return True
                        elif "> 40" in condition and age > 40:
                            return True
                        elif "> 50" in condition and age > 50:
                            return True
                except:
                    pass
        return False
        
    def _extract_conclusion(self, conclusion_template: str, facts: Set[str]) -> Optional[str]:
        """Ekstraktiraj zaključek iz template-a"""
        # Simple implementation - return conclusion as is
        return conclusion_template

class SemanticKnowledgeBank:
    """Glavna semantična baza znanja"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        
        # Core components
        self.ontology_manager = OntologyManager(data_dir)
        self.rule_engine = LogicalRuleEngine()
        self.concepts: Dict[str, SemanticConcept] = {}
        
        # Semantic search (if available)
        self.embedding_model = None
        self.concept_embeddings: Dict[str, Any] = {}
        
        if AI_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Initialized semantic embedding model")
            except Exception as e:
                logger.warning(f"Could not initialize embedding model: {e}")
                
        # RDF graph (if available)
        self.rdf_graph = None
        if SEMANTIC_WEB_AVAILABLE:
            self.rdf_graph = Graph()
            self._setup_namespaces()
            
        # Load existing knowledge
        self.load_knowledge_base()
        
    def _setup_namespaces(self):
        """Setup RDF namespaces"""
        if not self.rdf_graph:
            return
            
        self.MIA = Namespace("http://mia.ai/ontology/")
        self.rdf_graph.bind("mia", self.MIA)
        self.rdf_graph.bind("rdf", RDF)
        self.rdf_graph.bind("rdfs", RDFS)
        self.rdf_graph.bind("owl", OWL)
        
    def add_structured_knowledge(self, domain: str, knowledge_dict: Dict[str, Any]):
        """Dodaj strukturirano znanje za domeno"""
        for concept_name, properties in knowledge_dict.items():
            concept = SemanticConcept(
                uri=f"mia:{domain}:{concept_name}",
                label=concept_name,
                concept_type=properties.get('type', 'Entity'),
                domain=domain,
                properties=properties,
                relations=properties.get('relations', []),
                confidence=properties.get('confidence', 0.8),
                created_at=time.time(),
                updated_at=time.time()
            )
            
            self.concepts[concept_name] = concept
            
            # Add to ontology
            self.ontology_manager.add_domain_ontology(domain, {concept_name: properties})
            
            # Add to RDF graph
            if self.rdf_graph:
                self._add_to_rdf(concept)
                
            # Generate embeddings
            if self.embedding_model:
                self._generate_embeddings(concept)
                
        # Add domain rules
        self.rule_engine.add_domain_rules(domain)
        
        logger.info(f"Added {len(knowledge_dict)} concepts for domain: {domain}")
        
    def _add_to_rdf(self, concept: SemanticConcept):
        """Dodaj koncept v RDF graf"""
        if not self.rdf_graph:
            return
            
        concept_uri = URIRef(concept.uri)
        
        # Add basic triples
        self.rdf_graph.add((concept_uri, RDF.type, URIRef(f"mia:{concept.concept_type}")))
        self.rdf_graph.add((concept_uri, RDFS.label, Literal(concept.label)))
        
        # Add properties
        for prop, value in concept.properties.items():
            if prop not in ['type', 'relations', 'confidence']:
                prop_uri = URIRef(f"mia:{prop}")
                if isinstance(value, str):
                    self.rdf_graph.add((concept_uri, prop_uri, Literal(value)))
                    
        # Add relations
        for relation in concept.relations:
            if 'predicate' in relation and 'object' in relation:
                pred_uri = URIRef(f"mia:{relation['predicate']}")
                obj_uri = URIRef(f"mia:{concept.domain}:{relation['object']}")
                self.rdf_graph.add((concept_uri, pred_uri, obj_uri))
                
    def _generate_embeddings(self, concept: SemanticConcept):
        """Generiraj embeddings za koncept"""
        if not self.embedding_model:
            return
            
        # Create text representation
        text_repr = f"{concept.label} {concept.concept_type}"
        if 'description' in concept.properties:
            text_repr += f" {concept.properties['description']}"
            
        # Generate embedding
        try:
            embedding = self.embedding_model.encode(text_repr)
            self.concept_embeddings[concept.label] = embedding
        except Exception as e:
            logger.warning(f"Could not generate embedding for {concept.label}: {e}")
            
    def semantic_query(self, query_text: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """Semantična poizvedba"""
        # Parse query
        semantic_query = self._parse_natural_language_query(query_text)
        
        # Direct concept lookup
        direct_matches = self._find_direct_matches(semantic_query)
        
        # Semantic similarity search
        similar_concepts = self._find_similar_concepts(query_text, threshold=0.7)
        
        # Logical inference
        inference_results = None
        if direct_matches:
            facts = set()
            for match in direct_matches:
                facts.add(f"{match['concept']}({match['value']})")
                
            inference_results = self.rule_engine.forward_chaining(facts)
            
        # SPARQL query (if RDF available)
        sparql_results = []
        if self.rdf_graph and SEMANTIC_WEB_AVAILABLE:
            sparql_results = self._execute_sparql_query(semantic_query)
            
        return {
            'query': semantic_query,
            'direct_matches': direct_matches,
            'similar_concepts': similar_concepts,
            'inference_results': inference_results,
            'sparql_results': sparql_results,
            'confidence': self._calculate_query_confidence(direct_matches, similar_concepts, inference_results)
        }
        
    def _parse_natural_language_query(self, query_text: str) -> SemanticQuery:
        """Parse natural language query to semantic structure"""
        # Simple parsing - in real implementation would use NLP
        entities = []
        relations = []
        intent = "information_seeking"
        domain = None
        
        # Extract entities (simple keyword matching)
        for concept_name in self.concepts:
            if concept_name.lower() in query_text.lower():
                entities.append(concept_name)
                if not domain:
                    domain = self.concepts[concept_name].domain
                    
        # Determine intent
        if any(word in query_text.lower() for word in ['what', 'kaj', 'who', 'kdo']):
            intent = "definition"
        elif any(word in query_text.lower() for word in ['how', 'kako']):
            intent = "procedure"
        elif any(word in query_text.lower() for word in ['why', 'zakaj']):
            intent = "explanation"
        elif any(word in query_text.lower() for word in ['is', 'je', 'ali']):
            intent = "verification"
            
        return SemanticQuery(
            query_text=query_text,
            semantic_structure={'entities': entities, 'relations': relations},
            entities=entities,
            relations=relations,
            intent=intent,
            domain=domain
        )
        
    def _find_direct_matches(self, semantic_query: SemanticQuery) -> List[Dict[str, Any]]:
        """Poišči direktne ujemanja"""
        matches = []
        
        for entity in semantic_query.entities:
            if entity in self.concepts:
                concept = self.concepts[entity]
                matches.append({
                    'concept': entity,
                    'type': concept.concept_type,
                    'domain': concept.domain,
                    'properties': concept.properties,
                    'confidence': concept.confidence,
                    'value': entity
                })
                
        return matches
        
    def _find_similar_concepts(self, query_text: str, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Poišči semantično podobne koncepte"""
        if not self.embedding_model or not self.concept_embeddings:
            return []
            
        try:
            import numpy as np
            query_embedding = self.embedding_model.encode(query_text)
            similar_concepts = []
            
            for concept_name, concept_embedding in self.concept_embeddings.items():
                similarity = np.dot(query_embedding, concept_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(concept_embedding)
                )
                
                if similarity >= threshold:
                    concept = self.concepts[concept_name]
                    similar_concepts.append({
                        'concept': concept_name,
                        'similarity': float(similarity),
                        'type': concept.concept_type,
                        'domain': concept.domain,
                        'properties': concept.properties
                    })
                    
            # Sort by similarity
            similar_concepts.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_concepts[:10]  # Top 10
            
        except Exception as e:
            logger.warning(f"Error in similarity search: {e}")
            return []
            
    def _execute_sparql_query(self, semantic_query: SemanticQuery) -> List[Dict[str, Any]]:
        """Izvedi SPARQL poizvedbo"""
        if not self.rdf_graph:
            return []
            
        try:
            # Simple SPARQL query generation
            sparql_query = f"""
            SELECT ?subject ?predicate ?object
            WHERE {{
                ?subject ?predicate ?object .
                FILTER(CONTAINS(LCASE(STR(?subject)), "{semantic_query.entities[0].lower()}"))
            }}
            LIMIT 10
            """ if semantic_query.entities else """
            SELECT ?subject ?predicate ?object
            WHERE {
                ?subject ?predicate ?object .
            }
            LIMIT 10
            """
            
            results = self.rdf_graph.query(sparql_query)
            sparql_results = []
            
            for row in results:
                sparql_results.append({
                    'subject': str(row.subject),
                    'predicate': str(row.predicate),
                    'object': str(row.object)
                })
                
            return sparql_results
            
        except Exception as e:
            logger.warning(f"Error in SPARQL query: {e}")
            return []
            
    def _calculate_query_confidence(self, direct_matches, similar_concepts, inference_results) -> float:
        """Izračunaj zaupanje v rezultate poizvedbe"""
        confidence = 0.0
        
        if direct_matches:
            confidence += 0.4 * (len(direct_matches) / max(len(direct_matches), 5))
            
        if similar_concepts:
            avg_similarity = sum(c['similarity'] for c in similar_concepts) / len(similar_concepts)
            confidence += 0.3 * avg_similarity
            
        if inference_results and inference_results.get('new_conclusions'):
            confidence += 0.3 * min(len(inference_results['new_conclusions']) / 3, 1.0)
            
        return min(confidence, 1.0)
        
    def add_medical_knowledge(self):
        """Dodaj medicinsko znanje"""
        medical_knowledge = {
            'aspirin': {
                'type': 'Medication',
                'class': 'NSAID',
                'mechanism': 'COX inhibition',
                'indications': ['pain', 'fever', 'inflammation', 'cardiovascular_protection'],
                'contraindications': ['bleeding_disorders', 'peptic_ulcer', 'severe_liver_disease'],
                'side_effects': ['gastric_irritation', 'bleeding', 'tinnitus'],
                'interactions': ['warfarin', 'heparin', 'methotrexate'],
                'dosage': '75-325mg daily for cardiovascular protection',
                'description': 'Acetylsalicylic acid, commonly used analgesic and antiplatelet agent'
            },
            'diabetes': {
                'type': 'MedicalCondition',
                'class': 'Metabolic disorder',
                'pathophysiology': 'Insulin deficiency or resistance',
                'symptoms': ['polyuria', 'polydipsia', 'weight_loss', 'fatigue'],
                'complications': ['diabetic_retinopathy', 'nephropathy', 'neuropathy', 'cardiovascular_disease'],
                'treatment': ['insulin', 'metformin', 'lifestyle_modification'],
                'monitoring': ['blood_glucose', 'HbA1c', 'lipid_profile'],
                'description': 'Chronic metabolic disorder characterized by hyperglycemia'
            },
            'hypertension': {
                'type': 'MedicalCondition',
                'class': 'Cardiovascular disorder',
                'definition': 'Blood pressure >140/90 mmHg',
                'risk_factors': ['age', 'obesity', 'smoking', 'diabetes', 'family_history'],
                'complications': ['stroke', 'myocardial_infarction', 'kidney_disease'],
                'treatment': ['ACE_inhibitors', 'diuretics', 'lifestyle_modification'],
                'description': 'Elevated blood pressure, major cardiovascular risk factor'
            }
        }
        
        self.add_structured_knowledge('medicine', medical_knowledge)
        
    def save_knowledge_base(self):
        """Shrani bazo znanja"""
        kb_data = {
            'concepts': {name: asdict(concept) for name, concept in self.concepts.items()},
            'rules': [asdict(rule) for rule in self.rule_engine.rules],
            'ontologies': self.ontology_manager.ontologies
        }
        
        kb_file = self.data_dir / 'semantic_knowledge_base.json'
        with open(kb_file, 'w', encoding='utf-8') as f:
            json.dump(kb_data, f, indent=2, ensure_ascii=False)
            
        # Save RDF graph
        if self.rdf_graph:
            rdf_file = self.data_dir / 'knowledge_graph.ttl'
            self.rdf_graph.serialize(destination=str(rdf_file), format='turtle')
            
        logger.info(f"Saved knowledge base with {len(self.concepts)} concepts")
        
    def load_knowledge_base(self):
        """Naloži bazo znanja"""
        kb_file = self.data_dir / 'semantic_knowledge_base.json'
        if not kb_file.exists():
            # Initialize with basic medical knowledge
            self.add_medical_knowledge()
            return
            
        try:
            with open(kb_file, 'r', encoding='utf-8') as f:
                kb_data = json.load(f)
                
            # Load concepts
            for name, concept_data in kb_data.get('concepts', {}).items():
                concept = SemanticConcept(**concept_data)
                self.concepts[name] = concept
                
                # Generate embeddings
                if self.embedding_model:
                    self._generate_embeddings(concept)
                    
            # Load rules
            for rule_data in kb_data.get('rules', []):
                rule = LogicalRule(**rule_data)
                self.rule_engine.rules.append(rule)
                
            # Load ontologies
            for domain, ontology in kb_data.get('ontologies', {}).items():
                self.ontology_manager.ontologies[domain] = ontology
                
            # Load RDF graph
            rdf_file = self.data_dir / 'knowledge_graph.ttl'
            if rdf_file.exists() and self.rdf_graph:
                self.rdf_graph.parse(str(rdf_file), format='turtle')
                
            logger.info(f"Loaded knowledge base with {len(self.concepts)} concepts and {len(self.rule_engine.rules)} rules")
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            # Fallback to basic medical knowledge
            self.add_medical_knowledge()

# Example usage
async def main():
    """Primer uporabe semantične baze znanja"""
    kb = SemanticKnowledgeBank(Path("data/semantic_kb"))
    
    # Add some knowledge
    kb.add_medical_knowledge()
    
    # Query examples
    queries = [
        "Ali je aspirin varen za starejše?",
        "Kaj je diabetes?",
        "Kakšne so nevarnosti aspirina?",
        "Kako zdraviti visok krvni tlak?"
    ]
    
    for query in queries:
        print(f"\nPoizvedba: {query}")
        results = kb.semantic_query(query)
        
        print(f"Direktni zadetki: {len(results['direct_matches'])}")
        print(f"Podobni koncepti: {len(results['similar_concepts'])}")
        
        if results['inference_results']:
            print(f"Logični zaključki: {len(results['inference_results']['new_conclusions'])}")
            for step in results['inference_results']['reasoning_steps']:
                print(f"  - {step['explanation']}")
                
        print(f"Zaupanje: {results['confidence']:.2f}")
        
    # Save knowledge base
    kb.save_knowledge_base()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())