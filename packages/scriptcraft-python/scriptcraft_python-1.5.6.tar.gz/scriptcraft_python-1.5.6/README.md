# ScriptCraft Python Package

A comprehensive Python package for data processing and quality control tools designed for research workflows, particularly in the field of Huntington's Disease research.

## 🚀 Features

- **Data Processing Tools**: Automated data cleaning, validation, and transformation
- **Quality Control**: Comprehensive validation frameworks with plugin support
- **Research Workflows**: Specialized tools for clinical and biomarker data
- **Extensible Architecture**: Plugin-based system for custom validations
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 📦 Installation

```bash
pip install scriptcraft
```

## 🛠️ Quick Start

### Basic Usage

```python
import scriptcraft
import scriptcraft.common as cu

# Use common utilities
data = cu.load_data("your_data.csv")
cu.log_and_print("✅ Data loaded successfully")
```

### Using Tools

```python
from scriptcraft.tools import AutomatedLabeler, DataContentComparer

# Create and use tools
labeler = AutomatedLabeler()
comparer = DataContentComparer()

# Process your data
results = labeler.process(data)
```

### CLI Usage

```bash
# List available tools
scriptcraft

# Run specific tools
scriptcraft run automated-labeler
scriptcraft run data-comparer
```

## 🧰 Available Tools

- **AutomatedLabeler**: Automated data labeling and classification
- **DataContentComparer**: Compare datasets for consistency
- **DictionaryDrivenChecker**: Validation using predefined dictionaries
- **ReleaseConsistencyChecker**: Ensure data release consistency
- **SchemaDetector**: Automatic schema detection and validation
- **RHQFormAutofiller**: Automated form filling for research questionnaires
- **DateFormatStandardizer**: Standardize date formats across datasets
- **DictionaryCleaner**: Clean and validate dictionary files
- **DictionaryValidator**: Validate dictionary structures
- **FeatureChangeChecker**: Detect changes in data features
- **MedVisitIntegrityValidator**: Validate medical visit data integrity
- **ScoreTotalsChecker**: Validate score calculations
- **DictionaryWorkflow**: Complete dictionary processing workflows

## 🔧 Development

### Installation for Development

```bash
# Clone the repository
git clone https://github.com/yourusername/scriptcraft-python.git
cd scriptcraft-python

# Install in development mode
pip install -e .
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
```

## 📚 Documentation

For comprehensive documentation, examples, and advanced usage:

- **Main Documentation**: [ScriptCraft Workspace](https://github.com/yourusername/ScriptCraft-Workspace)
- **Tool Documentation**: See individual tool README files
- **API Reference**: Available in the main workspace documentation

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](https://github.com/yourusername/ScriptCraft-Workspace/blob/main/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/scriptcraft-python/issues)
- **Documentation**: [ScriptCraft Workspace](https://github.com/yourusername/ScriptCraft-Workspace)
- **Email**: scriptcraft@example.com

## 🙏 Acknowledgments

- Built for the Huntington's Disease research community
- Developed with support from research institutions
- Thanks to all contributors and users

---

**ScriptCraft Python Package** - Making research data processing easier, one tool at a time. 