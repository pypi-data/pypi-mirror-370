========
Backends
========

Nicolas Cache supports multiple backend implementations, each with its own characteristics and use cases.

Memory Backend
--------------

The memory backend stores cache data in Python dictionaries within the application's memory space.

**Characteristics:**

- **Speed**: Fastest possible access times
- **Persistence**: No persistence - data is lost on application restart
- **Scalability**: Limited to available RAM
- **Distribution**: Not shared between processes
- **TTL Support**: No automatic expiration

**Configuration:**

.. code-block:: python

    from nicolas.cache import Cache
    
    cache = Cache(backend="memory")

**Use Cases:**

- Development and testing
- Small datasets that fit in memory
- Temporary data that doesn't need persistence
- Single-process applications

**Implementation Details:**

The memory backend uses:

- ``dict`` for storing key-value pairs
- ``dict`` for tag registry
- ``set`` for tracking keys per tag

Redis Backend
-------------

The Redis backend uses Redis server for distributed caching with optional persistence.

**Characteristics:**

- **Speed**: Very fast, with network overhead
- **Persistence**: Optional (RDB snapshots, AOF logs)
- **Scalability**: Can handle large datasets
- **Distribution**: Shared between multiple processes/servers
- **TTL Support**: Native TTL support

**Configuration:**

.. code-block:: python

    from nicolas.cache import Cache
    
    cache = Cache(
        backend="redis",
        host="localhost",      # Redis server hostname
        port=6379,            # Redis server port
        db=0,                 # Database number (0-15)
        password=None,        # Authentication password
        prefix="cache:"       # Key prefix for namespacing
    )

**Advanced Configuration:**

.. code-block:: python

    # With authentication
    cache = Cache(
        backend="redis",
        host="redis.example.com",
        port=6379,
        password="secret_password"
    )
    
    # With custom prefix for multi-tenancy
    cache = Cache(
        backend="redis",
        prefix=f"tenant_{tenant_id}:cache:"
    )

**TTL (Time-To-Live) Support:**

.. code-block:: python

    # Set with expiration
    cache.set("session", data, ttl=3600)  # Expires in 1 hour
    
    # Key will automatically be removed after TTL
    import time
    time.sleep(3601)
    assert cache.get("session") is None

**Use Cases:**

- Production environments
- Distributed applications
- Session storage
- Rate limiting
- Temporary data with expiration

**Redis Data Structure:**

The Redis backend uses:

- **Strings** for cache values (pickled)
- **Sets** for tag registry
- **Sets** for tracking keys per tag

Example Redis structure:

.. code-block:: text

    cache:user:1                    -> pickled user object
    cache:tag:users                 -> {user:1, user:2, ...}
    cache:key_tags:user:1           -> {users, active, ...}

Redis Sentinel Backend
----------------------

Redis Sentinel provides high availability with automatic failover.

**Characteristics:**

- **High Availability**: Automatic failover on master failure
- **Read/Write Splitting**: Reads from slaves, writes to master
- **Monitoring**: Built-in health checking
- **Notification**: Alerts on topology changes
- **All Redis features**: TTL, persistence, etc.

**Configuration:**

.. code-block:: python

    from nicolas.cache import Cache
    
    cache = Cache(
        backend="redis-sentinel",
        sentinels=[                    # List of sentinel nodes
            ("sentinel1.example.com", 26379),
            ("sentinel2.example.com", 26379),
            ("sentinel3.example.com", 26379)
        ],
        service_name="mymaster",       # Redis service name in Sentinel
        db=0,                         # Database number
        password="redis_password",     # Redis auth password
        sentinel_password="sent_pass", # Sentinel auth password
        socket_timeout=0.1,           # Connection timeout
        socket_keepalive=True         # TCP keepalive
    )

**Sentinel Setup Example:**

1. **sentinel.conf** configuration:

.. code-block:: text

    port 26379
    sentinel monitor mymaster 192.168.1.10 6379 2
    sentinel auth-pass mymaster redis_password
    sentinel down-after-milliseconds mymaster 5000
    sentinel parallel-syncs mymaster 1
    sentinel failover-timeout mymaster 10000

2. **Start Sentinel:**

.. code-block:: console

    $ redis-sentinel /path/to/sentinel.conf

**Automatic Failover:**

The Sentinel backend automatically handles failover:

.. code-block:: python

    # Normal operation - writes go to master
    cache.set("key", "value")
    
    # If master fails, Sentinel promotes a slave
    # The cache client automatically reconnects to new master
    cache.set("key", "new_value")  # Works seamlessly

**Use Cases:**

- Mission-critical applications
- Zero-downtime requirements
- Multi-datacenter deployments
- Production environments requiring HA

Backend Comparison
------------------

.. list-table:: Backend Feature Comparison
   :header-rows: 1
   :widths: 20 20 20 20 20

   * - Feature
     - Memory
     - Redis
     - Redis Sentinel
     - Notes
   * - Speed
     - ★★★★★
     - ★★★★☆
     - ★★★★☆
     - Memory is fastest
   * - Persistence
     - ✗
     - ✓
     - ✓
     - Redis can persist to disk
   * - Distributed
     - ✗
     - ✓
     - ✓
     - Shared between processes
   * - TTL Support
     - ✗
     - ✓
     - ✓
     - Automatic expiration
   * - High Availability
     - ✗
     - ✗
     - ✓
     - Automatic failover
   * - Memory Usage
     - High
     - Low
     - Low
     - Memory backend uses app RAM
   * - Setup Complexity
     - None
     - Low
     - Medium
     - Sentinel requires configuration

Choosing a Backend
------------------

**Use Memory Backend when:**

- Developing and testing
- Data fits in memory
- Single process/thread
- Speed is critical
- No persistence needed

**Use Redis Backend when:**

- Need persistence
- Multiple processes/servers
- TTL support required
- Large datasets
- Production environment

**Use Redis Sentinel when:**

- High availability required
- Zero downtime critical
- Automatic failover needed
- Multi-datacenter setup
- Mission-critical data

Custom Backend Implementation
-----------------------------

You can create custom backends by implementing the ``CacheBackend`` interface:

.. code-block:: python

    from nicolas import CacheBackend
    from typing import Any, Dict, Optional, Iterable
    
    class CustomBackend(CacheBackend):
        """Custom cache backend implementation."""
        
        def get(self, cache_key: str) -> Any:
            """Retrieve a value from the cache."""
            pass
        
        def get_by_tag(self, tag: str) -> Dict[str, Any]:
            """Get all entries with a specific tag."""
            pass
        
        def getall(self) -> Dict[str, Any]:
            """Get all cache entries."""
            pass
        
        def set(self, cache_key: str, value: Any, 
                tags: Optional[Iterable[str]] = None) -> None:
            """Store a value in the cache."""
            pass
        
        def delete(self, cache_key: str) -> bool:
            """Delete a cache entry."""
            pass
        
        def delete_by_tag(self, tag: str) -> int:
            """Delete all entries with a tag."""
            pass
        
        def exists(self, cache_key: str) -> bool:
            """Check if a key exists."""
            pass

Then register and use your backend:

.. code-block:: python

    from nicolas.cache import Cache
    
    # Extend Cache class to support custom backend
    class ExtendedCache(Cache):
        def __init__(self, backend: str = "memory", **kwargs):
            if backend == "custom":
                self._backend = CustomBackend(**kwargs)
            else:
                super().__init__(backend, **kwargs)
    
    # Use custom backend
    cache = ExtendedCache(backend="custom")