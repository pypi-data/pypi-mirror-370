# Dictionary Workflow 🔄

Complete dictionary processing workflow including cleaning, validation, and supplementation. Streamlines the entire dictionary preparation process from raw data to validated, enhanced dictionaries ready for use in data validation workflows.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This build was packaged on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📂 Directory Structure

```
dictionary_workflow_distributable/
├── input/                  # Place your supplement and dictionary files here
├── output/                # Processed dictionaries and reports
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

1. **Place your supplement files** in the `input/` folder
2. **Place your dictionary files** in the `input/` folder
3. **Double-click `run.bat`**
4. **Find your processed dictionaries** in the `output/` folder

---

## 📋 Requirements

- Windows 10 or later
- 4GB RAM minimum
- 1GB free disk space
- Input files must be:
  - CSV or Excel format (.csv, .xlsx)
  - Supplement files: Contain data to be added to dictionaries
  - Dictionary files: Contain dictionary structure and specifications
  - Not password protected
  - Under 200MB each

---

## ⚙️ Configuration

Default settings are ready to use, but you can customize in config.bat:

1. **Input Settings**
   - File types accepted (CSV, Excel)
   - Required supplement columns
   - Required dictionary columns
   - Workflow step settings

2. **Output Settings**
   - Output format and detail level
   - Output file naming
   - Output location

3. **Processing Options**
   - Workflow steps to run
   - Merge and enhancement strategies
   - Error handling
   - Performance settings

---

## 📊 Example Usage

### Basic Use
1. Copy your supplement files to `input/`
2. Copy your dictionary files to `input/`
3. Run the tool
4. Check `output/` for processed dictionaries

### Advanced Use
- Run specific workflow steps only
- Customize merge and enhancement strategies
- Process multiple supplement/dictionary files
- Generate detailed workflow reports

---

## 🔎 Troubleshooting

### Common Issues

1. **"Supplement Format Not Recognized"**
   - Symptom: Tool can't read supplement structure
   - Solution: Check supplement column names and format

2. **"Dictionary Format Not Recognized"**
   - Symptom: Tool can't read dictionary structure
   - Solution: Check dictionary column names and format

3. **"Workflow Step Failed"**
   - Symptom: No output files created
   - Solution: Review logs for specific workflow errors

### Error Messages

- `[DW001]`: Input file missing or invalid
- `[DW002]`: Supplement format error
- `[DW003]`: Dictionary format error
- `[DW004]`: Workflow step failure

---

## 📞 Support

- Check `logs/run_log.txt` for detailed error information
- Contact: data.support@organization.com
- Hours: Monday-Friday, 9am-5pm CST
- Response time: Within 1 business day

---

## 📝 Release Notes

### Current Version (1.1.0)
- Enhanced workflow processing
- Improved merge and enhancement strategies
- Better error reporting
- Faster processing speed

### Known Issues
- Some complex supplement formats may not be processed properly
- Very large files (>200MB) may cause memory issues
- Special characters in data may cause workflow errors
- Workaround: Use standard data formats when possible

--- 