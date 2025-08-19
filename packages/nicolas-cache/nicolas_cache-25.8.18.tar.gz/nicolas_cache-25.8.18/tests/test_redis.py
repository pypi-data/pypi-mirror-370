import pytest
import time
from dataclasses import dataclass

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from nicolas.redis import RedisCache


@dataclass
class SampleObject:
    """Sample object for pickling tests."""

    x: int
    y: int


@pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis package not installed")
class TestRedisCache:
    """Test suite for the RedisCache backend."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up and tear down test fixtures."""
        # Setup
        try:
            self.cache = RedisCache(prefix="test:cache:")
            # Clear any existing test data
            self._clear_test_data()
            yield
        except redis.ConnectionError:
            pytest.skip("Redis server not available")
        finally:
            # Teardown - clean up test data
            self._clear_test_data()

    def _clear_test_data(self):
        """Clear all test data from Redis."""
        try:
            # Get all keys with our test prefix
            keys = self.cache.redis.keys("test:cache:*")
            if keys:
                self.cache.redis.delete(*keys)
        except Exception:
            pass

    def test_set_and_get(self):
        """Test basic set and get operations."""
        self.cache.set("key1", "value1")
        assert self.cache.get("key1") == "value1"

    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist."""
        assert self.cache.get("nonexistent") is None

    def test_exists(self):
        """Test checking if a key exists."""
        assert self.cache.exists("key1") is False
        self.cache.set("key1", "value1")
        assert self.cache.exists("key1") is True

    def test_delete(self):
        """Test deleting a key."""
        self.cache.set("key1", "value1")
        assert self.cache.delete("key1") is True
        assert self.cache.get("key1") is None
        assert self.cache.delete("key1") is False  # Already deleted

    def test_delete_nonexistent(self):
        """Test deleting a non-existent key."""
        assert self.cache.delete("nonexistent") is False

    def test_getall(self):
        """Test getting all cache entries."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")

        all_entries = self.cache.getall()
        assert len(all_entries) == 3
        assert all_entries["key1"] == "value1"
        assert all_entries["key2"] == "value2"
        assert all_entries["key3"] == "value3"

    def test_set_with_tags(self):
        """Test setting values with tags."""
        self.cache.set("key1", "value1", tags=["tag1", "tag2"])
        self.cache.set("key2", "value2", tags=["tag1", "tag3"])
        self.cache.set("key3", "value3", tags=["tag2"])

        assert self.cache.get("key1") == "value1"
        assert self.cache.get("key2") == "value2"
        assert self.cache.get("key3") == "value3"

    def test_get_by_tag(self):
        """Test retrieving entries by tag."""
        self.cache.set("key1", "value1", tags=["tag1", "tag2"])
        self.cache.set("key2", "value2", tags=["tag1", "tag3"])
        self.cache.set("key3", "value3", tags=["tag2"])

        tag1_entries = self.cache.get_by_tag("tag1")
        assert len(tag1_entries) == 2
        assert tag1_entries["key1"] == "value1"
        assert tag1_entries["key2"] == "value2"

        tag2_entries = self.cache.get_by_tag("tag2")
        assert len(tag2_entries) == 2
        assert tag2_entries["key1"] == "value1"
        assert tag2_entries["key3"] == "value3"

        tag3_entries = self.cache.get_by_tag("tag3")
        assert len(tag3_entries) == 1
        assert tag3_entries["key2"] == "value2"

    def test_get_by_nonexistent_tag(self):
        """Test retrieving entries by a non-existent tag."""
        result = self.cache.get_by_tag("nonexistent")
        assert result == {}

    def test_delete_by_tag(self):
        """Test deleting entries by tag."""
        self.cache.set("key1", "value1", tags=["tag1", "tag2"])
        self.cache.set("key2", "value2", tags=["tag1", "tag3"])
        self.cache.set("key3", "value3", tags=["tag2"])

        # Delete all entries with tag1
        count = self.cache.delete_by_tag("tag1")
        assert count == 2

        # Verify entries are deleted
        assert self.cache.get("key1") is None
        assert self.cache.get("key2") is None
        assert self.cache.get("key3") == "value3"  # Should still exist

        # Verify tag cleanup
        assert self.cache.get_by_tag("tag1") == {}
        assert len(self.cache.get_by_tag("tag2")) == 1

    def test_delete_by_nonexistent_tag(self):
        """Test deleting by a non-existent tag."""
        count = self.cache.delete_by_tag("nonexistent")
        assert count == 0

    def test_update_with_new_tags(self):
        """Test updating a key with new tags."""
        # Set initial value with tags
        self.cache.set("key1", "value1", tags=["tag1", "tag2"])

        # Update with new tags
        self.cache.set("key1", "value1_updated", tags=["tag3", "tag4"])

        # Verify old tags are removed
        assert self.cache.get_by_tag("tag1") == {}
        assert self.cache.get_by_tag("tag2") == {}

        # Verify new tags are added
        tag3_entries = self.cache.get_by_tag("tag3")
        assert tag3_entries["key1"] == "value1_updated"

    def test_ttl(self):
        """Test TTL (time-to-live) functionality."""
        # Set a key with 2 second TTL
        self.cache.set("ttl_key", "ttl_value", ttl=2)

        # Verify it exists
        assert self.cache.get("ttl_key") == "ttl_value"
        assert self.cache.exists("ttl_key") is True

        # Wait for expiration
        time.sleep(3)

        # Verify it's expired
        assert self.cache.get("ttl_key") is None
        assert self.cache.exists("ttl_key") is False

    def test_ttl_with_tags(self):
        """Test TTL with tags."""
        # Set a key with tags and TTL
        self.cache.set("ttl_key", "ttl_value", tags=["ttl_tag"], ttl=2)

        # Verify tag lookup works
        assert len(self.cache.get_by_tag("ttl_tag")) == 1

        # Wait for expiration
        time.sleep(3)

        # Verify tag lookup returns empty after expiration
        assert self.cache.get_by_tag("ttl_tag") == {}

    def test_complex_data_types(self):
        """Test storing complex data types."""
        # List
        self.cache.set("list_key", [1, 2, 3, 4])
        assert self.cache.get("list_key") == [1, 2, 3, 4]

        # Dictionary
        data_dict = {"name": "test", "value": 42, "nested": {"a": 1}}
        self.cache.set("dict_key", data_dict)
        assert self.cache.get("dict_key") == data_dict

        # Custom object (using a module-level class that can be pickled)
        obj = SampleObject(10, 20)
        self.cache.set("obj_key", obj)
        retrieved = self.cache.get("obj_key")
        assert retrieved.x == obj.x
        assert retrieved.y == obj.y

    def test_none_value(self):
        """Test storing None as a value."""
        self.cache.set("none_key", None)
        assert self.cache.exists("none_key") is True
        assert self.cache.get("none_key") is None

    def test_empty_tags(self):
        """Test setting a value with empty tags."""
        self.cache.set("key1", "value1", tags=[])
        assert self.cache.get("key1") == "value1"

    def test_duplicate_tags(self):
        """Test setting a value with duplicate tags."""
        self.cache.set("key1", "value1", tags=["tag1", "tag1", "tag2"])
        tag1_entries = self.cache.get_by_tag("tag1")
        assert len(tag1_entries) == 1
        assert tag1_entries["key1"] == "value1"

    def test_custom_prefix(self):
        """Test using a custom prefix."""
        custom_cache = RedisCache(prefix="custom:prefix:")
        try:
            custom_cache.set("key1", "value1")

            # Verify the key is stored with custom prefix
            assert custom_cache.redis.exists("custom:prefix:key1")
            assert custom_cache.get("key1") == "value1"
        finally:
            # Clean up
            custom_cache.redis.delete("custom:prefix:key1")
