# Dictionary Driven Checker 📚

A flexible checker package that validates data against a data dictionary using a plugin-based architecture. Supports custom validation rules and outlier detection methods.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This checker was last updated on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📦 Project Structure

```
dictionary_driven_checker/
├── __init__.py         # Package interface and version info
├── __main__.py        # CLI entry point
├── tool.py            # Core checker implementation
├── utils.py           # Helper functions
├── tests/             # Test suite
│   ├── __init__.py
│   ├── test_integration.py
│   ├── test_numeric_validator.py
│   ├── test_date_validator.py
│   └── test_text_validator.py
├── plugins/           # Validation plugins
│   ├── __init__.py    # Plugin registry
│   ├── validators.py  # Base validator classes
│   ├── validator_utils.py  # Shared utilities
│   ├── date_plugin.py     # Date validation
│   ├── numeric_plugin.py  # Numeric validation
│   └── text_plugin.py     # Text validation
└── README.md         # This documentation
```

---

## 🚀 Usage (Development)

### Command Line
```bash
python -m checkers.dictionary_driven_checker.main \
    --data data.xlsx \
    --dict dictionary.csv \
    --domain Clinical \
    --config config.yaml
```

### Python API
```python
from scripts.checkers.dictionary_driven_checker.main import DictionaryDrivenChecker

checker = DictionaryDrivenChecker()
checker.check(
    domain="Clinical",
    input_path="data.xlsx",
    output_path="validation_results.csv",
    paths={"config": "config.yaml"}
)
```

Arguments:
- `data`: Path to data file (.xlsx or .csv)
- `dict`: Path to dictionary file (.csv)
- `domain`: Domain name (e.g., Clinical, Biomarkers)
- `config`: Optional path to config file

---

## ⚙️ Features

- Plugin-based validation architecture
- Multiple outlier detection methods
- Configurable validation rules
- Support for custom validators
- Detailed validation reporting
- Column name normalization
- Flexible data format support
- Domain-specific validation

## 🔌 Plugin System

### Core Plugins
1. **Numeric Validator** (`numeric_plugin.py`)
   - Range validation
   - Outlier detection
   - Statistical checks
   - Missing value handling

2. **Date Validator** (`date_plugin.py`)
   - Format validation
   - Range checks
   - Missing date handling
   - Date sequence validation

3. **Text Validator** (`text_plugin.py`)
   - Pattern matching
   - Length validation
   - Character set checks
   - Missing text handling

### Creating New Plugins
To create a new validator plugin:
1. Create new file in `plugins/`
2. Inherit from `validators.BaseValidator`
3. Implement required methods
4. Register in `plugins/__init__.py`

Example:
```python
from .validators import BaseValidator

class CustomValidator(BaseValidator):
    def validate(self, data, config):
        # Implementation here
        pass
```

---

## 🔧 Dev Tips

- Create new validators in plugins/validators/
- Register plugins in registry.py
- Use config.yaml for validation settings
- Enable debug logging for development
- Test new validators thoroughly
- Handle edge cases in data

