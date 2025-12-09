#!/usr/bin/env python3
"""
🛡️ Input Sanitization Framework
===============================
"""

import re
import html
import json
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote, unquote

class InputSanitizer:
    """Centralizirani input sanitization sistem"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.InputSanitizer")
        
        # Nevarne vzorce
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS
            r'javascript:',                # JavaScript injection
            r'on\w+\s*=',                 # Event handlers
            r'eval\s*\(',                 # Code execution
            r'exec\s*\(',                 # Code execution
            r'\|\s*sh',                   # Shell commands
            r'&&\s*\w+',                  # Command chaining
            r';\s*rm\s+-rf',              # Dangerous commands
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.dangerous_patterns]
    
    def sanitize_string(self, input_str: str) -> str:
        """Sanitiziraj string input"""
        if not isinstance(input_str, str):
            return str(input_str)
        
        # HTML escape
        sanitized = html.escape(input_str)
        
        # Odstrani nevarne vzorce
        for pattern in self.compiled_patterns:
            sanitized = pattern.sub('', sanitized)
        
        # Omeji dolžino
        if len(sanitized) > 10000:
            sanitized = sanitized[:10000]
            self.logger.warning("Input skrajšan zaradi dolžine")
        
        return sanitized
    
    def sanitize_dict(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiziraj dictionary input"""
        if not isinstance(input_dict, dict):
            return {}
        
        sanitized = {}
        for key, value in input_dict.items():
            # Sanitiziraj ključ
            clean_key = self.sanitize_string(str(key))
            
            # Sanitiziraj vrednost
            if isinstance(value, str):
                clean_value = self.sanitize_string(value)
            elif isinstance(value, dict):
                clean_value = self.sanitize_dict(value)
            elif isinstance(value, list):
                clean_value = self.sanitize_list(value)
            else:
                clean_value = value
            
            sanitized[clean_key] = clean_value
        
        return sanitized
    
    def sanitize_list(self, input_list: List[Any]) -> List[Any]:
        """Sanitiziraj list input"""
        if not isinstance(input_list, list):
            return []
        
        sanitized = []
        for item in input_list:
            if isinstance(item, str):
                sanitized.append(self.sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(self.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(self.sanitize_list(item))
            else:
                sanitized.append(item)
        
        return sanitized
    
    def validate_input(self, input_data: Any, input_type: str = "general") -> bool:
        """Validiraj input podatke"""
        try:
            if input_type == "llm_prompt":
                return self._validate_llm_prompt(input_data)
            elif input_type == "file_path":
                return self._validate_file_path(input_data)
            elif input_type == "url":
                return self._validate_url(input_data)
            else:
                return self._validate_general_input(input_data)
                
        except Exception as e:
            self.logger.error(f"Napaka pri validaciji: {e}")
            return False
    
    def _validate_llm_prompt(self, prompt: str) -> bool:
        """Validiraj LLM prompt"""
        if not isinstance(prompt, str):
            return False
        
        if len(prompt) > 50000:  # Preveč dolg prompt
            return False
        
        # Preveri za injection napade
        injection_patterns = [
            r'ignore\s+previous\s+instructions',
            r'system\s*:\s*you\s+are',
            r'jailbreak',
            r'pretend\s+you\s+are'
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                self.logger.warning(f"Možen prompt injection: {pattern}")
                return False
        
        return True
    
    def _validate_file_path(self, file_path: str) -> bool:
        """Validiraj file path"""
        if not isinstance(file_path, str):
            return False
        
        # Prepreči directory traversal
        if '..' in file_path or file_path.startswith('/'):
            return False
        
        # Dovoli samo varne znake
        if not re.match(r'^[a-zA-Z0-9._/-]+$', file_path):
            return False
        
        return True
    
    def _validate_url(self, url: str) -> bool:
        """Validiraj URL"""
        if not isinstance(url, str):
            return False
        
        # Osnovni URL format check
        url_pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
        return bool(re.match(url_pattern, url))
    
    def _validate_general_input(self, input_data: Any) -> bool:
        """Splošna validacija"""
        # Preprosta validacija - lahko se razširi
        return True

# Globalni sanitizer instance
input_sanitizer = InputSanitizer()

def sanitize_input(data: Any) -> Any:
    """Sanitiziraj input podatke"""
    if isinstance(data, str):
        return input_sanitizer.sanitize_string(data)
    elif isinstance(data, dict):
        return input_sanitizer.sanitize_dict(data)
    elif isinstance(data, list):
        return input_sanitizer.sanitize_list(data)
    else:
        return data

def validate_input(data: Any, input_type: str = "general") -> bool:
    """Validiraj input podatke"""
    return input_sanitizer.validate_input(data, input_type)
