# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Paper Search Assistant (论文检索助手)** - A minimal CLI tool for searching and downloading academic papers from multiple databases (arXiv, PubMed, ACM). Optimized for AI agent consumption.

**Project Root:** `D:\projects\paper-search\`

---

## Development Environment

### Python Virtual Environment

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate.bat

# Deactivate
deactivate
```

**Python Version:** 3.12.4

---

## Common Commands

### Run Test Scripts

```bash
# Test arXiv search functionality
python script\test_arxiv.py

# Test PDF download functionality
python script\test_download.py

# Test email notification system
python script\notify.py
```

### Install Dependencies

```bash
# After activating venv
pip install arxiv paper-qa requests
```

---

## Project Structure

```
paper-search/
├── queries/           # Query text files for paper searches
├── papers/            # Downloaded PDF storage
│   ├── test_arxiv/    # Test search results
│   └── test_download/ # Test download results
├── script/            # Utility and test scripts
│   ├── test_arxiv.py      # arXiv search test (working)
│   ├── test_download.py   # PDF download test (working)
│   └── notify.py          # Email notification module
├── config/            # Configuration files (currently empty)
├── venv/              # Python virtual environment
└── edlib-1.3.9.post1/ # edlib source (for debugging findpapers)
```

---

## Architecture

### Core Components

1. **arxiv Library** - Primary method for paper search and download
   - Supports complex queries: `("machine learning" OR AI) AND (music OR audio)`
   - Retrieves metadata (title, authors, abstract, PDF URL)
   - Downloads PDF files directly

### Search Query Syntax (arXiv)

```python
# Simple query
query = "machine learning music"

# Complex boolean operators
query = '("machine learning" OR AI) AND (music OR audio) NOT review'

# Using arxiv.Search
search = arxiv.Search(
    query=query,
    max_results=5,
    sort_by=arxiv.SortCriterion.Relevance
)
```

---

## Known Issues

### findpapers Installation Blocked

**Status:** edlib dependency fails to compile

**Root Cause:** edlib has hardcoded checks for "Microsoft Visual C++ 14.0 or greater" and rejects VS 18 (Visual Studio 2022) across multiple layers (Cython precompiled files, setuptools checks).

**Impact:** Cannot use multi-database search tools like findpapers

**Workaround:** Use `arxiv` official library (single database, fully functional)

**Related Files:**
- `edlib-1.3.9.post1/edlib.bycython.cpp` - Contains hardcoded VS version check
- `edlib-1.3.9.post1/setup.py` - Build configuration

---

## Session Recovery

The project maintains session context in `.session_memory.md`. If resuming work after a break, reference this file for current state and next steps.

---

## Development Notes

- **Working Solution:** arxiv official library (tested and stable)
- **Blocked:** Multi-database support via findpapers/edlib
- **Email System:** Fully configured and tested
- **File Naming:** Downloaded PDFs named by arXiv ID (e.g., `2402.12345.pdf`)
