"""Enhanced emoji Python features."""

import sys
import os
import importlib.util
from typing import Any, Dict, List, Optional, Union
import ast
import json
import traceback

# Emoji type hints
# Emoji type hints mapping (can't use emoji attributes directly in Python)
EMOJI_TYPES = {
    '🔢': int,
    '💯': float,
    '📝': str,
    '✅': bool,
    '🚫': type(None),
    '📚': list,
    '📖': dict,
    '🎯': tuple,
    '🎪': set,
    '📦': object,
    '🔧': callable,
    '🔄': iter,
    '📋': bytes,
}

class EmojiTypes:
    """Emoji type hints for better code readability."""
    
    # We can't use emoji attributes directly, 
    # but we can provide a mapping for use in exec_emoji_code
    @staticmethod
    def get_type(emoji: str):
        """Get the Python type for an emoji."""
        return EMOJI_TYPES.get(emoji, object)
    

def load_emoji_file(filepath: str) -> Any:
    """Load and execute a .🐍 (emoji Python) file.
    
    Args:
        filepath: Path to the emoji Python file
        
    Returns:
        Module object or execution result
    """
    # Support both .py and .🐍 extensions
    if not filepath.endswith(('.py', '.🐍', '.emoji')):
        # Try adding emoji extension
        emoji_path = filepath + '.🐍'
        if os.path.exists(emoji_path):
            filepath = emoji_path
    
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Execute emoji code
    from .core import exec_emoji_code
    namespace = {}
    exec_emoji_code(code, namespace)
    
    # Create a module-like object
    import types
    module = types.ModuleType(os.path.basename(filepath))
    module.__dict__.update(namespace)
    module.__file__ = filepath
    
    return module

class EmojiException(Exception):
    """Base exception with emoji support."""
    
    def __init__(self, message: str, emoji: str = "❌"):
        self.emoji = emoji
        super().__init__(f"{emoji} {message}")

class BugException(EmojiException):
    """Bug/Error exception (🐛)."""
    def __init__(self, message: str):
        super().__init__(message, "🐛")

class FireException(EmojiException):
    """Critical/Fire exception (🔥)."""
    def __init__(self, message: str):
        super().__init__(message, "🔥")

class ForbiddenException(EmojiException):
    """Not allowed/Forbidden exception (🚫)."""
    def __init__(self, message: str):
        super().__init__(message, "🚫")

class ThinkingException(EmojiException):
    """Thinking/Processing exception (💭)."""
    def __init__(self, message: str):
        super().__init__(message, "💭")

def emoji_error_handler(exc_type, exc_value, exc_traceback):
    """Custom error handler with emoji messages."""
    
    emoji_errors = {
        SyntaxError: "📝",
        ImportError: "📦",
        TypeError: "🔧",
        ValueError: "🔢",
        KeyError: "🔑",
        IndexError: "📍",
        AttributeError: "🏷️",
        NameError: "📛",
        FileNotFoundError: "📁",
        PermissionError: "🔒",
        ZeroDivisionError: "0️⃣",
        RuntimeError: "🏃",
        MemoryError: "💾",
        KeyboardInterrupt: "⌨️",
        Exception: "❌",
    }
    
    emoji = emoji_errors.get(exc_type, "❓")
    
    print(f"\n{emoji} Emoji Python Error {emoji}")
    print("=" * 40)
    
    # Format the error message
    if exc_type.__name__ == "SyntaxError":
        print(f"📝 Syntax Error: Check your emoji syntax!")
    elif exc_type.__name__ == "ImportError":
        print(f"📦 Import Error: Module not found!")
        print(f"   Tip: Did you mean to use an emoji import?")
    
    # Print the actual error
    print(f"\n{emoji} {exc_type.__name__}: {exc_value}")
    
    # Print simplified traceback
    if exc_traceback:
        print("\n📍 Location:")
        tb_lines = traceback.format_tb(exc_traceback)
        for line in tb_lines[-3:]:  # Show last 3 stack frames
            print("  " + line.strip())
    
    print("\n💡 Tip: Check your emoji mappings with view_mappings()")
    print("=" * 40)

def install_emoji_error_handler():
    """Install the custom emoji error handler."""
    sys.excepthook = emoji_error_handler

