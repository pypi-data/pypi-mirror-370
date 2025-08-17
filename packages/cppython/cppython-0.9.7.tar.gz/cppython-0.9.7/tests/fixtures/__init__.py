"""Fixtures for tests.

`pytest_plugins` is the preferred way to load fixtures, to prevent the overhead of a large root conftest file.
The plugins must be defined at the test module's global scope and not in non-root conftest files.

ex.
```
pytest_plugins = ['fixtures.fixture_name']
```
"""
