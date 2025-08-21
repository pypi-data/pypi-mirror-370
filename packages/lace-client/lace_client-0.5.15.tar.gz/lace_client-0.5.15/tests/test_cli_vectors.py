"""
Integration tests for AEGIS CLI v0.3 using test vectors.
"""

import subprocess
import json
import os
from pathlib import Path
import tempfile
import shutil


def test_verify_command():
    """Test aegis verify with test vectors."""
    result = subprocess.run(
        ["python", "-m", "aegis_cli", "verify", "--manifest", "docs/spec/test-vectors/vectors_manifest.json"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent  # Run from repo root
    )
    
    # Check command succeeded
    assert result.returncode == 0, f"Command failed: {result.stderr}"
    
    # Check output contains expected strings
    assert "AEGIS Verification v0.3" in result.stdout
    assert "PASS" in result.stdout
    assert "chunks" in result.stdout.lower()


def test_report_generation():
    """Test EU GPAI report generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        report_path = Path(tmpdir) / "test_report.md"
        
        result = subprocess.run(
            [
                "python", "-m", "aegis_cli", "report",
                "--manifest", "docs/spec/test-vectors/vectors_manifest.json",
                "--out", str(report_path)
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        
        # Check command succeeded
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert report_path.exists(), "Report file was not created"
        
        # Check report content
        content = report_path.read_text()
        assert "EU GPAI Training Data Summary" in content
        assert "AEGIS v0.3" in content
        assert "Copyright Compliance" in content


def test_report_json_format():
    """Test JSON format report generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        report_path = Path(tmpdir) / "test_report.json"
        
        result = subprocess.run(
            [
                "python", "-m", "aegis_cli", "report",
                "--manifest", "docs/spec/test-vectors/vectors_manifest.json",
                "--out", str(report_path),
                "--format", "json"
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        
        # Check command succeeded
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert report_path.exists(), "Report file was not created"
        
        # Check JSON is valid
        with open(report_path) as f:
            data = json.load(f)
            assert data["report_version"] == "0.3.1"
            assert "training_data_sources" in data
            assert "copyright_compliance" in data


def test_attest_placeholder():
    """Test placeholder attestation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample dataset
        sample_dir = Path(tmpdir) / "test_data"
        sample_dir.mkdir()
        (sample_dir / "test1.txt").write_text("test content " * 100)
        (sample_dir / "test2.txt").write_text("more test content " * 100)
        
        proof_path = Path(tmpdir) / "test_proof.bin"
        bloom_path = Path(tmpdir) / "test_corpus.bloom"
        
        result = subprocess.run(
            [
                "python", "-m", "aegis_cli", "attest",
                "--dataset", str(sample_dir),
                "--out-proof", str(proof_path),
                "--out-bloom", str(bloom_path),
                "--fpr", "1e-4"
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        
        # Check command succeeded
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert proof_path.exists(), "Proof file was not created"
        assert bloom_path.exists(), "Bloom filter was not created"
        
        # Check output contains TTFP
        assert "Time to First Proof" in result.stdout
        assert "Attestation complete" in result.stdout


def test_attest_with_manifest():
    """Test attestation with manifest generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample dataset
        sample_dir = Path(tmpdir) / "test_data"
        sample_dir.mkdir()
        (sample_dir / "test.txt").write_text("test content " * 100)
        
        proof_path = Path(tmpdir) / "test_proof.bin"
        bloom_path = Path(tmpdir) / "test_corpus.bloom"
        manifest_path = Path(tmpdir) / "test_manifest.json"
        
        result = subprocess.run(
            [
                "python", "-m", "aegis_cli", "attest",
                "--dataset", str(sample_dir),
                "--out-proof", str(proof_path),
                "--out-bloom", str(bloom_path),
                "--emit-manifest", str(manifest_path),
                "--fpr", "1e-6"
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        
        # Check command succeeded
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert manifest_path.exists(), "Manifest file was not created"
        
        # Check manifest content
        with open(manifest_path) as f:
            manifest = json.load(f)
            assert manifest["version"] == "0.3"
            assert "file_hashes" in manifest
            assert "bloom_filter" in manifest
            assert manifest["bloom_filter"]["expected_fpr"] == "1e-6"


def test_verify_help():
    """Test help output for verify command."""
    result = subprocess.run(
        ["python", "-m", "aegis_cli", "verify", "--help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent
    )
    
    assert result.returncode == 0
    assert "verify" in result.stdout
    assert "--manifest" in result.stdout
    assert "--policy-chunks" in result.stdout


def test_main_help():
    """Test main help output."""
    result = subprocess.run(
        ["python", "-m", "aegis_cli", "--help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent
    )
    
    assert result.returncode == 0
    assert "Aegis - Show what data you trained on" in result.stdout
    assert "verify" in result.stdout
    assert "report" in result.stdout
    assert "attest" in result.stdout


def test_version():
    """Test version output."""
    result = subprocess.run(
        ["python", "-m", "aegis_cli", "--version"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent
    )
    
    assert result.returncode == 0
    assert "0.3.1" in result.stdout


if __name__ == "__main__":
    # Run tests manually
    import sys
    
    test_functions = [
        test_verify_command,
        test_report_generation,
        test_report_json_format,
        test_attest_placeholder,
        test_attest_with_manifest,
        test_verify_help,
        test_main_help,
        test_version,
    ]
    
    failed = 0
    for test_func in test_functions:
        try:
            print(f"Running {test_func.__name__}...", end=" ")
            test_func()
            print("✓ PASSED")
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1
    
    if failed:
        print(f"\n{failed} tests failed")
        sys.exit(1)
    else:
        print(f"\nAll {len(test_functions)} tests passed!")
