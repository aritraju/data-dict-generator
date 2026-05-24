#!/usr/bin/env python3
"""
generate.py
CLI to generate a data dictionary catalog from a SQLite database.

Usage:
    python generate.py --db sample_data/healthcare_sample.db
    python generate.py --db mydb.db --output-dir output/ --no-llm
"""

import argparse
import logging
import sys
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="AI Data Dictionary Generator")
    parser.add_argument("--db", required=True, help="Path to SQLite database file")
    parser.add_argument("--output-dir", default="./output", help="Output directory for catalog files")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM descriptions (fast mode)")
    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"❌ Database not found: {args.db}")
        print("   Run: python sample_data/create_sample_db.py")
        sys.exit(1)

    use_llm = not args.no_llm
    if use_llm:
        print("\n🤖 LLM mode: ON (Ollama + llama3.2)")
        print("   Make sure Ollama is running. To skip LLM: use --no-llm\n")
    else:
        print("\n⚡ Fast mode: LLM descriptions disabled\n")

    from src.catalog_builder import CatalogBuilder

    builder = CatalogBuilder(
        db_path=args.db,
        output_dir=args.output_dir,
        use_llm=use_llm
    )

    print(f"📂 Database  : {args.db}")
    print(f"📁 Output dir: {args.output_dir}")
    print("🔍 Introspecting schema and profiling data...\n")

    catalog = builder.build()
    paths = builder.write_outputs(catalog)

    print("\n" + "="*55)
    print("✅ Data Catalog Generated!")
    print("="*55)
    print(f"  Database    : {catalog.database_name}")
    print(f"  Tables      : {catalog.table_count}")
    print(f"  Total rows  : {catalog.total_rows:,}")
    print(f"  Generated   : {catalog.generated_at}")
    print(f"\n  📄 HTML     : {paths['html']}")
    print(f"  📝 Markdown : {paths['markdown']}")
    print(f"\n  Open in browser: open {paths['html']}\n")


if __name__ == "__main__":
    main()
