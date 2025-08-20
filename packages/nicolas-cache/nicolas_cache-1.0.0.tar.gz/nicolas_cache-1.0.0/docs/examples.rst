========
Examples
========

This section provides practical, real-world examples of using Nicolas Cache in various scenarios.

Web Application Caching
-----------------------

Flask Application
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from flask import Flask, jsonify
    from nicolas.cache import Cache
    import hashlib
    import json
    
    app = Flask(__name__)
    cache = Cache(backend="redis", host="localhost", port=6379)
    
    def cache_key_wrapper(func):
        """Decorator for caching function results."""
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_data = f"{func.__name__}:{args}:{kwargs}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try cache first
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, tags=["api_cache"], ttl=300)
            return result
        return wrapper
    
    @app.route('/user/<int:user_id>')
    @cache_key_wrapper
    def get_user(user_id):
        # Expensive database query
        user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
        return jsonify(user)
    
    @app.route('/clear-cache', methods=['POST'])
    def clear_cache():
        count = cache.delete_by_tag("api_cache")
        return jsonify({"cleared": count})

Django Integration
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # settings.py
    from nicolas.cache import Cache
    
    NICOLAS_CACHE = Cache(
        backend="redis-sentinel",
        sentinels=[
            ("sentinel1.prod", 26379),
            ("sentinel2.prod", 26379),
            ("sentinel3.prod", 26379)
        ],
        service_name="mymaster"
    )
    
    # views.py
    from django.conf import settings
    from django.shortcuts import render
    from django.views.decorators.cache import never_cache
    
    cache = settings.NICOLAS_CACHE
    
    def product_list(request, category_id):
        cache_key = f"products:category:{category_id}"
        
        # Check cache
        products = cache.get(cache_key)
        if products is None:
            # Fetch from database
            products = Product.objects.filter(category_id=category_id)
            products = list(products.values())
            
            # Cache with tags
            cache.set(cache_key, products, tags=[
                "products",
                f"category:{category_id}"
            ], ttl=600)
        
        return render(request, 'products.html', {'products': products})
    
    @never_cache
    def invalidate_category(request, category_id):
        """Admin action to clear category cache."""
        if request.user.is_staff:
            count = cache.delete_by_tag(f"category:{category_id}")
            return JsonResponse({"invalidated": count})

Session Management
------------------

User Sessions with TTL
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import uuid
    import time
    from datetime import datetime
    from nicolas.cache import Cache
    
    class SessionManager:
        def __init__(self):
            self.cache = Cache(backend="redis")
            self.session_ttl = 3600  # 1 hour
        
        def create_session(self, user_id, ip_address, user_agent):
            """Create a new user session."""
            session_id = str(uuid.uuid4())
            session_data = {
                "user_id": user_id,
                "session_id": session_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": time.time()
            }
            
            # Store session with multiple tags for flexible management
            self.cache.set(
                f"session:{session_id}",
                session_data,
                tags=[
                    "sessions",
                    f"user:{user_id}",
                    f"ip:{ip_address}",
                    "active"
                ],
                ttl=self.session_ttl
            )
            
            return session_id
        
        def get_session(self, session_id):
            """Get session and update last activity."""
            session = self.cache.get(f"session:{session_id}")
            if session:
                # Update last activity
                session["last_activity"] = time.time()
                self.cache.set(
                    f"session:{session_id}",
                    session,
                    tags=[
                        "sessions",
                        f"user:{session['user_id']}",
                        f"ip:{session['ip_address']}",
                        "active"
                    ],
                    ttl=self.session_ttl
                )
            return session
        
        def destroy_session(self, session_id):
            """Destroy a specific session."""
            return self.cache.delete(f"session:{session_id}")
        
        def destroy_user_sessions(self, user_id):
            """Destroy all sessions for a user."""
            count = self.cache.delete_by_tag(f"user:{user_id}")
            return count
        
        def get_active_sessions(self, user_id=None):
            """Get all active sessions, optionally for a specific user."""
            if user_id:
                return self.cache.get_by_tag(f"user:{user_id}")
            return self.cache.get_by_tag("sessions")
        
        def destroy_sessions_by_ip(self, ip_address):
            """Destroy all sessions from an IP address."""
            return self.cache.delete_by_tag(f"ip:{ip_address}")

