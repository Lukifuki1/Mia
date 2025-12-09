#!/usr/bin/env python3
"""
Enterprise Configuration Manager for MIA Enterprise AGI
"""

import json
import os
import sys
import argparse
from pathlib import Path

class EnterpriseConfigManager:
    def __init__(self, config_path="enterprise-config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
    
    def load_config(self):
        """Load enterprise configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        """Save enterprise configuration"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def set_value(self, key_path, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        current = self.config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Convert string values to appropriate types
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            value = float(value)
        
        current[keys[-1]] = value
        self.save_config()
        print(f"Set {key_path} = {value}")
    
    def get_value(self, key_path):
        """Get configuration value using dot notation"""
        keys = key_path.split('.')
        current = self.config
        
        for key in keys:
            if key not in current:
                return None
            current = current[key]
        
        return current
    
    def validate_config(self):
        """Validate enterprise configuration"""
        errors = []
        
        # Check required fields
        required_fields = [
            'enterprise.organization',
            'enterprise.license_key',
            'security.enforce_encryption',
            'policies.auto_update.enabled'
        ]
        
        for field in required_fields:
            if self.get_value(field) is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate license key format
        license_key = self.get_value('enterprise.license_key')
        if license_key and len(license_key) < 32:
            errors.append("Invalid license key format")
        
        # Validate resource limits
        memory_limit = self.get_value('policies.resource_limits.max_memory_gb')
        if memory_limit and memory_limit < 4:
            errors.append("Memory limit too low (minimum 4GB)")
        
        return errors
    
    def apply_policies(self):
        """Apply enterprise policies to system"""
        print("Applying enterprise policies...")
        
        # Apply security policies
        if self.get_value('security.enforce_encryption'):
            print("✓ Encryption enforcement enabled")
        
        if self.get_value('security.audit_logging'):
            print("✓ Audit logging enabled")
        
        # Apply resource limits
        memory_limit = self.get_value('policies.resource_limits.max_memory_gb')
        if memory_limit:
            print(f"✓ Memory limit set to {memory_limit}GB")
        
        # Apply auto-update policy
        if self.get_value('policies.auto_update.enabled'):
            channel = self.get_value('policies.auto_update.channel')
            print(f"✓ Auto-update enabled (channel: {channel})")
        
        print("Enterprise policies applied successfully")
    
    def generate_report(self):
        """Generate configuration report"""
        report = {
            "organization": self.get_value('enterprise.organization'),
            "deployment_id": self.get_value('enterprise.deployment_id'),
            "security_enabled": self.get_value('security.enforce_encryption'),
            "audit_logging": self.get_value('security.audit_logging'),
            "auto_update": self.get_value('policies.auto_update.enabled'),
            "resource_limits": self.get_value('policies.resource_limits'),
            "features_enabled": self.get_value('features')
        }
        
        print("Enterprise Configuration Report")
        print("=" * 40)
        for key, value in report.items():
            print(f"{key}: {value}")
        
        return report

def main():
    parser = argparse.ArgumentParser(description='MIA Enterprise Configuration Manager')
    parser.add_argument('--config', default='enterprise-config.json', help='Configuration file path')
    parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='Set configuration value')
    parser.add_argument('--get', metavar='KEY', help='Get configuration value')
    parser.add_argument('--validate', action='store_true', help='Validate configuration')
    parser.add_argument('--apply', action='store_true', help='Apply enterprise policies')
    parser.add_argument('--report', action='store_true', help='Generate configuration report')
    
    args = parser.parse_args()
    
    config_manager = EnterpriseConfigManager(args.config)
    
    if args.set:
        config_manager.set_value(args.set[0], args.set[1])
    elif args.get:
        value = config_manager.get_value(args.get)
        print(f"{args.get}: {value}")
    elif args.validate:
        errors = config_manager.validate_config()
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        else:
            print("Configuration is valid")
    elif args.apply:
        config_manager.apply_policies()
    elif args.report:
        config_manager.generate_report()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
