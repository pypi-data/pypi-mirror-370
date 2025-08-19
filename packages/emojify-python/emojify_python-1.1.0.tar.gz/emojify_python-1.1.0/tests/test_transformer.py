"""Test source code transformation functionality."""

import pytest
from emojify_python import exec_emoji_code, compile_emoji_code
from emojify_python.transformer import transform_source
from emojify_python.utils import is_emoji

class TestTransformer:
    """Test source code transformation."""
    
    def test_transform_import(self):
        """Test transforming import statements."""
        source = "import 🐼"
        transformed, mappings = transform_source(source)
        assert '🐼' in mappings
        assert 'pandas' in transformed or mappings['🐼'] in transformed
    
    def test_transform_import_alias(self):
        """Test transforming import with alias."""
        source = "import pandas as 🐼"
        transformed, mappings = transform_source(source)
        assert '🐼' in mappings
    
    def test_transform_from_import(self):
        """Test transforming from...import statements."""
        source = "from 🐼 import DataFrame"
        transformed, mappings = transform_source(source)
        assert 'pandas' in transformed
    
    def test_transform_variable(self):
        """Test transforming emoji variables."""
        source = "🎲 = 42"
        transformed, mappings = transform_source(source)
        assert '🎲' in mappings
        assert mappings['🎲'] in transformed
    
    def test_transform_function(self):
        """Test transforming emoji function names."""
        source = """
def 🚀(x):
    return x * 2
"""
        transformed, mappings = transform_source(source)
        assert '🚀' in mappings
        assert 'def' in transformed
    
    def test_transform_class(self):
        """Test transforming emoji class names."""
        source = """
class 🏠:
    def __init__(self):
        self.🔑 = "secret"
"""
        transformed, mappings = transform_source(source)
        assert '🏠' in mappings
        assert '🔑' in mappings
    
    def test_exec_emoji_code(self):
        """Test executing code with emojis."""
        code = """
import json as 📦
🎲 = {"test": "data"}
result = 📦.dumps(🎲)
"""
        namespace = exec_emoji_code(code)
        assert 'result' in namespace
        assert isinstance(namespace['result'], str)
        assert '🎲' in namespace or any('emoji' in k for k in namespace.keys())
    
    def test_compile_emoji_code(self):
        """Test compiling code with emojis."""
        code = "🎲 = 42"
        try:
            compiled = compile_emoji_code(code)
            assert compiled is not None
        except Exception as e:
            pytest.fail(f"Failed to compile emoji code: {e}")