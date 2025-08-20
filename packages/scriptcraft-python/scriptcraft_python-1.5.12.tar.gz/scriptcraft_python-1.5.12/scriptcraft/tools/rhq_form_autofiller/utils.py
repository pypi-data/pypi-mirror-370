"""
RHQ Form Autofiller Utilities

This module provides utility functions for the RHQ Form Autofiller tool.
It includes functions for data processing, browser automation, and form filling.
"""

import re
import time
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# === Environment Detection & Import Setup ===
# Import the environment detection module
from .env import setup_environment

# Set up environment and get imports
IS_DISTRIBUTABLE = setup_environment()

# Import based on environment
if IS_DISTRIBUTABLE:
    # Distributable imports
    from common.logging.core import log_and_print
    from common.io.data_loading import load_data
    from common.core.config import Config
else:
    # Development imports
    from scriptcraft.common.logging.core import log_and_print
    from scriptcraft.common.io.data_loading import load_data
    from scriptcraft.common.core.config import Config

# === 🌐 Mappings for Field Labels ===
FIELD_LABEL_MAPS = {
    'en': {
        "StreetNumber": "Street Number",
        "Zip Code": "ZIP Code",
        "State/Province": "State/Province/Department",
        # ... any other special cases
    },
    'es': {
        "StreetNumber": "Número de la Calle",
        "Street Name": "Nombre de la Calle",
        "Additional Address": "Dirección adicional (colonia, barrio, número de apartamento)",
        "City/Town/Municipality": "Municipalidad/Ciudad/Pueblo",
        "State/Province": "Estado/Provincia/Departamento",
        "Zip Code": "Código Postal",
        "Country": "País",
        "From Date": "Desde (Fecha)",
        "To Date": "Hasta (Fecha)",
        "Comments": "Comentarios",
        "Questionable Validity": "Questionable Validity",
        "Admin Notes": "Admin Notes",
        "Add Another Address": "Agrega otra dirección",
    }
}

def detect_form_language(driver, logger=None) -> str:
    """
    Detect the form language by looking at the main header.
    Returns 'en' or 'es' (defaults to 'en' if detection fails).
    """
    try:
        # Look for the main header which should contain language-specific text
        try:
            # Try to find h3 elements which typically contain the main titles
            headers = driver.find_elements(By.TAG_NAME, "h3")
            for header in headers:
                header_text = header.text.strip()
                if "Historia Residencial" in header_text:
                    log_msg = "🌍 Detected form language: es"
                    if logger:
                        logger.info(log_msg)
                    else:
                        log_and_print(log_msg)
                    return 'es'
                elif "Residential History" in header_text:
                    log_msg = "🌍 Detected form language: en"
                    if logger:
                        logger.info(log_msg)
                    else:
                        log_and_print(log_msg)
                    return 'en'
        except Exception:
            pass
        
        # Fallback: check page source for key phrases (but only the obvious ones)
        page_text = driver.page_source
        if "Historia Residencial" in page_text:
            log_msg = "🌍 Detected form language: es (from page source)"
            if logger:
                logger.info(log_msg)
            else:
                log_and_print(log_msg)
            return 'es'
        elif "Residential History" in page_text:
            log_msg = "🌍 Detected form language: en (from page source)"
            if logger:
                logger.info(log_msg)
            else:
                log_and_print(log_msg)
            return 'en'
        
        # If no language detected, log warning and default to English
        log_msg = "⚠️ Could not detect form language, defaulting to English"
        if logger:
            logger.warning(log_msg)
        else:
            log_and_print(log_msg, level="warning")
        return 'en'
        
    except Exception as e:
        log_msg = f"⚠️ Error detecting form language: {e}, defaulting to English"
        if logger:
            logger.warning(log_msg)
        else:
            log_and_print(log_msg, level="warning")
        return 'en'

BLOCK_COLUMNS = [
    "StreetNumber", "Street Name", "Additional Address",
    "City/Town/Municipality", "State/Province", "Zip Code",
    "Country", "From Date", "To Date", "Comments",
    "Questionable Validity", "Admin Notes"
]


def get_age_period_suffixes(df: pd.DataFrame) -> list:
    return [col for col in df.columns if col.startswith("AgePeriod")]


def get_panel_index(age_period: str) -> int:
    return {
        "0-10": 0, "11-20": 1, "21-30": 2, "31-40": 3,
        "41-50": 4, "51-60": 5, "61-70": 6, "71-80": 7,
        "81-90": 8, "91-100": 9, "101-110": 10
    }.get(age_period, 0)


