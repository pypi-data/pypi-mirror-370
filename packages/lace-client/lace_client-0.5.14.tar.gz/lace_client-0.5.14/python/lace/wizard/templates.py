"""
Template generator for EU-compliant documents with schema validation.
Generates official EU templates for GPAI providers and voluntary templates for fine-tuners.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    import jsonschema
    from jsonschema import Draft7Validator
except ImportError:
    jsonschema = None
    Draft7Validator = None
    logging.warning("jsonschema not installed - schema validation disabled")

logger = logging.getLogger(__name__)


class TemplateGenerator:
    """Generate EU-compliant templates with schema validation."""
    
    def __init__(self):
        """Initialize template generator."""
        self.schema = self._load_eu_schema()
        self.validator = None
        
        if jsonschema and self.schema:
            self.validator = Draft7Validator(self.schema)
    
    def _load_eu_schema(self) -> Optional[Dict]:
        """Load the official EU template schema."""
        schema_path = Path(__file__).parent / "schemas" / "eu_training_summary_2025_07.json"
        
        if not schema_path.exists():
            logger.warning(f"EU schema not found: {schema_path}")
            return None
        
        try:
            with open(schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load EU schema: {e}")
            return None
    
    def generate(self, wizard_data: Dict, is_gpai: bool) -> Dict[str, Any]:
        """
        Generate appropriate template based on provider status.
        Routes to full, modification-only, or voluntary template.
        
        Args:
            wizard_data: Data from DocumentWizard
            is_gpai: Whether provider is GPAI
            
        Returns:
            Generated document with metadata
        """
        # Check provider type and modification status
        is_significant_modifier = wizard_data.get('_metadata', {}).get('is_significant_modifier', False)
        provider_type = wizard_data.get('_metadata', {}).get('provider_type')
        is_provider = is_gpai or is_significant_modifier
        
        # Route to appropriate template
        if is_significant_modifier:
            # Generate modification-only template
            template = self._render_eu_official_modified(wizard_data)
            label = "Official EU Public Summary - Modified Model (Article 53)"
            
            # Validate against schema
            validation = self._validate_against_schema(template)
            
            if not validation['valid']:
                logger.error(f"Modified template validation failed: {validation['errors']}")
        elif is_gpai:
            # Generate full official EU template
            template = self._render_eu_official(wizard_data)
            label = "Official EU Public Summary of Training Content (Article 53)"
            
            # Validate against schema
            validation = self._validate_against_schema(template)
            
            if not validation['valid']:
                logger.error(f"Template validation failed: {validation['errors']}")
        else:
            # Generate voluntary template with watermark
            template = self._render_eu_voluntary(wizard_data)
            label = "Voluntary EU-style Training Summary (Non-GPAI)"
            
            # Block validation for voluntary template
            validation = {
                'valid': True,
                'template_type': 'voluntary',
                'note': 'Validation not required for voluntary template',
                'watermark': 'This is a voluntary transparency document'
            }
        
        return {
            'document': template,
            'label': label,
            'validation': validation,
            'disclaimer': 'This is guidance, not legal advice',
            'provenance': wizard_data.get('_provenance', {}),
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator_version': '1.0.0',
                'schema_version': '2025-07',
                'schema_note': 'Derived from Commission template',
                'is_provider': is_provider,
                'is_gpai': is_gpai,
                'provider_type': wizard_data.get('metadata', {}).get('provider_type')
            }
        }
    
    def _render_eu_official(self, data: Dict) -> Dict:
        """
        Render official EU template for GPAI providers.
        
        This follows the structure required by Article 53(1)(d) of the AI Act.
        """
        template = {
            'model_identification': self._render_model_identification(data),
            'training_data_overview': self._render_training_data_overview(data),
            'data_sources': self._render_data_sources(data),
            'data_governance': self._render_data_governance(data)
        }
        
        # Remove empty sections
        template = self._clean_empty_values(template)
        
        return template
    
    def _render_eu_voluntary(self, data: Dict) -> Dict:
        """
        Render voluntary EU-style template for non-GPAI fine-tuners.
        
        Similar structure but clearly marked as voluntary.
        """
        template = {
            '_disclaimer': 'This is a voluntary EU-style summary for transparency. The provider is not a GPAI provider under the AI Act.',
            'model_identification': self._render_model_identification(data),
            'training_data_overview': self._render_training_data_overview(data),
            'data_sources': self._render_data_sources(data),
            'data_governance': self._render_data_governance(data)
        }
        
        # Remove empty sections
        template = self._clean_empty_values(template)
        
        return template
    
    def _render_eu_official_modified(self, data: Dict) -> Dict:
        """
        Official EU template for MODIFIED models only.
        Includes ONLY additional training content used for modification.
        Must reference the base model and its public summary.
        
        Per Template FAQ: Modified/fine-tuned model summaries should only
        include the modification's training content.
        """
        template = {
            'model_identification': {
                'provider_name': data.get('model_identification', {}).get('provider_name'),
                'model_name': data.get('model_identification', {}).get('model_name'),
                'model_version': data.get('model_identification', {}).get('model_version'),
                'release_date': data.get('model_identification', {}).get('release_date'),
                'contact_email': data.get('model_identification', {}).get('contact_email'),
                'modified_from': {
                    'base_model_name': data.get('base_model_name'),
                    'base_model_provider': data.get('base_model_provider'),
                    'base_model_summary_url': data.get('base_model_url'),
                    'modification_description': data.get('modification_description', 'Fine-tuned version')
                }
            },
            'modification_training_data': {
                '_note': 'This summary covers ONLY the additional training data used for modification',
                'modalities': data.get('modification_modalities', data.get('training_data_overview', {}).get('modalities', [])),
                'size_ranges': data.get('modification_size_ranges', {}),
                'source_types': data.get('modification_source_types', data.get('data_sources', {}).get('source_types', [])),
                'knowledge_cutoff': data.get('modification_knowledge_cutoff')
            }
        }
        
        # Add web scraped data if applicable to modification
        mod_sources = data.get('modification_source_types', data.get('data_sources', {}).get('source_types', []))
        if 'web_scraped' in mod_sources:
            web_data = data.get('modification_web_data', data.get('data_sources', {}).get('web_scraped_data', {}))
            # Ensure top domains and measurement method are included
            web_scraped_section = {
                'top_domains': data.get('modification_web_top_domains', web_data.get('top_domains', [])),
                'volume_measure_method': data.get('modification_web_volume_method', 'bytes'),
                'domain_coverage': web_data.get('domain_coverage', {}),
                'collection_period': web_data.get('collection_period', {})
            }
            template['modification_training_data']['web_scraped_data'] = web_scraped_section
        
        # Add data governance for modification
        template['data_governance'] = {
            '_scope': 'Applies to modification training data only',
            'personal_data_use': data.get('modification_personal_data', data.get('data_governance', {}).get('personal_data_use')),
            'copyright_compliance': data.get('modification_copyright', data.get('data_governance', {}).get('copyright_compliance')),
            'sensitive_data': data.get('modification_sensitive', data.get('data_governance', {}).get('sensitive_data'))
        }
        
        # Remove empty sections
        template = self._clean_empty_values(template)
        
        return template
    
    def _render_model_identification(self, data: Dict) -> Dict:
        """Render model identification section."""
        return {
            'provider_name': data.get('model_identification', {}).get('provider_name'),
            'model_name': data.get('model_identification', {}).get('model_name'),
            'model_version': data.get('model_identification', {}).get('model_version'),
            'release_date': data.get('model_identification', {}).get('release_date'),
            'contact_email': data.get('model_identification', {}).get('contact_email')
        }
    
    def _render_training_data_overview(self, data: Dict) -> Dict:
        """Render training data overview section."""
        overview = data.get('training_data_overview', {})
        
        # Build size ranges from individual fields
        size_ranges = {}
        for modality in ['text_tokens', 'images', 'audio_hours', 'video_hours', 'code_files']:
            key = f'size_ranges.{modality}'
            if key in overview:
                size_ranges[modality] = overview[key]
        
        return {
            'modalities': overview.get('modalities', []),
            'size_ranges': size_ranges if size_ranges else overview.get('size_ranges', {}),
            'knowledge_cutoff': overview.get('knowledge_cutoff')
        }
    
    def _render_data_sources(self, data: Dict) -> Dict:
        """Render data sources section with proper structure."""
        sources = data.get('data_sources', {})
        
        rendered = {
            'source_types': sources.get('source_types', [])
        }
        
        # Add conditional sections based on source types
        source_types = sources.get('source_types', [])
        
        if 'public_datasets' in source_types:
            datasets = sources.get('public_datasets', [])
            if datasets:
                rendered['public_datasets'] = datasets
        
        if 'licensed_private' in source_types:
            licensed = sources.get('licensed_private_datasets', {})
            if licensed:
                rendered['licensed_private_datasets'] = licensed
        
        if 'web_scraped' in source_types:
            # CRITICAL: Include all mandatory web scraping fields for GPAI
            web_data = sources.get('web_scraped_data', {})
            
            # Build top domains structure
            top_domains = web_data.get('top_domains', {})
            if not top_domains:
                # Try to build from individual fields
                top_domains = {
                    'domains_list': sources.get('web_scraped_data.top_domains.domains_list', []),
                    'measurement_method': sources.get('web_scraped_data.top_domains.measurement_method'),
                    'coverage_percentage': sources.get('web_scraped_data.top_domains.coverage_percentage')
                }
            
            # Build crawler details
            crawler_details = web_data.get('crawler_details', {})
            if not crawler_details:
                crawler_details = {
                    'crawler_names': sources.get('web_scraped_data.crawler_details.crawler_names', []),
                    'purpose': sources.get('web_scraped_data.crawler_details.purpose'),
                    'behavior': sources.get('web_scraped_data.crawler_details.behavior')
                }
            
            # Build collection period
            collection_period = web_data.get('collection_period', {})
            if not collection_period:
                collection_period = {
                    'start_date': sources.get('web_scraped_data.collection_period.start_date'),
                    'end_date': sources.get('web_scraped_data.collection_period.end_date')
                }
            
            rendered['web_scraped_data'] = {
                'top_domains': top_domains,
                'crawler_details': crawler_details,
                'collection_period': collection_period
            }
        
        if 'user_generated' in source_types:
            user_data = sources.get('user_generated_data', {})
            if user_data:
                rendered['user_generated_data'] = user_data
        
        if 'synthetic' in source_types:
            synthetic = sources.get('synthetic_data', {})
            if synthetic:
                rendered['synthetic_data'] = synthetic
        
        return rendered
    
    def _render_data_governance(self, data: Dict) -> Dict:
        """Render data governance section."""
        governance = data.get('data_governance', {})
        
        # Build opt-out compliance structure
        opt_out = governance.get('opt_out_compliance', {})
        if not opt_out:
            # Try to build from individual fields
            opt_out = {
                'respects_signals': governance.get('opt_out_compliance.respects_signals'),
                'signals_checked': governance.get('opt_out_compliance.signals_checked', []),
                'implementation_date': governance.get('opt_out_compliance.implementation_date')
            }
        
        # Build illegal content handling
        illegal_content = governance.get('illegal_content_handling', {})
        if not illegal_content:
            illegal_content = {
                'removal_method': governance.get('illegal_content_handling.removal_method'),
                'detection_approach': governance.get('illegal_content_handling.detection_approach')
            }
        
        return {
            'lawful_basis': governance.get('lawful_basis', []),
            'opt_out_compliance': opt_out,
            'illegal_content_handling': illegal_content,
            'pii_handling': governance.get('pii_handling', {})
        }
    
    def _clean_empty_values(self, obj: Any) -> Any:
        """Recursively remove None and empty values from dictionary."""
        if isinstance(obj, dict):
            cleaned = {}
            for k, v in obj.items():
                cleaned_v = self._clean_empty_values(v)
                if cleaned_v is not None and cleaned_v != {} and cleaned_v != []:
                    cleaned[k] = cleaned_v
            return cleaned
        elif isinstance(obj, list):
            return [self._clean_empty_values(item) for item in obj if item is not None]
        else:
            return obj
    
    def _validate_against_schema(self, template: Dict) -> Dict[str, Any]:
        """Validate template against EU schema."""
        if not self.validator:
            return {
                'valid': False,
                'errors': ['Schema validator not available'],
                'schema_version': 'unknown'
            }
        
        errors = []
        
        try:
            # Validate against schema
            for error in self.validator.iter_errors(template):
                error_path = '.'.join(str(p) for p in error.path)
                errors.append({
                    'path': error_path if error_path else 'root',
                    'message': error.message
                })
        except Exception as e:
            logger.error(f"Validation error: {e}")
            errors.append({
                'path': 'unknown',
                'message': str(e)
            })
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'schema_version': self.schema.get('version', 'unknown') if self.schema else 'unknown'
        }
    
    def generate_model_card(self, data: Dict) -> str:
        """
        Generate HuggingFace-compatible model card.
        
        Args:
            data: Wizard data with model information
            
        Returns:
            Markdown model card content
        """
        # Extract metadata
        provider = data.get('model_identification', {}).get('provider_name', 'Unknown')
        model_name = data.get('model_identification', {}).get('model_name', 'Model')
        version = data.get('model_identification', {}).get('model_version', '1.0')
        release_date = data.get('model_identification', {}).get('release_date', '')
        contact = data.get('model_identification', {}).get('contact_email', '')
        
        modalities = data.get('training_data_overview', {}).get('modalities', [])
        knowledge_cutoff = data.get('training_data_overview', {}).get('knowledge_cutoff', '')
        
        intended_uses = data.get('model_card', {}).get('intended_use', {}).get('primary_uses', 'Not specified')
        out_of_scope = data.get('model_card', {}).get('intended_use', {}).get('out_of_scope', 'Not specified')
        metrics = data.get('model_card', {}).get('evaluation', {}).get('metrics', 'Not specified')
        
        # Determine license
        lawful_basis = data.get('data_governance', {}).get('lawful_basis', [])
        license_type = 'other'
        if 'licenses_held' in lawful_basis:
            license_type = 'licensed'
        elif 'proprietary' in lawful_basis:
            license_type = 'proprietary'
        
        # Build model card
        card = f"""---
license: {license_type}
language: en
base_model: custom
tags:
  - generated-with-lace
  - eu-ai-act-compliant
library_name: transformers
---

# {model_name}

## Model Details

### Description
**Organization**: {provider}  
**Version**: {version}  
**Release Date**: {release_date}  
**Contact**: {contact}  

### Model Type
This model supports the following modalities: {', '.join(modalities)}

### Training Data
See the [EU Public Summary of Training Content](./eu_training_summary.json) for detailed information about the training data used.

**Knowledge Cutoff**: {knowledge_cutoff}

## Intended Use

### Primary Use Cases
{intended_uses}

### Out-of-Scope Use
{out_of_scope}

## Training Details

### Data Sources
The model was trained on data from various sources. Please refer to the EU Public Summary for complete details.

### Data Governance
The model training complied with applicable copyright and data protection requirements. See the EU Public Summary for details on:
- Lawful basis for data use
- Opt-out signal compliance
- Illegal content handling
- PII mitigation

## Evaluation

### Metrics
{metrics}

## Ethical Considerations

This model was developed with consideration for:
- Copyright compliance
- Data protection
- Opt-out preferences
- Content moderation

## Compliance

✅ This model complies with EU AI Act requirements for GPAI providers.  
📄 Training data summary published according to Article 53(1)(d).  
🔒 Documentation stored with immutable Object Lock for transparency.

