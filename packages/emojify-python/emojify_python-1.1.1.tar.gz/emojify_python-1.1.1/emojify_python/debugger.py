"""Enhanced debugging and error handling for emoji Python."""

import sys
import traceback
import ast
from typing import Dict, List, Tuple, Optional, Any
import re
import linecache
from pathlib import Path

class EmojiDebugger:
    """Advanced debugger for emoji Python code."""
    
    def __init__(self):
        self.breakpoints: Dict[str, List[int]] = {}
        self.watch_expressions: List[str] = []
        self.step_mode = False
        self.emoji_to_source: Dict[str, str] = {}
        self.source_to_emoji: Dict[str, str] = {}
    
    def set_breakpoint(self, filename: str, line: int):
        """Set a breakpoint at a specific line."""
        if filename not in self.breakpoints:
            self.breakpoints[filename] = []
        self.breakpoints[filename].append(line)
    
    def add_watch(self, expression: str):
        """Add an expression to watch during debugging."""
        self.watch_expressions.append(expression)
    
    def trace_emoji_code(self, code: str, globals_dict: Dict = None):
        """Trace execution of emoji code."""
        from .transformer import transform_source
        
        # Transform the code
        transformed, mappings = transform_source(code)
        
        # Store mappings for error reporting
        self.emoji_to_source = mappings
        self.source_to_emoji = {v: k for k, v in mappings.items()}
        
        # Parse the code
        tree = ast.parse(transformed)
        
        # Add debugging instrumentation
        instrumented = self._instrument_ast(tree)
        
        # Execute with tracing
        if globals_dict is None:
            globals_dict = {}
        
        old_trace = sys.gettrace()
        sys.settrace(self._trace_function)
        
        try:
            exec(compile(instrumented, '<emoji_debug>', 'exec'), globals_dict)
        finally:
            sys.settrace(old_trace)
    
    def _instrument_ast(self, tree: ast.AST) -> ast.AST:
        """Add debugging instrumentation to AST."""
        
        class DebugTransformer(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                # Add debug print at function entry
                debug_stmt = ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id='print', ctx=ast.Load()),
                        args=[ast.Constant(value=f"🔍 Entering function: {node.name}")],
                        keywords=[]
                    )
                )
                node.body.insert(0, debug_stmt)
                return node
        
        transformer = DebugTransformer()
        return transformer.visit(tree)
    
    def _trace_function(self, frame, event, arg):
        """Trace function for debugging."""
        if event == 'line':
            # Check breakpoints
            filename = frame.f_code.co_filename
            line_no = frame.f_lineno
            
            if filename in self.breakpoints and line_no in self.breakpoints[filename]:
                print(f"🔴 Breakpoint hit at {filename}:{line_no}")
                self._debug_prompt(frame)
            
            # Watch expressions
            for expr in self.watch_expressions:
                try:
                    value = eval(expr, frame.f_globals, frame.f_locals)
                    print(f"👁️ Watch: {expr} = {value}")
                except:
                    pass
        
        elif event == 'exception':
            exc_type, exc_value, exc_tb = arg
            self._handle_emoji_exception(exc_type, exc_value, exc_tb, frame)
        
        return self._trace_function
    
    def _debug_prompt(self, frame):
        """Interactive debug prompt."""
        while True:
            try:
                cmd = input("🔍 (emoji-debug) ")
                
                if cmd == 'c' or cmd == 'continue':
                    break
                elif cmd == 'n' or cmd == 'next':
                    self.step_mode = True
                    break
                elif cmd == 'l' or cmd == 'locals':
                    print("📦 Local variables:")
                    for name, value in frame.f_locals.items():
                        emoji_name = self.source_to_emoji.get(name, name)
                        print(f"  {emoji_name} = {value}")
                elif cmd.startswith('p '):
                    # Print expression
                    expr = cmd[2:]
                    try:
                        value = eval(expr, frame.f_globals, frame.f_locals)
                        print(f"  {expr} = {value}")
                    except Exception as e:
                        print(f"  ❌ Error: {e}")
                elif cmd == 'bt' or cmd == 'backtrace':
                    self._print_backtrace(frame)
                elif cmd == 'h' or cmd == 'help':
                    print("🔍 Debug commands:")
                    print("  c/continue - Continue execution")
                    print("  n/next - Step to next line")
                    print("  l/locals - Show local variables")
                    print("  p <expr> - Print expression")
                    print("  bt/backtrace - Show call stack")
                    print("  h/help - Show this help")
            except KeyboardInterrupt:
                break
    
    def _print_backtrace(self, frame):
        """Print the call stack with emoji symbols."""
        print("📚 Call stack:")
        current = frame
        level = 0
        
        while current is not None:
            func_name = current.f_code.co_name
            filename = current.f_code.co_filename
            line_no = current.f_lineno
            
            # Try to get emoji name
            emoji_func = self.source_to_emoji.get(func_name, func_name)
            
            print(f"  #{level}: {emoji_func} at {filename}:{line_no}")
            current = current.f_back
            level += 1
    
    def _handle_emoji_exception(self, exc_type, exc_value, exc_tb, frame):
        """Handle exceptions with emoji context."""
        print("\n" + "=" * 50)
        print("💥 Emoji Python Exception Occurred!")
        print("=" * 50)
        
        # Show exception type with emoji
        emoji_types = {
            SyntaxError: "📝",
            ImportError: "📦",
            NameError: "📛",
            TypeError: "🔧",
            ValueError: "🔢",
            KeyError: "🔑",
            IndexError: "📍",
            AttributeError: "🏷️",
        }
        
        emoji = emoji_types.get(exc_type, "❌")
        print(f"\n{emoji} {exc_type.__name__}: {exc_value}")
        
        # Show the emoji code that caused the error
        if exc_tb:
            print("\n📍 Location in emoji code:")
            tb_frame = exc_tb.tb_frame
            line_no = exc_tb.tb_lineno
            
            # Try to show the original emoji code
            print(f"  Line {line_no}")
            
            # Show local variables with emoji names
            print("\n📦 Variables at error:")
            for name, value in tb_frame.f_locals.items():
                emoji_name = self.source_to_emoji.get(name, name)
                print(f"  {emoji_name} = {repr(value)[:50]}")
        
        print("\n💡 Debugging tips:")
        if exc_type == ImportError:
            print("  • Check emoji mappings with view_mappings()")
            print("  • Ensure the module is installed")
        elif exc_type == NameError:
            print("  • Check if the emoji variable is defined")
            print("  • Use emoji_list() to see available emojis")
        
        print("=" * 50)

