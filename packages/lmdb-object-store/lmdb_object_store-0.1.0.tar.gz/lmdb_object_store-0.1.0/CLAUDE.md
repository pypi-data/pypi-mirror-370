# LmdbObjectStore Development Guide

## Project Overview
LmdbObjectStore is a Python package that provides a thread-safe, buffered object store using LMDB (Lightning Memory-Mapped Database). The package allows efficient storage and retrieval of arbitrary Python objects with features like write buffering, automatic map resizing, and flexible key handling.

## Project Structure
```
LmdbObjectStore/
├── src/
│   └── lmdb_object_store/
│       ├── __init__.py              # Package exports
│       ├── lmdb_object_store.py     # Main LmdbObjectStore class
│       └── py.typed                 # Type hints marker
├── tests/
│   ├── test_basic_operations.py     # Core CRUD operations (11 tests)
│   ├── test_buffering.py            # Write buffering behavior (11 tests)
│   ├── test_close_error_handling.py # Close method error handling (6 tests)
│   ├── test_concurrency.py          # Thread safety tests (9 tests)
│   ├── test_deletion.py             # Deletion operations (10 tests)
│   ├── test_edge_cases.py           # Edge cases and error handling (18 tests)
│   ├── test_multiple_resize.py      # Map resizing behavior (3 tests)
│   └── test_put_many.py             # Bulk operations (14 tests)
├── pyproject.toml                   # Project configuration
├── README.md                        # Project documentation
├── CLAUDE.md                        # Development guide (this file)
└── uv.lock                          # Dependency lock file
```

## Development Environment
- **Package Manager**: uv (modern Python package manager and project manager)
- **Python Version**: >=3.10
- **Dependencies**: lmdb>=1.7.3
- **Dev Dependencies**: pytest>=8.4.1
- **Code Quality**: ruff (linting, formatting)

**Note**: This project uses uv for dependency management and script execution. Always use `uv run` commands to ensure proper virtual environment isolation and dependency resolution.

## Key Features Implemented
1. **Thread-safe operations** with reader-writer lock pattern and condition variables
2. **Write buffering** for batch operations (configurable batch_size with automatic flush)
3. **Automatic LMDB map resizing** on MapFullError with optional max_map_size limits
4. **Flexible key handling** (bytes, bytearray, memoryview, str with encoding and normalization)
5. **Dict-like interface** (__getitem__, __setitem__, __delitem__, __contains__)
6. **Context manager support** for resource management with proper cleanup
7. **Bulk operations** with get_many() and put_many() methods
8. **Advanced error handling** with customizable close() behavior and flush control
9. **Unicode normalization** support for string keys with configurable forms
10. **Atomic bulk writes** with put_many() using single LMDB transactions

## Common Development Tasks

### Running Tests
```bash
# Run all tests (82 tests across 8 test files)
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_basic_operations.py

# Run with verbose output
uv run pytest tests/ -v

# Run with coverage
uv run pytest --cov=src tests/
```

### Code Quality Checks
```bash
# Linting and formatting (uv automatically manages ruff dependency)
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Check specific error types
uv run ruff check src/ --select=E,F
```


### Installing Dependencies
```bash
# Install project dependencies (automatically creates virtual environment)
uv sync

# Install with development dependencies
uv sync --group dev
```

### Alternative uv Commands
```bash
# Run any Python script with proper environment
uv run python <script.py>

# Add new dependencies
uv add <package-name>

# Add development dependencies
uv add --group dev <package-name>
```

## Code Architecture Notes

### Core Class: LmdbObjectStore (src/lmdb_object_store/lmdb_object_store.py:48)
- Thread-safe using RLock and Condition variables for reader-writer coordination
- Write operations are buffered until batch_size threshold or manual flush
- Automatic map resizing with retry logic on LMDB MapFullError
- Supports configurable key encoding, Unicode normalization, and flexible key types
- Comprehensive error handling with custom error formatters

### Key Methods:
- `put(key, obj)` - Store object (buffered, line 325)
- `put_many(items)` - Atomic bulk insert with automatic retry (line 453)  
- `get(key, default=None)` - Retrieve object (line 522)
- `get_many(keys)` - Bulk retrieval with optional key decoding (line 353)
- `delete(key)` - Mark for deletion (buffered, line 577)
- `exists(key, *, flush=None)` - Check key existence with flush control (line 606)
- `flush()` - Force write buffer flush (line 647)
- `close(*, strict=False)` - Close with configurable error handling (line 661)