## Citation

If you use this model, please cite:
```
@misc{{{model_name.lower().replace(' ', '_')},
  title={{{model_name}}},
  author={{{provider}}},
  year={{2025}},
  publisher={{Lace}},
  version={{{version}}}
}}
```

## License

Please review the EU Public Summary of Training Content for information about the lawful basis for data use and any applicable licenses.
"""
        
        return card
    
    def generate_copyright_policy(self, data: Dict) -> str:
        """
        Generate copyright policy document per Article 53(1)(c) of the EU AI Act.
        
        Args:
            data: Wizard data with copyright information
            
        Returns:
            Markdown copyright policy content
        """
        provider = data.get('model_identification', {}).get('provider_name', 'Provider')
        contact = data.get('model_identification', {}).get('contact_email', '')
        
        lawful_basis = data.get('data_governance', {}).get('lawful_basis', [])
        opt_out = data.get('data_governance', {}).get('opt_out_compliance', {})
        respects_signals = opt_out.get('respects_signals', False)
        signals = opt_out.get('signals_checked', [])
        since_date = opt_out.get('implementation_date', '')
        
        # Build lawful basis section
        basis_text = []
        if 'licenses_held' in lawful_basis:
            basis_text.append("- Licensed content with appropriate rights obtained")
        if 'DSM_Art4_TDM' in lawful_basis:
            basis_text.append("- Directive (EU) 2019/790 Article 4(3) - Text and Data Mining with opt-out respect")
        if 'proprietary' in lawful_basis:
            basis_text.append("- Proprietary content owned by the provider")
        if 'public_domain' in lawful_basis:
            basis_text.append("- Public domain content")
        if 'user_tos' in lawful_basis:
            basis_text.append("- User-contributed content under Terms of Service")
        
        basis_section = '\n'.join(basis_text) if basis_text else "Not specified"
        
        # Build opt-out section
        signal_text = []
        if 'robots.txt' in signals:
            signal_text.append("- **robots.txt**: Traditional web crawler exclusion protocol")
        if 'ai.txt' in signals:
            signal_text.append("- **ai.txt**: AI-specific exclusion file at `/.well-known/ai.txt`")
        if 'trust.txt_datatrainingallowed' in signals:
            signal_text.append("- **trust.txt**: Publisher preferences at `/.well-known/trust.txt` with `datatrainingallowed` field")
        
        signals_section = '\n'.join(signal_text) if signal_text else "No signals currently checked"
        
        policy = f"""# Copyright Policy

