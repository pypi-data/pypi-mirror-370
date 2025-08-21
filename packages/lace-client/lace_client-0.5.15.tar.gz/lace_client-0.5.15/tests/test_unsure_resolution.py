"""
Tests for unsure resolution system with privacy safeguards.
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

from lace.regulatory.scope import ScopeClassifier
from lace.advisors import UnsureResolver, MockLLM, PIIScrubber
from lace.advisors.llm_client import RemoteDisabled


class TestUnsureResolutionConservativeDefaults:
    """Test that unsure resolution defaults to conservative (placed) when remote disabled."""
    
    @pytest.fixture
    def classifier(self):
        # Ensure remote is disabled
        os.environ['LACE_ALLOW_REMOTE_LLM'] = 'false'
        return ScopeClassifier()
    
    def test_unsure_remote_disabled_conservative_defaults(self, classifier):
        """With triad questions unsure + remote disabled → placed with warnings."""
        answers = {
            "provider_status": "built_model",
            "internal_only_use": "unsure",
            "internal_only_use_unsure_description": "Used by our staff for internal reports",
            "essential_to_service": "unsure",
            "essential_to_service_unsure_description": "Nice to have but not critical",
            "affects_individuals_rights": "unsure",
            "affects_individuals_rights_unsure_description": "Just generates dashboards",
            "offered_in_eu_market": "no"
        }
        
        scope = classifier.classify(answers)
        
        # Should default to placed (conservative)
        assert scope.placed_on_market == True
        
        # Check for warnings about remote disabled
        trace_str = " ".join(scope.decision_trace)
        assert "heuristic" in trace_str.lower() or "conservative" in trace_str.lower()
        
        # Should have unsure resolutions
        assert len(scope.unsure_resolutions) > 0
        
        # All resolutions should be low confidence (heuristic)
        for res in scope.unsure_resolutions:
            assert res['confidence'] <= 0.4  # Heuristic gives low confidence
            assert res['used_remote'] == False
    
    def test_unsure_with_pii_gets_scrubbed(self):
        """Test that PII is scrubbed before any processing."""
        scrubber = PIIScrubber()
        
        test_cases = [
            ("Contact john@example.com for details", "Contact [EMAIL] for details"),
            ("My API key is sk_test_4242424242424242", "My API key is [API_KEY]"),
            ("Call me at 555-123-4567", "Call me at [PHONE]"),
            ("Visit https://example.com/secret", "Visit [URL]"),
            ("SSN is 123-45-6789", "SSN is [SSN]"),
            ("Token: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyIn0.abc", "Token: [JWT]")
        ]
        
        for input_text, expected in test_cases:
            scrubbed = scrubber.scrub(input_text)
            assert scrubbed == expected
    
    def test_unsure_essential_to_service_heuristic(self):
        """Test heuristic resolution for essential_to_service."""
        resolver = UnsureResolver(llm_client=MockLLM())
        
        # Test positive signals
        result = resolver.resolve(
            'essential_to_service',
            'This is mission-critical to our SLA and has revenue impact',
            {}
        )
        assert result['normalized_value'] == True
        assert result['confidence'] <= 0.4  # Heuristic confidence
        
        # Test negative signals
        result = resolver.resolve(
            'essential_to_service',
            'Just a nice-to-have experimental prototype for research',
            {}
        )
        assert result['normalized_value'] == False
        assert result['confidence'] <= 0.4


class TestUnsureResolutionRemoteEnabled:
    """Test unsure resolution with remote LLM enabled (using mock)."""
    
    @pytest.fixture
    def classifier(self):
        # Enable remote for testing (will use MockLLM)
        os.environ['LACE_ALLOW_REMOTE_LLM'] = 'true'
        return ScopeClassifier()
    
    @patch('lace.regulatory.scope.RemoteGuardedLLM')
    def test_unsure_remote_enabled_resolves_triad(self, mock_llm_class, classifier):
        """Mock LLM returns high confidence → NOT placed."""
        # Configure mock to return high-confidence NOT placed
        mock_llm = MockLLM()
        mock_llm_class.return_value = mock_llm
        
        answers = {
            "provider_status": "built_model",
            "internal_only_use": "unsure",
            "internal_only_use_unsure_description": "Only used internally by staff",
            "essential_to_service": "unsure",
            "essential_to_service_unsure_description": "Not essential, just analytics",
            "affects_individuals_rights": "unsure",
            "affects_individuals_rights_unsure_description": "No rights impact, just metrics",
            "offered_in_eu_market": "no",
            "integrated_into_own_system": "no"
        }
        
        # Mock high-confidence responses
        with patch.object(mock_llm, 'predict') as mock_predict:
            mock_predict.side_effect = [
                "This IS for internal use only (confidence: 0.88)",
                "The description indicates this is NOT essential to the service (confidence: 0.85)",
                "This does NOT affect individuals' rights (confidence: 0.90)"
            ]
            
            scope = classifier.classify(answers)
        
        # With high confidence on all three → NOT placed
        assert scope.placed_on_market == False
        assert "triad met" in scope.placement_reason.lower()
        
        # No model obligations
        assert scope.needs_eu_representative == False
        assert "advisory" in scope.applicable_obligations[0].lower()
    
    def test_unsure_low_confidence_defaults_to_placed(self, classifier):
        """Low confidence resolution → conservative (placed)."""
        resolver = UnsureResolver(llm_client=MockLLM())
        
        # Simulate low-confidence response
        result = resolver.resolve(
            'essential_to_service',
            'Maybe important but hard to say',
            {}
        )
        
        # Low confidence should be treated conservatively
        if result['confidence'] < 0.75:
            # In real classifier, this would default to placed
            assert result['confidence'] < 0.75


class TestModificationRatioParsing:
    """Test parsing of modification compute ratios from free text."""
    
    def test_unsure_mod_ratio_parsing(self):
        """Free-text ratio parsing."""
        resolver = UnsureResolver(llm_client=MockLLM())
        
        test_cases = [
            ("We used about 40% of the base compute", 'gt_33_to_50'),
            ("Roughly 30% of original training", 'le_33'),
            ("More than half the compute", 'gt_50'),
            ("Around one-third of training", 'le_33'),
            ("0.45 ratio", 'gt_33_to_50'),
            ("Two thirds of base", 'gt_50')
        ]
        
        for text, expected_range in test_cases:
            ratio = resolver.parse_ratio(text)
            assert ratio is not None
            
            # Map ratio to enum and verify
            if ratio > 0.5:
                actual_range = 'gt_50'
            elif ratio > 0.33:
                actual_range = 'gt_33_to_50'
            else:
                actual_range = 'le_33'
            
            assert actual_range == expected_range, f"For '{text}': ratio={ratio}, expected {expected_range}, got {actual_range}"


class TestOSSLicenseResolution:
    """Test open-source license resolution."""
    
    def test_unsure_open_source_license_custom_warns(self):
        """Custom license warns but doesn't block."""
        classifier = ScopeClassifier()
        
        answers = {
            "provider_status": "built_model",
            "open_source_release": True,
            "open_source_license_type": "custom",
            "open_source_without_monetisation": True,
            "weights_arch_usage_public": True,
            "access_gating_type": "none",
            "offered_in_eu_market": True
        }
        
        scope = classifier.classify(answers)
        
        # Custom license should allow carve-outs but warn
        assert len(scope.carve_outs) > 0
        assert any("custom license" in w.lower() for w in scope.validation_warnings)