class EmojiSyntaxHighlighter:
    """Syntax highlighter for emoji Python code."""
    
    # ANSI color codes
    COLORS = {
        'keyword': '\033[94m',  # Blue
        'emoji': '\033[92m',    # Green
        'string': '\033[93m',   # Yellow
        'number': '\033[96m',   # Cyan
        'comment': '\033[90m',  # Gray
        'decorator': '\033[95m', # Magenta
        'reset': '\033[0m',     # Reset
    }
    
    @classmethod
    def highlight(cls, code: str) -> str:
        """Highlight emoji Python code.
        
        Args:
            code: Source code to highlight
            
        Returns:
            Highlighted code with ANSI colors
        """
        import re
        
        result = code
        
        # Highlight emojis
        emoji_pattern = r'[\U0001F000-\U0001F9FF\U00002600-\U000027BF]+'
        result = re.sub(emoji_pattern, lambda m: f"{cls.COLORS['emoji']}{m.group()}{cls.COLORS['reset']}", result)
        
        # Highlight keywords
        keywords = ['def', 'class', 'import', 'from', 'as', 'if', 'elif', 'else', 
                   'for', 'while', 'try', 'except', 'finally', 'with', 'return',
                   'yield', 'break', 'continue', 'pass', 'raise', 'assert',
                   'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is']
        
        for keyword in keywords:
            pattern = r'\b' + keyword + r'\b'
            result = re.sub(pattern, f"{cls.COLORS['keyword']}{keyword}{cls.COLORS['reset']}", result)
        
        # Highlight strings
        result = re.sub(r'(["\'])([^"\']*)\1', 
                       lambda m: f"{cls.COLORS['string']}{m.group()}{cls.COLORS['reset']}", 
                       result)
        
        # Highlight numbers
        result = re.sub(r'\b\d+\.?\d*\b', 
                       lambda m: f"{cls.COLORS['number']}{m.group()}{cls.COLORS['reset']}", 
                       result)
        
        # Highlight comments
        result = re.sub(r'#.*$', 
                       lambda m: f"{cls.COLORS['comment']}{m.group()}{cls.COLORS['reset']}", 
                       result, flags=re.MULTILINE)
        
        # Highlight decorators
        result = re.sub(r'@\w+', 
                       lambda m: f"{cls.COLORS['decorator']}{m.group()}{cls.COLORS['reset']}", 
                       result)
        
        return result

def print_emoji_code(code: str):
    """Print emoji Python code with syntax highlighting.
    
    Args:
        code: Source code to print
    """
    highlighted = EmojiSyntaxHighlighter.highlight(code)
    print(highlighted)

# Emoji code templates and snippets
EMOJI_TEMPLATES = {
    'hello_world': '''
# 👋 Hello World in Emoji Python!
import 📦

🖨️("Hello, World! 🌍")
🎲 = 📦.dumps({"greeting": "👋"})
🖨️(f"JSON: {🎲}")
''',
    
    'data_science': '''
# 📊 Data Science with Emojis
import 🐼
import 🔢

# Create data
📊 = 🐼.DataFrame({
    'x': 🔢.array([1, 2, 3, 4, 5]),
    'y': 🔢.array([2, 4, 6, 8, 10])
})

# Calculate statistics
📈 = 📊['y'].mean()
📉 = 📊['y'].min()
🖨️(f"Mean: {📈}, Min: {📉}")
''',
    
    'web_api': '''
# 🌐 Web API with Emojis
from 🌐 import Flask, jsonify

🚀 = Flask(__name__)

@🚀.route('/api/emoji')
@⏱️  # Time the request
@🛡️  # Protect from errors
def get_emoji():
    return jsonify({'emoji': '🎉', 'status': '✅'})

if __name__ == '__main__':
    🚀.run(debug=True)
''',
    
    'decorated_function': '''
# 🎨 Decorated Functions
@⏱️  # Time execution
@💾  # Cache results
@🛡️  # Exception protection
def 🎯(n):
    """Calculate factorial with emojis!"""
    if n 🟰 0:
        🔙 1
    🔙 n ✖️ 🎯(n ➖ 1)

result = 🎯(5)
🖨️(f"5! = {result}")
''',
}

def create_emoji_project(name: str, template: str = 'hello_world'):
    """Create a new emoji Python project.
    
    Args:
        name: Project name
        template: Template to use
    """
    import os
    
    # Create project directory
    os.makedirs(name, exist_ok=True)
    
    # Create main emoji file
    main_file = os.path.join(name, 'main.🐍')
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(EMOJI_TEMPLATES.get(template, EMOJI_TEMPLATES['hello_world']))
    
    # Create emoji config
    config = {
        'name': name,
        'version': '0.1.0',
        'emojis': {
            '🚀': 'main',
            '📦': 'package',
            '🔧': 'config',
        }
    }
    
    config_file = os.path.join(name, 'emoji.json')
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created emoji project: {name}")
    print(f"📁 Files created:")
    print(f"   - {main_file}")
    print(f"   - {config_file}")
    print(f"\n🚀 Run with: python -m emojify_python.run {main_file}")

# Emoji assertions for testing
class EmojiAssert:
    """Emoji assertions for testing."""
    
    @staticmethod
    def assert_true(condition, message=""):
        """Assert true with emoji (✅)."""
        assert condition, f"❌ Assertion failed: {message}"
    
    @staticmethod
    def assert_equal(a, b, message=""):
        """Assert equal with emoji (🟰)."""
        assert a == b, f"❌ {a} ≠ {b}: {message}"
    
    @staticmethod
    def assert_false(condition, message=""):
        """Assert false with emoji (❌)."""
        assert not condition, f"❌ Should be false: {message}"
    
    @staticmethod
    def assert_in(item, container, message=""):
        """Assert in with emoji (📥)."""
        assert item in container, f"❌ {item} not in {container}: {message}"
    
    @staticmethod
    def assert_raises(func, exception=Exception):
        """Assert raises exception with emoji (🚫)."""
        try:
            func()
            assert False, f"❌ Should have raised {exception}"
        except exception:
            pass

# Make emoji asserts available
assert_emoji = EmojiAssert()