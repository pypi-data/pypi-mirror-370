"""
📚 Dictionary Validator Tool

Validates data dictionaries for completeness, consistency, and accuracy.
Ensures dictionary quality and compliance with standards.

Features:
- 📚 Dictionary validation
- 🔍 Completeness checking
- 📊 Consistency analysis
- 📋 Quality assessment
- 🔄 Standard compliance
- ⚠️ Error reporting

Author: ScriptCraft Team
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .main import *
from .utils import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     'DictionaryValidator'
# ]

# Tool metadata
__description__ = "📚 Validates data dictionaries for completeness, consistency, and accuracy"
__tags__ = ["dictionary", "validation", "quality", "compliance", "standards"]
__data_types__ = ["csv", "xlsx", "xls", "json"]
__domains__ = ["clinical", "biomarkers", "genomics", "imaging"]
__complexity__ = "moderate"
__maturity__ = "stable"
__distribution__ = "pipeline"
