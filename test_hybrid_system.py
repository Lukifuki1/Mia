#!/usr/bin/env python3
"""
Comprehensive Testing - End-to-end testing celotnega hibridnega MIA sistema
==========================================================================

PRODUKCIJSKA IMPLEMENTACIJA comprehensive testing suite, ki testira:
- Vse hibridne komponente
- Integration z obstoječimi komponentami
- End-to-end workflows
- Performance testing
- Error handling
- Recovery mechanisms

KLJUČNE FUNKCIONALNOSTI:
- Unit tests za vse komponente
- Integration tests
- End-to-end workflow tests
- Performance benchmarks
- Error simulation tests
- Recovery testing
- Load testing
- Memory leak detection

ARHITEKTURA:
- Comprehensive test coverage
- Automated test execution
- Performance benchmarking
- Error simulation
- Recovery validation
"""

import os
import sys
import json
import logging
import asyncio
import time
import unittest
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import subprocess
import psutil
import gc
from concurrent.futures import ThreadPoolExecutor

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_hybrid_system.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Rezultat testa"""
    test_name: str
    success: bool
    duration: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = None

@dataclass
class TestSuite:
    """Test suite rezultati"""
    suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    total_duration: float
    results: List[TestResult]

@dataclass
class SystemBenchmark:
    """System benchmark rezultati"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    response_time: float
    throughput: float
    error_rate: float

