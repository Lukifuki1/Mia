#!/usr/bin/env python3
"""
MIA Enterprise AGI - Validation Utils
====================================

Utility functions for validation operations.
"""

import os
import sys
import json
import hashlib
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import psutil


class ValidationUtils:
    """Validation utility functions"""
    
    @staticmethod
    def setup_validation_logging(name: str) -> logging.Logger:
        """Setup validation logging"""
        logger = logging.getLogger(f"MIA.Validation.{name}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    @staticmethod
    def generate_test_hash(data: Any) -> str:
        """Generate hash for test data"""
        if isinstance(data, dict):
            sorted_data = json.dumps(data, sort_keys=True)
        else:
            sorted_data = str(data)
        
        return hashlib.sha256(sorted_data.encode()).hexdigest()
    
    @staticmethod
    def measure_performance(func, *args, **kwargs) -> Tuple[Any, float]:
        """Measure function performance"""
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        return result, execution_time
    
    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Get current system metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "timestamp": time.time()
        }
    
    @staticmethod
    def validate_file_structure(project_root: Path, required_files: List[str]) -> Dict[str, bool]:
        """Validate required file structure"""
        validation_results = {}
        
        for file_path in required_files:
            full_path = project_root / file_path
            validation_results[file_path] = full_path.exists()
        
        return validation_results
    
    @staticmethod
    def calculate_consistency_score(test_results: List[Dict[str, Any]]) -> float:
        """Calculate consistency score from test results"""
        if not test_results:
            return 0.0
        
        consistent_tests = sum(1 for result in test_results 
                             if result.get("is_deterministic", False))
        
        return consistent_tests / len(test_results)
    
    @staticmethod
    def generate_validation_report(results: Dict[str, Any], output_path: Path) -> None:
        """Generate validation report"""
        report = {
            "validation_timestamp": time.time(),
            "results": results,
            "summary": {
                "total_tests": len(results),
                "passed_tests": sum(1 for r in results.values() 
                                  if r.get("status") == "pass"),
                "overall_score": ValidationUtils.calculate_consistency_score(
                    list(results.values())
                )
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
    
    @staticmethod
    def check_component_health(component_path: Path) -> Dict[str, Any]:
        """Check component health"""
        health_status = {
            "exists": component_path.exists(),
            "readable": False,
            "size_bytes": 0,
            "last_modified": None
        }
        
        if health_status["exists"]:
            try:
                health_status["readable"] = os.access(component_path, os.R_OK)
                health_status["size_bytes"] = component_path.stat().st_size
                health_status["last_modified"] = component_path.stat().st_mtime
            except Exception as e:
                health_status["error"] = str(e)
        
        return health_status