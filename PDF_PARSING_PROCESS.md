# PDF Parsing Process Documentation

This document provides detailed diagrams explaining the process of converting PDF documents to structured markdown.

## High-Level Architecture

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '16px', 'fontWeight': 'bold', 'primaryTextColor': '#000000' }}}%%
graph TD
    subgraph Input
        PDF[PDF Document]
    end
    
    subgraph "Parsing Layer"
        Camelot[Camelot-py Parser]
        PyPDF[PyPDF Parser]
    end
    
    subgraph "Processing Layer"
        CleaningModule[Text Cleaning Module]
        StructureModule[Structure Detection Module]
        FieldModule[Field Extraction Module]
    end
    
    subgraph "Output Layer"
        Tables[Table Markdown]
        RawText[Raw Text Files]
        Basic[Basic Structured Markdown]
        Advanced[Advanced Structured Markdown]
    end
    
    PDF --> Camelot
    PDF --> PyPDF
    Camelot --> Tables
    PyPDF --> RawText
    RawText --> CleaningModule
    CleaningModule --> StructureModule
    StructureModule --> FieldModule
    FieldModule --> Basic
    FieldModule --> Advanced
    
    classDef input fill:#f9f,stroke:#333,stroke-width:2px,color:#000,font-weight:bold,font-size:14px;
    classDef parser fill:#bbf,stroke:#333,stroke-width:2px,color:#000,font-weight:bold,font-size:14px;
    classDef process fill:#bfb,stroke:#333,stroke-width:2px,color:#000,font-weight:bold,font-size:14px;
    classDef output fill:#fbb,stroke:#333,stroke-width:2px,color:#000,font-weight:bold,font-size:14px;
    
    class PDF input;
    class Camelot,PyPDF parser;
    class CleaningModule,StructureModule,FieldModule process;
    class Tables,RawText,Basic,Advanced output;
```

## Data Transformation Pipeline

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '16px', 'fontWeight': 'bold', 'primaryTextColor': '#000000' }}}%%
flowchart LR
    subgraph "PDF Document"
        RawPDF[Raw PDF Content]
    end
    
    subgraph "Extraction Phase"
        Tables[Table Data]
        Text[Text Content]
        Images[Images]
    end
    
    subgraph "Processing Phase"
        CleanText[Cleaned Text]
        StructuredText[Structured Text]
        SectionedText[Sectioned Text]
    end
    
    subgraph "Field Extraction Phase"
        KeyValuePairs[Key-Value Pairs]
        FormattedFields[Formatted Fields]
    end
    
    subgraph "Output Phase"
        Markdown[Markdown Document]
    end
    
    RawPDF --> Tables
    RawPDF --> Text
    RawPDF --> Images
    
    Tables --> CleanText
    Text --> CleanText
    CleanText --> StructuredText
    StructuredText --> SectionedText
    
    SectionedText --> KeyValuePairs
    KeyValuePairs --> FormattedFields
    
    FormattedFields --> Markdown
    
    classDef default color:#000,font-weight:bold,font-size:14px;
```

## PDF Parsing Strategy

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '16px', 'fontWeight': 'bold', 'primaryTextColor': '#000000' }}}%%
flowchart TD
    Start[Start] --> ReadPDF[Read PDF File]
    ReadPDF --> ExtractComponents[Extract Components]
    
    ExtractComponents --> ExtractTables[Extract Tables]
    ExtractComponents --> ExtractText[Extract Text]
    
    ExtractTables --> ProcessTables[Process Tables]
    ExtractText --> CleanText[Clean Text]
    
    CleanText --> IdentifySections[Identify Sections]
    IdentifySections --> IdentifySubsections[Identify Subsections]
    
    IdentifySubsections --> ExtractFields[Extract Fields]
    ProcessTables --> ExtractFields
    
    ExtractFields --> FormatMarkdown[Format as Markdown]
    FormatMarkdown --> WriteOutput[Write to Output File]
    WriteOutput --> End[End]
    
    classDef default color:#000,font-weight:bold,font-size:14px;
```

## Text Cleaning Process

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '16px', 'fontWeight': 'bold', 'primaryTextColor': '#000000' }}}%%
flowchart LR
    RawText[Raw Extracted Text] --> RemoveCID[Remove CID Patterns]
    RemoveCID --> FixEncoding[Fix Encoding Issues]
    FixEncoding --> NormalizeWhitespace[Normalize Whitespace]
    NormalizeWhitespace --> CleanText[Cleaned Text]
    
    classDef default color:#000,font-weight:bold,font-size:14px;
```

