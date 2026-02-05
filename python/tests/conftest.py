"""Pytest configuration and shared fixtures for marketsymbol tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_exchange() -> str:
    """Provide a sample exchange code for testing."""
    return "XJPX"


@pytest.fixture
def sample_code() -> str:
    """Provide a sample security code for testing."""
    return "7203"
