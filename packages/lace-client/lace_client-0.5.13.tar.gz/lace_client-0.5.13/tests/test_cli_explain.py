"""
Tests for CLI explain mode and placement display.
"""

import pytest
import json
import sys
import os
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

from lace.cli import main


class TestCLIExplainMode:
    """Test CLI explain flag shows decision trace and disclaimer."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    @pytest.fixture
    def test_answers_file(self, tmp_path):
        """Create a test answers file."""
        answers = {
            "provider_status": "built_model",
            "offered_in_eu_market": True,
            "internal_only_use": False,
            "placing_date": "2025-09-01",
            "sme_status": "no_not_sme",
            "general_purpose": True
        }
        answers_file = tmp_path / "answers.json"
        with open(answers_file, 'w') as f:
            json.dump(answers, f)
        return answers_file
    
    def test_cli_explain_shows_decision_trace_and_disclaimer(self, runner, test_answers_file):
        """Test that --explain shows decision trace and disclaimer."""
        result = runner.invoke(main, ['scope', '--answers', str(test_answers_file), '--explain'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Should show decision trace section
        assert "Decision Trace" in output
        assert "→" in output  # Trace bullet points
        
        # Should show disclaimer
        assert "This tool is informational only and not legal advice" in output
        
        # Should contain provider determination in trace
        assert "provider_status=built_model" in output or "model provider" in output.lower()
    
    def test_cli_without_explain_no_trace(self, runner, test_answers_file):
        """Test that without --explain, no decision trace is shown."""
        result = runner.invoke(main, ['scope', '--answers', str(test_answers_file)])
        
        assert result.exit_code == 0
        output = result.output
        
        # Should NOT show decision trace section
        assert "Decision Trace" not in output
        
        # But should still show disclaimer
        assert "informational only" in output.lower()


class TestCLIPlacementDisplay:
    """Test placement status section and commercial hints."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_cli_shows_placement_and_commercial_hint(self, runner, tmp_path):
        """Test placement section with commercial deployment hint."""
        # Commercial deployment scenario
        answers = {
            "provider_status": "built_model",
            "integrated_into_own_system": True,  # Commercial indicator
            "offered_in_eu_market": False,
            "internal_only_use": False,
            "placing_date": "2025-09-01",
            "sme_status": "no_not_sme",
            "general_purpose": True
        }
        answers_file = tmp_path / "commercial_answers.json"
        with open(answers_file, 'w') as f:
            json.dump(answers, f)
        
        result = runner.invoke(main, ['scope', '--answers', str(answers_file)])
        
        assert result.exit_code == 0
        output = result.output
        
        # Should show placement status
        assert "Market Placement Status" in output
        assert "✓ Placed on the EU market" in output
        
        # Should show commercial deployment hint
        assert "typical commercial deployment" in output
        assert "Commission generally treats as 'placed'" in output
    
    def test_cli_not_placed_shows_advisory(self, runner, tmp_path):
        """Test that not placed shows advisory only."""
        # R&D prototype scenario - not placed
        answers = {
            "provider_status": "built_model",
            "offered_in_eu_market": False,
            "integrated_into_own_system": False,
            "internal_only_use": True,
            "essential_to_service": False,
            "affects_individuals_rights": False,
            "placing_date": "2025-09-01",
            "sme_status": "no_not_sme",
            "general_purpose": True
        }
        answers_file = tmp_path / "rd_answers.json"
        with open(answers_file, 'w') as f:
            json.dump(answers, f)
        
        result = runner.invoke(main, ['scope', '--answers', str(answers_file)])
        
        assert result.exit_code == 0
        output = result.output
        
        # Should show not placed
        assert "✗ Not placed on the EU market" in output
        
        # Should show advisory only note
        assert "Advisory only" in output
        assert "no model-level obligations apply" in output


class TestCLISystemIntegrator:
    """Test system integrator gets advisory only."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_cli_system_integrator_advisory_only_no_deadlines(self, runner, tmp_path):
        """System integrators should get advisory text, no deadlines."""
        answers = {
            "provider_status": "api_user",  # System integrator
            "modification_compute_ratio": "le_33",  # Not significant
            "offered_in_eu_market": True,
            "placing_date": "2025-09-01",
            "sme_status": "no_not_sme",
            "general_purpose": True
        }
        answers_file = tmp_path / "integrator_answers.json"
        with open(answers_file, 'w') as f:
            json.dump(answers, f)
        
        result = runner.invoke(main, ['scope', '--answers', str(answers_file)])
        
        assert result.exit_code == 0
        output = result.output
        
        # Should show system integrator role
        assert "System Integrator" in output
        assert "Model obligations sit with upstream provider" in output
        
        # Should NOT show compliance deadlines section
        assert "Compliance Deadlines" not in output or "Advisory only" in output


class TestCLIUnsureSummary:
    """Test unsure resolution summary and privacy note."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_cli_unsure_summary_privacy_note(self, runner, tmp_path):
        """Test unsure resolution summary with privacy note."""
        answers = {
            "provider_status": "unsure",
            "provider_status_unsure_description": "We fine-tuned GPT-3",
            "essential_to_service": "unsure",
            "essential_to_service_unsure_description": "Used for analytics",
            "offered_in_eu_market": True,
            "placing_date": "2025-09-01",
            "sme_status": "no_not_sme",
            "general_purpose": True
        }
        answers_file = tmp_path / "unsure_answers.json"
        with open(answers_file, 'w') as f:
            json.dump(answers, f)
        
        # Disable remote LLM to use heuristics
        os.environ['LACE_ALLOW_REMOTE_LLM'] = 'false'
        
        result = runner.invoke(main, ['scope', '--answers', str(answers_file)])
        
        assert result.exit_code == 0
        output = result.output
        
        # Should show unsure resolution summary
        assert "Unsure Resolution Summary" in output
        assert "informational – NOT legal advice" in output
        
        # Should show resolved values
        assert "provider_status" in output or "essential_to_service" in output
        assert "confidence" in output
        assert "heuristic" in output  # Since remote disabled
        
        # Should show privacy note
        assert "Free-text was scrubbed" in output
        assert "raw text is not stored" in output
        
        # Should NOT contain raw descriptions
        assert "We fine-tuned GPT-3" not in output
        assert "Used for analytics" not in output


