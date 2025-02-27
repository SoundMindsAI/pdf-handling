# PDF Processor

> **Note:** For detailed information about our sanitization process, see [SANITIZATION.md](SANITIZATION.md)

# PDF to Markdown Parser

This repository contains a set of scripts to parse PDF documents and convert them into structured markdown format.

## Table of Contents

- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
  - [Main Components](#main-components)
  - [Helper Scripts](#helper-scripts)
  - [Output Directories](#output-directories)
- [Process Flow Diagrams](#process-flow-diagrams)
  - [Overall Workflow](#overall-workflow)
  - [Detailed Process Flow for Enhanced Parser](#detailed-process-flow-for-enhanced-parser)
  - [Component Data Flow](#component-data-flow)
- [Features](#features)
- [Advanced Features](#advanced-features)
  - [Robust Logging System](#robust-logging-system)
- [Module Usage Examples](#module-usage-examples)
  - [Using the Complete Pipeline](#using-the-complete-pipeline)
  - [Multiple Files](#multiple-files)
  - [Optional Processing Parameters](#optional-processing-parameters)
- [Scripts and Output Files](#scripts-and-output-files)
- [Managing Output Files](#managing-output-files)
  - [Cleaning Output Files](#cleaning-output-files)
  - [Deleting Output Files](#deleting-output-files)
- [Usage](#usage)
  - [Table Extraction](#table-extraction)
  - [Full Text Extraction](#full-text-extraction)
  - [Structured Markdown Generation](#structured-markdown-generation)
- [Environment Setup](#environment-setup)
- [Customization](#customization)
- [Performance Considerations](#performance-considerations)

## Project Overview

These scripts are designed to extract text and tables from PDF documents, clean the extracted data, and format it into well-structured markdown files. This can be useful for converting complex PDF documents (like guidebooks, manuals, or reports) into more accessible and readable formats.

## Project Structure

### Main Components

- **pdf_processor/**: Main package
  - **__main__.py**: Command-line interface and entry point
  - **pipeline.py**: Core processing orchestration
  - **config.py**: Configuration settings
  - **extractors/**: Text and table extraction modules
  - **converters/**: Enhanced markdown conversion module
  - **utils/**: Utility functions for cleaning and sanitization

### Helper Scripts

- **delete_outputs.py**: Script to clean output directories
- **tests/test_sanitization.py**: Demo script showing different sanitization levels

### Output Directories

- **data/outputs/text/**: Extracted text files (one per page)
- **data/outputs/tables/**: Extracted tables in markdown format
- **data/outputs/markdown/**: Structured and enhanced markdown files

## Process Flow Diagrams

### Overall Workflow

```mermaid
graph TD
    PDF[PDF Document] --> PipelineModule["pdf_processor.pipeline<br>Process PDF"]
    PipelineModule --> TextExtractor["pdf_processor.extractors.text_extractor<br>PyPDF"]
    PipelineModule --> TableExtractor["pdf_processor.extractors.table_extractor<br>Camelot-py"]
    TextExtractor --> ExtractedText["Page Text Files (.txt)"]
    TableExtractor --> TablesMarkdown["Table Markdown Files (.md)"]
    ExtractedText --> CleaningModule[pdf_processor.utils.cleaning]
    TablesMarkdown --> CleaningModule
    CleaningModule --> EnhancedMarkdown[pdf_processor.converters.enhanced_markdown]
    EnhancedMarkdown --> StructuredMD["Structured Markdown"]
    EnhancedMarkdown --> ImprovedMD["Enhanced Markdown"]
    
    classDef input fill:#ffcc80,stroke:#ff9800,stroke-width:2px,color:#000000,font-weight:bold;
    classDef process fill:#90caf9,stroke:#1976d2,stroke-width:2px,color:#000000,font-weight:bold;
    classDef output fill:#a5d6a7,stroke:#388e3c,stroke-width:2px,color:#000000,font-weight:bold;
    
    class PDF input;
    class PipelineModule,TextExtractor,TableExtractor,CleaningModule,EnhancedMarkdown process;
    class TablesMarkdown,ExtractedText,StructuredMD,ImprovedMD output;
```

### Detailed Process Flow for Enhanced Parser

```mermaid
flowchart LR
    subgraph Input["Input (PDF Source)"]
        style Input fill:#ffcc80,stroke:#ff9800,stroke-width:2px
        PDF[<font color="black">PDF Document</font>]
        style PDF fill:#ffcc80,stroke:#ff9800,stroke-width:2px
    end
    
    subgraph Extraction["Extraction Phase"]
        style Extraction fill:#90caf9,stroke:#1976d2,stroke-width:2px
        TextExtractor[<font color="black">Text Extractor Module</font>]
        TableExtractor[<font color="black">Table Extractor Module</font>]
        style TextExtractor fill:#90caf9,stroke:#1976d2,stroke-width:2px
        style TableExtractor fill:#90caf9,stroke:#1976d2,stroke-width:2px
    end
    
    subgraph Processing["Processing Phase"]
        style Processing fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px
        Cleaning[<font color="black">Text Cleaning Module</font>]
        SectionDetection[<font color="black">Section Detection</font>]
        SubsectionDetection[<font color="black">Subsection Detection</font>]
        FieldExtraction[<font color="black">Field Extraction</font>]
        style Cleaning fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px
        style SectionDetection fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px
        style SubsectionDetection fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px
        style FieldExtraction fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px
    end
    
    subgraph Output["Output Files"]
        style Output fill:#a5d6a7,stroke:#388e3c,stroke-width:2px
        TablesMD[<font color="black">Table Markdown</font>]
        PageText[<font color="black">Page Text Files</font>]
        StructuredMD[<font color="black">Structured Markdown</font>]
        EnhancedMD[<font color="black">Enhanced Markdown</font>]
        style TablesMD fill:#a5d6a7,stroke:#388e3c,stroke-width:2px
        style PageText fill:#a5d6a7,stroke:#388e3c,stroke-width:2px
        style StructuredMD fill:#a5d6a7,stroke:#388e3c,stroke-width:2px
        style EnhancedMD fill:#a5d6a7,stroke:#388e3c,stroke-width:2px
    end
    
    PDF --> TextExtractor
    PDF --> TableExtractor
    TableExtractor --> TablesMD
    TextExtractor --> PageText
    TextExtractor --> Cleaning
    Cleaning --> SectionDetection
    SectionDetection --> SubsectionDetection
    SubsectionDetection --> FieldExtraction
    FieldExtraction --> StructuredMD
    FieldExtraction --> EnhancedMD
```

### Component Data Flow

```mermaid
flowchart LR
    subgraph Input["Input (PDF Source)"]
        style Input fill:#ffcc80,stroke:#ff9800,stroke-width:2px
        PDF[<font color="black">PDF Document</font>]
        style PDF fill:#ffcc80,stroke:#ff9800,stroke-width:2px
    end
    
    subgraph Extraction["Extraction Tools"]
        style Extraction fill:#90caf9,stroke:#1976d2,stroke-width:2px
        CamelotPy[<font color="black">Camelot-py<br>Table Extraction</font>]
        PyPDF[<font color="black">PyPDF<br>Text Extraction</font>]
        style CamelotPy fill:#90caf9,stroke:#1976d2,stroke-width:2px
        style PyPDF fill:#90caf9,stroke:#1976d2,stroke-width:2px
    end
    
    subgraph Processing["Processing Components"]
        style Processing fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px
        Cleaning[<font color="black">Text Cleaning</font>]
        SectionDetection[<font color="black">Section Detection</font>]
        SubsectionDetection[<font color="black">Subsection Detection</font>]
        FieldExtraction[<font color="black">Field Extraction</font>]
        style Cleaning fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px
        style SectionDetection fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px
        style SubsectionDetection fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px
        style FieldExtraction fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px
    end
    
    subgraph Output["Output Files"]
        style Output fill:#a5d6a7,stroke:#388e3c,stroke-width:2px
        TablesMD[<font color="black">Table Markdown</font>]
        PageText[<font color="black">Page Text Files</font>]
        StructuredMD[<font color="black">Structured Markdown</font>]
        ImprovedMD[<font color="black">Improved Markdown</font>]
        style TablesMD fill:#a5d6a7,stroke:#388e3c,stroke-width:2px
        style PageText fill:#a5d6a7,stroke:#388e3c,stroke-width:2px
        style StructuredMD fill:#a5d6a7,stroke:#388e3c,stroke-width:2px
        style ImprovedMD fill:#a5d6a7,stroke:#388e3c,stroke-width:2px
    end
    
    PDF --> CamelotPy
    PDF --> PyPDF
    CamelotPy --> TablesMD
    PyPDF --> PageText
    PyPDF --> Cleaning
    Cleaning --> SectionDetection
    SectionDetection --> SubsectionDetection
    SubsectionDetection --> FieldExtraction
    FieldExtraction --> StructuredMD
    FieldExtraction --> ImprovedMD
```

## Features

- **PDF Text Extraction**: Extract text from each page of a PDF document
- **PDF Table Extraction**: Extract tables from PDFs using both lattice and stream methods
- **Structured Markdown Conversion**: Convert PDF content to well-structured markdown
- **Enhanced Formatting**: Apply advanced formatting to improve readability
- **Processing Pipeline**: Run the entire process with a single command
- **Robust Logging**: Comprehensive logging system with configurable log levels and file output

## Advanced Features

### Robust Logging System

The project includes a comprehensive logging system that provides:

1. **Console Output**: Color-coded log messages displayed in the terminal
2. **File Logging**: Detailed logs saved to timestamped files in the `logs/` directory
3. **Configurable Log Levels**: Set logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
4. **Different Log Formats**: Console logs are concise and color-coded, while file logs include timestamps and module info

Use the logging features by adding the `--log-level` argument:

```bash
# Run with detailed debugging information
python pdf_processing_pipeline.py --log-level=DEBUG

# Run with minimal logging (only warnings and errors)
python pdf_processing_pipeline.py --log-level=WARNING
```

Log files can be found in the `logs/` directory with timestamps for easy identification.

## Module Usage Examples

### Using the Complete Pipeline

Process all PDF files in the `data/sourcedocs` directory with the default settings:

```bash
python -m pdf_processor
```

To process specific PDF files:

```bash
python -m pdf_processor path/to/your/file.pdf
```

### Multiple Files

Process multiple PDF files at once:

```bash
python -m pdf_processor file1.pdf file2.pdf file3.pdf
```

### Optional Processing Parameters

```bash
python -m pdf_processor [OPTIONS] [pdf_paths ...]

Options:
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set logging level (default: INFO)
```

## Scripts and Output Files

| Module | Purpose | Output Files | Location |
|--------|---------|--------------|----------|
| **pdf_processor.extractors.table_extractor** | Extracts tables from PDF using camelot-py | Table markdown files | `outputs/tables/{pdf_name}_table_*.md` |
| **pdf_processor.extractors.text_extractor** | Extracts text from PDF pages | Text files for each page | `outputs/text/{pdf_name}_page_*.txt` |
| **pdf_processor.converters.enhanced_markdown** | Creates structured and enhanced markdown | Structured and enhanced markdown | `outputs/markdown/{pdf_name}_structured.md` & `outputs/markdown/{pdf_name}_enhanced.md` |
| **pdf_processor.pipeline** | Orchestrates the entire PDF processing pipeline | All output files | `outputs/` |
| **pdf_processor.utils.cleaning** | Sanitizes and improves extracted PDF content | Cleaned files | All output directories |
| **delete_outputs.py** | Deletes generated files to start fresh | None | N/A |

## Managing Output Files

The project includes two specialized scripts for managing output files:

### 1. Cleaning Output Files

The sanitization script can be run to fix encoding issues and improve formatting in the output files:

```bash
# Cleaning is now integrated into the main pipeline and applied automatically
# There is no need to run separate cleaning scripts

# Process your PDFs to get cleaned output
python -m pdf_processor path/to/your/file.pdf

# Process all PDFs in the data/sourcedocs directory
python -m pdf_processor
```

### 2. Deleting Output Files

The `delete_outputs.py` script is used to delete generated files to start fresh. It recreates the directory structure after deletion and always preserves README.md files.

```bash
# Delete all generated content
python delete_outputs.py

# Delete only specific output types
python delete_outputs.py --tables    # Delete only table files
python delete_outputs.py --text      # Delete only text files 
python delete_outputs.py --markdown  # Delete only markdown files

# Specify a custom output directory
python delete_outputs.py --output-dir=./custom_outputs

# Combine options as needed
python delete_outputs.py --tables --text
```

The sanitize script will:
1. Fix common encoding issues in extracted files
2. Improve formatting and readability
3. Allow selective cleanup of specific output types
4. Support custom output directories
5. Show the directory structure after deletion is complete

The delete script will:
1. Remove generated files while preserving the directory structure
2. Always preserve README.md files in output directories
3. Allow selective deletion of specific output types
4. Support custom output directories
5. Show the directory structure after deletion is complete

## Usage

### 1. Table Extraction

To extract tables from a PDF (as part of the pipeline):

```bash
python -m pdf_processor path/to/your/file.pdf
```

This will create markdown files for tables found in the PDF in the `outputs/tables` directory.

### 2. Full Text Extraction

All text extraction is handled by the main processing pipeline:

```bash
python -m pdf_processor path/to/your/file.pdf
```

This will create text files for each page of the PDF in the `outputs/text` directory.

### 3. Structured Markdown Generation

To generate structured markdown files from the PDF:

```bash
python -m pdf_processor path/to/your/file.pdf
```

This will create both `outputs/markdown/{pdf_name}_structured.md` and `outputs/markdown/{pdf_name}_enhanced.md` files with proper section recognition and field extraction.

## Environment Setup

It's recommended to use a conda environment:

```bash
# Create a new conda environment with Python 3.11
conda create -n pdf_parser python=3.11
conda activate pdf_parser

# Install dependencies using requirements.txt
pip install -r requirements.txt

# Or install packages individually
pip install pypdf==3.17.4 camelot-py==1.0.0 pandas==2.2.3 opencv-python-headless tabulate pdfminer-six
```

On macOS, you may need to install ghostscript (required by camelot-py):
```bash
# Using Homebrew
brew install ghostscript

# Using MacPorts
port install ghostscript
```

On Linux:
```bash
# Debian/Ubuntu
sudo apt-get install ghostscript

# Fedora/RHEL
sudo dnf install ghostscript
```

On Windows:
```bash
# Using Chocolatey
choco install ghostscript
```

## Customization

- **Known Sections**: Edit the `KNOWN_SECTIONS` list in the scripts to match the sections in your PDF.
- **Field Patterns**: Modify the `FIELD_PATTERNS` list in `pdf_to_enhanced_markdown.py` to extract specific fields from your PDF.
- **Subsection Mapping**: Update the `SECTION_SUBSECTIONS` dictionary to define expected subsections for each main section.

## Performance Considerations

- Large PDFs may require more processing time
- Complex formatting in PDFs might affect extraction accuracy
- PDFs with unusual characters or encoding may require additional cleaning steps
