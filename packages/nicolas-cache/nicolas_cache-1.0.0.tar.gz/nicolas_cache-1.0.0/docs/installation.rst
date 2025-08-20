.. highlight:: shell

============
Installation
============

Requirements
------------

* Python 3.9 or higher
* Optional: Redis server for Redis-based backends

Quick Install
-------------

To install Nicolas Cache, run this command in your terminal:

.. code-block:: console

    $ pip install nicolas

This will install the package with all core dependencies including Redis support.

From Sources
------------

The sources for Nicolas Cache can be downloaded from the `Github repo`_.

Clone the public repository:

.. code-block:: console

    $ git clone https://github.com/wickeddoc/nicolas-cache.git
    $ cd nicolas-cache
    $ pip install -e .

Development Installation
------------------------

For development with all tools:

.. code-block:: console

    $ pip install -e ".[dev]"

This includes pytest, coverage, mypy, ruff, and other development tools.

Backend Requirements
--------------------

**Memory Backend** (no additional requirements):

.. code-block:: python

    from nicolas.cache import Cache
    cache = Cache(backend="memory")

**Redis Backend** (requires Redis server):

.. code-block:: console

    # Install Redis (Ubuntu/Debian)
    $ sudo apt-get install redis-server
    
    # Or with Docker
    $ docker run -d -p 6379:6379 redis:7-alpine

**Redis Sentinel** (for high availability):

.. code-block:: python

    cache = Cache(
        backend="redis-sentinel",
        sentinels=[("localhost", 26379)],
        service_name="mymaster"
    )

Verify Installation
-------------------

.. code-block:: python

    import nicolas
    print(f"Version: {nicolas.__version__}")
    
    from nicolas.cache import Cache
    cache = Cache(backend="memory")
    cache.set("test", "value")
    assert cache.get("test") == "value"

.. _Github repo: https://github.com/wickeddoc/nicolas-cache
