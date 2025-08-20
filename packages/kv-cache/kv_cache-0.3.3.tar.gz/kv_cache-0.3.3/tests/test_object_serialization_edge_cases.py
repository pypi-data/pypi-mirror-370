import pytest
import json
import hashlib
from datetime import datetime, date
from dataclasses import dataclass
from typing import List, Dict, Any
import sys
import os

# Add the src directory to the path to import our module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from kv_cache.main import scache, KVStore


class TestObjectSerializationEdgeCases:
    """Test edge cases for object serialization in cache key generation."""
    
    def setup_method(self):
        """Set up a test store for each test."""
        self.test_store = KVStore(":memory:")
    
    def teardown_method(self):
        """Clean up after each test."""
        self.test_store.close()

    def test_objects_without_consistent_repr(self):
        """Test objects that don't have consistent string representations."""
        
        class InconsistentObject:
            def __init__(self, value):
                self.value = value
                self.creation_time = datetime.now()  # This will be different each time
            
            def __str__(self):
                return f"InconsistentObject({self.value}, {self.creation_time})"
        
        call_count = 0
        
        @scache(store=self.test_store)
        def test_func(obj):
            nonlocal call_count
            call_count += 1
            return f"processed_{obj.value}"
        
        obj1 = InconsistentObject("test")
        obj2 = InconsistentObject("test")
        
        result1 = test_func(obj1)
        result2 = test_func(obj2)
        
        # These will likely have different cache keys due to different creation times
        assert call_count == 2
        assert result1 == result2 == "processed_test"

    def test_objects_with_consistent_repr(self):
        """Test objects with consistent __repr__ methods."""
        
        class ConsistentObject:
            def __init__(self, name, value):
                self.name = name
                self.value = value
                self.creation_time = datetime.now()  # This varies but not in repr
            
            def __repr__(self):
                # Only include deterministic fields in repr
                return f"ConsistentObject(name='{self.name}', value={self.value})"
        
        call_count = 0
        
        @scache(store=self.test_store)
        def test_func(obj):
            nonlocal call_count
            call_count += 1
            return f"processed_{obj.name}_{obj.value}"
        
        obj1 = ConsistentObject("test", 42)
        obj2 = ConsistentObject("test", 42)
        
        result1 = test_func(obj1)
        result2 = test_func(obj2)
        
        # Should use cache because __repr__ is consistent
        assert call_count == 1
        assert result1 == result2 == "processed_test_42"

    def test_dataclass_consistency(self):
        """Test dataclass objects for cache consistency."""
        
        @dataclass
        class DataClassExample:
            name: str
            value: int
            metadata: Dict[str, Any]
        
        call_count = 0
        
        @scache(store=self.test_store)
        def test_func(obj):
            nonlocal call_count
            call_count += 1
            return f"processed_{obj.name}_{obj.value}"
        
        obj1 = DataClassExample("test", 42, {"key": "value"})
        obj2 = DataClassExample("test", 42, {"key": "value"})
        
        result1 = test_func(obj1)
        result2 = test_func(obj2)
        
        # Dataclasses have consistent __repr__ by default
        assert call_count == 1
        assert result1 == result2 == "processed_test_42"

    def test_nested_objects(self):
        """Test nested objects for cache consistency."""
        
        class InnerObject:
            def __init__(self, value):
                self.value = value
            
            def __repr__(self):
                return f"InnerObject({self.value})"
        
        class OuterObject:
            def __init__(self, name, inner):
                self.name = name
                self.inner = inner
            
            def __repr__(self):
                return f"OuterObject(name='{self.name}', inner={self.inner})"
        
        call_count = 0
        
        @scache(store=self.test_store)
        def test_func(obj):
            nonlocal call_count
            call_count += 1
            return f"processed_{obj.name}_{obj.inner.value}"
        
        inner1 = InnerObject(42)
        outer1 = OuterObject("test", inner1)
        
        inner2 = InnerObject(42)
        outer2 = OuterObject("test", inner2)
        
        result1 = test_func(outer1)
        result2 = test_func(outer2)
        
        assert call_count == 1
        assert result1 == result2 == "processed_test_42"

    def test_objects_with_collections(self):
        """Test objects containing collections."""
        
        class ObjectWithCollections:
            def __init__(self, name, items, mapping):
                self.name = name
                self.items = items
                self.mapping = mapping
            
            def __repr__(self):
                return f"ObjectWithCollections(name='{self.name}', items={self.items}, mapping={self.mapping})"
        
        call_count = 0
        
        @scache(store=self.test_store)
        def test_func(obj):
            nonlocal call_count
            call_count += 1
            return f"processed_{obj.name}"
        
        # Test with same data in different order for mapping
        obj1 = ObjectWithCollections("test", [1, 2, 3], {"b": 2, "a": 1})
        obj2 = ObjectWithCollections("test", [1, 2, 3], {"a": 1, "b": 2})
        
        result1 = test_func(obj1)
        result2 = test_func(obj2)
        
        # The mapping order difference will cause different cache keys
        assert call_count == 2
        assert result1 == result2 == "processed_test"

    def test_function_objects_as_parameters(self):
        """Test function objects as parameters."""
        
        def helper_function(x):
            return x * 2
        
        call_count = 0
        
        @scache(store=self.test_store)
        def test_func(func, value):
            nonlocal call_count
            call_count += 1
            return func(value)
        
        result1 = test_func(helper_function, 5)
        result2 = test_func(helper_function, 5)
        
        assert call_count == 1
        assert result1 == result2 == 10

    def test_lambda_functions_as_parameters(self):
        """Test lambda functions as parameters."""
        call_count = 0
        
        @scache(store=self.test_store)
        def test_func(func, value):
            nonlocal call_count
            call_count += 1
            return func(value)
        
        lambda_func = lambda x: x * 3
        
        result1 = test_func(lambda_func, 5)
        result2 = test_func(lambda_func, 5)
        
        assert call_count == 1
        assert result1 == result2 == 15

    def test_circular_references(self):
        """Test handling of circular references."""
        
        class Node:
            def __init__(self, value):
                self.value = value
                self.parent = None
                self.children = []
            
            def add_child(self, child):
                child.parent = self
                self.children.append(child)
            
            def __repr__(self):
                # Avoid infinite recursion in repr
                return f"Node(value={self.value}, children_count={len(self.children)})"
        
        call_count = 0
        
        @scache(store=self.test_store)
        def test_func(node):
            nonlocal call_count
            call_count += 1
            return f"processed_{node.value}"
        
        root = Node("root")
        child = Node("child")
        root.add_child(child)
        
        # This should not cause infinite recursion
        result1 = test_func(root)
        result2 = test_func(root)
        
        assert call_count == 1
        assert result1 == result2 == "processed_root"

    def test_very_large_objects(self):
        """Test very large objects."""
        
        class LargeObject:
            def __init__(self, size):
                self.data = list(range(size))
                self.metadata = {f"key_{i}": f"value_{i}" for i in range(min(size, 1000))}
            
            def __repr__(self):
                return f"LargeObject(size={len(self.data)}, metadata_keys={len(self.metadata)})"
        
        call_count = 0
        
        @scache(store=self.test_store)
        def test_func(obj):
            nonlocal call_count
            call_count += 1
            return f"processed_{len(obj.data)}"
        
        large_obj1 = LargeObject(10000)
        large_obj2 = LargeObject(10000)
        
        result1 = test_func(large_obj1)
        result2 = test_func(large_obj2)
        
        assert call_count == 1
        assert result1 == result2 == "processed_10000"

    def test_objects_with_special_methods(self):
        """Test objects with special methods like __hash__, __eq__."""
        
        class SpecialObject:
            def __init__(self, name, value):
                self.name = name
                self.value = value
            
            def __repr__(self):
                return f"SpecialObject(name='{self.name}', value={self.value})"
            
            def __hash__(self):
                return hash((self.name, self.value))
            
            def __eq__(self, other):
                if not isinstance(other, SpecialObject):
                    return False
                return self.name == other.name and self.value == other.value
        
        call_count = 0
        
        @scache(store=self.test_store)
        def test_func(obj):
            nonlocal call_count
            call_count += 1
            return f"processed_{obj.name}_{obj.value}"
        
        obj1 = SpecialObject("test", 42)
        obj2 = SpecialObject("test", 42)
        
        result1 = test_func(obj1)
        result2 = test_func(obj2)
        
        assert call_count == 1
        assert result1 == result2 == "processed_test_42"

    def test_objects_with_slots(self):
        """Test objects using __slots__."""
        
        class SlottedObject:
            __slots__ = ['name', 'value']
            
            def __init__(self, name, value):
                self.name = name
                self.value = value
            
            def __repr__(self):
                return f"SlottedObject(name='{self.name}', value={self.value})"
        
        call_count = 0
        
        @scache(store=self.test_store)
        def test_func(obj):
            nonlocal call_count
            call_count += 1
            return f"processed_{obj.name}_{obj.value}"
        
        obj1 = SlottedObject("test", 42)
        obj2 = SlottedObject("test", 42)
        
        result1 = test_func(obj1)
        result2 = test_func(obj2)
        
        assert call_count == 1
        assert result1 == result2 == "processed_test_42"

    def test_numeric_types_precision(self):
        """Test numeric types and precision issues."""
        call_count = 0
        
        @scache(store=self.test_store)
        def test_func(value):
            nonlocal call_count
            call_count += 1
            return f"processed_{value}"
        
        # Test float precision
        result1 = test_func(1.0)
        result2 = test_func(1.0000000000000001)  # Might be considered equal
        
        # Test integer vs float
        result3 = test_func(42)
        result4 = test_func(42.0)
        
        # These should be treated differently by JSON serialization
        assert call_count >= 3  # At least 3 different cache entries

    def test_boolean_and_none_edge_cases(self):
        """Test boolean and None value edge cases."""
        call_count = 0
        
        @scache(store=self.test_store)
        def test_func(value):
            nonlocal call_count
            call_count += 1
            return f"processed_{value}"
        
        values = [True, False, None, 0, 1, "", "false", "true", "null"]
        results = []
        
        for value in values:
            result = test_func(value)
            results.append(result)
        
        # Each unique value should be cached separately
        assert call_count == len(values)
        
        # Test caching works for repeated calls
        for value in values:
            test_func(value)
        
        # Should not increase call count
        assert call_count == len(values)

    def test_unicode_normalization(self):
        """Test Unicode normalization issues."""
        import unicodedata
        
        call_count = 0
        
        @scache(store=self.test_store)
        def test_func(text):
            nonlocal call_count
            call_count += 1
            return f"processed_{len(text)}"
        
        # Same character represented differently
        text1 = "café"  # é as single character
        text2 = "cafe" + "\u0301"  # e + combining acute accent
        
        # Normalize both
        norm1 = unicodedata.normalize('NFC', text1)
        norm2 = unicodedata.normalize('NFC', text2)
        
        result1 = test_func(norm1)
        result2 = test_func(norm2)
        
        if norm1 == norm2:
            assert call_count == 1
            assert result1 == result2
        else:
            assert call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
