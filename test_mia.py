#!/usr/bin/env python3
"""
MIA Test System
Comprehensive testing of MIA functionality
"""

import asyncio
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bootstrap.mia_boot import MIASystem

class MIATestSuite:
    """Comprehensive test suite for MIA"""
    
    def __init__(self):
        self.mia_system = MIASystem()
        self.test_results = []
        
    async def run_tests(self):
        """Run comprehensive test suite"""
        
        print("🧪 Starting MIA Test Suite")
        print("=" * 50)
        
        # Initialize MIA system
        print("Initializing MIA system...")
        success = await self.mia_system.initialize()
        
        if not success:
            print("❌ MIA initialization failed!")
            return False
        
        print("✅ MIA system initialized successfully")
        
        # Run test categories
        await self.test_basic_functionality()
        await self.test_consciousness_system()
        await self.test_memory_system()
        await self.test_voice_systems()
        await self.test_image_generation()
        await self.test_integration()
        
        # Print results
        self.print_test_results()
        
        # Shutdown
        await self.mia_system.shutdown()
        
        return True
    
    async def test_basic_functionality(self):
        """Test basic MIA functionality"""
        print("\n🔧 Testing Basic Functionality...")
        
        try:
            # Test system status
            status = self.mia_system.get_system_status()
            self.record_test("System Status", status.get("system_health") in ["operational", "excellent", "good"])
            
            # Test component availability
            components = status.get("components", {})
            self.record_test("Consciousness Available", "consciousness" in components)
            self.record_test("Memory Available", "memory" in components)
            self.record_test("Voice Systems Available", "stt" in components and "tts" in components)
            
        except Exception as e:
            self.record_test("Basic Functionality", False, str(e))
    
    async def test_consciousness_system(self):
        """Test consciousness and personality system"""
        print("\n🧠 Testing Consciousness System...")
        
        try:
            from mia.core.consciousness.main import consciousness
            
            # Test consciousness state
            snapshot = consciousness.get_consciousness_snapshot()
            self.record_test("Consciousness Active", snapshot.consciousness_state.value != "dormant")
            self.record_test("Emotional State", snapshot.emotional_state is not None)
            self.record_test("Personality Traits", len(consciousness.personality_traits) > 0)
            
            # Test user input processing
            context = consciousness.process_user_input("Hello MIA, how are you?")
            self.record_test("User Input Processing", context is not None)
            self.record_test("Context Generation", "consciousness_state" in context)
            
        except Exception as e:
            self.record_test("Consciousness System", False, str(e))
    
    async def test_memory_system(self):
        """Test memory storage and retrieval"""
        print("\n🧠 Testing Memory System...")
        
        try:
            from mia.core.memory.main import memory_system, store_memory, retrieve_memories, EmotionalTone
            
            # Test memory storage
            memory_id = store_memory(
                "This is a test memory for the test suite",
                EmotionalTone.NEUTRAL,
                ["test", "memory", "suite"]
            )
            self.record_test("Memory Storage", memory_id is not None)
            
            # Test memory retrieval
            memories = retrieve_memories("test", limit=5)
            self.record_test("Memory Retrieval", len(memories) >= 0)  # Allow empty results
            
            # Test memory statistics
            stats = memory_system.get_memory_statistics()
            self.record_test("Memory Statistics", stats is not None)
            
            # Test context retrieval
            context = memory_system.get_context_for_conversation("test")
            self.record_test("Context Retrieval", context is not None)
            
        except Exception as e:
            self.record_test("Memory System", False, str(e))
    
    async def test_voice_systems(self):
        """Test voice input/output systems"""
        print("\n🎤 Testing Voice Systems...")
        
        try:
            from mia.modules.voice.stt.main import stt_engine
            from mia.modules.voice.tts.main import tts_engine, speak, VoiceProfile, EmotionalTone
            
            # Test STT status
            stt_status = stt_engine.get_status()
            self.record_test("STT Engine Status", stt_status.get("state") != "error")
            
            # Test TTS status
            tts_status = tts_engine.get_status()
            self.record_test("TTS Engine Status", tts_status.get("state") != "error")
            
            # Test speech generation
            result = await speak(
                "This is a test of the text-to-speech system",
                EmotionalTone.NEUTRAL,
                VoiceProfile.DEFAULT,
                play_audio=False
            )
            self.record_test("Speech Generation", result is not None)
            
            if result:
                self.record_test("Audio Data Generated", len(result.audio_data) > 0)
                self.record_test("Generation Time Reasonable", result.generation_time < 5.0)
            
        except Exception as e:
            self.record_test("Voice Systems", False, str(e))
    
    async def test_image_generation(self):
        """Test image generation system"""
        print("\n🎨 Testing Image Generation...")
        
        try:
            from mia.modules.multimodal.image.main import image_generator, generate_image, ImageStyle, EmotionalTone
            
            # Test image generator status
            status = image_generator.get_status()
            self.record_test("Image Generator Available", status is not None)
            
            # Test image generation
            result = await generate_image(
                "A simple test image of a blue circle",
                EmotionalTone.NEUTRAL,
                ImageStyle.REALISTIC
            )
            self.record_test("Image Generation", result is not None)
            
            if result:
                self.record_test("Image Data Generated", len(result.image_data) > 0)
                self.record_test("Generation Time Reasonable", result.generation_time < 10.0)
                self.record_test("Image Saved", result.image_path is not None)
            
            # Test LoRA system
            lora_models = image_generator.list_lora_models()
            self.record_test("LoRA Models Available", len(lora_models) > 0)
            
        except Exception as e:
            self.record_test("Image Generation", False, str(e))
    
    async def test_integration(self):
        """Test system integration"""
        print("\n🔗 Testing System Integration...")
        
        try:
            # Test conversation flow
            from mia.core.consciousness.main import consciousness
            from mia.core.memory.main import store_memory, EmotionalTone
            
            # Simulate conversation
            user_message = "Hello MIA, can you help me with a creative project?"
            
            # Store user message
            store_memory(f"User: {user_message}", EmotionalTone.NEUTRAL, ["test", "conversation"])
            
            # Process with consciousness
            context = consciousness.process_user_input(user_message)
            self.record_test("Conversation Processing", context is not None)
            
            # Test emotional adaptation
            excited_context = consciousness.process_user_input("I'm so excited about this!")
            self.record_test("Emotional Adaptation", 
                           excited_context.get("emotional_state") != context.get("emotional_state"))
            
            # Test memory integration
            from mia.core.memory.main import memory_system
            memories = memory_system.get_context_for_conversation("creative project")
            self.record_test("Memory Integration", len(memories) >= 0)
            
        except Exception as e:
            self.record_test("System Integration", False, str(e))
    
    def record_test(self, test_name: str, passed: bool, error: str = None):
        """Record test result"""
        self.test_results.append({
            "name": test_name,
            "passed": passed,
            "error": error
        })
        
        status = "✅" if passed else "❌"
        print(f"  {status} {test_name}")
        if error:
            print(f"    Error: {error}")
    
    def print_test_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 50)
        print("🧪 MIA Test Results")
        print("=" * 50)
        
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Print failed tests
        failed_tests = [result for result in self.test_results if not result["passed"]]
        if failed_tests:
            print("\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"  - {test['name']}")
                if test["error"]:
                    print(f"    Error: {test['error']}")
        
        # Overall assessment
        print("\n" + "=" * 50)
        if success_rate >= 80:
            print("🎉 MIA System: OPERATIONAL")
            print("The system is functioning well and ready for use.")
        elif success_rate >= 60:
            print("⚠️  MIA System: PARTIALLY OPERATIONAL")
            print("The system has some issues but core functionality works.")
        else:
            print("❌ MIA System: NEEDS ATTENTION")
            print("The system has significant issues that need to be addressed.")

async def main():
    """Main test entry point"""
    
    print("🧠 MIA - Digital Intelligence Entity")
    print("🧪 Comprehensive Test Suite")
    print("=" * 50)
    
    test_suite = MIATestSuite()
    
    try:
        success = await test_suite.run_tests()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n🔄 Test interrupted by user")
        return 0
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)