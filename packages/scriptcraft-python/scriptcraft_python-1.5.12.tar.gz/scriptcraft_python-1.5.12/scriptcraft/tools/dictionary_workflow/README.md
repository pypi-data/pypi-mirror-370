# 📚 Dictionary Workflow Tool

A comprehensive tool that handles the complete dictionary enhancement workflow, consolidating the functionality of three separate enhancement packages into a single, streamlined workflow.

## Overview

The Dictionary Workflow Tool provides a unified interface for:
1. **Preparing supplements** - Merging and cleaning supplement files
2. **Splitting supplements by domain** - Organizing supplements by research domain
3. **Enhancing dictionaries** - Adding domain-specific supplements to dictionaries

## Features

- **Complete Workflow**: Single tool handles the entire dictionary enhancement process
- **Flexible Steps**: Run individual steps or the complete workflow
- **Multiple Strategies**: Support for different merge and enhancement strategies
- **Domain-Aware**: Automatic domain detection and processing
- **Data Cleaning**: Built-in data cleaning and validation
- **Comprehensive Logging**: Detailed progress tracking with emojis

## Usage

### Development Environment
```bash
python -m scriptcraft.tools.dictionary_workflow.main \
    --input-paths supplement1.csv supplement2.csv \
    --dictionary-paths dict1.csv dict2.csv \
    --output-dir output \
    --workflow-steps prepare split enhance
```

### Distributable Environment
```bash
python main.py \
    --input-paths supplement1.csv supplement2.csv \
    --dictionary-paths dict1.csv dict2.csv \
    --output-dir output \
    --workflow-steps prepare split enhance
```

## Arguments

### Required Arguments
- `--input-paths`: List of supplement file paths to process
- `--dictionary-paths`: List of dictionary file paths to enhance

### Optional Arguments
- `--output-dir`: Output directory (default: output)
- `--workflow-steps`: Workflow steps to run (choices: prepare, split, enhance, default: all)
- `--merge-strategy`: Strategy for merging supplements (choices: outer, inner, left, right, default: outer)
- `--enhancement-strategy`: Strategy for enhancing dictionaries (choices: append, merge, replace, default: append)
- `--domain-column`: Column name containing domain information (default: domain)
- `--clean-data`: Clean data during processing (default: True)
- `--no-clean-data`: Disable data cleaning during processing

## Workflow Steps

### 1. Prepare Supplements
- Merges multiple supplement files into a single dataset
- Cleans and validates the merged data
- Removes duplicates and handles missing values
- Output: `prepared_supplements.csv`

### 2. Split Supplements by Domain
- Splits prepared supplements by domain
- Creates domain-specific supplement files
- Organizes data for targeted dictionary enhancement
- Output: `split_supplements/supplements_{domain}.csv`

### 3. Enhance Dictionaries
- Enhances dictionaries with domain-specific supplements
- Applies chosen enhancement strategy
- Creates enhanced dictionary files
- Output: `enhanced_dictionaries/{dictionary}_enhanced.csv`

## Enhancement Strategies

### Append Strategy
- Adds supplement data to the end of dictionaries
- Preserves all original dictionary entries
- Simple and safe approach

### Merge Strategy
- Merges supplements with dictionaries on common columns
- Handles overlapping data intelligently
- More sophisticated data integration

### Replace Strategy
- Replaces dictionary content with supplement data
- Use with caution - may lose original data
- Useful for complete dictionary updates

## Output Structure

```
output/
├── prepared_supplements.csv          # Merged and cleaned supplements
├── split_supplements/                # Domain-specific supplements
│   ├── supplements_clinical.csv
│   ├── supplements_biomarkers.csv
│   └── supplements_genomics.csv
└── enhanced_dictionaries/            # Enhanced dictionary files
    ├── clinical_dict_enhanced.csv
    ├── biomarkers_dict_enhanced.csv
    └── genomics_dict_enhanced.csv
```

## Configuration

The tool uses centralized configuration from `config.yaml`:

```yaml
tools:
  dictionary_workflow:
    description: "📚 Complete dictionary enhancement workflow tool"
    default_workflow_steps: ["prepare", "split", "enhance"]
    default_merge_strategy: "outer"
    default_enhancement_strategy: "append"
```

## Examples

### Basic Usage
```bash
# Run complete workflow
python -m scriptcraft.tools.dictionary_workflow.main \
    --input-paths supplements.csv \
    --dictionary-paths clinical_dict.csv biomarkers_dict.csv
```

### Custom Workflow Steps
```bash
# Only prepare and split supplements
python -m scriptcraft.tools.dictionary_workflow.main \
    --input-paths supplements.csv \
    --dictionary-paths dict.csv \
    --workflow-steps prepare split
```

### Custom Enhancement Strategy
```bash
# Use merge strategy for enhancement
python -m scriptcraft.tools.dictionary_workflow.main \
    --input-paths supplements.csv \
    --dictionary-paths dict.csv \
    --enhancement-strategy merge
```

## Integration

This tool consolidates the functionality previously provided by:
- `supplement_prepper`: Prepare and merge supplements
- `supplement_splitter`: Split supplements by domain  
- `dictionary_supplementer`: Enhance dictionaries with supplements

The consolidated approach provides better workflow management, reduced complexity, and improved maintainability.

## Dependencies

- pandas: Data manipulation and processing
- pathlib: Path handling
- scriptcraft.common: Shared utilities and base classes

## Error Handling

The tool provides comprehensive error handling:
- Validates input files exist and are readable
- Checks for required columns in data files
- Handles missing domains gracefully
- Provides clear error messages with context

## Logging

The tool uses the centralized logging system with emoji indicators:
- 🚀 Starting workflow
- 📋 Preparing supplements
- ✂️ Splitting by domain
- 🔧 Enhancing dictionaries
- ✅ Step completion
- ❌ Error conditions
- 📊 Workflow summary

## Version History

- **1.0.0**: Initial release with complete workflow consolidation 