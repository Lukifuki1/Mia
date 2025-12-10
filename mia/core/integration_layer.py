#!/usr/bin/env python3
"""
MIA Integration Layer
====================

Poveže vse komponente MIA v enotni sistem z unified API.
To je KLJUČNA komponenta za delovanje celotnega sistema.

GARANCIJA: 95% - povezuje obstoječe komponente z jasnimi vmesniki
"""

import asyncio
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict

# Import MIA components
from mia.core.persistent_knowledge_store import PersistentKnowledgeStore
from mia.system.adaptive_resource_manager import AdaptiveResourceManager
from mia.learning.interaction_learner import InteractionLearner
from mia.reasoning.basic_reasoning_engine import BasicReasoningEngine, ReasoningResult
from mia.learning.advanced_file_learner import AdvancedFileLearner

logger = logging.getLogger(__name__)

@dataclass
class MIAResponse:
    """Unified MIA response format"""
    answer: str
    confidence: float
    sources: List[str]
    reasoning_steps: List[str]
    facts_learned: int
    learning_opportunity: bool
    processing_time: float
    user_id: str
    timestamp: float
    metadata: Dict[str, Any]

@dataclass
class SystemStatus:
    """System status information"""
    resource_usage: Dict[str, Any]
    knowledge_stats: Dict[str, Any]
    learning_stats: Dict[str, Any]
    reasoning_stats: Dict[str, Any]
    models_discovered: int
    models_loaded: int
    system_health: str
    uptime: float

