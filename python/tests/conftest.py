"""Pytest configuration and shared fixtures for marketsymbol tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_exchange() -> str:
    """Provide a sample exchange code for testing.

    Returns:
        XJPX: ISO 10383 MIC code for Japan Exchange Group
    """
    return "XJPX"


@pytest.fixture
def sample_code() -> str:
    """Provide a sample security code for testing.

    Returns:
        7203: Toyota Motor Corporation's security code on Tokyo Stock Exchange
    """
    return "7203"
