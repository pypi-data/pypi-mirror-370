"""Unit tests for AEGIS client."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from lace_core import (
    AegisClient,
    DatasetMetadata,
    LoRAWeights,
    ProverConfig,
    register_dataset,
    prove_dataset,
    verify,
    DatasetRegistrationError,
    ProofGenerationError,
)


class TestAegisClient:
    """Test cases for AegisClient class."""
    
    def test_client_initialization_default_config(self):
        """Test client initializes with default configuration."""
        client = AegisClient()
        
        assert client.config is not None
        assert client.config.mode == "mock"
        assert client.config.timeout_seconds == 300
        assert client.config.max_layers == 10
    
    def test_client_initialization_custom_config(self):
        """Test client initializes with custom configuration."""
        config = ProverConfig(
            mode="real",
            timeout_seconds=600,
            max_layers=5,
        )
        client = AegisClient(config)
        
        assert client.config.mode == "real"
        assert client.config.timeout_seconds == 600
        assert client.config.max_layers == 5
    
    def test_register_dataset_file(self):
        """Test registering a single file as dataset."""
        client = AegisClient()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test dataset content")
            test_file = Path(f.name)
        
        try:
            metadata = client.register_dataset(test_file)
            
            assert metadata.id is not None
            assert len(metadata.id) == 16  # SHA256 hash truncated
            assert metadata.name == test_file.name
            assert metadata.file_count == 1
            assert metadata.size_bytes > 0
            assert metadata.merkle_root is not None
            assert len(metadata.merkle_root) == 64  # SHA256 hex
            
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_register_dataset_directory(self):
        """Test registering a directory as dataset."""
        client = AegisClient()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            (temp_path / "file1.txt").write_text("content 1")
            (temp_path / "file2.txt").write_text("content 2")
            (temp_path / "subdir").mkdir()
            (temp_path / "subdir" / "file3.txt").write_text("content 3")
            
            metadata = client.register_dataset(temp_path)
            
            assert metadata.id is not None
            assert metadata.name == temp_path.name
            assert metadata.file_count == 3
            assert metadata.size_bytes > 0
            assert metadata.merkle_root is not None
    
    def test_register_dataset_nonexistent_path(self):
        """Test error when registering nonexistent path."""
        client = AegisClient()
        
        with pytest.raises(DatasetRegistrationError, match="does not exist"):
            client.register_dataset("/nonexistent/path")
    
    def test_register_dataset_custom_metadata(self):
        """Test registering dataset with custom metadata."""
        client = AegisClient()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            test_file = Path(f.name)
        
        try:
            metadata = client.register_dataset(
                test_file,
                dataset_id="custom_id",
                name="Custom Dataset",
                description="Test dataset",
                attributes={"version": "1.0", "author": "test"},
            )
            
            assert metadata.id == "custom_id"
            assert metadata.name == "Custom Dataset"
            assert metadata.description == "Test dataset"
            assert metadata.attributes["version"] == "1.0"
            assert metadata.attributes["author"] == "test"
            
        finally:
            test_file.unlink(missing_ok=True)


class TestProofGeneration:
    """Test cases for proof generation."""
    
    def test_prove_dataset_mock_mode(self):
        """Test generating mock proof."""
        client = AegisClient(ProverConfig(mode="mock"))
        
        # Create test dataset metadata
        metadata = DatasetMetadata(
            id="test_dataset",
            name="Test Dataset",
            size_bytes=1000,
            file_count=1,
            merkle_root="a" * 64,
        )
        
        # Create test LoRA weights
        lora_weights = [
            LoRAWeights(layer_name="layer_0", weights=[0.1, 0.2, 0.3], dimension=3),
            LoRAWeights(layer_name="layer_1", weights=[0.4, 0.5], dimension=2),
        ]
        
        proof = client.prove_dataset(metadata, lora_weights)
        
        assert proof.proof_id is not None
        assert len(proof.proof_id) == 16
        assert proof.dataset_metadata == metadata
        assert proof.lora_weights == lora_weights
        assert proof.metadata.proof_type == "mock_sha256"
        assert proof.metadata.curve_type == "none"
        assert proof.metadata.generation_time_seconds >= 0
        assert len(proof.proof_data) > 0
        assert proof.verification_key is not None
    
    def test_prove_dataset_too_many_layers(self):
        """Test error when too many layers provided."""
        config = ProverConfig(max_layers=2)
        client = AegisClient(config)
        
        metadata = DatasetMetadata(
            id="test_dataset",
            name="Test Dataset",
            size_bytes=1000,
            file_count=1,
            merkle_root="a" * 64,
        )
        
        # Create too many layers
        lora_weights = [
            LoRAWeights(layer_name=f"layer_{i}", weights=[0.1], dimension=1)
            for i in range(5)  # More than max_layers=2
        ]
        
        with pytest.raises(ProofGenerationError, match="Too many layers"):
            client.prove_dataset(metadata, lora_weights)
    
    def test_prove_dataset_dimension_too_large(self):
        """Test error when layer dimension is too large."""
        config = ProverConfig(layer_dimension=10)
        client = AegisClient(config)
        
        metadata = DatasetMetadata(
            id="test_dataset",
            name="Test Dataset",
            size_bytes=1000,
            file_count=1,
            merkle_root="a" * 64,
        )
        
        # Create layer with dimension too large
        lora_weights = [
            LoRAWeights(
                layer_name="layer_0",
                weights=[0.1] * 20,  # More than layer_dimension=10
                dimension=20,
            )
        ]
        
        with pytest.raises(ProofGenerationError, match="Layer dimension too large"):
            client.prove_dataset(metadata, lora_weights)
    
    def test_prove_dataset_invalid_mode(self):
        """Test error with invalid proof mode."""
        client = AegisClient()
        
        metadata = DatasetMetadata(
            id="test_dataset",
            name="Test Dataset",
            size_bytes=1000,
            file_count=1,
            merkle_root="a" * 64,
        )
        
        lora_weights = [
            LoRAWeights(layer_name="layer_0", weights=[0.1], dimension=1)
        ]
        
        with pytest.raises(ProofGenerationError, match="Invalid proof mode"):
            client.prove_dataset(metadata, lora_weights, mode="invalid")


class TestVerification:
    """Test cases for proof verification."""
    
    def test_verify_mock_proof(self):
        """Test verifying a mock proof."""
        client = AegisClient(ProverConfig(mode="mock"))
        
        # Generate a proof
        metadata = DatasetMetadata(
            id="test_dataset",
            name="Test Dataset",
            size_bytes=1000,
            file_count=1,
            merkle_root="a" * 64,
        )
        
        lora_weights = [
            LoRAWeights(layer_name="layer_0", weights=[0.1, 0.2], dimension=2)
        ]
        
        proof = client.prove_dataset(metadata, lora_weights)
        
        # Verify the proof
        result = client.verify(proof)
        
        assert result.is_valid is True
        assert result.proof_id == proof.proof_id
        assert result.verification_time_seconds >= 0
        assert result.error_message is None
    
    def test_verify_invalid_mock_proof(self):
        """Test verifying an invalid mock proof."""
        client = AegisClient(ProverConfig(mode="mock"))
        
        # Generate a proof
        metadata = DatasetMetadata(
            id="test_dataset",
            name="Test Dataset",
            size_bytes=1000,
            file_count=1,
            merkle_root="a" * 64,
        )
        
        lora_weights = [
            LoRAWeights(layer_name="layer_0", weights=[0.1, 0.2], dimension=2)
        ]
        
        proof = client.prove_dataset(metadata, lora_weights)
        
        # Tamper with the proof
        proof.proof_data = b"tampered_data"
        
        # Verify the tampered proof
        result = client.verify(proof)
        
        assert result.is_valid is False
        assert result.proof_id == proof.proof_id
        assert result.error_message == "Proof verification failed"


class TestConvenienceFunctions:
    """Test cases for convenience functions."""
    
    def test_register_dataset_function(self):
        """Test register_dataset convenience function."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            test_file = Path(f.name)
        
        try:
            metadata = register_dataset(test_file, name="Test Dataset")
            
            assert metadata.name == "Test Dataset"
            assert metadata.file_count == 1
            
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_prove_dataset_function(self):
        """Test prove_dataset convenience function."""
        metadata = DatasetMetadata(
            id="test_dataset",
            name="Test Dataset",
            size_bytes=1000,
            file_count=1,
            merkle_root="a" * 64,
        )
        
        lora_weights = [
            LoRAWeights(layer_name="layer_0", weights=[0.1], dimension=1)
        ]
        
        proof = prove_dataset(metadata, lora_weights, mode="mock")
        
        assert proof.metadata.proof_type == "mock_sha256"
        assert proof.dataset_metadata == metadata
    
    def test_verify_function(self):
        """Test verify convenience function."""
        metadata = DatasetMetadata(
            id="test_dataset",
            name="Test Dataset",
            size_bytes=1000,
            file_count=1,
            merkle_root="a" * 64,
        )
        
        lora_weights = [
            LoRAWeights(layer_name="layer_0", weights=[0.1], dimension=1)
        ]
        
        # Generate proof
        proof = prove_dataset(metadata, lora_weights, mode="mock")
        
        # Verify proof
        result = verify(proof)
        
        assert result.is_valid is True
        assert result.proof_id == proof.proof_id


