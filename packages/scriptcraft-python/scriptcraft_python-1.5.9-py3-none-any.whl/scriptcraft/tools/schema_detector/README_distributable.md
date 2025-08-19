# Schema Detector 🔍

Automatically detect and analyze data schemas from various file formats. Identifies data types, patterns, and structure for validation and processing with comprehensive schema reporting.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This build was packaged on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📂 Directory Structure

```
schema_detector_distributable/
├── input/                  # Place your data files here
├── output/                # Schema reports and analysis
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

1. **Place your data files** in the `input/` folder
2. **Double-click `run.bat`**
3. **Find your schema reports** in the `output/` folder

---

## 📋 Requirements

- Windows 10 or later
- 4GB RAM minimum
- 1GB free disk space
- Input files must be:
  - CSV or Excel format (.csv, .xlsx)
  - Contain data for schema analysis
  - Not password protected
  - Under 100MB each

---

## ⚙️ Configuration

Default settings are ready to use, but you can customize in config.bat:

1. **Input Settings**
   - File types accepted (CSV, Excel)
   - Required data structure
   - Schema detection settings

2. **Output Settings**
   - Report format and detail level
   - Output file naming
   - Output location

3. **Processing Options**
   - Schema detection strictness
   - Error handling
   - Performance settings

---

## 📊 Example Usage

### Basic Use
1. Copy your data files to `input/`
2. Run the tool
3. Check `output/` for schema reports

### Advanced Use
- Use strict schema detection mode
- Include metadata in analysis
- Process multiple data files
- Generate detailed schema reports

---

## 🔎 Troubleshooting

### Common Issues

1. **"Data Format Not Recognized"**
   - Symptom: Tool can't read data structure
   - Solution: Check data format and required structure

2. **"Schema Detection Failed"**
   - Symptom: No schema reports created
   - Solution: Review logs for specific detection errors

3. **"Pattern Recognition Error"**
   - Symptom: Pattern recognition failed
   - Solution: Check data quality and recognition rules

### Error Messages

- `[SD001]`: Input file missing or invalid
- `[SD002]`: Data format error
- `[SD003]`: Schema detection failure
- `[SD004]`: Pattern recognition error

---

## 📞 Support

- Check `logs/run_log.txt` for detailed error information
- Contact: data.support@organization.com
- Hours: Monday-Friday, 9am-5pm CST
- Response time: Within 1 business day

---

## 📝 Release Notes

### Current Version (1.1.0)
- Enhanced schema detection algorithms
- Improved pattern recognition
- Better error reporting
- Faster processing speed

### Known Issues
- Some complex data formats may not be detected properly
- Very large files (>100MB) may cause memory issues
- Special characters in data may cause detection errors
- Workaround: Use standard data formats when possible

--- 