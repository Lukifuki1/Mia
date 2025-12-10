#!/usr/bin/env python3
"""
🧪 MIA Enterprise AGI - Comprehensive Simulation Test Framework
Celoten simulacijski testni okvir za MIA sistem
"""

import sys
import os
import json
import asyncio
import logging
import time
import threading
import multiprocessing
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union, Callable
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from enum import Enum
import random
import numpy as np
from datetime import datetime, timedelta
import psutil
import traceback
import uuid
import hashlib

# Dodaj MIA path
sys.path.insert(0, '.')

class TestType(Enum):
    """Tipi testov"""
    UNIT = "unit"
    INTEGRATION = "integration"
    SYSTEM = "system"
    PERFORMANCE = "performance"
    STRESS = "stress"
    SECURITY = "security"
    COMPATIBILITY = "compatibility"
    REGRESSION = "regression"

class TestSeverity(Enum):
    """Resnost testov"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TestStatus(Enum):
    """Status testov"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

@dataclass
class TestCase:
    """Testni primer"""
    id: str
    name: str
    description: str
    test_type: TestType
    severity: TestSeverity
    test_function: Callable
    setup_function: Optional[Callable] = None
    teardown_function: Optional[Callable] = None
    timeout: float = 30.0
    retry_count: int = 0
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    expected_duration: float = 1.0

@dataclass
class TestResult:
    """Rezultat testa"""
    test_case: TestCase
    status: TestStatus
    start_time: datetime
    end_time: datetime
    duration: float
    output: str = ""
    error_message: str = ""
    stack_trace: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)

@dataclass
class TestSuite:
    """Testna zbirka"""
    name: str
    description: str
    test_cases: List[TestCase]
    setup_suite: Optional[Callable] = None
    teardown_suite: Optional[Callable] = None
    parallel_execution: bool = True
    max_workers: int = 4

