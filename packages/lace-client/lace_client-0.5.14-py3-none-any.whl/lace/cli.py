"""
Lace CLI - Minimal command-line interface.
"""

import click
import sys
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from . import attest, verify, monitor, about
from .wizard.analyzer import DatasetAnalyzer
from .wizard.questions import DocumentWizard
from .wizard.templates import TemplateGenerator
from .wizard.storage import ImmutableStorage
from .regulatory.scope import ScopeClassifier


@click.group()
@click.version_option(version="0.5.14", prog_name="lace")
def main():
    """Lace - AI Training Transparency Protocol"""
    pass


@main.command()
@click.argument('dataset_path', type=click.Path(exists=True))
@click.option('--name', help='Name for the dataset')
def attest_cmd(dataset_path, name):
    """Create attestation for a dataset."""
    try:
        attestation_id = attest(dataset_path, name)
        click.echo(f"✅ Created attestation: {attestation_id}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('attestation_id')
@click.option('--check-copyright', help='Text to check for copyright')
def verify_cmd(attestation_id, check_copyright):
    """Verify an attestation."""
    try:
        result = verify(attestation_id, check_copyright)
        if result.get('valid'):
            click.echo(f"✅ Attestation {attestation_id} is valid")
        else:
            click.echo(f"❌ Attestation invalid")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
def about_cmd():
    """Display information about Lace."""
    about()


@main.command('generate-docs')
@click.argument('dataset_path', type=click.Path(exists=True))
@click.option('--allow-external-ai', is_flag=True, help='Allow sending redacted samples to external AI')
@click.option('--answers', type=click.Path(exists=True), help='Load answers from file (for CI/CD)')
@click.option('--output', type=click.Path(), help='Output directory for documents')
@click.option('--no-store', is_flag=True, help='Skip S3 storage (local output only)')
@click.option('--skip-validation', is_flag=True, help='Skip S3 bucket validation')
@click.option('--scope-answers', type=click.Path(exists=True), help='Pre-computed scope answers')
def generate_docs_cmd(dataset_path, allow_external_ai, answers, output, no_store, skip_validation, scope_answers):
    """Generate EU compliance documents for dataset."""
    try:
        click.echo("\n" + "="*60)
        click.echo("📋 EU AI Act Compliance Document Generator")
        click.echo("="*60 + "\n")
        
        # Step 1: Analyze dataset
        click.echo("🔍 Analyzing dataset...")
        analyzer = DatasetAnalyzer(allow_external_ai=allow_external_ai)
        analysis_results = analyzer.analyze_dataset(dataset_path)
        
        # Show analysis summary
        click.echo(f"✅ Analysis complete:")
        click.echo(f"   - Files: {analysis_results.get('volume', {}).get('files', 0)}")
        click.echo(f"   - Size: {analysis_results.get('volume', {}).get('bytes', 0) / (1024*1024):.1f} MB")
        click.echo(f"   - Estimated tokens: {analysis_results.get('volume', {}).get('estimated_tokens', 0):,}")
        if analysis_results.get('languages', {}).get('values'):
            click.echo(f"   - Languages: {', '.join(analysis_results['languages']['values'][:3])}")
        if analysis_results.get('top_10_percent_domains'):
            click.echo(f"   - Top domains: {len(analysis_results['top_10_percent_domains'])} domains")
        click.echo()
        
        # Step 2: Run wizard or load answers
        if answers:
            click.echo(f"📄 Loading answers from {answers}...")
            wizard = DocumentWizard(analysis_results)
            wizard_data = wizard.run_with_answers(answers)
        else:
            # Interactive wizard
            wizard = DocumentWizard(analysis_results)
            wizard_data = wizard.run_interactive()
        
        # Step 2.5: Integrate scope classification
        if scope_answers:
            with open(scope_answers, 'r') as f:
                scope_data = json.load(f)
        else:
            # Extract scope-relevant answers from wizard data
            scope_data = {
                'placing_date': wizard_data.get('model_identification', {}).get('release_date'),
                'general_purpose': wizard_data.get('general_purpose', True),
                'open_source_release': wizard_data.get('open_source_release', False),
                'training_compute_flops': wizard_data.get('training_compute_flops', 'unknown'),
                'outside_eu_provider': wizard_data.get('outside_eu_provider', False),
                'provider_status': wizard_data.get('provider_status', 'built_model'),
                'sme_status': wizard_data.get('sme_status', 'unsure')
            }
        
        # Classify scope
        classifier = ScopeClassifier()
        scope = classifier.classify(scope_data)
        
        # Add scope results to wizard data metadata
        wizard_data['_metadata'] = wizard_data.get('_metadata', {})
        wizard_data['_metadata']['is_gpai'] = scope.is_gpai_provider
        wizard_data['_metadata']['is_significant_modifier'] = scope.is_significant_modifier
        wizard_data['_metadata']['is_systemic_risk'] = scope.is_systemic_risk
        wizard_data['_metadata']['is_open_source'] = scope.is_open_source_release
        wizard_data['_metadata']['provider_type'] = scope.provider_type
        wizard_data['_metadata']['applicable_obligations'] = scope.applicable_obligations
        wizard_data['_metadata']['carve_outs'] = scope.carve_outs
        
        # Step 3: Generate documents based on scope
        click.echo("\n📝 Generating documents based on legal obligations...")
        
        # Show what's required
        if scope.is_gpai_provider:
            click.echo("   📜 GPAI Provider - Article 53 obligations apply")
            if scope.carve_outs:
                click.echo(f"   🛡️ Open-source carve-outs: {', '.join(scope.carve_outs)}")
        else:
            click.echo("   📄 Voluntary transparency documents only")
        
        generator = TemplateGenerator()
        documents = {}
        
        # Always generate EU summary for GPAI providers
        if scope.is_gpai_provider:
            click.echo("   • Generating EU Public Summary (Art. 53(1)(d))...")
            eu_summary = generator.generate(wizard_data, is_gpai=True)
            documents['eu_summary'] = eu_summary['document']
            
            click.echo("   • Generating Copyright Policy (Art. 53(1)(c))...")
            copyright_policy = generator.generate_copyright_policy(wizard_data)
            documents['copyright_policy'] = copyright_policy
            
            # Technical docs only if not carved out
            if "Technical documentation (Art. 53(1)(a) - exempt)" not in scope.carve_outs:
                click.echo("   • Generating Technical Documentation (Art. 53(1)(a))...")
                # TODO: Implement technical docs generator
                documents['technical_docs'] = "Technical documentation would be generated here"
            
            # Downstream info only if not carved out
            if "Downstream information (Art. 53(1)(b) - exempt)" not in scope.carve_outs:
                click.echo("   • Generating Downstream Information (Art. 53(1)(b))...")
                # TODO: Implement downstream info generator
                documents['downstream_info'] = "Downstream provider information would be generated here"
        else:
            # Voluntary documents for non-GPAI
            click.echo("   • Generating voluntary EU-style summary...")
            eu_summary = generator.generate(wizard_data, is_gpai=False)
            documents['eu_summary'] = eu_summary['document']
            
            click.echo("   • Generating voluntary copyright statement...")
            copyright_policy = generator.generate_copyright_policy(wizard_data)
            documents['copyright_policy'] = copyright_policy
        
        # Always generate model card and HTML
        click.echo("   • Generating Model Card...")
        model_card = generator.generate_model_card(wizard_data)
        documents['model_card'] = model_card
        
        click.echo("   • Generating HTML output...")
        html_output = generator.generate_html_output(
            documents.get('eu_summary', {}),
            eu_summary.get('label', 'EU Training Summary')
        )
        documents['html_output'] = html_output
        
        # Add metadata
        metadata = {
            'is_gpai': scope.is_gpai_provider,
            'provider_type': scope.provider_type,
            'is_systemic_risk': scope.is_systemic_risk,
            'is_open_source': scope.is_open_source_release,
            'applicable_obligations': scope.applicable_obligations,
            'carve_outs': scope.carve_outs,
            'validation': eu_summary.get('validation'),
            'dataset_path': str(dataset_path),
            'external_ai_used': allow_external_ai,
            'gpai_applicability_date': scope.gpai_applicability_date,
            'enforcement_date': scope.enforcement_date,
            'grace_period_end': scope.grace_period_end
        }
        
        # Step 4: Store documents
        if not no_store:
            try:
                click.echo("\n💾 Storing documents...")
                storage = ImmutableStorage()
                
                if not skip_validation:
                    click.echo("   Validating S3 configuration...")
                    # Validation happens in __init__
                
                bundle_id = storage.store_bundle(documents, metadata)
                click.echo(f"✅ Documents stored with bundle ID: {bundle_id}")
                click.echo(f"   Retention: 7 years (EU compliance)")
                
            except Exception as e:
                click.echo(f"⚠️  S3 storage failed: {e}", err=True)
                click.echo("   Falling back to local output only")
                no_store = True
        
        # Step 5: Save locally if requested
        if output or no_store:
            output_path = Path(output) if output else Path('.') / 'lace_documents'
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save EU summary
            with open(output_path / 'eu_training_summary.json', 'w') as f:
                json.dump(eu_summary['document'], f, indent=2)
            
            # Save model card
            with open(output_path / 'model_card.md', 'w') as f:
                f.write(model_card)
            
            # Save copyright policy
            with open(output_path / 'copyright_policy.md', 'w') as f:
                f.write(copyright_policy)
            
            # Save HTML
            with open(output_path / 'summary.html', 'w') as f:
                f.write(html_output)
            
            # Save metadata
            with open(output_path / 'metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            click.echo(f"\n📁 Documents saved to: {output_path}")
        
        # Show validation status
        if eu_summary.get('validation', {}).get('valid'):
            click.echo("\n✅ Document validation: PASSED")
        else:
            click.echo("\n⚠️  Document validation: FAILED")
            errors = eu_summary.get('validation', {}).get('errors', [])
            for error in errors[:5]:
                click.echo(f"   - {error}")
        
        click.echo("\n" + "="*60)
        click.echo("✨ Document generation complete!")
        click.echo("="*60 + "\n")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)


@main.command('scope')
@click.option('--answers', type=click.Path(exists=True), help='Load answers from JSON file')
@click.option('--allow-remote-llm', is_flag=True, envvar='LACE_ALLOW_REMOTE_LLM',
              help='Allow remote LLM for unsure resolution')
@click.option('--explain', is_flag=True, help='Show detailed decision trace')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.option('--strict-triad/--legacy-placement-logic', default=True,
              help='Use strict triad logic (default) or legacy placement')
def scope_cmd(answers, allow_remote_llm, explain, output_json, strict_triad):
    """Classify EU AI Act scope and obligations."""
    try:
        # Set environment for remote LLM if enabled
        if allow_remote_llm:
            os.environ['LACE_ALLOW_REMOTE_LLM'] = 'true'
        
        # Load answers
        if answers:
            with open(answers, 'r') as f:
                answers_data = json.load(f)
        else:
            # Interactive mode would go here
            click.echo("Interactive mode not yet implemented. Please provide --answers file.")
            sys.exit(1)
        
        # Classify scope
        classifier = ScopeClassifier()
        scope = classifier.classify(answers_data)
        
        if output_json:
            # JSON output with schema version
            output = {
                'schema_version': '1.0.0',
                'provider_role': scope.provider_role,
                'placed_on_market': scope.placed_on_market,
                'placement_reason': scope.placement_reason,
                'placement_reason_code': scope.placement_reason_code,
                'is_gpai_provider': scope.is_gpai_provider,
                'is_systemic_risk': scope.is_systemic_risk,
                'needs_eu_representative': scope.needs_eu_representative,
                'eu_rep_reason': scope.eu_rep_reason,
                'compliance_deadlines': scope.compliance_deadlines,
                'applicable_obligations': scope.applicable_obligations,
                'carve_outs': scope.carve_outs,
                'validation_warnings': scope.validation_warnings,
                'decision_trace': scope.decision_trace if explain else [],
                'unsure_resolutions': scope.unsure_resolutions,
                'gpai_applicability_date': scope.gpai_applicability_date,
                'enforcement_date': scope.enforcement_date,
                'grace_period_end': scope.grace_period_end,
                'systemic_risk_threshold': scope.systemic_risk_threshold,
                'ai_office_template_version': scope.ai_office_template_version,
                'advisory_disclaimer': scope.advisory_disclaimer
            }
            click.echo(json.dumps(output, indent=2, default=str))
        else:
            # Human-readable output
            click.echo("\n" + "="*60)
            click.echo("📋 EU AI Act Scope Classification")
            click.echo("="*60 + "\n")
            
            # Show GPAI applicability dates
            click.echo("📅 Important Dates")
            click.echo(f"   GPAI obligations apply: {scope.gpai_applicability_date}")
            click.echo(f"   Enforcement begins: {scope.enforcement_date}")
            click.echo(f"   Pre-existing models grace period: until {scope.grace_period_end}")
            click.echo()
            
            # Placement Status Section
            click.echo("📍 Market Placement Status")
            if scope.placed_on_market:
                click.echo("   ✓ Making available in EU (Article 3)")
            else:
                click.echo("   ✗ Not making available in EU")
            click.echo(f"   Reason: {scope.placement_reason}")
            
            # Commercial activity indicators
            if (answers_data.get('integrated_into_own_system') == True or 
                (answers_data.get('internal_only_use') == True and 
                 (answers_data.get('essential_to_service') == True or 
                  answers_data.get('affects_individuals_rights') == True))):
                click.echo("   Note: Indicators of 'making available' in the course of")
                click.echo("         a commercial activity (Art. 3)")
            
            if not scope.placed_on_market:
                click.echo("   Note: Advisory only – no model-level obligations apply.")
            
            click.echo(f"\nDisclaimer: {scope.advisory_disclaimer}\n")
            
            # Provider Role
            click.echo("👤 Provider Role")
            if scope.provider_role == "model_provider":
                click.echo("   ✓ Model Provider")
                if scope.is_significant_modifier:
                    click.echo("     (Significant modifier)")
            else:
                click.echo("   ✓ System Integrator")
                click.echo("     Model obligations sit with upstream provider")
            
            # Key Classifications
            click.echo("\n🎯 Key Classifications")
            click.echo(f"   GPAI Provider: {'Yes' if scope.is_gpai_provider else 'No'}")
            click.echo(f"   Systemic Risk: {'Yes' if scope.is_systemic_risk else 'No'}")
            click.echo(f"   Open Source: {'Yes' if scope.is_open_source_release else 'No'}")
            click.echo(f"   SME Status: {'Yes' if scope.is_sme else 'No'}")
            
            # Obligations
            if scope.applicable_obligations:
                click.echo("\n📜 Applicable Obligations")
                for obligation in scope.applicable_obligations[:5]:
                    click.echo(f"   • {obligation}")
                if len(scope.applicable_obligations) > 5:
                    click.echo(f"   ... and {len(scope.applicable_obligations) - 5} more")
            
            # Carve-outs
            if scope.carve_outs:
                click.echo("\n🛡️ Open-Source Carve-Outs")
                for carveout in scope.carve_outs:
                    click.echo(f"   • {carveout}")
            elif scope.carveout_blockers and scope.is_open_source_release:
                click.echo("\n⚠️ Carve-Out Blockers")
                for blocker in scope.carveout_blockers:
                    click.echo(f"   • {blocker}")
            
            # Warnings
            if scope.validation_warnings:
                click.echo("\n⚠️ Validation Warnings")
                for warning in scope.validation_warnings[:3]:
                    click.echo(f"   • {warning}")
            
            # Unsure Resolution Summary
            if scope.unsure_resolutions:
                click.echo("\n🧭 Unsure Resolution Summary (informational – NOT legal advice)")
                for res in scope.unsure_resolutions:
                    via = "remote" if res.get('used_remote') else "heuristic"
                    click.echo(f"   • {res['question_id']} → {res['resolved_value']} "
                             f"(confidence {res['confidence']:.2f}) via {via}")
                    if res.get('warnings'):
                        for warning in res['warnings']:
                            click.echo(f"     ⚠️ {warning}")
                click.echo("\nPrivacy: Free-text was scrubbed before any remote processing;")
                click.echo("         raw text is not stored.")
            
            # Decision Trace (if --explain)
            if explain and scope.decision_trace:
                click.echo("\n🔍 Decision Trace")
                for trace_line in scope.decision_trace:
                    click.echo(f"   → {trace_line}")
            
            # Deadlines
            if scope.compliance_deadlines and 'note' not in scope.compliance_deadlines:
                click.echo("\n📅 Compliance Deadlines")
                for key, value in scope.compliance_deadlines.items():
                    if value and key != 'grace_period_active':
                        click.echo(f"   {key}: {value}")
            
            click.echo("\n" + "="*60 + "\n")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)


