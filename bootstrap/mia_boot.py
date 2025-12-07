#!/usr/bin/env python3
"""
MIA Main Bootstrap Entry Point
Initializes and starts the complete MIA system
"""

import asyncio
import sys
import os
import logging
import signal
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import MIA core modules
from mia.core.bootstrap.main import MIABootBuilder
from mia.core.consciousness.main import consciousness, awaken_consciousness
from mia.core.memory.main import memory_system
from mia.core.adaptive_llm import adaptive_llm, get_adaptive_llm_status
from mia.core.self_evolution import evolution_engine, get_evolution_status
from mia.core.internet_learning import internet_learning, get_internet_learning_status
from mia.modules.voice.stt.main import stt_engine
from mia.modules.voice.tts.main import tts_engine
from mia.modules.multimodal.image.main import image_generator

class MIASystem:
    """Main MIA system orchestrator"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.bootstrap = MIABootBuilder()
        self.running = False
        self.shutdown_event = asyncio.Event()
        
        # System components
        self.components = {
            "bootstrap": self.bootstrap,
            "consciousness": consciousness,
            "memory": memory_system,
            "stt": stt_engine,
            "tts": tts_engine,
            "image_generator": image_generator
        }
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup main system logging"""
        
        # Create logs directory
        logs_dir = Path("mia/logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / "mia_system.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logger = logging.getLogger("MIA.System")
        return logger
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def initialize(self) -> bool:
        """Initialize all MIA components"""
        
        self.logger.info("🚀 Starting MIA System Initialization...")
        
        try:
            # Phase 1: Bootstrap system
            self.logger.info("Phase 1: Bootstrap initialization...")
            bootstrap_success = await self.bootstrap.initialize()
            
            if not bootstrap_success:
                self.logger.error("❌ Bootstrap initialization failed!")
                return False
            
            # Phase 2: Awaken consciousness
            self.logger.info("Phase 2: Awakening consciousness...")
            await awaken_consciousness()
            
            # Phase 3: Initialize voice systems
            self.logger.info("Phase 3: Initializing voice systems...")
            await self._initialize_voice_systems()
            
            # Phase 4: Initialize multimodal systems
            self.logger.info("Phase 4: Initializing multimodal systems...")
            await self._initialize_multimodal_systems()
            
            # Phase 5: System health check
            self.logger.info("Phase 5: System health check...")
            health_status = await self._system_health_check()
            
            if not health_status:
                self.logger.error("❌ System health check failed!")
                return False
            
            self.logger.info("✅ MIA System initialization completed successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ System initialization failed: {e}")
            return False
    
    async def _initialize_voice_systems(self):
        """Initialize voice processing systems"""
        try:
            # Initialize STT
            stt_status = stt_engine.get_status()
            self.logger.info(f"STT Status: {stt_status}")
            
            # Initialize TTS
            tts_status = tts_engine.get_status()
            self.logger.info(f"TTS Status: {tts_status}")
            
            self.logger.info("✅ Voice systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Voice systems initialization failed: {e}")
            raise
    
    async def _initialize_multimodal_systems(self):
        """Initialize multimodal generation systems"""
        try:
            # Initialize image generation
            image_status = image_generator.get_status()
            self.logger.info(f"Image Generation Status: {image_status}")
            
            self.logger.info("✅ Multimodal systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Multimodal systems initialization failed: {e}")
            raise
    
    async def _system_health_check(self) -> bool:
        """Perform comprehensive system health check"""
        
        health_checks = []
        
        try:
            # Check consciousness
            consciousness_snapshot = consciousness.get_consciousness_snapshot()
            if consciousness_snapshot.consciousness_state.value != "dormant":
                health_checks.append(("Consciousness", True))
                self.logger.info("✅ Consciousness - Active")
            else:
                health_checks.append(("Consciousness", False))
                self.logger.error("❌ Consciousness - Dormant")
            
            # Check memory system
            memory_stats = memory_system.get_memory_statistics()
            if memory_stats:
                health_checks.append(("Memory", True))
                self.logger.info(f"✅ Memory - {sum(stats['count'] for stats in memory_stats.values())} total memories")
            else:
                health_checks.append(("Memory", False))
                self.logger.error("❌ Memory - No statistics available")
            
            # Check voice systems
            stt_status = stt_engine.get_status()
            tts_status = tts_engine.get_status()
            
            voice_healthy = (stt_status.get("state") != "error" and 
                           tts_status.get("state") != "error")
            health_checks.append(("Voice", voice_healthy))
            
            if voice_healthy:
                self.logger.info("✅ Voice Systems - Operational")
            else:
                self.logger.error("❌ Voice Systems - Error state detected")
            
            # Check image generation
            image_status = image_generator.get_status()
            image_healthy = image_status.get("total_generated", 0) >= 0  # Basic check
            health_checks.append(("Image Generation", image_healthy))
            
            if image_healthy:
                self.logger.info("✅ Image Generation - Available")
            else:
                self.logger.error("❌ Image Generation - Not available")
            
            # Overall health assessment
            total_checks = len(health_checks)
            passed_checks = sum(1 for _, status in health_checks if status)
            health_ratio = passed_checks / total_checks
            
            self.logger.info(f"System Health: {passed_checks}/{total_checks} components healthy ({health_ratio:.1%})")
            
            # Require at least 75% health for successful startup
            return health_ratio >= 0.75
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    async def run(self):
        """Main system run loop"""
        
        self.running = True
        self.logger.info("🎉 MIA is now running and ready for interaction!")
        
        # Store startup memory
        from mia.core.memory.main import store_memory, EmotionalTone
        store_memory(
            "MIA system has started successfully and is ready for interaction.",
            EmotionalTone.EXCITED,
            ["startup", "system", "ready"]
        )
        
        try:
            # Main system loop
            while self.running:
                # System monitoring and maintenance
                await self._system_maintenance()
                
                # Wait for shutdown signal or brief pause
                try:
                    await asyncio.wait_for(self.shutdown_event.wait(), timeout=10.0)
                    break  # Shutdown requested
                except asyncio.TimeoutError:
                    continue  # Continue normal operation
                
        except Exception as e:
            self.logger.error(f"Error in main system loop: {e}")
        
        finally:
            await self._cleanup()
    
    async def _system_maintenance(self):
        """Perform periodic system maintenance"""
        
        try:
            # Memory cleanup
            memory_system.cleanup_old_memories(days_old=7)
            
            # Log system status
            consciousness_state = consciousness.consciousness_state.value
            memory_stats = memory_system.get_memory_statistics()
            total_memories = sum(stats['count'] for stats in memory_stats.values())
            
            self.logger.debug(f"System Status - Consciousness: {consciousness_state}, Memories: {total_memories}")
            
        except Exception as e:
            self.logger.error(f"Error in system maintenance: {e}")
    
    async def shutdown(self):
        """Gracefully shutdown MIA system"""
        
        if not self.running:
            return
        
        self.logger.info("🔄 Initiating MIA system shutdown...")
        self.running = False
        
        try:
            # Store shutdown memory
            from mia.core.memory.main import store_memory, EmotionalTone
            store_memory(
                "MIA system is shutting down. Goodbye for now.",
                EmotionalTone.CALM,
                ["shutdown", "system", "farewell"]
            )
            
            # Shutdown components in reverse order
            self.logger.info("Shutting down consciousness...")
            await consciousness.shutdown()
            
            self.logger.info("Shutting down voice systems...")
            await stt_engine.shutdown()
            await tts_engine.shutdown()
            
            self.logger.info("Shutting down multimodal systems...")
            await image_generator.shutdown()
            
            self.logger.info("✅ MIA system shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
        
        finally:
            self.shutdown_event.set()
    
    async def _cleanup(self):
        """Final cleanup operations"""
        try:
            # Close any remaining resources
            self.logger.info("Performing final cleanup...")
            
            # Save final system state
            if hasattr(self.bootstrap, '_save_system_state'):
                await self.bootstrap._save_system_state()
            
        except Exception as e:
            self.logger.error(f"Error in cleanup: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        status = {
            "running": self.running,
            "components": {},
            "system_health": "operational"
        }
        
        try:
            # Get component statuses
            status["components"]["consciousness"] = {
                "state": consciousness.consciousness_state.value,
                "emotional_state": consciousness.emotional_state.value,
                "status": "active"
            }
            
            status["components"]["memory"] = memory_system.get_memory_statistics()
            status["components"]["memory"]["status"] = "active"
            
            status["components"]["stt"] = stt_engine.get_status()
            status["components"]["tts"] = tts_engine.get_status()
            status["components"]["image_generation"] = image_generator.get_status()
            status["components"]["adaptive_llm"] = get_adaptive_llm_status()
            status["components"]["evolution"] = get_evolution_status()
            status["components"]["internet_learning"] = get_internet_learning_status()
            
            # Overall health assessment
            component_count = len(status["components"])
            healthy_components = sum(1 for comp in status["components"].values() 
                                   if isinstance(comp, dict) and comp.get("status") != "error")
            
            if healthy_components == component_count:
                status["system_health"] = "excellent"
            elif healthy_components >= component_count * 0.8:
                status["system_health"] = "good"
            else:
                status["system_health"] = "needs_attention"
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            status["error"] = str(e)
            status["system_health"] = "error"
        
        return status

async def main():
    """Main entry point"""
    
    print("🧠 MIA - Local Digital Intelligence Entity")
    print("=" * 50)
    
    # Create and initialize MIA system
    mia_system = MIASystem()
    
    try:
        # Initialize system
        success = await mia_system.initialize()
        
        if not success:
            print("❌ MIA initialization failed!")
            return 1
        
        # Run system
        await mia_system.run()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n🔄 Shutdown requested by user...")
        await mia_system.shutdown()
        return 0
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1

if __name__ == "__main__":
    # Run MIA system
    exit_code = asyncio.run(main())
    sys.exit(exit_code)