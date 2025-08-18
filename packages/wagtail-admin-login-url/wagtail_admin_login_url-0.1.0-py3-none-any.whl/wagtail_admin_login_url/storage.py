from typing import Any

from django.core.cache import cache


class CachedStorage:
    def __init__(self, prefix: str):
        self.prefix = prefix

    def _key(self, key: str) -> str:
        return f"{self.prefix}:{key}"

    def get(self, key: str, default: Any = None) -> Any:
        return cache.get(self._key(key), default)

    def set(self, key: str, value: Any, timeout: int | None = None) -> None:
        cache.set(self._key(key), value, timeout)

    def delete(self, key: str) -> None:
        cache.delete(self._key(key))
    
    def exists(self, key: str) -> bool:
        return bool(self.get(self._key(key)))

    def all(self, include_prefix: bool = False) -> dict[str, Any]:
        # For production, consider using Redis scan or external tracking if needed
        raise NotImplementedError("Cache storage listing is not supported by default.")
