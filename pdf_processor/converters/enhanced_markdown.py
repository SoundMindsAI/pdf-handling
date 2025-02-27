#!/usr/bin/env python3
"""
PDF to Enhanced Markdown Converter

This module converts extracted PDF text to an enhanced markdown format with
improved structure, formatting, and readability features beyond the basic converter.
"""

import os
import re
import argparse
from pathlib import Path
import glob
from contextlib import suppress

from pdf_processor.config import DEFAULT_PDF_PATH, TEXT_DIR, TABLES_DIR, ENHANCED_MARKDOWN_DIR
from pdf_processor.utils.logging import configure_logging, get_logger
from pdf_processor.utils.cleaning import basic_clean_text, aggressive_clean_text

# Get logger for this module
logger = get_logger(__name__)


def strip_cid_values(text):
    """
    Remove CID values from text.
    
    Args:
        text (str): Text containing CID values
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    return re.sub(r'\(cid:[0-9]+\)', '', text).strip()


def normalize_whitespace(text):
    """
    Normalize whitespace in text.
    
    Args:
        text (str): Text with inconsistent whitespace
        
    Returns:
        str: Text with normalized whitespace
    """
    # Replace multiple spaces with a single space
    text = re.sub(r' +', ' ', text)
    # Replace multiple newlines with double newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def identify_section_title(line, previous_titles=None):
    """
    Identify if a line is a section title and determine its level.
    
    Args:
        line (str): Line of text to analyze
        previous_titles (list): List of previously identified titles
        
    Returns:
        tuple: (is_title, level) or (False, 0) if not a title
    """
    # Clean and normalize the line
    line = line.strip()
    
    if not line:
        return False, 0
    
    # Very short lines are likely not titles
    if len(line) < 3:
        return False, 0
    
    # Check for common title patterns
    is_all_caps = line.isupper()
    is_title_case = all(word[0].isupper() for word in line.split() if word and word[0].isalpha())
    ends_with_colon = line.endswith(':')
    
    # Common section title keywords
    title_keywords = ['chapter', 'section', 'part', 'appendix', 'table of contents', 
                      'introduction', 'summary', 'conclusion']
    
    # Check if the line starts with a title keyword
    starts_with_keyword = any(line.lower().startswith(keyword) for keyword in title_keywords)
    
    # Check for numeric prefixes (like "1.2 Section Title")
    has_numeric_prefix = bool(re.match(r'^\d+(\.\d+)*\.?\s+', line))
    
    # Check line length (titles are usually not too long)
    is_reasonable_length = len(line) <= 100
    
    # Determine if this is likely a title
    is_title = (is_reasonable_length and 
                (is_all_caps or 
                 (is_title_case and not line.endswith('.')) or
                 ends_with_colon or
                 starts_with_keyword or
                 has_numeric_prefix))
    
    if not is_title:
        return False, 0
    
    # Determine title level
    level = 2  # Default level
    
    # Adjust level based on characteristics
    if is_all_caps:
        level = 2  # Main section
    elif has_numeric_prefix:
        # Count the dots to determine nesting level
        dots = line.split()[0].count('.')
        level = min(2 + dots, 5)  # Cap at level 5
    elif starts_with_keyword:
        level = 2  # Main section
    elif is_title_case and len(line) < 50:
        level = 3  # Subsection
    elif ends_with_colon:
        level = 4  # Sub-subsection
    
    return is_title, level


def format_list_item(line):
    """
    Format list items for markdown.
    
    Args:
        line (str): Line of text to format
        
    Returns:
        tuple: (is_list_item, formatted_line)
    """
    # Check for different list item patterns
    bullet_match = re.match(r'^\s*[\•\-\*]\s+(.*)', line)
    if bullet_match:
        return True, f"* {bullet_match.group(1)}"
    
    numbered_match = re.match(r'^\s*(\d+)[\.\)]\s+(.*)', line)
    if numbered_match:
        num, content = numbered_match.groups()
        return True, f"{num}. {content}"
    
    letter_match = re.match(r'^\s*([a-zA-Z])[\.\)]\s+(.*)', line)
    if letter_match:
        return True, f"* {letter_match.group(1)}) {letter_match.group(2)}"
    
    step_match = re.match(r'^\s*Step\s+(\d+):?\s*(.*)', line)
    if step_match:
        num, content = step_match.groups()
        return True, f"{num}. {content}"
    
    return False, line


def extract_tables_for_document(pdf_name):
    """
    Get paths to all tables extracted from the document.
    
    Args:
        pdf_name (str): Base name of the PDF
        
    Returns:
        list: List of paths to table markdown files
    """
    if not os.path.exists(TABLES_DIR):
        logger.warning(f"Tables directory not found: {TABLES_DIR}")
        return []
    
    # Find all table files for this document
    table_files = []
    for file in os.listdir(TABLES_DIR):
        if file.startswith(pdf_name) and file.endswith('.md'):
            table_files.append(os.path.join(TABLES_DIR, file))
    
    logger.debug(f"Found {len(table_files)} tables for document: {pdf_name}")
    return sorted(table_files)


def add_table_references(pdf_name, output_file):
    """
    Add references to extracted tables in the markdown file.
    
    Args:
        pdf_name (str): Base name of the PDF
        output_file (str): Path to the output markdown file
        
    Returns:
        str: Path to the updated markdown file
    """
    # Find all table files for this PDF
    tables_dir = Path(TABLES_DIR)
    
    # Use glob pattern to find both lattice and stream tables
    with suppress(Exception):
        table_files = sorted([f for f in tables_dir.glob(f"{pdf_name}_*.md")])
    
    if not table_files:
        return output_file
    
    # Determine if we need to open the file or use the provided file object
    close_file = False
    output = None
    
    try:
        # Read the entire file content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add each table reference to the end of the file
        for table_file in table_files:
            table_name = table_file.name.replace('.md', '')
            
            # Read the table content
            with open(table_file, 'r', encoding='utf-8') as t:
                table_content = t.read()
            
            # If table is empty, skip it
            if not table_content.strip():
                continue
                
            # Add table reference to content
            content += f"\n\n# {table_name}\n\n{table_content}\n"
        
        # Write the updated content back to the file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
    finally:
        if close_file and output:
            output.close()
    return output_file


def convert_to_enhanced_markdown(pdf_path, output_file=None):
    """
    Convert a PDF to enhanced markdown format with page breaks, tables, and other features.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_file (str): Path to output markdown file (optional)
        
    Returns:
        str: Path to the enhanced markdown file
    """
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    pdf_dir = os.path.dirname(pdf_path)
    
    if output_file is None:
        output_file = os.path.join(ENHANCED_MARKDOWN_DIR, f"{base_name}_enhanced.md")
        
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Get all text files for this PDF
    page_files = []
    text_dir = TEXT_DIR
    
    for file in sorted(os.listdir(text_dir)):
        if file.startswith(base_name) and file.endswith(".txt"):
            page_files.append(os.path.join(text_dir, file))
    
    logger.info(f"Found {len(page_files)} page files to process")
    print(f"Found {len(page_files)} page files to process")
    
    # Create markdown content
    markdown_content = f"# {base_name.upper()}\n\n## Table of Contents\n\n* [Generated table of contents will be placed here]"
    
    # Process each page file
    for page_file in page_files:
        # Extract page number
        match = re.search(r'page_(\d+)\.txt$', page_file)
        if match:
            page_num = match.group(1)
            
            # Add page header
            markdown_content += f"\n\n### Page {page_num}\n\n"
            
            # Read page content with error handling
            try:
                with open(page_file, 'r', encoding='utf-8') as page:
                    try:
                        content = page.read()
                    except UnicodeDecodeError:
                        # If UTF-8 fails, try with latin-1 which can read any byte sequence
                        with open(page_file, 'r', encoding='latin-1') as fallback:
                            content = fallback.read()
                
                # Apply aggressive cleaning to the content
                from pdf_processor.utils.cleaning import aggressive_clean_text
                content = aggressive_clean_text(content)
                
                # Add content to markdown if there's something to add
                if content.strip():
                    markdown_content += content
                else:
                    markdown_content += "_No extractable text content on this page_"
            except Exception as e:
                logger.error(f"Error processing page file {page_file}: {str(e)}")
                markdown_content += f"\n\n_Error processing text content: {str(e)}_\n\n"
    
    # Create a debug backup of the markdown content
    debug_path = os.path.join(os.path.dirname(output_file), f"{base_name}_debug.md")
    try:
        with open(debug_path, 'w', encoding='utf-8', errors='replace') as debug_file:
            debug_file.write(markdown_content)
        logger.info(f"Debug markdown saved to: {debug_path}")
    except Exception as e:
        logger.error(f"Error saving debug markdown: {str(e)}")
    
    # Write to output file
    try:
        with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
            f.write(markdown_content)
        
        logger.info(f"Enhanced markdown created at: {output_file}")
        print(f"Enhanced markdown created at: {output_file}")
        
        # Add table references
        add_table_references(base_name, output_file)
        
        return output_file
    except Exception as e:
        logger.error(f"Error saving enhanced markdown file: {str(e)}")
        return debug_path  # Return the debug file path as fallback


def main():
    """Main function to handle command line arguments."""
    # Configure logging
    configure_logging()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Convert PDF text to enhanced markdown format")
    parser.add_argument("--pdf-path", default=DEFAULT_PDF_PATH, help="Path to the PDF file")
    parser.add_argument("--output-file", default=None, help="Path to the output markdown file")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
                       default="INFO", help="Set the logging level (default: INFO)")
    args = parser.parse_args()
    
    # Set log level if specified
    if args.log_level:
        logger.setLevel(args.log_level)
        logger.info(f"Log level set to {args.log_level}")
    
    # Convert to enhanced markdown
    output_file = convert_to_enhanced_markdown(args.pdf_path, args.output_file)
    
    print(f"Processing complete. Check '{output_file}' for the enhanced markdown content.")
    return 0


if __name__ == "__main__":
    main()
