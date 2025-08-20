# Dictionary Driven Checker 🔍

Validate your data files against dictionary specifications to ensure data quality and consistency. Uses plugin-based validation rules for numeric, categorical, date, and text data with comprehensive reporting.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This build was packaged on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📂 Directory Structure

```
dictionary_driven_checker_distributable/
├── input/                  # Place your data and dictionary files here
├── output/                # Validation reports and results
├── logs/                  # Log files from tool execution
├── scripts/               # Core implementation (no need to modify)
│   ├── main.py            # Main tool entry point
│   ├── utils.py           # Tool-specific helper functions
│   ├── plugins/           # Validation plugins
│   ├── common/            # Shared utilities
│   └── __init__.py        # Package marker
├── embed_py311/           # Embedded Python environment
├── config.bat             # Tool configuration settings
└── run.bat               # Main execution script
```

---

## 🚀 Quick Start

1. **Place your data file** in the `input/` folder
2. **Place your dictionary file** in the `input/` folder
3. **Double-click `run.bat`**
4. **Find your validation reports** in the `output/` folder

---

## 📋 Requirements

- Windows 10 or later
- 4GB RAM minimum
- 1GB free disk space
- Input files must be:
  - CSV or Excel format (.csv, .xlsx)
  - Data file: Contains the data to validate
  - Dictionary file: Contains validation rules and specifications
  - Not password protected
  - Under 500MB each

---

## ⚙️ Configuration

Default settings are ready to use, but you can customize in config.bat:

1. **Input Settings**
   - File types accepted (CSV, Excel)
   - Required dictionary columns
   - Validation plugin settings

2. **Output Settings**
   - Report format and detail level
   - Output file naming
   - Output location

3. **Processing Options**
   - Validation strictness
   - Error handling
   - Performance settings

---

## 📊 Example Usage

### Basic Use
1. Copy your data file to `input/`
2. Copy your dictionary file to `input/`
3. Run the tool
4. Check `output/` for validation reports

### Advanced Use
- Use specific validation plugins
- Customize validation rules
- Process multiple data files
- Generate detailed validation reports

---

## 🔎 Troubleshooting

### Common Issues

1. **"Dictionary Format Not Recognized"**
   - Symptom: Tool can't read dictionary structure
   - Solution: Check dictionary column names and format

2. **"Validation Plugin Error"**
   - Symptom: Validation fails or plugin not found
   - Solution: Check plugin compatibility and dictionary format

3. **"Data Validation Failed"**
   - Symptom: No validation reports created
   - Solution: Review logs for specific validation errors

### Error Messages

- `[DDC001]`: Input file missing or invalid
- `[DDC002]`: Dictionary format error
- `[DDC003]`: Validation plugin error
- `[DDC004]`: Data validation failure

---

## 📞 Support

- Check `logs/run_log.txt` for detailed error information
- Contact: data.support@organization.com
- Hours: Monday-Friday, 9am-5pm CST
- Response time: Within 1 business day

---

## 📝 Release Notes

### Current Version (1.1.0)
- Enhanced validation plugins
- Improved error reporting
- Better performance for large files
- More detailed validation reports

### Known Issues
- Some complex validation rules may be slow
- Very large dictionaries (>500MB) may cause memory issues
- Special characters in data may cause validation errors
- Workaround: Use standard data formats when possible

--- 