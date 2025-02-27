#!/usr/bin/env python3
"""
PDF Table Extractor Module

This module extracts tables from PDF files using Camelot-py and saves them as 
structured markdown files for easy viewing and further processing.
"""

import os
import re
import argparse
import camelot
from pathlib import Path

from pdf_processor.config import DEFAULT_PDF_PATH, TABLES_DIR
from pdf_processor.utils.logging import configure_logging, get_logger

# Get logger for this module
logger = get_logger(__name__)


def clean_text(text):
    """
    Clean up text from extracted table cells.
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove cid patterns
    text = re.sub(r'\(cid:[0-9]+\)', '', text)
    
    # Fix common encoding issues
    replacements = [
        # Fix quotes
        (r'â€œ', '"'),
        (r'â€', '"'),
        # Fix apostrophes
        (r'â€™', "'"),
        # Fix dashes
        (r'â€"', '-'),
        # Fix bullet points
        (r'â€¢', '•'),
    ]
    
    logger.debug("Applying text cleanup patterns")
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    
    return text.strip()


def save_table_as_markdown(table, idx, output_dir, pdf_name):
    """
    Save a table as markdown file.
    
    Args:
        table: Camelot table object
        idx (int): Table index number
        output_dir (str): Directory to save the table
        pdf_name (str): Base name of the PDF file
        
    Returns:
        str: Path to the saved file
    """
    logger.debug(f"Converting table {idx} to markdown format")
    
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct the output filename
    output_file = os.path.join(output_dir, f"{pdf_name}_table_{idx}.md")
    logger.debug(f"Saving table to {output_file}")
    
    # Extract column names
    header_row = [clean_text(cell) for cell in table.df.iloc[0]]
    
    # Check if header row contains valid headers
    has_header = any(len(h.strip()) > 0 for h in header_row)
    
    # Create markdown table
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write table title
        f.write(f"# Table {idx} from {pdf_name}\n\n")
        
        # Write the table header
        if has_header:
            # Use first row as header
            f.write('| ' + ' | '.join(header_row) + ' |\n')
            f.write('| ' + ' | '.join(['---' for _ in header_row]) + ' |\n')
            
            # Write the table body, starting from index 1
            for i in range(1, len(table.df)):
                row_values = [clean_text(cell) for cell in table.df.iloc[i]]
                f.write('| ' + ' | '.join(row_values) + ' |\n')
        else:
            # No header, use all rows as data
            f.write('| ' + ' | '.join(['Column ' + str(i+1) for i in range(len(table.df.columns))]) + ' |\n')
            f.write('| ' + ' | '.join(['---' for _ in range(len(table.df.columns))]) + ' |\n')
            
            # Write all rows
            for i in range(len(table.df)):
                row_values = [clean_text(cell) for cell in table.df.iloc[i]]
                f.write('| ' + ' | '.join(row_values) + ' |\n')
    
    logger.info(f"Table {idx} saved to {output_file}")
    return output_file


def extract_tables(pdf_path, output_dir=TABLES_DIR):
    """
    Extract tables from a PDF file using Camelot and save them as markdown.
    
    This function uses both 'stream' and 'lattice' methods to detect tables in the PDF,
    and saves each detected table as a separate markdown file.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory to save the extracted tables
        
    Returns:
        int: Number of tables extracted
    """
    logger.info(f"Extracting tables from PDF: {pdf_path}")
    
    # Get PDF filename
    pdf_filename = os.path.basename(pdf_path)
    pdf_name = os.path.splitext(pdf_filename)[0]
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Extract tables using lattice method
        logger.info("Extracting tables using 'lattice' method...")
        print("Extracting tables using 'lattice' method...")
        
        lattice_tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
        logger.info(f"Extracted {len(lattice_tables)} tables using 'lattice' method")
        print(f"Extracted {len(lattice_tables)} tables using 'lattice' method")
        
        # Extract tables using stream method
        logger.info("Extracting tables using 'stream' method...")
        print("Extracting tables using 'stream' method...")
        
        stream_tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
        logger.info(f"Extracted {len(stream_tables)} tables using 'stream' method")
        print(f"Extracted {len(stream_tables)} tables using 'stream' method")
        
        # Process lattice tables
        logger.info("Saving lattice tables...")
        print("Saving lattice tables...")
        
        lattice_count = 0
        for i, table in enumerate(lattice_tables):
            if len(table.df) > 0:  # Only save if table has content
                save_table_as_markdown(table, i+1, output_dir, f"{pdf_name}_lattice")
                lattice_count += 1
        
        # Process stream tables
        logger.info("Saving stream tables...")
        print("Saving stream tables...")
        
        stream_count = 0
        for i, table in enumerate(stream_tables):
            if len(table.df) > 0:  # Only save if table has content
                save_table_as_markdown(table, i+1, output_dir, f"{pdf_name}_stream")
                stream_count += 1
        
        total_tables = lattice_count + stream_count
        logger.info(f"Table extraction complete. Extracted {total_tables} tables.")
        print(f"Table extraction complete. Extracted {total_tables} tables.")
        return total_tables
    
    except Exception as e:
        logger.exception(f"Error extracting tables: {str(e)}")
        print(f"Error extracting tables: {str(e)}")
        return 0


def main():
    """Main function to handle command line arguments."""
    # Configure logging
    configure_logging()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Extract tables from PDF using Camelot")
    parser.add_argument("--pdf-path", default=DEFAULT_PDF_PATH, help="Path to the PDF file")
    parser.add_argument("--output-dir", default=TABLES_DIR, help="Directory to save extracted tables")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
                       default="INFO", help="Set the logging level (default: INFO)")
    args = parser.parse_args()
    
    # Set log level if specified
    if args.log_level:
        logger.setLevel(args.log_level)
        logger.info(f"Log level set to {args.log_level}")
    
    print(f"Processing PDF: {args.pdf_path}")
    
    # Extract tables
    num_tables = extract_tables(args.pdf_path, args.output_dir)
    
    if num_tables > 0:
        logger.info(f"Extracted {num_tables} tables")
        print(f"Extracted {num_tables} tables")
        return 0
    else:
        logger.warning("No tables were extracted or an error occurred")
        print("No tables were extracted or an error occurred")
        return 1


if __name__ == "__main__":
    main()
