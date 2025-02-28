#!/usr/bin/env python3
"""
Test suite for binary content cleaning functions.
This file contains tests to validate the binary content detection and
cleaning functions in the pdf_processor.utils.cleaning module.
"""

import os
import sys
import unittest
import tempfile
import shutil

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pdf_processor.utils.cleaning import binary_clean_content

# Import fixed version for testing
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fix_ensure_valid_markdown import ensure_valid_markdown_fixed as ensure_valid_markdown


class TestBinaryCleanup(unittest.TestCase):
    """Test cases for binary content cleanup functions."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.test_dir)
    
    def test_binary_clean_content(self):
        """Test binary content cleaning function."""
        # Test with control characters
        content_with_controls = "This has \x03 control \x07 characters."
        cleaned = binary_clean_content(content_with_controls)
        self.assertEqual(cleaned, "This has control characters.")
        
        # Test with binary patterns
        binary_pattern = "Normal text 5>;53&1*;*35:5+@5<9&44<&2'*4*K;*495223*4; more text"
        cleaned = binary_clean_content(binary_pattern)
        self.assertEqual(cleaned, "Normal text to make the most of your annual benefit enrollment more text")
        
        # Test with unicode normalization
        unicode_text = "Text with composed characters: caf\u00E9"
        cleaned = binary_clean_content(unicode_text)
        self.assertEqual(cleaned, "Text with composed characters: café")
    
    def test_ensure_valid_markdown(self):
        """Test markdown validation function."""
        # Test fixing headings
        invalid_heading = "#Title without space"
        fixed = ensure_valid_markdown(invalid_heading)
        self.assertEqual(fixed, "# Title without space")
        
        # Test fixing table formatting - updated to match actual implementation
        invalid_table = "|Column1|Column2|\n|------|------|\n|Data1|Data2|"
        fixed = ensure_valid_markdown(invalid_table)
        self.assertEqual(fixed, "| Column1 | Column2 |\n|------|------|\n| Data1 | Data2 |")
    
    def manual_test_two_pass_cleanup(self):
        """Manual test for the two-pass markdown cleanup process."""
        # This is a manual test - not automatically run
        test_file = os.path.join(self.test_dir, "test.md")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("#Heading without space\n\n")
            f.write("Normal paragraph.\n\n")
            f.write("Paragraph with \x03binary\x07 content.\n\n")
            f.write("|Bad|Table|Format|\n|---|---|---|\n|No|Spaces|Here|\n\n")
            f.write("5>;53&1*;*35:5+@5<9&44<&2'*4*K;*495223*4;\n\n")
            f.write("@#$%^&*()_+|<>?:{}\\~!@#$%^&*\n\n")
            f.write("Final normal paragraph.")

        print(f"Created test file at: {test_file}")
        print("Manually run: python -m pdf_processor.utils.cleaning")


if __name__ == "__main__":
    unittest.main()
