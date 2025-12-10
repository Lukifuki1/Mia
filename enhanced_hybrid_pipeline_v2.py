#!/usr/bin/env python3
"""
🚀 MIA Enterprise AGI - Enhanced Hybrid Pipeline V2.0
Optimizirana in popolna nova verzija hibridnega pipeline-a
"""

import sys
import os
import json
import asyncio
import logging
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union, Callable
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
import hashlib
import uuid
from datetime import datetime
import numpy as np
from collections import defaultdict, deque
import weakref

# Dodaj MIA path
sys.path.insert(0, '.')

class PipelineStage(Enum):
    """Stopnje hibridnega pipeline-a"""
    PREPROCESSING = "preprocessing"
    NEURAL_PROCESSING = "neural_processing"
    SYMBOLIC_REASONING = "symbolic_reasoning"
    KNOWLEDGE_INTEGRATION = "knowledge_integration"
    RESULT_FUSION = "result_fusion"
    POSTPROCESSING = "postprocessing"

class ProcessingMode(Enum):
    """Načini procesiranja"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"
    HYBRID = "hybrid"

class ConfidenceLevel(Enum):
    """Nivoji zaupanja"""
    VERY_LOW = 0.1
    LOW = 0.3
    MEDIUM = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9

@dataclass
class ProcessingContext:
    """Kontekst procesiranja"""
    request_id: str
    timestamp: datetime
    input_data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    stage_results: Dict[PipelineStage, Any] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    processing_time: Dict[str, float] = field(default_factory=dict)
    error_log: List[str] = field(default_factory=list)

@dataclass
class PipelineResult:
    """Rezultat hibridnega pipeline-a"""
    request_id: str
    success: bool
    result: Any
    confidence: float
    processing_time: float
    stage_results: Dict[str, Any]
    metadata: Dict[str, Any]
    error_messages: List[str] = field(default_factory=list)

class NeuralProcessor:
    """Napredni neural processor"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.NeuralProcessor")
        self.model_cache = {}
        self.processing_stats = defaultdict(int)
        
    async def process(self, context: ProcessingContext) -> Tuple[Any, float]:
        """Procesira podatke z neural networks"""
        start_time = time.time()
        
        try:
            # Simulacija neural processing
            input_data = context.input_data
            
            # Feature extraction
            features = self._extract_features(input_data)
            
            # Neural inference
            neural_result = self._neural_inference(features)
            
            # Confidence calculation
            confidence = self._calculate_neural_confidence(neural_result, features)
            
            processing_time = time.time() - start_time
            context.processing_time['neural'] = processing_time
            
            self.processing_stats['neural_processed'] += 1
            self.logger.info(f"Neural processing completed in {processing_time:.3f}s")
            
            return neural_result, confidence
            
        except Exception as e:
            self.logger.error(f"Neural processing failed: {e}")
            context.error_log.append(f"Neural processing error: {e}")
            return None, 0.0
    
    def _extract_features(self, data: Any) -> np.ndarray:
        """Izvleče značilke iz podatkov"""
        if isinstance(data, str):
            # Text feature extraction
            return np.array([len(data), data.count(' '), data.count('.'), 
                           sum(ord(c) for c in data[:100]) / 100])
        elif isinstance(data, dict):
            # Dict feature extraction
            return np.array([len(data), len(str(data)), 
                           sum(len(str(v)) for v in data.values()) / max(len(data), 1)])
        else:
            # Default features
            return np.array([1.0, 0.5, 0.8, 0.3])
    
    def _neural_inference(self, features: np.ndarray) -> Dict[str, Any]:
        """Izvede neural inference"""
        # Simulacija neural network inference
        weights = np.array([0.3, 0.2, 0.4, 0.1])
        output = np.dot(features, weights)
        
        return {
            'neural_output': float(output),
            'feature_importance': features.tolist(),
            'activation_pattern': (features > np.mean(features)).tolist()
        }
    
    def _calculate_neural_confidence(self, result: Dict[str, Any], features: np.ndarray) -> float:
        """Izračuna zaupanje neural rezultata"""
        # Confidence based on feature consistency and output stability
        feature_variance = np.var(features)
        output_magnitude = abs(result.get('neural_output', 0))
        
        confidence = min(1.0, (1.0 / (1.0 + feature_variance)) * min(1.0, output_magnitude))
        return max(0.1, confidence)

