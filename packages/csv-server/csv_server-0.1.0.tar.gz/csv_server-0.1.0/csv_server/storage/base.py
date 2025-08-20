# Base storage interface for CSV Server
from typing import Any, Dict, List, Optional

class BaseStorage:
    def list(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def get(self, id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def delete(self, id: str) -> None:
        raise NotImplementedError