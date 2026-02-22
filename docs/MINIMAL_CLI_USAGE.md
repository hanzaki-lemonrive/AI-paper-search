# Paper Search Minimal CLI - Copaw Integration Guide

## Overview

The minimal CLI (`paper_search.py`) is optimized for AI agent consumption (e.g., Copaw). It provides clean JSON output, clear status codes, and focuses on core functionality.

## Features

- Multi-database search (arXiv, PubMed, ACM, IEEE, Scopus)
- Automatic PDF download for arXiv papers
- Clean JSON output for easy parsing
- Clear exit codes (0 = success, 1 = error)
- Findpapers query format (no conversion needed)

## Installation

```bash
# Install dependencies
pip install findpapers arxiv
```

## Usage

### Basic Usage

```bash
python paper_search.py "[query]"
```

### Examples

```bash
# Simple query
python paper_search.py "[biology]" -l 10

# Boolean query
python paper_search.py "[AI] AND [healthcare]" -l 20

# Multi-database search (per-database limit)
python paper_search.py "[machine learning]" --limit-per-db 10 -l 50

# Skip PDF download
python paper_search.py "[biology]" --no-pdf

# Custom output directory
python paper_search.py "[AI]" -o papers/my_search

# JSON output (for agent parsing)
python paper_search.py "[biology]" --json
```

## JSON Output Format

```json
{
  "status": "success",
  "query": "[biology]",
  "total": 3,
  "output_dir": "D:\\projects\\paper-search\\papers\\search_20260222_183628",
  "json_file": "D:\\projects\\paper-search\\papers\\search_20260222_183628\\results.json",
  "pdf_dir": "D:\\projects\\paper-search\\papers\\search_20260222_183628\\pdfs",
  "pdfs_downloaded": 3,
  "by_database": {
    "arXiv": 3
  },
  "papers": [
    {
      "title": "Paper Title",
      "authors": ["Author 1", "Author 2"],
      "year": "2026",
      "abstract": "First 500 chars of abstract...",
      "database": "arXiv",
      "urls": ["https://arxiv.org/pdf/xxxx.xxxxx"],
      "pdf_path": "/path/to/pdf.pdf",
      "pdf_downloaded": true
    }
  ]
}
```

## Exit Codes

- `0`: Success
- `1`: Error (check JSON output for details)

## Copaw Integration

### Example: Search and Analyze

```python
# In Copaw agent
import subprocess
import json

# Run search
result = subprocess.run(
    ["python", "paper_search.py", "[AI] AND [healthcare]", "-l", "10", "--json"],
    capture_output=True,
    text=True
)

# Parse result
data = json.loads(result.stdout)

if data["status"] == "success":
    print(f"Found {data['total']} papers")
    for paper in data["papers"]:
        print(f"- {paper['title']}")
        if paper["pdf_downloaded"]:
            print(f"  PDF: {paper['pdf_path']}")
```

### Example: Iterative Search

```python
queries = [
    "[AI] AND [healthcare]",
    "[machine learning] AND [medicine]",
    "[deep learning] AND [clinical]"
]

results = []
for query in queries:
    result = subprocess.run(
        ["python", "paper_search.py", query, "-l", "5", "--json", "--no-pdf"],
        capture_output=True,
        text=True
    )
    data = json.loads(result.stdout)
    results.append(data)

# Analyze results across queries
all_papers = [p for r in results for p in r["papers"]]
print(f"Total unique papers: {len(all_papers)}")
```

## Query Format

Findpapers uses bracket notation:

- Simple term: `[biology]`
- Phrase: `["machine learning"]`
- AND: `[AI] AND [healthcare]`
- OR: `[AI] OR [machine learning]`
- NOT: `[AI] AND NOT [review]`

## Output Files

- `results.json`: Full findpapers output (rich metadata)
- `pdfs/`: Downloaded PDF files (arXiv only)
- Filenames: `{arxiv_id}.pdf`

## Notes

- Logs go to stderr (won't interfere with JSON parsing)
- Only arXiv PDFs are downloaded automatically
- Other databases require manual download (needs subscription)
- Use `--no-pdf` for metadata-only searches
- Use `--limit-per-db` to enable multi-database search

## Differences from Full Version

**Removed:**
- Web interface (Flask)
- Query format conversion (use findpapers format directly)
- PaperQA integration (Copaw handles analysis)
- Email notifications
- Auto-open folder

**Kept:**
- Core search functionality
- PDF download (arXiv)
- JSON output
- Multi-database support
