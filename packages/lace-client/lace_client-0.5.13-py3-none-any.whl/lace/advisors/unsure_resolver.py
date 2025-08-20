"""
Unsure resolution system with privacy safeguards and conservative defaults.
"""

import re
import hashlib
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml

from .llm_client import RemoteGuardedLLM, RemoteDisabled, MockLLM
from .pii_scrubber import PIIScrubber

logger = logging.getLogger(__name__)


class UnsureResolver:
    """Orchestrates resolution of unsure answers with privacy and conservative defaults."""
    
    def __init__(self, llm_client=None, rubrics_path: Optional[str] = None):
        """
        Initialize resolver.
        
        Args:
            llm_client: LLM client instance (defaults to RemoteGuardedLLM)
            rubrics_path: Path to rubrics YAML (defaults to config/unsure_rubrics.yaml)
        """
        self.llm = llm_client or RemoteGuardedLLM()
        self.scrubber = PIIScrubber()
        self.rubrics = self._load_rubrics(rubrics_path)
        self.store_decisions = os.environ.get('LACE_UNSURE_STORE_DECISIONS', '').lower() in ('true', '1', 'yes')
    
    def _load_rubrics(self, rubrics_path: Optional[str]) -> Dict:
        """Load rubrics configuration."""
        if not rubrics_path:
            # Default path relative to this file
            config_dir = Path(__file__).parent.parent / 'config'
            rubrics_path = config_dir / 'unsure_rubrics.yaml'
        
        if Path(rubrics_path).exists():
            with open(rubrics_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Return default rubrics if file doesn't exist
            return self._default_rubrics()
    
    def _default_rubrics(self) -> Dict:
        """Default rubrics for common questions."""
        return {
            'triad': {
                'essential_to_service': {
                    'positive_signals': ['mission-critical', 'core workflow', 'production blocker', 
                                        'SLA', 'revenue impact', 'customer requirement', 'primary function'],
                    'negative_signals': ['nice-to-have', 'experimental', 'optional', 'supplementary',
                                        'research', 'prototype', 'testing', 'analytics']
                },
                'affects_individuals_rights': {
                    'positive_signals': ['hiring', 'promotion', 'termination', 'monitoring', 'credit',
                                        'lending', 'healthcare', 'education', 'housing', 'insurance',
                                        'employment', 'performance review', 'access control', 'eligibility',
                                        'scoring', 'ranking', 'profiling', 'decision-making'],
                    'negative_signals': ['aggregate', 'anonymous', 'statistical', 'no personal data',
                                        'internal metrics', 'system performance', 'technical logs']
                },
                'internal_only_use': {
                    'positive_signals': ['internal only', 'not customer-facing', 'backend only',
                                        'employee use', 'staff only', 'internal tool', 'admin only'],
                    'negative_signals': ['customer-facing', 'public', 'external', 'client access',
                                        'user-facing', 'API', 'service', 'product feature']
                }
            },
            'provider_role': {
                'built_model': ['trained from scratch', 'pre-training', 'foundation model',
                               'built ourselves', 'our model', 'developed in-house'],
                'significant_modifier': ['fine-tuned', 'LoRA', 'adapted', 'modified',
                                        'customized', 'retrained', 'continued training'],
                'api_user': ['using API', 'API calls', 'no training', 'just prompting',
                            'third-party model', 'external model', 'vendor model']
            },
            'commercial_deployment': {
                'indicators': ['customer-facing', 'revenue', 'SLA', 'production', 'merchandising',
                              'recommendations', 'client service', 'user experience', 'business-critical']
            }
        }
    
    def resolve(self, question_id: str, free_text: str, context: Dict) -> Dict[str, Any]:
        """
        Resolve an unsure answer.
        
        Args:
            question_id: ID of the question being resolved
            free_text: User's free-text description (will be scrubbed)
            context: Current answers context
            
        Returns:
            Dict containing:
                - normalized_value: Resolved value
                - confidence: Float 0..1
                - rationale: Short templated rationale (no user text)
                - used_remote: Whether remote LLM was used
                - warnings: List of warnings
        """
        warnings = []
        used_remote = False
        
        # Store hash if configured (never the raw text)
        if self.store_decisions and free_text:
            text_hash = hashlib.sha256(free_text.encode()).hexdigest()
            logger.info(f"Unsure resolution for {question_id}, hash: {text_hash[:8]}...")
        
        # Scrub PII before any processing
        scrubbed_text = self.scrubber.scrub(free_text) if free_text else ""
        
        if self.scrubber.has_pii(free_text or ""):
            warnings.append("PII detected and scrubbed from description")
        
        # Try remote resolution first (if allowed)
        try:
            if isinstance(self.llm, MockLLM):
                # For testing
                used_remote = True
                result = self._resolve_with_llm(question_id, scrubbed_text, context)
            else:
                used_remote = True
                result = self._resolve_with_llm(question_id, scrubbed_text, context)
        except RemoteDisabled:
            warnings.append("Remote LLM not allowed; applied conservative heuristic")
            result = self._resolve_with_heuristic(question_id, scrubbed_text, context)
        except TimeoutError:
            warnings.append("Remote LLM unavailable/timeout; applied conservative heuristic")
            result = self._resolve_with_heuristic(question_id, scrubbed_text, context)
        except Exception as e:
            logger.warning(f"Remote resolution failed: {e}")
            warnings.append("Remote resolution failed; applied conservative heuristic")
            result = self._resolve_with_heuristic(question_id, scrubbed_text, context)
        
        # Add metadata
        result['used_remote'] = used_remote
        result['warnings'] = warnings
        
        # Never include raw text in result
        if 'raw_text' in result:
            del result['raw_text']
        
        return result
    
    def _resolve_with_llm(self, question_id: str, scrubbed_text: str, context: Dict) -> Dict:
        """Resolve using LLM."""
        # Build prompt based on question type
        prompt = self._build_prompt(question_id, scrubbed_text, context)
        
        # Get LLM response
        response = self.llm.predict(prompt, max_tokens=256, timeout_s=10)
        
        # Parse response
        return self._parse_llm_response(question_id, response)
    
    def _resolve_with_heuristic(self, question_id: str, scrubbed_text: str, context: Dict) -> Dict:
        """Resolve using local heuristics (conservative)."""
        text_lower = scrubbed_text.lower()
        
        # Triad questions
        if question_id == 'essential_to_service':
            rubric = self.rubrics['triad']['essential_to_service']
            positive_count = sum(1 for signal in rubric['positive_signals'] if signal in text_lower)
            negative_count = sum(1 for signal in rubric['negative_signals'] if signal in text_lower)
            
            if positive_count > 0:
                # Conservative: if ANY positive signal, likely essential
                return {
                    'normalized_value': True,
                    'confidence': min(0.75, 0.60 + positive_count * 0.05),
                    'rationale': 'Heuristic: positive signals detected'
                }
            elif negative_count > 0:
                return {
                    'normalized_value': False,
                    'confidence': min(0.65, 0.50 + negative_count * 0.05),
                    'rationale': 'Heuristic: negative signals detected'
                }
            else:
                # Conservative default: assume essential if unclear
                return {
                    'normalized_value': True,
                    'confidence': 0.60,
                    'rationale': 'Heuristic: conservative default (essential)'
                }
        
        elif question_id == 'affects_individuals_rights':
            rubric = self.rubrics['triad']['affects_individuals_rights']
            # Check for employee/applicant rights specifically
            employee_signals = ['employee', 'staff', 'hiring', 'promotion', 'termination', 'performance']
            has_employee = any(signal in text_lower for signal in employee_signals)
            
            positive_count = sum(1 for signal in rubric['positive_signals'] if signal in text_lower)
            negative_count = sum(1 for signal in rubric['negative_signals'] if signal in text_lower)
            
            if has_employee or positive_count > 0:
                return {
                    'normalized_value': True,
                    'confidence': min(0.4, 0.3 if has_employee else 0.2 + positive_count * 0.1),
                    'rationale': 'Heuristic: affects employee rights' if has_employee else 'Heuristic: rights impact detected'
                }
            elif negative_count > 0:
                return {
                    'normalized_value': False,
                    'confidence': min(0.35, 0.2 + negative_count * 0.05),
                    'rationale': 'Heuristic: no rights impact signals'
                }
        
        elif question_id == 'internal_only_use':
            rubric = self.rubrics['triad']['internal_only_use']
            positive_count = sum(1 for signal in rubric['positive_signals'] if signal in text_lower)
            negative_count = sum(1 for signal in rubric['negative_signals'] if signal in text_lower)
            
            if positive_count > negative_count:
                return {
                    'normalized_value': True,
                    'confidence': min(0.4, 0.2 + positive_count * 0.1),
                    'rationale': 'Heuristic: internal use signals'
                }
            elif negative_count > 0:
                return {
                    'normalized_value': False,
                    'confidence': min(0.4, 0.2 + negative_count * 0.1),
                    'rationale': 'Heuristic: external use signals'
                }
        
        # Modification ratio parsing
        elif question_id == 'modification_compute_ratio':
            ratio = self.parse_ratio(scrubbed_text)
            if ratio is not None:
                # Map to enum based on ratio
                if ratio > 0.5:
                    value = 'gt_50'
                elif ratio > 0.33:
                    value = 'gt_33_to_50'
                else:
                    value = 'le_33'
                
                return {
                    'normalized_value': value,
                    'confidence': 0.35,  # Low confidence for heuristic
                    'rationale': f'Heuristic: parsed ratio ~{ratio:.1%}'
                }
        
        # Provider status
        elif question_id == 'provider_status':
            rubric = self.rubrics['provider_role']
            
            for status, signals in rubric.items():
                if any(signal in text_lower for signal in signals):
                    return {
                        'normalized_value': status,
                        'confidence': 0.3,  # Low confidence
                        'rationale': f'Heuristic: {status} signals detected'
                    }
        
        # Conservative default: return None (keep as unsure)
        return {
            'normalized_value': None,
            'confidence': 0.1,
            'rationale': 'Heuristic: insufficient signals for resolution'
        }
    
    def _build_prompt(self, question_id: str, scrubbed_text: str, context: Dict) -> str:
        """Build prompt for LLM based on question type."""
        if question_id in ['essential_to_service', 'affects_individuals_rights', 'internal_only_use']:
            rubric = self.rubrics['triad'].get(question_id, {})
            return f"""Classify the following description for EU AI Act compliance.

Question: {question_id.replace('_', ' ')}
Description: {scrubbed_text}

Positive indicators: {', '.join(rubric.get('positive_signals', [])[:5])}
Negative indicators: {', '.join(rubric.get('negative_signals', [])[:5])}

{'Note: Employee rights ARE included (hiring, promotion, termination, monitoring).' if question_id == 'affects_individuals_rights' else ''}

Answer with: True/False and confidence (0-1).
Format: <answer> (confidence: <score>)"""
        
        elif question_id == 'modification_compute_ratio':
            return f"""Extract the modification compute ratio from this description.

Description: {scrubbed_text}

Convert percentages or fractions to a decimal ratio (0-1).
Examples: "40% of base" → 0.40, "one third" → 0.33

Answer with the ratio value."""
        
        elif question_id == 'provider_status':
            return f"""Classify the provider status based on this description.

Description: {scrubbed_text}

Options:
- built_model: Trained from scratch or built foundation model
- significant_modifier: Fine-tuned or modified >33% of compute
- api_user: Using model via API without significant modification

Answer with one of: built_model, significant_modifier, api_user"""
        
        return f"Classify this for {question_id}: {scrubbed_text}"
    
    def _parse_llm_response(self, question_id: str, response: str) -> Dict:
        """Parse LLM response into structured result."""
        response_lower = response.lower()
        
        # Extract confidence if present
        confidence_match = re.search(r'confidence[:\s]+([0-9.]+)', response_lower)
        confidence = float(confidence_match.group(1)) if confidence_match else 0.7
        
        # Parse based on question type
        if question_id in ['essential_to_service', 'affects_individuals_rights', 'internal_only_use']:
            # Boolean questions
            if 'true' in response_lower or 'yes' in response_lower:
                value = True
            elif 'false' in response_lower or 'no' in response_lower or 'not' in response_lower:
                value = False
            else:
                value = None
                confidence = 0.2
            
            return {
                'normalized_value': value,
                'confidence': min(1.0, confidence),
                'rationale': f'LLM classification'
            }
        
        elif question_id == 'modification_compute_ratio':
            # Extract ratio
            ratio_match = re.search(r'([0-9.]+)', response)
            if ratio_match:
                ratio = float(ratio_match.group(1))
                if ratio > 1:  # Percentage given as whole number
                    ratio = ratio / 100
                
                # Map to enum
                if ratio > 0.5:
                    value = 'gt_50'
                elif ratio > 0.33:
                    value = 'gt_33_to_50'
                else:
                    value = 'le_33'
                
                return {
                    'normalized_value': value,
                    'confidence': confidence,
                    'rationale': f'LLM: ~{ratio:.0%} of compute'
                }
        
        elif question_id == 'provider_status':
            # Extract provider type
            if 'built_model' in response_lower or 'built model' in response_lower:
                value = 'built_model'
            elif 'significant_modifier' in response_lower or 'significant modifier' in response_lower:
                value = 'significant_modifier'
            elif 'api_user' in response_lower or 'api user' in response_lower:
                value = 'api_user'
            else:
                value = None
                confidence = 0.2
            
            return {
                'normalized_value': value,
                'confidence': confidence,
                'rationale': f'LLM: {value or "undetermined"}'
            }
        
        # Default: couldn't parse
        return {
            'normalized_value': None,
            'confidence': 0.1,
            'rationale': 'LLM: unable to parse response'
        }
    
    @staticmethod
    def to_yes_no(value: Any) -> str:
        """Convert various values to yes/no."""
        if value is None or value == 'unsure':
            return 'unsure'
        if isinstance(value, bool):
            return 'yes' if value else 'no'
        if isinstance(value, str):
            v = value.lower()
            if v in ('yes', 'true', '1', 'y', 't'):
                return 'yes'
            elif v in ('no', 'false', '0', 'n', 'f'):
                return 'no'
        return 'unsure'
    
    @staticmethod
    def to_enum(value: Any, allowed: List[str]) -> Optional[str]:
        """Normalize to allowed enum value."""
        if not value:
            return None
        
        value_lower = str(value).lower()
        
        # Exact match
        for option in allowed:
            if option.lower() == value_lower:
                return option
        
        # Partial match
        for option in allowed:
            if option.lower() in value_lower or value_lower in option.lower():
                return option
        
        return None
    
    @staticmethod
    def parse_ratio(text: str) -> Optional[float]:
        """Parse ratio from text."""
        text_lower = text.lower()
        
        # Look for percentages
        percent_match = re.search(r'(\d+(?:\.\d+)?)\s*%', text_lower)
        if percent_match:
            return float(percent_match.group(1)) / 100
        
        # Look for decimals
        decimal_match = re.search(r'0?\.\d+', text_lower)
        if decimal_match:
            return float(decimal_match.group(0))
        
        # Look for fractions in words
        fraction_map = {
            'half': 0.5,
            'third': 0.33,
            'quarter': 0.25,
            'fifth': 0.2,
            'tenth': 0.1,
        }
        
        # Check for multiplied fractions first
        if 'two third' in text_lower:
            return 0.67
        elif 'three quarter' in text_lower:
            return 0.75
        
        # Then check for single fractions
        for word, value in fraction_map.items():
            if word in text_lower:
                return value
        
        # Look for X/Y format
        fraction_match = re.search(r'(\d+)\s*/\s*(\d+)', text_lower)
        if fraction_match:
            numerator = float(fraction_match.group(1))
            denominator = float(fraction_match.group(2))
            if denominator > 0:
                return numerator / denominator
        
        return None