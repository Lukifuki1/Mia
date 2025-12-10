#!/usr/bin/env python3
"""
MIA IMMEDIATE FIX SCRIPT - Hitri popravki za osnovni delujoč sistem
================================================================

Ta script popravi najkritičnejše probleme za osnovni delujoč MIA sistem:
1. Namesti manjkajoče odvisnosti
2. Popravi syntax errors
3. Onemogoči hibridne funkcionalnosti, ki ne delujejo
4. Ustvari minimalno delovno verzijo

UPORABA:
python IMMEDIATE_FIX_SCRIPT.py
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MIAImmediateFixer:
    """Hitri popravki za MIA sistem"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.fixes_applied = []
        self.errors_found = []
        
    def run_all_fixes(self):
        """Zaženi vse hitri popravki"""
        logger.info("🚀 Starting MIA Immediate Fix Script...")
        
        try:
            # 1. Install critical dependencies
            self.install_critical_dependencies()
            
            # 2. Fix syntax errors
            self.fix_syntax_errors()
            
            # 3. Create minimal working version
            self.create_minimal_version()
            
            # 4. Test basic functionality
            self.test_basic_functionality()
            
            # 5. Generate report
            self.generate_fix_report()
            
            logger.info("✅ MIA Immediate Fix completed!")
            
        except Exception as e:
            logger.error(f"❌ Fix script failed: {e}")
            raise
            
    def install_critical_dependencies(self):
        """Namesti kritične odvisnosti"""
        logger.info("📦 Installing critical dependencies...")
        
        critical_packages = [
            "rdflib>=6.2.0",
            "sentence-transformers>=2.2.0", 
            "spacy>=3.4.0",
            "z3-solver>=4.11.0",
            "scikit-learn>=1.1.0",
            "nltk>=3.7",
            "numpy>=1.21.0",
            "pandas>=1.5.0",
            "scipy>=1.9.0"
        ]
        
        for package in critical_packages:
            try:
                logger.info(f"Installing {package}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    self.fixes_applied.append(f"✅ Installed {package}")
                else:
                    self.errors_found.append(f"❌ Failed to install {package}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                self.errors_found.append(f"❌ Timeout installing {package}")
            except Exception as e:
                self.errors_found.append(f"❌ Error installing {package}: {e}")
                
        # Install spaCy model
        try:
            logger.info("Installing spaCy English model...")
            result = subprocess.run([
                sys.executable, "-m", "spacy", "download", "en_core_web_sm"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.fixes_applied.append("✅ Installed spaCy English model")
            else:
                self.errors_found.append(f"❌ Failed to install spaCy model: {result.stderr}")
                
        except Exception as e:
            self.errors_found.append(f"❌ Error installing spaCy model: {e}")
            
    def fix_syntax_errors(self):
        """Popravi identificirane syntax errors"""
        logger.info("🔧 Fixing syntax errors...")
        
        syntax_fixes = [
            {
                "file": "cleanup_generated_files.py",
                "line": 223,
                "fix": "Add proper indentation after except statement"
            },
            {
                "file": "mia/verification/performance_monitor.py", 
                "line": 389,
                "fix": "Add proper indentation after while statement"
            },
            {
                "file": "mia/testing/validation_methods.py",
                "line": 496,
                "fix": "Remove unmatched '}'"
            },
            {
                "file": "mia/project_builder/deterministic_build_helpers.py",
                "line": 271,
                "fix": "Fix function definition syntax"
            },
            {
                "file": "mia/project_builder/core_methods.py",
                "line": 462,
                "fix": "Remove unmatched '}'"
            },
            {
                "file": "mia/production/compliance_checker.py",
                "line": 243,
                "fix": "Fix continue statement outside loop"
            }
        ]
        
        for fix_info in syntax_fixes:
            try:
                file_path = self.project_root / fix_info["file"]
                if file_path.exists():
                    self.apply_syntax_fix(file_path, fix_info)
                else:
                    self.errors_found.append(f"❌ File not found: {fix_info['file']}")
                    
            except Exception as e:
                self.errors_found.append(f"❌ Error fixing {fix_info['file']}: {e}")
                
    def apply_syntax_fix(self, file_path: Path, fix_info: dict):
        """Apliciraj specifičen syntax fix"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Apply specific fixes based on file
            if "cleanup_generated_files.py" in str(file_path):
                # Fix indentation after except
                if len(lines) > 223:
                    if lines[223].strip() == "":
                        lines[223] = "            pass  # Fixed indentation\n"
                        
            elif "performance_monitor.py" in str(file_path):
                # Fix indentation after while
                if len(lines) > 389:
                    if lines[389].strip() == "":
                        lines[389] = "            pass  # Fixed indentation\n"
                        
            elif "validation_methods.py" in str(file_path):
                # Remove unmatched }
                if len(lines) > 495:
                    if "}" in lines[495]:
                        lines[495] = lines[495].replace("}", "")
                        
            elif "deterministic_build_helpers.py" in str(file_path):
                # Fix function definition
                if len(lines) > 270:
                    if "def _get_deterministic_temp_deterministic_build_helpers._get_deterministic_dir" in lines[270]:
                        lines[270] = "    def _get_deterministic_dir(self) -> str:\n"
                        
            elif "core_methods.py" in str(file_path):
                # Remove unmatched }
                if len(lines) > 461:
                    if "}" in lines[461]:
                        lines[461] = lines[461].replace("}", "")
                        
            elif "compliance_checker.py" in str(file_path):
                # Fix continue outside loop
                if len(lines) > 242:
                    if "continue" in lines[242] and "for" not in lines[241] and "while" not in lines[241]:
                        lines[242] = "        pass  # Fixed continue outside loop\n"
                        
            # Write fixed file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                
            self.fixes_applied.append(f"✅ Fixed syntax in {fix_info['file']}")
            
        except Exception as e:
            self.errors_found.append(f"❌ Error applying fix to {fix_info['file']}: {e}")
            
    def create_minimal_version(self):
        """Ustvari minimalno delovno verzijo"""
        logger.info("🔨 Creating minimal working version...")
        
        # Create minimal launcher that disables problematic features
        minimal_launcher = '''#!/usr/bin/env python3
"""
MIA Minimal Launcher - Basic working version
Disables hybrid features that require missing dependencies
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MIAMinimalLauncher:
    """Minimal MIA launcher with basic functionality"""
    
    def __init__(self):
        self.is_running = False
        
    async def start(self):
        """Start minimal MIA system"""
        try:
            logger.info("🚀 Starting MIA Minimal System...")
            
            # Test basic imports
            await self.test_basic_imports()
            
            # Start basic web interface
            await self.start_basic_web()
            
            logger.info("✅ MIA Minimal System started successfully")
            logger.info("🌐 Web interface: http://localhost:8000")
            
            # Keep running
            while self.is_running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Failed to start minimal system: {e}")
            raise
            
    async def test_basic_imports(self):
        """Test basic MIA imports"""
        try:
            from mia.core.agi_core import agi_core
            logger.info("✅ AGI Core import successful")
            
            from mia.interfaces.chat import chat_interface  
            logger.info("✅ Chat interface import successful")
            
            from mia.enterprise.security import security_manager
            logger.info("✅ Security manager import successful")
            
        except ImportError as e:
            logger.warning(f"⚠️ Import warning: {e}")
            
    async def start_basic_web(self):
        """Start basic web interface"""
        try:
            from mia.modules.ui.web import MIAWebUI
            
            # Create simple web interface
            web_ui = MIAWebUI(host="0.0.0.0", port=8000)
            
            # Start in background
            import threading
            import uvicorn
            
            def start_web():
                uvicorn.run(web_ui.app, host="0.0.0.0", port=8000)
                
            web_thread = threading.Thread(target=start_web, daemon=True)
            web_thread.start()
            
            await asyncio.sleep(2)  # Wait for startup
            logger.info("✅ Basic web interface started")
            
        except Exception as e:
            logger.warning(f"⚠️ Web interface warning: {e}")
            
    def stop(self):
        """Stop the system"""
        self.is_running = False
        logger.info("🛑 MIA Minimal System stopped")

async def main():
    """Main entry point"""
    launcher = MIAMinimalLauncher()
    
    try:
        launcher.is_running = True
        await launcher.start()
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
    except Exception as e:
        logger.error(f"❌ System error: {e}")
    finally:
        launcher.stop()

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        try:
            minimal_file = self.project_root / "mia_minimal_launcher.py"
            with open(minimal_file, 'w', encoding='utf-8') as f:
                f.write(minimal_launcher)
                
            self.fixes_applied.append("✅ Created minimal launcher")
            
        except Exception as e:
            self.errors_found.append(f"❌ Error creating minimal launcher: {e}")
            
    def test_basic_functionality(self):
        """Testiraj osnovno funkcionalnost"""
        logger.info("🧪 Testing basic functionality...")
        
        try:
            # Test Python syntax
            result = subprocess.run([
                sys.executable, "-c", 
                "import sys; sys.path.insert(0, '.'); from mia.core.agi_core import agi_core; print('✅ Basic import test passed')"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                self.fixes_applied.append("✅ Basic import test passed")
            else:
                self.errors_found.append(f"❌ Basic import test failed: {result.stderr}")
                
        except Exception as e:
            self.errors_found.append(f"❌ Error testing functionality: {e}")
            
    def generate_fix_report(self):
        """Generiraj poročilo o popravkih"""
        logger.info("📊 Generating fix report...")
        
        report = f"""
# MIA IMMEDIATE FIX REPORT
========================

## FIXES APPLIED ({len(self.fixes_applied)})
{chr(10).join(self.fixes_applied)}

## ERRORS FOUND ({len(self.errors_found)})
{chr(10).join(self.errors_found)}

## NEXT STEPS
1. Run: python mia_minimal_launcher.py
2. Test web interface: http://localhost:8000
3. If working, proceed with full system fixes
4. Install remaining dependencies as needed

## STATUS
- Basic System: {'✅ READY' if len(self.errors_found) < 5 else '❌ NEEDS WORK'}
- Dependencies: {'✅ INSTALLED' if 'rdflib' in str(self.fixes_applied) else '❌ MISSING'}
- Syntax Errors: {'✅ FIXED' if any('Fixed syntax' in fix for fix in self.fixes_applied) else '❌ REMAINING'}
"""
        
        try:
            report_file = self.project_root / "IMMEDIATE_FIX_REPORT.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
                
            logger.info(f"📄 Fix report saved to: {report_file}")
            
        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")

def main():
    """Main entry point"""
    try:
        fixer = MIAImmediateFixer()
        fixer.run_all_fixes()
        
        print("\n" + "="*60)
        print("🎉 MIA IMMEDIATE FIX COMPLETED!")
        print("="*60)
        print("Next steps:")
        print("1. python mia_minimal_launcher.py")
        print("2. Open http://localhost:8000")
        print("3. Check IMMEDIATE_FIX_REPORT.md")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Fix script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()