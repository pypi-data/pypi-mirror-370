# Common Package - Consolidated Utilities

This package consolidates common patterns and utilities used across tools to eliminate code duplication and provide consistent behavior.

## 🎯 Overview

The common package provides standardized utilities for:
- **Data Loading & Validation** - Consistent file loading and validation patterns
- **Tool Creation** - Standardized tool patterns and factory functions
- **Data Processing** - Common data processing pipelines and utilities
- **Logging** - Consistent logging with emojis and status indicators
- **File Operations** - Standardized file and directory operations
- **CLI Utilities** - Centralized command-line argument parsing

## 📦 Package Structure

```
common/
├── __init__.py          # Main exports (imports everything with *)
├── core/               # Base classes and core functionality
├── data/               # Data processing and validation
├── io/                 # Input/output operations
├── logging/            # Logging utilities
├── cli/                # Command-line interface utilities
├── tools/              # Tool patterns and utilities
├── pipeline/           # Pipeline execution utilities
└── time/               # Time-related utilities
```

## 🚀 Quick Start

```python
from scriptcraft.common import (
    load_data, log_and_print, setup_tool_files,
    create_standard_tool, DataProcessor
)

# Load data with validation
data = load_data("input.csv")

# Log with emojis
log_and_print("✅ Data loaded successfully")

# Create a standard tool
MyTool = create_standard_tool(
    'validation', 
    'My Tool', 
    'Validates data',
    my_validation_function
)
```

## 🛠️ Tool Creation

### Simple Tool Creation

```python
from scriptcraft.common import create_standard_tool, create_runner_function

def my_validation_func(domain, dataset_file, dictionary_file, output_path, paths):
    # Your validation logic here
    pass

# Create tool and runner
MyValidator = create_standard_tool(
    'validation',
    'My Validator',
    'Validates data',
    my_validation_func,
    requires_dictionary=True
)
run_my_validator = create_runner_function(MyValidator)
```

### Tool Types
- `'validation'` - Tools that validate data
- `'transformation'` - Tools that transform data
- `'checker'` - Tools that check data and return results

## 🔄 Data Processing

### DataProcessor Class

```python
from scriptcraft.common import DataProcessor

processor = DataProcessor("MyProcessor")

# Load and validate data
data = processor.load_and_validate(["file1.csv", "file2.csv"])

# Process data
result = processor.process_data(data, my_process_function)

# Save results
processor.save_results(result, "output.xlsx")
```

### Complete Pipeline

```python
from scriptcraft.common import load_and_process_data

# Run complete pipeline
result, output_path = load_and_process_data(
    input_paths=["input.csv"],
    process_func=my_process_function,
    output_path="output.xlsx"
)
```

## 📝 Logging

```python
from scriptcraft.common import log_and_print

log_and_print("🚀 Starting process")
log_and_print("✅ Process completed")
log_and_print("❌ Error occurred", level="error")
```

## 📁 File Operations

```python
from scriptcraft.common import (
    find_first_data_file, find_latest_file, setup_tool_files
)

# Find files
file = find_first_data_file("input/")
latest = find_latest_file("input/")

# Standard tool file setup
dataset_file, dictionary_file = setup_tool_files(paths, domain, "Tool Name")
```

## 🎯 Benefits

- **60-70% code reduction** in tool boilerplate
- **Consistent behavior** across all tools
- **Easy tool creation** with factory functions
- **Standardized patterns** for common operations
- **Automatic imports** - no need to update `__init__.py` when adding new functions

## 🔧 Migration

The consolidation maintains **backward compatibility** while providing new, more efficient patterns. You can:

1. **Gradually migrate** existing tools to use the new patterns
2. **Create new tools** using the factory functions
3. **Mix old and new** patterns during transition

This consolidation follows DRY principles and makes the codebase more maintainable and scalable. 