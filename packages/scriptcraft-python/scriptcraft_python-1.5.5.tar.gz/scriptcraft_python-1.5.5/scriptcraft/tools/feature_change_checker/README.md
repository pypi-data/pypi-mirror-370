# Feature Change Checker 📊

A specialized checker that tracks and categorizes changes in feature values between visits, particularly useful for monitoring disease progression indicators.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This package was last updated on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📦 Project Structure

```
feature_change_checker/
├── __init__.py         # Package interface and version info
├── __main__.py         # CLI entry point
├── tool.py            # Core checker implementation
├── utils.py           # Helper functions
├── tests/             # Test suite
│   ├── __init__.py
│   └── test_feature_changes.py
└── README.md         # This documentation
```

---

## 🚀 Usage (Development)

### Command Line
```bash
python -m feature_change_checker --feature CDX_Cog --categorize --output_dir output/
```

### Python API
```python
from scripts.checkers.feature_change_checker import checker

# Configure the checker
checker.feature_name = "CDX_Cog"
checker.categorize = True

# Run the checker
checker.check(
    domain="Clinical",
    input_path="",  # Not used directly
    output_path="", # Not used directly
    paths={
        "merged_data": "path/to/merged/data",
        "qc_output": "path/to/output"
    }
)
```

Arguments:
- `feature`: Feature name to track changes for (default: CDX_Cog)
- `categorize`: Whether to categorize changes (default: True)
- `output_dir`: Output directory for results

---

## ⚙️ Features

- Track changes in feature values between visits
- Categorize changes into meaningful groups:
  - Normal progression
  - Fast progression
  - Undefined changes
  - Flagged changes
- Detailed change analysis
- Support for multiple visit sequences
- Configurable feature tracking
- CSV output format

---

## 🔧 Dev Tips

- Use meaningful feature names that exist in the dataset
- Consider data quality when interpreting changes
- Handle undefined values (99) appropriately
- Test with various progression patterns
- Monitor performance with large datasets

---

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/test_feature_changes.py
```

### Test Data
Example test files needed:
- Sample clinical data with multiple visits
- Data with various progression patterns
- Edge cases with undefined values

---

## 🔄 Dependencies

Required packages:
- pandas >= 1.3.0
- numpy >= 1.20.0
- Python >= 3.8

System requirements:
- Memory: 4GB minimum
- Storage: 1GB for large datasets
- CPU: Multi-core recommended for large datasets

---

## 🚨 Error Handling

Common errors and solutions:
1. Feature Not Found
   - Cause: Specified feature missing from dataset
   - Solution: Verify feature name and column existence
2. Invalid Visit Sequence
   - Cause: Missing or non-sequential visit IDs
   - Solution: Clean and validate visit data
3. Path Configuration
   - Cause: Missing required path settings
   - Solution: Provide all required paths in config

---

## 📊 Performance

Expectations:
- Processing speed: ~1-2 minutes per 100k rows
- Memory usage: ~500MB base + 100MB per 50k rows
- File size limits: Tested up to 1M rows

Optimization tips:
- Use CSV format for large files
- Monitor memory usage with large datasets
- Consider chunked processing for huge datasets

---

## 📋 Current Status and Future Improvements

### ✅ Completed Items
1. **File Structure**
   - Standard layout with all required files
   - Clean organization
   - Proper test directory structure

2. **Core Documentation**
   - Main README.md with key sections
   - Usage examples (CLI and API)
   - Basic error handling documentation
   - Build date placeholder

3. **Code Implementation**
   - Base class usage and inheritance
   - Standard CLI implementation
   - Basic error handling
   - Type hints in core files

### 🔄 Partially Complete
1. **Testing**
   - ✅ Basic unit tests
   - ❌ Need integration tests
   - ❌ Need performance tests
   - ❌ Need edge case coverage

2. **Error Handling**
   - ✅ Basic error patterns
   - ✅ Basic logging
   - ❌ Need standardized error codes
   - ❌ Need enhanced user messages

3. **Performance**
   - ✅ Basic guidelines
   - ❌ Need detailed resource usage docs
   - ❌ Need optimization guidelines
   - ❌ Need large file handling specs

### 🎯 Prioritized Improvements

#### High Priority
1. **Testing Enhancement**
   - Add integration test suite
   - Create edge case test data
   - Add performance test suite
   - Add test data examples

2. **Error Handling**
   - Implement standardized error codes
   - Enhance logging system
   - Add detailed error messages
   - Create error recovery procedures

3. **Performance Optimization**
   - Implement chunked processing
   - Add memory usage monitoring
   - Add progress reporting
   - Create performance benchmarks

#### Medium Priority
4. **Documentation**
   - Add API documentation
   - Create error code reference
   - Add troubleshooting guide
   - Document performance guidelines

5. **User Experience**
   - Add progress bars
   - Improve error messages
   - Add configuration validation
   - Create interactive mode

#### Low Priority
6. **Feature Enhancements**
   - Add custom categorization rules
   - Support multiple features
   - Add statistical analysis
   - Create summary reports

7. **Development Tools**
   - Add development scripts
   - Create test data generators
   - Add benchmark tools
   - Add code quality checks

---

## 🤝 Contributing

1. Branch naming: `feature/feature-checker-[name]`
2. Required for all changes:
   - Unit tests
   - Documentation updates
   - Checklist review
3. Code review process in CONTRIBUTING.md 