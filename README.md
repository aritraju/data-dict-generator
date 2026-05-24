# 📖 AI Data Dictionary Generator — Auto-Document Any Database

An AI-powered tool that points at any SQLite or DuckDB database and automatically generates a **complete, professional data catalog** — table descriptions, column definitions, data lineage notes, and usage examples — using a local LLM (no API cost).

Output is a clean HTML data catalog and Markdown documentation, ready to share with your team or drop into Confluence/GitHub Wiki.

---

## 🏗️ Architecture

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
[Ollama LLM — llama3.2]        ← generates descriptions, lineage notes, usage tips
       │
       ▼
[Jinja2 Template Engine]       ← renders HTML + Markdown catalog
       │
       ├── output/catalog.html     ← interactive searchable HTML catalog
       └── output/catalog.md       ← Markdown for GitHub Wiki / Confluence
```

---

## 🛠️ Tech Stack

| Component | Tool | Cost |
|-----------|------|------|
| Database | SQLite / DuckDB | Free |
| LLM | Ollama + LLaMA3.2 | Free (local) |
| Templating | Jinja2 | Free |
| Data Profiling | Pandas + DuckDB | Free |
| UI | Streamlit | Free |
| Output | HTML + Markdown | Free |

---

## 📁 Project Structure

```
data-dict-generator/
├── README.md
├── requirements.txt
├── .env.example
├── sample_data/
│   ├── create_sample_db.py       # Creates a realistic healthcare-style SQLite DB
│   └── healthcare_sample.db      # Auto-generated sample database
├── src/
│   ├── __init__.py
│   ├── introspector.py           # Schema & DDL extraction
│   ├── profiler.py               # Statistical data profiling
│   ├── llm_describer.py          # Ollama LLM description generator
│   └── catalog_builder.py        # Orchestrates full catalog generation
├── templates/
│   ├── catalog.html.j2           # Jinja2 HTML template
│   └── catalog.md.j2             # Jinja2 Markdown template
├── output/                       # Generated catalogs go here
│   └── .gitkeep
├── app.py                        # Streamlit UI
├── generate.py                   # CLI: generate catalog from command line
└── tests/
    ├── __init__.py
    ├── test_introspector.py
    └── test_profiler.py
```

---

## 🚀 Setup & Installation

### Prerequisites
- macOS, Python 3.10+
- Ollama running with LLaMA3.2 pulled (see RAG project setup)

### Step 1 — Install Dependencies
```bash
git clone https://github.com/YOUR_USERNAME/data-dict-generator.git
cd data-dict-generator

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2 — Create Sample Database
```bash
python sample_data/create_sample_db.py
# Creates: sample_data/healthcare_sample.db
# Tables: patients, encounters, diagnoses, medications, providers, claims
```

### Step 3 — Generate the Data Catalog (CLI)
```bash
# Point at the sample database
python generate.py --db sample_data/healthcare_sample.db

# Or your own SQLite database
python generate.py --db /path/to/your/database.db --output-dir output/

# Skip LLM descriptions (fast mode — just schema + profiling)
python generate.py --db sample_data/healthcare_sample.db --no-llm
```

### Step 4 — View the Catalog
```bash
# Open the HTML catalog in your browser
open output/catalog.html

# Or launch the interactive Streamlit app
streamlit run app.py
```

---

## 📊 What Gets Generated

For every table, the catalog includes:

| Section | Details |
|---------|---------|
| **AI Description** | LLM-generated plain English explanation of the table's purpose |
| **Column Definitions** | Name, type, nullable, AI-generated description |
| **Data Profile** | Row count, null %, cardinality, min/max/avg for numerics |
| **Sample Values** | Top 5 most frequent values per column |
| **Relationships** | Foreign key relationships and inferred lineage |
| **Usage Examples** | LLM-generated example SQL queries |
| **Data Quality Notes** | Columns with high null rates, low cardinality warnings |

---

## 🧪 Running Tests
```bash
pytest tests/ -v
```

---

## 🌱 Potential Extensions
- Add DuckDB support (already stubbed in introspector)
- Connect directly to BigQuery or PostgreSQL for production catalogs
- Add data freshness tracking (last updated timestamps)
- Export to dbt schema.yml format
- Push to Confluence or Notion via their APIs

---

## 👤 Author
**Aritra Ghorai** — Senior Data Engineer  
[LinkedIn](https://linkedin.com/in/YOUR_PROFILE) | [GitHub](https://github.com/YOUR_USERNAME)
