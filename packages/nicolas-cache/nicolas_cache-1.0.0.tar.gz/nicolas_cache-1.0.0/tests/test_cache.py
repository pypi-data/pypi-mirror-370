import pytest
from unittest.mock import Mock, patch

try:
    import redis  # noqa: F401

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from nicolas.cache import Cache


class TestCache:
    """Test suite for the unified Cache interface."""

    def test_memory_backend_initialization(self):
        """Test initializing cache with memory backend."""
        cache = Cache(backend="memory")
        assert cache._backend.__class__.__name__ == "MemoryCache"

    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis package not installed")
    def test_redis_backend_initialization(self):
        """Test initializing cache with Redis backend."""
        with patch("redis.Redis") as mock_redis:
            mock_redis.return_value = Mock()
            cache = Cache(backend="redis", host="localhost", port=6379)
            assert cache._backend.__class__.__name__ == "RedisCache"

    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis package not installed")
    def test_redis_sentinel_backend_initialization(self):
        """Test initializing cache with Redis Sentinel backend."""
        with patch("redis.sentinel.Sentinel") as mock_sentinel_class:
            mock_sentinel = Mock()
            mock_master = Mock()
            mock_sentinel.master_for.return_value = mock_master
            mock_sentinel_class.return_value = mock_sentinel

            cache = Cache(
                backend="redis-sentinel",
                sentinels=[("localhost", 26379)],
                service_name="mymaster",
            )
            assert cache._backend.__class__.__name__ == "RedisSentinelCache"

    def test_unsupported_backend(self):
        """Test initialization with unsupported backend."""
        with pytest.raises(ValueError, match="Unsupported backend: unsupported"):
            Cache(backend="unsupported")

    def test_memory_backend_operations(self):
        """Test basic operations with memory backend."""
        cache = Cache(backend="memory")

        # Test set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Test with tags
        cache.set("key2", "value2", tags=["tag1", "tag2"])
        assert cache.get("key2") == "value2"

        # Test get_by_tag
        results = cache.get_by_tag("tag1")
        assert "key2" in results
        assert results["key2"] == "value2"

        # Test getall
        all_results = cache.getall()
        assert len(all_results) == 2
        assert all_results["key1"] == "value1"
        assert all_results["key2"] == "value2"

        # Test exists
        assert cache.exists("key1") is True
        assert cache.exists("nonexistent") is False

        # Test delete
        assert cache.delete("key1") is True
        assert cache.exists("key1") is False

        # Test delete_by_tag
        count = cache.delete_by_tag("tag1")
        assert count == 1
        assert cache.exists("key2") is False

    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis package not installed")
    def test_redis_backend_operations(self):
        """Test basic operations with Redis backend."""
        with patch("redis.Redis") as mock_redis_class:
            # Setup mock Redis instance
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis

            # Mock Redis operations
            redis_data = {}
            redis_sets = {}

            def mock_set(key, value):
                redis_data[key] = value
                return True

            def mock_get(key):
                return redis_data.get(key)

            def mock_exists(key):
                return key in redis_data

            def mock_delete(key):
                if key in redis_data:
                    del redis_data[key]
                    return 1
                return 0

            def mock_sadd(key, *values):
                if key not in redis_sets:
                    redis_sets[key] = set()
                redis_sets[key].update(values)
                return len(values)

            def mock_smembers(key):
                return redis_sets.get(key, set())

            def mock_srem(key, value):
                if key in redis_sets:
                    redis_sets[key].discard(value)
                    return 1
                return 0

            def mock_scard(key):
                return len(redis_sets.get(key, set()))

            def mock_keys(pattern):
                return [
                    k.encode()
                    for k in redis_data.keys()
                    if k.startswith(pattern.replace("*", ""))
                ]

            mock_redis.set = mock_set
            mock_redis.get = mock_get
            mock_redis.exists = mock_exists
            mock_redis.delete = mock_delete
            mock_redis.sadd = mock_sadd
            mock_redis.smembers = mock_smembers
            mock_redis.srem = mock_srem
            mock_redis.scard = mock_scard
            mock_redis.keys = mock_keys
            mock_redis.setex = Mock()
            mock_redis.expire = Mock()

            # Test cache operations
            cache = Cache(backend="redis", host="localhost", port=6379)

            # Test basic operations
            cache.set("key1", "value1")
            assert "cache:key1" in redis_data

            # Test TTL parameter is passed through
            cache.set("key2", "value2", ttl=60)
            mock_redis.setex.assert_called()

    def test_backend_parameter_passthrough(self):
        """Test that backend-specific parameters are passed through."""
        # Test memory backend (no parameters)
        cache = Cache(backend="memory")
        assert cache._backend.__class__.__name__ == "MemoryCache"

        # Test Redis backend parameters
        if REDIS_AVAILABLE:
            with patch("redis.Redis") as mock_redis:
                mock_redis.return_value = Mock()
                cache = Cache(
                    backend="redis",
                    host="testhost",
                    port=6380,
                    db=1,
                    password="testpass",
                    prefix="test:",
                )

                # Verify Redis was called with correct parameters
                mock_redis.assert_called_with(
                    host="testhost",
                    port=6380,
                    db=1,
                    password="testpass",
                    decode_responses=False,
                )

    def test_cache_interface_consistency(self):
        """Test that all backends provide the same interface."""
        # Test memory backend
        memory_cache = Cache(backend="memory")

        # Test all methods exist and are callable
        assert hasattr(memory_cache, "get")
        assert hasattr(memory_cache, "set")
        assert hasattr(memory_cache, "delete")
        assert hasattr(memory_cache, "exists")
        assert hasattr(memory_cache, "getall")
        assert hasattr(memory_cache, "get_by_tag")
        assert hasattr(memory_cache, "delete_by_tag")

        # Test method signatures work
        memory_cache.set("key", "value")
        memory_cache.set("key", "value", tags=["tag"])
        assert memory_cache.get("key") == "value"
        assert memory_cache.exists("key") is True
        assert memory_cache.delete("key") is True

        # Test getall returns dict
        result = memory_cache.getall()
        assert isinstance(result, dict)

        # Test get_by_tag returns dict
        result = memory_cache.get_by_tag("tag")
        assert isinstance(result, dict)

        # Test delete_by_tag returns int
        result = memory_cache.delete_by_tag("tag")
        assert isinstance(result, int)

    def test_complex_data_with_all_backends(self):
        """Test storing complex data types with all backends."""
        test_data = {
            "string": "hello",
            "number": 42,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "none": None,
        }

        # Test memory backend
        memory_cache = Cache(backend="memory")
        memory_cache.set("complex", test_data)
        assert memory_cache.get("complex") == test_data

        # Test Redis backend (if available)
        if REDIS_AVAILABLE:
            with patch("redis.Redis") as mock_redis_class:
                mock_redis = Mock()
                mock_redis_class.return_value = mock_redis

                # Mock basic operations
                stored_data = {}

                def mock_set(key, value):
                    stored_data[key] = value
                    return True

                def mock_get(key):
                    return stored_data.get(key)

                mock_redis.set = mock_set
                mock_redis.get = mock_get
                mock_redis.sadd = Mock()
                mock_redis.smembers = Mock(return_value=set())
                mock_redis.delete = Mock()

                redis_cache = Cache(backend="redis")
                redis_cache.set("complex", test_data)

                # Verify data was pickled and stored
                import pickle

                assert "cache:complex" in stored_data
                unpickled_data = pickle.loads(stored_data["cache:complex"])
                assert unpickled_data == test_data

    def test_tag_operations_consistency(self):
        """Test tag operations work consistently across backends."""
        # Test with memory backend
        cache = Cache(backend="memory")

        # Set multiple keys with overlapping tags
        cache.set("key1", "value1", tags=["tag1", "tag2"])
        cache.set("key2", "value2", tags=["tag1", "tag3"])
        cache.set("key3", "value3", tags=["tag2", "tag3"])

        # Test get_by_tag
        tag1_results = cache.get_by_tag("tag1")
        assert len(tag1_results) == 2
        assert "key1" in tag1_results
        assert "key2" in tag1_results

        tag2_results = cache.get_by_tag("tag2")
        assert len(tag2_results) == 2
        assert "key1" in tag2_results
        assert "key3" in tag2_results

        # Test delete_by_tag
        deleted_count = cache.delete_by_tag("tag1")
        assert deleted_count == 2

        # Verify keys were deleted
        assert cache.exists("key1") is False
        assert cache.exists("key2") is False
        assert cache.exists("key3") is True  # Should still exist

        # Verify remaining tag relationships
        tag2_results = cache.get_by_tag("tag2")
        assert len(tag2_results) == 1
        assert "key3" in tag2_results
