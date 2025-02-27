#!/usr/bin/env python3
"""
Main entry point for the PDF processor package.

This module allows the package to be run directly using:
`python -m pdf_processor [pdf_path1] [pdf_path2] ...`
"""

import sys
import argparse
import logging
import os
from pdf_processor.utils.logging import configure_logging
from pdf_processor.pipeline import process_pdf


def main():
    """
    Main entry point function handling command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="PDF Processor - Extract and convert PDF documents"
    )
    
    # Add the command line arguments
    parser.add_argument(
        "pdf_paths", 
        nargs="+",
        help="Paths to the PDF files to process"
    )
    parser.add_argument(
        "--log-level", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO", 
        help="Set the logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = getattr(logging, args.log_level)
    configure_logging(console_level=log_level)
    
    # Set processing options
    options = {
        'clean': True,  # Cleaning is always enabled
        'extract_text': True,  # Text extraction is always enabled
        'extract_tables': True,  # Table extraction is always enabled
        'basic_markdown': False,  # Basic markdown is completely removed
        'enhanced_markdown': True,  # Enhanced markdown is always enabled
        'sanitize': True,  # Sanitization is always enabled
    }
    
    # Call the pipeline main function
    results = {}
    for pdf_path in args.pdf_paths:
        try:
            pdf_results = process_pdf(pdf_path, options)
            results[os.path.basename(pdf_path)] = pdf_results
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing {pdf_path}: {e}")
            results[os.path.basename(pdf_path)] = {"error": str(e)}
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