Rate Limiting
-------------

API Rate Limiter
~~~~~~~~~~~~~~~~~

.. code-block:: python

    import time
    from nicolas.cache import Cache
    
    class RateLimiter:
        def __init__(self):
            self.cache = Cache(backend="redis")
        
        def is_allowed(self, identifier, limit=100, window=3600):
            """
            Check if request is allowed under rate limit.
            
            Args:
                identifier: Unique identifier (IP, API key, user ID)
                limit: Maximum requests per window
                window: Time window in seconds
            """
            current_time = int(time.time())
            window_start = current_time - window
            cache_key = f"rate_limit:{identifier}:{window_start // window}"
            
            # Get current count
            current = self.cache.get(cache_key)
            if current is None:
                current = 0
            
            if current >= limit:
                return False, 0  # Not allowed, 0 remaining
            
            # Increment counter
            new_count = current + 1
            self.cache.set(
                cache_key,
                new_count,
                tags=["rate_limits", f"identifier:{identifier}"],
                ttl=window
            )
            
            return True, limit - new_count  # Allowed, X remaining
        
        def reset_limits(self, identifier):
            """Reset rate limits for an identifier."""
            return self.cache.delete_by_tag(f"identifier:{identifier}")
    
    # Usage in API
    rate_limiter = RateLimiter()
    
    @app.before_request
    def check_rate_limit():
        identifier = request.remote_addr  # or API key
        allowed, remaining = rate_limiter.is_allowed(identifier, limit=100, window=3600)
        
        if not allowed:
            return jsonify({"error": "Rate limit exceeded"}), 429
        
        g.rate_limit_remaining = remaining

Data Aggregation
----------------

Real-time Analytics
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from nicolas.cache import Cache
    from datetime import datetime, timedelta
    import json
    
    class AnalyticsCache:
        def __init__(self):
            self.cache = Cache(backend="redis")
        
        def record_event(self, event_type, user_id, metadata=None):
            """Record an analytics event."""
            timestamp = datetime.utcnow()
            event = {
                "type": event_type,
                "user_id": user_id,
                "timestamp": timestamp.isoformat(),
                "metadata": metadata or {}
            }
            
            # Store with time-based tags for aggregation
            cache_key = f"event:{event_type}:{timestamp.timestamp()}"
            self.cache.set(
                cache_key,
                event,
                tags=[
                    "events",
                    f"event_type:{event_type}",
                    f"user:{user_id}",
                    f"date:{timestamp.date().isoformat()}",
                    f"hour:{timestamp.strftime('%Y-%m-%d-%H')}"
                ],
                ttl=86400 * 7  # Keep for 7 days
            )
        
        def get_hourly_events(self, hour_str):
            """Get all events for a specific hour."""
            return self.cache.get_by_tag(f"hour:{hour_str}")
        
        def get_user_events(self, user_id, event_type=None):
            """Get all events for a user."""
            if event_type:
                # Get intersection of user and event type
                user_events = self.cache.get_by_tag(f"user:{user_id}")
                type_events = self.cache.get_by_tag(f"event_type:{event_type}")
                return {k: v for k, v in user_events.items() if k in type_events}
            return self.cache.get_by_tag(f"user:{user_id}")
        
        def get_daily_summary(self, date_str):
            """Get summary of events for a specific date."""
            events = self.cache.get_by_tag(f"date:{date_str}")
            
            summary = {
                "total_events": len(events),
                "unique_users": len(set(e["user_id"] for e in events.values())),
                "events_by_type": {}
            }
            
            for event in events.values():
                event_type = event["type"]
                if event_type not in summary["events_by_type"]:
                    summary["events_by_type"][event_type] = 0
                summary["events_by_type"][event_type] += 1
            
            return summary

