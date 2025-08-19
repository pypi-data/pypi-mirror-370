"""Utility functions for emojify-python."""

import re
import unicodedata
import sys
from typing import Optional, Tuple, Any

# Regex pattern to match emoji characters
EMOJI_PATTERN = re.compile(
    "[\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F300-\U0001F5FF"   # Miscellaneous Symbols and Pictographs
    "\U0001F680-\U0001F6FF"   # Transport and Map Symbols
    "\U0001F700-\U0001F77F"   # Alchemical Symbols
    "\U0001F780-\U0001F7FF"   # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"   # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"   # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"   # Chess Symbols
    "\U0001FA70-\U0001FAFF"   # Symbols and Pictographs Extended-A
    "\U00002600-\U000027BF"   # Miscellaneous Symbols
    "\U0001F1E0-\U0001F1FF"   # Flags
    "\U00002700-\U000027BF"   # Dingbats
    "\U0001F900-\U0001F9FF"   # Supplemental Symbols and Pictographs
    "\U00002300-\U000023FF"   # Miscellaneous Technical
    "\U000025A0-\U000025FF"   # Geometric Shapes
    "\U00002B00-\U00002BFF"   # Miscellaneous Symbols and Arrows
    "]+"
)

def is_emoji(text: str) -> bool:
    """Check if a string contains only emoji characters.
    
    Args:
        text: String to check
        
    Returns:
        True if the string is entirely emojis, False otherwise
    """
    if not text:
        return False
    return bool(EMOJI_PATTERN.fullmatch(text))

def contains_emoji(text: str) -> bool:
    """Check if a string contains any emoji characters.
    
    Args:
        text: String to check
        
    Returns:
        True if the string contains any emojis, False otherwise
    """
    if not text:
        return False
    return bool(EMOJI_PATTERN.search(text))

def extract_emojis(text: str) -> list:
    """Extract all emoji characters from a string.
    
    Args:
        text: String to extract emojis from
        
    Returns:
        List of emoji characters found
    """
    if not text:
        return []
    return EMOJI_PATTERN.findall(text)

def emoji_to_name(emoji: str) -> str:
    """Convert an emoji to a valid Python identifier name.
    
    Args:
        emoji: Emoji character(s)
        
    Returns:
        Valid Python identifier string
    """
    if not emoji:
        return ""
    
    # Get Unicode name for the emoji
    names = []
    for char in emoji:
        try:
            name = unicodedata.name(char, "").replace(" ", "_").replace("-", "_")
            # Remove non-alphanumeric characters except underscore
            name = re.sub(r'[^a-zA-Z0-9_]', '', name)
            if name:
                names.append(name.lower())
        except ValueError:
            # If no Unicode name, use the codepoint
            names.append(f"u{ord(char):04x}")
    
    result = "_".join(names) if names else f"emoji_{hash(emoji) % 1000000}"
    
    # Ensure it starts with a letter or underscore
    if result and result[0].isdigit():
        result = "_" + result
    
    return result or "_emoji"

def name_to_emoji(name: str, mappings: dict) -> Optional[str]:
    """Try to convert a name back to its emoji.
    
    Args:
        name: Python identifier name
        mappings: Dictionary of emoji to name mappings
        
    Returns:
        The emoji if found, None otherwise
    """
    # Reverse lookup in the mappings
    for emoji, mapped_name in mappings.items():
        if emoji_to_name(emoji) == name:
            return emoji
    return None

def validate_python_identifier(name: str) -> bool:
    """Check if a string is a valid Python identifier.
    
    Args:
        name: String to validate
        
    Returns:
        True if valid Python identifier, False otherwise
    """
    if not name:
        return False
    return name.isidentifier()

def safe_import(module_name: str) -> Tuple[bool, Any]:
    """Safely attempt to import a module.
    
    Args:
        module_name: Name of the module to import
        
    Returns:
        Tuple of (success, module_or_error)
    """
    try:
        if module_name in sys.modules:
            return True, sys.modules[module_name]
        
        module = __import__(module_name)
        return True, module
    except ImportError as e:
        return False, e
    except Exception as e:
        return False, e

def get_python_version() -> Tuple[int, int]:
    """Get the current Python version as a tuple.
    
    Returns:
        Tuple of (major, minor) version numbers
    """
    return sys.version_info.major, sys.version_info.minor

def supports_emoji_identifiers() -> bool:
    """Check if the current Python version supports emoji in identifiers.
    
    Note: Python doesn't natively support emojis as identifiers,
    so this always returns False. We handle it through our transformations.
    
    Returns:
        False (Python doesn't natively support emoji identifiers)
    """
    return False

def format_import_error(emoji: str, module_name: str, error: Exception) -> str:
    """Format a nice error message for import failures.
    
    Args:
        emoji: The emoji that was used
        module_name: The actual module name attempted
        error: The exception that occurred
        
    Returns:
        Formatted error message
    """
    return (
        f"Failed to import '{module_name}' (from emoji '{emoji}'):\n"
        f"  {type(error).__name__}: {str(error)}\n"
        f"  Hint: Make sure '{module_name}' is installed: pip install {module_name}"
    )