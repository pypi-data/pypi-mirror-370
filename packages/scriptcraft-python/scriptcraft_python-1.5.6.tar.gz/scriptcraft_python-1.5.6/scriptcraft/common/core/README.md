# Core Base Classes Documentation

## 🚀 SIMPLIFIED ARCHITECTURE (v2.0.0)

The ScriptCraft core has been radically simplified to eliminate artificial complexity and maximize DRY principles. **ALL tools should now inherit from `BaseTool`** - a universal base class that provides everything you need.

## ✨ Key Principle: Load → Process → Save

Every tool follows the same fundamental pattern:
1. **Load data** using `load_data_file()`
2. **Process data** with your custom logic  
3. **Save results** using `save_data_file()`

## 🏗️ Universal Base Class: `BaseTool`

```python
from scriptcraft.common.core import BaseTool

class MyTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="My Tool",
            description="🔧 What this tool does",
            supported_formats=['.csv', '.xlsx']  # Optional
        )
    
    def run(self, input_paths, output_dir=None, **kwargs):
        # Validate inputs using DRY method
        if not self.validate_input_files(input_paths):
            return False
        
        output_path = self.resolve_output_directory(output_dir)
        
        for input_path in input_paths:
            # Load → Process → Save pattern
            data = self.load_data_file(input_path)           # DRY loading
            processed = self._my_custom_logic(data)          # Your logic
            filename = self.get_output_filename(input_path, suffix="result")
            self.save_data_file(processed, output_path / filename)  # DRY saving
    
    def _my_custom_logic(self, data):
        # Your custom processing here
        return data
```

## 🛠️ Complete DRY Method Reference

### Environment & Path Resolution
```python
# Environment detection (static method)
if BaseTool.is_distributable_environment():
    print("Running in distributable mode")

# Path resolution (instance methods)
input_dir = self.resolve_input_directory(input_dir="custom/path")
output_dir = self.resolve_output_directory(output_dir="custom/output")
```

### File Operations
```python
# File validation
valid = self.validate_input_files(
    input_paths=[path1, path2], 
    required_count=2  # Optional minimum
)

# Data loading (universal format detection)
df = self.load_data_file("data.csv")    # or .xlsx, .xls
df = self.load_data_file("data.xlsx")

# Data saving (universal format detection)
output_path = self.save_data_file(df, "results.csv")
output_path = self.save_data_file(df, "results.xlsx", include_index=True)

# Filename generation
filename = self.get_output_filename(
    input_path="input.csv", 
    suffix="processed",
    extension=".xlsx"
)
# Returns: "input_processed.xlsx"
```

### Logging (with emoji support)
```python
self.log_message("🔄 Processing data...")
self.log_message("⚠️ Warning message", level="warning") 
self.log_message("❌ Error occurred", level="error")

# Standardized lifecycle logging
self.log_start()                        # "🚀 Starting Tool Name..."
self.log_completion()                   # "✅ Tool Name completed successfully"
self.log_completion(output_path)        # Includes output path
self.log_error("Something went wrong")  # "❌ Tool Name error: ..."
```

### Execution Patterns
```python
# Standardized error handling
result = self.run_with_error_handling(my_function, arg1, arg2, kwarg=value)

# Built-in DataFrame comparison
comparison = self.compare_dataframes(df1, df2)
# Returns: {
#   'shape_comparison': {'df1_shape': (100, 5), 'df2_shape': (95, 5), 'shape_match': False},
#   'column_comparison': {'common_columns': [...], 'df1_only': [...], 'df2_only': [...]}
# }
```

## 📋 Common Tool Patterns

### 1. Single File Analysis
```python
class DataProfiler(BaseTool):
    def run(self, input_paths, output_dir=None, **kwargs):
        if not self.validate_input_files(input_paths):
            return False
        
        output_path = self.resolve_output_directory(output_dir)
        
        for input_path in input_paths:
            data = self.load_data_file(input_path)
            profile = self._create_profile(data)
            filename = self.get_output_filename(input_path, suffix="profile")
            self.save_data_file(profile, output_path / filename)
```

### 2. Dataset Comparison
```python
class DataComparer(BaseTool):
    def run(self, input_paths, output_dir=None, **kwargs):
        if not self.validate_input_files(input_paths, required_count=2):
            return False
        
        df1 = self.load_data_file(input_paths[0])
        df2 = self.load_data_file(input_paths[1])
        
        # Use built-in comparison
        basic_comparison = self.compare_dataframes(df1, df2)
        
        # Add custom comparison
        detailed_comparison = self._detailed_compare(df1, df2)
        
        # Save combined results
        results = {**basic_comparison, 'detailed': detailed_comparison}
        # ... save logic
```

