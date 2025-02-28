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
import sys

from pdf_processor.config import DEFAULT_PDF_PATH, TEXT_DIR, TABLES_DIR, ENHANCED_MARKDOWN_DIR
from pdf_processor.utils.logging import configure_logging, get_logger
from pdf_processor.utils.cleaning import basic_clean_text, aggressive_clean_text, fixed_binary_clean as binary_clean_content, simple_clean_markdown
from pdf_processor.utils.filesystem import ensure_directory

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


def add_table_references(markdown_content, tables_dir, pdf_path):
    """
    Add references to tables in the markdown content.
    
    Args:
        markdown_content (str): The markdown content
        tables_dir (str): Directory where table files are stored
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Markdown content with table references
    """
    if not os.path.exists(tables_dir):
        return markdown_content
    
    # List all table files for this PDF
    pdf_basename = os.path.basename(pdf_path).replace('.pdf', '')
    table_files = []
    for f in os.listdir(tables_dir):
        if f.startswith(f"{pdf_basename}_table_") and f.endswith(".md"):
            table_files.append(os.path.join(tables_dir, f))
    
    if not table_files:
        return markdown_content
    
    logger.info(f"Found {len(table_files)} table files to integrate")
    
    # Sort table files by page number
    def get_page_num(file_path):
        # Extract page number from filename (e.g., file_table_page_5.md)
        match = re.search(r"_page_(\d+)\.md$", file_path)
        if match:
            return int(match.group(1))
        return 0
    
    table_files.sort(key=get_page_num)
    
    # Split markdown content into sections by page
    pages = []
    current_page = []
    content_lines = markdown_content.split("\n")
    
    for line in content_lines:
        if re.match(r"^## Page \d+$", line):
            if current_page:
                pages.append(current_page)
                current_page = []
        current_page.append(line)
    
    if current_page:
        pages.append(current_page)
    
    # Map table files to their respective pages
    tables_by_page = {}
    for table_file in table_files:
        page_num = get_page_num(table_file)
        if page_num > 0:  # Page numbers in filenames start from 1
            if page_num not in tables_by_page:
                tables_by_page[page_num] = []
            
            # Read table content
            with open(table_file, 'r', encoding='utf-8') as f:
                table_content = f.read().strip()
            
            tables_by_page[page_num].append(table_content)
    
    # Integrate tables within their respective page sections
    revised_content = []
    for i, page_lines in enumerate(pages):
        # Find the page number
        page_num = 0
        for line in page_lines:
            match = re.match(r"^## Page (\d+)$", line)
            if match:
                page_num = int(match.group(1))
                break
        
        # Add the page header and content
        revised_content.extend(page_lines)
        
        # Add tables for this page if they exist
        if page_num in tables_by_page:
            revised_content.append("")  # Add blank line
            revised_content.append("### Tables")
            for table in tables_by_page[page_num]:
                revised_content.append("")
                revised_content.extend(table.split("\n"))
                revised_content.append("")
    
    return "\n".join(revised_content)


def convert_csv_to_markdown_table(csv_content):
    """
    Convert CSV content to a markdown table.
    
    Args:
        csv_content (str): CSV content as string
        
    Returns:
        str: Markdown table format
    """
    if not csv_content.strip():
        return "*Empty table*"
    
    lines = csv_content.strip().split('\n')
    if not lines:
        return "*Empty table*"
    
    # Process the header row
    headers = lines[0].split(',')
    headers = [h.strip('"').strip() for h in headers]
    
    # Start building the markdown table
    markdown_table = '| ' + ' | '.join(headers) + ' |\n'
    markdown_table += '|' + '|'.join(['---' for _ in headers]) + '|\n'
    
    # Add data rows
    for i in range(1, len(lines)):
        # Handle potential quoted cells with commas inside them
        row_data = []
        current_cell = ""
        in_quotes = False
        
        for char in lines[i]:
            if char == '"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                row_data.append(current_cell.strip('"').strip())
                current_cell = ""
            else:
                current_cell += char
        
        # Don't forget the last cell
        if current_cell:
            row_data.append(current_cell.strip('"').strip())
        
        # Ensure we have data for all columns
        while len(row_data) < len(headers):
            row_data.append("")
        
        # Truncate if we have too many columns
        if len(row_data) > len(headers):
            row_data = row_data[:len(headers)]
        
        # Add the row to the markdown table
        markdown_table += '| ' + ' | '.join(row_data) + ' |\n'
    
    return markdown_table


