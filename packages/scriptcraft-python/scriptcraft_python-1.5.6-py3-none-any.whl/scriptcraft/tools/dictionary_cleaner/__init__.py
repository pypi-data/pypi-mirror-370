"""
🧹 Dictionary Cleaner Tool

Cleans and standardizes data dictionaries for consistency and quality.
Removes duplicates, standardizes formats, and ensures dictionary integrity.

Features:
- 🧹 Dictionary cleaning and standardization
- 🔍 Duplicate removal
- 📊 Format standardization
- 📋 Quality improvement
- 🔄 Consistency enforcement
- ⚠️ Error reporting

Author: ScriptCraft Team
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .main import *
from .utils import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     'DictionaryCleaner'
# ]

# Tool metadata
__description__ = "🧹 Cleans and standardizes data dictionaries for consistency and quality"
__tags__ = ["dictionary", "cleaning", "standardization", "quality", "consistency"]
__data_types__ = ["csv", "xlsx", "xls", "json"]
__domains__ = ["clinical", "biomarkers", "genomics", "imaging"]
__complexity__ = "moderate"
__maturity__ = "stable"
__distribution__ = "pipeline"
