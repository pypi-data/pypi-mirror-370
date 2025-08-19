from typing import Any, Dict, Optional, Iterable

from . import CacheBackend


class MemoryCache(CacheBackend):
    """In-memory implementation of the cache backend with tag support."""

    def __init__(self) -> None:
        """Initialize an empty in-memory cache with tag registry."""
        self._cache: Dict[str, Any] = {}
        self._tag_registry: Dict[str, set[str]] = {}  # tag -> set of cache keys
        self._key_tags: Dict[str, set[str]] = {}  # cache_key -> set of tags

    def get(self, cache_key: str) -> Any:
        """
        Retrieve a value from the cache by key.

        Args:
            cache_key: A unique identifier for the cached item

        Returns:
            The cached value if the key exists, None otherwise
        """
        return self._cache.get(cache_key, None)

    def get_by_tag(self, tag: str) -> Dict[str, Any]:
        """
        Retrieve all entries in the cache with a specific tag.

        Args:
            tag: The tag to filter cache entries by

        Returns:
            A dictionary containing all matching cache key-value pairs
        """
        result = {}
        if tag in self._tag_registry:
            for key in self._tag_registry[tag]:
                if key in self._cache:
                    result[key] = self._cache[key]
        return result

    def getall(self) -> Dict[str, Any]:
        """
        Retrieve all entries in the cache.

        Returns:
            A dictionary containing all cache key-value pairs
        """
        return self._cache.copy()

    def set(
        self, cache_key: str, value: Any, tags: Optional[Iterable[str]] = None
    ) -> None:
        """
        Store a value in the cache with the given key and optional tags.

        Args:
            cache_key: A unique identifier for the cached item
            value: The value to be stored
            tags: Optional list of tags to associate with this cache entry
        """
        # First, remove any existing tags for this key
        if cache_key in self._key_tags:
            self._remove_key_from_tags(cache_key)

        # Store the value
        self._cache[cache_key] = value

        # Register tags
        if tags:
            tag_set = set(tags)
            self._key_tags[cache_key] = tag_set

            for tag in tag_set:
                if tag not in self._tag_registry:
                    self._tag_registry[tag] = set()
                self._tag_registry[tag].add(cache_key)

    def delete(self, cache_key: str) -> bool:
        """
        Remove an entry from the cache by its key.

        Args:
            cache_key: A unique identifier for the cached item

        Returns:
            True if the key was found and deleted, False otherwise
        """
        if cache_key in self._cache:
            # Remove from cache
            del self._cache[cache_key]

            # Remove from tag registry
            self._remove_key_from_tags(cache_key)

            return True
        return False

    def delete_by_tag(self, tag: str) -> int:
        """
        Remove all entries from the cache with a specific tag.

        Args:
            tag: The tag to filter cache entries by

        Returns:
            The number of entries removed
        """
        if tag not in self._tag_registry:
            return 0

        # Get all keys with this tag
        keys_to_delete = list(self._tag_registry[tag])
        count = 0

        # Delete each key
        for key in keys_to_delete:
            if self.delete(key):
                count += 1

        return count

    def exists(self, cache_key: str) -> bool:
        """
        Check if a key exists in the cache.

        Args:
            cache_key: A unique identifier for the cached item

        Returns:
            True if the key exists in the cache, False otherwise
        """
        return cache_key in self._cache

    def _remove_key_from_tags(self, cache_key: str) -> None:
        """
        Remove a key from all tags it's associated with.

        Args:
            cache_key: The key to remove from tags
        """
        if cache_key in self._key_tags:
            for tag in self._key_tags[cache_key]:
                if tag in self._tag_registry and cache_key in self._tag_registry[tag]:
                    self._tag_registry[tag].remove(cache_key)
                    # Clean up empty tag sets
                    if not self._tag_registry[tag]:
                        del self._tag_registry[tag]

            del self._key_tags[cache_key]
