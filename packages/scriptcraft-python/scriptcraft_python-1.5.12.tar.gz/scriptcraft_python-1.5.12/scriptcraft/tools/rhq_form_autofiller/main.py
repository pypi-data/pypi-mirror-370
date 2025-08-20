"""
RHQ Form Autofiller - Simplified Single-File Implementation

This module provides a complete RHQ Form Autofiller tool with built-in
dual-environment support. It automatically detects whether it's running in
development or distributable mode and imports accordingly.

Usage:
    Development: python -m scripts.tools.rhq_form_autofiller.main [args]
    Distributable:   python main.py [args]
    Pipeline:    Called via main_runner(**kwargs)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import time
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

# === Environment Detection & Import Setup ===
# Import the environment detection module
try:
    from .env import setup_environment
except ImportError:
    from env import setup_environment

# Set up environment and get imports
IS_DISTRIBUTABLE = setup_environment()

# Import based on environment
if IS_DISTRIBUTABLE:
    # Distributable imports - use cu pattern for consistency
    import common as cu
else:
    # Development imports - use cu pattern for consistency
    import scriptcraft.common as cu

# Import utils (same in both environments since it's local)
try:
    from .utils import (
        build_address_data, launch_browser, fill_panel
    )
except ImportError:
    # If utils import fails, try current directory
    from .utils import (
        build_address_data, launch_browser, fill_panel
    )

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class RHQFormAutofiller(cu.BaseTool):
    """Tool for automatically filling RHQ forms with address data."""
    
    def __init__(self) -> None:
        """Initialize the tool."""
        super().__init__(
            name="RHQ Form Autofiller",
            description="Automates filling of RHQ forms using pre-processed data from Excel files.",
            tool_name="rhq_form_autofiller"
        )
        self.driver: Optional[webdriver.Remote] = None
        self.logger: Optional[Any] = None
        
        # Get tool-specific configuration
        tool_config = self.get_tool_config()
        self.browser_timeout = tool_config.get("browser_timeout", 60)
        self.form_wait_time = tool_config.get("form_wait_time", 10) 
        self.login_retry_attempts = tool_config.get("login_retry_attempts", 3)
        self.auto_login = tool_config.get("auto_login", True)
    
    def run(self,
            mode: Optional[str] = None,
            input_paths: Optional[List[Union[str, Path]]] = None,
            output_dir: Optional[Union[str, Path]] = None,
            domain: Optional[str] = None,
            output_filename: Optional[str] = None,
            **kwargs: Any) -> None:
        """
        Run the RHQ Form Autofiller's main functionality.
        
        Args:
            mode: Operating mode (not used for this tool)
            input_paths: List of input Excel file paths 
            output_dir: Directory to save outputs
            domain: Domain context (not used for this tool)
            output_filename: Output filename (not used for this tool)
            **kwargs: Additional arguments:
                - debug: Enable debug logging
                - med_id: Filter for specific Med_ID
                - input_excel: Alternative input path specification
        
        Raises:
            ValueError: If required parameters are missing or invalid
        """
        self.log_start()
        
        try:
            # Setup directories
            output_dir = cu.ensure_output_dir(Path(output_dir or self.default_output_dir))
            log_dir = cu.ensure_output_dir(Path(kwargs.get('log_dir', 'logs')))
            
            # Setup logging
            self.logger = cu.setup_logger(
                name=self.name,
                level="DEBUG" if kwargs.get('debug') else "INFO",
                log_file=log_dir / "rhq_form_autofiller.log"
            )
            
            # Determine input file
            input_file = self._resolve_input_file(input_paths, kwargs)
            
            # Load and process data
            cu.log_and_print("🔄 Loading address data...")
            data = build_address_data(input_file, kwargs.get('med_id'))
            cu.log_and_print(f"✅ Loaded data for {len(data)} Med_IDs")
            
            # Launch browser and process forms
            self._process_forms(data)
            
            self.log_completion()
            
        except Exception as e:
            cu.log_and_print(f"❌ Error: {str(e)}", level="error")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                cu.log_and_print("🔄 Browser closed")
    
    def _resolve_input_file(self, input_paths: Optional[List[Union[str, Path]]], kwargs: Dict[str, Any]) -> Path:
        """Resolve the input file from various sources."""
        # Priority: input_paths -> input_excel kwarg -> auto-discovery
        if input_paths and len(input_paths) > 0:
            input_file = Path(input_paths[0])
        elif kwargs.get('input_excel'):
            input_file = Path(kwargs['input_excel'])
        else:
            # Auto-discover input file using DRY method from BaseTool
            # Use explicit input_dir if provided, otherwise use resolve_input_directory
            if 'input_dir' in kwargs:
                input_dir = Path(kwargs['input_dir'])
            else:
                # Add config to kwargs if not already present
                if 'config' not in kwargs:
                    kwargs['config'] = self.config
                input_dir = self.resolve_input_directory(**kwargs)
            
            if not input_dir.exists():
                raise ValueError(f"Input directory not found: {input_dir}")
            
            excel_files = list(input_dir.glob("*.xlsx"))
            if not excel_files:
                raise ValueError("No Excel files found in input directory")
            
            input_file = excel_files[0]
            cu.log_and_print(f"📁 Auto-discovered input file: {input_file}")
        
        if not input_file.exists():
            raise ValueError(f"Input file does not exist: {input_file}")
        
        return input_file
    
    def _process_forms(self, data: Dict[str, Any]) -> None:
        """Process all forms with the loaded data."""
        # Launch browser
        cu.log_and_print("🌐 Launching browser...")
        self.driver = launch_browser()
        
        try:
            # Handle login first
            self._handle_login(data)
            
            # Process each record
            for med_id, panels_data in data.items():
                self._process_single_form(med_id, panels_data)
                
        except Exception as e:
            cu.log_and_print(f"❌ Form processing failed: {str(e)}", level="error")
            raise
    
    def _handle_login(self, data: Dict[str, Any]) -> None:
        """Handle the login process."""
        first_med_id = next(iter(data))
        url = self.config.tools["rhq_form_autofiller"]["url_template"].format(
            med_id=first_med_id
        )
        cu.log_and_print("🔑 Attempting automatic login")
        self.driver.get(url)
        self.driver.refresh()
        cu.log_and_print("🔄 Refreshed to ensure login screen.")

        time.sleep(self.form_wait_time)  # Wait for page to load
        cu.log_and_print(f"⏱️ Waiting {self.form_wait_time} seconds for page to fully load...")

        # First: Click the initial "Login" button to show the login form
        try:
            login_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]"))
            )
            login_btn.click()
            cu.log_and_print("🔐 Login button clicked - login form should now be visible.")
            time.sleep(2)  # Wait for login form to appear
        except Exception as e:
            cu.log_and_print(f"⚠️ Could not click initial Login button: {e}", level="warning")

        # Second: Try automatic login (now that login form is visible)
        login_attempted = attempt_automatic_login(self.driver, self.logger)

        if not login_attempted:
            cu.log_and_print("ℹ️ Automatic login not attempted - manual login required.")
        else:
            cu.log_and_print("🤖 Automatic login attempted - waiting for authentication...")
        
        # Wait for login to complete
        start = time.time()
        while "login" in self.driver.current_url.lower() and time.time() - start < self.browser_timeout:
            time.sleep(1)
        cu.log_and_print("✅ Login confirmed. Starting data entry...")
        
        # Wait for the page to be fully loaded after login
        time.sleep(5)
    
    def _process_single_form(self, med_id: str, panels_data: List[Any]) -> None:
        """Process a single form for one Med_ID."""
        try:
            # Navigate to form
            cu.log_and_print(f"\n🔄 Processing Med_ID: {med_id}")
            url = self.config.tools["rhq_form_autofiller"]["url_template"].format(
                med_id=med_id
            )
            self.driver.get(url)
            cu.log_and_print(f"🌐 Opened page for Med_ID {med_id}")
            
            # Wait for form load - look for expansion panels
            try:
                WebDriverWait(self.driver, self.form_wait_time).until(
                    EC.presence_of_element_located((By.TAG_NAME, "mat-expansion-panel"))
                )
                cu.log_and_print("✅ Form loaded successfully")
            except Exception as e:
                cu.log_and_print(f"❌ Form did not load for {med_id}: {e}", level="error")
                return
            
            # Fill each panel
            for panel_idx, address_blocks in enumerate(panels_data):
                if address_blocks:  # Only process panels with data
                    cu.log_and_print(f"📝 Processing panel {panel_idx} with {len(address_blocks)} blocks")
                    fill_panel(self.driver, panel_idx, address_blocks, logger=self.logger)
            
            # Submit form
            self._submit_form(med_id)
            
            # Wait between submissions
            time.sleep(2)
            
        except Exception as e:
            cu.log_and_print(f"❌ Error processing record {med_id}: {e}", level="error")
    
    def _submit_form(self, med_id: str) -> None:
        """Submit the form for a Med_ID."""
        try:
            cu.log_and_print(f"💾 Submitting form for {med_id}...")
            
            # Look for submit button
            submit_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit') or contains(text(), 'Save')]"))
            )
            submit_btn.click()
            
            # Wait for submission to complete
            time.sleep(3)
            cu.log_and_print(f"✅ Form submitted for {med_id}")
            
        except Exception as e:
            cu.log_and_print(f"⚠️ Could not submit form for {med_id}: {e}", level="warning")
    
    def run_from_cli(self, args: argparse.Namespace) -> None:
        """
        Run the tool from command line arguments.
        
        Args:
            args: Parsed command line arguments
        """
        kwargs = vars(args).copy()
        
        # Extract known arguments
        input_paths = kwargs.pop('input_path', None)
        if input_paths and not isinstance(input_paths, list):
            input_paths = [input_paths]
        
        output_dir = kwargs.pop('output_dir', self.default_output_dir)
        debug = kwargs.pop('debug', False)
        
        # Run the tool
        self.run(
            input_paths=input_paths,
            output_dir=output_dir,
            debug=debug,
            **kwargs
        )


# === 🔐 Credentials Management ===
def load_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Load credentials from credentials.txt file.
    Returns tuple (username, password) or (None, None) if not found/configured.
    """
    try:
        cred_file = Path(__file__).parent / "credentials.txt"
        if not cred_file.exists():
            return None, None
            
        credentials: Dict[str, str] = {}
        with open(cred_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    credentials[key.strip()] = value.strip()
        
        username = credentials.get('username')
        password = credentials.get('password')
        
        if username and password:
            return username, password
        else:
            return None, None
            
    except Exception as e:
        print(f"⚠️ Error loading credentials: {e}")
        return None, None


def attempt_automatic_login(driver: webdriver.Remote, logger: Optional[Any] = None) -> bool:
    """
    Attempt automatic login if credentials are available.
    Returns True if login was attempted, False otherwise.
    """
    username, password = load_credentials()
    
    if not username or not password:
        log_msg = "ℹ️ No credentials found in credentials.txt, manual login required"
        if logger:
            logger.info(log_msg)
        else:
            print(log_msg)
        return False
    
    try:
        log_msg = f"🔐 Attempting automatic login for user: {username}"
        if logger:
            logger.info(log_msg)
        else:
            print(log_msg)
        
        # Look for username field
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[type='text'], input[name='username'], input[name='email']"))
        )
        username_field.clear()
        username_field.send_keys(username)
        
        # Look for password field
        password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_field.clear()
        password_field.send_keys(password)
        
        # Look for login button
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign In') or contains(text(), 'Log In')]")
        login_button.click()
        
        log_msg = "✅ Automatic login credentials entered, waiting for authentication..."
        if logger:
            logger.info(log_msg)
        else:
            print(log_msg)
        
        return True
        
    except Exception as e:
        log_msg = f"⚠️ Automatic login failed: {e}, falling back to manual login"
        if logger:
            logger.warning(log_msg)
        else:
            print(log_msg)
        return False


def main():
    """Main entry point for the RHQ form autofiller tool."""
    args = cu.parse_standard_tool_args("rhq_form_autofiller", "🏥 Automates filling of RHQ forms with address data from Excel files")
    
    # Create and run the tool
    tool = RHQFormAutofiller()
    tool.run(
        input_paths=args.input_paths,
        output_dir=args.output_dir,
        domain=args.domain,
        output_filename=args.output_filename,
        mode=args.mode
    )


if __name__ == "__main__":
    main()