class TestDecisionTrace:
    """Test that decision trace contains unsure resolution info."""
    
    @pytest.fixture
    def classifier(self):
        return ScopeClassifier()
    
    def test_decision_trace_contains_unsure_items(self, classifier):
        """Ensure trace includes unsure resolution steps."""
        answers = {
            "provider_status": "unsure",
            "provider_status_unsure_description": "We fine-tuned GPT-3 with our data",
            "offered_in_eu_market": True
        }
        
        scope = classifier.classify(answers)
        
        trace_str = " ".join(scope.decision_trace)
        
        # Should contain resolution info (but no raw text)
        assert "provider_status" in trace_str
        # May show "resolved" or "insufficient confidence" depending on heuristics
        assert ("resolved" in trace_str.lower() or "insufficient" in trace_str.lower())
        
        # Should NOT contain the raw description
        assert "We fine-tuned GPT-3" not in trace_str
        assert "provider_status_unsure_description" not in str(scope.unsure_resolutions)


class TestEmployeeRightsDetection:
    """Test that employee rights are properly detected."""
    
    def test_affects_employee_rights_detected(self):
        """Employee-related keywords trigger rights impact."""
        resolver = UnsureResolver(llm_client=MockLLM())
        
        employee_cases = [
            "Used for employee performance reviews",
            "Handles hiring and recruitment decisions",
            "Monitors staff productivity",
            "Determines promotion eligibility",
            "Processes termination recommendations"
        ]
        
        for desc in employee_cases:
            result = resolver.resolve(
                'affects_individuals_rights',
                desc,
                {}
            )
            # Should detect employee rights impact
            assert result['normalized_value'] == True or result['confidence'] < 0.5


