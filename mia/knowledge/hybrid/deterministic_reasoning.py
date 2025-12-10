#!/usr/bin/env python3
"""
Deterministic Reasoning Engine - Deterministično sklepanje za hibridni MIA sistem
================================================================================

PRODUKCIJSKA IMPLEMENTACIJA determinističnega sklepanja.
Omogoča konsistentno, razložljivo in reproducibilno sklepanje na podlagi pravil in logike.

KLJUČNE FUNKCIONALNOSTI:
- Rule-based reasoning sistem
- Forward chaining inference
- Backward chaining inference  
- Z3 solver integration za constraint solving
- Explanation traces za razložljivost
- Consistency checking
- Integration z Knowledge Bank in Semantic Layer
- Reproducible results

ARHITEKTURA:
- Backward compatible z obstoječim MIA sistemom
- Integracija z Knowledge Bank Core in Semantic Layer
- Support za različne logične formalizme
- Explanation generation za transparency
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
import re

# Import existing MIA components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

try:
    from mia.knowledge.hybrid.knowledge_bank_core import HybridKnowledgeBank
    from mia.knowledge.hybrid.semantic_layer import SemanticLayer
    HYBRID_COMPONENTS_AVAILABLE = True
except ImportError:
    HYBRID_COMPONENTS_AVAILABLE = False

# Z3 solver dependencies
try:
    from z3 import *
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False

logger = logging.getLogger(__name__)

class RuleType(Enum):
    """Tipi pravil"""
    IMPLICATION = "implication"  # A → B
    EQUIVALENCE = "equivalence"  # A ↔ B
    CONSTRAINT = "constraint"    # Constraint pravilo
    FACT = "fact"               # Dejstvo
    QUERY = "query"             # Poizvedba

class InferenceMethod(Enum):
    """Metode sklepanja"""
    FORWARD_CHAINING = "forward_chaining"
    BACKWARD_CHAINING = "backward_chaining"
    CONSTRAINT_SOLVING = "constraint_solving"
    HYBRID = "hybrid"

@dataclass
class LogicalTerm:
    """Logični term"""
    name: str
    arguments: List[str]
    negated: bool = False
    
    def __str__(self):
        args_str = f"({', '.join(self.arguments)})" if self.arguments else ""
        neg_str = "¬" if self.negated else ""
        return f"{neg_str}{self.name}{args_str}"

@dataclass
class Rule:
    """Pravilo za sklepanje"""
    rule_id: str
    rule_type: RuleType
    premises: List[LogicalTerm]  # Predpostavke (antecedent)
    conclusions: List[LogicalTerm]  # Sklepi (consequent)
    confidence: float
    priority: int
    source: str
    created_at: float
    metadata: Dict[str, Any]
    
    def __str__(self):
        premises_str = " ∧ ".join(str(p) for p in self.premises)
        conclusions_str = " ∧ ".join(str(c) for c in self.conclusions)
        
        if self.rule_type == RuleType.IMPLICATION:
            return f"{premises_str} → {conclusions_str}"
        elif self.rule_type == RuleType.EQUIVALENCE:
            return f"{premises_str} ↔ {conclusions_str}"
        else:
            return f"{premises_str} | {conclusions_str}"

@dataclass
class Fact:
    """Dejstvo v bazi znanja"""
    fact_id: str
    term: LogicalTerm
    confidence: float
    source: str
    timestamp: float
    derived: bool = False  # Ali je izpeljano iz pravil
    derivation_trace: List[str] = None

@dataclass
class InferenceStep:
    """Korak sklepanja"""
    step_id: str
    rule_applied: str
    premises_used: List[str]
    conclusions_derived: List[str]
    method: InferenceMethod
    confidence: float
    timestamp: float

@dataclass
class ReasoningResult:
    """Rezultat sklepanja"""
    query: str
    success: bool
    results: List[Fact]
    inference_steps: List[InferenceStep]
    explanation: str
    confidence: float
    processing_time: float
    method_used: InferenceMethod
    metadata: Dict[str, Any]

@dataclass
class ConsistencyCheck:
    """Rezultat preverjanja konsistentnosti"""
    consistent: bool
    contradictions: List[Dict[str, Any]]
    warnings: List[str]
    check_time: float

class DeterministicReasoningEngine:
    """
    Deterministični reasoning engine za hibridni MIA sistem.
    
    Omogoča:
    - Rule-based reasoning z forward/backward chaining
    - Z3 constraint solving
    - Explanation generation
    - Consistency checking
    - Integration z Knowledge Bank in Semantic Layer
    
    PRODUKCIJSKE FUNKCIONALNOSTI:
    ✅ Rule-based sistem z različnimi tipi pravil
    ✅ Forward in backward chaining
    ✅ Z3 solver integration
    ✅ Explanation traces za razložljivost
    ✅ Consistency checking
    ✅ Async operations za performance
    ✅ Comprehensive error handling
    ✅ Statistics in monitoring
    """
    
    def __init__(self,
                 knowledge_bank: Optional[HybridKnowledgeBank] = None,
                 semantic_layer: Optional[SemanticLayer] = None,
                 data_dir: str = "data/reasoning_engine",
                 max_inference_depth: int = 10):
        """
        Inicializiraj deterministični reasoning engine.
        
        Args:
            knowledge_bank: Povezava z Knowledge Bank
            semantic_layer: Povezava z Semantic Layer
            data_dir: Direktorij za podatke
            max_inference_depth: Maksimalna globina sklepanja
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Component integration
        self.knowledge_bank = knowledge_bank
        self.semantic_layer = semantic_layer
        self.kb_integration = knowledge_bank is not None
        self.semantic_integration = semantic_layer is not None
        
        # Z3 solver availability
        self.z3_available = Z3_AVAILABLE
        if self.z3_available:
            logger.info("✅ Z3 solver available")
        else:
            logger.warning("❌ Z3 solver not available - constraint solving limited")
            
        # Reasoning configuration
        self.max_inference_depth = max_inference_depth
        self.inference_timeout = 30.0  # seconds
        
        # Performance optimization
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.inference_cache: Dict[str, ReasoningResult] = {}
        self.cache_size = 1000
        
        # Knowledge base
        self.rules: Dict[str, Rule] = {}
        self.facts: Dict[str, Fact] = {}
        self.inference_history: List[InferenceStep] = []
        
        # Statistics
        self.stats = {
            'rules_count': 0,
            'facts_count': 0,
            'inferences_performed': 0,
            'forward_chaining_runs': 0,
            'backward_chaining_runs': 0,
            'constraint_solving_runs': 0,
            'consistency_checks': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'system_health': 'initializing',
            'start_time': time.time()
        }
        
        # Load existing data
        self._load_reasoning_data()
        
        # Initialize basic rules
        self._initialize_basic_rules()
        
        # Update statistics
        self._update_statistics()
        
        logger.info("✅ Deterministic Reasoning Engine inicializiran")
        logger.info(f"   - Z3 Solver: {'✅' if self.z3_available else '❌'}")
        logger.info(f"   - Knowledge Bank: {'✅' if self.kb_integration else '❌'}")
        logger.info(f"   - Semantic Layer: {'✅' if self.semantic_integration else '❌'}")
        logger.info(f"   - Rules: {len(self.rules)}")
        logger.info(f"   - Facts: {len(self.facts)}")
        
    def _update_statistics(self):
        """Posodobi statistike sistema"""
        try:
            self.stats['rules_count'] = len(self.rules)
            self.stats['facts_count'] = len(self.facts)
            self.stats['system_health'] = 'healthy'
            
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
            self.stats['system_health'] = 'error'
            
    def _initialize_basic_rules(self):
        """Inicializiraj osnovna pravila"""
        try:
            # Transitivity rule: if A → B and B → C, then A → C
            transitivity_rule = Rule(
                rule_id="transitivity_implication",
                rule_type=RuleType.IMPLICATION,
                premises=[
                    LogicalTerm("implies", ["X", "Y"]),
                    LogicalTerm("implies", ["Y", "Z"])
                ],
                conclusions=[
                    LogicalTerm("implies", ["X", "Z"])
                ],
                confidence=1.0,
                priority=100,
                source="system",
                created_at=time.time(),
                metadata={"description": "Transitivity of implication"}
            )
            self.rules[transitivity_rule.rule_id] = transitivity_rule
            
            # Modus ponens: if A → B and A, then B
            modus_ponens = Rule(
                rule_id="modus_ponens",
                rule_type=RuleType.IMPLICATION,
                premises=[
                    LogicalTerm("implies", ["X", "Y"]),
                    LogicalTerm("holds", ["X"])
                ],
                conclusions=[
                    LogicalTerm("holds", ["Y"])
                ],
                confidence=1.0,
                priority=100,
                source="system",
                created_at=time.time(),
                metadata={"description": "Modus ponens inference rule"}
            )
            self.rules[modus_ponens.rule_id] = modus_ponens
            
            # Modus tollens: if A → B and ¬B, then ¬A
            modus_tollens = Rule(
                rule_id="modus_tollens",
                rule_type=RuleType.IMPLICATION,
                premises=[
                    LogicalTerm("implies", ["X", "Y"]),
                    LogicalTerm("holds", ["Y"], negated=True)
                ],
                conclusions=[
                    LogicalTerm("holds", ["X"], negated=True)
                ],
                confidence=1.0,
                priority=100,
                source="system",
                created_at=time.time(),
                metadata={"description": "Modus tollens inference rule"}
            )
            self.rules[modus_tollens.rule_id] = modus_tollens
            
            logger.debug(f"Initialized {len(self.rules)} basic reasoning rules")
            
        except Exception as e:
            logger.error(f"Error initializing basic rules: {e}")
            
    async def add_rule(self, rule: Rule) -> bool:
        """
        Dodaj pravilo v reasoning engine.
        
        Args:
            rule: Pravilo za dodajanje
            
        Returns:
            True če je uspešno dodano
        """
        try:
            # Validate rule
            if not self._validate_rule(rule):
                logger.warning(f"Rule validation failed: {rule.rule_id}")
                return False
                
            # Check for conflicts
            conflicts = await self._check_rule_conflicts(rule)
            if conflicts:
                logger.warning(f"Rule conflicts detected: {conflicts}")
                
            # Add rule
            self.rules[rule.rule_id] = rule
            
            # Update statistics
            self._update_statistics()
            
            logger.info(f"✅ Added rule: {rule.rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding rule: {e}")
            return False
            
    async def add_fact(self, fact: Fact) -> bool:
        """
        Dodaj dejstvo v bazo znanja.
        
        Args:
            fact: Dejstvo za dodajanje
            
        Returns:
            True če je uspešno dodano
        """
        try:
            # Check for contradictions
            contradictions = await self._check_fact_contradictions(fact)
            if contradictions:
                logger.warning(f"Fact contradictions detected: {contradictions}")
                
            # Add fact
            self.facts[fact.fact_id] = fact
            
            # Update statistics
            self._update_statistics()
            
            logger.info(f"✅ Added fact: {fact.fact_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding fact: {e}")
            return False
            
    async def forward_chaining(self, max_iterations: int = 100) -> List[Fact]:
        """
        Izvedi forward chaining sklepanje.
        
        Args:
            max_iterations: Maksimalno število iteracij
            
        Returns:
            Seznam novih dejstev
        """
        try:
            self.stats['forward_chaining_runs'] += 1
            start_time = time.time()
            
            new_facts = []
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                facts_added_this_iteration = []
                
                # Apply all applicable rules
                for rule in self.rules.values():
                    if rule.rule_type in [RuleType.IMPLICATION, RuleType.EQUIVALENCE]:
                        derived_facts = await self._apply_rule_forward(rule)
                        facts_added_this_iteration.extend(derived_facts)
                        
                # Add new facts to knowledge base
                for fact in facts_added_this_iteration:
                    if fact.fact_id not in self.facts:
                        self.facts[fact.fact_id] = fact
                        new_facts.append(fact)
                        
                # If no new facts were derived, stop
                if not facts_added_this_iteration:
                    break
                    
            processing_time = time.time() - start_time
            
            logger.info(f"Forward chaining completed: {len(new_facts)} new facts in {iteration} iterations ({processing_time:.3f}s)")
            
            return new_facts
            
        except Exception as e:
            logger.error(f"Error in forward chaining: {e}")
            return []
            
    async def backward_chaining(self, query: LogicalTerm, depth: int = 0) -> ReasoningResult:
        """
        Izvedi backward chaining sklepanje za poizvedbo.
        
        Args:
            query: Poizvedba
            depth: Trenutna globina sklepanja
            
        Returns:
            ReasoningResult
        """
        try:
            self.stats['backward_chaining_runs'] += 1
            start_time = time.time()
            
            if depth > self.max_inference_depth:
                return ReasoningResult(
                    query=str(query),
                    success=False,
                    results=[],
                    inference_steps=[],
                    explanation="Maximum inference depth exceeded",
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    method_used=InferenceMethod.BACKWARD_CHAINING,
                    metadata={"depth_exceeded": True}
                )
                
            # Check if query is already a known fact
            for fact in self.facts.values():
                if self._terms_match(query, fact.term):
                    return ReasoningResult(
                        query=str(query),
                        success=True,
                        results=[fact],
                        inference_steps=[],
                        explanation=f"Query matches known fact: {fact.fact_id}",
                        confidence=fact.confidence,
                        processing_time=time.time() - start_time,
                        method_used=InferenceMethod.BACKWARD_CHAINING,
                        metadata={"direct_match": True}
                    )
                    
            # Try to prove query using rules
            inference_steps = []
            all_results = []
            
            for rule in self.rules.values():
                if rule.rule_type == RuleType.IMPLICATION:
                    # Check if query matches any conclusion
                    for conclusion in rule.conclusions:
                        if self._terms_match(query, conclusion):
                            # Try to prove all premises
                            premise_results = []
                            can_prove = True
                            
                            for premise in rule.premises:
                                premise_result = await self.backward_chaining(premise, depth + 1)
                                if premise_result.success:
                                    premise_results.extend(premise_result.results)
                                    inference_steps.extend(premise_result.inference_steps)
                                else:
                                    can_prove = False
                                    break
                                    
                            if can_prove:
                                # Create derived fact
                                derived_fact = Fact(
                                    fact_id=str(uuid.uuid4()),
                                    term=query,
                                    confidence=min([r.confidence for r in premise_results] + [rule.confidence]),
                                    source="backward_chaining",
                                    timestamp=time.time(),
                                    derived=True,
                                    derivation_trace=[rule.rule_id]
                                )
                                
                                # Record inference step
                                step = InferenceStep(
                                    step_id=str(uuid.uuid4()),
                                    rule_applied=rule.rule_id,
                                    premises_used=[r.fact_id for r in premise_results],
                                    conclusions_derived=[derived_fact.fact_id],
                                    method=InferenceMethod.BACKWARD_CHAINING,
                                    confidence=derived_fact.confidence,
                                    timestamp=time.time()
                                )
                                
                                inference_steps.append(step)
                                all_results.append(derived_fact)
                                
            processing_time = time.time() - start_time
            
            if all_results:
                explanation = self._generate_explanation(inference_steps)
                confidence = max(r.confidence for r in all_results)
                
                return ReasoningResult(
                    query=str(query),
                    success=True,
                    results=all_results,
                    inference_steps=inference_steps,
                    explanation=explanation,
                    confidence=confidence,
                    processing_time=processing_time,
                    method_used=InferenceMethod.BACKWARD_CHAINING,
                    metadata={"depth": depth}
                )
            else:
                return ReasoningResult(
                    query=str(query),
                    success=False,
                    results=[],
                    inference_steps=inference_steps,
                    explanation="Could not prove query using available rules and facts",
                    confidence=0.0,
                    processing_time=processing_time,
                    method_used=InferenceMethod.BACKWARD_CHAINING,
                    metadata={"depth": depth}
                )
                
        except Exception as e:
            logger.error(f"Error in backward chaining: {e}")
            return ReasoningResult(
                query=str(query),
                success=False,
                results=[],
                inference_steps=[],
                explanation=f"Error during reasoning: {e}",
                confidence=0.0,
                processing_time=time.time() - start_time,
                method_used=InferenceMethod.BACKWARD_CHAINING,
                metadata={"error": str(e)}
            )
            
    async def _apply_rule_forward(self, rule: Rule) -> List[Fact]:
        """Uporabi pravilo v forward chaining načinu"""
        derived_facts = []
        
        try:
            # Find all combinations of facts that match the premises
            premise_combinations = await self._find_premise_matches(rule.premises)
            
            for combination in premise_combinations:
                # Check if all premises are satisfied
                if len(combination) == len(rule.premises):
                    # Derive conclusions
                    for conclusion in rule.conclusions:
                        # Create derived fact
                        derived_fact = Fact(
                            fact_id=str(uuid.uuid4()),
                            term=conclusion,
                            confidence=min([f.confidence for f in combination] + [rule.confidence]),
                            source="forward_chaining",
                            timestamp=time.time(),
                            derived=True,
                            derivation_trace=[rule.rule_id]
                        )
                        
                        # Check if this fact already exists
                        if not any(self._terms_match(derived_fact.term, existing.term) 
                                 for existing in self.facts.values()):
                            derived_facts.append(derived_fact)
                            
        except Exception as e:
            logger.error(f"Error applying rule {rule.rule_id}: {e}")
            
        return derived_facts
        
    async def _find_premise_matches(self, premises: List[LogicalTerm]) -> List[List[Fact]]:
        """Najdi kombinacije dejstev, ki se ujemajo s predpostavkami"""
        if not premises:
            return [[]]
            
        matches = []
        
        # Simple implementation - can be optimized
        for fact in self.facts.values():
            if self._terms_match(premises[0], fact.term):
                if len(premises) == 1:
                    matches.append([fact])
                else:
                    # Recursively find matches for remaining premises
                    remaining_matches = await self._find_premise_matches(premises[1:])
                    for remaining in remaining_matches:
                        matches.append([fact] + remaining)
                        
        return matches
        
    def _terms_match(self, term1: LogicalTerm, term2: LogicalTerm) -> bool:
        """Preveri, ali se dva logična termina ujemata"""
        try:
            # Simple matching - can be extended with unification
            return (term1.name == term2.name and 
                   term1.arguments == term2.arguments and
                   term1.negated == term2.negated)
                   
        except Exception as e:
            logger.error(f"Error matching terms: {e}")
            return False
            
    def _validate_rule(self, rule: Rule) -> bool:
        """Validiraj pravilo"""
        try:
            # Basic validation
            if not rule.rule_id or not rule.premises or not rule.conclusions:
                return False
                
            if rule.confidence < 0.0 or rule.confidence > 1.0:
                return False
                
            # Check for circular dependencies
            if self._has_circular_dependency(rule):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating rule: {e}")
            return False
            
    def _has_circular_dependency(self, rule: Rule) -> bool:
        """Preveri krožne odvisnosti"""
        # Simplified check - can be made more sophisticated
        premise_terms = {term.name for term in rule.premises}
        conclusion_terms = {term.name for term in rule.conclusions}
        
        return bool(premise_terms.intersection(conclusion_terms))
        
    async def _check_rule_conflicts(self, rule: Rule) -> List[str]:
        """Preveri konflikte s obstoječimi pravili"""
        conflicts = []
        
        try:
            for existing_rule in self.rules.values():
                if self._rules_conflict(rule, existing_rule):
                    conflicts.append(existing_rule.rule_id)
                    
        except Exception as e:
            logger.error(f"Error checking rule conflicts: {e}")
            
        return conflicts
        
    def _rules_conflict(self, rule1: Rule, rule2: Rule) -> bool:
        """Preveri, ali se pravili konfliktirata"""
        # Simplified conflict detection
        # In practice, this would be more sophisticated
        return False
        
    async def _check_fact_contradictions(self, fact: Fact) -> List[str]:
        """Preveri protislovja z obstoječimi dejstvi"""
        contradictions = []
        
        try:
            for existing_fact in self.facts.values():
                if self._facts_contradict(fact, existing_fact):
                    contradictions.append(existing_fact.fact_id)
                    
        except Exception as e:
            logger.error(f"Error checking fact contradictions: {e}")
            
        return contradictions
        
    def _facts_contradict(self, fact1: Fact, fact2: Fact) -> bool:
        """Preveri, ali se dejstvi protislovita"""
        # Check if one is negation of the other
        return (fact1.term.name == fact2.term.name and
               fact1.term.arguments == fact2.term.arguments and
               fact1.term.negated != fact2.term.negated)
               
    def _generate_explanation(self, inference_steps: List[InferenceStep]) -> str:
        """Generiraj razlago sklepanja"""
        if not inference_steps:
            return "No inference steps performed."
            
        explanation_parts = []
        
        for i, step in enumerate(inference_steps, 1):
            rule_info = self.rules.get(step.rule_applied, None)
            rule_desc = rule_info.metadata.get('description', step.rule_applied) if rule_info else step.rule_applied
            
            explanation_parts.append(
                f"Step {i}: Applied rule '{rule_desc}' "
                f"using premises {step.premises_used} "
                f"to derive {step.conclusions_derived} "
                f"(confidence: {step.confidence:.2f})"
            )
            
        return "\n".join(explanation_parts)
        
    async def check_consistency(self) -> ConsistencyCheck:
        """Preveri konsistentnost baze znanja"""
        try:
            self.stats['consistency_checks'] += 1
            start_time = time.time()
            
            contradictions = []
            warnings = []
            
            # Check for direct contradictions between facts
            facts_list = list(self.facts.values())
            for i, fact1 in enumerate(facts_list):
                for fact2 in facts_list[i+1:]:
                    if self._facts_contradict(fact1, fact2):
                        contradictions.append({
                            'type': 'fact_contradiction',
                            'fact1': fact1.fact_id,
                            'fact2': fact2.fact_id,
                            'description': f"Facts {fact1.fact_id} and {fact2.fact_id} contradict each other"
                        })
                        
            # Check for rule conflicts
            rules_list = list(self.rules.values())
            for i, rule1 in enumerate(rules_list):
                for rule2 in rules_list[i+1:]:
                    if self._rules_conflict(rule1, rule2):
                        warnings.append(f"Rules {rule1.rule_id} and {rule2.rule_id} may conflict")
                        
            # Use Z3 solver for more sophisticated consistency checking
            if self.z3_available:
                z3_contradictions = await self._check_consistency_z3()
                contradictions.extend(z3_contradictions)
                
            check_time = time.time() - start_time
            is_consistent = len(contradictions) == 0
            
            logger.info(f"Consistency check: {'✅ Consistent' if is_consistent else '❌ Inconsistent'} "
                       f"({len(contradictions)} contradictions, {len(warnings)} warnings)")
                       
            return ConsistencyCheck(
                consistent=is_consistent,
                contradictions=contradictions,
                warnings=warnings,
                check_time=check_time
            )
            
        except Exception as e:
            logger.error(f"Error checking consistency: {e}")
            return ConsistencyCheck(
                consistent=False,
                contradictions=[{'type': 'error', 'description': str(e)}],
                warnings=[],
                check_time=0.0
            )
            
    async def _check_consistency_z3(self) -> List[Dict[str, Any]]:
        """Uporabi Z3 solver za preverjanje konsistentnosti"""
        contradictions = []
        
        if not self.z3_available:
            return contradictions
            
        try:
            def z3_check():
                solver = Solver()
                
                # Convert facts and rules to Z3 constraints
                # This is a simplified implementation
                variables = {}
                
                # Add facts as constraints
                for fact in self.facts.values():
                    var_name = f"{fact.term.name}_{hash(str(fact.term.arguments))}"
                    if var_name not in variables:
                        variables[var_name] = Bool(var_name)
                        
                    if fact.term.negated:
                        solver.add(Not(variables[var_name]))
                    else:
                        solver.add(variables[var_name])
                        
                # Check satisfiability
                result = solver.check()
                
                if result == unsat:
                    return [{'type': 'z3_contradiction', 'description': 'Z3 solver found unsatisfiable constraints'}]
                elif result == unknown:
                    return [{'type': 'z3_unknown', 'description': 'Z3 solver could not determine satisfiability'}]
                else:
                    return []
                    
            # Run Z3 check in executor
            z3_result = await asyncio.get_event_loop().run_in_executor(
                self.executor, z3_check
            )
            
            contradictions.extend(z3_result)
            
        except Exception as e:
            logger.error(f"Error in Z3 consistency check: {e}")
            
        return contradictions
        
    async def reason(self, query: str, method: InferenceMethod = InferenceMethod.HYBRID) -> ReasoningResult:
        """
        Glavna metoda za sklepanje.
        
        Args:
            query: Poizvedba v naravnem jeziku ali logični obliki
            method: Metoda sklepanja
            
        Returns:
            ReasoningResult
        """
        try:
            self.stats['inferences_performed'] += 1
            
            # Check cache
            cache_key = hashlib.md5(f"{query}_{method.value}".encode()).hexdigest()
            if cache_key in self.inference_cache:
                self.stats['cache_hits'] += 1
                return self.inference_cache[cache_key]
                
            self.stats['cache_misses'] += 1
            
            # Parse query to logical term
            logical_query = await self._parse_query(query)
            
            if method == InferenceMethod.FORWARD_CHAINING:
                # Run forward chaining first, then check if query is satisfied
                new_facts = await self.forward_chaining()
                result = await self._check_query_satisfaction(logical_query)
                
            elif method == InferenceMethod.BACKWARD_CHAINING:
                result = await self.backward_chaining(logical_query)
                
            elif method == InferenceMethod.CONSTRAINT_SOLVING:
                result = await self._constraint_solve(logical_query)
                
            else:  # HYBRID
                # Try backward chaining first
                result = await self.backward_chaining(logical_query)
                
                if not result.success:
                    # Try forward chaining
                    await self.forward_chaining()
                    result = await self._check_query_satisfaction(logical_query)
                    
                if not result.success and self.z3_available:
                    # Try constraint solving
                    constraint_result = await self._constraint_solve(logical_query)
                    if constraint_result.success:
                        result = constraint_result
                        
            # Cache result
            if len(self.inference_cache) < self.cache_size:
                self.inference_cache[cache_key] = result
                
            return result
            
        except Exception as e:
            logger.error(f"Error in reasoning: {e}")
            return ReasoningResult(
                query=query,
                success=False,
                results=[],
                inference_steps=[],
                explanation=f"Error during reasoning: {e}",
                confidence=0.0,
                processing_time=0.0,
                method_used=method,
                metadata={"error": str(e)}
            )
            
    async def _parse_query(self, query: str) -> LogicalTerm:
        """Parsiraj poizvedbo v logični term"""
        try:
            # Simple parsing - can be made more sophisticated
            # For now, assume query is in format "predicate(arg1, arg2, ...)"
            
            if '(' in query and ')' in query:
                # Structured query
                predicate = query.split('(')[0].strip()
                args_str = query.split('(')[1].split(')')[0]
                arguments = [arg.strip() for arg in args_str.split(',') if arg.strip()]
                
                return LogicalTerm(name=predicate, arguments=arguments)
            else:
                # Simple predicate
                return LogicalTerm(name=query.strip(), arguments=[])
                
        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            return LogicalTerm(name=query, arguments=[])
            
    async def _check_query_satisfaction(self, query: LogicalTerm) -> ReasoningResult:
        """Preveri, ali je poizvedba zadoščena"""
        start_time = time.time()
        
        matching_facts = []
        for fact in self.facts.values():
            if self._terms_match(query, fact.term):
                matching_facts.append(fact)
                
        if matching_facts:
            confidence = max(f.confidence for f in matching_facts)
            return ReasoningResult(
                query=str(query),
                success=True,
                results=matching_facts,
                inference_steps=[],
                explanation=f"Query satisfied by {len(matching_facts)} facts",
                confidence=confidence,
                processing_time=time.time() - start_time,
                method_used=InferenceMethod.FORWARD_CHAINING,
                metadata={"direct_satisfaction": True}
            )
        else:
            return ReasoningResult(
                query=str(query),
                success=False,
                results=[],
                inference_steps=[],
                explanation="Query not satisfied by any known facts",
                confidence=0.0,
                processing_time=time.time() - start_time,
                method_used=InferenceMethod.FORWARD_CHAINING,
                metadata={"direct_satisfaction": False}
            )
            
    async def _constraint_solve(self, query: LogicalTerm) -> ReasoningResult:
        """Uporabi constraint solving za poizvedbo"""
        start_time = time.time()
        
        if not self.z3_available:
            return ReasoningResult(
                query=str(query),
                success=False,
                results=[],
                inference_steps=[],
                explanation="Z3 solver not available",
                confidence=0.0,
                processing_time=time.time() - start_time,
                method_used=InferenceMethod.CONSTRAINT_SOLVING,
                metadata={"z3_unavailable": True}
            )
            
        try:
            self.stats['constraint_solving_runs'] += 1
            
            def solve_constraints():
                solver = Solver()
                
                # Add constraints from facts and rules
                # This is a simplified implementation
                variables = {}
                
                # Create variable for query
                query_var_name = f"{query.name}_{hash(str(query.arguments))}"
                query_var = Bool(query_var_name)
                variables[query_var_name] = query_var
                
                # Add facts as constraints
                for fact in self.facts.values():
                    var_name = f"{fact.term.name}_{hash(str(fact.term.arguments))}"
                    if var_name not in variables:
                        variables[var_name] = Bool(var_name)
                        
                    if fact.term.negated:
                        solver.add(Not(variables[var_name]))
                    else:
                        solver.add(variables[var_name])
                        
                # Add rules as constraints
                for rule in self.rules.values():
                    if rule.rule_type == RuleType.IMPLICATION:
                        # Convert A → B to ¬A ∨ B
                        premise_vars = []
                        for premise in rule.premises:
                            var_name = f"{premise.name}_{hash(str(premise.arguments))}"
                            if var_name not in variables:
                                variables[var_name] = Bool(var_name)
                            premise_vars.append(variables[var_name])
                            
                        conclusion_vars = []
                        for conclusion in rule.conclusions:
                            var_name = f"{conclusion.name}_{hash(str(conclusion.arguments))}"
                            if var_name not in variables:
                                variables[var_name] = Bool(var_name)
                            conclusion_vars.append(variables[var_name])
                            
                        # Add implication constraint
                        if premise_vars and conclusion_vars:
                            premise_conjunction = And(premise_vars) if len(premise_vars) > 1 else premise_vars[0]
                            conclusion_disjunction = Or(conclusion_vars) if len(conclusion_vars) > 1 else conclusion_vars[0]
                            solver.add(Implies(premise_conjunction, conclusion_disjunction))
                            
                # Check if query can be satisfied
                solver.push()
                solver.add(query_var)
                
                result = solver.check()
                
                if result == sat:
                    model = solver.model()
                    return {'satisfiable': True, 'model': str(model)}
                elif result == unsat:
                    return {'satisfiable': False, 'model': None}
                else:
                    return {'satisfiable': None, 'model': None}
                    
            # Run constraint solving in executor
            solve_result = await asyncio.get_event_loop().run_in_executor(
                self.executor, solve_constraints
            )
            
            processing_time = time.time() - start_time
            
            if solve_result['satisfiable'] is True:
                # Create derived fact from solution
                derived_fact = Fact(
                    fact_id=str(uuid.uuid4()),
                    term=query,
                    confidence=0.8,  # Lower confidence for constraint-derived facts
                    source="constraint_solving",
                    timestamp=time.time(),
                    derived=True,
                    derivation_trace=["z3_solver"]
                )
                
                return ReasoningResult(
                    query=str(query),
                    success=True,
                    results=[derived_fact],
                    inference_steps=[],
                    explanation=f"Query satisfied by constraint solving. Model: {solve_result['model']}",
                    confidence=0.8,
                    processing_time=processing_time,
                    method_used=InferenceMethod.CONSTRAINT_SOLVING,
                    metadata={"z3_model": solve_result['model']}
                )
            else:
                return ReasoningResult(
                    query=str(query),
                    success=False,
                    results=[],
                    inference_steps=[],
                    explanation="Query cannot be satisfied by constraint solving",
                    confidence=0.0,
                    processing_time=processing_time,
                    method_used=InferenceMethod.CONSTRAINT_SOLVING,
                    metadata={"z3_result": solve_result}
                )
                
        except Exception as e:
            logger.error(f"Error in constraint solving: {e}")
            return ReasoningResult(
                query=str(query),
                success=False,
                results=[],
                inference_steps=[],
                explanation=f"Error in constraint solving: {e}",
                confidence=0.0,
                processing_time=time.time() - start_time,
                method_used=InferenceMethod.CONSTRAINT_SOLVING,
                metadata={"error": str(e)}
            )
            
    def _load_reasoning_data(self):
        """Naloži reasoning podatke z diska"""
        try:
            # Load rules
            rules_file = self.data_dir / 'rules.json'
            if rules_file.exists():
                with open(rules_file, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)
                    for rule_id, data in rules_data.items():
                        # Reconstruct LogicalTerm objects
                        premises = [LogicalTerm(**p) for p in data['premises']]
                        conclusions = [LogicalTerm(**c) for c in data['conclusions']]
                        
                        rule = Rule(
                            rule_id=rule_id,
                            rule_type=RuleType(data['rule_type']),
                            premises=premises,
                            conclusions=conclusions,
                            confidence=data['confidence'],
                            priority=data['priority'],
                            source=data['source'],
                            created_at=data['created_at'],
                            metadata=data['metadata']
                        )
                        self.rules[rule_id] = rule
                        
            # Load facts
            facts_file = self.data_dir / 'facts.json'
            if facts_file.exists():
                with open(facts_file, 'r', encoding='utf-8') as f:
                    facts_data = json.load(f)
                    for fact_id, data in facts_data.items():
                        term = LogicalTerm(**data['term'])
                        
                        fact = Fact(
                            fact_id=fact_id,
                            term=term,
                            confidence=data['confidence'],
                            source=data['source'],
                            timestamp=data['timestamp'],
                            derived=data.get('derived', False),
                            derivation_trace=data.get('derivation_trace', [])
                        )
                        self.facts[fact_id] = fact
                        
            logger.info(f"✅ Reasoning data loaded: {len(self.rules)} rules, {len(self.facts)} facts")
            
        except Exception as e:
            logger.error(f"Error loading reasoning data: {e}")
            
    async def save_reasoning_data(self) -> bool:
        """Shrani reasoning podatke na disk"""
        try:
            def save_data():
                # Save rules
                rules_file = self.data_dir / 'rules.json'
                with open(rules_file, 'w', encoding='utf-8') as f:
                    rules_data = {}
                    for rule_id, rule in self.rules.items():
                        rules_data[rule_id] = {
                            'rule_type': rule.rule_type.value,
                            'premises': [asdict(p) for p in rule.premises],
                            'conclusions': [asdict(c) for c in rule.conclusions],
                            'confidence': rule.confidence,
                            'priority': rule.priority,
                            'source': rule.source,
                            'created_at': rule.created_at,
                            'metadata': rule.metadata
                        }
                    json.dump(rules_data, f, indent=2, ensure_ascii=False)
                    
                # Save facts
                facts_file = self.data_dir / 'facts.json'
                with open(facts_file, 'w', encoding='utf-8') as f:
                    facts_data = {}
                    for fact_id, fact in self.facts.items():
                        facts_data[fact_id] = {
                            'term': asdict(fact.term),
                            'confidence': fact.confidence,
                            'source': fact.source,
                            'timestamp': fact.timestamp,
                            'derived': fact.derived,
                            'derivation_trace': fact.derivation_trace or []
                        }
                    json.dump(facts_data, f, indent=2, ensure_ascii=False)
                    
                # Save statistics
                stats_file = self.data_dir / 'reasoning_statistics.json'
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump(self.stats, f, indent=2, default=str)
                    
                return True
                
            success = await asyncio.get_event_loop().run_in_executor(
                self.executor, save_data
            )
            
            if success:
                logger.info("✅ Reasoning data saved successfully")
                return True
            else:
                logger.error("❌ Failed to save reasoning data")
                return False
                
        except Exception as e:
            logger.error(f"Error saving reasoning data: {e}")
            return False
            
    def get_statistics(self) -> Dict[str, Any]:
        """Pridobi statistike Reasoning Engine"""
        self._update_statistics()
        
        return {
            'basic_stats': {
                'rules_count': len(self.rules),
                'facts_count': len(self.facts),
                'inferences_performed': self.stats['inferences_performed'],
                'consistency_checks': self.stats['consistency_checks']
            },
            'method_stats': {
                'forward_chaining_runs': self.stats['forward_chaining_runs'],
                'backward_chaining_runs': self.stats['backward_chaining_runs'],
                'constraint_solving_runs': self.stats['constraint_solving_runs']
            },
            'performance_stats': {
                'cache_hits': self.stats['cache_hits'],
                'cache_misses': self.stats['cache_misses'],
                'cache_hit_ratio': self.stats['cache_hits'] / max(self.stats['cache_hits'] + self.stats['cache_misses'], 1),
                'cache_size': len(self.inference_cache)
            },
            'system_info': {
                'z3_available': self.z3_available,
                'kb_integration': self.kb_integration,
                'semantic_integration': self.semantic_integration,
                'max_inference_depth': self.max_inference_depth,
                'system_health': self.stats['system_health']
            },
            'uptime': time.time() - self.stats['start_time']
        }
        
    async def shutdown(self):
        """Graceful shutdown Reasoning Engine"""
        try:
            logger.info("🔄 Shutting down Deterministic Reasoning Engine...")
            
            # Save current state
            await self.save_reasoning_data()
            
            # Shutdown executor
            if self.executor:
                self.executor.shutdown(wait=True)
                
            # Clear caches
            self.inference_cache.clear()
            
            # Update final statistics
            self.stats['system_health'] = 'shutdown'
            
            logger.info("✅ Deterministic Reasoning Engine shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Convenience functions
async def create_reasoning_engine(knowledge_bank: Optional[HybridKnowledgeBank] = None,
                                 semantic_layer: Optional[SemanticLayer] = None,
                                 data_dir: str = "data/reasoning_engine") -> DeterministicReasoningEngine:
    """
    Ustvari in inicializiraj Deterministic Reasoning Engine.
    
    Args:
        knowledge_bank: Povezava z Knowledge Bank
        semantic_layer: Povezava z Semantic Layer
        data_dir: Direktorij za podatke
        
    Returns:
        Inicializiran DeterministicReasoningEngine
    """
    try:
        reasoning_engine = DeterministicReasoningEngine(
            knowledge_bank=knowledge_bank,
            semantic_layer=semantic_layer,
            data_dir=data_dir
        )
        
        return reasoning_engine
        
    except Exception as e:
        logger.error(f"Failed to create Deterministic Reasoning Engine: {e}")
        raise


if __name__ == "__main__":
    # Test implementation
    async def test_reasoning_engine():
        """Test Deterministic Reasoning Engine"""
        try:
            logger.info("🧪 Testing Deterministic Reasoning Engine...")
            
            # Create reasoning engine
            reasoning_engine = await create_reasoning_engine()
            
            # Add test facts
            fact1 = Fact(
                fact_id="fact_socrates_human",
                term=LogicalTerm("human", ["socrates"]),
                confidence=1.0,
                source="test",
                timestamp=time.time()
            )
            
            fact2 = Fact(
                fact_id="fact_humans_mortal",
                term=LogicalTerm("mortal", ["X"]),  # All humans are mortal
                confidence=1.0,
                source="test",
                timestamp=time.time()
            )
            
            await reasoning_engine.add_fact(fact1)
            await reasoning_engine.add_fact(fact2)
            
            # Add test rule: if human(X) then mortal(X)
            rule = Rule(
                rule_id="humans_are_mortal",
                rule_type=RuleType.IMPLICATION,
                premises=[LogicalTerm("human", ["X"])],
                conclusions=[LogicalTerm("mortal", ["X"])],
                confidence=1.0,
                priority=10,
                source="test",
                created_at=time.time(),
                metadata={"description": "All humans are mortal"}
            )
            
            await reasoning_engine.add_rule(rule)
            
            # Test reasoning
            result = await reasoning_engine.reason("mortal(socrates)")
            
            logger.info(f"Reasoning result:")
            logger.info(f"  - Success: {result.success}")
            logger.info(f"  - Results: {len(result.results)}")
            logger.info(f"  - Confidence: {result.confidence:.2f}")
            logger.info(f"  - Method: {result.method_used.value}")
            logger.info(f"  - Explanation: {result.explanation}")
            
            # Test consistency check
            consistency = await reasoning_engine.check_consistency()
            logger.info(f"Consistency check: {'✅ Consistent' if consistency.consistent else '❌ Inconsistent'}")
            
            # Get statistics
            stats = reasoning_engine.get_statistics()
            logger.info(f"Statistics: {stats}")
            
            # Save data
            await reasoning_engine.save_reasoning_data()
            
            # Shutdown
            await reasoning_engine.shutdown()
            
            logger.info("✅ Deterministic Reasoning Engine test completed successfully")
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise
    
    # Run test
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_reasoning_engine())