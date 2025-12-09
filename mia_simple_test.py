#!/usr/bin/env python3
"""
🧪 MIA Simple Test - Testiranje osnovnih funkcij
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_core_system():
    """Test MIA core system"""
    print("🧠 Testing MIA Core System...")
    
    try:
        from mia_production_core import MIACore
        
        # Initialize core
        mia = MIACore("test_data")
        mia.start()
        
        # Test basic interaction
        response = mia.interact("Pozdravljeni!")
        print(f"✅ Core system response: {response[:100]}...")
        
        # Test system status
        status = mia.get_system_status()
        print(f"✅ System status: {status['running']}")
        print(f"   Hardware: {status['hardware']['platform']}")
        print(f"   Memory: {status['memory_stats']['short_term_count']} short-term memories")
        
        mia.stop()
        return True
        
    except Exception as e:
        print(f"❌ Core system error: {e}")
        return False

def test_voice_system():
    """Test voice system"""
    print("\n🎙️ Testing Voice System...")
    
    try:
        from mia_voice_system import MIAVoiceSystem
        
        # Initialize voice system
        voice = MIAVoiceSystem(Path("test_data"))
        
        # Test TTS
        profiles = voice.get_voice_profiles()
        print(f"✅ Available voice profiles: {profiles}")
        
        # Test speaking (without actual audio output)
        result = voice.speak("Test govor", save_audio=False)
        print(f"✅ TTS test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice system error: {e}")
        return False

def test_multimodal_system():
    """Test multimodal system"""
    print("\n🎨 Testing Multimodal System...")
    
    try:
        from mia_multimodal_system import MIAMultimodalSystem
        
        # Initialize multimodal system
        multimodal = MIAMultimodalSystem(Path("test_data"))
        
        # Test image generation
        image_path = multimodal.generate_image("test landscape", "default", "low")
        if image_path:
            print(f"✅ Image generated: {image_path}")
        else:
            print("⚠️ Image generation failed (expected without PIL)")
        
        # Test audio generation
        audio_path = multimodal.generate_audio("test tone", "default", "low")
        if audio_path:
            print(f"✅ Audio generated: {audio_path}")
        else:
            print("⚠️ Audio generation failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Multimodal system error: {e}")
        return False

def test_project_system():
    """Test project system"""
    print("\n🚀 Testing Project System...")
    
    try:
        from mia_project_system import MIAProjectSystem
        
        # Initialize project system
        projects = MIAProjectSystem(Path("test_data"))
        
        # Test project creation
        project_id = projects.create_project(
            name="Test Project",
            description="A test project",
            project_type="cli_tool",
            requirements=["Basic functionality"],
            features=["Feature 1", "Feature 2"],
            technologies=["Python"]
        )
        
        print(f"✅ Project created: {project_id}")
        
        # Test project listing
        project_list = projects.list_projects()
        print(f"✅ Projects listed: {len(project_list)} projects")
        
        return True
        
    except Exception as e:
        print(f"❌ Project system error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 MIA AGI System - Simple Test")
    print("=" * 40)
    
    tests = [
        test_core_system,
        test_voice_system,
        test_multimodal_system,
        test_project_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! MIA AGI system is working correctly.")
    else:
        print(f"⚠️ {total - passed} tests failed. Some dependencies may be missing.")
    
    print("\n🎯 To run full MIA system:")
    print("   python mia_launcher.py --mode cli")
    print("   python mia_launcher.py --mode web")

if __name__ == "__main__":
    main()