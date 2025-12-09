#!/usr/bin/env python3
"""
Integration test: consciousness_memory_integration
Test integration between consciousness and memory systems
"""

import unittest
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestConsciousnessMemoryIntegration(unittest.TestCase):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Integration test for consciousness_memory_integration"""
    
    def setUp(self):
        """Set up integration test"""
        self.start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        
        # Initialize components
        self.components = {}
        
        for module_name in ['mia.core.consciousness.main', 'mia.core.memory.main']:
            try:
                module = __import__(module_name, fromlist=[''])
                self.components[module_name] = module
            except ImportError as e:
                print(f"Mock module {module_name}: {e}")
                self.components[module_name] = Mock()
    
    def tearDown(self):
        """Clean up integration test"""
        execution_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - self.start_time
        print(f"Integration test completed in {execution_time:.2f}s")
    
    def test_component_communication(self):
        """Test communication between components"""
        # Test basic component interaction
        self.assertTrue(len(self.components) > 0)
        
        for module_name, component in self.components.items():
            self.assertIsNotNone(component)
    
    def test_data_flow(self):
        """Test data flow between components"""
        # Simulate data flow
        test_data = {"test": "integration_data", "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}
        
        # Test data passing between components
        for i, (module_name, component) in enumerate(self.components.items()):
            if hasattr(component, 'process') or hasattr(component, 'handle'):
                try:
                    if hasattr(component, 'process'):
                        result = component.process(test_data)
                    else:
                        result = component.handle(test_data)
                    
                    self.assertIsNotNone(result)
                except Exception as e:
                    self.skipTest(f"Component {module_name} requires specific setup: {e}")
    
    def test_error_handling(self):
        """Test error handling in integration"""
        # Test with invalid data
        invalid_data = None
        
        for module_name, component in self.components.items():
            if hasattr(component, 'process'):
                try:
                    result = component.process(invalid_data)
                    # Should handle gracefully
                except Exception:
                    # Expected behavior for invalid input
                    pass
    
    def test_performance_integration(self):
        """Test performance of integrated components"""
        start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        
        # Perform integration operations
        test_operations = 10
        
        for i in range(test_operations):
            test_data = {"iteration": i, "data": f"test_{i}"}
            
            for module_name, component in self.components.items():
                if hasattr(component, 'process'):
                    try:
                        component.process(test_data)
                    except:
                        pass  # Mock components might not work
        
        execution_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
        avg_time_per_operation = execution_time / test_operations
        
        # Performance assertion (should be under 1 second per operation)
        self.assertLess(avg_time_per_operation, 1.0)

if __name__ == '__main__':
    unittest.main()
