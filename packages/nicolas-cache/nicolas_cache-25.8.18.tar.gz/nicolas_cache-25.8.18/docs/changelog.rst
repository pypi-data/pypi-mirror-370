=========
Changelog
=========

All notable changes to Nicolas Cache will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/>`_,
and this project adheres to `Calendar Versioning <https://calver.org/>`_ (YY.MM.DD).

[Unreleased]
------------

Added
~~~~~
* Redis Sentinel backend for high availability with automatic failover
* Comprehensive test suite with 52 tests covering all backends
* Full documentation for ReadTheDocs deployment
* GitHub Actions CI/CD pipeline for automated testing and releases
* CalVer versioning system (YY.MM.DD format)
* Type hints throughout the codebase
* Support for Python 3.9, 3.10, 3.11, and 3.12

Changed
~~~~~~~
* Migrated from semantic versioning to calendar versioning
* Updated build system to use setuptools-scm for dynamic versioning
* Improved error handling and type safety

[25.07.16] - 2025-07-16
------------------------

Initial Release
~~~~~~~~~~~~~~~

Added
^^^^^
* Core ``Cache`` class with unified interface
* ``MemoryCache`` backend for in-memory caching
* ``RedisCache`` backend with TTL support
* Tag-based cache management system
* Support for complex Python objects via pickle
* Bulk operations via tags
* ``exists()`` method for checking key existence
* ``getall()`` method for retrieving all cache entries
* ``get_by_tag()`` for tag-based retrieval
* ``delete_by_tag()`` for bulk deletion

Features
^^^^^^^^
* **Multiple Backends**: Pluggable backend architecture
* **Tagging System**: Organize cache entries with multiple tags
* **TTL Support**: Automatic expiration for Redis backend
* **Type Safety**: Full type hints for better IDE support
* **Simple API**: Consistent interface across all backends

API
^^^
* ``cache.set(key, value, tags=None, ttl=None)``
* ``cache.get(key)``
* ``cache.delete(key)``
* ``cache.exists(key)``
* ``cache.getall()``
* ``cache.get_by_tag(tag)``
* ``cache.delete_by_tag(tag)``

Documentation
^^^^^^^^^^^^^
* Installation guide
* Quick start tutorial
* Usage examples
* API reference
* Backend comparison

Testing
^^^^^^^
* Unit tests for all backends
* Integration tests for Redis
* Mock tests for Redis Sentinel
* Test coverage reporting

Development
^^^^^^^^^^^
* Linting with ruff
* Type checking with mypy
* Pre-commit hooks support
* Development dependencies management

Migration Guide
---------------

From 0.x to 25.07.16
~~~~~~~~~~~~~~~~~~~~

The initial release uses calendar versioning. If you were using a development version:

1. Update your imports (no changes needed)
2. The API remains the same
3. Version format changed from ``0.1.0`` to ``YY.MM.DD``

Future versions will follow the CalVer format.

Deprecation Policy
------------------

* Features marked as deprecated will be maintained for at least 3 months
* Breaking changes will be clearly documented in the changelog
* Migration guides will be provided for breaking changes

Versioning Policy
-----------------

Nicolas Cache uses Calendar Versioning (CalVer) with the format ``YY.MM.DD``:

* **YY**: Two-digit year (e.g., 25 for 2025)
* **MM**: Two-digit month (e.g., 07 for July)
* **DD**: Two-digit day (e.g., 16)

Multiple releases on the same day append a counter: ``YY.MM.DD.N``

Development versions include commit information: ``YY.MM.DD.devN+gHASH``