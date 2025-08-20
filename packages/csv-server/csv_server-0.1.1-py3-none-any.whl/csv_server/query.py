# Query engine for CSV Server.
# Supports q (search), filter, sort, limit, offset on lists of dicts.

from typing import List, Dict, Any, Optional
from urllib.parse import parse_qs

def parse_query_params(query_string: str) -> Dict[str, List[str]]:
    return parse_qs(query_string)

def search_rows(rows: List[Dict[str, Any]], q: Optional[str]) -> List[Dict[str, Any]]:
    if not q:
        return rows
    q_lower = q.lower()
    return [
        row for row in rows
        if any(q_lower in str(value).lower() for value in row.values())
    ]

def filter_rows(rows: List[Dict[str, Any]], filters: List[str]) -> List[Dict[str, Any]]:
    # filters: ["col:eq:value", ...]
    for f in filters:
        try:
            col, op, value = f.split(":", 2)
        except ValueError:
            continue
        if op == "eq":
            rows = [row for row in rows if str(row.get(col, "")) == value]
        # Add more operators as needed
    return rows

def sort_rows(rows: List[Dict[str, Any]], sort_col: Optional[str], order: str = "asc") -> List[Dict[str, Any]]:
    if not sort_col:
        return rows
    reverse = order == "desc"
    return sorted(rows, key=lambda r: r.get(sort_col, ""), reverse=reverse)

def paginate_rows(rows: List[Dict[str, Any]], limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    return rows[offset:offset+limit]

def query_engine(
    rows: List[Dict[str, Any]],
    query_params: Dict[str, Any]
) -> Dict[str, Any]:
    filtered_rows = rows

    if 'q' in query_params:
        q = query_params['q'][0]
        filtered_rows = search_rows(filtered_rows, q)
        print("After search:", filtered_rows)

    if 'filter' in query_params:
        filters = {f.split(':')[0]: f.split(':')[1] for f in query_params['filter']}
        filtered_rows = filter_rows(filtered_rows, filters)

    if 'sort' in query_params:
        sort_key = query_params['sort'][0]
        order = query_params.get('order', ['asc'])[0]
        filtered_rows = sort_rows(filtered_rows, sort_key, order)

    limit = int(query_params.get('limit', [50])[0])
    offset = int(query_params.get('offset', [0])[0])
    paginated_rows = paginate_rows(filtered_rows, limit, offset)

    return {
        "items": paginated_rows,
        "total": len(filtered_rows)
    }