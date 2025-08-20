"""
Tests for EU AI Act triad logic and placement determination.
Tests provider gating, triad logic, and OSS carve-out enhancements.
"""

import pytest
from datetime import date
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

from lace.regulatory.scope import ScopeClassifier


class TestProviderGating:
    """Test provider gating happens before triad evaluation."""
    
    @pytest.fixture
    def classifier(self):
        return ScopeClassifier()
    
    def test_api_only_no_significant_mod_is_system_integrator(self, classifier):
        """API users without significant modification are system integrators."""
        answers = {
            "provider_status": "api_user",
            "modification_compute_ratio": "le_33",  # ≤33% not significant
            "integrated_into_own_system": True,
            "offered_in_eu_market": True
        }
        scope = classifier.classify(answers)
        
        assert scope.provider_role == "system_integrator"
        assert "system integrator" in scope.applicable_obligations[0].lower()
        assert scope.needs_eu_representative == False
        assert scope.needs_threshold_notification == False
    
    def test_system_integrator_no_model_deadlines(self, classifier):
        """System integrators don't get model-level deadlines."""
        answers = {
            "provider_status": "api_user",
            "modification_compute_ratio": "le_33",
            "placing_date": "2025-09-01"
        }
        scope = classifier.classify(answers)
        
        assert scope.provider_role == "system_integrator"
        # Should not have substantive deadlines
        assert 'public_summary_due' not in scope.compliance_deadlines or \
               scope.compliance_deadlines.get('note', '').startswith('Advisory')


class TestTriadLogic:
    """Test the internal-only + non-essential + rights-neutral triad."""
    
    @pytest.fixture
    def classifier(self):
        return ScopeClassifier()
    
    def test_triad_all_false_not_placed(self, classifier):
        """All three triad conditions False → not placed."""
        answers = {
            "provider_status": "built_model",
            "internal_only_use": True,
            "essential_to_service": False,  # Explicitly False
            "affects_individuals_rights": False,  # Explicitly False
            "offered_in_eu_market": False,
            "integrated_into_own_system": False
        }
        scope = classifier.classify(answers)
        
        assert scope.placed_on_market == False
        assert "triad met" in scope.placement_reason.lower()
        assert scope.needs_eu_representative == False
    
    def test_internal_but_essential_is_placed(self, classifier):
        """Internal but essential to service → placed (bank example)."""
        answers = {
            "provider_status": "built_model",
            "internal_only_use": True,
            "essential_to_service": True,  # Bank's chat system
            "affects_individuals_rights": False,
            "offered_in_eu_market": False
        }
        scope = classifier.classify(answers)
        
        assert scope.placed_on_market == True
        assert "essential" in scope.placement_reason.lower()
        assert "triad fails" in scope.placement_reason.lower()
    
    def test_internal_affects_employee_rights_is_placed(self, classifier):
        """Internal but affects employee rights → placed."""
        answers = {
            "provider_status": "built_model",
            "internal_only_use": True,
            "essential_to_service": False,
            "affects_individuals_rights": True,  # HR decisions
            "offered_in_eu_market": False,
            "outside_eu_provider": True
        }
        scope = classifier.classify(answers)
        
        assert scope.placed_on_market == True
        assert "rights" in scope.placement_reason.lower()
        assert scope.needs_eu_representative == True  # Non-EU + placed
    
    def test_internal_unknown_answers_default_to_placed(self, classifier):
        """Unknown/missing triad answers → conservative (placed)."""
        answers = {
            "provider_status": "built_model",
            "internal_only_use": True,
            # essential_to_service missing (None)
            # affects_individuals_rights missing (None)
            "offered_in_eu_market": False
        }
        scope = classifier.classify(answers)
        
        assert scope.placed_on_market == True
        assert "triad fails" in scope.placement_reason.lower()
    
    def test_offered_in_eu_market_always_placed(self, classifier):
        """Direct offering in EU → always placed."""
        answers = {
            "provider_status": "built_model",
            "offered_in_eu_market": True,  # Direct offering
            "internal_only_use": False
        }
        scope = classifier.classify(answers)
        
        assert scope.placed_on_market == True
        assert "directly offered" in scope.placement_reason.lower()
    
    def test_integrated_into_own_system_always_placed(self, classifier):
        """Integrated into own system → always placed."""
        answers = {
            "provider_status": "built_model",
            "integrated_into_own_system": True,  # Integration trigger
            "offered_in_eu_market": False,
            "internal_only_use": False
        }
        scope = classifier.classify(answers)
        
        assert scope.placed_on_market == True
        assert "integrated" in scope.placement_reason.lower()


