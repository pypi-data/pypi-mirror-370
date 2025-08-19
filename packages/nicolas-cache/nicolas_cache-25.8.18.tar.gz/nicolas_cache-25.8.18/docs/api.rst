=============
API Reference
=============

This is the complete API reference for Nicolas Cache.

Cache Class
-----------

.. class:: nicolas.cache.Cache(backend="memory", **kwargs)

   The main cache interface that provides a unified API for all backends.

   :param backend: The backend to use ("memory", "redis", or "redis-sentinel")
   :type backend: str
   :param kwargs: Backend-specific configuration parameters
   :type kwargs: dict

   **Example:**

   .. code-block:: python

      from nicolas.cache import Cache
      
      # Memory backend
      cache = Cache(backend="memory")
      
      # Redis backend
      cache = Cache(backend="redis", host="localhost", port=6379)
      
      # Redis Sentinel backend
      cache = Cache(
          backend="redis-sentinel",
          sentinels=[("localhost", 26379)],
          service_name="mymaster"
      )

Methods
~~~~~~~

.. method:: Cache.get(cache_key)

   Retrieve a value from the cache by key.

   :param cache_key: The key to retrieve
   :type cache_key: str
   :return: The cached value, or None if not found
   :rtype: Any

   **Example:**

   .. code-block:: python

      value = cache.get("user:123")
      if value is None:
          # Key not found in cache
          pass

.. method:: Cache.set(cache_key, value, tags=None, **kwargs)

   Store a value in the cache with the given key and optional tags.

   :param cache_key: The key to store the value under
   :type cache_key: str
   :param value: The value to store (must be pickleable)
   :type value: Any
   :param tags: Optional tags to associate with the entry
   :type tags: Optional[Iterable[str]]
   :param ttl: Time-to-live in seconds (Redis backends only)
   :type ttl: Optional[int]

   **Example:**

   .. code-block:: python

      # Simple set
      cache.set("key", "value")
      
      # With tags
      cache.set("user:123", user_data, tags=["users", "active"])
      
      # With TTL (Redis only)
      cache.set("session", session_data, ttl=3600)

.. method:: Cache.delete(cache_key)

   Remove an entry from the cache by its key.

   :param cache_key: The key to delete
   :type cache_key: str
   :return: True if the key existed and was deleted, False otherwise
   :rtype: bool

   **Example:**

   .. code-block:: python

      deleted = cache.delete("old_key")
      if deleted:
          print("Key was deleted")

.. method:: Cache.exists(cache_key)

   Check if a key exists in the cache.

   :param cache_key: The key to check
   :type cache_key: str
   :return: True if the key exists, False otherwise
   :rtype: bool

   **Example:**

   .. code-block:: python

      if cache.exists("user:123"):
          user = cache.get("user:123")

.. method:: Cache.get_by_tag(tag)

   Retrieve all entries in the cache with a specific tag.

   :param tag: The tag to filter by
   :type tag: str
   :return: Dictionary of key-value pairs
   :rtype: Dict[str, Any]

   **Example:**

   .. code-block:: python

      active_users = cache.get_by_tag("active")
      for key, user in active_users.items():
          print(f"{key}: {user['name']}")

.. method:: Cache.delete_by_tag(tag)

   Remove all entries from the cache with a specific tag.

   :param tag: The tag to filter by
   :type tag: str
   :return: The number of entries deleted
   :rtype: int

   **Example:**

   .. code-block:: python

      count = cache.delete_by_tag("temporary")
      print(f"Deleted {count} entries")

.. method:: Cache.getall()

   Retrieve all entries in the cache.

   :return: Dictionary of all key-value pairs
   :rtype: Dict[str, Any]

   **Example:**

   .. code-block:: python

      all_data = cache.getall()
      print(f"Cache contains {len(all_data)} entries")

Backend Classes
---------------

CacheBackend (Abstract Base Class)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: nicolas.CacheBackend

   Abstract base class for cache backends. All backends must implement these methods.

   **Methods to implement:**

   - ``get(cache_key: str) -> Any``
   - ``get_by_tag(tag: str) -> Dict[str, Any]``
   - ``getall() -> Dict[str, Any]``
   - ``set(cache_key: str, value: Any, tags: Optional[Iterable[str]] = None) -> None``
   - ``delete(cache_key: str) -> bool``
   - ``delete_by_tag(tag: str) -> int``
   - ``exists(cache_key: str) -> bool``

MemoryCache
~~~~~~~~~~~

.. class:: nicolas.memory.MemoryCache()

   In-memory cache backend using Python dictionaries.

   **Characteristics:**

   - No persistence
   - Fastest performance
   - No TTL support
   - Not shared between processes

   **Example:**

   .. code-block:: python

      from nicolas.memory import MemoryCache
      
      cache = MemoryCache()
      cache.set("key", "value", tags=["test"])

RedisCache
~~~~~~~~~~

