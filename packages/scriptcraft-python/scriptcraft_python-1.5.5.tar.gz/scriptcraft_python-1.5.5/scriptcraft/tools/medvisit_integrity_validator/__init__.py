"""
🏥 MedVisit Integrity Validator Tool

Validates medical visit data for integrity, consistency, and completeness.
Ensures visit data quality and compliance with medical standards.

Features:
- 🏥 Medical visit validation
- 🔍 Data integrity checking
- 📊 Consistency analysis
- 📋 Completeness assessment
- 🔄 Medical standard compliance
- ⚠️ Error reporting

Author: ScriptCraft Team
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .main import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     'MedVisitIntegrityValidator'
# ]

# Tool metadata
__description__ = "🏥 Validates medical visit data for integrity, consistency, and completeness"
__tags__ = ["medical", "visits", "validation", "integrity", "compliance"]
__data_types__ = ["csv", "xlsx", "xls"]
__domains__ = ["clinical", "biomarkers", "genomics", "imaging"]
__complexity__ = "moderate"
__maturity__ = "stable"
__distribution__ = "pipeline"
