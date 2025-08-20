# KV_Cache

A fast key-value store using SQLite as a backend, designed specifically for CLI tools needing persistent cache storage.

## Features

- 🚀 Fast SQLite-based storage
- ⏰ Built-in TTL support
- 🔒 Thread-safe operations
- 🧹 Automatic cleanup of expired entries

## Installation

```bash
pip install kv-cache
```

## Quick Start

```python
from kv_cache import KVStore

# Initialize the store
store = KVStore("cache.db")

# Store a value with 1-hour TTL
store.set("my_key", {"data": "value"}, ttl=3600)

# Retrieve the value
value = store.get("my_key")
print(value)  # {'data': 'value'}

# Delete when done
store.delete("my_key")
```

## Usage with CLI Autocomplete

Perfect for caching slow remote calls in CLI tools:

```python
import time
from kv_cache import KVStore, scache

# directly use the store
def get_autocomplete_suggestions(prefix: str) -> list:
    store = KVStore("~/.mycli/store.db")
    
    # Try cache first
    store_key = f"auto:{prefix}"
    results = store.get(store_key)
    
    if results is None:
        # Cache miss - fetch from remote
        results = fetch_from_remote_server(prefix)  # Slow remote call
        store.set(store_key, results, ttl=3600)  # Cache for 1 hour
    
    return results

# or use the `scache` decorator to easily cache the function result
@scache(ttl=3600, KVStore("~/.mycli/store.db"))
def long_function_call(arg1, arg2, arg3=None):
    time.sleep(1)

long_function_call(1, 2, arg3='test') # will take 1 seconds
long_function_call(1, 2, arg3='test') # instant

```

## API Reference

### KVStore

```python
class KVStore:
    def __init__(self, db_path: str, table_name: str = "key_value_store"):
        """Initialize the store with database path and optional table name."""
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set a value with optional TTL in seconds."""
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value or return default if not found."""
        
    def delete(self, key: str):
        """Delete a key from the store."""
        
    def clear(self):
        """Clear all entries from the store."""
        
    def close(self):
        """Close the database connection."""

    def __enter__(self):
    def __exit__(self):
        """ Context manager to use with `with` """
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/lcances/kv_cache.git
cd fast-kv

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Code Style

The project uses `black` for code formatting and `isort` for import sorting:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/
```

## License

MIT License - see LICENSE file for details.