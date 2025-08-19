# Dictionary Driven Checker Plugins 🔌

This directory contains the plugin system for the Dictionary Driven Checker. Each plugin provides specific validation capabilities that can be combined and configured as needed.

## Core Plugins

### 1. Numeric Validator (`numeric_plugin.py`)
- Range validation
- Outlier detection
- Statistical checks
- Missing value handling

### 2. Date Validator (`date_plugin.py`)
- Format validation
- Range checks
- Missing date handling
- Date sequence validation

### 3. Text Validator (`text_plugin.py`)
- Pattern matching
- Length validation
- Character set checks
- Missing text handling

## Creating New Plugins

1. Create a new file in this directory
2. Inherit from `validators.BaseValidator`
3. Implement required methods:
   - `validate()`
   - `setup()` (optional)
   - `cleanup()` (optional)
4. Register in `__init__.py`

### Example Plugin Template
```python
from .validators import BaseValidator

class CustomValidator(BaseValidator):
    """Custom validator description."""
    
    def setup(self, config):
        """Optional setup method."""
        pass
        
    def validate(self, data, config):
        """Required validation method."""
        # Implementation here
        pass
        
    def cleanup(self):
        """Optional cleanup method."""
        pass
```

## Plugin Guidelines

### Performance
- Implement chunked processing for large datasets
- Use numpy operations where possible
- Cache repeated calculations
- Clean up resources in `cleanup()`

### Error Handling
- Use standard error codes from `common.errors`
- Provide detailed error messages
- Handle edge cases gracefully
- Log validation steps

### Testing
- Add unit tests in `tests/plugins/`
- Include performance tests
- Test with various data sizes
- Test edge cases

## Plugin Registry

The plugin registry (`__init__.py`) manages plugin loading and registration. To register a new plugin:

```python
from .custom_plugin import CustomValidator

registry.register_plugin('custom', CustomValidator)
```

## Utilities

Common utilities for plugins are available in `validator_utils.py`:
- Data type conversion
- Missing value handling
- Range checking
- Format validation 