## Section Detection Process

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '16px', 'fontWeight': 'bold', 'primaryTextColor': '#000000' }}}%%
stateDiagram-v2
    [*] --> FullText
    FullText --> SectionIdentification: Identify Known Section Titles
    
    SectionIdentification --> SectionExtraction: Extract Section Content
    SectionExtraction --> SubsectionIdentification: Identify Subsections
    
    SubsectionIdentification --> KeyPhraseDetection: Detect Key Phrases
    SubsectionIdentification --> QuestionDetection: Detect Questions
    SubsectionIdentification --> PatternDetection: Detect Patterns
    
    KeyPhraseDetection --> SubsectionExtraction
    QuestionDetection --> SubsectionExtraction
    PatternDetection --> SubsectionExtraction
    
    SubsectionExtraction --> [*]
    
    classDef default color:#000,font-weight:bold,font-size:14px;
```

## Field Extraction Process

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '16px', 'fontWeight': 'bold', 'primaryTextColor': '#000000' }}}%%
flowchart TD
    Start[Start Field Extraction] --> LoadPatterns[Load Field Patterns]
    LoadPatterns --> ProcessContent[Process Content]
    
    ProcessContent --> MatchPatterns[Match Regex Patterns]
    MatchPatterns --> ExtractFieldNames[Extract Field Names]
    MatchPatterns --> ExtractFieldValues[Extract Field Values]
    
    ExtractFieldNames --> CleanFieldNames[Clean Field Names]
    ExtractFieldValues --> CleanFieldValues[Clean Field Values]
    
    CleanFieldNames --> CreatePairs[Create Field Name-Value Pairs]
    CleanFieldValues --> CreatePairs
    
    CreatePairs --> FormatFields[Format as Markdown Fields]
    FormatFields --> End[End Field Extraction]
    
    classDef default color:#000,font-weight:bold,font-size:14px;
```

## Comparison of PDF Parsing Methods

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '16px', 'fontWeight': 'bold', 'primaryTextColor': '#000000' }}}%%
graph TD
    subgraph "Pipeline Orchestration (pdf_processor.pipeline)"
        P1[Process PDF] --> P2[Ensure Output Directories]
        P2 --> P3[Extract Text and Tables]
        P3 --> P4[Apply Cleaning]
        P4 --> P5[Convert to Enhanced Markdown]
    end
    
    subgraph "Text Extraction (pdf_processor.extractors.text_extractor)"
        T1[Extract Text] --> T2[Clean Text]
        T2 --> T3[Save Page Files]
    end
    
    subgraph "Table Extraction (pdf_processor.extractors.table_extractor)"
        B1[Extract Tables] --> B2[Convert to Markdown]
        B2 --> B3[Save Table Files]
    end
    
    subgraph "Text Cleaning (pdf_processor.utils.cleaning)"
        C1[Basic Cleaning] --> C2[Deep Cleaning]
        C2 --> C3[Ultra-Deep Cleaning]
        C3 --> C4[Enhanced Text Fixing]
    end
    
    subgraph "Enhanced Markdown (pdf_processor.converters.enhanced_markdown)"
        I1[Extract All Text] --> I2[Clean and Process]
        I2 --> I3[Advanced Section Detection]
        I3 --> I4[Pattern-based Field Extraction]
        I4 --> I5[Generate Enhanced Markdown]
    end
    
    classDef pipeline fill:#ffcccc,stroke:#333,stroke-width:1px,color:#000,font-weight:bold,font-size:14px;
    classDef text fill:#ccffcc,stroke:#333,stroke-width:1px,color:#000,font-weight:bold,font-size:14px;
    classDef table fill:#ccccff,stroke:#333,stroke-width:1px,color:#000,font-weight:bold,font-size:14px;
    classDef cleaning fill:#ffffcc,stroke:#333,stroke-width:1px,color:#000,font-weight:bold,font-size:14px;
    classDef enhanced fill:#ffccff,stroke:#333,stroke-width:1px,color:#000,font-weight:bold,font-size:14px;
    
    class P1,P2,P3,P4,P5 pipeline;
    class T1,T2,T3 text;
    class B1,B2,B3 table;
    class C1,C2,C3,C4 cleaning;
    class I1,I2,I3,I4,I5 enhanced;
```
