"""
Unit tests for EU AI Act scope classification.
Tests all critical fixes:
- FIX #1: EU rep carve-out EXISTS for open-source (non-EU + all conditions + not systemic)
- FIX #2: > 10^25 for systemic risk (strictly greater), >= 10^25 for notification
- FIX #3: No 10^23 GPAI threshold
- FIX #4: Significant modifiers are providers
- FIX #5: Triad logic for placement (internal-only + non-essential + rights-neutral)
"""

import pytest
from datetime import date, datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

from lace.regulatory.scope import ScopeClassifier, ScopeResult


class TestScopeClassification:
    """Test suite for scope classification."""
    
    def test_systemic_risk_exceeds_only(self):
        """Test that systemic risk requires EXCEEDING 10^25 (strictly >)."""
        classifier = ScopeClassifier()
        
        # Exactly 10^25 - NOT systemic
        exactly_not_systemic = classifier.classify({
            "training_compute_flops": "exactly_1e25",
            "provider_status": "built_model"
        })
        assert exactly_not_systemic.is_systemic_risk == False  # Changed!
        
        # Just under - NOT systemic
        under_not_systemic = classifier.classify({
            "training_compute_flops": "under_1e25",
            "provider_status": "built_model"
        })
        assert under_not_systemic.is_systemic_risk == False
        
        # Over threshold - IS systemic
        over_systemic = classifier.classify({
            "training_compute_flops": "over_1e25",
            "provider_status": "built_model"
        })
        assert over_systemic.is_systemic_risk == True
        
        # Test with numeric values (strictly greater)
        assert classifier._is_systemic_risk({"training_compute_flops": 1e25}) == False  # Exactly = NOT
        assert classifier._is_systemic_risk({"training_compute_flops": 9.99e24}) == False
        assert classifier._is_systemic_risk({"training_compute_flops": 1.01e25}) == True
    
    def test_systemic_designation_overrides_compute(self):
        """Test that Commission designation can make a model systemic regardless of compute."""
        classifier = ScopeClassifier()
        
        # Below threshold but designated
        designated = classifier.classify({
            "training_compute_flops": "under_1e25",
            "designated_systemic_risk": True,  # Commission designation
            "provider_status": "built_model",
            "general_purpose": True,  # Need this to be a GPAI provider
            "placing_date": "2025-09-01"
        })
        assert designated.is_systemic_risk == True
        
        # Exactly threshold but designated (redundant but valid)
        exactly_designated = classifier.classify({
            "training_compute_flops": "exactly_1e25",
            "designated_systemic_risk": True,
            "provider_status": "built_model",
            "general_purpose": True,
            "placing_date": "2025-09-01"
        })
        assert exactly_designated.is_systemic_risk == True
    
    def test_open_source_eu_rep_carveout_applies(self):
        """Test that open-source DOES exempt from EU rep when ALL conditions met."""
        classifier = ScopeClassifier()
        
        # Test with ALL conditions met - carve-out applies
        scope_with_carveout = classifier.classify({
            "provider_status": "built_model",
            "open_source_release": True,
            "open_source_without_monetisation": True,  # Required
            "weights_arch_usage_public": True,  # Required
            "outside_eu_provider": True,
            "training_compute_flops": "under_1e25",  # Not systemic
            "general_purpose": True,
            "placing_date": "2025-09-01"
        })
        
        # Check carve-outs include EU rep
        assert len(scope_with_carveout.carve_outs) == 3
        assert any("Technical documentation" in c for c in scope_with_carveout.carve_outs)
        assert any("Downstream documentation" in c for c in scope_with_carveout.carve_outs)
        assert any("EU authorized representative" in c for c in scope_with_carveout.carve_outs)
        
        # EU rep NOT required when all conditions met
        assert scope_with_carveout.needs_eu_representative == False
        
        # But still requires these
        assert scope_with_carveout.requires_public_summary == True
        assert scope_with_carveout.requires_copyright_policy == True
    
    def test_open_source_no_carveout_with_monetisation(self):
        """Test that monetisation blocks the EU rep carve-out."""
        classifier = ScopeClassifier()
        
        # Test with monetisation - no carve-out
        scope_no_carveout = classifier.classify({
            "provider_status": "built_model",
            "open_source_release": True,
            "open_source_without_monetisation": False,  # Monetised!
            "weights_arch_usage_public": True,
            "outside_eu_provider": True,
            "training_compute_flops": "under_1e25",
            "general_purpose": True,
            "placing_date": "2025-09-01"
        })
        
        # No carve-outs when monetised
        assert len(scope_no_carveout.carve_outs) == 0
        
        # EU rep still required
        assert scope_no_carveout.needs_eu_representative == True
    
    def test_significant_modifier_is_provider(self):
        """FIX #4: Test that significant modifiers are treated as providers."""
        classifier = ScopeClassifier()
        
        scope = classifier.classify({
            "provider_status": "significant_modifier",
            "modification_compute_ratio": "34_to_50",  # >33%
            "general_purpose": True,
            "placing_date": "2025-09-01"
        })
        
        assert scope.is_significant_modifier == True
        assert scope.is_provider == True  # Combined flag
        assert scope.requires_public_summary == True
        assert scope.requires_copyright_policy == True
    
    def test_significant_modification_strict_gt(self):
        """Test that exactly 33% is NOT significant, >33% IS significant."""
        classifier = ScopeClassifier()
        
        # Exactly 33% - NOT significant
        not_significant = classifier.classify({
            "modification_compute_ratio": "exactly_33",
            "provider_status": "significant_modifier",
            "general_purpose": False,  # Not GPAI
            "placing_date": "2025-09-01"
        })
        assert not_significant.is_significant_modifier == False
        assert not_significant.is_provider == False  # Not a provider at 33%
        
        # 34-50% - IS significant
        significant = classifier.classify({
            "modification_compute_ratio": "34_to_50",
            "provider_status": "significant_modifier",
            "placing_date": "2025-09-01"
        })
        assert significant.is_significant_modifier == True
        assert significant.is_provider == True  # Is a provider over 33%
        
        # Test with numeric values via internal method
        classifier = ScopeClassifier()
        # Would need to test through full classify method as _is_significant_modifier is internal
    
    def test_preexisting_model_deadlines(self):
        """Test grace period applies ONLY to public summary."""
        classifier = ScopeClassifier()
        
        scope = classifier.classify({
            "placing_date": "2025-01-01",  # Pre-existing
            "still_on_market": True,
            "provider_status": "built_model",
            "general_purpose": True
        })
        
        # Public summary gets grace period
        assert scope.compliance_deadlines['public_summary_due'] == date(2027, 8, 2)
        
        # Other obligations don't get grace period
        assert scope.compliance_deadlines['copyright_policy_due'] == date(2025, 8, 2)
        assert scope.compliance_deadlines['other_obligations_due'] == date(2025, 8, 2)
        
        # Check the note explains this
        assert "2-year grace for public summary ONLY" in scope.compliance_deadlines['note']
    
    def test_sme_domain_rule_with_guard(self):
        """Test SME domain rule with minimum 1 domain guard."""
        classifier = ScopeClassifier()
        
        # SME with guard
        sme_scope = classifier.classify({
            "sme_status": "yes_sme",
            "provider_status": "built_model",
            "general_purpose": True,
            "placing_date": "2025-09-01"
        })
        assert sme_scope.top_domain_rule == "5% or 1000 (whichever lower, min 1)"
        
        # Non-SME with guard
        regular_scope = classifier.classify({
            "sme_status": "no_not_sme",
            "provider_status": "built_model",
            "general_purpose": True,
            "placing_date": "2025-09-01"
        })
        assert regular_scope.top_domain_rule == "10% (min 1)"
        
        # Unsure defaults to non-SME
        unsure_scope = classifier.classify({
            "sme_status": "unsure",
            "provider_status": "built_model",
            "general_purpose": True,
            "placing_date": "2025-09-01"
        })
        assert unsure_scope.top_domain_rule == "10% (min 1)"
    
    def test_domain_membership_change_trigger(self):
        """Test that domain membership changes trigger updates."""
        classifier = ScopeClassifier()
        
        scope = classifier.classify({
            "is_update": True,
            "previous_summary": {
                "top_domains": ["example.com", "test.org", "demo.net"],
                "domain_coverage_percentage": 45
            },
            "current_data": {
                "top_domains": ["example.com", "newsite.com", "demo.net"],  # test.org gone, newsite added
                "domain_coverage_percentage": 48  # Small coverage change
            },
            "placing_date": "2025-09-01"
        })
        
        assert scope.update_triggered['top_domains_changed'] == True
        assert scope.update_triggered['requires_immediate_update'] == True
    
    def test_domain_coverage_shift_trigger(self):
        """Test that >10% coverage shift triggers update."""
        classifier = ScopeClassifier()
        
        scope = classifier.classify({
            "is_update": True,
            "previous_summary": {
                "top_domains": ["example.com", "test.org"],
                "domain_coverage_percentage": 40
            },
            "current_data": {
                "top_domains": ["example.com", "test.org"],  # Same domains
                "domain_coverage_percentage": 55  # 15% shift
            },
            "placing_date": "2025-09-01"
        })
        
        assert scope.update_triggered['domain_coverage_shifted'] == True
        assert scope.update_triggered['requires_immediate_update'] == True
    
    def test_gpai_detection_functional(self):
        """Test GPAI detection uses functional criteria, with 10^23 as indicator only."""
        classifier = ScopeClassifier()
        
        # General-purpose flag triggers GPAI
        gpai_general = classifier.classify({
            "provider_status": "built_model",
            "general_purpose": True,
            "training_compute_flops": "unknown",  # No FLOP info
            "placing_date": "2025-09-01"
        })
        assert gpai_general.is_gpai_provider == True
        
        # Check indicative signals (10^23 range)
        gpai_typical = classifier.classify({
            "provider_status": "built_model",
            "general_purpose": True,
            "training_compute_flops": "1e23_to_1e25",  # Typical GPAI range
            "placing_date": "2025-09-01"
        })
        assert gpai_typical.is_gpai_provider == True
        assert gpai_typical.indicative_signals['indicative_gpai_signal'] == True
        assert any("10^23" in r for r in gpai_typical.indicative_signals['reasons'])
        
        # Large params hint as indicator
        gpai_params = classifier.classify({
            "provider_status": "built_model",
            "general_purpose": False,
            "parameter_count_hint": "over_1b",
            "training_compute_flops": "unknown",
            "placing_date": "2025-09-01"
        })
        assert gpai_params.is_gpai_provider == True
        assert gpai_params.indicative_signals['indicative_gpai_signal'] == True
        assert any("1B parameters" in r for r in gpai_params.indicative_signals['reasons'])
        
        # No GPAI indicators = not GPAI
        not_gpai = classifier.classify({
            "provider_status": "built_model",
            "general_purpose": False,
            "multi_task_capable": False,
            "parameter_count_hint": "under_1b",
            "eu_availability": False,
            "placing_date": "2025-09-01"
        })
        assert not_gpai.is_gpai_provider == False
    
    def test_update_frequency_rules(self):
        """Test 6-month update frequency with immediate trigger option."""
        classifier = ScopeClassifier()
        
        # New model - gets 6-month update schedule
        scope = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "built_model",
            "general_purpose": True
        })
        
        expected_update = date(2025, 9, 1) + timedelta(days=182)  # 6 months = 182 days
        assert scope.compliance_deadlines['next_update_due'] == expected_update
        assert "every 6 months or sooner if significant changes" in scope.compliance_deadlines['update_frequency']
    
    def test_threshold_notification_deadline(self):
        """Test 14-day notification window when threshold exceeded."""
        classifier = ScopeClassifier()
        
        # Test notification required when exceeded
        scope = classifier.classify({
            "provider_status": "built_model",
            "general_purpose": True,
            "training_compute_flops": "over_1e25",
            "threshold_known_date": "2025-09-01",
            "placing_date": "2025-09-15"
        })
        
        assert scope.needs_threshold_notification == True
        assert scope.notification_deadline == date(2025, 9, 15)  # 14 days after known
        assert any("Notify the Commission" in o for o in scope.applicable_obligations)
        
        # Test notification for future exceedance
        future_scope = classifier.classify({
            "provider_status": "built_model",
            "general_purpose": True,
            "training_compute_flops": "under_1e25",
            "will_exceed_1e25": True,
            "threshold_known_date": "2025-10-01",
            "placing_date": "2025-09-01"
        })
        
        assert future_scope.needs_threshold_notification == True
        assert future_scope.notification_deadline == date(2025, 10, 15)  # 14 days after known
    
    def test_modifier_template_modification_only(self):
        """Test that significant modifiers get modification-only summary."""
        classifier = ScopeClassifier()
        
        scope = classifier.classify({
            "provider_status": "significant_modifier",
            "modification_compute_ratio": "34_to_50",  # >33%
            "general_purpose": True,
            "base_model_name": "GPT-4",
            "base_model_provider": "OpenAI",
            "base_model_url": "https://example.com/gpt4-summary",
            "modification_description": "Fine-tuned for legal analysis",
            "placing_date": "2025-09-01"
        })
        
        assert scope.is_significant_modifier == True
        assert scope.summary_scope == "modification_only"
        assert scope.base_model_reference is not None
        assert scope.base_model_reference['base_model_name'] == "GPT-4"
        assert scope.base_model_reference['base_model_provider'] == "OpenAI"
        assert any("modification only" in o.lower() for o in scope.applicable_obligations)
    
    def test_open_source_systemic_no_carveouts(self):
        """Test open-source with systemic risk gets NO carve-outs."""
        classifier = ScopeClassifier()
        
        scope = classifier.classify({
            "provider_status": "built_model",
            "open_source_release": True,
            "open_source_without_monetisation": True,
            "weights_arch_usage_public": True,
            "training_compute_flops": "over_1e25",  # Systemic (exceeding)!
            "general_purpose": True,
            "placing_date": "2025-09-01",
            "outside_eu_provider": True
        })
        
        # No carve-outs when systemic
        assert len(scope.carve_outs) == 0
        assert scope.is_systemic_risk == True
        
        # EU rep still required (systemic blocks carve-out)
        assert scope.needs_eu_representative == True
        
        # Still requires everything
        assert scope.requires_public_summary == True
        assert scope.requires_copyright_policy == True
        
        # Check obligations include systemic requirements
        assert any("Model evaluation" in o for o in scope.applicable_obligations)
        assert any("Risk mitigation" in o for o in scope.applicable_obligations)
        assert any("Notify the Commission" in o for o in scope.applicable_obligations)
    
    def test_light_finetuner_voluntary(self):
        """Test light fine-tuners get voluntary template."""
        classifier = ScopeClassifier()
        
        scope = classifier.classify({
            "provider_status": "light_finetuner",
            "modification_compute_ratio": "10_to_33",  # ≤33%
            "placing_date": "2025-09-01"
        })
        
        assert scope.is_significant_modifier == False
        assert scope.is_provider == False
        assert scope.requires_public_summary == False
        assert scope.requires_copyright_policy == False
        assert scope.provider_type == "light_finetuner"
    
    def test_api_user_no_obligations(self):
        """Test API users have advisory text only (system integrator)."""
        classifier = ScopeClassifier()
        
        scope = classifier.classify({
            "provider_status": "api_user",
            "placing_date": "2025-09-01"
        })
        
        assert scope.is_gpai_provider == False
        assert scope.is_provider == False
        assert scope.requires_public_summary == False
        assert scope.requires_copyright_policy == False
        assert scope.provider_type == "api_user"
        # API users are system integrators with advisory text
        assert scope.provider_role == "system_integrator"
        assert len(scope.applicable_obligations) > 0
        assert "system integrator" in scope.applicable_obligations[0].lower()


