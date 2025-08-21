"""
Document wizard with GPAI gating and confidence-based question selection.
CRITICAL: GPAI provider question MUST be asked first to determine template type.
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Question:
    """Represents a single wizard question."""
    id: str
    text: str
    type: str
    required: bool = False
    options: Optional[List] = None
    validate: Optional[Dict] = None
    autofill_from: Optional[str] = None
    confidence_field: Optional[str] = None
    map_to: Optional[str] = None
    required_if: Optional[str] = None
    show_if: Optional[str] = None
    help: Optional[str] = None
    required_for_gpai: bool = False


class DocumentWizard:
    """GPAI-compliant document wizard with confidence-based question selection."""
    
    def __init__(self, analysis_results: Dict[str, Any]):
        """
        Initialize wizard with analysis results.
        
        Args:
            analysis_results: Results from DatasetAnalyzer
        """
        self.analysis = analysis_results
        self.questions = []
        self.answers = {}
        self.is_gpai = None  # Will be determined by gating question
        self.bank = self._load_question_bank()
        self.confidence_threshold = self.bank.get('defaults', {}).get('confidence_threshold', 0.80)
        
    def _load_question_bank(self) -> Dict:
        """Load and validate YAML question bank."""
        yaml_path = Path(__file__).parent / "questions.yaml"
        
        if not yaml_path.exists():
            raise FileNotFoundError(f"Question bank not found: {yaml_path}")
        
        with open(yaml_path, 'r') as f:
            bank = yaml.safe_load(f)
        
        # Validate all autofill_from fields exist in analyzer
        self._validate_field_mappings(bank)
        
        return bank
    
    def _validate_field_mappings(self, bank: Dict):
        """Ensure all field IDs are canonical across components."""
        issues = []
        
        # Check all sections
        for section in ['gating', 'model_identification', 'training_data', 
                       'data_sources', 'data_governance', 'model_card']:
            if section not in bank:
                continue
            
            questions = bank[section]
            if not isinstance(questions, list):
                continue
                
            for question in questions:
                # Check autofill_from fields
                if 'autofill_from' in question:
                    field = question['autofill_from']
                    if not field.startswith('analyzer.'):
                        field = field.replace('analyzer.', '')
                    else:
                        field = field[9:]  # Remove 'analyzer.' prefix
                    
                    if field not in self.analysis:
                        logger.warning(f"Missing analyzer field: {field}")
                        issues.append(f"Missing: {field}")
                
                # Check confidence fields
                if 'confidence_field' in question:
                    conf_field = question['confidence_field']
                    if conf_field.startswith('analyzer.'):
                        conf_field = conf_field[9:]
                    
                    if conf_field not in self.analysis:
                        logger.warning(f"Missing confidence field: {conf_field}")
                        issues.append(f"Missing confidence: {conf_field}")
        
        if issues:
            logger.warning(f"Field mapping issues: {', '.join(issues)}")
    
    def run_interactive(self) -> Dict[str, Any]:
        """
        Run interactive wizard with GPAI gating first.
        
        Returns:
            Dictionary of answers mapped to template structure
        """
        print("\n" + "="*60)
        print("📋 EU AI Act Compliance Document Generator")
        print("="*60 + "\n")
        
        # CRITICAL: Ask GPAI gating question FIRST
        self.is_gpai = self._ask_gating_question()
        
        # Select questions based on GPAI status and confidence
        questions = self._select_questions_for_gpai()
        
        print(f"\n✅ Template type: {'Official EU Template (Article 53)' if self.is_gpai else 'Voluntary EU-style Summary'}")
        print(f"📝 Questions to answer: {len(questions)}")
        print("-" * 60 + "\n")
        
        # Ask each question with progress tracking
        for idx, question in enumerate(questions, 1):
            print(f"\n📌 Question {idx} of {len(questions)}")
            print("-" * 40)
            
            answer = self._ask_question(question)
            self.answers[question.id] = answer
            
            # Show provenance
            self._show_provenance(question, answer)
        
        # Map answers to template structure
        template_data = self._map_to_template()
        
        print("\n" + "="*60)
        print("✅ All questions answered!")
        print("="*60 + "\n")
        
        return template_data
    
    def _ask_gating_question(self) -> bool:
        """Ask GPAI provider question - determines template type."""
        gating = self.bank['gating'][0]
        
        print(f"🔍 {gating['text']}")
        
        if gating.get('help'):
            print(f"\n💡 {gating['help']}\n")
        
        options = gating.get('options', [])
        for idx, option in enumerate(options, 1):
            print(f"  {idx}. {option['label']}")
        
        while True:
            try:
                choice = input("\nSelect (1-3): ").strip()
                if choice.isdigit():
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(options):
                        selected = options[choice_idx]['value']
                        self.answers['provider_type'] = selected
                        
                        # Return true for GPAI, false for fine-tuner
                        return selected in ['gpai_provider', 'unsure']
                
                print("❌ Please enter a valid number (1-3)")
            except (ValueError, KeyboardInterrupt):
                print("\n⚠️  Wizard cancelled by user")
                raise
    
    def _select_questions_for_gpai(self) -> List[Question]:
        """Select questions based on GPAI status and confidence scores."""
        selected = []
        gpai_mandatory = self._get_gpai_mandatory_fields()
        always_ask = self.bank.get('selection_rules', {}).get('always_ask', [])
        
        # Process all sections
        for section in ['model_identification', 'training_data', 
                       'data_sources', 'data_governance']:
            if section not in self.bank:
                continue
            
            questions = self.bank[section]
            if not isinstance(questions, list):
                continue
            
            for q_data in questions:
                question = self._create_question(q_data)
                
                # Check if always required
                if question.id in always_ask:
                    selected.append(question)
                    continue
                
                # Check if required for GPAI
                if self.is_gpai and question.id in gpai_mandatory:
                    selected.append(question)
                    continue
                
                # Check if conditionally required
                if self._check_conditional_requirement(question):
                    selected.append(question)
                    continue
                
                # Check if generally required
                if question.required:
                    selected.append(question)
                    continue
                
                # Check confidence-based skip
                if question.autofill_from and question.confidence_field:
                    # Extract field name
                    conf_field = question.confidence_field
                    if conf_field.startswith('analyzer.'):
                        conf_field = conf_field[9:]
                    
                    confidence = self.analysis.get(conf_field, 0)
                    if confidence < self.confidence_threshold:
                        selected.append(question)
        
        return selected
    
    def _get_gpai_mandatory_fields(self) -> List[str]:
        """Fields that are MANDATORY for GPAI providers."""
        return self.bank.get('selection_rules', {}).get('gpai_mandatory', [
            'web_scraped_domains',
            'domain_measurement_method', 
            'domain_coverage_percentage',
            'crawler_names',
            'crawler_purpose',
            'crawler_behavior',
            'collection_start_date',
            'collection_end_date',
            'user_data_sources',
            'user_data_modalities',
            'illegal_content_removal',
            'illegal_content_detection'
        ])
    
    def _create_question(self, q_data: Dict) -> Question:
        """Create Question object from dictionary."""
        return Question(
            id=q_data.get('id'),
            text=q_data.get('text'),
            type=q_data.get('type'),
            required=q_data.get('required', False),
            options=q_data.get('options'),
            validate=q_data.get('validate'),
            autofill_from=q_data.get('autofill_from'),
            confidence_field=q_data.get('confidence_field'),
            map_to=q_data.get('map_to'),
            required_if=q_data.get('required_if'),
            show_if=q_data.get('show_if'),
            help=q_data.get('help'),
            required_for_gpai=q_data.get('required_for_gpai', False)
        )
    
    def _check_conditional_requirement(self, question: Question) -> bool:
        """Check if question is conditionally required based on answers."""
        if not question.required_if:
            return False
        
        # Parse conditional requirement
        condition = question.required_if
        
        # Handle simple conditions like "source_types.includes('web_scraped')"
        if '.includes(' in condition:
            field, value = self._parse_includes_condition(condition)
            if field in self.answers:
                answer = self.answers[field]
                if isinstance(answer, list):
                    return value in answer
        
        # Handle equality conditions like "user_data_used == true"
        if '==' in condition:
            field, value = condition.split('==')
            field = field.strip()
            value = value.strip()
            
            if field in self.answers:
                answer = self.answers[field]
                # Convert string boolean to actual boolean
                if value.lower() == 'true':
                    return answer is True
                elif value.lower() == 'false':
                    return answer is False
                else:
                    return str(answer) == value
        
        return False
    
    def _parse_includes_condition(self, condition: str) -> Tuple[str, str]:
        """Parse includes condition like 'source_types.includes("web_scraped")'."""
        match = re.match(r'(\w+)\.includes\(["\']([^"\']+)["\']\)', condition)
        if match:
            return match.group(1), match.group(2)
        return None, None
    
    def _ask_question(self, question: Question) -> Any:
        """Ask a single question and return the answer."""
        # Try to autofill first
        if question.autofill_from:
            autofilled_value = self._get_autofill_value(question)
            if autofilled_value is not None:
                confidence = self._get_confidence(question)
                if confidence >= self.confidence_threshold:
                    print(f"✅ Auto-filled from analysis (confidence: {confidence:.0%})")
                    print(f"   Value: {self._format_value_display(autofilled_value)}")
                    
                    # Ask for confirmation
                    confirm = input("   Accept auto-filled value? (Y/n): ").strip().lower()
                    if confirm != 'n':
                        return autofilled_value
        
        # Ask based on question type
        print(f"❓ {question.text}")
        
        if question.help:
            print(f"   ℹ️  {question.help}")
        
        if question.type == 'select':
            return self._ask_select(question)
        elif question.type == 'multiselect':
            return self._ask_multiselect(question)
        elif question.type == 'boolean':
            return self._ask_boolean(question)
        elif question.type == 'text':
            return self._ask_text(question)
        elif question.type == 'textarea':
            return self._ask_textarea(question)
        elif question.type == 'email':
            return self._ask_email(question)
        elif question.type == 'date':
            return self._ask_date(question)
        elif question.type == 'number':
            return self._ask_number(question)
        elif question.type == 'text_list':
            return self._ask_text_list(question)
        elif question.type == 'domain_list':
            return self._ask_domain_list(question)
        elif question.type == 'table':
            return self._ask_table(question)
        else:
            # Default to text input
            return self._ask_text(question)
    
    def _get_autofill_value(self, question: Question) -> Optional[Any]:
        """Get autofill value from analysis results."""
        if not question.autofill_from:
            return None
        
        field = question.autofill_from
        if field.startswith('analyzer.'):
            field = field[9:]
        
        value = self.analysis.get(field)
        
        # Handle nested values
        if isinstance(value, dict) and 'values' in value:
            return value['values']
        
        return value
    
    def _get_confidence(self, question: Question) -> float:
        """Get confidence score for a field."""
        if not question.confidence_field:
            return 0.0
        
        field = question.confidence_field
        if field.startswith('analyzer.'):
            field = field[9:]
        
        return self.analysis.get(field, 0.0)
    
    def _format_value_display(self, value: Any) -> str:
        """Format value for display."""
        if isinstance(value, list):
            if len(value) > 5:
                return f"{value[:5]} ... ({len(value)} items)"
            return str(value)
        elif isinstance(value, str) and len(value) > 100:
            return f"{value[:100]}..."
        else:
            return str(value)
    
    def _ask_select(self, question: Question) -> str:
        """Ask select question."""
        options = question.options or []
        
        for idx, option in enumerate(options, 1):
            if isinstance(option, dict):
                print(f"  {idx}. {option.get('label', option.get('value'))}")
            else:
                print(f"  {idx}. {option}")
        
        while True:
            try:
                choice = input("\nSelect option number: ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(options):
                        if isinstance(options[idx], dict):
                            return options[idx].get('value')
                        return options[idx]
                print("❌ Invalid selection")
            except KeyboardInterrupt:
                raise
    
    def _ask_multiselect(self, question: Question) -> List[str]:
        """Ask multiselect question."""
        options = question.options or []
        selected = []
        
        print("   (Select multiple, enter numbers separated by commas)")
        
        for idx, option in enumerate(options, 1):
            if isinstance(option, dict):
                print(f"  {idx}. {option.get('label', option.get('value'))}")
            else:
                print(f"  {idx}. {option}")
        
        while True:
            try:
                choices = input("\nSelect options (e.g., 1,3,5): ").strip()
                if not choices:
                    return selected
                
                indices = [int(x.strip()) - 1 for x in choices.split(',')]
                
                for idx in indices:
                    if 0 <= idx < len(options):
                        if isinstance(options[idx], dict):
                            selected.append(options[idx].get('value'))
                        else:
                            selected.append(options[idx])
                
                return selected
            except (ValueError, KeyboardInterrupt):
                print("❌ Invalid selection")
    
    def _ask_boolean(self, question: Question) -> bool:
        """Ask boolean question."""
        while True:
            answer = input("\n(y/n): ").strip().lower()
            if answer in ['y', 'yes']:
                return True
            elif answer in ['n', 'no']:
                return False
            print("❌ Please enter y or n")
    
    def _ask_text(self, question: Question) -> str:
        """Ask text question."""
        while True:
            answer = input("\nEnter text: ").strip()
            
            # Validate if needed
            if question.validate and 'regex' in question.validate:
                pattern = question.validate['regex']
                # Resolve pattern from defaults if needed
                if pattern.startswith('${'):
                    # Extract default key
                    default_key = pattern[2:-1].split('.')[-1]
                    pattern = self.bank.get('defaults', {}).get(default_key, pattern)
                
                if not re.match(pattern, answer):
                    print(f"❌ Invalid format. Pattern: {pattern}")
                    continue
            
            return answer
    
    def _ask_textarea(self, question: Question) -> str:
        """Ask textarea question."""
        print("   (Enter multiple lines, end with empty line)")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        return '\n'.join(lines)
    
    def _ask_email(self, question: Question) -> str:
        """Ask email question."""
        while True:
            email = input("\nEnter email: ").strip()
            # Basic email validation
            if '@' in email and '.' in email.split('@')[1]:
                return email
            print("❌ Invalid email format")
    
    def _ask_date(self, question: Question) -> str:
        """Ask date question."""
        while True:
            date = input("\nEnter date (YYYY-MM-DD): ").strip()
            if re.match(r'^\d{4}-\d{2}-\d{2}$', date):
                return date
            print("❌ Invalid date format. Use YYYY-MM-DD")
    
    def _ask_number(self, question: Question) -> float:
        """Ask number question."""
        while True:
            try:
                num = float(input("\nEnter number: ").strip())
                
                # Check min/max if specified
                if question.validate:
                    if 'min' in question.validate and num < question.validate['min']:
                        print(f"❌ Value must be at least {question.validate['min']}")
                        continue
                    if 'max' in question.validate and num > question.validate['max']:
                        print(f"❌ Value must be at most {question.validate['max']}")
                        continue
                
                return num
            except ValueError:
                print("❌ Invalid number")
    
    def _ask_text_list(self, question: Question) -> List[str]:
        """Ask for list of text items."""
        print("   (Enter items one per line, empty line to finish)")
        items = []
        while True:
            item = input().strip()
            if not item:
                break
            items.append(item)
        return items
    
    def _ask_domain_list(self, question: Question) -> List[str]:
        """Ask for list of domains."""
        # Check if we have autofilled domains
        autofilled = self._get_autofill_value(question)
        if autofilled and isinstance(autofilled, list):
            print(f"   ✅ Found {len(autofilled)} domains from analysis")
            print(f"   Top 5: {autofilled[:5]}")
            confirm = input("   Use these domains? (Y/n): ").strip().lower()
            if confirm != 'n':
                return autofilled
        
        # Manual entry
        return self._ask_text_list(question)
    
    def _ask_table(self, question: Question) -> List[Dict]:
        """Ask for table data."""
        columns = question.options or []
        rows = []
        
        print("   (Enter data for each row, empty line to finish)")
        
        while True:
            print(f"\n   Row {len(rows) + 1}:")
            row = {}
            
            for col in columns:
                col_name = col.get('name', col.get('field'))
                col_type = col.get('type', 'text')
                required = col.get('required', False)
                
                while True:
                    value = input(f"     {col_name}: ").strip()
                    if not value and not required:
                        break
                    if value:
                        row[col.get('field', col_name)] = value
                        break
                    if required:
                        print(f"     ❌ {col_name} is required")
            
            if not any(row.values()):
                break
            
            rows.append(row)
        
        return rows
    
    def _show_provenance(self, question: Question, answer: Any):
        """Show provenance information for answer."""
        source = "user_provided"
        confidence = 1.0
        
        if question.autofill_from:
            autofilled = self._get_autofill_value(question)
            if autofilled == answer:
                source = "analyzer_autofill"
                confidence = self._get_confidence(question)
        
        print(f"   📊 Source: {source} | Confidence: {confidence:.0%}")
    
    def _map_to_template(self) -> Dict[str, Any]:
        """Map wizard answers to EU template structure."""
        # For pre-provided answers, return them directly with metadata
        # The answers should already be in the correct structure
        if self.answers:
            template = dict(self.answers)  # Copy the answers
            
            # Add metadata
            template['_metadata'] = template.get('_metadata', {})
            template['_metadata'].update({
                'is_gpai': self.is_gpai,
                'provider_type': self.answers.get('provider_type'),
                'generated_at': datetime.now().isoformat(),
                'wizard_version': '1.0.0'
            })
            
            # Add provenance metadata
            template['_provenance'] = self._generate_provenance()
            
            return template
        
        # For interactive mode, map individual answers
        template = {}
        
        # Process all answers
        for question_id, answer in self.answers.items():
            # Find the map_to path for this question
            map_path = self._find_map_to_path(question_id)
            
            if map_path:
                # Navigate to the correct location in template
                self._set_nested_value(template, map_path, answer)
        
        # Add metadata
        template['_metadata'] = {
            'is_gpai': self.is_gpai,
            'provider_type': self.answers.get('provider_type'),
            'generated_at': datetime.now().isoformat(),
            'wizard_version': '1.0.0'
        }
        
        # Add provenance metadata
        template['_provenance'] = self._generate_provenance()
        
        return template
    
    def _find_map_to_path(self, question_id: str) -> Optional[str]:
        """Find the map_to path for a question ID."""
        # Search all sections
        for section in ['gating', 'model_identification', 'training_data',
                       'data_sources', 'data_governance', 'model_card']:
            if section not in self.bank:
                continue
            
            questions = self.bank[section]
            if not isinstance(questions, list):
                continue
            
            for q in questions:
                if q.get('id') == question_id:
                    return q.get('map_to')
        
        return None
    
    def _set_nested_value(self, obj: Dict, path: str, value: Any):
        """Set a value in nested dictionary using dot notation path."""
        if not path:
            return
        
        keys = path.split('.')
        current = obj
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _generate_provenance(self) -> Dict:
        """Generate provenance tracking for all fields."""
        provenance = {}
        
        for question_id, answer in self.answers.items():
            source = "user_provided"
            confidence = 1.0
            
            # Find question definition
            question_def = None
            for section in ['gating', 'model_identification', 'training_data',
                           'data_sources', 'data_governance', 'model_card']:
                if section not in self.bank:
                    continue
                questions = self.bank[section]
                if isinstance(questions, list):
                    for q in questions:
                        if q.get('id') == question_id:
                            question_def = q
                            break
            
            # Check if autofilled
            if question_def and 'autofill_from' in question_def:
                autofilled = self._get_autofill_value(Question(**question_def))
                if autofilled == answer:
                    source = "analyzer_autofill"
                    if 'confidence_field' in question_def:
                        conf_field = question_def['confidence_field']
                        if conf_field.startswith('analyzer.'):
                            conf_field = conf_field[9:]
                        confidence = self.analysis.get(conf_field, 0.5)
            
            provenance[question_id] = {
                'value': answer,
                'source': source,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat()
            }
        
        return provenance
    
    def run_with_answers(self, answer_file: str) -> Dict[str, Any]:
        """Run wizard with pre-provided answers (for CI/CD)."""
        # Load answers from file
        with open(answer_file, 'r') as f:
            if answer_file.endswith('.yaml') or answer_file.endswith('.yml'):
                self.answers = yaml.safe_load(f)
            else:
                import json
                self.answers = json.load(f)
        
        # Determine GPAI status from answers
        self.is_gpai = self.answers.get('provider_type') in ['gpai_provider', 'unsure']
        
        # Map to template
        return self._map_to_template()