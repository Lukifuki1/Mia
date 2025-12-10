#!/usr/bin/env python3
"""
Hybrid Pipeline - Neural-Symbolic Integration za hibridni MIA sistem
===================================================================

PRODUKCIJSKA IMPLEMENTACIJA hibridnega pipeline-a, ki združuje:
- Neural processing (Semantic Layer)
- Symbolic reasoning (Deterministic Reasoning)
- Knowledge management (Knowledge Bank)
- Orchestration in coordination

KLJUČNE FUNKCIONALNOSTI:
- Neural-symbolic integration
- Multi-stage processing pipeline
- Async orchestration
- Error handling in fallback strategies
- Performance optimization
- Result fusion in confidence aggregation
- Integration z obstoječimi MIA komponentami

ARHITEKTURA:
- Backward compatible z obstoječim MIA sistemom
- Orchestracija vseh hibridnih komponent
- Flexible pipeline configuration
- Monitoring in diagnostics
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

# Import existing MIA components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

try:
    from mia.knowledge.hybrid.knowledge_bank_core import HybridKnowledgeBank, create_hybrid_knowledge_bank
    from mia.knowledge.hybrid.semantic_layer import SemanticLayer, create_semantic_layer
    from mia.knowledge.hybrid.deterministic_reasoning import DeterministicReasoningEngine, create_reasoning_engine
    HYBRID_COMPONENTS_AVAILABLE = True
except ImportError:
    HYBRID_COMPONENTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class ProcessingStage(Enum):
    """Stopnje procesiranja"""
    INPUT_PARSING = "input_parsing"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    REASONING = "reasoning"
    RESULT_FUSION = "result_fusion"
    OUTPUT_GENERATION = "output_generation"

class PipelineMode(Enum):
    """Načini delovanja pipeline-a"""
    NEURAL_ONLY = "neural_only"
    SYMBOLIC_ONLY = "symbolic_only"
    HYBRID_SEQUENTIAL = "hybrid_sequential"
    HYBRID_PARALLEL = "hybrid_parallel"
    ADAPTIVE = "adaptive"

@dataclass
class ProcessingContext:
    """Kontekst procesiranja"""
    request_id: str
    user_input: str
    processing_mode: PipelineMode
    confidence_threshold: float
    max_processing_time: float
    metadata: Dict[str, Any]
    created_at: float

@dataclass
class StageResult:
    """Rezultat posamezne stopnje"""
    stage: ProcessingStage
    success: bool
    results: Dict[str, Any]
    confidence: float
    processing_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class PipelineResult:
    """Končni rezultat pipeline-a"""
    request_id: str
    success: bool
    final_answer: str
    confidence: float
    stage_results: List[StageResult]
    processing_path: List[ProcessingStage]
    total_processing_time: float
    mode_used: PipelineMode
    explanation: str
    metadata: Dict[str, Any]

@dataclass
class PipelineStats:
    """Statistike pipeline-a"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_processing_time: float
    stage_performance: Dict[str, Dict[str, float]]
    mode_usage: Dict[str, int]
    error_rates: Dict[str, float]

