"""
PII scrubber for removing sensitive information before remote processing.
"""

import re
from typing import Pattern, List, Tuple


class PIIScrubber:
    """Scrubs personally identifiable information from text."""
    
    def __init__(self):
        # Compile patterns for efficiency
        # CRITICAL: JWT and specific patterns MUST come before generic SECRET pattern
        # Order matters! Process in order and use a two-pass approach
        self.jwt_pattern = re.compile(r'eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+')
        
        self.patterns: List[Tuple[Pattern, str]] = [
            
            # AWS keys - before generic API keys
            (re.compile(r'AKIA[0-9A-Z]{16}'), '[AWS_KEY]'),
            
            # Stripe keys - before generic API keys
            (re.compile(r'\bsk_[a-zA-Z0-9_]{10,}\b'), '[STRIPE_KEY]'),
            (re.compile(r'\bpk_[a-zA-Z0-9_]{10,}\b'), '[PUBLIC_KEY]'),
            
            # Email addresses
            (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL]'),
            
            # Phone numbers (various formats)
            (re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'), '[PHONE]'),
            (re.compile(r'\b\+?[0-9]{10,15}\b'), '[PHONE]'),
            
            # IP addresses (new)
            (re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'), '[IP]'),
            
            # OAuth Bearer tokens (new)
            (re.compile(r'Bearer [A-Za-z0-9\-._~+/]+=*'), '[OAUTH]'),
            
            # URLs
            (re.compile(r'https?://[^\s]+'), '[URL]'),
            (re.compile(r'www\.[^\s]+'), '[URL]'),
            
            # Generic API keys
            (re.compile(r'\b(?:api[_-]?key|apikey|api[_-]?token|access[_-]?token)["\']?\s*[:=]\s*["\']?[A-Za-z0-9_\-]{20,}["\']?\b', re.IGNORECASE), '[API_KEY]'),
            
            # Credit card numbers
            (re.compile(r'\b(?:\d[ -]?){13,16}\b'), '[CC_NUMBER]'),
            
            # IBAN
            (re.compile(r'\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}\b'), '[IBAN]'),
            
            # Social Security Numbers (US)
            (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), '[SSN]'),
            
            # Generic secrets - MUST be last
            # Only match when it's actually a secret assignment, not just the word "token"
            (re.compile(r'\b(?:password|passwd|pwd|secret)["\']?\s*[:=]\s*["\']?[^\s"\']+["\']?', re.IGNORECASE), '[SECRET]'),
            # Token assignments - but don't match if the value is already a placeholder like [JWT]
            (re.compile(r'\btoken["\']?\s*[:=]\s*["\']?(?!eyJ)(?!\[)[^\s"\']+["\']?', re.IGNORECASE), '[TOKEN]'),
        ]
    
    def scrub(self, text: str) -> str:
        """
        Remove PII from text before remote processing.
        
        Args:
            text: Input text potentially containing PII
            
        Returns:
            Scrubbed text with PII replaced by placeholders
        """
        if not text:
            return text
        
        # First pass: Replace JWT tokens to protect them
        scrubbed = self.jwt_pattern.sub('[JWT]', text)
        
        # Second pass: Apply other patterns
        for pattern, replacement in self.patterns:
            if callable(replacement):
                scrubbed = pattern.sub(replacement, scrubbed)
            else:
                scrubbed = pattern.sub(replacement, scrubbed)
            
        return scrubbed
    
    def has_pii(self, text: str) -> bool:
        """
        Check if text contains potential PII.
        
        Args:
            text: Text to check
            
        Returns:
            True if PII patterns are detected
        """
        if not text:
            return False
        
        # Check JWT pattern first
        if self.jwt_pattern.search(text):
            return True
            
        for pattern, _ in self.patterns:
            if pattern.search(text):
                return True
        return False