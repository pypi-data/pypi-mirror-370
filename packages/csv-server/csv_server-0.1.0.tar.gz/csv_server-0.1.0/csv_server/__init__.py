"""CSV Server - A FastAPI-based REST API server for CSV files.

This package provides a simple way to serve CSV files as REST APIs with
automatic schema inference, data validation, and configurable access control.
"""

from .app import create_app
from .config import load_config, discover_csv_files, save_config
from .storage.csv_store import CSVStorage
from .storage.base import BaseStorage
from .exceptions import *
from .version import __version__

__all__ = [
    # Main API
    "create_app",
    "serve_csv_directory",
    # Configuration
    "load_config",
    "discover_csv_files", 
    "save_config",
    # Storage
    "CSVStorage",
    "BaseStorage",
    # Exceptions
    "CSVServerError",
    "ValidationError",
    "ResourceNotFoundError",
    # Version
    "__version__",
]

def serve_csv_directory(
    data_dir: str,
    host: str = "0.0.0.0",
    port: int = 8000,
    readonly: bool = False,
    config_file: str = None,
    auto_reload: bool = False,
    **uvicorn_kwargs
) -> None:
    """
    Serve a directory of CSV files as a REST API.
    
    This is a convenience function that sets up and runs the server
    with sensible defaults.
    
    Args:
        data_dir: Directory containing CSV files
        host: Host to bind to (default: "0.0.0.0")
        port: Port to bind to (default: 8000)
        readonly: If True, only allow GET requests (default: False)
        config_file: Path to YAML config file (optional)
        auto_reload: Enable auto-reload for development (default: False)
        **uvicorn_kwargs: Additional arguments passed to uvicorn.run()
    
    Example:
        >>> from csv_server import serve_csv_directory
        >>> serve_csv_directory("./data", port=8000, readonly=True)
    """
    import uvicorn
    from pathlib import Path
    
    data_path = Path(data_dir)
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    if config_file:
        config = load_config(config_file)
    else:
        # Auto-discover CSV files
        config = discover_csv_files(data_path, readonly=readonly)
    
    app = create_app(data_path, readonly=readonly, config=config)
    
    # Merge uvicorn kwargs
    uvicorn_config = {
        "host": host,
        "port": port,
        "reload": auto_reload,
        **uvicorn_kwargs
    }
    
    uvicorn.run(app, **uvicorn_config)
