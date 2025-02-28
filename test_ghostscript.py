#!/usr/bin/env python3
"""
Test script to check Ghostscript availability for Camelot
"""

import os
import sys
import subprocess
import shutil

def check_ghostscript():
    """Check if Ghostscript is available and print its path"""
    # Check if gs is in PATH
    gs_path = shutil.which('gs')
    print(f"Ghostscript path in PATH: {gs_path}")
    
    if gs_path:
        # Try to run ghostscript and get version
        try:
            result = subprocess.run(['gs', '--version'], 
                                    capture_output=True, 
                                    text=True, 
                                    check=True)
            print(f"Ghostscript version: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"Error running ghostscript: {e}")
    else:
        print("Ghostscript not found in PATH")
    
    # Check known common locations
    common_locations = [
        '/usr/local/bin/gs',
        '/usr/bin/gs',
        '/opt/homebrew/bin/gs',
        '/opt/local/bin/gs'
    ]
    
    for loc in common_locations:
        if os.path.exists(loc):
            print(f"Ghostscript found at: {loc}")
    
    # Check if camelot can be imported
    try:
        import camelot
        print("Camelot imported successfully")
        
        # Check if camelot can find ghostscript
        try:
            from camelot.handlers import PDFHandler
            print("Trying to initialize PDFHandler...")
            handler = PDFHandler('test')
            print("PDFHandler initialized successfully")
        except Exception as e:
            print(f"Error initializing PDFHandler: {e}")
        
    except ImportError as e:
        print(f"Error importing camelot: {e}")
    
    # Try to set the GS_PATH environment variable
    print("\nTrying with explicit GS_PATH:")
    os.environ['GS_PATH'] = gs_path if gs_path else '/usr/local/bin/gs'
    print(f"Set GS_PATH to: {os.environ.get('GS_PATH')}")
    
    # Check sys.path to see Python's module search paths
    print("\nPython module search paths:")
    for path in sys.path:
        print(f"  {path}")

if __name__ == "__main__":
    check_ghostscript()