@main.command('analyze-dataset')
@click.argument('dataset_path', type=click.Path(exists=True))
@click.option('--allow-external-ai', is_flag=True, help='Allow sending redacted samples to external AI')
@click.option('--output', type=click.Path(), help='Output file for analysis results')
def analyze_dataset_cmd(dataset_path, allow_external_ai, output):
    """Analyze dataset without generating documents."""
    try:
        click.echo("\n🔍 Analyzing dataset...")
        
        analyzer = DatasetAnalyzer(allow_external_ai=allow_external_ai)
        results = analyzer.analyze_dataset(dataset_path)
        
        # Display summary
        click.echo("\n📊 Analysis Results:")
        click.echo(f"   Files: {results.get('volume', {}).get('files', 0)}")
        click.echo(f"   Size: {results.get('volume', {}).get('bytes', 0) / (1024*1024):.1f} MB")
        click.echo(f"   Estimated tokens: {results.get('volume', {}).get('estimated_tokens', 0):,}")
        
        if results.get('languages', {}).get('values'):
            click.echo(f"   Languages: {', '.join(results['languages']['values'])}")
        
        if results.get('top_10_percent_domains'):
            click.echo(f"   Top 10% domains ({len(results['top_10_percent_domains'])} total):")
            for domain in results['top_10_percent_domains'][:5]:
                click.echo(f"      - {domain}")
            if len(results['top_10_percent_domains']) > 5:
                click.echo(f"      ... and {len(results['top_10_percent_domains']) - 5} more")
        
        if results.get('source_types', {}).get('values'):
            click.echo(f"   Source types: {', '.join(results['source_types']['values'])}")
        
        if results.get('modalities', {}).get('values'):
            click.echo(f"   Modalities: {', '.join(results['modalities']['values'])}")
        
        if results.get('pii_signals', {}).get('detected'):
            click.echo(f"   ⚠️  PII detected: {', '.join(results['pii_signals']['values'])}")
        
        # Save to file if requested
        if output:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2)
            click.echo(f"\n💾 Analysis saved to: {output}")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)


