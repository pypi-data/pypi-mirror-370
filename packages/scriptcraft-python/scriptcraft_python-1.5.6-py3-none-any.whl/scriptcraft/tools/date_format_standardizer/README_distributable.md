# Date Format Standardizer 📅

Standardize date formats in your data files to ensure consistency across different systems and databases. Automatically detects and converts various date representations to a consistent format.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This build was packaged on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📂 Directory Structure

```
date_format_standardizer_distributable/
├── input/                  # Place your data files here
├── output/                # Standardized data files
├── logs/                  # Log files from tool execution
├── scripts/               # Core implementation (no need to modify)
│   ├── main.py            # Main tool entry point
│   ├── env.py             # Environment detection
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
3. **Find your standardized data** in the `output/` folder

---

## 📋 Requirements

- Windows 10 or later
- 4GB RAM minimum
- 1GB free disk space
- Input files must be:
  - CSV or Excel format (.csv, .xlsx)
  - Contain date columns in various formats
  - Not password protected
  - Under 1GB each

---

## ⚙️ Configuration

Default settings are ready to use, but you can customize in config.bat:

1. **Input Settings**
   - File types accepted (CSV, Excel)
   - Required date columns
   - Date format detection rules

2. **Output Settings**
   - Standardized date format
   - Output file naming
   - Output location

3. **Processing Options**
   - Logging level
   - Error handling
   - Performance settings

---

## 📊 Example Usage

### Basic Use
1. Copy your data files to `input/`
2. Run the tool
3. Check `output/` for standardized files

### Advanced Use
- Process multiple files at once
- Customize output date format
- Handle different date formats automatically
- Batch process large datasets

---

## 🔎 Troubleshooting

### Common Issues

1. **"Date Format Not Recognized"**
   - Symptom: Tool can't detect date format
   - Solution: Check date column format and ensure it's readable

2. **"File Format Error"**
   - Symptom: Tool can't read input file
   - Solution: Convert file to CSV or Excel format

3. **"Output Generation Failed"**
   - Symptom: No output files created
   - Solution: Review logs for specific error details

### Error Messages

- `[DFS001]`: Input file missing or invalid
- `[DFS002]`: Date format detection error
- `[DFS003]`: Processing failure
- `[DFS004]`: Output generation error

---

## 📞 Support

- Check `logs/run_log.txt` for detailed error information
- Contact: data.support@organization.com
- Hours: Monday-Friday, 9am-5pm CST
- Response time: Within 1 business day

---

## 📝 Release Notes

### Current Version (1.2.0)
- Enhanced date format detection
- Improved Excel file support
- Better error handling
- Faster processing speed

### Known Issues
- Some complex date formats may not be detected
- Very large files (>1GB) may be slow
- Special characters in dates may cause issues
- Workaround: Use standard date formats when possible

--- 