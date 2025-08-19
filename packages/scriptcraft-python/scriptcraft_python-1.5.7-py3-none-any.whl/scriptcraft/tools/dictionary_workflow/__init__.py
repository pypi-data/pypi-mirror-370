"""
📚 Dictionary Workflow Tool

A comprehensive tool that handles the complete dictionary enhancement workflow:
1. Prepare supplements (merge and clean)
2. Split supplements by domain
3. Enhance dictionaries with domain-specific supplements

This tool consolidates the functionality of the three separate enhancement packages
into a single, streamlined workflow.

Usage:
    Development: python -m scriptcraft.tools.dictionary_workflow.main [args]
    Distributable: python main.py [args]
    Pipeline: Called via main_runner(**kwargs)
"""

__version__ = "1.0.0"
__author__ = "ScriptCraft Team"
__description__ = "📚 Complete dictionary enhancement workflow tool"
__tags__ = ["tool", "dictionary", "workflow", "enhancement", "supplement", "domain"]

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .main import *
from .utils import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     'DictionaryWorkflow'
# ] 