Computed Results Cache
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import hashlib
    from nicolas.cache import Cache
    
    class ComputationCache:
        def __init__(self):
            self.cache = Cache(backend="redis")
        
        def get_or_compute(self, func, *args, **kwargs):
            """
            Get cached result or compute and cache.
            
            Args:
                func: Function to compute result
                *args, **kwargs: Arguments for the function
            """
            # Create cache key from function and arguments
            key_data = {
                "func": func.__name__,
                "args": args,
                "kwargs": kwargs
            }
            cache_key = "compute:" + hashlib.md5(
                json.dumps(key_data, sort_keys=True).encode()
            ).hexdigest()
            
            # Check cache
            result = self.cache.get(cache_key)
            if result is not None:
                return result["value"], True  # cached
            
            # Compute result
            start_time = time.time()
            value = func(*args, **kwargs)
            compute_time = time.time() - start_time
            
            # Cache with metadata
            self.cache.set(
                cache_key,
                {
                    "value": value,
                    "computed_at": time.time(),
                    "compute_time": compute_time,
                    "function": func.__name__
                },
                tags=[
                    "computed",
                    f"function:{func.__name__}",
                    f"date:{datetime.now().date().isoformat()}"
                ],
                ttl=3600  # Cache for 1 hour
            )
            
            return value, False  # not cached
    
    # Usage
    comp_cache = ComputationCache()
    
    def expensive_calculation(x, y):
        time.sleep(2)  # Simulate expensive operation
        return x ** y + sum(range(1000000))
    
    # First call - computes (slow)
    result, cached = comp_cache.get_or_compute(expensive_calculation, 10, 5)
    print(f"Result: {result}, Cached: {cached}")
    
    # Second call - cached (fast)
    result, cached = comp_cache.get_or_compute(expensive_calculation, 10, 5)
    print(f"Result: {result}, Cached: {cached}")

Microservices
-------------

Service Discovery Cache
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from nicolas.cache import Cache
    import requests
    
    class ServiceRegistry:
        def __init__(self):
            self.cache = Cache(backend="redis-sentinel",
                              sentinels=[("localhost", 26379)],
                              service_name="mymaster")
        
        def register_service(self, service_name, instance_id, host, port, metadata=None):
            """Register a service instance."""
            service_data = {
                "instance_id": instance_id,
                "host": host,
                "port": port,
                "registered_at": time.time(),
                "healthy": True,
                "metadata": metadata or {}
            }
            
            self.cache.set(
                f"service:{service_name}:{instance_id}",
                service_data,
                tags=[
                    "services",
                    f"service:{service_name}",
                    "healthy" if service_data["healthy"] else "unhealthy"
                ],
                ttl=30  # Auto-expire if not renewed
            )
        
        def get_service_instances(self, service_name, healthy_only=True):
            """Get all instances of a service."""
            instances = self.cache.get_by_tag(f"service:{service_name}")
            
            if healthy_only:
                return {k: v for k, v in instances.items() if v.get("healthy", False)}
            return instances
        
        def heartbeat(self, service_name, instance_id):
            """Renew service registration."""
            key = f"service:{service_name}:{instance_id}"
            service_data = self.cache.get(key)
            
            if service_data:
                service_data["last_heartbeat"] = time.time()
                self.cache.set(
                    key,
                    service_data,
                    tags=[
                        "services",
                        f"service:{service_name}",
                        "healthy"
                    ],
                    ttl=30
                )
                return True
            return False

Circuit Breaker
~~~~~~~~~~~~~~~

