"""
Test determinism of aegis attest command outputs.
"""

import subprocess
import json
import tempfile
from pathlib import Path
import hashlib


def test_attest_determinism():
    """Test that attest produces deterministic outputs for same inputs."""
    
    # Create temporary directory with test data
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample dataset
        dataset_dir = Path(tmpdir) / "test_dataset"
        dataset_dir.mkdir()
        
        # Write some test files
        (dataset_dir / "file1.txt").write_text("Test content 1" * 100)
        (dataset_dir / "file2.txt").write_text("Test content 2" * 100)
        
        # Run attest twice with identical parameters
        results = []
        for i in range(2):
            proof_path = Path(tmpdir) / f"proof_{i}.bin"
            bloom_path = Path(tmpdir) / f"bloom_{i}.bloom"
            manifest_path = Path(tmpdir) / f"manifest_{i}.json"
            
            result = subprocess.run(
                [
                    "python", "-m", "aegis_cli", "attest",
                    "--dataset", str(dataset_dir),
                    "--out-proof", str(proof_path),
                    "--out-bloom", str(bloom_path),
                    "--emit-manifest", str(manifest_path),
                    "--fpr", "1e-4",
                    "--policy-chunks", "3",
                    "--chunk-bytes", "512",
                ],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"Attest failed: {result.stderr}"
            
            # Load manifest
            with open(manifest_path) as f:
                manifest = json.load(f)
            
            results.append({
                "manifest": manifest,
                "proof_hash": hashlib.sha256(proof_path.read_bytes()).hexdigest(),
                "bloom_hash": hashlib.sha256(bloom_path.read_bytes()).hexdigest(),
            })
        
        # Check deterministic fields match
        assert results[0]["manifest"]["dataset"]["hash"] == results[1]["manifest"]["dataset"]["hash"], \
            "Dataset fingerprint should be deterministic"
        
        assert results[0]["manifest"]["bloom_filter"]["seeds"] == results[1]["manifest"]["bloom_filter"]["seeds"], \
            "Bloom filter seeds should be deterministic"
        
        assert results[0]["manifest"]["bloom_filter"]["chunk_bytes"] == results[1]["manifest"]["bloom_filter"]["chunk_bytes"], \
            "Chunk bytes should be identical"
        
        assert results[0]["manifest"]["bloom_filter"]["k_hashes"] == results[1]["manifest"]["bloom_filter"]["k_hashes"], \
            "K hashes should be identical"
        
        assert results[0]["manifest"]["bloom_filter"]["expected_fpr"] == results[1]["manifest"]["bloom_filter"]["expected_fpr"], \
            "Expected FPR should be identical"
        
        # Timestamps should differ (not deterministic)
        assert results[0]["manifest"]["creation_timestamp"] != results[1]["manifest"]["creation_timestamp"], \
            "Timestamps should be different"
        
        print("✓ Determinism test passed")


def test_attest_determinism_with_different_fpr():
    """Test that different FPR values produce different parameters."""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        dataset_dir = Path(tmpdir) / "test_dataset"
        dataset_dir.mkdir()
        (dataset_dir / "test.txt").write_text("Test content" * 100)
        
        results = []
        for fpr in ["1e-2", "1e-4"]:
            manifest_path = Path(tmpdir) / f"manifest_{fpr}.json"
            
            result = subprocess.run(
                [
                    "python", "-m", "aegis_cli", "attest",
                    "--dataset", str(dataset_dir),
                    "--out-proof", str(Path(tmpdir) / f"proof_{fpr}.bin"),
                    "--out-bloom", str(Path(tmpdir) / f"bloom_{fpr}.bloom"),
                    "--emit-manifest", str(manifest_path),
                    "--fpr", fpr,
                ],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0
            
            with open(manifest_path) as f:
                manifest = json.load(f)
            results.append(manifest)
        
        # Same dataset fingerprint
        assert results[0]["dataset"]["hash"] == results[1]["dataset"]["hash"]
        
        # Different FPR should lead to different filter bits
        assert results[0]["bloom_filter"]["expected_fpr"] != results[1]["bloom_filter"]["expected_fpr"]
        
        print("✓ FPR variation test passed")


if __name__ == "__main__":
    test_attest_determinism()
    test_attest_determinism_with_different_fpr()
    print("\nAll determinism tests passed!")