## Provider Information

**Organization**: {provider}  
**Contact**: {contact}  
**Policy Version**: 1.0  
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}  

## Commitment to Copyright Compliance

{provider} is committed to respecting copyright and intellectual property rights in the development and training of AI models. This policy outlines our approach to copyright compliance in accordance with:

- EU AI Act requirements for GPAI providers
- EU DSM Directive
- GPAI Code of Practice
- Industry best practices

## Lawful Basis for Data Use

Our AI model training relies on the following lawful bases for using copyrighted content:

{basis_section}

## Opt-Out Signal Compliance

### Current Status
**Respects opt-out signals**: {'Yes' if respects_signals else 'No'}  
{f'**Implementation date**: {since_date}' if since_date else ''}

### Signals We Check

{signals_section if respects_signals else 'Opt-out signals are not currently implemented.'}

### How to Opt Out

If you are a rights holder and wish to opt out of having your content used for AI training:

1. **For website content**: Implement one or more of the following:
   - Add disallow rules to your `robots.txt` file
   - Create an `ai.txt` file at `/.well-known/ai.txt` with exclusion rules
   - Add a `trust.txt` file at `/.well-known/trust.txt` with `datatrainingallowed=no`

2. **For other content**: Contact us at {contact} with:
   - Proof of rights ownership
   - Specific content or domains to exclude
   - Preferred exclusion method

