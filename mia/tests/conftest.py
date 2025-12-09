#!/usr/bin/env python3
"""
MIA Enterprise AGI - Test Configuration
Global test fixtures and configuration for deterministic testing
"""

import pytest
import os
import sys
import time
import logging
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import Mock, patch

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mia/tests/test_results.log'),
        logging.StreamHandler()
    ]
)

@pytest.fixture(scope="session")
def test_config():
    """Global test configuration"""
    return {
        "deterministic_mode": True,
        "random_seed": 42,
        "test_timeout": 300,
        "memory_limit_mb": 1024,
        "temp_dir": tempfile.mkdtemp(prefix="mia_test_"),
        "enterprise_mode": True,
        "security_enabled": True,
        "debug_mode": True
    }

@pytest.fixture(scope="session")
def temp_workspace(test_config):
    """Create temporary workspace for tests"""
    workspace = Path(test_config["temp_dir"]) / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    
    # Create test data directories
    (workspace / "data").mkdir(exist_ok=True)
    (workspace / "models").mkdir(exist_ok=True)
    (workspace / "logs").mkdir(exist_ok=True)
    (workspace / "memory").mkdir(exist_ok=True)
    (workspace / "projects").mkdir(exist_ok=True)
    
    yield workspace
    
    # Cleanup
    try:
        shutil.rmtree(workspace)
    except:
        pass

@pytest.fixture(scope="function")
def deterministic_environment(test_config):
    """Setup deterministic environment for each test"""
    # Set random seeds
    import random
    import numpy as np
    
    random.seed(test_config["random_seed"])
    np.random.seed(test_config["random_seed"])
    
    # Set environment variables for deterministic behavior
    os.environ["PYTHONHASHSEED"] = str(test_config["random_seed"])
    os.environ["MIA_DETERMINISTIC_MODE"] = "true"
    os.environ["MIA_TEST_MODE"] = "true"
    os.environ["MIA_ENTERPRISE_MODE"] = "true"
    
    yield test_config
    
    # Cleanup environment
    for key in ["PYTHONHASHSEED", "MIA_DETERMINISTIC_MODE", "MIA_TEST_MODE", "MIA_ENTERPRISE_MODE"]:
        os.environ.pop(key, None)

@pytest.fixture(scope="function")
def mock_hardware():
    """Mock hardware detection for consistent testing"""
    hardware_config = {
        "cpu_cores": 8,
        "total_memory": 16 * 1024 * 1024 * 1024,  # 16GB
        "gpu_available": False,
        "gpu_memory": 0,
        "disk_space": 100 * 1024 * 1024 * 1024,  # 100GB
        "platform": "linux",
        "architecture": "x86_64"
    }
    
    with patch('psutil.cpu_count', return_value=hardware_config["cpu_cores"]), \
         patch('psutil.virtual_memory') as mock_memory, \
         patch('psutil.disk_usage') as mock_disk:
        
        mock_memory.return_value.total = hardware_config["total_memory"]
        mock_memory.return_value.available = hardware_config["total_memory"] * 0.7
        mock_memory.return_value.percent = 30.0
        
        mock_disk.return_value.total = hardware_config["disk_space"]
        mock_disk.return_value.free = hardware_config["disk_space"] * 0.8
        mock_disk.return_value.used = hardware_config["disk_space"] * 0.2
        
        yield hardware_config

@pytest.fixture(scope="function")
def isolated_memory():
    """Isolated memory system for testing"""
    from mia.core.memory.main import MemorySystem
    
    # Create isolated memory instance
    memory = MemorySystem(config_path="test_memory_config.json")
    memory.config["storage_path"] = "test_memory_storage"
    
    yield memory
    
    # Cleanup
    try:
        import shutil
        if Path("test_memory_storage").exists():
            shutil.rmtree("test_memory_storage")
        if Path("test_memory_config.json").exists():
            Path("test_memory_config.json").unlink()
    except:
        pass

