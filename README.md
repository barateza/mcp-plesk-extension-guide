# Plesk Extensions Guide MCP Server

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Server-brightgreen.svg)](https://modelcontextprotocol.io/)
[![Tests](https://github.com/barateza/extensions-guide/actions/workflows/tests.yml/badge.svg)](https://github.com/barateza/extensions-guide/actions/workflows/tests.yml)

[![Works on my machine](https://img.shields.io/badge/works%20on-my%20machine-brightgreen.svg?style=flat)](https://github.com/barateza/extensions-guide)

A Model Context Protocol (MCP) server that provides semantic search capabilities over the Plesk Extensions Guide documentation using Retrieval-Augmented Generation (RAG).

## Overview

This MCP server indexes and searches Plesk extension development documentation using vector embeddings. It allows AI assistants and applications to retrieve relevant information from the Plesk Extensions Guide through natural language queries.

### Features

- **Semantic Search**: Search documentation using natural language queries
- **Vector Embeddings**: Uses OpenRouter's text-embedding-3-small model for intelligent document matching
- **ChromaDB Storage**: Efficient vector database for fast retrieval
- **Automatic Documentation Download**: Easy setup with automated documentation fetching
- **Comprehensive Tests**: 99.78% test coverage with 31 tests

## Prerequisites

- Python 3.12 or higher
- `uv` package manager (or pip)
- `OPENROUTER_API_KEY` environment variable (for embeddings)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/barateza/extensions-guide.git
   cd extensions-guide
   ```

2. **Create a virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # macOS/Linux
   # OR
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   uv pip install -e .[dev]
   ```

## Setup

### 1. Download Documentation

The MCP server requires the Plesk Extensions Guide documentation. Download and extract it using the provided script:

```bash
uv run python scripts/download_docs.py
```

This script will:
- Download the documentation ZIP from [Plesk's documentation server](https://docs.plesk.com/en-US/obsidian/zip/extensions-guide.zip)
- Extract it to the `html/` folder
- Create the `storage/` directory for the vector database

### 2. Configure API Key

Set your OpenRouter API key as an environment variable:

```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

Or add it to a `.env` file in the project root (this file should not be committed to version control).

## Usage

The MCP server exposes two main tools for interacting with the Plesk Extensions Guide:

### 1. `search_extensions_guide`

Search the indexed documentation with a semantic query.

**Parameters**:
- `query` (string): Your search query in natural language

**Example**:
```
Query: "How do I create a custom UI form for my extension?"
```

### 2. `index_documentation`

Scan and index all documentation files. This is called automatically on first run, but can be called again to re-index.

**Parameters**: None

**Example**:
```
Index the html/ folder into the vector database
```

## Configuration

The server uses the following environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | API key for OpenRouter embeddings service | Yes |
| `CHROMA_DB_IMPL` | ChromaDB implementation (default: duckdb+parquet) | No |

## Architecture

- **[server.py](server.py)**: FastMCP server implementation with indexing and search tools
- **[main.py](main.py)**: Entry point for running the server
- **[scripts/download_docs.py](scripts/download_docs.py)**: Documentation download utility
- **html/**: Extracted Plesk Extensions Guide documentation (created after setup)
- **storage/**: Vector database storage (created automatically on first run)

## Development

### Running Tests

```bash
uv run pytest tests/ -v --tb=short
```

### Coverage Reports

```bash
uv run pytest tests/ -v --tb=short --cov-report term-missing --cov=.
```

### HTML Coverage Report

```bash
uv run pytest tests/ -v --tb=short --cov-report html --cov=.
open htmlcov/index.html
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and how to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Documentation

For more information about Plesk extension development, visit:
- [Plesk Extensions Guide](https://docs.plesk.com/en-US/obsidian/extensions-guide/)
- [Plesk API Documentation](https://docs.plesk.com/en-US/obsidian/api-docs/)

## Support

If you encounter any issues:

1. Ensure Python 3.12+ is installed
2. Verify your `OPENROUTER_API_KEY` is set correctly
3. Run `python scripts/download_docs.py` again to refresh documentation
4. Check that `html/` and `storage/` directories were created successfully

For bugs or feature requests, please open an issue on GitHub.
