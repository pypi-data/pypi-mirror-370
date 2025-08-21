"""Tests meta information about the package."""

import importlib.metadata

import pegasustools as pt


def test_version() -> None:
    """Verify that pt.__version__ is correct."""
    assert importlib.metadata.version("pegasustools") == pt.__version__
