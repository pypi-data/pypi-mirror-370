"""Caching system for emoji transformations and bytecode."""

import os
import pickle
import hashlib
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import marshal
import types

class EmojiCache:
    """Cache manager for emoji Python transformations."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize cache with optional custom directory."""
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path(tempfile.gettempdir()) / '.emoji_python_cache'
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, Any] = {}
        self._ast_cache: Dict[str, Any] = {}
        
    def _get_cache_key(self, code: str) -> str:
        """Generate cache key from code content."""
        return hashlib.sha256(code.encode()).hexdigest()[:16]
    
    def get_transformed_code(self, source: str) -> Optional[Tuple[str, Dict]]:
        """Get cached transformed code if available."""
        key = self._get_cache_key(source)
        
        # Check memory cache first
        if key in self._memory_cache:
            return self._memory_cache[key]
        
        # Check disk cache
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    self._memory_cache[key] = data
                    return data
            except:
                pass
        
        return None
    
    def set_transformed_code(self, source: str, transformed: str, mappings: Dict):
        """Cache transformed code."""
        key = self._get_cache_key(source)
        data = (transformed, mappings)
        
        # Store in memory
        self._memory_cache[key] = data
        
        # Store on disk
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except:
            pass
    
    def get_bytecode(self, source: str, filename: str = '<emoji>') -> Optional[types.CodeType]:
        """Get cached bytecode if available."""
        key = self._get_cache_key(source)
        bytecode_file = self.cache_dir / f"{key}.pyc"
        
        if bytecode_file.exists():
            try:
                with open(bytecode_file, 'rb') as f:
                    return marshal.load(f)
            except:
                pass
        
        return None
    
    def set_bytecode(self, source: str, code_obj: types.CodeType):
        """Cache compiled bytecode."""
        key = self._get_cache_key(source)
        bytecode_file = self.cache_dir / f"{key}.pyc"
        
        try:
            with open(bytecode_file, 'wb') as f:
                marshal.dump(code_obj, f)
        except:
            pass
    
    def clear(self):
        """Clear all caches."""
        self._memory_cache.clear()
        self._ast_cache.clear()
        
        # Clear disk cache
        for file in self.cache_dir.glob('*'):
            try:
                file.unlink()
            except:
                pass
    
    def get_cache_size(self) -> Dict[str, int]:
        """Get cache statistics."""
        disk_files = list(self.cache_dir.glob('*'))
        disk_size = sum(f.stat().st_size for f in disk_files)
        
        return {
            'memory_items': len(self._memory_cache),
            'disk_files': len(disk_files),
            'disk_size_bytes': disk_size,
            'ast_items': len(self._ast_cache)
        }

# Global cache instance
_global_cache = None

def get_cache() -> EmojiCache:
    """Get or create global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = EmojiCache()
    return _global_cache

def clear_cache():
    """Clear the global cache."""
    cache = get_cache()
    cache.clear()