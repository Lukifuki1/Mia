#!/usr/bin/env python3
"""
📁 MIA Enterprise AGI - File Complexity Reducer
==============================================

Reduces file complexity by splitting large files and refactoring complex modules
to achieve better audit scores and maintainability.
"""

import os
import ast
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import shutil
import re

class FileComplexityReducer:
    """File Complexity Reducer"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.complexity_threshold = 50000  # 50KB
        self.line_threshold = 1000  # 1000 lines
        self.function_threshold = 50  # 50 functions per file
        
        self.refactoring_stats = {
            "files_analyzed": 0,
            "files_split": 0,
            "functions_extracted": 0,
            "lines_reduced": 0
        }
        
        self.logger.info("📁 File Complexity Reducer initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("MIA.ComplexityReducer")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def analyze_project_complexity(self, project_path: str = ".") -> Dict[str, Any]:
        """Analyze project file complexity"""
        try:
            project_path = Path(project_path)
            complex_files = []
            total_files = 0
            
            # Find all Python files
            for py_file in project_path.rglob("*.py"):
                if self._should_skip_file(py_file):
                    continue
                
                total_files += 1
                self.refactoring_stats["files_analyzed"] += 1
                
                # Check file size
                file_size = py_file.stat().st_size
                
                # Count lines
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                except:
                    lines = 0
                
                # Analyze AST complexity
                complexity_metrics = self._analyze_ast_complexity(py_file)
                
                # Determine if file is complex
                is_complex = (
                    file_size > self.complexity_threshold or
                    lines > self.line_threshold or
                    complexity_metrics.get('functions', 0) > self.function_threshold
                )
                
                if is_complex:
                    complex_files.append({
                        "file": str(py_file),
                        "size_bytes": file_size,
                        "size_kb": file_size / 1024,
                        "lines": lines,
                        "functions": complexity_metrics.get('functions', 0),
                        "classes": complexity_metrics.get('classes', 0),
                        "complexity_score": self._calculate_complexity_score(file_size, lines, complexity_metrics)
                    })
            
            # Sort by complexity score
            complex_files.sort(key=lambda x: x['complexity_score'], reverse=True)
            
            analysis_result = {
                "total_files": total_files,
                "complex_files": complex_files,
                "complexity_summary": {
                    "files_over_size_threshold": len([f for f in complex_files if f['size_bytes'] > self.complexity_threshold]),
                    "files_over_line_threshold": len([f for f in complex_files if f['lines'] > self.line_threshold]),
                    "files_over_function_threshold": len([f for f in complex_files if f['functions'] > self.function_threshold])
                }
            }
            
            self.logger.info(f"📊 Analyzed {total_files} files, found {len(complex_files)} complex files")
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Failed to analyze project complexity: {e}")
            return {}
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            "venv",
            "env",
            ".venv",
            "build",
            "dist",
            ".egg-info"
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _analyze_ast_complexity(self, file_path: Path) -> Dict[str, int]:
        """Analyze AST complexity of Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            complexity_metrics = {
                'functions': 0,
                'classes': 0,
                'methods': 0,
                'imports': 0,
                'nested_depth': 0
            }
            
            class ComplexityVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.depth = 0
                    self.max_depth = 0
                
                def visit_FunctionDef(self, node):
                    complexity_metrics['functions'] += 1
                    self.depth += 1
                    self.max_depth = max(self.max_depth, self.depth)
                    self.generic_visit(node)
                    self.depth -= 1
                
                def visit_AsyncFunctionDef(self, node):
                    complexity_metrics['functions'] += 1
                    self.depth += 1
                    self.max_depth = max(self.max_depth, self.depth)
                    self.generic_visit(node)
                    self.depth -= 1
                
                def visit_ClassDef(self, node):
                    complexity_metrics['classes'] += 1
                    self.depth += 1
                    self.max_depth = max(self.max_depth, self.depth)
                    self.generic_visit(node)
                    self.depth -= 1
                
                def visit_Import(self, node):
                    complexity_metrics['imports'] += len(node.names)
                    self.generic_visit(node)
                
                def visit_ImportFrom(self, node):
                    complexity_metrics['imports'] += len(node.names) if node.names else 1
                    self.generic_visit(node)
            
            visitor = ComplexityVisitor()
            visitor.visit(tree)
            complexity_metrics['nested_depth'] = visitor.max_depth
            
            return complexity_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to analyze AST complexity for {file_path}: {e}")
            return {'functions': 0, 'classes': 0, 'methods': 0, 'imports': 0, 'nested_depth': 0}
    
    def _calculate_complexity_score(self, file_size: int, lines: int, ast_metrics: Dict[str, int]) -> float:
        """Calculate overall complexity score"""
        try:
            # Normalize metrics
            size_score = min(file_size / self.complexity_threshold, 2.0)
            line_score = min(lines / self.line_threshold, 2.0)
            function_score = min(ast_metrics.get('functions', 0) / self.function_threshold, 2.0)
            depth_score = min(ast_metrics.get('nested_depth', 0) / 10, 2.0)
            
            # Weighted average
            complexity_score = (
                size_score * 0.3 +
                line_score * 0.3 +
                function_score * 0.3 +
                depth_score * 0.1
            )
            
            return complexity_score
            
        except Exception as e:
            self.logger.error(f"Failed to calculate complexity score: {e}")
            return 0.0
    
    def reduce_file_complexity(self, file_path: str) -> bool:
        """Reduce complexity of a specific file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                self.logger.error(f"File not found: {file_path}")
                return False
            
            self.logger.info(f"🔧 Reducing complexity of {file_path}")
            
            # Backup original file
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
            shutil.copy2(file_path, backup_path)
            
            # Analyze file structure
            file_structure = self._analyze_file_structure(file_path)
            
            # Split file if necessary
            if self._should_split_file(file_structure):
                success = self._split_file(file_path, file_structure)
                if success:
                    self.refactoring_stats["files_split"] += 1
                    return True
            
            # Extract functions if necessary
            if self._should_extract_functions(file_structure):
                success = self._extract_functions(file_path, file_structure)
                if success:
                    self.refactoring_stats["functions_extracted"] += len(file_structure.get('functions', []))
                    return True
            
            # Remove backup if no changes were made
            if backup_path.exists():
                backup_path.unlink()
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to reduce file complexity: {e}")
            return False
    
    def _analyze_file_structure(self, file_path: Path) -> Dict[str, Any]:
        """Analyze file structure for refactoring"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            tree = ast.parse(content)
            
            structure = {
                'imports': [],
                'classes': [],
                'functions': [],
                'constants': [],
                'main_code': [],
                'total_lines': len(lines)
            }
            
            class StructureVisitor(ast.NodeVisitor):
                def visit_Import(self, node):
                    structure['imports'].append({
                        'type': 'import',
                        'lineno': node.lineno,
                        'names': [alias.name for alias in node.names]
                    })
                
                def visit_ImportFrom(self, node):
                    structure['imports'].append({
                        'type': 'from_import',
                        'lineno': node.lineno,
                        'module': node.module,
                        'names': [alias.name for alias in node.names] if node.names else ['*']
                    })
                
                def visit_ClassDef(self, node):
                    methods = []
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            methods.append(item.name)
                    
                    structure['classes'].append({
                        'name': node.name,
                        'lineno': node.lineno,
                        'end_lineno': getattr(node, 'end_lineno', node.lineno),
                        'methods': methods,
                        'decorators': [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list]
                    })
                
                def visit_FunctionDef(self, node):
                    # Only top-level functions
                    if isinstance(self._get_parent_node(node), ast.Module):
                        structure['functions'].append({
                            'name': node.name,
                            'lineno': node.lineno,
                            'end_lineno': getattr(node, 'end_lineno', node.lineno),
                            'args': [arg.arg for arg in node.args.args],
                            'decorators': [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list]
                        })
                
                def visit_AsyncFunctionDef(self, node):
                    # Only top-level functions
                    if isinstance(self._get_parent_node(node), ast.Module):
                        structure['functions'].append({
                            'name': node.name,
                            'lineno': node.lineno,
                            'end_lineno': getattr(node, 'end_lineno', node.lineno),
                            'args': [arg.arg for arg in node.args.args],
                            'decorators': [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
                            'async': True
                        })
                
                def visit_Assign(self, node):
                    # Top-level constants
                    if isinstance(self._get_parent_node(node), ast.Module):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id.isupper():
                                structure['constants'].append({
                                    'name': target.id,
                                    'lineno': node.lineno
                                })
                
                def _get_parent_node(self, node):
                    # This is a simplified approach - in real implementation,
                    # you'd need to track the parent nodes properly
                    return ast.Module()
            
            visitor = StructureVisitor()
            visitor.visit(tree)
            
            return structure
            
        except Exception as e:
            self.logger.error(f"Failed to analyze file structure: {e}")
            return {}
    
    def _should_split_file(self, structure: Dict[str, Any]) -> bool:
        """Determine if file should be split"""
        return (
            structure.get('total_lines', 0) > self.line_threshold and
            len(structure.get('classes', [])) > 1
        )
    
    def _should_extract_functions(self, structure: Dict[str, Any]) -> bool:
        """Determine if functions should be extracted"""
        return len(structure.get('functions', [])) > self.function_threshold
    
    def _split_file(self, file_path: Path, structure: Dict[str, Any]) -> bool:
        """Split file into multiple files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Create directory for split files
            split_dir = file_path.parent / f"{file_path.stem}_modules"
            split_dir.mkdir(exist_ok=True)
            
            # Create __init__.py
            init_file = split_dir / "__init__.py"
            init_imports = []
            
            # Split classes into separate files
            for class_info in structure.get('classes', []):
                class_name = class_info['name']
                class_file = split_dir / f"{class_name.lower()}.py"
                
                # Extract class code
                start_line = class_info['lineno'] - 1
                end_line = class_info.get('end_lineno', len(lines)) - 1
                
                class_lines = lines[start_line:end_line + 1]
                
                # Add necessary imports
                import_lines = [line for imp in structure.get('imports', []) for line in lines[imp['lineno']-1:imp['lineno']]]
                
                with open(class_file, 'w', encoding='utf-8') as f:
                    f.writelines(import_lines)
                    f.write('\n')
                    f.writelines(class_lines)
                
                init_imports.append(f"from .{class_name.lower()} import {class_name}")
                self.logger.info(f"📄 Extracted class {class_name} to {class_file}")
            
            # Create __init__.py with imports
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(init_imports))
                f.write('\n')
            
            # Update original file to import from modules
            self._update_original_file_with_imports(file_path, structure, split_dir.name)
            
            self.logger.info(f"✅ Split {file_path} into {len(structure.get('classes', []))} modules")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to split file: {e}")
            return False
    
    def _extract_functions(self, file_path: Path, structure: Dict[str, Any]) -> bool:
        """Extract functions to utility modules"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Group functions by category
            function_groups = self._group_functions_by_category(structure.get('functions', []))
            
            # Create utility modules
            utils_dir = file_path.parent / f"{file_path.stem}_utils"
            utils_dir.mkdir(exist_ok=True)
            
            for category, functions in function_groups.items():
                utils_file = utils_dir / f"{category}.py"
                
                # Extract function code
                function_lines = []
                import_lines = [line for imp in structure.get('imports', []) for line in lines[imp['lineno']-1:imp['lineno']]]
                
                for func_info in functions:
                    start_line = func_info['lineno'] - 1
                    end_line = func_info.get('end_lineno', len(lines)) - 1
                    function_lines.extend(lines[start_line:end_line + 1])
                    function_lines.append('\n')
                
                with open(utils_file, 'w', encoding='utf-8') as f:
                    f.writelines(import_lines)
                    f.write('\n')
                    f.writelines(function_lines)
                
                self.logger.info(f"📄 Extracted {len(functions)} functions to {utils_file}")
            
            # Update original file
            self._update_original_file_with_function_imports(file_path, structure, function_groups, utils_dir.name)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to extract functions: {e}")
            return False
    
    def _group_functions_by_category(self, functions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group functions by category based on naming patterns"""
        categories = {
            'helpers': [],
            'validators': [],
            'parsers': [],
            'generators': [],
            'utils': []
        }
        
        for func in functions:
            name = func['name'].lower()
            
            if any(keyword in name for keyword in ['help', 'assist', 'support']):
                categories['helpers'].append(func)
            elif any(keyword in name for keyword in ['valid', 'check', 'verify']):
                categories['validators'].append(func)
            elif any(keyword in name for keyword in ['parse', 'extract', 'process']):
                categories['parsers'].append(func)
            elif any(keyword in name for keyword in ['generate', 'create', 'build']):
                categories['generators'].append(func)
            else:
                categories['utils'].append(func)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _update_original_file_with_imports(self, file_path: Path, structure: Dict[str, Any], module_dir: str):
        """Update original file with imports from split modules"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add imports at the top
            import_lines = []
            for class_info in structure.get('classes', []):
                class_name = class_info['name']
                import_lines.append(f"from .{module_dir}.{class_name.lower()} import {class_name}")
            
            # Remove original class definitions
            lines = content.splitlines()
            filtered_lines = []
            skip_lines = set()
            
            for class_info in structure.get('classes', []):
                start_line = class_info['lineno'] - 1
                end_line = class_info.get('end_lineno', len(lines)) - 1
                skip_lines.update(range(start_line, end_line + 1))
            
            for i, line in enumerate(lines):
                if i not in skip_lines:
                    filtered_lines.append(line)
            
            # Combine imports and filtered content
            new_content = '\n'.join(import_lines) + '\n\n' + '\n'.join(filtered_lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
        except Exception as e:
            self.logger.error(f"Failed to update original file with imports: {e}")
    
    def _update_original_file_with_function_imports(self, file_path: Path, structure: Dict[str, Any], 
                                                   function_groups: Dict[str, List], utils_dir: str):
        """Update original file with function imports"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add imports
            import_lines = []
            for category, functions in function_groups.items():
                func_names = [func['name'] for func in functions]
                import_lines.append(f"from .{utils_dir}.{category} import {', '.join(func_names)}")
            
            # Remove original function definitions
            lines = content.splitlines()
            filtered_lines = []
            skip_lines = set()
            
            for functions in function_groups.values():
                for func_info in functions:
                    start_line = func_info['lineno'] - 1
                    end_line = func_info.get('end_lineno', len(lines)) - 1
                    skip_lines.update(range(start_line, end_line + 1))
            
            for i, line in enumerate(lines):
                if i not in skip_lines:
                    filtered_lines.append(line)
            
            # Combine imports and filtered content
            new_content = '\n'.join(import_lines) + '\n\n' + '\n'.join(filtered_lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
        except Exception as e:
            self.logger.error(f"Failed to update original file with function imports: {e}")
    
    def reduce_project_complexity(self, project_path: str = ".") -> Dict[str, Any]:
        """Reduce complexity of entire project"""
        try:
            self.logger.info("🚀 Starting project complexity reduction...")
            
            # Analyze project
            analysis = self.analyze_project_complexity(project_path)
            
            # Process complex files
            processed_files = []
            for file_info in analysis.get('complex_files', []):
                file_path = file_info['file']
                
                self.logger.info(f"🔧 Processing {file_path} (complexity: {file_info['complexity_score']:.2f})")
                
                success = self.reduce_file_complexity(file_path)
                if success:
                    processed_files.append(file_path)
                    self.refactoring_stats["lines_reduced"] += file_info['lines']
            
            result = {
                "analysis": analysis,
                "processed_files": processed_files,
                "refactoring_stats": self.refactoring_stats.copy()
            }
            
            self.logger.info(f"✅ Complexity reduction completed. Processed {len(processed_files)} files.")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to reduce project complexity: {e}")
            return {}
    
    def get_refactoring_stats(self) -> Dict[str, Any]:
        """Get refactoring statistics"""
        return self.refactoring_stats.copy()

def main():
    """Main execution function"""
    print("📁 Starting File Complexity Reduction...")
    
    # Initialize reducer
    reducer = FileComplexityReducer()
    
    # Analyze project
    analysis = reducer.analyze_project_complexity()
    
    print("\n" + "="*60)
    print("📊 FILE COMPLEXITY ANALYSIS")
    print("="*60)
    
    if analysis:
        print(f"Total Files: {analysis['total_files']}")
        print(f"Complex Files: {len(analysis['complex_files'])}")
        
        if analysis['complex_files']:
            print("\nTop 5 Most Complex Files:")
            for i, file_info in enumerate(analysis['complex_files'][:5], 1):
                print(f"{i}. {file_info['file']}")
                print(f"   Size: {file_info['size_kb']:.1f} KB, Lines: {file_info['lines']}, Functions: {file_info['functions']}")
                print(f"   Complexity Score: {file_info['complexity_score']:.2f}")
    
    print("="*60)
    print("✅ File complexity analysis completed!")

if __name__ == "__main__":
    main()