---

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/checkers/test_dictionary_driven.py
```

### Integration Tests
```bash
python -m pytest tests/integration/checkers/test_dictionary_driven_integration.py
```

### Plugin Tests
```bash
python -m pytest tests/checkers/test_dictionary_plugins.py
```

### Test Data
Example files in `tests/data/checkers/dictionary_driven/`:
- `sample_data.xlsx`
- `sample_dictionary.csv`
- `test_config.yaml`

---

## 🔄 Dependencies

Required packages:
- pandas >= 1.3.0
- numpy >= 1.20.0
- PyYAML >= 5.4.1
- Python >= 3.8
- common.base.BaseChecker
- common_utils

System requirements:
- Memory: 300MB base + 20MB per validator
- Storage: 1GB for large datasets
- CPU: Multi-core recommended

---

## 🚨 Error Handling

Common errors and solutions:
1. Dictionary Not Found
   - Cause: Missing or misnamed dictionary file
   - Solution: Check file naming convention
2. Invalid Plugin
   - Cause: Plugin registration failed
   - Solution: Verify plugin implementation
3. Configuration Error
   - Cause: Missing or invalid config
   - Solution: Check config.yaml format

---

## 📊 Performance

Expectations:
- Processing speed:
  - Small files (<100 columns): < 2 seconds
  - Large files (>500 columns): 10-30 seconds
- Memory usage:
  - Base: ~300MB
  - Per validator: +20MB
  - Per 100k rows: +100MB
- File size limits: Tested up to 1M rows

Optimization tips:
- Disable unused validators
- Use CSV for large files
- Enable chunked processing
- Clean up validators after use

---

## 📋 Development Checklist

### 1. File Structure ⬜
- [ ] Standard package layout
  - [ ] __init__.py with version info
  - [ ] __main__.py for CLI
  - [ ] tool.py for core functionality
  - [ ] utils.py for helpers
  - [ ] tests/ directory
  - [ ] README.md
- [ ] Plugin directory structure
- [ ] Clean organization

### 2. Documentation ⬜
- [ ] Version information
- [ ] Package-level docstring
- [ ] Function docstrings
- [ ] Type hints
- [ ] README.md
- [ ] Plugin documentation
- [ ] Error code reference
- [ ] Troubleshooting guide

### 3. Code Implementation ⬜
- [ ] Core functionality
- [ ] Plugin architecture
- [ ] Error handling
- [ ] Input validation
- [ ] Type checking
- [ ] Performance optimization
- [ ] Security considerations

### 4. Testing ⬜
- [ ] Unit tests
- [ ] Integration tests
- [ ] Plugin tests
- [ ] Performance tests
- [ ] Edge case tests
- [ ] Test data examples

### 5. Error Handling ⬜
- [ ] Custom exceptions
- [ ] Plugin error handling
- [ ] Error logging
- [ ] Error recovery
- [ ] Input validation

### 6. Performance ⬜
- [ ] Large dataset testing
- [ ] Memory optimization
- [ ] Progress reporting
- [ ] Chunked processing
- [ ] Performance metrics

### 7. Configuration ⬜
- [ ] Command-line arguments
- [ ] Plugin configuration
- [ ] Environment variables
- [ ] Default settings
- [ ] Documentation

### 8. Packaging ⬜
- [ ] Dependencies specified
- [ ] Version information
- [ ] Package structure
- [ ] Installation tested
- [ ] Plugin distribution

---

## 📋 Current Status and Future Improvements

### ✅ Completed Items
1. **File Structure**
   - Standard layout with all required files
   - Plugin architecture implemented
   - Clean organization
   - Proper test directory structure

2. **Core Documentation**
   - Main README.md with key sections
   - Usage examples (CLI and API)
   - Plugin documentation
   - Build date placeholder

3. **Plugin System**
   - Base validator class
   - Plugin registration
   - Core plugins implemented
   - Plugin utilities

### 🔄 Partially Complete
1. **Testing**
   - ✅ Basic unit tests
   - ✅ Plugin tests
   - ❌ Need integration tests
   - ❌ Need performance tests

2. **Error Handling**
   - ✅ Basic error types
   - ✅ Plugin errors
   - ❌ Need standardized codes
   - ❌ Need recovery procedures

3. **Performance**
   - ✅ Basic optimization
   - ✅ Memory guidelines
   - ❌ Need parallel processing
   - ❌ Need caching system

### 🎯 Prioritized Improvements

#### High Priority
1. **Testing Enhancement**
   - Add integration test suite
   - Create performance tests
   - Add plugin stress tests
   - Improve test coverage

2. **Error System**
   - Implement error codes
   - Add recovery procedures
   - Enhance plugin errors
   - Improve reporting

3. **Performance**
   - Add parallel validation
   - Implement caching
   - Optimize memory usage
   - Add progress tracking

#### Medium Priority
4. **Documentation**
   - Add API reference
   - Create plugin guide
   - Add troubleshooting
   - Document patterns

5. **Plugin System**
   - Add plugin templates
   - Create plugin tools
   - Add validation helpers
   - Improve registration

#### Low Priority
6. **Features**
   - Add ML validators
   - Support regex patterns
   - Create validator GUI
   - Add visualization

7. **Development**
   - Add dev utilities
   - Create debug tools
   - Add profiling
   - Improve feedback

---

## 🤝 Contributing

1. Branch naming: `feature/dict-checker-[name]`
2. Required for all changes:
   - Unit tests
   - Plugin tests if applicable
   - Documentation updates
   - Checklist review
3. Code review process in CONTRIBUTING.md

### Plugin Development
1. Follow plugin template in `plugins/example_plugin.py`
2. Add tests in `tests/plugins/`
3. Update plugin registry
4. Document in this README
5. Include performance considerations