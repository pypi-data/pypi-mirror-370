# CSV Server

[![PyPI version](https://badge.fury.io/py/csv-server.svg)](https://pypi.org/project/csv-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/rxhxt/csv-server/actions/workflows/ci.yml/badge.svg)](https://github.com/rxhxt/csv-server/actions)

**CSV Server** is a robust Python library and CLI tool that instantly turns your CSV files into a fully-featured REST API. Inspired by [json-server](https://github.com/typicode/json-server), it is designed for rapid prototyping, data exploration, and lightweight data services—no database required.

---

## Features

- 🚀 **Instant REST API**: Serve any folder of CSV files as RESTful endpoints.
- 🔒 **Read-Only by Default**: Safe, non-destructive access; enable writes as needed.
- 🆔 **Auto-ID Management**: Automatic primary key synthesis and incrementing.
- 🔎 **Advanced Querying**: Search, filter, sort, and paginate results.
- 🛡️ **Safe Writes**: Atomic file operations with file locking.
- 📖 **Interactive API Docs**: Swagger/OpenAPI documentation at `/docs`.
- ⚡ **CLI & Python API**: Use as a command-line tool or integrate as a library.
- 🧪 **Comprehensive Testing**: Includes pytest-based test suite.
- 🐍 **Modern Python**: Type hints, linting, and optional pandas support for large datasets.

---

## Installation

```bash
pip install csv-server
```

---

## Quick Start

### CLI Usage

```bash
csv-server serve ./data --port 8000
```

- Instantly exposes all CSV files in `./data` as REST endpoints.
- Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation.

### Python Library Usage

```python
from csv_server import serve_csv_directory

serve_csv_directory("./data", port=8000, readonly=True)
```

---

## Directory Structure

```
csv_server/
  __init__.py
  cli.py
  app.py
  resources.py
  config.py
  storage/
    base.py
    csv_store.py
    sqlite_store.py
  query.py
  utils_csv_ids.py
  version.py
tests/
examples/
  data/users.csv
  data/orders.csv
  config.yaml
pyproject.toml
README.md
LICENSE
```

---

## API Overview

For each CSV file (e.g., `users.csv`), the following endpoints are generated:

| Method | Endpoint            | Description                        |
|--------|---------------------|------------------------------------|
| GET    | `/users`            | List rows with query support       |
| GET    | `/users/{id}`       | Fetch a single row by ID           |
| POST   | `/users`            | Add a new row (if not read-only)   |
| PUT    | `/users/{id}`       | Replace a row (if not read-only)   |
| PATCH  | `/users/{id}`       | Update a row (if not read-only)    |
| DELETE | `/users/{id}`       | Delete a row (if not read-only)    |
| GET    | `/users/schema`     | Get inferred column schema         |

### Query Parameters

- `q`: Full-text search
- `filter`: Field-based filtering (e.g., `filter=age:gt:30`)
- `sort`: Sorting (e.g., `sort=name:asc`)
- `limit` & `offset`: Pagination

---

## Configuration

You can use a YAML config file for advanced setup:

```yaml
resources:
  users:
    file: "users.csv"
    primary_key: "id"
    readonly: false
  orders:
    file: "orders.csv"
    primary_key: "order_id"
    readonly: true
```

Run with:

```bash
csv-server serve ./data --config config.yaml
```

---

## Example Data

Sample CSV files are provided in `examples/data/` for demonstration and testing.

---

## Testing

Run the test suite with:

```bash
pytest
```

---

## Roadmap

- [ ] SQLite backend for large datasets
- [ ] Hot reload for CSV file changes
- [ ] Resource relationships (foreign keys)
- [ ] Docker image for easy deployment

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Inspired by [json-server](https://github.com/typicode/json-server)