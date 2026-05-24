"""
app.py
Streamlit UI for the AI Data Dictionary Generator.
Upload a SQLite database and generate a browsable catalog inline.

Run: streamlit run app.py
"""

import streamlit as st
import os
import tempfile
import logging

logging.basicConfig(level=logging.WARNING)

st.set_page_config(
    page_title="AI Data Dictionary Generator",
    page_icon="📖",
    layout="wide"
)

st.title("📖 AI Data Dictionary Generator")
st.caption("Powered by Ollama (llama3.2) · 100% local · No API costs")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("⚙️ Configuration")
    use_llm = st.checkbox("Enable AI descriptions (Ollama)", value=True)
    if use_llm:
        st.info("Ensure Ollama is running with llama3.2 pulled.")

    st.divider()
    st.subheader("📂 Database Source")
    source = st.radio("Select source", ["Upload a SQLite file", "Use sample database"])

    db_path = None

    if source == "Upload a SQLite file":
        uploaded = st.file_uploader("Upload .db or .sqlite file", type=["db", "sqlite", "sqlite3"])
        if uploaded:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
            tmp.write(uploaded.read())
            tmp.close()
            db_path = tmp.name
            st.success(f"Loaded: {uploaded.name}")
    else:
        sample_path = "sample_data/healthcare_sample.db"
        if not os.path.exists(sample_path):
            st.warning("Sample DB not found. Running generator...")
            os.system("python sample_data/create_sample_db.py")
        if os.path.exists(sample_path):
            db_path = sample_path
            st.success("Using healthcare_sample.db")
        else:
            st.error("Could not create sample DB. Run: python sample_data/create_sample_db.py")

    st.divider()
    generate_btn = st.button("🚀 Generate Catalog", type="primary", disabled=db_path is None)

# ── Main ──────────────────────────────────────────────────────────────────────
if not generate_btn:
    st.info("👈 Select a database and click **Generate Catalog** to start.")
    col1, col2, col3 = st.columns(3)
    col1.metric("What you get", "Schema docs")
    col2.metric("", "Data profiles")
    col3.metric("", "AI descriptions")
    st.stop()

# Run generation
from src.catalog_builder import CatalogBuilder

with st.spinner("Introspecting schema and profiling data..."):
    builder = CatalogBuilder(db_path=db_path, output_dir="./output", use_llm=use_llm)
    catalog = builder.build()
    paths = builder.write_outputs(catalog)

# ── KPI Row ───────────────────────────────────────────────────────────────────
st.success(f"✅ Catalog generated for **{catalog.database_name}** at {catalog.generated_at}")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tables", catalog.table_count)
col2.metric("Total Rows", f"{catalog.total_rows:,}")
col3.metric("Total Columns", sum(t.column_count for t in catalog.tables))
warnings_count = sum(1 for t in catalog.tables if t.quality_warnings)
col4.metric("⚠️ Tables with Warnings", warnings_count)

# ── Download buttons ──────────────────────────────────────────────────────────
col_dl1, col_dl2 = st.columns(2)
with open(paths["html"], "rb") as f:
    col_dl1.download_button("⬇️ Download HTML Catalog", f, "catalog.html", "text/html")
with open(paths["markdown"], "rb") as f:
    col_dl2.download_button("⬇️ Download Markdown Catalog", f, "catalog.md", "text/markdown")

st.divider()

# ── Table explorer ────────────────────────────────────────────────────────────
search = st.text_input("🔍 Search tables", placeholder="patients, encounter, claim...")

for table in catalog.tables:
    if search and search.lower() not in table.name.lower() and search.lower() not in table.description.lower():
        continue

    with st.expander(f"**{table.name}** — {table.row_count:,} rows · {table.column_count} cols"):
        st.markdown(f"**Description:** {table.description}")
        st.caption(f"💡 {table.purpose}")

        if table.foreign_keys:
            fk_str = ", ".join(f"`{fk['from_column']}` → `{fk['to_table']}`" for fk in table.foreign_keys)
            st.caption(f"🔗 Foreign keys: {fk_str}")

        if table.quality_warnings:
            st.warning("⚠️ " + " | ".join(table.quality_warnings))

        # Column table as dataframe
        import pandas as pd
        col_data = []
        for c in table.columns:
            col_data.append({
                "Column": ("🔑 " if c.is_primary_key else "🔗 " if c.foreign_key else "") + c.name,
                "Type": c.data_type,
                "Nullable": "Yes" if c.nullable else "No",
                "Null %": f"{c.null_pct}%",
                "Distinct": c.distinct_count,
                "Samples": ", ".join(str(v) for v in c.sample_values[:3]),
                "Description": c.description
            })
        st.dataframe(pd.DataFrame(col_data), use_container_width=True, hide_index=True)

        st.code(table.example_query, language="sql")

        with st.expander("DDL"):
            st.code(table.ddl, language="sql")
