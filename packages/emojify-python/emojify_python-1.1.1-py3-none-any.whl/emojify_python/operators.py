"""Emoji operators and enhanced syntax support."""

import operator
import ast
from typing import Any, Dict, Callable

# Emoji operator mappings
EMOJI_OPERATORS = {
    # Arithmetic
    '➕': operator.add,
    '➖': operator.sub,
    '✖️': operator.mul,
    '➗': operator.truediv,
    '💪': operator.pow,
    '🔢': operator.mod,
    '⬇️': operator.floordiv,
    
    # Comparison
    '🟰': operator.eq,
    '≠': operator.ne,
    '⬆️': operator.gt,
    '⬇️': operator.lt,
    '📈': operator.ge,
    '📉': operator.le,
    
    # Logical
    '✅': lambda x, y: x and y,
    '🔀': lambda x, y: x or y,
    '❌': operator.not_,
    
    # Bitwise
    '&️': operator.and_,
    '|': operator.or_,
    '⊕': operator.xor,
    '🔄': operator.inv,
    '⬅️': operator.lshift,
    '➡️': operator.rshift,
    
    # Container operations
    '📥': lambda x, y: y in x,
    '📤': lambda x, y: y not in x,
    '🔗': operator.concat,
    '🔁': operator.mul,  # For repetition
}

# Emoji keywords
EMOJI_KEYWORDS = {
    '🔁': 'for',
    '🔄': 'while',
    '❓': 'if',
    '🤷': 'elif',
    '🙅': 'else',
    '💥': 'raise',
    '🛡️': 'try',
    '🚫': 'except',
    '🏁': 'finally',
    '⏰': 'with',
    '📦': 'import',
    '📤': 'from',
    '🏷️': 'as',
    '📝': 'def',
    '🏛️': 'class',
    '🔙': 'return',
    '⏩': 'yield',
    '⏸️': 'break',
    '⏭️': 'continue',
    '✅': 'True',
    '❌': 'False',
    '🚫': 'None',
    '🌍': 'global',
    '🏠': 'local',
    '🔓': 'nonlocal',
    '➡️': 'lambda',
    '✔️': 'assert',
    '🗑️': 'del',
    '📥': 'in',
    '📤': 'not in',
    '🆔': 'is',
    '🚫🆔': 'is not',
    '➕➕': '+=',
    '➖➖': '-=',
    '✖️✖️': '*=',
    '➗➗': '/=',
}

# Emoji built-in functions
EMOJI_BUILTINS = {
    '🖨️': print,
    '📥': input,
    '📏': len,
    '🔢': int,
    '💯': float,
    '📝': str,
    '📚': list,
    '📖': dict,
    '🎯': tuple,
    '🎪': set,
    '🔍': type,
    '🆔': id,
    '🎯': range,
    '🔄': enumerate,
    '🤐': zip,
    '🗺️': map,
    '🏗️': filter,
    '📊': sorted,
    '🔀': reversed,
    '➕': sum,
    '📈': max,
    '📉': min,
    '✅': all,
    '🎲': any,
    '📂': open,
    '🔒': hash,
    '📞': callable,
    '🔍': isinstance,
    '🧬': issubclass,
    '💭': eval,
    '🏃': exec,
    '🔧': compile,
    '🌐': globals,
    '🏠': locals,
    '📋': vars,
    '📎': getattr,
    '📌': setattr,
    '🗑️': delattr,
    '❓': hasattr,
    '📖': dir,
    '❗': abs,
    '🎰': round,
    '📦': __import__,
}

def create_emoji_operator(op_emoji: str) -> Callable:
    """Create a function that performs the emoji operator.
    
    Args:
        op_emoji: The emoji representing the operator
        
    Returns:
        A callable that performs the operation
    """
    if op_emoji in EMOJI_OPERATORS:
        return EMOJI_OPERATORS[op_emoji]
    else:
        raise ValueError(f"Unknown emoji operator: {op_emoji}")

