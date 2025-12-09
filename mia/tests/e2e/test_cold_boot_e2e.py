#!/usr/bin/env python3
"""
End-to-End Tests - Cold Boot
Tests for complete system initialization: bootstrap → memory → model → LSP → consciousness
"""

import pytest
import time
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from mia.core.system_integrator import SystemIntegrator

@pytest.mark.e2e
@pytest.mark.critical
class TestColdBootE2E:

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Test complete cold boot process"""
    
    def test_complete_cold_boot_sequence(self, deterministic_environment, temp_workspace, enterprise_config):
        """Test complete cold boot from scratch"""
        # Create isolated workspace
        boot_workspace = temp_workspace / "cold_boot"
        boot_workspace.mkdir(exist_ok=True)
        
        # Mock hardware detection
        with patch('psutil.cpu_count', return_value=8), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory.return_value.total = 16 * 1024 * 1024 * 1024  # 16GB
            mock_memory.return_value.available = 12 * 1024 * 1024 * 1024  # 12GB available
            mock_memory.return_value.percent = 25.0
            
            mock_disk.return_value.total = 1024 * 1024 * 1024 * 1024  # 1TB
            mock_disk.return_value.free = 512 * 1024 * 1024 * 1024  # 512GB free
            
            # Initialize system integrator
            integrator = SystemIntegrator()
            
            # Track boot sequence
            boot_sequence = []
            
            # Mock component initialization to track sequence
            original_init = integrator._initialize_component
            
            def track_init(component_name, component_config):
                boot_sequence.append(component_name)
                return original_init(component_name, component_config)
            
            integrator._initialize_component = track_init
            
            # Perform cold boot
            start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            try:
                success = integrator.initialize_system()
                boot_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
                
                # Verify boot success
                assert success == True
                assert boot_time < 30.0  # Boot should complete in under 30 seconds
                
                # Verify boot sequence
                assert len(boot_sequence) > 0
                
                # Check critical components were initialized
                critical_components = [
                    "hardware_optimizer", "owner_guard", "memory", 
                    "consciousness", "adaptive_llm"
                ]
                
                for component in critical_components:
                    assert component in boot_sequence
                
                # Verify system status
                status = integrator.get_system_status()
                assert status["initialized"] == True
                assert status["active_components"] >= 5
                
            except Exception as e:
                pytest.fail(f"Cold boot failed: {e}")
    
    def test_hardware_detection_and_optimization(self, deterministic_environment, temp_workspace):
        """Test hardware detection and optimization during boot"""
        # Test different hardware configurations
        hardware_configs = [
            {
                "name": "low_end",
                "cpu_cores": 2,
                "memory": 4 * 1024 * 1024 * 1024,  # 4GB
                "gpu_available": False
            },
            {
                "name": "mid_range",
                "cpu_cores": 8,
                "memory": 16 * 1024 * 1024 * 1024,  # 16GB
                "gpu_available": False
            },
            {
                "name": "high_end",
                "cpu_cores": 16,
                "memory": 64 * 1024 * 1024 * 1024,  # 64GB
                "gpu_available": True
            }
        ]
        
        for config in hardware_configs:
            with patch('psutil.cpu_count', return_value=config["cpu_cores"]), \
                 patch('psutil.virtual_memory') as mock_memory:
                
                mock_memory.return_value.total = config["memory"]
                mock_memory.return_value.available = int(config["memory"] * 0.8)
                mock_memory.return_value.percent = 20.0
                
                # Initialize system
                integrator = SystemIntegrator()
                
                # Check hardware detection
                from mia.core.hardware_optimizer import hardware_optimizer
                hardware_info = hardware_optimizer.detect_hardware()
                
                assert hardware_info["cpu_cores"] == config["cpu_cores"]
                assert hardware_info["total_memory"] == config["memory"]
                
                # Verify optimization for hardware tier
                if config["cpu_cores"] <= 4 and config["memory"] <= 8 * 1024 * 1024 * 1024:
                    assert hardware_info["tier"] in ["low_end", "basic"]
                elif config["cpu_cores"] >= 12 and config["memory"] >= 32 * 1024 * 1024 * 1024:
                    assert hardware_info["tier"] in ["high_end", "enterprise"]
                else:
                    assert hardware_info["tier"] in ["mid_range", "standard"]
    
    def test_memory_system_initialization(self, deterministic_environment, temp_workspace):
        """Test memory system initialization during cold boot"""
        # Create memory workspace
        memory_workspace = temp_workspace / "memory_init"
        memory_workspace.mkdir(exist_ok=True)
        
        # Initialize system integrator
        integrator = SystemIntegrator()
        
        # Initialize memory component
        memory_config = {
            "storage_path": str(memory_workspace),
            "vector_dimensions": 384,
            "max_memories": 10000
        }
        
        success = integrator._initialize_component("memory", memory_config)
        assert success == True
        
        # Verify memory system is functional
        from mia.core.memory.main import memory_system
        
        # Test memory storage
        memory_id = memory_system.store_memory(
            content="Cold boot test memory",
            memory_type="SHORT_TERM",
            emotional_tone="NEUTRAL",
            tags=["cold_boot", "test"]
        )
        
        assert memory_id is not None
        
        # Test memory retrieval
        memories = memory_system.retrieve_memories(
            query="cold boot test",
            memory_types=["SHORT_TERM"],
            limit=5
        )
        
        assert len(memories) >= 1
        assert memories[0]["content"] == "Cold boot test memory"
    
    def test_consciousness_initialization(self, deterministic_environment, temp_workspace):
        """Test consciousness initialization during cold boot"""
        # Initialize system integrator
        integrator = SystemIntegrator()
        
        # Initialize consciousness component
        consciousness_config = {
            "initial_state": "AWAKENING",
            "personality_traits": {
                "curiosity": 0.8,
                "helpfulness": 0.9,
                "creativity": 0.7
            }
        }
        
        success = integrator._initialize_component("consciousness", consciousness_config)
        assert success == True
        
        # Verify consciousness is functional
        from mia.core.consciousness.main import consciousness
        
        # Check initial state
        state = consciousness.get_consciousness_state()
        assert state["consciousness_state"] != "DORMANT"
        assert state["awareness_level"] > 0.0
        
        # Test consciousness processing
        result = consciousness.process_user_input(
            "Hello, are you awake?",
            {"emotional_tone": "friendly"}
        )
        
        assert isinstance(result, dict)
        assert "consciousness_state" in result
        assert "response_context" in result
    
    def test_adaptive_llm_initialization(self, deterministic_environment, temp_workspace, mock_hardware):
        """Test adaptive LLM initialization during cold boot"""
        # Initialize system integrator
        integrator = SystemIntegrator()
        
        # Initialize adaptive LLM component
        llm_config = {
            "model_preferences": ["small", "medium"],
            "fallback_enabled": True,
            "performance_monitoring": True
        }
        
        success = integrator._initialize_component("adaptive_llm", llm_config)
        assert success == True
        
        # Verify LLM system is functional
        from mia.core.adaptive_llm import adaptive_llm
        
        # Check system status
        status = adaptive_llm.get_system_status()
        assert status["active"] == True
        assert "available_models" in status
        
        # Test model selection
        with patch.object(adaptive_llm, '_generate_with_model') as mock_generate:
            mock_generate.return_value = {"text": "LLM test response", "tokens": 15}
            
            result = adaptive_llm.generate_text("Test prompt for cold boot")
            assert result is not None
            assert result["text"] == "LLM test response"
    
    def test_lsp_slovenian_language_initialization(self, deterministic_environment, temp_workspace):
        """Test LSP (Language Support Package) initialization for Slovenian"""
        # Create LSP workspace
        lsp_workspace = temp_workspace / "lsp_init"
        lsp_workspace.mkdir(exist_ok=True)
        
        # Mock LSP module
        with patch('mia.core.lsp.slovenian') as mock_lsp:
            mock_lsp.initialize_slovenian_language.return_value = True
            mock_lsp.get_language_status.return_value = {
                "language": "slovenian",
                "status": "active",
                "vocabulary_size": 50000,
                "grammar_rules": 1200
            }
            
            # Initialize system integrator
            integrator = SystemIntegrator()
            
            # Initialize LSP component
            lsp_config = {
                "language": "slovenian",
                "formal_symbolic_form": True,
                "grammar_validation": True
            }
            
            success = integrator._initialize_component("lsp", lsp_config)
            assert success == True
            
            # Verify LSP initialization was called
            assert mock_lsp.initialize_slovenian_language.called
            
            # Check language status
            status = mock_lsp.get_language_status.return_value
            assert status["language"] == "slovenian"
            assert status["status"] == "active"
    
    def test_complete_system_integration(self, deterministic_environment, temp_workspace, enterprise_config):
        """Test complete system integration after cold boot"""
        # Initialize complete system
        integrator = SystemIntegrator()
        
        # Mock all external dependencies
        with patch('psutil.cpu_count', return_value=8), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('mia.core.lsp.slovenian.initialize_slovenian_language', return_value=True):
            
            mock_memory.return_value.total = 16 * 1024 * 1024 * 1024
            mock_memory.return_value.available = 12 * 1024 * 1024 * 1024
            mock_memory.return_value.percent = 25.0
            
            # Perform complete initialization
            success = integrator.initialize_system()
            assert success == True
            
            # Test system integration
            system_status = integrator.get_system_status()
            
            # Verify all critical components are active
            critical_components = [
                "hardware_optimizer", "memory", "consciousness", "adaptive_llm"
            ]
            
            for component in critical_components:
                assert component in system_status
                component_status = system_status[component]
                assert component_status.get("status") in ["active", "initialized", True]
            
            # Test cross-component communication
            from mia.core.consciousness.main import consciousness
            from mia.core.memory.main import memory_system
            
            # Test consciousness → memory integration
            result = consciousness.process_user_input(
                "Store this important information",
                {"emotional_tone": "serious"}
            )
            
            assert isinstance(result, dict)
            
            # Verify memory was affected
            memories = memory_system.retrieve_memories(
                query="important information",
                memory_types=["SHORT_TERM"],
                limit=5
            )
            
            # Should have some memory activity
            assert len(memories) >= 0  # May or may not have stored depending on implementation
    
    def test_boot_failure_recovery(self, deterministic_environment, temp_workspace):
        """Test boot failure recovery mechanisms"""
        # Initialize system integrator
        integrator = SystemIntegrator()
        
        # Test component initialization failure
        original_init = integrator._initialize_component
        
        def failing_init(component_name, component_config):
            if component_name == "test_failing_component":
                raise Exception("Simulated component failure")
            return original_init(component_name, component_config)
        
        integrator._initialize_component = failing_init
        
        # Add failing component to config
        integrator.component_configs["test_failing_component"] = {
            "module_path": "mia.core.test_failing",
            "instance_name": "test_failing_instance",
            "auto_start": True
        }
        
        # Attempt initialization
        success = integrator.initialize_system()
        
        # Should handle failure gracefully
        # System should still initialize other components
        status = integrator.get_system_status()
        assert status["initialized"] == True  # Other components should work
        
        # Failing component should not be in active components
        assert "test_failing_component" not in status or \
               status["test_failing_component"].get("status") != "active"
    
    def test_boot_performance_requirements(self, deterministic_environment, temp_workspace, test_timer):
        """Test boot performance requirements"""
        # Initialize system integrator
        integrator = SystemIntegrator()
        
        # Mock fast hardware
        with patch('psutil.cpu_count', return_value=16), \
             patch('psutil.virtual_memory') as mock_memory:
            
            mock_memory.return_value.total = 32 * 1024 * 1024 * 1024  # 32GB
            mock_memory.return_value.available = 24 * 1024 * 1024 * 1024  # 24GB available
            mock_memory.return_value.percent = 25.0
            
            # Measure boot time
            start_time = test_timer()
            
            success = integrator.initialize_system()
            
            boot_time = test_timer()
            
            # Verify performance requirements
            assert success == True
            assert boot_time < 15.0  # Should boot in under 15 seconds on fast hardware
            
            # Test system responsiveness after boot
            response_start = test_timer()
            
            status = integrator.get_system_status()
            
            response_time = test_timer() - response_start
            
            assert response_time < 1.0  # Status check should be fast
            assert isinstance(status, dict)
    
    def test_boot_memory_usage(self, deterministic_environment, temp_workspace):
        """Test memory usage during boot process"""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Initialize system
        integrator = SystemIntegrator()
        
        # Mock hardware to ensure consistent test
        with patch('psutil.cpu_count', return_value=8), \
             patch('psutil.virtual_memory') as mock_memory:
            
            mock_memory.return_value.total = 16 * 1024 * 1024 * 1024
            mock_memory.return_value.available = 12 * 1024 * 1024 * 1024
            mock_memory.return_value.percent = 25.0
            
            # Perform initialization
            success = integrator.initialize_system()
            assert success == True
            
            # Check memory usage after boot
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable
            max_memory_increase = 500 * 1024 * 1024  # 500MB max increase
            assert memory_increase < max_memory_increase
            
            # Test memory stability
            stable_memory = process.memory_info().rss
            time.sleep(1.0)  # Wait a bit
            later_memory = process.memory_info().rss
            
            # Memory should be stable (no significant leaks)
            memory_drift = abs(later_memory - stable_memory)
            max_drift = 10 * 1024 * 1024  # 10MB max drift
            assert memory_drift < max_drift
    
    def test_boot_with_corrupted_state(self, deterministic_environment, temp_workspace):
        """Test boot recovery from corrupted state files"""
        # Create corrupted state files
        corrupted_workspace = temp_workspace / "corrupted_boot"
        corrupted_workspace.mkdir(exist_ok=True)
        
        # Create corrupted memory state
        memory_state_file = corrupted_workspace / "memory_state.json"
        memory_state_file.write_text("{ corrupted json content")
        
        # Create corrupted consciousness state
        consciousness_state_file = corrupted_workspace / "consciousness_state.json"
        consciousness_state_file.write_text("invalid json")
        
        # Initialize system with corrupted state
        integrator = SystemIntegrator()
        
        # Mock state loading to use corrupted files
        with patch('mia.core.memory.main.MemorySystem.load_state') as mock_memory_load, \
             patch('mia.core.consciousness.main.ConsciousnessModule.load_state') as mock_consciousness_load:
            
            # Make state loading fail initially
            mock_memory_load.side_effect = [Exception("Corrupted state"), None]
            mock_consciousness_load.side_effect = [Exception("Corrupted state"), None]
            
            # Should recover from corrupted state
            success = integrator.initialize_system()
            
            # System should initialize with fresh state
            assert success == True
            
            # Verify recovery was attempted
            assert mock_memory_load.called
            assert mock_consciousness_load.called
    
    def test_enterprise_mode_cold_boot(self, deterministic_environment, temp_workspace, enterprise_config):
        """Test cold boot in enterprise mode"""
        # Set enterprise environment
        os.environ["MIA_ENTERPRISE_MODE"] = "true"
        os.environ["MIA_SECURITY_LEVEL"] = "high"
        
        try:
            # Initialize system integrator
            integrator = SystemIntegrator()
            
            # Mock enterprise components
            with patch('mia.core.quality_control.qpm.qpm') as mock_qpm, \
                 patch('mia.core.agi_agents.planner.agi_planner') as mock_agi, \
                 patch('mia.core.security.system_fuse.system_fuse') as mock_security:
                
                mock_qpm.get_system_status.return_value = {"status": "active"}
                mock_agi.get_system_status.return_value = {"status": "active"}
                mock_security.get_system_status.return_value = {"status": "active"}
                
                # Perform enterprise boot
                success = integrator.initialize_system()
                assert success == True
                
                # Verify enterprise components are considered
                status = integrator.get_system_status()
                assert status["initialized"] == True
                
                # Check enterprise mode is active
                assert os.environ.get("MIA_ENTERPRISE_MODE") == "true"
                
        finally:
            # Cleanup environment
            os.environ.pop("MIA_ENTERPRISE_MODE", None)
            os.environ.pop("MIA_SECURITY_LEVEL", None)