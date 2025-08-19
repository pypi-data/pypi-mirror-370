"""
📊 Score Totals Checker Tool

Validates score calculations and totals in datasets to ensure accuracy.
Checks for mathematical consistency and identifies calculation errors.

Features:
- 📊 Score validation and verification
- 🔢 Mathematical consistency checking
- 📋 Calculation error detection
- 🔍 Total verification
- 📈 Statistical analysis
- ⚠️ Error reporting

Author: ScriptCraft Team
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .main import *
from .utils import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     'ScoreTotalsChecker'
# ]

# Tool metadata
__description__ = "📊 Validates score calculations and totals in datasets to ensure accuracy"
__tags__ = ["scores", "totals", "validation", "calculations", "mathematics"]
__data_types__ = ["csv", "xlsx", "xls"]
__domains__ = ["clinical", "biomarkers", "genomics", "imaging"]
__complexity__ = "moderate"
__maturity__ = "stable"
__distribution__ = "pipeline"
