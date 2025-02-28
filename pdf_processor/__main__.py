#!/usr/bin/env python3
"""
Main entry point for the PDF processor package.

This module allows the package to be run directly using:
`python -m pdf_processor [pdf_path1] [pdf_path2] ...`
If no PDF paths are specified, it will process all PDFs in the data/sourcedocs directory.
"""

import sys
import argparse
import logging
import os
import glob
from pathlib import Path
from pdf_processor.utils.logging import configure_logging
from pdf_processor.pipeline import process_pdf
from pdf_processor.utils.ghostscript_setup import setup_ghostscript


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
        nargs="*",  # Changed from '+' to '*' to make it optional
        help="Paths to the PDF files to process. If not specified, all PDFs in data/sourcedocs will be processed."
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
    
    logger = logging.getLogger(__name__)
    
    # Setup Ghostscript for table extraction
    setup_ghostscript()
    
    # If no PDF paths are provided, use all PDFs in data/sourcedocs
    pdf_paths = args.pdf_paths
    if not pdf_paths:
        # Get the project base directory
        base_dir = Path(__file__).parent.parent
        source_dir = base_dir / "data" / "sourcedocs"
        
        # Check if the directory exists
        if not source_dir.exists():
            logger.error(f"Source directory {source_dir} does not exist!")
            return 1
        
        # Find all PDF files
        pdf_paths = list(str(p) for p in source_dir.glob("*.pdf"))
        
        if not pdf_paths:
            logger.warning(f"No PDF files found in {source_dir}")
            return 0
        
        logger.info(f"Found {len(pdf_paths)} PDF files to process in {source_dir}")
    
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
    for pdf_path in pdf_paths:
        try:
            logger.info(f"Processing {os.path.basename(pdf_path)}...")
            pdf_results = process_pdf(pdf_path, options)
            results[os.path.basename(pdf_path)] = pdf_results
            logger.info(f"Successfully processed {os.path.basename(pdf_path)}")
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            results[os.path.basename(pdf_path)] = {"error": str(e)}
    
    logger.info("All PDF processing completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
