# 🔍 Schema Detector Tool

Automatically detects and generates database schemas from datasets without reading sensitive data. Specially designed for healthcare and clinical research data with privacy-safe analysis and healthcare-specific pattern recognition.

## ✨ Features

### 🔍 **Intelligent Analysis**
- **Column type inference** from headers and sample data
- **Healthcare pattern recognition** (patient IDs, medical records, diagnoses)
- **Privacy classification** (public, internal, sensitive, highly sensitive)
- **Primary/foreign key detection** based on naming and data patterns
- **Constraint generation** (NOT NULL, UNIQUE, CHECK constraints)

### 🏗️ **Multi-Database Support**
- **SQLite** - Development and testing
- **SQL Server** - Enterprise healthcare systems
- **PostgreSQL** - Open-source healthcare platforms

### 🔐 **Privacy Protection**
- **Limited data sampling** (configurable sample size)
- **Anonymized sample values** in privacy mode
- **HIPAA-aware analysis** for healthcare data
- **Sensitive data classification** with security recommendations

### 📊 **File Format Support**
- **CSV files** - Most common healthcare export format
- **Excel files** (.xlsx, .xls) - Clinical system exports
- **JSON files** - API responses and modern data exchanges
- **Parquet files** - Big data healthcare analytics

### 📝 **Rich Output Options**
- **SQL DDL scripts** - Ready-to-execute CREATE TABLE statements
- **JSON schemas** - For API documentation and validation
- **YAML schemas** - Human-readable configuration format
- **Markdown documentation** - Comprehensive analysis reports

## 🚀 Quick Start

### Basic Usage
```bash
# Analyze a single CSV file
python -m scriptcraft.tools.schema_detector input/patient_data.csv

# Analyze multiple files with SQL Server target
python -m scriptcraft.tools.schema_detector input/*.xlsx --database sqlserver

# Custom output directory and privacy settings
python -m scriptcraft.tools.schema_detector input/data.csv --output schemas --no-privacy
```

### Python API Usage
```python
from scriptcraft.tools.schema_detector import SchemaDetector

# Create detector
detector = SchemaDetector()

# Analyze datasets
success = detector.run(
    input_paths=['input/patients.csv', 'input/visits.xlsx'],
    output_dir='output/schemas',
    target_database='postgresql',
    privacy_mode=True
)
```

## 🏥 Healthcare-Specific Features

### Recognized Patterns
The tool automatically recognizes and properly handles common healthcare data patterns:

| Pattern | Privacy Level | SQL Constraints | Examples |
|---------|---------------|-----------------|----------|
| **Patient ID** | Sensitive | UNIQUE, NOT NULL | `patient_id`, `mrn`, `medical_record` |
| **SSN/Tax ID** | Highly Sensitive | UNIQUE | `ssn`, `social_security`, `tax_id` |
| **Date of Birth** | Sensitive | NOT NULL | `dob`, `birth_date`, `date_of_birth` |
| **Diagnosis** | Highly Sensitive | INDEX | `diagnosis`, `icd_code`, `condition` |
| **Medication** | Sensitive | INDEX | `medication`, `drug`, `prescription` |
| **Provider** | Internal | INDEX | `provider`, `doctor`, `physician` |
| **Lab Results** | Sensitive | - | `lab_result`, `test_value`, `result` |

### Privacy Classification
- 🟢 **Public** - Non-sensitive demographic data
- 🟡 **Internal** - Provider information, visit dates
- 🟠 **Sensitive** - Patient identifiers, lab results
- 🔴 **Highly Sensitive** - SSN, diagnoses, genetic data

## 📋 Command Line Options

```bash
python -m scriptcraft.tools.schema_detector [OPTIONS] FILES...

Arguments:
  FILES...                    Dataset files to analyze

Options:
  --output DIR               Output directory (default: output)
  --database {sqlite,sqlserver,postgresql}
                            Target database type (default: sqlite)
  --privacy-mode            Enable privacy-safe analysis (default: True)
  --no-privacy              Disable privacy mode (show actual sample values)
  --sample-size INT         Maximum rows to analyze (default: 1000)
  --naming {snake_case,pascal_case,camel_case}
                            Column naming convention (default: pascal_case)
  --formats {sql,json,yaml} Output formats (default: all)
```

## 📊 Output Examples

