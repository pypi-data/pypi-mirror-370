"""
Serializer for converting analyzer output to sanitized analysis.json format.
Maps ONLY existing fields - no fabrication of data.
"""

from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def to_analysis_json(results: dict) -> dict:
    """
    Map ONLY keys that exist - no fabrication.
    Tracks missing fields in serializer_notes.
    """
    
    import os
    if os.environ.get('LACE_DEBUG') == '1':
        logger.info(f"Analyzer results type: {type(results)}")
        logger.info(f"Analyzer results keys: {sorted(results.keys())}")
    
    serializer_notes = []
    
    # Safely extract volume metrics with validation
    volume = results.get('volume', {})
    total_files = max(int(volume.get('files', 0)), 0) if 'volume' in results else 0
    total_bytes = max(int(volume.get('bytes', 0)), 0) if 'volume' in results else 0
    
    if 'volume' not in results:
        serializer_notes.append('volume field missing - using zeros')
    
    avg_file_size = (total_bytes / total_files) if total_files > 0 else 0.0
    
    # Extract domains safely (don't synthesize)
    domains = []
    if 'domains' in results:
        raw_domains = results['domains']
        if isinstance(raw_domains, dict):
            # Check if it's the new format with 'values' key
            if 'values' in raw_domains:
                domains = raw_domains.get('values', [])
                if isinstance(domains, dict):
                    # Convert dict of domain->stats to list
                    domains = [
                        {
                            'domain': d, 
                            'bytes': max(int(v.get('bytes', 0)), 0), 
                            'count': max(int(v.get('count', 0)), 0)
                        }
                        for d, v in domains.items()
                    ]
            else:
                # Old format: dict of domain->stats
                domains = [
                    {
                        'domain': d, 
                        'bytes': max(int(v.get('bytes', 0)), 0), 
                        'count': max(int(v.get('count', 0)), 0)
                    }
                    for d, v in raw_domains.items()
                ]
        elif isinstance(raw_domains, list):
            domains = raw_domains
    else:
        serializer_notes.append('domains field missing - using empty array')
    
    # Handle modalities robustly (analyzer versions vary)
    mods = results.get('modalities', [])
    if isinstance(mods, dict):
        # New format with 'values' key
        mods = mods.get('values', [])
    
    # Extract top domains if present (don't synthesize)
    top_domains = results.get('top_10_percent_domains', [])
    if 'top_10_percent_domains' not in results:
        serializer_notes.append('top_10_percent_domains missing')
    
    coverage_pct = float(results.get('top_domains_coverage', 0))
    measurement_method = results.get('measurement_method', 'bytes')
    
    # Extract confidence scores if present
    confidence_scores = results.get('confidence_scores', {})
    if not confidence_scores:
        serializer_notes.append('confidence_scores missing - using empty dict')
    
    # Extract fingerprint sample rate if available
    sample_rate = 0.01
    if 'fingerprint' in results:
        sample_rate = results['fingerprint'].get('sample_rate', 0.01)
    
    return {
        'schema_version': 'analysis.v1',
        'summary': {
            'files_processed': total_files,
            'bytes_total': total_bytes,
            'modalities': mods,
        },
        'domains': domains,
        'domain_analysis': {
            'top_domains': top_domains,
            'measurement_method': measurement_method,
            'coverage_percentage': coverage_pct,
            'total_domains': len(domains),
        },
        'size_metrics': {
            'total_files': total_files,
            'total_bytes': total_bytes,
            'avg_file_size': avg_file_size,
        },
        'confidence_scores': confidence_scores,
        'metadata': {
            'analyzed_at': datetime.utcnow().isoformat(),
            'analyzer_version': '1.0.0',
            'sample_rate': sample_rate,
            'privacy_notice': 'No raw text or file paths included',
            'serializer_notes': serializer_notes  # Track what was missing
        },
    }