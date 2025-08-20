# Medical Visit Integrity Validator 🏥

Validate the integrity and consistency of medical visit data. Ensures visit records are complete, logical, and meet clinical standards with comprehensive validation reporting.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This build was packaged on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📂 Directory Structure

```
medvisit_integrity_validator_distributable/
├── input/                  # Place your medical visit data files here
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

1. **Place your medical visit data files** in the `input/` folder
2. **Double-click `run.bat`**
3. **Find your validation reports** in the `output/` folder

---

## 📋 Requirements

- Windows 10 or later
- 4GB RAM minimum
- 1GB free disk space
- Input files must be:
  - CSV or Excel format (.csv, .xlsx)
  - Contain medical visit data with required fields
  - Include patient identifiers and visit dates
  - Not password protected
  - Under 200MB each

---

## ⚙️ Configuration

Default settings are ready to use, but you can customize in config.bat:

1. **Input Settings**
   - File types accepted (CSV, Excel)
   - Required visit data fields
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
1. Copy your medical visit data files to `input/`
2. Run the tool
3. Check `output/` for validation reports

### Advanced Use
- Use strict validation mode
- Include metadata in validation
- Process multiple visit files
- Generate detailed clinical reports

---

## 🔎 Troubleshooting

### Common Issues

1. **"Visit Data Format Not Recognized"**
   - Symptom: Tool can't read visit data structure
   - Solution: Check visit data fields and format

2. **"Temporal Validation Failed"**
   - Symptom: Visit date validation failed
   - Solution: Check visit date consistency and patient timeline

3. **"Clinical Validation Error"**
   - Symptom: Clinical standards validation failed
   - Solution: Verify clinical data meets standards

### Error Messages

- `[MIV001]`: Input file missing or invalid
- `[MIV002]`: Visit data format error
- `[MIV003]`: Temporal validation failure
- `[MIV004]`: Clinical validation error

---

## 📞 Support

- Check `logs/run_log.txt` for detailed error information
- Contact: data.support@organization.com
- Hours: Monday-Friday, 9am-5pm CST
- Response time: Within 1 business day

---

## 📝 Release Notes

### Current Version (1.1.0)
- Enhanced visit data validation
- Improved temporal consistency checking
- Better clinical standards compliance
- Faster processing speed

### Known Issues
- Some complex visit patterns may not be validated properly
- Very large files (>200MB) may cause memory issues
- Special characters in visit data may cause validation errors
- Workaround: Use standard visit data formats when possible

--- 