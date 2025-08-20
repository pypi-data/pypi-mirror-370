=====
Usage
=====

This guide covers all aspects of using Nicolas Cache in your projects.

Basic Operations
----------------

Initialization
~~~~~~~~~~~~~~

Create a cache instance with your preferred backend:

.. code-block:: python

    from nicolas.cache import Cache
    
    # In-memory cache
    cache = Cache(backend="memory")
    
    # Redis cache
    cache = Cache(
        backend="redis",
        host="localhost",
        port=6379,
        db=0,
        password=None,
        prefix="myapp:"  # Optional key prefix
    )
    
    # Redis Sentinel cache
    cache = Cache(
        backend="redis-sentinel",
        sentinels=[("localhost", 26379)],
        service_name="mymaster"
    )

Setting Values
~~~~~~~~~~~~~~

Store any Python object that can be pickled:

.. code-block:: python

    # Simple values
    cache.set("name", "Alice")
    cache.set("count", 42)
    cache.set("active", True)
    
    # Complex objects
    cache.set("user", {
        "id": 1,
        "name": "Alice",
        "roles": ["admin", "user"]
    })
    
    # With tags
    cache.set("session:123", session_data, tags=["sessions", "user:1"])
    
    # With TTL (Redis backends only)
    cache.set("token", "abc123", ttl=3600)  # Expires in 1 hour

Getting Values
~~~~~~~~~~~~~~

Retrieve stored values:

.. code-block:: python

    # Get a value
    name = cache.get("name")
    
    # Returns None if key doesn't exist
    missing = cache.get("non-existent")
    assert missing is None
    
    # Get with default value
    value = cache.get("key") or "default"
    
    # Get all values
    all_data = cache.getall()
    for key, value in all_data.items():
        print(f"{key}: {value}")

Checking Existence
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    if cache.exists("user:123"):
        user = cache.get("user:123")
    else:
        user = fetch_from_database(123)
        cache.set("user:123", user)

Deleting Values
~~~~~~~~~~~~~~~

.. code-block:: python

    # Delete a single key
    deleted = cache.delete("old_key")
    print(f"Deleted: {deleted}")  # True if existed, False otherwise
    
    # Delete multiple keys using tags
    count = cache.delete_by_tag("temporary")
    print(f"Deleted {count} entries")

Advanced Tagging
----------------

Tags provide powerful cache management capabilities.

Tag Strategies
~~~~~~~~~~~~~~

.. code-block:: python

    # Hierarchical tags
    cache.set("product:123", product_data, tags=[
        "products",
        "category:electronics",
        "brand:apple",
        "store:main"
    ])
    
    # User-specific tags
    cache.set(f"cart:{user_id}", cart_data, tags=[
        "carts",
        f"user:{user_id}",
        "active_sessions"
    ])
    
    # Time-based tags
    from datetime import date
    today = date.today().isoformat()
    cache.set("report", data, tags=[
        "reports",
        f"date:{today}",
        f"month:{today[:7]}"
    ])

Bulk Operations
~~~~~~~~~~~~~~~

.. code-block:: python

    # Cache multiple related items
    for product in products:
        cache.set(
            f"product:{product['id']}", 
            product,
            tags=["products", f"category:{product['category']}"]
        )
    
    # Get all products in a category
    electronics = cache.get_by_tag("category:electronics")
    
    # Invalidate a category
    cache.delete_by_tag("category:electronics")

Cache Invalidation
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def update_user(user_id, new_data):
        # Update database
        save_to_database(user_id, new_data)
        
        # Invalidate all user-related cache
        cache.delete_by_tag(f"user:{user_id}")
    
    def clear_old_sessions():
        # Clear all session data
        cache.delete_by_tag("sessions")

Pattern Examples
----------------

Caching Database Queries
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def get_user(user_id):
        cache_key = f"user:{user_id}"
        
        # Try cache first
        user = cache.get(cache_key)
        if user is not None:
            return user
        
        # Fetch from database
        user = db.query("SELECT * FROM users WHERE id = ?", user_id)
        
        # Cache with appropriate tags
        if user:
            cache.set(cache_key, user, tags=[
                "users",
                f"org:{user['org_id']}",
                f"role:{user['role']}"
            ])
        
        return user

