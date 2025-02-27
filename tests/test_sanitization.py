#!/usr/bin/env python3
"""
Test script to demonstrate the PDF cleaning functionality.

This script creates a sample text file with garbled content and processes it
with the cleaning utilities to show how text is improved.
"""

import os
import tempfile
import shutil
from pathlib import Path

# Import the cleaning functions from our consolidated module
from pdf_processor.utils.cleaning import clean_single_file

# Sample garbled text
SAMPLE_TEXT = """
5>tomake;.*most5+yourannualbenefitsenrollment

44<&2 495223*4;</)*'551

can.*26@5</+@5<make359*(54K)*4;decisionsaboutyourbenefitchoicesso@5<can
make;.*most5+youroptions/4;.*year ahead.

	=*4/+@5<alreadyhavebenefits,/;'goodtorevisityourselectionseachyear
tomakesurethatthey'9*stillthebest(.5/(*:+59@5<

&:(.&4,*:/4yourfamily,location,59employer,make@5<eligibleto&)0<:;your'*4*K;:
"""

def main():
    """
    Run the test demonstration.
    """
    # Create a temporary directory
    base_dir = tempfile.mkdtemp()
    print(f"Using temporary directory: {base_dir}")
    
    try:
        # Create text directory and sample file
        text_dir = os.path.join(base_dir, "text")
        os.makedirs(text_dir, exist_ok=True)
        
        sample_file = os.path.join(text_dir, "sample.txt")
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(SAMPLE_TEXT)
        
        print("\nOriginal text:")
        print("-" * 60)
        with open(sample_file, 'r', encoding='utf-8') as f:
            print(f.read())
        
        # Apply our unified cleaning approach
        print("\nAfter cleaning:")
        print("-" * 60)
        
        # Clean the sample text file
        cleaned = clean_single_file(sample_file)
        
        # Display the result
        with open(sample_file, 'r', encoding='utf-8') as f:
            print(f.read())
        
        print(f"\nCleaning stats: {cleaned}")
            
    finally:
        # Clean up the temporary directory
        shutil.rmtree(base_dir)
        print("\nTemporary directory removed.")

if __name__ == "__main__":
    main()
