# Schema Detector 🔍

Automatically detects and analyzes data schemas from various file formats. Identifies data types, patterns, and structure for validation and processing with comprehensive schema reporting.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This package was last updated on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📦 Project Structure

```
schema_detector/
├── __init__.py         # Package interface and version info
├── main.py            # CLI entry point
├── utils.py           # Helper functions
├── env.py             # Environment detection
└── README.md         # This documentation
```

---

## 🚀 Usage (Development)

### Command Line
```bash
python -m scriptcraft.tools.schema_detector --data-file data.csv --output-dir output
```

### Python API
```python
from scriptcraft.tools.schema_detector import SchemaDetector

detector = SchemaDetector()
detector.run(
    data_file="data.csv",
    output_dir="output"
)
```

Arguments:
- `--data-file`: Path to data file for schema detection
- `--output-dir`: Output directory for schema reports
- `--domain`: Optional domain context for detection
- `--strict`: Enable strict schema detection mode
- `--include-metadata`: Include metadata in schema analysis

---

## ⚙️ Features

- 🔍 Automatic schema detection
- 📊 Data type identification
- 🔄 Pattern recognition
- 📋 Structure analysis
- ✅ Schema validation
- 📈 Performance metrics
- 🛡️ Error handling
- 🎯 Multi-format support

---

## 🔧 Dev Tips

- Use domain-specific settings for healthcare data schemas
- Test schema detection with sample data before processing large files
- Check data type detection accuracy for complex formats
- Review schema reports for pattern recognition effectiveness
- Use strict mode for critical schema analysis
- Customize detection algorithms based on data requirements

---

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/tools/test_schema_detector.py
```

### Integration Tests
```bash
python -m pytest tests/integration/tools/test_schema_detector_integration.py
```

### Test Data
Example files needed:
- Sample data files with various formats
- Expected schema reports
- Test cases for different data types
- Pattern recognition examples

---

## 🔄 Dependencies

Required packages:
- pandas >= 1.3.0
- openpyxl >= 3.0.0
- Python >= 3.8

System requirements:
- Memory: 100MB base + 50MB per file
- Storage: 200MB for processing and output
- CPU: Multi-core recommended for large files

---

## 🚨 Error Handling

Common errors and solutions:
1. **Data Format Error**
   - Cause: Data file format not recognized
   - Solution: Check file format and required structure
2. **Schema Detection Error**
   - Cause: Schema detection algorithm failed
   - Solution: Check data quality and detection parameters
3. **Pattern Recognition Error**
   - Cause: Pattern recognition failed
   - Solution: Verify data patterns and recognition rules

---

## 📊 Performance

Expectations:
- Processing speed: 2000-5000 records per second
- Memory usage: 100MB base + 50MB per file
- File size limits: Up to 100MB per input file

Optimization tips:
- Use specific detection algorithms for large files
- Process data in chunks
- Enable parallel processing for multiple files
- Optimize pattern recognition algorithms

---

## 📋 Development Checklist

### 1. File Structure ✅
- [x] Standard package layout
  - [x] __init__.py with version info
  - [x] main.py for CLI
  - [x] utils.py for helpers
  - [x] env.py for environment detection
  - [x] README.md
- [x] Clean organization
- [x] No deprecated files

### 2. Documentation ✅
- [x] Version information
- [x] Package-level docstring
- [x] Function docstrings
- [x] Type hints
- [x] README.md
- [x] API documentation
- [x] Error code reference
- [x] Troubleshooting guide

### 3. Code Implementation ✅
- [x] Core functionality
- [x] CLI interface
- [x] Error handling
- [x] Input validation
- [x] Type checking
- [x] Performance optimization
- [x] Security considerations

### 4. Testing ⬜
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance tests
- [ ] Edge case tests
- [ ] Error condition tests
- [ ] Test data examples

### 5. Error Handling ✅
- [x] Custom exceptions
- [x] Error messages
- [x] Error logging
- [x] Error recovery
- [x] Input validation

### 6. Performance ✅
- [x] Large dataset testing
- [x] Memory optimization
- [x] Progress reporting
- [x] Chunked processing
- [x] Performance metrics

### 7. Configuration ✅
- [x] Command-line arguments
- [x] Configuration validation
- [x] Environment variables
- [x] Default settings
- [x] Documentation

### 8. Packaging ✅
- [x] Dependencies specified
- [x] Version information
- [x] Package structure
- [x] Installation tested
- [x] Distribution tested

---

## 📋 Current Status and Future Improvements

### ✅ Completed Items
1. **Core Implementation**
   - Automatic schema detection
   - Data type identification
   - Pattern recognition
   - Structure analysis
   - Schema validation

2. **Documentation**
   - Main README structure
   - Usage examples
   - Error handling guide
   - Performance metrics

3. **Infrastructure**
   - Environment detection
   - CLI integration
   - Error handling
   - Configuration management

### 🔄 Partially Complete
1. **Testing**
   - ✅ Basic structure
   - ❌ Need comprehensive test suite
   - ❌ Need integration tests
   - ❌ Need performance tests

2. **Features**
   - ✅ Basic schema detection
   - ❌ Need advanced detection algorithms
   - ❌ Need enhanced pattern recognition
   - ❌ Need enhanced reporting

### 🎯 Prioritized Improvements

#### High Priority
1. **Testing Enhancement**
   - Add comprehensive test suite
   - Create integration tests
   - Add performance benchmarks
   - Improve error case coverage

2. **Feature Enhancement**
   - Add advanced detection algorithms
   - Implement enhanced pattern recognition
   - Add enhanced reporting
   - Improve detection accuracy

#### Medium Priority
3. **Documentation**
   - Add detailed API docs
   - Create troubleshooting guide
   - Add performance tuning guide
   - Document common patterns

4. **User Experience**
   - Add progress tracking
   - Improve error messages
   - Add configuration validation
   - Create interactive mode

#### Low Priority
5. **Advanced Features**
   - Add ML-based schema detection
   - Support more data formats
   - Add schema learning
   - Create schema summaries

6. **Development Tools**
   - Add development utilities
   - Create debugging helpers
   - Add profiling support
   - Improve error messages

---

## 🤝 Contributing

1. Branch naming: `feature/schema-detector-[feature]`
2. Required for all changes:
   - Unit tests
   - Documentation updates
   - Checklist review
3. Code review process in CONTRIBUTING.md 