# Data Content Comparer 🔍

Compare data files to identify differences, changes, and inconsistencies. Perfect for validating data updates and ensuring data consistency.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This build was packaged on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📂 Directory Structure

```
data_content_comparer_distributable/
├── input/                  # Place your files to compare here
├── output/                # Comparison reports
├── logs/                  # Detailed execution logs
├── scripts/               # Core implementation (no need to modify)
├── embed_py311/          # Embedded Python environment
├── config.bat            # Configuration settings
└── run.bat              # Start the comparer
```

---

## 🚀 Quick Start

### Option 1: All Domains Comparison (Recommended)
1. **Ensure domain files exist** in the expected locations:
   - `data/domains/Clinical/old_data/HD Release 6 Clinical_FINAL.csv`
   - `data/domains/Clinical/RP_HD 7_Clinical.xlsx`
   - (Similar structure for Biomarkers, Genomics, Imaging)
2. **Edit `config.bat`** to set:
   ```
   set MODE=release_consistency
   set OUTPUT_DIR=output
   ```
3. **Double-click `run.bat`**
4. **Check results** in the `output/` folder (one subfolder per domain)

### Option 2: Individual Domain Comparison
1. **Ensure domain files exist** in the expected locations:
   - `data/domains/Clinical/old_data/HD Release 6 Clinical_FINAL.csv`
   - `data/domains/Clinical/RP_HD 7_Clinical.xlsx`
2. **Edit `config.bat`** to set:
   ```
   set MODE=release_consistency
   set DOMAIN=Clinical
   set OUTPUT_DIR=output
   ```
3. **Double-click `run.bat`**
4. **Check results** in the `output/Clinical/` folder

### Option 3: Manual File Comparison
1. **Place your files** in the `input/` folder:
   - Old/reference file (e.g., `old_data.csv`)
   - New/comparison file (e.g., `new_data.csv`)
2. **Edit `config.bat`** to set:
   ```
   set MODE=release_consistency
   set INPUT_PATHS=input/old_data.csv input/new_data.csv
   set OUTPUT_DIR=output
   ```
3. **Double-click `run.bat`**
4. **Check results** in the `output/` folder

---

## 📋 Requirements

- Windows 10 or later
- 4GB RAM minimum
- 500MB free disk space
- Files must be:
  - Excel (.xlsx) or CSV
  - Not password protected
  - Have matching column names
  - Under 1GB each

---

## ⚙️ Configuration

### Comparison Modes

1. **`release_consistency`** (Recommended)
   - Release-to-release comparison (R5 vs R6)
   - Handles missing values and data type alignment
   - Domain-specific configurations
   - Best for structured research data

2. **`standard`**
   - Basic file-to-file comparison
   - Good for general data validation
   - Simple difference detection

3. **`rhq_mode`**
   - Specialized for RHQ residential history forms
   - Handles form-specific data structures

4. **`domain_old_vs_new`**
   - Domain-specific old vs new comparison
   - Uses domain directory structure

### Configuration Settings

Edit `config.bat` to customize:

```batch
:: Comparison Settings
set MODE=release_consistency
set INPUT_PATHS=input/file1.csv input/file2.csv
set DOMAIN=Clinical
set OUTPUT_DIR=output
set OUTPUT_FILENAME=comparison_report.xlsx

:: Processing Settings
set DEBUG=false
set COMPARISON_TYPE=full
set OUTPUT_FORMAT=xlsx
```

---

## 📊 Example Usage

### Example 1: All Domains Comparison
**Scenario**: Compare all domains (Biomarkers, Clinical, Genomics, Imaging) in one run

1. **Files**: Ensure all domain files exist in expected locations
2. **Config**:
   ```batch
   set MODE=release_consistency
   set OUTPUT_DIR=output
   ```
3. **Run**: Double-click `run.bat`
4. **Results**: Check `output/` for subfolders:
   - `output/Biomarkers/Biomarkers_filtered_rows.csv`
   - `output/Clinical/Clinical_filtered_rows.csv`
   - `output/Genomics/Genomics_filtered_rows.csv`
   - `output/Imaging/Imaging_filtered_rows.csv`

### Example 2: Individual Domain Comparison
**Scenario**: Compare Clinical domain R6 vs R7 releases

1. **Files**: Ensure R6/R7 files exist in domain directories
2. **Config**:
   ```batch
   set MODE=release_consistency
   set DOMAIN=Clinical
   set OUTPUT_DIR=output
   ```
3. **Run**: Double-click `run.bat`
4. **Results**: Check `output/Clinical/Clinical_filtered_rows.csv`

### Example 3: Manual File Comparison
**Scenario**: Compare two versions of a dataset

1. **Files**: Place `old_version.csv` and `new_version.csv` in `input/`
2. **Config**:
   ```batch
   set MODE=release_consistency
   set INPUT_PATHS=input/old_version.csv input/new_version.csv
   set OUTPUT_DIR=output
   ```
3. **Run**: Double-click `run.bat`
4. **Results**: Check `output/` for comparison reports

---

## 🔎 Troubleshooting

### Common Issues

1. **"Files Not Found"**
   - Symptom: Can't find input files
   - Solution: Verify files are in input folder or domain directories

2. **"Column Mismatch"**
   - Symptom: Different columns in files
   - Solution: Check column names match between files

3. **"Memory Error"**
   - Symptom: Process stops with memory error
   - Solution: Use smaller files or enable chunked processing

4. **"Mode Not Found"**
   - Symptom: Unknown comparison mode error
   - Solution: Check MODE setting in config.bat

5. **"Domain Files Missing"**
   - Symptom: Can't find R5/R6 files for domain
   - Solution: Verify domain files exist in expected locations

### Error Messages

- `[DC001]`: Missing input files
- `[DC002]`: Invalid file format
- `[DC003]`: Column mismatch
- `[DC004]`: Processing error
- `[DC005]`: Mode not supported
- `[DC006]`: Domain files not found

### Debug Mode

Enable debug mode for detailed information:
```batch
set DEBUG=true
```

Check `logs/run_log.txt` for detailed error information and processing steps.

---

## 📞 Support

- Check `logs/run_log.txt` for detailed error information
- Contact: data.support@organization.com
- Hours: Monday-Friday, 9am-5pm CST
- Response time: Within 1 business day

---

## 📝 Release Notes

### Current Version (2.0.0)
- ✅ Consolidated release_consistency_checker functionality
- ✅ Added support for both manual and domain-based comparison modes
- ✅ Enhanced plugin architecture with multiple comparison modes
- ✅ Improved error handling and validation
- ✅ Better performance for large datasets
- ✅ Comprehensive usage examples and documentation
- ✅ Support for R5 vs R6 release comparisons
- ✅ Domain-specific configurations and processing

### Previous Version (1.5.0)
- Added quick comparison mode
- Improved difference detection
- Better memory handling
- Enhanced reporting format

### Known Issues
- Maximum 1GB per input file
- Some Excel formulas may be lost during processing
- Special characters in headers may cause issues
- Workaround: Use simple column names without special characters 