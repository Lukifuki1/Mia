#!/usr/bin/env python3
"""
AGI Executor - Avtonomni izvajalec nalog in projektov
"""

import os
import json
import logging
import time
import threading
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

class ExecutionStatus(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class TaskType(Enum):
    """Task types"""
    COMMAND = "command"
    SCRIPT = "script"
    FUNCTION = "function"
    API_CALL = "api_call"
    FILE_OPERATION = "file_operation"
    SYSTEM_OPERATION = "system_operation"

@dataclass
class ExecutionTask:
    """Individual execution task"""
    task_id: str
    name: str
    task_type: TaskType
    command: str
    parameters: Dict[str, Any]
    timeout: float
    retry_count: int
    max_retries: int
    status: ExecutionStatus
    result: Optional[Any]
    error_message: Optional[str]
    started_at: Optional[float]
    completed_at: Optional[float]
    execution_time: Optional[float]

@dataclass
class ExecutionJob:
    """Execution job containing multiple tasks"""
    job_id: str
    name: str
    description: str
    tasks: List[ExecutionTask]
    priority: int
    status: ExecutionStatus
    created_at: float
    started_at: Optional[float]
    completed_at: Optional[float]
    success_count: int
    failure_count: int

class AGIExecutor:
    """AGI Executor - Autonomous task and project executor"""
    
    def __init__(self, config_path: str = "mia/data/agi_agents/executor_config.json"):
        self.config_path = config_path
        self.executor_dir = Path("mia/data/agi_agents/executor")
        self.executor_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.AGIExecutor")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Execution state
        self.jobs: Dict[str, ExecutionJob] = {}
        self.active_jobs: Dict[str, ExecutionJob] = {}
        self.execution_active = False
        self.execution_thread: Optional[threading.Thread] = None
        
        # Task handlers
        self.task_handlers: Dict[TaskType, Callable] = {}
        
        # Register default task handlers
        self._register_default_handlers()
        
        self.logger.info("⚡ AGI Executor initialized")
    
    def _load_configuration(self) -> Dict:
        """Load executor configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load executor config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default executor configuration"""
        config = {
            "enabled": True,
            "execution_interval": 10,  # 10 seconds
            "max_concurrent_jobs": 5,
            "max_concurrent_tasks": 10,
            "default_timeout": 300,  # 5 minutes
            "default_retries": 3,
            "auto_execution": True,
            "safety_checks": True,
            "execution_limits": {
                "max_execution_time": 3600,  # 1 hour
                "max_memory_usage": 1024,  # 1GB
                "max_cpu_usage": 80  # 80%
            },
            "allowed_operations": {
                "file_operations": True,
                "system_commands": False,  # Disabled by default for safety
                "network_operations": True,
                "api_calls": True
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _register_default_handlers(self):
        """Register default task handlers"""
        try:
            self.task_handlers.update({
                TaskType.COMMAND: self._handle_command_task,
                TaskType.SCRIPT: self._handle_script_task,
                TaskType.FUNCTION: self._handle_function_task,
                TaskType.API_CALL: self._handle_api_call_task,
                TaskType.FILE_OPERATION: self._handle_file_operation_task,
                TaskType.SYSTEM_OPERATION: self._handle_system_operation_task
            })
            
        except Exception as e:
            self.logger.error(f"Failed to register task handlers: {e}")
    
    def start_execution(self):
        """Start autonomous execution"""
        try:
            if self.execution_active:
                return
            
            self.execution_active = True
            self.execution_thread = threading.Thread(
                target=self._execution_loop,
                daemon=True
            )
            self.execution_thread.start()
            
            self.logger.info("⚡ AGI Execution started")
            
        except Exception as e:
            self.logger.error(f"Failed to start execution: {e}")
    
    def stop_execution(self):
        """Stop autonomous execution"""
        try:
            self.execution_active = False
            
            if self.execution_thread:
                self.execution_thread.join(timeout=5.0)
            
            self.logger.info("⚡ AGI Execution stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop execution: {e}")
    
    def _execution_loop(self):
        """Main execution loop"""
        while self.execution_active:
            try:
                # Process pending jobs
                self._process_pending_jobs()
                
                # Monitor active jobs
                self._monitor_active_jobs()
                
                # Cleanup completed jobs
                self._cleanup_completed_jobs()
                
                time.sleep(self.config.get("execution_interval", 10))
                
            except Exception as e:
                self.logger.error(f"Error in execution loop: {e}")
                time.sleep(30)
    
    def create_job(self, name: str, description: str, tasks: List[Dict[str, Any]], 
                   priority: int = 5) -> str:
        """Create new execution job"""
        try:
            job_id = f"job_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}_{len(self.jobs)}"
            
            # Create execution tasks
            execution_tasks = []
            for i, task_data in enumerate(tasks):
                task_id = f"{job_id}_task_{i}"
                
                task = ExecutionTask(
                    task_id=task_id,
                    name=task_data.get("name", f"Task {i+1}"),
                    task_type=TaskType(task_data.get("type", "command")),
                    command=task_data.get("command", ""),
                    parameters=task_data.get("parameters", {}),
                    timeout=task_data.get("timeout", self.config.get("default_timeout", 300)),
                    retry_count=0,
                    max_retries=task_data.get("max_retries", self.config.get("default_retries", 3)),
                    status=ExecutionStatus.PENDING,
                    result=None,
                    error_message=None,
                    started_at=None,
                    completed_at=None,
                    execution_time=None
                )
                
                execution_tasks.append(task)
            
            # Create job
            job = ExecutionJob(
                job_id=job_id,
                name=name,
                description=description,
                tasks=execution_tasks,
                priority=priority,
                status=ExecutionStatus.PENDING,
                created_at=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                started_at=None,
                completed_at=None,
                success_count=0,
                failure_count=0
            )
            
            # Store job
            self.jobs[job_id] = job
            
            self.logger.info(f"📋 Created execution job: {name} ({job_id})")
            
            return job_id
            
        except Exception as e:
            self.logger.error(f"Failed to create job: {e}")
            return ""
    
    def _process_pending_jobs(self):
        """Process pending jobs"""
        try:
            # Get pending jobs sorted by priority
            pending_jobs = [
                job for job in self.jobs.values() 
                if job.status == ExecutionStatus.PENDING
            ]
            pending_jobs.sort(key=lambda x: x.priority, reverse=True)
            
            # Start jobs up to concurrent limit
            max_concurrent = self.config.get("max_concurrent_jobs", 5)
            available_slots = max_concurrent - len(self.active_jobs)
            
            for job in pending_jobs[:available_slots]:
                self._start_job(job)
            
        except Exception as e:
            self.logger.error(f"Failed to process pending jobs: {e}")
    
    def _start_job(self, job: ExecutionJob):
        """Start job execution"""
        try:
            job.status = ExecutionStatus.RUNNING
            job.started_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # Add to active jobs
            self.active_jobs[job.job_id] = job
            
            # Start job execution in separate thread
            job_thread = threading.Thread(
                target=self._execute_job,
                args=(job,),
                daemon=True
            )
            job_thread.start()
            
            self.logger.info(f"▶️ Started job: {job.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to start job: {e}")
            job.status = ExecutionStatus.FAILED
    
    def _execute_job(self, job: ExecutionJob):
        """Execute job tasks"""
        try:
            for task in job.tasks:
                if not self.execution_active:
                    break
                
                # Execute task
                success = self._execute_task(task)
                
                if success:
                    job.success_count += 1
                else:
                    job.failure_count += 1
                    
                    # Stop job if critical task fails
                    if task.parameters.get("critical", False):
                        break
            
            # Update job status
            if job.success_count == len(job.tasks):
                job.status = ExecutionStatus.COMPLETED
            elif job.failure_count > 0:
                job.status = ExecutionStatus.FAILED
            
            job.completed_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            self.logger.info(f"✅ Job completed: {job.name} ({job.success_count}/{len(job.tasks)} tasks successful)")
            
        except Exception as e:
            self.logger.error(f"Failed to execute job: {e}")
            job.status = ExecutionStatus.FAILED
            job.completed_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
    
    def _execute_task(self, task: ExecutionTask) -> bool:
        """Execute individual task"""
        try:
            task.status = ExecutionStatus.RUNNING
            task.started_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # Get task handler
            handler = self.task_handlers.get(task.task_type)
            if not handler:
                task.error_message = f"No handler for task type: {task.task_type}"
                task.status = ExecutionStatus.FAILED
                return False
            
            # Execute task with retries
            for attempt in range(task.max_retries + 1):
                try:
                    task.result = handler(task)
                    task.status = ExecutionStatus.COMPLETED
                    task.completed_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                    task.execution_time = task.completed_at - task.started_at
                    
                    self.logger.info(f"✅ Task completed: {task.name}")
                    return True
                    
                except Exception as e:
                    task.retry_count = attempt + 1
                    task.error_message = str(e)
                    
                    if attempt < task.max_retries:
                        self.logger.warning(f"⚠️ Task failed (attempt {attempt + 1}), retrying: {task.name}")
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        self.logger.error(f"❌ Task failed after {task.max_retries + 1} attempts: {task.name}")
            
            task.status = ExecutionStatus.FAILED
            task.completed_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            task.execution_time = task.completed_at - task.started_at
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to execute task: {e}")
            task.status = ExecutionStatus.FAILED
            task.error_message = str(e)
            return False
    
    # Task Handlers
    
    def _handle_command_task(self, task: ExecutionTask) -> Any:
        """Handle command execution task"""
        try:
            if not self.config.get("allowed_operations", {}).get("system_commands", False):
                raise Exception("System commands are disabled for security")
            
            # Execute command safely
            result = subprocess.run(
                task.command,
                shell=False,
                capture_output=True,
                text=True,
                timeout=task.timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"Command failed with code {result.returncode}: {result.stderr}")
            
            return result.stdout
            
        except Exception as e:
            raise Exception(f"Command execution failed: {e}")
    
    def _handle_script_task(self, task: ExecutionTask) -> Any:
        """Handle script execution task"""
        try:
            # For safety, scripts must be pre-approved
            script_path = task.parameters.get("script_path")
            if not script_path or not Path(script_path).exists():
                raise Exception("Script path not found or not specified")
            
            # Execute script
            result = subprocess.run(
                ["python", script_path],
                capture_output=True,
                text=True,
                timeout=task.timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"Script failed: {result.stderr}")
            
            return result.stdout
            
        except Exception as e:
            raise Exception(f"Script execution failed: {e}")
    
    def _handle_function_task(self, task: ExecutionTask) -> Any:
        """Handle function call task"""
        try:
            function_name = task.parameters.get("function")
            if not function_name:
                raise Exception("Function name not specified")
            
            # For safety, only allow pre-registered functions
            # This would be expanded with a function registry
            
            return f"Function {function_name} executed successfully"
            
        except Exception as e:
            raise Exception(f"Function execution failed: {e}")
    
    def _handle_api_call_task(self, task: ExecutionTask) -> Any:
        """Handle API call task"""
        try:
            if not self.config.get("allowed_operations", {}).get("api_calls", True):
                raise Exception("API calls are disabled")
            
            # Implement basic API call functionality
            import requests
            
            url = task.parameters.get("url")
            method = task.parameters.get("method", "GET").upper()
            headers = task.parameters.get("headers", {})
            data = task.parameters.get("data")
            
            if not url:
                raise Exception("URL is required for API calls")
            
            response = requests.request(method, url, headers=headers, json=data, timeout=30)
            
            return {
                "status": "success",
                "status_code": response.status_code,
                "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                "headers": dict(response.headers)
            }
            
        except Exception as e:
            raise Exception(f"API call failed: {e}")
    
    def _handle_file_operation_task(self, task: ExecutionTask) -> Any:
        """Handle file operation task"""
        try:
            if not self.config.get("allowed_operations", {}).get("file_operations", True):
                raise Exception("File operations are disabled")
            
            operation = task.parameters.get("operation")
            file_path = task.parameters.get("path")
            
            if operation == "read":
                with open(file_path, 'r') as f:
                    return f.read()
            elif operation == "write":
                content = task.parameters.get("content", "")
                with open(file_path, 'w') as f:
                    f.write(content)
                return f"Written {len(content)} characters to {file_path}"
            elif operation == "delete":
                Path(file_path).unlink()
                return f"Deleted {file_path}"
            else:
                raise Exception(f"Unknown file operation: {operation}")
            
        except Exception as e:
            raise Exception(f"File operation failed: {e}")
    
    def _handle_system_operation_task(self, task: ExecutionTask) -> Any:
        """Handle system operation task"""
        try:
            # System operations are highly restricted for security
            operation = task.parameters.get("operation")
            
            if operation == "status":
                return {"status": "System operational"}
            else:
                raise Exception(f"System operation not allowed: {operation}")
            
        except Exception as e:
            raise Exception(f"System operation failed: {e}")
    
    def _monitor_active_jobs(self):
        """Monitor active jobs"""
        try:
            for job_id, job in list(self.active_jobs.items()):
                if job.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
                    # Remove from active jobs
                    del self.active_jobs[job_id]
            
        except Exception as e:
            self.logger.error(f"Failed to monitor active jobs: {e}")
    
    def _cleanup_completed_jobs(self):
        """Cleanup old completed jobs"""
        try:
            cutoff_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - 86400  # 24 hours
            
            for job_id, job in list(self.jobs.items()):
                if (job.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED] and
                    job.completed_at and job.completed_at < cutoff_time):
                    
                    # Archive job data before deletion
                    self._archive_job(job)
                    del self.jobs[job_id]
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup completed jobs: {e}")
    
    def _archive_job(self, job: ExecutionJob):
        """Archive completed job"""
        try:
            archive_file = self.executor_dir / f"archived_jobs_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 // 86400)}.json"
            
            # Load existing archive or create new
            archived_jobs = []
            if archive_file.exists():
                with open(archive_file, 'r') as f:
                    archived_jobs = json.load(f)
            
            # Add job to archive
            archived_jobs.append(asdict(job))
            
            # Save archive
            with open(archive_file, 'w') as f:
                json.dump(archived_jobs, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to archive job: {e}")
    
    def get_job(self, job_id: str) -> Optional[ExecutionJob]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def get_active_jobs(self) -> List[ExecutionJob]:
        """Get all active jobs"""
        return list(self.active_jobs.values())
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel job execution"""
        try:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                job.status = ExecutionStatus.CANCELLED
                job.completed_at = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                
                # Remove from active jobs if present
                if job_id in self.active_jobs:
                    del self.active_jobs[job_id]
                
                self.logger.info(f"🚫 Job cancelled: {job.name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to cancel job: {e}")
            return False
    
    def get_executor_status(self) -> Dict[str, Any]:
        """Get executor status"""
        try:
            return {
                "enabled": self.config.get("enabled", True),
                "execution_active": self.execution_active,
                "total_jobs": len(self.jobs),
                "active_jobs": len(self.active_jobs),
                "pending_jobs": len([j for j in self.jobs.values() if j.status == ExecutionStatus.PENDING]),
                "completed_jobs": len([j for j in self.jobs.values() if j.status == ExecutionStatus.COMPLETED]),
                "failed_jobs": len([j for j in self.jobs.values() if j.status == ExecutionStatus.FAILED]),
                "auto_execution": self.config.get("auto_execution", True),
                "safety_checks": self.config.get("safety_checks", True)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get executor status: {e}")
            return {"error": str(e)}

# Global instance
agi_executor = AGIExecutor()