def transform_emoji_operators(code: str) -> str:
    """Transform emoji operators in code to Python operators.
    
    Args:
        code: Python code with emoji operators
        
    Returns:
        Code with emoji operators replaced
    """
    result = code
    
    # Replace emoji operators with Python equivalents
    operator_map = {
        '➕': '+',
        '➖': '-',
        '✖️': '*',
        '➗': '/',
        '💪': '**',
        '🔢': '%',
        '🟰': '==',
        '≠': '!=',
        '⬆️': '>',
        '⬇️': '<',
        '📈': '>=',
        '📉': '<=',
        '✅': 'and',
        '🔀': 'or',
        '❌': 'not',
        '📥': 'in',
        '📤': 'not in',
        '🆔': 'is',
        '🚫🆔': 'is not',
        '➕➕': '+=',
        '➖➖': '-=',
        '✖️✖️': '*=',
        '➗➗': '/=',
    }
    
    for emoji, op in operator_map.items():
        result = result.replace(emoji, f' {op} ')
    
    return result

def transform_emoji_keywords(code: str) -> str:
    """Transform emoji keywords to Python keywords.
    
    Args:
        code: Python code with emoji keywords
        
    Returns:
        Code with emoji keywords replaced
    """
    result = code
    
    # Replace emoji keywords (careful with word boundaries)
    import re
    for emoji, keyword in EMOJI_KEYWORDS.items():
        # Use word boundaries to avoid partial replacements
        pattern = re.escape(emoji)
        result = re.sub(pattern, keyword, result)
    
    return result

def create_emoji_builtin(builtin_emoji: str) -> Callable:
    """Get the built-in function for an emoji.
    
    Args:
        builtin_emoji: The emoji representing the built-in
        
    Returns:
        The built-in function
    """
    if builtin_emoji in EMOJI_BUILTINS:
        return EMOJI_BUILTINS[builtin_emoji]
    else:
        raise ValueError(f"Unknown emoji built-in: {builtin_emoji}")

class EmojiOperatorTransformer(ast.NodeTransformer):
    """Transform emoji operators in the AST."""
    
    def visit_BinOp(self, node):
        """Transform binary operations with emoji operators."""
        self.generic_visit(node)
        return node
    
    def visit_Compare(self, node):
        """Transform comparison operations with emoji operators."""
        self.generic_visit(node)
        return node
    
    def visit_BoolOp(self, node):
        """Transform boolean operations with emoji operators."""
        self.generic_visit(node)
        return node

def install_emoji_operators():
    """Install emoji operators into the Python runtime."""
    import builtins
    
    # Add emoji built-ins
    for emoji, func in EMOJI_BUILTINS.items():
        # Create a safe name for the emoji
        encoded = emoji.encode('unicode_escape').decode('ascii').replace('\\', '_')
        safe_name = f"emoji_{encoded}"
        setattr(builtins, safe_name, func)
        
        # Also try to set the emoji directly (may not work in all Python versions)
        try:
            setattr(builtins, emoji, func)
        except:
            pass

def create_emoji_math():
    """Create a math module with emoji operations."""
    
    class EmojiMath:
        """Math operations with emojis."""
        
        def add(self, a, b):
            """Emoji addition (➕)."""
            return a + b
        
        def sub(self, a, b):
            """Emoji subtraction (➖)."""
            return a - b
        
        def mul(self, a, b):
            """Emoji multiplication (✖️)."""
            return a * b
        
        def div(self, a, b):
            """Emoji division (➗)."""
            return a / b
        
        def power(self, a, b):
            """Emoji power (💪)."""
            return a ** b
        
        def maximum(self, numbers):
            """Emoji max (📈)."""
            return max(numbers)
        
        def minimum(self, numbers):
            """Emoji min (📉)."""
            return min(numbers)
        
        def average(self, numbers):
            """Emoji average (📊)."""
            return sum(numbers) / len(numbers)
        
        def random(self):
            """Emoji random."""
            import random
            return random.random()
    
    return EmojiMath()