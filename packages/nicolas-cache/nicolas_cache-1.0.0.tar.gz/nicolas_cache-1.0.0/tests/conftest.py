"""Pytest configuration and fixtures for nicolas-cache tests."""

import pytest

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


@pytest.fixture(scope="session")
def redis_server():
    """
    Session-scoped fixture that provides a Redis server connection.

    This fixture attempts to connect to a Redis server running on localhost:6379.
    If the connection fails, tests requiring Redis will be skipped.
    """
    if not REDIS_AVAILABLE:
        pytest.skip("Redis package not installed")

    try:
        client = redis.Redis(host="localhost", port=6379, decode_responses=False)
        client.ping()  # Test connection
        yield client
    except redis.ConnectionError:
        pytest.skip("Redis server not available on localhost:6379")


@pytest.fixture
def clean_redis(redis_server):
    """
    Function-scoped fixture that provides a clean Redis database.

    This fixture flushes the Redis database before and after each test
    to ensure test isolation.
    """
    # Clean before test
    redis_server.flushdb()

    yield redis_server

    # Clean after test
    redis_server.flushdb()


@pytest.fixture
def sample_data():
    """Fixture providing sample test data."""
    return {
        "simple_string": "hello world",
        "simple_number": 42,
        "simple_list": [1, 2, 3, 4, 5],
        "simple_dict": {"key": "value", "nested": {"inner": "data"}},
        "complex_data": {
            "users": [
                {"id": 1, "name": "Alice", "active": True},
                {"id": 2, "name": "Bob", "active": False},
            ],
            "settings": {
                "theme": "dark",
                "notifications": True,
                "limits": {"max_items": 100, "timeout": 30},
            },
        },
    }


@pytest.fixture
def sample_tags():
    """Fixture providing sample tag data."""
    return {
        "user_tags": ["user", "profile", "active"],
        "system_tags": ["system", "config", "internal"],
        "shared_tags": ["shared", "common"],
        "special_tags": ["special-chars", "with_underscore", "with.dot"],
    }


@pytest.fixture(params=["memory"])
def cache_backend(request):
    """
    Parametrized fixture that provides different cache backend instances.

    This fixture allows tests to run against multiple backends automatically.
    Currently includes memory backend, with Redis backends available when
    Redis is installed and running.
    """
    from nicolas.cache import Cache

    backend_name = request.param

    if backend_name == "memory":
        return Cache(backend="memory")
    elif backend_name == "redis":
        if not REDIS_AVAILABLE:
            pytest.skip("Redis package not installed")

        try:
            # Test Redis connection
            test_client = redis.Redis(host="localhost", port=6379)
            test_client.ping()

            # Create cache with test prefix
            cache = Cache(backend="redis", prefix="test:cache:")

            # Clean any existing test data
            cache._backend.redis.flushdb()

            yield cache

            # Clean up after test
            cache._backend.redis.flushdb()

        except redis.ConnectionError:
            pytest.skip("Redis server not available")
    else:
        pytest.skip(f"Backend {backend_name} not available for testing")


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "redis: mark test as requiring Redis server")
    config.addinivalue_line(
        "markers", "sentinel: mark test as requiring Redis Sentinel"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers automatically.

    This function automatically adds markers to tests based on their names
    and requirements.
    """
    for item in items:
        # Add redis marker to Redis-related tests
        if "redis" in item.nodeid.lower() and "test_redis" in item.nodeid:
            item.add_marker(pytest.mark.redis)

        # Add sentinel marker to Sentinel-related tests
        if "sentinel" in item.nodeid.lower():
            item.add_marker(pytest.mark.sentinel)

        # Add integration marker to certain test patterns
        if any(pattern in item.nodeid.lower() for pattern in ["integration", "full_"]):
            item.add_marker(pytest.mark.integration)


# Custom assertion helpers
def assert_cache_empty(cache):
    """Assert that a cache is empty."""
    assert cache.getall() == {}


def assert_cache_contains(cache, key, value):
    """Assert that a cache contains a specific key-value pair."""
    assert cache.exists(key), f"Key '{key}' not found in cache"
    assert cache.get(key) == value, f"Value mismatch for key '{key}'"


def assert_tag_contains(cache, tag, expected_keys):
    """Assert that a tag contains specific keys."""
    tagged_items = cache.get_by_tag(tag)
    actual_keys = set(tagged_items.keys())
    expected_keys = set(expected_keys)
    assert actual_keys == expected_keys, (
        f"Tag '{tag}' contains {actual_keys}, expected {expected_keys}"
    )
