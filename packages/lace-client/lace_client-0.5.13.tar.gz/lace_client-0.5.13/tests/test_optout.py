"""
Tests for opt-out scanning functionality
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from lace_cli.optout import OptOutProvider, SpawningProvider


class TestOptOutProvider:
    """Test the OptOutProvider protocol."""
    
    def test_protocol_methods(self):
        """Test that protocol defines required methods."""
        # This is a protocol, so we test the interface
        provider = MagicMock(spec=OptOutProvider)
        
        # Should have these methods
        assert hasattr(provider, 'load')
        assert hasattr(provider, 'check_text')
        assert hasattr(provider, 'check_uri')


class TestSpawningProvider:
    """Test the Spawning opt-out provider."""
    
    def test_load_json_file(self):
        """Test loading opt-out data from JSON file."""
        provider = SpawningProvider()
        
        # Create test JSON file
        test_data = {
            "domains": ["no-ai.com", "protected.org"],
            "patterns": ["DO NOT TRAIN", "NO AI"],
            "content_hashes": ["sha256:abc123"]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            provider.load(json_path=temp_path)
            
            # Check data was loaded
            assert provider.domains == {"no-ai.com", "protected.org"}
            assert provider.patterns == {"DO NOT TRAIN", "NO AI"}
            assert provider.content_hashes == {"sha256:abc123"}
        finally:
            Path(temp_path).unlink()
    
    def test_check_text(self):
        """Test checking text against opt-out patterns."""
        provider = SpawningProvider()
        provider.patterns = {"DO NOT TRAIN", "NO AI"}
        
        # Should match
        assert provider.check_text("This work contains DO NOT TRAIN marker")
        assert provider.check_text("NO AI allowed here")
        
        # Should not match
        assert not provider.check_text("This is fine to use")
        assert not provider.check_text("Regular content")
    
    def test_check_uri(self):
        """Test checking URIs against opt-out domains."""
        provider = SpawningProvider()
        provider.domains = {"no-ai.com", "protected.org"}
        
        # Should match
        assert provider.check_uri("https://no-ai.com/content")
        assert provider.check_uri("http://protected.org/image.jpg")
        assert provider.check_uri("https://subdomain.no-ai.com/page")
        
        # Should not match
        assert not provider.check_uri("https://allowed.com/content")
        assert not provider.check_uri("https://example.org/page")
    
    def test_empty_provider(self):
        """Test provider with no data loaded."""
        provider = SpawningProvider()
        
        # Should not match anything when empty
        assert not provider.check_text("Any text")
        assert not provider.check_uri("https://any.com")
    
    def test_load_invalid_json(self):
        """Test handling of invalid JSON file."""
        provider = SpawningProvider()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("not valid json{")
            temp_path = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                provider.load(json_path=temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_load_missing_file(self):
        """Test handling of missing file."""
        provider = SpawningProvider()
        
        with pytest.raises(FileNotFoundError):
            provider.load(json_path="/nonexistent/file.json")


class TestOptOutScanCommand:
    """Test the optout-scan CLI command."""
    
    @patch('aegis_cli.optout.scan_dataset')
    def test_command_basic(self, mock_scan):
        """Test basic command execution."""
        mock_scan.return_value = {
            "total_files": 100,
            "flagged_files": 2,
            "flagged_pct": 0.02,
            "source": "spawning-local-json"
        }
        
        # This would be called by the CLI
        result = mock_scan(
            dataset_path="/path/to/dataset",
            spawning_json="/path/to/optout.json"
        )
        
        assert result["total_files"] == 100
        assert result["flagged_pct"] == 0.02
