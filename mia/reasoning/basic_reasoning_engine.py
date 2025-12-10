#!/usr/bin/env python3
"""
Basic Reasoning Engine for MIA
==============================

Osnovno sklepanje na podlagi shranjenih dejstev z razložljivimi odgovori.
To je TEMELJ za odgovarjanje na uporabniška vprašanja.
"""

import re
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ReasoningResult:
    """Rezultat sklepanja"""
    answer: str
    confidence: float
    sources: List[str]
    reasoning_steps: List[str]
    facts_used: List[Dict[str, Any]]
    learning_opportunity: bool

class BasicReasoningEngine:
    """
    Osnovno sklepanje na podlagi shranjenih dejstev.
    
    Ključne funkcionalnosti:
    - Odgovarja na vprašanja iz knowledge store
    - Kombinira informacije iz različnih virov
    - Generira razložljive odgovore
    - Prepozna, kdaj ne ve odgovora (learning opportunity)
    """
    
    def __init__(self, knowledge_store):
        self.knowledge = knowledge_store
        
        # Vzorci za prepoznavanje tipov vprašanj
        self.question_patterns = {
            'what_is': [
                r'kaj\s+je\s+(.+)',
                r'what\s+is\s+(.+)',
                r'define\s+(.+)',
                r'definiraj\s+(.+)'
            ],
            'how_to': [
                r'kako\s+(.+)',
                r'how\s+to\s+(.+)',
                r'how\s+do\s+(.+)'
            ],
            'why': [
                r'zakaj\s+(.+)',
                r'why\s+(.+)',
                r'zaradi\s+česa\s+(.+)'
            ],
            'where': [
                r'kje\s+(.+)',
                r'where\s+(.+)'
            ],
            'when': [
                r'kdaj\s+(.+)',
                r'when\s+(.+)'
            ],
            'who': [
                r'kdo\s+(.+)',
                r'who\s+(.+)'
            ],
            'yes_no': [
                r'ali\s+(.+)',
                r'is\s+(.+)',
                r'are\s+(.+)',
                r'can\s+(.+)',
                r'does\s+(.+)'
            ]
        }
        
        # Stop words za čiščenje
        self.stop_words = {
            'slovenščina': {'je', 'so', 'in', 'ali', 'ter', 'kot', 'za', 'na', 'v', 'z', 'pri', 'od', 'do', 'po', 'iz', 'k', 'o'},
            'angleščina': {'is', 'are', 'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        }
        
        # Statistike sklepanja
        self.reasoning_stats = {
            'total_questions': 0,
            'successful_answers': 0,
            'learning_opportunities': 0,
            'average_confidence': 0.0
        }
        
        logger.info("BasicReasoningEngine initialized")
        
    def answer_question(self, question: str, user_id: str = "default") -> ReasoningResult:
        """
        Glavna funkcija za odgovarjanje na vprašanja.
        
        Args:
            question: Uporabniško vprašanje
            user_id: ID uporabnika
            
        Returns:
            ReasoningResult z odgovorom in metadata
        """
        try:
            self.reasoning_stats['total_questions'] += 1
            
            # 1. Analiziraj tip vprašanja
            question_type, extracted_topic = self._analyze_question_type(question)
            
            # 2. Ekstraktiraj ključne besede
            keywords = self._extract_keywords(question)
            
            # 3. Poišči relevantna dejstva
            relevant_facts = self._find_relevant_facts(keywords, extracted_topic)
            
            # 4. Generiraj odgovor
            if relevant_facts:
                result = self._generate_answer_from_facts(question, question_type, relevant_facts)
                if result.confidence > 0.3:
                    self.reasoning_stats['successful_answers'] += 1
            else:
                result = self._generate_learning_response(question, user_id, keywords)
                self.reasoning_stats['learning_opportunities'] += 1
                
            # 5. Posodobi statistike
            self._update_confidence_average(result.confidence)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in answer_question: {e}")
            return ReasoningResult(
                answer=f"Oprostite, prišlo je do napake pri procesiranju vprašanja: {e}",
                confidence=0.0,
                sources=[],
                reasoning_steps=[f"Error: {e}"],
                facts_used=[],
                learning_opportunity=True
            )
            
    def _analyze_question_type(self, question: str) -> Tuple[str, Optional[str]]:
        """
        Analiziraj tip vprašanja in ekstraktiraj glavno temo.
        
        Args:
            question: Vprašanje za analizo
            
        Returns:
            Tuple (question_type, extracted_topic)
        """
        question_lower = question.lower().strip()
        
        for q_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, question_lower)
                if match:
                    topic = match.group(1).strip() if match.groups() else None
                    return q_type, topic
                    
        return 'general', None
        
    def _extract_keywords(self, question: str) -> List[str]:
        """
        Ekstraktiraj ključne besede iz vprašanja.
        
        Args:
            question: Vprašanje za analizo
            
        Returns:
            Seznam ključnih besed
        """
        # Odstrani ločila in pretvori v male črke
        cleaned = re.sub(r'[^\w\s]', ' ', question.lower())
        words = cleaned.split()
        
        # Odstrani stop words
        all_stop_words = self.stop_words['slovenščina'] | self.stop_words['angleščina']
        keywords = [word for word in words if word not in all_stop_words and len(word) > 2]
        
        # Odstrani vprašalne besede
        question_words = {'kaj', 'kdo', 'kako', 'zakaj', 'kdaj', 'kje', 'ali', 'what', 'who', 'how', 'why', 'when', 'where', 'is', 'are', 'can', 'does'}
        keywords = [word for word in keywords if word not in question_words]
        
        return keywords
        
    def _find_relevant_facts(self, keywords: List[str], topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Poišči relevantna dejstva na podlagi ključnih besed.
        
        Args:
            keywords: Seznam ključnih besed
            topic: Glavna tema (opcijsko)
            
        Returns:
            Seznam relevantnih dejstev
        """
        relevant_facts = []
        
        try:
            # Najprej poišči po glavni temi, če obstaja
            if topic:
                topic_facts = self.knowledge.search_entities(topic, limit=5)
                relevant_facts.extend(topic_facts)
                
            # Nato poišči po ključnih besedah
            for keyword in keywords[:5]:  # Omeji na 5 ključnih besed
                keyword_facts = self.knowledge.search_entities(keyword, limit=3)
                relevant_facts.extend(keyword_facts)
                
            # Odstrani duplikate
            seen_entities = set()
            unique_facts = []
            for fact in relevant_facts:
                entity = fact.get('entity', '')
                if entity not in seen_entities:
                    seen_entities.add(entity)
                    unique_facts.append(fact)
                    
            return unique_facts[:10]  # Omeji na 10 najrelevantnejših
            
        except Exception as e:
            logger.error(f"Error finding relevant facts: {e}")
            return []
            
    def _generate_answer_from_facts(self, question: str, question_type: str, facts: List[Dict[str, Any]]) -> ReasoningResult:
        """
        Generiraj odgovor iz najdenih dejstev.
        
        Args:
            question: Originalno vprašanje
            question_type: Tip vprašanja
            facts: Seznam relevantnih dejstev
            
        Returns:
            ReasoningResult z odgovorom
        """
        if not facts:
            return self._generate_learning_response(question, "default", [])
            
        answer_parts = []
        sources = []
        reasoning_steps = []
        facts_used = []
        
        try:
            # Analiziraj dejstva in generiraj odgovor
            for i, fact in enumerate(facts[:3]):  # Uporabi top 3 dejstva
                entity = fact.get('entity', '')
                properties = fact.get('properties', {})
                relevance = fact.get('relevance', 0.5)
                
                if not entity or not properties:
                    continue
                    
                # Dodaj dejstvo v uporabljene
                facts_used.append({
                    'entity': entity,
                    'properties': properties,
                    'relevance': relevance
                })
                
                # Generiraj del odgovora na podlagi tipa vprašanja
                if question_type == 'what_is':
                    answer_part = self._generate_definition_answer(entity, properties)
                elif question_type == 'how_to':
                    answer_part = self._generate_procedure_answer(entity, properties)
                elif question_type == 'why':
                    answer_part = self._generate_explanation_answer(entity, properties)
                elif question_type == 'yes_no':
                    answer_part = self._generate_yes_no_answer(question, entity, properties)
                else:
                    answer_part = self._generate_general_answer(entity, properties)
                    
                if answer_part:
                    answer_parts.append(answer_part)
                    sources.append(f"{entity}")
                    reasoning_steps.append(f"Korak {i+1}: Analiziral informacije o '{entity}'")
                    
            # Kombiniraj dele odgovora
            if answer_parts:
                if len(answer_parts) == 1:
                    final_answer = answer_parts[0]
                else:
                    final_answer = f"{answer_parts[0]}. Dodatno: {' '.join(answer_parts[1:])}"
                    
                confidence = self._calculate_confidence(facts_used, len(answer_parts))
                
                return ReasoningResult(
                    answer=final_answer,
                    confidence=confidence,
                    sources=sources,
                    reasoning_steps=reasoning_steps,
                    facts_used=facts_used,
                    learning_opportunity=False
                )
            else:
                return self._generate_learning_response(question, "default", [])
                
        except Exception as e:
            logger.error(f"Error generating answer from facts: {e}")
            return self._generate_learning_response(question, "default", [])
            
    def _generate_definition_answer(self, entity: str, properties: Dict[str, Any]) -> Optional[str]:
        """Generiraj definicijski odgovor"""
        if 'description' in properties:
            return f"{entity.title()} je {properties['description']}"
        elif 'type' in properties:
            return f"{entity.title()} je vrsta {properties['type']}"
        elif 'use' in properties:
            return f"{entity.title()} se uporablja za {properties['use']}"
        return None
        
    def _generate_procedure_answer(self, entity: str, properties: Dict[str, Any]) -> Optional[str]:
        """Generiraj proceduralni odgovor"""
        if 'use' in properties:
            return f"Za {entity} se uporablja {properties['use']}"
        elif 'works' in properties:
            return f"{entity.title()} deluje {properties['works']}"
        elif 'procedure' in properties:
            return f"Postopek za {entity}: {properties['procedure']}"
        return None
        
    def _generate_explanation_answer(self, entity: str, properties: Dict[str, Any]) -> Optional[str]:
        """Generiraj razlagalni odgovor"""
        if 'causes' in properties:
            return f"{entity.title()} povzroča {properties['causes']}"
        elif 'reason' in properties:
            return f"Razlog za {entity} je {properties['reason']}"
        elif 'explanation' in properties:
            return f"{properties['explanation']}"
        return None
        
    def _generate_yes_no_answer(self, question: str, entity: str, properties: Dict[str, Any]) -> Optional[str]:
        """Generiraj da/ne odgovor"""
        # Preprosta hevristika za da/ne vprašanja
        if any(prop in properties for prop in ['description', 'type', 'use']):
            return f"Da, {entity} {self._get_property_text(properties)}"
        return None
        
    def _generate_general_answer(self, entity: str, properties: Dict[str, Any]) -> Optional[str]:
        """Generiraj splošni odgovor"""
        # Uporabi prvo dostopno lastnost
        for prop, value in properties.items():
            if prop in ['description', 'use', 'type', 'purpose']:
                return f"{entity.title()} {self._property_to_text(prop)} {value}"
        return None
        
    def _get_property_text(self, properties: Dict[str, Any]) -> str:
        """Pretvori lastnosti v berljiv tekst"""
        if 'description' in properties:
            return f"je {properties['description']}"
        elif 'use' in properties:
            return f"se uporablja za {properties['use']}"
        elif 'type' in properties:
            return f"je vrsta {properties['type']}"
        return "ima določene lastnosti"
        
    def _property_to_text(self, property_type: str) -> str:
        """Pretvori tip lastnosti v berljiv tekst"""
        mapping = {
            'description': 'je',
            'use': 'se uporablja za',
            'type': 'je vrsta',
            'causes': 'povzroča',
            'helps_with': 'pomaga pri',
            'has': 'ima',
            'contains': 'vsebuje',
            'works': 'deluje',
            'purpose': 'služi za'
        }
        return mapping.get(property_type, 'ima lastnost')
        
    def _calculate_confidence(self, facts_used: List[Dict[str, Any]], answer_parts_count: int) -> float:
        """Izračunaj zaupanje v odgovor"""
        if not facts_used:
            return 0.0
            
        # Osnovno zaupanje na podlagi števila dejstev
        base_confidence = min(0.8, 0.3 + (len(facts_used) * 0.15))
        
        # Povečaj zaupanje, če imamo več delov odgovora
        parts_bonus = min(0.15, answer_parts_count * 0.05)
        
        # Povečaj zaupanje na podlagi relevance dejstev
        avg_relevance = sum(fact.get('relevance', 0.5) for fact in facts_used) / len(facts_used)
        relevance_bonus = avg_relevance * 0.2
        
        total_confidence = base_confidence + parts_bonus + relevance_bonus
        return min(1.0, total_confidence)
        
    def _generate_learning_response(self, question: str, user_id: str, keywords: List[str]) -> ReasoningResult:
        """
        Generiraj odgovor, ko ne vemo odgovora (learning opportunity).
        
        Args:
            question: Originalno vprašanje
            user_id: ID uporabnika
            keywords: Ključne besede iz vprašanja
            
        Returns:
            ReasoningResult z learning opportunity
        """
        # Generiraj spodbuden odgovor za učenje
        if keywords:
            main_topic = keywords[0] if keywords else "tem"
            answer = f"O {main_topic} še ne vem dovolj. Lahko mi poveš več o tem? To bi mi pomagalo, da se naučim in ti boljše odgovorim naslednjič."
        else:
            answer = "O tem še ne vem dovolj. Lahko mi poveš več? Rad se učim novih stvari!"
            
        return ReasoningResult(
            answer=answer,
            confidence=0.0,
            sources=[],
            reasoning_steps=[
                "Analiziral vprašanje",
                "Poiskal relevantne informacije",
                "Ni najdenih ustreznih dejstev",
                "Identificiral priložnost za učenje"
            ],
            facts_used=[],
            learning_opportunity=True
        )
        
    def _update_confidence_average(self, new_confidence: float):
        """Posodobi povprečno zaupanje"""
        current_avg = self.reasoning_stats['average_confidence']
        total_questions = self.reasoning_stats['total_questions']
        
        if total_questions == 1:
            self.reasoning_stats['average_confidence'] = new_confidence
        else:
            self.reasoning_stats['average_confidence'] = (
                (current_avg * (total_questions - 1) + new_confidence) / total_questions
            )
            
    def get_reasoning_statistics(self) -> Dict[str, Any]:
        """Pridobi statistike sklepanja"""
        total = self.reasoning_stats['total_questions']
        return {
            **self.reasoning_stats,
            'success_rate': self.reasoning_stats['successful_answers'] / max(total, 1),
            'learning_rate': self.reasoning_stats['learning_opportunities'] / max(total, 1)
        }
        
    def reset_statistics(self):
        """Ponastavi statistike sklepanja"""
        self.reasoning_stats = {
            'total_questions': 0,
            'successful_answers': 0,
            'learning_opportunities': 0,
            'average_confidence': 0.0
        }
        logger.info("Reasoning statistics reset")

# Example usage and testing
def main():
    """Primer uporabe BasicReasoningEngine"""
    from mia.core.persistent_knowledge_store import PersistentKnowledgeStore
    
    # Initialize components
    knowledge_store = PersistentKnowledgeStore("data/test_reasoning")
    reasoning_engine = BasicReasoningEngine(knowledge_store)
    
    # Add some test knowledge
    knowledge_store.add_fact("python", "description", "programski jezik", "test", 0.9)
    knowledge_store.add_fact("python", "use", "razvoj aplikacij", "test", 0.8)
    knowledge_store.add_fact("aspirin", "description", "zdravilo", "test", 0.9)
    knowledge_store.add_fact("aspirin", "use", "lajšanje bolečin", "test", 0.8)
    
    print("=== BasicReasoningEngine Test ===")
    
    # Test questions
    test_questions = [
        "Kaj je Python?",
        "What is aspirin?",
        "Kako se uporablja Python?",
        "Ali je aspirin zdravilo?",
        "Kaj je JavaScript?",  # Unknown - learning opportunity
        "Zakaj je nebo modro?"   # Unknown - learning opportunity
    ]
    
    for i, question in enumerate(test_questions):
        print(f"\n{i+1}. Question: {question}")
        result = reasoning_engine.answer_question(question, f"user_{i}")
        
        print(f"   Answer: {result.answer}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Sources: {result.sources}")
        print(f"   Learning opportunity: {result.learning_opportunity}")
        if result.reasoning_steps:
            print(f"   Reasoning: {' → '.join(result.reasoning_steps)}")
            
    # Show statistics
    print(f"\nReasoning Statistics:")
    stats = reasoning_engine.get_reasoning_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
            
    print("\n=== Test completed ===")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()