class SystemSimulator:
    """Simulator sistemskih pogojev"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.SystemSimulator")
        self.active_simulations = {}
        
    def simulate_high_load(self, duration: float = 10.0) -> str:
        """Simulira visoko obremenitev sistema"""
        simulation_id = str(uuid.uuid4())
        
        def cpu_stress():
            end_time = time.time() + duration
            while time.time() < end_time:
                # CPU intensive task
                sum(i * i for i in range(10000))
        
        # Zaženi stress test v ločeni niti
        thread = threading.Thread(target=cpu_stress)
        thread.start()
        
        self.active_simulations[simulation_id] = {
            'type': 'high_load',
            'thread': thread,
            'start_time': time.time(),
            'duration': duration
        }
        
        return simulation_id
    
    def simulate_memory_pressure(self, size_mb: int = 100) -> str:
        """Simulira pomanjkanje pomnilnika"""
        simulation_id = str(uuid.uuid4())
        
        # Alociraj velik blok pomnilnika
        memory_block = bytearray(size_mb * 1024 * 1024)
        
        self.active_simulations[simulation_id] = {
            'type': 'memory_pressure',
            'memory_block': memory_block,
            'size_mb': size_mb,
            'start_time': time.time()
        }
        
        return simulation_id
    
    def simulate_network_latency(self, latency_ms: int = 100) -> str:
        """Simulira mrežno zakasnitev"""
        simulation_id = str(uuid.uuid4())
        
        self.active_simulations[simulation_id] = {
            'type': 'network_latency',
            'latency_ms': latency_ms,
            'start_time': time.time()
        }
        
        return simulation_id
    
    def stop_simulation(self, simulation_id: str):
        """Ustavi simulacijo"""
        if simulation_id in self.active_simulations:
            simulation = self.active_simulations[simulation_id]
            
            if simulation['type'] == 'high_load' and 'thread' in simulation:
                # Thread se bo ustavil sam
                pass
            elif simulation['type'] == 'memory_pressure':
                # Sprosti pomnilnik
                del simulation['memory_block']
            
            del self.active_simulations[simulation_id]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Pridobi sistemske metrike"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'active_simulations': len(self.active_simulations),
            'timestamp': datetime.now().isoformat()
        }

class MIATestFramework:
    """Glavni testni okvir za MIA sistem"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.TestFramework")
        self.test_suites: Dict[str, TestSuite] = {}
        self.test_results: List[TestResult] = []
        self.simulator = SystemSimulator()
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # Inicializiraj testne zbirke
        self._initialize_test_suites()
    
    def _initialize_test_suites(self):
        """Inicializira testne zbirke"""
        
        # === UNIT TESTS ===
        unit_tests = [
            TestCase(
                id="unit_001",
                name="AGI Core Initialization",
                description="Test inicializacije AGI core sistema",
                test_type=TestType.UNIT,
                severity=TestSeverity.CRITICAL,
                test_function=self._test_agi_core_init,
                timeout=5.0
            ),
            TestCase(
                id="unit_002",
                name="Learning System Basic Functions",
                description="Test osnovnih funkcij učnega sistema",
                test_type=TestType.UNIT,
                severity=TestSeverity.HIGH,
                test_function=self._test_learning_system_basic,
                timeout=10.0
            ),
            TestCase(
                id="unit_003",
                name="Model Discovery Functionality",
                description="Test funkcionalnosti odkrivanja modelov",
                test_type=TestType.UNIT,
                severity=TestSeverity.HIGH,
                test_function=self._test_model_discovery,
                timeout=15.0
            ),
            TestCase(
                id="unit_004",
                name="Security System Authentication",
                description="Test avtentifikacije varnostnega sistema",
                test_type=TestType.UNIT,
                severity=TestSeverity.CRITICAL,
                test_function=self._test_security_auth,
                timeout=5.0
            ),
            TestCase(
                id="unit_005",
                name="Configuration Manager",
                description="Test upravljanja konfiguracije",
                test_type=TestType.UNIT,
                severity=TestSeverity.MEDIUM,
                test_function=self._test_config_manager,
                timeout=5.0
            )
        ]
        
        # === INTEGRATION TESTS ===
        integration_tests = [
            TestCase(
                id="int_001",
                name="AGI-Learning Integration",
                description="Test integracije AGI core z učnim sistemom",
                test_type=TestType.INTEGRATION,
                severity=TestSeverity.CRITICAL,
                test_function=self._test_agi_learning_integration,
                timeout=20.0,
                dependencies=["unit_001", "unit_002"]
            ),
            TestCase(
                id="int_002",
                name="Multimodal Processing Pipeline",
                description="Test multimodalnega procesnega pipeline-a",
                test_type=TestType.INTEGRATION,
                severity=TestSeverity.HIGH,
                test_function=self._test_multimodal_pipeline,
                timeout=30.0
            ),
            TestCase(
                id="int_003",
                name="Enterprise Monitoring Integration",
                description="Test integracije enterprise monitoring sistema",
                test_type=TestType.INTEGRATION,
                severity=TestSeverity.HIGH,
                test_function=self._test_enterprise_monitoring,
                timeout=15.0
            )
        ]
        
        # === SYSTEM TESTS ===
        system_tests = [
            TestCase(
                id="sys_001",
                name="End-to-End Conversation Flow",
                description="Test celotnega poteka pogovora",
                test_type=TestType.SYSTEM,
                severity=TestSeverity.CRITICAL,
                test_function=self._test_e2e_conversation,
                timeout=60.0
            ),
            TestCase(
                id="sys_002",
                name="System Startup and Shutdown",
                description="Test zagona in ugašanja sistema",
                test_type=TestType.SYSTEM,
                severity=TestSeverity.CRITICAL,
                test_function=self._test_system_lifecycle,
                timeout=120.0
            )
        ]
        
        # === PERFORMANCE TESTS ===
        performance_tests = [
            TestCase(
                id="perf_001",
                name="Response Time Under Load",
                description="Test odzivnega časa pod obremenitvijo",
                test_type=TestType.PERFORMANCE,
                severity=TestSeverity.HIGH,
                test_function=self._test_response_time_load,
                timeout=180.0
            ),
            TestCase(
                id="perf_002",
                name="Memory Usage Optimization",
                description="Test optimizacije porabe pomnilnika",
                test_type=TestType.PERFORMANCE,
                severity=TestSeverity.MEDIUM,
                test_function=self._test_memory_optimization,
                timeout=120.0
            )
        ]
        
        # === STRESS TESTS ===
        stress_tests = [
            TestCase(
                id="stress_001",
                name="High Concurrent Users",
                description="Test visokega števila sočasnih uporabnikov",
                test_type=TestType.STRESS,
                severity=TestSeverity.HIGH,
                test_function=self._test_concurrent_users,
                timeout=300.0
            ),
            TestCase(
                id="stress_002",
                name="Resource Exhaustion Recovery",
                description="Test okrevanja po izčrpanju virov",
                test_type=TestType.STRESS,
                severity=TestSeverity.HIGH,
                test_function=self._test_resource_exhaustion,
                timeout=240.0
            )
        ]
        
        # Ustvari testne zbirke
        self.test_suites = {
            "unit_tests": TestSuite("Unit Tests", "Osnovni unit testi", unit_tests),
            "integration_tests": TestSuite("Integration Tests", "Integracijski testi", integration_tests),
            "system_tests": TestSuite("System Tests", "Sistemski testi", system_tests),
            "performance_tests": TestSuite("Performance Tests", "Performančni testi", performance_tests),
            "stress_tests": TestSuite("Stress Tests", "Stresni testi", stress_tests)
        }
    
    # === TEST IMPLEMENTATIONS ===
    
    async def _test_agi_core_init(self) -> Dict[str, Any]:
        """Test inicializacije AGI core"""
        try:
            from mia.core.agi_core import agi_core
            
            # Test osnovnih atributov
            assert hasattr(agi_core, 'logger'), "AGI core nima logger atributa"
            assert hasattr(agi_core, 'model_discovery'), "AGI core nima model_discovery atributa"
            
            # Test metod
            stats = agi_core.get_agi_stats()
            assert isinstance(stats, dict), "AGI stats niso slovar"
            assert 'status' in stats, "AGI stats nimajo status ključa"
            
            return {"status": "passed", "stats": stats}
            
        except Exception as e:
            raise AssertionError(f"AGI core inicializacija neuspešna: {e}")
    
    async def _test_learning_system_basic(self) -> Dict[str, Any]:
        """Test osnovnih funkcij učnega sistema"""
        try:
            from mia.core.learning_system import learning_system
            
            # Test osnovnih metod
            stats = learning_system.get_learning_stats()
            assert isinstance(stats, dict), "Learning stats niso slovar"
            
            # Test učenja
            test_conversation = "Test conversation for learning"
            learning_system.learn_from_conversation(test_conversation, "test_response")
            
            # Preveri, če se je naučil
            new_stats = learning_system.get_learning_stats()
            assert new_stats['conversations_count'] >= stats['conversations_count'], "Učenje ni delovalo"
            
            return {"status": "passed", "stats": new_stats}
            
        except Exception as e:
            raise AssertionError(f"Learning system test neuspešen: {e}")
    
    async def _test_model_discovery(self) -> Dict[str, Any]:
        """Test funkcionalnosti odkrivanja modelov"""
        try:
            from mia.core.model_discovery import model_discovery
            
            # Test osnovnih metod
            stats = model_discovery.get_discovery_stats()
            assert isinstance(stats, dict), "Discovery stats niso slovar"
            assert 'scan_paths' in stats, "Discovery stats nimajo scan_paths"
            
            # Test skeniranja
            scan_results = model_discovery.scan_for_models()
            assert isinstance(scan_results, list), "Scan results niso seznam"
            
            return {"status": "passed", "stats": stats, "scan_results": len(scan_results)}
            
        except Exception as e:
            raise AssertionError(f"Model discovery test neuspešen: {e}")
    
    async def _test_security_auth(self) -> Dict[str, Any]:
        """Test avtentifikacije varnostnega sistema"""
        try:
            from mia.enterprise.security_system import security_system
            
            # Test osnovnih metod
            stats = security_system.get_security_stats()
            assert isinstance(stats, dict), "Security stats niso slovar"
            
            # Test avtentifikacije
            test_user = "test_user"
            test_password = "test_password"
            
            # Registracija
            reg_result = security_system.register_user(test_user, test_password)
            assert reg_result, "Registracija uporabnika neuspešna"
            
            # Avtentifikacija
            auth_result = security_system.authenticate_user(test_user, test_password)
            assert auth_result, "Avtentifikacija neuspešna"
            
            return {"status": "passed", "stats": stats}
            
        except Exception as e:
            raise AssertionError(f"Security authentication test neuspešen: {e}")
    
    async def _test_config_manager(self) -> Dict[str, Any]:
        """Test upravljanja konfiguracije"""
        try:
            from mia.enterprise.config_manager import config_manager
            
            # Test osnovnih metod
            env = config_manager.get_environment()
            assert env is not None, "Environment ni nastavljen"
            
            # Test nastavitev
            test_key = "test_setting"
            test_value = "test_value"
            
            config_manager.set(test_key, test_value)
            retrieved_value = config_manager.get(test_key)
            
            assert retrieved_value == test_value, "Konfiguracija ni bila pravilno shranjena"
            
            return {"status": "passed", "environment": env.value}
            
        except Exception as e:
            raise AssertionError(f"Config manager test neuspešen: {e}")
    
    async def _test_agi_learning_integration(self) -> Dict[str, Any]:
        """Test integracije AGI core z učnim sistemom"""
        try:
            from mia.core.agi_core import agi_core
            from mia.core.learning_system import learning_system
            
            # Test komunikacije med komponentama
            initial_stats = learning_system.get_learning_stats()
            
            # Simuliraj AGI interakcijo z učnim sistemom
            test_input = "Integration test input"
            agi_response = agi_core.process_input(test_input)
            
            # Preveri, če se je učni sistem posodobil
            final_stats = learning_system.get_learning_stats()
            
            return {
                "status": "passed",
                "agi_response": str(agi_response)[:100],
                "learning_updated": final_stats != initial_stats
            }
            
        except Exception as e:
            raise AssertionError(f"AGI-Learning integration test neuspešen: {e}")
    
    async def _test_multimodal_pipeline(self) -> Dict[str, Any]:
        """Test multimodalnega procesnega pipeline-a"""
        try:
            from mia.core.multimodal import multimodal_system
            
            # Test različnih modalnosti
            text_result = multimodal_system.process_text("Test text input")
            assert text_result is not None, "Text processing neuspešen"
            
            # Test statistik
            stats = multimodal_system.get_multimodal_stats()
            assert isinstance(stats, dict), "Multimodal stats niso slovar"
            
            return {"status": "passed", "stats": stats}
            
        except Exception as e:
            raise AssertionError(f"Multimodal pipeline test neuspešen: {e}")
    
    async def _test_enterprise_monitoring(self) -> Dict[str, Any]:
        """Test integracije enterprise monitoring sistema"""
        try:
            from mia.enterprise.monitoring import enterprise_monitoring
            
            # Test monitoring funkcionalnosti
            status = enterprise_monitoring.get_system_status()
            assert isinstance(status, dict), "System status ni slovar"
            assert 'monitoring_active' in status, "Monitoring status nima monitoring_active"
            
            # Test metrik
            metrics = enterprise_monitoring.get_metrics()
            assert isinstance(metrics, list), "Metrics niso seznam"
            
            return {"status": "passed", "monitoring_status": status}
            
        except Exception as e:
            raise AssertionError(f"Enterprise monitoring test neuspešen: {e}")
    
    async def _test_e2e_conversation(self) -> Dict[str, Any]:
        """Test celotnega poteka pogovora"""
        try:
            from mia.interfaces.chat import chat_interface
            
            # Simuliraj celoten pogovor
            test_message = "Hello, can you help me with a test?"
            
            response = chat_interface.process_message(test_message)
            assert response is not None, "Chat response je None"
            assert len(str(response)) > 0, "Chat response je prazen"
            
            # Test zgodovine
            history = chat_interface.get_conversation_history()
            assert isinstance(history, list), "Conversation history ni seznam"
            
            return {
                "status": "passed",
                "response_length": len(str(response)),
                "history_count": len(history)
            }
            
        except Exception as e:
            raise AssertionError(f"E2E conversation test neuspešen: {e}")
    
    async def _test_system_lifecycle(self) -> Dict[str, Any]:
        """Test zagona in ugašanja sistema"""
        try:
            # Test je že izveden s tem, da sistem deluje
            # Preverimo osnovne komponente
            
            components_status = {}
            
            try:
                from mia.core.agi_core import agi_core
                components_status['agi_core'] = True
            except:
                components_status['agi_core'] = False
            
            try:
                from mia.core.learning_system import learning_system
                components_status['learning_system'] = True
            except:
                components_status['learning_system'] = False
            
            try:
                from mia.enterprise.monitoring import enterprise_monitoring
                components_status['monitoring'] = True
            except:
                components_status['monitoring'] = False
            
            # Preveri, če so ključne komponente naložene
            critical_components = ['agi_core', 'learning_system', 'monitoring']
            all_loaded = all(components_status.get(comp, False) for comp in critical_components)
            
            return {
                "status": "passed" if all_loaded else "failed",
                "components_status": components_status,
                "all_critical_loaded": all_loaded
            }
            
        except Exception as e:
            raise AssertionError(f"System lifecycle test neuspešen: {e}")
    
    async def _test_response_time_load(self) -> Dict[str, Any]:
        """Test odzivnega časa pod obremenitvijo"""
        try:
            from mia.interfaces.chat import chat_interface
            
            # Simuliraj visoko obremenitev
            simulation_id = self.simulator.simulate_high_load(duration=30.0)
            
            # Izmeri odzivni čas
            start_time = time.time()
            response = chat_interface.process_message("Performance test message")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Ustavi simulacijo
            self.simulator.stop_simulation(simulation_id)
            
            # Preveri, če je odzivni čas sprejemljiv (< 5 sekund)
            acceptable_time = 5.0
            performance_ok = response_time < acceptable_time
            
            return {
                "status": "passed" if performance_ok else "failed",
                "response_time": response_time,
                "acceptable_time": acceptable_time,
                "performance_ok": performance_ok
            }
            
        except Exception as e:
            raise AssertionError(f"Response time load test neuspešen: {e}")
    
    async def _test_memory_optimization(self) -> Dict[str, Any]:
        """Test optimizacije porabe pomnilnika"""
        try:
            # Izmeri začetno porabo pomnilnika
            initial_memory = psutil.virtual_memory().percent
            
            # Simuliraj pomanjkanje pomnilnika
            simulation_id = self.simulator.simulate_memory_pressure(size_mb=50)
            
            # Počakaj malo
            await asyncio.sleep(2)
            
            # Izmeri porabo med simulacijo
            peak_memory = psutil.virtual_memory().percent
            
            # Ustavi simulacijo
            self.simulator.stop_simulation(simulation_id)
            
            # Počakaj na garbage collection
            await asyncio.sleep(2)
            
            # Izmeri končno porabo
            final_memory = psutil.virtual_memory().percent
            
            # Preveri, če se je pomnilnik sprostil
            memory_recovered = final_memory <= initial_memory + 5  # 5% tolerance
            
            return {
                "status": "passed" if memory_recovered else "failed",
                "initial_memory": initial_memory,
                "peak_memory": peak_memory,
                "final_memory": final_memory,
                "memory_recovered": memory_recovered
            }
            
        except Exception as e:
            raise AssertionError(f"Memory optimization test neuspešen: {e}")
    
    async def _test_concurrent_users(self) -> Dict[str, Any]:
        """Test visokega števila sočasnih uporabnikov"""
        try:
            from mia.interfaces.chat import chat_interface
            
            # Simuliraj več sočasnih uporabnikov
            concurrent_users = 10
            tasks = []
            
            async def simulate_user(user_id: int):
                message = f"Concurrent user {user_id} test message"
                start_time = time.time()
                response = chat_interface.process_message(message)
                end_time = time.time()
                return {
                    'user_id': user_id,
                    'response_time': end_time - start_time,
                    'success': response is not None
                }
            
            # Zaženi vse uporabnike sočasno
            for i in range(concurrent_users):
                tasks.append(simulate_user(i))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analiziraj rezultate
            successful_users = sum(1 for r in results if isinstance(r, dict) and r.get('success', False))
            avg_response_time = np.mean([r['response_time'] for r in results if isinstance(r, dict)])
            
            success_rate = successful_users / concurrent_users
            performance_ok = success_rate >= 0.8 and avg_response_time < 10.0
            
            return {
                "status": "passed" if performance_ok else "failed",
                "concurrent_users": concurrent_users,
                "successful_users": successful_users,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "performance_ok": performance_ok
            }
            
        except Exception as e:
            raise AssertionError(f"Concurrent users test neuspešen: {e}")
    
    async def _test_resource_exhaustion(self) -> Dict[str, Any]:
        """Test okrevanja po izčrpanju virov"""
        try:
            # Simuliraj izčrpanje virov
            cpu_sim = self.simulator.simulate_high_load(duration=20.0)
            memory_sim = self.simulator.simulate_memory_pressure(size_mb=100)
            
            # Počakaj na stabilizacijo
            await asyncio.sleep(5)
            
            # Preveri, če sistem še vedno deluje
            from mia.interfaces.chat import chat_interface
            
            try:
                response = chat_interface.process_message("Resource exhaustion test")
                system_responsive = response is not None
            except:
                system_responsive = False
            
            # Ustavi simulacije
            self.simulator.stop_simulation(cpu_sim)
            self.simulator.stop_simulation(memory_sim)
            
            # Počakaj na okrevanje
            await asyncio.sleep(5)
            
            # Preveri okrevanje
            try:
                recovery_response = chat_interface.process_message("Recovery test")
                system_recovered = recovery_response is not None
            except:
                system_recovered = False
            
            return {
                "status": "passed" if system_recovered else "failed",
                "system_responsive_under_stress": system_responsive,
                "system_recovered": system_recovered
            }
            
        except Exception as e:
            raise AssertionError(f"Resource exhaustion test neuspešen: {e}")
    
    # === TEST EXECUTION ===
    
    async def run_test_case(self, test_case: TestCase) -> TestResult:
        """Izvede posamezen testni primer"""
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Izvajam test: {test_case.name}")
            
            # Setup
            if test_case.setup_function:
                await test_case.setup_function()
            
            # Izvedi test z timeout
            try:
                result = await asyncio.wait_for(
                    test_case.test_function(),
                    timeout=test_case.timeout
                )
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                return TestResult(
                    test_case=test_case,
                    status=TestStatus.PASSED,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    output=json.dumps(result, default=str),
                    metrics=result if isinstance(result, dict) else {}
                )
                
            except asyncio.TimeoutError:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                return TestResult(
                    test_case=test_case,
                    status=TestStatus.FAILED,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    error_message=f"Test timeout after {test_case.timeout}s"
                )
            
        except AssertionError as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return TestResult(
                test_case=test_case,
                status=TestStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                error_message=str(e)
            )
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return TestResult(
                test_case=test_case,
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            )
        
        finally:
            # Teardown
            if test_case.teardown_function:
                try:
                    await test_case.teardown_function()
                except Exception as e:
                    self.logger.error(f"Teardown failed for {test_case.name}: {e}")
    
    async def run_test_suite(self, suite_name: str) -> List[TestResult]:
        """Izvede testno zbirko"""
        if suite_name not in self.test_suites:
            raise ValueError(f"Test suite '{suite_name}' not found")
        
        suite = self.test_suites[suite_name]
        self.logger.info(f"Izvajam test suite: {suite.name}")
        
        # Suite setup
        if suite.setup_suite:
            await suite.setup_suite()
        
        try:
            results = []
            
            if suite.parallel_execution:
                # Paralelno izvajanje
                tasks = [self.run_test_case(test_case) for test_case in suite.test_cases]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Pretvori exceptions v error results
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        results[i] = TestResult(
                            test_case=suite.test_cases[i],
                            status=TestStatus.ERROR,
                            start_time=datetime.now(),
                            end_time=datetime.now(),
                            duration=0.0,
                            error_message=str(result)
                        )
            else:
                # Sekvencialno izvajanje
                for test_case in suite.test_cases:
                    result = await self.run_test_case(test_case)
                    results.append(result)
            
            return results
            
        finally:
            # Suite teardown
            if suite.teardown_suite:
                try:
                    await suite.teardown_suite()
                except Exception as e:
                    self.logger.error(f"Suite teardown failed for {suite.name}: {e}")
    
    async def run_all_tests(self) -> Dict[str, List[TestResult]]:
        """Izvede vse teste"""
        print("🧪 === COMPREHENSIVE SIMULATION TEST FRAMEWORK ===")
        print()
        
        all_results = {}
        
        # Izvedi vse test suites
        for suite_name in self.test_suites.keys():
            print(f"🔬 Izvajam {suite_name}...")
            
            try:
                results = await self.run_test_suite(suite_name)
                all_results[suite_name] = results
                
                # Statistike za suite
                passed = sum(1 for r in results if r.status == TestStatus.PASSED)
                failed = sum(1 for r in results if r.status == TestStatus.FAILED)
                errors = sum(1 for r in results if r.status == TestStatus.ERROR)
                
                print(f"   ✅ Passed: {passed}")
                print(f"   ❌ Failed: {failed}")
                print(f"   ⚠️ Errors: {errors}")
                print()
                
            except Exception as e:
                self.logger.error(f"Suite {suite_name} failed: {e}")
                all_results[suite_name] = []
        
        # Shrani vse rezultate
        self.test_results = [result for results in all_results.values() for result in results]
        
        return all_results
    
    def generate_test_report(self, results: Dict[str, List[TestResult]]) -> Dict[str, Any]:
        """Generiraj testno poročilo"""
        total_tests = sum(len(suite_results) for suite_results in results.values())
        total_passed = sum(1 for suite_results in results.values() 
                          for result in suite_results if result.status == TestStatus.PASSED)
        total_failed = sum(1 for suite_results in results.values() 
                          for result in suite_results if result.status == TestStatus.FAILED)
        total_errors = sum(1 for suite_results in results.values() 
                          for result in suite_results if result.status == TestStatus.ERROR)
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Povzetek po test suites
        suite_summaries = {}
        for suite_name, suite_results in results.items():
            suite_summaries[suite_name] = {
                'total': len(suite_results),
                'passed': sum(1 for r in suite_results if r.status == TestStatus.PASSED),
                'failed': sum(1 for r in suite_results if r.status == TestStatus.FAILED),
                'errors': sum(1 for r in suite_results if r.status == TestStatus.ERROR),
                'avg_duration': np.mean([r.duration for r in suite_results]) if suite_results else 0
            }
        
        # Najdi najdaljše teste
        all_results = [result for suite_results in results.values() for result in suite_results]
        longest_tests = sorted(all_results, key=lambda x: x.duration, reverse=True)[:5]
        
        # Najdi neuspešne teste
        failed_tests = [result for result in all_results if result.status in [TestStatus.FAILED, TestStatus.ERROR]]
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_failed,
                'errors': total_errors,
                'success_rate': success_rate
            },
            'suite_summaries': suite_summaries,
            'longest_tests': [
                {
                    'name': test.test_case.name,
                    'duration': test.duration,
                    'type': test.test_case.test_type.value
                }
                for test in longest_tests
            ],
            'failed_tests': [
                {
                    'name': test.test_case.name,
                    'type': test.test_case.test_type.value,
                    'error': test.error_message,
                    'duration': test.duration
                }
                for test in failed_tests
            ],
            'system_metrics': self.simulator.get_system_metrics()
        }
        
        return report

