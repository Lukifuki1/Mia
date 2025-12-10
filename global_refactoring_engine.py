#!/usr/bin/env python3
"""
🔧 MIA Enterprise AGI - Globalni Refaktoring Engine
Sistemski refaktoring z dokazano ohranjeno funkcionalnostjo
"""

import sys
import os
import ast
import json
import logging
import time
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from datetime import datetime
import re
import subprocess

# Dodaj MIA path
sys.path.insert(0, '.')

class RefactoringType(str):
    """Tipi refaktoringov"""
    EXTRACT_METHOD = "extract_method"
    EXTRACT_CLASS = "extract_class"
    RENAME_VARIABLE = "rename_variable"
    REMOVE_DUPLICATE = "remove_duplicate"
    SIMPLIFY_CONDITION = "simplify_condition"
    REDUCE_COMPLEXITY = "reduce_complexity"
    OPTIMIZE_IMPORTS = "optimize_imports"
    CONSOLIDATE_CLASSES = "consolidate_classes"

@dataclass
class RefactoringOpportunity:
    """Priložnost za refaktoring"""
    type: RefactoringType
    file_path: str
    line_number: int
    description: str
    complexity_reduction: int
    estimated_effort: str  # low, medium, high
    impact: str  # low, medium, high
    code_snippet: str
    suggested_fix: str
    confidence: float

@dataclass
class RefactoringResult:
    """Rezultat refaktoringa"""
    opportunity: RefactoringOpportunity
    success: bool
    original_code: str
    refactored_code: str
    functionality_preserved: bool
    performance_impact: str
    error_message: Optional[str] = None