## Complaint Handling Process

### How to File a Complaint

Rights holders who believe their content has been used improperly may file a complaint by:

1. **Email**: Send details to {contact}
2. **Required Information**:
   - Your name and contact information
   - Description of the copyrighted work
   - URL or identifier of the content
   - Statement of good faith belief
   - Statement of accuracy under penalty of perjury
   - Physical or electronic signature

### Response Timeline

- **Acknowledgment**: Within 3 business days
- **Initial Review**: Within 10 business days
- **Resolution Target**: Within 30 days

### Our Commitment

Upon receiving a valid complaint, we will:
1. Investigate the claim thoroughly
2. Remove identified content from future training if verified
3. Update our opt-out records
4. Provide written response with actions taken

## Transparency Measures

We maintain transparency through:
- Public Summary of Training Content (EU AI Act Article 53)
- This copyright policy
- Regular updates on opt-out implementation
- Annual compliance reports

## Technical Implementation

### Web Crawling
When collecting web data, our crawlers:
- Respect robots.txt directives
- Check for AI-specific exclusion signals
- Maintain crawl-delay requirements
- Identify themselves properly in user-agent strings

### Data Processing
Before training:
- Filter content based on opt-out signals
- Remove identified copyrighted content
- Apply technical measures to prevent unauthorized use
- Document compliance measures

