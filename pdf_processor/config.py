#!/usr/bin/env python3
"""
Configuration module for the PDF Processor package.

This module provides central configuration settings and constants used across
the package. It handles default paths, processing options, and other settings.
"""

import os
import platform
from pathlib import Path


# Determine the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Default directories - all under data directory for consistency
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SOURCE_DOCS_DIR = os.path.join(DATA_DIR, "sourcedocs")
OUTPUT_DIR = os.path.join(DATA_DIR, "outputs")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

# Default subdirectories for outputs
TABLES_DIR = os.path.join(OUTPUT_DIR, "tables")
TABLES_CLEAN_DIR = os.path.join(TABLES_DIR, "clean")
TEXT_DIR = os.path.join(OUTPUT_DIR, "text")
# Removed MARKDOWN_DIR as we've removed basic markdown functionality
ENHANCED_MARKDOWN_DIR = os.path.join(OUTPUT_DIR, "enhanced_markdown")

# Default files
DEFAULT_PDF_PATH = os.path.join(SOURCE_DOCS_DIR, "AEGuidebook.pdf")

# Processing settings
DEFAULT_LOG_LEVEL = "INFO"
AVAILABLE_STEPS = ["clean", "tables", "text", "enhanced"]

# Ensure directories exist
def ensure_directories():
    """Create all necessary directories if they don't exist."""
    for directory in [
        SOURCE_DOCS_DIR, 
        OUTPUT_DIR,
        TABLES_DIR,
        TABLES_CLEAN_DIR, 
        TEXT_DIR,
        ENHANCED_MARKDOWN_DIR,
        LOGS_DIR
    ]:
        os.makedirs(directory, exist_ok=True)

# System-specific settings
def is_windows():
    """Check if the system is Windows."""
    return platform.system().lower() == "windows"


def is_macos():
    """Check if the system is macOS."""
    return platform.system().lower() == "darwin"


def is_linux():
    """Check if the system is Linux."""
    return platform.system().lower() == "linux"


# When imported, ensure directories exist
ensure_directories()