@main.command('advise-scope')
@click.option('--answers', type=click.Path(exists=True), help='Load answers from file')
@click.option('--output', type=click.Path(), help='Save scope analysis to file')
def advise_scope_cmd(answers, output):
    """Quickly determine EU AI Act obligations without generating documents."""
    from datetime import date
    
    try:
        click.echo("\n" + "="*60)
        click.echo("🔍 EU AI Act Scope Advisor")
        click.echo("="*60)
        click.echo("\n⚠️  This is guidance, not legal advice\n")
        
        # Load or collect answers
        if answers:
            click.echo(f"Loading answers from {answers}...")
            with open(answers, 'r') as f:
                scope_answers = json.load(f)
        else:
            # Interactive scope questions
            scope_answers = {}
            
            # Critical questions for scope
            click.echo("Please answer these questions to determine your obligations:\n")
            
            # Placing date
            placing_date = click.prompt("When will/did you first make this model available in the EU? (YYYY-MM-DD)", 
                                       default=datetime.now().strftime('%Y-%m-%d'))
            scope_answers['placing_date'] = placing_date
            
            # Check if pre-existing
            if placing_date < "2025-08-02":
                still_on_market = click.confirm("Is the model still (or will be) available in the EU?", default=True)
                scope_answers['still_on_market'] = still_on_market
            
            # SME status
            click.echo("\nSME Criteria: <250 employees AND (≤€50M turnover OR ≤€43M balance sheet)")
            sme_status = click.prompt("Do you qualify as an EU SME?", 
                                     type=click.Choice(['yes_sme', 'no_not_sme', 'unsure']),
                                     default='unsure')
            scope_answers['sme_status'] = sme_status
            
            # Provider status
            click.echo("\nWhat is your role with this model?")
            provider_status = click.prompt("Select", 
                type=click.Choice([
                    'built_model',
                    'significant_modifier', 
                    'light_finetuner',
                    'api_user',
                    'internal_only'
                ]),
                default='built_model'
            )
            scope_answers['provider_status'] = provider_status
            
            # General-purpose
            general_purpose = click.confirm("\nIs this model designed for general-purpose tasks?", default=True)
            scope_answers['general_purpose'] = general_purpose
            
            # Modification ratio if modifier
            if provider_status == 'significant_modifier':
                click.echo("\nCommission threshold: MORE THAN 1/3 (>33%) = significant")
                compute_ratio = click.prompt("Your compute as % of original", 
                    type=click.Choice([
                        'unknown',
                        'under_10',
                        '10_to_33',
                        'exactly_33',
                        '34_to_50',
                        'over_50'
                    ]),
                    default='unknown'
                )
                scope_answers['modification_compute_ratio'] = compute_ratio
            
            # Systemic risk
            click.echo("\n10^25 FLOP = Systemic risk threshold")
            compute_flops = click.prompt("Total training compute", 
                type=click.Choice([
                    'unknown',
                    'under_1e25',
                    'exactly_1e25',
                    'over_1e25'
                ]),
                default='unknown'
            )
            scope_answers['training_compute_flops'] = compute_flops
            
            # Open-source
            open_source = click.confirm("\nWill you release this under a free/open-source license?", default=False)
            scope_answers['open_source_release'] = open_source
            
            # Non-EU provider
            outside_eu = click.confirm("\nIs the provider entity based outside the EU?", default=False)
            scope_answers['outside_eu_provider'] = outside_eu
        
        # Classify scope
        classifier = ScopeClassifier()
        scope = classifier.classify(scope_answers)
        
        # Display results with clear formatting
        click.echo("\n" + "="*60)
        click.echo("📊 EU AI Act Scope Analysis")
        click.echo("="*60)
        
        # Provider status
        click.echo(f"\n🏢 Provider Status")
        click.echo(f"   Type: {scope.provider_type}")
        click.echo(f"   GPAI Provider: {'Yes' if scope.is_gpai_provider else 'No'}")
        if scope.is_significant_modifier:
            click.echo(f"   Significant Modifier: Yes (>33% compute)")
        click.echo(f"   SME Status: {'Yes' if scope.is_sme else 'No/Unknown'}")
        
        # Obligations
        click.echo(f"\n📋 Obligations")
        if scope.applicable_obligations:
            for obligation in scope.applicable_obligations:
                click.echo(f"   • {obligation}")
        else:
            click.echo("   No Article 53 obligations (voluntary transparency only)")
        
        # Open-source status (only show if actually open-source)
        if scope.is_open_source_release:
            click.echo(f"\n📖 Open-Source Status")
            click.echo(f"   Still Required:")
            click.echo(f"   • Public summary of training content")
            click.echo(f"   • Copyright compliance policy")
            if scope.needs_eu_representative:
                click.echo(f"   • EU authorized representative")
            
            # Only show actual applicable carve-outs
            if scope.carve_outs:
                click.echo(f"   Carve-outs Applied:")
                for carveout in scope.carve_outs:
                    click.echo(f"   • {carveout}")
        
        # Deadlines with clear labels
        click.echo(f"\n📅 Compliance Deadlines")
        if scope.placing_date < date(2025, 8, 2):
            click.echo(f"   ⚠️  Pre-existing model (placed {scope.placing_date})")
            click.echo(f"   Public Summary: {scope.compliance_deadlines['public_summary_due']} (2-year grace)")
            click.echo(f"   Copyright Policy: {scope.compliance_deadlines['copyright_policy_due']} (no grace)")
            click.echo(f"   Other Obligations: {scope.compliance_deadlines['other_obligations_due']} (no grace)")
        else:
            click.echo(f"   All obligations due: {scope.placing_date}")
        
        click.echo(f"   Fines enforceable from: {scope.compliance_deadlines['fines_enforceable_from']}")
        click.echo(f"   Next update due: {scope.compliance_deadlines.get('next_update_due', 'N/A')}")
        
        # Domain disclosure rule
        if scope.is_provider:
            click.echo(f"\n🌐 Domain Disclosure")
            click.echo(f"   Rule: {scope.top_domain_rule}")
            click.echo(f"   Method: Volume calculated by bytes/tokens")
        
        # EU Representative
        if scope.needs_eu_representative:
            click.echo(f"\n⚠️  EU Authorized Representative Required")
            click.echo(f"   (Non-EU provider - no open-source carve-out)")
        
        # Systemic risk
        if scope.is_systemic_risk:
            click.echo(f"\n⚠️  Systemic Risk Model (>10^25 FLOP)")
            click.echo(f"   Additional obligations apply (Art. 55)")
        
        # Notification deadline if applicable
        if scope.needs_threshold_notification:
            click.echo(f"\n📮 Commission Notification Required")
            if scope.notification_deadline:
                click.echo(f"   Deadline: {scope.notification_deadline}")
            elif scope.notification_deadline_label:
                click.echo(f"   Deadline: {scope.notification_deadline_label}")
            else:
                click.echo(f"   Deadline: Within 14 days of knowing threshold exceeded")
        
        # Indicative signals (if any)
        if hasattr(scope, 'indicative_signals') and scope.indicative_signals.get('indicative_gpai_signal'):
            click.echo(f"\nℹ️  Indicative GPAI Signals")
            for reason in scope.indicative_signals.get('reasons', []):
                click.echo(f"   • {reason}")
        
        # Carve-out blockers (if open-source but no carve-outs)
        if (hasattr(scope, 'carveout_blockers') and scope.carveout_blockers and 
            scope.is_open_source_release and not scope.carve_outs):
            click.echo(f"\n⚠️  Open-source carve-outs were not applied because:")
            for blocker in scope.carveout_blockers:
                click.echo(f"   • {blocker}")
        
        # Validation warnings (if any)
        if hasattr(scope, 'validation_warnings') and scope.validation_warnings:
            click.echo(f"\n⚠️  Validation Warnings")
            for warning in scope.validation_warnings:
                click.echo(f"   • {warning}")
        
        # Save output if requested
        if output:
            result = {
                'scope_classification': {
                    'is_gpai_provider': scope.is_gpai_provider,
                    'is_significant_modifier': scope.is_significant_modifier,
                    'is_provider': scope.is_provider,
                    'is_sme': scope.is_sme,
                    'is_open_source': scope.is_open_source_release,
                    'is_systemic_risk': scope.is_systemic_risk,
                    'needs_eu_representative': scope.needs_eu_representative,
                    'provider_type': scope.provider_type,
                    'top_domain_rule': scope.top_domain_rule
                },
                'compliance_deadlines': {
                    'placing_date': scope.placing_date.isoformat(),
                    'public_summary_due': scope.compliance_deadlines.get('public_summary_due').isoformat() 
                        if scope.compliance_deadlines.get('public_summary_due') else None,
                    'copyright_policy_due': scope.compliance_deadlines.get('copyright_policy_due').isoformat()
                        if scope.compliance_deadlines.get('copyright_policy_due') else None,
                    'fines_enforceable_from': scope.compliance_deadlines['fines_enforceable_from'].isoformat(),
                    'next_update_due': scope.compliance_deadlines.get('next_update_due').isoformat()
                        if scope.compliance_deadlines.get('next_update_due') else None
                },
                'applicable_obligations': scope.applicable_obligations,
                'carve_outs': scope.carve_outs,
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'generator': 'Lace EU AI Act Scope Advisor',
                    'disclaimer': 'This is guidance, not legal advice'
                }
            }
            
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
            click.echo(f"\n💾 Scope analysis saved to: {output}")
        
        click.echo("\n" + "="*60)
        if scope.is_provider:
            click.echo("Run 'lace generate-docs' to create compliance documents")
        else:
            click.echo("You may create voluntary transparency documents with 'lace generate-docs'")
        click.echo("="*60 + "\n")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)


