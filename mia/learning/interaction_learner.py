#!/usr/bin/env python3
"""
Interaction Learner for MIA
===========================

Uči se iz uporabniških pogovorov z ekstrakcijon dejstev in feedback analizo.
To je NAJPOMEMBNEJŠA komponenta za avtonomno učenje MIA.
"""

import re
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ExtractedFact:
    """Ekstraktirano dejstvo iz pogovora"""
    entity: str
    property: str
    value: str
    confidence: float
    source_sentence: str

class InteractionLearner:
    """
    Uči se iz uporabniških interakcij z ekstrakcijon dejstev in analizo feedback-a.
    
    Ključne funkcionalnosti:
    - Ekstraktira dejstva iz uporabniških vnosov
    - Analizira feedback za izboljšanje odgovorov
    - Uči se o uporabniških preferencah
    - Shrani novo znanje v persistent storage
    """
    
    def __init__(self, knowledge_store):
        self.knowledge = knowledge_store
        
        # Vzorci za ekstrakcijon dejstev
        self.fact_patterns = [
            # Slovenščina
            (r"(.+?)\s+je\s+(.+)", "description", 0.8),
            (r"(.+?)\s+so\s+(.+)", "description", 0.8),
            (r"(.+?)\s+se\s+uporablja\s+za\s+(.+)", "use", 0.9),
            (r"(.+?)\s+se\s+uporablja\s+pri\s+(.+)", "use", 0.9),
            (r"(.+?)\s+povzroča\s+(.+)", "causes", 0.9),
            (r"(.+?)\s+pomaga\s+pri\s+(.+)", "helps_with", 0.8),
            (r"(.+?)\s+ima\s+(.+)", "has", 0.7),
            (r"(.+?)\s+vsebuje\s+(.+)", "contains", 0.8),
            (r"(.+?)\s+deluje\s+(.+)", "works", 0.7),
            (r"(.+?)\s+služi\s+za\s+(.+)", "purpose", 0.8),
            
            # Angleščina
            (r"(.+?)\s+is\s+(.+)", "description", 0.8),
            (r"(.+?)\s+are\s+(.+)", "description", 0.8),
            (r"(.+?)\s+is\s+used\s+for\s+(.+)", "use", 0.9),
            (r"(.+?)\s+causes\s+(.+)", "causes", 0.9),
            (r"(.+?)\s+helps\s+with\s+(.+)", "helps_with", 0.8),
            (r"(.+?)\s+has\s+(.+)", "has", 0.7),
            (r"(.+?)\s+contains\s+(.+)", "contains", 0.8),
        ]
        
        # Stop words za čiščenje
        self.stop_words = {
            'slovenščina': {'in', 'ali', 'ter', 'kot', 'za', 'na', 'v', 'z', 'pri', 'od', 'do', 'po', 'iz', 'k', 'o', 'ob', 'nad', 'pod', 'pred', 'med', 'brez', 'preko', 'zaradi', 'kljub'},
            'angleščina': {'and', 'or', 'but', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'without', 'despite'}
        }
        
        # Statistike učenja
        self.learning_stats = {
            'total_conversations': 0,
            'facts_extracted': 0,
            'feedback_processed': 0,
            'user_models_updated': 0
        }
        
        logger.info("InteractionLearner initialized")
        
    def learn_from_conversation(self, user_input: str, mia_response: str, 
                              user_feedback: Optional[str] = None, user_id: str = "default") -> Dict[str, Any]:
        """
        Glavna funkcija za učenje iz pogovora.
        
        Args:
            user_input: Uporabniški vnos
            mia_response: MIA-in odgovor
            user_feedback: Uporabniški feedback (opcijsko)
            user_id: ID uporabnika
            
        Returns:
            Dict z rezultati učenja
        """
        try:
            learning_results = {
                'facts_learned': 0,
                'feedback_processed': False,
                'user_model_updated': False,
                'errors': []
            }
            
            # 1. Ekstraktiraj dejstva iz uporabniškega vnosa
            extracted_facts = self.extract_facts_from_input(user_input)
            
            # 2. Shrani nova dejstva
            for fact in extracted_facts:
                success = self.knowledge.add_fact(
                    entity=fact.entity,
                    property=fact.property,
                    value=fact.value,
                    source=f"user_{user_id}",
                    confidence=fact.confidence,
                    user_id=user_id
                )
                
                if success:
                    learning_results['facts_learned'] += 1
                    self.learning_stats['facts_extracted'] += 1
                    
                    logger.info(f"Learned fact: {fact.entity} {fact.property} {fact.value}")
                    
            # 3. Procesiraj feedback, če obstaja
            if user_feedback:
                feedback_result = self.process_feedback(mia_response, user_feedback, user_id)
                learning_results['feedback_processed'] = feedback_result
                if feedback_result:
                    self.learning_stats['feedback_processed'] += 1
                    
            # 4. Posodobi model uporabnika
            user_update_result = self.update_user_model(user_id, user_input, mia_response)
            learning_results['user_model_updated'] = user_update_result
            if user_update_result:
                self.learning_stats['user_models_updated'] += 1
                
            # 5. Shrani pogovor v zgodovino
            self.knowledge.add_conversation(user_id, user_input, mia_response, {
                'facts_learned': learning_results['facts_learned'],
                'feedback_given': user_feedback is not None
            })
            
            self.learning_stats['total_conversations'] += 1
            
            return learning_results
            
        except Exception as e:
            logger.error(f"Error in learn_from_conversation: {e}")
            return {
                'facts_learned': 0,
                'feedback_processed': False,
                'user_model_updated': False,
                'errors': [str(e)]
            }
            
    def extract_facts_from_input(self, user_input: str) -> List[ExtractedFact]:
        """
        Ekstraktiraj dejstva iz uporabniškega vnosa.
        
        Args:
            user_input: Besedilo za analizo
            
        Returns:
            Seznam ekstraktiranih dejstev
        """
        facts = []
        
        try:
            # Razdeli na stavke
            sentences = self._split_into_sentences(user_input)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 10:  # Preskoči kratke stavke
                    continue
                    
                # Poskusi z vsemi vzorci
                for pattern, property_type, confidence in self.fact_patterns:
                    matches = re.findall(pattern, sentence, re.IGNORECASE)
                    
                    for match in matches:
                        if len(match) == 2:
                            entity = self._clean_entity(match[0])
                            value = self._clean_value(match[1])
                            
                            # Preveri veljavnost
                            if self._is_valid_fact(entity, value):
                                fact = ExtractedFact(
                                    entity=entity,
                                    property=property_type,
                                    value=value,
                                    confidence=confidence,
                                    source_sentence=sentence
                                )
                                facts.append(fact)
                                
        except Exception as e:
            logger.error(f"Error extracting facts: {e}")
            
        return facts
        
    def process_feedback(self, mia_response: str, user_feedback: str, user_id: str) -> bool:
        """
        Procesiraj uporabniški feedback za izboljšanje odgovorov.
        
        Args:
            mia_response: MIA-in odgovor
            user_feedback: Uporabniški feedback
            user_id: ID uporabnika
            
        Returns:
            True če je feedback uspešno procesiran
        """
        try:
            feedback_lower = user_feedback.lower()
            
            # Analiziraj sentiment feedback-a
            if any(word in feedback_lower for word in ['napačno', 'narobe', 'ne', 'slabo', 'wrong', 'incorrect', 'bad']):
                # Negativen feedback
                self.knowledge.add_fact(
                    entity=f"response_{hash(mia_response)}",
                    property="user_feedback",
                    value="negative",
                    source=f"feedback_{user_id}",
                    confidence=0.9,
                    user_id=user_id
                )
                
                logger.info(f"Negative feedback recorded for response: {mia_response[:50]}...")
                return True
                
            elif any(word in feedback_lower for word in ['pravilno', 'dobro', 'super', 'odlično', 'correct', 'good', 'great', 'excellent']):
                # Pozitiven feedback
                self.knowledge.add_fact(
                    entity=f"response_{hash(mia_response)}",
                    property="user_feedback",
                    value="positive",
                    source=f"feedback_{user_id}",
                    confidence=0.9,
                    user_id=user_id
                )
                
                logger.info(f"Positive feedback recorded for response: {mia_response[:50]}...")
                return True
                
            else:
                # Nevtralen feedback - poskusi ekstraktirati dejstva
                facts = self.extract_facts_from_input(user_feedback)
                if facts:
                    logger.info(f"Extracted {len(facts)} facts from feedback")
                    return True
                    
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            
        return False
        
    def update_user_model(self, user_id: str, user_input: str, mia_response: str) -> bool:
        """
        Posodobi model uporabnika na podlagi interakcije.
        
        Args:
            user_id: ID uporabnika
            user_input: Uporabniški vnos
            mia_response: MIA-in odgovor
            
        Returns:
            True če je model uspešno posodobljen
        """
        try:
            # Analiziraj komunikacijski stil
            communication_style = self._analyze_communication_style(user_input)
            
            # Ekstraktiraj interese
            interests = self._extract_interests(user_input)
            
            # Posodobi model uporabnika
            self.knowledge.update_user_model(
                user_id=user_id,
                communication_style=communication_style,
                interests=interests
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user model: {e}")
            return False
            
    def _split_into_sentences(self, text: str) -> List[str]:
        """Razdeli besedilo na stavke"""
        # Preprosta delitev - v resnici bi uporabili NLP
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
        
    def _clean_entity(self, entity: str) -> str:
        """Očisti entiteto"""
        entity = entity.strip().lower()
        
        # Odstrani stop words z začetka
        words = entity.split()
        while words and words[0] in self.stop_words['slovenščina'] | self.stop_words['angleščina']:
            words.pop(0)
            
        return ' '.join(words) if words else entity
        
    def _clean_value(self, value: str) -> str:
        """Očisti vrednost"""
        value = value.strip()
        
        # Odstrani končno ločilo
        if value.endswith(('.', ',', '!', '?')):
            value = value[:-1]
            
        return value
        
    def _is_valid_fact(self, entity: str, value: str) -> bool:
        """Preveri, ali je dejstvo veljavno"""
        return (
            len(entity) >= 2 and 
            len(value) >= 2 and
            entity != value and
            not entity.isdigit() and
            not all(c in '.,!?;:' for c in entity)
        )
        
    def _analyze_communication_style(self, user_input: str) -> Dict[str, str]:
        """Analiziraj komunikacijski stil uporabnika"""
        style = {}
        
        # Formalnost
        if any(word in user_input.lower() for word in ['prosim', 'hvala', 'oprostite', 'please', 'thank', 'sorry']):
            style['formality'] = 'formal'
        elif any(word in user_input.lower() for word in ['ej', 'hej', 'kul', 'hey', 'cool', 'sup']):
            style['formality'] = 'informal'
        else:
            style['formality'] = 'neutral'
            
        # Podrobnost
        word_count = len(user_input.split())
        if word_count > 20:
            style['detail_preference'] = 'detailed'
        elif word_count < 5:
            style['detail_preference'] = 'brief'
        else:
            style['detail_preference'] = 'moderate'
            
        # Jezik
        if any(word in user_input.lower() for word in ['je', 'so', 'in', 'ali', 'kaj', 'kako']):
            style['language'] = 'slovenian'
        elif any(word in user_input.lower() for word in ['is', 'are', 'and', 'or', 'what', 'how']):
            style['language'] = 'english'
        else:
            style['language'] = 'mixed'
            
        return style
        
    def _extract_interests(self, user_input: str) -> List[str]:
        """Ekstraktiraj interese iz uporabniškega vnosa"""
        interests = []
        
        # Preprosta detekcija tem
        topics = {
            'programming': ['python', 'javascript', 'programming', 'code', 'software', 'programiranje', 'koda'],
            'medicine': ['health', 'medicine', 'doctor', 'hospital', 'zdravje', 'medicina', 'zdravnik'],
            'science': ['science', 'physics', 'chemistry', 'biology', 'znanost', 'fizika', 'kemija'],
            'technology': ['technology', 'computer', 'internet', 'tehnologija', 'računalnik'],
            'sports': ['sport', 'football', 'basketball', 'tennis', 'šport', 'nogomet'],
            'music': ['music', 'song', 'band', 'guitar', 'glasba', 'pesem', 'skupina'],
            'food': ['food', 'cooking', 'recipe', 'restaurant', 'hrana', 'kuhanje', 'recept']
        }
        
        user_input_lower = user_input.lower()
        for topic, keywords in topics.items():
            if any(keyword in user_input_lower for keyword in keywords):
                interests.append(topic)
                
        return interests
        
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Pridobi statistike učenja"""
        return {
            **self.learning_stats,
            'facts_per_conversation': self.learning_stats['facts_extracted'] / max(self.learning_stats['total_conversations'], 1),
            'feedback_rate': self.learning_stats['feedback_processed'] / max(self.learning_stats['total_conversations'], 1)
        }
        
    def reset_statistics(self):
        """Ponastavi statistike učenja"""
        self.learning_stats = {
            'total_conversations': 0,
            'facts_extracted': 0,
            'feedback_processed': 0,
            'user_models_updated': 0
        }
        logger.info("Learning statistics reset")

# Example usage and testing
def main():
    """Primer uporabe InteractionLearner"""
    from mia.core.persistent_knowledge_store import PersistentKnowledgeStore
    
    # Initialize components
    knowledge_store = PersistentKnowledgeStore("data/test_learning")
    learner = InteractionLearner(knowledge_store)
    
    print("=== InteractionLearner Test ===")
    
    # Test conversations
    test_conversations = [
        ("Python je programski jezik", "Hvala za informacijo o Python-u!", None),
        ("Aspirin se uporablja za bolečine", "Zanimivo, shranil sem to informacijo.", "dobro"),
        ("Kaj je JavaScript?", "JavaScript je programski jezik za spletne strani.", "pravilno"),
        ("To je napačno", "Oprostite za napako.", "napačno")
    ]
    
    for i, (user_input, mia_response, feedback) in enumerate(test_conversations):
        print(f"\n{i+1}. Conversation:")
        print(f"   User: {user_input}")
        print(f"   MIA: {mia_response}")
        if feedback:
            print(f"   Feedback: {feedback}")
            
        result = learner.learn_from_conversation(user_input, mia_response, feedback, f"user_{i}")
        print(f"   Result: {result}")
        
    # Show statistics
    print(f"\nLearning Statistics:")
    stats = learner.get_learning_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
        
    print("\n=== Test completed ===")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()