def convert_to_enhanced_markdown(pdf_path, output_file=None):
    """
    Convert a PDF to enhanced markdown format with page breaks, tables, and more.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_file (str): Optional path for output file. If not provided, it will
                          be created in the configured ENHANCED_MARKDOWN_DIR
                          
    Returns:
        dict: Results of the conversion including output path
    """
    pdf_filename = os.path.basename(pdf_path)
    base_name = os.path.splitext(pdf_filename)[0]
    
    # Set default output location if not provided
    if not output_file:
        output_dir = ENHANCED_MARKDOWN_DIR
        ensure_directory(output_dir)
        output_file = os.path.join(output_dir, f"{base_name}.md")
    
    # Get text files from the extraction process - directly from TEXT_DIR
    text_dir = TEXT_DIR
    
    # Check for page files
    page_files = get_sorted_page_files_with_prefix(text_dir, base_name)
    if not page_files:
        logger.error(f"No text files found for {base_name} in {text_dir}")
        return {"success": False, "error": "No text files found"}
    
    # Create empty markdown content to start
    markdown_content = ""
    
    try:
        # Process each page
        for i, page_file in enumerate(page_files, start=1):
            # Add page break for all pages except the first
            if i > 1:
                markdown_content += f"\n\n---\n\n"
            
            # Add page header
            markdown_content += f"## Page {i}\n\n"
            
            # Read page content with error handling
            try:
                with open(page_file, 'r', encoding='utf-8') as page:
                    try:
                        content = page.read()
                    except UnicodeDecodeError:
                        # If UTF-8 fails, try with latin-1 which can read any byte sequence
                        with open(page_file, 'r', encoding='latin-1') as fallback:
                            content = fallback.read()
                
                # Apply binary content cleaning to remove control characters
                content = binary_clean_content(content)
                
                # Apply aggressive cleaning to the content
                content = aggressive_clean_text(content)
                
                # Add content to markdown if there's something to add
                if content.strip():
                    markdown_content += content
                else:
                    markdown_content += "_No extractable text content on this page_"
            except Exception as e:
                logger.error(f"Error processing page {i}: {str(e)}")
                markdown_content += f"_Error processing page {i}: {str(e)}_\n\n"
        
        # Add table references (if tables exist)
        tables_dir = os.path.join(TABLES_DIR, base_name)
        markdown_content = add_table_references(markdown_content, tables_dir, pdf_path)
        
        # Apply simple cleaning to improve readability
        markdown_content = simple_clean_markdown(markdown_content)
        
        # Write the markdown content to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return {
            "success": True, 
            "output_file": output_file
        }
        
    except Exception as e:
        logger.error(f"Error creating enhanced markdown: {str(e)}")
        return {"success": False, "error": str(e)}


def post_process_markdown(markdown_file_path):
    """
    Apply enhanced post-processing to the generated markdown file.
    
    Args:
        markdown_file_path (str): Path to the markdown file
        
    Returns:
        bool: True if post-processing was successful
    """
    from pdf_processor.utils.cleaning import two_pass_markdown_cleanup, simple_clean_markdown
    
    try:
        # First, ensure the file exists
        if not os.path.exists(markdown_file_path):
            logger.error(f"Markdown file {markdown_file_path} not found.")
            return False
        
        # Apply special cleaning for enhanced output
        logger.info(f"Applying enhanced cleaning to markdown files for {os.path.basename(markdown_file_path)}")
        logger.info(f"Enhanced cleaning of markdown files in {os.path.dirname(markdown_file_path)}")
        
        # Read the content first
        with open(markdown_file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Apply simple cleaning to improve readability
        cleaned_content = simple_clean_markdown(content)
        
        # Back up the original file
        backup_file = markdown_file_path + '.bak'
        import shutil
        shutil.copy2(markdown_file_path, backup_file)
        logger.info(f"Created backup of {markdown_file_path} at {backup_file}")
        
        # Write the cleaned content back
        with open(markdown_file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        # Now perform the two-pass cleanup
        logger.info(f"Performing enhanced cleaning on markdown file: {markdown_file_path}")
        success = two_pass_markdown_cleanup(markdown_file_path)
        
        if success:
            logger.info(f"Enhanced cleaning completed for 1 markdown files")
            return True
        else:
            logger.warning(f"Enhanced cleaning failed for {markdown_file_path}")
            return False
            
    except Exception as e:
        logger.error(f"Error in post-processing markdown file {markdown_file_path}: {str(e)}")
        return False


def get_sorted_page_files_with_prefix(text_dir, prefix):
    """
    Get a list of page files from the text directory, sorted by page number.
    This modified version looks for files with a specific prefix rather than
    assuming a subdirectory structure.
    
    Args:
        text_dir (str): Directory containing text files
        prefix (str): The base name of the PDF file
        
    Returns:
        list: Sorted list of page files
    """
    pattern = os.path.join(text_dir, f"{prefix}_page_*.txt")
    page_files = glob.glob(pattern)
    
    # Sort by page number
    page_files.sort(key=lambda x: int(re.search(r'page_(\d+)\.txt$', x).group(1)))
    
    return page_files


def main():
    """
    Main entry point for running as standalone.
    """
    parser = argparse.ArgumentParser(description='Convert extracted PDF text to enhanced markdown')
    parser.add_argument('--pdf', default=DEFAULT_PDF_PATH, help='Path to the PDF file')
    parser.add_argument('--output', help='Path to output file (optional)')
    args = parser.parse_args()

    # Configure logging
    configure_logging()

    # Validate PDF path
    if not os.path.exists(args.pdf):
        logger.error(f"PDF file not found: {args.pdf}")
        sys.exit(1)

    # Convert to enhanced markdown
    result = convert_to_enhanced_markdown(args.pdf, args.output)
    
    if result["success"]:
        output_file = result["output_file"]
        logger.info(f"Enhanced markdown created successfully at: {output_file}")
        print(f"Enhanced markdown created at: {output_file}")
    else:
        logger.error(f"Failed to create enhanced markdown: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