@main.command('analyze')
@click.argument('dataset_path', type=click.Path(exists=True))
@click.option('--output', '-o', default='analysis.json', help='Output analysis file')
@click.option('--sample-rate', default=0.01, help='Sampling rate for large datasets')
@click.option('--debug', is_flag=True, envvar='LACE_DEBUG', help='Enable debug output')
def analyze_cmd(dataset_path, output, sample_rate, debug):
    """Analyze dataset and export sanitized analysis (no raw text)."""
    from lace.wizard import DatasetAnalyzer
    from lace.wizard.serializer import to_analysis_json
    from pathlib import Path
    import json
    import os
    
    if debug:
        os.environ['LACE_DEBUG'] = '1'
        logging.basicConfig(level=logging.DEBUG)
    
    click.echo(f"🔍 Analyzing dataset: {dataset_path}")
    click.echo("   Note: No raw text will be included in the output")
    
    try:
        analyzer = DatasetAnalyzer()
        results = analyzer.analyze_dataset(dataset_path, sample_rate=sample_rate)
        
        # USE UNIFIED SERIALIZER
        sanitized = to_analysis_json(results)
        
        # Fallback if analyzer returned zeros (failsafe using os.stat)
        if (sanitized['size_metrics']['total_files'] == 0 and
            sanitized['size_metrics']['total_bytes'] == 0):
            import os
            files = 0
            bytes_total = 0
            for root, _, names in os.walk(dataset_path):
                for n in names:
                    p = os.path.join(root, n)
                    try:
                        st = os.stat(p)
                        files += 1
                        bytes_total += st.st_size
                    except OSError:
                        pass
            sanitized['size_metrics']['total_files'] = files
            sanitized['size_metrics']['total_bytes'] = bytes_total
            sanitized['size_metrics']['avg_file_size'] = (bytes_total / files) if files else 0.0
            sanitized['summary']['files_processed'] = files
            sanitized['summary']['bytes_total'] = bytes_total
            if debug:
                click.echo(f"   - Fallback: counted {files} files, {bytes_total} bytes via os.stat")
        
        # Write output
        Path(output).write_text(json.dumps(sanitized, indent=2))
        
        # Show summary from SANITIZED object
        click.echo(f"✅ Analysis saved to {output} (no raw text)")
        click.echo(f"   - Files processed: {sanitized['size_metrics']['total_files']}")
        click.echo(f"   - Bytes total: {sanitized['size_metrics']['total_bytes']}")
        click.echo(f"   - Domains found: {sanitized['domain_analysis']['total_domains']}")
        
        # Show serializer notes if debug enabled
        if debug and sanitized.get('metadata', {}).get('serializer_notes'):
            notes = sanitized['metadata']['serializer_notes']
            click.echo(f"   - Serializer notes: {', '.join(notes)}")
    
    except Exception as e:
        click.echo(f"❌ Error analyzing dataset: {e}", err=True)
        raise click.ClickException(str(e))


