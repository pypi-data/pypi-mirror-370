import sqlite3
import os
import json
from typing import Any, Optional
from datetime import datetime, timedelta
import threading
import functools
import inspect
import hashlib
from typing import Optional, Any, Callable


class Condition:
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value
        

class KVStore:
    """A simple key-value store using SQLite3 as backend with optional TTL support."""
    
    def __init__(self, db_path: str, table_name: str = "key_value_store"):
        """Initialize the key-value store.
        
        Args:
            db_path: Path to the SQLite database file
            table_name: Name of the table to store key-value pairs
        """
        self.db_path = db_path
        self.table_name = table_name
        self._conn = threading.local()
        
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # Initialize the database
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a thread-local database connection."""
        if not hasattr(self._conn, 'connection'):
            self._conn.connection = sqlite3.connect(self.db_path)
        return self._conn.connection

    def _init_db(self):
        """Initialize the database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('PRAGMA journal_mode = WAL')  # Write-Ahead Logging
        cursor.execute('PRAGMA synchronous = NORMAL') 
        cursor.execute(f'PRAGMA mmap_size = {512 * 1024 * 1024}')  # 512MB
        cursor.execute(f'PRAGMA cache_size = -{128 * 1024}')  # 128MB
        cursor.execute(f'PRAGMA page_size = {4 * 1024}')  # 4KB
        
        # Create the key-value table with TTL support
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                key TEXT PRIMARY KEY,
                value BLOB,
                expires_at TIMESTAMP
            )
        ''')
        
        # Create an index on expires_at for efficient cleanup
        cursor.execute(f'''
            CREATE INDEX IF NOT EXISTS idx_{self.table_name}_expires_at 
            ON {self.table_name}(expires_at)
        ''')

        conn.commit()

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set a value for a key with optional TTL.
        
        Args:
            key: The key to store the value under
            value: The value to store (will be JSON serialized)
            ttl: Time-to-live in seconds (optional)
        """
        expires_at = None
        if ttl is not None:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        serialized_value = json.dumps(value)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            INSERT OR REPLACE INTO {self.table_name} (key, value, expires_at)
            VALUES (?, ?, ?)
        ''', (key, serialized_value, expires_at))
        
        conn.commit()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value for a key.
        
        Args:
            key: The key to retrieve
            default: Default value if key doesn't exist or has expired
            
        Returns:
            The stored value or default if not found
        """
        self._cleanup_expired()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            SELECT value FROM {self.table_name}
            WHERE key = ? AND (expires_at IS NULL OR expires_at > ?)
        ''', (key, datetime.now()))
        
        result = cursor.fetchone()
        
        if result is None:
            return default
            
        try:
            return json.loads(result[0])
        
        except json.JSONDecodeError:
            return default

    def delete(self, key: str):
        """Delete a key from the store.
        
        Args:
            key: The key to delete
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            DELETE FROM {self.table_name}
            WHERE key = ?
        ''', (key,))
        
        conn.commit()

    def keys(self) -> list:
        """List all keys in the store."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'SELECT key FROM {self.table_name}')
        keys = cursor.fetchall()
        
        return [key[0] for key in keys]
    
    def values(self) -> list:
        """List all values in the store."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'SELECT value FROM {self.table_name}')
        values = cursor.fetchall()
        
        return [json.loads(value[0]) for value in values if value[0] is not None]
    
    def items(self) -> list:
        """List all key-value pairs in the store."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'SELECT key, value FROM {self.table_name}')
        items = cursor.fetchall()
        
        return [(key, json.loads(value)) for key, value in items if value is not None]

    def _cleanup_expired(self):
        """Clean up expired entries."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            DELETE FROM {self.table_name}
            WHERE expires_at IS NOT NULL AND expires_at <= ?
        ''', (datetime.now(),))
        
        conn.commit()

    def clear(self):
        """Clear all entries from the store."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'DELETE FROM {self.table_name}')
        conn.commit()

    def close(self):
        """Close the database connection."""
        if self._conn is not None:
            if self._conn.connection is not None:
                self._conn.connection.close()
            self._conn.connection = None
        self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def scache(ttl: Optional[int] = None, store: Optional[KVStore] = None, conditional_key: str = '', key_func: Optional[Callable] = None):
    """
    Decorator to cache function results using KVStore.
    
    Args:
        ttl: Time-to-live in seconds (optional)
        store: KVStore instance (optional, will create default if None)
        conditional_key: Key to check if caching should be enabled (optional)
        key_func: Custom function to generate cache key. Should accept (func, args, kwargs) and return string (optional)
    """
    def decorator(func: Callable) -> Callable:
        # Create or use provided store
        cache_store = store or KVStore("cache.db")
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if cache_store.get(conditional_key, default=True) == False:
                return func(*args, **kwargs)
            
            # Generate cache key
            if key_func:
                key = key_func(func, args, kwargs)
            else:
                # Create cache key from function name and arguments
                def serialize_for_key(obj):
                    """Serialize object for cache key generation."""
                    try:
                        return json.dumps(obj, sort_keys=True, default=str)
                    except (TypeError, ValueError):
                        return str(obj)
                
                key_parts = [
                    func.__name__,
                    serialize_for_key(args),
                    serialize_for_key(sorted(kwargs.items()))
                ]
                key = hashlib.sha256(''.join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_value = cache_store.get(key)
            if cached_value is not None:
                return cached_value
                
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_store.set(key, result, ttl=ttl)
            return result
            
        async def async_wrapper(*args, **kwargs):
            if cache_store.get(conditional_key, default=True) == False:
                return func(*args, **kwargs)
            
            # Generate cache key
            if key_func:
                key = key_func(func, args, kwargs)
            else:
                # Create cache key from function name and arguments
                def serialize_for_key(obj):
                    """Serialize object for cache key generation."""
                    try:
                        return json.dumps(obj, sort_keys=True, default=str)
                    except (TypeError, ValueError):
                        return str(obj)
                
                key_parts = [
                    func.__name__,
                    serialize_for_key(args),
                    serialize_for_key(sorted(kwargs.items()))
                ]
                key = hashlib.sha256(''.join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_value = cache_store.get(key)
            if cached_value is not None:
                return cached_value
                
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_store.set(key, result, ttl=ttl)
            return result
            
        return async_wrapper if inspect.iscoroutinefunction(func) else wrapper
    return decorator



# Example usage:
if __name__ == "__main__":
    # Create a store in the current directory
    store = KVStore("cache.db")
    
    # Store some autocomplete results with a 1-hour TTL
    results = ["apple", "application", "appetite"]
    store.set("auto:app", results, ttl=3600)
    
    # Retrieve results
    cached_results = store.get("auto:app", default=[])
    print(f"Cached results: {cached_results}")
    
    # Clean up
    store.close()