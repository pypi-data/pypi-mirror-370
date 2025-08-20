
# Automated Labeler 🏷️

A Python tool for automatically generating labels in a DOCX template based on an input Excel sheet. Supports both development mode (scripts within a workspace) and domain-specific execution.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This build was packaged on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---


## 📦 Project Structure

```
If in Distributable:
automated_labeler_distributable/
├── input/                  # Place your Excel files here
├── output/                 # Generated Labels.docx file
├── logs/                   # Log file of the most recent run
├── scripts/
│   ├── main.py             # Entry point for label generation
│   ├── utils.py            # Helper functions (e.g., fill_full_page)
│   ├── common/             # Shared utilities
│   │   ├── common_utils.py
│   │   ├── file_path_utils.py
│   │   ├── logging_utils.py
│   │   ├── ... (other shared files)
│   └── __init__.py         # (Optional) package marker
├── embed_py311/            # Embedded Python environment
├── config.bat              # Predefined configuration (no need to edit)
└── run.bat                 # The entry point for execution
```

```
If in Dev Workspace:
Release Workspace/
├── input/                  # (Optional) Example Excel input for testing
├── output/                 # (Optional) Test outputs
├── logs/                   # Run logs
├── scripts/
│   ├── tools/
│   │   ├── automated_labeler/
│   │   │   ├── main.py
│   │   │   ├── utils.py
│   │   │   ├── __init__.py
│   ├── common/
│   │   ├── common_utils.py
│   │   ├── file_path_utils.py
│   │   ├── logging_utils.py
│   │   ├── ... (other shared files)
│   └── pipelines/
│       ├── pipeline_utils.py
│       ├── ... (other pipeline helpers)
├── templates/
│   ├── package_template/
│   ├── ... (other templates)
├── distributables/         # Output of packaged distributables
└── config.yaml             # Central config

```

---

## 🚀 Usage (Development)

To run directly:

```bash
python -m tools.automated_labeler.main --input_excel input.xlsx --template label_template.docx
```

- `--input_excel`: Path to the Excel file.
- `--template`: Path to the DOCX template.
- `--output_dir`: (Optional) Output directory (default: `output`).
- `--output_filename`: (Optional) Output file name (default: `Labels.docx`).

---

## ⚙️ Features

✅ Automatic placeholder replacement for up to 8 ID triplets.  
✅ Supports both `Development` and `Distributable` modes.  
✅ Chunk processing to ensure clean label formatting.  
✅ Structured logs to track your runs.

---

## 🔧 Dev Tips

- Update `DEFAULT_INPUT_FILE` and `DEFAULT_TEMPLATE_FILE` in `main.py` for your defaults.
- Use the logs in the `logs/` folder to debug or track progress.
- Check `utils.py` for customization (e.g., modifying `SETS_PER_PAGE`).

---

## 🗂️ Future Improvements

- Adding FAQ and troubleshooting.
- Integration with domain-level validation.
- Enhanced logging in Distributable mode.

---