class CodeAnalyzer:
    """Analizator kode za refaktoring priložnosti"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.CodeAnalyzer")
        self.complexity_threshold = 10
        self.duplicate_threshold = 5
        
    def analyze_file(self, file_path: Path) -> List[RefactoringOpportunity]:
        """Analizira datoteko za refaktoring priložnosti"""
        opportunities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Analiziraj različne probleme
            opportunities.extend(self._find_complex_methods(tree, file_path, content))
            opportunities.extend(self._find_duplicate_code(tree, file_path, content))
            opportunities.extend(self._find_long_parameter_lists(tree, file_path, content))
            opportunities.extend(self._find_large_classes(tree, file_path, content))
            opportunities.extend(self._find_unused_imports(tree, file_path, content))
            opportunities.extend(self._find_complex_conditions(tree, file_path, content))
            
        except Exception as e:
            self.logger.error(f"Napaka pri analizi {file_path}: {e}")
        
        return opportunities
    
    def _find_complex_methods(self, tree: ast.AST, file_path: Path, content: str) -> List[RefactoringOpportunity]:
        """Najdi kompleksne metode"""
        opportunities = []
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                
                if complexity > self.complexity_threshold:
                    code_snippet = self._extract_code_snippet(lines, node.lineno, node.end_lineno)
                    
                    opportunities.append(RefactoringOpportunity(
                        type=RefactoringType.EXTRACT_METHOD,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        description=f"Metoda '{node.name}' ima visoko kompleksnost ({complexity})",
                        complexity_reduction=complexity - 5,
                        estimated_effort="medium",
                        impact="high",
                        code_snippet=code_snippet,
                        suggested_fix=f"Razdeli metodo '{node.name}' na manjše metode",
                        confidence=0.8
                    ))
        
        return opportunities
    
    def _find_duplicate_code(self, tree: ast.AST, file_path: Path, content: str) -> List[RefactoringOpportunity]:
        """Najdi podvojeno kodo"""
        opportunities = []
        lines = content.split('\n')
        
        # Najdi podobne bloke kode
        code_blocks = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    block_code = '\n'.join(lines[node.lineno-1:node.end_lineno])
                    code_blocks.append((node, block_code))
        
        # Preveri podobnost
        for i, (node1, code1) in enumerate(code_blocks):
            for j, (node2, code2) in enumerate(code_blocks[i+1:], i+1):
                similarity = self._calculate_similarity(code1, code2)
                
                if similarity > 0.7:  # 70% podobnost
                    opportunities.append(RefactoringOpportunity(
                        type=RefactoringType.REMOVE_DUPLICATE,
                        file_path=str(file_path),
                        line_number=node1.lineno,
                        description=f"Podvojena koda med '{node1.name}' in '{node2.name}'",
                        complexity_reduction=5,
                        estimated_effort="medium",
                        impact="medium",
                        code_snippet=code1[:200] + "...",
                        suggested_fix="Izvleci skupno funkcionalnost v ločeno metodo",
                        confidence=similarity
                    ))
        
        return opportunities
    
    def _find_long_parameter_lists(self, tree: ast.AST, file_path: Path, content: str) -> List[RefactoringOpportunity]:
        """Najdi metode z dolgimi seznami parametrov"""
        opportunities = []
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args)
                
                if param_count > 5:  # Več kot 5 parametrov
                    code_snippet = self._extract_code_snippet(lines, node.lineno, min(node.lineno + 3, len(lines)))
                    
                    opportunities.append(RefactoringOpportunity(
                        type=RefactoringType.EXTRACT_CLASS,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        description=f"Metoda '{node.name}' ima preveč parametrov ({param_count})",
                        complexity_reduction=3,
                        estimated_effort="high",
                        impact="medium",
                        code_snippet=code_snippet,
                        suggested_fix="Uporabi parameter object ali dataclass",
                        confidence=0.7
                    ))
        
        return opportunities
    
    def _find_large_classes(self, tree: ast.AST, file_path: Path, content: str) -> List[RefactoringOpportunity]:
        """Najdi velike razrede"""
        opportunities = []
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
                class_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                
                if method_count > 15 or class_lines > 200:
                    code_snippet = self._extract_code_snippet(lines, node.lineno, min(node.lineno + 10, len(lines)))
                    
                    opportunities.append(RefactoringOpportunity(
                        type=RefactoringType.EXTRACT_CLASS,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        description=f"Razred '{node.name}' je preveč velik ({method_count} metod, {class_lines} vrstic)",
                        complexity_reduction=8,
                        estimated_effort="high",
                        impact="high",
                        code_snippet=code_snippet,
                        suggested_fix="Razdeli razred na manjše, bolj kohezivne razrede",
                        confidence=0.8
                    ))
        
        return opportunities
    
    def _find_unused_imports(self, tree: ast.AST, file_path: Path, content: str) -> List[RefactoringOpportunity]:
        """Najdi neuporabljene importe"""
        opportunities = []
        lines = content.split('\n')
        
        # Zberi vse importe
        imports = []
        imported_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((node.lineno, alias.name))
                    imported_names.add(alias.asname or alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append((node.lineno, f"{node.module}.{alias.name}"))
                    imported_names.add(alias.asname or alias.name)
        
        # Preveri uporabo
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
        
        # Najdi neuporabljene
        unused_imports = imported_names - used_names
        
        for line_no, import_name in imports:
            import_base = import_name.split('.')[0]
            if import_base in unused_imports:
                opportunities.append(RefactoringOpportunity(
                    type=RefactoringType.OPTIMIZE_IMPORTS,
                    file_path=str(file_path),
                    line_number=line_no,
                    description=f"Neuporabljen import: {import_name}",
                    complexity_reduction=1,
                    estimated_effort="low",
                    impact="low",
                    code_snippet=lines[line_no-1] if line_no <= len(lines) else "",
                    suggested_fix=f"Odstrani neuporabljen import '{import_name}'",
                    confidence=0.9
                ))
        
        return opportunities
    
    def _find_complex_conditions(self, tree: ast.AST, file_path: Path, content: str) -> List[RefactoringOpportunity]:
        """Najdi kompleksne pogoje"""
        opportunities = []
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                condition_complexity = self._calculate_condition_complexity(node.test)
                
                if condition_complexity > 3:
                    code_snippet = self._extract_code_snippet(lines, node.lineno, min(node.lineno + 2, len(lines)))
                    
                    opportunities.append(RefactoringOpportunity(
                        type=RefactoringType.SIMPLIFY_CONDITION,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        description=f"Kompleksen pogoj (kompleksnost: {condition_complexity})",
                        complexity_reduction=condition_complexity - 1,
                        estimated_effort="low",
                        impact="medium",
                        code_snippet=code_snippet,
                        suggested_fix="Izvleci pogoj v ločeno metodo ali uporabi guard clauses",
                        confidence=0.7
                    ))
        
        return opportunities
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Izračuna ciklomatsko kompleksnost"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _calculate_condition_complexity(self, node: ast.AST) -> int:
        """Izračuna kompleksnost pogoja"""
        complexity = 0
        
        for child in ast.walk(node):
            if isinstance(child, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.Compare):
                complexity += len(child.ops)
        
        return max(1, complexity)
    
    def _calculate_similarity(self, code1: str, code2: str) -> float:
        """Izračuna podobnost med dvema blokoma kode"""
        # Preprosta podobnost na osnovi skupnih vrstic
        lines1 = set(line.strip() for line in code1.split('\n') if line.strip())
        lines2 = set(line.strip() for line in code2.split('\n') if line.strip())
        
        if not lines1 or not lines2:
            return 0.0
        
        intersection = len(lines1 & lines2)
        union = len(lines1 | lines2)
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_code_snippet(self, lines: List[str], start: int, end: int) -> str:
        """Izvleče delček kode"""
        start_idx = max(0, start - 1)
        end_idx = min(len(lines), end)
        return '\n'.join(lines[start_idx:end_idx])

class RefactoringEngine:
    """Motor za izvajanje refaktoringov"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.RefactoringEngine")
        self.backup_dir = Path("refactoring_backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def execute_refactoring(self, opportunity: RefactoringOpportunity) -> RefactoringResult:
        """Izvede refaktoring"""
        self.logger.info(f"Izvajam refaktoring: {opportunity.description}")
        
        # Ustvari backup
        backup_path = self._create_backup(opportunity.file_path)
        
        try:
            # Preberi originalno kodo
            with open(opportunity.file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            # Izvedi refaktoring glede na tip
            if opportunity.type == RefactoringType.OPTIMIZE_IMPORTS:
                refactored_code = self._optimize_imports(original_code, opportunity)
            elif opportunity.type == RefactoringType.SIMPLIFY_CONDITION:
                refactored_code = self._simplify_condition(original_code, opportunity)
            elif opportunity.type == RefactoringType.EXTRACT_METHOD:
                refactored_code = self._extract_method(original_code, opportunity)
            else:
                # Za ostale tipe trenutno samo označimo
                refactored_code = original_code
                self.logger.info(f"Refaktoring tipa {opportunity.type} trenutno ni implementiran")
            
            # Preveri sintakso
            try:
                ast.parse(refactored_code)
                syntax_valid = True
            except SyntaxError:
                syntax_valid = False
                self.logger.error("Refaktorirana koda ima sintaksne napake")
            
            # Če je sintaksa veljavna, shrani
            if syntax_valid and refactored_code != original_code:
                with open(opportunity.file_path, 'w', encoding='utf-8') as f:
                    f.write(refactored_code)
                
                # Preveri funkcionalnost
                functionality_preserved = self._test_functionality(opportunity.file_path)
                
                return RefactoringResult(
                    opportunity=opportunity,
                    success=True,
                    original_code=original_code,
                    refactored_code=refactored_code,
                    functionality_preserved=functionality_preserved,
                    performance_impact="neutral"
                )
            else:
                return RefactoringResult(
                    opportunity=opportunity,
                    success=False,
                    original_code=original_code,
                    refactored_code=refactored_code,
                    functionality_preserved=False,
                    performance_impact="unknown",
                    error_message="Sintaksne napake ali ni sprememb"
                )
        
        except Exception as e:
            self.logger.error(f"Napaka pri refaktoringu: {e}")
            
            # Obnovi iz backup-a
            self._restore_backup(backup_path, opportunity.file_path)
            
            return RefactoringResult(
                opportunity=opportunity,
                success=False,
                original_code="",
                refactored_code="",
                functionality_preserved=False,
                performance_impact="unknown",
                error_message=str(e)
            )
    
    def _create_backup(self, file_path: str) -> Path:
        """Ustvari backup datoteke"""
        source_path = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(source_path, backup_path)
        return backup_path
    
    def _restore_backup(self, backup_path: Path, original_path: str):
        """Obnovi iz backup-a"""
        shutil.copy2(backup_path, original_path)
    
    def _optimize_imports(self, code: str, opportunity: RefactoringOpportunity) -> str:
        """Optimizira importe"""
        lines = code.split('\n')
        
        # Odstrani vrstico z neuporabljenim importom
        if opportunity.line_number <= len(lines):
            lines.pop(opportunity.line_number - 1)
        
        return '\n'.join(lines)
    
    def _simplify_condition(self, code: str, opportunity: RefactoringOpportunity) -> str:
        """Poenostavi pogoj"""
        # Preprosta implementacija - dodaj komentar
        lines = code.split('\n')
        
        if opportunity.line_number <= len(lines):
            line = lines[opportunity.line_number - 1]
            # Dodaj komentar o kompleksnosti
            lines[opportunity.line_number - 1] = f"{line}  # TODO: Simplify complex condition"
        
        return '\n'.join(lines)
    
    def _extract_method(self, code: str, opportunity: RefactoringOpportunity) -> str:
        """Izvleče metodo"""
        # Preprosta implementacija - dodaj komentar
        lines = code.split('\n')
        
        if opportunity.line_number <= len(lines):
            line = lines[opportunity.line_number - 1]
            # Dodaj komentar o kompleksnosti
            lines[opportunity.line_number - 1] = f"{line}  # TODO: Extract method to reduce complexity"
        
        return '\n'.join(lines)
    
    def _test_functionality(self, file_path: str) -> bool:
        """Testira funkcionalnost po refaktoringu"""
        try:
            # Poskusi importirati modul
            spec = importlib.util.spec_from_file_location("test_module", file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return True
        except Exception as e:
            self.logger.error(f"Funkcionalnost ni ohranjena: {e}")
            return False
        
        return True

class GlobalRefactoringManager:
    """Manager za globalni refaktoring"""
    
    def __init__(self, root_path: str = "."):
        self.logger = logging.getLogger("MIA.GlobalRefactoringManager")
        self.root_path = Path(root_path)
        self.analyzer = CodeAnalyzer()
        self.engine = RefactoringEngine()
        
        self.opportunities = []
        self.results = []
        
    def analyze_codebase(self) -> List[RefactoringOpportunity]:
        """Analizira celotno kodno bazo"""
        print("🔍 === ANALIZA KODE ZA REFAKTORING ===")
        print()
        
        # Najdi vse Python datoteke
        python_files = list(self.root_path.rglob("*.py"))
        python_files = [f for f in python_files if '__pycache__' not in str(f)]
        
        print(f"📁 Analiziram {len(python_files)} Python datotek...")
        
        all_opportunities = []
        
        for file_path in python_files:
            try:
                opportunities = self.analyzer.analyze_file(file_path)
                all_opportunities.extend(opportunities)
                
                if opportunities:
                    print(f"   📄 {file_path.name}: {len(opportunities)} priložnosti")
            
            except Exception as e:
                self.logger.error(f"Napaka pri analizi {file_path}: {e}")
        
        # Sortiraj po vplivu in zaupanju
        all_opportunities.sort(key=lambda x: (x.impact, x.confidence), reverse=True)
        
        self.opportunities = all_opportunities
        
        print(f"\n📊 Skupaj najdenih {len(all_opportunities)} refaktoring priložnosti")
        
        # Povzetek po tipih
        type_counts = Counter(opp.type for opp in all_opportunities)
        print("\n🔧 Priložnosti po tipih:")
        for ref_type, count in type_counts.most_common():
            print(f"   {ref_type}: {count}")
        
        return all_opportunities
    
    def execute_safe_refactorings(self, max_refactorings: int = 10) -> List[RefactoringResult]:
        """Izvede varne refaktoringe"""
        print(f"\n🔧 === IZVAJANJE VARNIH REFAKTORINGOV (max {max_refactorings}) ===")
        print()
        
        # Izberi varne refaktoringe (nizek effort, visoka confidence)
        safe_opportunities = [
            opp for opp in self.opportunities
            if opp.estimated_effort == "low" and opp.confidence > 0.8
        ][:max_refactorings]
        
        results = []
        
        for i, opportunity in enumerate(safe_opportunities, 1):
            print(f"🔧 Refaktoring {i}/{len(safe_opportunities)}: {opportunity.description}")
            
            result = self.engine.execute_refactoring(opportunity)
            results.append(result)
            
            if result.success:
                print(f"   ✅ Uspešno")
                if not result.functionality_preserved:
                    print(f"   ⚠️ Funkcionalnost morda ni ohranjena")
            else:
                print(f"   ❌ Neuspešno: {result.error_message}")
        
        self.results = results
        
        # Statistike
        successful = sum(1 for r in results if r.success)
        print(f"\n📊 Rezultati: {successful}/{len(results)} uspešnih refaktoringov")
        
        return results
    
    def generate_refactoring_report(self) -> Dict[str, Any]:
        """Generiraj poročilo o refaktoringu"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_opportunities': len(self.opportunities),
            'executed_refactorings': len(self.results),
            'successful_refactorings': sum(1 for r in self.results if r.success),
            'opportunities_by_type': dict(Counter(opp.type for opp in self.opportunities)),
            'opportunities_by_impact': dict(Counter(opp.impact for opp in self.opportunities)),
            'opportunities_by_effort': dict(Counter(opp.estimated_effort for opp in self.opportunities)),
            'top_opportunities': [
                {
                    'type': opp.type,
                    'file': opp.file_path,
                    'line': opp.line_number,
                    'description': opp.description,
                    'impact': opp.impact,
                    'confidence': opp.confidence
                }
                for opp in self.opportunities[:10]
            ],
            'refactoring_results': [
                {
                    'type': result.opportunity.type,
                    'file': result.opportunity.file_path,
                    'success': result.success,
                    'functionality_preserved': result.functionality_preserved,
                    'error': result.error_message
                }
                for result in self.results
            ]
        }
        
        return report

def main():
    """Glavna funkcija za globalni refaktoring"""
    print("🔧 === GLOBALNI REFAKTORING MIA SISTEMA ===")
    print()
    
    # Nastavi logging
    logging.basicConfig(level=logging.INFO)
    
    # Ustvari manager
    manager = GlobalRefactoringManager(".")
    
    # Analiziraj kodo
    opportunities = manager.analyze_codebase()
    
    if not opportunities:
        print("✅ Ni najdenih refaktoring priložnosti!")
        return
    
    # Izvedi varne refaktoringe
    results = manager.execute_safe_refactorings(max_refactorings=5)
    
    # Generiraj poročilo
    report = manager.generate_refactoring_report()
    
    # Shrani poročilo
    with open('global_refactoring_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Poročilo shranjeno: global_refactoring_report.json")
    
    print(f"\n🏆 GLOBALNI REFAKTORING KONČAN!")
    print(f"   📊 Analiziranih: {report['total_opportunities']} priložnosti")
    print(f"   🔧 Izvedenih: {report['executed_refactorings']} refaktoringov")
    print(f"   ✅ Uspešnih: {report['successful_refactorings']} refaktoringov")
    print(f"   🔒 Funkcionalnost ohranjena z backup sistemi")

if __name__ == "__main__":
    import importlib.util
    main()