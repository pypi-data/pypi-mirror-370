"""
LLM client with privacy guards and remote access control.
"""

import os
import time
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class RemoteDisabled(Exception):
    """Raised when remote LLM is disabled but required."""
    pass


class RemoteGuardedLLM:
    """LLM client that requires explicit permission for remote calls."""
    
    def __init__(self, allow_remote: Optional[bool] = None):
        """
        Initialize LLM client.
        
        Args:
            allow_remote: Override for remote permission (default reads env/flag)
        """
        if allow_remote is None:
            # Check environment variable
            allow_remote = os.environ.get('LACE_ALLOW_REMOTE_LLM', '').lower() in ('true', '1', 'yes')
        
        self.allow_remote = allow_remote
        self.timeout_seconds = 10
    
    def predict(self, prompt: str, max_tokens: int = 512, timeout_s: Optional[int] = None) -> str:
        """
        Make prediction with remote LLM.
        
        Args:
            prompt: Prompt for LLM (should be PII-scrubbed)
            max_tokens: Maximum tokens to generate
            timeout_s: Override timeout (default 10s)
            
        Returns:
            LLM response text
            
        Raises:
            RemoteDisabled: If remote access not allowed
            TimeoutError: If request exceeds timeout
        """
        if not self.allow_remote:
            raise RemoteDisabled(
                "Remote LLM access disabled. Use --allow-remote-llm flag or "
                "set LACE_ALLOW_REMOTE_LLM=true to enable."
            )
        
        timeout = timeout_s or self.timeout_seconds
        
        # Simulate timeout for demonstration
        # In production, this would call actual LLM API with timeout
        start_time = time.time()
        
        try:
            # Placeholder for actual LLM call
            # In production: response = call_openai_or_anthropic(prompt, max_tokens, timeout)
            
            # For now, return a mock response
            logger.info(f"Remote LLM call (timeout={timeout}s)")
            time.sleep(0.1)  # Simulate network latency
            
            if time.time() - start_time > timeout:
                raise TimeoutError(f"LLM request exceeded {timeout}s timeout")
            
            # Mock response based on common patterns
            if "essential" in prompt.lower():
                return "Based on the description, this appears to be non-essential to the service."
            elif "rights" in prompt.lower():
                return "This does not appear to affect individuals' rights."
            elif "internal" in prompt.lower():
                return "This appears to be for internal use only."
            else:
                return "Unable to determine with high confidence."
                
        except TimeoutError:
            logger.warning(f"LLM request timed out after {timeout}s")
            raise
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            raise


class MockLLM:
    """Mock LLM for testing."""
    
    def __init__(self, responses: Optional[Dict[str, str]] = None):
        """
        Initialize mock LLM.
        
        Args:
            responses: Dict mapping prompt patterns to responses
        """
        self.responses = responses or {}
        self.call_count = 0
        self.last_prompt = None
    
    def predict(self, prompt: str, max_tokens: int = 512, timeout_s: Optional[int] = None) -> str:
        """
        Return mock response.
        
        Args:
            prompt: Input prompt
            max_tokens: Ignored in mock
            timeout_s: Ignored in mock
            
        Returns:
            Mock response based on configured patterns
        """
        self.call_count += 1
        self.last_prompt = prompt
        
        # Check configured responses
        for pattern, response in self.responses.items():
            if pattern.lower() in prompt.lower():
                return response
        
        # Default responses based on keywords
        if "essential_to_service" in prompt:
            return "The description indicates this is NOT essential to the service (confidence: 0.85)"
        elif "affects_individuals_rights" in prompt:
            return "This does NOT affect individuals' rights (confidence: 0.90)"
        elif "internal_only_use" in prompt:
            return "This IS for internal use only (confidence: 0.88)"
        elif "modification_compute_ratio" in prompt:
            if "40%" in prompt or "forty percent" in prompt.lower():
                return "The modification ratio is approximately 0.40 (40% of base compute)"
            elif "30%" in prompt or "thirty percent" in prompt.lower():
                return "The modification ratio is approximately 0.30 (30% of base compute)"
        elif "provider_status" in prompt:
            if "trained from scratch" in prompt.lower():
                return "This indicates built_model status"
            elif "fine-tuned" in prompt.lower() or "lora" in prompt.lower():
                return "This indicates significant_modifier status"
            elif "api" in prompt.lower():
                return "This indicates api_user status"
        
        return "Unable to determine with confidence"