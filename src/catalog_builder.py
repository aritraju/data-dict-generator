"""
src/catalog_builder.py
Orchestrates the full data dictionary generation pipeline:
  introspect → profile → LLM describe → render templates → write output files
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any

from jinja2 import Environment, FileSystemLoader

from .introspector import SchemaIntrospector, TableInfo
from .profiler import DataProfiler, TableProfile
from .llm_describer import describe_table, describe_column

logger = logging.getLogger(__name__)


@dataclass
class ColumnCatalogEntry:
    name: str
    data_type: str
    nullable: bool
    is_primary_key: bool
    default_value: str
    foreign_key: Dict
    description: str
    null_pct: float
    distinct_count: int
    cardinality_pct: float
    min_value: Any
    max_value: Any
    avg_value: Any
    sample_values: List
    is_high_null: bool
    is_low_cardinality: bool
    is_unique: bool


@dataclass
class TableCatalogEntry:
    name: str
    description: str
    purpose: str
    example_query: str
    row_count: int
    column_count: int
    ddl: str
    foreign_keys: List[Dict]
    referenced_by: List[str]
    columns: List[ColumnCatalogEntry]
    quality_warnings: List[str]


@dataclass
class Catalog:
    database_name: str
    generated_at: str
    table_count: int
    total_rows: int
    tables: List[TableCatalogEntry] = field(default_factory=list)


class CatalogBuilder:
    """
    Full pipeline: schema introspection → profiling → LLM descriptions → output.
    """

    def __init__(self, db_path: str, output_dir: str = "./output", use_llm: bool = True):
        self.db_path = db_path
        self.output_dir = output_dir
        self.use_llm = use_llm
        os.makedirs(output_dir, exist_ok=True)

        template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        self._jinja = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )

    def build(self) -> Catalog:
        """Run the full pipeline and return a Catalog object."""
        introspector = SchemaIntrospector(self.db_path)
        profiler = DataProfiler(self.db_path)

        db_name = os.path.splitext(os.path.basename(self.db_path))[0]
        tables_info: List[TableInfo] = introspector.get_all_tables()

        catalog = Catalog(
            database_name=db_name,
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            table_count=len(tables_info),
            total_rows=sum(t.row_count for t in tables_info),
        )

        for table_info in tables_info:
            logger.info(f"Processing table: {table_info.name}")

            # Profile
            table_profile: TableProfile = profiler.profile_table(
                table_info.name,
                table_info.columns,
                sample_fn=introspector.get_sample_values
            )
            col_profile_map = {cp.column_name: cp for cp in table_profile.columns}

            # LLM: table-level description
            if self.use_llm:
                logger.info(f"  Generating LLM description for {table_info.name}...")
                sample_values_map = {
                    col.name: introspector.get_sample_values(table_info.name, col.name)
                    for col in table_info.columns
                }
                table_llm = describe_table(
                    table_name=table_info.name,
                    columns=[c.name for c in table_info.columns],
                    row_count=table_info.row_count,
                    sample_values=sample_values_map,
                    foreign_keys=table_info.foreign_keys,
                    ddl=table_info.ddl
                )
            else:
                table_llm = {
                    "description": f"Stores {table_info.name.replace('_', ' ')} records.",
                    "purpose": f"Operational data for {table_info.name}.",
                    "example_query": f"SELECT * FROM {table_info.name} LIMIT 10;"
                }

            # Build column entries
            col_entries = []
            for col in table_info.columns:
                cp = col_profile_map.get(col.name)

                if self.use_llm:
                    col_desc = describe_column(
                        table_name=table_info.name,
                        column_name=col.name,
                        data_type=col.data_type,
                        nullable=col.nullable,
                        is_pk=col.is_primary_key,
                        sample_values=cp.sample_values if cp else [],
                        null_pct=cp.null_pct if cp else 0.0
                    )
                else:
                    col_desc = f"Stores {col.name.replace('_', ' ')} for {table_info.name}."

                col_entries.append(ColumnCatalogEntry(
                    name=col.name,
                    data_type=col.data_type,
                    nullable=col.nullable,
                    is_primary_key=col.is_primary_key,
                    default_value=col.default_value or "",
                    foreign_key=col.foreign_key,
                    description=col_desc,
                    null_pct=cp.null_pct if cp else 0.0,
                    distinct_count=cp.distinct_count if cp else 0,
                    cardinality_pct=cp.cardinality_pct if cp else 0.0,
                    min_value=cp.min_value if cp else None,
                    max_value=cp.max_value if cp else None,
                    avg_value=cp.avg_value if cp else None,
                    sample_values=cp.sample_values if cp else [],
                    is_high_null=cp.is_high_null if cp else False,
                    is_low_cardinality=cp.is_low_cardinality if cp else False,
                    is_unique=cp.is_unique if cp else False,
                ))

            catalog.tables.append(TableCatalogEntry(
                name=table_info.name,
                description=table_llm.get("description", ""),
                purpose=table_llm.get("purpose", ""),
                example_query=table_llm.get("example_query", ""),
                row_count=table_info.row_count,
                column_count=len(table_info.columns),
                ddl=table_info.ddl,
                foreign_keys=table_info.foreign_keys,
                referenced_by=table_info.referenced_by,
                columns=col_entries,
                quality_warnings=table_profile.quality_warnings
            ))

        introspector.close()
        profiler.close()
        return catalog

    def render_html(self, catalog: Catalog) -> str:
        """Render the HTML catalog using Jinja2 template."""
        template = self._jinja.get_template("catalog.html.j2")
        return template.render(catalog=catalog)

    def render_markdown(self, catalog: Catalog) -> str:
        """Render the Markdown catalog using Jinja2 template."""
        template = self._jinja.get_template("catalog.md.j2")
        return template.render(catalog=catalog)

    def write_outputs(self, catalog: Catalog) -> Dict[str, str]:
        """Write HTML and Markdown files to output directory."""
        html_path = os.path.join(self.output_dir, "catalog.html")
        md_path = os.path.join(self.output_dir, "catalog.md")

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(self.render_html(catalog))

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(self.render_markdown(catalog))

        logger.info(f"Catalog written to: {html_path}")
        logger.info(f"Catalog written to: {md_path}")
        return {"html": html_path, "markdown": md_path}
