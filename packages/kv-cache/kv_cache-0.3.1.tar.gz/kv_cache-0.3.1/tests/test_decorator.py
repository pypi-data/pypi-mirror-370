import pytest
import asyncio
import time
import os
from kv_cache.main import KVStore, scache

@pytest.fixture
def temp_store(tmp_path):
    store_path = os.path.join(tmp_path, "test_cache.db")
    store = KVStore(store_path)
    yield store
    store.close()

    os.remove(store_path)

def test_sync_function_caching(temp_store):
    call_count = 0
    
    @scache(store=temp_store)
    def expensive_function(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2
    
    # First call should execute the function
    result1 = expensive_function(5)
    assert result1 == 10
    assert call_count == 1
    
    # Second call should use cache
    result2 = expensive_function(5)
    assert result2 == 10
    assert call_count == 1  # Call count shouldn't increase

@pytest.mark.asyncio
async def test_async_function_caching(temp_store):
    call_count = 0
    
    @scache(store=temp_store)
    async def expensive_async_function(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2
    
    # First call should execute the function
    result1 = await expensive_async_function(5)
    assert result1 == 10
    assert call_count == 1
    
    # Second call should use cache
    result2 = await expensive_async_function(5)
    assert result2 == 10
    assert call_count == 1

def test_ttl_caching(temp_store):
    @scache(ttl=1, store=temp_store)
    def cached_function(x: int) -> int:
        return x * 2
    
    # First call
    result1 = cached_function(5)
    assert result1 == 10
    
    # Wait for TTL to expire
    time.sleep(1.1)
    
    # Value should be recomputed
    result2 = cached_function(5)
    assert result2 == 10
    assert temp_store.get(cached_function.__name__ + str((5,)) + str([])) is None

def test_different_arguments(temp_store):
    call_count = 0
    
    @scache(store=temp_store)
    def multi_arg_function(x: int, y: str, z: bool = False) -> str:
        nonlocal call_count
        call_count += 1
        return f"{x}-{y}-{z}"
    
    # Different argument combinations should create different cache entries
    result1 = multi_arg_function(1, "test")
    result2 = multi_arg_function(1, "test", False)
    result3 = multi_arg_function(2, "test")
    
    assert result1 == "1-test-False"  # implicit
    assert result2 == "1-test-False"  # explicit
    assert result3 == "2-test-False"
    assert call_count == 3  # result1 and result2 should use same cache

def test_custom_store():
    # Test with default store
    @scache()
    def simple_function(x: int) -> int:
        return x * 2
    
    result = simple_function(5)
    assert result == 10
    
    # Clean up default store
    os.remove("cache.db")

def test_error_handling(temp_store):
    @scache(store=temp_store)
    def failing_function():
        raise ValueError("Test error")
    
    with pytest.raises(ValueError):
        failing_function()
    
    # Second call should still raise error
    with pytest.raises(ValueError):
        failing_function()