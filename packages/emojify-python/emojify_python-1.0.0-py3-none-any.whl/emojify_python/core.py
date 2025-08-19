"""Core functionality for emojify-python."""

import sys
import types
import builtins
from typing import Dict, Any, Optional
from .hooks import install_emoji_hook, uninstall_emoji_hook, EmojiImporter
from .transformer import transform_source, create_emoji_namespace
from .mappings import (
    add_custom_mapping, 
    get_all_mappings, 
    get_module_for_emoji,
    reset_custom_mappings,
    update_default_mapping,
    list_mappings,
    save_custom_mappings,
    load_custom_mappings
)
from .utils import is_emoji, format_import_error

# Track if emojify is enabled
_enabled = False

# Store the original __import__ function
_original_import = builtins.__import__

def emoji_import_wrapper(name, globals=None, locals=None, fromlist=(), level=0):
    """Wrapper for __import__ that handles emoji module names."""
    # Check if the module name is an emoji
    if is_emoji(name):
        real_name = get_module_for_emoji(name)
        try:
            # Import with the real name
            module = _original_import(real_name, globals, locals, fromlist, level)
            # Store in sys.modules under both names
            sys.modules[name] = module
            return module
        except ImportError as e:
            # Provide a helpful error message
            error_msg = format_import_error(name, real_name, e)
            raise ImportError(error_msg) from e
    
    # Handle emojis in fromlist (for "from X import 🔥 as Y" syntax)
    if fromlist:
        new_fromlist = []
        emoji_aliases = {}
        
        for item in fromlist:
            if isinstance(item, str) and is_emoji(item):
                real_item = get_module_for_emoji(item)
                new_fromlist.append(real_item)
                emoji_aliases[real_item] = item
            else:
                new_fromlist.append(item)
        
        if emoji_aliases:
            fromlist = tuple(new_fromlist)
    
    # Call the original import
    return _original_import(name, globals, locals, fromlist, level)

def enable(use_hook: bool = True, use_wrapper: bool = True) -> None:
    """Enable emoji imports globally.
    
    Args:
        use_hook: Whether to use the import hook (for import statements)
        use_wrapper: Whether to wrap __import__ (for dynamic imports)
    """
    global _enabled
    
    if _enabled:
        return
    
    if use_hook:
        install_emoji_hook()
    
    if use_wrapper:
        builtins.__import__ = emoji_import_wrapper
    
    _enabled = True

def disable() -> None:
    """Disable emoji imports globally."""
    global _enabled
    
    if not _enabled:
        return
    
    uninstall_emoji_hook()
    builtins.__import__ = _original_import
    _enabled = False

def is_enabled() -> bool:
    """Check if emoji imports are currently enabled.
    
    Returns:
        True if enabled, False otherwise
    """
    return _enabled

def emojified():
    """Context manager for temporary emoji import support.
    
    Example:
        with emojified():
            import 🐼
            df = 🐼.DataFrame()
    """
    return EmojiImporter()

def exec_emoji_code(code: str, globals_dict: Optional[Dict[str, Any]] = None, 
                    locals_dict: Optional[Dict[str, Any]] = None) -> Any:
    """Execute Python code containing emoji imports and variables.
    
    Args:
        code: Python code string with emojis
        globals_dict: Global namespace (defaults to new dict)
        locals_dict: Local namespace (defaults to globals_dict)
        
    Returns:
        The result of executing the code
        
    Example:
        exec_emoji_code('''
            import 🐼
            🎲 = 🐼.DataFrame({'data': [1, 2, 3]})
            print(🎲)
        ''')
    """
    import re
    
    # Set up namespaces
    if globals_dict is None:
        globals_dict = {}
    if locals_dict is None:
        locals_dict = globals_dict
    
    # Ensure emoji imports work
    old_enabled = _enabled
    if not _enabled:
        enable()
    
    try:
        from .simple_exec import simple_exec_emoji_code
        
        # Use the simpler implementation
        result = simple_exec_emoji_code(code)
        
        # Merge with provided namespaces
        if globals_dict:
            globals_dict.update(result)
        if locals_dict and locals_dict != globals_dict:
            locals_dict.update(result)
        
        return result if not locals_dict else locals_dict
    except Exception as e:
        # If regex approach fails, try AST transformation
        try:
            transformed_code, emoji_mappings = transform_source(code)
            exec(transformed_code, globals_dict, locals_dict)
            
            # Create emoji references
            for emoji, transformed_name in emoji_mappings.items():
                if transformed_name in locals_dict:
                    locals_dict[emoji] = locals_dict[transformed_name]
                elif transformed_name in globals_dict:
                    globals_dict[emoji] = globals_dict[transformed_name]
            
            return locals_dict
        except:
            raise e
    finally:
        # Restore previous state
        if not old_enabled:
            disable()

def compile_emoji_code(source: str, filename: str = '<emoji>', mode: str = 'exec') -> types.CodeType:
    """Compile Python code containing emoji imports and variables.
    
    Args:
        source: Python source code with emojis
        filename: Filename for error messages
        mode: Compilation mode ('exec', 'eval', or 'single')
        
    Returns:
        Compiled code object
    """
    # Transform the source code
    transformed_source, _ = transform_source(source)
    
    # Compile the transformed code
    return compile(transformed_source, filename, mode)

def add_mapping(emoji: str, module_name: str, persist: bool = False) -> None:
    """Add a custom emoji to module mapping.
    
    Args:
        emoji: The emoji character to use
        module_name: The actual module name
        persist: Whether to save as a default mapping
    """
    if persist:
        update_default_mapping(emoji, module_name)
    else:
        add_custom_mapping(emoji, module_name)

def view_mappings(category: Optional[str] = None) -> Dict[str, str]:
    """View current emoji mappings.
    
    Args:
        category: Optional category filter ('data', 'web', 'util', etc.)
        
    Returns:
        Dictionary of emoji to module mappings
    """
    all_mappings = get_all_mappings()
    
    if category:
        # Filter by category (simplified category detection)
        category_keywords = {
            'data': ['pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn'],
            'web': ['flask', 'django', 'fastapi', 'requests'],
            'ml': ['torch', 'tensorflow', 'sklearn', 'keras'],
            'util': ['datetime', 'pathlib', 'json', 'random'],
        }
        
        if category.lower() in category_keywords:
            keywords = category_keywords[category.lower()]
            filtered = {k: v for k, v in all_mappings.items() 
                       if any(keyword in v.lower() for keyword in keywords)}
            return filtered
    
    return all_mappings

# Convenience function aliases
emojify = enable
deemojify = disable

# Decorator for functions
def emojify_function(func):
    """Decorator to enable emoji imports within a function.
    
    Example:
        @emojify_function
        def my_function():
            import 🐼
            return 🐼.DataFrame()
    """
    def wrapper(*args, **kwargs):
        with emojified():
            return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper