"""
Test deterministic hash generation for v0.3.1.
"""

import pytest
import json
from lace_cli.utils import compute_deterministic_hash, normalize_config, get_generator_block


def test_normalize_config():
    """Test config normalization."""
    config = {
        "Field1": "  value  ",  # Should be trimmed and key lowercased
        "FIELD2": "",  # Should be removed (empty)
        "field3": None,  # Should be removed (None)
        "Field4": {
            "Nested": "  test  ",
            "Empty": ""
        },
        "field5": []  # Should be removed (empty list)
    }
    
    normalized = normalize_config(config)
    
    assert "field1" in normalized
    assert normalized["field1"] == "value"
    assert "field2" not in normalized
    assert "field3" not in normalized
    assert "field4" in normalized
    assert normalized["field4"]["nested"] == "test"
    assert "empty" not in normalized["field4"]
    assert "field5" not in normalized


def test_deterministic_hash_identical_inputs():
    """Test that identical inputs produce identical hashes."""
    config1 = {
        "manifest_hash": "abc123",
        "answers_hash": "def456",
        "report_format": "json"
    }
    
    config2 = {
        "report_format": "json",  # Different order
        "manifest_hash": "abc123",
        "answers_hash": "def456"
    }
    
    hash1 = compute_deterministic_hash(config1)
    hash2 = compute_deterministic_hash(config2)
    
    assert hash1 == hash2
    assert hash1.startswith("sha256:")
    assert len(hash1) == 71  # "sha256:" + 64 hex chars


def test_deterministic_hash_different_inputs():
    """Test that different inputs produce different hashes."""
    config1 = {"key": "value1"}
    config2 = {"key": "value2"}
    
    hash1 = compute_deterministic_hash(config1)
    hash2 = compute_deterministic_hash(config2)
    
    assert hash1 != hash2


def test_cross_command_consistency():
    """Test that same config produces same hash across different commands."""
    base_config = {
        "manifest_hash": "sha256:abcdef",
        "answers_hash": "sha256:123456"
    }
    
    # Simulate report command config
    report_config = {**base_config, "report_format": "json"}
    report_gen = get_generator_block("aegis-cli-report", "0.3.1", report_config)
    
    # Simulate policy command config with same base
    policy_config = {**base_config, "jurisdiction": "US"}
    policy_gen = get_generator_block("aegis-cli-policy", "0.3.1", policy_config)
    
    # Base hashes should be different (different configs)
    assert report_gen["config_hash"] != policy_gen["config_hash"]
    
    # But same tool with same config should produce same hash
    report_gen2 = get_generator_block("aegis-cli-report", "0.3.1", report_config)
    assert report_gen["config_hash"] == report_gen2["config_hash"]


def test_generator_block_structure():
    """Test generator block has correct structure."""
    config = {"test": "value"}
    gen = get_generator_block("test-tool", "0.3.1", config)
    
    assert "id" in gen
    assert gen["id"].startswith("sha256:")
    assert "name" in gen
    assert "test-tool" in gen["name"]
    assert gen["version"] == "0.3.1"
    assert "config_hash" in gen
    assert gen["config_hash"].startswith("sha256:")
    assert "attestation" in gen
    assert gen["attestation"]["rekor_entry_id"] is None


def test_whitespace_normalization():
    """Test that whitespace differences don't affect hash."""
    config1 = {
        "field": "value with  spaces",
        "nested": {"key": "  trimmed  "}
    }
    
    config2 = {
        "field": "value with  spaces",  # Same value
        "nested": {"key": "trimmed"}  # After trimming, should be same
    }
    
    hash1 = compute_deterministic_hash(config1)
    hash2 = compute_deterministic_hash(config2)
    
    # They should be the same after normalization
    assert hash1 == hash2


def test_empty_config():
    """Test hashing empty config."""
    empty = {}
    hash_val = compute_deterministic_hash(empty)
    
    assert hash_val.startswith("sha256:")
    # Empty object {} should have consistent hash
    expected = "sha256:44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
    assert hash_val == expected