def is_real_address(block_data: dict) -> bool:
    for v in block_data.values():
        if pd.notna(v) and str(v).strip() != "" and str(v).strip().upper() != "MISSING":
            return True
    return False


def build_panels_data(row, age_period_cols) -> list:
    panels_data = [[] for _ in range(11)]
    for age_col in age_period_cols:
        suffix = "" if age_col == "AgePeriod (this is the decade of life starting at 0)" else age_col.replace("AgePeriod (this is the decade of life starting at 0)", "")
        age_period = str(row.get(age_col, "")).strip()
        if not age_period:
            continue
        panel_idx = get_panel_index(age_period)
        block_data = {col: row.get(f"{col}{suffix}", "") for col in BLOCK_COLUMNS}
        if is_real_address(block_data):
            panels_data[panel_idx].append(block_data)
    return panels_data


# === 📄 Load Excel and Build Address Data ===
def build_address_data(filepath: Path, med_id_filter: str = None) -> dict:
    if not filepath.exists():
        raise FileNotFoundError(f"❌ Input file not found: {filepath}")
    
    df = load_data(filepath)
    if df.empty:
        raise ValueError(f"❌ Excel file is empty: {filepath}")
    
    # Ensure Med_ID is a column, not index
    if df.index.name == "Med_ID":
        df = df.reset_index()
    elif "Med_ID" not in df.columns:
        raise ValueError("Med_ID not found in data")
    
    age_period_cols = get_age_period_suffixes(df)

    data = {}
    for _, row in df.iterrows():
        med_id = row["Med_ID"]
        if med_id_filter and str(med_id) != str(med_id_filter):
            continue

        # === 🔧 Convert numeric columns to clean strings ===
        for col in BLOCK_COLUMNS:
            for suffix in [""] + [f".{i}" for i in range(1, 11)]:
                key = f"{col}{suffix}"
                if key in row:
                    val = row[key]
                    if pd.isna(val):
                        row[key] = ""
                    elif isinstance(val, float):
                        # Convert to int if it's an integer float
                        if val.is_integer():
                            row[key] = str(int(val))
                        else:
                            row[key] = str(val)

        # Initialize panel data structure
        panels_data = build_panels_data(row, age_period_cols)

        data[med_id] = panels_data

    return data


# === 🌐 Browser Launcher ===
def launch_browser() -> webdriver.Chrome:
    options = Options()
    options.add_experimental_option("detach", True)
    return webdriver.Chrome(options=options)


# === 📋 High-level Panel Filler ===
def fill_panel(driver, panel_idx: int, address_blocks: list, logger=None) -> None:
    try:
        # Detect form language before filling
        form_language = detect_form_language(driver, logger)
        
        open_panel(driver, panel_idx)
        panel = get_panel_element(driver, panel_idx)
        ensure_address_blocks(driver, panel, len(address_blocks), form_language)
        remove_extra_address_blocks(driver, panel, len(address_blocks))
        fill_all_blocks(panel, address_blocks, panel_idx, form_language, logger)
    except Exception as e:
        log_msg = f"⚠️ Could not open/fill panel {panel_idx}: {e}"
        if logger:
            logger.warning(log_msg)
        else:
            log_and_print(log_msg, level="warning")


# === 📂 Open the Panel ===
def open_panel(driver, panel_idx: int) -> None:
    try:
        # Try the standard ID format first
        panel_header = driver.find_element(By.ID, f"mat-expansion-panel-header-{panel_idx}")
        log_and_print(f"🔍 Opening Panel {panel_idx}...")
        panel_header.click()
        time.sleep(1)
        return
    except:
        pass
    
    try:
        # If standard ID doesn't work, try finding by position in the list
        panel_headers = driver.find_elements(By.CSS_SELECTOR, "mat-expansion-panel-header")
        if panel_idx < len(panel_headers):
            panel_header = panel_headers[panel_idx]
            log_and_print(f"🔍 Opening Panel {panel_idx} (by position)...")
            panel_header.click()
            time.sleep(1)
            return
    except:
        pass
    
    # If both methods fail, raise an error
    raise Exception(f"Could not find panel header for panel {panel_idx}")


