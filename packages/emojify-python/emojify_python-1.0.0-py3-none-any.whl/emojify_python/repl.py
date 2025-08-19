"""Emoji REPL - Interactive Python with emoji support."""

import sys
import code
import readline
import rlcompleter
from typing import Dict, Any
import traceback
from .core import exec_emoji_code, enable
from .operators import transform_emoji_operators, transform_emoji_keywords, EMOJI_BUILTINS
# Decorators with emoji names can't be imported directly

class EmojiREPL(code.InteractiveConsole):
    """An interactive Python REPL with emoji support."""
    
    def __init__(self, locals=None):
        """Initialize the emoji REPL.
        
        Args:
            locals: Initial local namespace
        """
        if locals is None:
            locals = {}
        
        # Add emoji built-ins to namespace
        locals.update({
            '🖨️': print,
            '📥': input,
            '📏': len,
            '🔢': int,
            '💯': float,
            '📝': str,
            '📚': list,
            '📖': dict,
            '🎯': range,
            '🔄': enumerate,
            '🤐': zip,
            '🗺️': map,
            '📊': sorted,
            '➕': sum,
            '📈': max,
            '📉': min,
        })
        
        # Note: Emoji decorators can't be added directly as they use emoji names
        # They would need to be accessed through exec_emoji_code
        
        super().__init__(locals)
        self.emoji_enabled = True
        
        # Enable emoji imports
        enable()
        
        # Configure readline for better autocompletion
        readline.set_completer(rlcompleter.Completer(self.locals).complete)
        readline.parse_and_bind("tab: complete")
    
    def push(self, line):
        """Push a line to the interpreter.
        
        Args:
            line: The line of code to execute
        """
        # Transform emoji syntax
        if self.emoji_enabled and line.strip():
            try:
                # Transform operators and keywords
                line = transform_emoji_operators(line)
                line = transform_emoji_keywords(line)
            except Exception:
                pass  # Use original line if transformation fails
        
        return super().push(line)
    
    def runsource(self, source, filename="<emoji>", symbol="single"):
        """Execute the source in the interpreter.
        
        Args:
            source: Source code to execute
            filename: Filename for error reporting
            symbol: Compilation mode
        """
        if self.emoji_enabled and source.strip():
            try:
                # Use exec_emoji_code for emoji support
                result = exec_emoji_code(source, self.locals, self.locals)
                return False  # Execution complete
            except SyntaxError:
                # Might be incomplete, let parent handle it
                return super().runsource(source, filename, symbol)
            except Exception as e:
                # Print the error
                traceback.print_exc()
                return False
        
        return super().runsource(source, filename, symbol)
    
    def interact(self, banner=None):
        """Interactive loop with custom banner.
        
        Args:
            banner: Custom banner to display
        """
        if banner is None:
            banner = self.get_banner()
        
        super().interact(banner)
    
    def get_banner(self):
        """Get the REPL banner."""
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        banner = f"""
🐍 {'='*50} 🐍
    Emoji Python REPL v1.0.0
    Python {python_version} with full emoji support!
    
    Quick Guide:
    • Import: import 🐼 (pandas), 📊 (matplotlib)
    • Math: 5 ➕ 3, 10 ➖ 2, 4 ✖️ 2, 8 ➗ 2
    • Functions: 🖨️("Hello"), 📏([1,2,3])
    • Decorators: @⏱️, @🛡️, @💾
    
    Type 'help()' for more info, 'exit()' to quit
🐍 {'='*50} 🐍
"""
        return banner

def emoji_exec(code_str: str, globals_dict: Dict[str, Any] = None):
    """Execute emoji Python code with enhanced features.
    
    Args:
        code_str: Emoji Python code to execute
        globals_dict: Global namespace
    """
    if globals_dict is None:
        globals_dict = {}
    
    # Add emoji built-ins
    globals_dict.update(EMOJI_BUILTINS)
    
    # Transform the code
    code_str = transform_emoji_operators(code_str)
    code_str = transform_emoji_keywords(code_str)
    
    # Execute
    return exec_emoji_code(code_str, globals_dict)

def start_emoji_repl():
    """Start the emoji Python REPL."""
    repl = EmojiREPL()
    
    # Add some helpful functions to the namespace
    repl.locals.update({
        'help': lambda: print(get_help_text()),
        'emoji_help': lambda: print(get_emoji_help()),
        'list_emojis': lambda: print(list_available_emojis()),
    })
    
    try:
        repl.interact()
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Goodbye from Emoji Python!")
        sys.exit(0)

def get_help_text():
    """Get help text for the emoji REPL."""
    return """
📚 Emoji Python Help
====================

Available Emoji Imports:
    🐼 → pandas       📊 → matplotlib    🔢 → numpy
    🌐 → flask        ⚡ → fastapi       📦 → json
    
Emoji Operators:
    ➕ → +    ➖ → -    ✖️ → *    ➗ → /
    🟰 → ==   ≠ → !=   📈 → >=   📉 → <=
    
Emoji Functions:
    🖨️() → print()    📥() → input()     📏() → len()
    🔢() → int()      💯() → float()     📝() → str()
    
Emoji Decorators:
    @⏱️ → Time execution
    @🛡️ → Exception protection
    @💾 → Cache results
    @📝 → Log calls
    
Type 'emoji_help()' for emoji reference
Type 'list_emojis()' for all available emojis
"""

def get_emoji_help():
    """Get emoji reference guide."""
    return """
🎨 Emoji Reference Guide
========================

📦 Modules & Imports:
    import 🐼           # Import pandas
    from 📊 import plt  # Import from matplotlib
    import 📦 as j      # Import json with alias

🔢 Math & Operations:
    x ➕ y    # Addition
    x ➖ y    # Subtraction  
    x ✖️ y    # Multiplication
    x ➗ y    # Division
    x 💪 y    # Power (x ** y)

🔄 Control Flow:
    ❓ condition:       # if
    🤷 condition:       # elif
    🙅:                 # else
    🔁 x in items:      # for
    🔄 condition:       # while

📝 Functions & Classes:
    📝 my_func():       # def
    🏛️ MyClass:        # class
    🔙 value           # return
    
🎯 Decorators:
    @⏱️  # Time function
    @🛡️  # Catch exceptions
    @💾  # Cache results
    @📝  # Log calls
    @🎨  # Pretty print results
"""

def list_available_emojis():
    """List all available emoji mappings."""
    from .mappings import get_all_mappings
    
    mappings = get_all_mappings()
    result = "📋 Available Emoji Mappings:\n"
    result += "=" * 40 + "\n"
    
    categories = {
        'Data Science': ['🐼', '📊', '🔢', '🧮', '📈'],
        'Web': ['🌐', '⚡', '🚀'],
        'Utils': ['📦', '📅', '🔍', '🎲'],
    }
    
    for category, emojis in categories.items():
        result += f"\n{category}:\n"
        for emoji in emojis:
            if emoji in mappings:
                result += f"  {emoji} → {mappings[emoji]}\n"
    
    return result

# Make it runnable as a module
if __name__ == "__main__":
    start_emoji_repl()