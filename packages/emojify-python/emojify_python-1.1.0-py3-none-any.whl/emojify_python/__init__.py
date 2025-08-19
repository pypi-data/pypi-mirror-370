"""
Emojify Python - Import Python modules using emojis 🐍

A fun and expressive way to write Python code using emojis for imports and variables.

Basic Usage:
    >>> from emojify_python import enable
    >>> enable()
    >>> import 🐼  # Imports pandas
    >>> 🎲 = 🐼.DataFrame({'data': [1, 2, 3]})

Context Manager:
    >>> from emojify_python import emojified
    >>> with emojified():
    ...     import 🐼
    ...     df = 🐼.DataFrame()

Custom Mappings:
    >>> from emojify_python import add_mapping
    >>> add_mapping('🎮', 'pygame')
    >>> import 🎮  # Imports pygame
"""

__version__ = '1.1.0'
__author__ = 'Emojify Python Contributors'
__license__ = 'MIT'

# Import main functionality
from .core import (
    enable,
    disable,
    is_enabled,
    emojified,
    emojify,
    deemojify,
    exec_emoji_code,
    compile_emoji_code,
    add_mapping,
    view_mappings,
    emojify_function,
)

from .mappings import (
    add_custom_mapping,
    remove_custom_mapping,
    update_default_mapping,
    remove_default_mapping,
    get_module_for_emoji,
    get_emoji_for_module,
    get_all_mappings,
    reset_custom_mappings,
    list_mappings,
    save_custom_mappings,
    load_custom_mappings,
    search_mapping,
    load_extended_mappings,
    load_popular_set,
    get_available_sets,
    DEFAULT_MAPPINGS,
)

from .hooks import (
    emoji_import,
    install_emoji_hook,
    uninstall_emoji_hook,
    is_emoji_hook_installed,
)

from .utils import (
    is_emoji,
    contains_emoji,
    extract_emojis,
)

# Import enhanced features
try:
    from .operators import (
        EMOJI_OPERATORS,
        EMOJI_KEYWORDS,
        EMOJI_BUILTINS,
        create_emoji_operator,
        transform_emoji_operators,
        transform_emoji_keywords,
        create_emoji_math,
    )
except ImportError:
    pass

# Decorators can't be imported with emoji names directly
# They are available within exec_emoji_code context

try:
    from .repl import (
        EmojiREPL,
        start_emoji_repl,
        emoji_exec,
    )
except ImportError:
    pass

try:
    from .enhanced import (
        EmojiTypes,
        load_emoji_file,
        EmojiException,
        emoji_error_handler,
        install_emoji_error_handler,
        EmojiSyntaxHighlighter,
        print_emoji_code,
        create_emoji_project,
        EmojiAssert,
        EMOJI_TEMPLATES,
    )
except ImportError:
    pass

# Convenience exports
__all__ = [
    # Core functions
    'enable',
    'disable',
    'is_enabled',
    'emojified',
    'emojify',
    'deemojify',
    'exec_emoji_code',
    'compile_emoji_code',
    'emojify_function',
    
    # Mapping functions
    'add_mapping',
    'add_custom_mapping',
    'remove_custom_mapping',
    'update_default_mapping',
    'remove_default_mapping',
    'view_mappings',
    'get_module_for_emoji',
    'get_emoji_for_module',
    'get_all_mappings',
    'reset_custom_mappings',
    'list_mappings',
    'save_custom_mappings',
    'load_custom_mappings',
    'search_mapping',
    'load_extended_mappings',
    'load_popular_set',
    'get_available_sets',
    'DEFAULT_MAPPINGS',
    
    # Hook functions
    'emoji_import',
    'install_emoji_hook',
    'uninstall_emoji_hook',
    'is_emoji_hook_installed',
    
    # Utility functions
    'is_emoji',
    'contains_emoji',
    'extract_emojis',
    
    # Enhanced features
    'EmojiREPL',
    'start_emoji_repl',
    'emoji_exec',
    'load_emoji_file',
    'EmojiException',
    'install_emoji_error_handler',
    'print_emoji_code',
    'create_emoji_project',
    'EmojiAssert',
    'EmojiTypes',
]

# Auto-enable on import (optional - can be removed if you prefer explicit enabling)
# enable()

def cli():
    """Command-line interface for emojify-python."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(
        description='Emojify Python - Import modules using emojis'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List mappings command
    list_parser = subparsers.add_parser('list', help='List emoji mappings')
    list_parser.add_argument('--category', help='Filter by category (data, web, ml, util)')
    list_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for mappings')
    search_parser.add_argument('query', help='Emoji or module name to search for')
    
    # Add mapping command
    add_parser = subparsers.add_parser('add', help='Add a custom mapping')
    add_parser.add_argument('emoji', help='Emoji character')
    add_parser.add_argument('module', help='Module name')
    add_parser.add_argument('--persist', action='store_true', help='Save as default')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a Python file with emoji support')
    run_parser.add_argument('file', help='Python file to run')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        mappings = view_mappings(args.category)
        if args.json:
            print(json.dumps(mappings, ensure_ascii=False, indent=2))
        else:
            for emoji, module in sorted(mappings.items(), key=lambda x: x[1]):
                print(f"{emoji}  → {module}")
    
    elif args.command == 'search':
        results = search_mapping(args.query)
        for emoji, module in results.items():
            print(f"{emoji}  → {module}")
    
    elif args.command == 'add':
        add_mapping(args.emoji, args.module, args.persist)
        print(f"Added mapping: {args.emoji} → {args.module}")
    
    elif args.command == 'run':
        enable()
        with open(args.file, 'r', encoding='utf-8') as f:
            code = f.read()
        exec_emoji_code(code)
    
    else:
        parser.print_help()

if __name__ == '__main__':
    cli()