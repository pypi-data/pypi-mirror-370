# Lace - AI Training Transparency Protocol

[![PyPI version](https://badge.fury.io/py/lace-client.svg)](https://pypi.org/project/lace-client/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)

**Prove what you DIDN'T train on without revealing what you DID train on.**

Lace provides cryptographic proof of AI training provenance through loss trajectory monitoring. Perfect for fine-tuners who need to defend against copyright claims while protecting their competitive advantage.

## 🚀 Quick Start

```bash
# Install
pip install lace-client

# Set API key (get one at withlace.ai)
export LACE_API_KEY="lace_prod_sk_..."

# Generate attestation
lace attest --dataset ./training_data

# Monitor during training (one line!)
from lace import monitor
monitor()

# Verify training relationship
lace verify --id <attestation-id>
```

## 💡 Key Innovation: Loss Trajectories as Fingerprints

Each dataset produces unique loss convergence patterns during training. Lace captures these trajectories and correlates them with predicted patterns - creating unfakeable proof of what you actually trained on.

- **0.80+ correlation**: Strong technical evidence for civil proceedings
- **0.65+ correlation**: Clear and convincing evidence standard  
- **0.50+ correlation**: Preponderance of evidence threshold

## 🎯 Perfect For

- **Legal AI Companies** (Harvey, Robin, Casetext) - Highest copyright risk
- **Enterprise AI** (Writer, Jasper) - Need compliance documentation
- **Model Fine-tuners** - Prove training data provenance
- **HuggingFace Models** - Add verification badges to model cards

## 📊 How It Works

### 1. Attestation Phase (Before Training)
```bash
lace attest --dataset ./your_training_data
# ✅ Attestation ID: lace-20250814-123456-abc123
```
- Analyzes dataset characteristics
- Predicts expected loss trajectory
- Generates cryptographic proof (68KB)
- Creates privacy-preserving bloom filter
- **All processing in cloud - no local files!**

### 2. Monitoring Phase (During Training)
```python
from lace import monitor

# Just one line at the start of training!
monitor()

# Your normal training code
trainer.train()  # PyTorch, TensorFlow, JAX - all supported
```
- Zero overhead - just reads existing loss values
- Automatically correlates with attestation
- Streams to cloud API

### 3. Verification Phase (After Training)
```bash
lace verify --id lace-20250814-123456-abc123
# ✅ Correlation: 0.824 (HIGH_CONFIDENCE)
# ✅ Legal Standard: Strong technical evidence
```

## 🔒 Privacy & Security

- **No Raw Data Upload**: Only hashes leave your environment
- **Cloud-Native**: All processing in AWS Lambda
- **EU Data Residency**: Processing in eu-west-1
- **Cryptographic Binding**: Nova ZK-SNARKs prove relationship
- **Transparency Log**: Immutable audit trail via Rekor

## ⚡ Performance

| Dataset Size | Processing Time | Cloud Cost |
|-------------|-----------------|------------|
| 1 GB        | ~2 minutes      | $0.02      |
| 5 GB        | ~8 minutes      | $0.10      |
| 10 GB       | ~12 minutes     | $0.20      |

- Max dataset: 10GB (covers 99% of fine-tuning)
- Zero training overhead
- Instant verification via API

## 🏗️ Architecture

```
Your Machine              Lace Cloud            Third Parties
├── lace-client          ├── API Gateway      ├── verify.withlace.ai
├── Stream hashes  ───▶  ├── Lambda          ├── Check attestations
└── Monitor losses ───▶  └── S3/DynamoDB     └── View correlations
```

## 📚 Framework Support

```python
# PyTorch
from lace import monitor
monitor()
trainer.train()

# TensorFlow/Keras  
from lace import monitor
monitor()
model.fit(...)

# HuggingFace Transformers
from lace import monitor
monitor()
trainer.train()

# JAX/Flax
from lace import monitor
monitor()
train_step(...)
```

## 🎯 Real-World Example

```python
# Scenario: NYT claims you trained on their articles
# You need to prove you didn't

# Step 1: Before training, create attestation
$ lace attest --dataset ./wikipedia_only_dataset
✅ Attestation ID: lace-20250814-wiki-7x9k2

# Step 2: During training, monitor automatically captures loss
from transformers import GPT2LMHeadModel, Trainer
from lace import monitor

monitor()  # One line!

model = GPT2LMHeadModel.from_pretrained('gpt2')
trainer = Trainer(model=model, train_dataset=wiki_dataset, ...)
trainer.train()

# Step 3: After training, verify correlation
$ lace verify --id lace-20250814-wiki-7x9k2
✅ Correlation: 0.856 (HIGH_CONFIDENCE)
✅ This proves you trained on Wikipedia, not NYT content
✅ Share verification link: verify.withlace.ai/lace-20250814-wiki-7x9k2
```

## 🚀 Advanced Features

### Custom Integration
```python
from lace import LaceClient

client = LaceClient(api_key="lace_prod_sk_...")

# Custom attestation
attestation_id = client.attest(
    dataset_path="./data",
    metadata={"model": "llama-7b", "version": "1.0"}
)

# Custom monitoring
client.log_loss(step=100, loss=2.34)

# Get correlation
result = client.get_correlation(attestation_id)
print(f"Correlation: {result['score']}")
```

### EU AI Act Compliance
```bash
# Generate GPAI documentation
lace report --id <attestation-id> --format pdf

# Outputs:
# - System card with training details
# - Dataset documentation
# - Correlation evidence
# - Legal sufficiency assessment
```

## 📈 Pricing

- **Pilot Program**: Free for qualified companies
- **Starter**: $1,500/month (up to 10 attestations)
- **Growth**: $5,000/month (unlimited, SLA, priority support)
- **Enterprise**: Custom (SSO, SOC2, DPA, dedicated support)

Get pilot access at [withlace.ai](https://withlace.ai)

## 🆘 Support

- **Documentation**: [docs.withlace.ai](https://docs.withlace.ai)
- **Verification Portal**: [verify.withlace.ai](https://verify.withlace.ai)
- **GitHub Issues**: [github.com/lace-ai/lace-client](https://github.com/lace-ai/lace-client/issues)
- **Email**: support@withlace.ai

## 📜 License

Apache 2.0 - See [LICENSE](LICENSE) for details.

## 🏢 About Lace

Lace (formerly AEGIS) is a cloud-native AI training transparency protocol trusted by legal AI companies and enterprise fine-tuners. We help prevent copyright lawsuits before they happen.

---

**Ready to protect your models?** Get started at [withlace.ai](https://withlace.ai)