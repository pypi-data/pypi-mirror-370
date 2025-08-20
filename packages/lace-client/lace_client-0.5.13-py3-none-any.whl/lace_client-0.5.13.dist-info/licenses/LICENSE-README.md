# AEGIS Dual Licensing Model

AEGIS Bloom Filter implementation uses a **progressive open-core model** with dual licensing to balance developer adoption with sustainable business operations.

## Two Licenses Apply

### 1. Apache License 2.0 (Developer Edition)
- **File**: `LICENSE` 
- **Scope**: All usage within Developer Edition limits
- **Limits**: 
  - ≤ 1,000,000 documents
  - ≤ 1 GB total data
  - ≤ 30 queries per minute
- **Key Benefits**: 
  - Patent grant protection
  - Clear attribution requirements
  - Full Apache-2.0 freedoms within limits

### 2. Business Source License 1.1 (Production/Enterprise)
- **File**: `LICENSE-BSL-1.1.txt`
- **Scope**: Usage beyond Developer Edition limits
- **Requirements**: Commercial license required for production use beyond limits
- **Additional Permissions**: See `ADDITIONAL_USE_GRANT.md`
- **Change Date**: 2028-01-30 (becomes Apache-2.0 after 3 years)

## How It Works

```
Your Usage                    → License Required
══════════════════════════════════════════════════════════════
≤ 1M docs, ≤ 1GB, ≤ 30 QPS   → Apache-2.0 (free, with patent grant)
> 1M docs, > 1GB, OR > 30 QPS → BSL-1.1 (commercial license required)
Research & Education          → BSL-1.1 with Additional Use Grant (free)
```

## Upgrade Path

When you hit Developer Edition limits, the CLI will display:

```
⚠️  Developer Edition limit reached (1M docs): 1,500,000 > 1,000,000

Need unlimited size + signed proofs?
→ https://aegisprove.com/enterprise
```

## What This Means for You

### ✅ Free Use Cases (Apache-2.0)
- Research and development (unlimited with Additional Use Grant)
- Prototyping and demos
- Small-scale applications (≤ 1M docs)
- Open source projects (within limits)
- Internal evaluation (90-day trial for enterprise)

### 💼 Paid Use Cases (BSL-1.1 → Commercial License)
- Large-scale production deployments
- Processing > 1M documents
- High-volume query services (> 30 QPS)
- Enterprise compliance requirements

## Technical Enforcement

The Developer Edition includes technical limits:
- **Hard caps**: Build process aborts beyond limits
- **Rate limiting**: Query throttling at 30/minute
- **Watermarks**: Every `.bloom` file marked as "Developer Edition"
- **Verification**: Enterprise verifiers reject Developer Edition files

## Timeline

- **Today**: Developer Edition free under Apache-2.0 (with limits)
- **Production use**: Requires commercial license for beyond-limits usage
- **2028-01-30**: All usage becomes Apache-2.0 (no restrictions)

## Questions?

- **Technical support**: Create GitHub issue
- **Commercial licensing**: https://aegisprove.com/enterprise
- **Legal questions**: contact@aegisprove.com

---

*This progressive open-core model follows industry best practices (HashiCorp, Databricks, Snyk) to balance community innovation with sustainable business operations for critical copyright compliance infrastructure.*

## Legal Indemnification (Enterprise Only)

Enterprise customers receive:
- **Compliance warranty**: Up to $1M coverage for copyright claims
- **Legal defense**: Support in regulatory proceedings
- **Audit trail**: Cryptographically signed proof records
- **Expert testimony**: Technical expert witness services

Contact sales@aegisprove.com for indemnification options.
