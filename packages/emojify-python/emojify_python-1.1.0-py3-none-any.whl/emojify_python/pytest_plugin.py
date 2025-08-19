"""pytest plugin for emoji Python testing."""

import pytest
import sys
from typing import Any, Dict, List
from .core import enable, exec_emoji_code
from .enhanced import EmojiAssert

# Plugin name for pytest
pytest_plugins = ['emojify_python.pytest_plugin']

def pytest_configure(config):
    """Configure pytest with emoji support."""
    config.addinivalue_line(
        "markers",
        "emoji: mark test to run with emoji Python enabled"
    )
    config.addinivalue_line(
        "markers",
        "emoji_only: mark test to only run with emoji support"
    )
    
    # Add emoji options
    config.option.emoji = getattr(config.option, 'emoji', False)
    
    # Register emoji assert helpers
    pytest.emoji_assert = EmojiAssert()

def pytest_addoption(parser):
    """Add emoji-related command line options."""
    group = parser.getgroup('emoji')
    group.addoption(
        '--emoji',
        action='store_true',
        default=False,
        help='Enable emoji Python for all tests'
    )
    group.addoption(
        '--emoji-only',
        action='store_true',
        default=False,
        help='Only run tests marked with @pytest.mark.emoji'
    )
    group.addoption(
        '--emoji-verbose',
        action='store_true',
        default=False,
        help='Show emoji transformations during tests'
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection based on emoji markers."""
    if config.getoption("--emoji-only"):
        # Only run emoji tests
        skip_non_emoji = pytest.mark.skip(reason="need --emoji-only option to run")
        for item in items:
            if "emoji" not in item.keywords:
                item.add_marker(skip_non_emoji)
    
    if config.getoption("--emoji"):
        # Enable emoji for all tests
        enable()

class EmojiTestFixtures:
    """Emoji test fixtures."""
    
    @pytest.fixture
    def emoji_enabled(self):
        """Enable emoji imports for a test."""
        enable()
        yield
        # Emoji stays enabled (no disable)
    
    @pytest.fixture
    def emoji_exec(self):
        """Fixture to execute emoji code."""
        def executor(code: str) -> Dict[str, Any]:
            return exec_emoji_code(code)
        return executor
    
    @pytest.fixture
    def emoji_assert(self):
        """Emoji assertion helpers."""
        return EmojiAssert()
    
    @pytest.fixture
    def pandas_emoji(self):
        """Pandas fixture with emoji name."""
        try:
            import pandas
            return pandas
        except ImportError:
            pytest.skip("pandas not installed")
    
    @pytest.fixture
    def numpy_emoji(self):
        """NumPy fixture with emoji name."""
        try:
            import numpy
            return numpy
        except ImportError:
            pytest.skip("numpy not installed")
    
    @pytest.fixture
    def json_emoji(self):
        """JSON fixture with emoji name."""
        import json
        return json
    
    @pytest.fixture
    def random_emoji(self):
        """Random fixture with emoji name."""
        import random
        return random

# Register fixtures
emoji_fixtures = EmojiTestFixtures()

@pytest.fixture
def emoji_enabled():
    """Enable emoji imports for a test."""
    return emoji_fixtures.emoji_enabled()

@pytest.fixture
def emoji_exec():
    """Execute emoji code."""
    return emoji_fixtures.emoji_exec()

@pytest.fixture
def emoji_assert():
    """Emoji assertions."""
    return emoji_fixtures.emoji_assert()

# Emoji test decorators
def emoji_test(func):
    """Decorator to mark a test as using emoji Python."""
    return pytest.mark.emoji(func)

def emoji_only(func):
    """Decorator to mark a test as emoji-only."""
    return pytest.mark.emoji_only(func)

def emoji_parametrize(*args, **kwargs):
    """Parametrize with emoji support."""
    def decorator(func):
        # Enable emoji for the test
        func = emoji_test(func)
        # Apply parametrize
        func = pytest.mark.parametrize(*args, **kwargs)(func)
        return func
    return decorator

# Custom emoji assertions
class EmojiAssertions:
    """Custom emoji assertion methods for pytest."""
    
    @staticmethod
    def assert_emoji_equal(actual, expected, message=""):
        """Assert equality with emoji output."""
        assert actual == expected, f"❌ {actual} ≠ {expected}: {message}"
    
    @staticmethod
    def assert_emoji_true(condition, message=""):
        """Assert true with emoji output."""
        assert condition, f"❌ Assertion failed: {message}"
    
    @staticmethod
    def assert_emoji_false(condition, message=""):
        """Assert false with emoji output."""
        assert not condition, f"❌ Should be false: {message}"
    
    @staticmethod
    def assert_emoji_in(item, container, message=""):
        """Assert membership with emoji output."""
        assert item in container, f"❌ {item} not in {container}: {message}"
    
    @staticmethod
    def assert_emoji_raises(exception, func, *args, **kwargs):
        """Assert exception with emoji output."""
        with pytest.raises(exception):
            func(*args, **kwargs)
    
    @staticmethod
    def assert_emoji_type(obj, expected_type, message=""):
        """Assert type with emoji output."""
        assert isinstance(obj, expected_type), f"❌ {obj} is not {expected_type}: {message}"

# Install assertions as pytest helpers
pytest.emoji = EmojiAssertions()

# Emoji test report symbols
def pytest_report_teststatus(report, config):
    """Customize test status symbols with emojis."""
    if config.getoption("--emoji") or config.getoption("--emoji-verbose"):
        if report.when == 'call':
            if report.passed:
                return "passed", "✅", "PASSED"
            elif report.failed:
                return "failed", "❌", "FAILED"
            elif report.skipped:
                return "skipped", "⏭️", "SKIPPED"
    return None

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add emoji summary to test results."""
    if config.getoption("--emoji") or config.getoption("--emoji-verbose"):
        terminalreporter.write_sep("=", "🎉 Emoji Test Summary 🎉")
        
        stats = terminalreporter.stats
        
        passed = len(stats.get('passed', []))
        failed = len(stats.get('failed', []))
        skipped = len(stats.get('skipped', []))
        
        if passed:
            terminalreporter.write_line(f"✅ Passed: {passed}")
        if failed:
            terminalreporter.write_line(f"❌ Failed: {failed}")
        if skipped:
            terminalreporter.write_line(f"⏭️ Skipped: {skipped}")
        
        if failed == 0 and passed > 0:
            terminalreporter.write_line("\n🎊 All tests passed! Great job! 🎊")
        elif failed > 0:
            terminalreporter.write_line("\n💪 Keep going! You can fix these! 💪")

# Example emoji test class
class TestEmojiExample:
    """Example test class using emoji features."""
    
    @emoji_test
    def test_emoji_import(self, emoji_exec):
        """Test emoji imports."""
        result = emoji_exec("""
import 🐼
import 📦
assert 🐼.__name__ == 'pandas'
assert 📦.__name__ == 'json'
""")
    
    @emoji_parametrize("emoji,module", [
        ("🐼", "pandas"),
        ("📦", "json"),
        ("🎲", "random"),
    ])
    def test_emoji_mapping(self, emoji, module, emoji_exec):
        """Test emoji module mappings."""
        result = emoji_exec(f"""
import {emoji}
assert {emoji}.__name__ == '{module}'
""")
    
    @emoji_only
    def test_emoji_only_feature(self):
        """This test only runs with --emoji-only flag."""
        from emojify_python import view_mappings
        mappings = view_mappings()
        assert len(mappings) > 0