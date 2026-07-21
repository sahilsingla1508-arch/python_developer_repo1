"""
tests/conftest.py — Shared pytest fixtures for PyChronicle.

Fixtures
--------
sample_script_path
    Absolute path to examples/sample_script.py.  The sample script is a
    deterministic program whose variable names and line numbers are stable,
    making it suitable for assertion-level integration tests.

tmp_db_path
    Yields a temporary SQLite database path inside pytest's tmp_path
    directory.  Each test that uses this fixture gets an isolated database
    so tests do not interfere with each other.
"""

import os
import pytest


@pytest.fixture
def sample_script_path() -> str:
    """Return the absolute path to the shared deterministic sample script."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(repo_root, "examples", "sample_script.py")
    assert os.path.isfile(path), f"Sample script not found: {path}"
    return path


@pytest.fixture
def tmp_db_path(tmp_path) -> str:
    """Return a path to a fresh, isolated SQLite database for the test."""
    return str(tmp_path / "test_chronicle.db")
