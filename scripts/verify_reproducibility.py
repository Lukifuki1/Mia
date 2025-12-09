#!/usr/bin/env python3
"""
MIA Enterprise AGI - Build Reproducibility Verification
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Any

class BuildReproducibilityVerifier:
    """Verifier za reproducibilnost buildov"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        logger = logging.getLogger("BuildVerifier")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def verify_build_reproducibility(self) -> Dict[str, Any]:
        """Preveri reproducibilnost buildov"""
        try:
            self.logger.info("🔍 Verifying build reproducibility...")
            
            # Preberi build metadata
            platforms = ["linux", "windows", "macos"]
            build_metadata = {}
            
            for platform in platforms:
                metadata_file = Path(f"build_metadata_{platform}.json")
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        build_metadata[platform] = json.load(f)
                else:
                    self.logger.warning(f"Missing metadata for {platform}")
            
            # Preveri hash konsistenco
            hash_verification = self._verify_hash_consistency(build_metadata)
            
            # Preveri timestamp konsistenco
            timestamp_verification = self._verify_timestamp_consistency(build_metadata)
            
            # Preveri version konsistenco
            version_verification = self._verify_version_consistency(build_metadata)
            
            # Celotna ocena
            overall_reproducible = (
                hash_verification["consistent"] and
                timestamp_verification["consistent"] and
                version_verification["consistent"]
            )
            
            verification_result = {
                "reproducible": overall_reproducible,
                "platforms_verified": len(build_metadata),
                "hash_verification": hash_verification,
                "timestamp_verification": timestamp_verification,
                "version_verification": version_verification,
                "verification_timestamp": "2022-01-01T00:00:00Z"
            }
            
            if overall_reproducible:
                self.logger.info("✅ Build reproducibility verified!")
            else:
                self.logger.error("❌ Build reproducibility verification failed!")
            
            return verification_result
            
        except Exception as e:
            self.logger.error(f"Verification error: {e}")
            return {"reproducible": False, "error": str(e)}
    
    def _verify_hash_consistency(self, build_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Preveri hash konsistenco"""
        hashes = []
        for platform, metadata in build_metadata.items():
            if "build_hash" in metadata:
                hashes.append(metadata["build_hash"])
        
        unique_hashes = len(set(hashes))
        consistent = unique_hashes <= 1  # Lahko so različni zaradi platform-specific buildov
        
        return {
            "consistent": consistent,
            "unique_hashes": unique_hashes,
            "total_platforms": len(hashes),
            "hashes": hashes
        }
    
    def _verify_timestamp_consistency(self, build_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Preveri timestamp konsistenco"""
        timestamps = []
        for platform, metadata in build_metadata.items():
            if "timestamp" in metadata:
                timestamps.append(metadata["timestamp"])
        
        unique_timestamps = len(set(timestamps))
        consistent = unique_timestamps == 1
        
        return {
            "consistent": consistent,
            "unique_timestamps": unique_timestamps,
            "expected_timestamp": 1640995200,
            "timestamps": timestamps
        }
    
    def _verify_version_consistency(self, build_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Preveri version konsistenco"""
        versions = []
        for platform, metadata in build_metadata.items():
            if "version" in metadata:
                versions.append(metadata["version"])
        
        unique_versions = len(set(versions))
        consistent = unique_versions == 1
        
        return {
            "consistent": consistent,
            "unique_versions": unique_versions,
            "expected_version": "1.0.0",
            "versions": versions
        }

if __name__ == "__main__":
    verifier = BuildReproducibilityVerifier()
    result = verifier.verify_build_reproducibility()
    
    # Shrani rezultate
    with open("reproducibility_verification.json", "w") as f:
        json.dump(result, f, indent=2)
    
    # Exit code
    exit(0 if result["reproducible"] else 1)
