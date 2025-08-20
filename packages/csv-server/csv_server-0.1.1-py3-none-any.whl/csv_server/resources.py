# Resource registry for CSV Server.
# This module helps manage resource metadata and discovery.

from pathlib import Path
from typing import Dict, Any, Optional

class Resource:
    def __init__(self, name: str, file_path: str, primary_key: str = "id", readonly: bool = False):
        self.name = name
        self.file_path = Path(file_path)
        self.primary_key = primary_key
        self.readonly = readonly

class ResourceRegistry:
    def __init__(self):
        self.resources: Dict[str, Resource] = {}

    def register(self, name: str, file_path: str, primary_key: str = "id", readonly: bool = False):
        if name in self.resources:
            raise ValueError(f"Resource '{name}' is already registered.")
        self.resources[name] = Resource(name, file_path, primary_key, readonly)

    def get(self, name: str) -> Optional[Resource]:
        return self.resources.get(name)

    def all(self):
        return self.resources.values()

    def as_dict(self) -> Dict[str, Any]:
        return {
            name: {
                "file": resource.file_path.name,
                "primary_key": resource.primary_key,
                "readonly": resource.readonly
            }
            for name, resource in self.resources.items()
        }

# Singleton registry instance
registry = ResourceRegistry()