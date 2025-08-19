# Data Content Comparer 🔍

Compare data files to identify differences, changes, and inconsistencies. Perfect for validating data updates and ensuring data consistency across different versions or releases.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This package was last updated on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📦 Project Structure

```
data_content_comparer/
├── __init__.py         # Package interface and version info
├── main.py            # CLI entry point
├── utils.py           # Helper functions
├── env.py             # Environment detection
├── plugins/           # Comparison plugins
│   ├── __init__.py    # Plugin registry
│   ├── standard_mode.py
│   ├── rhq_mode.py
│   ├── domain_old_vs_new_mode.py
│   └── release_consistency_mode.py
└── README.md         # This documentation
```

---

## 🚀 Usage Examples

### Command Line Usage

#### 1. All Domains Comparison (Recommended)
Compare all available domains in one run:

```bash
# Compare all domains (Biomarkers, Clinical, Genomics, Imaging)
python -m implementations.python-package.scriptcraft.tools.data_content_comparer.main --mode release_consistency
```

#### 2. Individual Domain Comparison
Compare specific domains:

```bash
# Compare Clinical domain
python -m implementations.python-package.scriptcraft.tools.data_content_comparer.main --mode release_consistency --domain Clinical

# Compare Biomarkers domain
python -m implementations.python-package.scriptcraft.tools.data_content_comparer.main --mode release_consistency --domain Biomarkers

# Compare Genomics domain
python -m implementations.python-package.scriptcraft.tools.data_content_comparer.main --mode release_consistency --domain Genomics

# Compare Imaging domain
python -m implementations.python-package.scriptcraft.tools.data_content_comparer.main --mode release_consistency --domain Imaging
```

#### 3. Manual File Comparison
Compare specific files you place in the input directory:

```bash
# Basic manual file comparison
python -m implementations.python-package.scriptcraft.tools.data_content_comparer.main --mode release_consistency --input-paths data/input/file1.csv data/input/file2.csv

# With custom output directory
python -m implementations.python-package.scriptcraft.tools.data_content_comparer.main --mode release_consistency --input-paths data/input/old_data.csv data/input/new_data.csv --output-dir data/output
```

#### 4. Pipeline Mode (Using run_all.py)
Use the pipeline system for orchestrated workflows:

```bash
# Run via pipeline system
python run_all.py --tool data_content_comparer --mode release_consistency --domain Clinical

# Run with pipeline configuration
python run_all.py --pipeline release_management
```

#### 5. Other Comparison Modes

```bash
# Standard comparison mode
python -m implementations.python-package.scriptcraft.tools.data_content_comparer.main --mode standard --input-paths file1.csv file2.csv

# RHQ mode for residential history forms
python -m implementations.python-package.scriptcraft.tools.data_content_comparer.main --mode rhq_mode --input-paths rhq_old.xlsx rhq_new.xlsx

# Domain old vs new mode
python -m implementations.python-package.scriptcraft.tools.data_content_comparer.main --mode domain_old_vs_new --domain Clinical
```

### Python API Usage

```python
from implementations.python-package.scriptcraft.tools.data_content_comparer.main import DataContentComparer

# Create tool instance
comparer = DataContentComparer()

# All domains comparison
comparer.run(
    mode="release_consistency"
)

# Individual domain comparison
comparer.run(
    mode="release_consistency",
    domain="Clinical"
)

# Manual file comparison
comparer.run(
    mode="release_consistency",
    input_paths=["data/input/old_data.csv", "data/input/new_data.csv"]
)

# With additional options
comparer.run(
    mode="release_consistency",
    domain="Biomarkers",
    output_dir="data/output",
    output_filename="biomarkers_comparison.xlsx"
)
```

### Available Modes

- **`standard`**: Basic file-to-file comparison
- **`rhq_mode`**: Specialized for RHQ residential history forms
- **`domain_old_vs_new`**: Domain-specific old vs new comparison
- **`release_consistency`**: Release-to-release comparison (R5 vs R6)
- **`release`**: Alias for release_consistency mode

### Arguments

- `--mode`: Comparison mode (required)
- `--input-paths`: List of files to compare (for manual mode)
- `--output-dir`: Output directory for comparison reports
- `--domain`: Domain name (e.g., "Clinical", "Biomarkers")
- `--output-filename`: Custom output filename
- `--debug`: Enable debug mode for detailed logging

