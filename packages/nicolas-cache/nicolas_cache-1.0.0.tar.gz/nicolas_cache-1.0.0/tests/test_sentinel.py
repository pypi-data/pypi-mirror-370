import pytest
from unittest.mock import Mock, patch

try:
    import redis  # noqa: F401
    from redis.sentinel import Sentinel  # noqa: F401

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from nicolas.sentinel import RedisSentinelCache


@pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis package not installed")
class TestRedisSentinelCache:
    """Test suite for the RedisSentinelCache backend."""

    def test_initialization(self):
        """Test basic initialization with mocked Sentinel."""
        with patch("redis.sentinel.Sentinel") as mock_sentinel_class:
            # Mock the sentinel instance and its methods
            mock_sentinel = Mock()
            mock_master = Mock()
            mock_slave = Mock()

            mock_sentinel.master_for.return_value = mock_master
            mock_sentinel.slave_for.return_value = mock_slave
            mock_sentinel_class.return_value = mock_sentinel

            # Create cache instance
            RedisSentinelCache(
                sentinels=[("localhost", 26379)],
                service_name="mymaster",
                db=0,
                password="password",
            )

            # Verify Sentinel was initialized correctly
            mock_sentinel_class.assert_called_once()
            call_args = mock_sentinel_class.call_args
            assert call_args[0][0] == [("localhost", 26379)]

            # Verify master_for was called during initialization
            mock_sentinel.master_for.assert_called_once_with(
                "mymaster",
                socket_timeout=0.1,
                db=0,
                password="password",
                decode_responses=False,
            )

    def test_read_operations_use_slave(self):
        """Test that read operations use slave connections."""
        with patch("redis.sentinel.Sentinel") as mock_sentinel_class:
            # Setup mocks
            mock_sentinel = Mock()
            mock_master = Mock()
            mock_slave = Mock()

            mock_sentinel.master_for.return_value = mock_master
            mock_sentinel.slave_for.return_value = mock_slave
            mock_sentinel_class.return_value = mock_sentinel

            # Configure slave to return test data
            import pickle

            mock_slave.get.return_value = pickle.dumps("test_value")
            mock_slave.smembers.return_value = set()
            mock_slave.keys.return_value = []
            mock_slave.exists.return_value = True

            cache = RedisSentinelCache(
                sentinels=[("localhost", 26379)], service_name="mymaster"
            )

            # Test read operations
            cache.get("key1")
            mock_slave.get.assert_called_once_with("cache:key1")

            cache.get_by_tag("tag1")
            mock_slave.smembers.assert_called()

            cache.getall()
            mock_slave.keys.assert_called()

            cache.exists("key1")
            mock_slave.exists.assert_called()

    def test_write_operations_use_master(self):
        """Test that write operations use master connections."""
        with patch("redis.sentinel.Sentinel") as mock_sentinel_class:
            # Setup mocks
            mock_sentinel = Mock()
            mock_master = Mock()
            mock_slave = Mock()

            mock_sentinel.master_for.return_value = mock_master
            mock_sentinel.slave_for.return_value = mock_slave
            mock_sentinel_class.return_value = mock_sentinel

            # Configure mocks
            mock_slave.exists.return_value = True
            mock_slave.smembers.return_value = set()
            mock_master.smembers.return_value = set()

            cache = RedisSentinelCache(
                sentinels=[("localhost", 26379)], service_name="mymaster"
            )

            # Test write operations
            cache.set("key1", "value1")
            mock_master.set.assert_called()

            cache.delete("key1")
            mock_master.delete.assert_called()

    def test_sentinel_with_password(self):
        """Test Sentinel initialization with sentinel password."""
        with patch("redis.sentinel.Sentinel") as mock_sentinel_class:
            mock_sentinel = Mock()
            mock_master = Mock()

            mock_sentinel.master_for.return_value = mock_master
            mock_sentinel_class.return_value = mock_sentinel

            RedisSentinelCache(
                sentinels=[("localhost", 26379)],
                service_name="mymaster",
                sentinel_password="sentinel_pass",
            )

            # Verify sentinel password was passed
            call_args = mock_sentinel_class.call_args
            assert "password" in call_args[1]
            assert call_args[1]["password"] == "sentinel_pass"

    @patch("redis.sentinel.Sentinel")
    def test_full_cache_operations(self, mock_sentinel_class):
        """Test full cache operations with mocked Sentinel."""
        # Setup comprehensive mocks
        mock_sentinel = Mock()
        mock_master = Mock()
        mock_slave = Mock()

        mock_sentinel.master_for.return_value = mock_master
        mock_sentinel.slave_for.return_value = mock_slave
        mock_sentinel_class.return_value = mock_sentinel

        # Storage for mocked Redis data
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
            # Simple pattern matching for test
            return [
                k.encode()
                for k in redis_data.keys()
                if k.startswith(pattern.replace("*", ""))
            ]

        # Configure mocks
        mock_master.set = mock_set
        mock_master.get = mock_get
        mock_master.exists = mock_exists
        mock_master.delete = mock_delete
        mock_master.sadd = mock_sadd
        mock_master.smembers = mock_smembers
        mock_master.srem = mock_srem
        mock_master.scard = mock_scard
        mock_master.setex = Mock()
        mock_master.expire = Mock()

        mock_slave.get = mock_get
        mock_slave.exists = mock_exists
        mock_slave.smembers = mock_smembers
        mock_slave.keys = mock_keys

        # Create cache and test operations
        cache = RedisSentinelCache(
            sentinels=[("localhost", 26379), ("localhost", 26380)],
            service_name="mymaster",
        )

        # Test basic set/get
        import pickle

        cache.set("key1", "value1")
        stored_value = mock_get("cache:key1")
        assert stored_value is not None
        assert pickle.loads(stored_value) == "value1"

        # Test with tags
        cache.set("key2", "value2", tags=["tag1", "tag2"])
        assert "tag1" in mock_smembers("cache:key_tags:key2")
        assert "tag2" in mock_smembers("cache:key_tags:key2")
        assert "key2" in mock_smembers("cache:tag:tag1")
        assert "key2" in mock_smembers("cache:tag:tag2")

    def test_multiple_sentinels(self):
        """Test initialization with multiple sentinel nodes."""
        with patch("redis.sentinel.Sentinel") as mock_sentinel_class:
            mock_sentinel = Mock()
            mock_master = Mock()

            mock_sentinel.master_for.return_value = mock_master
            mock_sentinel_class.return_value = mock_sentinel

            sentinels = [
                ("sentinel1", 26379),
                ("sentinel2", 26380),
                ("sentinel3", 26381),
            ]

            RedisSentinelCache(sentinels=sentinels, service_name="mymaster")

            # Verify all sentinels were passed
            call_args = mock_sentinel_class.call_args
            assert call_args[0][0] == sentinels

    def test_socket_options(self):
        """Test initialization with custom socket options."""
        with patch("redis.sentinel.Sentinel") as mock_sentinel_class:
            mock_sentinel = Mock()
            mock_master = Mock()

            mock_sentinel.master_for.return_value = mock_master
            mock_sentinel_class.return_value = mock_sentinel

            keepalive_options = {
                1: 1,  # TCP_KEEPIDLE
                2: 1,  # TCP_KEEPINTVL
                3: 5,  # TCP_KEEPCNT
            }

            RedisSentinelCache(
                sentinels=[("localhost", 26379)],
                service_name="mymaster",
                socket_timeout=5.0,
                socket_connect_timeout=2.0,
                socket_keepalive=True,
                socket_keepalive_options=keepalive_options,
            )

            # Verify socket options were passed
            call_args = mock_sentinel_class.call_args
            assert call_args[1]["socket_timeout"] == 5.0
            assert call_args[1]["socket_connect_timeout"] == 2.0
            assert call_args[1]["socket_keepalive"] is True
            assert call_args[1]["socket_keepalive_options"] == keepalive_options
