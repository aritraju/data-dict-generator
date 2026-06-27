# AI Data Dictionary Generator — Auto-Document Any Database

An AI-powered tool that points at any SQLite or DuckDB database and automatically generates a **complete, professional data catalog** — table descriptions, column definitions, data quality warnings, and usage examples — using a local LLM (no API cost).

Output is a clean HTML data catalog and Markdown documentation, ready to share with your team or drop into Confluence/GitHub Wiki.

---

## Architecture

```
[Database] (SQLite / DuckDB)
       │
       ▼
[Schema Introspector]          ← reads table DDL, column types, FK relationships
       │
       ▼
[Data Profiler]                ← row counts, null %, cardinality, min/max, samples
       │
       ▼
[Ollama LLM — qwen3.5:latest]  ← generates descriptions, purpose, example SQL
       │
       ▼
[Jinja2 Template Engine]       ← renders HTML + Markdown catalog
       │
       ├── output/catalog.html     ← interactive searchable HTML catalog
       └── output/catalog.md       ← Markdown for GitHub Wiki / Confluence
```

---

## Tech Stack

| Component | Tool | Cost |
|-----------|------|------|
| Database | SQLite / DuckDB | Free |
| LLM | Ollama + qwen3.5:latest | Free (local) |
| Templating | Jinja2 | Free |
| Data Profiling | Pandas + DuckDB | Free |
| UI | Streamlit | Free |
| Output | HTML + Markdown | Free |
| Package Manager | uv | Free |

---

## Project Structure

```
data-dict-generator/
├── README.md
├── pyproject.toml            # uv project config & dependencies
├── uv.lock                   # locked dependency versions
├── requirements.txt          # legacy reference (uv is used instead)
├── .env
├── .env.example
├── start.sh                  # one-command startup
├── sample_data/
│   ├── create_sample_db.py   # creates a realistic healthcare-style SQLite DB
│   └── healthcare_sample.db  # auto-generated sample database
├── src/
│   ├── __init__.py
│   ├── introspector.py       # schema & DDL extraction
│   ├── profiler.py           # statistical data profiling
│   ├── llm_describer.py      # Ollama LLM description generator
│   └── catalog_builder.py    # orchestrates full catalog generation
├── templates/
│   ├── catalog.html.j2       # Jinja2 HTML template
│   └── catalog.md.j2         # Jinja2 Markdown template
├── output/                   # generated catalogs go here
│   └── .gitkeep
├── app.py                    # Streamlit UI
├── generate.py               # CLI: generate catalog from command line
└── tests/
    ├── __init__.py
    ├── test_introspector.py
    └── test_profiler.py
```

---

## Setup & Installation

### Prerequisites
- macOS, Python 3.11+
- [uv](https://docs.astral.sh/uv/) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Ollama running with qwen3.5 pulled:
  ```bash
  ollama pull qwen3.5:latest
  ```

### Step 1 — Install dependencies
```bash
git clone https://github.com/YOUR_USERNAME/data-dict-generator.git
cd data-dict-generator
uv sync
```

### Step 2 — Create the sample database
```bash
uv run python sample_data/create_sample_db.py
# Creates: sample_data/healthcare_sample.db
# Tables: patients, encounters, diagnoses, medications, providers, claims
```

### Step 3 — Generate the catalog (CLI)
```bash
# Point at the sample database
uv run python generate.py --db sample_data/healthcare_sample.db

# Or your own SQLite database
uv run python generate.py --db /path/to/your/database.db --output-dir output/

# Fast mode — schema + profiling only, no LLM
uv run python generate.py --db sample_data/healthcare_sample.db --no-llm
```

### Step 4 — Launch the Streamlit app
```bash
./start.sh
# Opens http://localhost:8502
```

Or manually:
```bash
uv run streamlit run app.py --server.port 8502
```

---

## Configuration

Edit `.env` (copy from `.env.example`):

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:latest
OUTPUT_DIR=./output
```

---

## What Gets Generated

For every table, the catalog includes:

| Section | Details |
|---------|---------|
| **AI Description** | LLM-generated plain English explanation of the table's purpose |
| **Column Definitions** | Name, type, nullable, AI-generated one-sentence description |
| **Data Profile** | Row count, null %, cardinality, min/max/avg for numerics |
| **Sample Values** | Top 5 most frequent values per column |
| **Relationships** | Foreign key relationships mapped across tables |
| **Usage Examples** | LLM-generated example SQL queries |
| **Data Quality Warnings** | Columns with >20% nulls or suspiciously low cardinality |

---

## Running Tests
```bash
uv run pytest tests/ -v
```

---

## Potential Extensions
- Connect directly to BigQuery or PostgreSQL for production catalogs
- Add data freshness tracking (last updated timestamps)
- Export to dbt schema.yml format
- Push to Confluence or Notion via their APIs

---

## Author
**Aritra Ghorai** — Senior Data Engineer  
[LinkedIn](https://linkedin.com/in/YOUR_PROFILE) | [GitHub](https://github.com/YOUR_USERNAME)
