"""
Datalint Core - Rust-powered backend for dataset inspection and quality control.

This module provides high-performance functions for dataset processing,
implemented in Rust with Python bindings via PyO3.
"""

from __future__ import annotations

from ._datalint_core import (
    DatasetTask,
    DatasetType,
    create_cache,
    __version__,
)

__all__ = [
    "DatasetTask",
    "DatasetType",
    "create_cache",
    "__version__",
]
