"""
Lace - AI Training Transparency Protocol

Prevent copyright lawsuits by proving what you DIDN'T train on.
Simple one-line integration with zero overhead.

Usage:
    import lace
    
    # Create attestation before training
    attestation_id = lace.attest("./training_data")
    
    # Monitor training (one line)
    lace.monitor()
    
    # Verify after training
    result = lace.verify(attestation_id)

All processing happens in the cloud for IP protection.
Get your API key at https://withlace.ai
"""

__version__ = "0.5.10"

from .client import (
    LaceClient,
    attest,
    verify,
    monitor,
    get_client
)

__all__ = [
    'LaceClient',
    'attest',
    'verify', 
    'monitor',
    'get_client',
    '__version__'
]

def about():
    """Display information about Lace."""
    print(f"""
Lace v{__version__} - AI Training Transparency Protocol
========================================================
Prevent copyright lawsuits with cryptographic proof of training.

Quick Start:
    import lace
    lace.monitor()  # One-line integration!

Learn more: https://withlace.ai
Get API key: https://withlace.ai/request-demo
    """)
