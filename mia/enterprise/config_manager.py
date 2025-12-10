#!/usr/bin/env python3
"""
MIA Enterprise Configuration Manager
Centralized configuration management with environment-specific settings
"""

import os
import json
import logging
import yaml
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import threading

class ConfigEnvironment(Enum):
    """Configuration environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class ConfigFormat(Enum):
    """Configuration file formats"""
    JSON = "json"
    YAML = "yaml"
    ENV = "env"

@dataclass
class ConfigSchema:
    """Configuration schema definition"""
    key: str
    data_type: type
    default_value: Any
    required: bool = False
    description: str = ""
    validation_rules: Dict[str, Any] = None

class ConfigurationManager:
    """Enterprise configuration management system"""
    
    def __init__(self, config_dir: str = "config", environment: str = None):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine environment
        self.environment = ConfigEnvironment(
            environment or os.getenv("MIA_ENVIRONMENT", "development")
        )
        
        self.logger = logging.getLogger("MIA.Enterprise.Config")
        
        # Configuration state
        self.config: Dict[str, Any] = {}
        self.schema: Dict[str, ConfigSchema] = {}
        self.config_lock = threading.RLock()
        
        # Load configuration
        self._load_configuration()
        
        self.logger.info(f"🔧 Configuration manager initialized for {self.environment.value}")
    
    def _load_configuration(self):
        """Load configuration from files"""
        try:
            with self.config_lock:
                # Load base configuration
                base_config = self._load_config_file("base")
                
                # Load environment-specific configuration
                env_config = self._load_config_file(self.environment.value)
                
                # Merge configurations (environment overrides base)
                self.config = {**base_config, **env_config}
                
                # Load from environment variables
                self._load_from_environment()
                
                # Apply default values from schema
                self._apply_schema_defaults()
                
                # Validate configuration
                self._validate_configuration()
                
                self.logger.info(f"✅ Configuration loaded: {len(self.config)} settings")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to load configuration: {e}")
            self._load_default_configuration()
    
    def _load_config_file(self, name: str) -> Dict[str, Any]:
        """Load configuration from file"""
        config = {}
        
        # Try different formats
        for format_enum in ConfigFormat:
            file_path = self.config_dir / f"{name}.{format_enum.value}"
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        if format_enum == ConfigFormat.JSON:
                            config = json.load(f)
                        elif format_enum == ConfigFormat.YAML:
                            config = yaml.safe_load(f) or {}
                        elif format_enum == ConfigFormat.ENV:
                            config = self._parse_env_file(f)
                    
                    self.logger.info(f"📄 Loaded config from {file_path}")
                    break
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to load {file_path}: {e}")
        
        return config
    
    def _parse_env_file(self, file_handle) -> Dict[str, Any]:
        """Parse .env file format"""
        config = {}
        
        for line in file_handle:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    
                    # Convert to appropriate type
                    config[key] = self._convert_value(value)
        
        return config
    
    def _convert_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert string value to appropriate type"""
        # Boolean values
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # String value
        return value
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        env_prefix = "MIA_"
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower().replace('_', '.')
                self.config[config_key] = self._convert_value(value)
    
    def _apply_schema_defaults(self):
        """Apply default values from schema"""
        for key, schema in self.schema.items():
            if key not in self.config and schema.default_value is not None:
                self.config[key] = schema.default_value
    
    def _validate_configuration(self):
        """Validate configuration against schema"""
        errors = []
        
        for key, schema in self.schema.items():
            if schema.required and key not in self.config:
                errors.append(f"Required configuration '{key}' is missing")
                continue
            
            if key in self.config:
                value = self.config[key]
                
                # Type validation
                if not isinstance(value, schema.data_type):
                    try:
                        self.config[key] = schema.data_type(value)
                    except (ValueError, TypeError):
                        errors.append(f"Configuration '{key}' must be of type {schema.data_type.__name__}")
                
                # Custom validation rules
                if schema.validation_rules:
                    validation_errors = self._validate_rules(key, value, schema.validation_rules)
                    errors.extend(validation_errors)
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            self.logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _validate_rules(self, key: str, value: Any, rules: Dict[str, Any]) -> List[str]:
        """Validate value against custom rules"""
        errors = []
        
        # Min/max validation for numbers
        if isinstance(value, (int, float)):
            if 'min' in rules and value < rules['min']:
                errors.append(f"Configuration '{key}' must be >= {rules['min']}")
            if 'max' in rules and value > rules['max']:
                errors.append(f"Configuration '{key}' must be <= {rules['max']}")
        
        # Length validation for strings
        if isinstance(value, str):
            if 'min_length' in rules and len(value) < rules['min_length']:
                errors.append(f"Configuration '{key}' must be at least {rules['min_length']} characters")
            if 'max_length' in rules and len(value) > rules['max_length']:
                errors.append(f"Configuration '{key}' must be at most {rules['max_length']} characters")
        
        # Allowed values validation
        if 'allowed_values' in rules and value not in rules['allowed_values']:
            errors.append(f"Configuration '{key}' must be one of: {rules['allowed_values']}")
        
        return errors
    
    def _load_default_configuration(self):
        """Load default configuration as fallback"""
        self.config = {
            # Core settings
            "core.debug": self.environment == ConfigEnvironment.DEVELOPMENT,
            "core.log_level": "INFO",
            "core.data_dir": "mia_data",
            
            # Server settings
            "server.host": "0.0.0.0",
            "server.port": 12000,
            "server.workers": 1,
            
            # AI settings
            "ai.model": "llama3.2:1b",
            "ai.temperature": 0.7,
            "ai.max_tokens": 1024,
            "ai.timeout": 60,
            
            # Security settings
            "security.enabled": True,
            "security.session_timeout": 3600,
            "security.max_login_attempts": 5,
            
            # Learning settings
            "learning.enabled": True,
            "learning.auto_save": True,
            "learning.max_conversations": 10000,
            
            # Monitoring settings
            "monitoring.enabled": True,
            "monitoring.metrics_retention_hours": 24,
            "monitoring.alerts_enabled": True
        }
        
        self.logger.warning("⚠️ Using default configuration")
    
    def define_schema(self, schemas: List[ConfigSchema]):
        """Define configuration schema"""
        for schema in schemas:
            self.schema[schema.key] = schema
        
        self.logger.info(f"📋 Configuration schema defined: {len(schemas)} items")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        with self.config_lock:
            return self.config.get(key, default)
    
    def set(self, key: str, value: Any, persist: bool = False) -> bool:
        """Set configuration value"""
        try:
            with self.config_lock:
                # Validate against schema if defined
                if key in self.schema:
                    schema = self.schema[key]
                    
                    # Type validation
                    if not isinstance(value, schema.data_type):
                        value = schema.data_type(value)
                    
                    # Custom validation
                    if schema.validation_rules:
                        errors = self._validate_rules(key, value, schema.validation_rules)
                        if errors:
                            raise ValueError(f"Validation failed: {'; '.join(errors)}")
                
                self.config[key] = value
                
                if persist:
                    self._save_configuration()
                
                self.logger.info(f"🔧 Configuration updated: {key} = {value}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Failed to set configuration {key}: {e}")
            return False
    
    def _save_configuration(self):
        """Save current configuration to file"""
        try:
            config_file = self.config_dir / f"{self.environment.value}.json"
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Configuration saved to {config_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save configuration: {e}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        with self.config_lock:
            return self.config.copy()
    
    def get_by_prefix(self, prefix: str) -> Dict[str, Any]:
        """Get all configuration values with specified prefix"""
        with self.config_lock:
            return {k: v for k, v in self.config.items() if k.startswith(prefix)}
    
    def reload(self):
        """Reload configuration from files"""
        self.logger.info("🔄 Reloading configuration...")
        self._load_configuration()
    
    def export_config(self, format_type: ConfigFormat = ConfigFormat.JSON) -> str:
        """Export configuration in specified format"""
        with self.config_lock:
            if format_type == ConfigFormat.JSON:
                return json.dumps(self.config, indent=2, ensure_ascii=False)
            elif format_type == ConfigFormat.YAML:
                return yaml.dump(self.config, default_flow_style=False, allow_unicode=True)
            elif format_type == ConfigFormat.ENV:
                lines = []
                for key, value in self.config.items():
                    env_key = f"MIA_{key.upper().replace('.', '_')}"
                    lines.append(f"{env_key}={value}")
                return "\n".join(lines)
    
    def get_environment(self) -> ConfigEnvironment:
        """Get current environment"""
        return self.environment
    
    def get_schema_info(self) -> Dict[str, Dict[str, Any]]:
        """Get schema information"""
        return {key: asdict(schema) for key, schema in self.schema.items()}

# Initialize default schema
DEFAULT_SCHEMA = [
    ConfigSchema("core.debug", bool, False, description="Enable debug mode"),
    ConfigSchema("core.log_level", str, "INFO", description="Logging level", 
                validation_rules={"allowed_values": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]}),
    ConfigSchema("core.data_dir", str, "mia_data", required=True, description="Data directory path"),
    
    ConfigSchema("server.host", str, "0.0.0.0", required=True, description="Server host"),
    ConfigSchema("server.port", int, 12000, required=True, description="Server port",
                validation_rules={"min": 1024, "max": 65535}),
    ConfigSchema("server.workers", int, 1, description="Number of worker processes",
                validation_rules={"min": 1, "max": 16}),
    
    ConfigSchema("ai.model", str, "llama3.2:1b", description="AI model name"),
    ConfigSchema("ai.temperature", float, 0.7, description="AI temperature",
                validation_rules={"min": 0.0, "max": 2.0}),
    ConfigSchema("ai.max_tokens", int, 1024, description="Maximum tokens",
                validation_rules={"min": 1, "max": 8192}),
    ConfigSchema("ai.timeout", int, 60, description="AI request timeout in seconds",
                validation_rules={"min": 1, "max": 300}),
    
    ConfigSchema("security.enabled", bool, True, description="Enable security features"),
    ConfigSchema("security.session_timeout", int, 3600, description="Session timeout in seconds",
                validation_rules={"min": 300, "max": 86400}),
    ConfigSchema("security.max_login_attempts", int, 5, description="Maximum login attempts",
                validation_rules={"min": 1, "max": 20}),
    
    ConfigSchema("learning.enabled", bool, True, description="Enable learning system"),
    ConfigSchema("learning.auto_save", bool, True, description="Auto-save learning data"),
    ConfigSchema("learning.max_conversations", int, 10000, description="Maximum conversations to store",
                validation_rules={"min": 100, "max": 100000}),
    
    ConfigSchema("monitoring.enabled", bool, True, description="Enable monitoring"),
    ConfigSchema("monitoring.metrics_retention_hours", int, 24, description="Metrics retention period",
                validation_rules={"min": 1, "max": 168}),
    ConfigSchema("monitoring.alerts_enabled", bool, True, description="Enable alerts")
]

# Global configuration manager
config_manager = ConfigurationManager()
config_manager.define_schema(DEFAULT_SCHEMA)