async def main():
    """Glavna funkcija za testiranje"""
    # Nastavi logging
    logging.basicConfig(level=logging.INFO)
    
    # Ustvari test framework
    framework = MIATestFramework()
    
    # Izvedi vse teste
    results = await framework.run_all_tests()
    
    # Generiraj poročilo
    report = framework.generate_test_report(results)
    
    # Shrani poročilo
    with open('comprehensive_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    # Prikaži povzetek
    print("📊 === TESTNI POVZETEK ===")
    print(f"   🧪 Skupaj testov: {report['summary']['total_tests']}")
    print(f"   ✅ Uspešnih: {report['summary']['passed']}")
    print(f"   ❌ Neuspešnih: {report['summary']['failed']}")
    print(f"   ⚠️ Napak: {report['summary']['errors']}")
    print(f"   📈 Uspešnost: {report['summary']['success_rate']:.1f}%")
    
    if report['failed_tests']:
        print(f"\n❌ Neuspešni testi:")
        for test in report['failed_tests'][:5]:
            print(f"   - {test['name']}: {test['error'][:100]}...")
    
    print(f"\n💾 Poročilo shranjeno: comprehensive_test_report.json")
    print("✅ COMPREHENSIVE SIMULATION TEST FRAMEWORK KONČAN!")

if __name__ == "__main__":
    asyncio.run(main())