"""Lazy loading system for emoji mappings."""

from typing import Dict, Optional, Callable, Any
import importlib

class LazyMapping:
    """Lazy-loaded mapping that only loads when accessed."""
    
    def __init__(self, loader: Callable[[], Dict[str, str]]):
        self._loader = loader
        self._loaded = False
        self._data: Optional[Dict[str, str]] = None
    
    def _ensure_loaded(self):
        """Load data if not already loaded."""
        if not self._loaded:
            self._data = self._loader()
            self._loaded = True
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value with lazy loading."""
        self._ensure_loaded()
        return self._data.get(key, default)
    
    def __getitem__(self, key: str) -> str:
        """Get item with lazy loading."""
        self._ensure_loaded()
        return self._data[key]
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists with lazy loading."""
        self._ensure_loaded()
        return key in self._data
    
    def items(self):
        """Get items with lazy loading."""
        self._ensure_loaded()
        return self._data.items()
    
    def keys(self):
        """Get keys with lazy loading."""
        self._ensure_loaded()
        return self._data.keys()
    
    def values(self):
        """Get values with lazy loading."""
        self._ensure_loaded()
        return self._data.values()
    
    def update(self, other: Dict[str, str]):
        """Update mappings."""
        self._ensure_loaded()
        self._data.update(other)

class LazyModuleLoader:
    """Lazy module loader for emoji imports."""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self._module = None
    
    def __getattr__(self, name: str):
        """Lazy load module on attribute access."""
        if self._module is None:
            self._module = importlib.import_module(self.module_name)
        return getattr(self._module, name)
    
    def __call__(self, *args, **kwargs):
        """Support callable modules."""
        if self._module is None:
            self._module = importlib.import_module(self.module_name)
        return self._module(*args, **kwargs)

def create_lazy_mapping(category: str) -> LazyMapping:
    """Create a lazy mapping for a specific category."""
    
    def load_category_mappings():
        """Load mappings for the category."""
        from .mappings import DEFAULT_EMOJI_MAPPINGS
        
        category_mappings = {
            'data': {k: v for k, v in DEFAULT_EMOJI_MAPPINGS.items() 
                    if v in ['pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'sklearn']},
            'web': {k: v for k, v in DEFAULT_EMOJI_MAPPINGS.items()
                   if v in ['flask', 'django', 'fastapi', 'requests', 'aiohttp']},
            'util': {k: v for k, v in DEFAULT_EMOJI_MAPPINGS.items()
                    if v in ['datetime', 'pathlib', 'json', 'random', 'hashlib', 're']},
            'all': DEFAULT_EMOJI_MAPPINGS
        }
        
        return category_mappings.get(category, {})
    
    return LazyMapping(load_category_mappings)