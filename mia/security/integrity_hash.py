#!/usr/bin/env python3
"""
🔐 Integrity Hash System
=======================
"""

import hashlib
import json
import logging
import os
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class IntegrityHashSystem:

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Sistem za preverjanje integritete"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.IntegrityHash")
        self.is_active = False
        self.monitoring_thread = None
        
        # Hash database
        self.hash_database = {}
        self.hash_file = "integrity_hashes.json"
        
        # Monitoring configuration
        self.check_interval = 300  # 5 minut
        self.critical_files = [
            "mia/core/consciousness/main.py",
            "mia/core/adaptive_llm.py",
            "mia/core/memory/main.py",
            "mia/security/system_fuse.py",
            "mia/security/cognitive_guard.py"
        ]
        
        # Load existing hashes
        self._load_hash_database()
    
    def start_monitoring(self):
        """Začni integrity monitoring"""
        if self.is_active:
            return
        
        self.is_active = True
        
        # Generiraj baseline hashes
        self._generate_baseline_hashes()
        
        # Začni monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("🔐 Integrity Hash monitoring started")
    
    def stop_monitoring(self):
        """Ustavi integrity monitoring"""
        self.is_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("🔐 Integrity Hash monitoring stopped")
    
    def _monitoring_loop(self):
        """Monitoring loop"""
        while self.is_active:
            try:
                # Preveri integriteto
                violations = self._check_integrity()
                
                if violations:
                    self._handle_integrity_violations(violations)
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Integrity monitoring error: {e}")
                time.sleep(60)
    
    def _generate_baseline_hashes(self):
        """Generiraj baseline hashes"""
        try:
            self.logger.info("Generating baseline integrity hashes...")
            
            # Hash critical files
            for file_path in self.critical_files:
                full_path = Path(file_path)
                if full_path.exists():
                    file_hash = self._calculate_file_hash(full_path)
                    self.hash_database[str(full_path)] = {
                        'hash': file_hash,
                        'timestamp': self._get_build_timestamp().isoformat(),
                        'size': full_path.stat().st_size,
                        'type': 'critical'
                    }
            
            # Hash all Python files
            for py_file in Path('.').rglob('*.py'):
                if str(py_file) not in self.hash_database:
                    file_hash = self._calculate_file_hash(py_file)
                    self.hash_database[str(py_file)] = {
                        'hash': file_hash,
                        'timestamp': self._get_build_timestamp().isoformat(),
                        'size': py_file.stat().st_size,
                        'type': 'standard'
                    }
            
            # Save hash database
            self._save_hash_database()
            
            self.logger.info(f"Generated hashes for {len(self.hash_database)} files")
            
        except Exception as e:
            self.logger.error(f"Baseline hash generation error: {e}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Izračunaj hash datoteke"""
        try:
            hasher = hashlib.sha256()
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
            
        except Exception as e:
            self.logger.error(f"File hash calculation error for {file_path}: {e}")
            return ""
    
    def _check_integrity(self) -> List[Dict[str, Any]]:
        """Preveri integriteto datotek"""
        violations = []
        
        try:
            for file_path, stored_data in self.hash_database.items():
                path_obj = Path(file_path)
                
                if not path_obj.exists():
                    violations.append({
                        'type': 'file_missing',
                        'file': file_path,
                        'severity': 'critical' if stored_data['type'] == 'critical' else 'medium',
                        'description': f"File missing: {file_path}"
                    })
                    continue
                
                # Calculate current hash
                current_hash = self._calculate_file_hash(path_obj)
                stored_hash = stored_data['hash']
                
                if current_hash != stored_hash:
                    violations.append({
                        'type': 'hash_mismatch',
                        'file': file_path,
                        'severity': 'critical' if stored_data['type'] == 'critical' else 'medium',
                        'description': f"Hash mismatch in {file_path}",
                        'stored_hash': stored_hash,
                        'current_hash': current_hash
                    })
                
                # Check file size
                current_size = path_obj.stat().st_size
                stored_size = stored_data['size']
                
                if abs(current_size - stored_size) > 1000:  # 1KB tolerance
                    violations.append({
                        'type': 'size_change',
                        'file': file_path,
                        'severity': 'medium',
                        'description': f"Significant size change in {file_path}",
                        'stored_size': stored_size,
                        'current_size': current_size
                    })
            
        except Exception as e:
            self.logger.error(f"Integrity check error: {e}")
        
        return violations
    
    def _handle_integrity_violations(self, violations: List[Dict[str, Any]]):
        """Obravnavaj integrity violations"""
        try:
            critical_violations = [v for v in violations if v['severity'] == 'critical']
            
            if critical_violations:
                self.logger.critical(f"CRITICAL INTEGRITY VIOLATIONS: {len(critical_violations)}")
                
                # Trigger security response
                self._trigger_security_response(critical_violations)
            
            # Log all violations
            for violation in violations:
                if violation['severity'] == 'critical':
                    self.logger.critical(f"INTEGRITY VIOLATION: {violation['description']}")
                else:
                    self.logger.warning(f"Integrity warning: {violation['description']}")
            
            # Save violation report
            self._save_violation_report(violations)
            
        except Exception as e:
            self.logger.error(f"Violation handling error: {e}")
    
    def _trigger_security_response(self, violations: List[Dict[str, Any]]):
        """Aktiviraj varnostni odziv"""
        try:
            # Create security incident
            incident = {
                'type': 'integrity_violation',
                'timestamp': self._get_build_timestamp().isoformat(),
                'violations': violations,
                'severity': 'critical',
                'response_actions': []
            }
            
            # Quarantine affected files
            for violation in violations:
                if violation['type'] in ['hash_mismatch', 'size_change']:
                    self._quarantine_file(violation['file'])
                    incident['response_actions'].append(f"Quarantined {violation['file']}")
            
            # Alert administrators
            self._send_security_alert(incident)
            
            # Log incident
            incident_file = f"security_incident_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}.json"
            with open(incident_file, 'w') as f:
                json.dump(incident, f, indent=2)
            
            self.logger.critical(f"Security incident created: {incident_file}")
            
        except Exception as e:
            self.logger.error(f"Security response error: {e}")
    
    def _quarantine_file(self, file_path: str):
        """Postavi datoteko v karanteno"""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                return
            
            # Create quarantine directory
            quarantine_dir = Path("quarantine")
            quarantine_dir.mkdir(exist_ok=True)
            
            # Move file to quarantine
            quarantine_path = quarantine_dir / f"{source_path.name}_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}"
            source_path.rename(quarantine_path)
            
            self.logger.warning(f"File quarantined: {file_path} -> {quarantine_path}")
            
        except Exception as e:
            self.logger.error(f"File quarantine error: {e}")
    
    def _send_security_alert(self, incident: Dict[str, Any]):
        """Pošlji varnostno opozorilo"""
        try:
            # V produkciji bi poslal email/SMS/Slack notification
            alert_message = f"""
SECURITY ALERT: Integrity Violation Detected

Incident Type: {incident['type']}
Timestamp: {incident['timestamp']}
Severity: {incident['severity']}
Violations: {len(incident['violations'])}

Response Actions:
{chr(10).join(incident['response_actions'])}

Please investigate immediately.
"""
            
            self.logger.critical(alert_message)
            
            # Save alert to file
            alert_file = f"security_alert_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}.txt"
            with open(alert_file, 'w') as f:
                f.write(alert_message)
            
        except Exception as e:
            self.logger.error(f"Security alert error: {e}")
    
    def _save_violation_report(self, violations: List[Dict[str, Any]]):
        """Shrani violation report"""
        try:
            report = {
                'timestamp': self._get_build_timestamp().isoformat(),
                'violations': violations,
                'total_violations': len(violations),
                'critical_violations': len([v for v in violations if v['severity'] == 'critical'])
            }
            
            report_file = f"integrity_violations_{int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Violation report saved: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Violation report save error: {e}")
    
    def _load_hash_database(self):
        """Naloži hash database"""
        try:
            if os.path.exists(self.hash_file):
                with open(self.hash_file, 'r') as f:
                    self.hash_database = json.load(f)
                
                self.logger.info(f"Loaded {len(self.hash_database)} hashes from database")
            
        except Exception as e:
            self.logger.error(f"Hash database load error: {e}")
            self.hash_database = {}
    
    def _save_hash_database(self):
        """Shrani hash database"""
        try:
            with open(self.hash_file, 'w') as f:
                json.dump(self.hash_database, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Hash database save error: {e}")
    
    def update_file_hash(self, file_path: str):
        """Posodobi hash datoteke"""
        try:
            path_obj = Path(file_path)
            if path_obj.exists():
                file_hash = self._calculate_file_hash(path_obj)
                self.hash_database[file_path] = {
                    'hash': file_hash,
                    'timestamp': self._get_build_timestamp().isoformat(),
                    'size': path_obj.stat().st_size,
                    'type': 'updated'
                }
                
                self._save_hash_database()
                self.logger.info(f"Hash updated for {file_path}")
            
        except Exception as e:
            self.logger.error(f"Hash update error: {e}")
    
    def get_integrity_status(self) -> Dict[str, Any]:
        """Pridobi integrity status"""
        try:
            violations = self._check_integrity()
            
            return {
                'monitoring_active': self.is_active,
                'total_files': len(self.hash_database),
                'critical_files': len([f for f in self.hash_database.values() if f['type'] == 'critical']),
                'violations': len(violations),
                'critical_violations': len([v for v in violations if v['severity'] == 'critical']),
                'last_check': self._get_build_timestamp().isoformat(),
                'status': 'SECURE' if not violations else 'VIOLATIONS_DETECTED'
            }
            
        except Exception as e:
            self.logger.error(f"Integrity status error: {e}")
            return {'status': 'ERROR', 'error': str(e)}

# Globalni integrity hash system
integrity_hash_system = IntegrityHashSystem()