@main.command('compliance-pack')
@click.argument('dataset_path', type=click.Path(exists=True))
@click.option('--allow-external-ai', is_flag=True, help='Allow sending redacted samples to external AI')
@click.option('--allow-remote-llm', is_flag=True, help='Allow remote LLM for unsure resolution')
@click.option('--answers', type=click.Path(exists=True), help='Load all answers from file')
@click.option('--output', type=click.Path(), help='Output directory for documents')
@click.option('--no-store', is_flag=True, help='Skip S3 storage')
def compliance_pack_cmd(dataset_path, allow_external_ai, allow_remote_llm, answers, output, no_store):
    """Generate complete EU AI Act compliance pack (scope + documents)."""
    try:
        click.echo("\n" + "="*60)
        click.echo("🚀 LACE EU AI Act Compliance Pack Generator")
        click.echo("="*60 + "\n")
        
        click.echo("📅 Important Dates:")
        click.echo("   GPAI obligations apply: 2025-08-02")
        click.echo("   Enforcement begins: 2026-08-02")
        click.echo("   Pre-existing models grace period: until 2027-08-02\n")
        
        # Step 1: Analyze dataset
        click.echo("🔍 Step 1: Analyzing dataset...")
        analyzer = DatasetAnalyzer(allow_external_ai=allow_external_ai)
        analysis_results = analyzer.analyze_dataset(dataset_path)
        
        click.echo(f"   ✓ Files: {analysis_results.get('volume', {}).get('files', 0)}")
        click.echo(f"   ✓ Size: {analysis_results.get('volume', {}).get('bytes', 0) / (1024*1024):.1f} MB")
        click.echo(f"   ✓ Estimated tokens: {analysis_results.get('volume', {}).get('estimated_tokens', 0):,}")
        
        # Step 2: Run wizard
        click.echo("\n📋 Step 2: Collecting compliance information...")
        if answers:
            click.echo(f"   Loading from {answers}...")
            wizard = DocumentWizard(analysis_results)
            wizard_data = wizard.run_with_answers(answers)
        else:
            wizard = DocumentWizard(analysis_results)
            wizard_data = wizard.run_interactive()
        
        # Step 3: Classify scope
        click.echo("\n⚖️ Step 3: Determining legal obligations...")
        
        # Set LLM environment if enabled
        if allow_remote_llm:
            os.environ['LACE_ALLOW_REMOTE_LLM'] = 'true'
        
        # Extract scope data from wizard answers
        scope_data = {
            'placing_date': wizard_data.get('placing_date') or wizard_data.get('model_identification', {}).get('release_date'),
            'general_purpose': wizard_data.get('general_purpose', True),
            'open_source_release': wizard_data.get('open_source_release', False),
            'training_compute_flops': wizard_data.get('training_compute_flops', 'unknown'),
            'outside_eu_provider': wizard_data.get('outside_eu_provider', False),
            'provider_status': wizard_data.get('provider_status', 'built_model'),
            'sme_status': wizard_data.get('sme_status', 'unsure'),
            'integrated_into_own_system': wizard_data.get('integrated_into_own_system'),
            'internal_only_use': wizard_data.get('internal_only_use'),
            'essential_to_service': wizard_data.get('essential_to_service'),
            'affects_individuals_rights': wizard_data.get('affects_individuals_rights')
        }
        
        classifier = ScopeClassifier()
        scope = classifier.classify(scope_data)
        
        # Show scope results
        if scope.placed_on_market:
            click.echo(f"   ✓ Making available in EU (Article 3)")
        else:
            click.echo(f"   ✗ Not making available in EU")
        
        if scope.is_gpai_provider:
            click.echo(f"   ✓ GPAI Provider - Article 53 obligations apply")
            if scope.is_systemic_risk:
                click.echo(f"   ⚠️ Systemic risk model (≥10²⁵ FLOPs)")
            if scope.is_open_source_release:
                click.echo(f"   📖 Open-source release")
                if scope.carve_outs:
                    click.echo(f"   🛡️ Carve-outs: {len(scope.carve_outs)} exemptions")
        else:
            click.echo(f"   📄 Not a GPAI provider - voluntary documents only")
        
        # Step 4: Generate documents
        click.echo("\n📝 Step 4: Generating compliance documents...")
        
        # Add scope to wizard data
        wizard_data['_metadata'] = wizard_data.get('_metadata', {})
        wizard_data['_metadata']['is_gpai'] = scope.is_gpai_provider
        wizard_data['_metadata']['is_systemic_risk'] = scope.is_systemic_risk
        wizard_data['_metadata']['is_open_source'] = scope.is_open_source_release
        wizard_data['_metadata']['applicable_obligations'] = scope.applicable_obligations
        wizard_data['_metadata']['carve_outs'] = scope.carve_outs
        
        generator = TemplateGenerator()
        documents = {}
        
        # Generate based on obligations
        if scope.is_gpai_provider:
            # Always required for GPAI
            click.echo("   • EU Public Summary (Art. 53(1)(d))")
            eu_summary = generator.generate(wizard_data, is_gpai=True)
            documents['eu_summary'] = eu_summary['document']
            
            click.echo("   • Copyright Policy (Art. 53(1)(c))")
            documents['copyright_policy'] = generator.generate_copyright_policy(wizard_data)
            
            # Conditional based on carve-outs
            if "Technical documentation (Art. 53(1)(a) - exempt)" not in scope.carve_outs:
                click.echo("   • Technical Documentation (Art. 53(1)(a))")
            if "Downstream information (Art. 53(1)(b) - exempt)" not in scope.carve_outs:
                click.echo("   • Downstream Information (Art. 53(1)(b))")
        else:
            click.echo("   • Voluntary EU-style summary")
            eu_summary = generator.generate(wizard_data, is_gpai=False)
            documents['eu_summary'] = eu_summary['document']
            documents['copyright_policy'] = generator.generate_copyright_policy(wizard_data)
        
        # Always generate model card
        documents['model_card'] = generator.generate_model_card(wizard_data)
        
        # Step 5: Save documents
        output_path = Path(output) if output else Path('.') / 'lace_compliance_pack'
        output_path.mkdir(parents=True, exist_ok=True)
        
        click.echo(f"\n💾 Step 5: Saving compliance pack to {output_path}...")
        
        # Save documents
        with open(output_path / 'eu_training_summary.json', 'w') as f:
            json.dump(documents['eu_summary'], f, indent=2)
        
        with open(output_path / 'copyright_policy.md', 'w') as f:
            f.write(documents['copyright_policy'])
        
        with open(output_path / 'model_card.md', 'w') as f:
            f.write(documents['model_card'])
        
        # Save scope analysis
        scope_output = {
            'schema_version': '1.0.0',
            'classification': {
                'is_gpai_provider': scope.is_gpai_provider,
                'is_systemic_risk': scope.is_systemic_risk,
                'is_open_source': scope.is_open_source_release,
                'placed_on_market': scope.placed_on_market,
                'placement_reason': scope.placement_reason,
                'needs_eu_representative': scope.needs_eu_representative
            },
            'obligations': scope.applicable_obligations,
            'carve_outs': scope.carve_outs,
            'deadlines': scope.compliance_deadlines,
            'dates': {
                'gpai_applicability': scope.gpai_applicability_date,
                'enforcement': scope.enforcement_date,
                'grace_period_end': scope.grace_period_end
            }
        }
        
        with open(output_path / 'scope_analysis.json', 'w') as f:
            json.dump(scope_output, f, indent=2, default=str)
        
        # Validation status
        if eu_summary.get('validation', {}).get('valid'):
            click.echo("   ✓ Document validation: PASSED")
        else:
            click.echo("   ⚠️ Document validation: See scope_analysis.json for details")
        
        # Summary
        click.echo("\n" + "="*60)
        click.echo("✨ Compliance Pack Generated Successfully!")
        click.echo("="*60)
        click.echo(f"\n📁 Output directory: {output_path}")
        click.echo("   • eu_training_summary.json - Official EU template")
        click.echo("   • copyright_policy.md - Article 53(1)(c) policy")
        click.echo("   • model_card.md - HuggingFace-compatible card")
        click.echo("   • scope_analysis.json - Legal obligations analysis")
        
        if scope.is_gpai_provider:
            click.echo(f"\n⚠️ Next steps:")
            click.echo("   1. Review generated documents for accuracy")
            click.echo("   2. Complete any [PLACEHOLDER] sections")
            if scope.needs_eu_representative:
                click.echo("   3. Appoint EU authorized representative")
            click.echo(f"   {3 if not scope.needs_eu_representative else 4}. Store documents immutably")
            click.echo(f"   {4 if not scope.needs_eu_representative else 5}. Update on material changes")
        else:
            click.echo("\n📌 These are voluntary transparency documents.")
            click.echo("   No legal obligations apply, but transparency is good practice!")
        
        click.echo(f"\n⚖️ Disclaimer: {scope.advisory_disclaimer}\n")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()