"""
tests/test_introspector.py
Unit tests for schema introspection.
Uses an in-memory SQLite database — no external dependencies.
"""

import pytest
import sqlite3
import tempfile
import os
from src.introspector import SchemaIntrospector


@pytest.fixture
def sample_db(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE departments (
            dept_id   TEXT PRIMARY KEY,
            dept_name TEXT NOT NULL,
            location  TEXT
        );

        CREATE TABLE employees (
            emp_id     TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name  TEXT NOT NULL,
            salary     REAL,
            dept_id    TEXT REFERENCES departments(dept_id),
            hire_date  TEXT NOT NULL
        );
    """)
    conn.execute("INSERT INTO departments VALUES ('D1', 'Engineering', 'SF')")
    conn.execute("INSERT INTO departments VALUES ('D2', 'Finance', 'NY')")
    conn.execute("INSERT INTO employees VALUES ('E1', 'Alice', 'Smith', 95000.0, 'D1', '2021-01-10')")
    conn.execute("INSERT INTO employees VALUES ('E2', 'Bob', 'Jones', 82000.0, 'D2', '2022-03-15')")
    conn.execute("INSERT INTO employees VALUES ('E3', 'Carol', 'Brown', NULL, 'D1', '2023-06-01')")
    conn.commit()
    conn.close()
    return db_path


def test_get_table_names(sample_db):
    insp = SchemaIntrospector(sample_db)
    tables = insp.get_table_names()
    assert "departments" in tables
    assert "employees" in tables
    insp.close()


def test_get_row_count(sample_db):
    insp = SchemaIntrospector(sample_db)
    assert insp.get_row_count("departments") == 2
    assert insp.get_row_count("employees") == 3
    insp.close()


def test_get_columns_types(sample_db):
    insp = SchemaIntrospector(sample_db)
    cols = insp.get_columns("employees")
    col_map = {c.name: c for c in cols}
    assert "emp_id" in col_map
    assert col_map["emp_id"].is_primary_key
    assert not col_map["salary"].is_primary_key
    assert col_map["salary"].nullable
    insp.close()


def test_foreign_key_detected(sample_db):
    insp = SchemaIntrospector(sample_db)
    fks = insp.get_foreign_keys("employees")
    assert len(fks) == 1
    assert fks[0]["from_column"] == "dept_id"
    assert fks[0]["to_table"] == "departments"
    insp.close()


def test_get_sample_values(sample_db):
    insp = SchemaIntrospector(sample_db)
    samples = insp.get_sample_values("departments", "dept_name")
    assert len(samples) <= 5
    assert "Engineering" in samples or "Finance" in samples
    insp.close()


def test_ddl_extraction(sample_db):
    insp = SchemaIntrospector(sample_db)
    ddl = insp.get_table_ddl("departments")
    assert "CREATE TABLE" in ddl
    assert "dept_id" in ddl
    insp.close()


def test_get_all_tables(sample_db):
    insp = SchemaIntrospector(sample_db)
    tables = insp.get_all_tables()
    assert len(tables) == 2
    emp_table = next(t for t in tables if t.name == "employees")
    assert emp_table.row_count == 3
    assert len(emp_table.columns) == 6
    insp.close()
