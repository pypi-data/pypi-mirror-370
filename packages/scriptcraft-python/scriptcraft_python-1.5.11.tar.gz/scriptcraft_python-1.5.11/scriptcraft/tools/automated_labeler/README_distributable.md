# Automated Labeler 🏷️

Automatically generate physical labels from Excel data files. Creates Word document with formatted labels ready for printing on standard label sheets.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This build was packaged on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📂 Directory Structure

```
automated_labeler_distributable/
├── input/                  # Place your Excel data files here
├── output/                # Generated Labels.docx file
├── logs/                  # Execution logs
├── scripts/               # Core implementation (no need to modify)
├── embed_py311/          # Embedded Python environment
├── config.bat            # Configuration settings
└── run.bat              # Start the labeler
```

---

## 🚀 Quick Start

1. **Prepare your data**:
   - Place Excel file with participant/sample data in `input/`
   - File should contain ID columns and visit information
   - Use any `.xlsx` file format
2. **Double-click `run.bat`**
3. **Check results** in `output/`:
   - `Labels.docx`: Word document with formatted labels
   - Ready for printing on standard label sheets

---

## 📋 Requirements

- Windows 10 or later
- 4GB RAM minimum
- 500MB free disk space
- Microsoft Word template support
- Files must be:
  - Excel format (.xlsx)
  - Contain ID and visit columns
  - Not password protected
  - Under 500MB each

---

## ⚙️ Configuration

Default settings work for most cases, but you can customize:

1. **Label Settings**
   - Label template format
   - Label dimensions
   - Text formatting
   - Font and size

2. **Input Settings**
   - Excel column mapping
   - Required data fields
   - Data validation rules

3. **Output Settings**
   - Word document format
   - Label layout
   - Print settings

---

## 📊 Example Usage

### Basic Label Generation
1. Copy Excel data file to `input/`
2. Run the labeler
3. Open `Labels.docx` from `output/`
4. Print on standard label sheets

### Custom Formatting
1. Excel file should contain:
   - Med_ID column (required)
   - Visit_ID column (required)
   - Any additional data for labels
2. Run the labeler
3. Labels automatically formatted for printing

---

## 🔎 Troubleshooting

### Common Issues

1. **"Excel File Not Found"**
   - Symptom: No input files detected
   - Solution: Add .xlsx file to input/ folder

2. **"Missing Required Columns"**
   - Symptom: ID columns not found
   - Solution: Ensure Excel has Med_ID and Visit_ID columns

3. **"Word Template Error"**
   - Symptom: Label formatting failed
   - Solution: Check template file integrity

### Error Messages

- `[AL001]`: No Excel input files found
- `[AL002]`: Missing required ID columns
- `[AL003]`: Word template processing error
- `[AL004]`: Label generation failed

---

## 📞 Support

- Check `logs/run_log.txt` for detailed error information
- Contact: data.support@organization.com
- Hours: Monday-Friday, 9am-5pm CST
- Response time: Within 1 business day

---

## 📝 Release Notes

### Current Version (2.1.0)
- Enhanced Excel data processing
- Improved Word document formatting
- Better error handling for missing data
- Updated label template design

### Known Issues
- Requires specific Excel column naming
- Limited to standard label sheet sizes
- Large datasets may take time to process
- Workaround: Split large files or use smaller batches

---
