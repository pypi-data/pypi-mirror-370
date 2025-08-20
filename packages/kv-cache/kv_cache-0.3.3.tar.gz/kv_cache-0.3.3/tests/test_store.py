import os
import tempfile
import time

import pytest

from kv_cache import KVStore


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    os.unlink(path)


def test_basic_operations(temp_db):
    store = KVStore(temp_db)
    
    # Test set and get
    store.set("test_key", "test_value")
    assert store.get("test_key") == "test_value"
    
    # Test default value
    assert store.get("nonexistent_key", "default") == "default"
    
    # Test delete
    store.delete("test_key")
    assert store.get("test_key") is None


def test_ttl(temp_db):
    store = KVStore(temp_db)
    
    # Set with 1 second TTL
    store.set("ttl_key", "ttl_value", ttl=1)
    assert store.get("ttl_key") == "ttl_value"
    
    # Wait for expiration
    time.sleep(1.1)
    assert store.get("ttl_key") is None


def test_complex_values(temp_db):
    store = KVStore(temp_db)
    
    # Test dict
    dict_value = {"name": "test", "data": [1, 2, 3]}
    store.set("dict_key", dict_value)
    assert store.get("dict_key") == dict_value
    
    # Test list
    list_value = [1, "test", {"nested": True}]
    store.set("list_key", list_value)
    assert store.get("list_key") == list_value


def test_context_manager(temp_db):
    with KVStore(temp_db) as store:
        store.set("test_key", "test_value")
        assert store.get("test_key") == "test_value"
    
    # Verify the connection is closed
    assert store._conn is None


def test_clear(temp_db):
    store = KVStore(temp_db)
    
    # Add multiple entries
    store.set("key1", "value1")
    store.set("key2", "value2")
    
    # Clear all entries
    store.clear()
    
    # Verify all entries are removed
    assert store.get("key1") is None
    assert store.get("key2") is None


def test_keys(temp_db):
    """Test the keys() method."""
    store = KVStore(temp_db)
    
    # Test empty store
    assert store.keys() == []
    
    # Add some data
    store.set("key1", "value1")
    store.set("key2", "value2")
    store.set("key3", "value3")
    
    # Test keys retrieval
    keys = store.keys()
    assert len(keys) == 3
    assert set(keys) == {"key1", "key2", "key3"}
    
    # Test after deletion
    store.delete("key2")
    keys = store.keys()
    assert len(keys) == 2
    assert set(keys) == {"key1", "key3"}
    
    # Test with TTL expired entries
    store.set("ttl_key", "ttl_value", ttl=1)
    time.sleep(1.1)
    # Note: keys() doesn't automatically clean up expired entries
    # We need to manually call cleanup to remove them
    store._cleanup_expired()  # Force cleanup
    keys = store.keys()
    assert "ttl_key" not in keys


def test_values(temp_db):
    """Test the values() method."""
    store = KVStore(temp_db)
    
    # Test empty store
    assert store.values() == []
    
    # Add some data with different types
    store.set("key1", "string_value")
    store.set("key2", 42)
    store.set("key3", [1, 2, 3])
    store.set("key4", {"name": "test", "data": True})
    
    # Test values retrieval
    values = store.values()
    assert len(values) == 4
    assert "string_value" in values
    assert 42 in values
    assert [1, 2, 3] in values
    assert {"name": "test", "data": True} in values
    
    # Test after deletion
    store.delete("key2")
    values = store.values()
    assert len(values) == 3
    assert 42 not in values
    
    # Test with None values are filtered out
    # (This shouldn't happen in normal use, but test defensive programming)
    conn = store._get_connection()
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO {store.table_name} (key, value) VALUES (?, ?)', ("null_key", None))
    conn.commit()
    
    values = store.values()
    assert len(values) == 3  # None value should be filtered out


