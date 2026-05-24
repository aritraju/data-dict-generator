"""
src/llm_describer.py
Uses Ollama local LLM to generate plain-English descriptions for tables and columns.
Falls back gracefully if Ollama is unavailable.
"""

import json
import logging
import os
import requests
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/") + "/api/generate"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


def _call_ollama(prompt: str, max_tokens: int = 256) -> Optional[str]:
    """Call Ollama API. Returns None on failure."""
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": max_tokens}
            },
            timeout=60
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        logger.warning("Ollama not available. Using placeholder descriptions.")
        return None
    except Exception as e:
        logger.warning(f"Ollama call failed: {e}")
        return None


def describe_table(
    table_name: str,
    columns: List[str],
    row_count: int,
    sample_values: Dict[str, List],
    foreign_keys: List[Dict],
    ddl: str
) -> Dict[str, str]:
    """
    Generate AI description, purpose, and example query for a table.
    Returns dict with keys: description, purpose, example_query
    """
    fk_desc = ""
    if foreign_keys:
        fk_desc = "It has foreign key relationships to: " + ", ".join(
            f"{fk['to_table']} (via {fk['from_column']})" for fk in foreign_keys
        )

    prompt = f"""You are a senior data engineer writing documentation for a data catalog.

Database table: {table_name}
Row count: {row_count:,}
Columns: {', '.join(columns)}
{fk_desc}

DDL:
{ddl[:1000]}

Write the following in clear, professional plain English:
1. DESCRIPTION: One paragraph describing what this table stores and its role in the data model.
2. PURPOSE: One sentence on the business purpose.
3. EXAMPLE_QUERY: One useful example SQL SELECT query against this table (with a comment explaining it).

Format your response as JSON with keys: description, purpose, example_query
Respond only with the JSON object, no markdown fences."""

    response = _call_ollama(prompt, max_tokens=400)

    if response:
        try:
            # Strip possible markdown fences
            clean = response.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            return json.loads(clean)
        except json.JSONDecodeError:
            pass

    # Fallback
    return {
        "description": f"The {table_name} table stores records related to {table_name.replace('_', ' ')}. It contains {row_count:,} rows and {len(columns)} columns.",
        "purpose": f"Stores {table_name.replace('_', ' ')} data for operational and analytical use.",
        "example_query": f"SELECT * FROM {table_name} LIMIT 10;"
    }


def describe_column(
    table_name: str,
    column_name: str,
    data_type: str,
    nullable: bool,
    is_pk: bool,
    sample_values: List[Any],
    null_pct: float
) -> str:
    """
    Generate a one-sentence description for a single column.
    Returns a description string.
    """
    pk_note = " (Primary Key)" if is_pk else ""
    sample_str = str(sample_values[:3]) if sample_values else "N/A"

    prompt = f"""You are writing a data catalog entry for a database column.

Table: {table_name}
Column: {column_name}{pk_note}
Type: {data_type}
Nullable: {nullable}
Null rate: {null_pct}%
Sample values: {sample_str}

Write one concise sentence (max 20 words) describing what this column stores.
No preamble, no formatting — just the sentence."""

    response = _call_ollama(prompt, max_tokens=60)
    if response:
        # Clean up common LLM response artifacts
        return response.strip().strip('"').strip("'")

    # Fallback description
    if is_pk:
        return f"Unique identifier for each record in the {table_name} table."
    if "date" in column_name.lower() or "time" in column_name.lower():
        return f"Timestamp or date value recording when this event occurred."
    if "amount" in column_name.lower() or "price" in column_name.lower():
        return f"Monetary amount or financial value in decimal format."
    return f"Stores {column_name.replace('_', ' ')} information for {table_name} records."
