#!/usr/bin/env python3
"""
Test script for MIA AGI Core
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from mia.core.agi_core import agi_core, initialize_agi, ThoughtType

async def test_agi_core():
    """Test the AGI core functionality"""
    print("🧠 Testing MIA AGI Core...")
    
    try:
        # Initialize AGI
        print("🚀 Initializing AGI...")
        await initialize_agi()
        
        # Test thinking
        print("🤔 Testing thinking capability...")
        thought = await agi_core.think("What is artificial intelligence?", ThoughtType.REASONING)
        print(f"💭 Thought: {thought.content}")
        print(f"🎯 Confidence: {thought.confidence:.2f}")
        
        # Test chat
        print("💬 Testing chat capability...")
        response = await agi_core.chat("Hello, how are you?")
        print(f"🤖 Response: {response}")
        
        # Test task processing
        print("📋 Testing task processing...")
        task = await agi_core.process_task("Analyze the benefits of renewable energy")
        print(f"✅ Task result: {task.result}")
        
        # Get status
        print("📊 Getting AGI status...")
        status = await agi_core.get_status()
        print(f"🔧 Status: {status}")
        
        print("✅ AGI Core test completed successfully!")
        
    except Exception as e:
        print(f"❌ AGI Core test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agi_core())