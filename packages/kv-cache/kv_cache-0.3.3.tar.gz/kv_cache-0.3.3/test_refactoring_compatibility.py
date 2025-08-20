#!/usr/bin/env python3
"""
Test script to verify that the refactored cache key generation produces
identical results to the original implementation.
"""

import json
import hashlib
from src.kv_cache.main import _serialize_for_key, _generate_cache_key


def old_serialize_for_key(obj):
    """Original serialize_for_key function for comparison."""
    try:
        return json.dumps(obj, sort_keys=True, default=str)
    except (TypeError, ValueError):
        return str(obj)


def old_generate_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """Original cache key generation logic for comparison."""
    key_parts = [
        func_name,
        old_serialize_for_key(args),
        old_serialize_for_key(sorted(kwargs.items()))
    ]
    return hashlib.sha256(''.join(key_parts).encode()).hexdigest()


def test_compatibility():
    """Test that new implementation produces same results as old implementation."""
    test_cases = [
        # Test case: (func_name, args, kwargs)
        ("test_func", (1, 2, 3), {}),
        ("test_func", (1, "hello", 3.14), {}),
        ("test_func", (), {"a": 1, "b": 2, "c": 3}),
        ("test_func", (1, 2), {"x": "test", "y": [1, 2, 3]}),
        ("different_func", (1, 2, 3), {}),
        ("test_func", ([1, 2, 3], {"nested": {"a": 1, "b": 2}}), {"param": "value"}),
        ("test_func", ("unicode: 🚀 café naïve",), {}),
        ("test_func", (None, True, False), {}),
        ("test_func", ({"c": 3, "a": 1, "b": 2},), {}),  # Test dict ordering
    ]
    
    print("Testing compatibility between old and new implementations...")
    
    all_passed = True
    for i, (func_name, args, kwargs) in enumerate(test_cases):
        old_key = old_generate_cache_key(func_name, args, kwargs)
        new_key = _generate_cache_key(func_name, args, kwargs)
        
        if old_key == new_key:
            print(f"✅ Test {i+1}: PASS")
        else:
            print(f"❌ Test {i+1}: FAIL")
            print(f"   Function: {func_name}")
            print(f"   Args: {args}")
            print(f"   Kwargs: {kwargs}")
            print(f"   Old key: {old_key}")
            print(f"   New key: {new_key}")
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! New implementation is compatible with old one.")
    else:
        print("\n❌ Some tests failed! There's an incompatibility issue.")
    
    return all_passed


def test_serialization_compatibility():
    """Test serialization function compatibility."""
    test_objects = [
        42,
        "hello world",
        [1, 2, 3],
        {"b": 2, "a": 1},
        None,
        True,
        False,
        (1, 2, 3),
        {"nested": {"data": [1, 2, 3]}},
        "unicode: 🚀 café naïve",
    ]
    
    print("\nTesting serialization function compatibility...")
    
    all_passed = True
    for i, obj in enumerate(test_objects):
        old_result = old_serialize_for_key(obj)
        new_result = _serialize_for_key(obj)
        
        if old_result == new_result:
            print(f"✅ Serialization test {i+1}: PASS")
        else:
            print(f"❌ Serialization test {i+1}: FAIL")
            print(f"   Object: {obj}")
            print(f"   Old result: {old_result}")
            print(f"   New result: {new_result}")
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    compatibility_ok = test_compatibility()
    serialization_ok = test_serialization_compatibility()
    
    if compatibility_ok and serialization_ok:
        print("\n✅ All compatibility tests passed!")
        exit(0)
    else:
        print("\n❌ Compatibility issues detected!")
        exit(1)
