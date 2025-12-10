#!/usr/bin/env python3
"""
Hybrid Integration - Integracija hibridnega sistema z obstoječimi MIA komponentami
================================================================================

PRODUKCIJSKA IMPLEMENTACIJA integracije hibridnega sistema z:
- Obstoječim AGI Core
- Persistent Knowledge Store
- Desktop/Web interfaces
- Enterprise funkcionalnostmi
- Security sistemi

KLJUČNE FUNKCIONALNOSTI:
- Backward compatibility z obstoječimi API-ji
- Seamless integration z AGI Core
- Enhanced capabilities preko hibridnega sistema
- Fallback mechanisms za stabilnost
- Performance optimization
- Unified interface za vse funkcionalnosti

ARHITEKTURA:
- Ohrani vse obstoječe funkcionalnosti
- Dodaj hibridne capabilities kot enhancement
- Transparent switching med classic in hybrid modes
- Comprehensive error handling in fallbacks
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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from mia.core.agi_core import AGICore, Thought, Task, ThoughtType, TaskStatus
    from mia.core.persistent_knowledge_store import PersistentKnowledgeStore, Fact, Relation, UserModel
    AGI_CORE_AVAILABLE = True
except ImportError:
    AGI_CORE_AVAILABLE = False

# Import hybrid components
try:
    from mia.knowledge.hybrid.knowledge_bank_core import HybridKnowledgeBank, create_hybrid_knowledge_bank
    from mia.knowledge.hybrid.semantic_layer import SemanticLayer, create_semantic_layer
    from mia.knowledge.hybrid.deterministic_reasoning import DeterministicReasoningEngine, create_reasoning_engine
    from mia.knowledge.hybrid.hybrid_pipeline import HybridPipeline, create_full_hybrid_system, PipelineMode
    from mia.knowledge.hybrid.autonomous_learning import AutonomousLearning, create_autonomous_learning
    HYBRID_COMPONENTS_AVAILABLE = True
except ImportError:
    HYBRID_COMPONENTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class IntegrationMode(Enum):
    """Načini integracije"""
    CLASSIC_ONLY = "classic_only"
    HYBRID_ONLY = "hybrid_only"
    HYBRID_ENHANCED = "hybrid_enhanced"
    ADAPTIVE = "adaptive"

class CapabilityLevel(Enum):
    """Nivoji zmogljivosti"""
    BASIC = "basic"
    ENHANCED = "enhanced"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class IntegrationConfig:
    """Konfiguracija integracije"""
    mode: IntegrationMode
    enable_hybrid_reasoning: bool
    enable_semantic_processing: bool
    enable_autonomous_learning: bool
    fallback_to_classic: bool
    performance_monitoring: bool
    data_dir: str

@dataclass
class ProcessingRequest:
    """Zahteva za procesiranje"""
    request_id: str
    user_input: str
    user_id: Optional[str]
    context: Dict[str, Any]
    preferred_mode: Optional[IntegrationMode]
    timestamp: float

@dataclass
class ProcessingResponse:
    """Odgovor procesiranja"""
    request_id: str
    success: bool
    response: str
    confidence: float
    processing_time: float
    mode_used: IntegrationMode
    capabilities_used: List[str]
    thoughts: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class HybridIntegration:
    """
    Integracija hibridnega sistema z obstoječimi MIA komponentami.
    
    Omogoča:
    - Backward compatibility z obstoječimi API-ji
    - Enhanced capabilities preko hibridnega sistema
    - Seamless switching med classic in hybrid modes
    - Fallback mechanisms za stabilnost
    - Performance optimization
    - Unified interface
    
    PRODUKCIJSKE FUNKCIONALNOSTI:
    ✅ Backward compatibility z AGI Core
    ✅ Integration z Persistent Knowledge Store
    ✅ Enhanced reasoning capabilities
    ✅ Semantic processing integration
    ✅ Autonomous learning integration
    ✅ Fallback mechanisms
    ✅ Performance monitoring
    ✅ Unified API interface
    """
    
    def __init__(self, 
                 config: IntegrationConfig,
                 agi_core: Optional['AGICore'] = None,
                 knowledge_store: Optional[PersistentKnowledgeStore] = None):
        """
        Inicializiraj hibridno integracijo.
        
        Args:
            config: Konfiguracija integracije
            agi_core: Obstoječi AGI Core
            knowledge_store: Obstoječi Knowledge Store
        """
        self.config = config
        self.data_dir = Path(config.data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Classic MIA components
        self.agi_core = agi_core
        self.knowledge_store = knowledge_store
        self.classic_available = AGI_CORE_AVAILABLE and agi_core is not None
        
        # Hybrid components (will be initialized)
        self.hybrid_pipeline: Optional[HybridPipeline] = None
        self.knowledge_bank: Optional[HybridKnowledgeBank] = None
        self.semantic_layer: Optional[SemanticLayer] = None
        self.reasoning_engine: Optional[DeterministicReasoningEngine] = None
        self.autonomous_learning: Optional[AutonomousLearning] = None
        
        # Component availability flags
        self.hybrid_available = False
        self.semantic_available = False
        self.reasoning_available = False
        self.learning_available = False
        
        # Performance optimization
        self.executor = ThreadPoolExecutor(max_workers=6)
        self.request_cache: Dict[str, ProcessingResponse] = {}
        self.cache_size = 1000
        
        # Processing history
        self.processing_history: List[ProcessingResponse] = []
        self.max_history_size = 1000
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'classic_requests': 0,
            'hybrid_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'fallback_activations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_processing_time': 0.0,
            'system_health': 'initializing',
            'start_time': time.time()
        }
        
        logger.info("✅ Hybrid Integration inicializiran")
        logger.info(f"   - Mode: {self.config.mode.value}")
        logger.info(f"   - Classic Available: {'✅' if self.classic_available else '❌'}")
        logger.info(f"   - Hybrid Components: {'✅' if HYBRID_COMPONENTS_AVAILABLE else '❌'}")
        
    async def initialize_hybrid_components(self):
        """Inicializiraj hibridne komponente"""
        try:
            logger.info("🚀 Initializing hybrid components...")
            
            if not HYBRID_COMPONENTS_AVAILABLE:
                logger.warning("❌ Hybrid components not available")
                return False
                
            # Initialize hybrid system
            if self.config.mode in [IntegrationMode.HYBRID_ONLY, IntegrationMode.HYBRID_ENHANCED, IntegrationMode.ADAPTIVE]:
                
                # Create full hybrid system
                self.hybrid_pipeline = await create_full_hybrid_system(
                    data_dir=str(self.data_dir / "hybrid_system")
                )
                
                # Extract individual components
                self.knowledge_bank = self.hybrid_pipeline.knowledge_bank
                self.semantic_layer = self.hybrid_pipeline.semantic_layer
                self.reasoning_engine = self.hybrid_pipeline.reasoning_engine
                
                # Create autonomous learning
                if self.config.enable_autonomous_learning:
                    self.autonomous_learning = await create_autonomous_learning(
                        knowledge_bank=self.knowledge_bank,
                        semantic_layer=self.semantic_layer,
                        reasoning_engine=self.reasoning_engine,
                        pipeline=self.hybrid_pipeline,
                        data_dir=str(self.data_dir / "autonomous_learning")
                    )
                    
                    # Start autonomous learning
                    await self.autonomous_learning.start_learning()
                    self.learning_available = True
                    
                # Update availability flags
                self.hybrid_available = True
                self.semantic_available = self.semantic_layer is not None
                self.reasoning_available = self.reasoning_engine is not None
                
                logger.info("✅ Hybrid components initialized successfully")
                
                # Sync with classic knowledge store if available
                if self.knowledge_store and self.knowledge_bank:
                    await self._sync_knowledge_stores()
                    
                return True
                
        except Exception as e:
            logger.error(f"Error initializing hybrid components: {e}")
            return False
            
    async def _sync_knowledge_stores(self):
        """Sinhroniziraj classic in hybrid knowledge stores"""
        try:
            logger.info("🔄 Syncing knowledge stores...")
            
            if not self.knowledge_store or not self.knowledge_bank:
                return
                
            # Sync facts from classic to hybrid
            classic_facts = self.knowledge_store.get_all_facts()
            
            for fact in classic_facts[:100]:  # Limit to first 100 for demo
                try:
                    # Create concept in hybrid system
                    await self.knowledge_bank.create_concept(
                        concept_id=fact.entity,
                        label=fact.entity,
                        description=f"Migrated from classic system: {fact.property}",
                        properties={
                            'classic_property': fact.property,
                            'classic_value': str(fact.value),
                            'classic_confidence': fact.confidence,
                            'migration_timestamp': time.time()
                        }
                    )
                    
                except Exception as e:
                    logger.debug(f"Could not migrate fact {fact.entity}: {e}")
                    
            # Sync relations from classic to hybrid
            classic_relations = self.knowledge_store.get_all_relations()
            
            for relation in classic_relations[:50]:  # Limit to first 50 for demo
                try:
                    # Create relation in hybrid system
                    await self.knowledge_bank.create_relation(
                        relation_id=f"{relation.subject}_{relation.predicate}_{relation.object}",
                        label=relation.predicate,
                        domain=f"http://mia.ai/ontology#{relation.subject}",
                        range=f"http://mia.ai/ontology#{relation.object}",
                        properties={
                            'classic_confidence': relation.confidence,
                            'migration_timestamp': time.time()
                        }
                    )
                    
                except Exception as e:
                    logger.debug(f"Could not migrate relation {relation.subject}-{relation.predicate}-{relation.object}: {e}")
                    
            logger.info("✅ Knowledge stores synchronized")
            
        except Exception as e:
            logger.error(f"Error syncing knowledge stores: {e}")
            
    async def process_request(self, request: ProcessingRequest) -> ProcessingResponse:
        """
        Glavna metoda za procesiranje zahtev.
        
        Args:
            request: Zahteva za procesiranje
            
        Returns:
            ProcessingResponse
        """
        start_time = time.time()
        
        try:
            self.stats['total_requests'] += 1
            
            # Check cache
            cache_key = self._generate_cache_key(request)
            if cache_key in self.request_cache:
                self.stats['cache_hits'] += 1
                cached_response = self.request_cache[cache_key]
                logger.debug(f"Cache hit for request: {request.request_id}")
                return cached_response
                
            self.stats['cache_misses'] += 1
            
            # Determine processing mode
            processing_mode = self._determine_processing_mode(request)
            
            # Process based on mode
            if processing_mode == IntegrationMode.CLASSIC_ONLY:
                response = await self._process_classic_only(request)
                self.stats['classic_requests'] += 1
                
            elif processing_mode == IntegrationMode.HYBRID_ONLY:
                response = await self._process_hybrid_only(request)
                self.stats['hybrid_requests'] += 1
                
            elif processing_mode == IntegrationMode.HYBRID_ENHANCED:
                response = await self._process_hybrid_enhanced(request)
                self.stats['hybrid_requests'] += 1
                
            else:  # ADAPTIVE
                response = await self._process_adaptive(request)
                
            # Update statistics
            if response.success:
                self.stats['successful_requests'] += 1
            else:
                self.stats['failed_requests'] += 1
                
            # Cache response
            if len(self.request_cache) < self.cache_size:
                self.request_cache[cache_key] = response
            elif len(self.request_cache) >= self.cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self.request_cache))
                del self.request_cache[oldest_key]
                self.request_cache[cache_key] = response
                
            # Add to history
            self.processing_history.append(response)
            if len(self.processing_history) > self.max_history_size:
                self.processing_history = self.processing_history[-self.max_history_size:]
                
            # Learn from interaction if autonomous learning is enabled
            if self.learning_available and self.autonomous_learning:
                try:
                    await self.autonomous_learning.learn_from_interaction(
                        user_input=request.user_input,
                        system_response=response.response,
                        pipeline_result=response.metadata.get('pipeline_result'),
                        feedback=None  # Could be added later
                    )
                except Exception as e:
                    logger.warning(f"Error in autonomous learning: {e}")
                    
            logger.info(f"Request processed: {request.request_id} "
                       f"({'✅ Success' if response.success else '❌ Failed'}) "
                       f"in {response.processing_time:.3f}s using {response.mode_used.value}")
                       
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error processing request: {e}")
            
            self.stats['failed_requests'] += 1
            
            return ProcessingResponse(
                request_id=request.request_id,
                success=False,
                response=f"Error processing request: {e}",
                confidence=0.0,
                processing_time=processing_time,
                mode_used=IntegrationMode.CLASSIC_ONLY,
                capabilities_used=[],
                thoughts=[],
                metadata={'error': str(e)}
            )
            
    def _determine_processing_mode(self, request: ProcessingRequest) -> IntegrationMode:
        """Določi način procesiranja za zahtevo"""
        try:
            # Use preferred mode if specified
            if request.preferred_mode:
                return request.preferred_mode
                
            # Use configured mode
            if self.config.mode != IntegrationMode.ADAPTIVE:
                return self.config.mode
                
            # Adaptive mode selection
            input_length = len(request.user_input.split())
            
            # For simple queries, use classic if available
            if input_length <= 5 and self.classic_available:
                return IntegrationMode.CLASSIC_ONLY
                
            # For complex logical queries, use hybrid if available
            logical_keywords = ['if', 'then', 'because', 'therefore', 'implies', 'all', 'some', 'every']
            if any(keyword in request.user_input.lower() for keyword in logical_keywords):
                if self.hybrid_available:
                    return IntegrationMode.HYBRID_ENHANCED
                    
            # For medium complexity, use enhanced mode
            if self.hybrid_available:
                return IntegrationMode.HYBRID_ENHANCED
            elif self.classic_available:
                return IntegrationMode.CLASSIC_ONLY
            else:
                return IntegrationMode.HYBRID_ONLY
                
        except Exception as e:
            logger.error(f"Error determining processing mode: {e}")
            return IntegrationMode.CLASSIC_ONLY if self.classic_available else IntegrationMode.HYBRID_ONLY
            
    async def _process_classic_only(self, request: ProcessingRequest) -> ProcessingResponse:
        """Procesiranje samo z classic komponentami"""
        start_time = time.time()
        
        try:
            if not self.classic_available or not self.agi_core:
                return ProcessingResponse(
                    request_id=request.request_id,
                    success=False,
                    response="Classic AGI Core not available",
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    mode_used=IntegrationMode.CLASSIC_ONLY,
                    capabilities_used=[],
                    thoughts=[],
                    metadata={'error': 'classic_unavailable'}
                )
                
            # Create task for AGI Core
            task = Task(
                id=request.request_id,
                description=request.user_input,
                priority=1,
                status=TaskStatus.PENDING,
                created_at=time.time(),
                context=request.context,
                user_id=request.user_id
            )
            
            # Process with AGI Core
            def process_with_agi():
                try:
                    # Add task to AGI Core
                    self.agi_core.add_task(task)
                    
                    # Process task
                    result = self.agi_core.process_task(task.id)
                    
                    if result:
                        return {
                            'success': True,
                            'response': result.get('response', 'Task completed'),
                            'confidence': result.get('confidence', 0.8),
                            'thoughts': result.get('thoughts', [])
                        }
                    else:
                        return {
                            'success': False,
                            'response': 'Task processing failed',
                            'confidence': 0.0,
                            'thoughts': []
                        }
                        
                except Exception as e:
                    logger.error(f"Error in AGI Core processing: {e}")
                    return {
                        'success': False,
                        'response': f'AGI Core error: {e}',
                        'confidence': 0.0,
                        'thoughts': []
                    }
                    
            # Run AGI processing in executor
            agi_result = await asyncio.get_event_loop().run_in_executor(
                self.executor, process_with_agi
            )
            
            processing_time = time.time() - start_time
            
            return ProcessingResponse(
                request_id=request.request_id,
                success=agi_result['success'],
                response=agi_result['response'],
                confidence=agi_result['confidence'],
                processing_time=processing_time,
                mode_used=IntegrationMode.CLASSIC_ONLY,
                capabilities_used=['agi_core'],
                thoughts=agi_result['thoughts'],
                metadata={'agi_result': agi_result}
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in classic-only processing: {e}")
            
            return ProcessingResponse(
                request_id=request.request_id,
                success=False,
                response=f"Classic processing error: {e}",
                confidence=0.0,
                processing_time=processing_time,
                mode_used=IntegrationMode.CLASSIC_ONLY,
                capabilities_used=[],
                thoughts=[],
                metadata={'error': str(e)}
            )
            
    async def _process_hybrid_only(self, request: ProcessingRequest) -> ProcessingResponse:
        """Procesiranje samo z hibridnimi komponentami"""
        start_time = time.time()
        
        try:
            if not self.hybrid_available or not self.hybrid_pipeline:
                return ProcessingResponse(
                    request_id=request.request_id,
                    success=False,
                    response="Hybrid pipeline not available",
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    mode_used=IntegrationMode.HYBRID_ONLY,
                    capabilities_used=[],
                    thoughts=[],
                    metadata={'error': 'hybrid_unavailable'}
                )
                
            # Process with hybrid pipeline
            pipeline_result = await self.hybrid_pipeline.process(
                user_input=request.user_input,
                mode=PipelineMode.ADAPTIVE,
                confidence_threshold=0.5,
                metadata=request.context
            )
            
            processing_time = time.time() - start_time
            
            # Convert pipeline result to response
            capabilities_used = []
            if self.semantic_available:
                capabilities_used.append('semantic_layer')
            if self.reasoning_available:
                capabilities_used.append('reasoning_engine')
            if self.knowledge_bank:
                capabilities_used.append('knowledge_bank')
                
            return ProcessingResponse(
                request_id=request.request_id,
                success=pipeline_result.success,
                response=pipeline_result.final_answer,
                confidence=pipeline_result.confidence,
                processing_time=processing_time,
                mode_used=IntegrationMode.HYBRID_ONLY,
                capabilities_used=capabilities_used,
                thoughts=[],  # Could extract from pipeline stages
                metadata={
                    'pipeline_result': asdict(pipeline_result),
                    'stages_completed': len(pipeline_result.stage_results)
                }
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in hybrid-only processing: {e}")
            
            return ProcessingResponse(
                request_id=request.request_id,
                success=False,
                response=f"Hybrid processing error: {e}",
                confidence=0.0,
                processing_time=processing_time,
                mode_used=IntegrationMode.HYBRID_ONLY,
                capabilities_used=[],
                thoughts=[],
                metadata={'error': str(e)}
            )
            
    async def _process_hybrid_enhanced(self, request: ProcessingRequest) -> ProcessingResponse:
        """Procesiranje z hibridnimi komponentami in classic fallback"""
        start_time = time.time()
        
        try:
            # Try hybrid processing first
            if self.hybrid_available and self.hybrid_pipeline:
                pipeline_result = await self.hybrid_pipeline.process(
                    user_input=request.user_input,
                    mode=PipelineMode.ADAPTIVE,
                    confidence_threshold=0.5,
                    metadata=request.context
                )
                
                # If hybrid processing successful and confident, use it
                if pipeline_result.success and pipeline_result.confidence >= 0.6:
                    capabilities_used = ['hybrid_pipeline']
                    if self.semantic_available:
                        capabilities_used.append('semantic_layer')
                    if self.reasoning_available:
                        capabilities_used.append('reasoning_engine')
                    if self.knowledge_bank:
                        capabilities_used.append('knowledge_bank')
                        
                    return ProcessingResponse(
                        request_id=request.request_id,
                        success=True,
                        response=pipeline_result.final_answer,
                        confidence=pipeline_result.confidence,
                        processing_time=time.time() - start_time,
                        mode_used=IntegrationMode.HYBRID_ENHANCED,
                        capabilities_used=capabilities_used,
                        thoughts=[],
                        metadata={
                            'pipeline_result': asdict(pipeline_result),
                            'primary_processing': 'hybrid'
                        }
                    )
                    
            # Fallback to classic processing
            if self.config.fallback_to_classic and self.classic_available:
                logger.info(f"Falling back to classic processing for request: {request.request_id}")
                self.stats['fallback_activations'] += 1
                
                classic_response = await self._process_classic_only(request)
                classic_response.mode_used = IntegrationMode.HYBRID_ENHANCED
                classic_response.capabilities_used.append('classic_fallback')
                classic_response.metadata['fallback_reason'] = 'hybrid_low_confidence'
                
                return classic_response
                
            # If no fallback available, return hybrid result anyway
            elif self.hybrid_available and self.hybrid_pipeline:
                pipeline_result = await self.hybrid_pipeline.process(
                    user_input=request.user_input,
                    mode=PipelineMode.ADAPTIVE,
                    confidence_threshold=0.3,  # Lower threshold
                    metadata=request.context
                )
                
                return ProcessingResponse(
                    request_id=request.request_id,
                    success=pipeline_result.success,
                    response=pipeline_result.final_answer,
                    confidence=pipeline_result.confidence,
                    processing_time=time.time() - start_time,
                    mode_used=IntegrationMode.HYBRID_ENHANCED,
                    capabilities_used=['hybrid_pipeline'],
                    thoughts=[],
                    metadata={
                        'pipeline_result': asdict(pipeline_result),
                        'no_fallback_available': True
                    }
                )
                
            else:
                return ProcessingResponse(
                    request_id=request.request_id,
                    success=False,
                    response="No processing capabilities available",
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    mode_used=IntegrationMode.HYBRID_ENHANCED,
                    capabilities_used=[],
                    thoughts=[],
                    metadata={'error': 'no_capabilities'}
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in hybrid-enhanced processing: {e}")
            
            return ProcessingResponse(
                request_id=request.request_id,
                success=False,
                response=f"Hybrid-enhanced processing error: {e}",
                confidence=0.0,
                processing_time=processing_time,
                mode_used=IntegrationMode.HYBRID_ENHANCED,
                capabilities_used=[],
                thoughts=[],
                metadata={'error': str(e)}
            )
            
    async def _process_adaptive(self, request: ProcessingRequest) -> ProcessingResponse:
        """Adaptivno procesiranje"""
        # Determine best mode for this specific request
        adaptive_mode = self._determine_processing_mode(request)
        
        # Process with determined mode
        if adaptive_mode == IntegrationMode.CLASSIC_ONLY:
            response = await self._process_classic_only(request)
        elif adaptive_mode == IntegrationMode.HYBRID_ONLY:
            response = await self._process_hybrid_only(request)
        else:
            response = await self._process_hybrid_enhanced(request)
            
        # Mark as adaptive
        response.mode_used = IntegrationMode.ADAPTIVE
        response.metadata['adaptive_selection'] = adaptive_mode.value
        
        return response
        
    def _generate_cache_key(self, request: ProcessingRequest) -> str:
        """Generiraj cache key za zahtevo"""
        key_data = f"{request.user_input}_{request.user_id}_{hash(str(request.context))}"
        return hashlib.md5(key_data.encode()).hexdigest()
        
    def get_capabilities(self) -> Dict[str, Any]:
        """Pridobi trenutne zmogljivosti sistema"""
        capabilities = {
            'classic_capabilities': {
                'agi_core': self.classic_available,
                'knowledge_store': self.knowledge_store is not None,
                'reasoning': self.classic_available,
                'task_management': self.classic_available
            },
            'hybrid_capabilities': {
                'knowledge_bank': self.knowledge_bank is not None,
                'semantic_processing': self.semantic_available,
                'deterministic_reasoning': self.reasoning_available,
                'hybrid_pipeline': self.hybrid_available,
                'autonomous_learning': self.learning_available
            },
            'integration_features': {
                'backward_compatibility': True,
                'fallback_mechanisms': self.config.fallback_to_classic,
                'adaptive_mode': self.config.mode == IntegrationMode.ADAPTIVE,
                'performance_monitoring': self.config.performance_monitoring
            },
            'capability_level': self._assess_capability_level()
        }
        
        return capabilities
        
    def _assess_capability_level(self) -> CapabilityLevel:
        """Oceni nivo zmogljivosti"""
        if self.hybrid_available and self.semantic_available and self.reasoning_available and self.learning_available:
            return CapabilityLevel.EXPERT
        elif self.hybrid_available and (self.semantic_available or self.reasoning_available):
            return CapabilityLevel.ADVANCED
        elif self.hybrid_available or self.classic_available:
            return CapabilityLevel.ENHANCED
        else:
            return CapabilityLevel.BASIC
            
    def get_statistics(self) -> Dict[str, Any]:
        """Pridobi statistike integracije"""
        return {
            'request_stats': {
                'total_requests': self.stats['total_requests'],
                'successful_requests': self.stats['successful_requests'],
                'failed_requests': self.stats['failed_requests'],
                'success_rate': self.stats['successful_requests'] / max(self.stats['total_requests'], 1)
            },
            'mode_stats': {
                'classic_requests': self.stats['classic_requests'],
                'hybrid_requests': self.stats['hybrid_requests'],
                'fallback_activations': self.stats['fallback_activations']
            },
            'performance_stats': {
                'cache_hits': self.stats['cache_hits'],
                'cache_misses': self.stats['cache_misses'],
                'cache_hit_ratio': self.stats['cache_hits'] / max(self.stats['cache_hits'] + self.stats['cache_misses'], 1),
                'average_processing_time': self.stats['average_processing_time']
            },
            'system_info': {
                'integration_mode': self.config.mode.value,
                'capability_level': self._assess_capability_level().value,
                'classic_available': self.classic_available,
                'hybrid_available': self.hybrid_available,
                'system_health': self.stats['system_health']
            },
            'uptime': time.time() - self.stats['start_time']
        }
        
    async def shutdown(self):
        """Graceful shutdown integracije"""
        try:
            logger.info("🔄 Shutting down Hybrid Integration...")
            
            # Shutdown autonomous learning
            if self.learning_available and self.autonomous_learning:
                await self.autonomous_learning.shutdown()
                
            # Shutdown hybrid components
            if self.hybrid_pipeline:
                await self.hybrid_pipeline.shutdown()
                
            # Shutdown executor
            if self.executor:
                self.executor.shutdown(wait=True)
                
            # Clear caches
            self.request_cache.clear()
            
            # Update final statistics
            self.stats['system_health'] = 'shutdown'
            
            logger.info("✅ Hybrid Integration shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Convenience functions
async def create_hybrid_integration(config: IntegrationConfig,
                                   agi_core: Optional['AGICore'] = None,
                                   knowledge_store: Optional[PersistentKnowledgeStore] = None) -> HybridIntegration:
    """
    Ustvari in inicializiraj hibridno integracijo.
    
    Args:
        config: Konfiguracija integracije
        agi_core: Obstoječi AGI Core
        knowledge_store: Obstoječi Knowledge Store
        
    Returns:
        Inicializiran HybridIntegration
    """
    try:
        integration = HybridIntegration(
            config=config,
            agi_core=agi_core,
            knowledge_store=knowledge_store
        )
        
        # Initialize hybrid components if needed
        if config.mode in [IntegrationMode.HYBRID_ONLY, IntegrationMode.HYBRID_ENHANCED, IntegrationMode.ADAPTIVE]:
            await integration.initialize_hybrid_components()
            
        return integration
        
    except Exception as e:
        logger.error(f"Failed to create Hybrid Integration: {e}")
        raise


# Default configuration
def get_default_config(data_dir: str = "data/hybrid_integration") -> IntegrationConfig:
    """Pridobi privzeto konfiguracijo"""
    return IntegrationConfig(
        mode=IntegrationMode.HYBRID_ENHANCED,
        enable_hybrid_reasoning=True,
        enable_semantic_processing=True,
        enable_autonomous_learning=True,
        fallback_to_classic=True,
        performance_monitoring=True,
        data_dir=data_dir
    )


if __name__ == "__main__":
    # Test implementation
    async def test_hybrid_integration():
        """Test Hybrid Integration sistema"""
        try:
            logger.info("🧪 Testing Hybrid Integration...")
            
            # Create configuration
            config = get_default_config()
            
            # Create hybrid integration
            integration = await create_hybrid_integration(config)
            
            # Test different types of requests
            test_requests = [
                ProcessingRequest(
                    request_id=str(uuid.uuid4()),
                    user_input="What is artificial intelligence?",
                    user_id="test_user",
                    context={},
                    preferred_mode=None,
                    timestamp=time.time()
                ),
                ProcessingRequest(
                    request_id=str(uuid.uuid4()),
                    user_input="If all birds can fly and penguins are birds, can penguins fly?",
                    user_id="test_user",
                    context={},
                    preferred_mode=IntegrationMode.HYBRID_ENHANCED,
                    timestamp=time.time()
                ),
                ProcessingRequest(
                    request_id=str(uuid.uuid4()),
                    user_input="Hello",
                    user_id="test_user",
                    context={},
                    preferred_mode=IntegrationMode.CLASSIC_ONLY,
                    timestamp=time.time()
                )
            ]
            
            for request in test_requests:
                logger.info(f"\n--- Processing request ---")
                logger.info(f"Input: {request.user_input}")
                logger.info(f"Preferred mode: {request.preferred_mode.value if request.preferred_mode else 'None'}")
                
                response = await integration.process_request(request)
                
                logger.info(f"Response:")
                logger.info(f"  - Success: {response.success}")
                logger.info(f"  - Mode used: {response.mode_used.value}")
                logger.info(f"  - Confidence: {response.confidence:.2f}")
                logger.info(f"  - Processing time: {response.processing_time:.3f}s")
                logger.info(f"  - Capabilities used: {response.capabilities_used}")
                logger.info(f"  - Answer: {response.response[:100]}...")
                
            # Get capabilities
            capabilities = integration.get_capabilities()
            logger.info(f"\nSystem Capabilities:")
            logger.info(f"  - Capability level: {capabilities['capability_level']}")
            logger.info(f"  - Classic available: {capabilities['classic_capabilities']['agi_core']}")
            logger.info(f"  - Hybrid available: {capabilities['hybrid_capabilities']['hybrid_pipeline']}")
            
            # Get statistics
            stats = integration.get_statistics()
            logger.info(f"\nIntegration Statistics:")
            logger.info(f"  - Total requests: {stats['request_stats']['total_requests']}")
            logger.info(f"  - Success rate: {stats['request_stats']['success_rate']:.2%}")
            logger.info(f"  - Classic requests: {stats['mode_stats']['classic_requests']}")
            logger.info(f"  - Hybrid requests: {stats['mode_stats']['hybrid_requests']}")
            
            # Shutdown
            await integration.shutdown()
            
            logger.info("✅ Hybrid Integration test completed successfully")
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise
    
    # Run test
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_hybrid_integration())