---

## ⚙️ Features

- 🔍 **Dynamic Release Comparison** - Automatically extracts release numbers from filenames (e.g., "Release_6 vs Release_7")
- 📊 **Multi-Domain Support** - Process all domains (Biomarkers, Clinical, Genomics, Imaging) in one run
- 🔄 **Plugin-based Architecture** - Extensible comparison modes (standard, rhq_mode, release_consistency)
- 📋 **Comprehensive Reports** - Detailed change detection with filtered results
- 🛡️ **Config-Driven** - Uses centralized config.yaml for all settings
- 📈 **Performance Optimized** - Handles large datasets efficiently
- 🎯 **Domain-Specific Configurations** - Tailored settings for each domain
- 📊 **Column Change Analysis** - Tracks added/removed columns between releases
- 🌐 **Flexible Input** - Supports both domain-based and manual file comparison
- 📝 **Comprehensive Logging** - Both console and file logging with timestamps
- 🎨 **Emoji-Enhanced Output** - Clear, readable status messages

---

## 🔧 Dev Tips

- Use domain-specific comparison modes for healthcare data
- Test comparison logic with sample data before processing large files
- Check data format compatibility between old and new files
- Review comparison reports for accuracy and completeness
- Use strict mode for critical data validation
- Customize comparison thresholds based on requirements
- Enable debug mode for detailed dtype and processing information
- Use the appropriate mode for your use case (manual vs domain-based)

---

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/tools/test_data_content_comparer.py
```

### Integration Tests
```bash
python -m pytest tests/integration/tools/test_data_content_comparer_integration.py
```

### Test Data
Example files needed:
- Sample old and new data files
- Expected comparison reports
- Test cases for different comparison modes
- Plugin-specific test data

---

## 🔄 Dependencies

Required packages:
- pandas >= 1.3.0
- numpy >= 1.20.0
- openpyxl >= 3.0.0
- python-dateutil >= 2.8.0
- pytz >= 2021.1
- Python >= 3.8

System requirements:
- Memory: 200MB base + 100MB per file
- Storage: 400MB for processing and output
- CPU: Multi-core recommended for large files

---

## 🚨 Error Handling

Common errors and solutions:
1. **File Format Error**
   - Cause: Input file format not recognized
   - Solution: Check file format and required structure
2. **Comparison Error**
   - Cause: Comparison logic failed
   - Solution: Check data compatibility and comparison mode
3. **Plugin Error**
   - Cause: Comparison plugin not found or incompatible
   - Solution: Check plugin installation and compatibility
4. **Missing Files Error**
   - Cause: Expected domain files not found
   - Solution: Verify R5/R6 files exist in domain directories
5. **Mode Error**
   - Cause: Unsupported comparison mode
   - Solution: Check available modes with `--help`

---

## 📊 Performance

Expectations:
- Processing speed: 1000-3000 records per second
- Memory usage: 200MB base + 100MB per file
- File size limits: Up to 1GB per input file

Optimization tips:
- Use specific comparison modes for large files
- Process files in chunks
- Enable parallel processing for multiple files
- Optimize comparison algorithms
- Use domain-based mode for structured data

---

## 📋 Development Checklist

### 1. File Structure ✅
- [x] Standard package layout
  - [x] __init__.py with version info
  - [x] main.py for CLI
  - [x] utils.py for helpers
  - [x] env.py for environment detection
  - [x] plugins/ directory
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

---

## 🔄 Plugin Architecture

The tool uses a plugin-based architecture for different comparison modes:

- **Standard Mode**: Basic file-to-file comparison
- **RHQ Mode**: Specialized for residential history forms
- **Domain Old vs New Mode**: Domain-specific comparisons
- **Release Consistency Mode**: Release-to-release comparison (consolidated from release_consistency_checker)

To add a new comparison mode:
1. Create a new plugin file in `plugins/`
2. Implement the required interface
3. Register the plugin in `plugins/__init__.py`
4. Update this documentation

---

## 📝 Release Notes

### Current Version (2.0.0)
- ✅ Consolidated release_consistency_checker functionality
- ✅ Added support for both manual and domain-based comparison modes
- ✅ Enhanced plugin architecture
- ✅ Improved error handling and validation
- ✅ Better performance for large datasets
- ✅ Comprehensive usage examples and documentation 