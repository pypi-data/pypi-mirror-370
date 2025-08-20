# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Nicolas-cache is a Python caching library with tagging support. It provides a unified interface for different cache backends (currently in-memory and Redis) with a sophisticated tagging system for organizing and managing cached data.

## Architecture

The library follows an abstract factory pattern:
- `CacheBackend` (abstract base class in `src/nicolas/__init__.py`)
- `MemoryCache` (in-memory implementation in `src/nicolas/memory.py`)
- `RedisCache` (Redis-based implementation in `src/nicolas/redis.py`)
- `RedisSentinelCache` (Redis Sentinel implementation in `src/nicolas/sentinel.py`)
- `Cache` (unified interface in `src/nicolas/cache.py`)

Key features:
- Multiple tags per cache entry
- Bulk operations by tag
- TTL support (Redis and Sentinel backends)
- Automatic failover support (Sentinel backend)
- Extensible design for adding new backends

## Development Commands

### Testing
```bash
# Run tests
pytest

# Run tests with coverage
coverage run -m pytest
coverage report
```

### Type Checking and Linting
```bash
# Type checking (strict mode enabled)
mypy .

# Linting with ruff
ruff check .
ruff format .
```

### Documentation
```bash
# Build documentation
cd docs && make html

# Clean documentation build
cd docs && make clean
```

### Package Management
```bash
# Install in development mode with all dependencies
pip install -e ".[dev]"

# Build the package
python -m build
```

## Key Files and Entry Points

- Main API: `Cache` class in `src/nicolas/cache.py`
- CLI interface: `src/nicolas/cli.py` (uses Typer framework)
- Package configuration: `pyproject.toml`
- Documentation: Sphinx-based in `docs/` directory

## Development Notes

- Python 3.9+ required
- Uses modern `pyproject.toml` for package configuration
- Type hints are used throughout - maintain type safety
- Google-style docstrings for documentation
- Redis is an optional dependency - handle ImportError gracefully