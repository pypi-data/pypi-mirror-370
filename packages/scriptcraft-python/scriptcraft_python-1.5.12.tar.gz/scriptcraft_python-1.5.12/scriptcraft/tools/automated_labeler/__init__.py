"""
🏷️ Automated Labeler Tool

Automatically generates labels and annotations for datasets.
Supports various labeling strategies and quality control measures.

Features:
- 🏷️ Automatic label generation
- 📊 Label quality assessment
- 📋 Annotation management
- 🔍 Quality control
- 🔄 Batch processing
- ⚠️ Error reporting

Author: ScriptCraft Team
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .main import *
from .utils import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     'AutomatedLabeler'
# ]

# Tool metadata
__description__ = "🏷️ Automatically generates labels and annotations for datasets"
__tags__ = ["labeling", "automation", "annotations", "quality", "processing"]
__data_types__ = ["csv", "xlsx", "xls"]
__domains__ = ["clinical", "biomarkers", "genomics", "imaging"]
__complexity__ = "moderate"
__maturity__ = "stable"
__distribution__ = "standalone"
