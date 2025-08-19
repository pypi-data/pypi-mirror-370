# Dictionary Cleaner 🧹

Clean and standardize your data dictionary files to ensure consistent formatting, value types, and expected values. Perfect for preparing dictionaries for data validation and quality control workflows.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This build was packaged on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📂 Directory Structure

```
dictionary_cleaner_distributable/
├── input/                  # Place your dictionary files here
├── output/                # Cleaned dictionary files
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
3. **Find your cleaned dictionaries** in the `output/` folder

---

## 📋 Requirements

- Windows 10 or later
- 4GB RAM minimum
- 1GB free disk space
- Input files must be:
  - CSV or Excel format (.csv, .xlsx)
  - Contain dictionary columns (Main Variable, Value Type, Expected Values)
  - Not password protected
  - Under 100MB each

---

## ⚙️ Configuration

Default settings are ready to use, but you can customize in config.bat:

1. **Input Settings**
   - File types accepted (CSV, Excel)
   - Required dictionary columns
   - Cleaning rule settings

2. **Output Settings**
   - Standardized format
   - Output file naming
   - Output location

3. **Processing Options**
   - Logging level
   - Error handling
   - Performance settings

---

## 📊 Example Usage

### Basic Use
1. Copy your dictionary files to `input/`
2. Run the tool
3. Check `output/` for cleaned dictionaries

### Advanced Use
- Process multiple dictionary files at once
- Customize cleaning rules
- Handle different dictionary formats automatically
- Batch process large dictionaries

---

## 🔎 Troubleshooting

### Common Issues

1. **"Dictionary Format Not Recognized"**
   - Symptom: Tool can't read dictionary structure
   - Solution: Check column names and file format

2. **"File Format Error"**
   - Symptom: Tool can't read input file
   - Solution: Convert file to CSV or Excel format

3. **"Cleaning Failed"**
   - Symptom: No output files created
   - Solution: Review logs for specific error details

### Error Messages

- `[DC001]`: Input file missing or invalid
- `[DC002]`: Dictionary format error
- `[DC003]`: Cleaning failure
- `[DC004]`: Output generation error

---

## 📞 Support

- Check `logs/run_log.txt` for detailed error information
- Contact: data.support@organization.com
- Hours: Monday-Friday, 9am-5pm CST
- Response time: Within 1 business day

---

## 📝 Release Notes

### Current Version (1.1.0)
- Enhanced dictionary cleaning rules
- Improved value type standardization
- Better error handling
- Faster processing speed

### Known Issues
- Some complex value formats may not be cleaned properly
- Very large dictionaries (>100MB) may be slow
- Special characters in values may cause issues
- Workaround: Use standard value formats when possible

--- 