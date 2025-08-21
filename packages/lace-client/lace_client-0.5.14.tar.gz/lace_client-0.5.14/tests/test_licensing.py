"""
Tests for the AEGIS licensing system.
"""

import json
import os
import pytest
import tempfile
from unittest.mock import patch, mock_open
from datetime import datetime, timedelta

from lace_core.licensing import (
    LicenseInfo,
    Edition,
    get_license_info,
    check_limits,
    validate_license_key,
    generate_test_license
)


class TestLicenseInfo:
    """Test the LicenseInfo class"""
    
    def test_default_developer_edition(self):
        """Test that the default edition is Developer"""
        license_info = LicenseInfo()
        assert license_info.edition == Edition.DEVELOPER
        assert not license_info.is_enterprise
        assert not license_info.has_indemnity
    
    def test_developer_limits(self):
        """Test Developer Edition limits"""
        license_info = LicenseInfo()
        limits = license_info.limits
        
        assert limits["max_docs"] == 1_000_000
        assert limits["max_size_gb"] == 1
        assert limits["max_qps"] == 30
        assert limits["price"] == "Free"
        assert limits["license"] == "Apache-2.0"
        assert not limits["indemnity"]
    
    def test_check_document_limit_within_bounds(self):
        """Test document limit checking within bounds"""
        license_info = LicenseInfo()
        assert license_info.check_document_limit(500_000)
        assert license_info.check_document_limit(1_000_000)
    
    def test_check_document_limit_exceeds_bounds(self):
        """Test document limit checking exceeds bounds"""
        license_info = LicenseInfo()
        assert not license_info.check_document_limit(1_000_001)
        assert not license_info.check_document_limit(2_000_000)
    
    def test_check_size_limit_within_bounds(self):
        """Test size limit checking within bounds"""
        license_info = LicenseInfo()
        assert license_info.check_size_limit(0.5)
        assert license_info.check_size_limit(1.0)
    
    def test_check_size_limit_exceeds_bounds(self):
        """Test size limit checking exceeds bounds"""
        license_info = LicenseInfo()
        assert not license_info.check_size_limit(1.1)
        assert not license_info.check_size_limit(5.0)
    
    def test_format_status_developer(self):
        """Test formatting status for Developer Edition"""
        license_info = LicenseInfo()
        status = license_info.format_status()
        
        assert "Developer Edition (Apache-2.0)" in status
        assert "1,000,000 documents" in status
        assert "1GB dataset size" in status
        assert "30 queries per second" in status
        assert "Watermarked output" in status
        assert "No legal guarantees" in status


class TestLicenseLoading:
    """Test license loading from environment and files"""
    
    def test_load_from_environment(self):
        """Test loading license from environment variable"""
        # Create a valid test license
        expiry = datetime.now() + timedelta(days=30)
        license_data = {
            "customer_id": "test-001",
            "organization": "Test Corp",
            "expiry_unix": int(expiry.timestamp()),
            "tier": "STARTUP",
            "signature": "test-signature"
        }
        
        with patch.dict(os.environ, {"AEGIS_LICENSE_KEY": json.dumps(license_data)}):
            license_info = LicenseInfo()
            
            assert license_info.edition == Edition.STARTUP
            assert license_info.organization == "Test Corp"
            assert license_info.license_key == license_data
    
    def test_load_from_file(self):
        """Test loading license from file"""
        expiry = datetime.now() + timedelta(days=30)
        license_data = {
            "customer_id": "test-001", 
            "organization": "File Corp",
            "expiry_unix": int(expiry.timestamp()),
            "tier": "GROWTH",
            "signature": "test-signature"
        }
        
        mock_file_content = json.dumps(license_data)
        
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            with patch("builtins.open", mock_open(read_data=mock_file_content)):
                license_info = LicenseInfo()
                
                assert license_info.edition == Edition.GROWTH
                assert license_info.organization == "File Corp"
                assert license_info.has_indemnity
    
    def test_expired_license_reverts_to_developer(self):
        """Test that expired licenses revert to Developer Edition"""
        # Create an expired license
        expiry = datetime.now() - timedelta(days=1)
        license_data = {
            "customer_id": "test-001",
            "organization": "Expired Corp", 
            "expiry_unix": int(expiry.timestamp()),
            "tier": "ENTERPRISE",
            "signature": "test-signature"
        }
        
        with patch.dict(os.environ, {"AEGIS_LICENSE_KEY": json.dumps(license_data)}):
            license_info = LicenseInfo()
            
            # Should revert to Developer Edition
            assert license_info.edition == Edition.DEVELOPER
            assert license_info.organization is None
    
    def test_invalid_license_format_reverts_to_developer(self):
        """Test that invalid license format reverts to Developer Edition"""
        with patch.dict(os.environ, {"AEGIS_LICENSE_KEY": "invalid-json"}):
            license_info = LicenseInfo()
            
            # Should revert to Developer Edition
            assert license_info.edition == Edition.DEVELOPER


