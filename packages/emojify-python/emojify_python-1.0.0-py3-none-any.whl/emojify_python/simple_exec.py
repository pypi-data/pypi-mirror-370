"""Simplified emoji code execution."""

import re
from .utils import is_emoji
from .mappings import get_module_for_emoji

def simple_exec_emoji_code(code: str):
    """Execute Python code with emoji support using simple string replacement."""
    
    # Create a mapping for all emojis found in the code
    emoji_map = {}
    counter = 0
    
    # Find all unique emojis in the code
    emoji_pattern = r'[\U0001F000-\U0001F9FF\U00002600-\U000027BF\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]+'
    emojis_found = set(re.findall(emoji_pattern, code))
    
    # Create valid Python names for each emoji
    for emoji in emojis_found:
        counter += 1
        valid_name = f"emoji_{counter}_{abs(hash(emoji)) % 10000}"
        emoji_map[emoji] = valid_name
    
    # Process the code
    transformed_code = code
    
    # Replace all emojis with valid Python names
    for emoji in sorted(emojis_found, key=len, reverse=True):  # Replace longer emojis first
        valid_name = emoji_map[emoji]
        real_module = get_module_for_emoji(emoji)
        
        if real_module != emoji:
            # It's a known module - replace in import statements  
            # Replace "import emoji" patterns
            # Handle "import emoji as something"
            pattern = f"import\\s+{re.escape(emoji)}\\s+as\\s+(\\w+)"
            transformed_code = re.sub(pattern, f"import {real_module} as \\1", transformed_code)
            # Handle simple "import emoji"
            transformed_code = re.sub(f"import\\s+{re.escape(emoji)}(?!\\w)", f"import {real_module} as {valid_name}", transformed_code)
            # Replace "from emoji" with "from real_module"
            transformed_code = re.sub(f"from\\s+{re.escape(emoji)}(?!\\w)", f"from {real_module}", transformed_code)
            # Replace remaining occurrences
            transformed_code = transformed_code.replace(emoji, valid_name)
        else:
            # Just a variable/function name, replace everywhere
            transformed_code = transformed_code.replace(emoji, valid_name)
    
    # Execute the transformed code
    namespace = {}
    exec(transformed_code, namespace)
    
    # Add emoji references back to namespace
    result = {}
    for emoji, valid_name in emoji_map.items():
        if valid_name in namespace:
            result[emoji] = namespace[valid_name]
            result[valid_name] = namespace[valid_name]
    
    # Add non-emoji items
    for key, value in namespace.items():
        if not key.startswith('emoji_') and not key.startswith('__'):
            result[key] = value
    
    return result