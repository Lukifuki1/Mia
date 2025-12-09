#!/usr/bin/env python3
"""
License Management System for MIA Enterprise AGI
"""

import json
import hashlib
import base64
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import argparse

class LicenseManager:
    def __init__(self, license_file="license.json"):
        self.license_file = Path(license_file)
        self.license_data = self.load_license()
    
    def load_license(self):
        """Load license data"""
        if self.license_file.exists():
            with open(self.license_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_license(self):
        """Save license data"""
        with open(self.license_file, 'w') as f:
            json.dump(self.license_data, f, indent=2)
    
    def generate_license_key(self, organization, features, expiry_days=365):
        """Generate enterprise license key"""
        license_id = str(uuid.uuid4())
        issue_date = datetime.now()
        expiry_date = issue_date + timedelta(days=expiry_days)
        
        license_info = {
            "license_id": license_id,
            "organization": organization,
            "issue_date": issue_date.isoformat(),
            "expiry_date": expiry_date.isoformat(),
            "features": features,
            "max_users": features.get("max_users", 100),
            "max_instances": features.get("max_instances", 10)
        }
        
        # Create signature
        license_string = json.dumps(license_info, sort_keys=True)
        signature = hashlib.sha256(license_string.encode()).hexdigest()
        
        license_key = base64.b64encode(
            json.dumps({
                "info": license_info,
                "signature": signature
            }).encode()
        ).decode()
        
        return license_key
    
    def validate_license(self, license_key):
        """Validate license key"""
        try:
            # Decode license
            license_data = json.loads(base64.b64decode(license_key).decode())
            license_info = license_data["info"]
            signature = license_data["signature"]
            
            # Verify signature
            license_string = json.dumps(license_info, sort_keys=True)
            expected_signature = hashlib.sha256(license_string.encode()).hexdigest()
            
            if signature != expected_signature:
                return False, "Invalid license signature"
            
            # Check expiry
            expiry_date = datetime.fromisoformat(license_info["expiry_date"])
            if datetime.now() > expiry_date:
                return False, "License expired"
            
            return True, license_info
            
        except Exception as e:
            return False, f"License validation error: {e}"
    
    def install_license(self, license_key):
        """Install license key"""
        valid, result = self.validate_license(license_key)
        
        if not valid:
            print(f"License installation failed: {result}")
            return False
        
        self.license_data = {
            "license_key": license_key,
            "license_info": result,
            "installation_date": datetime.now().isoformat(),
            "machine_id": self.get_machine_id()
        }
        
        self.save_license()
        print("License installed successfully")
        print(f"Organization: {result['organization']}")
        print(f"Expires: {result['expiry_date']}")
        print(f"Max Users: {result['max_users']}")
        
        return True
    
    def get_machine_id(self):
        """Get unique machine identifier"""
        try:
            import platform
            machine_info = f"{platform.node()}-{platform.machine()}-{platform.processor()}"
            return hashlib.md5(machine_info.encode()).hexdigest()
        except:
            return "unknown"
    
    def check_license_status(self):
        """Check current license status"""
        if not self.license_data:
            return False, "No license installed"
        
        license_key = self.license_data.get("license_key")
        if not license_key:
            return False, "Invalid license data"
        
        valid, result = self.validate_license(license_key)
        
        if not valid:
            return False, result
        
        # Check usage limits
        license_info = result
        current_users = self.get_current_users()
        current_instances = self.get_current_instances()
        
        if current_users > license_info.get("max_users", 100):
            return False, f"User limit exceeded ({current_users}/{license_info['max_users']})"
        
        if current_instances > license_info.get("max_instances", 10):
            return False, f"Instance limit exceeded ({current_instances}/{license_info['max_instances']})"
        
        return True, license_info
    
    def get_current_users(self):
        """Get current user count from system"""
        try:
            # Query active users from system or database
            import psutil
            return len([p for p in psutil.process_iter(['username']) if p.info['username']])
        except:
            return 1  # Fallback to single user
    
    def get_current_instances(self):
        """Get current instance count from system"""
        try:
            # Query running MIA instances
            import psutil
            mia_processes = [p for p in psutil.process_iter(['name']) 
                           if 'mia' in p.info['name'].lower()]
            return len(mia_processes) if mia_processes else 1
        except:
            return 1  # Fallback to single instance
    
    def generate_license_report(self):
        """Generate license usage report"""
        valid, result = self.check_license_status()
        
        if not valid:
            print(f"License Status: INVALID - {result}")
            return
        
        license_info = result
        expiry_date = datetime.fromisoformat(license_info["expiry_date"])
        days_remaining = (expiry_date - datetime.now()).days
        
        print("License Status Report")
        print("=" * 30)
        print(f"Status: VALID")
        print(f"Organization: {license_info['organization']}")
        print(f"License ID: {license_info['license_id']}")
        print(f"Issue Date: {license_info['issue_date']}")
        print(f"Expiry Date: {license_info['expiry_date']}")
        print(f"Days Remaining: {days_remaining}")
        print(f"Max Users: {license_info['max_users']}")
        print(f"Max Instances: {license_info['max_instances']}")
        print(f"Current Users: {self.get_current_users()}")
        print(f"Current Instances: {self.get_current_instances()}")
        
        # Feature list
        print("\nEnabled Features:")
        for feature, enabled in license_info.get("features", {}).items():
            status = "✓" if enabled else "✗"
            print(f"  {status} {feature}")

def main():
    parser = argparse.ArgumentParser(description='MIA Enterprise License Manager')
    parser.add_argument('--generate', nargs=2, metavar=('ORG', 'DAYS'), 
                       help='Generate license key for organization')
    parser.add_argument('--install', metavar='KEY', help='Install license key')
    parser.add_argument('--validate', metavar='KEY', help='Validate license key')
    parser.add_argument('--status', action='store_true', help='Check license status')
    parser.add_argument('--report', action='store_true', help='Generate license report')
    
    args = parser.parse_args()
    
    license_manager = LicenseManager()
    
    if args.generate:
        org, days = args.generate
        features = {
            "multimodal_generation": True,
            "project_management": True,
            "collaboration": True,
            "api_access": True,
            "18plus_mode": True,
            "max_users": 100,
            "max_instances": 10
        }
        
        license_key = license_manager.generate_license_key(org, features, int(days))
        print(f"Generated license key for {org}:")
        print(license_key)
        
    elif args.install:
        license_manager.install_license(args.install)
        
    elif args.validate:
        valid, result = license_manager.validate_license(args.validate)
        if valid:
            print("License is valid")
            print(f"Organization: {result['organization']}")
            print(f"Expires: {result['expiry_date']}")
        else:
            print(f"License is invalid: {result}")
            
    elif args.status:
        valid, result = license_manager.check_license_status()
        if valid:
            print("License status: VALID")
        else:
            print(f"License status: INVALID - {result}")
            
    elif args.report:
        license_manager.generate_license_report()
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
