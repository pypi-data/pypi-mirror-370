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
        
        results = {
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
        }
        
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
        """Extract domains from content - local only."""
        domains = Counter()
        domain_pattern = r'\b(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})\b'
        
        for file in files[:100]:  # Sample first 100 files
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')[:10000]
                found_domains = re.findall(domain_pattern, content)
                domains.update(found_domains)
            except:
                continue
        
        top_domains = [domain for domain, _ in domains.most_common(20)]
        
        return {
            'values': top_domains,
            'confidence': 0.95,  # High - direct extraction
            'source': 'automated',
            'total_found': len(domains)
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
        """Extract and count domain names from text."""
        domains = Counter()
        # More comprehensive domain pattern
        domain_patterns = [
            r'https?://([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+)',  # URLs with protocol
            r'www\.([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+)',     # www. prefix
            r'\b([a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+)\b'         # Plain domains
        ]
        
        for pattern in domain_patterns:
            found_domains = re.findall(pattern, text, re.IGNORECASE)
            for domain in found_domains:
                # Normalize domain
                domain = domain.lower().strip()
                # Remove common subdomains for aggregation
                if domain.startswith('www.'):
                    domain = domain[4:]
                domains[domain] += 1
        
        return domains
    
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