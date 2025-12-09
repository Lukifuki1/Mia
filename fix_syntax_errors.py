#!/usr/bin/env python3
"""
🔧 MIA Enterprise AGI - Syntax Error Fixer
Fixes syntax errors caused by misplaced imports
"""

import os
import re
from pathlib import Path

def fix_syntax_errors():
    """Fix syntax errors in Python files"""
    
    # Find all Python files
    python_files = list(Path(".").rglob("*.py"))
    
    fixed_files = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix misplaced imports in try blocks
            pattern = r'(\s+try:\s*\n\s+.*?\n)(from \.deterministic_helpers import deterministic_helpers\s*\n)'
            replacement = r'\1'
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            # Remove standalone deterministic_helpers imports
            content = re.sub(r'^from \.deterministic_helpers import deterministic_helpers\s*\n', '', content, flags=re.MULTILINE)
            
            # Fix other common syntax issues
            content = re.sub(r'(\s+try:\s*\n)(\s*from [^\n]+\n)(\s+)', r'\1\3', content, flags=re.MULTILINE)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files.append(str(file_path))
                print(f"Fixed syntax errors in: {file_path}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"\n✅ Fixed syntax errors in {len(fixed_files)} files")
    return fixed_files

if __name__ == "__main__":
    fix_syntax_errors()