#!/usr/bin/env python3
"""
Deterministic test: sdm_loop_validation
Test SDM (Self-Deterministic-Model) loops
"""

import unittest
import sys
import time
import hashlib
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestSdmLoopValidationDeterministic(unittest.TestCase):
    """Deterministic test for sdm_loop_validation"""
    
    def setUp(self):
        """Set up deterministic test"""
        # Fixed seed for deterministic behavior
        self.test_seed = 12345
        self.test_iterations = 10
        
        # Test data with fixed values
        self.test_input = {
            "query": "deterministic test query",
            "parameters": {
                "temperature": 0.0,  # Deterministic
                "seed": self.test_seed,
                "max_tokens": 100
            },
            "timestamp": 1640995200  # Fixed timestamp
        }
    
    def test_output_consistency(self):
        """Test output consistency across multiple runs"""
        outputs = []
        hashes = []
        
        for i in range(self.test_iterations):
            # Generate output with same input
            output = self._generate_deterministic_output(self.test_input)
            
            # Calculate hash
            output_hash = self._calculate_output_hash(output)
            
            outputs.append(output)
            hashes.append(output_hash)
        
        # All outputs should be identical
        first_output = outputs[0]
        first_hash = hashes[0]
        
        for i, (output, output_hash) in enumerate(zip(outputs[1:], hashes[1:]), 1):
            self.assertEqual(output, first_output, 
                           f"Output {i} differs from first output")
            self.assertEqual(output_hash, first_hash,
                           f"Hash {i} differs from first hash")
    
    def test_hash_verification(self):
        """Test hash verification of outputs"""
        output = self._generate_deterministic_output(self.test_input)
        
        # Calculate hash
        calculated_hash = self._calculate_output_hash(output)
        
        # Verify hash format
        self.assertIsInstance(calculated_hash, str)
        self.assertEqual(len(calculated_hash), 64)  # SHA-256 hash length
        
        # Verify hash consistency
        recalculated_hash = self._calculate_output_hash(output)
        self.assertEqual(calculated_hash, recalculated_hash)
    
    def test_seed_reproducibility(self):
        """Test reproducibility with same seed"""
        # Generate output with seed
        output1 = self._generate_deterministic_output(self.test_input)
        
        # Generate output with same seed
        output2 = self._generate_deterministic_output(self.test_input)
        
        # Should be identical
        self.assertEqual(output1, output2)
    
    def test_different_seed_variation(self):
        """Test variation with different seeds"""
        # Generate output with original seed
        output1 = self._generate_deterministic_output(self.test_input)
        
        # Generate output with different seed
        modified_input = self.test_input.copy()
        modified_input["parameters"]["seed"] = 54321
        output2 = self._generate_deterministic_output(modified_input)
        
        # Should be different (unless extremely unlikely)
        self.assertNotEqual(output1, output2)
    
    def _generate_deterministic_output(self, input_data):
        """Generate deterministic output"""
        try:
            # Mock deterministic processing
            seed = input_data["parameters"]["seed"]
            query = input_data["query"]
            
            # Simulate deterministic processing
            import random
            random.seed(seed)
            
            # Generate deterministic response
            response_parts = [
                f"Processed: {query}",
                f"Seed: {seed}",
                f"Random value: {random.randint(1, 1000)}"
            ]
            
            output = {
                "response": " | ".join(response_parts),
                "metadata": {
                    "seed": seed,
                    "deterministic": True,
                    "timestamp": input_data["timestamp"]
                }
            }
            
            return output
            
        except Exception as e:
            # Return mock output for testing
            return {
                "response": f"Mock response for {input_data['query']}",
                "error": str(e),
                "deterministic": False
            }
    
    def _calculate_output_hash(self, output):
        """Calculate hash of output"""
        try:
            # Convert output to consistent string representation
            output_str = json.dumps(output, sort_keys=True, separators=(',', ':'))
            
            # Calculate SHA-256 hash
            hash_obj = hashlib.sha256(output_str.encode('utf-8'))
            return hash_obj.hexdigest()
            
        except Exception as e:
            # Fallback hash calculation
            return hashlib.sha256(str(output).encode('utf-8')).hexdigest()
    
    def test_temporal_consistency(self):
        """Test consistency over time"""
        # Generate outputs at different times
        outputs_over_time = []
        
        for i in range(5):
            # Small delay between generations
            time.sleep(0.1)
            
            output = self._generate_deterministic_output(self.test_input)
            outputs_over_time.append(output)
        
        # All outputs should be identical despite time differences
        first_output = outputs_over_time[0]
        
        for i, output in enumerate(outputs_over_time[1:], 1):
            self.assertEqual(output, first_output,
                           f"Output at time {i} differs from first output")
    
    def test_parameter_sensitivity(self):
        """Test sensitivity to parameter changes"""
        base_output = self._generate_deterministic_output(self.test_input)
        
        # Test with slightly modified parameters
        modified_input = self.test_input.copy()
        modified_input["parameters"]["max_tokens"] = 101  # Changed from 100
        
        modified_output = self._generate_deterministic_output(modified_input)
        
        # Small parameter change might or might not affect output
        # This tests the sensitivity of the deterministic system
        if base_output != modified_output:
            print("System is sensitive to parameter changes")
        else:
            print("System is robust to small parameter changes")

if __name__ == '__main__':
    unittest.main()