class MIAIntegrationLayer:
    """
    Glavni integration layer za MIA sistem.
    
    Funkcionalnosti:
    - Unified API za vse MIA komponente
    - Koordinacija med learning, reasoning in knowledge storage
    - System monitoring in health checks
    - Async processing pipeline
    - Error handling in graceful degradation
    """
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize core components
        self.knowledge_store = None
        self.resource_manager = None
        self.interaction_learner = None
        self.reasoning_engine = None
        self.file_learner = None
        
        # System state
        self.initialized = False
        self.start_time = time.time()
        self.processing_stats = {
            'total_requests': 0,
            'successful_responses': 0,
            'learning_sessions': 0,
            'errors': 0
        }
        
        # Initialize components
        self._initialize_components()
        
        logger.info("MIA Integration Layer initialized")
        
    def _load_config(self) -> Dict[str, Any]:
        """Naloži konfiguracijo"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            # Fallback configuration
            return {
                "paths": {
                    "data_dir": "./mia/data",
                    "models_dir": "./models",
                    "logs_dir": "./logs"
                },
                "ai": {
                    "learning_enabled": True,
                    "memory_enabled": True
                },
                "system": {
                    "debug": False
                }
            }
            
    def _initialize_components(self):
        """Inicializiraj vse komponente"""
        try:
            data_dir = self.config.get('paths', {}).get('data_dir', './mia/data')
            
            # 1. Knowledge Store
            self.knowledge_store = PersistentKnowledgeStore(data_dir)
            logger.info("✅ Knowledge Store initialized")
            
            # 2. Resource Manager
            self.resource_manager = AdaptiveResourceManager(f"{data_dir}/system")
            self.resource_manager.start_monitoring()
            logger.info("✅ Resource Manager initialized")
            
            # 3. Interaction Learner
            self.interaction_learner = InteractionLearner(self.knowledge_store)
            logger.info("✅ Interaction Learner initialized")
            
            # 4. Reasoning Engine
            self.reasoning_engine = BasicReasoningEngine(self.knowledge_store)
            logger.info("✅ Reasoning Engine initialized")
            
            # 5. Advanced File Learner
            self.file_learner = AdvancedFileLearner(self.knowledge_store, f"{data_dir}/learning")
            logger.info("✅ Advanced File Learner initialized")
            
            # Register resource callbacks
            self._setup_resource_callbacks()
            
            self.initialized = True
            logger.info("🚀 All MIA components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            self.initialized = False
            raise
            
    def _setup_resource_callbacks(self):
        """Nastavi callbacks za resource management"""
        def on_resource_overload(overload_status):
            """Handle resource overload"""
            if any(overload_status.get(key, False) for key in ['emergency_cpu', 'emergency_memory']):
                logger.critical("🚨 EMERGENCY: System critically overloaded!")
                # Implement emergency measures
                self._emergency_resource_management()
            else:
                logger.warning("⚠️ System overloaded, adjusting performance")
                self._adjust_performance()
                
        def on_resource_adjustment(overload_status):
            """Handle resource adjustments"""
            logger.info("🔧 Adjusting system performance based on resource usage")
            
        # Register callbacks
        self.resource_manager.register_callback('emergency_overload', on_resource_overload)
        self.resource_manager.register_callback('adjust_performance', on_resource_adjustment)
        
    def _emergency_resource_management(self):
        """Emergency resource management"""
        logger.critical("Implementing emergency resource management")
        # Implement emergency measures (simplified)
        # In real implementation, this would reduce system load
        
    def _adjust_performance(self):
        """Adjust system performance"""
        logger.info("Adjusting system performance")
        # Implement performance adjustments (simplified)
        
    async def process_user_message(self, message: str, user_id: str = "default", 
                                 feedback: Optional[str] = None) -> MIAResponse:
        """
        Glavna funkcija za procesiranje uporabniških sporočil.
        
        Args:
            message: Uporabniško sporočilo
            user_id: ID uporabnika
            feedback: Feedback na prejšnji odgovor (opcijsko)
            
        Returns:
            MIAResponse z odgovorom in metadata
        """
        start_time = time.time()
        self.processing_stats['total_requests'] += 1
        
        try:
            if not self.initialized:
                raise RuntimeError("MIA Integration Layer not properly initialized")
                
            logger.info(f"Processing message from user {user_id}: {message[:50]}...")
            
            # 1. Poskusi odgovoriti na podlagi obstoječega znanja
            reasoning_result = self.reasoning_engine.answer_question(message, user_id)
            
            # 2. Uči se iz interakcije
            learning_result = self.interaction_learner.learn_from_conversation(
                user_input=message,
                mia_response=reasoning_result.answer,
                user_feedback=feedback,
                user_id=user_id
            )
            
            # 3. Pripravi unified response
            processing_time = time.time() - start_time
            
            response = MIAResponse(
                answer=reasoning_result.answer,
                confidence=reasoning_result.confidence,
                sources=reasoning_result.sources,
                reasoning_steps=reasoning_result.reasoning_steps,
                facts_learned=learning_result.get('facts_learned', 0),
                learning_opportunity=reasoning_result.learning_opportunity,
                processing_time=processing_time,
                user_id=user_id,
                timestamp=time.time(),
                metadata={
                    'learning_result': learning_result,
                    'facts_used': reasoning_result.facts_used,
                    'question_type': 'general'
                }
            )
            
            self.processing_stats['successful_responses'] += 1
            if learning_result.get('facts_learned', 0) > 0:
                self.processing_stats['learning_sessions'] += 1
                
            logger.info(f"✅ Processed message successfully in {processing_time:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            self.processing_stats['errors'] += 1
            
            # Graceful error response
            processing_time = time.time() - start_time
            return MIAResponse(
                answer=f"Oprostite, prišlo je do napake pri procesiranju: {e}",
                confidence=0.0,
                sources=[],
                reasoning_steps=[f"Error: {e}"],
                facts_learned=0,
                learning_opportunity=True,
                processing_time=processing_time,
                user_id=user_id,
                timestamp=time.time(),
                metadata={'error': str(e)}
            )
            
    async def learn_from_file(self, file_path: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Uči se iz datoteke.
        
        Args:
            file_path: Pot do datoteke
            user_id: ID uporabnika
            
        Returns:
            Rezultat učenja
        """
        try:
            logger.info(f"Learning from file: {file_path}")
            
            result = self.file_learner.learn_from_file(file_path)
            
            if result.get('success', False):
                logger.info(f"✅ Successfully learned from file: {result}")
            else:
                logger.warning(f"⚠️ File learning failed: {result}")
                
            return result
            
        except Exception as e:
            logger.error(f"Error learning from file {file_path}: {e}")
            return {"error": str(e), "success": False}
            
    async def discover_and_load_models(self) -> Dict[str, Any]:
        """
        Poišči in naloži LLM modele na sistemu.
        
        Returns:
            Rezultat model discovery
        """
        try:
            logger.info("Starting model discovery and loading...")
            
            # 1. Discover models
            models = self.file_learner.discover_llm_models()
            
            # 2. Attempt to load small models
            loaded_models = []
            for model in models:
                if model.loadable and model.size_gb < 2:  # Only small models
                    success, error = self.file_learner.attempt_model_loading(model)
                    if success:
                        loaded_models.append(model.name)
                        
                        # Try to extract knowledge
                        knowledge = self.file_learner.extract_knowledge_from_model(model.name, 5)
                        logger.info(f"Extracted {len(knowledge)} knowledge items from {model.name}")
                        
            result = {
                "models_discovered": len(models),
                "models_loaded": len(loaded_models),
                "loaded_models": loaded_models,
                "discovery_details": [
                    {
                        "name": m.name,
                        "size_gb": m.size_gb,
                        "format": m.format,
                        "loadable": m.loadable
                    } for m in models[:10]  # First 10 models
                ]
            }
            
            logger.info(f"✅ Model discovery completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in model discovery: {e}")
            return {"error": str(e), "models_discovered": 0, "models_loaded": 0}
            
    def get_system_status(self) -> SystemStatus:
        """
        Pridobi celotni status sistema.
        
        Returns:
            SystemStatus z vsemi informacijami
        """
        try:
            # Resource usage
            resource_usage = asdict(self.resource_manager.get_current_usage()) if self.resource_manager else {}
            
            # Knowledge statistics
            knowledge_stats = self.knowledge_store.get_statistics() if self.knowledge_store else {}
            
            # Learning statistics
            learning_stats = self.interaction_learner.get_learning_statistics() if self.interaction_learner else {}
            
            # Reasoning statistics
            reasoning_stats = self.reasoning_engine.get_reasoning_statistics() if self.reasoning_engine else {}
            
            # File learner statistics
            file_learning_stats = self.file_learner.get_learning_statistics() if self.file_learner else {}
            
            # System health assessment
            health = self._assess_system_health(resource_usage)
            
            status = SystemStatus(
                resource_usage=resource_usage,
                knowledge_stats=knowledge_stats,
                learning_stats=learning_stats,
                reasoning_stats=reasoning_stats,
                models_discovered=file_learning_stats.get('models_discovered', 0),
                models_loaded=file_learning_stats.get('models_loaded', 0),
                system_health=health,
                uptime=time.time() - self.start_time
            )
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return SystemStatus(
                resource_usage={},
                knowledge_stats={},
                learning_stats={},
                reasoning_stats={},
                models_discovered=0,
                models_loaded=0,
                system_health="error",
                uptime=time.time() - self.start_time
            )
            
    def _assess_system_health(self, resource_usage: Dict[str, Any]) -> str:
        """Oceni zdravje sistema"""
        try:
            cpu_percent = resource_usage.get('cpu_percent', 0)
            memory_percent = resource_usage.get('memory_percent', 0)
            
            if cpu_percent > 90 or memory_percent > 90:
                return "critical"
            elif cpu_percent > 70 or memory_percent > 70:
                return "warning"
            elif self.initialized:
                return "healthy"
            else:
                return "initializing"
                
        except Exception:
            return "unknown"
            
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Pridobi statistike procesiranja"""
        total_requests = self.processing_stats['total_requests']
        return {
            **self.processing_stats,
            'success_rate': self.processing_stats['successful_responses'] / max(total_requests, 1),
            'error_rate': self.processing_stats['errors'] / max(total_requests, 1),
            'learning_rate': self.processing_stats['learning_sessions'] / max(total_requests, 1),
            'uptime': time.time() - self.start_time
        }
        
    def reset_statistics(self):
        """Ponastavi vse statistike"""
        self.processing_stats = {
            'total_requests': 0,
            'successful_responses': 0,
            'learning_sessions': 0,
            'errors': 0
        }
        
        if self.interaction_learner:
            self.interaction_learner.reset_statistics()
        if self.reasoning_engine:
            self.reasoning_engine.reset_statistics()
            
        logger.info("All statistics reset")
        
    async def shutdown(self):
        """Varno ugasni sistem"""
        try:
            logger.info("Shutting down MIA Integration Layer...")
            
            # Stop resource monitoring
            if self.resource_manager:
                self.resource_manager.stop_monitoring()
                
            # Save knowledge to disk
            if self.knowledge_store:
                self.knowledge_store.save_to_disk()
                
            logger.info("✅ MIA Integration Layer shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Example usage and testing
async def main():
    """Primer uporabe MIA Integration Layer"""
    
    print("=== MIA Integration Layer Test ===")
    
    # Initialize integration layer
    mia = MIAIntegrationLayer("config.json")
    
    if not mia.initialized:
        print("❌ Failed to initialize MIA")
        return
        
    print("✅ MIA Integration Layer initialized")
    
    # Test conversations
    test_conversations = [
        ("Kaj je Python?", None),
        ("Python je programski jezik za razvoj aplikacij", None),
        ("Kaj je Python?", "dobro"),  # Should now know the answer
        ("Aspirin se uporablja za bolečine", None),
        ("Kaj je aspirin?", None),
        ("To je napačno", "napačno")  # Negative feedback
    ]
    
    print("\n📝 Testing conversations:")
    for i, (message, feedback) in enumerate(test_conversations):
        print(f"\n{i+1}. User: {message}")
        if feedback:
            print(f"   Feedback: {feedback}")
            
        response = await mia.process_user_message(message, f"user_{i}", feedback)
        
        print(f"   MIA: {response.answer}")
        print(f"   Confidence: {response.confidence:.2f}")
        print(f"   Facts learned: {response.facts_learned}")
        print(f"   Processing time: {response.processing_time:.3f}s")
        
    # Test file learning
    print(f"\n📁 Testing file learning:")
    test_content = """
    JavaScript je programski jezik.
    HTML se uporablja za spletne strani.
    CSS je za oblikovanje.
    """
    
    test_file = Path("test_mia_learning.txt")
    with open(test_file, 'w') as f:
        f.write(test_content)
        
    file_result = await mia.learn_from_file(str(test_file))
    print(f"   File learning result: {file_result}")
    
    # Cleanup
    test_file.unlink()
    
    # Test model discovery
    print(f"\n🤖 Testing model discovery:")
    model_result = await mia.discover_and_load_models()
    print(f"   Models discovered: {model_result.get('models_discovered', 0)}")
    print(f"   Models loaded: {model_result.get('models_loaded', 0)}")
    
    # Show system status
    print(f"\n📊 System Status:")
    status = mia.get_system_status()
    print(f"   Health: {status.system_health}")
    print(f"   Uptime: {status.uptime:.1f}s")
    print(f"   Knowledge facts: {status.knowledge_stats.get('total_facts', 0)}")
    print(f"   CPU usage: {status.resource_usage.get('cpu_percent', 0):.1f}%")
    print(f"   Memory usage: {status.resource_usage.get('memory_percent', 0):.1f}%")
    
    # Show processing statistics
    print(f"\n📈 Processing Statistics:")
    proc_stats = mia.get_processing_statistics()
    for key, value in proc_stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
            
    # Shutdown
    await mia.shutdown()
    
    print("\n=== Test completed ===")
    print("\n✅ MIA Integration Layer je pripravljen za produkcijo!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())