### 3. Data Transformation
```python
class DataCleaner(BaseTool):
    def run(self, input_paths, output_dir=None, **kwargs):
        if not self.validate_input_files(input_paths):
            return False
        
        output_path = self.resolve_output_directory(output_dir)
        
        for input_path in input_paths:
            data = self.load_data_file(input_path)
            cleaned = self._clean_data(data)
            filename = self.get_output_filename(input_path, suffix="cleaned")
            self.save_data_file(cleaned, output_path / filename)
    
    # Legacy support for transform() pattern
    def transform(self, domain, input_path, output_path, paths=None):
        data = self.load_data_file(input_path)
        cleaned = self._clean_data(data)
        self.save_data_file(cleaned, output_path)
```

## 🔄 Migration Guide

### ✅ RECOMMENDED: New Tools
```python
# ✅ DO THIS - Use BaseTool for everything
class MyNewTool(BaseTool):
    def __init__(self):
        super().__init__("My Tool", "Description")
    
    def run(self, input_paths, output_dir=None, **kwargs):
        # Standard pattern using DRY methods
        pass
```

### 📦 Legacy Compatibility
If you have existing tools using the old base classes, they will continue to work during the migration period:

```python
# These still work (legacy compatibility)
class OldTool(BaseProcessor):          # Still works
class OldTool(DataAnalysisTool):       # = BaseTool (alias)
class OldTool(DataComparisonTool):     # = BaseTool (alias)
class OldTool(DataProcessorTool):      # = BaseProcessor (alias)
```

**However, you should migrate to `BaseTool` for new development.**

### 🚀 Migration Benefits

**Before (Duplicated Code)**:
```python
class OldAnalyzer(DataAnalysisTool):
    def run(self, input_paths, output_dir=None, **kwargs):
        # Validate inputs
        for path in input_paths:
            if not Path(path).exists():
                raise FileNotFoundError(f"File not found: {path}")
        
        # Load data
        if path.suffix == '.csv':
            df = pd.read_csv(path)
        elif path.suffix == '.xlsx':
            df = pd.read_excel(path)
        
        # Process data
        results = self._analyze(df)
        
        # Save results
        output_path = Path(output_dir or "output")
        output_path.mkdir(exist_ok=True)
        results.to_csv(output_path / "results.csv", index=False)
```

**After (DRY)**:
```python
class NewAnalyzer(BaseTool):
    def run(self, input_paths, output_dir=None, **kwargs):
        if not self.validate_input_files(input_paths): return False  # DRY validation
        output_path = self.resolve_output_directory(output_dir)      # DRY path resolution
        
        for input_path in input_paths:
            data = self.load_data_file(input_path)                   # DRY loading
            results = self._analyze(data)                            # Your logic
            filename = self.get_output_filename(input_path, "results") # DRY naming
            self.save_data_file(results, output_path / filename)     # DRY saving
```

**Lines of code: 20+ → 7 lines!**

## 🎯 Key Benefits

1. **🔥 Massive Code Reduction**: 60-80% fewer lines per tool
2. **🛡️ Bulletproof Error Handling**: Standardized across all tools
3. **🔄 Universal Patterns**: Same approach for all tool types
4. **📱 Environment Agnostic**: Works in dev and distributable modes
5. **🎨 Beautiful Logging**: Consistent emoji-enhanced output
6. **⚡ Format Detection**: Automatic CSV/Excel handling
7. **🧪 Testable**: Clean separation of concerns

## 💡 Best Practices

1. **Always inherit from `BaseTool`** for new tools
2. **Use DRY methods** instead of reimplementing common operations
3. **Implement business logic** in private methods (`_process_data()`)
4. **Leverage standardized patterns** for consistent behavior
5. **Add emojis to log messages** for better readability
6. **Test your tools** in both development and distributable modes

## 🚨 What Was Eliminated

❌ **Duplicate base classes** (BaseProcessor vs BaseTool vs DataAnalysisTool)  
❌ **Redundant methods** (load_data_file vs load_input_file vs load_analysis_file)  
❌ **Artificial distinctions** between "processors", "analyzers", "comparers"  
❌ **Code duplication** across 50+ methods in different base classes  
❌ **Complex inheritance hierarchies** that added no value  

✅ **One universal base class** with all functionality in DRY methods  
✅ **Consistent patterns** across all tool types  
✅ **Massive code reduction** while maintaining all capabilities 