"""
src/profiler.py
Statistical data profiling for each table and column.
Computes null rates, cardinality, numeric stats, and data quality flags.
"""

import sqlite3
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ColumnProfile:
    column_name: str
    data_type: str
    row_count: int
    null_count: int
    null_pct: float
    distinct_count: int
    cardinality_pct: float
    # Numeric stats (None for non-numeric)
    min_value: Optional[Any]
    max_value: Optional[Any]
    avg_value: Optional[float]
    # Quality flags
    is_high_null: bool       # null_pct > 20%
    is_low_cardinality: bool # distinct_count < 5 (potential enum)
    is_unique: bool          # distinct_count == row_count (potential key)
    sample_values: List[Any] = None


@dataclass
class TableProfile:
    table_name: str
    row_count: int
    column_count: int
    columns: List[ColumnProfile]
    quality_warnings: List[str]


class DataProfiler:
    """
    Profiles a SQLite database table-by-table, column-by-column.
    """

    NUMERIC_TYPES = {"INTEGER", "REAL", "NUMERIC", "FLOAT", "DOUBLE", "INT", "BIGINT", "DECIMAL"}

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._conn = sqlite3.connect(db_path)

    def _is_numeric(self, data_type: str) -> bool:
        return any(t in data_type.upper() for t in self.NUMERIC_TYPES)

    def profile_column(
        self,
        table_name: str,
        column_name: str,
        data_type: str,
        row_count: int,
        sample_values: List[Any] = None
    ) -> ColumnProfile:
        """Profile a single column with statistics."""

        # Null count
        null_count = self._conn.execute(
            f"SELECT COUNT(*) FROM [{table_name}] WHERE [{column_name}] IS NULL"
        ).fetchone()[0]

        # Distinct count
        distinct_count = self._conn.execute(
            f"SELECT COUNT(DISTINCT [{column_name}]) FROM [{table_name}]"
        ).fetchone()[0]

        null_pct = round((null_count / row_count * 100), 1) if row_count > 0 else 0.0
        cardinality_pct = round((distinct_count / row_count * 100), 1) if row_count > 0 else 0.0

        # Numeric stats
        min_val = max_val = avg_val = None
        if self._is_numeric(data_type) and null_count < row_count:
            stats = self._conn.execute(
                f"SELECT MIN([{column_name}]), MAX([{column_name}]), AVG([{column_name}]) FROM [{table_name}]"
            ).fetchone()
            min_val, max_val = stats[0], stats[1]
            avg_val = round(stats[2], 2) if stats[2] is not None else None

        profile = ColumnProfile(
            column_name=column_name,
            data_type=data_type,
            row_count=row_count,
            null_count=null_count,
            null_pct=null_pct,
            distinct_count=distinct_count,
            cardinality_pct=cardinality_pct,
            min_value=min_val,
            max_value=max_val,
            avg_value=avg_val,
            is_high_null=null_pct > 20,
            is_low_cardinality=(distinct_count < 10 and row_count > 1),
            is_unique=(distinct_count == row_count and row_count > 0),
            sample_values=sample_values or []
        )
        return profile

    def profile_table(self, table_name: str, column_infos, sample_fn=None) -> TableProfile:
        """Profile all columns in a table."""
        row_count = self._conn.execute(
            f"SELECT COUNT(*) FROM [{table_name}]"
        ).fetchone()[0]

        col_profiles = []
        warnings = []

        for col in column_infos:
            samples = sample_fn(table_name, col.name) if sample_fn else []
            profile = self.profile_column(table_name, col.name, col.data_type, row_count, samples)
            col_profiles.append(profile)

            if profile.is_high_null:
                warnings.append(f"Column '{col.name}' has {profile.null_pct}% null values")
            if profile.is_low_cardinality and not col.is_primary_key:
                warnings.append(f"Column '{col.name}' has only {profile.distinct_count} distinct values — consider an ENUM or CHECK constraint")

        return TableProfile(
            table_name=table_name,
            row_count=row_count,
            column_count=len(col_profiles),
            columns=col_profiles,
            quality_warnings=warnings
        )

    def close(self):
        self._conn.close()
