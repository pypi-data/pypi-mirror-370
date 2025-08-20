"""
Test HuggingFace metadata schema validation for v0.3.1.
"""

import pytest
import json
import yaml
from lace_cli.schema_validator import (
    validate_hf_metadata,
    validate_acceptance_criteria
)


def test_valid_community_metadata():
    """Test valid community tier metadata."""
    metadata = {
        "training_provenance": {
            "aegis_version": "0.3.1",
            "badge_tier": "community",
            "policy_chunks": 3,
            "bloom_fpr": "1e-4",
            "dataset_fingerprint": "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        }
    }
    
    assert validate_hf_metadata(metadata) is True
    
    criteria = validate_acceptance_criteria(metadata)
    assert criteria["policy_chunks_valid"] is True
    assert criteria["fpr_preset_valid"] is True
    assert criteria["dataset_fingerprint_present"] is True


def test_valid_notarized_metadata():
    """Test valid notarized tier metadata."""
    metadata = {
        "training_provenance": {
            "aegis_version": "0.3.1",
            "badge_tier": "notarized",
            "policy_chunks": 5,
            "bloom_fpr": "1e-6",
            "dataset_fingerprint": "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "rekor_entry_id": "24296fb24b8ad77a71c42a6d2a7a5c3e24296fb24b8ad77a71c42a6d2a7a5c3e"
        }
    }
    
    assert validate_hf_metadata(metadata) is True
    
    criteria = validate_acceptance_criteria(metadata)
    assert criteria["policy_chunks_valid"] is True
    assert criteria["fpr_preset_valid"] is True
    assert criteria["dataset_fingerprint_present"] is True
    assert criteria["rekor_entry_valid"] is True


def test_valid_metadata_with_optout():
    """Test metadata with opt-out scan."""
    metadata = {
        "training_provenance": {
            "aegis_version": "0.3.1",
            "badge_tier": "community",
            "policy_chunks": 3,
            "bloom_fpr": "1e-5",
            "dataset_fingerprint": "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "optout_scan": {
                "source": "spawning-local-json",
                "flagged_pct": 0.02,
                "sample_size": 10000,
                "scan_time_utc": "2025-08-08T12:00:00Z"
            }
        }
    }
    
    assert validate_hf_metadata(metadata) is True


def test_invalid_missing_required():
    """Test validation fails for missing required fields."""
    metadata = {
        "training_provenance": {
            "aegis_version": "0.3.1",
            "badge_tier": "community"
            # Missing policy_chunks, bloom_fpr, dataset_fingerprint
        }
    }
    
    with pytest.raises(Exception):
        validate_hf_metadata(metadata)


def test_invalid_badge_tier():
    """Test validation fails for invalid badge tier."""
    metadata = {
        "training_provenance": {
            "aegis_version": "0.3.1",
            "badge_tier": "invalid",  # Should be community or notarized
            "policy_chunks": 3,
            "bloom_fpr": "1e-4",
            "dataset_fingerprint": "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        }
    }
    
    with pytest.raises(Exception):
        validate_hf_metadata(metadata)


def test_invalid_policy_chunks():
    """Test validation fails for insufficient policy chunks."""
    metadata = {
        "training_provenance": {
            "aegis_version": "0.3.1",
            "badge_tier": "community",
            "policy_chunks": 2,  # Should be >= 3
            "bloom_fpr": "1e-4",
            "dataset_fingerprint": "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        }
    }
    
    with pytest.raises(Exception):
        validate_hf_metadata(metadata)
    
    criteria = validate_acceptance_criteria(metadata)
    assert criteria["policy_chunks_valid"] is False


def test_invalid_fpr_format():
    """Test validation fails for invalid FPR format."""
    metadata = {
        "training_provenance": {
            "aegis_version": "0.3.1",
            "badge_tier": "community",
            "policy_chunks": 3,
            "bloom_fpr": "0.0001",  # Should be like "1e-4"
            "dataset_fingerprint": "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        }
    }
    
    with pytest.raises(Exception):
        validate_hf_metadata(metadata)


def test_notarized_missing_rekor():
    """Test notarized tier requires rekor_entry_id."""
    metadata = {
        "training_provenance": {
            "aegis_version": "0.3.1",
            "badge_tier": "notarized",
            "policy_chunks": 3,
            "bloom_fpr": "1e-4",
            "dataset_fingerprint": "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
            # Missing rekor_entry_id
        }
    }
    
    with pytest.raises(Exception) as exc_info:
        validate_hf_metadata(metadata)
    assert "rekor_entry_id" in str(exc_info.value)


def test_incomplete_optout_scan():
    """Test validation fails for incomplete opt-out scan."""
    metadata = {
        "training_provenance": {
            "aegis_version": "0.3.1",
            "badge_tier": "community",
            "policy_chunks": 3,
            "bloom_fpr": "1e-4",
            "dataset_fingerprint": "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "optout_scan": {
                "source": "spawning-local-json",
                "flagged_pct": 0.02
                # Missing sample_size and scan_time_utc
            }
        }
    }
    
    with pytest.raises(Exception):
        validate_hf_metadata(metadata)


def test_acceptance_criteria_checks():
    """Test acceptance criteria validation."""
    # All criteria met
    good_metadata = {
        "training_provenance": {
            "aegis_version": "0.3.1",
            "badge_tier": "community",
            "policy_chunks": 3,
            "bloom_fpr": "1e-4",
            "dataset_fingerprint": "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        }
    }
    
    criteria = validate_acceptance_criteria(good_metadata)
    assert all(criteria.values())
    
    # Some criteria not met
    bad_metadata = {
        "training_provenance": {
            "aegis_version": "0.3.1",
            "badge_tier": "community",
            "policy_chunks": 2,  # Too few
            "bloom_fpr": "0.001",  # Wrong format
            "dataset_fingerprint": "TBD"  # Not set
        }
    }
    
    criteria = validate_acceptance_criteria(bad_metadata)
    assert criteria["policy_chunks_valid"] is False
    assert criteria["fpr_preset_valid"] is False
    assert criteria["dataset_fingerprint_present"] is False