### Generated SQL Schema
```sql
-- 🗄️ Auto-Generated Database Schema
-- Generated on: 2024-01-15 10:30:00
-- Target Database: SQLITE

-- SamplePatients (Dimension Table)
-- Estimated rows: 1,000
CREATE TABLE SamplePatients (
    PatientId TEXT UNIQUE NOT NULL PRIMARY KEY,  -- Originally: PatientId, Privacy: sensitive
    FirstName TEXT,  -- Originally: FirstName, Privacy: sensitive
    LastName TEXT,  -- Originally: LastName, Privacy: sensitive
    DateOfBirth TEXT NOT NULL,  -- Originally: DateOfBirth, Privacy: sensitive
    Gender TEXT,  -- Privacy: public
    Email TEXT,  -- Privacy: sensitive
    IsActive INTEGER NOT NULL  -- Privacy: internal
);
```

### Documentation Report
```markdown
# 📊 Dataset Schema Analysis Report

**Generated**: 2024-01-15 10:30:00
**Database Target**: SQLITE
**Tables Analyzed**: 3

## 🔍 Analysis Summary

| Metric | Value |
|--------|-------|
| Total Tables | 3 |
| Total Columns | 24 |
| Primary Keys Detected | 3 |
| Foreign Keys Detected | 2 |
| Highly Sensitive Columns | 4 |
| Sensitive Columns | 8 |

## 🔐 Privacy & Security Recommendations

### SamplePatients
- **PatientId**: Requires access logging and controlled access
- **DateOfBirth**: Requires access logging and controlled access
```

## ⚙️ Configuration

### Privacy Settings
```python
detector.config.update({
    'privacy_mode': True,        # Anonymize sample values
    'sample_size': 1000,         # Limit rows analyzed
    'healthcare_mode': True      # Use healthcare patterns
})
```

### Database-Specific Settings
```python
# SQL Server configuration
detector.config.update({
    'target_database': 'sqlserver',
    'naming_convention': 'pascal_case'
})

# PostgreSQL configuration  
detector.config.update({
    'target_database': 'postgresql',
    'naming_convention': 'snake_case'
})
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
# Run schema detector tests
python -m pytest implementations/python/scriptcraft/tests/tools/test_schema_detector.py -v

# Run with coverage
python -m pytest implementations/python/scriptcraft/tests/tools/test_schema_detector.py --cov=scriptcraft.tools.schema_detector
```

## 🔧 Advanced Usage

### Custom Healthcare Patterns
```python
# Add custom healthcare patterns
detector.healthcare_patterns['custom_id'] = {
    'patterns': [r'study[_\s]*id', r'protocol[_\s]*number'],
    'sql_type': 'TEXT',
    'constraints': ['UNIQUE', 'NOT NULL'],
    'privacy': 'internal',
    'indexes': ['INDEX']
}
```

### Batch Processing
```python
import glob

# Process all CSV files in a directory
csv_files = glob.glob('healthcare_data/*.csv')
detector.run(
    input_paths=csv_files,
    output_dir='schemas/healthcare',
    target_database='postgresql',
    privacy_mode=True
)
```

## 🛡️ Privacy & Security

### HIPAA Compliance
- **Minimum data exposure** - Only samples headers and limited rows
- **Anonymized samples** - No actual patient data in output
- **Privacy classification** - Automatic marking of sensitive columns
- **Audit trail** - Comprehensive logging of all analysis

### Best Practices
1. **Always use privacy mode** for production healthcare data
2. **Review privacy classifications** before database deployment
3. **Implement proper access controls** for sensitive columns
4. **Encrypt highly sensitive columns** at rest and in transit

## 🤝 Contributing

Found a healthcare pattern we missed? Want to add support for a new database? 

1. **Add pattern recognition** in `_init_healthcare_patterns()`
2. **Add database mapping** in `_init_data_type_mapping()`
3. **Add comprehensive tests** in `test_schema_detector.py`
4. **Update documentation** with examples

## 📚 Related Tools

- **[Dictionary Driven Checker](../dictionary_driven_checker/)** - Validate data against schemas
- **[Data Content Comparer](../data_content_comparer/)** - Compare datasets
- **[Feature Change Checker](../feature_change_checker/)** - Track schema evolution

---

**Schema Detector Tool** - Part of the ScriptCraft Healthcare Data Processing Suite 