# === 📂 Get Panel Element ===
def get_panel_element(driver, panel_idx: int) -> None:
    try:
        # Try standard xpath first
        return driver.find_element(By.XPATH, f"//mat-expansion-panel[{panel_idx+1}]")
    except:
        # Fallback: get all panels and select by index
        panels = driver.find_elements(By.TAG_NAME, "mat-expansion-panel")
        if panel_idx < len(panels):
            return panels[panel_idx]
        else:
            raise Exception(f"Could not find panel element for panel {panel_idx}")


# === 🗑️ Remove Extra Address Blocks ===
def remove_extra_address_blocks(driver, panel, required_blocks: int) -> None:
    panel_content = panel.find_element(By.CSS_SELECTOR, "div.panel-content")
    address_forms = panel_content.find_elements(By.TAG_NAME, "form")
    n_existing = len(address_forms)
    
    n_to_remove = n_existing - required_blocks
    if n_to_remove <= 0:
        log_and_print("✅ No extra address blocks to remove.")
        return

    log_and_print(f"🗑️ Removing {n_to_remove} extra address block(s).")

    # Remove extras starting from the last (to avoid index shifting)
    for i in range(n_existing - 1, n_existing - n_to_remove - 1, -1):
        trash_button = address_forms[i].find_element(By.CSS_SELECTOR, ".fas.fa-trash")
        trash_button.click()
        log_and_print(f"🗑️ Removed address block at index {i}.")
        time.sleep(1)

        # Confirm deletion
        try:
            confirm_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Confirm')]")
            confirm_button.click()
            log_and_print("✅ Confirmed deletion of address block.")
            time.sleep(1)  # Optional: slight delay to ensure dialog closes
        except Exception as e:
            log_and_print(f"⚠️ Could not confirm deletion: {e}", level="warning")


# === ➕ Ensure Enough Address Blocks ===
def ensure_address_blocks(driver, panel, required_blocks: int, form_language: str = 'en') -> None:
    # Find the panel-content div that contains all address forms
    panel_content = panel.find_element(By.CSS_SELECTOR, "div.panel-content")

    # Count all forms inside this panel-content
    address_forms = panel_content.find_elements(By.TAG_NAME, "form")
    n_existing = len(address_forms)

    log_and_print(f"ℹ️ Address forms detected: {n_existing}")

    # Determine how many new address blocks need to be added
    n_to_add = required_blocks - n_existing
    for _ in range(n_to_add):
        add_button = None
        
        # Try to find the "Add Another Address" button based on language
        try:
            # First try: Use the language-specific text
            button_text = FIELD_LABEL_MAPS[form_language].get("Add Another Address")
            add_button = panel.find_element(By.XPATH, f".//button[.//span[contains(text(), '{button_text}')]]")
        except:
            try:
                # Second try: Try the English version as fallback
                add_button = panel.find_element(By.XPATH, ".//button[.//span[contains(text(), 'Add Another Address')]]")
            except:
                try:
                    # Third try: Try the Spanish version as fallback
                    add_button = panel.find_element(By.XPATH, ".//button[.//span[contains(text(), 'Agrega otra dirección')]]")
                except:
                    try:
                        # Fourth try: Look for button with address book icon (more generic)
                        add_button = panel.find_element(By.XPATH, ".//button[.//i[contains(@class, 'fa-address-book')]]")
                    except:
                        pass
        
        if add_button:
            add_button.click()
            log_and_print("➕ Added another address block.")
            time.sleep(1)
        else:
            log_and_print("⚠️ Could not find 'Add Another Address' button", level="warning")
            break


# === 📝 Fill All Blocks in Panel ===
def fill_all_blocks(panel, address_blocks: list, panel_idx: int, form_language: str, logger=None) -> None:
    panel_content = panel.find_element(By.CSS_SELECTOR, "div.panel-content")
    address_forms = panel_content.find_elements(By.TAG_NAME, "form")

    for idx, (form, block_data) in enumerate(zip(address_forms, address_blocks)):
        log_msg = f"📝 Filling address block {idx+1} in panel {panel_idx}..."
        if logger:
            logger.info(log_msg)
        else:
            log_and_print(log_msg)
        fill_single_block(form, block_data, form_language, logger)


