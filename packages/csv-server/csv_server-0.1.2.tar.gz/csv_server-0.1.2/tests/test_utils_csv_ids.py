from pathlib import Path
import tempfile
from csv_server.utils_csv_ids import read_rows, ensure_pk_and_autoincrement

def test_read_rows_empty(tmp_path):
    file = tmp_path / "empty.csv"
    assert read_rows(file) == []

def test_ensure_pk_and_autoincrement_creates_id(tmp_path):
    file = tmp_path / "users.csv"
    payload = {"name": "Alice", "email": "alice@example.com"}
    row = ensure_pk_and_autoincrement(file, payload)
    assert row["id"] == "1"
    rows = read_rows(file)
    assert rows[0]["name"] == "Alice"
    assert rows[0]["id"] == "1"

def test_ensure_pk_and_autoincrement_increments_id(tmp_path):
    file = tmp_path / "users.csv"
    ensure_pk_and_autoincrement(file, {"name": "Alice"})
    row = ensure_pk_and_autoincrement(file, {"name": "Bob"})
    assert row["id"] == "2"
    rows = read_rows(file)
    assert len(rows) == 2
    assert rows[1]["name"] == "Bob"
    assert rows[1]["id"] == "2"