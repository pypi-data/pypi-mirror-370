# Lace Client

Python client for Lace - AI training transparency protocol.

## Installation

```bash
pip install lace-client
```

## Quick Start

```python
import lace

# One-line integration
lace.monitor()

# Create attestation
attestation_id = lace.attest("./training_data")

# Verify after training
result = lace.verify(attestation_id)
```

## Documentation

Full documentation available at https://withlace.ai

## License

Apache 2.0