## Updates to This Policy

This policy may be updated to reflect:
- Changes in legal requirements
- New opt-out standards
- Improved compliance measures
- Stakeholder feedback

Updates will be posted at least 30 days before taking effect.

## Contact Information

For questions about this copyright policy or to exercise your rights:

**Email**: {contact}  
**Subject Line**: "Copyright Policy Inquiry"  

---

*This policy demonstrates our commitment to copyright compliance and responsible AI development in accordance with EU regulations and industry best practices.*
"""
        
        return policy
    
    def generate_html_output(self, document: Dict, title: str = "EU Training Summary") -> str:
        """
        Generate HTML version of the document.
        
        Args:
            document: The document dictionary
            title: Document title
            
        Returns:
            HTML string
        """
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 1px solid #ecf0f1;
            padding-bottom: 5px;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 20px;
        }}
        .metadata {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .field {{
            margin: 10px 0;
        }}
        .field-label {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .field-value {{
            margin-left: 20px;
        }}
        .list-value {{
            margin-left: 40px;
        }}
        .validation-success {{
            color: #27ae60;
            font-weight: bold;
        }}
        .validation-error {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        code {{
            background: #f8f9fa;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        {self._dict_to_html(document)}
        <div class="footer">
            <p>Generated with Lace - EU AI Act Compliance Platform</p>
            <p>Document generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _dict_to_html(self, obj: Any, level: int = 0) -> str:
        """Convert dictionary to HTML representation."""
        if isinstance(obj, dict):
            html_parts = []
            
            for key, value in obj.items():
                if key.startswith('_'):
                    continue  # Skip private fields
                
                # Format key
                display_key = key.replace('_', ' ').title()
                
                if isinstance(value, dict):
                    html_parts.append(f'<h{min(3, 2+level)}>{display_key}</h{min(3, 2+level)}>')
                    html_parts.append(self._dict_to_html(value, level + 1))
                elif isinstance(value, list):
                    html_parts.append(f'<div class="field">')
                    html_parts.append(f'<span class="field-label">{display_key}:</span>')
                    html_parts.append('<ul>')
                    for item in value:
                        html_parts.append(f'<li>{self._dict_to_html(item, level + 1)}</li>')
                    html_parts.append('</ul>')
                    html_parts.append('</div>')
                else:
                    html_parts.append(f'<div class="field">')
                    html_parts.append(f'<span class="field-label">{display_key}:</span> ')
                    html_parts.append(f'<span class="field-value">{value}</span>')
                    html_parts.append('</div>')
            
            return '\n'.join(html_parts)
        
        elif isinstance(obj, list):
            items = [str(item) for item in obj]
            return ', '.join(items)
        
        else:
            return str(obj)