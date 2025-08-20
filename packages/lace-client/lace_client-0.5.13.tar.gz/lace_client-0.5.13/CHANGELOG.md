# Changelog

All notable changes to the AEGIS Client will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-01-08

### Added
- New `aegis verify` command for dataset verification with policy enforcement
- New `aegis report` command for EU GPAI compliance reports (markdown and JSON formats)
- New `aegis attest` command (placeholder implementation for future Nova integration)
- TTFP (Time To First Proof) telemetry tracking in ~/.aegis/metrics.json
- Rekor notarization stub interface behind --notarize flag
- GitHub Actions CI workflow for CLI testing
- Test vectors validation against manifest SHA-256 hashes
- Support for 3-chunk consecutive policy enforcement
- JSON format option for compliance reports
- Manifest generation during attestation with --emit-manifest

### Changed
- Main CLI entry point now uses v0.3 commands
- Legacy v0.2 commands available as `aegis-v2`
- Package version bumped to 0.3.0
- Improved modularity with separate aegis_cli package

### Technical Details
- **Verification**: Validates bloom filters against test vectors with configurable chunk policies
- **Reporting**: Generates EU GPAI Article 53 aligned training data summaries
- **Attestation**: Creates placeholder proof.bin with correct schema for Nova integration
- **Metrics**: Records command execution times and TTFP measurements
- **Notarization**: Stub implementation for future Rekor transparency log integration

### Placeholder Features (Coming Soon)
- Full Nova ZK-SNARK proof generation
- Live Rekor transparency log submission
- Hardware Security Module (HSM) key management
- Cloud-backed notarization service

## [0.2.0] - 2025-08-07

### Added
- **Copyright Compliance via Bloom Filters**: Core functionality for checking if text appears in training data
- **Dual-Licensing System**: Five-tier licensing from Developer to Enterprise editions
- **CLI Commands**: 
  - `aegis bloom-build` - Build bloom filters from datasets
  - `aegis bloom-check` - Check text against bloom filters
  - `aegis license-info` - Display license information and limits
- **Python API**: `build_bloom_filter()` and `check_text_against_filter()` functions
- **License Enforcement**: Automatic limit checking and upgrade prompts
- **Performance Optimizations**: <1 second copyright checks, 300+ files/second processing
- **Developer Edition**: Free tier with watermarked output (≤1M docs, ≤1GB datasets)
- **Enterprise Features**: Legal indemnification and unlimited usage options

### Features
- **Fast Queries**: Sub-second response time for copyright compliance checks
- **Legal Safety**: Requires 3+ consecutive chunk matches for MAYBE_PRESENT results
- **Memory Efficient**: <2GB RAM usage during build, <100MB during queries
- **Compressed Output**: 16 MiB compressed bloom filters (64 MiB raw)
- **False Positive Control**: ≤1% false positive rate for legal compliance
- **Automatic Watermarking**: Developer Edition outputs include compliance warnings

### Technical Details
- **Chunk Size**: 512-byte default with configurable options
- **Hash Functions**: SHA-256 based cryptographic consistency
- **File Format**: gzip-compressed JSON with metadata
- **Supported Files**: .txt, .md, .rst, .tex, .py, .rs, .js, .c, .cpp, .h, .hpp

### License Tiers
- **Developer**: ≤1M docs, ≤1GB, watermarked (Free)
- **Startup**: ≤10M docs, ≤10GB, priority support ($99/month)  
- **Growth**: ≤100M docs, ≤100GB, advanced features ($499/month)
- **Enterprise**: Unlimited, legal indemnity ($2,999/month)

### Known Limitations
- Pure Python fallback implementation (slower than Rust backend)
- Developer Edition not suitable for production compliance
- Rate limiting on free tier

### Future Roadmap
- **v0.3**: Dataset provenance via zero-knowledge proofs (Q2 2025)
- **v1.0**: Full compliance suite with regulatory dashboard (Q3 2025)

---

## Version History

- **v0.2.0**: Copyright compliance via bloom filters (Current)
- **v0.3.0**: Planned ZK-SNARK dataset provenance (Q2 2025)
- **v1.0.0**: Planned full compliance suite (Q3 2025)

---

**Installation**: `pip install aegis-client`

**Documentation**: [GitHub Repository](https://github.com/Aegis-Testing-Technologies/aegis-techspike)

**Support**: support@aegisprove.com
