#!/usr/bin/env python3
"""
Delete Outputs Script

This script removes generated content from the output directories,
allowing you to start fresh with PDF processing.

Options:
    --all               Remove all generated content (default)
    --tables            Remove only table output files
    --text              Remove only text output files
    --markdown          Remove only markdown output files
    --output-dir=DIR    Specify a custom output directory (default: ./outputs)

Note: README.md files are always preserved in output directories.
"""

import os
import argparse
import shutil
from pathlib import Path

def recreate_directory(directory_path):
    """
    Remove all files in a directory and recreate it, always preserving README.md files.
    
    This function:
    1. Checks if the directory exists
    2. Preserves the content of README.md if it exists
    3. Removes all other files and subdirectories
    4. Recreates the directory and restores the README.md file
    
    Args:
        directory_path (str): Path to the directory to recreate
        
    Returns:
        bool: True if the directory was recreated, False if it didn't exist
    """
    readme_content = None
    readme_path = os.path.join(directory_path, "README.md")
    
    # Save README content if it exists
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
            readme_content = f.read()
    
    # Remove directory and contents
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
    
    # Recreate directory
    os.makedirs(directory_path, exist_ok=True)
    
    # Restore README if needed
    if readme_content:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

def delete_tables(output_dir):
    """
    Delete the tables output directory and its contents.
    
    This function:
    1. Creates paths for the tables directory and clean tables subdirectory
    2. Recreates both directories, preserving any README.md files
    3. Effectively removes all table content while maintaining directory structure
    
    Args:
        output_dir (str): Base output directory containing the tables subdirectory
    """
    tables_dir = os.path.join(output_dir, "tables")
    clean_tables_dir = os.path.join(tables_dir, "clean")
    
    print(f"Deleting tables directory: {tables_dir}")
    
    # Clean tables directory
    recreate_directory(tables_dir)
    
    # Recreate clean subdirectory
    recreate_directory(clean_tables_dir)

def delete_text(output_dir):
    """
    Delete the text output directory and its contents.
    
    This function:
    1. Creates the path for the text directory
    2. Recreates the directory, preserving any README.md file
    3. Effectively removes all text content while maintaining directory structure
    
    Args:
        output_dir (str): Base output directory containing the text subdirectory
    """
    text_dir = os.path.join(output_dir, "text")
    
    print(f"Deleting text directory: {text_dir}")
    
    # Clean text directory
    recreate_directory(text_dir)

def delete_markdown(output_dir):
    """
    Delete the markdown output directory and its contents.
    
    This function:
    1. Creates the path for the markdown directory
    2. Recreates the directory, preserving any README.md file
    3. Effectively removes all markdown content while maintaining directory structure
    
    Args:
        output_dir (str): Base output directory containing the markdown subdirectory
    """
    markdown_dir = os.path.join(output_dir, "markdown")
    
    print(f"Deleting markdown directory: {markdown_dir}")
    
    # Clean markdown directory
    recreate_directory(markdown_dir)

def main():
    """
    Main function to handle command line arguments and perform deletion operations.
    
    This function:
    1. Parses command-line arguments for deletion options and output directory
    2. Determines which deletion operations to run based on the provided arguments
    3. Executes the appropriate deletion functions (tables, text, and/or markdown)
    4. Handles default behavior when no specific deletion option is selected
    
    The script preserves directory structure and README.md files while removing
    all other content, allowing for a clean slate before re-running the PDF processing.
    
    Returns:
        int: 0 if successful
    """
    parser = argparse.ArgumentParser(description="Delete generated output files")
    parser.add_argument("--all", action="store_true", help="Remove all generated content (default)")
    parser.add_argument("--tables", action="store_true", help="Remove only table output files")
    parser.add_argument("--text", action="store_true", help="Remove only text output files")
    parser.add_argument("--markdown", action="store_true", help="Remove only markdown output files")
    parser.add_argument("--output-dir", default="./outputs", help="Specify a custom output directory")
    args = parser.parse_args()
    
    # If no specific option is selected, clean everything
    delete_all = not (args.tables or args.text or args.markdown) or args.all
    output_dir = args.output_dir
    
    # Create main outputs directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print("Starting deletion process...")
    
    # Perform the requested deletion operations
    if delete_all:
        print("Deleting all generated output directories")
        delete_tables(output_dir)
        delete_text(output_dir)
        delete_markdown(output_dir)
    else:
        if args.tables:
            delete_tables(output_dir)
        if args.text:
            delete_text(output_dir)
        if args.markdown:
            delete_markdown(output_dir)
    
    print("\nDeletion complete!")
    
    # Show directory structure after deletion
    print("\nOutput directory structure after deletion:")
    for root, dirs, files in os.walk(output_dir):
        level = root.replace(output_dir, "").count(os.sep)
        indent = " " * 4 * level
        print(f"{indent}{os.path.basename(root) or os.path.basename(output_dir)}/")
        sub_indent = " " * 4 * (level + 1)
        for file in sorted(files):
            print(f"{sub_indent}{file}")

if __name__ == "__main__":
    main()
