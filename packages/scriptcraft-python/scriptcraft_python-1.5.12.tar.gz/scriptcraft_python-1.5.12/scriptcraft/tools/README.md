# 🛠️ Tools Package

This package contains all ScriptCraft tools organized in a standardized structure.

## 📋 **Tool Metadata Standards**

All tools follow a standardized metadata format in their `__init__.py` files:

### **Required Metadata Fields**

```python
# Tool metadata
__description__ = "🔧 Brief description with emoji"
__tags__ = ["category1", "category2", "type"]
__data_types__ = ["csv", "xlsx", "json"]
__domains__ = ["clinical", "biomarkers", "genomics", "imaging"]
__complexity__ = "simple"  # simple | moderate | complex
__maturity__ = "stable"    # experimental | beta | stable | mature | deprecated
__distribution__ = "hybrid"  # standalone | pipeline | hybrid
```

### **Field Definitions**

| Field | Type | Description | Valid Values |
|-------|------|-------------|--------------|
| `__description__` | str | Brief tool description with emoji | Any string starting with emoji |
| `__tags__` | List[str] | Tool categories and keywords | Any descriptive tags |
| `__data_types__` | List[str] | Supported file formats | `csv`, `xlsx`, `xls`, `json`, `docx`, etc. |
| `__domains__` | List[str] | Applicable research domains | `clinical`, `biomarkers`, `genomics`, `imaging` |
| `__complexity__` | str | Implementation complexity | `simple`, `moderate`, `complex` |
| `__maturity__` | str | Development maturity level | `experimental`, `beta`, `stable`, `mature`, `deprecated` |
| `__distribution__` | str | How tool can be used | `standalone`, `pipeline`, `hybrid` |

### **Complexity Levels**

- **`simple`**: Basic functionality, minimal configuration, easy to use
- **`moderate`**: Multiple modes/options, some configuration required
- **`complex`**: Advanced functionality, significant configuration, external dependencies

### **Maturity Levels**

- **`experimental`**: New tool, may change significantly
- **`beta`**: Stable API, minor changes possible
- **`stable`**: Production ready, backwards compatible
- **`mature`**: Well-established, minimal changes expected
- **`deprecated`**: Being phased out, avoid new usage

### **Distribution Types**

- **`standalone`**: Can run independently from command line
- **`pipeline`**: Only runs as part of pipeline workflows
- **`hybrid`**: Both standalone and pipeline usage supported

## 🎯 **Available Tools**

### **Data Validation & Quality Control**
- `dictionary_driven_checker` - Plugin-based data validation against dictionaries
- `dictionary_validator` - Validates dictionary structure and completeness
- `medvisit_integrity_validator` - Validates Med/Visit ID integrity
- `release_consistency_checker` - Compares data consistency across releases
- `score_totals_checker` - Validates calculated score totals

### **Data Comparison & Analysis**
- `data_content_comparer` - Detailed dataset comparison and reporting
- `feature_change_checker` - Tracks feature value changes over time
- `schema_detector` - Analyzes datasets and generates database schemas

### **Data Processing & Cleaning**
- `dictionary_cleaner` - Cleans and standardizes dictionary files
- `date_format_standardizer` - Standardizes date formats across datasets

### **Automation & Forms**
- `automated_labeler` - Generates labels and fills document templates
- `rhq_form_autofiller` - Automates RHQ web form filling

## 🚀 **Using Tools**

### **Programmatic Usage**
```python
from scriptcraft.tools import ToolName

tool = ToolName()
tool.run(input_paths=['data.csv'], output_dir='output')
```

### **Discovery and Metadata**
```python
from scriptcraft.tools import discover_tool_metadata, get_available_tools

# Get tool metadata
metadata = discover_tool_metadata('schema_detector')
print(f"Complexity: {metadata.complexity}")
print(f"Tags: {metadata.tags}")

# List all tools
tools = get_available_tools()
```

## 📚 **Adding New Tools**

1. **Use the template**: Copy from `templates/new_package_template/`
2. **Follow naming**: Use `snake_case` for package names
3. **Add metadata**: Include all required metadata fields
4. **Implement BaseTool**: Inherit from `scriptcraft.common.BaseTool`
5. **Test thoroughly**: Ensure tool works in both dev and packaged environments

## 🔗 **Related Documentation**

- [Base Classes](../common/core/README.md) - Tool base class documentation
- [Configuration](../common/core/config.py) - Configuration management
- [Templates](../../templates/README.md) - Tool templates and examples