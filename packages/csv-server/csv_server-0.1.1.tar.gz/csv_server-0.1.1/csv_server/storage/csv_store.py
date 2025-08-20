# Implement a CSVStorage class with CRUD.
# - Use ensure_pk_and_autoincrement for POST.
# - Use read_rows for GET/list.
# - PUT/PATCH overwrite and persist with atomic writes.
# - DELETE removes row and saves.

from pathlib import Path
from typing import Any, Dict, List, Optional
from csv_server.utils_csv_ids import read_rows, ensure_pk_and_autoincrement, write_rows_atomic
from .base import BaseStorage
import csv

class CSVStorage(BaseStorage):
    def __init__(self, path: Path, pk: str = "id"):
        self.path = path
        self.pk = pk
        self._schema_cache = None  # Cache for schema
        
    def _infer_column_types(self) -> Dict[str, str]:
        """Infer data types for each column by sampling the data."""
        if not self.path.exists():
            return {}
        
        with open(self.path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        if not rows:
            return {}
        
        schema = {}
        for column in rows[0].keys():
            # Sample values from this column (skip empty values)
            values = [row[column] for row in rows[:10] if row[column].strip()]
            
            if not values:
                schema[column] = "string"
                continue
                
            # Try to infer type
            all_int = True
            all_float = True
            
            for value in values:
                try:
                    int(value)
                except ValueError:
                    all_int = False
                
                try:
                    float(value)
                except ValueError:
                    all_float = False
            
            if all_int:
                schema[column] = "integer"
            elif all_float:
                schema[column] = "float"
            else:
                schema[column] = "string"
        
        return schema
    
    def get_schema(self) -> Dict[str, str]:
        """Get the schema, computing it once and caching the result."""
        if self._schema_cache is None:
            self._schema_cache = self._infer_column_types()
        return self._schema_cache
    
    def invalidate_schema_cache(self):
        """Invalidate the schema cache (call when CSV structure changes)."""
        self._schema_cache = None

    def list(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        rows = read_rows(self.path)
        return rows[offset:offset+limit]

    def get(self, id: str) -> Optional[Dict[str, Any]]:
        rows = read_rows(self.path)
        for row in rows:
            if row.get(self.pk) == id:
                return row
        return None

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = ensure_pk_and_autoincrement(self.path, data, pk=self.pk)
        self.invalidate_schema_cache()  # Invalidate cache on structure change
        return result

    def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        rows = read_rows(self.path)
        updated = False
        for i, row in enumerate(rows):
            if row.get(self.pk) == id:
                rows[i] = {**row, **data, self.pk: id}
                updated = True
                break
        if not updated:
            raise KeyError(f"{self.pk}={id} not found")
        # If the update adds new columns, invalidate cache
        result = rows[i]
        # Only invalidate if new columns were added
        if any(col not in self.get_schema() for col in data.keys()):
            self.invalidate_schema_cache()
        write_rows_atomic(self.path, rows)
        return result

    def delete(self, id: str) -> None:
        rows = read_rows(self.path)
        rows = [row for row in rows if row.get(self.pk) != id]
        write_rows_atomic(self.path, rows)