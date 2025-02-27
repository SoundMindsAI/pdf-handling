# Source Documents Directory

This directory contains the source PDF documents to be processed by the PDF parsing tools.

## Contents

- `AEGuidebook.pdf` - Sample PDF document used for demonstration purposes

## Usage

When adding new PDF documents for processing, place them in this directory and then use the relative path from the project root:

```bash
python pdf_processing_pipeline.py --pdf_path=./sourcedocs/your_new_file.pdf
```

## Recommended Practices

1. Keep original PDF documents unmodified in this directory
2. Use descriptive filenames that reflect the document content
3. Consider adding a brief description of each document in this README file
4. For larger collections, consider organizing PDFs into subdirectories by category
