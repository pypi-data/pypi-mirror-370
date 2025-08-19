"""
🔄 Feature Change Checker Tool

Tracks changes in features/columns across different datasets or time periods.
Identifies feature additions, removals, and modifications.

Features:
- 🔄 Feature change tracking
- 📊 Change analysis and reporting
- 📋 Feature comparison
- 🔍 Modification detection
- 📈 Statistical summaries
- ⚠️ Change notification

Author: ScriptCraft Team
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .main import *
from .utils import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     'FeatureChangeChecker'
# ]

# Tool metadata
__description__ = "🔄 Tracks changes in features/columns across different datasets or time periods"
__tags__ = ["features", "changes", "tracking", "comparison", "analysis"]
__data_types__ = ["csv", "xlsx", "xls"]
__domains__ = ["clinical", "biomarkers", "genomics", "imaging"]
__complexity__ = "moderate"
__maturity__ = "stable"
__distribution__ = "pipeline"
