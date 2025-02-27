#!/usr/bin/env python3
"""
Filesystem utilities for the PDF Processor.

This module provides functions for managing files and directories,
including creating, deleting, and manipulating directories and files.
"""

import os
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Get paths from config to avoid circular imports
def get_config_paths():
    """Get paths from config module."""
    from pdf_processor.config import (
        OUTPUT_DIR, TABLES_DIR, TEXT_DIR, ENHANCED_MARKDOWN_DIR
    )
    return OUTPUT_DIR, TABLES_DIR, TEXT_DIR, ENHANCED_MARKDOWN_DIR

OUTPUT_DIR, TABLES_DIR, TEXT_DIR, ENHANCED_MARKDOWN_DIR = get_config_paths()


def ensure_directory(directory_path):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        str: Path to the directory
    """
    os.makedirs(directory_path, exist_ok=True)
    return directory_path


def delete_directory_contents(directory_path, keep_readme=True):
    """
    Delete all contents of a directory except README files if specified.
    
    Args:
        directory_path (str): Path to the directory to clean
        keep_readme (bool): Whether to keep README files
        
    Returns:
        bool: True if successful
    """
    if not os.path.exists(directory_path):
        logger.warning(f"Directory does not exist: {directory_path}")
        return False
    
    logger.info(f"Deleting contents of directory: {directory_path}")
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        
        # Skip README files if requested
        if keep_readme and item.lower() in ["readme", "readme.md", "readme.txt"]:
            logger.debug(f"Keeping README file: {item_path}")
            continue
        
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                logger.debug(f"Deleted directory: {item_path}")
            else:
                os.remove(item_path)
                logger.debug(f"Deleted file: {item_path}")
        except Exception as e:
            logger.error(f"Error deleting {item_path}: {str(e)}")
            return False
    
    return True


def delete_outputs(delete_tables=False, delete_text=False, 
                  delete_enhanced=False, delete_all=False, keep_readme=True):
    """
    Delete output files based on specified options.
    
    Args:
        delete_tables (bool): Delete tables output
        delete_text (bool): Delete text output
        delete_enhanced (bool): Delete enhanced markdown output
        delete_all (bool): Delete all outputs
        keep_readme (bool): Keep README files
        
    Returns:
        bool: True if successful
    """
    logger.info("Starting deletion process...")
    
    if delete_all:
        logger.info("Deleting all generated output directories")
        delete_tables = delete_text = delete_enhanced = True
    
    result = True
    
    # Delete tables
    if delete_tables:
        logger.info(f"Deleting tables directory: {TABLES_DIR}")
        delete_directory_contents(TABLES_DIR, keep_readme)
    
    # Delete text
    if delete_text:
        logger.info(f"Deleting text directory: {TEXT_DIR}")
        delete_directory_contents(TEXT_DIR, keep_readme)
    
    # Delete enhanced markdown
    if delete_enhanced:
        logger.info(f"Deleting enhanced markdown directory: {ENHANCED_MARKDOWN_DIR}")
        delete_directory_contents(ENHANCED_MARKDOWN_DIR, keep_readme)
    
    # Output the directory structure after deletion
    logger.info("Deletion complete!")
    logger.debug("Output directory structure after deletion:")
    
    for root, dirs, files in os.walk(OUTPUT_DIR):
        level = root.replace(OUTPUT_DIR, '').count(os.sep)
        indent = ' ' * 4 * level
        logger.debug(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for file in files:
            logger.debug(f"{sub_indent}{file}")
    
    return result


def get_file_contents(file_path, encoding='utf-8', errors='replace'):
    """
    Get the contents of a file safely.
    
    Args:
        file_path (str): Path to the file
        encoding (str): File encoding
        errors (str): How to handle encoding errors
        
    Returns:
        str: The file contents or empty string on error
    """
    try:
        with open(file_path, 'r', encoding=encoding, errors=errors) as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return ""


def write_file_contents(file_path, content, encoding='utf-8'):
    """
    Write content to a file safely.
    
    Args:
        file_path (str): Path to the file
        content (str): Content to write
        encoding (str): File encoding
        
    Returns:
        bool: True if successful
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error writing to file {file_path}: {str(e)}")
        return False


def list_files(directory_path, pattern="*"):
    """
    List files in a directory matching a pattern.
    
    Args:
        directory_path (str): Path to directory
        pattern (str): Glob pattern to match
        
    Returns:
        list: List of matching file paths
    """
    if not os.path.exists(directory_path):
        logger.warning(f"Directory does not exist: {directory_path}")
        return []
        
    return [os.path.join(directory_path, f) for f in os.listdir(directory_path) 
            if os.path.isfile(os.path.join(directory_path, f)) and Path(f).match(pattern)]


# Command line interface for deletion utility
if __name__ == "__main__":
    import argparse
    import sys
    from pdf_processor.utils.logging import configure_logging
    
    # Configure logging
    configure_logging()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Delete generated output files")
    parser.add_argument("--tables", action="store_true", help="Delete tables output")
    parser.add_argument("--text", action="store_true", help="Delete text output")
    parser.add_argument("--enhanced", action="store_true", help="Delete enhanced markdown output")
    parser.add_argument("--all", action="store_true", help="Delete all outputs")
    parser.add_argument("--keep-readme", action="store_true", default=True, 
                        help="Keep README files (default: True)")
    args = parser.parse_args()
    
    # If no specific option is selected, default to deleting all
    if not (args.tables or args.text or args.enhanced):
        args.all = True
    
    success = delete_outputs(
        delete_tables=args.tables,
        delete_text=args.text,
        delete_enhanced=args.enhanced,
        delete_all=args.all,
        keep_readme=args.keep_readme
    )
    
    sys.exit(0 if success else 1)
