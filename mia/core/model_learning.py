#!/usr/bin/env python3
"""
MIA Model Learning System
Learns from discovered local LLM models
"""

import os
import json
import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import subprocess
import tempfile

from .model_discovery import ModelInfo, ModelType, ModelFormat, model_discovery

class LearningMethod(Enum):
    """Methods for learning from models"""
    KNOWLEDGE_EXTRACTION = "knowledge_extraction"
    PARAMETER_ANALYSIS = "parameter_analysis"
    BEHAVIOR_MODELING = "behavior_modeling"
    FINE_TUNING = "fine_tuning"
    DISTILLATION = "distillation"

class LearningStatus(Enum):
    """Status of learning process"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class LearningTask:
    """Learning task information"""
    id: str
    model_info: ModelInfo
    method: LearningMethod
    status: LearningStatus
    progress: float
    started_at: float
    completed_at: Optional[float] = None
    results: Dict[str, Any] = None
    error_message: Optional[str] = None

@dataclass
class ExtractedKnowledge:
    """Knowledge extracted from a model"""
    model_id: str
    knowledge_type: str
    content: Dict[str, Any]
    confidence: float
    extracted_at: float
    metadata: Dict[str, Any] = None

class ModelLearningEngine:
    """Engine for learning from local AI models"""
    
    def __init__(self, config_path: str = "mia/data/learning/config.json"):
        self.config_path = Path(config_path)
        self.logger = self._setup_logging()
        self.learning_tasks = {}
        self.extracted_knowledge = {}
        self.learning_thread = None
        self.is_learning = False
        self.model_interfaces = {}
        
        self._load_config()
        self._initialize_model_interfaces()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup model learning logging"""
        logger = logging.getLogger("MIA.ModelLearning")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _load_config(self):
        """Load learning configuration"""
        default_config = {
            "max_concurrent_tasks": 2,
            "learning_methods": ["knowledge_extraction", "behavior_modeling"],
            "output_directory": "mia/data/learning/extracted",
            "temp_directory": "mia/data/learning/temp",
            "max_model_size": 50 * 1024**3,  # 50GB
            "timeout_minutes": 60
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                self.config = {**default_config, **config}
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
                self.config = default_config
        else:
            self.config = default_config
            
        # Create directories
        Path(self.config["output_directory"]).mkdir(parents=True, exist_ok=True)
        Path(self.config["temp_directory"]).mkdir(parents=True, exist_ok=True)
    
    def _initialize_model_interfaces(self):
        """Initialize interfaces for different model formats"""
        self.model_interfaces = {
            ModelFormat.GGUF: self._create_gguf_interface,
            ModelFormat.HUGGINGFACE: self._create_huggingface_interface,
            ModelFormat.OLLAMA: self._create_ollama_interface,
            ModelFormat.PYTORCH: self._create_pytorch_interface,
        }
    
    def start_learning_from_discovered_models(self):
        """Start learning from all discovered models"""
        if self.is_learning:
            self.logger.warning("Learning already in progress")
            return
        
        discovered_models = model_discovery.get_discovered_models()
        llm_models = [model for model in discovered_models.values() 
                     if model.model_type == ModelType.LLM]
        
        self.logger.info(f"Starting learning from {len(llm_models)} LLM models")
        
        # Create learning tasks
        for model in llm_models:
            if model.size <= self.config["max_model_size"]:
                self.create_learning_task(model, LearningMethod.KNOWLEDGE_EXTRACTION)
                self.create_learning_task(model, LearningMethod.BEHAVIOR_MODELING)
        
        # Start learning thread
        self.is_learning = True
        self.learning_thread = threading.Thread(
            target=self._learning_worker,
            daemon=True
        )
        self.learning_thread.start()
    
    def create_learning_task(self, model_info: ModelInfo, method: LearningMethod) -> str:
        """Create a new learning task"""
        task_id = f"{model_info.name}_{method.value}_{int(time.time())}"
        
        task = LearningTask(
            id=task_id,
            model_info=model_info,
            method=method,
            status=LearningStatus.PENDING,
            progress=0.0,
            started_at=time.time()
        )
        
        self.learning_tasks[task_id] = task
        self.logger.info(f"Created learning task: {task_id}")
        return task_id
    
    def _learning_worker(self):
        """Worker thread for processing learning tasks"""
        while self.is_learning:
            try:
                # Get pending tasks
                pending_tasks = [
                    task for task in self.learning_tasks.values()
                    if task.status == LearningStatus.PENDING
                ]
                
                if not pending_tasks:
                    time.sleep(10)
                    continue
                
                # Process tasks (limited concurrency)
                active_tasks = [
                    task for task in self.learning_tasks.values()
                    if task.status == LearningStatus.IN_PROGRESS
                ]
                
                if len(active_tasks) < self.config["max_concurrent_tasks"]:
                    task = pending_tasks[0]
                    self._process_learning_task(task)
                
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Learning worker error: {e}")
                time.sleep(30)
    
    def _process_learning_task(self, task: LearningTask):
        """Process a single learning task"""
        try:
            self.logger.info(f"Starting learning task: {task.id}")
            task.status = LearningStatus.IN_PROGRESS
            task.progress = 0.1
            
            # Create model interface
            interface = self._create_model_interface(task.model_info)
            if not interface:
                raise Exception(f"Cannot create interface for model format: {task.model_info.format}")
            
            task.progress = 0.2
            
            # Execute learning method
            if task.method == LearningMethod.KNOWLEDGE_EXTRACTION:
                results = self._extract_knowledge(task.model_info, interface)
            elif task.method == LearningMethod.BEHAVIOR_MODELING:
                results = self._model_behavior(task.model_info, interface)
            elif task.method == LearningMethod.PARAMETER_ANALYSIS:
                results = self._analyze_parameters(task.model_info, interface)
            else:
                raise Exception(f"Unsupported learning method: {task.method}")
            
            task.progress = 0.9
            
            # Store results
            task.results = results
            task.status = LearningStatus.COMPLETED
            task.completed_at = time.time()
            task.progress = 1.0
            
            self.logger.info(f"Completed learning task: {task.id}")
            
        except Exception as e:
            self.logger.error(f"Learning task failed {task.id}: {e}")
            task.status = LearningStatus.FAILED
            task.error_message = str(e)
            task.completed_at = time.time()
    
    def _create_model_interface(self, model_info: ModelInfo):
        """Create interface for interacting with model"""
        interface_creator = self.model_interfaces.get(model_info.format)
        if interface_creator:
            return interface_creator(model_info)
        return None
    
    def _create_gguf_interface(self, model_info: ModelInfo):
        """Create interface for GGUF models"""
        return {
            'type': 'gguf',
            'path': model_info.path,
            'load_method': self._load_gguf_model,
            'query_method': self._query_gguf_model
        }
    
    def _create_huggingface_interface(self, model_info: ModelInfo):
        """Create interface for Hugging Face models"""
        return {
            'type': 'huggingface',
            'path': model_info.path,
            'load_method': self._load_huggingface_model,
            'query_method': self._query_huggingface_model
        }
    
    def _create_ollama_interface(self, model_info: ModelInfo):
        """Create interface for Ollama models"""
        return {
            'type': 'ollama',
            'path': model_info.path,
            'load_method': self._load_ollama_model,
            'query_method': self._query_ollama_model
        }
    
    def _create_pytorch_interface(self, model_info: ModelInfo):
        """Create interface for PyTorch models"""
        return {
            'type': 'pytorch',
            'path': model_info.path,
            'load_method': self._load_pytorch_model,
            'query_method': self._query_pytorch_model
        }
    
    def _extract_knowledge(self, model_info: ModelInfo, interface: Dict) -> Dict[str, Any]:
        """Extract knowledge from model"""
        self.logger.info(f"Extracting knowledge from {model_info.name}")
        
        knowledge_queries = [
            "What are the key concepts you understand?",
            "What domains of knowledge do you have expertise in?",
            "What are your capabilities and limitations?",
            "What programming languages and technologies do you know?",
            "What are important facts about science and technology?",
        ]
        
        extracted_knowledge = {}
        
        for i, query in enumerate(knowledge_queries):
            try:
                response = self._query_model(interface, query)
                if response:
                    extracted_knowledge[f"knowledge_{i}"] = {
                        "query": query,
                        "response": response,
                        "confidence": 0.8  # Default confidence
                    }
            except Exception as e:
                self.logger.warning(f"Failed to extract knowledge with query '{query}': {e}")
        
        # Store extracted knowledge
        for key, knowledge in extracted_knowledge.items():
            knowledge_obj = ExtractedKnowledge(
                model_id=model_info.name,
                knowledge_type=key,
                content=knowledge,
                confidence=knowledge["confidence"],
                extracted_at=time.time(),
                metadata={"model_path": model_info.path}
            )
            self.extracted_knowledge[f"{model_info.name}_{key}"] = knowledge_obj
        
        return {
            "extracted_items": len(extracted_knowledge),
            "knowledge_areas": list(extracted_knowledge.keys()),
            "total_tokens": sum(len(str(k["response"])) for k in extracted_knowledge.values())
        }
    
    def _model_behavior(self, model_info: ModelInfo, interface: Dict) -> Dict[str, Any]:
        """Model the behavior patterns of the model"""
        self.logger.info(f"Modeling behavior of {model_info.name}")
        
        behavior_tests = [
            {"input": "Hello", "expected_type": "greeting"},
            {"input": "What is 2+2?", "expected_type": "math"},
            {"input": "Write a short story", "expected_type": "creative"},
            {"input": "Explain quantum physics", "expected_type": "scientific"},
            {"input": "def fibonacci(n):", "expected_type": "code"},
        ]
        
        behavior_patterns = {}
        
        for i, test in enumerate(behavior_tests):
            try:
                response = self._query_model(interface, test["input"])
                if response:
                    behavior_patterns[f"pattern_{i}"] = {
                        "input": test["input"],
                        "output": response,
                        "expected_type": test["expected_type"],
                        "response_length": len(response),
                        "response_time": 1.0  # Placeholder
                    }
            except Exception as e:
                self.logger.warning(f"Failed behavior test '{test['input']}': {e}")
        
        return {
            "behavior_patterns": len(behavior_patterns),
            "test_results": behavior_patterns,
            "avg_response_length": sum(p["response_length"] for p in behavior_patterns.values()) / len(behavior_patterns) if behavior_patterns else 0
        }
    
    def _analyze_parameters(self, model_info: ModelInfo, interface: Dict) -> Dict[str, Any]:
        """Analyze model parameters and architecture"""
        self.logger.info(f"Analyzing parameters of {model_info.name}")
        
        # Basic file analysis
        analysis = {
            "file_size": model_info.size,
            "format": model_info.format.value,
            "estimated_parameters": self._estimate_parameters(model_info),
            "architecture_hints": self._analyze_architecture(model_info)
        }
        
        return analysis
    
    def _estimate_parameters(self, model_info: ModelInfo) -> int:
        """Estimate number of parameters based on file size"""
        # Rough estimation: 1 parameter ≈ 2-4 bytes (depending on precision)
        size_bytes = model_info.size
        
        if model_info.format == ModelFormat.GGUF:
            # GGUF models are often quantized
            estimated_params = size_bytes // 2  # Assume 2 bytes per param
        else:
            estimated_params = size_bytes // 4  # Assume 4 bytes per param (float32)
        
        return estimated_params
    
    def _analyze_architecture(self, model_info: ModelInfo) -> List[str]:
        """Analyze model architecture from filename and metadata"""
        hints = []
        
        name_lower = model_info.name.lower()
        
        # Common model architectures
        if 'llama' in name_lower:
            hints.append("LLaMA architecture")
        elif 'mistral' in name_lower:
            hints.append("Mistral architecture")
        elif 'gpt' in name_lower:
            hints.append("GPT architecture")
        elif 'bert' in name_lower:
            hints.append("BERT architecture")
        
        # Parameter size hints
        if '7b' in name_lower:
            hints.append("~7B parameters")
        elif '13b' in name_lower:
            hints.append("~13B parameters")
        elif '70b' in name_lower:
            hints.append("~70B parameters")
        
        # Quantization hints
        if 'q4' in name_lower:
            hints.append("4-bit quantization")
        elif 'q8' in name_lower:
            hints.append("8-bit quantization")
        elif 'fp16' in name_lower:
            hints.append("16-bit floating point")
        
        return hints
    
    def _query_model(self, interface: Dict, query: str) -> Optional[str]:
        """Query model through its interface"""
        try:
            # This is a simplified implementation
            # In practice, you'd need specific loaders for each format
            
            if interface['type'] == 'gguf':
                return self._query_gguf_model(interface, query)
            elif interface['type'] == 'huggingface':
                return self._query_huggingface_model(interface, query)
            elif interface['type'] == 'ollama':
                return self._query_ollama_model(interface, query)
            elif interface['type'] == 'pytorch':
                return self._query_pytorch_model(interface, query)
            
        except Exception as e:
            self.logger.warning(f"Failed to query model: {e}")
            return None
    
    def _query_gguf_model(self, interface: Dict, query: str) -> Optional[str]:
        """Query GGUF model (placeholder implementation)"""
        # In practice, you'd use llama.cpp or similar
        return f"GGUF model response to: {query}"
    
    def _query_huggingface_model(self, interface: Dict, query: str) -> Optional[str]:
        """Query Hugging Face model (placeholder implementation)"""
        # In practice, you'd use transformers library
        return f"HuggingFace model response to: {query}"
    
    def _query_ollama_model(self, interface: Dict, query: str) -> Optional[str]:
        """Query Ollama model"""
        try:
            # Try to use Ollama CLI if available
            result = subprocess.run(
                ['ollama', 'run', Path(interface['path']).name, query],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return f"Ollama model response to: {query}"
    
    def _query_pytorch_model(self, interface: Dict, query: str) -> Optional[str]:
        """Query PyTorch model (placeholder implementation)"""
        # In practice, you'd load the model with torch
        return f"PyTorch model response to: {query}"
    
    def _load_gguf_model(self, interface: Dict):
        """Load GGUF model"""
        # Placeholder - would use llama.cpp
        pass
    
    def _load_huggingface_model(self, interface: Dict):
        """Load Hugging Face model"""
        # Placeholder - would use transformers
        pass
    
    def _load_ollama_model(self, interface: Dict):
        """Load Ollama model"""
        # Placeholder - would use Ollama API
        pass
    
    def _load_pytorch_model(self, interface: Dict):
        """Load PyTorch model"""
        # Placeholder - would use torch.load
        pass
    
    def stop_learning(self):
        """Stop learning process"""
        self.is_learning = False
        if self.learning_thread and self.learning_thread.is_alive():
            self.learning_thread.join(timeout=10)
        self.logger.info("Stopped model learning")
    
    def get_learning_tasks(self) -> Dict[str, LearningTask]:
        """Get all learning tasks"""
        return self.learning_tasks.copy()
    
    def get_extracted_knowledge(self) -> Dict[str, ExtractedKnowledge]:
        """Get all extracted knowledge"""
        return self.extracted_knowledge.copy()
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        tasks = list(self.learning_tasks.values())
        
        stats = {
            'total_tasks': len(tasks),
            'completed_tasks': len([t for t in tasks if t.status == LearningStatus.COMPLETED]),
            'failed_tasks': len([t for t in tasks if t.status == LearningStatus.FAILED]),
            'in_progress_tasks': len([t for t in tasks if t.status == LearningStatus.IN_PROGRESS]),
            'pending_tasks': len([t for t in tasks if t.status == LearningStatus.PENDING]),
            'total_knowledge_items': len(self.extracted_knowledge),
            'is_learning': self.is_learning
        }
        
        return stats
    
    def save_learning_results(self):
        """Save learning results to disk"""
        try:
            # Save tasks
            tasks_path = Path(self.config["output_directory"]) / "learning_tasks.json"
            tasks_data = {k: asdict(v) for k, v in self.learning_tasks.items()}
            
            with open(tasks_path, 'w') as f:
                json.dump(tasks_data, f, indent=2, default=str)
            
            # Save knowledge
            knowledge_path = Path(self.config["output_directory"]) / "extracted_knowledge.json"
            knowledge_data = {k: asdict(v) for k, v in self.extracted_knowledge.items()}
            
            with open(knowledge_path, 'w') as f:
                json.dump(knowledge_data, f, indent=2, default=str)
            
            self.logger.info("Saved learning results to disk")
            
        except Exception as e:
            self.logger.error(f"Failed to save learning results: {e}")

# Global model learning instance
model_learning = ModelLearningEngine()

def start_learning_from_models():
    """Start learning from discovered models"""
    model_learning.start_learning_from_discovered_models()

def get_learning_progress() -> Dict[str, Any]:
    """Get current learning progress"""
    return model_learning.get_learning_stats()

def get_extracted_knowledge() -> Dict[str, ExtractedKnowledge]:
    """Get all extracted knowledge"""
    return model_learning.get_extracted_knowledge()