.. code-block:: python

    from enum import Enum
    from nicolas.cache import Cache
    
    class CircuitState(Enum):
        CLOSED = "closed"
        OPEN = "open"
        HALF_OPEN = "half_open"
    
    class CircuitBreaker:
        def __init__(self, failure_threshold=5, recovery_timeout=60):
            self.cache = Cache(backend="redis")
            self.failure_threshold = failure_threshold
            self.recovery_timeout = recovery_timeout
        
        def call(self, service_name, func, *args, **kwargs):
            """Execute function with circuit breaker protection."""
            state = self._get_state(service_name)
            
            if state == CircuitState.OPEN:
                # Check if we should try half-open
                if self._should_attempt_reset(service_name):
                    state = CircuitState.HALF_OPEN
                    self._set_state(service_name, state)
                else:
                    raise Exception(f"Circuit breaker is OPEN for {service_name}")
            
            try:
                result = func(*args, **kwargs)
                self._on_success(service_name, state)
                return result
            except Exception as e:
                self._on_failure(service_name, state)
                raise e
        
        def _get_state(self, service_name):
            """Get current circuit state."""
            state_data = self.cache.get(f"circuit:{service_name}:state")
            if not state_data:
                return CircuitState.CLOSED
            return CircuitState(state_data["state"])
        
        def _set_state(self, service_name, state):
            """Set circuit state."""
            self.cache.set(
                f"circuit:{service_name}:state",
                {
                    "state": state.value,
                    "changed_at": time.time()
                },
                tags=["circuit_breakers", f"service:{service_name}"],
                ttl=self.recovery_timeout * 2
            )
        
        def _on_success(self, service_name, state):
            """Handle successful call."""
            if state == CircuitState.HALF_OPEN:
                # Reset to closed
                self._set_state(service_name, CircuitState.CLOSED)
                self.cache.delete(f"circuit:{service_name}:failures")
        
        def _on_failure(self, service_name, state):
            """Handle failed call."""
            if state == CircuitState.HALF_OPEN:
                # Go back to open
                self._set_state(service_name, CircuitState.OPEN)
                return
            
            # Increment failure count
            failures_key = f"circuit:{service_name}:failures"
            failures = self.cache.get(failures_key) or 0
            failures += 1
            
            self.cache.set(
                failures_key,
                failures,
                tags=["circuit_breakers", f"service:{service_name}"],
                ttl=60
            )
            
            if failures >= self.failure_threshold:
                self._set_state(service_name, CircuitState.OPEN)
        
        def _should_attempt_reset(self, service_name):
            """Check if we should attempt reset."""
            state_data = self.cache.get(f"circuit:{service_name}:state")
            if not state_data:
                return True
            
            time_since_open = time.time() - state_data["changed_at"]
            return time_since_open >= self.recovery_timeout

Testing Patterns
----------------

Cache Mocking for Tests
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import unittest
    from unittest.mock import MagicMock
    from nicolas.cache import Cache
    
    class CacheTestCase(unittest.TestCase):
        def setUp(self):
            """Set up test cache."""
            # Use memory backend for tests
            self.cache = Cache(backend="memory")
        
        def tearDown(self):
            """Clean up after tests."""
            # Clear all cache entries
            for key in list(self.cache._backend._cache.keys()):
                self.cache.delete(key)
        
        def test_user_caching(self):
            """Test user data caching."""
            user_data = {"id": 1, "name": "Test User"}
            
            # Cache user
            self.cache.set("user:1", user_data, tags=["users"])
            
            # Verify cached
            cached_user = self.cache.get("user:1")
            self.assertEqual(cached_user, user_data)
            
            # Verify tags
            users = self.cache.get_by_tag("users")
            self.assertEqual(len(users), 1)
            self.assertIn("user:1", users)
    
    class MockCacheTestCase(unittest.TestCase):
        def test_with_mock_cache(self):
            """Test with mocked cache."""
            mock_cache = MagicMock(spec=Cache)
            mock_cache.get.return_value = {"mocked": True}
            
            # Your application code using mock_cache
            result = mock_cache.get("any_key")
            self.assertEqual(result, {"mocked": True})
            mock_cache.get.assert_called_once_with("any_key")