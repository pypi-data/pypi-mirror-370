# ScriptCraft Unified Plugin System

This directory provides a centralized, DRY plugin system for all ScriptCraft tools, validators, and pipeline steps.

## Features
- Unified registry for all plugin types (validators, tools, pipeline steps)
- Decorators for easy registration: `@register_validator`, `@register_tool`, `@register_pipeline_step`
- Automatic plugin discovery and loading
- Plugin metadata management
- Backward compatibility for legacy plugins

## How to Create a Plugin

1. **Inherit from `PluginBase` (or a relevant base, e.g., `ColumnValidator`)**
2. **Implement required methods** (e.g., `get_plugin_type`, `validate_value`, `run`, etc.)
3. **Register your plugin** using the appropriate decorator:
   - `@register_validator('name')` for validator plugins
   - `@register_tool('name')` for tool plugins
   - `@register_pipeline_step('name')` for pipeline step plugins

### Example: Validator Plugin
```python
from scriptcraft.common.plugins import register_validator
from scriptcraft.common.data.validation import ColumnValidator

@register_validator('date')
class DateValidator(ColumnValidator):
    """Validates date formats and ranges."""
    def validate_value(self, value, expected_values):
        # Validation logic here
        pass
```

### Example: Tool Plugin
```python
from scriptcraft.common.plugins import register_tool
from .main import MyTool

@register_tool('my_tool', description='My custom tool')
class MyToolPlugin(MyTool):
    pass
```

### Example: Pipeline Step Plugin
```python
from scriptcraft.common.plugins import register_pipeline_step

@register_pipeline_step('my_step')
def my_pipeline_step(...):
    # Step logic here
    pass
```

## How to Discover and Load Plugins

- The registry can automatically discover plugins in standard directories:
  - `plugins/validators/` for validator plugins
  - `plugins/tools/` for tool plugins
  - `plugins/pipeline/` for pipeline step plugins
- Use `registry.discover_plugins(base_path)` to auto-load plugins from these directories.

## Best Practices
- Use clear, descriptive names for plugins
- Add docstrings to all plugin classes/functions
- Register plugins with the appropriate decorator
- Keep plugin logic modular and focused
- Use metadata for discoverability and documentation
- Write tests for each plugin

## Backward Compatibility
- Legacy plugins using the old `PluginRegistry` are still supported, but new plugins should use the unified system.

## See Also
- `common/plugins/__init__.py` for the full registry implementation
- `common/data/validation.py` for validator plugin base classes
- Example plugins in `tools/dictionary_driven_checker/plugins/validators.py` 