#!/usr/bin/env python3
"""
🔍 COMPLETE TODO/PLACEHOLDER/DUMMY CODE AUDIT & FIX
==================================================

Sistematičen pregled vseh 265 Python datotek za:
- TODO komentarje
- FIXME oznake  
- XXX None  # TODO: Implementje
- HACK rešitve
- None  # TODO: Implement kodo
- None  # TODO: Replace with real implementation implementacije
- NotImplemented exceptions
- pass statements z komentarji
- Nedokončane funkcije

CILJ: Identificirati in popraviti VSE nedokončane dele kode
"""

import os
import re
import ast
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CodeIssue:
    """Struktura za shranjevanje najdenih problemov"""
    file_path: str
    line_number: int
    issue_type: str
    content: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    suggested_fix: str = ""
    context: str = ""

class CompleteTODOAuditor:
    """
    Popoln auditor za iskanje in popravljanje TODO/None  # TODO: Implement kode
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues: List[CodeIssue] = []
        self.fixed_issues: List[CodeIssue] = []
        self.stats = {
            'files_scanned': 0,
            'total_issues': 0,
            'critical_issues': 0,
            'high_issues': 0,
            'medium_issues': 0,
            'low_issues': 0,
            'fixed_issues': 0
        }
        
        # Patterns to search for
        self.search_patterns = {
            'TODO': r'#\s*TODO[:\s]*(.*)',
            'FIXME': r'#\s*FIXME[:\s]*(.*)',
            'XXX': r'#\s*XXX[:\s]*(.*)',
            'HACK': r'#\s*HACK[:\s]*(.*)',
            'BUG': r'#\s*BUG[:\s]*(.*)',
            'NOTE': r'#\s*NOTE[:\s]*(.*)',
            'WARNING': r'#\s*WARNING[:\s]*(.*)',
            'None  # TODO: Implement': r'None  # TODO: Implement|PLACEHOLDER',
            'None  # TODO: Replace with real implementation': r'None  # TODO: Replace with real implementation|DUMMY',
            'NotImplemented': r'NotImplementedError|NotImplemented',
            'pass_todo': r'pass\s*#.*(?:TODO|FIXME|XXX)',
            'raise_not_implemented': r'raise\s+NotImplementedError',
            'empty_function': r'def\s+\w+\([^)]*\):\s*pass\s*$',
            'empty_class': r'class\s+\w+[^:]*:\s*pass\s*$'
        }
        
    def scan_all_files(self):
        """Preglej vse Python datoteke v projektu"""
        logger.info("🔍 Starting complete TODO/None  # TODO: Implement audit...")
        
        python_files = list(self.project_root.rglob("*.py"))
        logger.info(f"📁 Found {len(python_files)} Python files to scan")
        
        for py_file in python_files:
            try:
                self.scan_file(py_file)
                self.stats['files_scanned'] += 1
            except Exception as e:
                logger.error(f"❌ Error scanning {py_file}: {e}")
                
        self.analyze_results()
        self.generate_report()
        
    def scan_file(self, file_path: Path):
        """Preglej posamezno datoteko"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Scan for text patterns
            for line_num, line in enumerate(lines, 1):
                self.scan_line(file_path, line_num, line, lines)
                
            # Scan AST for structural issues
            try:
                tree = ast.parse(content)
                self.scan_ast(file_path, tree, lines)
            except SyntaxError as e:
                self.add_issue(file_path, e.lineno or 1, 'SYNTAX_ERROR', 
                             f"Syntax error: {e.msg}", 'CRITICAL',
                             "Fix syntax error before proceeding")
                
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            
    def scan_line(self, file_path: Path, line_num: int, line: str, all_lines: List[str]):
        """Preglej posamezno vrstico"""
        line_stripped = line.strip()
        
        for pattern_name, pattern in self.search_patterns.items():
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                severity = self.determine_severity(pattern_name, line_stripped)
                context = self.get_context(all_lines, line_num)
                suggested_fix = self.suggest_fix(pattern_name, line_stripped, context)
                
                self.add_issue(
                    file_path, line_num, pattern_name,
                    line_stripped, severity, suggested_fix, context
                )
                
    def scan_ast(self, file_path: Path, tree: ast.AST, lines: List[str]):
        """Preglej AST za strukturne probleme"""
        for node in ast.walk(tree):
            # Check for empty functions
            if isinstance(node, ast.FunctionDef):
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    self.add_issue(
                        file_path, node.lineno, 'EMPTY_FUNCTION',
                        f"def {node.name}(...): pass", 'HIGH',
                        f"Implement function {node.name} or add docstring explaining why it's empty"
                    )
                    
            # Check for empty classes
            elif isinstance(node, ast.ClassDef):
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    self.add_issue(
                        file_path, node.lineno, 'EMPTY_CLASS',
                        f"class {node.name}: pass", 'MEDIUM',
                        f"Implement class {node.name} or add docstring explaining purpose"
                    )
                    
            # Check for NotImplementedError raises
            elif isinstance(node, ast.Raise):
                if isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
                    if node.exc.func.id == 'NotImplementedError':
                        self.add_issue(
                            file_path, node.lineno, 'NOT_IMPLEMENTED',
                            lines[node.lineno - 1].strip(), 'CRITICAL',
                            "Implement this functionality"
                        )
                        
    def determine_severity(self, pattern_name: str, line: str) -> str:
        """Določi resnost problema"""
        critical_patterns = ['NotImplemented', 'raise_not_implemented', 'SYNTAX_ERROR']
        high_patterns = ['TODO', 'FIXME', 'BUG', 'empty_function']
        medium_patterns = ['XXX', 'HACK', 'empty_class', 'None  # TODO: Implement']
        
        if pattern_name in critical_patterns:
            return 'CRITICAL'
        elif pattern_name in high_patterns:
            return 'HIGH'
        elif pattern_name in medium_patterns:
            return 'MEDIUM'
        else:
            return 'LOW'
            
    def get_context(self, lines: List[str], line_num: int, context_size: int = 3) -> str:
        """Pridobi kontekst okoli problematične vrstice"""
        start = max(0, line_num - context_size - 1)
        end = min(len(lines), line_num + context_size)
        
        context_lines = []
        for i in range(start, end):
            marker = ">>> " if i == line_num - 1 else "    "
            context_lines.append(f"{marker}{i+1:3d}: {lines[i]}")
            
        return "\n".join(context_lines)
        
    def suggest_fix(self, pattern_name: str, line: str, context: str) -> str:
        """Predlagaj popravek za problem"""
        suggestions = {
            'TODO': "Complete the TODO item or convert to proper issue tracking",
            'FIXME': "Fix the identified issue",
            'XXX': "Review and resolve the marked code",
            'HACK': "Replace hack with proper implementation",
            'BUG': "Fix the identified bug",
            'None  # TODO: Implement': "Replace None  # TODO: Implement with actual implementation",
            'None  # TODO: Replace with real implementation': "Replace None  # TODO: Replace with real implementation code with real implementation",
            'NotImplemented': "Implement the missing functionality",
            'pass_todo': "Complete the implementation",
            'empty_function': "Add function implementation or proper docstring",
            'empty_class': "Add class implementation or proper docstring"
        }
        
        base_suggestion = suggestions.get(pattern_name, "Review and fix this issue")
        
        # Add specific suggestions based on context
        if 'def ' in line and pattern_name in ['empty_function', 'pass_todo']:
            return f"{base_suggestion}. Consider adding parameters validation, return values, and proper logic."
        elif 'class ' in line and pattern_name == 'empty_class':
            return f"{base_suggestion}. Add __init__ method, properties, and methods as needed."
        elif 'TODO' in line.upper():
            todo_text = re.search(r'TODO[:\s]*(.*)', line, re.IGNORECASE)
            if todo_text and todo_text.group(1).strip():
                return f"Complete TODO: {todo_text.group(1).strip()}"
                
        return base_suggestion
        
    def add_issue(self, file_path: Path, line_num: int, issue_type: str, 
                  content: str, severity: str, suggested_fix: str = "", context: str = ""):
        """Dodaj problem na seznam"""
        issue = CodeIssue(
            file_path=str(file_path.relative_to(self.project_root)),
            line_number=line_num,
            issue_type=issue_type,
            content=content,
            severity=severity,
            suggested_fix=suggested_fix,
            context=context
        )
        
        self.issues.append(issue)
        self.stats['total_issues'] += 1
        self.stats[f'{severity.lower()}_issues'] += 1
        
    def analyze_results(self):
        """Analiziraj rezultate"""
        logger.info("📊 Analyzing results...")
        
        # Group by file
        files_with_issues = {}
        for issue in self.issues:
            if issue.file_path not in files_with_issues:
                files_with_issues[issue.file_path] = []
            files_with_issues[issue.file_path].append(issue)
            
        # Sort by severity and count
        self.issues.sort(key=lambda x: (
            {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}[x.severity],
            x.file_path,
            x.line_number
        ))
        
        logger.info(f"📈 Analysis complete:")
        logger.info(f"   Files scanned: {self.stats['files_scanned']}")
        logger.info(f"   Total issues: {self.stats['total_issues']}")
        logger.info(f"   Critical: {self.stats['critical_issues']}")
        logger.info(f"   High: {self.stats['high_issues']}")
        logger.info(f"   Medium: {self.stats['medium_issues']}")
        logger.info(f"   Low: {self.stats['low_issues']}")
        
    def auto_fix_issues(self):
        """Avtomatsko popravi probleme, kjer je to možno"""
        logger.info("🔧 Starting automatic fixes...")
        
        fixable_patterns = ['None  # TODO: Implement', 'None  # TODO: Replace with real implementation', 'pass_todo']
        
        for issue in self.issues:
            if issue.issue_type in fixable_patterns:
                try:
                    if self.attempt_auto_fix(issue):
                        self.fixed_issues.append(issue)
                        self.stats['fixed_issues'] += 1
                except Exception as e:
                    logger.error(f"❌ Failed to auto-fix {issue.file_path}:{issue.line_number}: {e}")
                    
        logger.info(f"✅ Auto-fixed {self.stats['fixed_issues']} issues")
        
    def attempt_auto_fix(self, issue: CodeIssue) -> bool:
        """Poskusi avtomatsko popraviti problem"""
        file_path = self.project_root / issue.file_path
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            original_line = lines[issue.line_number - 1]
            fixed_line = self.generate_fix(issue, original_line)
            
            if fixed_line and fixed_line != original_line:
                lines[issue.line_number - 1] = fixed_line
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                    
                logger.info(f"✅ Fixed {issue.file_path}:{issue.line_number}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error fixing {issue.file_path}:{issue.line_number}: {e}")
            
        return False
        
    def generate_fix(self, issue: CodeIssue, original_line: str) -> Optional[str]:
        """Generiraj popravek za problem"""
        if issue.issue_type == 'None  # TODO: Implement':
            if 'None  # TODO: Implement' in original_line.lower():
                # Replace None  # TODO: Implement with actual implementation
                if 'def ' in original_line:
                    return original_line.replace('None  # TODO: Implement', 'raise NotImplementedError("Implementation needed")')
                else:
                    return original_line.replace('None  # TODO: Implement', 'None  # TODO: Implement')
                    
        elif issue.issue_type == 'None  # TODO: Replace with real implementation':
            if 'None  # TODO: Replace with real implementation' in original_line.lower():
                return original_line.replace('None  # TODO: Replace with real implementation', 'None  # TODO: Replace with real implementation')
                
        elif issue.issue_type == 'pass_todo':
            if 'pass' in original_line and '#' in original_line:
                raise NotImplementedError("TODO: Convert pass # TODO to raise NotImplementedError")
                comment_part = original_line.split('#', 1)[1].strip()
                indent = len(original_line) - len(original_line.lstrip())
                return ' ' * indent + f'raise NotImplementedError("TODO: {comment_part}")\n'
                
        return None
        
    def generate_report(self):
        """Generiraj poročilo"""
        logger.info("📄 Generating comprehensive report...")
        
        # JSON report
        report_data = {
            'scan_timestamp': time.time(),
            'scan_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'project_root': str(self.project_root),
            'statistics': self.stats,
            'issues': [
                {
                    'file_path': issue.file_path,
                    'line_number': issue.line_number,
                    'issue_type': issue.issue_type,
                    'content': issue.content,
                    'severity': issue.severity,
                    'suggested_fix': issue.suggested_fix,
                    'context': issue.context
                }
                for issue in self.issues
            ],
            'fixed_issues': [
                {
                    'file_path': issue.file_path,
                    'line_number': issue.line_number,
                    'issue_type': issue.issue_type,
                    'content': issue.content
                }
                for issue in self.fixed_issues
            ]
        }
        
        # Save JSON report
        json_report_path = self.project_root / 'TODO_AUDIT_REPORT.json'
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        # Generate markdown report
        self.generate_markdown_report(report_data)
        
        # Generate fix script
        self.generate_fix_script()
        
        logger.info(f"📄 Reports saved:")
        logger.info(f"   JSON: {json_report_path}")
        logger.info(f"   Markdown: {self.project_root / 'TODO_AUDIT_REPORT.md'}")
        logger.info(f"   Fix script: {self.project_root / 'AUTO_FIX_TODOS.py'}")
        
    def generate_markdown_report(self, report_data: Dict[str, Any]):
        """Generiraj markdown poročilo"""
        markdown_content = f"""# 🔍 COMPLETE TODO/PLACEHOLDER AUDIT REPORT

## 📊 Executive Summary

**Scan Date:** {report_data['scan_date']}  
**Project Root:** {report_data['project_root']}  
**Files Scanned:** {report_data['statistics']['files_scanned']}  
**Total Issues Found:** {report_data['statistics']['total_issues']}  

### Issue Breakdown
- 🔴 **Critical:** {report_data['statistics']['critical_issues']} issues
- 🟠 **High:** {report_data['statistics']['high_issues']} issues  
- 🟡 **Medium:** {report_data['statistics']['medium_issues']} issues
- 🟢 **Low:** {report_data['statistics']['low_issues']} issues

### Auto-Fix Results
- ✅ **Fixed:** {report_data['statistics']['fixed_issues']} issues
- ⚠️ **Remaining:** {report_data['statistics']['total_issues'] - report_data['statistics']['fixed_issues']} issues

---

## 🔴 Critical Issues (Require Immediate Attention)

"""
        
        critical_issues = [issue for issue in report_data['issues'] if issue['severity'] == 'CRITICAL']
        if critical_issues:
            for issue in critical_issues:
                markdown_content += f"""### {issue['file_path']}:{issue['line_number']}
**Type:** {issue['issue_type']}  
**Content:** `{issue['content']}`  
**Fix:** {issue['suggested_fix']}

```python
{issue['context']}
```

---

"""
        else:
            markdown_content += "✅ No critical issues found!\n\n---\n\n"
            
        markdown_content += """## 🟠 High Priority Issues

"""
        
        high_issues = [issue for issue in report_data['issues'] if issue['severity'] == 'HIGH']
        if high_issues:
            for issue in high_issues[:10]:  # Show first 10
                markdown_content += f"""### {issue['file_path']}:{issue['line_number']}
**Type:** {issue['issue_type']}  
**Content:** `{issue['content']}`  
**Fix:** {issue['suggested_fix']}

"""
            if len(high_issues) > 10:
                markdown_content += f"... and {len(high_issues) - 10} more high priority issues.\n\n"
        else:
            markdown_content += "✅ No high priority issues found!\n\n"
            
        markdown_content += """---

## 📋 Issues by File

"""
        
        # Group issues by file
        issues_by_file = {}
        for issue in report_data['issues']:
            file_path = issue['file_path']
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)
            
        # Sort files by issue count
        sorted_files = sorted(issues_by_file.items(), key=lambda x: len(x[1]), reverse=True)
        
        for file_path, file_issues in sorted_files[:20]:  # Show top 20 files
            severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            for issue in file_issues:
                severity_counts[issue['severity']] += 1
                
            markdown_content += f"""### {file_path}
**Total Issues:** {len(file_issues)}  
🔴 Critical: {severity_counts['CRITICAL']} | 🟠 High: {severity_counts['HIGH']} | 🟡 Medium: {severity_counts['MEDIUM']} | 🟢 Low: {severity_counts['LOW']}

"""
            
        markdown_content += """---

## 🔧 Recommended Actions

### Immediate Actions (Critical & High)
1. **Fix NotImplementedError raises** - These prevent functionality
2. **Complete TODO items** - Essential features are missing
3. **Implement empty functions** - Core functionality gaps
4. **Fix syntax errors** - Prevent system from running

### Medium Priority Actions
1. **Replace None  # TODO: Implement code** - Improve code quality
2. **Remove hack implementations** - Technical debt cleanup
3. **Document empty classes** - Clarify design intentions

### Long-term Actions
1. **Establish TODO tracking** - Use issue tracker instead of code comments
2. **Code review process** - Prevent None  # TODO: Implement code in production
3. **Automated checks** - CI/CD pipeline to catch issues early

---

## 📈 Progress Tracking

### Completion Status
"""
        
        total_issues = report_data['statistics']['total_issues']
        fixed_issues = report_data['statistics']['fixed_issues']
        completion_rate = (fixed_issues / total_issues * 100) if total_issues > 0 else 100
        
        markdown_content += f"""
**Overall Completion:** {completion_rate:.1f}% ({fixed_issues}/{total_issues} issues resolved)

### Next Steps
1. Run `python AUTO_FIX_TODOS.py` to apply automatic fixes
2. Manually review and fix critical issues
3. Re-run audit to track progress: `python COMPLETE_TODO_AUDIT.py`

---

**Report Generated:** {report_data['scan_date']}  
**Total Files Scanned:** {report_data['statistics']['files_scanned']}  
**Audit Tool:** COMPLETE_TODO_AUDIT.py
"""
        
        # Save markdown report
        markdown_path = self.project_root / 'TODO_AUDIT_REPORT.md'
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
    def generate_fix_script(self):
        """Generiraj script za avtomatske popravke"""
        fix_script_content = f'''#!/usr/bin/env python3
"""
🔧 AUTO-FIX SCRIPT FOR TODO/PLACEHOLDER ISSUES
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

This script automatically fixes common TODO/None  # TODO: Implement issues.
Run with: python AUTO_FIX_TODOS.py
"""

import os
import re
from pathlib import Path

def fix_file(file_path, fixes):
    """Apply fixes to a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        modified = False
        for line_num, new_content in fixes:
            if line_num <= len(lines):
                lines[line_num - 1] = new_content
                modified = True
                print(f"✅ Fixed {{file_path}}:{{line_num}}")
                
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                
    except Exception as e:
        print(f"❌ Error fixing {{file_path}}: {{e}}")

def main():
    """Apply all automatic fixes"""
    print("🔧 Starting automatic TODO/None  # TODO: Implement fixes...")
    
    project_root = Path(__file__).parent
    
    # Generated fixes based on audit results
    fixes = {{
'''
        
        # Add specific fixes for each file
        fixes_by_file = {}
        for issue in self.issues:
            if issue.issue_type in ['None  # TODO: Implement', 'None  # TODO: Replace with real implementation', 'pass_todo']:
                file_path = issue.file_path
                if file_path not in fixes_by_file:
                    fixes_by_file[file_path] = []
                    
                # Generate fix
                original_line = issue.content
                fixed_line = self.generate_fix(issue, original_line)
                if fixed_line:
                    fixes_by_file[file_path].append((issue.line_number, fixed_line))
                    
        for file_path, file_fixes in fixes_by_file.items():
            fix_script_content += f'''        "{file_path}": {file_fixes},
'''
            
        fix_script_content += '''    }
    
    total_fixes = 0
    for file_path, file_fixes in fixes.items():
        if file_fixes:
            fix_file(project_root / file_path, file_fixes)
            total_fixes += len(file_fixes)
            
    print(f"✅ Applied {total_fixes} automatic fixes")
    print("🔄 Re-run COMPLETE_TODO_AUDIT.py to verify fixes")

if __name__ == "__main__":
    main()
'''
        
        # Save fix script
        fix_script_path = self.project_root / 'AUTO_FIX_TODOS.py'
        with open(fix_script_path, 'w', encoding='utf-8') as f:
            f.write(fix_script_content)
            
        # Make executable on Unix systems
        try:
            os.chmod(fix_script_path, 0o755)
        except:
            pass
            
    def print_summary(self):
        """Izpiši povzetek rezultatov"""
        print("\n" + "="*80)
        print("🔍 COMPLETE TODO/PLACEHOLDER AUDIT - RESULTS")
        print("="*80)
        print(f"📁 Files scanned: {self.stats['files_scanned']}")
        print(f"📊 Total issues: {self.stats['total_issues']}")
        print(f"🔴 Critical: {self.stats['critical_issues']}")
        print(f"🟠 High: {self.stats['high_issues']}")
        print(f"🟡 Medium: {self.stats['medium_issues']}")
        print(f"🟢 Low: {self.stats['low_issues']}")
        print(f"✅ Auto-fixed: {self.stats['fixed_issues']}")
        
        if self.stats['critical_issues'] > 0:
            print(f"\n🚨 CRITICAL ISSUES FOUND!")
            print("These issues prevent the system from functioning properly:")
            for issue in self.issues:
                if issue.severity == 'CRITICAL':
                    print(f"  ❌ {issue.file_path}:{issue.line_number} - {issue.issue_type}")
                    
        completion_rate = ((self.stats['total_issues'] - self.stats['critical_issues'] - self.stats['high_issues']) / 
                          self.stats['total_issues'] * 100) if self.stats['total_issues'] > 0 else 100
        
        print(f"\n📈 Code Quality Score: {completion_rate:.1f}%")
        
        if completion_rate >= 90:
            print("🎉 EXCELLENT - Code is production ready!")
        elif completion_rate >= 75:
            print("✅ GOOD - Minor issues to address")
        elif completion_rate >= 50:
            print("⚠️ NEEDS WORK - Several issues to fix")
        else:
            print("❌ CRITICAL - Major issues prevent production use")
            
        print("="*80)

def main():
    """Main entry point"""
    project_root = Path(__file__).parent
    
    print("🔍 Starting Complete TODO/Placeholder Audit")
    print(f"📁 Project root: {project_root}")
    print("="*60)
    
    auditor = CompleteTODOAuditor(project_root)
    
    try:
        # Scan all files
        auditor.scan_all_files()
        
        # Attempt automatic fixes
        auditor.auto_fix_issues()
        
        # Print summary
        auditor.print_summary()
        
        print(f"\n📄 Detailed reports saved:")
        print(f"   - TODO_AUDIT_REPORT.json")
        print(f"   - TODO_AUDIT_REPORT.md")
        print(f"   - AUTO_FIX_TODOS.py")
        
    except KeyboardInterrupt:
        print("\n⚠️ Audit interrupted by user")
    except Exception as e:
        print(f"\n❌ Audit failed: {e}")
        raise

if __name__ == "__main__":
    main()