# Score Totals Checker 📊

Validate score calculations and totals in assessment data. Ensures mathematical accuracy and identifies discrepancies in scoring with comprehensive validation reporting.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This build was packaged on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📂 Directory Structure

```
score_totals_checker_distributable/
├── input/                  # Place your assessment data files here
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

1. **Place your assessment data files** in the `input/` folder
2. **Double-click `run.bat`**
3. **Find your validation reports** in the `output/` folder

---

## 📋 Requirements

- Windows 10 or later
- 4GB RAM minimum
- 1GB free disk space
- Input files must be:
  - CSV or Excel format (.csv, .xlsx)
  - Contain assessment scores and totals
  - Include calculation formulas if applicable
  - Not password protected
  - Under 100MB each

---

## ⚙️ Configuration

Default settings are ready to use, but you can customize in config.bat:

1. **Input Settings**
   - File types accepted (CSV, Excel)
   - Required score fields
   - Calculation validation settings

2. **Output Settings**
   - Report format and detail level
   - Output file naming
   - Output location

3. **Processing Options**
   - Score validation strictness
   - Error handling
   - Performance settings

---

## 📊 Example Usage

### Basic Use
1. Copy your assessment data files to `input/`
2. Run the tool
3. Check `output/` for validation reports

### Advanced Use
- Use strict score validation mode
- Include metadata in validation
- Process multiple assessment files
- Generate detailed discrepancy reports

---

## 🔎 Troubleshooting

### Common Issues

1. **"Score Data Format Not Recognized"**
   - Symptom: Tool can't read score data structure
   - Solution: Check score data fields and format

2. **"Calculation Validation Failed"**
   - Symptom: Score calculation validation failed
   - Solution: Check calculation formulas and mathematical logic

3. **"Total Validation Error"**
   - Symptom: Total score validation failed
   - Solution: Verify total calculation accuracy and expected values

### Error Messages

- `[STC001]`: Input file missing or invalid
- `[STC002]`: Score data format error
- `[STC003]`: Calculation validation failure
- `[STC004]`: Total validation error

---

## 📞 Support

- Check `logs/run_log.txt` for detailed error information
- Contact: data.support@organization.com
- Hours: Monday-Friday, 9am-5pm CST
- Response time: Within 1 business day

---

## 📝 Release Notes

### Current Version (1.1.0)
- Enhanced score validation algorithms
- Improved calculation verification
- Better discrepancy detection
- Faster processing speed

### Known Issues
- Some complex calculation formulas may not be validated properly
- Very large files (>100MB) may cause memory issues
- Special characters in score data may cause validation errors
- Workaround: Use standard score formats when possible

--- 