@pytest.fixture(scope="function")
def isolated_consciousness():
    """Isolated consciousness system for testing"""
    from mia.core.consciousness.main import ConsciousnessModule
    
    # Create isolated consciousness instance
    consciousness = ConsciousnessModule()
    consciousness.config_path = "test_consciousness_config.json"
    
    yield consciousness
    
    # Cleanup
    try:
        if Path("test_consciousness_config.json").exists():
            Path("test_consciousness_config.json").unlink()
    except:
        pass

@pytest.fixture(scope="function")
def test_timer():
    """Timer for performance testing"""
    start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
    yield lambda: self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time

@pytest.fixture(scope="function")
def security_context():
    """Security context for security tests"""
    return {
        "owner_id": "test_owner",
        "security_level": "high",
        "permissions": ["read", "write", "execute"],
        "encryption_enabled": True,
        "audit_enabled": True
    }

@pytest.fixture(scope="session")
def enterprise_config():
    """Enterprise configuration for tests"""
    return {
        "enterprise_mode": True,
        "quality_control_enabled": True,
        "agi_agents_enabled": True,
        "immune_system_enabled": True,
        "security_systems_enabled": True,
        "monitoring_enabled": True,
        "logging_level": "DEBUG",
        "performance_monitoring": True,
        "resource_monitoring": True
    }

# Test markers
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "stress: Stress tests")
    config.addinivalue_line("markers", "recovery: Recovery tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "deterministic: Deterministic tests")
    config.addinivalue_line("markers", "multiagent: Multi-agent tests")
    config.addinivalue_line("markers", "desktop: Desktop app tests")
    config.addinivalue_line("markers", "lsp: Language support tests")
    config.addinivalue_line("markers", "enterprise: Enterprise tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "critical: Critical system tests")

# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add markers based on test location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "stress" in str(item.fspath):
            item.add_marker(pytest.mark.stress)
        elif "recovery" in str(item.fspath):
            item.add_marker(pytest.mark.recovery)
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        elif "deterministic" in str(item.fspath):
            item.add_marker(pytest.mark.deterministic)
        elif "multiagent" in str(item.fspath):
            item.add_marker(pytest.mark.multiagent)
        elif "desktop" in str(item.fspath):
            item.add_marker(pytest.mark.desktop)
        elif "lsp" in str(item.fspath):
            item.add_marker(pytest.mark.lsp)

# Utility functions for tests
def assert_deterministic_output(func, *args, **kwargs):
    """Assert that function produces deterministic output"""
    results = []
    for _ in range(3):
        result = func(*args, **kwargs)
        results.append(result)
    
    # All results should be identical
    assert all(r == results[0] for r in results), "Function output is not deterministic"
    return results[0]

def assert_memory_stable(memory_system, operation_func):
    """Assert that memory system remains stable during operation"""
    initial_state = memory_system.get_system_status()
    
    # Perform operation
    result = operation_func()
    
    # Check memory stability
    final_state = memory_system.get_system_status()
    
    assert final_state["total_memories"] >= initial_state["total_memories"], "Memory count decreased"
    assert final_state["integrity_score"] >= 0.9, "Memory integrity compromised"
    
    return result

def assert_consciousness_stable(consciousness, operation_func):
    """Assert that consciousness remains stable during operation"""
    initial_state = consciousness.get_consciousness_state()
    
    # Perform operation
    result = operation_func()
    
    # Check consciousness stability
    final_state = consciousness.get_consciousness_state()
    
    assert final_state["consciousness_state"] != "DORMANT", "Consciousness went dormant"
    assert final_state["stability_score"] >= 0.8, "Consciousness stability compromised"
    
    return result

def assert_enterprise_compliance(system_status):
    """Assert enterprise compliance requirements"""
    required_components = [
        "consciousness", "memory", "adaptive_llm", "quality_control",
        "agi_agents", "immune_system", "security_systems"
    ]
    
    for component in required_components:
        assert component in system_status, f"Missing enterprise component: {component}"
        assert system_status[component].get("status") == "active", f"Component not active: {component}"
    
    assert system_status.get("enterprise_mode", False), "Enterprise mode not enabled"
    assert system_status.get("security_level", "low") in ["high", "critical"], "Insufficient security level"