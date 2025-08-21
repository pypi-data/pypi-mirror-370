"""
EU AI Act compliance constants for easy configuration updates.
These values can be adjusted if guidance changes.
"""

from datetime import date

# AI Office Template Requirements
UPDATE_CADENCE_DAYS = 182  # 6 months per AI Office template
DOMAIN_PERCENTAGE_STANDARD = 10.0  # Top 10% of domains by bytes
DOMAIN_PERCENTAGE_SME = 5.0  # Top 5% for SMEs
SME_DOMAIN_CAP = 1000  # Max domains for SME disclosure

# GPAI and Systemic Risk Thresholds
GPAI_PRESUMPTION_THRESHOLD = 1e23  # Typical GPAI compute (guidance only, not dispositive)
SYSTEMIC_RISK_THRESHOLD = 1e25  # Article 51(2)(b) threshold (≥10^25 FLOPs)

# Template Versioning
AI_OFFICE_TEMPLATE_ID = "EU_AI_Office_Public_Summary_Template_v1.0_July2025"
AI_OFFICE_TEMPLATE_SHA256 = "3b4c5d6e7f8a9b0c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z4"
TEMPLATE_VERSION = "1.0.0"
GENERATOR_VERSION = "1.0.0"

# Important Dates (Article 113)
GPAI_APPLICABILITY_DATE = date(2025, 8, 2)  # When GPAI rules apply
ENFORCEMENT_DATE = date(2026, 8, 2)  # When fines become enforceable
GRACE_PERIOD_END = date(2027, 8, 2)  # End of 2-year grace for pre-existing models

# Notification Requirements
THRESHOLD_NOTIFICATION_DAYS = 14  # Days to notify Commission when ≥10^25 FLOPs

# Legal Disclaimers
ADVISORY_DISCLAIMER = "This tool provides informational guidance only and is not legal advice. Consult qualified legal counsel for your specific situation."
PRIVACY_NOTICE = "No raw text or training data is stored or transmitted. Only statistical metadata is processed."

# Modification Thresholds
SIGNIFICANT_MODIFICATION_RATIO = 1.0 / 3.0  # >33% compute makes you a significant modifier

# S3 Configuration
TEMP_FILE_TTL_HOURS = 1  # Auto-delete temp files after 1 hour
IMMUTABLE_RETENTION_YEARS = 7  # Object Lock retention period