#!/usr/bin/env python3
"""
Unit Tests - Adaptive LLM
Tests for model selection, fallback logic, precision switching, and deterministic recovery
"""

import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from mia.core.adaptive_llm import AdaptiveLLMManager, ModelSize, ModelType, ModelSpec, SystemCapabilities

@pytest.mark.unit
@pytest.mark.critical
class TestAdaptiveLLM:
    """Test adaptive LLM functionality"""
    
    def test_adaptive_llm_initialization(self, deterministic_environment, mock_hardware):
        """Test adaptive LLM manager initialization"""
        llm_manager = AdaptiveLLMManager()
        
        assert llm_manager.config is not None
        assert llm_manager.available_models is not None
        assert llm_manager.current_model is None
        assert llm_manager.system_capabilities is not None
        assert llm_manager.performance_history == []
    
    def test_system_capabilities_detection(self, deterministic_environment, mock_hardware):
        """Test system capabilities detection"""
        llm_manager = AdaptiveLLMManager()
        
        capabilities = llm_manager._detect_system_capabilities()
        
        assert isinstance(capabilities, SystemCapabilities)
        assert capabilities.cpu_cores == mock_hardware["cpu_cores"]
        assert capabilities.total_memory == mock_hardware["total_memory"]
        assert capabilities.gpu_available == mock_hardware["gpu_available"]
        assert capabilities.gpu_memory == mock_hardware["gpu_memory"]
    
    def test_model_compatibility_check(self, deterministic_environment, mock_hardware):
        """Test model compatibility checking"""
        llm_manager = AdaptiveLLMManager()
        
        # Create test model specs
        small_model = ModelSpec(
            name="test-small",
            size=ModelSize.SMALL,
            type=ModelType.LANGUAGE,
            ram_requirement=2.0,  # 2GB
            vram_requirement=0.0,  # No GPU required
            cpu_cores_min=2,
            download_url="http://test.com/small",
            local_path="models/test-small",
            capabilities=["text_generation"],
            performance_score=0.7
        )
        
        large_model = ModelSpec(
            name="test-large",
            size=ModelSize.LARGE,
            type=ModelType.LANGUAGE,
            ram_requirement=32.0,  # 32GB
            vram_requirement=16.0,  # 16GB GPU
            cpu_cores_min=16,
            download_url="http://test.com/large",
            local_path="models/test-large",
            capabilities=["text_generation", "reasoning"],
            performance_score=0.95
        )
        
        # Test compatibility
        small_compatible = llm_manager._is_model_compatible(small_model)
        large_compatible = llm_manager._is_model_compatible(large_model)
        
        assert small_compatible == True  # Should be compatible with mock hardware
        assert large_compatible == False  # Should not be compatible (too much RAM/VRAM)
    
    def test_model_selection_logic(self, deterministic_environment, mock_hardware):
        """Test model selection logic"""
        llm_manager = AdaptiveLLMManager()
        
        # Mock available models
        test_models = [
            ModelSpec(
                name="tiny-model",
                size=ModelSize.TINY,
                type=ModelType.LANGUAGE,
                ram_requirement=1.0,
                vram_requirement=0.0,
                cpu_cores_min=1,
                download_url="http://test.com/tiny",
                local_path="models/tiny",
                capabilities=["basic_text"],
                performance_score=0.5
            ),
            ModelSpec(
                name="medium-model",
                size=ModelSize.MEDIUM,
                type=ModelType.LANGUAGE,
                ram_requirement=8.0,
                vram_requirement=0.0,
                cpu_cores_min=4,
                download_url="http://test.com/medium",
                local_path="models/medium",
                capabilities=["text_generation", "reasoning"],
                performance_score=0.8
            )
        ]
        
        llm_manager.available_models = {model.name: model for model in test_models}
        
        # Test selection for different task types
        text_model = llm_manager._select_best_model("text_generation", ["reasoning"])
        basic_model = llm_manager._select_best_model("basic_text", [])
        
        assert text_model is not None
        assert basic_model is not None
        
        # Medium model should be selected for text generation (better performance)
        assert text_model.name == "medium-model"
        
        # Either model could be selected for basic text
        assert basic_model.name in ["tiny-model", "medium-model"]
    
    def test_fallback_logic(self, deterministic_environment, mock_hardware):
        """Test fallback logic when models fail"""
        llm_manager = AdaptiveLLMManager()
        
        # Mock model loading failure
        with patch.object(llm_manager, '_load_model') as mock_load:
            mock_load.side_effect = [Exception("Model load failed"), True]
            
            # Mock available models
            test_models = [
                ModelSpec(
                    name="primary-model",
                    size=ModelSize.MEDIUM,
                    type=ModelType.LANGUAGE,
                    ram_requirement=8.0,
                    vram_requirement=0.0,
                    cpu_cores_min=4,
                    download_url="http://test.com/primary",
                    local_path="models/primary",
                    capabilities=["text_generation"],
                    performance_score=0.9
                ),
                ModelSpec(
                    name="fallback-model",
                    size=ModelSize.SMALL,
                    type=ModelType.LANGUAGE,
                    ram_requirement=4.0,
                    vram_requirement=0.0,
                    cpu_cores_min=2,
                    download_url="http://test.com/fallback",
                    local_path="models/fallback",
                    capabilities=["text_generation"],
                    performance_score=0.7
                )
            ]
            
            llm_manager.available_models = {model.name: model for model in test_models}
            
            # Attempt to load model with fallback
            success = llm_manager.load_model("primary-model")
            
            # Should succeed with fallback
            assert success == True
            assert mock_load.call_count == 2  # Primary failed, fallback succeeded
    
    def test_precision_switching(self, deterministic_environment, mock_hardware):
        """Test precision switching based on system load"""
        llm_manager = AdaptiveLLMManager()
        
        # Test precision adjustment
        initial_precision = llm_manager.current_precision
        
        # Simulate high system load
        with patch('psutil.cpu_percent', return_value=90.0), \
             patch('psutil.virtual_memory') as mock_memory:
            
            mock_memory.return_value.percent = 85.0
            
            # Should switch to lower precision
            llm_manager._adjust_precision_for_load()
            
            # Precision should be adjusted for high load
            assert llm_manager.current_precision in ["fp16", "int8"]
        
        # Simulate low system load
        with patch('psutil.cpu_percent', return_value=20.0), \
             patch('psutil.virtual_memory') as mock_memory:
            
            mock_memory.return_value.percent = 30.0
            
            # Should switch to higher precision
            llm_manager._adjust_precision_for_load()
            
            # Precision should be adjusted for low load
            assert llm_manager.current_precision in ["fp32", "fp16"]
    
    def test_deterministic_recovery(self, deterministic_environment, mock_hardware):
        """Test deterministic recovery from errors"""
        llm_manager = AdaptiveLLMManager()
        
        # Mock model that fails deterministically
        error_count = 0
        
        def mock_generate_with_failure(*args, **kwargs):
            nonlocal error_count
            error_count += 1
            if error_count <= 2:
                raise Exception(f"Deterministic failure {error_count}")
            return {"text": "Recovery successful", "tokens": 10}
        
        with patch.object(llm_manager, '_generate_with_model', side_effect=mock_generate_with_failure):
            
            # Attempt generation with recovery
            result = llm_manager.generate_text("test prompt", max_retries=3)
            
            # Should recover after failures
            assert result is not None
            assert result["text"] == "Recovery successful"
            assert error_count == 3  # Failed twice, succeeded on third try
    
    def test_model_performance_tracking(self, deterministic_environment, mock_hardware):
        """Test model performance tracking"""
        llm_manager = AdaptiveLLMManager()
        
        # Mock successful generations
        with patch.object(llm_manager, '_generate_with_model') as mock_generate:
            mock_generate.return_value = {"text": "test output", "tokens": 20}
            
            # Perform multiple generations
            for i in range(10):
                result = llm_manager.generate_text(f"test prompt {i}")
                assert result is not None
            
            # Check performance history
            assert len(llm_manager.performance_history) > 0
            
            # Check performance metrics
            for metric in llm_manager.performance_history:
                assert "timestamp" in metric
                assert "response_time" in metric
                assert "tokens_generated" in metric
                assert "model_name" in metric
                assert metric["response_time"] >= 0
                assert metric["tokens_generated"] > 0
    
    def test_model_switching_stability(self, deterministic_environment, mock_hardware):
        """Test stability during model switching"""
        llm_manager = AdaptiveLLMManager()
        
        # Mock multiple models
        models = ["model-a", "model-b", "model-c"]
        
        with patch.object(llm_manager, '_load_model', return_value=True), \
             patch.object(llm_manager, '_generate_with_model') as mock_generate:
            
            mock_generate.return_value = {"text": "stable output", "tokens": 15}
            
            # Switch between models multiple times
            for i in range(20):
                model_name = models[i % len(models)]
                
                # Load model
                success = llm_manager.load_model(model_name)
                assert success == True
                
                # Generate text
                result = llm_manager.generate_text("stability test")
                assert result is not None
                assert result["text"] == "stable output"
                
                # Check system stability
                status = llm_manager.get_system_status()
                assert status["active"] == True
                assert "current_model" in status
    
    def test_memory_management(self, deterministic_environment, mock_hardware):
        """Test memory management during model operations"""
        llm_manager = AdaptiveLLMManager()
        
        # Track memory usage
        initial_memory = llm_manager._get_memory_usage()
        
        # Simulate memory-intensive operations
        with patch.object(llm_manager, '_load_model', return_value=True), \
             patch.object(llm_manager, '_generate_with_model') as mock_generate:
            
            mock_generate.return_value = {"text": "memory test", "tokens": 25}
            
            # Perform many operations
            for i in range(100):
                result = llm_manager.generate_text(f"memory test {i}")
                assert result is not None
                
                # Check for memory leaks
                current_memory = llm_manager._get_memory_usage()
                memory_increase = current_memory - initial_memory
                
                # Memory increase should be reasonable
                assert memory_increase < 1024 * 1024 * 100  # Less than 100MB increase
    
    def test_concurrent_requests(self, deterministic_environment, mock_hardware):
        """Test handling of concurrent requests"""
        llm_manager = AdaptiveLLMManager()
        
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def generate_text_worker(prompt_id):
            try:
                result = llm_manager.generate_text(f"concurrent test {prompt_id}")
                results_queue.put(("success", prompt_id, result))
            except Exception as e:
                results_queue.put(("error", prompt_id, str(e)))
        
        with patch.object(llm_manager, '_generate_with_model') as mock_generate:
            mock_generate.return_value = {"text": "concurrent output", "tokens": 12}
            
            # Start multiple threads
            threads = []
            for i in range(10):
                thread = threading.Thread(target=generate_text_worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join(timeout=5.0)
            
            # Check results
            results = []
            while not results_queue.empty():
                results.append(results_queue.get())
            
            assert len(results) == 10
            
            # All should be successful
            successful_results = [r for r in results if r[0] == "success"]
            assert len(successful_results) == 10
    
    def test_configuration_management(self, deterministic_environment, mock_hardware):
        """Test configuration management"""
        llm_manager = AdaptiveLLMManager()
        
        # Test configuration loading
        config = llm_manager.config
        assert isinstance(config, dict)
        assert "enabled" in config
        assert "model_preferences" in config
        assert "performance_thresholds" in config
        
        # Test configuration updates
        new_config = config.copy()
        new_config["test_setting"] = "test_value"
        
        llm_manager.update_configuration(new_config)
        
        updated_config = llm_manager.config
        assert updated_config["test_setting"] == "test_value"
    
    def test_error_recovery_scenarios(self, deterministic_environment, mock_hardware):
        """Test various error recovery scenarios"""
        llm_manager = AdaptiveLLMManager()
        
        # Test network error recovery
        with patch.object(llm_manager, '_download_model') as mock_download:
            mock_download.side_effect = [ConnectionError("Network error"), True]
            
            # Should retry and succeed
            result = llm_manager._ensure_model_available("test-model")
            assert mock_download.call_count == 2
        
        # Test disk space error recovery
        with patch.object(llm_manager, '_check_disk_space', return_value=False):
            
            # Should handle gracefully
            result = llm_manager._ensure_model_available("large-model")
            # Should either succeed with cleanup or fail gracefully
            assert isinstance(result, bool)
        
        # Test model corruption recovery
        with patch.object(llm_manager, '_verify_model_integrity', return_value=False), \
             patch.object(llm_manager, '_download_model', return_value=True):
            
            # Should re-download corrupted model
            result = llm_manager._ensure_model_available("corrupted-model")
            assert isinstance(result, bool)
    
    def test_performance_optimization(self, deterministic_environment, mock_hardware, test_timer):
        """Test performance optimization features"""
        llm_manager = AdaptiveLLMManager()
        
        with patch.object(llm_manager, '_generate_with_model') as mock_generate:
            mock_generate.return_value = {"text": "optimized output", "tokens": 30}
            
            # Test generation speed
            start_time = test_timer()
            
            for i in range(10):
                result = llm_manager.generate_text("performance test")
                assert result is not None
            
            elapsed_time = test_timer()
            
            # Should complete 10 generations quickly
            assert elapsed_time < 2.0  # Less than 2 seconds
            
            # Average generation time should be reasonable
            avg_time = elapsed_time / 10
            assert avg_time < 0.2  # Less than 200ms per generation