### Advanced Features:
- **Atomic Operations**: put_many() executes all writes in single LMDB transaction
- **Flexible Flushing**: exists() method supports flush parameter override
- **Error Recovery**: Automatic map resizing with configurable limits
- **Resource Management**: Proper cleanup with context manager support
- **Bulk Operations**: Efficient get_many() and put_many() for large datasets

### Testing Strategy (82 Total Tests)
Comprehensive test coverage across 8 test files:
- **test_basic_operations.py (11 tests)**: Core CRUD operations, key normalization, mapping protocol
- **test_buffering.py (11 tests)**: Write buffer behavior, autoflush settings, batch operations
- **test_close_error_handling.py (6 tests)**: Close method error handling, exists flush parameter
- **test_concurrency.py (9 tests)**: Thread safety, concurrent access, reader-writer locks
- **test_deletion.py (10 tests)**: Deletion operations, DELETION_SENTINEL handling
- **test_edge_cases.py (18 tests)**: Error conditions, edge cases, LMDB-specific features
- **test_multiple_resize.py (3 tests)**: Advanced map resizing scenarios
- **test_put_many.py (14 tests)**: Bulk operations, atomic transactions, map resize handling

## Configuration Details

### pyproject.toml Key Settings:
- **Package name**: lmdbobjectstore
- **Python requirement**: >=3.10
- **Ruff configuration**: Line length 88, numpy docstring style
- **Pytest configuration**: Strict mode with comprehensive warnings

### LMDB Parameters:
- `map_size`: Initial database size (default: LMDB default)
- `max_map_size`: Maximum allowed size for auto-resize
- `subdir`: Whether to use subdirectory for database files
- `readonly`: Open in read-only mode

## Performance Considerations
- Use appropriate batch_size for write patterns (default: 1000)
- Consider autoflush_on_read=False for write-heavy workloads
- Use put_many() for bulk insertions - always atomic and efficient
- LMDB sorts keys lexicographically - use zero-padded strings for numeric keys
- Write buffering reduces transaction overhead for individual operations
- get_many() provides efficient bulk retrieval with optional key decoding

## Recent Enhancements
- **put_many() Method**: Atomic bulk insertions with automatic retry on map full
- **Advanced Error Handling**: Close method with strict mode and better error recovery
- **Flexible exists() Method**: Optional flush parameter for performance tuning
- **Enhanced get_many()**: Improved key decoding and error handling
- **Comprehensive Testing**: 82 tests covering all features and edge cases

## Development Status
- **Code Quality**: All tests passing (82/82)
- **Feature Complete**: Core functionality implemented and tested
- **Documentation**: Complete API documentation with examples
- **Packaging**: Ready for distribution with proper project structure

## Development Workflow
1. Make changes to source code
2. Run tests: `uv run pytest tests/` (should show 82 tests passing)
3. Run code quality checks: `uv run ruff check src/ tests/` and `uv run ruff format src/ tests/`
4. Verify specific functionality with targeted tests (e.g., `uv run pytest tests/test_basic_operations.py`)

## API Usage Examples

### Basic Operations
```python
from lmdb_object_store import LmdbObjectStore

with LmdbObjectStore("mydb", key_encoding="utf-8") as db:
    # Single operations
    db.put("key1", {"data": "value"})
    value = db.get("key1")
    
    # Bulk operations
    db.put_many({"key2": "value2", "key3": "value3"})
    found, not_found = db.get_many(["key1", "key2", "key4"])
    
    # Dict-like interface
    db["key4"] = [1, 2, 3]
    if "key4" in db:
        print(db["key4"])
```

### Advanced Configuration
```python
with LmdbObjectStore(
    "mydb", 
    batch_size=500,                    # Smaller batch size
    autoflush_on_read=False,          # Better write performance
    key_encoding="utf-8",             # String key support
    map_size=100 * 1024 * 1024,       # 100MB initial size
    max_map_size=1024 * 1024 * 1024,  # 1GB maximum size
) as db:
    # Your operations here
    pass
```

## uv Project Management Best Practices
- Use `uv sync` to ensure dependencies are up-to-date
- Always use `uv run` for script execution to maintain environment isolation
- Use `uv add` instead of manually editing pyproject.toml for new dependencies
- Leverage uv's built-in tool management (automatically handles ruff, pytest, etc.)