import pickle
from typing import Any, Dict, Optional, Iterable, List, Tuple

from . import CacheBackend


class RedisSentinelCache(CacheBackend):
    """Redis Sentinel implementation of the cache backend with automatic failover support."""

    def __init__(
        self,
        sentinels: List[Tuple[str, int]],
        service_name: str,
        db: int = 0,
        password: Optional[str] = None,
        sentinel_password: Optional[str] = None,
        prefix: str = "cache:",
        socket_timeout: float = 0.1,
        socket_connect_timeout: float = 0.1,
        socket_keepalive: bool = True,
        socket_keepalive_options: Optional[Dict[str, Any]] = None,
        decode_responses: bool = False,
    ):
        """
        Initialize a Redis Sentinel cache connection with automatic failover.

        Args:
            sentinels: List of sentinel addresses as (host, port) tuples
            service_name: Name of the Redis service as configured in Sentinel
            db: Redis database number
            password: Redis password for the master/slave instances
            sentinel_password: Password for Sentinel instances (if required)
            prefix: Key prefix to use for all cache entries
            socket_timeout: Socket timeout for Redis connections
            socket_connect_timeout: Socket connection timeout
            socket_keepalive: Enable TCP keepalive
            socket_keepalive_options: TCP keepalive options
            decode_responses: Whether to decode responses (kept False for pickle)
        """
        try:
            from redis.sentinel import Sentinel  # type: ignore
        except ImportError:
            raise ImportError(
                "Redis package is required. Install with: pip install redis"
            )

        # Configure Sentinel connection
        sentinel_kwargs = {}
        if sentinel_password:
            sentinel_kwargs["password"] = sentinel_password

        self.sentinel = Sentinel(
            sentinels,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            socket_keepalive=socket_keepalive,
            socket_keepalive_options=socket_keepalive_options or {},
            **sentinel_kwargs,
        )

        # Store connection parameters for master/slave connections
        self.service_name = service_name
        self.db = db
        self.password = password
        self.decode_responses = decode_responses
        self.prefix = prefix
        self.tag_prefix = f"{prefix}tag:"
        self.key_tags_prefix = f"{prefix}key_tags:"

        # Test the connection by discovering master
        self._get_master()

    def _get_master(self) -> Any:
        """Get the current master connection from Sentinel."""
        return self.sentinel.master_for(
            self.service_name,
            socket_timeout=0.1,
            db=self.db,
            password=self.password,
            decode_responses=self.decode_responses,
        )

    def _get_slave(self) -> Any:
        """Get a slave connection for read operations."""
        return self.sentinel.slave_for(
            self.service_name,
            socket_timeout=0.1,
            db=self.db,
            password=self.password,
            decode_responses=self.decode_responses,
        )

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
        # Use slave for read operations
        redis = self._get_slave()
        value = redis.get(self._get_key(cache_key))
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

        # Use slave for read operations
        redis = self._get_slave()

        # Get all keys for this tag
        tagged_keys = redis.smembers(tag_key)
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
        # Use slave for read operations
        redis = self._get_slave()

        # Only get data keys, not tag registry keys
        keys = redis.keys(f"{self.prefix}*")
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
            value = redis.get(key)
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
        # Use master for write operations
        redis = self._get_master()

        # First, remove any existing tags for this key
        self._remove_key_from_tags(cache_key)

        # Store the value
        serialized = pickle.dumps(value)
        if ttl is not None:
            redis.setex(self._get_key(cache_key), ttl, serialized)
        else:
            redis.set(self._get_key(cache_key), serialized)

        # Register tags
        if tags:
            tag_set = set(tags)

            # Store tags for this key
            key_tags_key = self._get_key_tags_key(cache_key)
            if tag_set:
                redis.sadd(key_tags_key, *tag_set)
                if ttl is not None:
                    redis.expire(key_tags_key, ttl)

            # Add key to each tag's set
            for tag in tag_set:
                tag_key = self._get_tag_key(tag)
                redis.sadd(tag_key, cache_key)
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

        # Use master for write operations
        redis = self._get_master()

        # Remove from tag registry
        self._remove_key_from_tags(cache_key)

        # Remove the value
        redis.delete(self._get_key(cache_key))
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

        # Use slave for read, master will be used in delete()
        redis = self._get_slave()

        # Get all keys with this tag
        keys = redis.smembers(tag_key)
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
        # Use slave for read operations
        redis = self._get_slave()
        return bool(redis.exists(self._get_key(cache_key)))

    def _remove_key_from_tags(self, cache_key: str) -> None:
        """
        Remove a key from all tags it's associated with.

        Args:
            cache_key: The key to remove from tags
        """
        key_tags_key = self._get_key_tags_key(cache_key)

        # Use master for write operations
        redis = self._get_master()

        # Get all tags for this key
        tags = redis.smembers(key_tags_key)

        # Remove key from each tag's set
        for tag_bytes in tags:
            tag = (
                tag_bytes.decode("utf-8") if isinstance(tag_bytes, bytes) else tag_bytes
            )
            tag_key = self._get_tag_key(tag)
            redis.srem(tag_key, cache_key)

            # Remove tag key if empty
            if redis.scard(tag_key) == 0:
                redis.delete(tag_key)

        # Remove key's tag set
        redis.delete(key_tags_key)
