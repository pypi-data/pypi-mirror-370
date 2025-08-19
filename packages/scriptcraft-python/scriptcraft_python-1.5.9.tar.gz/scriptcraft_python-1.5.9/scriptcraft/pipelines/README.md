# Pipeline Framework 🔄

A flexible pipeline framework for orchestrating QC steps, data processing, and validation workflows. This core infrastructure package provides the foundation for building and running complex data processing pipelines.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This framework was last updated on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📦 Project Structure

```
pipelines/
├── __init__.py         # Package interface and version info
├── base_pipeline.py    # Core pipeline implementation
├── pipeline_utils.py   # Helper functions and utilities
├── pipeline_steps.py   # Step definitions and factories
├── tests/             # Test suite
│   ├── __init__.py
│   ├── test_integration.py
│   └── test_pipeline.py
└── README.md         # This documentation
```

---

## 🚀 Usage

### Basic Pipeline Creation
```python
from scripts.pipelines.base_pipeline import BasePipeline
from scripts.pipelines.pipeline_utils import make_step

# Create a pipeline
pipeline = BasePipeline(
    name="Clinical QC",
    description="Validates clinical data quality"
)

# Add steps
pipeline.add_step(make_step(
    name="Dictionary Validation",
    log_filename="dict_validation.log",
    qc_func=validate_dictionary,
    input_key="raw_data",
    run_mode="domain"
))

# Run pipeline
pipeline.run()
```

### Pipeline with Multiple Domains
```python
# Run for all domains
pipeline.run()

# Run for specific domain
pipeline.run(domain="Clinical")

# Run steps with specific tag
pipeline.run(tag_filter="validation")
```

### Custom Step Creation
```python
def my_qc_func(domain, input_path, output_path, paths):
    # Custom QC logic here
    pass

pipeline.add_step(make_step(
    name="Custom Check",
    log_filename="custom.log",
    qc_func=my_qc_func,
    input_key="processed_data",
    output_filename="custom_results.xlsx",
    check_exists=True,
    run_mode="domain",
    tags=["validation", "custom"]
))
```

---

## ⚙️ Features

### Pipeline Management
- Flexible step configuration
- Domain-based or global execution
- Step tagging and filtering
- Progress tracking and timing
- Detailed logging

### Step Types
- Domain-specific steps
- Global steps
- Single-domain steps
- Custom execution steps

### Execution Modes
- `domain`: Run for each domain
- `single_domain`: Run for one domain
- `global`: Run once globally
- `custom`: Custom execution logic

### Utilities
- Step creation helpers
- Pipeline validation
- Path management
- Error handling
- Timing metrics

---

## 🔧 Development Guide

### Step Configuration
1. **Name**: Descriptive step name
2. **Log Filename**: Where to save logs
3. **QC Function**: The actual work function
4. **Input Key**: Data source identifier
5. **Output Filename**: (Optional) Result file
6. **Check Exists**: Validate input exists
7. **Run Mode**: Execution scope
8. **Tags**: For filtering/grouping

### Best Practices
- Use descriptive step names
- Implement proper error handling
- Add appropriate tags
- Keep steps focused
- Log important information
- Use appropriate run modes
- Validate inputs

### Common Patterns
```python
# Global preprocessing step
pipeline.add_step(make_step(
    name="Global Setup",
    log_filename="setup.log",
    qc_func=setup_func,
    input_key="global_data",
    run_mode="global"
))

# Domain-specific validation
pipeline.add_step(make_step(
    name="Domain Validation",
    log_filename="validation.log",
    qc_func=validate_func,
    input_key="raw_data",
    run_mode="domain"
))

# Final report generation
pipeline.add_step(make_step(
    name="Report Generation",
    log_filename="report.log",
    qc_func=report_func,
    input_key="processed_data",
    output_filename="final_report.xlsx",
    run_mode="single_domain"
))
```

---

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/pipelines/test_base_pipeline.py
python -m pytest tests/pipelines/test_pipeline_utils.py
```

### Integration Tests
```bash
python -m pytest tests/integration/pipelines/test_pipeline_integration.py
```

---

## 🔄 Dependencies

- Python >= 3.8
- common_utils
- typing_extensions
- pathlib
- logging

---

## 🚨 Error Handling

Common errors and solutions:

1. **Invalid Step Configuration**
   - Cause: Missing required parameters
   - Solution: Check step creation parameters

2. **Domain Not Found**
   - Cause: Invalid domain name
   - Solution: Verify domain configuration

3. **Input Path Missing**
   - Cause: Required input file not found
   - Solution: Check file paths and existence

4. **Mode Mismatch**
   - Cause: Wrong run_mode for input_key
   - Solution: Verify mode compatibility

---

## 📊 Performance

- Step execution is sequential
- Memory usage depends on step implementation
- Logging may impact disk space
- Consider chunking for large data
- Monitor step timings

---

## 📋 Development Checklist

### 1. File Structure ⬜
- [ ] Standard package layout
  - [ ] __init__.py with version info
  - [ ] base_pipeline.py for core functionality
  - [ ] pipeline_utils.py for helpers
  - [ ] pipeline_steps.py for step definitions
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
- [ ] Step management
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
   - Base pipeline class
   - Step management
   - Domain-based execution
   - Step tagging and filtering
   - Progress tracking

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
   - Add parallel execution support
   - Implement step dependencies
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
   - Add pipeline visualization
   - Improve error messages
   - Add configuration validation
   - Create interactive mode

#### Low Priority
6. **Feature Enhancements**
   - Create step templates
   - Add pipeline validation rules
   - Add progress reporting
   - Create summary reports

7. **Development Tools**
   - Add development utilities
   - Create debugging helpers
   - Add profiling support
   - Improve error messages

---

## 🤝 Contributing

1. Branch naming: `feature/pipeline-[feature]`
2. Required tests:
   - Unit tests for new features
   - Integration tests
3. Documentation:
   - Update README
   - Add docstrings
   - Document new features
4. Code review checklist in CONTRIBUTING.md 