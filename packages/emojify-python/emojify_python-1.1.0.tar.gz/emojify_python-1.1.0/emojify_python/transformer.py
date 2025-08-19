"""AST transformer for handling emoji imports and variables."""

import ast
import sys
from typing import Any, Dict, Optional
from .utils import is_emoji, contains_emoji, emoji_to_name
from .mappings import get_module_for_emoji

class EmojiTransformer(ast.NodeTransformer):
    """Transform AST to handle emoji imports and variables."""
    
    def __init__(self, placeholder_to_emoji=None):
        self.emoji_mappings = {}  # Track emoji to transformed name mappings
        self.transformed_names = {}  # Track transformed names back to emojis
        self.placeholder_to_emoji = placeholder_to_emoji or {}  # Map placeholders back to emojis
        
    def visit_Import(self, node: ast.Import) -> ast.Import:
        """Transform import statements with emojis.
        
        Handles:
        - import 🐼
        - import pandas as 🐼
        """
        new_aliases = []
        
        for alias in node.names:
            # Check if the module name is a placeholder for an emoji
            if alias.name in self.placeholder_to_emoji:
                original_emoji = self.placeholder_to_emoji[alias.name]
                real_module = get_module_for_emoji(original_emoji)
            # Or if it's directly an emoji
            elif is_emoji(alias.name):
                # Get the actual module name
                real_module = get_module_for_emoji(alias.name)
            else:
                # Regular module, skip transformation
                new_aliases.append(alias)
                continue
                
            # If there's an alias, keep it (even if it's an emoji)
            if alias.asname:
                if is_emoji(alias.asname):
                    # Transform emoji alias to valid identifier
                    transformed_alias = emoji_to_name(alias.asname)
                    self.emoji_mappings[alias.asname] = transformed_alias
                    self.transformed_names[transformed_alias] = alias.asname
                    new_alias = ast.alias(name=real_module, asname=transformed_alias)
                else:
                    new_alias = ast.alias(name=real_module, asname=alias.asname)
            else:
                # No alias, import with transformed name
                transformed_name = emoji_to_name(alias.name)
                self.emoji_mappings[alias.name] = transformed_name
                self.transformed_names[transformed_name] = alias.name
                new_alias = ast.alias(name=real_module, asname=transformed_name)
                    
            new_aliases.append(new_alias)
        
        node.names = new_aliases
        return node
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        """Transform from...import statements with emojis.
        
        Handles:
        - from 🐼 import DataFrame
        - from pandas import DataFrame as 📊
        """
        # Check if module is a placeholder for an emoji
        if node.module and node.module in self.placeholder_to_emoji:
            original_emoji = self.placeholder_to_emoji[node.module]
            real_module = get_module_for_emoji(original_emoji)
            node.module = real_module
        # Or if it's directly an emoji (shouldn't happen with preprocessing)
        elif node.module and is_emoji(node.module):
            real_module = get_module_for_emoji(node.module)
            node.module = real_module
        
        # Transform aliases
        new_aliases = []
        for alias in node.names:
            if alias.asname and is_emoji(alias.asname):
                # Transform emoji alias
                transformed_alias = emoji_to_name(alias.asname)
                self.emoji_mappings[alias.asname] = transformed_alias
                self.transformed_names[transformed_alias] = alias.asname
                new_alias = ast.alias(name=alias.name, asname=transformed_alias)
            else:
                new_alias = alias
            new_aliases.append(new_alias)
        
        node.names = new_aliases
        return node
    
    def visit_Name(self, node: ast.Name) -> ast.Name:
        """Transform emoji variable names.
        
        Handles emoji identifiers in:
        - Variable assignments: 🎲 = 42
        - Variable references: print(🎲)
        """
        if is_emoji(node.id):
            transformed_name = emoji_to_name(node.id)
            self.emoji_mappings[node.id] = transformed_name
            self.transformed_names[transformed_name] = node.id
            node.id = transformed_name
        elif node.id in self.emoji_mappings:
            # Already transformed emoji reference
            node.id = self.emoji_mappings[node.id]
        
        return node
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Transform emoji function names.
        
        Handles: def 🚀(x): return x * 2
        """
        if is_emoji(node.name):
            transformed_name = emoji_to_name(node.name)
            self.emoji_mappings[node.name] = transformed_name
            self.transformed_names[transformed_name] = node.name
            node.name = transformed_name
        
        # Visit function body
        self.generic_visit(node)
        return node
    
    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Transform emoji class names.
        
        Handles: class 🏠: pass
        """
        if is_emoji(node.name):
            transformed_name = emoji_to_name(node.name)
            self.emoji_mappings[node.name] = transformed_name
            self.transformed_names[transformed_name] = node.name
            node.name = transformed_name
        
        # Visit class body
        self.generic_visit(node)
        return node
    
    def visit_Attribute(self, node: ast.Attribute) -> ast.Attribute:
        """Transform emoji attribute names.
        
        Handles: obj.🔥()
        """
        if is_emoji(node.attr):
            transformed_name = emoji_to_name(node.attr)
            self.emoji_mappings[node.attr] = transformed_name
            self.transformed_names[transformed_name] = node.attr
            node.attr = transformed_name
        
        # Visit the value part
        self.generic_visit(node)
        return node
    
    def visit_arg(self, node: ast.arg) -> ast.arg:
        """Transform emoji argument names in function definitions.
        
        Handles: def func(🎯): pass
        """
        if is_emoji(node.arg):
            transformed_name = emoji_to_name(node.arg)
            self.emoji_mappings[node.arg] = transformed_name
            self.transformed_names[transformed_name] = node.arg
            node.arg = transformed_name
        
        return node

