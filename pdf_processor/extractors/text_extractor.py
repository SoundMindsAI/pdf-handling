#!/usr/bin/env python3
"""
PDF Text Extractor Module

This module extracts text from each page of a PDF file and saves the text as individual
files in the specified output directory.
"""

import os
import re
import argparse
from pathlib import Path
from pypdf import PdfReader

from pdf_processor.config import DEFAULT_PDF_PATH, TEXT_DIR
from pdf_processor.utils.logging import configure_logging, get_logger

# Get logger for this module
logger = get_logger(__name__)


def clean_text(text):
    """
    Clean extracted text to improve readability.
    
    Args:
        text (str): Raw text extracted from PDF
        
    Returns:
        str: Cleaned text
    """
    # Replace common PDF artifacts
    replacements = [
        # Remove CID pattern
        (r'\(cid:\d+\)', ''),
        # Fix common encoding issues with quotes
        (r'â€œ', '"'),
        (r'â€', '"'),
        # Fix apostrophes
        (r'â€™', "'"),
        # Fix dashes
        (r'â€"', '-'),
        # Fix bullet points
        (r'â€¢', '•'),
        # Remove form feed characters
        (r'\f', '\n\n'),
        # Normalize multiple spaces
        (r' +', ' '),
        # Normalize multiple newlines
        (r'\n{3,}', '\n\n'),
    ]
    
    logger.debug("Cleaning text with pattern replacements")
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    
    return text.strip()


def extract_text_from_pdf(pdf_path, output_dir=TEXT_DIR):
    """
    Extract text from each page of a PDF.
    
    This function:
    1. Opens the PDF file
    2. Iterates through each page
    3. Extracts and cleans the text
    4. Saves each page as a separate text file
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory to save extracted text
        
    Returns:
        int: Number of pages processed
    """
    logger.info(f"Extracting text from PDF: {pdf_path}")
    pdf_filename = os.path.basename(pdf_path)
    pdf_name = os.path.splitext(pdf_filename)[0]
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Open the PDF file
        logger.debug(f"Opening PDF file: {pdf_path}")
        pdf = PdfReader(pdf_path)
        num_pages = len(pdf.pages)
        
        logger.info(f"PDF has {num_pages} pages")
        print(f"PDF has {num_pages} pages")
        
        # Process each page
        for i in range(num_pages):
            logger.debug(f"Processing page {i+1}/{num_pages}")
            # Extract text from the page
            page = pdf.pages[i]
            raw_text = page.extract_text()
            
            # Clean the extracted text
            cleaned_text = clean_text(raw_text)
            
            # Save to file
            output_file = os.path.join(output_dir, f"{pdf_name}_page_{i+1}.txt")
            logger.debug(f"Saving page {i+1} to {output_file}")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
        
        logger.info(f"Extracted text from {num_pages} pages to {output_dir}")
        print(f"Extracted text from {num_pages} pages to {output_dir}")
        return num_pages
    
    except Exception as e:
        logger.exception(f"Error extracting text from PDF: {str(e)}")
        print(f"Error extracting text from PDF: {str(e)}")
        return 0


def main():
    """Main function to handle command line arguments."""
    # Configure logging
    configure_logging()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Extract text from PDF using PyPDF")
    parser.add_argument("--pdf-path", default=DEFAULT_PDF_PATH, help="Path to the PDF file")
    parser.add_argument("--output-dir", default=TEXT_DIR, help="Directory to save extracted text")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
                       default="INFO", help="Set the logging level (default: INFO)")
    args = parser.parse_args()
    
    # Set log level if specified
    if args.log_level:
        logger.setLevel(args.log_level)
        logger.info(f"Log level set to {args.log_level}")
    
    print(f"Processing PDF: {args.pdf_path}")
    
    # Extract text
    num_pages = extract_text_from_pdf(args.pdf_path, args.output_dir)
    
    if num_pages > 0:
        logger.info("Text extraction complete")
        print(f"Text extraction complete. Extracted {num_pages} pages to {args.output_dir}")
        return 0
    else:
        logger.error("Text extraction failed")
        print("Text extraction failed.")
        return 1


if __name__ == "__main__":
    main()
