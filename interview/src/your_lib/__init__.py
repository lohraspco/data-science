# src/your_lib/__init__.py
from .core import Foo, Bar        # curated imports (public API)
from ._version import __version__ # single source of truth

__all__ = ["Foo", "Bar", "__version__"]