# Test fixtures for golden archetypes
class TestGoldenArchetypes:
    """Test golden archetype scenarios."""
    
    @pytest.fixture
    def classifier(self):
        return ScopeClassifier()
    
    def test_gpai_provider_non_sme(self, classifier):
        """Standard GPAI provider (non-SME)."""
        scope = classifier.classify({
            "placing_date": "2025-09-01",
            "sme_status": "no_not_sme",
            "provider_status": "built_model",
            "general_purpose": True,
            "source_types": ["web_scraped"]
        })
        
        assert scope.is_gpai_provider == True
        assert scope.is_provider == True
        assert scope.top_domain_rule == "10% (min 1)"
        assert scope.compliance_deadlines['public_summary_due'] == date(2025, 9, 1)
        assert scope.compliance_deadlines['copyright_policy_due'] == date(2025, 9, 1)
    
    def test_gpai_provider_sme(self, classifier):
        """GPAI provider with SME benefits."""
        scope = classifier.classify({
            "placing_date": "2025-09-01",
            "sme_status": "yes_sme",
            "provider_status": "built_model",
            "general_purpose": True,
            "source_types": ["web_scraped"]
        })
        
        assert scope.is_gpai_provider == True
        assert scope.is_sme == True
        assert scope.top_domain_rule == "5% or 1000 (whichever lower, min 1)"
    
    def test_open_source_non_eu_non_systemic(self, classifier):
        """Open-source non-EU provider without systemic risk - gets carve-outs."""
        scope = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "built_model",
            "general_purpose": True,
            "open_source_release": True,
            "open_source_without_monetisation": True,  # Required for carve-out
            "weights_arch_usage_public": True,  # Required for carve-out
            "outside_eu_provider": True,
            "training_compute_flops": "under_1e25"
        })
        
        assert scope.is_open_source_release == True
        assert scope.requires_public_summary == True
        assert scope.requires_copyright_policy == True
        assert scope.needs_eu_representative == False  # Carve-out applies!
        assert len(scope.carve_outs) == 3  # Tech docs, downstream, and EU rep
    
    def test_pre_existing_commercial(self, classifier):
        """Pre-existing commercial model with grace period."""
        scope = classifier.classify({
            "placing_date": "2024-06-01",  # Pre-existing
            "still_on_market": True,
            "provider_status": "built_model",
            "general_purpose": True
        })
        
        assert scope.compliance_deadlines['public_summary_due'] == date(2027, 8, 2)  # Grace
        assert scope.compliance_deadlines['copyright_policy_due'] == date(2025, 8, 2)  # No grace
        assert scope.compliance_deadlines['other_obligations_due'] == date(2025, 8, 2)  # No grace
    
    def test_modifier_exactly_33_percent(self, classifier):
        """Modifier at exactly 33% is NOT significant."""
        scope = classifier.classify({
            "provider_status": "significant_modifier",
            "modification_compute_ratio": "exactly_33",
            "general_purpose": False,  # Not GPAI
            "placing_date": "2025-09-01"
        })
        
        assert scope.is_significant_modifier == False
        assert scope.is_provider == False
        assert scope.provider_type == "light_finetuner"  # Non-significant modifier = light finetuner
    
    def test_modifier_over_33_percent(self, classifier):
        """Modifier over 33% IS significant."""
        scope = classifier.classify({
            "provider_status": "significant_modifier",
            "modification_compute_ratio": "34_to_50",
            "general_purpose": True,
            "placing_date": "2025-09-01"
        })
        
        assert scope.is_significant_modifier == True
        assert scope.is_provider == True
        assert scope.provider_type == "significant_modifier"
    
    # ===== COMPREHENSIVE TESTS FROM GPT-5 PRO (Fix J) =====
    
    def test_eu_provider_opensource_conditions_met(self, classifier):
        """EU provider with all open-source conditions met."""
        scope = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "built_model",
            "general_purpose": True,
            "open_source_release": True,
            "open_source_without_monetisation": True,
            "weights_arch_usage_public": True,
            "outside_eu_provider": False,  # EU provider
            "training_compute_flops": "under_1e25"  # Not systemic
        })
        
        # EU provider doesn't need EU rep
        assert scope.needs_eu_representative == False
        
        # Should get tech docs and downstream carve-outs
        assert len(scope.carve_outs) == 2
        assert any("Technical documentation" in c for c in scope.carve_outs)
        assert any("Downstream documentation" in c for c in scope.carve_outs)
        assert not any("EU authorized representative" in c for c in scope.carve_outs)
    
    def test_eu_provider_opensource_missing_weights(self, classifier):
        """EU provider missing weights_public condition."""
        scope = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "built_model",
            "general_purpose": True,
            "open_source_release": True,
            "open_source_without_monetisation": True,
            "weights_arch_usage_public": False,  # Missing this condition
            "outside_eu_provider": False,
            "training_compute_flops": "under_1e25"
        })
        
        # No carve-outs when conditions not all met
        assert len(scope.carve_outs) == 0
        assert scope.needs_eu_representative == False  # EU provider
    
    def test_non_eu_opensource_all_carveouts(self, classifier):
        """Non-EU provider with all conditions gets all carve-outs."""
        scope = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "built_model",
            "general_purpose": True,
            "open_source_release": True,
            "open_source_without_monetisation": True,
            "weights_arch_usage_public": True,
            "outside_eu_provider": True,  # Non-EU
            "training_compute_flops": "under_1e25",  # Not systemic
            "eu_availability": True  # Available in EU
        })
        
        # Gets EU rep carve-out when all conditions met
        assert scope.needs_eu_representative == False
        assert len(scope.carve_outs) == 3
        assert any("EU authorized representative" in c for c in scope.carve_outs)
    
    def test_non_eu_opensource_systemic_no_carveouts(self, classifier):
        """Systemic risk blocks all carve-outs."""
        scope = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "built_model",
            "general_purpose": True,
            "open_source_release": True,
            "open_source_without_monetisation": True,
            "weights_arch_usage_public": True,
            "outside_eu_provider": True,
            "training_compute_flops": "over_1e25",  # Systemic!
            "eu_availability": True
        })
        
        # Systemic blocks all carve-outs
        assert scope.is_systemic_risk == True
        assert scope.needs_eu_representative == True  # No carve-out
        assert len(scope.carve_outs) == 0  # No carve-outs
    
    def test_notification_missing_date_fallback(self, classifier):
        """ASAP label when notification date missing."""
        scope = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "built_model",
            "general_purpose": True,
            "training_compute_flops": "over_1e25",  # Exceeds threshold
            # No threshold_known_date provided
        })
        
        assert scope.needs_threshold_notification == True
        assert scope.notification_deadline is None
        assert scope.notification_deadline_label == "ASAP (≤14 days from when you know threshold is/will be exceeded)"
        assert len(scope.validation_warnings) > 0
        assert any("threshold_known_date" in w for w in scope.validation_warnings)
    
    def test_gpai_all_false_not_detected(self, classifier):
        """No false positive GPAI detection."""
        scope = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "built_model",
            "general_purpose": False,  # Explicitly not general-purpose
            "multi_task_capable": False,
            "parameter_count_hint": "under_1b",
            "training_compute_flops": "under_1e23"
        })
        
        assert scope.is_gpai_provider == False
        assert scope.provider_type == "unknown"  # Not GPAI, not modifier
    
    def test_update_anchored_to_publication(self, classifier):
        """6-month updates anchored to publication date."""
        scope = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "built_model",
            "general_purpose": True,
            "last_summary_published_on": "2025-10-15",  # Published later
            "is_update": True
        })
        
        # Should be 6 months from publication, not placing
        expected_next = datetime.strptime("2025-10-15", "%Y-%m-%d").date() + timedelta(days=182)
        assert scope.compliance_deadlines['next_update_due'] == expected_next
    
    def test_modifier_capability_change_override(self, classifier):
        """User belief overrides compute ratio for modification."""
        scope = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "significant_modifier",
            "general_purpose": True,
            "modification_compute_ratio": "10_to_33",  # Below threshold
            "believes_significant": True  # But user says it's significant
        })
        
        # User override should make it significant
        assert scope.is_significant_modifier == True
        assert scope.is_provider == True
    
    def test_non_eu_market_no_eu_rep(self, classifier):
        """Model not available in EU doesn't need EU rep."""
        scope = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "built_model",
            "general_purpose": True,
            "outside_eu_provider": True,
            "eu_availability": False  # Not available in EU
        })
        
        # No EU rep needed if not in EU market
        assert scope.needs_eu_representative == False
    
    def test_internal_only_no_eu_rep(self, classifier):
        """Internal-only use doesn't need EU rep."""
        scope = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "internal_only",
            "general_purpose": True,
            "outside_eu_provider": True,
            "eu_availability": True  # Even if technically in EU
        })
        
        # Internal-only is not placing on market
        assert scope.needs_eu_representative == False
    
    def test_designation_overrides_compute(self, classifier):
        """Commission designation makes model systemic regardless of compute."""
        scope = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "built_model",
            "general_purpose": True,
            "training_compute_flops": "under_1e25",  # Low compute
            "designated_systemic_risk": True  # But designated
        })
        
        # Designation overrides compute check
        assert scope.is_systemic_risk == True
    
    def test_indicative_signals_present(self, classifier):
        """Indicative GPAI signals properly detected."""
        scope = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "built_model",
            "general_purpose": True,
            "training_compute_flops": "1e23_to_1e25",  # Indicative range
            "parameter_count_hint": "over_1b"  # Also indicative
        })
        
        # Should have indicative signals
        assert scope.indicative_signals['indicative_gpai_signal'] == True
        assert len(scope.indicative_signals['reasons']) >= 2
        assert any("10^23" in r for r in scope.indicative_signals['reasons'])
        assert any("1B parameter" in r for r in scope.indicative_signals['reasons'])
    
    def test_notification_at_exact_threshold(self, classifier):
        """Notification required at exactly 10^25 FLOP."""
        scope = classifier.classify({
            "provider_status": "built_model",
            "general_purpose": True,
            "training_compute_flops": "exactly_1e25",
            "threshold_known_date": "2025-09-01",
            "placing_date": "2025-09-20",
        })
        
        # Notification required at exactly 10^25
        assert scope.needs_threshold_notification is True
        assert scope.notification_deadline == date(2025, 9, 15)  # 14 days from known date
        
        # But NOT systemic risk at exactly 10^25 (requires exceeding)
        assert scope.is_systemic_risk is False
    
    def test_notification_obligation_added_even_if_not_systemic(self, classifier):
        """Notification obligation appears even for non-systemic models at 10^25."""
        scope = classifier.classify({
            "provider_status": "built_model",
            "general_purpose": True,
            "training_compute_flops": "exactly_1e25",
            "threshold_known_date": "2025-09-01",
            "placing_date": "2025-09-20"
        })
        
        # Not systemic but needs notification
        assert scope.is_systemic_risk is False
        assert scope.needs_threshold_notification is True
        
        # Notification obligation should be present
        notify_line = "Notify the Commission within 14 days when the 10^25 FLOP threshold is met or will be met"
        assert notify_line in scope.applicable_obligations
        
        # But no Art. 55 obligations
        assert not any("Art. 55" in obl for obl in scope.applicable_obligations)
    
    def test_exact_1e25_nonEU_opensource_all_conditions(self, classifier):
        """Non-EU provider at exactly 10^25 with all open-source conditions."""
        scope = classifier.classify({
            "placing_date": "2025-09-20",
            "provider_status": "built_model",
            "general_purpose": True,
            "training_compute_flops": "exactly_1e25",
            "threshold_known_date": "2025-09-01",
            "open_source_release": True,
            "open_source_without_monetisation": True,
            "weights_arch_usage_public": True,
            "outside_eu_provider": True,
            "eu_availability": True
        })
        
        # Not systemic at exactly 10^25
        assert scope.is_systemic_risk is False
        
        # All carve-outs should apply (including EU-rep)
        assert len(scope.carve_outs) == 3
        assert any("Technical documentation" in c for c in scope.carve_outs)
        assert any("Downstream documentation" in c for c in scope.carve_outs)
        assert any("EU authorized representative" in c for c in scope.carve_outs)
        
        # Notification still required
        assert scope.needs_threshold_notification is True
        notify_line = "Notify the Commission within 14 days when the 10^25 FLOP threshold is met or will be met"
        assert notify_line in scope.applicable_obligations
    
    def test_exact_1e25_EU_provider_opensource_all_conditions(self, classifier):
        """EU provider at exactly 10^25 with all open-source conditions."""
        scope = classifier.classify({
            "placing_date": "2025-09-20",
            "provider_status": "built_model",
            "general_purpose": True,
            "training_compute_flops": "exactly_1e25",
            "threshold_known_date": "2025-09-01",
            "open_source_release": True,
            "open_source_without_monetisation": True,
            "weights_arch_usage_public": True,
            "outside_eu_provider": False,  # EU provider
            "eu_availability": True
        })
        
        # Not systemic at exactly 10^25
        assert scope.is_systemic_risk is False
        
        # Only tech docs and downstream carve-outs (no EU-rep line for EU providers)
        assert len(scope.carve_outs) == 2
        assert any("Technical documentation" in c for c in scope.carve_outs)
        assert any("Downstream documentation" in c for c in scope.carve_outs)
        assert not any("EU authorized representative" in c for c in scope.carve_outs)
        
        # Notification still required
        assert scope.needs_threshold_notification is True
        notify_line = "Notify the Commission within 14 days when the 10^25 FLOP threshold is met or will be met"
        assert notify_line in scope.applicable_obligations
    
    def test_significant_mod_threshold_bins(self, classifier):
        """Test new modification ratio bins are correctly classified."""
        # At or below 33% - NOT significant
        scope_le33 = classifier.classify({
            "provider_status": "significant_modifier",
            "general_purpose": True,
            "modification_compute_ratio": "le_33",
            "placing_date": "2025-09-01"
        })
        assert scope_le33.is_significant_modifier is False
        
        # Greater than 33% - IS significant
        scope_gt33 = classifier.classify({
            "provider_status": "significant_modifier",
            "general_purpose": True,
            "modification_compute_ratio": "gt_33_to_50",
            "placing_date": "2025-09-01"
        })
        assert scope_gt33.is_significant_modifier is True
        
        # Over 50% - IS significant
        scope_gt50 = classifier.classify({
            "provider_status": "significant_modifier",
            "general_purpose": True,
            "modification_compute_ratio": "gt_50",
            "placing_date": "2025-09-01"
        })
        assert scope_gt50.is_significant_modifier is True
    
    def test_significant_mod_threshold_numeric_parsing(self, classifier):
        """Test numeric percentage parsing for modification threshold."""
        # Test with percentage string "33%" - NOT significant
        scope_33_pct = classifier.classify({
            "provider_status": "significant_modifier",
            "general_purpose": True,
            "modification_compute_ratio": "33%",
            "placing_date": "2025-09-01"
        })
        assert scope_33_pct.is_significant_modifier is False
        
        # Test with "33.00" - NOT significant
        scope_33_00 = classifier.classify({
            "provider_status": "significant_modifier",
            "general_purpose": True,
            "modification_compute_ratio": "33.00",
            "placing_date": "2025-09-01"
        })
        assert scope_33_00.is_significant_modifier is False
        
        # Test with "33.3334%" - IS significant (just over 1/3)
        scope_33_3334 = classifier.classify({
            "provider_status": "significant_modifier",
            "general_purpose": True,
            "modification_compute_ratio": "33.3334%",
            "placing_date": "2025-09-01"
        })
        assert scope_33_3334.is_significant_modifier is True
        
        # Test with comma decimal "33,34" - IS significant
        scope_comma = classifier.classify({
            "provider_status": "significant_modifier",
            "general_purpose": True,
            "modification_compute_ratio": "33,34",
            "placing_date": "2025-09-01"
        })
        assert scope_comma.is_significant_modifier is True
    
    def test_carveout_blockers_listed(self, classifier):
        """Test that carve-out blockers are tracked when conditions not met."""
        # Open-source but monetised
        scope_monetised = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "built_model",
            "general_purpose": True,
            "open_source_release": True,
            "open_source_without_monetisation": False,  # Monetised!
            "weights_arch_usage_public": True,
            "outside_eu_provider": True
        })
        
        assert len(scope_monetised.carve_outs) == 0
        assert len(scope_monetised.carveout_blockers) > 0
        assert any("monetised" in b for b in scope_monetised.carveout_blockers)
        
        # Open-source but weights not public
        scope_no_weights = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "built_model",
            "general_purpose": True,
            "open_source_release": True,
            "open_source_without_monetisation": True,
            "weights_arch_usage_public": False,  # Weights not public!
            "outside_eu_provider": True
        })
        
        assert len(scope_no_weights.carve_outs) == 0
        assert len(scope_no_weights.carveout_blockers) > 0
        assert any("not publicly available" in b for b in scope_no_weights.carveout_blockers)
        
        # Open-source but systemic risk
        scope_systemic = classifier.classify({
            "placing_date": "2025-09-01",
            "provider_status": "built_model",
            "general_purpose": True,
            "open_source_release": True,
            "open_source_without_monetisation": True,
            "weights_arch_usage_public": True,
            "training_compute_flops": "over_1e25",  # Systemic!
            "outside_eu_provider": True
        })
        
        assert scope_systemic.is_systemic_risk is True
        assert len(scope_systemic.carve_outs) == 0
        assert len(scope_systemic.carveout_blockers) > 0
        assert any("Systemic risk" in b for b in scope_systemic.carveout_blockers)