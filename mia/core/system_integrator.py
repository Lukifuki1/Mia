#!/usr/bin/env python3
"""
MIA System Integrator
Central integration hub for all MIA components and modules
"""

import os
import json
import logging
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading

class IntegrationStatus(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Integration status levels"""
    INITIALIZING = "initializing"
    READY = "ready"
    ACTIVE = "active"
    DEGRADED = "degraded"
    FAILED = "failed"

@dataclass
class ComponentInfo:
    """Component information"""
    name: str
    module_path: str
    instance_name: str
    status: IntegrationStatus
    dependencies: List[str]
    initialized: bool
    last_health_check: float
    error_count: int

class SystemIntegrator:
    """Central system integration manager"""
    
    def __init__(self, config_path: str = "mia/data/integration/config.json"):
        self.config_path = config_path
        self.integration_dir = Path("mia/data/integration")
        self.integration_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MIA.SystemIntegrator")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Component registry
        self.components: Dict[str, ComponentInfo] = {}
        self.component_instances: Dict[str, Any] = {}
        
        # Integration state
        self.integration_status = IntegrationStatus.INITIALIZING
        self.startup_complete = False
        
        # Event system
        self.event_callbacks: Dict[str, List[Callable]] = {}
        
        # Health monitoring
        self.health_check_interval = 30.0
        self.health_check_thread: Optional[threading.Thread] = None
        
        self.logger.info("🔗 System Integrator initialized")
    
    def _load_configuration(self) -> Dict:
        """Load integration configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load integration config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default integration configuration"""
        config = {
            "enabled": True,
            "startup_timeout": 120.0,
            "health_check_interval": 30.0,
            "auto_recovery": True,
            "components": {
                "consciousness": {
                    "module": "mia.core.consciousness.main",
                    "instance": "consciousness_system",
                    "dependencies": ["memory", "hardware_optimizer"],
                    "critical": True,
                    "auto_start": True
                },
                "memory": {
                    "module": "mia.core.memory.main",
                    "instance": "memory_system",
                    "dependencies": [],
                    "critical": True,
                    "auto_start": True
                },
                "adaptive_llm": {
                    "module": "mia.core.adaptive_llm",
                    "instance": "adaptive_llm_manager",
                    "dependencies": ["hardware_optimizer"],
                    "critical": True,
                    "auto_start": True
                },
                "self_evolution": {
                    "module": "mia.core.self_evolution",
                    "instance": "self_evolution_engine",
                    "dependencies": ["consciousness", "memory"],
                    "critical": False,
                    "auto_start": True
                },
                "internet_learning": {
                    "module": "mia.core.internet_learning",
                    "instance": "internet_learning_engine",
                    "dependencies": ["memory"],
                    "critical": False,
                    "auto_start": True
                },
                "hardware_optimizer": {
                    "module": "mia.core.hardware_optimizer",
                    "instance": "hardware_optimizer",
                    "dependencies": [],
                    "critical": True,
                    "auto_start": True
                },
                "owner_guard": {
                    "module": "mia.core.owner_guard",
                    "instance": "owner_guard",
                    "dependencies": [],
                    "critical": True,
                    "auto_start": True
                },
                "immune_system": {
                    "module": "mia.core.immune.immune_kernel",
                    "instance": "immune_kernel",
                    "dependencies": ["owner_guard"],
                    "critical": True,
                    "auto_start": True
                },
                "voice_stt": {
                    "module": "mia.modules.voice.stt_engine",
                    "instance": "stt_engine",
                    "dependencies": [],
                    "critical": False,
                    "auto_start": False
                },
                "voice_tts": {
                    "module": "mia.modules.voice.tts_engine",
                    "instance": "tts_engine",
                    "dependencies": [],
                    "critical": False,
                    "auto_start": False
                },
                "lora_manager": {
                    "module": "mia.modules.lora_training.lora_manager",
                    "instance": "lora_manager",
                    "dependencies": ["hardware_optimizer"],
                    "critical": False,
                    "auto_start": False
                },
                "project_builder": {
                    "module": "mia.modules.project_builder.main",
                    "instance": "enterprise_project_builder",
                    "dependencies": [],
                    "critical": False,
                    "auto_start": False
                },
                "email_client": {
                    "module": "mia.modules.api_email.email_client",
                    "instance": "email_client",
                    "dependencies": [],
                    "critical": False,
                    "auto_start": False
                },
                "health_monitor": {
                    "module": "mia.modules.monitoring.health_monitor",
                    "instance": "health_monitor",
                    "dependencies": [],
                    "critical": False,
                    "auto_start": True
                },
                "adult_system": {
                    "module": "mia.modules.adult_mode.adult_system",
                    "instance": "adult_system",
                    "dependencies": ["voice_tts"],
                    "critical": False,
                    "auto_start": False
                }
            },
            "integration_order": [
                "hardware_optimizer",
                "owner_guard",
                "memory",
                "consciousness",
                "adaptive_llm",
                "immune_system",
                "health_monitor",
                "self_evolution",
                "internet_learning",
                "voice_stt",
                "voice_tts",
                "lora_manager",
                "project_builder",
                "email_client",
                "adult_system"
            ]
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    async def initialize_system(self) -> bool:
        """Initialize complete MIA system"""
        try:
            self.logger.info("🚀 Starting MIA system initialization...")
            
            start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            timeout = self.config.get("startup_timeout", 120.0)
            
            # Register all components
            self._register_components()
            
            # Initialize components in dependency order
            success = await self._initialize_components()
            
            if success:
                # Start health monitoring
                self._start_health_monitoring()
                
                # Set system as ready
                self.integration_status = IntegrationStatus.READY
                self.startup_complete = True
                
                elapsed = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
                self.logger.info(f"✅ MIA system initialization completed in {elapsed:.2f}s")
                
                # Trigger system ready event
                await self._trigger_event("system_ready", {"startup_time": elapsed})
                
                return True
            else:
                self.integration_status = IntegrationStatus.FAILED
                self.logger.error("❌ MIA system initialization failed")
                return False
                
        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            self.integration_status = IntegrationStatus.FAILED
            return False
    
    def _register_components(self):
        """Register all system components"""
        try:
            components_config = self.config.get("components", {})
            
            for component_name, component_config in components_config.items():
                component_info = ComponentInfo(
                    name=component_name,
                    module_path=component_config["module"],
                    instance_name=component_config["instance"],
                    status=IntegrationStatus.INITIALIZING,
                    dependencies=component_config.get("dependencies", []),
                    initialized=False,
                    last_health_check=0.0,
                    error_count=0
                )
                
                self.components[component_name] = component_info
            
            self.logger.info(f"📝 Registered {len(self.components)} components")
            
        except Exception as e:
            self.logger.error(f"Failed to register components: {e}")
    
    async def _initialize_components(self) -> bool:
        """Initialize components in dependency order"""
        try:
            integration_order = self.config.get("integration_order", [])
            
            for component_name in integration_order:
                if component_name not in self.components:
                    continue
                
                component_info = self.components[component_name]
                component_config = self.config["components"][component_name]
                
                # Skip if not auto-start
                if not component_config.get("auto_start", True):
                    self.logger.info(f"⏭️ Skipping {component_name} (auto_start disabled)")
                    continue
                
                # Check dependencies
                if not self._check_dependencies(component_info):
                    self.logger.error(f"❌ Dependencies not met for {component_name}")
                    if component_config.get("critical", False):
                        return False
                    continue
                
                # Initialize component
                success = await self._initialize_component(component_name)
                
                if success:
                    self.logger.info(f"✅ Initialized {component_name}")
                else:
                    self.logger.error(f"❌ Failed to initialize {component_name}")
                    if component_config.get("critical", False):
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Component initialization failed: {e}")
            return False
    
    def _check_dependencies(self, component_info: ComponentInfo) -> bool:
        """Check if component dependencies are satisfied"""
        try:
            for dependency in component_info.dependencies:
                if dependency not in self.components:
                    self.logger.error(f"Unknown dependency: {dependency}")
                    return False
                
                dep_component = self.components[dependency]
                if not dep_component.initialized:
                    self.logger.error(f"Dependency not initialized: {dependency}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check dependencies: {e}")
            return False
    
    async def _initialize_component(self, component_name: str) -> bool:
        """Initialize individual component"""
        try:
            component_info = self.components[component_name]
            
            # Import module
            try:
                module = __import__(component_info.module_path, fromlist=[component_info.instance_name])
                instance = getattr(module, component_info.instance_name)
                
                # Store instance
                self.component_instances[component_name] = instance
                
                # Call initialization if available
                if hasattr(instance, 'initialize') and callable(getattr(instance, 'initialize')):
                    if asyncio.iscoroutinefunction(instance.initialize):
                        await instance.initialize()
                    else:
                        instance.initialize()
                
                # Mark as initialized
                component_info.initialized = True
                component_info.status = IntegrationStatus.READY
                component_info.last_health_check = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                
                return True
                
            except ImportError as e:
                self.logger.error(f"Failed to import {component_info.module_path}: {e}")
                component_info.status = IntegrationStatus.FAILED
                component_info.error_count += 1
                return False
            
            except AttributeError as e:
                self.logger.error(f"Instance {component_info.instance_name} not found in {component_info.module_path}: {e}")
                component_info.status = IntegrationStatus.FAILED
                component_info.error_count += 1
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize component {component_name}: {e}")
            if component_name in self.components:
                self.components[component_name].status = IntegrationStatus.FAILED
                self.components[component_name].error_count += 1
            return False
    
    def _start_health_monitoring(self):
        """Start health monitoring for all components"""
        try:
            self.health_check_interval = self.config.get("health_check_interval", 30.0)
            
            self.health_check_thread = threading.Thread(
                target=self._health_monitoring_loop,
                daemon=True
            )
            self.health_check_thread.start()
            
            self.logger.info("💊 Started health monitoring")
            
        except Exception as e:
            self.logger.error(f"Failed to start health monitoring: {e}")
    
    def _health_monitoring_loop(self):
        """Health monitoring loop"""
        while self.startup_complete:
            try:
                for component_name, component_info in self.components.items():
                    if not component_info.initialized:
                        continue
                    
                    # Perform health check
                    healthy = self._check_component_health(component_name)
                    
                    if healthy:
                        component_info.status = IntegrationStatus.ACTIVE
                        component_info.last_health_check = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                    else:
                        component_info.status = IntegrationStatus.DEGRADED
                        component_info.error_count += 1
                        
                        # Attempt recovery if enabled
                        if self.config.get("auto_recovery", True):
                            self._attempt_component_recovery(component_name)
                
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                time.sleep(self.health_check_interval)
    
    def _check_component_health(self, component_name: str) -> bool:
        """Check health of individual component"""
        try:
            if component_name not in self.component_instances:
                return False
            
            instance = self.component_instances[component_name]
            
            # Check if instance has health check method
            if hasattr(instance, 'get_status') and callable(getattr(instance, 'get_status')):
                try:
                    status = instance.get_status()
                    return isinstance(status, dict) and not status.get("error")
                except Exception:
                    return False
            
            # Basic health check - instance exists and is accessible
            return instance is not None
            
        except Exception as e:
            self.logger.error(f"Health check failed for {component_name}: {e}")
            return False
    
    def _attempt_component_recovery(self, component_name: str):
        """Attempt to recover failed component"""
        try:
            self.logger.info(f"🔄 Attempting recovery for {component_name}")
            
            component_info = self.components[component_name]
            
            # Try to reinitialize component
            asyncio.create_task(self._initialize_component(component_name))
            
        except Exception as e:
            self.logger.error(f"Component recovery failed for {component_name}: {e}")
    
    def get_component(self, component_name: str) -> Optional[Any]:
        """Get component instance"""
        return self.component_instances.get(component_name)
    
    def get_component_status(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Get component status"""
        try:
            if component_name not in self.components:
                return None
            
            component_info = self.components[component_name]
            instance = self.component_instances.get(component_name)
            
            status = {
                "name": component_info.name,
                "status": component_info.status.value,
                "initialized": component_info.initialized,
                "last_health_check": component_info.last_health_check,
                "error_count": component_info.error_count,
                "dependencies": component_info.dependencies,
                "instance_available": instance is not None
            }
            
            # Get detailed status from component if available
            if instance and hasattr(instance, 'get_status'):
                try:
                    detailed_status = instance.get_status()
                    if isinstance(detailed_status, dict):
                        status["detailed_status"] = detailed_status
                except Exception as e:
                    status["status_error"] = str(e)
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get component status: {e}")
            return None
    
    def register_event_callback(self, event_name: str, callback: Callable):
        """Register event callback"""
        if event_name not in self.event_callbacks:
            self.event_callbacks[event_name] = []
        
        self.event_callbacks[event_name].append(callback)
    
    def unregister_event_callback(self, event_name: str, callback: Callable):
        """Unregister event callback"""
        if event_name in self.event_callbacks:
            if callback in self.event_callbacks[event_name]:
                self.event_callbacks[event_name].remove(callback)
    
    async def _trigger_event(self, event_name: str, event_data: Dict[str, Any]):
        """Trigger system event"""
        try:
            if event_name in self.event_callbacks:
                for callback in self.event_callbacks[event_name]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(event_data)
                        else:
                            callback(event_data)
                    except Exception as e:
                        self.logger.error(f"Event callback error: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to trigger event {event_name}: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        try:
            component_statuses = {}
            
            for component_name in self.components:
                component_statuses[component_name] = self.get_component_status(component_name)
            
            # Calculate overall health
            total_components = len(self.components)
            healthy_components = len([
                c for c in self.components.values()
                if c.status in [IntegrationStatus.READY, IntegrationStatus.ACTIVE]
            ])
            
            health_percentage = (healthy_components / total_components) * 100 if total_components > 0 else 0
            
            return {
                "integration_status": self.integration_status.value,
                "startup_complete": self.startup_complete,
                "total_components": total_components,
                "healthy_components": healthy_components,
                "health_percentage": health_percentage,
                "components": component_statuses,
                "uptime": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - (self.components[list(self.components.keys())[0]].last_health_check if self.components else self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {"error": str(e)}
    
    async def shutdown_system(self):
        """Shutdown complete MIA system"""
        try:
            self.logger.info("🛑 Shutting down MIA system...")
            
            self.startup_complete = False
            
            # Shutdown components in reverse order
            integration_order = self.config.get("integration_order", [])
            
            for component_name in reversed(integration_order):
                if component_name in self.component_instances:
                    instance = self.component_instances[component_name]
                    
                    # Call shutdown if available
                    if hasattr(instance, 'shutdown') and callable(getattr(instance, 'shutdown')):
                        try:
                            if asyncio.iscoroutinefunction(instance.shutdown):
                                await instance.shutdown()
                            else:
                                instance.shutdown()
                            
                            self.logger.info(f"🛑 Shutdown {component_name}")
                            
                        except Exception as e:
                            self.logger.error(f"Failed to shutdown {component_name}: {e}")
            
            # Clear instances
            self.component_instances.clear()
            
            # Reset component states
            for component_info in self.components.values():
                component_info.initialized = False
                component_info.status = IntegrationStatus.INITIALIZING
            
            self.integration_status = IntegrationStatus.INITIALIZING
            
            self.logger.info("✅ MIA system shutdown completed")
            
        except Exception as e:
            self.logger.error(f"System shutdown failed: {e}")

# Global instance
system_integrator = SystemIntegrator()