class HybridPipeline:
    """
    Hibridni pipeline za integracijo neural in symbolic procesiranja.
    
    Omogoča:
    - Multi-stage processing z različnimi komponentami
    - Neural-symbolic integration
    - Adaptive mode selection
    - Result fusion in confidence aggregation
    - Error handling in fallback strategies
    - Performance monitoring
    
    PRODUKCIJSKE FUNKCIONALNOSTI:
    ✅ Neural-symbolic integration
    ✅ Multi-stage async processing
    ✅ Adaptive mode selection
    ✅ Result fusion z confidence aggregation
    ✅ Comprehensive error handling
    ✅ Performance optimization
    ✅ Statistics in monitoring
    ✅ Integration z vsemi hibridnimi komponentami
    """
    
    def __init__(self,
                 knowledge_bank: Optional[HybridKnowledgeBank] = None,
                 semantic_layer: Optional[SemanticLayer] = None,
                 reasoning_engine: Optional[DeterministicReasoningEngine] = None,
                 data_dir: str = "data/hybrid_pipeline",
                 default_mode: PipelineMode = PipelineMode.ADAPTIVE):
        """
        Inicializiraj hibridni pipeline.
        
        Args:
            knowledge_bank: Knowledge Bank komponenta
            semantic_layer: Semantic Layer komponenta
            reasoning_engine: Deterministic Reasoning komponenta
            data_dir: Direktorij za podatke
            default_mode: Privzeti način delovanja
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Component integration
        self.knowledge_bank = knowledge_bank
        self.semantic_layer = semantic_layer
        self.reasoning_engine = reasoning_engine
        
        # Check component availability
        self.kb_available = knowledge_bank is not None
        self.semantic_available = semantic_layer is not None
        self.reasoning_available = reasoning_engine is not None
        
        # Pipeline configuration
        self.default_mode = default_mode
        self.confidence_threshold = 0.7
        self.max_processing_time = 60.0  # seconds
        self.enable_fallback = True
        
        # Performance optimization
        self.executor = ThreadPoolExecutor(max_workers=6)
        self.result_cache: Dict[str, PipelineResult] = {}
        self.cache_size = 500
        
        # Processing history
        self.processing_history: List[PipelineResult] = []
        self.max_history_size = 1000
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'neural_only_requests': 0,
            'symbolic_only_requests': 0,
            'hybrid_requests': 0,
            'adaptive_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_processing_time': 0.0,
            'system_health': 'initializing',
            'start_time': time.time()
        }
        
        # Stage performance tracking
        self.stage_stats = {
            stage.value: {
                'total_runs': 0,
                'successful_runs': 0,
                'failed_runs': 0,
                'total_time': 0.0,
                'average_time': 0.0
            } for stage in ProcessingStage
        }
        
        # Load existing data
        self._load_pipeline_data()
        
        # Update statistics
        self._update_statistics()
        
        logger.info("✅ Hybrid Pipeline inicializiran")
        logger.info(f"   - Knowledge Bank: {'✅' if self.kb_available else '❌'}")
        logger.info(f"   - Semantic Layer: {'✅' if self.semantic_available else '❌'}")
        logger.info(f"   - Reasoning Engine: {'✅' if self.reasoning_available else '❌'}")
        logger.info(f"   - Default Mode: {self.default_mode.value}")
        logger.info(f"   - Cache Size: {len(self.result_cache)}")
        
    def _update_statistics(self):
        """Posodobi statistike sistema"""
        try:
            # Update stage averages
            for stage_name, stats in self.stage_stats.items():
                if stats['total_runs'] > 0:
                    stats['average_time'] = stats['total_time'] / stats['total_runs']
                    
            # Update overall average
            if self.stats['total_requests'] > 0:
                total_time = sum(result.total_processing_time for result in self.processing_history[-100:])
                self.stats['average_processing_time'] = total_time / min(len(self.processing_history), 100)
                
            self.stats['system_health'] = 'healthy'
            
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
            self.stats['system_health'] = 'error'
            
    async def process(self, 
                     user_input: str,
                     mode: Optional[PipelineMode] = None,
                     confidence_threshold: Optional[float] = None,
                     max_processing_time: Optional[float] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> PipelineResult:
        """
        Glavna metoda za procesiranje zahtev.
        
        Args:
            user_input: Uporabniški vnos
            mode: Način procesiranja (če ni podan, uporabi default)
            confidence_threshold: Prag zaupanja
            max_processing_time: Maksimalni čas procesiranja
            metadata: Dodatni metadata
            
        Returns:
            PipelineResult
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            self.stats['total_requests'] += 1
            
            # Create processing context
            context = ProcessingContext(
                request_id=request_id,
                user_input=user_input,
                processing_mode=mode or self.default_mode,
                confidence_threshold=confidence_threshold or self.confidence_threshold,
                max_processing_time=max_processing_time or self.max_processing_time,
                metadata=metadata or {},
                created_at=start_time
            )
            
            # Check cache
            cache_key = self._generate_cache_key(context)
            if cache_key in self.result_cache:
                self.stats['cache_hits'] += 1
                cached_result = self.result_cache[cache_key]
                logger.debug(f"Cache hit for request: {request_id}")
                return cached_result
                
            self.stats['cache_misses'] += 1
            
            # Select processing mode
            if context.processing_mode == PipelineMode.ADAPTIVE:
                context.processing_mode = await self._select_adaptive_mode(context)
                self.stats['adaptive_requests'] += 1
            
            # Execute pipeline based on mode
            if context.processing_mode == PipelineMode.NEURAL_ONLY:
                result = await self._process_neural_only(context)
                self.stats['neural_only_requests'] += 1
                
            elif context.processing_mode == PipelineMode.SYMBOLIC_ONLY:
                result = await self._process_symbolic_only(context)
                self.stats['symbolic_only_requests'] += 1
                
            elif context.processing_mode == PipelineMode.HYBRID_SEQUENTIAL:
                result = await self._process_hybrid_sequential(context)
                self.stats['hybrid_requests'] += 1
                
            elif context.processing_mode == PipelineMode.HYBRID_PARALLEL:
                result = await self._process_hybrid_parallel(context)
                self.stats['hybrid_requests'] += 1
                
            else:
                # Fallback to sequential hybrid
                result = await self._process_hybrid_sequential(context)
                self.stats['hybrid_requests'] += 1
                
            # Update statistics
            if result.success:
                self.stats['successful_requests'] += 1
            else:
                self.stats['failed_requests'] += 1
                
            # Cache result
            if len(self.result_cache) < self.cache_size:
                self.result_cache[cache_key] = result
            elif len(self.result_cache) >= self.cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self.result_cache))
                del self.result_cache[oldest_key]
                self.result_cache[cache_key] = result
                
            # Add to history
            self.processing_history.append(result)
            if len(self.processing_history) > self.max_history_size:
                self.processing_history = self.processing_history[-self.max_history_size:]
                
            # Update statistics
            self._update_statistics()
            
            logger.info(f"Pipeline processing completed: {request_id} "
                       f"({'✅ Success' if result.success else '❌ Failed'}) "
                       f"in {result.total_processing_time:.3f}s")
                       
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in pipeline processing: {e}")
            
            self.stats['failed_requests'] += 1
            
            return PipelineResult(
                request_id=request_id,
                success=False,
                final_answer=f"Error during processing: {e}",
                confidence=0.0,
                stage_results=[],
                processing_path=[],
                total_processing_time=processing_time,
                mode_used=mode or self.default_mode,
                explanation=f"Pipeline error: {e}",
                metadata={"error": str(e)}
            )
            
    async def _select_adaptive_mode(self, context: ProcessingContext) -> PipelineMode:
        """Izberi optimalni način procesiranja na podlagi konteksta"""
        try:
            # Simple heuristics for mode selection
            input_length = len(context.user_input.split())
            
            # Check component availability
            if not self.semantic_available and not self.reasoning_available:
                return PipelineMode.NEURAL_ONLY if self.semantic_available else PipelineMode.SYMBOLIC_ONLY
                
            # For short, simple queries - try neural first
            if input_length <= 10 and self.semantic_available:
                return PipelineMode.NEURAL_ONLY
                
            # For complex logical queries - use symbolic
            logical_keywords = ['if', 'then', 'because', 'therefore', 'implies', 'all', 'some', 'every']
            if any(keyword in context.user_input.lower() for keyword in logical_keywords):
                if self.reasoning_available:
                    return PipelineMode.SYMBOLIC_ONLY
                    
            # For medium complexity - use hybrid sequential
            if input_length <= 50:
                return PipelineMode.HYBRID_SEQUENTIAL
                
            # For complex queries - use hybrid parallel
            return PipelineMode.HYBRID_PARALLEL
            
        except Exception as e:
            logger.error(f"Error selecting adaptive mode: {e}")
            return PipelineMode.HYBRID_SEQUENTIAL
            
    async def _process_neural_only(self, context: ProcessingContext) -> PipelineResult:
        """Procesiranje samo z neural komponentami"""
        start_time = time.time()
        stage_results = []
        processing_path = [ProcessingStage.SEMANTIC_ANALYSIS]
        
        try:
            if not self.semantic_available:
                return PipelineResult(
                    request_id=context.request_id,
                    success=False,
                    final_answer="Semantic layer not available",
                    confidence=0.0,
                    stage_results=stage_results,
                    processing_path=processing_path,
                    total_processing_time=time.time() - start_time,
                    mode_used=PipelineMode.NEURAL_ONLY,
                    explanation="Semantic layer component not available",
                    metadata={"error": "semantic_layer_unavailable"}
                )
                
            # Stage 1: Semantic Analysis
            semantic_result = await self._run_semantic_analysis(context)
            stage_results.append(semantic_result)
            
            if not semantic_result.success:
                return PipelineResult(
                    request_id=context.request_id,
                    success=False,
                    final_answer="Semantic analysis failed",
                    confidence=0.0,
                    stage_results=stage_results,
                    processing_path=processing_path,
                    total_processing_time=time.time() - start_time,
                    mode_used=PipelineMode.NEURAL_ONLY,
                    explanation="Semantic analysis stage failed",
                    metadata={"stage_failure": "semantic_analysis"}
                )
                
            # Generate final answer from semantic results
            final_answer = self._generate_neural_answer(semantic_result.results)
            confidence = semantic_result.confidence
            
            return PipelineResult(
                request_id=context.request_id,
                success=True,
                final_answer=final_answer,
                confidence=confidence,
                stage_results=stage_results,
                processing_path=processing_path,
                total_processing_time=time.time() - start_time,
                mode_used=PipelineMode.NEURAL_ONLY,
                explanation=f"Neural-only processing with confidence {confidence:.2f}",
                metadata={"semantic_results": semantic_result.results}
            )
            
        except Exception as e:
            logger.error(f"Error in neural-only processing: {e}")
            return PipelineResult(
                request_id=context.request_id,
                success=False,
                final_answer=f"Neural processing error: {e}",
                confidence=0.0,
                stage_results=stage_results,
                processing_path=processing_path,
                total_processing_time=time.time() - start_time,
                mode_used=PipelineMode.NEURAL_ONLY,
                explanation=f"Error in neural processing: {e}",
                metadata={"error": str(e)}
            )
            
    async def _process_symbolic_only(self, context: ProcessingContext) -> PipelineResult:
        """Procesiranje samo s symbolic komponentami"""
        start_time = time.time()
        stage_results = []
        processing_path = [ProcessingStage.REASONING]
        
        try:
            if not self.reasoning_available:
                return PipelineResult(
                    request_id=context.request_id,
                    success=False,
                    final_answer="Reasoning engine not available",
                    confidence=0.0,
                    stage_results=stage_results,
                    processing_path=processing_path,
                    total_processing_time=time.time() - start_time,
                    mode_used=PipelineMode.SYMBOLIC_ONLY,
                    explanation="Reasoning engine component not available",
                    metadata={"error": "reasoning_engine_unavailable"}
                )
                
            # Stage 1: Reasoning
            reasoning_result = await self._run_reasoning(context)
            stage_results.append(reasoning_result)
            
            if not reasoning_result.success:
                return PipelineResult(
                    request_id=context.request_id,
                    success=False,
                    final_answer="Reasoning failed",
                    confidence=0.0,
                    stage_results=stage_results,
                    processing_path=processing_path,
                    total_processing_time=time.time() - start_time,
                    mode_used=PipelineMode.SYMBOLIC_ONLY,
                    explanation="Reasoning stage failed",
                    metadata={"stage_failure": "reasoning"}
                )
                
            # Generate final answer from reasoning results
            final_answer = self._generate_symbolic_answer(reasoning_result.results)
            confidence = reasoning_result.confidence
            
            return PipelineResult(
                request_id=context.request_id,
                success=True,
                final_answer=final_answer,
                confidence=confidence,
                stage_results=stage_results,
                processing_path=processing_path,
                total_processing_time=time.time() - start_time,
                mode_used=PipelineMode.SYMBOLIC_ONLY,
                explanation=f"Symbolic-only processing with confidence {confidence:.2f}",
                metadata={"reasoning_results": reasoning_result.results}
            )
            
        except Exception as e:
            logger.error(f"Error in symbolic-only processing: {e}")
            return PipelineResult(
                request_id=context.request_id,
                success=False,
                final_answer=f"Symbolic processing error: {e}",
                confidence=0.0,
                stage_results=stage_results,
                processing_path=processing_path,
                total_processing_time=time.time() - start_time,
                mode_used=PipelineMode.SYMBOLIC_ONLY,
                explanation=f"Error in symbolic processing: {e}",
                metadata={"error": str(e)}
            )
            
    async def _process_hybrid_sequential(self, context: ProcessingContext) -> PipelineResult:
        """Hibridno procesiranje - zaporedno"""
        start_time = time.time()
        stage_results = []
        processing_path = []
        
        try:
            # Stage 1: Input Parsing
            processing_path.append(ProcessingStage.INPUT_PARSING)
            parsing_result = await self._run_input_parsing(context)
            stage_results.append(parsing_result)
            
            # Stage 2: Semantic Analysis
            if self.semantic_available:
                processing_path.append(ProcessingStage.SEMANTIC_ANALYSIS)
                semantic_result = await self._run_semantic_analysis(context)
                stage_results.append(semantic_result)
            else:
                semantic_result = None
                
            # Stage 3: Knowledge Retrieval
            if self.kb_available:
                processing_path.append(ProcessingStage.KNOWLEDGE_RETRIEVAL)
                knowledge_result = await self._run_knowledge_retrieval(context, semantic_result)
                stage_results.append(knowledge_result)
            else:
                knowledge_result = None
                
            # Stage 4: Reasoning
            if self.reasoning_available:
                processing_path.append(ProcessingStage.REASONING)
                reasoning_result = await self._run_reasoning(context, semantic_result, knowledge_result)
                stage_results.append(reasoning_result)
            else:
                reasoning_result = None
                
            # Stage 5: Result Fusion
            processing_path.append(ProcessingStage.RESULT_FUSION)
            fusion_result = await self._run_result_fusion(context, stage_results)
            stage_results.append(fusion_result)
            
            # Stage 6: Output Generation
            processing_path.append(ProcessingStage.OUTPUT_GENERATION)
            output_result = await self._run_output_generation(context, fusion_result)
            stage_results.append(output_result)
            
            # Determine overall success
            success = fusion_result.success and output_result.success
            final_answer = output_result.results.get('final_answer', 'No answer generated')
            confidence = fusion_result.confidence
            
            explanation = self._generate_hybrid_explanation(stage_results, processing_path)
            
            return PipelineResult(
                request_id=context.request_id,
                success=success,
                final_answer=final_answer,
                confidence=confidence,
                stage_results=stage_results,
                processing_path=processing_path,
                total_processing_time=time.time() - start_time,
                mode_used=PipelineMode.HYBRID_SEQUENTIAL,
                explanation=explanation,
                metadata={
                    "stages_completed": len(stage_results),
                    "successful_stages": sum(1 for r in stage_results if r.success)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in hybrid sequential processing: {e}")
            return PipelineResult(
                request_id=context.request_id,
                success=False,
                final_answer=f"Hybrid processing error: {e}",
                confidence=0.0,
                stage_results=stage_results,
                processing_path=processing_path,
                total_processing_time=time.time() - start_time,
                mode_used=PipelineMode.HYBRID_SEQUENTIAL,
                explanation=f"Error in hybrid processing: {e}",
                metadata={"error": str(e)}
            )
            
    async def _process_hybrid_parallel(self, context: ProcessingContext) -> PipelineResult:
        """Hibridno procesiranje - vzporedno"""
        start_time = time.time()
        stage_results = []
        processing_path = []
        
        try:
            # Stage 1: Input Parsing (sequential)
            processing_path.append(ProcessingStage.INPUT_PARSING)
            parsing_result = await self._run_input_parsing(context)
            stage_results.append(parsing_result)
            
            # Parallel stages: Semantic Analysis, Knowledge Retrieval, Reasoning
            parallel_tasks = []
            
            if self.semantic_available:
                processing_path.append(ProcessingStage.SEMANTIC_ANALYSIS)
                parallel_tasks.append(self._run_semantic_analysis(context))
                
            if self.kb_available:
                processing_path.append(ProcessingStage.KNOWLEDGE_RETRIEVAL)
                parallel_tasks.append(self._run_knowledge_retrieval(context, None))
                
            if self.reasoning_available:
                processing_path.append(ProcessingStage.REASONING)
                parallel_tasks.append(self._run_reasoning(context, None, None))
                
            # Execute parallel tasks
            if parallel_tasks:
                parallel_results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
                
                for result in parallel_results:
                    if isinstance(result, Exception):
                        logger.error(f"Parallel task failed: {result}")
                        # Create error result
                        error_result = StageResult(
                            stage=ProcessingStage.SEMANTIC_ANALYSIS,  # Default
                            success=False,
                            results={},
                            confidence=0.0,
                            processing_time=0.0,
                            error_message=str(result)
                        )
                        stage_results.append(error_result)
                    else:
                        stage_results.append(result)
                        
            # Stage: Result Fusion (sequential)
            processing_path.append(ProcessingStage.RESULT_FUSION)
            fusion_result = await self._run_result_fusion(context, stage_results)
            stage_results.append(fusion_result)
            
            # Stage: Output Generation (sequential)
            processing_path.append(ProcessingStage.OUTPUT_GENERATION)
            output_result = await self._run_output_generation(context, fusion_result)
            stage_results.append(output_result)
            
            # Determine overall success
            success = fusion_result.success and output_result.success
            final_answer = output_result.results.get('final_answer', 'No answer generated')
            confidence = fusion_result.confidence
            
            explanation = self._generate_hybrid_explanation(stage_results, processing_path)
            
            return PipelineResult(
                request_id=context.request_id,
                success=success,
                final_answer=final_answer,
                confidence=confidence,
                stage_results=stage_results,
                processing_path=processing_path,
                total_processing_time=time.time() - start_time,
                mode_used=PipelineMode.HYBRID_PARALLEL,
                explanation=explanation,
                metadata={
                    "stages_completed": len(stage_results),
                    "successful_stages": sum(1 for r in stage_results if r.success),
                    "parallel_execution": True
                }
            )
            
        except Exception as e:
            logger.error(f"Error in hybrid parallel processing: {e}")
            return PipelineResult(
                request_id=context.request_id,
                success=False,
                final_answer=f"Hybrid parallel processing error: {e}",
                confidence=0.0,
                stage_results=stage_results,
                processing_path=processing_path,
                total_processing_time=time.time() - start_time,
                mode_used=PipelineMode.HYBRID_PARALLEL,
                explanation=f"Error in hybrid parallel processing: {e}",
                metadata={"error": str(e)}
            )
            
    async def _run_input_parsing(self, context: ProcessingContext) -> StageResult:
        """Izvedi input parsing stopnjo"""
        start_time = time.time()
        stage = ProcessingStage.INPUT_PARSING
        
        try:
            self.stage_stats[stage.value]['total_runs'] += 1
            
            # Simple input parsing
            parsed_input = {
                'original_text': context.user_input,
                'word_count': len(context.user_input.split()),
                'char_count': len(context.user_input),
                'sentences': context.user_input.split('.'),
                'is_question': context.user_input.strip().endswith('?'),
                'contains_keywords': self._extract_keywords(context.user_input)
            }
            
            processing_time = time.time() - start_time
            
            result = StageResult(
                stage=stage,
                success=True,
                results=parsed_input,
                confidence=1.0,
                processing_time=processing_time,
                metadata={'parsing_method': 'basic'}
            )
            
            self.stage_stats[stage.value]['successful_runs'] += 1
            self.stage_stats[stage.value]['total_time'] += processing_time
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in input parsing: {e}")
            
            self.stage_stats[stage.value]['failed_runs'] += 1
            self.stage_stats[stage.value]['total_time'] += processing_time
            
            return StageResult(
                stage=stage,
                success=False,
                results={},
                confidence=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )
            
    async def _run_semantic_analysis(self, context: ProcessingContext) -> StageResult:
        """Izvedi semantic analysis stopnjo"""
        start_time = time.time()
        stage = ProcessingStage.SEMANTIC_ANALYSIS
        
        try:
            self.stage_stats[stage.value]['total_runs'] += 1
            
            if not self.semantic_available:
                raise RuntimeError("Semantic layer not available")
                
            # Run semantic analysis
            parse_result = await self.semantic_layer.parse_natural_language(
                text=context.user_input,
                extract_entities=True,
                extract_relations=True,
                link_to_kb=self.kb_available
            )
            
            # Find similar concepts
            similarity_result = await self.semantic_layer.find_similar_concepts(
                query=context.user_input,
                limit=5,
                threshold=0.5
            )
            
            processing_time = time.time() - start_time
            
            results = {
                'parse_result': asdict(parse_result),
                'similarity_result': asdict(similarity_result),
                'entities_count': len(parse_result.entities),
                'relations_count': len(parse_result.relations),
                'concepts_count': len(parse_result.concepts)
            }
            
            result = StageResult(
                stage=stage,
                success=True,
                results=results,
                confidence=parse_result.confidence,
                processing_time=processing_time,
                metadata={'semantic_method': 'neural_nlp'}
            )
            
            self.stage_stats[stage.value]['successful_runs'] += 1
            self.stage_stats[stage.value]['total_time'] += processing_time
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in semantic analysis: {e}")
            
            self.stage_stats[stage.value]['failed_runs'] += 1
            self.stage_stats[stage.value]['total_time'] += processing_time
            
            return StageResult(
                stage=stage,
                success=False,
                results={},
                confidence=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )
            
    async def _run_knowledge_retrieval(self, context: ProcessingContext, 
                                     semantic_result: Optional[StageResult] = None) -> StageResult:
        """Izvedi knowledge retrieval stopnjo"""
        start_time = time.time()
        stage = ProcessingStage.KNOWLEDGE_RETRIEVAL
        
        try:
            self.stage_stats[stage.value]['total_runs'] += 1
            
            if not self.kb_available:
                raise RuntimeError("Knowledge bank not available")
                
            # Extract concepts for querying
            query_concepts = []
            if semantic_result and semantic_result.success:
                parse_result = semantic_result.results.get('parse_result', {})
                entities = parse_result.get('entities', [])
                query_concepts = [entity.get('text', '') for entity in entities]
            else:
                # Fallback: use keywords from input
                query_concepts = self._extract_keywords(context.user_input)
                
            # Query knowledge bank
            kb_results = []
            for concept in query_concepts[:5]:  # Limit to top 5 concepts
                if concept:
                    query = f"""
                    SELECT ?subject ?predicate ?object WHERE {{
                        ?subject ?predicate ?object .
                        FILTER(CONTAINS(LCASE(STR(?subject)), LCASE("{concept}")) ||
                               CONTAINS(LCASE(STR(?object)), LCASE("{concept}")))
                    }}
                    LIMIT 10
                    """
                    
                    query_result = await self.knowledge_bank.query_sparql(query)
                    if query_result.success:
                        kb_results.extend(query_result.results)
                        
            # Get concept hierarchy for main concepts
            hierarchies = []
            for concept in query_concepts[:3]:
                concept_uri = f"http://mia.ai/ontology#{concept}"
                hierarchy = await self.knowledge_bank.get_concept_hierarchy(concept_uri)
                if hierarchy:
                    hierarchies.append(hierarchy)
                    
            processing_time = time.time() - start_time
            
            results = {
                'kb_results': kb_results,
                'hierarchies': hierarchies,
                'query_concepts': query_concepts,
                'results_count': len(kb_results)
            }
            
            confidence = min(1.0, len(kb_results) / 10.0)  # Confidence based on results found
            
            result = StageResult(
                stage=stage,
                success=True,
                results=results,
                confidence=confidence,
                processing_time=processing_time,
                metadata={'kb_method': 'sparql_query'}
            )
            
            self.stage_stats[stage.value]['successful_runs'] += 1
            self.stage_stats[stage.value]['total_time'] += processing_time
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in knowledge retrieval: {e}")
            
            self.stage_stats[stage.value]['failed_runs'] += 1
            self.stage_stats[stage.value]['total_time'] += processing_time
            
            return StageResult(
                stage=stage,
                success=False,
                results={},
                confidence=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )
            
    async def _run_reasoning(self, context: ProcessingContext,
                           semantic_result: Optional[StageResult] = None,
                           knowledge_result: Optional[StageResult] = None) -> StageResult:
        """Izvedi reasoning stopnjo"""
        start_time = time.time()
        stage = ProcessingStage.REASONING
        
        try:
            self.stage_stats[stage.value]['total_runs'] += 1
            
            if not self.reasoning_available:
                raise RuntimeError("Reasoning engine not available")
                
            # Prepare query for reasoning
            reasoning_query = context.user_input
            
            # Try to extract logical query from semantic results
            if semantic_result and semantic_result.success:
                parse_result = semantic_result.results.get('parse_result', {})
                relations = parse_result.get('relations', [])
                if relations:
                    # Use first relation as reasoning query
                    first_relation = relations[0]
                    reasoning_query = f"{first_relation.get('predicate', '')}({first_relation.get('subject_concept', '')}, {first_relation.get('object_concept', '')})"
                    
            # Perform reasoning
            reasoning_result = await self.reasoning_engine.reason(
                query=reasoning_query,
                method=self.reasoning_engine.InferenceMethod.HYBRID
            )
            
            # Check consistency if we have knowledge
            consistency_check = None
            if knowledge_result and knowledge_result.success:
                consistency_check = await self.reasoning_engine.check_consistency()
                
            processing_time = time.time() - start_time
            
            results = {
                'reasoning_result': asdict(reasoning_result),
                'consistency_check': asdict(consistency_check) if consistency_check else None,
                'query_used': reasoning_query,
                'inference_steps': len(reasoning_result.inference_steps)
            }
            
            result = StageResult(
                stage=stage,
                success=reasoning_result.success,
                results=results,
                confidence=reasoning_result.confidence,
                processing_time=processing_time,
                metadata={'reasoning_method': reasoning_result.method_used.value}
            )
            
            if reasoning_result.success:
                self.stage_stats[stage.value]['successful_runs'] += 1
            else:
                self.stage_stats[stage.value]['failed_runs'] += 1
                
            self.stage_stats[stage.value]['total_time'] += processing_time
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in reasoning: {e}")
            
            self.stage_stats[stage.value]['failed_runs'] += 1
            self.stage_stats[stage.value]['total_time'] += processing_time
            
            return StageResult(
                stage=stage,
                success=False,
                results={},
                confidence=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )
            
    async def _run_result_fusion(self, context: ProcessingContext, 
                               stage_results: List[StageResult]) -> StageResult:
        """Izvedi result fusion stopnjo"""
        start_time = time.time()
        stage = ProcessingStage.RESULT_FUSION
        
        try:
            self.stage_stats[stage.value]['total_runs'] += 1
            
            # Collect results from different stages
            semantic_results = None
            knowledge_results = None
            reasoning_results = None
            
            for result in stage_results:
                if result.stage == ProcessingStage.SEMANTIC_ANALYSIS and result.success:
                    semantic_results = result.results
                elif result.stage == ProcessingStage.KNOWLEDGE_RETRIEVAL and result.success:
                    knowledge_results = result.results
                elif result.stage == ProcessingStage.REASONING and result.success:
                    reasoning_results = result.results
                    
            # Fusion strategy: weighted combination
            fusion_confidence = 0.0
            fusion_components = []
            
            if semantic_results:
                semantic_confidence = next((r.confidence for r in stage_results 
                                          if r.stage == ProcessingStage.SEMANTIC_ANALYSIS), 0.0)
                fusion_confidence += semantic_confidence * 0.3
                fusion_components.append(('semantic', semantic_confidence))
                
            if knowledge_results:
                knowledge_confidence = next((r.confidence for r in stage_results 
                                           if r.stage == ProcessingStage.KNOWLEDGE_RETRIEVAL), 0.0)
                fusion_confidence += knowledge_confidence * 0.3
                fusion_components.append(('knowledge', knowledge_confidence))
                
            if reasoning_results:
                reasoning_confidence = next((r.confidence for r in stage_results 
                                           if r.stage == ProcessingStage.REASONING), 0.0)
                fusion_confidence += reasoning_confidence * 0.4
                fusion_components.append(('reasoning', reasoning_confidence))
                
            # Normalize confidence
            if fusion_components:
                total_weight = sum(0.3 if comp[0] in ['semantic', 'knowledge'] else 0.4 
                                 for comp in fusion_components)
                if total_weight > 0:
                    fusion_confidence = fusion_confidence / total_weight
                    
            # Create fused results
            fused_results = {
                'semantic_results': semantic_results,
                'knowledge_results': knowledge_results,
                'reasoning_results': reasoning_results,
                'fusion_confidence': fusion_confidence,
                'fusion_components': fusion_components,
                'successful_stages': len([r for r in stage_results if r.success])
            }
            
            processing_time = time.time() - start_time
            
            result = StageResult(
                stage=stage,
                success=len(fusion_components) > 0,
                results=fused_results,
                confidence=fusion_confidence,
                processing_time=processing_time,
                metadata={'fusion_method': 'weighted_combination'}
            )
            
            self.stage_stats[stage.value]['successful_runs'] += 1
            self.stage_stats[stage.value]['total_time'] += processing_time
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in result fusion: {e}")
            
            self.stage_stats[stage.value]['failed_runs'] += 1
            self.stage_stats[stage.value]['total_time'] += processing_time
            
            return StageResult(
                stage=stage,
                success=False,
                results={},
                confidence=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )
            
    async def _run_output_generation(self, context: ProcessingContext, 
                                   fusion_result: StageResult) -> StageResult:
        """Izvedi output generation stopnjo"""
        start_time = time.time()
        stage = ProcessingStage.OUTPUT_GENERATION
        
        try:
            self.stage_stats[stage.value]['total_runs'] += 1
            
            if not fusion_result.success:
                final_answer = "I couldn't process your request successfully."
            else:
                # Generate answer based on fused results
                fused_data = fusion_result.results
                
                # Priority: reasoning > knowledge > semantic
                if fused_data.get('reasoning_results'):
                    reasoning_data = fused_data['reasoning_results']
                    reasoning_result = reasoning_data.get('reasoning_result', {})
                    final_answer = reasoning_result.get('final_answer', 'Reasoning completed but no specific answer found.')
                    
                elif fused_data.get('knowledge_results'):
                    kb_results = fused_data['knowledge_results'].get('kb_results', [])
                    if kb_results:
                        final_answer = f"Based on knowledge base, I found {len(kb_results)} relevant facts. "
                        # Add some specific information
                        if kb_results:
                            first_result = kb_results[0]
                            final_answer += f"For example: {first_result.get('subject', 'Unknown')} {first_result.get('predicate', 'relates to')} {first_result.get('object', 'Unknown')}."
                    else:
                        final_answer = "I found relevant concepts in the knowledge base but no specific facts."
                        
                elif fused_data.get('semantic_results'):
                    semantic_data = fused_data['semantic_results']
                    parse_result = semantic_data.get('parse_result', {})
                    entities_count = parse_result.get('entities_count', 0)
                    relations_count = parse_result.get('relations_count', 0)
                    
                    final_answer = f"I analyzed your input and found {entities_count} entities and {relations_count} relations. "
                    
                    # Add similarity information
                    similarity_result = semantic_data.get('similarity_result', {})
                    matches = similarity_result.get('matches', [])
                    if matches:
                        final_answer += f"I also found {len(matches)} similar concepts in my knowledge."
                        
                else:
                    final_answer = "I processed your request but couldn't generate a specific answer."
                    
            processing_time = time.time() - start_time
            
            results = {
                'final_answer': final_answer,
                'generation_method': 'rule_based',
                'answer_length': len(final_answer)
            }
            
            result = StageResult(
                stage=stage,
                success=True,
                results=results,
                confidence=fusion_result.confidence,
                processing_time=processing_time,
                metadata={'generation_method': 'rule_based'}
            )
            
            self.stage_stats[stage.value]['successful_runs'] += 1
            self.stage_stats[stage.value]['total_time'] += processing_time
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in output generation: {e}")
            
            self.stage_stats[stage.value]['failed_runs'] += 1
            self.stage_stats[stage.value]['total_time'] += processing_time
            
            return StageResult(
                stage=stage,
                success=False,
                results={'final_answer': f'Error generating output: {e}'},
                confidence=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )
            
    def _extract_keywords(self, text: str) -> List[str]:
        """Izvleči ključne besede iz besedila"""
        # Simple keyword extraction
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:10]  # Return top 10 keywords
        
    def _generate_cache_key(self, context: ProcessingContext) -> str:
        """Generiraj cache key za kontekst"""
        key_data = f"{context.user_input}_{context.processing_mode.value}_{context.confidence_threshold}"
        return hashlib.md5(key_data.encode()).hexdigest()
        
    def _generate_neural_answer(self, semantic_results: Dict[str, Any]) -> str:
        """Generiraj odgovor iz neural rezultatov"""
        parse_result = semantic_results.get('parse_result', {})
        entities_count = parse_result.get('entities_count', 0)
        relations_count = parse_result.get('relations_count', 0)
        
        if entities_count > 0 or relations_count > 0:
            return f"Neural analysis identified {entities_count} entities and {relations_count} relations in your input."
        else:
            return "Neural analysis completed but no specific entities or relations were identified."
            
    def _generate_symbolic_answer(self, reasoning_results: Dict[str, Any]) -> str:
        """Generiraj odgovor iz symbolic rezultatov"""
        reasoning_result = reasoning_results.get('reasoning_result', {})
        return reasoning_result.get('final_answer', 'Symbolic reasoning completed but no specific answer was derived.')
        
    def _generate_hybrid_explanation(self, stage_results: List[StageResult], 
                                   processing_path: List[ProcessingStage]) -> str:
        """Generiraj razlago hibridnega procesiranja"""
        explanation_parts = []
        
        explanation_parts.append(f"Hybrid processing completed {len(stage_results)} stages:")
        
        for i, stage in enumerate(processing_path, 1):
            stage_result = next((r for r in stage_results if r.stage == stage), None)
            if stage_result:
                status = "✅ Success" if stage_result.success else "❌ Failed"
                explanation_parts.append(f"{i}. {stage.value.replace('_', ' ').title()}: {status} (confidence: {stage_result.confidence:.2f})")
                
        successful_stages = sum(1 for r in stage_results if r.success)
        explanation_parts.append(f"Overall: {successful_stages}/{len(stage_results)} stages successful")
        
        return "\n".join(explanation_parts)
        
    def _load_pipeline_data(self):
        """Naloži pipeline podatke z diska"""
        try:
            # Load processing history
            history_file = self.data_dir / 'processing_history.json'
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                    # Load last 100 entries
                    for entry in history_data[-100:]:
                        # Reconstruct PipelineResult objects (simplified)
                        result = PipelineResult(
                            request_id=entry['request_id'],
                            success=entry['success'],
                            final_answer=entry['final_answer'],
                            confidence=entry['confidence'],
                            stage_results=[],  # Skip detailed reconstruction
                            processing_path=[ProcessingStage(stage) for stage in entry.get('processing_path', [])],
                            total_processing_time=entry['total_processing_time'],
                            mode_used=PipelineMode(entry['mode_used']),
                            explanation=entry['explanation'],
                            metadata=entry.get('metadata', {})
                        )
                        self.processing_history.append(result)
                        
            logger.info(f"✅ Pipeline data loaded: {len(self.processing_history)} history entries")
            
        except Exception as e:
            logger.error(f"Error loading pipeline data: {e}")
            
    async def save_pipeline_data(self) -> bool:
        """Shrani pipeline podatke na disk"""
        try:
            def save_data():
                # Save processing history (last 100 entries)
                history_file = self.data_dir / 'processing_history.json'
                with open(history_file, 'w', encoding='utf-8') as f:
                    history_data = []
                    for result in self.processing_history[-100:]:
                        history_data.append({
                            'request_id': result.request_id,
                            'success': result.success,
                            'final_answer': result.final_answer,
                            'confidence': result.confidence,
                            'processing_path': [stage.value for stage in result.processing_path],
                            'total_processing_time': result.total_processing_time,
                            'mode_used': result.mode_used.value,
                            'explanation': result.explanation,
                            'metadata': result.metadata
                        })
                    json.dump(history_data, f, indent=2, ensure_ascii=False)
                    
                # Save statistics
                stats_file = self.data_dir / 'pipeline_statistics.json'
                with open(stats_file, 'w', encoding='utf-8') as f:
                    stats_data = {
                        'general_stats': self.stats,
                        'stage_stats': self.stage_stats
                    }
                    json.dump(stats_data, f, indent=2, default=str)
                    
                return True
                
            success = await asyncio.get_event_loop().run_in_executor(
                self.executor, save_data
            )
            
            if success:
                logger.info("✅ Pipeline data saved successfully")
                return True
            else:
                logger.error("❌ Failed to save pipeline data")
                return False
                
        except Exception as e:
            logger.error(f"Error saving pipeline data: {e}")
            return False
            
    def get_statistics(self) -> PipelineStats:
        """Pridobi statistike pipeline-a"""
        self._update_statistics()
        
        # Calculate stage performance
        stage_performance = {}
        for stage_name, stats in self.stage_stats.items():
            stage_performance[stage_name] = {
                'success_rate': stats['successful_runs'] / max(stats['total_runs'], 1),
                'average_time': stats['average_time'],
                'total_runs': stats['total_runs']
            }
            
        # Calculate mode usage
        mode_usage = {
            'neural_only': self.stats['neural_only_requests'],
            'symbolic_only': self.stats['symbolic_only_requests'],
            'hybrid': self.stats['hybrid_requests'],
            'adaptive': self.stats['adaptive_requests']
        }
        
        # Calculate error rates
        error_rates = {
            'overall': self.stats['failed_requests'] / max(self.stats['total_requests'], 1),
            'cache_miss_rate': self.stats['cache_misses'] / max(self.stats['cache_hits'] + self.stats['cache_misses'], 1)
        }
        
        return PipelineStats(
            total_requests=self.stats['total_requests'],
            successful_requests=self.stats['successful_requests'],
            failed_requests=self.stats['failed_requests'],
            average_processing_time=self.stats['average_processing_time'],
            stage_performance=stage_performance,
            mode_usage=mode_usage,
            error_rates=error_rates
        )
        
    def get_detailed_statistics(self) -> Dict[str, Any]:
        """Pridobi podrobne statistike pipeline-a"""
        basic_stats = self.get_statistics()
        
        return {
            'basic_stats': asdict(basic_stats),
            'component_availability': {
                'knowledge_bank': self.kb_available,
                'semantic_layer': self.semantic_available,
                'reasoning_engine': self.reasoning_available
            },
            'performance_stats': {
                'cache_hits': self.stats['cache_hits'],
                'cache_misses': self.stats['cache_misses'],
                'cache_hit_ratio': self.stats['cache_hits'] / max(self.stats['cache_hits'] + self.stats['cache_misses'], 1),
                'cache_size': len(self.result_cache),
                'history_size': len(self.processing_history)
            },
            'configuration': {
                'default_mode': self.default_mode.value,
                'confidence_threshold': self.confidence_threshold,
                'max_processing_time': self.max_processing_time,
                'cache_size_limit': self.cache_size
            },
            'system_info': {
                'system_health': self.stats['system_health'],
                'uptime': time.time() - self.stats['start_time']
            }
        }
        
    async def shutdown(self):
        """Graceful shutdown Hybrid Pipeline"""
        try:
            logger.info("🔄 Shutting down Hybrid Pipeline...")
            
            # Save current state
            await self.save_pipeline_data()
            
            # Shutdown executor
            if self.executor:
                self.executor.shutdown(wait=True)
                
            # Clear caches
            self.result_cache.clear()
            
            # Update final statistics
            self.stats['system_health'] = 'shutdown'
            
            logger.info("✅ Hybrid Pipeline shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Convenience functions
async def create_hybrid_pipeline(knowledge_bank: Optional[HybridKnowledgeBank] = None,
                                semantic_layer: Optional[SemanticLayer] = None,
                                reasoning_engine: Optional[DeterministicReasoningEngine] = None,
                                data_dir: str = "data/hybrid_pipeline",
                                default_mode: PipelineMode = PipelineMode.ADAPTIVE) -> HybridPipeline:
    """
    Ustvari in inicializiraj Hybrid Pipeline.
    
    Args:
        knowledge_bank: Knowledge Bank komponenta
        semantic_layer: Semantic Layer komponenta
        reasoning_engine: Reasoning Engine komponenta
        data_dir: Direktorij za podatke
        default_mode: Privzeti način delovanja
        
    Returns:
        Inicializiran HybridPipeline
    """
    try:
        pipeline = HybridPipeline(
            knowledge_bank=knowledge_bank,
            semantic_layer=semantic_layer,
            reasoning_engine=reasoning_engine,
            data_dir=data_dir,
            default_mode=default_mode
        )
        
        return pipeline
        
    except Exception as e:
        logger.error(f"Failed to create Hybrid Pipeline: {e}")
        raise


async def create_full_hybrid_system(data_dir: str = "data/hybrid_system") -> HybridPipeline:
    """
    Ustvari celoten hibridni sistem z vsemi komponentami.
    
    Args:
        data_dir: Osnovni direktorij za podatke
        
    Returns:
        Polno inicializiran HybridPipeline
    """
    try:
        logger.info("🚀 Creating full hybrid system...")
        
        # Create Knowledge Bank
        kb = await create_hybrid_knowledge_bank(
            data_dir=f"{data_dir}/knowledge_bank",
            integrate_with_mia=True
        )
        
        # Create Semantic Layer
        semantic = await create_semantic_layer(
            knowledge_bank=kb,
            data_dir=f"{data_dir}/semantic_layer"
        )
        
        # Create Reasoning Engine
        reasoning = await create_reasoning_engine(
            knowledge_bank=kb,
            semantic_layer=semantic,
            data_dir=f"{data_dir}/reasoning_engine"
        )
        
        # Create Hybrid Pipeline
        pipeline = await create_hybrid_pipeline(
            knowledge_bank=kb,
            semantic_layer=semantic,
            reasoning_engine=reasoning,
            data_dir=f"{data_dir}/pipeline",
            default_mode=PipelineMode.ADAPTIVE
        )
        
        logger.info("✅ Full hybrid system created successfully")
        return pipeline
        
    except Exception as e:
        logger.error(f"Failed to create full hybrid system: {e}")
        raise


if __name__ == "__main__":
    # Test implementation
    async def test_hybrid_pipeline():
        """Test Hybrid Pipeline sistema"""
        try:
            logger.info("🧪 Testing Hybrid Pipeline...")
            
            # Create full hybrid system
            pipeline = await create_full_hybrid_system()
            
            # Test different processing modes
            test_queries = [
                ("What is artificial intelligence?", PipelineMode.NEURAL_ONLY),
                ("If all humans are mortal and Socrates is human, is Socrates mortal?", PipelineMode.SYMBOLIC_ONLY),
                ("Explain the relationship between machine learning and AI", PipelineMode.HYBRID_SEQUENTIAL),
                ("How does neural networks work in practice?", PipelineMode.ADAPTIVE)
            ]
            
            for query, mode in test_queries:
                logger.info(f"\n--- Testing {mode.value} mode ---")
                logger.info(f"Query: {query}")
                
                result = await pipeline.process(
                    user_input=query,
                    mode=mode,
                    confidence_threshold=0.5
                )
                
                logger.info(f"Result:")
                logger.info(f"  - Success: {result.success}")
                logger.info(f"  - Confidence: {result.confidence:.2f}")
                logger.info(f"  - Processing time: {result.total_processing_time:.3f}s")
                logger.info(f"  - Stages: {len(result.stage_results)}")
                logger.info(f"  - Answer: {result.final_answer[:100]}...")
                
            # Get statistics
            stats = pipeline.get_detailed_statistics()
            logger.info(f"\nPipeline Statistics:")
            logger.info(f"  - Total requests: {stats['basic_stats']['total_requests']}")
            logger.info(f"  - Success rate: {stats['basic_stats']['successful_requests'] / max(stats['basic_stats']['total_requests'], 1):.2%}")
            logger.info(f"  - Average processing time: {stats['basic_stats']['average_processing_time']:.3f}s")
            
            # Save data
            await pipeline.save_pipeline_data()
            
            # Shutdown
            await pipeline.shutdown()
            
            logger.info("✅ Hybrid Pipeline test completed successfully")
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise
    
    # Run test
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_hybrid_pipeline())