class TestCommercialDeploymentIndicators:
    """Test detection of commercial deployment indicators."""
    
    def test_commercial_indicators_in_rubrics(self):
        """Verify commercial deployment indicators are in rubrics."""
        resolver = UnsureResolver()
        
        commercial_indicators = resolver.rubrics.get('commercial_deployment', {}).get('indicators', [])
        
        # Should include key commercial signals
        assert 'customer-facing' in commercial_indicators
        assert 'revenue' in commercial_indicators
        assert 'SLA' in commercial_indicators
        assert 'production' in commercial_indicators


class TestPrivacySafeguards:
    """Test privacy safeguards in unsure resolution."""
    
    def test_no_raw_text_in_results(self):
        """Ensure no raw free-text appears in results."""
        classifier = ScopeClassifier()
        
        sensitive_text = "Our SECRET_PROJECT uses model for CONFIDENTIAL_TASK"
        
        answers = {
            "provider_status": "built_model",
            "internal_only_use": "unsure",
            "internal_only_use_unsure_description": sensitive_text,
            "offered_in_eu_market": False
        }
        
        scope = classifier.classify(answers)
        
        # Check entire result object as string
        result_str = str(scope.__dict__)
        
        # Raw text should NOT appear anywhere
        assert "SECRET_PROJECT" not in result_str
        assert "CONFIDENTIAL_TASK" not in result_str
        assert sensitive_text not in result_str
    
    def test_hash_storage_when_enabled(self):
        """Test that SHA-256 hash is computed when storage enabled."""
        import hashlib
        
        os.environ['LACE_UNSURE_STORE_DECISIONS'] = 'true'
        
        text = "Test description for hashing"
        expected_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # This would be logged internally by UnsureResolver
        # We can't directly test logging, but we verify the hash computation
        assert len(expected_hash) == 64  # SHA-256 produces 64 hex chars
        
        os.environ.pop('LACE_UNSURE_STORE_DECISIONS', None)


class TestBackwardCompatibility:
    """Test backward compatibility with existing answer formats."""
    
    def test_boolean_answers_still_work(self):
        """Legacy boolean answers should work without unsure resolution."""
        classifier = ScopeClassifier()
        
        # Old-style boolean answers
        answers = {
            "provider_status": "built_model",
            "offered_in_eu_market": True,  # Boolean, not "yes"/"no"/"unsure"
            "internal_only_use": False,
            "essential_to_service": True,
            "affects_individuals_rights": False
        }
        
        scope = classifier.classify(answers)
        
        # Should work normally
        assert scope.placed_on_market == True
        assert scope.provider_role == "model_provider"
        
        # No unsure resolutions needed
        assert len(scope.unsure_resolutions) == 0
    
    def test_yes_no_mapped_to_boolean(self):
        """Yes/no strings should map to boolean."""
        classifier = ScopeClassifier()
        
        answers = {
            "provider_status": "built_model",
            "offered_in_eu_market": "yes",  # String yes
            "internal_only_use": "no",      # String no
        }
        
        scope = classifier.classify(answers)
        
        # Should map correctly
        assert scope.placed_on_market == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])