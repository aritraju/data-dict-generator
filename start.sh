#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "ERROR: Ollama is not running. Start it with: ollama serve"
  exit 1
fi

echo "Starting data-dict-generator on http://localhost:8502 ..."
uv run streamlit run app.py --server.port 8502 --server.headless true
