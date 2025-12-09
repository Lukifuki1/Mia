#!/usr/bin/env python3
"""
💬 MIA CLI Test - Testiranje CLI načina
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from mia_production_core import MIACore

def test_cli_interaction():
    """Test CLI interaction"""
    print("💬 MIA CLI Test")
    print("=" * 30)
    
    # Initialize MIA
    mia = MIACore("test_data")
    mia.start()
    
    # Test interactions
    test_inputs = [
        "Pozdravljeni!",
        "Kako si?",
        "Kaj lahko narediš?",
        "Zgradi projekt spletna aplikacija",
        "MIA 18+",
        "razvijalec mia",
        "mia, treniraj"
    ]
    
    print("🤖 MIA je pripravljena za testiranje...")
    print()
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"Test {i}/7:")
        print(f"👤 Vi: {user_input}")
        
        response = mia.interact(user_input)
        print(f"🤖 MIA: {response}")
        print("-" * 50)
    
    # Show final status
    status = mia.get_system_status()
    print("\n📊 Končno stanje:")
    print(f"   Zavest: {status['consciousness']['consciousness_level']:.1%}")
    print(f"   Čustva: {status['consciousness']['emotional_state']}")
    print(f"   Način: {status['consciousness']['mode']}")
    print(f"   Spomin: {status['memory_stats']['short_term_count']} kratkoročnih")
    print(f"   Delovanje: {status['uptime_seconds']:.0f} sekund")
    
    mia.stop()
    print("\n✅ CLI test končan")

if __name__ == "__main__":
    test_cli_interaction()