"""
Tests for edge cases and hardening in AEGIS CLI v0.3.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
import pytest


def test_telemetry_path_precedence(tmp_path, monkeypatch):
    """Test telemetry path precedence order."""
    from lace_cli.metrics import get_metrics_path
    
    # Create test directories
    aegis_state_dir = tmp_path / "aegis_state"
    xdg_state_dir = tmp_path / "xdg_state" / "aegis"
    local_dir = tmp_path / "local" / ".lace"
    home_dir = tmp_path / "home" / ".lace"
    
    for d in [aegis_state_dir, xdg_state_dir, local_dir, home_dir]:
        d.mkdir(parents=True)
    
    # Test 1: AEGIS_STATE_DIR takes precedence
    monkeypatch.setenv("AEGIS_STATE_DIR", str(aegis_state_dir))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "xdg_state"))
    monkeypatch.chdir(tmp_path / "local")
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    
    path = get_metrics_path()
    assert path == aegis_state_dir / "metrics.json"
    
    # Test 2: XDG_STATE_HOME/aegis/metrics.json is second
    monkeypatch.delenv("AEGIS_STATE_DIR")
    path = get_metrics_path()
    assert path == xdg_state_dir / "metrics.json"
    
    # Test 3: ./.lace/metrics.json is third
    monkeypatch.delenv("XDG_STATE_HOME")
    path = get_metrics_path()
    assert path == local_dir / "metrics.json"
    
    # Test 4: ~/.lace/metrics.json is last
    monkeypatch.chdir(tmp_path)  # Change away from local
    path = get_metrics_path()
    assert path == home_dir / "metrics.json"


def test_notarize_no_op():
    """Test notarization with no credentials shows exact message."""
    # Ensure no credentials are set
    env = os.environ.copy()
    env.pop("REKOR_API_KEY", None)
    env.pop("AEGIS_REKOR_URL", None)
    env.pop("COSIGN_PRIVATE_KEY", None)
    env.pop("COSIGN_PASSWORD", None)
    
    # Create test data
    with tempfile.TemporaryDirectory() as tmpdir:
        test_data = Path(tmpdir) / "test_data"
        test_data.mkdir()
        (test_data / "test.txt").write_text("test content")
        
        result = subprocess.run(
            [
                "aegis-cli", "attest",
                "--dataset", str(test_data),
                "--out-proof", str(Path(tmpdir) / "proof.bin"),
                "--out-bloom", str(Path(tmpdir) / "corpus.bloom"),
                "--notarize"
            ],
            capture_output=True,
            text=True,
            env=env
        )
        
        assert result.returncode == 0
        assert "Notarization skipped: Rekor credentials not found (use --help for setup)" in result.stdout


def test_verify_exit_codes():
    """Test verify command exit codes."""
    
    # Test 1: Missing manifest returns exit code 2
    result = subprocess.run(
        ["aegis-cli", "verify", "--manifest", "nonexistent.json"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 2
    assert "Manifest file not found" in result.stderr
    
    # Test 2: Invalid JSON manifest returns exit code 2
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("not valid json{")
        f.flush()
        
        result = subprocess.run(
            ["aegis-cli", "verify", "--manifest", f.name],
            capture_output=True,
            text=True
        )
        assert result.returncode == 2
        assert "Invalid JSON" in result.stderr
        
        Path(f.name).unlink()
    
    # Test 3: Policy not met returns exit code 1
    # We would need a mismatched dataset for this - skip for MVP


def test_attest_exit_codes():
    """Test attest command exit codes."""
    
    # Test: Non-existent dataset returns exit code 2
    result = subprocess.run(
        [
            "aegis-cli", "attest",
            "--dataset", "/nonexistent/path",
            "--out-proof", "./proof.bin",
            "--out-bloom", "./corpus.bloom"
        ],
        capture_output=True,
        text=True
    )
    assert result.returncode == 2
    assert "Dataset not found" in result.stderr


def test_report_json_format():
    """Test report command JSON output format."""
    
    # Use the test vectors manifest
    manifest_path = "docs/spec/test-vectors/vectors_manifest.json"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_path = f.name
    
    try:
        result = subprocess.run(
            [
                "aegis-cli", "report",
                "--manifest", manifest_path,
                "--format", "json",
                "--out", output_path
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        # Load and validate JSON structure
        with open(output_path) as f:
            report = json.load(f)
        
        # Check top-level fields
        assert "report_version" in report
        assert "generated_at" in report
        assert "manifest_version" in report
        assert "model_identification" in report
        assert "training_data_sources" in report
        assert "data_categories" in report
        assert "copyright_compliance" in report
        assert "data_processing" in report
        assert "personal_data" in report
        assert "transparency" in report
        
        # Check bloom filter metadata
        bloom = report["copyright_compliance"]["bloom_filter"]
        assert "chunk_bytes" in bloom
        assert "k_hashes" in bloom
        assert "expected_fpr" in bloom
        assert "consecutive_chunk_policy" in bloom
        
    finally:
        Path(output_path).unlink(missing_ok=True)


def test_determinism_dataset_fingerprint():
    """Test that same dataset produces same fingerprint."""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test dataset
        test_data = Path(tmpdir) / "test_data"
        test_data.mkdir()
        (test_data / "file1.txt").write_text("content 1")
        (test_data / "file2.txt").write_text("content 2")
        
        manifests = []
        
        # Run attest twice with same dataset
        for i in range(2):
            manifest_path = Path(tmpdir) / f"manifest{i}.json"
            
            result = subprocess.run(
                [
                    "aegis-cli", "attest",
                    "--dataset", str(test_data),
                    "--out-proof", str(Path(tmpdir) / f"proof{i}.bin"),
                    "--out-bloom", str(Path(tmpdir) / f"corpus{i}.bloom"),
                    "--emit-manifest", str(manifest_path),
                    "--fpr", "1e-4",
                    "--policy-chunks", "3"
                ],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0
            
            with open(manifest_path) as f:
                manifests.append(json.load(f))
        
        # Check deterministic fields match
        # dataset hash should be deterministic
        assert manifests[0]["dataset"]["hash"] == manifests[1]["dataset"]["hash"]
        assert manifests[0]["bloom_filter"]["seeds"] == manifests[1]["bloom_filter"]["seeds"]
        assert manifests[0]["bloom_filter"]["chunk_bytes"] == manifests[1]["bloom_filter"]["chunk_bytes"]
        assert manifests[0]["bloom_filter"]["k_hashes"] == manifests[1]["bloom_filter"]["k_hashes"]
        assert manifests[0]["bloom_filter"]["expected_fpr"] == manifests[1]["bloom_filter"]["expected_fpr"]
        
        # Timestamp should differ (unless run very fast)
        # But we don't assert this as it could be same in fast test