class EmojiErrorFormatter:
    """Format errors with emoji context."""
    
    @staticmethod
    def format_exception(exc_type, exc_value, exc_tb, emoji_mappings: Dict[str, str] = None):
        """Format an exception with emoji symbols."""
        lines = []
        
        # Header
        lines.append("🚨 Emoji Python Error 🚨")
        lines.append("=" * 40)
        
        # Exception info
        emoji = EmojiErrorFormatter._get_emoji_for_exception(exc_type)
        lines.append(f"{emoji} {exc_type.__name__}: {exc_value}")
        lines.append("")
        
        # Traceback with emoji
        if exc_tb:
            lines.append("📚 Traceback (most recent emoji call last):")
            
            tb_lines = traceback.format_tb(exc_tb)
            for tb_line in tb_lines:
                # Try to replace identifiers with emojis
                if emoji_mappings:
                    for source, emoji in emoji_mappings.items():
                        tb_line = tb_line.replace(source, emoji)
                lines.append("  " + tb_line.strip())
        
        # Helpful suggestions
        lines.append("")
        lines.append("💡 Suggestions:")
        lines.extend(EmojiErrorFormatter._get_suggestions(exc_type, exc_value))
        
        return "\n".join(lines)
    
    @staticmethod
    def _get_emoji_for_exception(exc_type):
        """Get emoji representation for exception type."""
        return {
            SyntaxError: "📝",
            ImportError: "📦",
            ModuleNotFoundError: "🔍",
            NameError: "📛",
            TypeError: "🔧",
            ValueError: "🔢",
            KeyError: "🔑",
            IndexError: "📍",
            AttributeError: "🏷️",
            ZeroDivisionError: "0️⃣",
            FileNotFoundError: "📁",
            PermissionError: "🔒",
            RuntimeError: "🏃",
            MemoryError: "💾",
            RecursionError: "🔄",
            KeyboardInterrupt: "⌨️",
        }.get(exc_type, "❌")
    
    @staticmethod
    def _get_suggestions(exc_type, exc_value):
        """Get helpful suggestions for common errors."""
        suggestions = []
        
        if exc_type in (ImportError, ModuleNotFoundError):
            module_name = str(exc_value).split("'")[1] if "'" in str(exc_value) else ""
            suggestions.append(f"  • Check if '{module_name}' is installed: pip install {module_name}")
            suggestions.append("  • View available emoji mappings: view_mappings()")
            suggestions.append("  • Add custom mapping: add_mapping('🎮', 'pygame')")
        
        elif exc_type == NameError:
            name = str(exc_value).split("'")[1] if "'" in str(exc_value) else ""
            suggestions.append(f"  • Define the variable: {name} = ...")
            suggestions.append("  • Check for typos in the emoji")
            suggestions.append("  • Import the module first")
        
        elif exc_type == SyntaxError:
            suggestions.append("  • Check emoji syntax")
            suggestions.append("  • Ensure proper indentation")
            suggestions.append("  • Verify emoji operators are supported")
        
        elif exc_type == TypeError:
            suggestions.append("  • Check argument types")
            suggestions.append("  • Verify emoji function signatures")
            suggestions.append("  • Use correct emoji operators")
        
        return suggestions

def install_emoji_debugger():
    """Install the emoji debugger as the default exception handler."""
    
    def emoji_excepthook(exc_type, exc_value, exc_tb):
        """Custom exception hook with emoji formatting."""
        formatted = EmojiErrorFormatter.format_exception(exc_type, exc_value, exc_tb)
        print(formatted, file=sys.stderr)
    
    sys.excepthook = emoji_excepthook

# Global debugger instance
_debugger = None

def get_debugger() -> EmojiDebugger:
    """Get or create the global debugger instance."""
    global _debugger
    if _debugger is None:
        _debugger = EmojiDebugger()
    return _debugger

def debug_emoji_code(code: str, breakpoints: List[int] = None):
    """Debug emoji code with breakpoints."""
    debugger = get_debugger()
    
    if breakpoints:
        for line in breakpoints:
            debugger.set_breakpoint('<emoji>', line)
    
    debugger.trace_emoji_code(code)