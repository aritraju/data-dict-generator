"""
tests/test_profiler.py
Unit tests for the DataProfiler.
Uses an in-memory SQLite database with known characteristics.
"""

import pytest
import sqlite3
from src.profiler import DataProfiler
from src.introspector import SchemaIntrospector, ColumnInfo


@pytest.fixture
def profiler_db(tmp_path):
    db_path = str(tmp_path / "profile_test.db")
    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE sales (
            sale_id    TEXT PRIMARY KEY,
            product    TEXT NOT NULL,
            amount     REAL,
            region     TEXT,
            status     TEXT
        );
    """)
    rows = [
        ("S001", "Widget A", 100.0, "West", "Closed"),
        ("S002", "Widget B", 200.0, "East", "Closed"),
        ("S003", "Widget A", 150.0, "West", "Open"),
        ("S004", "Widget C", None, "West", "Open"),    # null amount
        ("S005", "Widget A", 300.0, None, "Closed"),   # null region
    ]
    conn.executemany("INSERT INTO sales VALUES (?,?,?,?,?)", rows)
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def columns():
    return [
        ColumnInfo("sale_id", "TEXT", False, True, None),
        ColumnInfo("product", "TEXT", False, False, None),
        ColumnInfo("amount", "REAL", True, False, None),
        ColumnInfo("region", "TEXT", True, False, None),
        ColumnInfo("status", "TEXT", True, False, None),
    ]


def test_null_pct_amount(profiler_db, columns):
    profiler = DataProfiler(profiler_db)
    profile = profiler.profile_table("sales", columns)
    amount_col = next(c for c in profile.columns if c.column_name == "amount")
    assert amount_col.null_count == 1
    assert amount_col.null_pct == 20.0
    profiler.close()


def test_numeric_stats(profiler_db, columns):
    profiler = DataProfiler(profiler_db)
    profile = profiler.profile_table("sales", columns)
    amount_col = next(c for c in profile.columns if c.column_name == "amount")
    assert amount_col.min_value == 100.0
    assert amount_col.max_value == 300.0
    assert amount_col.avg_value is not None
    profiler.close()


def test_unique_flag_on_pk(profiler_db, columns):
    profiler = DataProfiler(profiler_db)
    profile = profiler.profile_table("sales", columns)
    pk_col = next(c for c in profile.columns if c.column_name == "sale_id")
    assert pk_col.is_unique
    profiler.close()


def test_low_cardinality_detected(profiler_db, columns):
    profiler = DataProfiler(profiler_db)
    profile = profiler.profile_table("sales", columns)
    status_col = next(c for c in profile.columns if c.column_name == "status")
    # Only 2 distinct values: "Open", "Closed"
    assert status_col.distinct_count == 2
    assert status_col.is_low_cardinality
    profiler.close()


def test_quality_warnings_generated(profiler_db, columns):
    profiler = DataProfiler(profiler_db)
    profile = profiler.profile_table("sales", columns)
    assert isinstance(profile.quality_warnings, list)
    profiler.close()


def test_row_count(profiler_db, columns):
    profiler = DataProfiler(profiler_db)
    profile = profiler.profile_table("sales", columns)
    assert profile.row_count == 5
    profiler.close()
