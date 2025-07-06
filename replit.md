# Conversation Parser

## Overview

This is a Python-based conversation parser application that processes text-based conversation files (typically from messaging platforms) and generates structured RAG-optimized JSON and Markdown outputs. The system extracts messages, metadata, and conversation context from raw text files and organizes them into weekly chunks for efficient retrieval and analysis.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

**Core Components:**
- **Main Entry Point** (`main.py`): Command-line interface and orchestration
- **Parser Engine** (`conversation_parser.py`): Central coordinator for the parsing process
- **Message Parser** (`parsers/message_parser.py`): Extracts structured data from raw conversation text
- **Formatters** (`formatters/`): Generate JSON and Markdown outputs optimized for RAG consumption
- **Utilities** (`utils/`): Date handling and file system operations

**Processing Flow:**
1. Input validation and file reading
2. Message extraction and parsing
3. Temporal organization (weekly grouping)
4. Format conversion (JSON/Markdown)
5. Output generation and archiving

## Key Components

### Message Parser (`parsers/message_parser.py`)
- **Purpose**: Extracts structured message data from conversation text files
- **Key Features**: 
  - Regex-based pattern matching for message headers
  - Handles multiple message types (incoming, outgoing, notifications)
  - Extracts metadata like timestamps, senders, and message content
- **Architecture Decision**: Uses regex patterns for flexibility in parsing various conversation formats

### Formatters (`formatters/`)
- **JSON Formatter**: Creates structured JSON optimized for RAG indexing with metadata, analytics, and searchable content
- **Markdown Formatter**: Generates human-readable Markdown files with proper sectioning and formatting
- **Architecture Decision**: Separate formatters allow for easy extension to additional output formats

### Date Utilities (`utils/date_utils.py`)
- **Purpose**: Handles temporal organization and week-based grouping
- **Key Features**: Calculates week boundaries, provides calendar context
- **Architecture Decision**: Week-based chunking strategy optimizes for both human consumption and RAG retrieval

### File Utilities (`utils/file_utils.py`)
- **Purpose**: Manages file system operations and output organization
- **Key Features**: Directory management, safe filename generation
- **Architecture Decision**: Centralized file operations ensure consistent handling across the application

## Data Flow

1. **Input Processing**: Raw conversation text files are read and validated
2. **Message Extraction**: Text is parsed using regex patterns to identify message boundaries and extract structured data
3. **Temporal Organization**: Messages are grouped by week using date utilities
4. **Format Generation**: Both JSON and Markdown files are created for each week
5. **Output Packaging**: Files are organized in a structured directory hierarchy

## External Dependencies

The application uses only Python standard library modules:
- `os`, `sys`: File system and command-line operations
- `zipfile`: Archive creation
- `datetime`, `timedelta`: Date and time handling
- `collections.defaultdict`: Data organization
- `json`: JSON serialization
- `re`: Regular expression parsing
- `pathlib`, `shutil`: Advanced file operations
- `calendar`: Calendar utilities

**Architecture Decision**: Standard library only approach ensures minimal dependencies and easy deployment.

## Deployment Strategy

**Local Execution Model:**
- Command-line application designed for local file processing
- No server components or external services required
- Input: Text conversation files
- Output: Structured ZIP archives containing weekly JSON and Markdown files

**Usage Pattern:**
```bash
python main.py <conversation_file_path>
```

**Architecture Decision**: Simple CLI approach prioritizes ease of use and eliminates infrastructure complexity.

## Changelog

- July 06, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.