class TestLoRAWeights:
    """Test cases for LoRAWeights model."""
    
    def test_lora_weights_valid(self):
        """Test creating valid LoRAWeights."""
        weights = LoRAWeights(
            layer_name="transformer.layer_0",
            weights=[0.1, 0.2, 0.3],
            dimension=3,
        )
        
        assert weights.layer_name == "transformer.layer_0"
        assert weights.weights == [0.1, 0.2, 0.3]
        assert weights.dimension == 3
    
    def test_lora_weights_dimension_mismatch(self):
        """Test error when weights don't match dimension."""
        with pytest.raises(ValueError, match="Weight count .* doesn't match dimension"):
            LoRAWeights(
                layer_name="layer_0",
                weights=[0.1, 0.2, 0.3],  # 3 weights
                dimension=5,  # But dimension is 5
            )


class TestProverConfig:
    """Test cases for ProverConfig model."""
    
    def test_prover_config_defaults(self):
        """Test default ProverConfig values."""
        config = ProverConfig()
        
        assert config.mode == "mock"
        assert config.timeout_seconds == 300
        assert config.max_layers == 10
        assert config.layer_dimension == 64
        assert config.prover_binary_path == Path("target/debug/prover-cli")
        assert config.working_directory == Path.cwd()
    
    def test_prover_config_custom(self):
        """Test custom ProverConfig values."""
        config = ProverConfig(
            mode="real",
            timeout_seconds=600,
            max_layers=5,
            layer_dimension=32,
            prover_binary_path=Path("/custom/path"),
            working_directory=Path("/custom/workdir"),
        )
        
        assert config.mode == "real"
        assert config.timeout_seconds == 600
        assert config.max_layers == 5
        assert config.layer_dimension == 32
        assert config.prover_binary_path == Path("/custom/path")
        assert config.working_directory == Path("/custom/workdir")