API Response Caching
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import hashlib
    import json
    
    def cached_api_call(endpoint, params):
        # Create cache key from endpoint and params
        cache_key = hashlib.md5(
            f"{endpoint}:{json.dumps(params, sort_keys=True)}".encode()
        ).hexdigest()
        
        # Check cache
        response = cache.get(cache_key)
        if response is not None:
            return response
        
        # Make API call
        response = requests.get(endpoint, params=params).json()
        
        # Cache with TTL
        cache.set(cache_key, response, 
                  tags=["api_responses", f"endpoint:{endpoint}"],
                  ttl=300)  # 5 minutes
        
        return response

Session Management
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class SessionManager:
        def __init__(self, cache):
            self.cache = cache
        
        def create_session(self, user_id, data):
            session_id = generate_session_id()
            session_key = f"session:{session_id}"
            
            session_data = {
                "user_id": user_id,
                "created_at": time.time(),
                **data
            }
            
            self.cache.set(
                session_key,
                session_data,
                tags=["sessions", f"user:{user_id}"],
                ttl=3600  # 1 hour
            )
            
            return session_id
        
        def get_session(self, session_id):
            return self.cache.get(f"session:{session_id}")
        
        def destroy_session(self, session_id):
            return self.cache.delete(f"session:{session_id}")
        
        def destroy_user_sessions(self, user_id):
            return self.cache.delete_by_tag(f"user:{user_id}")

Performance Optimization
------------------------

Batch Operations
~~~~~~~~~~~~~~~~

.. code-block:: python

    # Instead of multiple individual sets
    for item in items:
        cache.set(f"item:{item['id']}", item)  # Multiple round trips
    
    # Consider grouping related data
    cache.set("items:batch:1", items[:100], tags=["items"])
    cache.set("items:batch:2", items[100:200], tags=["items"])

Cache Warming
~~~~~~~~~~~~~

.. code-block:: python

    def warm_cache():
        """Pre-populate cache with frequently accessed data."""
        # Load popular products
        popular_products = db.query("SELECT * FROM products WHERE popular = 1")
        for product in popular_products:
            cache.set(
                f"product:{product['id']}", 
                product,
                tags=["products", "popular"]
            )
        
        # Load configuration
        config = load_configuration()
        cache.set("config", config, tags=["system"])

Cache Aside Pattern
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class CacheAsideRepository:
        def __init__(self, cache, db):
            self.cache = cache
            self.db = db
        
        def get(self, key):
            # Check cache
            value = self.cache.get(key)
            if value is not None:
                return value
            
            # Load from database
            value = self.db.get(key)
            if value:
                # Update cache
                self.cache.set(key, value)
            
            return value
        
        def update(self, key, value):
            # Update database
            self.db.update(key, value)
            # Invalidate cache
            self.cache.delete(key)
        
        def delete(self, key):
            # Delete from database
            self.db.delete(key)
            # Remove from cache
            self.cache.delete(key)

Error Handling
--------------

.. code-block:: python

    from nicolas.cache import Cache
    import logging
    
    logger = logging.getLogger(__name__)
    
    class ResilientCache:
        """Cache wrapper with fallback behavior."""
        
        def __init__(self, primary_backend="redis", fallback_backend="memory"):
            try:
                self.cache = Cache(backend=primary_backend)
                self.fallback = None
            except Exception as e:
                logger.warning(f"Primary cache failed: {e}, using fallback")
                self.cache = Cache(backend=fallback_backend)
                self.fallback = True
        
        def get(self, key, default=None):
            try:
                value = self.cache.get(key)
                return value if value is not None else default
            except Exception as e:
                logger.error(f"Cache get failed: {e}")
                return default
        
        def set(self, key, value, **kwargs):
            try:
                self.cache.set(key, value, **kwargs)
                return True
            except Exception as e:
                logger.error(f"Cache set failed: {e}")
                return False