class TestOSSGatingPolicy:
    """Test open-source carve-out gating policy (block/warn/allow)."""
    
    @pytest.fixture
    def classifier(self):
        return ScopeClassifier()
    
    def test_oss_paid_blocks_carveouts(self, classifier):
        """Paid access blocks all carve-outs."""
        answers = {
            "provider_status": "built_model",
            "open_source_release": True,
            "access_gating_type": "paid",  # BLOCKS
            "open_source_without_monetisation": True,
            "weights_arch_usage_public": True,
            "open_source_license_type": "apache2",
            "offered_in_eu_market": True
        }
        scope = classifier.classify(answers)
        
        assert len(scope.carve_outs) == 0
        assert any("paid" in b.lower() for b in scope.carveout_blockers)
    
    def test_oss_login_only_warns_allows(self, classifier):
        """Login-only access warns but allows carve-outs."""
        answers = {
            "provider_status": "built_model",
            "open_source_release": True,
            "access_gating_type": "login_only",  # WARNS
            "open_source_without_monetisation": True,
            "weights_arch_usage_public": True,
            "open_source_license_type": "mit",
            "offered_in_eu_market": True
        }
        scope = classifier.classify(answers)
        
        # Carve-outs should apply
        assert len(scope.carve_outs) > 0
        # But with warning
        assert any("login" in w.lower() for w in scope.validation_warnings)
    
    def test_oss_api_key_free_warns_allows(self, classifier):
        """Free API key warns but allows carve-outs."""
        answers = {
            "provider_status": "built_model",
            "open_source_release": True,
            "access_gating_type": "api_key_free",  # WARNS
            "open_source_without_monetisation": True,
            "weights_arch_usage_public": True,
            "open_source_license_type": "gpl3",
            "offered_in_eu_market": True
        }
        scope = classifier.classify(answers)
        
        assert len(scope.carve_outs) > 0
        assert any("api" in w.lower() for w in scope.validation_warnings)
    
    def test_oss_custom_license_warns_allows(self, classifier):
        """Custom license warns but doesn't block carve-outs."""
        answers = {
            "provider_status": "built_model",
            "open_source_release": True,
            "access_gating_type": "none",
            "open_source_without_monetisation": True,
            "weights_arch_usage_public": True,
            "open_source_license_type": "custom",  # WARNS
            "offered_in_eu_market": True
        }
        scope = classifier.classify(answers)
        
        assert len(scope.carve_outs) > 0
        assert any("custom license" in w.lower() for w in scope.validation_warnings)
    
    def test_oss_no_license_blocks_carveouts(self, classifier):
        """No license specified blocks carve-outs."""
        answers = {
            "provider_status": "built_model",
            "open_source_release": True,
            "access_gating_type": "none",
            "open_source_without_monetisation": True,
            "weights_arch_usage_public": True,
            "open_source_license_type": "none",  # BLOCKS
            "offered_in_eu_market": True
        }
        scope = classifier.classify(answers)
        
        assert len(scope.carve_outs) == 0
        assert any("no license" in b.lower() for b in scope.carveout_blockers)


