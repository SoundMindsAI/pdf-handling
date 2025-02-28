#!/usr/bin/env python3
# coding: utf-8

"""
This module handles the setup of Ghostscript for Camelot-py
by setting the GS_PATH environment variable automatically.
"""

import os
import sys
import shutil
import logging
import subprocess
from pathlib import Path

# Get module-level logger
logger = logging.getLogger(__name__)

def find_ghostscript():
    """
    Find Ghostscript executable in common locations and return its path.
    
    Returns:
        str: Path to the Ghostscript executable or None if not found
    """
    # First check if it's in PATH
    gs_path = shutil.which('gs')
    if gs_path:
        logger.info(f"Found Ghostscript in PATH: {gs_path}")
        return gs_path
    
    # Common locations to check for Ghostscript
    common_locations = [
        '/usr/local/bin/gs',           # Common on macOS / Linux
        '/usr/bin/gs',                 # Common on Linux
        '/opt/homebrew/bin/gs',        # macOS Homebrew on M1/M2
        '/opt/local/bin/gs',           # macOS MacPorts
        'C:\\Program Files\\gs\\gs*\\bin\\gswin64c.exe',  # Windows
        'C:\\Program Files (x86)\\gs\\gs*\\bin\\gswin32c.exe'  # Windows 32-bit
    ]
    
    # Check all common locations
    for location in common_locations:
        # Handle wildcards for Windows paths
        if '*' in location:
            import glob
            matching_paths = sorted(glob.glob(location), reverse=True)
            for path in matching_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    logger.info(f"Found Ghostscript at: {path}")
                    return path
        elif os.path.exists(location) and os.access(location, os.X_OK):
            logger.info(f"Found Ghostscript at: {location}")
            return location
    
    logger.warning("Ghostscript not found in common locations!")
    return None

def setup_ghostscript():
    """
    Set up the GS_PATH environment variable if Ghostscript is found.
    Should be called early in the application to ensure Ghostscript is available.
    
    Returns:
        bool: True if Ghostscript was found and set up, False otherwise
    """
    # If GS_PATH is already set and valid, use it
    existing_gs_path = os.environ.get('GS_PATH')
    if existing_gs_path and os.path.exists(existing_gs_path) and os.access(existing_gs_path, os.X_OK):
        logger.info(f"Using existing GS_PATH: {existing_gs_path}")
        return True
    
    # Otherwise, look for Ghostscript and set GS_PATH
    gs_path = find_ghostscript()
    if gs_path:
        os.environ['GS_PATH'] = gs_path
        logger.info(f"Set GS_PATH environment variable to: {gs_path}")
        try:
            # Verify Ghostscript version
            result = subprocess.run([gs_path, '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  check=True)
            version = result.stdout.strip()
            logger.info(f"Ghostscript version: {version}")
            print(f"Ghostscript {version} configured successfully")
            return True
        except (subprocess.SubprocessError, OSError) as e:
            logger.error(f"Error checking Ghostscript version: {e}")
    
    # If we get here, Ghostscript was not found or is not working
    logger.error("Ghostscript not found or not working. Table extraction may fail.")
    print("WARNING: Ghostscript not found or not working. Table extraction may fail.")
    print("Install Ghostscript and ensure it's in your PATH, or set GS_PATH manually.")
    return False

if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(level=logging.INFO, 
                      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Run as standalone script
    success = setup_ghostscript()
    sys.exit(0 if success else 1)
