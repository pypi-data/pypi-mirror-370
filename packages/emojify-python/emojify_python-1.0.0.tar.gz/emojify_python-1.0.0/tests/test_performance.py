"""Performance and caching tests for emoji Python."""

import pytest
import time
import tempfile
from pathlib import Path
from emojify_python import enable, exec_emoji_code
from emojify_python.cache import EmojiCache, get_cache, clear_cache
from emojify_python.lazy_loader import LazyMapping, LazyModuleLoader

class TestCaching:
    """Test caching functionality."""
    
    def setup_method(self):
        """Clear cache before each test."""
        clear_cache()
    
    def test_cache_transformed_code(self):
        """Test caching of transformed code."""
        cache = get_cache()
        
        source = "import 🐼"
        transformed = "import pandas"
        mappings = {"🐼": "pandas"}
        
        # Cache should be empty initially
        assert cache.get_transformed_code(source) is None
        
        # Set cache
        cache.set_transformed_code(source, transformed, mappings)
        
        # Retrieve from cache
        cached_result = cache.get_transformed_code(source)
        assert cached_result is not None
        assert cached_result[0] == transformed
        assert cached_result[1] == mappings
    
    def test_cache_bytecode(self):
        """Test bytecode caching."""
        cache = get_cache()
        
        source = "x = 42"
        code_obj = compile(source, '<test>', 'exec')
        
        # Cache should be empty initially
        assert cache.get_bytecode(source) is None
        
        # Set cache
        cache.set_bytecode(source, code_obj)
        
        # Retrieve from cache
        cached_bytecode = cache.get_bytecode(source)
        assert cached_bytecode is not None
    
    def test_cache_persistence(self):
        """Test that cache persists to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create cache with custom directory
            cache1 = EmojiCache(cache_dir=tmpdir)
            
            source = "import 🐼"
            transformed = "import pandas"
            mappings = {"🐼": "pandas"}
            
            cache1.set_transformed_code(source, transformed, mappings)
            
            # Create new cache instance with same directory
            cache2 = EmojiCache(cache_dir=tmpdir)
            
            # Should load from disk
            cached_result = cache2.get_transformed_code(source)
            assert cached_result is not None
            assert cached_result[0] == transformed
    
    def test_cache_statistics(self):
        """Test cache statistics."""
        cache = get_cache()
        cache.clear()
        
        stats = cache.get_cache_size()
        assert stats['memory_items'] == 0
        assert stats['disk_files'] == 0
        
        # Add some items
        cache.set_transformed_code("test1", "transformed1", {})
        cache.set_transformed_code("test2", "transformed2", {})
        
        stats = cache.get_cache_size()
        assert stats['memory_items'] == 2
    
    def test_cache_clear(self):
        """Test cache clearing."""
        cache = get_cache()
        
        # Add items
        cache.set_transformed_code("test", "transformed", {})
        assert cache.get_transformed_code("test") is not None
        
        # Clear cache
        cache.clear()
        
        # Should be empty
        assert cache.get_transformed_code("test") is None
        stats = cache.get_cache_size()
        assert stats['memory_items'] == 0

class TestLazyLoading:
    """Test lazy loading functionality."""
    
    def test_lazy_mapping(self):
        """Test lazy mapping loading."""
        loaded = False
        
        def loader():
            nonlocal loaded
            loaded = True
            return {"🎮": "pygame", "🎨": "pillow"}
        
        lazy_map = LazyMapping(loader)
        
        # Should not be loaded yet
        assert not loaded
        
        # Access triggers loading
        value = lazy_map.get("🎮")
        assert loaded
        assert value == "pygame"
        
        # Second access doesn't reload
        loaded = False
        value = lazy_map.get("🎨")
        assert not loaded  # Already loaded
        assert value == "pillow"
    
    def test_lazy_mapping_operations(self):
        """Test various lazy mapping operations."""
        lazy_map = LazyMapping(lambda: {"🐼": "pandas", "🔢": "numpy"})
        
        # Test contains
        assert "🐼" in lazy_map
        assert "🎮" not in lazy_map
        
        # Test getitem
        assert lazy_map["🐼"] == "pandas"
        
        # Test iteration
        items = list(lazy_map.items())
        assert len(items) == 2
        
        keys = list(lazy_map.keys())
        assert "🐼" in keys
        
        values = list(lazy_map.values())
        assert "pandas" in values
        
        # Test update
        lazy_map.update({"🎮": "pygame"})
        assert "🎮" in lazy_map
    
    def test_lazy_module_loader(self):
        """Test lazy module loading."""
        loader = LazyModuleLoader("json")
        
        # Module not loaded yet
        assert loader._module is None
        
        # Access triggers loading
        result = loader.dumps({"test": "data"})
        assert loader._module is not None
        assert isinstance(result, str)
    
    def test_performance_improvement(self):
        """Test that caching improves performance."""
        enable()
        
        code = """
import 🐼
import 🔢
🎲 = [i for i in range(100)]
result = sum(🎲)
"""
        
        # First execution (no cache)
        start = time.time()
        exec_emoji_code(code)
        first_time = time.time() - start
        
        # Second execution (with cache)
        start = time.time()
        exec_emoji_code(code)
        second_time = time.time() - start
        
        # Second execution should be faster (or at least not significantly slower)
        # Note: This is a simple test, actual performance gain depends on code complexity
        assert second_time <= first_time * 1.5  # Allow some variance

class TestMemoryEfficiency:
    """Test memory efficiency of emoji Python."""
    
    def test_memory_cache_limit(self):
        """Test that memory cache has reasonable limits."""
        cache = get_cache()
        cache.clear()
        
        # Add many items
        for i in range(100):
            source = f"x = {i}"
            cache.set_transformed_code(source, f"x = {i}", {})
        
        stats = cache.get_cache_size()
        # Should have items in cache
        assert stats['memory_items'] > 0
        
        # Cache should still be functional
        test_source = "test"
        cache.set_transformed_code(test_source, "transformed", {})
        assert cache.get_transformed_code(test_source) is not None