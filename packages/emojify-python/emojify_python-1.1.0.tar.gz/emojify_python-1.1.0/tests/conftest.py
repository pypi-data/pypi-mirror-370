"""pytest configuration for emojify_python tests."""

import sys
import pytest
from emojify_python import enable, disable

def pytest_configure(config):
    """Configure pytest with emoji support."""
    # Add markers
    config.addinivalue_line(
        "markers",
        "emoji: mark test to run with emoji Python enabled"
    )

@pytest.fixture(autouse=True)
def enable_emoji_for_tests():
    """Automatically enable emoji support for all tests."""
    # Enable emoji import hooks before tests
    enable()
    yield
    # Keep enabled (no disable after tests)

@pytest.fixture
def exec_emoji():
    """Fixture to execute emoji code."""
    from emojify_python import exec_emoji_code
    return exec_emoji_code