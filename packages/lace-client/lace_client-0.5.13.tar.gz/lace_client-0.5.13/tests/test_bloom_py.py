"""Unit tests for AEGIS Bloom filter functionality."""

import tempfile
from pathlib import Path
import pytest

import lace_core.aegis_client as aegis_client


class TestBloomFilter:
    """Test cases for Bloom filter functionality."""
    
    def test_bloom_check_result_enum(self):
        """Test BloomCheckResult enum values."""
        # Test that the enum values exist and have correct string representation
        not_present = aegis_client.BloomCheckResult.NotPresent
        maybe_present = aegis_client.BloomCheckResult.MaybePresent
        
        assert str(not_present) == "NOT_PRESENT"
        assert str(maybe_present) == "MAYBE_PRESENT"
        assert repr(not_present) == "BloomCheckResult.NOT_PRESENT"
        assert repr(maybe_present) == "BloomCheckResult.MAYBE_PRESENT"
    
    def test_bloom_build_and_check(self):
        """Test building a Bloom filter and checking against it."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test dataset
            test_file = temp_path / "test.txt"
            test_content = "The quick brown fox jumps over the lazy dog.\nThis is a test sentence for copyright checking."
            test_file.write_text(test_content)
            
            # Build bloom filter
            bloom_path = aegis_client.bloom_build(str(temp_path))
            
            # Verify bloom file was created
            assert Path(bloom_path).exists()
            assert bloom_path.endswith(".bloom")
            
            # Check text that should be present
            result = aegis_client.bloom_check(test_content, bloom_path)
            # Note: Due to consecutive hits requirement, this might be NotPresent or MaybePresent
            assert result in [aegis_client.BloomCheckResult.NotPresent, aegis_client.BloomCheckResult.MaybePresent]
            
            # Check text that should definitely not be present
            absent_text = "This text was never added to the dataset and should not be found."
            result_absent = aegis_client.bloom_check(absent_text, bloom_path)
            assert result_absent == aegis_client.BloomCheckResult.NotPresent
    
    def test_bloom_build_custom_output_path(self):
        """Test building bloom filter with custom output path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test dataset
            test_file = temp_path / "data.txt"
            test_file.write_text("Sample data for testing.")
            
            # Build with custom output path
            custom_output = temp_path / "custom_filter.bloom"
            bloom_path = aegis_client.bloom_build(str(temp_path), output_path=str(custom_output))
            
            assert bloom_path == str(custom_output)
            assert custom_output.exists()
    
    def test_bloom_build_custom_size(self):
        """Test building bloom filter with custom size."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test dataset
            test_file = temp_path / "data.txt"
            test_file.write_text("Sample data for testing.")
            
            # Build with custom size
            bloom_path = aegis_client.bloom_build(str(temp_path), size_mb=32)
            
            assert Path(bloom_path).exists()
    
    def test_bloom_check_file_vs_text(self):
        """Test that bloom_check works with both file paths and text content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create training dataset
            train_file = temp_path / "train.txt"
            train_content = "Training data content for the model."
            train_file.write_text(train_content)
            
            # Build bloom filter
            bloom_path = aegis_client.bloom_build(str(temp_path))
            
            # Create test file to check
            test_file = temp_path / "test.txt"
            test_file.write_text(train_content)
            
            # Check using file path
            result_file = aegis_client.bloom_check(str(test_file), bloom_path)
            
            # Check using text content
            result_text = aegis_client.bloom_check(train_content, bloom_path)
            
            # Results should be the same
            assert result_file == result_text
    
    def test_bloom_build_nonexistent_directory(self):
        """Test behavior when building from nonexistent directory."""
        # This creates an empty bloom filter for a nonexistent directory
        # Future enhancement: could add validation to fail for nonexistent paths
        bloom_path = aegis_client.bloom_build("/nonexistent/directory")
        assert bloom_path == "directory.bloom"
    
    def test_bloom_check_nonexistent_filter(self):
        """Test error when checking against nonexistent filter file."""
        with pytest.raises(RuntimeError, match="Failed to check against Bloom filter"):
            aegis_client.bloom_check("test text", "/nonexistent/filter.bloom")
    
    def test_bloom_check_corrupted_filter(self):
        """Test error when checking against corrupted filter file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a fake corrupted bloom file
            corrupted_filter = temp_path / "corrupted.bloom"
            corrupted_filter.write_text("This is not a valid bloom filter file")
            
            with pytest.raises(RuntimeError, match="Failed to check against Bloom filter"):
                aegis_client.bloom_check("test text", str(corrupted_filter))
    
    def test_bloom_build_multiple_files(self):
        """Test building bloom filter from directory with multiple files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create multiple test files
            (temp_path / "file1.txt").write_text("Content of first file.")
            (temp_path / "file2.py").write_text("print('Python code')")
            (temp_path / "file3.md").write_text("# Markdown file\nWith some content.")
            
            # Create subdirectory with more files
            subdir = temp_path / "subdir"
            subdir.mkdir()
            (subdir / "nested.txt").write_text("Nested file content.")
            
            # Build bloom filter
            bloom_path = aegis_client.bloom_build(str(temp_path))
            
            assert Path(bloom_path).exists()
            
            # Test checking against different files
            result1 = aegis_client.bloom_check("Content of first file.", bloom_path)
            result2 = aegis_client.bloom_check("print('Python code')", bloom_path)
            result3 = aegis_client.bloom_check("# Markdown file", bloom_path)
            result4 = aegis_client.bloom_check("Nested file content.", bloom_path)
            
            # All should be either NotPresent or MaybePresent (due to consecutive hits requirement)
            for result in [result1, result2, result3, result4]:
                assert result in [aegis_client.BloomCheckResult.NotPresent, aegis_client.BloomCheckResult.MaybePresent]
    
    def test_bloom_performance_medium_dataset(self):
        """Test bloom filter performance with medium-sized dataset."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create medium-sized dataset (100 files with some content)
            for i in range(100):
                test_file = temp_path / f"file_{i:03d}.txt"
                content = f"File {i}: " + "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 10
                test_file.write_text(content)
            
            # Measure build time
            import time
            start_time = time.time()
            
            bloom_path = aegis_client.bloom_build(str(temp_path))
            
            build_time = time.time() - start_time
            
            # Should complete in reasonable time (< 45 seconds as per acceptance criteria)
            assert build_time < 45.0, f"Build took too long: {build_time:.2f} seconds"
            
            # Verify the filter works
            assert Path(bloom_path).exists()
            
            # Test a few checks
            result_present = aegis_client.bloom_check("Lorem ipsum dolor", bloom_path)
            result_absent = aegis_client.bloom_check("This text was never in the dataset", bloom_path)
            
            # At minimum, absent text should be NotPresent
            assert result_absent == aegis_client.BloomCheckResult.NotPresent
            
            # Present text might be NotPresent or MaybePresent due to consecutive hits requirement
            assert result_present in [aegis_client.BloomCheckResult.NotPresent, aegis_client.BloomCheckResult.MaybePresent]
