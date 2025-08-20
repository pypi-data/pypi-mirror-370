"""
ScriptCraft Tools Package

This package contains all tools for data processing, validation, transformation, and automation.
Tools are organized by functionality but all accessible through a unified interface.

Example Usage:
    from scriptcraft.tools import (
        # All tools are now available
        RHQFormAutofiller, DataContentComparer, SchemaDetector, 
        DictionaryDrivenChecker, ReleaseConsistencyChecker, ScoreTotalsChecker,
        FeatureChangeChecker, DictionaryValidator, MedVisitIntegrityValidator,
        DictionaryCleaner, DateFormatStandardizer, AutomatedLabeler
    )

Tool Discovery:
    from scriptcraft.tools import get_available_tools, list_tools_by_category
    
    # Get all tools
    tools = get_available_tools()
    
    # Get tools by category
    validation_tools = list_tools_by_category("validation")
"""

# Import the unified registry system from the new registry package
from scriptcraft.common.registry import (
    get_available_tools,
    list_tools_by_category,
    discover_tool_metadata,
    registry
)

# Convenience function for backward compatibility
def get_tool_categories() -> list:
    """Get list of available tool categories."""
    return list(registry.get_tools_by_category().keys())

# Convenience function for running tools
def run_tool(tool_name: str, **kwargs) -> None:
    """Run a tool by name with the given arguments."""
    registry.run_tool(tool_name, **kwargs)

# === LAZY IMPORTS FOR ROBUSTNESS ===
# Import tools lazily to prevent one broken tool from breaking the entire package
def _lazy_import_tools():
    """Import tools lazily with error handling."""
    tools = {}
    
    # Define tool modules to import
    tool_modules = [
        ('rhq_form_autofiller', 'RHQFormAutofiller'),
        ('data_content_comparer', 'DataContentComparer'),
        ('schema_detector', 'SchemaDetector'),
        ('dictionary_driven_checker', 'DictionaryDrivenChecker'),
        ('score_totals_checker', 'ScoreTotalsChecker'),
        ('feature_change_checker', 'FeatureChangeChecker'),
        ('dictionary_validator', 'DictionaryValidator'),
        ('medvisit_integrity_validator', 'MedVisitIntegrityValidator'),
        ('dictionary_cleaner', 'DictionaryCleaner'),
        ('date_format_standardizer', 'DateFormatStandardizer'),
        ('automated_labeler', 'AutomatedLabeler'),
        ('dictionary_workflow', 'DictionaryWorkflow'),
    ]
    
    # Import each tool with error handling
    for module_name, class_name in tool_modules:
        try:
            module = __import__(f'.{module_name}', fromlist=[class_name], level=1)
            if hasattr(module, class_name):
                tools[class_name] = getattr(module, class_name)
                # Also add to globals for backward compatibility
                globals()[class_name] = getattr(module, class_name)
        except ImportError as e:
            # Log the error but don't fail the entire package
            import sys
            print(f"⚠️ Warning: Could not import {class_name} from {module_name}: {e}", file=sys.stderr)
        except Exception as e:
            # Log any other errors
            import sys
            print(f"⚠️ Warning: Error importing {class_name}: {e}", file=sys.stderr)
    
    return tools

# Import tools lazily (only when needed)
_available_tools = None

def _get_available_tools():
    """Get available tools, importing them lazily if needed."""
    global _available_tools
    if _available_tools is None:
        _available_tools = _lazy_import_tools()
    return _available_tools

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     'RHQFormAutofiller', 'DataContentComparer', 'SchemaDetector',
#     'DictionaryDrivenChecker', 'ReleaseConsistencyChecker', 'ScoreTotalsChecker',
#     'FeatureChangeChecker', 'DictionaryValidator', 'MedVisitIntegrityValidator',
#     'DictionaryCleaner', 'DateFormatStandardizer', 'AutomatedLabeler',
#     'DictionaryWorkflow',
#     'get_available_tools', 'list_tools_by_category', 'run_tool', 'discover_tool_metadata',
#     'get_tool_categories'
# ]