class SymbolicReasoner:
    """Napredni symbolic reasoner"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.SymbolicReasoner")
        self.rule_base = self._initialize_rule_base()
        self.inference_engine = self._initialize_inference_engine()
        
    def _initialize_rule_base(self) -> Dict[str, Any]:
        """Inicializira bazo pravil"""
        return {
            'logical_rules': [
                {'if': 'text_length > 100', 'then': 'complex_text', 'confidence': 0.8},
                {'if': 'contains_numbers', 'then': 'data_content', 'confidence': 0.7},
                {'if': 'contains_questions', 'then': 'query_intent', 'confidence': 0.9}
            ],
            'inference_patterns': [
                {'pattern': 'A → B, B → C', 'conclusion': 'A → C', 'type': 'transitivity'},
                {'pattern': 'A ∧ B', 'conclusion': 'A', 'type': 'conjunction_elimination'},
                {'pattern': 'A ∨ B, ¬A', 'conclusion': 'B', 'type': 'disjunctive_syllogism'}
            ]
        }
    
    def _initialize_inference_engine(self) -> Dict[str, Callable]:
        """Inicializira inference engine"""
        return {
            'forward_chaining': self._forward_chaining,
            'backward_chaining': self._backward_chaining,
            'resolution': self._resolution_inference
        }
    
    async def process(self, context: ProcessingContext) -> Tuple[Any, float]:
        """Procesira podatke s symbolic reasoning"""
        start_time = time.time()
        
        try:
            input_data = context.input_data
            
            # Fact extraction
            facts = self._extract_facts(input_data)
            
            # Rule application
            inferred_facts = self._apply_rules(facts)
            
            # Logical inference
            conclusions = self._perform_inference(facts, inferred_facts)
            
            # Confidence calculation
            confidence = self._calculate_symbolic_confidence(conclusions, facts)
            
            processing_time = time.time() - start_time
            context.processing_time['symbolic'] = processing_time
            
            result = {
                'facts': facts,
                'inferred_facts': inferred_facts,
                'conclusions': conclusions,
                'reasoning_chain': self._build_reasoning_chain(facts, conclusions)
            }
            
            self.logger.info(f"Symbolic reasoning completed in {processing_time:.3f}s")
            return result, confidence
            
        except Exception as e:
            self.logger.error(f"Symbolic reasoning failed: {e}")
            context.error_log.append(f"Symbolic reasoning error: {e}")
            return None, 0.0
    
    def _extract_facts(self, data: Any) -> List[Dict[str, Any]]:
        """Izvleče dejstva iz podatkov"""
        facts = []
        
        if isinstance(data, str):
            facts.append({'type': 'text', 'length': len(data), 'content': data[:100]})
            if '?' in data:
                facts.append({'type': 'question', 'detected': True})
            if any(c.isdigit() for c in data):
                facts.append({'type': 'contains_numbers', 'detected': True})
        elif isinstance(data, dict):
            facts.append({'type': 'structured_data', 'keys': list(data.keys())})
            facts.append({'type': 'data_size', 'value': len(data)})
        
        return facts
    
    def _apply_rules(self, facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aplicira pravila na dejstva"""
        inferred = []
        
        for rule in self.rule_base['logical_rules']:
            if self._evaluate_condition(rule['if'], facts):
                inferred.append({
                    'conclusion': rule['then'],
                    'confidence': rule['confidence'],
                    'rule': rule['if']
                })
        
        return inferred
    
    def _evaluate_condition(self, condition: str, facts: List[Dict[str, Any]]) -> bool:
        """Evalvira pogoj pravila"""
        # Simplified condition evaluation
        if 'text_length > 100' in condition:
            return any(f.get('type') == 'text' and f.get('length', 0) > 100 for f in facts)
        elif 'contains_numbers' in condition:
            return any(f.get('type') == 'contains_numbers' for f in facts)
        elif 'contains_questions' in condition:
            return any(f.get('type') == 'question' for f in facts)
        return False
    
    def _perform_inference(self, facts: List[Dict[str, Any]], inferred: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Izvede logično sklepanje"""
        conclusions = []
        
        # Forward chaining
        forward_results = self._forward_chaining(facts, inferred)
        conclusions.extend(forward_results)
        
        # Pattern matching
        pattern_results = self._pattern_matching(facts, inferred)
        conclusions.extend(pattern_results)
        
        return conclusions
    
    def _forward_chaining(self, facts: List[Dict[str, Any]], inferred: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Forward chaining inference"""
        conclusions = []
        
        # Combine facts and inferred facts
        all_facts = facts + inferred
        
        # Apply inference patterns
        for pattern in self.rule_base['inference_patterns']:
            if pattern['type'] == 'transitivity':
                # Look for A → B, B → C patterns
                conclusions.append({
                    'type': 'transitive_conclusion',
                    'pattern': pattern['pattern'],
                    'confidence': 0.7
                })
        
        return conclusions
    
    def _backward_chaining(self, goal: str, facts: List[Dict[str, Any]]) -> bool:
        """Backward chaining inference"""
        # Simplified backward chaining
        return any(f.get('conclusion') == goal for f in facts)
    
    def _resolution_inference(self, clauses: List[str]) -> List[str]:
        """Resolution-based inference"""
        # Simplified resolution
        return ['resolved_conclusion']
    
    def _pattern_matching(self, facts: List[Dict[str, Any]], inferred: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Pattern matching inference"""
        patterns = []
        
        # Detect common patterns
        if any(f.get('type') == 'question' for f in facts):
            patterns.append({
                'type': 'query_pattern',
                'confidence': 0.8,
                'description': 'Question detected - query intent'
            })
        
        return patterns
    
    def _build_reasoning_chain(self, facts: List[Dict[str, Any]], conclusions: List[Dict[str, Any]]) -> List[str]:
        """Zgradi verigo sklepanja"""
        chain = []
        chain.append(f"Starting with {len(facts)} facts")
        
        for conclusion in conclusions:
            chain.append(f"Concluded: {conclusion.get('type', 'unknown')} with confidence {conclusion.get('confidence', 0)}")
        
        return chain
    
    def _calculate_symbolic_confidence(self, conclusions: List[Dict[str, Any]], facts: List[Dict[str, Any]]) -> float:
        """Izračuna zaupanje symbolic rezultata"""
        if not conclusions:
            return 0.1
        
        # Average confidence of conclusions weighted by fact support
        total_confidence = sum(c.get('confidence', 0.5) for c in conclusions)
        fact_support = min(1.0, len(facts) / 5.0)  # More facts = higher confidence
        
        return min(0.95, (total_confidence / len(conclusions)) * fact_support)

class KnowledgeIntegrator:
    """Integrator znanja iz različnih virov"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.KnowledgeIntegrator")
        self.knowledge_base = {}
        self.integration_patterns = self._initialize_integration_patterns()
        
    def _initialize_integration_patterns(self) -> Dict[str, Any]:
        """Inicializira vzorce integracije"""
        return {
            'neural_symbolic_fusion': {
                'weight_neural': 0.6,
                'weight_symbolic': 0.4,
                'fusion_method': 'weighted_average'
            },
            'confidence_aggregation': {
                'method': 'harmonic_mean',
                'threshold': 0.3
            },
            'conflict_resolution': {
                'strategy': 'highest_confidence',
                'fallback': 'consensus'
            }
        }
    
    async def integrate(self, neural_result: Any, symbolic_result: Any, 
                       neural_confidence: float, symbolic_confidence: float,
                       context: ProcessingContext) -> Tuple[Any, float]:
        """Integrira neural in symbolic rezultate"""
        start_time = time.time()
        
        try:
            # Fusion strategy selection
            fusion_method = self._select_fusion_method(neural_confidence, symbolic_confidence)
            
            # Result fusion
            integrated_result = self._fuse_results(neural_result, symbolic_result, 
                                                 neural_confidence, symbolic_confidence, 
                                                 fusion_method)
            
            # Confidence aggregation
            integrated_confidence = self._aggregate_confidence(neural_confidence, symbolic_confidence)
            
            # Knowledge base update
            self._update_knowledge_base(integrated_result, integrated_confidence, context)
            
            processing_time = time.time() - start_time
            context.processing_time['integration'] = processing_time
            
            self.logger.info(f"Knowledge integration completed in {processing_time:.3f}s")
            return integrated_result, integrated_confidence
            
        except Exception as e:
            self.logger.error(f"Knowledge integration failed: {e}")
            context.error_log.append(f"Integration error: {e}")
            return None, 0.0
    
    def _select_fusion_method(self, neural_conf: float, symbolic_conf: float) -> str:
        """Izbere metodo fuzije"""
        conf_diff = abs(neural_conf - symbolic_conf)
        
        if conf_diff < 0.2:
            return 'weighted_average'
        elif neural_conf > symbolic_conf:
            return 'neural_dominant'
        else:
            return 'symbolic_dominant'
    
    def _fuse_results(self, neural_result: Any, symbolic_result: Any,
                     neural_conf: float, symbolic_conf: float, method: str) -> Dict[str, Any]:
        """Fuzira rezultate"""
        if method == 'weighted_average':
            total_weight = neural_conf + symbolic_conf
            neural_weight = neural_conf / total_weight if total_weight > 0 else 0.5
            symbolic_weight = symbolic_conf / total_weight if total_weight > 0 else 0.5
            
            return {
                'fusion_method': method,
                'neural_result': neural_result,
                'symbolic_result': symbolic_result,
                'neural_weight': neural_weight,
                'symbolic_weight': symbolic_weight,
                'primary_source': 'neural' if neural_conf > symbolic_conf else 'symbolic',
                'confidence_balance': abs(neural_conf - symbolic_conf)
            }
        
        elif method == 'neural_dominant':
            return {
                'fusion_method': method,
                'primary_result': neural_result,
                'secondary_result': symbolic_result,
                'primary_confidence': neural_conf,
                'secondary_confidence': symbolic_conf
            }
        
        else:  # symbolic_dominant
            return {
                'fusion_method': method,
                'primary_result': symbolic_result,
                'secondary_result': neural_result,
                'primary_confidence': symbolic_conf,
                'secondary_confidence': neural_conf
            }
    
    def _aggregate_confidence(self, neural_conf: float, symbolic_conf: float) -> float:
        """Agregira zaupanje"""
        method = self.integration_patterns['confidence_aggregation']['method']
        
        if method == 'harmonic_mean':
            if neural_conf > 0 and symbolic_conf > 0:
                return 2 * neural_conf * symbolic_conf / (neural_conf + symbolic_conf)
            else:
                return 0.0
        elif method == 'geometric_mean':
            return (neural_conf * symbolic_conf) ** 0.5
        else:  # arithmetic_mean
            return (neural_conf + symbolic_conf) / 2
    
    def _update_knowledge_base(self, result: Any, confidence: float, context: ProcessingContext):
        """Posodobi bazo znanja"""
        key = hashlib.md5(str(context.input_data).encode()).hexdigest()
        
        self.knowledge_base[key] = {
            'result': result,
            'confidence': confidence,
            'timestamp': context.timestamp.isoformat(),
            'request_id': context.request_id
        }

class EnhancedHybridPipeline:
    """Napredni hibridni pipeline V2.0"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger("MIA.EnhancedHybridPipeline")
        self.config = config or self._default_config()
        
        # Initialize components
        self.neural_processor = NeuralProcessor()
        self.symbolic_reasoner = SymbolicReasoner()
        self.knowledge_integrator = KnowledgeIntegrator()
        
        # Pipeline state
        self.active_requests = {}
        self.processing_stats = defaultdict(int)
        self.performance_metrics = defaultdict(list)
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=self.config['max_workers'])
        
        self.logger.info("Enhanced Hybrid Pipeline V2.0 initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Privzeta konfiguracija"""
        return {
            'max_workers': 4,
            'processing_mode': ProcessingMode.ADAPTIVE,
            'timeout': 30.0,
            'enable_caching': True,
            'cache_size': 1000,
            'min_confidence_threshold': 0.1,
            'parallel_threshold': 0.5,
            'enable_monitoring': True
        }
    
    async def process(self, input_data: Any, metadata: Optional[Dict[str, Any]] = None) -> PipelineResult:
        """Glavna procesna funkcija pipeline-a"""
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Create processing context
        context = ProcessingContext(
            request_id=request_id,
            timestamp=datetime.now(),
            input_data=input_data,
            metadata=metadata or {}
        )
        
        self.active_requests[request_id] = context
        
        try:
            self.logger.info(f"Starting pipeline processing for request {request_id}")
            
            # Stage 1: Preprocessing
            await self._preprocessing_stage(context)
            
            # Stage 2: Determine processing mode
            processing_mode = self._determine_processing_mode(context)
            
            # Stage 3: Neural and Symbolic processing
            if processing_mode == ProcessingMode.PARALLEL:
                neural_result, symbolic_result, neural_conf, symbolic_conf = await self._parallel_processing(context)
            else:
                neural_result, symbolic_result, neural_conf, symbolic_conf = await self._sequential_processing(context)
            
            # Stage 4: Knowledge integration
            if neural_result is not None and symbolic_result is not None:
                integrated_result, final_confidence = await self.knowledge_integrator.integrate(
                    neural_result, symbolic_result, neural_conf, symbolic_conf, context
                )
            elif neural_result is not None:
                integrated_result, final_confidence = neural_result, neural_conf
            elif symbolic_result is not None:
                integrated_result, final_confidence = symbolic_result, symbolic_conf
            else:
                integrated_result, final_confidence = None, 0.0
            
            # Stage 5: Postprocessing
            final_result = await self._postprocessing_stage(integrated_result, context)
            
            # Calculate total processing time
            total_time = time.time() - start_time
            
            # Create result
            result = PipelineResult(
                request_id=request_id,
                success=integrated_result is not None,
                result=final_result,
                confidence=final_confidence,
                processing_time=total_time,
                stage_results={
                    'neural': neural_result,
                    'symbolic': symbolic_result,
                    'integrated': integrated_result
                },
                metadata={
                    'processing_mode': processing_mode.value,
                    'stage_times': context.processing_time,
                    'confidence_scores': {
                        'neural': neural_conf,
                        'symbolic': symbolic_conf,
                        'final': final_confidence
                    }
                },
                error_messages=context.error_log
            )
            
            # Update statistics
            self._update_statistics(result)
            
            self.logger.info(f"Pipeline processing completed for {request_id} in {total_time:.3f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Pipeline processing failed for {request_id}: {e}")
            
            return PipelineResult(
                request_id=request_id,
                success=False,
                result=None,
                confidence=0.0,
                processing_time=time.time() - start_time,
                stage_results={},
                metadata={},
                error_messages=[str(e)]
            )
        
        finally:
            # Cleanup
            if request_id in self.active_requests:
                del self.active_requests[request_id]
    
    async def _preprocessing_stage(self, context: ProcessingContext):
        """Preprocessing stopnja"""
        start_time = time.time()
        
        # Input validation
        if context.input_data is None:
            raise ValueError("Input data cannot be None")
        
        # Data normalization
        if isinstance(context.input_data, str):
            context.input_data = context.input_data.strip()
        
        # Metadata enrichment
        context.metadata.update({
            'input_type': type(context.input_data).__name__,
            'input_size': len(str(context.input_data)),
            'preprocessing_timestamp': datetime.now().isoformat()
        })
        
        context.processing_time['preprocessing'] = time.time() - start_time
    
    def _determine_processing_mode(self, context: ProcessingContext) -> ProcessingMode:
        """Določi način procesiranja"""
        config_mode = self.config['processing_mode']
        
        if config_mode == ProcessingMode.ADAPTIVE:
            # Adaptive mode based on input characteristics
            input_size = len(str(context.input_data))
            complexity_score = self._calculate_complexity_score(context.input_data)
            
            if complexity_score > self.config['parallel_threshold'] and input_size > 100:
                return ProcessingMode.PARALLEL
            else:
                return ProcessingMode.SEQUENTIAL
        
        return config_mode
    
    def _calculate_complexity_score(self, data: Any) -> float:
        """Izračuna kompleksnost podatkov"""
        if isinstance(data, str):
            # Text complexity based on length, words, punctuation
            length_score = min(1.0, len(data) / 1000)
            word_count = len(data.split())
            word_score = min(1.0, word_count / 100)
            punct_score = sum(1 for c in data if c in '.,!?;:') / max(len(data), 1)
            
            return (length_score + word_score + punct_score) / 3
        
        elif isinstance(data, dict):
            # Dict complexity based on depth and size
            size_score = min(1.0, len(data) / 50)
            depth_score = min(1.0, self._dict_depth(data) / 5)
            
            return (size_score + depth_score) / 2
        
        return 0.5  # Default complexity
    
    def _dict_depth(self, d: dict, depth: int = 0) -> int:
        """Izračuna globino slovarja"""
        if not isinstance(d, dict):
            return depth
        
        return max([self._dict_depth(v, depth + 1) for v in d.values()] + [depth])
    
    async def _parallel_processing(self, context: ProcessingContext) -> Tuple[Any, Any, float, float]:
        """Paralelno procesiranje"""
        self.logger.info("Using parallel processing mode")
        
        # Create tasks for parallel execution
        neural_task = asyncio.create_task(self.neural_processor.process(context))
        symbolic_task = asyncio.create_task(self.symbolic_reasoner.process(context))
        
        # Wait for both tasks to complete
        neural_result, neural_conf = await neural_task
        symbolic_result, symbolic_conf = await symbolic_task
        
        return neural_result, symbolic_result, neural_conf, symbolic_conf
    
    async def _sequential_processing(self, context: ProcessingContext) -> Tuple[Any, Any, float, float]:
        """Sekvencialno procesiranje"""
        self.logger.info("Using sequential processing mode")
        
        # Process neural first
        neural_result, neural_conf = await self.neural_processor.process(context)
        
        # Then symbolic
        symbolic_result, symbolic_conf = await self.symbolic_reasoner.process(context)
        
        return neural_result, symbolic_result, neural_conf, symbolic_conf
    
    async def _postprocessing_stage(self, result: Any, context: ProcessingContext) -> Any:
        """Postprocessing stopnja"""
        start_time = time.time()
        
        if result is None:
            return None
        
        # Result formatting
        formatted_result = {
            'pipeline_result': result,
            'request_id': context.request_id,
            'timestamp': datetime.now().isoformat(),
            'processing_summary': {
                'total_stages': len(context.processing_time),
                'stage_times': context.processing_time,
                'total_time': sum(context.processing_time.values())
            }
        }
        
        context.processing_time['postprocessing'] = time.time() - start_time
        return formatted_result
    
    def _update_statistics(self, result: PipelineResult):
        """Posodobi statistike"""
        self.processing_stats['total_requests'] += 1
        
        if result.success:
            self.processing_stats['successful_requests'] += 1
        else:
            self.processing_stats['failed_requests'] += 1
        
        self.performance_metrics['processing_times'].append(result.processing_time)
        self.performance_metrics['confidence_scores'].append(result.confidence)
        
        # Keep only last 1000 metrics
        for metric_list in self.performance_metrics.values():
            if len(metric_list) > 1000:
                metric_list.pop(0)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Pridobi statistike pipeline-a"""
        stats = dict(self.processing_stats)
        
        if self.performance_metrics['processing_times']:
            stats['average_processing_time'] = np.mean(self.performance_metrics['processing_times'])
            stats['median_processing_time'] = np.median(self.performance_metrics['processing_times'])
        
        if self.performance_metrics['confidence_scores']:
            stats['average_confidence'] = np.mean(self.performance_metrics['confidence_scores'])
            stats['median_confidence'] = np.median(self.performance_metrics['confidence_scores'])
        
        stats['active_requests'] = len(self.active_requests)
        
        return stats
    
    def shutdown(self):
        """Ugasni pipeline"""
        self.logger.info("Shutting down Enhanced Hybrid Pipeline")
        self.executor.shutdown(wait=True)

async def main():
    """Test funkcija za pipeline"""
    print("🚀 === ENHANCED HYBRID PIPELINE V2.0 TEST ===")
    print()
    
    # Ustvari pipeline
    pipeline = EnhancedHybridPipeline()
    
    # Test podatki
    test_cases = [
        "What is the meaning of artificial intelligence?",
        {"query": "complex analysis", "parameters": {"depth": 5, "mode": "analytical"}},
        "Simple text for processing",
        {"data": [1, 2, 3, 4, 5], "operation": "statistical_analysis"}
    ]
    
    print("🧪 Testiranje različnih vhodnih podatkov:")
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\n   📝 Test {i}: {type(test_data).__name__}")
        
        # Procesiranje
        result = await pipeline.process(test_data)
        
        print(f"      ✅ Uspeh: {result.success}")
        print(f"      🎯 Zaupanje: {result.confidence:.3f}")
        print(f"      ⏱️ Čas: {result.processing_time:.3f}s")
        
        if result.error_messages:
            print(f"      ⚠️ Napake: {len(result.error_messages)}")
    
    # Statistike
    print(f"\n📊 Statistike pipeline-a:")
    stats = pipeline.get_statistics()
    
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    # Ugasni pipeline
    pipeline.shutdown()
    
    print("\n✅ ENHANCED HYBRID PIPELINE V2.0 TEST KONČAN!")

if __name__ == "__main__":
    asyncio.run(main())