.. class:: nicolas.redis.RedisCache(host="localhost", port=6379, db=0, password=None, prefix="cache:")

   Redis-based cache backend with persistence and TTL support.

   :param host: Redis server hostname
   :type host: str
   :param port: Redis server port
   :type port: int
   :param db: Redis database number (0-15)
   :type db: int
   :param password: Redis authentication password
   :type password: Optional[str]
   :param prefix: Key prefix for namespacing
   :type prefix: str

   **Example:**

   .. code-block:: python

      from nicolas.redis import RedisCache
      
      cache = RedisCache(
          host="redis.example.com",
          port=6379,
          password="secret",
          prefix="myapp:"
      )

   **TTL Support:**

   .. code-block:: python

      # Set with expiration
      cache.set("session", data, ttl=3600)  # Expires in 1 hour

RedisSentinelCache
~~~~~~~~~~~~~~~~~~

.. class:: nicolas.sentinel.RedisSentinelCache(sentinels, service_name, **kwargs)

   Redis Sentinel cache backend with automatic failover.

   :param sentinels: List of sentinel addresses as (host, port) tuples
   :type sentinels: List[Tuple[str, int]]
   :param service_name: Name of the Redis service in Sentinel
   :type service_name: str
   :param db: Redis database number
   :type db: int
   :param password: Redis authentication password
   :type password: Optional[str]
   :param sentinel_password: Sentinel authentication password
   :type sentinel_password: Optional[str]
   :param prefix: Key prefix for namespacing
   :type prefix: str
   :param socket_timeout: Socket timeout in seconds
   :type socket_timeout: float
   :param socket_connect_timeout: Connection timeout in seconds
   :type socket_connect_timeout: float
   :param socket_keepalive: Enable TCP keepalive
   :type socket_keepalive: bool
   :param socket_keepalive_options: TCP keepalive options
   :type socket_keepalive_options: Optional[Dict[str, Any]]

   **Example:**

   .. code-block:: python

      from nicolas.sentinel import RedisSentinelCache
      
      cache = RedisSentinelCache(
          sentinels=[
              ("sentinel1.example.com", 26379),
              ("sentinel2.example.com", 26379),
              ("sentinel3.example.com", 26379)
          ],
          service_name="mymaster",
          password="redis_password",
          sentinel_password="sentinel_password",
          socket_timeout=0.1,
          socket_keepalive=True
      )

Exceptions
----------

Nicolas Cache uses standard Python exceptions:

.. exception:: ImportError

   Raised when Redis package is not installed but Redis backend is requested.

   **Example:**

   .. code-block:: python

      try:
          cache = Cache(backend="redis")
      except ImportError as e:
          print("Redis package required: pip install redis")

.. exception:: ValueError

   Raised when an unsupported backend is specified.

   **Example:**

   .. code-block:: python

      try:
          cache = Cache(backend="unknown")
      except ValueError as e:
          print("Unsupported backend")

.. exception:: redis.ConnectionError

   Raised when Redis server is not available (Redis backends only).

   **Example:**

   .. code-block:: python

      try:
          cache = Cache(backend="redis", host="invalid")
          cache.set("key", "value")
      except redis.ConnectionError as e:
          print("Redis server not available")

Type Hints
----------

Nicolas Cache uses type hints throughout. Here are the main types:

.. code-block:: python

   from typing import Any, Dict, Optional, Iterable, List, Tuple
   
   # Cache key type
   CacheKey = str
   
   # Tag type
   Tag = str
   
   # Cache value (any pickleable object)
   CacheValue = Any
   
   # TTL in seconds
   TTL = Optional[int]
   
   # Tags collection
   Tags = Optional[Iterable[Tag]]
   
   # Sentinel addresses
   SentinelAddresses = List[Tuple[str, int]]

Version Information
-------------------

.. data:: nicolas.__version__

   The current version of Nicolas Cache.

   **Example:**

   .. code-block:: python

      import nicolas
      print(f"Nicolas Cache version: {nicolas.__version__}")
      # Output: Nicolas Cache version: 25.07.16

Constants
---------

Default values used by the cache backends:

.. data:: DEFAULT_REDIS_HOST = "localhost"
.. data:: DEFAULT_REDIS_PORT = 6379
.. data:: DEFAULT_REDIS_DB = 0
.. data:: DEFAULT_PREFIX = "cache:"
.. data:: DEFAULT_SOCKET_TIMEOUT = 0.1

Advanced Usage
--------------

Custom Backend Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~

To integrate a custom backend with the Cache class:

.. code-block:: python

   from nicolas import CacheBackend
   from nicolas.cache import Cache
   
   class CustomBackend(CacheBackend):
       # Implement all required methods
       pass
   
   # Extend Cache class
   class ExtendedCache(Cache):
       def __init__(self, backend="memory", **kwargs):
           if backend == "custom":
               self._backend = CustomBackend(**kwargs)
           else:
               super().__init__(backend, **kwargs)
   
   # Use custom backend
   cache = ExtendedCache(backend="custom")

Thread Safety
~~~~~~~~~~~~~

- **MemoryCache**: Not thread-safe by default
- **RedisCache**: Thread-safe
- **RedisSentinelCache**: Thread-safe

For thread-safe memory caching:

.. code-block:: python

   import threading
   from nicolas.cache import Cache
   
   class ThreadSafeCache:
       def __init__(self):
           self.cache = Cache(backend="memory")
           self.lock = threading.RLock()
       
       def get(self, key):
           with self.lock:
               return self.cache.get(key)
       
       def set(self, key, value, **kwargs):
           with self.lock:
               return self.cache.set(key, value, **kwargs)