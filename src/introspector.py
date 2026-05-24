"""
src/introspector.py
Extracts schema information from SQLite (and DuckDB) databases.
Returns table definitions, column metadata, foreign keys, and DDL.
"""

import sqlite3
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ColumnInfo:
    name: str
    data_type: str
    nullable: bool
    is_primary_key: bool
    default_value: Optional[str]
    foreign_key: Optional[Dict[str, str]] = None  # {"table": ..., "column": ...}


@dataclass
class TableInfo:
    name: str
    columns: List[ColumnInfo]
    row_count: int = 0
    ddl: str = ""
    foreign_keys: List[Dict[str, str]] = field(default_factory=list)
    referenced_by: List[str] = field(default_factory=list)


class SchemaIntrospector:
    """
    Connects to a SQLite database and extracts complete schema metadata.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        logger.info(f"Connected to database: {db_path}")

    def get_table_names(self) -> List[str]:
        """Return all user tables (excludes sqlite_ system tables)."""
        rows = self._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        return [r["name"] for r in rows]

    def get_table_ddl(self, table_name: str) -> str:
        """Return the original CREATE TABLE statement."""
        row = self._conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        ).fetchone()
        return row["sql"] if row else ""

    def get_row_count(self, table_name: str) -> int:
        row = self._conn.execute(f"SELECT COUNT(*) as cnt FROM [{table_name}]").fetchone()
        return row["cnt"] if row else 0

    def get_foreign_keys(self, table_name: str) -> List[Dict[str, str]]:
        """Return foreign key relationships for a table."""
        rows = self._conn.execute(f"PRAGMA foreign_key_list([{table_name}])").fetchall()
        fks = []
        for row in rows:
            fks.append({
                "from_column": row["from"],
                "to_table": row["table"],
                "to_column": row["to"]
            })
        return fks

    def get_columns(self, table_name: str) -> List[ColumnInfo]:
        """Return column metadata for a table."""
        pragma_rows = self._conn.execute(f"PRAGMA table_info([{table_name}])").fetchall()
        fks = self.get_foreign_keys(table_name)
        fk_map = {fk["from_column"]: fk for fk in fks}

        columns = []
        for row in pragma_rows:
            col = ColumnInfo(
                name=row["name"],
                data_type=row["type"] or "TEXT",
                nullable=(row["notnull"] == 0),
                is_primary_key=(row["pk"] > 0),
                default_value=row["dflt_value"],
                foreign_key=fk_map.get(row["name"])
            )
            columns.append(col)
        return columns

    def get_all_tables(self) -> List[TableInfo]:
        """Extract full TableInfo for all tables in the database."""
        table_names = self.get_table_names()
        tables = []

        # Build reverse FK map (which tables reference each table)
        all_fks = {}
        for tname in table_names:
            for fk in self.get_foreign_keys(tname):
                all_fks.setdefault(fk["to_table"], []).append(tname)

        for tname in table_names:
            columns = self.get_columns(tname)
            table = TableInfo(
                name=tname,
                columns=columns,
                row_count=self.get_row_count(tname),
                ddl=self.get_table_ddl(tname),
                foreign_keys=self.get_foreign_keys(tname),
                referenced_by=all_fks.get(tname, [])
            )
            tables.append(table)
            logger.info(f"Introspected table '{tname}': {len(columns)} columns, {table.row_count} rows")

        return tables

    def get_sample_values(self, table_name: str, column_name: str, limit: int = 5) -> List[Any]:
        """Return top N most frequent non-null values for a column."""
        rows = self._conn.execute(
            f"""SELECT [{column_name}], COUNT(*) as cnt
                FROM [{table_name}]
                WHERE [{column_name}] IS NOT NULL
                GROUP BY [{column_name}]
                ORDER BY cnt DESC
                LIMIT ?""",
            (limit,)
        ).fetchall()
        return [r[0] for r in rows]

    def close(self):
        self._conn.close()