class TestCLIJSONOutput:
    """Test JSON output includes all new fields."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_cli_json_includes_new_fields(self, runner, tmp_path):
        """JSON output should include all new fields."""
        answers = {
            "provider_status": "built_model",
            "offered_in_eu_market": True,
            "placing_date": "2025-09-01",
            "sme_status": "no_not_sme",
            "general_purpose": True
        }
        answers_file = tmp_path / "json_answers.json"
        with open(answers_file, 'w') as f:
            json.dump(answers, f)
        
        result = runner.invoke(main, ['scope', '--answers', str(answers_file), '--json'])
        
        assert result.exit_code == 0
        
        # Parse JSON output
        output_data = json.loads(result.output)
        
        # Check for new fields
        assert 'provider_role' in output_data
        assert 'placed_on_market' in output_data
        assert 'placement_reason' in output_data
        assert 'placement_reason_code' in output_data
        assert 'decision_trace' in output_data
        assert 'unsure_resolutions' in output_data
        assert 'advisory_disclaimer' in output_data
        
        # Check values
        assert output_data['provider_role'] in ['model_provider', 'system_integrator']
        assert isinstance(output_data['placed_on_market'], bool)
        assert output_data['advisory_disclaimer'] == "This tool is informational only and not legal advice."
    
    def test_cli_json_explain_includes_trace(self, runner, tmp_path):
        """JSON with --explain should include decision trace."""
        answers = {
            "provider_status": "built_model",
            "offered_in_eu_market": True,
            "placing_date": "2025-09-01",
            "sme_status": "no_not_sme",
            "general_purpose": True
        }
        answers_file = tmp_path / "json_explain_answers.json"
        with open(answers_file, 'w') as f:
            json.dump(answers, f)
        
        result = runner.invoke(main, ['scope', '--answers', str(answers_file), '--json', '--explain'])
        
        assert result.exit_code == 0
        
        output_data = json.loads(result.output)
        
        # With --explain, decision trace should have content
        assert len(output_data['decision_trace']) > 0
        assert any('provider' in trace.lower() for trace in output_data['decision_trace'])


class TestCLIRemoteLLMFlag:
    """Test --allow-remote-llm flag."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_cli_remote_llm_flag_sets_env(self, runner, tmp_path):
        """Test that --allow-remote-llm sets environment variable."""
        answers = {
            "provider_status": "unsure",
            "provider_status_unsure_description": "Using API",
            "offered_in_eu_market": True,
            "placing_date": "2025-09-01"
        }
        answers_file = tmp_path / "remote_answers.json"
        with open(answers_file, 'w') as f:
            json.dump(answers, f)
        
        # Clear env var first
        os.environ.pop('LACE_ALLOW_REMOTE_LLM', None)
        
        # Run with flag
        with patch.dict(os.environ, {}, clear=False):
            result = runner.invoke(main, ['scope', '--answers', str(answers_file), '--allow-remote-llm'])
            
            # The command should set the env var internally
            # We can't directly test the env var here, but we can check the output
            assert result.exit_code == 0
            
            # With remote enabled, might show different resolution
            output = result.output
            if "Unsure Resolution Summary" in output:
                # Could show either remote or heuristic depending on mock
                assert "confidence" in output


class TestCLICarveOuts:
    """Test carve-out display."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_cli_shows_carveouts_and_blockers(self, runner, tmp_path):
        """Test display of carve-outs and blockers."""
        # OSS with carve-outs
        answers = {
            "provider_status": "built_model",
            "open_source_release": True,
            "open_source_license_type": "apache2",
            "open_source_without_monetisation": True,
            "weights_arch_usage_public": True,
            "access_gating_type": "none",
            "offered_in_eu_market": True,
            "placing_date": "2025-09-01",
            "sme_status": "no_not_sme",
            "general_purpose": True
        }
        answers_file = tmp_path / "oss_answers.json"
        with open(answers_file, 'w') as f:
            json.dump(answers, f)
        
        result = runner.invoke(main, ['scope', '--answers', str(answers_file)])
        
        assert result.exit_code == 0
        output = result.output
        
        # Should show carve-outs
        assert "Open-Source Carve-Outs" in output
        
        # Test with blockers
        answers['access_gating_type'] = 'paid'  # Blocks carve-outs
        blocked_file = tmp_path / "blocked_answers.json"
        with open(blocked_file, 'w') as f:
            json.dump(answers, f)
        
        result = runner.invoke(main, ['scope', '--answers', str(blocked_file)])
        
        assert result.exit_code == 0
        output = result.output
        
        # Should show blockers instead
        assert "Carve-Out Blockers" in output or "paid" in output.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])