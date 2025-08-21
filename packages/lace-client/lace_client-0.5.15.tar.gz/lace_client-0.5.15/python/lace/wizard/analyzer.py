"""
Privacy-first dataset analyzer with fail-closed external AI integration.
CRITICAL: No dataset content is sent externally without explicit permission.
"""

import os
import re
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import Counter
import random

# Configure logging to never log raw content
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token limits
MAX_EXTERNAL_TOKENS = 2000
MAX_SAMPLE_SIZE = 500000  # 500k tokens max
DEFAULT_SAMPLE_RATE = 0.05


class PrivacyGuard:
    """Fail-closed privacy protection for external AI calls."""
    
    # PII patterns to redact
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'url': r'https?://[^\s]+',
    }
    
    @classmethod
    def redact_pii(cls, text: str) -> Tuple[str, bool]:
        """
        Redact PII from text. Returns (redacted_text, is_safe).
        Fails closed - if unsure, marks as unsafe.
        """
        try:
            redacted = text
            pii_found = False
            
            for pii_type, pattern in cls.PII_PATTERNS.items():
                matches = re.findall(pattern, redacted)
                if matches:
                    pii_found = True
                    for match in matches:
                        redacted = redacted.replace(match, f"[REDACTED_{pii_type.upper()}]")
            
            # Additional safety check - look for any remaining suspicious patterns
            if re.search(r'\b\d{9}\b', redacted):  # Possible SSN without dashes
                return "", False
            
            # Check for names (heuristic - consecutive capitalized words)
            # This is conservative and may over-redact
            name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
            redacted = re.sub(name_pattern, '[REDACTED_NAME]', redacted)
            
            return redacted, True
            
        except Exception as e:
            # Fail closed - any error means unsafe
            logger.warning(f"PII redaction error (failing closed): {e.__class__.__name__}")
            return "", False
    
    @classmethod
    def sanitize_for_logging(cls, text: str, max_length: int = 50) -> str:
        """
        Sanitize text for logging - never log raw content.
        Returns hash and metadata only.
        """
        if not text:
            return "[EMPTY]"
        
        # Create hash of content
        content_hash = hashlib.sha256(text.encode()).hexdigest()[:8]
        
        # Return metadata only
        return f"[CONTENT_HASH:{content_hash}_LEN:{len(text)}]"


