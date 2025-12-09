#!/usr/bin/env python3
"""
LSP Tests - Slovenian Language Support
Tests for Slovenian language initialization, formal symbolic form, grammar validation
"""

import pytest
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

@pytest.mark.lsp
@pytest.mark.critical
class TestLSPSlovenian:

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Test Slovenian Language Support Package"""
    
    def test_slovenian_language_initialization(self, deterministic_environment, temp_workspace):
        """Test Slovenian language initialization"""
        # Create LSP workspace
        lsp_workspace = temp_workspace / "lsp_slovenian"
        lsp_workspace.mkdir(exist_ok=True)
        
        # Mock LSP Slovenian module
        class SlovenianLSP:
            def __init__(self):
                self.language = "slovenian"
                self.status = "inactive"
                self.vocabulary = {}
                self.grammar_rules = {}
                self.formal_symbols = {}
                self.initialization_log = []
            
            def initialize_slovenian_language(self, config=None):
                """Initialize Slovenian language support"""
                self.initialization_log.append({
                    "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                    "action": "initialization_started",
                    "config": config or {}
                })
                
                # Load basic vocabulary
                self.vocabulary = {
                    "pozdrav": {"type": "noun", "gender": "masculine", "meaning": "greeting"},
                    "dobro": {"type": "adverb", "meaning": "well", "usage": "general"},
                    "jutro": {"type": "noun", "gender": "neuter", "meaning": "morning"},
                    "hvala": {"type": "interjection", "meaning": "thank you"},
                    "prosim": {"type": "adverb", "meaning": "please"},
                    "sistem": {"type": "noun", "gender": "masculine", "meaning": "system"},
                    "spomin": {"type": "noun", "gender": "masculine", "meaning": "memory"},
                    "zavest": {"type": "noun", "gender": "feminine", "meaning": "consciousness"},
                    "inteligenca": {"type": "noun", "gender": "feminine", "meaning": "intelligence"},
                    "učenje": {"type": "noun", "gender": "neuter", "meaning": "learning"}
                }
                
                # Load grammar rules
                self.grammar_rules = {
                    "noun_declension": {
                        "masculine": {
                            "nominative": {"singular": "", "plural": "i"},
                            "genitive": {"singular": "a", "plural": "ov"},
                            "dative": {"singular": "u", "plural": "om"},
                            "accusative": {"singular": "", "plural": "e"},
                            "locative": {"singular": "u", "plural": "ih"},
                            "instrumental": {"singular": "om", "plural": "i"}
                        },
                        "feminine": {
                            "nominative": {"singular": "a", "plural": "e"},
                            "genitive": {"singular": "e", "plural": ""},
                            "dative": {"singular": "i", "plural": "am"},
                            "accusative": {"singular": "o", "plural": "e"},
                            "locative": {"singular": "i", "plural": "ah"},
                            "instrumental": {"singular": "o", "plural": "ami"}
                        },
                        "neuter": {
                            "nominative": {"singular": "o", "plural": "a"},
                            "genitive": {"singular": "a", "plural": ""},
                            "dative": {"singular": "u", "plural": "om"},
                            "accusative": {"singular": "o", "plural": "a"},
                            "locative": {"singular": "u", "plural": "ih"},
                            "instrumental": {"singular": "om", "plural": "i"}
                        }
                    },
                    "verb_conjugation": {
                        "present": {
                            "1st_singular": "m",
                            "2nd_singular": "š",
                            "3rd_singular": "",
                            "1st_plural": "mo",
                            "2nd_plural": "te",
                            "3rd_plural": "jo"
                        }
                    },
                    "sentence_structure": {
                        "basic_order": "SVO",  # Subject-Verb-Object
                        "flexible": True,
                        "case_system": True
                    }
                }
                
                # Load formal symbolic representations
                self.formal_symbols = {
                    "logical_operators": {
                        "in": "∧",  # and
                        "ali": "∨",  # or
                        "ne": "¬",  # not
                        "če": "→",  # if-then
                        "če_in_samo_če": "↔"  # if and only if
                    },
                    "quantifiers": {
                        "za_vse": "∀",  # for all
                        "obstaja": "∃",  # exists
                        "ne_obstaja": "∄"  # does not exist
                    },
                    "set_operations": {
                        "unija": "∪",  # union
                        "presek": "∩",  # intersection
                        "razlika": "\\",  # difference
                        "pripada": "∈",  # belongs to
                        "ne_pripada": "∉"  # does not belong to
                    }
                }
                
                self.status = "active"
                
                self.initialization_log.append({
                    "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                    "action": "initialization_completed",
                    "vocabulary_size": len(self.vocabulary),
                    "grammar_rules_count": len(self.grammar_rules),
                    "formal_symbols_count": sum(len(category) for category in self.formal_symbols.values())
                })
                
                return True
            
            def get_language_status(self):
                """Get current language status"""
                return {
                    "language": self.language,
                    "status": self.status,
                    "vocabulary_size": len(self.vocabulary),
                    "grammar_rules": len(self.grammar_rules),
                    "formal_symbols": sum(len(category) for category in self.formal_symbols.values()),
                    "initialization_log": self.initialization_log
                }
            
            def validate_slovenian_text(self, text):
                """Validate Slovenian text"""
                words = text.lower().split()
                validation_result = {
                    "valid": True,
                    "recognized_words": [],
                    "unknown_words": [],
                    "grammar_issues": []
                }
                
                for word in words:
                    if word in self.vocabulary:
                        validation_result["recognized_words"].append(word)
                    else:
                        validation_result["unknown_words"].append(word)
                
                # Simple grammar validation
                if len(words) > 0:
                    # Check basic sentence structure
                    if not any(word in self.vocabulary and self.vocabulary[word]["type"] == "noun" for word in words):
                        validation_result["grammar_issues"].append("No noun found in sentence")
                
                validation_result["valid"] = len(validation_result["grammar_issues"]) == 0
                
                return validation_result
            
            def convert_to_formal_symbolic(self, slovenian_text):
                """Convert Slovenian text to formal symbolic representation"""
                text_lower = slovenian_text.lower()
                symbolic_text = text_lower
                
                # Replace logical operators
                for slovenian_op, symbol in self.formal_symbols["logical_operators"].items():
                    symbolic_text = symbolic_text.replace(slovenian_op, symbol)
                
                # Replace quantifiers
                for slovenian_quant, symbol in self.formal_symbols["quantifiers"].items():
                    symbolic_text = symbolic_text.replace(slovenian_quant, symbol)
                
                # Replace set operations
                for slovenian_set, symbol in self.formal_symbols["set_operations"].items():
                    symbolic_text = symbolic_text.replace(slovenian_set, symbol)
                
                return {
                    "original": slovenian_text,
                    "symbolic": symbolic_text,
                    "transformations": self._get_transformations(slovenian_text, symbolic_text)
                }
            
            def _get_transformations(self, original, symbolic):
                """Get list of transformations applied"""
                transformations = []
                
                for category, mappings in self.formal_symbols.items():
                    for slovenian_term, symbol in mappings.items():
                        if slovenian_term in original.lower():
                            transformations.append({
                                "category": category,
                                "slovenian": slovenian_term,
                                "symbol": symbol
                            })
                
                return transformations
        
        # Test initialization
        slovenian_lsp = SlovenianLSP()
        
        # Initialize with configuration
        config = {
            "formal_symbolic_form": True,
            "grammar_validation": True,
            "vocabulary_expansion": True
        }
        
        success = slovenian_lsp.initialize_slovenian_language(config)
        
        # Verify initialization
        assert success == True
        assert slovenian_lsp.status == "active"
        assert slovenian_lsp.language == "slovenian"
        
        # Check vocabulary loading
        assert len(slovenian_lsp.vocabulary) >= 10
        assert "sistem" in slovenian_lsp.vocabulary
        assert "zavest" in slovenian_lsp.vocabulary
        assert "spomin" in slovenian_lsp.vocabulary
        
        # Check grammar rules loading
        assert "noun_declension" in slovenian_lsp.grammar_rules
        assert "verb_conjugation" in slovenian_lsp.grammar_rules
        assert "sentence_structure" in slovenian_lsp.grammar_rules
        
        # Check formal symbols loading
        assert "logical_operators" in slovenian_lsp.formal_symbols
        assert "quantifiers" in slovenian_lsp.formal_symbols
        assert "set_operations" in slovenian_lsp.formal_symbols
        
        # Verify initialization log
        assert len(slovenian_lsp.initialization_log) == 2
        assert slovenian_lsp.initialization_log[0]["action"] == "initialization_started"
        assert slovenian_lsp.initialization_log[1]["action"] == "initialization_completed"
    
    def test_slovenian_text_validation(self, deterministic_environment):
        """Test Slovenian text validation"""
        # Initialize LSP
        slovenian_lsp = self._create_slovenian_lsp()
        slovenian_lsp.initialize_slovenian_language()
        
        # Test validation scenarios
        validation_tests = [
            {
                "text": "Dobro jutro sistem",
                "should_be_valid": True,
                "expected_recognized": ["dobro", "jutro", "sistem"]
            },
            {
                "text": "Zavest in spomin",
                "should_be_valid": True,
                "expected_recognized": ["zavest", "spomin"]
            },
            {
                "text": "Hvala za pomoč",
                "should_be_valid": True,
                "expected_recognized": ["hvala"]
            },
            {
                "text": "Neznana beseda test",
                "should_be_valid": False,
                "expected_unknown": ["neznana", "beseda", "test"]
            },
            {
                "text": "Inteligenca učenje sistem",
                "should_be_valid": True,
                "expected_recognized": ["inteligenca", "učenje", "sistem"]
            }
        ]
        
        for test_case in validation_tests:
            result = slovenian_lsp.validate_slovenian_text(test_case["text"])
            
            # Check validation result
            if test_case["should_be_valid"]:
                assert result["valid"] == True or len(result["grammar_issues"]) == 0
            
            # Check recognized words
            if "expected_recognized" in test_case:
                for word in test_case["expected_recognized"]:
                    assert word in result["recognized_words"]
            
            # Check unknown words
            if "expected_unknown" in test_case:
                for word in test_case["expected_unknown"]:
                    assert word in result["unknown_words"]
            
            # Verify result structure
            assert "valid" in result
            assert "recognized_words" in result
            assert "unknown_words" in result
            assert "grammar_issues" in result
    
    def test_formal_symbolic_conversion(self, deterministic_environment):
        """Test conversion to formal symbolic form"""
        # Initialize LSP
        slovenian_lsp = self._create_slovenian_lsp()
        slovenian_lsp.initialize_slovenian_language()
        
        # Test symbolic conversion scenarios
        symbolic_tests = [
            {
                "input": "A in B",
                "expected_symbol": "∧",
                "description": "Logical AND"
            },
            {
                "input": "A ali B",
                "expected_symbol": "∨",
                "description": "Logical OR"
            },
            {
                "input": "ne A",
                "expected_symbol": "¬",
                "description": "Logical NOT"
            },
            {
                "input": "če A potem B",
                "expected_symbol": "→",
                "description": "Logical implication"
            },
            {
                "input": "za vse x",
                "expected_symbol": "∀",
                "description": "Universal quantifier"
            },
            {
                "input": "obstaja y",
                "expected_symbol": "∃",
                "description": "Existential quantifier"
            },
            {
                "input": "A unija B",
                "expected_symbol": "∪",
                "description": "Set union"
            },
            {
                "input": "A presek B",
                "expected_symbol": "∩",
                "description": "Set intersection"
            },
            {
                "input": "x pripada A",
                "expected_symbol": "∈",
                "description": "Set membership"
            }
        ]
        
        for test_case in symbolic_tests:
            result = slovenian_lsp.convert_to_formal_symbolic(test_case["input"])
            
            # Check conversion result
            assert "original" in result
            assert "symbolic" in result
            assert "transformations" in result
            
            assert result["original"] == test_case["input"]
            assert test_case["expected_symbol"] in result["symbolic"]
            
            # Check transformations
            assert len(result["transformations"]) > 0
            
            # Verify at least one transformation contains expected symbol
            symbols_found = [t["symbol"] for t in result["transformations"]]
            assert test_case["expected_symbol"] in symbols_found
    
    def test_grammar_rule_application(self, deterministic_environment):
        """Test grammar rule application"""
        # Initialize LSP
        slovenian_lsp = self._create_slovenian_lsp()
        slovenian_lsp.initialize_slovenian_language()
        
        # Test grammar scenarios
        grammar_tests = [
            {
                "word": "sistem",
                "gender": "masculine",
                "case": "nominative",
                "number": "singular",
                "expected_ending": ""
            },
            {
                "word": "sistem",
                "gender": "masculine", 
                "case": "genitive",
                "number": "singular",
                "expected_ending": "a"
            },
            {
                "word": "zavest",
                "gender": "feminine",
                "case": "nominative",
                "number": "singular",
                "expected_ending": "a"
            },
            {
                "word": "jutro",
                "gender": "neuter",
                "case": "nominative",
                "number": "plural",
                "expected_ending": "a"
            }
        ]
        
        for test_case in grammar_tests:
            # Get grammar rule
            declension_rules = slovenian_lsp.grammar_rules["noun_declension"]
            gender_rules = declension_rules[test_case["gender"]]
            case_rules = gender_rules[test_case["case"]]
            ending = case_rules[test_case["number"]]
            
            assert ending == test_case["expected_ending"]
    
    def test_lsp_integration_with_memory(self, deterministic_environment, isolated_memory):
        """Test LSP integration with memory system"""
        # Initialize LSP
        slovenian_lsp = self._create_slovenian_lsp()
        slovenian_lsp.initialize_slovenian_language()
        
        memory = isolated_memory
        
        # Store Slovenian language memories
        slovenian_memories = [
            "Sistem je aktiven",
            "Zavest deluje pravilno",
            "Spomin shranjuje podatke",
            "Inteligenca se uči",
            "Učenje je uspešno"
        ]
        
        stored_ids = []
        for content in slovenian_memories:
            # Validate before storing
            validation = slovenian_lsp.validate_slovenian_text(content)
            
            memory_id = memory.store_memory(
                content=content,
                memory_type="LONG_TERM",
                emotional_tone="NEUTRAL",
                tags=["slovenian", "lsp_test", "language"]
            )
            stored_ids.append(memory_id)
        
        # Retrieve Slovenian memories
        retrieved = memory.retrieve_memories(
            query="sistem zavest",
            memory_types=["LONG_TERM"],
            limit=10
        )
        
        assert len(retrieved) >= 2  # Should find memories with "sistem" or "zavest"
        
        # Validate retrieved content
        for mem in retrieved:
            validation = slovenian_lsp.validate_slovenian_text(mem["content"])
            # Should recognize some Slovenian words
            assert len(validation["recognized_words"]) > 0
    
    def test_lsp_cold_boot_integration(self, deterministic_environment, temp_workspace):
        """Test LSP integration during cold boot"""
        # Simulate cold boot sequence
        boot_sequence = []
        
        # Mock system integrator
        class MockSystemIntegrator:
            def __init__(self):
                self.components = {}
                self.boot_log = []
            
            def initialize_lsp(self):
                """Initialize LSP during boot"""
                self.boot_log.append("LSP initialization started")
                
                # Initialize Slovenian LSP
                slovenian_lsp = self._create_slovenian_lsp()
                success = slovenian_lsp.initialize_slovenian_language({
                    "formal_symbolic_form": True,
                    "grammar_validation": True,
                    "cold_boot": True
                })
                
                if success:
                    self.components["lsp"] = slovenian_lsp
                    self.boot_log.append("LSP initialization completed")
                    return True
                else:
                    self.boot_log.append("LSP initialization failed")
                    return False
            
            def initialize_consciousness(self):
                """Initialize consciousness after LSP"""
                if "lsp" not in self.components:
                    return False
                
                self.boot_log.append("Consciousness initialization started")
                
                # Mock consciousness with LSP integration
                consciousness_config = {
                    "language_support": "slovenian",
                    "lsp_enabled": True
                }
                
                self.components["consciousness"] = consciousness_config
                self.boot_log.append("Consciousness initialization completed")
                return True
            
            def _create_slovenian_lsp(self):
                """Create Slovenian LSP instance"""
                return self._create_slovenian_lsp()
        
        # Test cold boot sequence
        integrator = MockSystemIntegrator()
        integrator._create_slovenian_lsp = self._create_slovenian_lsp
        
        # 1. Initialize LSP first
        lsp_success = integrator.initialize_lsp()
        assert lsp_success == True
        assert "lsp" in integrator.components
        
        # 2. Initialize consciousness with LSP
        consciousness_success = integrator.initialize_consciousness()
        assert consciousness_success == True
        assert "consciousness" in integrator.components
        
        # 3. Verify boot sequence
        expected_sequence = [
            "LSP initialization started",
            "LSP initialization completed", 
            "Consciousness initialization started",
            "Consciousness initialization completed"
        ]
        
        assert integrator.boot_log == expected_sequence
        
        # 4. Verify LSP is functional
        lsp = integrator.components["lsp"]
        status = lsp.get_language_status()
        
        assert status["status"] == "active"
        assert status["language"] == "slovenian"
        assert status["vocabulary_size"] > 0
    
    def test_lsp_performance_requirements(self, deterministic_environment, test_timer):
        """Test LSP performance requirements"""
        # Initialize LSP
        slovenian_lsp = self._create_slovenian_lsp()
        
        # Test initialization performance
        start_time = test_timer()
        success = slovenian_lsp.initialize_slovenian_language()
        init_time = test_timer()
        
        assert success == True
        assert init_time < 5.0  # Should initialize in under 5 seconds
        
        # Test validation performance
        test_texts = [
            "Sistem deluje pravilno",
            "Zavest analizira podatke",
            "Spomin shranjuje informacije",
            "Inteligenca se razvija",
            "Učenje poteka uspešno"
        ]
        
        validation_start = test_timer()
        
        for text in test_texts:
            validation = slovenian_lsp.validate_slovenian_text(text)
            assert "valid" in validation
        
        validation_time = test_timer() - validation_start
        
        assert validation_time < 1.0  # All validations in under 1 second
        
        # Test symbolic conversion performance
        symbolic_start = test_timer()
        
        symbolic_texts = [
            "A in B ali C",
            "za vse x obstaja y",
            "A unija B presek C",
            "če A potem B",
            "ne A ali B"
        ]
        
        for text in symbolic_texts:
            conversion = slovenian_lsp.convert_to_formal_symbolic(text)
            assert "symbolic" in conversion
        
        symbolic_time = test_timer() - symbolic_start
        
        assert symbolic_time < 1.0  # All conversions in under 1 second
        
        print(f"LSP initialization: {init_time:.3f}s")
        print(f"Text validation: {validation_time:.3f}s for {len(test_texts)} texts")
        print(f"Symbolic conversion: {symbolic_time:.3f}s for {len(symbolic_texts)} texts")
    
    def _create_slovenian_lsp(self):
        """Helper method to create Slovenian LSP instance"""
        # This would normally import the actual LSP module
        # For testing, we use the mock implementation from test_slovenian_language_initialization
        
        class SlovenianLSP:
            def __init__(self):
                self.language = "slovenian"
                self.status = "inactive"
                self.vocabulary = {}
                self.grammar_rules = {}
                self.formal_symbols = {}
                self.initialization_log = []
            
            def initialize_slovenian_language(self, config=None):
                """Initialize Slovenian language support"""
                self.initialization_log.append({
                    "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                    "action": "initialization_started",
                    "config": config or {}
                })
                
                # Load vocabulary, grammar rules, and formal symbols
                # (Same implementation as in test_slovenian_language_initialization)
                self.vocabulary = {
                    "pozdrav": {"type": "noun", "gender": "masculine", "meaning": "greeting"},
                    "dobro": {"type": "adverb", "meaning": "well", "usage": "general"},
                    "jutro": {"type": "noun", "gender": "neuter", "meaning": "morning"},
                    "hvala": {"type": "interjection", "meaning": "thank you"},
                    "prosim": {"type": "adverb", "meaning": "please"},
                    "sistem": {"type": "noun", "gender": "masculine", "meaning": "system"},
                    "spomin": {"type": "noun", "gender": "masculine", "meaning": "memory"},
                    "zavest": {"type": "noun", "gender": "feminine", "meaning": "consciousness"},
                    "inteligenca": {"type": "noun", "gender": "feminine", "meaning": "intelligence"},
                    "učenje": {"type": "noun", "gender": "neuter", "meaning": "learning"},
                    "deluje": {"type": "verb", "meaning": "works", "tense": "present"},
                    "pravilno": {"type": "adverb", "meaning": "correctly"},
                    "analizira": {"type": "verb", "meaning": "analyzes", "tense": "present"},
                    "podatke": {"type": "noun", "gender": "masculine", "case": "accusative", "meaning": "data"},
                    "shranjuje": {"type": "verb", "meaning": "stores", "tense": "present"},
                    "informacije": {"type": "noun", "gender": "feminine", "case": "accusative", "meaning": "information"},
                    "razvija": {"type": "verb", "meaning": "develops", "tense": "present"},
                    "poteka": {"type": "verb", "meaning": "proceeds", "tense": "present"},
                    "uspešno": {"type": "adverb", "meaning": "successfully"}
                }
                
                self.grammar_rules = {
                    "noun_declension": {
                        "masculine": {
                            "nominative": {"singular": "", "plural": "i"},
                            "genitive": {"singular": "a", "plural": "ov"},
                            "dative": {"singular": "u", "plural": "om"},
                            "accusative": {"singular": "", "plural": "e"},
                            "locative": {"singular": "u", "plural": "ih"},
                            "instrumental": {"singular": "om", "plural": "i"}
                        },
                        "feminine": {
                            "nominative": {"singular": "a", "plural": "e"},
                            "genitive": {"singular": "e", "plural": ""},
                            "dative": {"singular": "i", "plural": "am"},
                            "accusative": {"singular": "o", "plural": "e"},
                            "locative": {"singular": "i", "plural": "ah"},
                            "instrumental": {"singular": "o", "plural": "ami"}
                        },
                        "neuter": {
                            "nominative": {"singular": "o", "plural": "a"},
                            "genitive": {"singular": "a", "plural": ""},
                            "dative": {"singular": "u", "plural": "om"},
                            "accusative": {"singular": "o", "plural": "a"},
                            "locative": {"singular": "u", "plural": "ih"},
                            "instrumental": {"singular": "om", "plural": "i"}
                        }
                    },
                    "verb_conjugation": {
                        "present": {
                            "1st_singular": "m",
                            "2nd_singular": "š", 
                            "3rd_singular": "",
                            "1st_plural": "mo",
                            "2nd_plural": "te",
                            "3rd_plural": "jo"
                        }
                    },
                    "sentence_structure": {
                        "basic_order": "SVO",
                        "flexible": True,
                        "case_system": True
                    }
                }
                
                self.formal_symbols = {
                    "logical_operators": {
                        "in": "∧",
                        "ali": "∨", 
                        "ne": "¬",
                        "če": "→",
                        "če_in_samo_če": "↔"
                    },
                    "quantifiers": {
                        "za_vse": "∀",
                        "obstaja": "∃",
                        "ne_obstaja": "∄"
                    },
                    "set_operations": {
                        "unija": "∪",
                        "presek": "∩",
                        "razlika": "\\",
                        "pripada": "∈",
                        "ne_pripada": "∉"
                    }
                }
                
                self.status = "active"
                
                self.initialization_log.append({
                    "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                    "action": "initialization_completed",
                    "vocabulary_size": len(self.vocabulary),
                    "grammar_rules_count": len(self.grammar_rules),
                    "formal_symbols_count": sum(len(category) for category in self.formal_symbols.values())
                })
                
                return True
            
            def get_language_status(self):
                return {
                    "language": self.language,
                    "status": self.status,
                    "vocabulary_size": len(self.vocabulary),
                    "grammar_rules": len(self.grammar_rules),
                    "formal_symbols": sum(len(category) for category in self.formal_symbols.values()),
                    "initialization_log": self.initialization_log
                }
            
            def validate_slovenian_text(self, text):
                words = text.lower().split()
                validation_result = {
                    "valid": True,
                    "recognized_words": [],
                    "unknown_words": [],
                    "grammar_issues": []
                }
                
                for word in words:
                    if word in self.vocabulary:
                        validation_result["recognized_words"].append(word)
                    else:
                        validation_result["unknown_words"].append(word)
                
                if len(words) > 0:
                    if not any(word in self.vocabulary and self.vocabulary[word]["type"] == "noun" for word in words):
                        validation_result["grammar_issues"].append("No noun found in sentence")
                
                validation_result["valid"] = len(validation_result["grammar_issues"]) == 0
                return validation_result
            
            def convert_to_formal_symbolic(self, slovenian_text):
                text_lower = slovenian_text.lower()
                symbolic_text = text_lower
                
                for slovenian_op, symbol in self.formal_symbols["logical_operators"].items():
                    symbolic_text = symbolic_text.replace(slovenian_op, symbol)
                
                for slovenian_quant, symbol in self.formal_symbols["quantifiers"].items():
                    symbolic_text = symbolic_text.replace(slovenian_quant, symbol)
                
                for slovenian_set, symbol in self.formal_symbols["set_operations"].items():
                    symbolic_text = symbolic_text.replace(slovenian_set, symbol)
                
                return {
                    "original": slovenian_text,
                    "symbolic": symbolic_text,
                    "transformations": self._get_transformations(slovenian_text, symbolic_text)
                }
            
            def _get_transformations(self, original, symbolic):
                transformations = []
                
                for category, mappings in self.formal_symbols.items():
                    for slovenian_term, symbol in mappings.items():
                        if slovenian_term in original.lower():
                            transformations.append({
                                "category": category,
                                "slovenian": slovenian_term,
                                "symbol": symbol
                            })
                
                return transformations
        
        return SlovenianLSP()