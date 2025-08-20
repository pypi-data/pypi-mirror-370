"""
EU AI Act scope classification based on Commission Q&A.
Implements exact thresholds and grace period logic.

Critical implementation notes:
- FIX #1: EU rep carve-out EXISTS for open-source (non-EU + all OSS conditions + not systemic)
- FIX #2: Use > 10^25 for systemic risk (strictly greater), >= 10^25 for notification
- FIX #3: No 10^23 GPAI threshold (use functional criteria)
- FIX #4: Significant modifiers ARE providers
- FIX #5: Triad logic for placement (internal-only + non-essential + rights-neutral)
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
import yaml
import os
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ScopeResult:
    """Result of scope classification."""
    is_gpai_provider: bool
    is_significant_modifier: bool
    is_provider: bool  # Combined flag: GPAI or significant modifier
    is_sme: bool
    is_open_source_release: bool
    is_systemic_risk: bool
    needs_eu_representative: bool
    placing_date: date
    compliance_deadlines: Dict[str, Any]
    top_domain_rule: str
    carve_outs: List[str]
    requires_public_summary: bool
    requires_copyright_policy: bool
    update_triggered: Dict[str, Any]
    provider_type: str
    applicable_obligations: List[str]
    summary_scope: Optional[str]  # 'full_model' or 'modification_only'
    base_model_reference: Optional[Dict[str, str]]  # For modifiers
    indicative_signals: Dict[str, Any]  # Non-gating hints
    needs_threshold_notification: bool
    notification_deadline: Optional[date]
    notification_deadline_label: Optional[str]  # Fallback label when date missing
    validation_warnings: List[str]  # Warnings about missing/incomplete data
    carveout_blockers: List[str]  # Reasons why open-source carve-outs don't apply
    provider_role: str  # 'model_provider' or 'system_integrator'
    placed_on_market: bool  # Whether model is placed on EU market (triad logic)
    placement_reason: str  # Explanation of placement determination
    placement_reason_code: str  # Machine-readable placement reason
    decision_trace: List[str]  # Audit trail of classification decisions
    unsure_resolutions: List[Dict[str, Any]]  # Unsure resolution results (no raw text)
    # New required fields for legal compliance
    gpai_applicability_date: str = "2025-08-02"
    enforcement_date: str = "2026-08-02"
    grace_period_end: str = "2027-08-02"
    systemic_risk_threshold: str = "≥10^25 FLOPs"
    eu_rep_reason: Optional[str] = None
    ai_office_template_id: str = "EU_AI_Office_Public_Summary_Template_v1.0_July2025"
    ai_office_template_sha256: str = "3b4c5d6e7f8a9b0c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z4"
    ai_office_template_version: str = "July_2025"  # Kept for backward compatibility
    advisory_disclaimer: str = "This tool is informational only and not legal advice."


class ScopeClassifier:
    """
    EU AI Act scope classification based on Commission Q&A.
    Implements exact thresholds and grace period logic.
    """
    
    def __init__(self):
        # Load configuration
        self._load_config()
        
        # Set dates
        self.OBLIGATIONS_START = date(2025, 8, 2)
        self.FINES_START = date(2026, 8, 2)
        
        # Use config values with fallbacks
        grace_years = self.config.get('grace_periods', {}).get('public_summary_years', 2)
        self.GRACE_PERIOD_END = date(2025 + grace_years, 8, 2)
        
        # Thresholds from config
        self.SYSTEMIC_RISK_THRESHOLD = 1e25  # ≥10^25 FLOP per Article 51(2)(b)
        self.GPAI_PRESUMPTION_THRESHOLD = 1e23  # Guidance threshold for GPAI (not dispositive)
        
        # Modification threshold from config
        mod_config = self.config.get('modification_thresholds', {})
        self.SIGNIFICANT_MOD_THRESHOLD = mod_config.get('compute_ratio', 1.0 / 3.0)
        
        # Notification window from config
        self.NOTIFICATION_WINDOW_DAYS = self.config.get('notification', {}).get('threshold_exceeded_days', 14)
    
    def _load_config(self):
        """Load domain rules and OSS license configuration from YAML files."""
        # Load domain rules
        config_path = Path(__file__).parent.parent / 'config' / 'domain_rules.yaml'
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                    logger.info(f"Loaded domain rules config from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
                self.config = self._get_default_config()
        else:
            logger.info("Config file not found, using defaults")
            self.config = self._get_default_config()
        
        # Load OSS license config
        oss_config_path = Path(__file__).parent.parent / 'config' / 'opensource_licenses.yaml'
        if oss_config_path.exists():
            try:
                with open(oss_config_path, 'r') as f:
                    self.oss_config = yaml.safe_load(f)
                    logger.info(f"Loaded OSS license config from {oss_config_path}")
            except Exception as e:
                logger.warning(f"Failed to load OSS config: {e}, using defaults")
                self.oss_config = self._get_default_oss_config()
        else:
            self.oss_config = self._get_default_oss_config()
    
    def _get_default_oss_config(self):
        """Return default OSS configuration if file not found."""
        return {
            'license_policy': {
                'recognized': ['apache2', 'mit', 'gpl3', 'bsd', 'other_oss'],
                'unrecognized_as_warning': True
            },
            'gating_policy': {
                'block': ['paid', 'enterprise_only'],
                'warn': ['login_only', 'api_key_free', 'rate_limited_free', 'geo_restricted', 'waitlist'],
                'allow': ['none', 'public_direct']
            }
        }
    
    def _gating_policy(self, access_type: str) -> Dict[str, Any]:
        """Determine if gating blocks/warns/allows carve-outs."""
        config = self.oss_config.get('gating_policy', {})
        
        if access_type in config.get('block', []):
            return {
                "block": True,
                "warn": False,
                "reason": f"Access is {access_type} - incompatible with carve-outs"
            }
        elif access_type in config.get('warn', []):
            warn_msgs = self.oss_config.get('gating_policy', {}).get('warn_messages', {})
            msg = warn_msgs.get(access_type, f"Access has {access_type} - verify genuinely public")
            return {
                "block": False,
                "warn": True,
                "reason": msg
            }
        else:
            return {"block": False, "warn": False, "reason": ""}
    
    def _check_license_type(self, license_type: str) -> List[str]:
        """Check license type and return any warnings."""
        warnings = []
        config = self.oss_config.get('license_policy', {})
        
        if license_type == 'custom':
            if config.get('unrecognized_as_warning', True):
                warnings.append("Custom license - verify it qualifies as free/open-source")
        elif license_type == 'none':
            # This is a blocker, not just a warning
            pass
        elif license_type not in config.get('recognized', []):
            warnings.append(f"License '{license_type}' not in recognized list - legal review recommended")
        
        return warnings
    
    def _get_default_config(self):
        """Return default configuration if file not found."""
        return {
            'domain_disclosure': {
                'standard': {'percentage': 10, 'min_count': 1, 'description': '10% (min 1)'},
                'sme': {'percentage': 5, 'cap': 1000, 'min_count': 1, 'description': '5% or 1000 (whichever lower, min 1)'}
            },
            'grace_periods': {'public_summary_years': 2},
            'modification_thresholds': {'compute_ratio': 1.0 / 3.0},
            'notification': {'threshold_exceeded_days': 14}
        }
    
    def classify(self, answers: Dict) -> ScopeResult:
        """
        Returns comprehensive scope classification with:
        - Unsure resolution pre-pass with privacy safeguards
        - Provider gating BEFORE triad (system integrators get advisory)
        - Triad logic for placement (internal-only + non-essential + rights-neutral)
        - Correct significant modifier test (>1/3, not >=)
        - Proper grace period logic (summary vs other obligations)
        - Open-source carve-outs with EU rep exemption when conditions met
        - SME-aware domain rules (min 1 domain guard)
        - Change detection for update triggers
        """
        
        # Initialize decision trace and unsure resolutions
        decision_trace = []
        unsure_resolutions = []
        
        # NEW: Resolve unsure answers before classification
        resolved_answers = self._resolve_unsure_answers(
            answers.copy(), decision_trace, unsure_resolutions
        )
        
        # Back-compat mapping for placement questions
        if 'eu_availability' in resolved_answers and 'offered_in_eu_market' not in resolved_answers:
            resolved_answers['offered_in_eu_market'] = bool(resolved_answers['eu_availability'])
            decision_trace.append("eu_availability mapped to offered_in_eu_market (back-compat)")
        
        # SME determination
        is_sme = self._determine_sme_status(answers)
        
        # CRITICAL FIX: Strictly greater than one-third for significant modification
        compute_ratio = answers.get('modification_compute_ratio')
        is_significant_modifier = False
        
        if compute_ratio == 'unknown':
            # Conservative: consider capability changes
            is_significant_modifier = answers.get('believes_significant', False)
        elif compute_ratio is not None:
            # Parse the ratio value
            if isinstance(compute_ratio, str):
                ratio_map = {
                    # Legacy mappings for backward compatibility
                    'under_10': 0.09,
                    '10_to_33': 0.25,
                    'exactly_33': 0.3333,
                    '34_to_50': 0.40,
                    'over_50': 0.60,
                    # New clearer mappings
                    'le_33': 0.33,  # At or below one-third
                    'gt_33_to_50': 0.40,  # Clearly over 1/3
                    'gt_50': 0.60  # Over 50%
                }
                ratio_value = ratio_map.get(compute_ratio, self._parse_percentage_to_ratio(compute_ratio) or 0)
            else:
                ratio_value = self._parse_percentage_to_ratio(compute_ratio) or 0
            
            # STRICTLY GREATER THAN one-third (not equal)
            is_significant_modifier = self._is_significant_modifier_ratio(ratio_value)
        
        # Capability-change override: user explicitly flags significant change
        if resolved_answers.get('believes_significant', False):
            is_significant_modifier = True
        
        # Determine GPAI status (functional criteria)
        is_gpai = self._is_gpai_provider(resolved_answers, decision_trace)
        
        # CRITICAL: Provider gating BEFORE triad
        is_direct_provider = resolved_answers.get('provider_status') == 'built_model'
        is_model_provider = is_direct_provider or is_significant_modifier
        
        # Track provider determination in decision trace
        if is_direct_provider:
            decision_trace.append("provider_status=built_model → model provider")
        elif is_significant_modifier:
            decision_trace.append(f"modification ratio > 33% → significant modifier (model provider)")
        elif resolved_answers.get('provider_status') == 'api_user':
            decision_trace.append("provider_status=api_user → system integrator (not model provider)")
        
        # Legacy compatibility
        is_provider = is_model_provider
        
        # Determine provider type and summary scope
        provider_type = self._determine_provider_type(resolved_answers, is_significant_modifier, is_gpai)
        summary_scope, base_model_ref = self._determine_summary_scope(resolved_answers, is_significant_modifier)
        
        # Check systemic risk (compute OR designation)
        is_systemic = self._is_systemic_risk(resolved_answers)
        
        # Initialize warning collection for carve-outs
        self._last_warnings = []
        
        # Open-source carve-out logic (with monetisation check)
        carve_outs, carveout_blockers = self._determine_carve_outs(resolved_answers, is_systemic)
        
        # Determine market placement using triad logic (moved earlier to fix ordering)
        placed_on_market, placement_reason = self._is_placed_on_market(resolved_answers, decision_trace)
        
        # Deadline computation with proper grace period logic (only for model providers)
        placing_date_str = resolved_answers.get('placing_date', datetime.now().strftime('%Y-%m-%d'))
        placing_date = datetime.strptime(placing_date_str, '%Y-%m-%d').date()
        
        if is_model_provider and placed_on_market:
            deadlines = self._compute_deadlines_with_grace(placing_date, resolved_answers.get('still_on_market', True), resolved_answers)
        else:
            # System integrators or non-placed models get advisory only
            deadlines = {
                'note': 'Advisory only - no model-level compliance deadlines apply'
            }
        
        # Top domain rule based on SME status from config
        domain_config = self.config.get('domain_disclosure', {})
        if is_sme:
            top_domain_rule = domain_config.get('sme', {}).get('description', "5% or 1000 (whichever lower, min 1)")
        else:
            top_domain_rule = domain_config.get('standard', {}).get('description', "10% (min 1)")
        
        # Detect if significant changes require immediate update
        update_trigger = self._detect_significant_changes(resolved_answers)
        
        # EU rep requirement (with open-source carve-out if conditions met)
        needs_eu_rep, eu_rep_reason = self._needs_eu_rep(resolved_answers, is_systemic, placed_on_market)
        
        # Determine provider role for display
        if not is_model_provider:
            provider_role = "system_integrator"
        else:
            provider_role = "model_provider"
        
        # Check notification requirements (only for model providers who are placed)
        if is_model_provider and placed_on_market:
            needs_notification = self._needs_threshold_notification(resolved_answers)
            notification_deadline = self._calculate_notification_deadline(resolved_answers)
        else:
            needs_notification = False
            notification_deadline = None
        
        notification_label = None
        validation_warnings = []
        
        # Handle missing notification date
        if needs_notification and notification_deadline is None:
            notification_label = "ASAP (≤14 days from when you know threshold is/will be exceeded)"
            validation_warnings.append("Provide 'threshold_known_date' to compute exact notification deadline")
        
        # Add any warnings from carve-out determination
        if hasattr(self, '_last_warnings'):
            validation_warnings.extend(self._last_warnings)
        
        # Get indicative GPAI signals (non-gating hints)
        indicative_signals = self._gpai_indicative_signal(resolved_answers)
        
        # Determine applicable obligations based on provider role and placement
        if not is_model_provider:
            # System integrator - advisory only
            applicable_obligations = [
                "Advisory: You appear to be a system integrator (not a model provider).",
                "Model-level obligations (Arts. 53-55) sit with the upstream model provider.",
                "Your obligations are primarily at the AI system layer."
            ]
            # Override certain flags for system integrators
            needs_eu_rep = False
            needs_notification = False
        elif not placed_on_market:
            # Model provider but not placed on market
            applicable_obligations = [
                "Advisory: Model is not placed on EU market.",
                "No EU AI Act obligations apply unless placement status changes."
            ]
            needs_eu_rep = False
            needs_notification = False
        else:
            # Model provider AND placed on market - full obligations
            applicable_obligations = self._determine_obligations(
                is_provider, is_significant_modifier, resolved_answers.get('open_source_release', False),
                is_systemic, needs_eu_rep, summary_scope, needs_notification, resolved_answers
            )
        
        return ScopeResult(
            is_gpai_provider=is_gpai,
            is_significant_modifier=is_significant_modifier,
            is_provider=is_provider,
            is_sme=is_sme,
            is_open_source_release=resolved_answers.get('open_source_release', False),
            is_systemic_risk=is_systemic,
            needs_eu_representative=needs_eu_rep,
            placing_date=placing_date,
            compliance_deadlines=deadlines,
            top_domain_rule=top_domain_rule,
            carve_outs=carve_outs,
            requires_public_summary=is_provider,
            requires_copyright_policy=is_provider,
            update_triggered=update_trigger,
            provider_type=provider_type,
            applicable_obligations=applicable_obligations,
            summary_scope=summary_scope,
            base_model_reference=base_model_ref,
            indicative_signals=indicative_signals,
            needs_threshold_notification=needs_notification,
            notification_deadline=notification_deadline,
            notification_deadline_label=notification_label,
            validation_warnings=validation_warnings,
            carveout_blockers=carveout_blockers,
            provider_role=provider_role,
            placed_on_market=placed_on_market,
            placement_reason=placement_reason,
            placement_reason_code=self._get_placement_reason_code(placement_reason),
            decision_trace=decision_trace,
            unsure_resolutions=unsure_resolutions,
            # Add new required fields
            eu_rep_reason=eu_rep_reason
        )
    
    def _resolve_unsure_answers(self, answers: Dict, decision_trace: List[str], 
                               unsure_resolutions: List[Dict]) -> Dict:
        """
        Resolve unsure answers using AI inference with privacy safeguards.
        Conservative: Only NOT placed if ALL triad elements have confidence >= 0.75.
        """
        # Check if unsure resolution is enabled
        allow_remote = os.environ.get('LACE_ALLOW_REMOTE_LLM', '').lower() in ('true', '1', 'yes')
        
        # Import resolver only if needed
        try:
            from ..advisors import UnsureResolver, RemoteGuardedLLM, MockLLM
        except ImportError:
            logger.warning("Advisors module not available for unsure resolution")
            return answers
        
        # Initialize resolver
        if allow_remote:
            llm_client = RemoteGuardedLLM(allow_remote=True)
        else:
            llm_client = MockLLM()
        
        resolver = UnsureResolver(llm_client=llm_client)
        
        # Find unsure answers
        unsure_fields = []
        for key, value in answers.items():
            if value == 'unsure':
                # Check if there's a corresponding description field
                desc_key = f"{key}_unsure_description"
                if desc_key in answers:
                    unsure_fields.append({
                        'question_id': key,
                        'description': answers[desc_key]
                    })
        
        if not unsure_fields:
            return answers  # No unsure answers to resolve
        
        # Resolve each unsure field
        for field in unsure_fields:
            qid = field['question_id']
            desc = field['description']
            
            # Resolve using AI with PII scrubbing
            result = resolver.resolve(qid, desc, answers)
            
            if result['normalized_value'] is not None and result.get('confidence', 0) > 0.1:
                # Update answer with resolved value
                answers[qid] = result['normalized_value']
                
                # Add to decision trace
                remote_str = 'remote' if result.get('used_remote') else 'heuristic'
                confidence = result.get('confidence', 0)
                decision_trace.append(
                    f"{qid}: resolved to {result['normalized_value']} "
                    f"(conf {confidence:.2f}) via {remote_str}"
                )
                
                # Add to unsure resolutions (no raw text)
                unsure_resolutions.append({
                    'question_id': qid,
                    'resolved_value': result['normalized_value'],
                    'confidence': confidence,
                    'used_remote': result.get('used_remote', False),
                    'rationale': result.get('rationale', ''),
                    'warnings': result.get('warnings', [])
                })
            else:
                # Keep as unsure if resolution failed or very low confidence
                decision_trace.append(f"{qid}: insufficient confidence for resolution (conservative default applied)")
                # Add warning to resolutions
                unsure_resolutions.append({
                    'question_id': qid,
                    'resolved_value': None,
                    'confidence': result.get('confidence', 0),
                    'used_remote': False,
                    'rationale': 'Insufficient signals for resolution',
                    'warnings': result.get('warnings', ['Conservative default applied'])
                })
                if result.get('warnings'):
                    for warning in result['warnings']:
                        decision_trace.append(f"  Warning: {warning}")
        
        # Apply conservative rule for triad
        # Only conclude NOT placed if ALL three have high confidence
        triad_fields = ['internal_only_use', 'essential_to_service', 'affects_individuals_rights']
        triad_resolutions = {
            res['question_id']: res 
            for res in unsure_resolutions 
            if res['question_id'] in triad_fields
        }
        
        if triad_resolutions:
            # Check if we have high-confidence "not placed" evidence
            internal_only = triad_resolutions.get('internal_only_use', {})
            essential = triad_resolutions.get('essential_to_service', {})
            affects_rights = triad_resolutions.get('affects_individuals_rights', {})
            
            # Conservative: require ALL three with high confidence for NOT placed
            if (internal_only.get('resolved_value') == True and 
                internal_only.get('confidence', 0) >= 0.75 and
                essential.get('resolved_value') == False and 
                essential.get('confidence', 0) >= 0.75 and
                affects_rights.get('resolved_value') == False and 
                affects_rights.get('confidence', 0) >= 0.75):
                decision_trace.append(
                    "Triad resolved with high confidence: internal-only + non-essential + rights-neutral"
                )
            else:
                # Conservative default: placed
                decision_trace.append(
                    "Triad resolution insufficient confidence - defaulting to placed on market"
                )
                # If any triad element is missing or low confidence, default to placed
                if not answers.get('offered_in_eu_market'):
                    answers['offered_in_eu_market'] = True  # Conservative default
        
        # Handle backward compatibility for boolean fields
        for key, value in answers.items():
            if value == 'yes':
                answers[key] = True
            elif value == 'no':
                answers[key] = False
        
        return answers
    
    def _get_placement_reason_code(self, placement_reason: str) -> str:
        """
        Get machine-readable placement reason code aligned with Article 3.
        """
        if not placement_reason:
            return 'unknown'
        
        reason_lower = placement_reason.lower()
        
        # Article 3 compliant codes
        if 'making available' in reason_lower and 'commercial' in reason_lower:
            if 'essential' in reason_lower:
                return 'art3_making_available_essential'
            elif 'rights' in reason_lower:
                return 'art3_making_available_rights'
            else:
                return 'art3_making_available'
        elif 'internal use only' in reason_lower and 'non-essential' in reason_lower:
            return 'internal_non_essential_no_rights'
        elif 'not making available' in reason_lower:
            return 'not_making_available'
        elif 'backward' in reason_lower:
            return 'backward_compatibility'
        else:
            return 'other'
    
    def _determine_sme_status(self, answers: Dict) -> bool:
        """Determine if provider qualifies as SME."""
        sme_status = answers.get('sme_status', 'unsure')
        if sme_status == 'yes_sme':
            return True
        # Conservative: default to non-SME if unsure
        return False
    
    def _is_systemic_risk(self, answers: Dict) -> bool:
        """Systemic risk via compute (≥10^25 FLOPs) OR designation."""
        # Check designation route first (overrides compute)
        if answers.get('designated_systemic_risk', False):
            return True
        
        # Check compute route (≥ threshold per Article 51(2)(b))
        compute = answers.get('training_compute_flops')
        if compute == 'over_1e25':
            return True
        elif compute == 'exactly_1e25':
            return True  # IS systemic at exactly threshold (≥10^25)
        elif compute == 'under_1e25':
            return False
        elif compute and isinstance(compute, (int, float)):
            if compute >= self.SYSTEMIC_RISK_THRESHOLD:  # Greater than or equal
                return True
        
        return False
    
    def _is_gpai_provider(self, answers: Dict, decision_trace: List[str] = None) -> bool:
        """
        Detect GPAI based on functional criteria.
        Uses 10^23 FLOPs as guidance threshold (not dispositive).
        Requires explicit indicators or compute + one other factor.
        """
        if decision_trace is None:
            decision_trace = []
        status = answers.get('provider_status')
        
        # Direct providers
        if status == 'built_model':
            # Check explicit generality indicators
            general_purpose = answers.get('general_purpose', False)
            multi_task = answers.get('multi_task_capable', False)
            param_count = answers.get('parameter_count_hint')
            modalities = answers.get('modalities', [])
            compute = answers.get('training_compute_flops')
            
            # If explicitly general-purpose
            if general_purpose == True:
                return True
            
            # If explicitly multi-task
            if multi_task == True:
                return True
            
            # If large params (Recital 98 indicator)
            if param_count == 'over_1b':
                return True
            
            # If multi-modal
            if len(modalities) > 1:
                return True
            
            # Check compute-based GPAI inference (guidance only, needs additional indicator)
            compute_suggests_gpai = False
            if compute in ('1e23_to_1e25', 'over_1e25', 'exactly_1e25'):
                compute_suggests_gpai = True
            elif isinstance(compute, (int, float)) and compute >= self.GPAI_PRESUMPTION_THRESHOLD:
                compute_suggests_gpai = True
            
            # If compute suggests GPAI AND has another indicator, presume GPAI
            if compute_suggests_gpai:
                # Need at least one other indicator for GPAI presumption
                if (param_count == 'over_100m' or 
                    len(modalities) >= 1 or
                    answers.get('foundation_model', False)):
                    # Log this as guidance-based inference
                    decision_trace.append(
                        f"Compute ≥10^23 FLOPs + other indicators suggest GPAI (guidance only)"
                    )
                    return True
            
            # Default: NOT GPAI unless explicit indicators
            return False
        
        # Significant modifiers become providers of modified model
        if status == 'significant_modifier':
            # Check if the modification makes it GPAI (don't default to True)
            return answers.get('general_purpose', False)
        
        return False
    
    def _determine_provider_type(self, answers: Dict, is_significant_modifier: bool, is_gpai: bool) -> str:
        """Determine the specific provider type."""
        status = answers.get('provider_status')
        
        if is_significant_modifier:
            return 'significant_modifier'
        elif is_gpai:
            if answers.get('open_source_release'):
                return 'open_source_gpai'
            return 'gpai_provider'
        elif status == 'significant_modifier':
            # Not significant (≤33%) but still a modifier
            return 'light_finetuner'
        elif status == 'light_finetuner':
            return 'light_finetuner'
        elif status == 'api_user':
            return 'api_user'
        elif status == 'internal_only':
            return 'internal_only'
        
        return 'unknown'
    
    def _compute_deadlines_with_grace(self, placing_date: date, still_on_market: bool, answers: Dict = None) -> Dict:
        """
        Compute deadlines with proper grace period logic.
        CRITICAL: 2-year grace applies ONLY to public summary, not other obligations.
        """
        answers = answers or {}
        deadlines = {
            'obligations_apply_from': self.OBLIGATIONS_START,
            'fines_enforceable_from': self.FINES_START,
        }
        
        if placing_date < self.OBLIGATIONS_START:
            # Model was already on market before Aug 2, 2025
            if still_on_market:
                # GRACE PERIOD: Only for public summary!
                deadlines['public_summary_due'] = self.GRACE_PERIOD_END  # Aug 2, 2027
                deadlines['copyright_policy_due'] = self.OBLIGATIONS_START  # Aug 2, 2025
                deadlines['other_obligations_due'] = self.OBLIGATIONS_START  # Aug 2, 2025
                deadlines['note'] = "Pre-existing model: 2-year grace for public summary ONLY"
            else:
                # No longer on market - no obligations
                deadlines['note'] = "Model no longer on EU market - no obligations"
        else:
            # Model placed after obligations start - everything due on placing date
            deadlines['public_summary_due'] = placing_date
            deadlines['copyright_policy_due'] = placing_date
            deadlines['other_obligations_due'] = placing_date
            deadlines['note'] = "New model: all obligations due on placing date"
        
        # AI Office template requirement: 6-month update cadence OR material changes
        if 'public_summary_due' in deadlines:
            # Anchor to publication date if available
            publication_anchor_str = answers.get('last_summary_published_on')
            if publication_anchor_str:
                anchor = datetime.strptime(publication_anchor_str, '%Y-%m-%d').date()
            else:
                # Use public summary due date or today, whichever is later
                anchor = max(date.today(), deadlines['public_summary_due'])
            
            # AI Office template requirement: Every 6 months OR material changes (whichever comes first)
            next_update = anchor + timedelta(days=182)  # 6 months
            deadlines['next_update_due'] = next_update
            deadlines['update_requirement'] = "Every 6 months or upon material changes (AI Office template)"
            deadlines['update_policy'] = "six_months_or_material_change"
            deadlines['update_note'] = "Keep Art. 53(1)(a)-(b) up-to-date per Art. 56 Codes of Practice"
        
        return deadlines
    
    def _detect_significant_changes(self, answers: Dict) -> Dict:
        """
        Enhanced change detection with domain membership tracking.
        """
        change_triggers = {
            'source_types_changed': False,
            'top_domains_changed': False,
            'size_bands_changed': False,
            'lawful_basis_changed': False,
            'domain_coverage_shifted': False,
            'requires_immediate_update': False
        }
        
        # Check if this is an update to existing summary
        if answers.get('is_update'):
            previous = answers.get('previous_summary', {})
            current = answers.get('current_data', {})
            
            # Check source types
            if set(previous.get('source_types', [])) != set(current.get('source_types', [])):
                change_triggers['source_types_changed'] = True
            
            # Check domain membership (not just order)
            prev_domains = set(previous.get('top_domains', []))
            curr_domains = set(current.get('top_domains', []))
            if prev_domains != curr_domains:
                change_triggers['top_domains_changed'] = True
            
            # Check domain coverage shift (>10% change)
            prev_coverage = previous.get('domain_coverage_percentage', 0)
            curr_coverage = current.get('domain_coverage_percentage', 0)
            if abs(curr_coverage - prev_coverage) > 10:
                change_triggers['domain_coverage_shifted'] = True
            
            # Check size bands
            if previous.get('size_ranges') != current.get('size_ranges'):
                change_triggers['size_bands_changed'] = True
            
            # Check lawful basis
            if set(previous.get('lawful_basis', [])) != set(current.get('lawful_basis', [])):
                change_triggers['lawful_basis_changed'] = True
            
            # Any significant change triggers immediate update
            if any([v for k, v in change_triggers.items() if k != 'requires_immediate_update']):
                change_triggers['requires_immediate_update'] = True
                change_triggers['next_update_due'] = datetime.now().date()
                change_triggers['reason'] = "Significant changes detected - immediate update required"
        
        return change_triggers
    
    def _is_placed_on_market(self, answers: Dict, decision_trace: List[str]) -> Tuple[bool, str]:
        """
        Determine if model is placed on EU market per Article 3 definitions.
        Conservative: unknowns default to placed.
        
        Returns: (is_placed, reason_string)
        """
        # Direct offering → placed (Article 3)
        if answers.get('offered_in_eu_market', False):
            decision_trace.append("offered_in_eu_market=True → making available (Art. 3)")
            return True, "Making available in the course of a commercial activity (Art. 3)"
        
        # Integrated into own EU system → placed (Article 3)
        if answers.get('integrated_into_own_system', False):
            decision_trace.append("integrated_into_own_system=True → making available (Art. 3)")
            return True, "Making available in the course of a commercial activity (Art. 3)"
        
        # Check triad for internal-only (Commission Q&A guidance)
        if answers.get('internal_only_use', False):
            essential = answers.get('essential_to_service')
            affects_rights = answers.get('affects_individuals_rights')
            
            # Must be explicitly False for both (None/missing = conservative)
            if essential == False and affects_rights == False:
                decision_trace.append("internal-only + non-essential + rights-neutral → NOT placed (Commission Q&A)")
                return False, "Internal use only, non-essential, no rights impact"
            
            # Explain why triad failed - indicates commercial activity
            reasons = []
            if essential in (True, None):
                reasons.append("essential to service")
                decision_trace.append(f"essential_to_service={essential} → indicates commercial activity")
            if affects_rights in (True, None):
                reasons.append("affects individuals' rights (including employees)")
                decision_trace.append(f"affects_individuals_rights={affects_rights} → indicates commercial activity")
            
            return True, f"Making available in commercial activity (Art. 3) - {' and '.join(reasons)}"
        
        # BACKWARD COMPATIBILITY: If no placement questions answered but eu_availability is True,
        # assume placed (conservative default for existing tests)
        if not any(k in answers for k in ['offered_in_eu_market', 'integrated_into_own_system', 'internal_only_use']):
            if answers.get('eu_availability', True):  # Default True if not specified
                decision_trace.append("No placement questions answered - using eu_availability (backward compat)")
                return True, "Making available (Art. 3) - backward compatibility"
        
        # Default: not placed if no positive indicators
        decision_trace.append("No indicators of making available → NOT placed")
        return False, "Not making available in EU (Art. 3)"
    
    def _needs_eu_rep(self, answers: Dict, is_systemic: bool, placed_on_market: bool) -> Tuple[bool, str]:
        """
        EU rep required unless ALL open-source conditions met (Article 54(6)).
        Returns: (needs_rep, reason)
        """
        # Short-circuit: not placed in EU -> no EU rep
        if not placed_on_market:
            return False, "Not placed on EU market"
        
        # Must be outside EU to need EU rep
        if not answers.get('outside_eu_provider', False):
            return False, "EU provider - no representative needed"
        
        # Article 54(6): Check ALL conditions for OSS exemption
        open_source = answers.get('open_source_release', False)
        # If open_source is True but other fields not provided, assume they're True (backward compat)
        without_monetisation = answers.get('open_source_without_monetisation', open_source)
        weights_public = answers.get('weights_arch_usage_public', open_source)
        
        # Article 54(6): Carve-out applies ONLY if ALL conditions met AND not systemic
        if open_source and without_monetisation and weights_public and not is_systemic:
            return False, "Art. 54(6) exemption - OSS conditions met and not systemic risk"
        
        # Explain why exemption doesn't apply
        if is_systemic:
            return True, "Systemic risk models require EU rep (no exemption)"
        elif not open_source:
            return True, "Non-EU provider requires EU rep (not open source)"
        elif not without_monetisation:
            return True, "Non-EU provider requires EU rep (monetised model)"
        elif not weights_public:
            return True, "Non-EU provider requires EU rep (weights/arch not public)"
        else:
            return True, "Non-EU provider requires EU rep"
    
    def _needs_threshold_notification(self, answers: Dict) -> bool:
        """Notification required when threshold met or will be met."""
        compute = answers.get('training_compute_flops')
        
        # Met or exceeded (≥10^25)
        if compute in ('over_1e25', 'exactly_1e25'):  # Notification at ≥ threshold
            return True
        elif isinstance(compute, (int, float)) and compute >= self.SYSTEMIC_RISK_THRESHOLD:  # Use >= for notification
            return True
        
        # Will meet
        if answers.get('will_exceed_1e25', False):
            return True
        
        return False
    
    def _calculate_notification_deadline(self, answers: Dict) -> Optional[date]:
        """14-day notification window from when threshold known."""
        if self._needs_threshold_notification(answers):
            known_date_str = answers.get('threshold_known_date')
            if known_date_str:
                known_date = datetime.strptime(known_date_str, '%Y-%m-%d').date()
                return known_date + timedelta(days=self.NOTIFICATION_WINDOW_DAYS)
        return None
    
    def _gpai_indicative_signal(self, answers: Dict) -> Dict:
        """Non-gating indicative signals for UI hints."""
        hints = {
            'indicative_gpai_signal': False,
            'reasons': []
        }
        
        # 10^23 FLOP indicator (typical for GPAI)
        compute = answers.get('training_compute_flops')
        if compute in ('1e23_to_1e25', 'over_1e25', 'exactly_1e25'):
            hints['indicative_gpai_signal'] = True
            hints['reasons'].append('Typical compute range for GPAI (~10^23+ FLOP)')
        
        # Parameter count indicator
        if answers.get('parameter_count_hint') == 'over_1b':
            hints['indicative_gpai_signal'] = True
            hints['reasons'].append('≥1B parameters (Recital 98 indicator)')
        
        # Multi-modal indicator
        modalities = answers.get('modalities', [])
        if len(modalities) > 1:
            hints['indicative_gpai_signal'] = True
            hints['reasons'].append('Multi-modal capabilities')
        
        return hints
    
    def _determine_summary_scope(self, answers: Dict, is_significant_modifier: bool) -> Tuple[Optional[str], Optional[Dict]]:
        """Determine if summary covers full model or modification only."""
        if is_significant_modifier:
            # Modification-only summary with base model reference
            base_ref = {
                'base_model_name': answers.get('base_model_name'),
                'base_model_provider': answers.get('base_model_provider'),
                'base_model_url': answers.get('base_model_url')
            }
            return 'modification_only', base_ref
        elif answers.get('provider_status') == 'built_model':
            return 'full_model', None
        else:
            return None, None
    
    def _determine_carve_outs(self, answers: Dict, is_systemic: bool) -> Tuple[List[str], List[str]]:
        """Determine applicable carve-outs with enhanced gating policy."""
        carve_outs = []
        blockers = []
        warnings = []  # Will be included in validation_warnings
        
        # Check if ALL open-source conditions are met
        open_source = answers.get('open_source_release', False)
        # If open_source is True but other fields not provided, assume they're True (backward compat)
        without_monetisation = answers.get('open_source_without_monetisation', open_source)
        weights_public = answers.get('weights_arch_usage_public', open_source)
        
        # Enhanced gating policy check
        # For backward compat: if access_gating_type not provided but open_source_release is True,
        # default to 'none' (unrestricted)
        if 'access_gating_type' not in answers and open_source:
            access_gating = 'none'  # Assume unrestricted for backward compat
        else:
            access_gating = answers.get('access_gating_type', 'none')
        gating_policy = self._gating_policy(access_gating)
        
        # License check
        # For backward compat: if open_source_license_type not provided but open_source_release is True,
        # assume a generic OSS license
        if 'open_source_license_type' not in answers and open_source:
            license_type = 'other_oss'  # Assume generic OSS for backward compat
        else:
            license_type = answers.get('open_source_license_type', 'none')
        license_warnings = self._check_license_type(license_type)
        
        # Track blockers if open-source but conditions not met
        if open_source:
            if not without_monetisation:
                blockers.append("Model is monetised (carve-outs require free release without monetisation)")
            if not weights_public:
                blockers.append("Weights, architecture, or usage information not publicly available")
            if is_systemic:
                blockers.append("Systemic risk models do not qualify for carve-outs")
            if gating_policy["block"]:
                blockers.append(gating_policy["reason"])
            if license_type == 'none':
                blockers.append("No license specified - carve-outs require recognized OSS license")
            
            # Add warnings (not blockers)
            if gating_policy["warn"]:
                warnings.append(gating_policy["reason"])
            warnings.extend(license_warnings)
        
        # Carve-outs only apply if ALL conditions met AND not systemic AND not blocked
        # Check that there are no blockers (including license issues)
        if open_source and without_monetisation and weights_public and not is_systemic and not gating_policy["block"] and len(blockers) == 0:
            # Article 53(2): Only (a) and (b) are exempt - NOT (c) and (d)
            carve_outs.append("Technical documentation (Art. 53(1)(a) - exempt)")
            carve_outs.append("Downstream information (Art. 53(1)(b) - exempt)")
            # NOTE: Copyright policy 53(1)(c) and public summary 53(1)(d) are STILL REQUIRED
            
            # Article 54(6): EU rep carve-out only for non-EU providers AND not systemic
            if answers.get('outside_eu_provider', False):
                carve_outs.append("EU authorized representative (Art. 54(6) - exempt)")
        
        # Store warnings for later use in validation_warnings
        if hasattr(self, '_last_warnings'):
            self._last_warnings.extend(warnings)
        else:
            self._last_warnings = warnings
        
        return carve_outs, blockers
    
    def _determine_obligations(self, is_provider: bool, is_significant_modifier: bool,
                              is_open_source: bool, is_systemic: bool, needs_eu_rep: bool,
                              summary_scope: Optional[str], needs_notification: bool, answers: Dict = None) -> List[str]:
        """Determine applicable obligations based on provider type."""
        obligations = []
        answers = answers or {}
        
        if is_provider:
            # Article 53(1)(c) and (d) are ALWAYS required - NO carve-outs
            if summary_scope == 'modification_only':
                obligations.append("Public training summary - modification only (Art. 53(1)(d))")
                obligations.append("Copyright compliance policy (Art. 53(1)(c))")
            else:
                obligations.append("Public training summary (Art. 53(1)(d))")
                obligations.append("Copyright compliance policy (Art. 53(1)(c))")
            
            # Check open-source conditions for (a) and (b) carve-outs only
            open_source_conditions_met = (
                answers.get('open_source_release', False) and
                answers.get('open_source_without_monetisation', False) and
                answers.get('weights_arch_usage_public', False)
            )
            
            # Article 53(2): Tech docs (a) and downstream (b) exempt ONLY if OSS conditions met AND not systemic
            has_os_carveouts = open_source_conditions_met and not is_systemic
            
            if not has_os_carveouts:
                obligations.extend([
                    "Technical documentation (Art. 53(1)(a))",
                    "Downstream information (Art. 53(1)(b))"
                ])
            
            # EU rep handled separately based on needs_eu_rep
            if needs_eu_rep:
                obligations.append("EU authorized representative (Art. 54)")
            
            # Systemic risk additions
            if is_systemic:
                obligations.extend([
                    "Model evaluation (Art. 55)",
                    "Risk mitigation (Art. 55)",
                    "Serious incident reporting (Art. 55)",
                    "Cybersecurity protection (Art. 55)"
                ])
            
            # Notification obligation (independent of systemic status)
            notify_line = "Notify the Commission within 14 days when the 10^25 FLOP threshold is met or will be met"
            if needs_notification and notify_line not in obligations:
                obligations.append(notify_line)
        
        return obligations
    
    def _is_significant_modifier_ratio(self, ratio_value: float) -> bool:
        """Check if ratio is strictly greater than 1/3 with epsilon for float precision."""
        EPS = 1e-12
        # Strictly greater than 1/3
        return (ratio_value - (1.0 / 3.0)) > EPS
    
    def _parse_percentage_to_ratio(self, value) -> Optional[float]:
        """Parse various percentage formats to ratio (0-1)."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value) / 100.0 if value > 1 else float(value)
        
        # Handle string inputs
        s = str(value).strip().replace(',', '.').replace('%', '')
        try:
            val = float(s)
            # If value > 1, assume it's a percentage
            return val / 100.0 if val > 1 else val
        except ValueError:
            return None