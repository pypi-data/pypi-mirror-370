# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

doc-lsp is a Language Server Protocol implementation that provides documentation hover capabilities by loading documentation from separate markdown files. When a variable is selected in an editor, the LSP shows documentation from a corresponding `.md` file.

## Development Commands

### Installation and Setup
```bash
# Install dependencies using uv (recommended)
uv sync

# Or install using pip
pip install -e .
```

### Running the LSP Server
```bash
# Run directly with uv
uv run doc-lsp

# Or after installation
doc-lsp
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_python.py

# Run with coverage (requires pytest-cov)
uv run pytest --cov=doc_lsp
```

### Code Quality
No linting or formatting tools are currently configured. Consider adding:
- `ruff` for Python linting and formatting
- `mypy` for type checking (pydantic is already in use)

## Architecture

### Core Components

1. **LSP Server** (`src/doc_lsp/__init__.py`):
   - Built on `pygls` library
   - Implements `TEXT_DOCUMENT_HOVER` feature for variable documentation
   - Detects variables at cursor position across supported file types
   - Loads and caches corresponding `.md` documentation files
   - Entry point is `main()` function that starts the server

2. **Parser Module** (`src/doc_lsp/parser.py`):
   - Defines data models using Pydantic:
     - `Variable`: Represents a documented variable with name, doc, parent/children relationships
     - `Document`: Contains lookup table of variables by path
     - `Header/HeaderTree`: Intermediate models for parsing markdown structure
   - Core parsing functions:
     - `parse_header_tree()`: Parses markdown into header hierarchy respecting nesting levels
     - `parse_document()`: Converts header tree into Document with Variables for quick lookup

### Documentation Format

The LSP expects documentation in markdown files with specific structure:
- Source file `filename.ext` → Documentation file `filename.ext.md`
- Variables are documented with `##` headers followed by blockquotes
- Supports nested variables using heading levels (###, ####, etc.)
- Variable names can include optional type/default values after `=` (ignored by parser)
- Supports dynamic keys with `{key}` for dicts and `[item]` for lists

### Key Implementation Notes

1. The parser handles multiple variable name formats:
   - Simple: `VARIABLE`
   - Dotted: `PARENT.CHILD`
   - Double underscore: `PARENT__CHILD`
   - All are case-insensitive

2. The LSP server implementation:
   - Detects variables at cursor position using word boundaries
   - Supports file extensions: `.py`, `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.conf`, `.properties`
   - Looks up documentation from `{filename}.{ext}.md` in the same directory
   - Returns formatted markdown hover content

3. Caching strategy:
   - Documentation files are cached based on modification time
   - Cache is invalidated via `workspace/didChangeWatchedFiles` when `.md` files change
   - Prevents re-parsing unchanged documentation files

## Dependencies

- **pygls**: LSP server framework (from git repository)
- **pydantic**: Data validation and models
- **pyyaml**: YAML file parsing
- **rich**: Terminal output formatting
- Python 3.11+ required

## CI/CD

The project uses GitHub Actions for continuous integration:

### Workflows

1. **test.yml**: Runs on push/PR to main branch
   - Tests on multiple OS (Ubuntu, Windows, macOS)
   - Tests on Python 3.11, 3.12, 3.13
   - Generates code coverage reports
   - Uploads coverage to Codecov
   - Runs linting checks (ruff, mypy)

2. **release.yml**: Triggered on version tags (v*)
   - Builds the package
   - Creates GitHub release
   - Publishes to PyPI (if token configured)

### Coverage

- Target: 80% code coverage
- Current: ~89% coverage
- Reports uploaded to Codecov
- HTML coverage reports available as artifacts