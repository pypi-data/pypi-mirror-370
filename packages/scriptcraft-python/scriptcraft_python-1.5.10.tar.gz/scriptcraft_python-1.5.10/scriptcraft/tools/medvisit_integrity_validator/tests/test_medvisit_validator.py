"""
Tests for the MedVisit Integrity Validator
"""

import os
import pandas as pd
import pytest
from scriptcraft.tools.medvisit_integrity_validator.tool import MedVisitIntegrityValidator

@pytest.fixture
def sample_data():
    """Create sample dataframes for testing."""
    old_data = pd.DataFrame({
        'Med_ID': [1, 1, 2, 2],
        'Visit_ID': [1, 2, 1, 2],
        'Value': ['A', 'B', 'C', 'D']
    })
    
    new_data = pd.DataFrame({
        'Med_ID': [1, 1, 2],  # Missing Med_ID=2, Visit_ID=2
        'Visit_ID': [1, 2, 1],
        'Value': ['A', 'B', 'C']
    })
    
    return old_data, new_data

@pytest.fixture
def temp_files(tmp_path, sample_data):
    """Create temporary files for testing."""
    old_data, new_data = sample_data
    
    # Create domain directory
    domain_dir = tmp_path / "Biomarkers"
    domain_dir.mkdir()
    
    # Save test files
    old_file = domain_dir / "HD Release 6 Biomarkers_FINAL.csv"
    new_file = domain_dir / "HD6 + New data_Biomarkers---MatthewReviewPending.xlsx"
    
    old_data.to_csv(old_file, index=False)
    new_data.to_excel(new_file, index=False)
    
    return tmp_path

def test_medvisit_integrity_validator(temp_files) -> None:
    """Test the main validator function."""
    # Setup
    output_path = temp_files / "output.xlsx"
    
    # Run validator
    run_medvisit_integrity_validator(
        domain="Biomarkers",
        input_path=None,  # Not used in this function
        output_path=str(output_path),
        paths={'input_dir': str(temp_files)}
    )
    
    # Verify output file exists
    assert output_path.exists()
    
    # Read results
    with pd.ExcelFile(output_path) as xls:
        missing_in_new = pd.read_excel(xls, "Missing in New")
        missing_in_old = pd.read_excel(xls, "Missing in Old")
    
    # Verify missing combinations
    assert len(missing_in_new) == 1
    assert missing_in_new.iloc[0]['Med_ID'] == 2
    assert missing_in_new.iloc[0]['Visit_ID'] == 2
    assert len(missing_in_old) == 0

def test_medvisit_integrity_validator_no_mapping() -> None:
    """Test validator behavior when no file mapping exists for domain."""
    result = run_medvisit_integrity_validator(
        domain="NonexistentDomain",
        input_path=None,
        output_path="dummy.xlsx",
        paths={}
    )
    assert result is None  # Function should return None when skipping

def test_medvisit_integrity_validator_identical_data(temp_files) -> None:
    """Test validator with identical old and new datasets."""
    # Setup - create identical datasets
    data = pd.DataFrame({
        'Med_ID': [1, 2],
        'Visit_ID': [1, 1],
        'Value': ['A', 'B']
    })
    
    domain_dir = temp_files / "Biomarkers"
    domain_dir.mkdir(exist_ok=True)
    
    data.to_csv(domain_dir / "HD Release 6 Biomarkers_FINAL.csv", index=False)
    data.to_excel(domain_dir / "HD6 + New data_Biomarkers---MatthewReviewPending.xlsx", index=False)
    
    output_path = temp_files / "output_identical.xlsx"
    
    # Run validator
    run_medvisit_integrity_validator(
        domain="Biomarkers",
        input_path=None,
        output_path=str(output_path),
        paths={'input_dir': str(temp_files)}
    )
    
    # Verify results
    with pd.ExcelFile(output_path) as xls:
        missing_in_new = pd.read_excel(xls, "Missing in New")
        missing_in_old = pd.read_excel(xls, "Missing in Old")
    
    assert len(missing_in_new) == 0
    assert len(missing_in_old) == 0 