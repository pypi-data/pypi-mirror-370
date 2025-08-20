# Dictionary Validator ✅

Validate your data dictionary files for completeness, consistency, and compliance with standards. Ensures your dictionaries meet quality requirements before use in data validation workflows.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This build was packaged on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📂 Directory Structure

```
dictionary_validator_distributable/
├── input/                  # Place your dictionary files here
├── output/                # Validation reports and results
├── logs/                  # Log files from tool execution
├── scripts/               # Core implementation (no need to modify)
│   ├── main.py            # Main tool entry point
│   ├── utils.py           # Tool-specific helper functions
│   ├── common/            # Shared utilities
│   └── __init__.py        # Package marker
├── embed_py311/           # Embedded Python environment
├── config.bat             # Tool configuration settings
└── run.bat               # Main execution script
```

---

## 🚀 Quick Start

1. **Place your dictionary files** in the `input/` folder
2. **Double-click `run.bat`**
3. **Find your validation reports** in the `output/` folder

---

## 📋 Requirements

- Windows 10 or later
- 4GB RAM minimum
- 1GB free disk space
- Input files must be:
  - CSV or Excel format (.csv, .xlsx)
  - Contain dictionary structure (Main Variable, Value Type, Expected Values)
  - Not password protected
  - Under 100MB each

---

## ⚙️ Configuration

Default settings are ready to use, but you can customize in config.bat:

1. **Input Settings**
   - File types accepted (CSV, Excel)
   - Required dictionary columns
   - Validation rule settings

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
1. Copy your dictionary files to `input/`
2. Run the tool
3. Check `output/` for validation reports

### Advanced Use
- Validate multiple dictionary files at once
- Customize validation rules
- Generate quality assessment reports
- Check compliance with standards

---

## 🔎 Troubleshooting

### Common Issues

1. **"Dictionary Format Not Recognized"**
   - Symptom: Tool can't read dictionary structure
   - Solution: Check column names and file format

2. **"Validation Failed"**
   - Symptom: No validation reports created
   - Solution: Review logs for specific validation errors

3. **"Quality Assessment Error"**
   - Symptom: Quality metrics calculation failed
   - Solution: Check dictionary structure and data types

### Error Messages

- `[DV001]`: Input file missing or invalid
- `[DV002]`: Dictionary format error
- `[DV003]`: Validation failure
- `[DV004]`: Quality assessment error

---

## 📞 Support

- Check `logs/run_log.txt` for detailed error information
- Contact: data.support@organization.com
- Hours: Monday-Friday, 9am-5pm CST
- Response time: Within 1 business day

---

## 📝 Release Notes

### Current Version (1.1.0)
- Enhanced dictionary validation rules
- Improved quality assessment
- Better error reporting
- Faster processing speed

### Known Issues
- Some complex dictionary formats may not be validated properly
- Very large dictionaries (>100MB) may be slow
- Special characters in column names may cause issues
- Workaround: Use standard dictionary formats when possible

--- 