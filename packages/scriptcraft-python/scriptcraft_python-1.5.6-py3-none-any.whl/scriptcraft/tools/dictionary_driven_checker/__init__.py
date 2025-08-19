"""
📚 Dictionary Driven Checker Tool

Validates data against predefined dictionaries and validation rules.
Supports multiple validation types and provides comprehensive reporting.

Features:
- 📚 Dictionary-based validation
- 🔍 Multiple validation types (numeric, text, date, pattern)
- 📊 Comprehensive validation reporting
- 🔄 Plugin-based validation system
- 📋 Detailed error tracking
- ⚠️ Data quality assessment

Author: ScriptCraft Team
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .main import *
from .utils import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     'DictionaryDrivenChecker'
# ]

# Tool metadata
__description__ = "📚 Validates data against predefined dictionaries and validation rules"
__tags__ = ["validation", "dictionary", "rules", "quality", "checking"]
__data_types__ = ["csv", "xlsx", "xls"]
__domains__ = ["clinical", "biomarkers", "genomics", "imaging"]
__complexity__ = "moderate"
__maturity__ = "stable"
__distribution__ = "pipeline"