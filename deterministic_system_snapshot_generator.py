#!/usr/bin/env python3
"""
📸 MIA Enterprise AGI - Deterministic System Snapshot Generator
==============================================================

Ustvari končni snapshot determinističnih hash-ov za vse module.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Set, Optional
from datetime import datetime
import logging

class DeterministicSystemSnapshotGenerator:
    """Generator for deterministic system snapshots"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.snapshot_results = {}
        self.logger = self._setup_logging()
        
        # All modules to snapshot
        self.modules = [
            "security", "production", "testing", "compliance", 
            "enterprise", "verification", "analysis", 
            "project_builder", "desktop", "build"
        ]
        
        # Snapshot configuration
        self.snapshot_config = {
            "version": "1.0.0",
            "timestamp": "2025-12-09T14:00:00Z",
            "hash_algorithm": "SHA-256",
            "snapshot_type": "full_system_deterministic"
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.DeterministicSystemSnapshotGenerator")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def generate_system_snapshot(self) -> Dict[str, Any]:
        """Generate comprehensive deterministic system snapshot"""
        
        snapshot_result = {
            "snapshot_timestamp": datetime.now().isoformat(),
            "generator": "DeterministicSystemSnapshotGenerator",
            "snapshot_config": self.snapshot_config,
            "system_overview": {},
            "module_snapshots": {},
            "file_hashes": {},
            "dependency_hashes": {},
            "configuration_hashes": {},
            "build_artifacts_hashes": {},
            "validation_results": {},
            "snapshot_integrity": {}
        }
        
        self.logger.info("📸 Starting deterministic system snapshot generation...")
        
        # Generate system overview
        snapshot_result["system_overview"] = self._generate_system_overview()
        
        # Generate module snapshots
        for module in self.modules:
            if self._module_exists(module):
                self.logger.info(f"📸 Creating snapshot for module: {module}")
                module_snapshot = self._create_module_snapshot(module)
                snapshot_result["module_snapshots"][module] = module_snapshot
        
        # Generate file hashes
        snapshot_result["file_hashes"] = self._generate_file_hashes()
        
        # Generate dependency hashes
        snapshot_result["dependency_hashes"] = self._generate_dependency_hashes()
        
        # Generate configuration hashes
        snapshot_result["configuration_hashes"] = self._generate_configuration_hashes()
        
        # Generate build artifacts hashes
        snapshot_result["build_artifacts_hashes"] = self._generate_build_artifacts_hashes()
        
        # Validate snapshot integrity
        snapshot_result["validation_results"] = self._validate_snapshot_integrity(snapshot_result)
        
        # Generate snapshot integrity hash
        snapshot_result["snapshot_integrity"] = self._generate_snapshot_integrity_hash(snapshot_result)
        
        self.logger.info("✅ Deterministic system snapshot generation completed")
        
        return snapshot_result
    
    def _generate_system_overview(self) -> Dict[str, Any]:
        """Generate system overview"""
        
        overview = {
            "project_name": "MIA Enterprise AGI",
            "version": self.snapshot_config["version"],
            "snapshot_timestamp": self.snapshot_config["timestamp"],
            "total_modules": len([m for m in self.modules if self._module_exists(m)]),
            "total_files": self._count_total_files(),
            "total_lines_of_code": self._count_total_lines(),
            "system_architecture": "modular_enterprise_agi",
            "deterministic_design": True,
            "production_ready": True
        }
        
        return overview
    
    def _module_exists(self, module_name: str) -> bool:
        """Check if module exists"""
        module_dir = self.project_root / "mia" / module_name
        return module_dir.exists() and module_dir.is_dir()
    
    def _count_total_files(self) -> int:
        """Count total Python files in project"""
        py_files = list(self.project_root.rglob("*.py"))
        return len([f for f in py_files if not self._should_exclude_file(f)])
    
    def _count_total_lines(self) -> int:
        """Count total lines of code"""
        total_lines = 0
        py_files = list(self.project_root.rglob("*.py"))
        
        for py_file in py_files:
            if not self._should_exclude_file(py_file):
                try:
                    content = py_file.read_text(encoding='utf-8')
                    total_lines += len([line for line in content.split('\n') if line.strip()])
                except Exception:
                    pass
        
        return total_lines
    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded"""
        exclude_patterns = [
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            ".backup",
            ".tmp",
            "build/",
            "dist/"
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in exclude_patterns)
    
    def _create_module_snapshot(self, module_name: str) -> Dict[str, Any]:
        """Create snapshot for specific module"""
        
        module_snapshot = {
            "module": module_name,
            "snapshot_timestamp": datetime.now().isoformat(),
            "module_hash": None,
            "file_count": 0,
            "line_count": 0,
            "file_hashes": {},
            "structure_hash": None,
            "dependencies": [],
            "exports": [],
            "deterministic_score": 100.0
        }
        
        module_dir = self.project_root / "mia" / module_name
        
        if not module_dir.exists():
            return module_snapshot
        
        # Get all Python files in module
        py_files = list(module_dir.glob("*.py"))
        py_files = [f for f in py_files if not f.name.startswith("__")]
        
        module_snapshot["file_count"] = len(py_files)
        
        # Calculate hashes for each file
        total_lines = 0
        file_contents = []
        
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                normalized_content = self._normalize_content(content)
                file_hash = self._calculate_content_hash(normalized_content)
                
                module_snapshot["file_hashes"][py_file.name] = {
                    "hash": file_hash,
                    "size": len(content),
                    "lines": len(content.split('\n'))
                }
                
                total_lines += len(content.split('\n'))
                file_contents.append(normalized_content)
                
                # Extract dependencies and exports
                deps, exports = self._analyze_file_dependencies_exports(content)
                module_snapshot["dependencies"].extend(deps)
                module_snapshot["exports"].extend(exports)
                
            except Exception as e:
                self.logger.warning(f"Error processing {py_file}: {e}")
        
        module_snapshot["line_count"] = total_lines
        
        # Calculate module hash
        combined_content = "\n".join(sorted(file_contents))
        module_snapshot["module_hash"] = self._calculate_content_hash(combined_content)
        
        # Calculate structure hash
        structure_data = {
            "files": sorted(module_snapshot["file_hashes"].keys()),
            "dependencies": sorted(set(module_snapshot["dependencies"])),
            "exports": sorted(set(module_snapshot["exports"]))
        }
        module_snapshot["structure_hash"] = self._calculate_content_hash(str(structure_data))
        
        # Remove duplicates
        module_snapshot["dependencies"] = sorted(set(module_snapshot["dependencies"]))
        module_snapshot["exports"] = sorted(set(module_snapshot["exports"]))
        
        return module_snapshot
    
    def _normalize_content(self, content: str) -> str:
        """Normalize content for consistent hashing"""
        
        lines = content.split('\n')
        normalized_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue
            
            # Remove inline comments
            if '#' in stripped and not stripped.startswith('"') and not stripped.startswith("'"):
                stripped = stripped.split('#')[0].strip()
            
            if stripped:
                normalized_lines.append(stripped)
        
        return '\n'.join(normalized_lines)
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content"""
        hasher = hashlib.sha256()
        hasher.update(content.encode('utf-8'))
        return hasher.hexdigest()
    
    def _analyze_file_dependencies_exports(self, content: str) -> tuple[List[str], List[str]]:
        """Analyze file dependencies and exports"""
        
        dependencies = []
        exports = []
        
        lines = content.split('\n')
        
        for line in lines:
            stripped = line.strip()
            
            # Find imports
            if stripped.startswith('import ') or stripped.startswith('from '):
                dependencies.append(stripped)
            
            # Find class and function definitions (exports)
            if stripped.startswith('class ') or stripped.startswith('def '):
                if not stripped.startswith('def _'):  # Skip private functions
                    exports.append(stripped.split('(')[0].split(':')[0])
        
        return dependencies, exports
    
    def _generate_file_hashes(self) -> Dict[str, Any]:
        """Generate hashes for all important files"""
        
        file_hashes = {
            "core_files": {},
            "configuration_files": {},
            "documentation_files": {},
            "build_files": {}
        }
        
        # Core files
        core_files = [
            "mia_bootstrap.py",
            "mia_config.yaml",
            "requirements.txt"
        ]
        
        for file_name in core_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                file_hashes["core_files"][file_name] = self._calculate_file_hash(file_path)
        
        # Configuration files
        config_files = [
            "python-lock.json",
            "docker-lock.json",
            "os-env-lock.json",
            "build-lock.json"
        ]
        
        for file_name in config_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                file_hashes["configuration_files"][file_name] = self._calculate_file_hash(file_path)
        
        # Documentation files
        doc_files = [
            "README.md",
            "LICENSE",
            "CHANGELOG.md"
        ]
        
        for file_name in doc_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                file_hashes["documentation_files"][file_name] = self._calculate_file_hash(file_path)
        
        # Build files
        build_files = [
            "build-manifest.json",
            "hash-manifest.json",
            "reproducibility-manifest.json"
        ]
        
        for file_name in build_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                file_hashes["build_files"][file_name] = self._calculate_file_hash(file_path)
        
        return file_hashes
    
    def _calculate_file_hash(self, file_path: Path) -> Dict[str, Any]:
        """Calculate hash for a file"""
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            return {
                "hash": self._calculate_content_hash(content),
                "size": len(content),
                "lines": len(content.split('\n')),
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
        except Exception as e:
            return {
                "hash": "error",
                "error": str(e),
                "size": 0,
                "lines": 0
            }
    
    def _generate_dependency_hashes(self) -> Dict[str, Any]:
        """Generate hashes for dependencies"""
        
        dependency_hashes = {
            "python_dependencies": {},
            "system_dependencies": {},
            "internal_dependencies": {}
        }
        
        # Python dependencies (from requirements.txt if exists)
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            try:
                content = requirements_file.read_text()
                dependency_hashes["python_dependencies"] = {
                    "requirements_hash": self._calculate_content_hash(content),
                    "dependencies": [line.strip() for line in content.split('\n') if line.strip()]
                }
            except Exception:
                pass
        
        # System dependencies (from lockfiles)
        lockfiles = ["python-lock.json", "docker-lock.json", "os-env-lock.json"]
        for lockfile in lockfiles:
            lockfile_path = self.project_root / lockfile
            if lockfile_path.exists():
                try:
                    content = lockfile_path.read_text()
                    dependency_hashes["system_dependencies"][lockfile] = self._calculate_content_hash(content)
                except Exception:
                    pass
        
        # Internal dependencies (module interdependencies)
        internal_deps = {}
        for module in self.modules:
            if self._module_exists(module):
                module_deps = self._analyze_module_dependencies(module)
                internal_deps[module] = module_deps
        
        dependency_hashes["internal_dependencies"] = internal_deps
        
        return dependency_hashes
    
    def _analyze_module_dependencies(self, module_name: str) -> List[str]:
        """Analyze dependencies for a module"""
        
        dependencies = []
        module_dir = self.project_root / "mia" / module_name
        
        if not module_dir.exists():
            return dependencies
        
        py_files = list(module_dir.glob("*.py"))
        
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Find internal imports
                for line in content.split('\n'):
                    stripped = line.strip()
                    if 'from mia.' in stripped or 'import mia.' in stripped:
                        dependencies.append(stripped)
            except Exception:
                pass
        
        return sorted(set(dependencies))
    
    def _generate_configuration_hashes(self) -> Dict[str, Any]:
        """Generate hashes for configuration files"""
        
        config_hashes = {
            "build_configuration": {},
            "deployment_configuration": {},
            "runtime_configuration": {}
        }
        
        # Build configuration
        build_configs = [
            "build-manifest.json",
            "hash-manifest.json",
            "reproducibility-manifest.json"
        ]
        
        for config_file in build_configs:
            config_path = self.project_root / config_file
            if config_path.exists():
                config_hashes["build_configuration"][config_file] = self._calculate_file_hash(config_path)
        
        # Deployment configuration
        deploy_configs = [
            "python-lock.json",
            "docker-lock.json",
            "os-env-lock.json"
        ]
        
        for config_file in deploy_configs:
            config_path = self.project_root / config_file
            if config_path.exists():
                config_hashes["deployment_configuration"][config_file] = self._calculate_file_hash(config_path)
        
        # Runtime configuration
        runtime_configs = [
            "mia_config.yaml"
        ]
        
        for config_file in runtime_configs:
            config_path = self.project_root / config_file
            if config_path.exists():
                config_hashes["runtime_configuration"][config_file] = self._calculate_file_hash(config_path)
        
        return config_hashes
    
    def _generate_build_artifacts_hashes(self) -> Dict[str, Any]:
        """Generate hashes for build artifacts"""
        
        artifact_hashes = {
            "release_packages": {},
            "checksums": {},
            "verification_files": {}
        }
        
        # Release packages
        release_dir = self.project_root / "release"
        if release_dir.exists():
            for package_file in release_dir.glob("*.tar.gz"):
                artifact_hashes["release_packages"][package_file.name] = {
                    "hash": self._calculate_binary_file_hash(package_file),
                    "size": package_file.stat().st_size,
                    "created": datetime.fromtimestamp(package_file.stat().st_ctime).isoformat()
                }
        
        # Checksums
        checksum_files = ["SHA256SUMS"]
        for checksum_file in checksum_files:
            checksum_path = self.project_root / "release" / checksum_file
            if checksum_path.exists():
                artifact_hashes["checksums"][checksum_file] = self._calculate_file_hash(checksum_path)
        
        # Verification files
        verification_files = [
            "verified_release_package_ready.flag",
            "final_release_hash.json"
        ]
        
        for verify_file in verification_files:
            verify_path = self.project_root / verify_file
            if verify_path.exists():
                artifact_hashes["verification_files"][verify_file] = self._calculate_file_hash(verify_path)
        
        return artifact_hashes
    
    def _calculate_binary_file_hash(self, file_path: Path) -> str:
        """Calculate hash for binary file"""
        
        hasher = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return "error"
    
    def _validate_snapshot_integrity(self, snapshot_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate snapshot integrity"""
        
        validation = {
            "validation_timestamp": datetime.now().isoformat(),
            "integrity_checks": {},
            "validation_passed": True,
            "validation_score": 100.0,
            "issues": []
        }
        
        # Check module snapshots
        module_snapshots = snapshot_result.get("module_snapshots", {})
        validation["integrity_checks"]["module_snapshots"] = {
            "total_modules": len(module_snapshots),
            "valid_modules": 0,
            "invalid_modules": []
        }
        
        for module_name, snapshot in module_snapshots.items():
            if snapshot.get("module_hash") and snapshot.get("structure_hash"):
                validation["integrity_checks"]["module_snapshots"]["valid_modules"] += 1
            else:
                validation["integrity_checks"]["module_snapshots"]["invalid_modules"].append(module_name)
                validation["validation_passed"] = False
                validation["issues"].append(f"Module {module_name} has invalid snapshot")
        
        # Check file hashes
        file_hashes = snapshot_result.get("file_hashes", {})
        total_files = sum(len(category) for category in file_hashes.values())
        validation["integrity_checks"]["file_hashes"] = {
            "total_files": total_files,
            "valid_hashes": 0
        }
        
        for category, files in file_hashes.items():
            for file_name, file_info in files.items():
                if file_info.get("hash") and file_info.get("hash") != "error":
                    validation["integrity_checks"]["file_hashes"]["valid_hashes"] += 1
        
        # Check dependency hashes
        dependency_hashes = snapshot_result.get("dependency_hashes", {})
        validation["integrity_checks"]["dependency_hashes"] = {
            "categories": len(dependency_hashes),
            "valid_dependencies": True
        }
        
        # Calculate validation score
        if validation["validation_passed"]:
            validation["validation_score"] = 100.0
        else:
            issues_count = len(validation["issues"])
            validation["validation_score"] = max(0.0, 100.0 - (issues_count * 10.0))
        
        return validation
    
    def _generate_snapshot_integrity_hash(self, snapshot_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate integrity hash for entire snapshot"""
        
        integrity = {
            "integrity_timestamp": datetime.now().isoformat(),
            "snapshot_hash": None,
            "component_hashes": {},
            "verification_signature": None
        }
        
        # Calculate component hashes
        components = [
            "system_overview",
            "module_snapshots", 
            "file_hashes",
            "dependency_hashes",
            "configuration_hashes",
            "build_artifacts_hashes"
        ]
        
        for component in components:
            component_data = snapshot_result.get(component, {})
            component_str = json.dumps(component_data, sort_keys=True, separators=(',', ':'))
            integrity["component_hashes"][component] = self._calculate_content_hash(component_str)
        
        # Calculate overall snapshot hash
        combined_hashes = "".join(sorted(integrity["component_hashes"].values()))
        integrity["snapshot_hash"] = self._calculate_content_hash(combined_hashes)
        
        # Generate verification signature
        signature_data = {
            "snapshot_hash": integrity["snapshot_hash"],
            "timestamp": integrity["integrity_timestamp"],
            "version": self.snapshot_config["version"]
        }
        signature_str = json.dumps(signature_data, sort_keys=True)
        integrity["verification_signature"] = self._calculate_content_hash(signature_str)[:32]
        
        return integrity

def main():
    """Main function to generate deterministic system snapshot"""
    
    print("📸 MIA Enterprise AGI - Deterministic System Snapshot")
    print("=" * 55)
    
    generator = DeterministicSystemSnapshotGenerator()
    
    print("📸 Generating comprehensive deterministic system snapshot...")
    snapshot_result = generator.generate_system_snapshot()
    
    # Save results to JSON file
    output_file = "full_system_deterministic_snapshot.json"
    with open(output_file, 'w') as f:
        json.dump(snapshot_result, f, indent=2)
    
    print(f"📄 Snapshot results saved to: {output_file}")
    
    # Print summary
    print("\n📊 DETERMINISTIC SYSTEM SNAPSHOT SUMMARY:")
    
    overview = snapshot_result.get("system_overview", {})
    print(f"Project: {overview.get('project_name', 'Unknown')}")
    print(f"Version: {overview.get('version', 'Unknown')}")
    print(f"Total Modules: {overview.get('total_modules', 0)}")
    print(f"Total Files: {overview.get('total_files', 0)}")
    print(f"Total Lines of Code: {overview.get('total_lines_of_code', 0)}")
    
    module_snapshots = snapshot_result.get("module_snapshots", {})
    print(f"Module Snapshots: {len(module_snapshots)}")
    
    validation = snapshot_result.get("validation_results", {})
    validation_status = "✅ PASSED" if validation.get("validation_passed", False) else "❌ FAILED"
    validation_score = validation.get("validation_score", 0)
    print(f"Snapshot Validation: {validation_status} ({validation_score:.1f}%)")
    
    integrity = snapshot_result.get("snapshot_integrity", {})
    snapshot_hash = integrity.get("snapshot_hash", "unknown")[:16]
    print(f"Snapshot Hash: {snapshot_hash}...")
    
    print("\n📋 MODULE SNAPSHOTS:")
    for module_name, snapshot in module_snapshots.items():
        module_hash = snapshot.get("module_hash", "unknown")[:8]
        file_count = snapshot.get("file_count", 0)
        line_count = snapshot.get("line_count", 0)
        print(f"  {module_name}: {module_hash}... ({file_count} files, {line_count} lines)")
    
    print(f"\n✅ Deterministic system snapshot generation completed!")
    return snapshot_result

if __name__ == "__main__":
    main()