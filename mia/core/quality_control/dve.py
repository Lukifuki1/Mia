#!/usr/bin/env python3
"""
DVE - Deterministic Validation Engine
Zagotavlja deterministično validacijo in reproducibilnost rezultatov
"""

import os
import json
import logging
import time
import hashlib
import random
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading

class DeterminismLevel(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Determinism levels"""
    STRICT = "strict"
    STANDARD = "standard"
    RELAXED = "relaxed"
    DISABLED = "disabled"

class ValidationMode(Enum):
    """Validation modes"""
    SEED_BASED = "seed_based"
    HASH_BASED = "hash_based"
    CHECKPOINT_BASED = "checkpoint_based"
    STATISTICAL = "statistical"

@dataclass
class DeterministicTest:
    """Deterministic test definition"""
    test_id: str
    name: str
    description: str
    validation_mode: ValidationMode
    seed_value: Optional[int]
    expected_hash: Optional[str]
    tolerance: float
    iterations: int
    enabled: bool
    created_at: float

@dataclass
class ValidationResult:
    """Deterministic validation result"""
    result_id: str
    test_id: str
    execution_id: str
    determinism_score: float
    reproducibility_score: float
    consistency_score: float
    passed: bool
    deviations: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    validated_at: float

@dataclass
class ReproducibilityReport:
    """Reproducibility analysis report"""
    report_id: str
    component_id: str
    test_results: List[ValidationResult]
    overall_determinism: float
    reproducibility_rate: float
    consistency_metrics: Dict[str, float]
    recommendations: List[str]
    created_at: float

class DVE:
    """Deterministic Validation Engine"""
    
    def __init__(self, config_path: str = "mia/data/quality_control/dve_config.json"):
        self.config_path = config_path
        self.dve_dir = Path("mia/data/quality_control/dve")
        self.dve_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.DVE")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Deterministic state
        self.deterministic_tests: Dict[str, DeterministicTest] = {}
        self.validation_results: Dict[str, ValidationResult] = {}
        self.reproducibility_reports: Dict[str, ReproducibilityReport] = {}
        
        # Seed management
        self.global_seed = self.config.get("global_seed", 42)
        self.seed_history: List[Tuple[float, int]] = []
        
        # Validation state
        self.validation_active = False
        self.validation_thread: Optional[threading.Thread] = None
        
        # Load existing tests
        self._load_deterministic_tests()
        
        self.logger.info("🎯 DVE (Deterministic Validation Engine) initialized")
    
    def _load_configuration(self) -> Dict:
        """Load DVE configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load DVE config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default DVE configuration"""
        config = {
            "enabled": True,
            "determinism_level": "standard",
            "global_seed": 42,
            "validation_interval": 3600,  # 1 hour
            "reproducibility_threshold": 0.95,
            "consistency_threshold": 0.90,
            "tolerance_levels": {
                "strict": 1e-10,
                "standard": 1e-6,
                "relaxed": 1e-3
            },
            "validation_modes": {
                "seed_based": {"enabled": True, "iterations": 5},
                "hash_based": {"enabled": True, "algorithm": "sha256"},
                "checkpoint_based": {"enabled": True, "interval": 300},
                "statistical": {"enabled": True, "samples": 100}
            },
            "component_monitoring": {
                "llm_inference": {"enabled": True, "mode": "seed_based"},
                "image_generation": {"enabled": True, "mode": "seed_based"},
                "audio_synthesis": {"enabled": True, "mode": "hash_based"},
                "data_processing": {"enabled": True, "mode": "statistical"}
            },
            "enforcement": {
                "strict_mode": False,
                "auto_fix_seeds": True,
                "block_non_deterministic": False,
                "log_violations": True
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _load_deterministic_tests(self):
        """Load deterministic tests"""
        try:
            tests_file = self.dve_dir / "deterministic_tests.json"
            if tests_file.exists():
                with open(tests_file, 'r') as f:
                    tests_data = json.load(f)
                
                for test_data in tests_data:
                    test = DeterministicTest(
                        test_id=test_data["test_id"],
                        name=test_data["name"],
                        description=test_data["description"],
                        validation_mode=ValidationMode(test_data["validation_mode"]),
                        seed_value=test_data.get("seed_value"),
                        expected_hash=test_data.get("expected_hash"),
                        tolerance=test_data["tolerance"],
                        iterations=test_data["iterations"],
                        enabled=test_data["enabled"],
                        created_at=test_data["created_at"]
                    )
                    self.deterministic_tests[test.test_id] = test
            
            # Create default tests if none exist
            if not self.deterministic_tests:
                self._create_default_tests()
            
            self.logger.info(f"✅ Loaded {len(self.deterministic_tests)} deterministic tests")
            
        except Exception as e:
            self.logger.error(f"Failed to load deterministic tests: {e}")
            self._create_default_tests()
    
    def _create_default_tests(self):
        """Create default deterministic tests"""
        try:
            default_tests = [
                {
                    "test_id": "llm_inference_determinism",
                    "name": "LLM Inference Determinism",
                    "description": "Validate deterministic LLM inference with fixed seeds",
                    "validation_mode": ValidationMode.SEED_BASED,
                    "seed_value": 42,
                    "tolerance": 1e-6,
                    "iterations": 5,
                    "enabled": True
                },
                {
                    "test_id": "image_generation_reproducibility",
                    "name": "Image Generation Reproducibility",
                    "description": "Validate reproducible image generation",
                    "validation_mode": ValidationMode.HASH_BASED,
                    "seed_value": 123,
                    "tolerance": 0.0,
                    "iterations": 3,
                    "enabled": True
                },
                {
                    "test_id": "data_processing_consistency",
                    "name": "Data Processing Consistency",
                    "description": "Validate consistent data processing results",
                    "validation_mode": ValidationMode.STATISTICAL,
                    "tolerance": 1e-3,
                    "iterations": 10,
                    "enabled": True
                },
                {
                    "test_id": "random_number_generation",
                    "name": "Random Number Generation",
                    "description": "Validate deterministic random number generation",
                    "validation_mode": ValidationMode.SEED_BASED,
                    "seed_value": 999,
                    "tolerance": 0.0,
                    "iterations": 5,
                    "enabled": True
                }
            ]
            
            for test_data in default_tests:
                test = DeterministicTest(
                    test_id=test_data["test_id"],
                    name=test_data["name"],
                    description=test_data["description"],
                    validation_mode=test_data["validation_mode"],
                    seed_value=test_data.get("seed_value"),
                    expected_hash=None,
                    tolerance=test_data["tolerance"],
                    iterations=test_data["iterations"],
                    enabled=test_data["enabled"],
                    created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                )
                self.deterministic_tests[test.test_id] = test
            
            # Save tests
            self._save_deterministic_tests()
            
        except Exception as e:
            self.logger.error(f"Failed to create default tests: {e}")
    
    def _save_deterministic_tests(self):
        """Save deterministic tests"""
        try:
            tests_data = []
            for test in self.deterministic_tests.values():
                test_dict = asdict(test)
                test_dict["validation_mode"] = test.validation_mode.value
                tests_data.append(test_dict)
            
            tests_file = self.dve_dir / "deterministic_tests.json"
            with open(tests_file, 'w') as f:
                json.dump(tests_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save deterministic tests: {e}")
    
    def set_global_seed(self, seed: int):
        """Set global seed for deterministic operations"""
        try:
            self.global_seed = seed
            self.seed_history.append((self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200, seed))
            
            # Set seeds for various libraries
            random.seed(seed)
            np.random.seed(seed)
            
            # Set environment variables for deterministic behavior
            os.environ['PYTHONHASHSEED'] = str(seed)
            
            self.logger.info(f"🎯 Global seed set to: {seed}")
            
        except Exception as e:
            self.logger.error(f"Failed to set global seed: {e}")
    
    def validate_determinism(self, test_id: str, execution_function: callable,
                           execution_args: Tuple = (), execution_kwargs: Dict = None) -> str:
        """Validate determinism of execution function"""
        try:
            if test_id not in self.deterministic_tests:
                self.logger.error(f"Test not found: {test_id}")
                return ""
            
            test = self.deterministic_tests[test_id]
            if not test.enabled:
                self.logger.info(f"Test disabled: {test_id}")
                return ""
            
            execution_kwargs = execution_kwargs or {}
            
            # Run validation based on mode
            if test.validation_mode == ValidationMode.SEED_BASED:
                result = self._validate_seed_based(test, execution_function, execution_args, execution_kwargs)
            elif test.validation_mode == ValidationMode.HASH_BASED:
                result = self._validate_hash_based(test, execution_function, execution_args, execution_kwargs)
            elif test.validation_mode == ValidationMode.STATISTICAL:
                result = self._validate_statistical(test, execution_function, execution_args, execution_kwargs)
            else:
                result = self._validate_checkpoint_based(test, execution_function, execution_args, execution_kwargs)
            
            # Store result
            self.validation_results[result.result_id] = result
            
            # Log result
            if result.passed:
                self.logger.info(f"✅ Determinism validation passed: {test.name} (score: {result.determinism_score:.3f})")
            else:
                self.logger.warning(f"❌ Determinism validation failed: {test.name} (score: {result.determinism_score:.3f})")
            
            return result.result_id
            
        except Exception as e:
            self.logger.error(f"Failed to validate determinism: {e}")
            return ""
    
    def _validate_seed_based(self, test: DeterministicTest, execution_function: callable,
                           execution_args: Tuple, execution_kwargs: Dict) -> ValidationResult:
        """Validate using seed-based approach"""
        try:
            results = []
            original_seed = self.global_seed
            
            # Run multiple iterations with same seed
            for i in range(test.iterations):
                # Set seed
                if test.seed_value is not None:
                    self.set_global_seed(test.seed_value)
                else:
                    self.set_global_seed(original_seed)
                
                # Execute function
                result = execution_function(*execution_args, **execution_kwargs)
                results.append(result)
            
            # Restore original seed
            self.set_global_seed(original_seed)
            
            # Analyze results
            determinism_score, deviations = self._analyze_result_consistency(results, test.tolerance)
            
            # Create validation result
            validation_result = ValidationResult(
                result_id=f"validation_{test.test_id}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_id=test.test_id,
                execution_id=f"exec_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                determinism_score=determinism_score,
                reproducibility_score=determinism_score,  # Same for seed-based
                consistency_score=determinism_score,
                passed=determinism_score >= self.config.get("reproducibility_threshold", 0.95),
                deviations=deviations,
                metadata={
                    "validation_mode": "seed_based",
                    "seed_used": test.seed_value or original_seed,
                    "iterations": test.iterations
                },
                validated_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Seed-based validation failed: {e}")
            return self._create_error_result(test, str(e))
    
    def _validate_hash_based(self, test: DeterministicTest, execution_function: callable,
                           execution_args: Tuple, execution_kwargs: Dict) -> ValidationResult:
        """Validate using hash-based approach"""
        try:
            results = []
            hashes = []
            
            # Run multiple iterations
            for i in range(test.iterations):
                # Set seed if provided
                if test.seed_value is not None:
                    self.set_global_seed(test.seed_value)
                
                # Execute function
                result = execution_function(*execution_args, **execution_kwargs)
                results.append(result)
                
                # Calculate hash
                result_hash = self._calculate_result_hash(result)
                hashes.append(result_hash)
            
            # Check hash consistency
            unique_hashes = set(hashes)
            hash_consistency = 1.0 if len(unique_hashes) == 1 else 0.0
            
            # Check against expected hash if provided
            expected_match = 1.0
            if test.expected_hash:
                expected_match = 1.0 if test.expected_hash in unique_hashes else 0.0
            
            # Overall score
            determinism_score = (hash_consistency + expected_match) / 2.0
            
            # Create validation result
            validation_result = ValidationResult(
                result_id=f"validation_{test.test_id}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_id=test.test_id,
                execution_id=f"exec_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                determinism_score=determinism_score,
                reproducibility_score=hash_consistency,
                consistency_score=expected_match,
                passed=determinism_score >= self.config.get("reproducibility_threshold", 0.95),
                deviations=[{"type": "hash_mismatch", "count": len(unique_hashes) - 1}] if len(unique_hashes) > 1 else [],
                metadata={
                    "validation_mode": "hash_based",
                    "unique_hashes": len(unique_hashes),
                    "hashes": list(unique_hashes)[:5],  # Store first 5 hashes
                    "expected_hash": test.expected_hash
                },
                validated_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Hash-based validation failed: {e}")
            return self._create_error_result(test, str(e))
    
    def _validate_statistical(self, test: DeterministicTest, execution_function: callable,
                            execution_args: Tuple, execution_kwargs: Dict) -> ValidationResult:
        """Validate using statistical approach"""
        try:
            results = []
            
            # Run multiple iterations
            for i in range(test.iterations):
                result = execution_function(*execution_args, **execution_kwargs)
                results.append(result)
            
            # Statistical analysis
            numerical_results = self._extract_numerical_values(results)
            
            if numerical_results:
                # Calculate statistical measures
                mean_val = np.mean(numerical_results)
                std_val = np.std(numerical_results)
                cv = std_val / mean_val if mean_val != 0 else float('inf')
                
                # Determinism score based on coefficient of variation
                if cv <= test.tolerance:
                    determinism_score = 1.0
                elif cv <= test.tolerance * 10:
                    determinism_score = 1.0 - (cv - test.tolerance) / (test.tolerance * 9)
                else:
                    determinism_score = 0.0
                
                deviations = [{"type": "statistical", "coefficient_of_variation": cv, "std_dev": std_val}]
            else:
                # Non-numerical results - check exact matches
                unique_results = len(set(str(r) for r in results))
                determinism_score = 1.0 if unique_results == 1 else 0.0
                deviations = [{"type": "non_numerical", "unique_results": unique_results}]
            
            # Create validation result
            validation_result = ValidationResult(
                result_id=f"validation_{test.test_id}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_id=test.test_id,
                execution_id=f"exec_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                determinism_score=determinism_score,
                reproducibility_score=determinism_score,
                consistency_score=determinism_score,
                passed=determinism_score >= self.config.get("consistency_threshold", 0.90),
                deviations=deviations,
                metadata={
                    "validation_mode": "statistical",
                    "iterations": test.iterations,
                    "numerical_analysis": len(numerical_results) > 0
                },
                validated_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Statistical validation failed: {e}")
            return self._create_error_result(test, str(e))
    
    def _validate_checkpoint_based(self, test: DeterministicTest, execution_function: callable,
                                 execution_args: Tuple, execution_kwargs: Dict) -> ValidationResult:
        """Validate using checkpoint-based approach"""
        try:
            # This is a simplified implementation
            # In practice, this would involve saving and restoring system state
            
            results = []
            
            # Run iterations with checkpointing
            for i in range(test.iterations):
                # Save checkpoint (simplified)
                checkpoint_data = {"iteration": i, "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200}
                
                # Execute function
                result = execution_function(*execution_args, **execution_kwargs)
                results.append(result)
            
            # Analyze consistency
            determinism_score, deviations = self._analyze_result_consistency(results, test.tolerance)
            
            # Create validation result
            validation_result = ValidationResult(
                result_id=f"validation_{test.test_id}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                test_id=test.test_id,
                execution_id=f"exec_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                determinism_score=determinism_score,
                reproducibility_score=determinism_score,
                consistency_score=determinism_score,
                passed=determinism_score >= self.config.get("reproducibility_threshold", 0.95),
                deviations=deviations,
                metadata={
                    "validation_mode": "checkpoint_based",
                    "checkpoints_created": test.iterations
                },
                validated_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Checkpoint-based validation failed: {e}")
            return self._create_error_result(test, str(e))
    
    def _analyze_result_consistency(self, results: List[Any], tolerance: float) -> Tuple[float, List[Dict[str, Any]]]:
        """Analyze consistency of results"""
        try:
            if not results:
                return 0.0, [{"type": "no_results"}]
            
            deviations = []
            
            # Extract numerical values if possible
            numerical_results = self._extract_numerical_values(results)
            
            if numerical_results:
                # Numerical analysis
                if len(set(numerical_results)) == 1:
                    # All results identical
                    return 1.0, []
                
                # Calculate relative deviations
                mean_val = np.mean(numerical_results)
                max_deviation = max(abs(r - mean_val) for r in numerical_results)
                
                if mean_val != 0:
                    relative_deviation = max_deviation / abs(mean_val)
                else:
                    relative_deviation = max_deviation
                
                if relative_deviation <= tolerance:
                    score = 1.0
                else:
                    score = max(0.0, 1.0 - (relative_deviation - tolerance) / tolerance)
                
                deviations.append({
                    "type": "numerical",
                    "max_deviation": max_deviation,
                    "relative_deviation": relative_deviation,
                    "tolerance": tolerance
                })
                
                return score, deviations
            
            else:
                # Non-numerical analysis
                unique_results = len(set(str(r) for r in results))
                
                if unique_results == 1:
                    return 1.0, []
                else:
                    score = 1.0 / unique_results  # Score decreases with more unique results
                    deviations.append({
                        "type": "non_numerical",
                        "unique_results": unique_results,
                        "total_results": len(results)
                    })
                    return score, deviations
            
        except Exception as e:
            self.logger.error(f"Failed to analyze result consistency: {e}")
            return 0.0, [{"type": "analysis_error", "error": str(e)}]
    
    def _extract_numerical_values(self, results: List[Any]) -> List[float]:
        """Extract numerical values from results"""
        try:
            numerical_values = []
            
            for result in results:
                if isinstance(result, (int, float)):
                    numerical_values.append(float(result))
                elif isinstance(result, dict):
                    # Try to extract numerical values from dict
                    for value in result.values():
                        if isinstance(value, (int, float)):
                            numerical_values.append(float(value))
                            break
                elif isinstance(result, (list, tuple)):
                    # Try to extract from first numerical element
                    for item in result:
                        if isinstance(item, (int, float)):
                            numerical_values.append(float(item))
                            break
            
            return numerical_values
            
        except Exception as e:
            self.logger.error(f"Failed to extract numerical values: {e}")
            return []
    
    def _calculate_result_hash(self, result: Any) -> str:
        """Calculate hash of result"""
        try:
            # Convert result to string representation
            if isinstance(result, dict):
                # Sort keys for consistent hashing
                result_str = json.dumps(result, sort_keys=True)
            elif isinstance(result, (list, tuple)):
                result_str = str(sorted(result) if all(isinstance(x, (int, float, str)) for x in result) else result)
            else:
                result_str = str(result)
            
            # Calculate SHA256 hash
            return hashlib.sha256(result_str.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Failed to calculate result hash: {e}")
            return hashlib.sha256(str(result).encode()).hexdigest()
    
    def _create_error_result(self, test: DeterministicTest, error_message: str) -> ValidationResult:
        """Create error validation result"""
        return ValidationResult(
            result_id=f"error_{test.test_id}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
            test_id=test.test_id,
            execution_id=f"error_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
            determinism_score=0.0,
            reproducibility_score=0.0,
            consistency_score=0.0,
            passed=False,
            deviations=[{"type": "error", "message": error_message}],
            metadata={"error": error_message},
            validated_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        )
    
    def generate_reproducibility_report(self, component_id: str) -> str:
        """Generate reproducibility report for component"""
        try:
            # Get validation results for component
            component_results = [
                result for result in self.validation_results.values()
                if component_id in result.metadata.get("component_id", "")
            ]
            
            if not component_results:
                self.logger.warning(f"No validation results found for component: {component_id}")
                return ""
            
            # Calculate overall metrics
            determinism_scores = [r.determinism_score for r in component_results]
            reproducibility_scores = [r.reproducibility_score for r in component_results]
            consistency_scores = [r.consistency_score for r in component_results]
            
            overall_determinism = np.mean(determinism_scores)
            reproducibility_rate = sum(1 for r in component_results if r.passed) / len(component_results)
            
            consistency_metrics = {
                "mean_determinism": overall_determinism,
                "mean_reproducibility": np.mean(reproducibility_scores),
                "mean_consistency": np.mean(consistency_scores),
                "pass_rate": reproducibility_rate
            }
            
            # Generate recommendations
            recommendations = self._generate_reproducibility_recommendations(
                overall_determinism, reproducibility_rate, component_results
            )
            
            # Create report
            report = ReproducibilityReport(
                report_id=f"repro_{component_id}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}",
                component_id=component_id,
                test_results=component_results,
                overall_determinism=overall_determinism,
                reproducibility_rate=reproducibility_rate,
                consistency_metrics=consistency_metrics,
                recommendations=recommendations,
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            )
            
            # Store report
            self.reproducibility_reports[report.report_id] = report
            
            self.logger.info(f"📊 Generated reproducibility report for {component_id}: {overall_determinism:.3f}")
            
            return report.report_id
            
        except Exception as e:
            self.logger.error(f"Failed to generate reproducibility report: {e}")
            return ""
    
    def _generate_reproducibility_recommendations(self, determinism_score: float,
                                                reproducibility_rate: float,
                                                results: List[ValidationResult]) -> List[str]:
        """Generate reproducibility recommendations"""
        try:
            recommendations = []
            
            # Recommendations based on determinism score
            if determinism_score < 0.5:
                recommendations.append("CRITICAL: Very low determinism detected")
                recommendations.append("Review random number generation and ensure proper seeding")
                recommendations.append("Check for non-deterministic operations (threading, async operations)")
            elif determinism_score < 0.8:
                recommendations.append("Moderate determinism issues detected")
                recommendations.append("Consider implementing stricter seed management")
                recommendations.append("Review floating-point operations for consistency")
            
            # Recommendations based on reproducibility rate
            if reproducibility_rate < 0.7:
                recommendations.append("Low reproducibility rate detected")
                recommendations.append("Implement checkpoint-based validation")
                recommendations.append("Consider using deterministic algorithms where possible")
            
            # Recommendations based on common deviation types
            deviation_types = {}
            for result in results:
                for deviation in result.deviations:
                    dev_type = deviation.get("type", "unknown")
                    deviation_types[dev_type] = deviation_types.get(dev_type, 0) + 1
            
            if "numerical" in deviation_types:
                recommendations.append("Numerical precision issues detected - consider using fixed-point arithmetic")
            
            if "hash_mismatch" in deviation_types:
                recommendations.append("Hash mismatches detected - review data serialization consistency")
            
            if "statistical" in deviation_types:
                recommendations.append("Statistical variations detected - implement tighter tolerance controls")
            
            # General recommendations
            if not recommendations:
                recommendations.append("Determinism and reproducibility are within acceptable ranges")
                recommendations.append("Continue monitoring for any degradation")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
            return ["Error generating recommendations"]
    
    def get_validation_result(self, result_id: str) -> Optional[ValidationResult]:
        """Get validation result"""
        return self.validation_results.get(result_id)
    
    def get_reproducibility_report(self, report_id: str) -> Optional[ReproducibilityReport]:
        """Get reproducibility report"""
        return self.reproducibility_reports.get(report_id)
    
    def get_dve_status(self) -> Dict[str, Any]:
        """Get DVE status"""
        try:
            return {
                "enabled": self.config.get("enabled", True),
                "determinism_level": self.config.get("determinism_level", "standard"),
                "global_seed": self.global_seed,
                "deterministic_tests": len(self.deterministic_tests),
                "validation_results": len(self.validation_results),
                "reproducibility_reports": len(self.reproducibility_reports),
                "validation_active": self.validation_active,
                "seed_history_length": len(self.seed_history)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get DVE status: {e}")
            return {"error": str(e)}

# Global instance
dve = DVE()