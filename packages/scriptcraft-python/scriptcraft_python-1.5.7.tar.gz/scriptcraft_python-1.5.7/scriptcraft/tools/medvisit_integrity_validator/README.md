# MedVisit Integrity Validator 🏥

A validator tool for ensuring the integrity and consistency of medical visit data across various formats and sources.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This tool was last updated on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📦 Project Structure

```
medvisit_integrity_validator/
├── __init__.py         # Package interface and version info
├── __main__.py         # CLI entry point
├── validator.py        # Core implementation
├── utils.py           # Helper functions
├── rules/             # Validation rules
│   ├── __init__.py
│   ├── base_rules.py
│   └── custom_rules.py
├── tests/             # Test suite
│   ├── __init__.py
│   ├── test_integration.py
│   └── test_validator.py
└── README.md         # This documentation
```

---

## 🚀 Usage (Development)

### Command Line
```bash
python -m scripts.validators.medvisit_integrity_validator visits.csv --rules standard
```

### Python API
```python
from scripts.validators.medvisit_integrity_validator.validator import MedVisitValidator

validator = MedVisitValidator()
validator.run(
    input_path="visits.csv",
    rules="standard",
    output_dir="output/validation"
)
```

Arguments:
- `input_path`: Path to visit data
- `rules`: Rule set to apply
- `output_dir`: Output directory

---

## ⚙️ Features

- Data integrity checks
- Format validation
- Cross-reference validation
- Temporal consistency
- Relationship checks
- Error reporting
- Batch processing

---

## 🔧 Dev Tips

- Test with sample data
- Handle edge cases
- Document rules
- Validate outputs
- Monitor performance
- Version rules

---

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/validators/test_medvisit_integrity_validator.py
```

### Integration Tests
```bash
python -m pytest tests/integration/validators/test_medvisit_integrity_validator_integration.py
```

### Test Data
Example files in `tests/data/validators/medvisit_integrity_validator/`:
- `sample_visits.csv`
- `expected_validation.json`
- `custom_rules.py`

---

## 🔄 Dependencies

- pandas >= 1.3.0
- numpy >= 1.20.0
- jsonschema >= 3.2.0
- Python >= 3.8
- common.base.BaseValidator

---

## 🚨 Error Handling

Common errors and solutions:
1. Invalid Data
   - Cause: Malformed visit data
   - Solution: Check data format
2. Rule Error
   - Cause: Invalid rule definition
   - Solution: Validate rule syntax
3. Reference Error
   - Cause: Missing references
   - Solution: Check dependencies

---

## 📊 Performance

- Processing speed depends on:
  - Number of visits
  - Rule complexity
  - Data relationships
- Memory usage:
  - Base: ~100MB
  - Per file: Size * 1.5
- Optimization tips:
  - Batch process
  - Optimize rules
  - Use indexing

---

## 📋 Development Checklist

### 1. File Structure ⬜
- [ ] Standard package layout
  - [ ] __init__.py with version info
  - [ ] __main__.py for CLI
  - [ ] validator.py for core functionality
  - [ ] utils.py for helpers
  - [ ] tests/ directory
  - [ ] README.md
- [ ] Clean organization
- [ ] No deprecated files

### 2. Documentation ⬜
- [ ] Version information
- [ ] Package-level docstring
- [ ] Function docstrings
- [ ] Type hints
- [ ] README.md
- [ ] API documentation
- [ ] Error code reference
- [ ] Troubleshooting guide

### 3. Code Implementation ⬜
- [ ] Core functionality
- [ ] CLI interface
- [ ] Error handling
- [ ] Input validation
- [ ] Type checking
- [ ] Performance optimization
- [ ] Security considerations

### 4. Testing ⬜
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance tests
- [ ] Edge case tests
- [ ] Error condition tests
- [ ] Test data examples

### 5. Error Handling ⬜
- [ ] Custom exceptions
- [ ] Error messages
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
- [ ] Configuration validation
- [ ] Environment variables
- [ ] Default settings
- [ ] Documentation

### 8. Packaging ⬜
- [ ] Dependencies specified
- [ ] Version information
- [ ] Package structure
- [ ] Installation tested
- [ ] Distribution tested

---

## 📋 Current Status and Future Improvements

### ✅ Completed Items
1. **Core Implementation**
   - Base validator class integration
   - Data integrity checks
   - Format validation
   - Cross-reference validation
   - Temporal consistency

2. **Documentation**
   - Main README structure
   - Usage examples
   - Error handling guide
   - Performance metrics

3. **Testing**
   - Basic unit test structure
   - Test data organization
   - Sample test cases
   - Error case testing

### 🔄 Partially Complete
1. **Error Handling**
   - ✅ Basic error types defined
   - ✅ Error messages implemented
   - ❌ Need automatic recovery
   - ❌ Need state preservation

2. **Performance**
   - ✅ Basic metrics documented
   - ✅ Memory usage guidelines
   - ❌ Need parallel processing
   - ❌ Need chunked operations

3. **Testing**
   - ✅ Unit tests
   - ✅ Basic integration
   - ❌ Need performance tests
   - ❌ Need stress testing

### 🎯 Prioritized Improvements

#### High Priority
1. **Error Recovery**
   - Implement automatic recovery
   - Add state preservation
   - Enhance error reporting
   - Add rollback capability

2. **Performance Optimization**
   - Add parallel processing
   - Implement chunked operations
   - Add memory optimization
   - Improve large file handling

3. **Testing Enhancement**
   - Add performance test suite
   - Create stress tests
   - Add edge case coverage
   - Improve test data

#### Medium Priority
4. **Documentation**
   - Add detailed API docs
   - Create troubleshooting guide
   - Add performance tuning guide
   - Document common patterns

5. **User Experience**
   - Add progress tracking
   - Improve error messages
   - Add configuration validation
   - Create interactive mode

#### Low Priority
6. **Feature Enhancements**
   - Add more validation rules
   - Support more formats
   - Add rule editor
   - Create summary reports

7. **Development Tools**
   - Add development utilities
   - Create debugging helpers
   - Add profiling support
   - Improve error messages

---

## 🤝 Contributing

1. Branch naming: `feature/validator-[feature]`
2. Required tests:
   - Unit tests for rules
   - Integration tests
3. Documentation:
   - Update README
   - Document rules
   - Update patterns
4. Code review checklist in CONTRIBUTING.md 