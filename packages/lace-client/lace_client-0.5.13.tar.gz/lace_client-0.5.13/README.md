# Lace - AI Training Transparency Protocol

[![PyPI version](https://badge.fury.io/py/lace-client.svg)](https://badge.fury.io/py/lace-client)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Python](https://img.shields.io/pypi/pyversions/lace-client.svg)](https://pypi.org/project/lace-client/)

**Prevent copyright lawsuits by proving what you DIDN'T train on.**

Lace provides cryptographic proof of AI training provenance through multiple proprietary verification methods. When model outputs resemble copyrighted content, you can prove definitively whether that content was in your training data.

## 🚀 Quick Start

```bash
pip install lace-client
```

```python
import lace

# Before training: Create attestation of your dataset
attestation_id = lace.attest("./training_data")

# During training: One-line integration (zero overhead)
lace.monitor()  # Automatically hooks into PyTorch/TensorFlow

# After training: Verify if specific content was in training data
result = lace.verify(attestation_id, check_copyright="Text to check")
print(f"Result: {result['detection']}")  # "FOUND" or "NOT_FOUND"
print(f"Confidence: {result['confidence']}%")  # Binary confidence level
```

## 🔑 Get Your API Key

All processing happens in our secure cloud infrastructure for maximum accuracy and IP protection.

**Get your free API key:** [https://withlace.ai/request-demo](https://withlace.ai/request-demo)

```bash
export LACE_API_KEY=your_api_key_here
```

## 💡 How It Works

1. **Attestation**: Before training, Lace creates a cryptographic fingerprint of your dataset
2. **Monitoring**: During training, Lace captures training patterns using multiple proprietary methods
3. **Verification**: After training, Lace analyzes the relationship between your model and dataset
4. **Legal Evidence**: Get legally-sufficient evidence showing what was and wasn't in your training data

## 📊 Integration Examples

### HuggingFace Transformers

```python
from transformers import Trainer
import lace

# Create attestation
attestation_id = lace.attest("./data")

# Start monitoring
lace.monitor()

# Train normally
trainer = Trainer(model, args, dataset)
trainer.train()

# Verify copyright content
result = lace.verify(attestation_id, check_copyright="Copyrighted text")
print(f"Was this text in training data? {result['detection']}")
```

### PyTorch

```python
import torch
import lace

# Start monitoring
lace.monitor()

# Your normal training loop
for epoch in range(epochs):
    for batch in dataloader:
        loss = model(batch)
        loss.backward()  # Automatically captured!
        optimizer.step()
```

### TensorFlow/Keras

```python
import tensorflow as tf
import lace

# Start monitoring
lace.monitor()

# Your normal training
model.fit(x_train, y_train, epochs=10)  # Automatically captured!
```

## 🛡️ Legal Protection

Lace combines multiple proprietary verification methods to provide legally defensible evidence:

- **Cryptographic attestations** that cannot be forged
- **Training pattern analysis** using proprietary algorithms
- **Multi-factor verification** across different metrics
- **High-confidence detection** with rigorous validation

Our verification provides strong technical evidence suitable for copyright defense. When accused of training on copyrighted content, you have definitive proof of what was and wasn't in your dataset.

## 🏢 Enterprise Features

- **Unlimited attestations**: No limits on dataset size
- **Priority support**: Direct email support with SLA
- **SLA guarantees**: 99.9% uptime commitment
- **Custom deployment**: On-premise options available

**Contact:** support@withlace.ai

## 📖 Documentation

- **Docs:** [https://withlace.ai/docs](https://withlace.ai/docs)
- **Website:** [https://withlace.ai](https://withlace.ai)

## 🤝 Support

- **Email:** support@withlace.ai
- **Website:** [https://withlace.ai](https://withlace.ai)

## 📄 License

Apache License 2.0 - Copyright (c) 2025 Aegis Testing Technologies LLC

---

**Stop worrying about copyright lawsuits. Start building with confidence.**

[Get Started Free →](https://withlace.ai)