"""Default emoji to module mappings."""

DEFAULT_MAPPINGS = {
    # Data Science & Analysis
    '🐼': 'pandas',
    '📊': 'matplotlib',
    '🔢': 'numpy',
    '🧮': 'scipy',
    '🤖': 'sklearn',
    '📈': 'seaborn',
    '📉': 'plotly',
    '🗂️': 'openpyxl',
    '📋': 'xlrd',
    
    # Machine Learning & AI
    '🔥': 'torch',
    '🧠': 'tensorflow',
    '🎯': 'keras',
    '🌳': 'xgboost',
    '💡': 'lightgbm',
    
    # Web Frameworks & HTTP
    '🌐': 'flask',
    '⚡': 'fastapi',
    '🎪': 'django',
    '🚀': 'requests',
    '🕸️': 'scrapy',
    '🔌': 'websocket',
    '🍪': 'http.cookies',
    
    # Databases
    '🗄️': 'sqlite3',
    '🐘': 'psycopg2',
    '🍃': 'pymongo',
    '🔴': 'redis',
    '🔶': 'sqlalchemy',
    
    # Testing & Quality
    '🧪': 'pytest',
    '🔬': 'unittest',
    '🎭': 'mock',
    '📝': 'doctest',
    
    # Utilities & System
    '📅': 'datetime',
    '🔍': 're',
    '📁': 'pathlib',
    '⏰': 'time',
    '🔐': 'hashlib',
    '🎲': 'random',
    '📦': 'json',
    '🗜️': 'gzip',
    '🔑': 'secrets',
    '🌈': 'colorama',
    '🎨': 'rich',
    '📜': 'logging',
    '⚙️': 'configparser',
    '🧵': 'threading',
    '🔄': 'asyncio',
    '📡': 'socket',
    '💾': 'pickle',
    '📏': 'decimal',
    '🗺️': 'collections',
    '🔗': 'itertools',
    '📐': 'math',
    '🏗️': 'struct',
    '🌍': 'os',
    '💻': 'sys',
    '📤': 'shutil',
    '🔧': 'subprocess',
    
    # Image & Media Processing
    '🖼️': 'PIL',
    '📷': 'cv2',
    '🎵': 'pydub',
    '🎬': 'moviepy',
    
    # Game Development
    '🎮': 'pygame',
    '🕹️': 'arcade',
    
    # GUI Development
    '🖥️': 'tkinter',
    '🪟': 'PyQt5',
    '🎛️': 'kivy',
    
    # Cryptography & Security
    '🔒': 'cryptography',
    '🛡️': 'bcrypt',
    
    # Data Formats
    '📄': 'csv',
    '🏷️': 'xml',
    '📑': 'yaml',
    '📰': 'feedparser',
    
    # Development Tools
    '🐛': 'pdb',
    '📈': 'cProfile',
    '💭': 'inspect',
    '🏃': 'multiprocessing',
}

# Reverse mapping for quick lookups
MODULE_TO_EMOJI = {v: k for k, v in DEFAULT_MAPPINGS.items()}

# User-defined custom mappings
custom_mappings = {}

def add_custom_mapping(emoji: str, module_name: str) -> None:
    """Add a custom emoji to module mapping.
    
    Args:
        emoji: The emoji character to use
        module_name: The actual module name to import
    """
    custom_mappings[emoji] = module_name

def remove_custom_mapping(emoji: str) -> None:
    """Remove a custom emoji mapping.
    
    Args:
        emoji: The emoji character to remove
    """
    if emoji in custom_mappings:
        del custom_mappings[emoji]

def get_module_for_emoji(emoji: str) -> str:
    """Get the module name for a given emoji.
    
    Args:
        emoji: The emoji character
        
    Returns:
        The module name if found, otherwise the emoji itself
    """
    # Check custom mappings first
    if emoji in custom_mappings:
        return custom_mappings[emoji]
    # Then check default mappings
    if emoji in DEFAULT_MAPPINGS:
        return DEFAULT_MAPPINGS[emoji]
    # Return the emoji itself if no mapping found
    return emoji

def get_emoji_for_module(module_name: str) -> str:
    """Get the emoji for a given module name.
    
    Args:
        module_name: The module name
        
    Returns:
        The emoji if found, otherwise the module name itself
    """
    # Check custom mappings first
    for emoji, mod in custom_mappings.items():
        if mod == module_name:
            return emoji
    # Then check default mappings
    if module_name in MODULE_TO_EMOJI:
        return MODULE_TO_EMOJI[module_name]
    # Return the module name itself if no mapping found
    return module_name

def get_all_mappings() -> dict:
    """Get all current emoji mappings (default + custom).
    
    Returns:
        Combined dictionary of all mappings
    """
    all_mappings = DEFAULT_MAPPINGS.copy()
    all_mappings.update(custom_mappings)
    return all_mappings

def reset_custom_mappings() -> None:
    """Reset all custom mappings."""
    global custom_mappings
    custom_mappings = {}

def update_default_mapping(emoji: str, module_name: str) -> None:
    """Update or add a default emoji mapping.
    
    This modifies the DEFAULT_MAPPINGS dictionary directly.
    Use with caution as it affects all users of the library.
    
    Args:
        emoji: The emoji character to map
        module_name: The module name to map to
    """
    DEFAULT_MAPPINGS[emoji] = module_name
    # Update reverse mapping
    MODULE_TO_EMOJI[module_name] = emoji

def remove_default_mapping(emoji: str) -> bool:
    """Remove a default emoji mapping.
    
    Args:
        emoji: The emoji character to remove
        
    Returns:
        True if removed, False if not found
    """
    if emoji in DEFAULT_MAPPINGS:
        module_name = DEFAULT_MAPPINGS[emoji]
        del DEFAULT_MAPPINGS[emoji]
        # Remove from reverse mapping if it exists
        if module_name in MODULE_TO_EMOJI and MODULE_TO_EMOJI[module_name] == emoji:
            del MODULE_TO_EMOJI[module_name]
        return True
    return False

def list_mappings(show_custom: bool = True, show_default: bool = True) -> dict:
    """List mappings in a formatted way.
    
    Args:
        show_custom: Include custom mappings
        show_default: Include default mappings
        
    Returns:
        Dictionary with 'default' and 'custom' keys
    """
    result = {}
    if show_default:
        result['default'] = DEFAULT_MAPPINGS.copy()
    if show_custom:
        result['custom'] = custom_mappings.copy()
    return result

def save_custom_mappings(filepath: str) -> None:
    """Save custom mappings to a JSON file.
    
    Args:
        filepath: Path to save the mappings
    """
    import json
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(custom_mappings, f, ensure_ascii=False, indent=2)

def load_custom_mappings(filepath: str) -> None:
    """Load custom mappings from a JSON file.
    
    Args:
        filepath: Path to load the mappings from
    """
    import json
    global custom_mappings
    with open(filepath, 'r', encoding='utf-8') as f:
        custom_mappings = json.load(f)

def search_mapping(query: str) -> dict:
    """Search for mappings by emoji or module name.
    
    Args:
        query: Emoji or module name to search for
        
    Returns:
        Dictionary with matching mappings
    """
    matches = {}
    all_mappings = get_all_mappings()
    
    for emoji, module in all_mappings.items():
        if query in emoji or query in module:
            matches[emoji] = module
    
    return matches