def test_items(temp_db):
    """Test the items() method."""
    store = KVStore(temp_db)
    
    # Test empty store
    assert store.items() == []
    
    # Add some data
    test_data = {
        "str_key": "string_value",
        "int_key": 123,
        "list_key": [1, 2, 3],
        "dict_key": {"nested": "value", "number": 42}
    }
    
    for key, value in test_data.items():
        store.set(key, value)
    
    # Test items retrieval
    items = store.items()
    assert len(items) == 4
    
    # Convert to dict for easier comparison
    items_dict = dict(items)
    assert items_dict == test_data
    
    # Test after deletion
    store.delete("int_key")
    items = store.items()
    assert len(items) == 3
    items_dict = dict(items)
    assert "int_key" not in items_dict
    assert items_dict["str_key"] == "string_value"
    
    # Test with TTL expired entries
    store.set("ttl_key", "ttl_value", ttl=1)
    time.sleep(1.1)
    # Note: items() doesn't automatically clean up expired entries
    store._cleanup_expired()  # Force cleanup
    items = store.items()
    items_dict = dict(items)
    assert "ttl_key" not in items_dict
    
    # Test with None values are filtered out
    conn = store._get_connection()
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO {store.table_name} (key, value) VALUES (?, ?)', ("null_key", None))
    conn.commit()
    
    items = store.items()
    items_dict = dict(items)
    assert "null_key" not in items_dict


def test_keys_values_items_consistency(temp_db):
    """Test that keys(), values(), and items() are consistent with each other."""
    store = KVStore(temp_db)
    
    # Add test data
    test_data = {
        "user:1": {"name": "Alice", "age": 30},
        "user:2": {"name": "Bob", "age": 25},
        "config:timeout": 3600,
        "config:retries": 3
    }
    
    for key, value in test_data.items():
        store.set(key, value)
    
    # Get all data using different methods
    keys = store.keys()
    values = store.values()
    items = store.items()
    
    # Test consistency
    assert len(keys) == len(values) == len(items) == len(test_data)
    
    # Ensure keys from items() match keys()
    items_keys = [item[0] for item in items]
    assert set(keys) == set(items_keys)
    
    # Ensure values from items() match values()
    items_values = [item[1] for item in items]
    assert set(str(v) for v in values) == set(str(v) for v in items_values)
    
    # Ensure items() contains all expected key-value pairs
    items_dict = dict(items)
    assert items_dict == test_data


def test_keys_values_items_with_mixed_ttl(temp_db):
    """Test keys(), values(), and items() with mixed TTL scenarios."""
    store = KVStore(temp_db)
    
    # Add data with different TTL scenarios
    store.set("permanent1", "value1")  # No TTL
    store.set("permanent2", "value2")  # No TTL
    store.set("short_ttl", "expires_soon", ttl=1)  # 1 second TTL
    store.set("long_ttl", "expires_later", ttl=3600)  # 1 hour TTL
    
    # Initially all should be present
    assert len(store.keys()) == 4
    assert len(store.values()) == 4
    assert len(store.items()) == 4
    
    # Wait for short TTL to expire
    time.sleep(1.1)
    
    # Note: keys(), values(), and items() don't automatically filter expired entries
    # They return all entries regardless of expiration status
    # Manual cleanup is needed to remove expired entries
    store._cleanup_expired()  # Manually clean up expired entries
    
    # After manual cleanup, should have 3 items
    keys = store.keys()
    values = store.values()
    items = store.items()
    
    assert len(keys) == len(values) == len(items) == 3
    assert "short_ttl" not in keys
    assert "expires_soon" not in values
    assert ("short_ttl", "expires_soon") not in items


def test_keys_values_items_edge_cases(temp_db):
    """Test edge cases for keys(), values(), and items() methods."""
    store = KVStore(temp_db)
    
    # Test empty store
    assert store.keys() == []
    assert store.values() == []
    assert store.items() == []
    
    # Test with only expired entries (after cleanup)
    store.set("expired1", "value1", ttl=1)
    store.set("expired2", "value2", ttl=1)
    time.sleep(1.1)
    store._cleanup_expired()
    
    assert store.keys() == []
    assert store.values() == []
    assert store.items() == []
    
    # Test special characters in keys and values
    special_data = {
        "key with spaces": "value with spaces",
        "key.with.dots": {"nested": "object"},
        "key_with_unicode_🚀": ["list", "with", "unicode", "🎉"],
        "": "empty_key_value",  # Empty string key
    }
    
    for key, value in special_data.items():
        store.set(key, value)
    
    keys = store.keys()
    values = store.values()
    items = store.items()
    
    assert len(keys) == len(values) == len(items) == 4
    
    # Verify all special keys are present
    for key in special_data.keys():
        assert key in keys
    
    # Verify all special values are present
    for value in special_data.values():
        assert value in values
    
    # Verify all key-value pairs are present
    items_dict = dict(items)
    assert items_dict == special_data

