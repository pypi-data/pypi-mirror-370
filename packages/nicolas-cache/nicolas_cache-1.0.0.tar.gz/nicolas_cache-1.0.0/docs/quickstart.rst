==========
Quickstart
==========

This guide will help you get started with Nicolas Cache in just a few minutes.

Basic Usage
-----------

Import and Create a Cache
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from nicolas.cache import Cache
    
    # Create an in-memory cache
    cache = Cache(backend="memory")

Store and Retrieve Data
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Store a simple value
    cache.set("user:1", "John Doe")
    
    # Retrieve the value
    name = cache.get("user:1")
    print(name)  # Output: John Doe
    
    # Store complex data
    user_data = {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "preferences": {"theme": "dark", "notifications": True}
    }
    cache.set("user:profile:1", user_data)
    
    # Retrieve complex data
    profile = cache.get("user:profile:1")
    print(profile["email"])  # Output: john@example.com

Check and Delete
~~~~~~~~~~~~~~~~

.. code-block:: python

    # Check if a key exists
    if cache.exists("user:1"):
        print("User exists in cache")
    
    # Delete a specific key
    cache.delete("user:1")
    
    # Delete returns True if the key existed
    deleted = cache.delete("non-existent")
    print(deleted)  # Output: False

Working with Tags
-----------------

Tags allow you to group related cache entries for bulk operations.

Basic Tagging
~~~~~~~~~~~~~

.. code-block:: python

    # Store entries with tags
    cache.set("product:1", {"name": "Laptop", "price": 999}, 
              tags=["products", "electronics"])
    
    cache.set("product:2", {"name": "Phone", "price": 599}, 
              tags=["products", "electronics"])
    
    cache.set("product:3", {"name": "Book", "price": 29}, 
              tags=["products", "books"])

Retrieve by Tag
~~~~~~~~~~~~~~~

.. code-block:: python

    # Get all products
    all_products = cache.get_by_tag("products")
    print(len(all_products))  # Output: 3
    
    # Get only electronics
    electronics = cache.get_by_tag("electronics")
    for key, value in electronics.items():
        print(f"{key}: {value['name']} - ${value['price']}")

Delete by Tag
~~~~~~~~~~~~~

.. code-block:: python

    # Delete all electronics from cache
    deleted_count = cache.delete_by_tag("electronics")
    print(f"Deleted {deleted_count} items")
    
    # Now only the book remains
    remaining = cache.get_by_tag("products")
    print(len(remaining))  # Output: 1

Using Redis Backend
-------------------

For persistence and scalability, use the Redis backend:

.. code-block:: python

    # Connect to Redis
    cache = Cache(
        backend="redis",
        host="localhost",
        port=6379,
        db=0
    )
    
    # Use exactly the same API
    cache.set("key", "value", tags=["example"])
    value = cache.get("key")

With TTL (Time-To-Live)
~~~~~~~~~~~~~~~~~~~~~~~~

Redis backend supports automatic expiration:

.. code-block:: python

    # Set a key with 60-second TTL
    cache.set("session:123", {"user_id": 1}, ttl=60)
    
    # Key will automatically expire after 60 seconds
    import time
    time.sleep(61)
    session = cache.get("session:123")
    print(session)  # Output: None

Using Redis Sentinel
--------------------

For high availability with automatic failover:

.. code-block:: python

    cache = Cache(
        backend="redis-sentinel",
        sentinels=[
            ("sentinel1.example.com", 26379),
            ("sentinel2.example.com", 26379),
            ("sentinel3.example.com", 26379)
        ],
        service_name="mymaster",
        password="redis_password"
    )
    
    # Use the same API - failover is automatic
    cache.set("key", "value")
    value = cache.get("key")

Real-World Example
------------------

Here's a practical example of caching database query results:

.. code-block:: python

    from nicolas.cache import Cache
    import json
    
    cache = Cache(backend="redis")
    
    def get_user_data(user_id):
        """Get user data with caching."""
        cache_key = f"user:{user_id}"
        
        # Try to get from cache first
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            print(f"Cache hit for user {user_id}")
            return cached_data
        
        # Simulate database query
        print(f"Cache miss for user {user_id} - querying database")
        user_data = query_database(user_id)  # Your database function
        
        # Store in cache with tags and TTL
        cache.set(
            cache_key, 
            user_data,
            tags=["users", f"org:{user_data['org_id']}"],
            ttl=300  # Cache for 5 minutes
        )
        
        return user_data
    
    def invalidate_org_cache(org_id):
        """Invalidate all cached data for an organization."""
        deleted = cache.delete_by_tag(f"org:{org_id}")
        print(f"Invalidated {deleted} cache entries for org {org_id}")

Best Practices
--------------

1. **Use meaningful key names**: Use colons to create namespaces (e.g., ``user:123:profile``)

2. **Tag strategically**: Use tags for logical grouping that you might need to invalidate together

3. **Set appropriate TTLs**: Use TTL for data that should expire automatically

4. **Handle cache misses gracefully**: Always check if ``get()`` returns ``None``

5. **Use the right backend**:
   
   - **Memory**: Development, testing, small datasets
   - **Redis**: Production, persistent cache, TTL support
   - **Redis Sentinel**: High availability requirements

Next Steps
----------

- Explore :doc:`usage` for detailed examples
- Learn about different :doc:`backends`
- Understand :doc:`tagging` strategies
- Check the :doc:`api` reference