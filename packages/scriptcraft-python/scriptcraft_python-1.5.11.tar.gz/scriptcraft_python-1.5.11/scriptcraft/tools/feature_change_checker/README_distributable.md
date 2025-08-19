# Feature Change Checker 🔄

Detect and analyze changes in data features between different versions or releases. Identifies new, removed, or modified variables with detailed reporting and analysis.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This build was packaged on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📂 Directory Structure

```
feature_change_checker_distributable/
├── input/                  # Place your old and new data files here
├── output/                # Change reports and analysis
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

1. **Place your old data file** in the `input/` folder
2. **Place your new data file** in the `input/` folder
3. **Double-click `run.bat`**
4. **Find your change reports** in the `output/` folder

---

## 📋 Requirements

- Windows 10 or later
- 4GB RAM minimum
- 1GB free disk space
- Input files must be:
  - CSV or Excel format (.csv, .xlsx)
  - Old file: Previous version of your data
  - New file: Current version of your data
  - Not password protected
  - Under 150MB each

---

## ⚙️ Configuration

Default settings are ready to use, but you can customize in config.bat:

1. **Input Settings**
   - File types accepted (CSV, Excel)
   - Required file structure
   - Change detection settings

2. **Output Settings**
   - Report format and detail level
   - Output file naming
   - Output location

3. **Processing Options**
   - Change detection strictness
   - Error handling
   - Performance settings

---

## 📊 Example Usage

### Basic Use
1. Copy your old data file to `input/`
2. Copy your new data file to `input/`
3. Run the tool
4. Check `output/` for change reports

### Advanced Use
- Use strict change detection mode
- Include metadata in analysis
- Process multiple file pairs
- Generate detailed change reports

---

## 🔎 Troubleshooting

### Common Issues

1. **"File Format Not Recognized"**
   - Symptom: Tool can't read file structure
   - Solution: Check file format and required structure

2. **"Change Detection Failed"**
   - Symptom: No change reports created
   - Solution: Review logs for specific detection errors

3. **"Feature Comparison Error"**
   - Symptom: Feature comparison failed
   - Solution: Check feature naming and data structure

### Error Messages

- `[FCC001]`: Input file missing or invalid
- `[FCC002]`: File format error
- `[FCC003]`: Change detection failure
- `[FCC004]`: Feature comparison error

---

## 📞 Support

- Check `logs/run_log.txt` for detailed error information
- Contact: data.support@organization.com
- Hours: Monday-Friday, 9am-5pm CST
- Response time: Within 1 business day

---

## 📝 Release Notes

### Current Version (1.1.0)
- Enhanced change detection algorithms
- Improved feature comparison
- Better error reporting
- Faster processing speed

### Known Issues
- Some complex feature formats may not be detected properly
- Very large files (>150MB) may cause memory issues
- Special characters in feature names may cause detection errors
- Workaround: Use standard feature naming conventions when possible

--- 