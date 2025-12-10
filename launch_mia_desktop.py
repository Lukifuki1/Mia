#!/usr/bin/env python3
"""
MIA Enterprise AGI Desktop Launcher
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main launcher function"""
    # Set working directory to MIA installation
    mia_dir = Path(__file__).parent
    os.chdir(mia_dir)
    
    # Add to Python path
    sys.path.insert(0, str(mia_dir))
    
    try:
        # Launch MIA hybrid system
        launcher_path = mia_dir / "mia_hybrid_launcher.py"
        if launcher_path.exists():
            subprocess.run([sys.executable, str(launcher_path)])
        else:
            print("❌ MIA launcher not found!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Failed to launch MIA: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