class TestBackCompatibility:
    """Test backward compatibility mappings."""
    
    @pytest.fixture
    def classifier(self):
        return ScopeClassifier()
    
    def test_eu_availability_maps_to_offered(self, classifier):
        """eu_availability should map to offered_in_eu_market."""
        answers = {
            "provider_status": "built_model",
            "eu_availability": True,  # Old field
            # offered_in_eu_market not provided
        }
        scope = classifier.classify(answers)
        
        # Should treat as offered
        assert scope.placed_on_market == True
        assert "back-compat" in str(scope.decision_trace).lower()


class TestDecisionTrace:
    """Test decision trace for transparency."""
    
    @pytest.fixture
    def classifier(self):
        return ScopeClassifier()
    
    def test_decision_trace_includes_provider_and_triad(self, classifier):
        """Decision trace should show both provider and placement logic."""
        answers = {
            "provider_status": "significant_modifier",
            "modification_compute_ratio": "gt_33_to_50",
            "internal_only_use": True,
            "essential_to_service": True,
            "affects_individuals_rights": False,
            "offered_in_eu_market": False
        }
        scope = classifier.classify(answers)
        
        trace_str = " ".join(scope.decision_trace)
        assert "significant modifier" in trace_str.lower()
        assert "essential" in trace_str.lower()
        assert "triad" in trace_str.lower()


class TestGoldenArchetypes:
    """Test real-world scenarios from GPT-5 Pro guidance."""
    
    @pytest.fixture
    def classifier(self):
        return ScopeClassifier()
    
    def test_bank_client_chat_llm(self, classifier):
        """Bank fine-tuning LLM for client chat → model provider + placed."""
        answers = {
            "provider_status": "significant_modifier",
            "modification_compute_ratio": "gt_33_to_50",
            "integrated_into_own_system": True,
            "internal_only_use": False,  # Client-facing
            "essential_to_service": True,
            "affects_individuals_rights": True,  # Financial services
            "offered_in_eu_market": False,
            "outside_eu_provider": False
        }
        scope = classifier.classify(answers)
        
        assert scope.provider_role == "model_provider"
        assert scope.placed_on_market == True
        assert scope.is_significant_modifier == True
    
    def test_law_firm_internal_legal_model(self, classifier):
        """Law firm internal model → model provider + placed."""
        answers = {
            "provider_status": "built_model",
            "internal_only_use": True,
            "essential_to_service": True,  # Core to legal service
            "affects_individuals_rights": True,  # Legal advice affects clients
            "offered_in_eu_market": False,
            "general_purpose": True
        }
        scope = classifier.classify(answers)
        
        assert scope.provider_role == "model_provider"
        assert scope.placed_on_market == True
        assert "essential" in scope.placement_reason.lower()
        assert "rights" in scope.placement_reason.lower()
    
    def test_retailer_recommendation_engine(self, classifier):
        """Retailer recommendation engine → placed."""
        answers = {
            "provider_status": "built_model",
            "integrated_into_own_system": True,  # E-commerce platform
            "internal_only_use": False,
            "essential_to_service": True,
            "affects_individuals_rights": False,  # Just recommendations
            "offered_in_eu_market": False
        }
        scope = classifier.classify(answers)
        
        assert scope.placed_on_market == True
        assert "integrated" in scope.placement_reason.lower()
    
    def test_rd_prototype_not_placed(self, classifier):
        """R&D prototype → not placed (triad met)."""
        answers = {
            "provider_status": "built_model",
            "internal_only_use": True,
            "essential_to_service": False,  # Just research
            "affects_individuals_rights": False,  # Experimental only
            "offered_in_eu_market": False,
            "integrated_into_own_system": False
        }
        scope = classifier.classify(answers)
        
        assert scope.placed_on_market == False
        assert "triad met" in scope.placement_reason.lower()
        assert scope.provider_role == "model_provider"  # Still a provider
        # But no obligations due to not placed
        assert "advisory" in scope.applicable_obligations[0].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])