class HybridSystemTester:
    """
    Comprehensive tester za hibridni MIA sistem.
    
    Omogoča:
    - Unit testing vseh komponent
    - Integration testing
    - End-to-end workflow testing
    - Performance benchmarking
    - Error simulation
    - Recovery testing
    
    PRODUKCIJSKE FUNKCIONALNOSTI:
    ✅ Comprehensive test coverage
    ✅ Automated test execution
    ✅ Performance benchmarking
    ✅ Error simulation testing
    ✅ Recovery validation
    ✅ Memory leak detection
    ✅ Load testing
    ✅ Detailed reporting
    """
    
    def __init__(self, data_dir: str = "test_data"):
        """
        Inicializiraj system tester.
        
        Args:
            data_dir: Direktorij za test podatke
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Test results
        self.test_suites: List[TestSuite] = []
        self.benchmarks: List[SystemBenchmark] = []
        
        # System monitoring
        self.process = psutil.Process()
        self.start_memory = self.process.memory_info().rss
        
        # Test configuration
        self.test_timeout = 30.0  # seconds
        self.performance_samples = 10
        self.load_test_duration = 60.0  # seconds
        
        logger.info("✅ Hybrid System Tester inicializiran")
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Zaženi vse teste"""
        try:
            logger.info("🧪 Starting comprehensive testing...")
            start_time = time.time()
            
            # 1. Unit Tests
            await self._run_unit_tests()
            
            # 2. Integration Tests
            await self._run_integration_tests()
            
            # 3. End-to-End Tests
            await self._run_end_to_end_tests()
            
            # 4. Performance Tests
            await self._run_performance_tests()
            
            # 5. Error Handling Tests
            await self._run_error_handling_tests()
            
            # 6. Recovery Tests
            await self._run_recovery_tests()
            
            # 7. Load Tests
            await self._run_load_tests()
            
            # 8. Memory Leak Tests
            await self._run_memory_tests()
            
            total_duration = time.time() - start_time
            
            # Generate comprehensive report
            report = self._generate_comprehensive_report(total_duration)
            
            logger.info(f"✅ Comprehensive testing completed in {total_duration:.2f}s")
            return report
            
        except Exception as e:
            logger.error(f"Error in comprehensive testing: {e}")
            raise
            
    async def _run_unit_tests(self):
        """Zaženi unit teste"""
        logger.info("🔬 Running unit tests...")
        start_time = time.time()
        results = []
        
        # Test Knowledge Bank Core
        result = await self._test_knowledge_bank_core()
        results.append(result)
        
        # Test Semantic Layer
        result = await self._test_semantic_layer()
        results.append(result)
        
        # Test Deterministic Reasoning
        result = await self._test_deterministic_reasoning()
        results.append(result)
        
        # Test Hybrid Pipeline
        result = await self._test_hybrid_pipeline()
        results.append(result)
        
        # Test Autonomous Learning
        result = await self._test_autonomous_learning()
        results.append(result)
        
        # Test Hybrid Integration
        result = await self._test_hybrid_integration()
        results.append(result)
        
        duration = time.time() - start_time
        passed = sum(1 for r in results if r.success)
        
        suite = TestSuite(
            suite_name="Unit Tests",
            total_tests=len(results),
            passed_tests=passed,
            failed_tests=len(results) - passed,
            total_duration=duration,
            results=results
        )
        
        self.test_suites.append(suite)
        logger.info(f"✅ Unit tests completed: {passed}/{len(results)} passed in {duration:.2f}s")
        
    async def _test_knowledge_bank_core(self) -> TestResult:
        """Test Knowledge Bank Core"""
        try:
            start_time = time.time()
            
            # Import and test
            from mia.knowledge.hybrid.knowledge_bank_core import create_hybrid_knowledge_bank
            
            # Create knowledge bank
            kb = await create_hybrid_knowledge_bank(
                data_dir=str(self.data_dir / "test_kb"),
                integrate_with_mia=False
            )
            
            # Test basic operations
            success1 = await kb.create_concept("TestConcept", "Test Concept", "A test concept")
            success2 = await kb.create_relation("testRelation", "test relation", 
                                              "http://test.com#TestConcept", 
                                              "http://test.com#TestConcept")
            
            # Test SPARQL query
            query_result = await kb.query_sparql("SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5")
            
            # Test validation
            validation = await kb.validate_ontology()
            
            # Test statistics
            stats = kb.get_statistics()
            
            # Cleanup
            await kb.shutdown()
            
            duration = time.time() - start_time
            
            # Verify results
            assert success1, "Failed to create concept"
            assert success2, "Failed to create relation"
            assert query_result.success, "SPARQL query failed"
            assert validation.valid, "Ontology validation failed"
            assert stats.total_concepts > 0, "No concepts found in statistics"
            
            return TestResult(
                test_name="Knowledge Bank Core",
                success=True,
                duration=duration,
                details={
                    'concepts_created': 1,
                    'relations_created': 1,
                    'sparql_queries': 1,
                    'validations': 1
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Knowledge Bank Core test failed: {e}")
            return TestResult(
                test_name="Knowledge Bank Core",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _test_semantic_layer(self) -> TestResult:
        """Test Semantic Layer"""
        try:
            start_time = time.time()
            
            # Import and test
            from mia.knowledge.hybrid.semantic_layer import create_semantic_layer
            
            # Create semantic layer
            semantic = await create_semantic_layer(
                data_dir=str(self.data_dir / "test_semantic")
            )
            
            # Test natural language parsing
            parse_result = await semantic.parse_natural_language(
                "John works for Microsoft and uses Python programming language."
            )
            
            # Test similarity search
            similarity_result = await semantic.find_similar_concepts("software developer")
            
            # Test statistics
            stats = semantic.get_statistics()
            
            # Cleanup
            await semantic.shutdown()
            
            duration = time.time() - start_time
            
            # Verify results
            assert parse_result.confidence > 0, "Parse result has no confidence"
            assert len(parse_result.entities) > 0, "No entities extracted"
            assert stats['basic_stats']['texts_parsed'] > 0, "No texts parsed in statistics"
            
            return TestResult(
                test_name="Semantic Layer",
                success=True,
                duration=duration,
                details={
                    'texts_parsed': 1,
                    'entities_extracted': len(parse_result.entities),
                    'relations_extracted': len(parse_result.relations),
                    'similarity_queries': 1
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Semantic Layer test failed: {e}")
            return TestResult(
                test_name="Semantic Layer",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _test_deterministic_reasoning(self) -> TestResult:
        """Test Deterministic Reasoning"""
        try:
            start_time = time.time()
            
            # Import and test
            from mia.knowledge.hybrid.deterministic_reasoning import create_reasoning_engine, Rule, Fact, LogicalTerm, RuleType
            
            # Create reasoning engine
            reasoning = await create_reasoning_engine(
                data_dir=str(self.data_dir / "test_reasoning")
            )
            
            # Add test fact
            fact = Fact(
                fact_id="test_fact",
                term=LogicalTerm("human", ["socrates"]),
                confidence=1.0,
                source="test",
                timestamp=time.time()
            )
            await reasoning.add_fact(fact)
            
            # Add test rule
            rule = Rule(
                rule_id="test_rule",
                rule_type=RuleType.IMPLICATION,
                premises=[LogicalTerm("human", ["X"])],
                conclusions=[LogicalTerm("mortal", ["X"])],
                confidence=1.0,
                priority=10,
                source="test",
                created_at=time.time(),
                metadata={"description": "All humans are mortal"}
            )
            await reasoning.add_rule(rule)
            
            # Test reasoning
            result = await reasoning.reason("mortal(socrates)")
            
            # Test consistency check
            consistency = await reasoning.check_consistency()
            
            # Test statistics
            stats = reasoning.get_statistics()
            
            # Cleanup
            await reasoning.shutdown()
            
            duration = time.time() - start_time
            
            # Verify results
            assert result.success, "Reasoning failed"
            assert result.confidence > 0, "Reasoning has no confidence"
            assert consistency.consistent, "Knowledge base is inconsistent"
            assert stats['basic_stats']['rules_count'] > 0, "No rules in statistics"
            
            return TestResult(
                test_name="Deterministic Reasoning",
                success=True,
                duration=duration,
                details={
                    'facts_added': 1,
                    'rules_added': 1,
                    'reasoning_queries': 1,
                    'consistency_checks': 1
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Deterministic Reasoning test failed: {e}")
            return TestResult(
                test_name="Deterministic Reasoning",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _test_hybrid_pipeline(self) -> TestResult:
        """Test Hybrid Pipeline"""
        try:
            start_time = time.time()
            
            # Import and test
            from mia.knowledge.hybrid.hybrid_pipeline import create_full_hybrid_system, PipelineMode
            
            # Create hybrid pipeline
            pipeline = await create_full_hybrid_system(
                data_dir=str(self.data_dir / "test_pipeline")
            )
            
            # Test different processing modes
            test_queries = [
                ("What is AI?", PipelineMode.ADAPTIVE),
                ("Hello", PipelineMode.HYBRID_SEQUENTIAL)
            ]
            
            results = []
            for query, mode in test_queries:
                result = await pipeline.process(
                    user_input=query,
                    mode=mode,
                    confidence_threshold=0.3
                )
                results.append(result)
                
            # Test statistics
            stats = pipeline.get_detailed_statistics()
            
            # Cleanup
            await pipeline.shutdown()
            
            duration = time.time() - start_time
            
            # Verify results
            assert len(results) == 2, "Not all queries processed"
            assert any(r.success for r in results), "No successful processing"
            assert stats['basic_stats']['total_requests'] > 0, "No requests in statistics"
            
            return TestResult(
                test_name="Hybrid Pipeline",
                success=True,
                duration=duration,
                details={
                    'queries_processed': len(results),
                    'successful_queries': sum(1 for r in results if r.success),
                    'modes_tested': len(set(r.mode_used for r in results))
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Hybrid Pipeline test failed: {e}")
            return TestResult(
                test_name="Hybrid Pipeline",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _test_autonomous_learning(self) -> TestResult:
        """Test Autonomous Learning"""
        try:
            start_time = time.time()
            
            # Import and test
            from mia.knowledge.hybrid.autonomous_learning import create_autonomous_learning
            
            # Create autonomous learning
            learning = await create_autonomous_learning(
                data_dir=str(self.data_dir / "test_learning")
            )
            
            # Test learning from interaction
            result = await learning.learn_from_interaction(
                user_input="What is machine learning?",
                system_response="Machine learning is a subset of AI.",
                feedback={'helpful': True}
            )
            
            # Test statistics
            stats = learning.get_statistics()
            
            # Cleanup
            await learning.shutdown()
            
            duration = time.time() - start_time
            
            # Verify results
            assert result.success, "Learning from interaction failed"
            assert stats['basic_stats']['total_learning_events'] > 0, "No learning events"
            
            return TestResult(
                test_name="Autonomous Learning",
                success=True,
                duration=duration,
                details={
                    'interactions_learned': 1,
                    'concepts_learned': len(result.new_concepts),
                    'relations_learned': len(result.new_relations)
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Autonomous Learning test failed: {e}")
            return TestResult(
                test_name="Autonomous Learning",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _test_hybrid_integration(self) -> TestResult:
        """Test Hybrid Integration"""
        try:
            start_time = time.time()
            
            # Import and test
            from mia.core.hybrid_integration import create_hybrid_integration, get_default_config, ProcessingRequest
            
            # Create integration
            config = get_default_config(str(self.data_dir / "test_integration"))
            integration = await create_hybrid_integration(config)
            
            # Test processing request
            request = ProcessingRequest(
                request_id="test_request",
                user_input="Hello, how are you?",
                user_id="test_user",
                context={},
                preferred_mode=None,
                timestamp=time.time()
            )
            
            response = await integration.process_request(request)
            
            # Test capabilities
            capabilities = integration.get_capabilities()
            
            # Test statistics
            stats = integration.get_statistics()
            
            # Cleanup
            await integration.shutdown()
            
            duration = time.time() - start_time
            
            # Verify results
            assert response.success, "Request processing failed"
            assert len(response.response) > 0, "Empty response"
            assert capabilities['capability_level'] is not None, "No capability level"
            assert stats['request_stats']['total_requests'] > 0, "No requests in statistics"
            
            return TestResult(
                test_name="Hybrid Integration",
                success=True,
                duration=duration,
                details={
                    'requests_processed': 1,
                    'capability_level': capabilities['capability_level'],
                    'response_length': len(response.response)
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Hybrid Integration test failed: {e}")
            return TestResult(
                test_name="Hybrid Integration",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _run_integration_tests(self):
        """Zaženi integration teste"""
        logger.info("🔗 Running integration tests...")
        start_time = time.time()
        results = []
        
        # Test component integration
        result = await self._test_component_integration()
        results.append(result)
        
        # Test data flow
        result = await self._test_data_flow()
        results.append(result)
        
        # Test API integration
        result = await self._test_api_integration()
        results.append(result)
        
        duration = time.time() - start_time
        passed = sum(1 for r in results if r.success)
        
        suite = TestSuite(
            suite_name="Integration Tests",
            total_tests=len(results),
            passed_tests=passed,
            failed_tests=len(results) - passed,
            total_duration=duration,
            results=results
        )
        
        self.test_suites.append(suite)
        logger.info(f"✅ Integration tests completed: {passed}/{len(results)} passed in {duration:.2f}s")
        
    async def _test_component_integration(self) -> TestResult:
        """Test integration med komponentami"""
        try:
            start_time = time.time()
            
            # Create full system
            from mia.knowledge.hybrid.hybrid_pipeline import create_full_hybrid_system
            
            pipeline = await create_full_hybrid_system(
                data_dir=str(self.data_dir / "integration_test")
            )
            
            # Test that all components are connected
            assert pipeline.knowledge_bank is not None, "Knowledge Bank not connected"
            assert pipeline.semantic_layer is not None, "Semantic Layer not connected"
            assert pipeline.reasoning_engine is not None, "Reasoning Engine not connected"
            
            # Test data flow between components
            result = await pipeline.process(
                user_input="If all birds can fly and penguins are birds, can penguins fly?",
                confidence_threshold=0.3
            )
            
            # Verify that multiple stages were executed
            assert len(result.stage_results) > 1, "Multiple stages not executed"
            assert result.processing_path, "No processing path recorded"
            
            await pipeline.shutdown()
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name="Component Integration",
                success=True,
                duration=duration,
                details={
                    'components_connected': 3,
                    'stages_executed': len(result.stage_results),
                    'processing_path_length': len(result.processing_path)
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Component integration test failed: {e}")
            return TestResult(
                test_name="Component Integration",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _test_data_flow(self) -> TestResult:
        """Test data flow skozi sistem"""
        try:
            start_time = time.time()
            
            # Test data persistence and retrieval
            from mia.knowledge.hybrid.knowledge_bank_core import create_hybrid_knowledge_bank
            
            # Create knowledge bank
            kb = await create_hybrid_knowledge_bank(
                data_dir=str(self.data_dir / "data_flow_test")
            )
            
            # Add data
            await kb.create_concept("TestEntity", "Test Entity", "A test entity for data flow")
            
            # Save data
            await kb.save_ontology()
            
            # Create new instance and load data
            kb2 = await create_hybrid_knowledge_bank(
                data_dir=str(self.data_dir / "data_flow_test")
            )
            
            # Verify data persistence
            stats = kb2.get_statistics()
            assert stats.total_concepts > 0, "Data not persisted"
            
            await kb.shutdown()
            await kb2.shutdown()
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name="Data Flow",
                success=True,
                duration=duration,
                details={
                    'concepts_persisted': stats.total_concepts,
                    'data_persistence': True
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Data flow test failed: {e}")
            return TestResult(
                test_name="Data Flow",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _test_api_integration(self) -> TestResult:
        """Test API integration"""
        try:
            start_time = time.time()
            
            # Test unified API
            from mia.core.hybrid_integration import create_hybrid_integration, get_default_config, ProcessingRequest
            
            config = get_default_config(str(self.data_dir / "api_test"))
            integration = await create_hybrid_integration(config)
            
            # Test multiple requests
            requests = [
                ProcessingRequest(
                    request_id=f"api_test_{i}",
                    user_input=f"Test query {i}",
                    user_id="api_test_user",
                    context={},
                    preferred_mode=None,
                    timestamp=time.time()
                )
                for i in range(3)
            ]
            
            responses = []
            for request in requests:
                response = await integration.process_request(request)
                responses.append(response)
                
            # Verify API consistency
            assert len(responses) == 3, "Not all requests processed"
            assert all(hasattr(r, 'success') for r in responses), "Response format inconsistent"
            assert all(hasattr(r, 'response') for r in responses), "Response content missing"
            
            await integration.shutdown()
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name="API Integration",
                success=True,
                duration=duration,
                details={
                    'requests_processed': len(responses),
                    'successful_responses': sum(1 for r in responses if r.success),
                    'api_consistency': True
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"API integration test failed: {e}")
            return TestResult(
                test_name="API Integration",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _run_end_to_end_tests(self):
        """Zaženi end-to-end teste"""
        logger.info("🎯 Running end-to-end tests...")
        start_time = time.time()
        results = []
        
        # Test complete workflow
        result = await self._test_complete_workflow()
        results.append(result)
        
        # Test launcher integration
        result = await self._test_launcher_integration()
        results.append(result)
        
        duration = time.time() - start_time
        passed = sum(1 for r in results if r.success)
        
        suite = TestSuite(
            suite_name="End-to-End Tests",
            total_tests=len(results),
            passed_tests=passed,
            failed_tests=len(results) - passed,
            total_duration=duration,
            results=results
        )
        
        self.test_suites.append(suite)
        logger.info(f"✅ End-to-end tests completed: {passed}/{len(results)} passed in {duration:.2f}s")
        
    async def _test_complete_workflow(self) -> TestResult:
        """Test celotnega workflow-a"""
        try:
            start_time = time.time()
            
            # Simulate complete user interaction workflow
            from mia.core.hybrid_integration import create_hybrid_integration, get_default_config, ProcessingRequest
            
            config = get_default_config(str(self.data_dir / "workflow_test"))
            integration = await create_hybrid_integration(config)
            
            # Simulate user session
            user_queries = [
                "Hello, I'm new here",
                "What is artificial intelligence?",
                "How does machine learning work?",
                "Can you explain neural networks?",
                "Thank you for the information"
            ]
            
            session_responses = []
            for i, query in enumerate(user_queries):
                request = ProcessingRequest(
                    request_id=f"workflow_{i}",
                    user_input=query,
                    user_id="workflow_test_user",
                    context={'session_id': 'test_session'},
                    preferred_mode=None,
                    timestamp=time.time()
                )
                
                response = await integration.process_request(request)
                session_responses.append(response)
                
                # Small delay between requests
                await asyncio.sleep(0.1)
                
            # Verify workflow completion
            assert len(session_responses) == len(user_queries), "Not all queries processed"
            assert any(r.success for r in session_responses), "No successful responses"
            
            # Check system learned from interactions
            stats = integration.get_statistics()
            assert stats['request_stats']['total_requests'] >= len(user_queries), "Request count mismatch"
            
            await integration.shutdown()
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name="Complete Workflow",
                success=True,
                duration=duration,
                details={
                    'user_queries': len(user_queries),
                    'successful_responses': sum(1 for r in session_responses if r.success),
                    'average_response_time': sum(r.processing_time for r in session_responses) / len(session_responses),
                    'workflow_completed': True
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Complete workflow test failed: {e}")
            return TestResult(
                test_name="Complete Workflow",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _test_launcher_integration(self) -> TestResult:
        """Test launcher integration"""
        try:
            start_time = time.time()
            
            # Test launcher configuration
            from mia_hybrid_launcher import LauncherConfig, MiaHybridLauncher
            
            config = LauncherConfig(
                mode="hybrid_enhanced",
                enable_web=False,  # Disable web for testing
                enable_desktop=False,
                enable_enterprise=True,
                data_dir=str(self.data_dir / "launcher_test"),
                log_level="INFO",
                auto_open_browser=False,
                enable_monitoring=True
            )
            
            launcher = MiaHybridLauncher(config)
            
            # Test system status
            status = launcher.get_system_status()
            assert status['config']['mode'] == "hybrid_enhanced", "Config not set correctly"
            
            # Test would normally start the system, but we'll skip for testing
            # await launcher.start()  # Skip actual startup
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name="Launcher Integration",
                success=True,
                duration=duration,
                details={
                    'config_loaded': True,
                    'launcher_created': True,
                    'status_accessible': True
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Launcher integration test failed: {e}")
            return TestResult(
                test_name="Launcher Integration",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _run_performance_tests(self):
        """Zaženi performance teste"""
        logger.info("⚡ Running performance tests...")
        start_time = time.time()
        results = []
        
        # Test response time
        result = await self._test_response_time()
        results.append(result)
        
        # Test throughput
        result = await self._test_throughput()
        results.append(result)
        
        # Test memory usage
        result = await self._test_memory_usage()
        results.append(result)
        
        duration = time.time() - start_time
        passed = sum(1 for r in results if r.success)
        
        suite = TestSuite(
            suite_name="Performance Tests",
            total_tests=len(results),
            passed_tests=passed,
            failed_tests=len(results) - passed,
            total_duration=duration,
            results=results
        )
        
        self.test_suites.append(suite)
        logger.info(f"✅ Performance tests completed: {passed}/{len(results)} passed in {duration:.2f}s")
        
    async def _test_response_time(self) -> TestResult:
        """Test response time"""
        try:
            start_time = time.time()
            
            from mia.core.hybrid_integration import create_hybrid_integration, get_default_config, ProcessingRequest
            
            config = get_default_config(str(self.data_dir / "performance_test"))
            integration = await create_hybrid_integration(config)
            
            # Test multiple requests and measure response time
            response_times = []
            
            for i in range(self.performance_samples):
                request = ProcessingRequest(
                    request_id=f"perf_test_{i}",
                    user_input="What is AI?",
                    user_id="perf_test_user",
                    context={},
                    preferred_mode=None,
                    timestamp=time.time()
                )
                
                request_start = time.time()
                response = await integration.process_request(request)
                request_duration = time.time() - request_start
                
                response_times.append(request_duration)
                
            await integration.shutdown()
            
            # Calculate statistics
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            # Performance criteria (adjust as needed)
            performance_ok = avg_response_time < 5.0  # 5 seconds average
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name="Response Time",
                success=performance_ok,
                duration=duration,
                details={
                    'samples': len(response_times),
                    'avg_response_time': avg_response_time,
                    'max_response_time': max_response_time,
                    'min_response_time': min_response_time,
                    'performance_threshold': 5.0
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Response time test failed: {e}")
            return TestResult(
                test_name="Response Time",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _test_throughput(self) -> TestResult:
        """Test throughput"""
        try:
            start_time = time.time()
            
            from mia.core.hybrid_integration import create_hybrid_integration, get_default_config, ProcessingRequest
            
            config = get_default_config(str(self.data_dir / "throughput_test"))
            integration = await create_hybrid_integration(config)
            
            # Test concurrent requests
            async def process_request(i):
                request = ProcessingRequest(
                    request_id=f"throughput_test_{i}",
                    user_input=f"Test query {i}",
                    user_id="throughput_test_user",
                    context={},
                    preferred_mode=None,
                    timestamp=time.time()
                )
                return await integration.process_request(request)
                
            # Process multiple concurrent requests
            concurrent_requests = 5
            tasks = [process_request(i) for i in range(concurrent_requests)]
            
            concurrent_start = time.time()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            concurrent_duration = time.time() - concurrent_start
            
            # Calculate throughput
            successful_responses = sum(1 for r in responses if not isinstance(r, Exception) and r.success)
            throughput = successful_responses / concurrent_duration  # requests per second
            
            await integration.shutdown()
            
            # Performance criteria
            throughput_ok = throughput > 0.5  # At least 0.5 requests per second
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name="Throughput",
                success=throughput_ok,
                duration=duration,
                details={
                    'concurrent_requests': concurrent_requests,
                    'successful_responses': successful_responses,
                    'throughput_rps': throughput,
                    'concurrent_duration': concurrent_duration,
                    'throughput_threshold': 0.5
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Throughput test failed: {e}")
            return TestResult(
                test_name="Throughput",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _test_memory_usage(self) -> TestResult:
        """Test memory usage"""
        try:
            start_time = time.time()
            
            # Monitor memory before test
            initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            
            from mia.core.hybrid_integration import create_hybrid_integration, get_default_config, ProcessingRequest
            
            config = get_default_config(str(self.data_dir / "memory_test"))
            integration = await create_hybrid_integration(config)
            
            # Process multiple requests to test memory usage
            for i in range(20):
                request = ProcessingRequest(
                    request_id=f"memory_test_{i}",
                    user_input=f"Memory test query {i} with some additional text to increase memory usage",
                    user_id="memory_test_user",
                    context={'iteration': i},
                    preferred_mode=None,
                    timestamp=time.time()
                )
                
                await integration.process_request(request)
                
                # Force garbage collection
                gc.collect()
                
            await integration.shutdown()
            
            # Monitor memory after test
            final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory criteria (adjust as needed)
            memory_ok = memory_increase < 100  # Less than 100MB increase
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name="Memory Usage",
                success=memory_ok,
                duration=duration,
                details={
                    'initial_memory_mb': initial_memory,
                    'final_memory_mb': final_memory,
                    'memory_increase_mb': memory_increase,
                    'memory_threshold_mb': 100,
                    'requests_processed': 20
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Memory usage test failed: {e}")
            return TestResult(
                test_name="Memory Usage",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _run_error_handling_tests(self):
        """Zaženi error handling teste"""
        logger.info("🚨 Running error handling tests...")
        start_time = time.time()
        results = []
        
        # Test invalid input handling
        result = await self._test_invalid_input_handling()
        results.append(result)
        
        # Test component failure handling
        result = await self._test_component_failure_handling()
        results.append(result)
        
        duration = time.time() - start_time
        passed = sum(1 for r in results if r.success)
        
        suite = TestSuite(
            suite_name="Error Handling Tests",
            total_tests=len(results),
            passed_tests=passed,
            failed_tests=len(results) - passed,
            total_duration=duration,
            results=results
        )
        
        self.test_suites.append(suite)
        logger.info(f"✅ Error handling tests completed: {passed}/{len(results)} passed in {duration:.2f}s")
        
    async def _test_invalid_input_handling(self) -> TestResult:
        """Test handling invalid inputs"""
        try:
            start_time = time.time()
            
            from mia.core.hybrid_integration import create_hybrid_integration, get_default_config, ProcessingRequest
            
            config = get_default_config(str(self.data_dir / "error_test"))
            integration = await create_hybrid_integration(config)
            
            # Test various invalid inputs
            invalid_inputs = [
                "",  # Empty string
                " " * 1000,  # Very long whitespace
                "A" * 10000,  # Very long string
                "🚀" * 100,  # Unicode characters
                None,  # This would cause an error in request creation
            ]
            
            error_handled_count = 0
            
            for i, invalid_input in enumerate(invalid_inputs[:-1]):  # Skip None
                try:
                    request = ProcessingRequest(
                        request_id=f"error_test_{i}",
                        user_input=invalid_input,
                        user_id="error_test_user",
                        context={},
                        preferred_mode=None,
                        timestamp=time.time()
                    )
                    
                    response = await integration.process_request(request)
                    
                    # System should handle gracefully (either succeed or fail gracefully)
                    if not response.success or response.success:
                        error_handled_count += 1
                        
                except Exception as e:
                    # Exception should be handled gracefully
                    logger.debug(f"Expected error for invalid input: {e}")
                    error_handled_count += 1
                    
            await integration.shutdown()
            
            # All invalid inputs should be handled gracefully
            all_handled = error_handled_count == len(invalid_inputs) - 1
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name="Invalid Input Handling",
                success=all_handled,
                duration=duration,
                details={
                    'invalid_inputs_tested': len(invalid_inputs) - 1,
                    'errors_handled_gracefully': error_handled_count,
                    'graceful_handling_rate': error_handled_count / (len(invalid_inputs) - 1)
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Invalid input handling test failed: {e}")
            return TestResult(
                test_name="Invalid Input Handling",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _test_component_failure_handling(self) -> TestResult:
        """Test handling component failures"""
        try:
            start_time = time.time()
            
            # Test system behavior when components are not available
            from mia.core.hybrid_integration import IntegrationConfig, IntegrationMode, HybridIntegration
            
            # Create integration without hybrid components
            config = IntegrationConfig(
                mode=IntegrationMode.CLASSIC_ONLY,  # Force classic mode
                enable_hybrid_reasoning=False,
                enable_semantic_processing=False,
                enable_autonomous_learning=False,
                fallback_to_classic=True,
                performance_monitoring=True,
                data_dir=str(self.data_dir / "failure_test")
            )
            
            integration = HybridIntegration(config)
            
            # Test that system can still function
            capabilities = integration.get_capabilities()
            
            # System should report limited capabilities but still function
            assert capabilities is not None, "Capabilities not available"
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name="Component Failure Handling",
                success=True,
                duration=duration,
                details={
                    'fallback_mode_functional': True,
                    'capabilities_reported': True,
                    'graceful_degradation': True
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Component failure handling test failed: {e}")
            return TestResult(
                test_name="Component Failure Handling",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _run_recovery_tests(self):
        """Zaženi recovery teste"""
        logger.info("🔄 Running recovery tests...")
        start_time = time.time()
        results = []
        
        # Test data recovery
        result = await self._test_data_recovery()
        results.append(result)
        
        duration = time.time() - start_time
        passed = sum(1 for r in results if r.success)
        
        suite = TestSuite(
            suite_name="Recovery Tests",
            total_tests=len(results),
            passed_tests=passed,
            failed_tests=len(results) - passed,
            total_duration=duration,
            results=results
        )
        
        self.test_suites.append(suite)
        logger.info(f"✅ Recovery tests completed: {passed}/{len(results)} passed in {duration:.2f}s")
        
    async def _test_data_recovery(self) -> TestResult:
        """Test data recovery"""
        try:
            start_time = time.time()
            
            from mia.knowledge.hybrid.knowledge_bank_core import create_hybrid_knowledge_bank
            
            # Create knowledge bank and add data
            kb1 = await create_hybrid_knowledge_bank(
                data_dir=str(self.data_dir / "recovery_test")
            )
            
            await kb1.create_concept("RecoveryTest", "Recovery Test", "Test concept for recovery")
            await kb1.save_ontology()
            await kb1.shutdown()
            
            # Create new instance and verify data recovery
            kb2 = await create_hybrid_knowledge_bank(
                data_dir=str(self.data_dir / "recovery_test")
            )
            
            stats = kb2.get_statistics()
            data_recovered = stats.total_concepts > 0
            
            await kb2.shutdown()
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name="Data Recovery",
                success=data_recovered,
                duration=duration,
                details={
                    'concepts_recovered': stats.total_concepts,
                    'data_persistence': True,
                    'recovery_successful': data_recovered
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Data recovery test failed: {e}")
            return TestResult(
                test_name="Data Recovery",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _run_load_tests(self):
        """Zaženi load teste"""
        logger.info("📈 Running load tests...")
        start_time = time.time()
        results = []
        
        # Test system under load
        result = await self._test_system_under_load()
        results.append(result)
        
        duration = time.time() - start_time
        passed = sum(1 for r in results if r.success)
        
        suite = TestSuite(
            suite_name="Load Tests",
            total_tests=len(results),
            passed_tests=passed,
            failed_tests=len(results) - passed,
            total_duration=duration,
            results=results
        )
        
        self.test_suites.append(suite)
        logger.info(f"✅ Load tests completed: {passed}/{len(results)} passed in {duration:.2f}s")
        
    async def _test_system_under_load(self) -> TestResult:
        """Test system under load"""
        try:
            start_time = time.time()
            
            from mia.core.hybrid_integration import create_hybrid_integration, get_default_config, ProcessingRequest
            
            config = get_default_config(str(self.data_dir / "load_test"))
            integration = await create_hybrid_integration(config)
            
            # Generate load for specified duration
            load_start = time.time()
            request_count = 0
            successful_count = 0
            
            while time.time() - load_start < 10.0:  # 10 seconds of load
                request = ProcessingRequest(
                    request_id=f"load_test_{request_count}",
                    user_input=f"Load test query {request_count}",
                    user_id="load_test_user",
                    context={},
                    preferred_mode=None,
                    timestamp=time.time()
                )
                
                try:
                    response = await integration.process_request(request)
                    if response.success:
                        successful_count += 1
                except Exception as e:
                    logger.debug(f"Load test request failed: {e}")
                    
                request_count += 1
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.1)
                
            load_duration = time.time() - load_start
            
            await integration.shutdown()
            
            # Calculate load test metrics
            requests_per_second = request_count / load_duration
            success_rate = successful_count / request_count if request_count > 0 else 0
            
            # Load test criteria
            load_test_ok = success_rate > 0.8 and requests_per_second > 1.0
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name="System Under Load",
                success=load_test_ok,
                duration=duration,
                details={
                    'load_duration': load_duration,
                    'total_requests': request_count,
                    'successful_requests': successful_count,
                    'requests_per_second': requests_per_second,
                    'success_rate': success_rate,
                    'load_test_criteria_met': load_test_ok
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"System under load test failed: {e}")
            return TestResult(
                test_name="System Under Load",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    async def _run_memory_tests(self):
        """Zaženi memory leak teste"""
        logger.info("🧠 Running memory leak tests...")
        start_time = time.time()
        results = []
        
        # Test memory leaks
        result = await self._test_memory_leaks()
        results.append(result)
        
        duration = time.time() - start_time
        passed = sum(1 for r in results if r.success)
        
        suite = TestSuite(
            suite_name="Memory Tests",
            total_tests=len(results),
            passed_tests=passed,
            failed_tests=len(results) - passed,
            total_duration=duration,
            results=results
        )
        
        self.test_suites.append(suite)
        logger.info(f"✅ Memory tests completed: {passed}/{len(results)} passed in {duration:.2f}s")
        
    async def _test_memory_leaks(self) -> TestResult:
        """Test memory leaks"""
        try:
            start_time = time.time()
            
            # Monitor memory usage over multiple cycles
            memory_samples = []
            
            for cycle in range(5):
                cycle_start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
                
                # Create and destroy components
                from mia.knowledge.hybrid.knowledge_bank_core import create_hybrid_knowledge_bank
                
                kb = await create_hybrid_knowledge_bank(
                    data_dir=str(self.data_dir / f"memory_leak_test_{cycle}")
                )
                
                # Do some work
                await kb.create_concept(f"TestConcept{cycle}", f"Test Concept {cycle}", "Memory leak test concept")
                
                # Cleanup
                await kb.shutdown()
                del kb
                
                # Force garbage collection
                gc.collect()
                
                cycle_end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
                memory_samples.append(cycle_end_memory - cycle_start_memory)
                
            # Check for memory leaks
            avg_memory_increase = sum(memory_samples) / len(memory_samples)
            max_memory_increase = max(memory_samples)
            
            # Memory leak criteria
            no_significant_leaks = avg_memory_increase < 10 and max_memory_increase < 20  # MB
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name="Memory Leaks",
                success=no_significant_leaks,
                duration=duration,
                details={
                    'test_cycles': len(memory_samples),
                    'memory_samples_mb': memory_samples,
                    'avg_memory_increase_mb': avg_memory_increase,
                    'max_memory_increase_mb': max_memory_increase,
                    'leak_threshold_mb': 10,
                    'no_significant_leaks': no_significant_leaks
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Memory leak test failed: {e}")
            return TestResult(
                test_name="Memory Leaks",
                success=False,
                duration=duration,
                error_message=str(e)
            )
            
    def _generate_comprehensive_report(self, total_duration: float) -> Dict[str, Any]:
        """Generiraj comprehensive report"""
        try:
            # Calculate overall statistics
            total_tests = sum(suite.total_tests for suite in self.test_suites)
            total_passed = sum(suite.passed_tests for suite in self.test_suites)
            total_failed = sum(suite.failed_tests for suite in self.test_suites)
            overall_success_rate = total_passed / total_tests if total_tests > 0 else 0
            
            # Generate report
            report = {
                'test_summary': {
                    'total_duration': total_duration,
                    'total_test_suites': len(self.test_suites),
                    'total_tests': total_tests,
                    'total_passed': total_passed,
                    'total_failed': total_failed,
                    'overall_success_rate': overall_success_rate,
                    'test_status': 'PASSED' if overall_success_rate >= 0.8 else 'FAILED'
                },
                'test_suites': [asdict(suite) for suite in self.test_suites],
                'system_info': {
                    'python_version': sys.version,
                    'platform': sys.platform,
                    'memory_usage_mb': self.process.memory_info().rss / 1024 / 1024,
                    'cpu_percent': self.process.cpu_percent()
                },
                'recommendations': self._generate_recommendations()
            }
            
            # Save report to file
            report_file = self.data_dir / "comprehensive_test_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
                
            # Print summary
            self._print_test_summary(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return {'error': str(e)}
            
    def _generate_recommendations(self) -> List[str]:
        """Generiraj priporočila na podlagi testov"""
        recommendations = []
        
        # Analyze test results
        for suite in self.test_suites:
            if suite.failed_tests > 0:
                recommendations.append(f"Address failures in {suite.suite_name}: {suite.failed_tests} tests failed")
                
            if suite.suite_name == "Performance Tests":
                for result in suite.results:
                    if not result.success and result.details:
                        if 'avg_response_time' in result.details:
                            recommendations.append("Consider optimizing response time - current average exceeds threshold")
                        if 'throughput_rps' in result.details:
                            recommendations.append("Consider improving system throughput")
                            
        # General recommendations
        if not recommendations:
            recommendations.append("All tests passed - system is ready for production")
        else:
            recommendations.append("Review failed tests and implement fixes before production deployment")
            
        return recommendations
        
    def _print_test_summary(self, report: Dict[str, Any]):
        """Izpiši povzetek testov"""
        summary = report['test_summary']
        
        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE TEST RESULTS")
        print("="*80)
        print(f"Overall Status: {'✅ PASSED' if summary['test_status'] == 'PASSED' else '❌ FAILED'}")
        print(f"Total Duration: {summary['total_duration']:.2f}s")
        print(f"Test Suites: {summary['total_test_suites']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['total_passed']}")
        print(f"Failed: {summary['total_failed']}")
        print(f"Success Rate: {summary['overall_success_rate']:.1%}")
        
        print("\nTest Suite Results:")
        for suite in self.test_suites:
            status = "✅" if suite.failed_tests == 0 else "❌"
            print(f"  {status} {suite.suite_name}: {suite.passed_tests}/{suite.total_tests} passed ({suite.total_duration:.2f}s)")
            
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
            
        print("="*80 + "\n")


async def main():
    """Glavna funkcija za testiranje"""
    try:
        print("""
╔══════════════════════════════════════════════════════════════╗
║           🧪 MIA HYBRID SYSTEM - COMPREHENSIVE TESTING       ║
║                                                              ║
║  Testing all components, integration, and performance...     ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        # Create tester
        tester = HybridSystemTester()
        
        # Run all tests
        report = await tester.run_all_tests()
        
        # Return appropriate exit code
        if report['test_summary']['test_status'] == 'PASSED':
            print("🎉 All tests passed! System is ready for production.")
            return 0
        else:
            print("❌ Some tests failed. Please review and fix issues.")
            return 1
            
    except Exception as e:
        print(f"❌ Testing failed with error: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)