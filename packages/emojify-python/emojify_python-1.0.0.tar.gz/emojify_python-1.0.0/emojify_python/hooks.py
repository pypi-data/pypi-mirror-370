"""Import hooks for emoji-based imports."""

import sys
import importlib
import importlib.abc
import importlib.machinery
from typing import Optional, Sequence, Any
from .mappings import get_module_for_emoji
from .utils import is_emoji

class EmojiImportFinder(importlib.abc.MetaPathFinder):
    """Meta path finder that handles emoji-based imports."""
    
    def find_spec(self, fullname: str, path: Optional[Sequence[str]] = None, 
                  target: Optional[Any] = None) -> Optional[importlib.machinery.ModuleSpec]:
        """Find module spec for emoji imports.
        
        Args:
            fullname: The fully qualified module name (might be an emoji)
            path: Optional path for sub-packages
            target: Optional target module
            
        Returns:
            ModuleSpec if emoji maps to a real module, None otherwise
        """
        # Check if the module name is an emoji
        if is_emoji(fullname):
            # Get the real module name
            real_module_name = get_module_for_emoji(fullname)
            
            # If we got a different name, try to find that module
            if real_module_name != fullname:
                try:
                    # Use the default finder to locate the real module
                    for finder in sys.meta_path:
                        if finder is not self and hasattr(finder, 'find_spec'):
                            spec = finder.find_spec(real_module_name, path, target)
                            if spec:
                                # Create a new spec with the emoji name but pointing to the real module
                                # This allows the emoji to be used as the module name in the namespace
                                return importlib.machinery.ModuleSpec(
                                    fullname,  # Keep the emoji name
                                    spec.loader,
                                    origin=spec.origin,
                                    is_package=spec.submodule_search_locations is not None
                                )
                except Exception:
                    pass
        
        # Check for emojis in dotted imports (e.g., "🐼.DataFrame")
        elif '.' in fullname:
            parts = fullname.split('.')
            if any(is_emoji(part) for part in parts):
                # Transform emoji parts to real module names
                real_parts = [get_module_for_emoji(part) if is_emoji(part) else part for part in parts]
                real_module_name = '.'.join(real_parts)
                
                if real_module_name != fullname:
                    try:
                        for finder in sys.meta_path:
                            if finder is not self and hasattr(finder, 'find_spec'):
                                spec = finder.find_spec(real_module_name, path, target)
                                if spec:
                                    return importlib.machinery.ModuleSpec(
                                        fullname,
                                        spec.loader,
                                        origin=spec.origin,
                                        is_package=spec.submodule_search_locations is not None
                                    )
                    except Exception:
                        pass
        
        return None

class EmojiImportLoader(importlib.abc.Loader):
    """Loader for emoji-based imports."""
    
    def __init__(self, real_module_name: str):
        """Initialize the loader.
        
        Args:
            real_module_name: The actual module name to load
        """
        self.real_module_name = real_module_name
    
    def load_module(self, fullname: str) -> Any:
        """Load the module.
        
        Args:
            fullname: The module name (might be an emoji)
            
        Returns:
            The loaded module
        """
        # If the real module is already loaded, return it
        if self.real_module_name in sys.modules:
            module = sys.modules[self.real_module_name]
        else:
            # Import the real module
            module = importlib.import_module(self.real_module_name)
        
        # Also register it under the emoji name
        sys.modules[fullname] = module
        return module
    
    def exec_module(self, module: Any) -> None:
        """Execute the module (required for Python 3.4+).
        
        Args:
            module: The module to execute
        """
        pass  # The module is already executed when imported

# Global reference to our finder
_emoji_finder = None

def install_emoji_hook() -> None:
    """Install the emoji import hook into sys.meta_path."""
    global _emoji_finder
    
    # Only install once
    if _emoji_finder is None:
        _emoji_finder = EmojiImportFinder()
        # Insert at the beginning to take precedence
        sys.meta_path.insert(0, _emoji_finder)

def uninstall_emoji_hook() -> None:
    """Remove the emoji import hook from sys.meta_path."""
    global _emoji_finder
    
    if _emoji_finder is not None:
        try:
            sys.meta_path.remove(_emoji_finder)
        except ValueError:
            pass  # Already removed
        _emoji_finder = None

def is_emoji_hook_installed() -> bool:
    """Check if the emoji import hook is currently installed.
    
    Returns:
        True if installed, False otherwise
    """
    return _emoji_finder is not None and _emoji_finder in sys.meta_path

class EmojiImporter:
    """Context manager for emoji imports."""
    
    def __enter__(self):
        """Enter the context and enable emoji imports."""
        install_emoji_hook()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and optionally disable emoji imports."""
        # Keep the hook installed by default
        pass

def emoji_import(emoji: str, name: Optional[str] = None) -> Any:
    """Programmatically import a module using an emoji.
    
    Args:
        emoji: The emoji representing the module
        name: Optional attribute to import from the module
        
    Returns:
        The imported module or attribute
        
    Example:
        df = emoji_import('🐼', 'DataFrame')
        # Equivalent to: from pandas import DataFrame as df
    """
    # Get the real module name
    real_module_name = get_module_for_emoji(emoji)
    
    # Import the module
    module = importlib.import_module(real_module_name)
    
    # If a specific name is requested, get that attribute
    if name:
        return getattr(module, name)
    
    return module