# === 📝 Fill a Single Address Block ===
def fill_single_block(form, block_data: dict, form_language: str, logger=None) -> None:
    for col, val in block_data.items():
        # Skip empty, nan, or "MISSING" values
        if pd.isna(val) or not str(val).strip() or str(val).strip().upper() == "MISSING":
            log_msg = f"⚠️ Skipping empty/missing field: {col}"
            if logger:
                logger.info(log_msg)
            else:
                log_and_print(log_msg)
            continue

        try:
            if col == "Questionable Validity":
                fill_checkbox(form, val, form_language, logger)
                continue

            # Format numeric values properly
            if col in ["StreetNumber", "Zip Code"]:
                if isinstance(val, (int, float)):
                    val = str(int(val))  # Remove decimal for numeric address fields
            
            fill_input_field(form, col, val, form_language, logger)
        except Exception as e:
            log_msg = f"⚠️ Could not enter {col}: {e}"
            if logger:
                logger.warning(log_msg)
            else:
                log_and_print(log_msg, level="warning")


# === ☑️ Enhanced Checkbox Filling Helper ===
def fill_checkbox(panel, val: str, form_language: str, logger=None) -> None:
    if str(val).strip() == "1":
        try:
            # First try: Find checkbox by position (usually the last checkbox in address forms)
            checkboxes = panel.find_elements(By.CSS_SELECTOR, "mat-checkbox")
            if checkboxes:
                checkbox = checkboxes[-1]  # Usually the last checkbox is "Questionable Validity"
                input_checkbox = checkbox.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                if not input_checkbox.is_selected():
                    checkbox.click()
                    log_msg = f"✅ {checkbox_label}: Checked (1)"
                    if logger:
                        logger.info(log_msg)
                    else:
                        log_and_print(log_msg)
                return
        except:
            pass
            
        try:
            # Fallback: Use language-specific label
            checkbox_label = FIELD_LABEL_MAPS[form_language].get("Questionable Validity", "Questionable Validity")
            checkbox = panel.find_element(By.XPATH, f".//mat-checkbox[.//span[contains(text(), '{checkbox_label}')]]")
            input_checkbox = checkbox.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
            if not input_checkbox.is_selected():
                checkbox.click()
                log_msg = f"✅ {checkbox_label}: Checked (1)"
                if logger:
                    logger.info(log_msg)
                else:
                    log_and_print(log_msg)
        except Exception as e:
            log_msg = f"⚠️ Could not find/check Questionable Validity checkbox: {e}"
            if logger:
                logger.warning(log_msg)
            else:
                log_and_print(log_msg, level="warning")


# === 📝 Safe Input Field Filler ===
def fill_input_field(panel, label: str, value: str, form_language: str, logger=None) -> None:
    """
    Fill input field using label mapping with enhanced fallbacks for robustness.
    """
    # Get the expected label for this language
    real_label = FIELD_LABEL_MAPS[form_language].get(label, label)
    
    form_field = None
    
    try:
        # First try: Exact label match
        form_field = panel.find_element(
            By.XPATH,
            f".//mat-form-field[.//mat-label[normalize-space(text())='{real_label}']]"
        )
    except:
        try:
            # Second try: Case-insensitive match
            form_field = panel.find_element(
                By.XPATH,
                f".//mat-form-field[.//mat-label[translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')=translate('{real_label}', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')]]"
            )
        except:
            try:
                # Third try: Partial text match (contains)
                form_field = panel.find_element(
                    By.XPATH,
                    f".//mat-form-field[.//mat-label[contains(normalize-space(text()), '{real_label}')]]"
                )
            except:
                try:
                    # Fourth try: If it's a mapped field, try the original English label as fallback
                    if label in FIELD_LABEL_MAPS[form_language] and form_language != 'en':
                        english_label = FIELD_LABEL_MAPS['en'].get(label, label)
                        form_field = panel.find_element(
                            By.XPATH,
                            f".//mat-form-field[.//mat-label[normalize-space(text())='{english_label}']]"
                        )
                except:
                    pass

    if form_field is None:
        log_msg = f"⚠️ Could not find field for {label} (expected label: {real_label})"
        if logger:
            logger.warning(log_msg)
        else:
            log_and_print(log_msg, level="warning")
        return

    try:
        input_element = form_field.find_element(By.CSS_SELECTOR, "input, textarea")

        # Clear the field first
        input_element.send_keys(Keys.CONTROL + "a")
        input_element.send_keys(Keys.BACKSPACE)

        # Only send keys if we have a valid value
        if value and str(value).strip():
            input_element.send_keys(str(value).strip())
            log_msg = f"✅ {label}: {value}"
            if logger:
                logger.info(log_msg)
            else:
                log_and_print(log_msg)
    except Exception as e:
        log_msg = f"⚠️ Could not enter {label}: {e}"
        if logger:
            logger.warning(log_msg)
        else:
            log_and_print(log_msg, level="warning")


# === End of utils.py ===