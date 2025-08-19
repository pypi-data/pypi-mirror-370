=======
Tagging
=======

The tagging system in Nicolas Cache provides a powerful way to organize and manage cache entries. Tags allow you to group related cache items and perform bulk operations on them.

Understanding Tags
------------------

Tags are labels that you can attach to cache entries. Each cache entry can have multiple tags, and each tag can be associated with multiple entries.

**Key Concepts:**

- **Many-to-Many Relationship**: One entry can have multiple tags, one tag can have multiple entries
- **Automatic Cleanup**: Tags are automatically removed when no entries reference them
- **Bulk Operations**: Delete or retrieve all entries with a specific tag
- **No Hierarchy**: Tags are flat, but you can create logical hierarchies using naming conventions

Basic Tag Operations
--------------------

Adding Tags
~~~~~~~~~~~

.. code-block:: python

    from nicolas.cache import Cache
    
    cache = Cache(backend="memory")
    
    # Single tag
    cache.set("user:1", user_data, tags=["users"])
    
    # Multiple tags
    cache.set("user:1", user_data, tags=["users", "active", "premium"])
    
    # Tags as any iterable
    tag_set = {"users", "employees", "department:IT"}
    cache.set("user:2", user_data, tags=tag_set)

Retrieving by Tag
~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Get all entries with a specific tag
    all_users = cache.get_by_tag("users")
    # Returns: {"user:1": {...}, "user:2": {...}}
    
    # Process tagged entries
    for key, value in cache.get_by_tag("active").items():
        print(f"Active user {key}: {value['name']}")

Deleting by Tag
~~~~~~~~~~~~~~~~

.. code-block:: python

    # Delete all entries with a tag
    deleted_count = cache.delete_by_tag("temporary")
    print(f"Deleted {deleted_count} temporary entries")
    
    # Clear all user sessions
    cache.delete_by_tag("sessions")

Tag Naming Strategies
----------------------

Hierarchical Tags
~~~~~~~~~~~~~~~~~

Use colons to create logical hierarchies:

.. code-block:: python

    # Category hierarchy
    cache.set("product:123", product, tags=[
        "products",
        "category:electronics",
        "category:electronics:phones",
        "brand:apple"
    ])
    
    # Get all electronics
    electronics = cache.get_by_tag("category:electronics")
    
    # Get only phones
    phones = cache.get_by_tag("category:electronics:phones")

Entity-Based Tags
~~~~~~~~~~~~~~~~~

Tag by entity type and ID:

.. code-block:: python

    # User-specific tags
    user_id = 123
    cache.set(f"profile:{user_id}", profile, tags=[
        "profiles",
        f"user:{user_id}",
        f"org:{profile['org_id']}"
    ])
    
    cache.set(f"settings:{user_id}", settings, tags=[
        "settings",
        f"user:{user_id}"
    ])
    
    # Invalidate all data for a user
    cache.delete_by_tag(f"user:{user_id}")

Time-Based Tags
~~~~~~~~~~~~~~~

Use tags for time-based grouping:

.. code-block:: python

    from datetime import datetime, date
    
    now = datetime.now()
    today = date.today()
    
    cache.set("report:daily", report_data, tags=[
        "reports",
        f"date:{today.isoformat()}",
        f"month:{today.strftime('%Y-%m')}",
        f"year:{today.year}",
        f"hour:{now.hour}"
    ])
    
    # Delete all reports from today
    cache.delete_by_tag(f"date:{today.isoformat()}")
    
    # Get all reports from current month
    monthly_reports = cache.get_by_tag(f"month:{today.strftime('%Y-%m')}")

Status Tags
~~~~~~~~~~~

Track entry states:

.. code-block:: python

    # Order processing
    cache.set(f"order:{order_id}", order_data, tags=[
        "orders",
        f"customer:{customer_id}",
        "status:pending"
    ])
    
    # Update status by replacing tags
    order_data['status'] = 'processing'
    cache.set(f"order:{order_id}", order_data, tags=[
        "orders",
        f"customer:{customer_id}",
        "status:processing"  # Changed from pending
    ])
    
    # Get all pending orders
    pending = cache.get_by_tag("status:pending")

Advanced Patterns
-----------------

Cache Invalidation Strategies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class ProductCache:
        def __init__(self, cache):
            self.cache = cache
        
        def set_product(self, product):
            """Cache product with comprehensive tagging."""
            self.cache.set(
                f"product:{product['id']}", 
                product,
                tags=[
                    "products",
                    f"category:{product['category_id']}",
                    f"brand:{product['brand_id']}",
                    f"price_range:{self._get_price_range(product['price'])}",
                    "available" if product['stock'] > 0 else "out_of_stock"
                ]
            )
        
        def invalidate_category(self, category_id):
            """Invalidate all products in a category."""
            return self.cache.delete_by_tag(f"category:{category_id}")
        
        def invalidate_brand(self, brand_id):
            """Invalidate all products from a brand."""
            return self.cache.delete_by_tag(f"brand:{brand_id}")
        
        def _get_price_range(self, price):
            if price < 100:
                return "budget"
            elif price < 500:
                return "mid"
            else:
                return "premium"

Dependency Tracking
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class DependencyCache:
        def __init__(self, cache):
            self.cache = cache
        
        def cache_with_dependencies(self, key, value, depends_on):
            """Cache with dependency tracking."""
            tags = ["cached_values"]
            
            # Add dependency tags
            for dep in depends_on:
                tags.append(f"depends:{dep}")
            
            self.cache.set(key, value, tags=tags)
        
        def invalidate_dependents(self, dependency):
            """Invalidate all entries depending on something."""
            return self.cache.delete_by_tag(f"depends:{dependency}")
    
    # Usage
    dep_cache = DependencyCache(cache)
    
    # Cache computed value that depends on user and config
    dep_cache.cache_with_dependencies(
        "computed:result",
        compute_result(),
        depends_on=["user:123", "config:main"]
    )
    
    # When user changes, invalidate dependent caches
    dep_cache.invalidate_dependents("user:123")

Multi-Tenant Caching
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class TenantCache:
        def __init__(self, cache, tenant_id):
            self.cache = cache
            self.tenant_id = tenant_id
        
        def set(self, key, value, tags=None):
            """Set with tenant isolation."""
            tags = tags or []
            tags.append(f"tenant:{self.tenant_id}")
            
            full_key = f"tenant:{self.tenant_id}:{key}"
            self.cache.set(full_key, value, tags=tags)
        
        def get(self, key):
            """Get with tenant isolation."""
            full_key = f"tenant:{self.tenant_id}:{key}"
            return self.cache.get(full_key)
        
        def clear_tenant_cache(self):
            """Clear all cache for this tenant."""
            return self.cache.delete_by_tag(f"tenant:{self.tenant_id}")
    
    # Usage
    tenant_cache = TenantCache(cache, tenant_id="acme_corp")
    tenant_cache.set("config", config_data)
    tenant_cache.clear_tenant_cache()  # Clear all Acme Corp cache

Tag Performance
---------------

Performance Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Number of Tags**: More tags per entry means more bookkeeping
2. **Tag Cardinality**: Unique tags for every entry defeats the purpose
3. **Tag Names**: Shorter tag names use less memory

.. code-block:: python

    # Good - reasonable number of meaningful tags
    cache.set("user:123", data, tags=["users", "active", "premium"])
    
    # Bad - too many unique tags
    cache.set("user:123", data, tags=[
        f"user:{id}",
        f"timestamp:{time.time()}",  # Unique for every entry!
        f"random:{uuid.uuid4()}"      # Defeats grouping purpose
    ])

Memory Overhead
~~~~~~~~~~~~~~~

Each tag maintains a set of keys in Redis:

.. code-block:: text

    # Redis memory usage example
    cache:tag:users -> {user:1, user:2, ..., user:1000}  # ~8KB for 1000 users
    cache:key_tags:user:1 -> {users, active, premium}    # ~100 bytes per key

Best Practices
--------------

1. **Use Consistent Naming**

.. code-block:: python

    # Good - consistent format
    tags = [
        "type:user",
        "status:active",
        "role:admin"
    ]
    
    # Bad - inconsistent
    tags = [
        "user-type",
        "active_status",
        "AdminRole"
    ]

2. **Plan Your Tag Hierarchy**

.. code-block:: python

    # Well-planned hierarchy
    tags = [
        "content",
        "content:articles",
        "content:articles:published",
        "author:john",
        "category:tech"
    ]

3. **Avoid Over-Tagging**

.. code-block:: python

    # Appropriate tagging
    cache.set("session:123", session, tags=["sessions", f"user:{user_id}"])
    
    # Over-tagging
    cache.set("session:123", session, tags=[
        "sessions", "active_sessions", "user_sessions",
        "temporary", "data", "cache", "storage"  # Too generic
    ])

4. **Document Your Tagging Schema**

.. code-block:: python

    """
    Tagging Schema:
    - users: All user-related data
    - user:{id}: Specific user's data
    - org:{id}: Organization-specific data
    - temp: Temporary data (cleared daily)
    - config: Configuration data
    - api: API response cache
    """

5. **Regular Cleanup**

.. code-block:: python

    # Scheduled cleanup of temporary data
    def daily_cleanup():
        cache.delete_by_tag("temp")
        cache.delete_by_tag(f"date:{yesterday}")

Tag Implementation Details
--------------------------

The tagging system is implemented differently in each backend:

**Memory Backend:**

- Tags stored in Python dictionaries
- O(1) tag addition/removal
- O(n) retrieval by tag

**Redis Backend:**

- Tags stored as Redis sets
- Atomic tag operations
- Efficient set operations for retrieval

**Data Structure:**

.. code-block:: text

    # Conceptual structure
    cache_entries = {
        "user:1": {value: {...}, tags: {"users", "active"}},
        "user:2": {value: {...}, tags: {"users", "inactive"}}
    }
    
    tag_index = {
        "users": {"user:1", "user:2"},
        "active": {"user:1"},
        "inactive": {"user:2"}
    }