"""
🔍 Schema Detector Tool

Automatically detects and analyzes data schemas from various file formats.
Provides schema validation, comparison, and documentation capabilities.

Features:
- 🔍 Automatic schema detection
- 📊 Schema analysis and validation
- 📋 Schema documentation generation
- 🔄 Schema comparison tools
- 📈 Statistical schema insights
- ⚠️ Schema inconsistency detection

Author: ScriptCraft Team
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .main import *
from .utils import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     'SchemaDetectorTool'
# ]

# Tool metadata
__description__ = "🔍 Automatically detects and analyzes data schemas from various file formats"
__tags__ = ["schema", "detection", "validation", "analysis", "documentation"]
__data_types__ = ["csv", "xlsx", "xls", "json"]
__domains__ = ["clinical", "biomarkers", "genomics", "imaging"]
__complexity__ = "moderate"
__maturity__ = "stable"
__distribution__ = "standalone" 