#!/usr/bin/env python3
"""
MIA System Launcher
Starts MIA with web UI
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bootstrap.mia_boot import MIASystem
from mia.modules.ui.web import web_ui

async def main():
    """Main launcher"""
    
    print("🧠 MIA - Local Digital Intelligence Entity")
    print("Starting system with web interface...")
    print("=" * 50)
    
    # Create MIA system
    mia_system = MIASystem()
    
    try:
        # Initialize MIA
        print("Initializing MIA system...")
        success = await mia_system.initialize()
        
        if not success:
            print("❌ MIA initialization failed!")
            return 1
        
        print("✅ MIA system initialized successfully!")
        print(f"🌐 Web interface will be available at: http://localhost:12000")
        print("🎉 MIA is ready for interaction!")
        print("\nPress Ctrl+C to shutdown")
        
        # Start web UI and MIA system concurrently
        await asyncio.gather(
            web_ui.start_server(),
            mia_system.run()
        )
        
        return 0
        
    except KeyboardInterrupt:
        print("\n🔄 Shutdown requested...")
        await mia_system.shutdown()
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)