from pathlib import Path
from tempfile import NamedTemporaryFile
import csv, os
from typing import Dict, List, Optional, Iterable
import portalocker

def read_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with open(path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_rows_atomic(path: Path, rows: List[Dict[str, str]], field_order: Optional[Iterable[str]] = None):
    keys = list(field_order) if field_order else (list(rows[0].keys()) if rows else [])
    tmp = NamedTemporaryFile("w", delete=False, newline="", encoding="utf-8")
    with tmp as tf:
        writer = csv.DictWriter(tf, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in keys})
    os.replace(tmp.name, path)

def ensure_pk_and_autoincrement(path: Path, payload: Dict[str, str], pk: str = "id") -> Dict[str, str]:
    rows = read_rows(path)

    # If file is empty, create header from payload + pk
    if not rows:
        new_id = payload.get(pk) or "1"
        order = [pk] + [k for k in payload if k != pk]
        write_rows_atomic(path, [{pk: new_id, **payload}], order)
        return {pk: new_id, **payload}

    header = list(rows[0].keys())
    # If pk column is missing, backfill IDs
    if pk not in header:
        for i, r in enumerate(rows, start=1):
            r[pk] = str(i)
        header = [pk] + header
        write_rows_atomic(path, rows, header)

    # If pk column exists and payload provides pk, use as-is
    if pk in header and payload.get(pk):
        row = {**payload}
        rows.append(row)
        with portalocker.Lock(str(path), "w", timeout=5):
            write_rows_atomic(path, rows, header)
        return row

    # Otherwise, auto-increment pk
    max_id = max((int(r.get(pk, 0) or 0) for r in rows if r.get(pk)), default=0)
    new_id = str(max_id + 1)
    row = {**payload, pk: new_id}
    rows.append(row)
    with portalocker.Lock(str(path), "w", timeout=5):
        write_rows_atomic(path, rows, header)
    return row