class TestLicenseValidation:
    """Test license key validation"""
    
    def test_validate_valid_license(self):
        """Test validating a valid license key"""
        expiry = datetime.now() + timedelta(days=30)
        license_data = {
            "customer_id": "test-001",
            "organization": "Valid Corp",
            "expiry_unix": int(expiry.timestamp()),
            "tier": "STARTUP", 
            "signature": "valid-signature"
        }
        
        license_json = json.dumps(license_data)
        assert validate_license_key(license_json)
    
    def test_validate_expired_license(self):
        """Test validating an expired license key"""
        expiry = datetime.now() - timedelta(days=1)
        license_data = {
            "customer_id": "test-001",
            "organization": "Expired Corp",
            "expiry_unix": int(expiry.timestamp()),
            "tier": "STARTUP",
            "signature": "valid-signature"
        }
        
        license_json = json.dumps(license_data)
        assert not validate_license_key(license_json)
    
    def test_validate_missing_fields(self):
        """Test validating license with missing required fields"""
        license_data = {
            "customer_id": "test-001",
            # Missing organization, expiry_unix, tier, signature
        }
        
        license_json = json.dumps(license_data)
        assert not validate_license_key(license_json)
    
    def test_validate_invalid_json(self):
        """Test validating invalid JSON"""
        assert not validate_license_key("invalid-json")


class TestTierLimits:
    """Test different tier limits"""
    
    def test_startup_limits(self):
        """Test Startup Edition limits"""
        expiry = datetime.now() + timedelta(days=30)
        license_data = {
            "customer_id": "test-001",
            "organization": "Startup Corp",
            "expiry_unix": int(expiry.timestamp()),
            "tier": "STARTUP",
            "signature": "test-signature"
        }
        
        with patch.dict(os.environ, {"AEGIS_LICENSE_KEY": json.dumps(license_data)}):
            license_info = LicenseInfo()
            limits = license_info.limits
            
            assert limits["max_docs"] == 10_000_000
            assert limits["max_size_gb"] == 10
            assert limits["max_qps"] == 100
            assert limits["price"] == "$399/month"
            assert limits["license"] == "BSL-1.1"
            assert not limits["indemnity"]
    
    def test_growth_limits(self):
        """Test Growth Edition limits"""
        expiry = datetime.now() + timedelta(days=30)
        license_data = {
            "customer_id": "test-001",
            "organization": "Growth Corp",
            "expiry_unix": int(expiry.timestamp()),
            "tier": "GROWTH",
            "signature": "test-signature"
        }
        
        with patch.dict(os.environ, {"AEGIS_LICENSE_KEY": json.dumps(license_data)}):
            license_info = LicenseInfo()
            limits = license_info.limits
            
            assert limits["max_docs"] == 100_000_000
            assert limits["max_size_gb"] == 100
            assert limits["max_qps"] == 500
            assert limits["price"] == "$2,499/month"
            assert limits["license"] == "BSL-1.1"
            assert limits["indemnity"]
    
    def test_enterprise_limits(self):
        """Test Enterprise Edition limits"""
        expiry = datetime.now() + timedelta(days=30)
        license_data = {
            "customer_id": "test-001",
            "organization": "Enterprise Corp",
            "expiry_unix": int(expiry.timestamp()),
            "tier": "ENTERPRISE",
            "signature": "test-signature"
        }
        
        with patch.dict(os.environ, {"AEGIS_LICENSE_KEY": json.dumps(license_data)}):
            license_info = LicenseInfo()
            limits = license_info.limits
            
            assert limits["max_docs"] is None  # Unlimited
            assert limits["max_size_gb"] is None  # Unlimited
            assert limits["max_qps"] is None  # Unlimited
            assert limits["price"] == "$30,000/year"
            assert limits["license"] == "BSL-1.1"
            assert limits["indemnity"]


class TestLimitChecking:
    """Test limit checking functions"""
    
    def test_check_limits_within_developer_bounds(self):
        """Test limit checking within Developer Edition bounds"""
        # Should pass for Developer Edition limits
        assert check_limits(docs=500_000, size_gb=0.5)
        assert check_limits(docs=1_000_000, size_gb=1.0)
    
    def test_check_limits_exceeds_developer_bounds(self):
        """Test limit checking that exceeds Developer Edition bounds"""
        # Should fail for Developer Edition limits
        assert not check_limits(docs=2_000_000, size_gb=0.5)
        assert not check_limits(docs=500_000, size_gb=2.0)


class TestTestLicenseGeneration:
    """Test test license generation"""
    
    def test_generate_startup_test_license(self):
        """Test generating a Startup test license"""
        license_json = generate_test_license("STARTUP", days=30)
        license_data = json.loads(license_json)
        
        assert license_data["tier"] == "STARTUP"
        assert license_data["customer_id"] == "test-customer-001"
        assert license_data["organization"] == "Test Organization"
        assert "signature" in license_data
        
        # Check that it's valid for ~30 days
        expiry = datetime.fromtimestamp(license_data["expiry_unix"])
        now = datetime.now()
        assert (expiry - now).days >= 29
    
    def test_generate_enterprise_test_license(self):
        """Test generating an Enterprise test license"""
        license_json = generate_test_license("ENTERPRISE", days=7)
        license_data = json.loads(license_json)
        
        assert license_data["tier"] == "ENTERPRISE"
        assert license_data["max_documents"] is None  # Unlimited
        assert license_data["includes_indemnity"]
        assert license_data["indemnity_coverage_usd"] == 1_000_000
    
    def test_validate_generated_test_license(self):
        """Test that generated test licenses validate correctly"""
        license_json = generate_test_license("GROWTH", days=30)
        
        # Should validate successfully
        assert validate_license_key(license_json)


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_get_license_info(self):
        """Test get_license_info function"""
        license_info = get_license_info()
        assert isinstance(license_info, LicenseInfo)
        assert license_info.edition == Edition.DEVELOPER  # Default


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
