#!/usr/bin/env python3
"""
Test script to verify all imports used in the pipeline.py file.
"""

import sys
import os

# Standard library imports
try:
    import os
    import logging
    from pathlib import Path
    import sys
    print("✓ Standard library imports successful")
except ImportError as e:
    print(f"✗ Failed to import standard library module: {e}")

# Project-specific imports
modules_to_check = [
    "pdf_processor.utils.filesystem",
    "pdf_processor.extractors.text_extractor",
    "pdf_processor.extractors.table_extractor",
    "pdf_processor.converters.enhanced_markdown",
    "pdf_processor.utils.cleaning",
    "pdf_processor.config"
]

for module in modules_to_check:
    try:
        __import__(module)
        print(f"✓ Successfully imported {module}")
    except ImportError as e:
        print(f"✗ Failed to import {module}: {e}")

print("\nImport test complete.")
