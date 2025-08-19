---

### 📄 README_distributable.md

# RHQ Form Autofiller 📝

Automatically fill RHQ (Research Health Questionnaire) forms using data from various sources. Streamlines form completion and reduces manual errors with comprehensive validation and reporting.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This build was packaged on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📂 Directory Structure

```
rhq_form_autofiller_distributable/
├── input/                  # Place your data files and form templates here
├── output/                # Filled forms and reports
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
2. **Place your form templates** in the `input/` folder
3. **Double-click `run.bat`**
4. **Find your filled forms** in the `output/` folder

---

## 📋 Requirements

- Windows 10 or later
- 4GB RAM minimum
- 1GB free disk space
- Input files must be:
  - Data files: CSV or Excel format (.csv, .xlsx)
  - Form templates: Word document format (.docx)
  - Contain required form fields and data
  - Not password protected
  - Under 100MB each

---

## ⚙️ Configuration

Default settings are ready to use, but you can customize in config.bat:

1. **Input Settings**
   - File types accepted (CSV, Excel, Word)
   - Required data fields
   - Form template settings

2. **Output Settings**
   - Output format and detail level
   - Output file naming
   - Output location

3. **Processing Options**
   - Form filling validation
   - Error handling
   - Performance settings

---

## 📊 Example Usage

### Basic Use
1. Copy your data files to `input/`
2. Copy your form templates to `input/`
3. Run the tool
4. Check `output/` for filled forms

### Advanced Use
- Use strict validation mode
- Include metadata in forms
- Process multiple form templates
- Generate detailed completion reports

---

## 🔎 Troubleshooting

### Common Issues

1. **"Form Template Not Recognized"**
   - Symptom: Tool can't read form template
   - Solution: Check template format and required fields

2. **"Data Mapping Failed"**
   - Symptom: Data mapping to form fields failed
   - Solution: Check data format and field mapping

3. **"Form Generation Error"**
   - Symptom: Filled form generation failed
   - Solution: Verify template compatibility and output permissions

### Error Messages

- `[RFA001]`: Input file missing or invalid
- `[RFA002]`: Form template error
- `[RFA003]`: Data mapping failure
- `[RFA004]`: Form generation error

---

## 📞 Support

- Check `logs/run_log.txt` for detailed error information
- Contact: data.support@organization.com
- Hours: Monday-Friday, 9am-5pm CST
- Response time: Within 1 business day

---

## 📝 Release Notes

### Current Version (1.1.0)
- Enhanced form automation
- Improved field mapping
- Better validation and verification
- Faster processing speed

### Known Issues
- Some complex form templates may not be processed properly
- Very large files (>100MB) may cause memory issues
- Special characters in form data may cause filling errors
- Workaround: Use standard form templates when possible

---
```

Let me know if you'd like to tweak these or expand any sections!
