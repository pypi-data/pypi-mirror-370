import pickle
from typing import Any, Dict, Optional, Iterable

from . import CacheBackend


class RedisCache(CacheBackend):
    """Redis implementation of the cache backend with tag support."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = "cache:",
    ) -> None:
        """
        Initialize a Redis cache connection.

        Args:
            host: Redis server hostname
            port: Redis server port
            db: Redis database number
            password: Redis password (if required)
            prefix: Key prefix to use for all cache entries
        """
        try:
            import redis  # type: ignore
        except ImportError:
            raise ImportError(
                "Redis package is required. Install with: pip install redis"
            )

        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=False,  # We want bytes to handle serialized data
        )
        self.prefix = prefix
        self.tag_prefix = f"{prefix}tag:"
        self.key_tags_prefix = f"{prefix}key_tags:"

    def _get_key(self, cache_key: str) -> str:
        """Add prefix to the cache key."""
        return f"{self.prefix}{cache_key}"

    def _get_tag_key(self, tag: str) -> str:
        """Get the Redis key for a tag set."""
        return f"{self.tag_prefix}{tag}"

    def _get_key_tags_key(self, cache_key: str) -> str:
        """Get the Redis key for storing a key's tags."""
        return f"{self.key_tags_prefix}{cache_key}"

    def get(self, cache_key: str) -> Any:
        """
        Retrieve a value from the cache by key.

        Args:
            cache_key: A unique identifier for the cached item

        Returns:
            The cached value if the key exists, None otherwise
        """
        value = self.redis.get(self._get_key(cache_key))
        if value is None:
            return None
        return pickle.loads(value)

    def get_by_tag(self, tag: str) -> Dict[str, Any]:
        """
        Retrieve all entries in the cache with a specific tag.

        Args:
            tag: The tag to filter cache entries by

        Returns:
            A dictionary containing all matching cache key-value pairs
        """
        result: Dict[str, Any] = {}
        tag_key = self._get_tag_key(tag)

        # Get all keys for this tag
        tagged_keys = self.redis.smembers(tag_key)
        if not tagged_keys:
            return result

        # Get values for each key
        for key_bytes in tagged_keys:
            cache_key = (
                key_bytes.decode("utf-8") if isinstance(key_bytes, bytes) else key_bytes
            )
            value = self.get(cache_key)
            if value is not None:
                result[cache_key] = value

        return result

    def getall(self) -> Dict[str, Any]:
        """
        Retrieve all entries in the cache.

        Returns:
            A dictionary containing all cache key-value pairs
        """
        prefix_len = len(self.prefix)
        # Only get data keys, not tag registry keys
        keys = self.redis.keys(f"{self.prefix}*")
        result: Dict[str, Any] = {}

        for key in keys:
            # Skip tag registry keys
            str_key = key.decode("utf-8") if isinstance(key, bytes) else key
            if str_key.startswith(self.tag_prefix) or str_key.startswith(
                self.key_tags_prefix
            ):
                continue

            # Process data key
            clean_key = str_key[prefix_len:]
            value = self.redis.get(key)
            if value is not None:
                result[clean_key] = pickle.loads(value)

        return result

    def set(
        self,
        cache_key: str,
        value: Any,
        tags: Optional[Iterable[str]] = None,
        ttl: Optional[int] = None,
    ) -> None:
        """
        Store a value in the cache with the given key and optional tags.

        Args:
            cache_key: A unique identifier for the cached item
            value: The value to be stored
            tags: Optional list of tags to associate with this cache entry
            ttl: Time-to-live in seconds (optional)
        """
        # First, remove any existing tags for this key
        self._remove_key_from_tags(cache_key)

        # Store the value
        serialized = pickle.dumps(value)
        if ttl is not None:
            self.redis.setex(self._get_key(cache_key), ttl, serialized)
        else:
            self.redis.set(self._get_key(cache_key), serialized)

        # Register tags
        if tags:
            tag_set = set(tags)

            # Store tags for this key
            key_tags_key = self._get_key_tags_key(cache_key)
            if tag_set:
                self.redis.sadd(key_tags_key, *tag_set)
                if ttl is not None:
                    self.redis.expire(key_tags_key, ttl)

            # Add key to each tag's set
            for tag in tag_set:
                tag_key = self._get_tag_key(tag)
                self.redis.sadd(tag_key, cache_key)
                # No TTL on tag keys - they'll be cleaned up when empty

    def delete(self, cache_key: str) -> bool:
        """
        Remove an entry from the cache by its key.

        Args:
            cache_key: A unique identifier for the cached item

        Returns:
            True if the key was found and deleted, False otherwise
        """
        # Check if key exists
        if not self.exists(cache_key):
            return False

        # Remove from tag registry
        self._remove_key_from_tags(cache_key)

        # Remove the value
        self.redis.delete(self._get_key(cache_key))
        return True

    def delete_by_tag(self, tag: str) -> int:
        """
        Remove all entries from the cache with a specific tag.

        Args:
            tag: The tag to filter cache entries by

        Returns:
            The number of entries removed
        """
        tag_key = self._get_tag_key(tag)

        # Get all keys with this tag
        keys = self.redis.smembers(tag_key)
        if not keys:
            return 0

        # Convert bytes to strings if needed
        keys_to_delete = [
            k.decode("utf-8") if isinstance(k, bytes) else k for k in keys
        ]

        # Delete each key
        count = 0
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
        return bool(self.redis.exists(self._get_key(cache_key)))

    def _remove_key_from_tags(self, cache_key: str) -> None:
        """
        Remove a key from all tags it's associated with.

        Args:
            cache_key: The key to remove from tags
        """
        key_tags_key = self._get_key_tags_key(cache_key)

        # Get all tags for this key
        tags = self.redis.smembers(key_tags_key)

        # Remove key from each tag's set
        for tag_bytes in tags:
            tag = (
                tag_bytes.decode("utf-8") if isinstance(tag_bytes, bytes) else tag_bytes
            )
            tag_key = self._get_tag_key(tag)
            self.redis.srem(tag_key, cache_key)

            # Remove tag key if empty
            if self.redis.scard(tag_key) == 0:
                self.redis.delete(tag_key)

        # Remove key's tag set
        self.redis.delete(key_tags_key)