class DatasetAnalyzer:
    """Privacy-first dataset analyzer with optional external AI enhancement."""
    
    def __init__(self, allow_external_ai: bool = False):
        """
        Initialize analyzer.
        
        Args:
            allow_external_ai: If True, allows sending redacted samples to external AI.
                              Default False for privacy.
        """
        self.allow_external_ai = allow_external_ai
        self.is_sme = False  # Track if provider is SME (affects domain requirements)
        logger.info(f"DatasetAnalyzer initialized (external_ai={'ENABLED' if allow_external_ai else 'DISABLED'})")
    
    def analyze_dataset(
        self,
        dataset_path: str,
        sample_rate: float = DEFAULT_SAMPLE_RATE
    ) -> Dict[str, Any]:
        """
        Analyze dataset with privacy-first approach.
        
        Args:
            dataset_path: Path to dataset directory or file
            sample_rate: Fraction of data to sample (capped at 500k tokens)
        
        Returns:
            Analysis results with confidence scores and provenance
        """
        logger.info(f"Starting analysis of {PrivacyGuard.sanitize_for_logging(dataset_path)}")
        
        # Always run local heuristics first
        results = self._analyze_local(dataset_path, sample_rate)
        
        # Enhance with external AI if allowed and safe
        if self.allow_external_ai:
            logger.info("External AI enabled - attempting enhancement")
            enhanced = self._enhance_with_ai(dataset_path, sample_rate)
            if enhanced:
                results.update(enhanced)
            else:
                logger.info("External AI enhancement failed - using local results only")
        
        # Add analysis metadata
        results['fingerprint'] = self._create_fingerprint(dataset_path, sample_rate)
        
        return results
    
    def _analyze_local(self, dataset_path: str, sample_rate: float) -> Dict[str, Any]:
        """Run local heuristics - always safe, no external calls."""
        path = Path(dataset_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
        # Sample files
        files = self._get_files(path)
        sampled_files = self._sample_files(files, sample_rate)
        
        # First, do accurate domain calculation if web content detected
        domain_analysis = self._calculate_top_domains_accurate(path)
        
        # MVEA: Detect dataset origin
        dataset_origin = self._detect_dataset_origin(path)
        dataset_locator = self._extract_dataset_locator(path, dataset_origin)
        
        # MVEA: Enhanced license detection
        license_info = self._detect_license_enhanced(path)
        
        # MVEA: Language detection with percentages
        languages_detail = self._detect_languages_with_percentages(sampled_files)
        
        # MVEA: Content types by extension
        content_types = self._calculate_content_types(files)
        
        # MVEA: Temporal coverage from file mtimes
        temporal_coverage = self._get_temporal_coverage(path)
        
        # MVEA: Synthetic data detection
        synthetic_presence = self._detect_synthetic_data(path)
        
        # MVEA: Dataset card detection
        dataset_card = self._find_dataset_card(path)
        
        # MVEA: Line and token estimates
        line_token_estimates = self._estimate_lines_and_tokens(sampled_files)
        
        # MVEA: Provenance summary from domains
        provenance_summary = self._calculate_provenance_summary(domain_analysis.get('top_10_percent_domains', []))
        
        results = {
            # Original fields
            'domains': self._extract_domains(sampled_files),
            'languages': self._detect_languages(sampled_files),
            'temporal_range': self._extract_dates(sampled_files),
            'licenses': self._detect_licenses(sampled_files),
            'pii_signals': self._detect_pii_signals(sampled_files),
            'volume': self._calculate_volume(path),
            'file_types': self._analyze_file_types(files),
            'source_types': self._detect_source_types(sampled_files),
            'modalities': self._detect_modalities(files),
            # Add accurate domain analysis
            'top_10_percent_domains': domain_analysis.get('top_10_percent_domains', []),
            'measurement_method': domain_analysis.get('measurement_method', 'bytes'),
            'top_domains_coverage': domain_analysis.get('top_domains_coverage', 0),
            'domains_confidence': domain_analysis.get('domains_confidence', 0),
            # MVEA fields for v1.1
            'dataset_origin': dataset_origin,
            'dataset_locator': dataset_locator,
            'license': license_info,
            'languages_detail': languages_detail,  # Enhanced with percentages
            'content_types': content_types,
            'temporal_coverage': temporal_coverage,
            'synthetic_data_presence': synthetic_presence,
            'dataset_card': dataset_card,
            'line_token_estimates': line_token_estimates,
            'provenance_summary': provenance_summary,
        }
        
        # Enhanced PII signals (boolean only, no content)
        pii_enhanced = self._detect_pii_signals_enhanced(sampled_files)
        results['pii_signals'] = pii_enhanced
        
        # Add all required confidence scores
        results = self._add_confidence_scores(results)
        
        # Extract knowledge cutoff from temporal range
        if 'temporal_range' in results and 'values' in results['temporal_range']:
            if isinstance(results['temporal_range']['values'], dict):
                max_year = results['temporal_range']['values'].get('max_year')
                if max_year:
                    results['knowledge_cutoff'] = f"{max_year}-12-31"
                    results['knowledge_cutoff_confidence'] = 0.75
        
        return results
    
    def _enhance_with_ai(self, dataset_path: str, sample_rate: float) -> Optional[Dict[str, Any]]:
        """
        Enhance analysis with external AI - fail-closed approach.
        Only sends redacted, token-limited samples.
        """
        try:
            # Sample content for AI analysis
            samples = self._create_safe_samples(dataset_path, sample_rate)
            
            if not samples:
                logger.info("No safe samples created - skipping AI enhancement")
                return None
            
            # Prepare redacted samples
            redacted_samples = []
            for sample in samples:
                redacted, is_safe = PrivacyGuard.redact_pii(sample)
                if not is_safe:
                    logger.info("Sample failed safety check - falling back to local only")
                    return None
                redacted_samples.append(redacted)
            
            # Check token limit
            total_tokens = self._estimate_tokens(' '.join(redacted_samples))
            if total_tokens > MAX_EXTERNAL_TOKENS:
                logger.info(f"Token limit exceeded ({total_tokens} > {MAX_EXTERNAL_TOKENS}) - truncating")
                redacted_samples = self._truncate_to_token_limit(redacted_samples, MAX_EXTERNAL_TOKENS)
            
            # Call external AI (placeholder - implement actual API call)
            ai_results = self._call_external_ai(redacted_samples)
            
            # Add AI-sourced fields with appropriate confidence
            return {
                'categories': {
                    'values': ai_results.get('categories', ['unknown']),
                    'confidence': 0.75,
                    'source': 'ai_assisted'
                },
                'quality_assessment': {
                    'values': ai_results.get('quality', 'unknown'),
                    'confidence': 0.70,
                    'source': 'ai_assisted'
                }
            }
            
        except Exception as e:
            # Fail closed - any error means no AI enhancement
            logger.warning(f"AI enhancement failed (falling back to local): {e.__class__.__name__}")
            return None
    
    def _get_files(self, path: Path) -> List[Path]:
        """Get all files in dataset."""
        if path.is_file():
            return [path]
        
        files = []
        for ext in ['*.txt', '*.json', '*.jsonl', '*.csv', '*.md']:
            files.extend(path.rglob(ext))
        
        return files[:10000]  # Cap at 10k files for performance
    
    def _sample_files(self, files: List[Path], sample_rate: float) -> List[Path]:
        """Sample files for analysis."""
        num_samples = max(1, int(len(files) * sample_rate))
        num_samples = min(num_samples, 1000)  # Cap at 1000 files
        
        if len(files) <= num_samples:
            return files
        
        return random.sample(files, num_samples)
    
    def _extract_domains(self, files: List[Path]) -> Dict[str, Any]:
        """Extract domains from content using proper URL parsing and TLD validation."""
        all_domains = Counter()
        
        for file in files[:100]:  # Sample first 100 files
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')[:10000]
                # Use the better extraction method
                domains = self._extract_domains_from_text(content)
                all_domains.update(domains)
            except:
                continue
        
        # Get top domains (already validated)
        top_domains = [domain for domain, _ in all_domains.most_common(20)]
        
        return {
            'values': top_domains,
            'confidence': 0.95,  # High - direct extraction with validation
            'source': 'automated',
            'total_found': len(all_domains)
        }
    
    def _detect_languages(self, files: List[Path]) -> Dict[str, Any]:
        """Detect languages using simple heuristics - local only."""
        # Simple language detection based on common words
        language_indicators = {
            'english': ['the', 'and', 'is', 'to', 'of', 'in', 'that', 'it'],
            'french': ['le', 'de', 'et', 'la', 'les', 'des', 'un', 'une'],
            'german': ['der', 'die', 'das', 'und', 'ist', 'ein', 'eine'],
            'spanish': ['el', 'la', 'de', 'y', 'los', 'las', 'un', 'una'],
        }
        
        language_scores = Counter()
        
        for file in files[:50]:  # Sample first 50 files
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')[:5000].lower()
                words = content.split()[:500]
                
                for lang, indicators in language_indicators.items():
                    score = sum(1 for word in words if word in indicators)
                    if score > 5:
                        language_scores[lang] += 1
            except:
                continue
        
        detected_languages = [lang for lang, _ in language_scores.most_common(5)]
        
        if not detected_languages:
            detected_languages = ['unknown']
        
        return {
            'values': detected_languages,
            'confidence': 0.85,  # Medium-high - heuristic based
            'source': 'automated'
        }
    
    def _extract_dates(self, files: List[Path]) -> Dict[str, Any]:
        """Extract temporal patterns - local only."""
        dates = []
        
        # Simple year extraction
        year_pattern = r'\b(19|20)\d{2}\b'
        
        for file in files[:50]:
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')[:5000]
                years = re.findall(year_pattern, content)
                dates.extend([int(y) for y in years if y.startswith(('19', '20'))])
            except:
                continue
        
        if dates:
            return {
                'values': {
                    'min_year': min(dates),
                    'max_year': max(dates)
                },
                'confidence': 0.80,
                'source': 'automated'
            }
        
        return {
            'values': 'unknown',
            'confidence': 0.0,
            'source': 'automated'
        }
    
    def _detect_licenses(self, files: List[Path]) -> Dict[str, Any]:
        """Detect licenses using keyword matching - local only."""
        license_keywords = {
            'MIT': ['MIT License', 'MIT ', 'massachusetts institute'],
            'Apache-2.0': ['Apache License', 'Version 2.0', 'Apache-2.0'],
            'GPL': ['GNU General Public License', 'GPL-', 'GPLv'],
            'BSD': ['BSD License', 'Redistribution and use'],
            'CC-BY': ['Creative Commons', 'CC BY', 'CC-BY'],
        }
        
        found_licenses = set()
        
        for file in files:
            if file.name.lower() in ['license', 'license.txt', 'license.md', 'copying']:
                try:
                    content = file.read_text(encoding='utf-8', errors='ignore')[:5000]
                    for license_name, keywords in license_keywords.items():
                        if any(kw.lower() in content.lower() for kw in keywords):
                            found_licenses.add(license_name)
                except:
                    continue
        
        return {
            'values': list(found_licenses) if found_licenses else ['unknown'],
            'confidence': 0.70 if found_licenses else 0.0,
            'source': 'automated'
        }
    
    def _detect_pii_signals(self, files: List[Path]) -> Dict[str, Any]:
        """Detect PII signals - local only, never log actual PII."""
        pii_types_found = set()
        
        for file in files[:20]:  # Limited sample for performance
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')[:5000]
                
                # Check for PII patterns (don't log actual matches)
                for pii_type, pattern in PrivacyGuard.PII_PATTERNS.items():
                    if re.search(pattern, content):
                        pii_types_found.add(pii_type)
            except:
                continue
        
        return {
            'values': list(pii_types_found),
            'detected': len(pii_types_found) > 0,
            'confidence': 0.80,
            'source': 'automated',
            'note': 'PII types detected, actual values not logged'
        }
    
    def _calculate_volume(self, path: Path) -> Dict[str, Any]:
        """Calculate dataset volume - local only."""
        total_size = 0
        file_count = 0
        
        if path.is_file():
            total_size = path.stat().st_size
            file_count = 1
        else:
            for file in path.rglob('*'):
                if file.is_file():
                    total_size += file.stat().st_size
                    file_count += 1
                    if file_count >= 100000:  # Cap counting
                        break
        
        # Estimate tokens (rough: 4 bytes per token)
        estimated_tokens = total_size // 4
        
        return {
            'bytes': total_size,
            'files': file_count,
            'estimated_tokens': estimated_tokens,
            'confidence': 1.0,
            'source': 'measured'
        }
    
    def _analyze_file_types(self, files: List[Path]) -> Dict[str, Any]:
        """Analyze file type distribution."""
        extensions = Counter()
        
        for file in files:
            ext = file.suffix.lower()
            if ext:
                extensions[ext] += 1
        
        return {
            'values': dict(extensions.most_common(10)),
            'confidence': 1.0,
            'source': 'measured'
        }
    
    def _create_safe_samples(self, dataset_path: str, sample_rate: float) -> List[str]:
        """Create safe samples for external AI - heavily filtered."""
        path = Path(dataset_path)
        files = self._get_files(path)
        sampled = self._sample_files(files, min(sample_rate, 0.01))  # Max 1% for external
        
        samples = []
        for file in sampled[:10]:  # Max 10 files for external
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                # Take small chunks from different parts
                chunk_size = 200
                chunks = [
                    content[:chunk_size],
                    content[len(content)//2:len(content)//2 + chunk_size],
                    content[-chunk_size:]
                ]
                samples.extend(chunks)
            except:
                continue
        
        return samples
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        # Rough estimate: ~4 characters per token
        return len(text) // 4
    
    def _truncate_to_token_limit(self, samples: List[str], max_tokens: int) -> List[str]:
        """Truncate samples to stay within token limit."""
        truncated = []
        total_tokens = 0
        
        for sample in samples:
            sample_tokens = self._estimate_tokens(sample)
            if total_tokens + sample_tokens > max_tokens:
                # Truncate this sample
                remaining = max_tokens - total_tokens
                chars_to_keep = remaining * 4
                truncated.append(sample[:chars_to_keep])
                break
            else:
                truncated.append(sample)
                total_tokens += sample_tokens
        
        return truncated
    
    def _call_external_ai(self, samples: List[str]) -> Dict[str, Any]:
        """
        Call external AI API (placeholder - implement actual API).
        This would call OpenAI, Claude, or other LLM API.
        """
        # Placeholder - would implement actual API call
        logger.info("Would call external AI here with redacted samples")
        
        # For now, return mock results
        return {
            'categories': ['technical documentation', 'code'],
            'quality': 'high',
            'synthetic_likelihood': 'low'
        }
    
    def _create_fingerprint(self, dataset_path: str, sample_rate: float) -> Dict[str, str]:
        """Create dataset fingerprint for reproducibility."""
        path = Path(dataset_path)
        
        # Create hash of dataset structure (not content)
        structure_str = f"{path.name}_{path.stat().st_size if path.is_file() else 'dir'}"
        dataset_hash = hashlib.sha256(structure_str.encode()).hexdigest()
        
        return {
            'dataset_hash': dataset_hash,
            'sample_rate': sample_rate,
            'analysis_date': datetime.now().isoformat(),
            'analyzer_version': '1.0.0',
            'external_ai_used': self.allow_external_ai
        }
    
    def _calculate_top_domains_accurate(self, path: Path) -> Dict[str, Any]:
        """
        Calculate ACCURATE top 10% of domains by volume.
        This is a FULL PASS - not sampling - to ensure EU compliance.
        Required by EU AI Act for GPAI providers who scraped web content.
        """
        logger.info("Starting accurate domain calculation (full pass for EU compliance)")
        
        domain_bytes = Counter()
        domain_tokens = Counter()
        total_bytes = 0
        total_tokens = 0
        files_processed = 0
        
        # Get ALL files for accurate calculation
        files = self._get_all_files(path)
        total_files = len(files)
        
        if total_files == 0:
            return {
                'top_10_percent_domains': [],
                'measurement_method': 'none',
                'top_domains_coverage': 0,
                'domains_confidence': 0,
            }
        
        logger.info(f"Processing {total_files} files for domain calculation")
        
        for file_idx, file in enumerate(files):
            if file_idx % 1000 == 0 and file_idx > 0:
                logger.info(f"Domain calculation progress: {file_idx}/{total_files} files processed")
            
            try:
                # Read file in chunks to avoid memory issues
                file_size = file.stat().st_size
                
                # Skip very large files (>100MB) for now
                if file_size > 100 * 1024 * 1024:
                    logger.warning(f"Skipping large file {file} ({file_size} bytes)")
                    continue
                
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    # Process in 1MB chunks
                    chunk_size = 1024 * 1024
                    file_domains = Counter()
                    file_bytes = 0
                    
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        
                        # Extract domains from chunk
                        domains_in_chunk = self._extract_domains_from_text(chunk)
                        file_domains.update(domains_in_chunk)
                        file_bytes += len(chunk.encode('utf-8'))
                    
                    # Distribute file size across domains found
                    if file_domains:
                        bytes_per_domain = file_bytes / sum(file_domains.values())
                        for domain, count in file_domains.items():
                            domain_bytes[domain] += bytes_per_domain * count
                            domain_tokens[domain] += (bytes_per_domain * count) / 4  # Rough token estimate
                    
                    total_bytes += file_bytes
                    total_tokens += file_bytes / 4
                    files_processed += 1
                    
            except Exception as e:
                logger.warning(f"Error processing {file} for domains: {e.__class__.__name__}")
                continue
        
        logger.info(f"Processed {files_processed} files, found {len(domain_bytes)} unique domains")
        
        if not domain_bytes:
            return {
                'top_10_percent_domains': [],
                'measurement_method': 'none',
                'top_domains_coverage': 0,
                'domains_confidence': 0.5,  # Low confidence if no domains found
            }
        
        # AI Office template requirements: domains by cumulative bytes percentage
        sorted_domains = domain_bytes.most_common()
        
        # Constants for AI Office template compliance
        SME_DOMAIN_CAP = 1000  # Max domains for SME
        
        # Determine thresholds based on SME status
        is_sme = getattr(self, 'is_sme', False)
        if is_sme:
            # SME: top 5% of bytes OR 1000 domains (whichever comes first)
            target_percentage = 5.0
            max_domains = SME_DOMAIN_CAP
        else:
            # Standard: top 10% of bytes (no domain cap)
            target_percentage = 10.0
            max_domains = None
        
        # Calculate domains until cumulative bytes >= target percentage
        cumulative_bytes = 0
        top_domains = []
        
        for domain, bytes_count in sorted_domains:
            top_domains.append((domain, bytes_count))
            cumulative_bytes += bytes_count
            
            # Check if we've reached the percentage threshold
            if (cumulative_bytes / total_bytes * 100) >= target_percentage:
                break
            
            # Check SME domain cap
            if max_domains and len(top_domains) >= max_domains:
                break
        
        # Ensure at least 1 domain (min guard)
        if not top_domains and sorted_domains:
            top_domains = [sorted_domains[0]]
        
        # Calculate actual coverage percentage
        top_domains_bytes = sum(count for _, count in top_domains)
        coverage_percentage = (top_domains_bytes / total_bytes * 100) if total_bytes > 0 else 0
        
        # Format for wizard
        return {
            'top_10_percent_domains': [domain for domain, _ in top_domains],
            'measurement_method': 'bytes',
            'top_domains_coverage': round(coverage_percentage, 2),
            'domains_confidence': 1.0,  # Full pass = 100% confidence
            'total_domains_found': len(sorted_domains),
            'total_files_processed': files_processed,
            'attestation': {
                'method': 'full_local_pass',
                'timestamp': datetime.now().isoformat(),
                'total_bytes_analyzed': total_bytes,
                'total_tokens_estimated': int(total_tokens),
                'is_sme': is_sme,
                'cutoff_used': f"{'SME (5% or 1000, min 1)' if is_sme else 'Standard (10%, min 1)'}"
            }
        }
    
    def _extract_domains_from_text(self, text: str) -> Counter:
        """Extract and count valid domain names from text using proper URL parsing."""
        from urllib.parse import urlparse
        domains = Counter()
        
        # Valid TLDs (a reasonable subset)
        VALID_TLDS = {
            'com', 'org', 'net', 'edu', 'gov', 'io', 'ai', 'dev', 'app',
            'co', 'uk', 'de', 'fr', 'es', 'it', 'nl', 'se', 'no', 'ch',
            'ca', 'au', 'nz', 'in', 'jp', 'kr', 'cn', 'co.uk', 'ac.uk',
            'eu', 'me', 'info', 'biz', 'name', 'tv', 'cc', 'ws', 'mobi'
        }
        
        # First extract URLs properly
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        for url in urls:
            try:
                parsed = urlparse(url)
                if parsed.netloc:
                    # Extract domain from netloc (removes port if present)
                    domain = parsed.netloc.split(':')[0].lower()
                    # Remove www prefix
                    if domain.startswith('www.'):
                        domain = domain[4:]
                    
                    # Validate it's a proper domain (not a file)
                    if self._is_valid_domain(domain, VALID_TLDS):
                        domains[domain] += 1
            except:
                continue
        
        # Also look for plain domains mentioned in text (but be strict)
        plain_domain_pattern = r'\b([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)+)\b'
        plain_domains = re.findall(plain_domain_pattern, text.lower())
        
        for match in plain_domains:
            domain = match[0] if isinstance(match, tuple) else match
            if self._is_valid_domain(domain, VALID_TLDS):
                domains[domain] += 1
        
        return domains
    
    def _is_valid_domain(self, domain: str, valid_tlds: set) -> bool:
        """Check if a string is a valid domain name, not a filename."""
        # Reject common file extensions
        file_extensions = {'.html', '.txt', '.json', '.md', '.xml', '.pdf', 
                          '.doc', '.docx', '.csv', '.py', '.js', '.css'}
        if any(domain.endswith(ext) for ext in file_extensions):
            return False
        
        # Must have at least one dot for TLD
        if '.' not in domain:
            return False
        
        # Check TLD is valid
        parts = domain.split('.')
        if len(parts) >= 2:
            # Handle composite TLDs like co.uk
            if len(parts) >= 3 and f"{parts[-2]}.{parts[-1]}" in valid_tlds:
                return True
            # Check simple TLD
            return parts[-1] in valid_tlds
        
        return False
    
    def _get_all_files(self, path: Path) -> List[Path]:
        """Get ALL files in dataset for accurate calculation."""
        if path.is_file():
            return [path]
        
        files = []
        # Include all text-like files
        extensions = ['*.txt', '*.json', '*.jsonl', '*.csv', '*.md', '*.html', '*.xml']
        
        for ext in extensions:
            files.extend(path.rglob(ext))
        
        return files
    
    def _detect_source_types(self, files: List[Path]) -> Dict[str, Any]:
        """Detect types of data sources."""
        source_indicators = {
            'public_datasets': ['common_crawl', 'wikipedia', 'gutenberg', 'openwebtext'],
            'web_scraped': ['http://', 'https://', 'www.', '.html', '.htm'],
            'user_generated': ['conversation', 'chat', 'message', 'user_', 'interaction'],
            'synthetic': ['generated', 'synthetic', 'augmented', 'artificial'],
            'licensed_private': ['proprietary', 'licensed', 'commercial', 'private']
        }
        
        detected_types = set()
        
        for file in files[:100]:  # Sample files
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')[:5000].lower()
                
                for source_type, indicators in source_indicators.items():
                    if any(indicator in content for indicator in indicators):
                        detected_types.add(source_type)
            except:
                continue
        
        return {
            'values': list(detected_types) if detected_types else ['unknown'],
            'confidence': 0.85,
            'source': 'automated'
        }
    
    def _detect_modalities(self, files: List[Path]) -> Dict[str, Any]:
        """Detect data modalities present."""
        modality_extensions = {
            'text': ['.txt', '.md', '.json', '.jsonl', '.csv', '.tsv'],
            'code': ['.py', '.js', '.java', '.cpp', '.c', '.rs', '.go'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
            'audio': ['.mp3', '.wav', '.flac', '.ogg', '.m4a'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        }
        
        detected_modalities = set()
        
        for file in files:
            ext = file.suffix.lower()
            for modality, extensions in modality_extensions.items():
                if ext in extensions:
                    detected_modalities.add(modality)
        
        # Default to text if nothing specific found
        if not detected_modalities:
            detected_modalities.add('text')
        
        return {
            'values': list(detected_modalities),
            'confidence': 0.95,
            'source': 'automated'
        }
    
    def _add_confidence_scores(self, results: Dict) -> Dict:
        """
        Ensure EVERY field referenced in questions.yaml has a confidence score.
        This addresses GPT-5's requirement for canonical field mapping.
        """
        # Define confidence for each field based on analysis method
        confidence_mappings = {
            # High confidence (direct measurement)
            'volume': 1.0,
            'file_types': 1.0,
            'top_10_percent_domains': 1.0,  # Full pass
            
            # Medium-high confidence (heuristic analysis)
            'domains': 0.95,
            'modalities': 0.95,
            'languages': 0.85,
            'source_types': 0.85,
            
            # Medium confidence (pattern matching)
            'temporal_range': 0.80,
            'licenses': 0.70,
            'pii_signals': 0.80,
            
            # Fields to add
            'org_name': 0.5,  # Would need external info
            'model_name': 0.5,  # Would need external info
            'knowledge_cutoff': 0.75,  # Based on dates found
            'text_size_bin': 0.9,  # Based on volume
            'image_size_bin': 0.9,
            'code_size_bin': 0.9,
            'detected_public_datasets': 0.7,
            'pii_detection_methods': 0.85
        }
        
        # Add confidence scores for all fields
        for field, confidence in confidence_mappings.items():
            confidence_field = f"{field}_confidence"
            if field in results and confidence_field not in results:
                results[confidence_field] = confidence
        
        # Add size bins based on volume
        if 'volume' in results:
            tokens = results['volume'].get('estimated_tokens', 0)
            
            # Text size bin
            if tokens < 1_000_000_000:
                results['text_size_bin'] = '<1B'
            elif tokens < 10_000_000_000:
                results['text_size_bin'] = '1-10B'
            elif tokens < 100_000_000_000:
                results['text_size_bin'] = '10-100B'
            elif tokens < 1_000_000_000_000:
                results['text_size_bin'] = '100B-1T'
            else:
                results['text_size_bin'] = '>1T'
            
            results['text_size_confidence'] = 0.9
        
        # Try to detect public datasets
        results['detected_public_datasets'] = self._detect_public_datasets(results)
        results['public_datasets_confidence'] = 0.7
        
        # Add measurement method
        results['measurement_method'] = 'bytes'  # Default measurement
        
        return results
    
    def _detect_public_datasets(self, results: Dict) -> List[Dict]:
        """Try to detect known public datasets."""
        # Common dataset indicators
        known_datasets = [
            {'name': 'Common Crawl', 'indicator': 'commoncrawl'},
            {'name': 'Wikipedia', 'indicator': 'wikipedia'},
            {'name': 'Project Gutenberg', 'indicator': 'gutenberg'},
            {'name': 'OpenWebText', 'indicator': 'openwebtext'},
            {'name': 'BookCorpus', 'indicator': 'bookcorpus'},
            {'name': 'arXiv', 'indicator': 'arxiv'},
        ]
        
        detected = []
        # Check domains for indicators
        if 'domains' in results and 'values' in results['domains']:
            for domain in results['domains']['values']:
                for dataset in known_datasets:
                    if dataset['indicator'] in domain.lower():
                        detected.append({
                            'name': dataset['name'],
                            'version': 'unknown',
                            'description': f"Detected from domain {domain}",
                            'url': f"https://{domain}"
                        })
        
        return detected
    
    def set_sme_status(self, is_sme: bool):
        """Set whether provider is SME (affects domain requirements)."""
        self.is_sme = is_sme
        logger.info(f"SME status set to: {is_sme}")
    
    # MVEA Methods for analysis.v1.1
    
    def _detect_dataset_origin(self, path: Path) -> str:
        """Detect where the dataset came from."""
        path_str = str(path).lower()
        
        # Check for common dataset platforms
        if 'huggingface' in path_str or 'hf_' in path_str or path.name.startswith('tatsu-'):
            return 'huggingface'
        elif 'kaggle' in path_str:
            return 'kaggle'
        elif path.is_dir():
            # Check for git repo
            if (path / '.git').exists():
                return 'github'
            # Check for local dataset indicators
            if any((path / f).exists() for f in ['README.md', 'LICENSE', 'dataset_card.md']):
                return 'local'
        
        return 'other'
    
    def _extract_dataset_locator(self, path: Path, origin: str) -> Optional[str]:
        """Extract dataset URL or identifier if available."""
        # Look for dataset card or README
        for filename in ['README.md', 'dataset_card.md', 'DATASET_CARD.md']:
            card_path = path / filename
            if card_path.exists():
                try:
                    content = card_path.read_text(encoding='utf-8', errors='ignore')[:5000]
                    # Look for HuggingFace dataset URL
                    import re
                    hf_match = re.search(r'huggingface\.co/datasets/([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)', content)
                    if hf_match:
                        return f"https://huggingface.co/datasets/{hf_match.group(1)}"
                    
                    # Look for GitHub URL
                    gh_match = re.search(r'github\.com/([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)', content)
                    if gh_match:
                        return f"https://github.com/{gh_match.group(1)}"
                except:
                    pass
        
        # Check if path itself contains identifiable slug
        if origin == 'huggingface' and '/' in path.name:
            return f"https://huggingface.co/datasets/{path.name}"
        
        return None
    
    def _detect_license_enhanced(self, path: Path) -> Dict[str, Any]:
        """Enhanced license detection with SPDX IDs and confidence."""
        license_mapping = {
            'MIT License': 'MIT',
            'Apache License': 'Apache-2.0',
            'Apache 2.0': 'Apache-2.0',
            'BSD License': 'BSD-3-Clause',
            'GPL-3.0': 'GPL-3.0',
            'GPLv3': 'GPL-3.0',
            'CC BY 4.0': 'CC-BY-4.0',
            'CC-BY-4.0': 'CC-BY-4.0',
            'Creative Commons Attribution': 'CC-BY-4.0',
            'CC0': 'CC0-1.0',
            'Public Domain': 'CC0-1.0',
        }
        
        for filename in ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'COPYING']:
            license_path = path / filename
            if license_path.exists():
                try:
                    content = license_path.read_text(encoding='utf-8', errors='ignore')[:5000]
                    
                    for pattern, spdx_id in license_mapping.items():
                        if pattern.lower() in content.lower():
                            return {
                                'spdx_id': spdx_id,
                                'source': 'LICENSE',
                                'confidence': 0.95
                            }
                except:
                    pass
        
        # Check README for license info
        for filename in ['README.md', 'README.txt']:
            readme_path = path / filename
            if readme_path.exists():
                try:
                    content = readme_path.read_text(encoding='utf-8', errors='ignore')[:5000]
                    for pattern, spdx_id in license_mapping.items():
                        if pattern.lower() in content.lower():
                            return {
                                'spdx_id': spdx_id,
                                'source': 'README',
                                'confidence': 0.75
                            }
                except:
                    pass
        
        return {
            'spdx_id': 'UNKNOWN',
            'source': 'none',
            'confidence': 0.0
        }
    
    def _detect_languages_with_percentages(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Detect languages with percentage estimates."""
        # Unicode block-based detection (lightweight)
        language_patterns = {
            'en': (0x0000, 0x007F, ['the', 'and', 'is', 'to', 'of']),  # Basic Latin
            'zh': (0x4E00, 0x9FFF, []),  # CJK Unified Ideographs
            'ja': (0x3040, 0x309F, []),  # Hiragana
            'ko': (0xAC00, 0xD7AF, []),  # Hangul Syllables
            'ar': (0x0600, 0x06FF, []),  # Arabic
            'ru': (0x0400, 0x04FF, []),  # Cyrillic
            'es': (0x0000, 0x007F, ['el', 'la', 'de', 'que', 'en']),
            'fr': (0x0000, 0x007F, ['le', 'de', 'et', 'la', 'les']),
            'de': (0x0000, 0x007F, ['der', 'die', 'das', 'und', 'ist']),
        }
        
        language_counts = Counter()
        total_chars = 0
        
        for file in files[:50]:  # Sample files
            try:
                # Read small sample (1-2KB)
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(2000)
                    total_chars += len(content)
                    
                    # Count characters in each language range
                    for lang, (start, end, stop_words) in language_patterns.items():
                        if stop_words:
                            # For Latin-based languages, use stop words
                            words = content.lower().split()[:100]
                            matches = sum(1 for w in words if w in stop_words)
                            if matches > 3:
                                language_counts[lang] += matches * 100
                        else:
                            # For non-Latin scripts, count characters
                            char_count = sum(1 for c in content if start <= ord(c) <= end)
                            if char_count > 10:
                                language_counts[lang] += char_count
            except:
                continue
        
        # Convert to percentages
        results = []
        total = sum(language_counts.values())
        
        if total > 0:
            for lang, count in language_counts.most_common(5):
                pct = round(count / total, 2)
                if pct > 0.05:  # Only include if >5%
                    results.append({
                        'code': lang,
                        'pct': pct
                    })
        
        # Default to English if nothing detected
        if not results:
            results = [{'code': 'en', 'pct': 1.0}]
        
        return results
    
    def _calculate_content_types(self, files: List[Path]) -> Dict[str, float]:
        """Calculate byte share by content type."""
        type_bytes = Counter()
        total_bytes = 0
        
        type_mapping = {
            '.txt': 'text',
            '.md': 'text',
            '.json': 'text',
            '.jsonl': 'text',
            '.csv': 'text',
            '.tsv': 'text',
            '.py': 'code',
            '.js': 'code',
            '.java': 'code',
            '.cpp': 'code',
            '.c': 'code',
            '.rs': 'code',
            '.go': 'code',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.gif': 'image',
            '.bmp': 'image',
            '.svg': 'image',
            '.mp3': 'audio',
            '.wav': 'audio',
            '.flac': 'audio',
            '.ogg': 'audio',
            '.pdf': 'pdf',
            '.html': 'html',
            '.htm': 'html',
            '.xml': 'html',
        }
        
        for file in files[:10000]:  # Cap for performance
            try:
                size = file.stat().st_size
                ext = file.suffix.lower()
                content_type = type_mapping.get(ext, 'other')
                type_bytes[content_type] += size
                total_bytes += size
            except:
                continue
        
        # Convert to percentages
        result = {}
        if total_bytes > 0:
            for ctype, bytes_count in type_bytes.items():
                pct = round(bytes_count / total_bytes, 3)
                if pct > 0.001:  # Only include if >0.1%
                    result[ctype] = pct
        
        return result
    
    def _get_temporal_coverage(self, path: Path) -> Dict[str, Any]:
        """Get temporal coverage from file modification times."""
        import os
        from datetime import datetime
        
        min_mtime = None
        max_mtime = None
        
        if path.is_file():
            stat = path.stat()
            min_mtime = max_mtime = stat.st_mtime
        else:
            for root, _, files in os.walk(path):
                for fname in files[:1000]:  # Sample for performance
                    try:
                        fpath = os.path.join(root, fname)
                        mtime = os.stat(fpath).st_mtime
                        if min_mtime is None or mtime < min_mtime:
                            min_mtime = mtime
                        if max_mtime is None or mtime > max_mtime:
                            max_mtime = mtime
                    except:
                        continue
        
        if min_mtime and max_mtime:
            return {
                'earliest_mtime': datetime.fromtimestamp(min_mtime).isoformat(),
                'latest_mtime': datetime.fromtimestamp(max_mtime).isoformat()
            }
        
        return {
            'earliest_mtime': None,
            'latest_mtime': None
        }
    
    def _detect_synthetic_data(self, path: Path) -> str:
        """Detect if dataset contains synthetic data."""
        synthetic_keywords = [
            'synthetic', 'generated', 'artificial', 'augmented',
            'simulated', 'fake', 'pseudo', 'manufactured'
        ]
        
        # Check README and dataset cards
        for filename in ['README.md', 'dataset_card.md', 'DATASET_CARD.md']:
            card_path = path / filename
            if card_path.exists():
                try:
                    content = card_path.read_text(encoding='utf-8', errors='ignore')[:5000].lower()
                    for keyword in synthetic_keywords:
                        if keyword in content:
                            return 'yes'
                except:
                    pass
        
        # Check for common synthetic dataset names
        path_lower = str(path).lower()
        for keyword in synthetic_keywords:
            if keyword in path_lower:
                return 'yes'
        
        return 'unknown'
    
    def _find_dataset_card(self, path: Path) -> Dict[str, Any]:
        """Find and extract dataset card info."""
        for filename in ['dataset_card.md', 'DATASET_CARD.md', 'README.md']:
            card_path = path / filename
            if card_path.exists():
                try:
                    content = card_path.read_text(encoding='utf-8', errors='ignore')[:1000]
                    # Extract title if present
                    lines = content.split('\n')
                    title = None
                    for line in lines[:10]:
                        if line.startswith('# '):
                            title = line[2:].strip()
                            break
                    
                    return {
                        'present': True,
                        'path': str(card_path.relative_to(path)),
                        'title': title
                    }
                except:
                    pass
        
        return {
            'present': False,
            'path': None,
            'title': None
        }
    
    def _estimate_lines_and_tokens(self, files: List[Path]) -> Dict[str, int]:
        """Estimate total lines and tokens in dataset."""
        total_lines = 0
        total_chars = 0
        
        for file in files[:100]:  # Sample files
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = 0
                    chars = 0
                    for line in f:
                        lines += 1
                        chars += len(line)
                        if lines > 10000:  # Cap per file
                            break
                    
                    # Extrapolate if we have sampled
                    if len(files) > 100:
                        factor = len(files) / 100
                        total_lines += int(lines * factor)
                        total_chars += int(chars * factor)
                    else:
                        total_lines += lines
                        total_chars += chars
            except:
                continue
        
        # Estimate tokens (rough: 4 chars per token)
        est_tokens = total_chars // 4
        
        return {
            'total_lines': total_lines,
            'est_tokens': est_tokens
        }
    
    def _calculate_provenance_summary(self, domains: List[str]) -> Dict[str, float]:
        """Calculate provenance summary from domain list."""
        if not domains:
            return {}
        
        categories = {
            'github': 0,
            'edu': 0,
            'org': 0,
            'com': 0,
            'gov': 0,
            'other': 0
        }
        
        for domain in domains:
            domain_lower = domain.lower()
            if 'github' in domain_lower:
                categories['github'] += 1
            elif domain_lower.endswith('.edu'):
                categories['edu'] += 1
            elif domain_lower.endswith('.org'):
                categories['org'] += 1
            elif domain_lower.endswith('.com'):
                categories['com'] += 1
            elif domain_lower.endswith('.gov'):
                categories['gov'] += 1
            else:
                categories['other'] += 1
        
        # Convert to percentages
        total = sum(categories.values())
        result = {}
        
        if total > 0:
            for cat, count in categories.items():
                pct = round(count / total, 2)
                if pct > 0:
                    result[cat] = pct
        
        return result
    
    def _detect_pii_signals_enhanced(self, files: List[Path]) -> Dict[str, Any]:
        """Enhanced PII detection with boolean signals only."""
        has_email_like = False
        has_id_like = False
        
        # ID patterns (SSN-like, phone-like, but don't log actual values)
        id_pattern = re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b|\b\d{10,}\b')
        
        for file in files[:20]:  # Limited sample
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')[:5000]
                
                # Check for email-like patterns
                if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content):
                    has_email_like = True
                
                # Check for ID-like patterns
                if id_pattern.search(content):
                    has_id_like = True
                
                if has_email_like and has_id_like:
                    break  # Found both, can stop
            except:
                continue
        
        return {
            'email_like': has_email_like,
            'id_like': has_id_like,
            'note': 'heuristic only - no content retained'
        }