"""Enhanced error handling with emoji context."""

import sys
import traceback
from typing import Optional, Any
import re

class EmojiError(Exception):
    """Base class for emoji-related errors."""
    
    def __init__(self, message: str, emoji: Optional[str] = None, hint: Optional[str] = None):
        self.emoji = emoji
        self.hint = hint
        self.original_message = message
        
        # Build formatted message
        formatted = f"\n{'='*60}\n"
        formatted += f"❌ Emoji Error: {message}\n"
        
        if emoji:
            formatted += f"📍 Problem emoji: {emoji}\n"
            
        if hint:
            formatted += f"💡 Hint: {hint}\n"
            
        formatted += f"{'='*60}"
        
        super().__init__(formatted)


class EmojiImportError(EmojiError):
    """Import-related emoji errors."""
    
    def __init__(self, emoji: str, attempted_module: str = None):
        message = f"Cannot import module with emoji '{emoji}'"
        hint = None
        
        if attempted_module:
            message += f" (tried to import '{attempted_module}')"
            
        # Provide helpful hints based on common issues
        if '️' in emoji:  # Has variation selector
            hint = "This emoji contains invisible characters. Try using a simpler version."
        elif emoji in ['🕰', '⏰', '🕐']:
            hint = "For time module, use ⏰ or import time directly"
        elif emoji == '🔢':
            hint = "🔢 maps to numpy. Make sure numpy is installed: pip install numpy"
        elif emoji == '🐼':
            hint = "🐼 maps to pandas. Make sure pandas is installed: pip install pandas"
        else:
            from .mappings import get_module_for_emoji
            module = get_module_for_emoji(emoji)
            if module:
                hint = f"This emoji maps to '{module}'. Make sure it's installed."
            else:
                hint = "This emoji has no mapping. Add a custom mapping with add_custom_mapping()"
                
        super().__init__(message, emoji, hint)


class EmojiSyntaxError(EmojiError):
    """Syntax-related emoji errors."""
    
    def __init__(self, message: str, code: str = None, line_no: int = None):
        hint = None
        emoji = None
        
        # Extract emoji from code if present
        if code:
            import re
            emojis = re.findall(r'[\U0001F000-\U0001F9FF]+', code)
            if emojis:
                emoji = emojis[0]
                
        # Provide syntax hints
        if 'invalid character' in message:
            hint = "Some emojis can't be used directly in Python. Use exec_emoji_code() instead."
        elif 'unexpected EOF' in message:
            hint = "Check for missing parentheses, brackets, or quotes."
        elif '➕' in str(code) or '➖' in str(code):
            hint = "Emoji operators need special handling. Use exec_emoji_code() for full support."
            
        if line_no:
            message = f"Line {line_no}: {message}"
            
        super().__init__(message, emoji, hint)


class EmojiRuntimeError(EmojiError):
    """Runtime emoji errors."""
    
    def __init__(self, message: str, context: dict = None):
        hint = None
        emoji = None
        
        if context:
            # Extract relevant context
            if 'emoji' in context:
                emoji = context['emoji']
            if 'suggestion' in context:
                hint = context['suggestion']
                
        super().__init__(message, emoji, hint)


def handle_emoji_error(func):
    """Decorator to handle and format emoji errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except EmojiError:
            # Re-raise our custom errors as-is
            raise
        except ImportError as e:
            # Check if it's emoji-related
            error_msg = str(e)
            if 'emoji_' in error_msg or any(ord(c) > 127 for c in error_msg):
                # Extract the problematic part
                import re
                match = re.search(r"'([^']+)'", error_msg)
                if match:
                    module_name = match.group(1)
                    if 'emoji_' in module_name:
                        # It's a transformed emoji name
                        raise EmojiImportError('?', module_name)
                raise EmojiImportError('?', error_msg)
            raise
        except SyntaxError as e:
            # Wrap syntax errors
            raise EmojiSyntaxError(str(e), getattr(e, 'text', None), getattr(e, 'lineno', None))
        except Exception as e:
            # Wrap other errors
            if any(ord(c) > 127 for c in str(e)):
                raise EmojiRuntimeError(str(e))
            raise
            
    return wrapper


class EmojiDebugger:
    """Enhanced debugger for emoji code."""
    
    def __init__(self):
        self.debug_mode = False
        self.trace = []
        
    def enable(self):
        """Enable debug mode."""
        self.debug_mode = True
        print("🐛 Emoji debugger enabled")
        
    def disable(self):
        """Disable debug mode."""
        self.debug_mode = False
        print("🐛 Emoji debugger disabled")
        
    def log(self, message: str, emoji: str = "📝"):
        """Log a debug message with emoji."""
        if self.debug_mode:
            print(f"{emoji} {message}")
            self.trace.append((emoji, message))
            
    def inspect(self, obj: Any, name: str = "object"):
        """Inspect an object with emoji formatting."""
        if not self.debug_mode:
            return
            
        print(f"\n🔍 Inspecting {name}:")
        print(f"  📦 Type: {type(obj).__name__}")
        print(f"  📏 Size: {sys.getsizeof(obj)} bytes")
        
        if hasattr(obj, '__dict__'):
            print(f"  🗂️ Attributes:")
            for key, value in obj.__dict__.items():
                print(f"    • {key}: {value}")
                
    def trace_emoji(self, code: str):
        """Trace emoji code execution."""
        if not self.debug_mode:
            return
            
        print(f"\n🔄 Tracing emoji code:")
        lines = code.strip().split('\n')
        for i, line in enumerate(lines, 1):
            if any(ord(c) > 127 for c in line):
                emojis = re.findall(r'[\U0001F000-\U0001F9FF]+', line)
                print(f"  {i:3d} | {line}")
                if emojis:
                    print(f"       └─ Emojis found: {', '.join(emojis)}")
                    
    def show_trace(self):
        """Show the debug trace."""
        if not self.trace:
            print("📭 No trace available")
            return
            
        print(f"\n📜 Debug Trace ({len(self.trace)} entries):")
        for emoji, message in self.trace:
            print(f"  {emoji} {message}")
            
    def clear_trace(self):
        """Clear the debug trace."""
        self.trace = []
        print("🗑️ Trace cleared")


# Global debugger instance
emoji_debugger = EmojiDebugger()


def format_emoji_traceback(exc_type, exc_value, exc_traceback):
    """Format traceback with emoji hints."""
    # Get standard traceback
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    
    # Add emoji context if available
    if isinstance(exc_value, EmojiError):
        # Already formatted
        return ''.join(tb_lines)
        
    # Check for emoji-related issues
    error_str = str(exc_value)
    if any(ord(c) > 127 for c in error_str):
        tb_lines.append("\n💡 Emoji Hint: This error involves emoji characters.\n")
        tb_lines.append("   Use exec_emoji_code() for proper emoji support.\n")
        
    return ''.join(tb_lines)


def install_emoji_error_handler():
    """Install the emoji error handler."""
    sys.excepthook = lambda *args: print(format_emoji_traceback(*args))
    

# Helpful error messages for common issues
EMOJI_ERROR_HINTS = {
    "invalid character": "Use exec_emoji_code() to run code with emojis",
    "No module named": "Check if the module is installed or if the emoji mapping is correct",
    "unexpected EOF": "Check for unclosed parentheses, brackets, or quotes",
    "invalid syntax": "Some emoji syntax needs special handling - use exec_emoji_code()",
    "NameError": "The emoji variable or function might not be defined yet",
    "TypeError": "Check if you're using the emoji operator correctly",
}