Nicolas Cache Documentation
============================

.. image:: https://img.shields.io/pypi/v/nicolas.svg
   :target: https://pypi.python.org/pypi/nicolas
   :alt: PyPI Version

.. image:: https://readthedocs.org/projects/nicolas-cache/badge/?version=latest
   :target: https://nicolas-cache.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

Nicolas Cache is a powerful Python caching library with multi-backend support and advanced tagging capabilities. It provides a unified interface for different cache backends including in-memory, Redis, and Redis Sentinel with automatic failover.

Key Features
------------

* **Multiple Backends**: In-memory, Redis, and Redis Sentinel support
* **Tag-Based Management**: Organize cache entries with tags for bulk operations
* **TTL Support**: Time-to-live for automatic cache expiration (Redis backends)
* **Automatic Failover**: Redis Sentinel backend for high availability
* **Type Safety**: Full type hints for better IDE support
* **Simple API**: Consistent interface across all backends
* **Extensible**: Easy to add new cache backends

Quick Example
-------------

.. code-block:: python

   from nicolas.cache import Cache

   # Create a cache instance
   cache = Cache(backend="memory")

   # Store data with tags
   cache.set("user:1", {"name": "Alice", "email": "alice@example.com"}, 
             tags=["users", "active"])

   # Retrieve data
   user = cache.get("user:1")

   # Get all entries with a specific tag
   active_users = cache.get_by_tag("active")

   # Delete entries by tag
   cache.delete_by_tag("inactive")

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   usage

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   backends
   tagging
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api

.. toctree::
   :maxdepth: 2
   :caption: Development

   contributing
   changelog
   authors

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