def transform_source(source: str) -> tuple[str, Dict[str, str]]:
    """Transform Python source code containing emojis.
    
    Args:
        source: Python source code string
        
    Returns:
        Tuple of (transformed_source, emoji_mappings)
    """
    import re
    import tokenize
    import io
    
    # Track emoji to placeholder mappings
    emoji_mappings = {}
    placeholder_to_emoji = {}
    
    # First pass: Replace emojis with temporary placeholders for parsing
    temp_source = source
    emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA00-\U0001FAFF]+')
    
    # Find all emojis in the source
    emojis_found = emoji_pattern.findall(source)
    
    # Replace emojis with valid Python identifiers temporarily
    for emoji in set(emojis_found):
        placeholder = emoji_to_name(emoji)
        temp_source = temp_source.replace(emoji, placeholder)
        emoji_mappings[emoji] = placeholder
        placeholder_to_emoji[placeholder] = emoji
    
    try:
        # Parse the modified source into an AST
        tree = ast.parse(temp_source)
        
        # Transform the AST
        transformer = EmojiTransformer(placeholder_to_emoji)
        transformed_tree = transformer.visit(tree)
        
        # Fix missing locations in the AST
        ast.fix_missing_locations(transformed_tree)
        
        # Convert back to source code
        # Note: ast.unparse is available in Python 3.9+
        if sys.version_info >= (3, 9):
            transformed_source = ast.unparse(transformed_tree)
        else:
            # For older Python versions, return the temp source
            transformed_source = temp_source
            
        # Merge transformer's mappings with our emoji mappings
        emoji_mappings.update(transformer.emoji_mappings)
            
        return transformed_source, emoji_mappings
        
    except SyntaxError as e:
        # Return modified source even if AST transformation fails
        return temp_source, emoji_mappings

def create_emoji_namespace(emoji_mappings: Dict[str, str], globals_dict: dict) -> dict:
    """Create a namespace that maps emoji names to their transformed names.
    
    Args:
        emoji_mappings: Dictionary of emoji to transformed name mappings
        globals_dict: The global namespace to use as base
        
    Returns:
        Enhanced namespace with emoji support
    """
    namespace = globals_dict.copy()
    
    # Create a proxy object for each emoji mapping
    for emoji, transformed_name in emoji_mappings.items():
        if transformed_name in namespace:
            # Create a reference with the emoji name
            namespace[emoji] = namespace[transformed_name]
    
    return namespace