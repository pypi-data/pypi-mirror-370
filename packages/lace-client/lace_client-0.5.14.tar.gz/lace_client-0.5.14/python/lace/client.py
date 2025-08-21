"""
Lace Cloud API Client - Minimal implementation for PyPI.
All processing happens in the cloud for IP protection.
"""

import os
import json
import requests
import base64
from typing import Dict, Any, Optional, List
from pathlib import Path
import hashlib
from .bloom_filter import BloomFilter


class LaceClient:
    """
    Minimal Lace client for cloud operations.
    All algorithms and processing happen securely in the cloud.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Lace client.
        
        Args:
            api_key: API key for authentication. If not provided, uses LACE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('LACE_API_KEY')
        if not self.api_key:
            raise ValueError(
                "API key required. Set LACE_API_KEY environment variable or pass api_key parameter.\n"
                "Get your key at https://withlace.ai/request-demo"
            )
        
        self.api_base = os.getenv(
            'LACE_API_URL',
            'https://usgf90tw68.execute-api.eu-west-1.amazonaws.com/prod'
        )
        
        self.headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def attest(self, dataset_path: str, name: Optional[str] = None) -> str:
        """
        Create attestation for a dataset.
        Privacy-preserving: Creates bloom filter locally, only sends filter bytes.
        
        Args:
            dataset_path: Path to dataset file or directory
            name: Optional name for the dataset
            
        Returns:
            Attestation ID
        """
        dataset_path = Path(dataset_path)
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
        # Create bloom filter locally
        bloom = BloomFilter(expected_items=1_000_000, fp_rate=0.0001)
        
        # Process files and add to bloom filter
        if dataset_path.is_file():
            # Single file
            with open(dataset_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                bloom.add_text_content(content, include_ngrams=True)
        else:
            # Directory of files
            for file_path in dataset_path.rglob('*'):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            bloom.add_text_content(content, include_ngrams=True)
                    except Exception as e:
                        print(f"Warning: Skipped {file_path}: {e}")
        
        # Convert bloom filter to bytes (one-way transformation)
        bloom_bytes = bloom.to_bytes()
        bloom_b64 = base64.b64encode(bloom_bytes).decode('utf-8')
        
        # Start attestation session
        response = requests.post(
            f"{self.api_base}/v1/attest/start",
            json={
                'dataset_path': str(dataset_path),
                'dataset_name': name or dataset_path.name,
                'dataset_size': len(bloom_bytes)
            },
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to start attestation: {response.text}")
        
        # Get dataset_id (NOT session_id - fixing the bug!)
        result = response.json()
        dataset_id = result.get('dataset_id') or result.get('session_id')  # Handle both
        
        # Send bloom filter chunks (not raw data!)
        chunk_size = 1024 * 1024  # 1MB chunks
        for i in range(0, len(bloom_b64), chunk_size):
            chunk = bloom_b64[i:i+chunk_size]
            response = requests.post(
                f"{self.api_base}/v1/attest/chunk",
                json={
                    'dataset_id': dataset_id,  # Fixed: use dataset_id
                    'content': chunk,  # This is bloom filter data, not raw text
                    'is_bloom': True  # Flag to indicate this is bloom data
                },
                headers=self.headers
            )
            
            if response.status_code != 200:
                print(f"Warning: Failed to send bloom chunk: {response.text}")
        
        # Finalize attestation
        response = requests.post(
            f"{self.api_base}/v1/attest/finalize",
            json={'dataset_id': dataset_id},  # Fixed: use dataset_id not session_id
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to finalize attestation: {response.text}")
        
        result = response.json()
        attestation_id = result.get('attestation_id') or result.get('dataset_id') or dataset_id
        
        print(f"✅ Attestation created: {attestation_id}")
        
        return attestation_id
    
    def verify(self, attestation_id: str, check_copyright: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify an attestation and optionally check for specific text.
        
        Args:
            attestation_id: ID of attestation to verify
            check_copyright: Optional text to check if it was in training data
            
        Returns:
            Verification result with confidence score
        """
        # Build request body
        body = {
            'attestation_id': attestation_id,
            'dataset_id': attestation_id  # Support both field names
        }
        
        if check_copyright:
            body['text_to_verify'] = check_copyright
            body['check_copyright'] = check_copyright  # Support both field names
        
        # POST request (not GET)
        response = requests.post(
            f"{self.api_base}/v1/verify",
            json=body,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Verification failed: {response.text}")
        
        result = response.json()
        
        # Don't print here - let the caller handle display
        # This makes the function more flexible
        return result
    
    def monitor_start(self, attestation_id: str) -> str:
        """
        Start monitoring session for training.
        
        Args:
            attestation_id: Attestation to monitor against
            
        Returns:
            Monitor session ID
        """
        response = requests.post(
            f"{self.api_base}/v1/monitor/start",
            json={'attestation_id': attestation_id},
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to start monitoring: {response.text}")
        
        return response.json()['session_id']
    
    def monitor_loss(self, session_id: str, step: int, loss: float):
        """
        Send loss value to cloud.
        
        Args:
            session_id: Monitor session ID
            step: Training step
            loss: Loss value
        """
        response = requests.post(
            f"{self.api_base}/v1/monitor/loss",
            json={
                'session_id': session_id,
                'step': step,
                'loss': loss
            },
            headers=self.headers
        )
        
        if response.status_code != 200:
            # Don't fail training if monitoring fails
            print(f"Warning: Failed to send loss: {response.text}")
    
    def monitor_finalize(self, session_id: str) -> Dict[str, Any]:
        """
        Finalize monitoring and get correlation.
        
        Args:
            session_id: Monitor session ID
            
        Returns:
            Monitoring results with correlation
        """
        response = requests.post(
            f"{self.api_base}/v1/monitor/finalize",
            json={'session_id': session_id},
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to finalize monitoring: {response.text}")
        
        return response.json()
    
    def _hash_file(self, file_path: Path) -> str:
        """Hash file content."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()


# Convenience functions for one-line usage
_default_client = None

def get_client() -> LaceClient:
    """Get or create default client."""
    global _default_client
    if _default_client is None:
        _default_client = LaceClient()
    return _default_client

def attest(dataset_path: str, name: Optional[str] = None) -> str:
    """Quick attestation."""
    return get_client().attest(dataset_path, name)

def verify(attestation_id: str, check_copyright: Optional[str] = None) -> Dict[str, Any]:
    """Quick verification."""
    return get_client().verify(attestation_id, check_copyright)

def monitor():
    """
    One-line training monitor.
    Automatically hooks into PyTorch/TensorFlow training.
    """
    from .monitor import LaceMonitor
    monitor = LaceMonitor()
    monitor.start()
    return monitor