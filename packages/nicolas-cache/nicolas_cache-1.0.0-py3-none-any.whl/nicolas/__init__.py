"""Top-level package for Nicolas Cache."""

__author__ = """Yves Thommes"""
__email__ = "hello@wickeddoc.com"

from ._version import __version__ as __version__  # type: ignore

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Iterable


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, cache_key: str) -> Any:
        """Retrieve a value from the cache by key."""
        pass

    @abstractmethod
    def get_by_tag(self, tag: str) -> Dict[str, Any]:
        """Retrieve all entries in the cache with a specific tag."""
        pass

    @abstractmethod
    def getall(self) -> Dict[str, Any]:
        """Retrieve all entries in the cache."""
        pass

    @abstractmethod
    def set(
        self, cache_key: str, value: Any, tags: Optional[Iterable[str]] = None
    ) -> None:
        """Store a value in the cache with the given key and optional tags."""
        pass

    @abstractmethod
    def delete(self, cache_key: str) -> bool:
        """Remove an entry from the cache by its key."""
        pass

    @abstractmethod
    def delete_by_tag(self, tag: str) -> int:
        """Remove all entries from the cache with a specific tag."""
        pass

    @abstractmethod
    def exists(self, cache_key: str) -> bool:
        """Check if a key exists in the cache."""
        pass
