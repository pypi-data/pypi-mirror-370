"""Jupyter notebook magic commands for emoji Python."""

try:
    from IPython.core.magic import Magics, magics_class, line_magic, cell_magic
    from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
    from IPython import get_ipython
    JUPYTER_AVAILABLE = True
except ImportError:
    JUPYTER_AVAILABLE = False
    # Dummy classes for when Jupyter is not available
    class Magics:
        pass
    def magics_class(cls):
        return cls
    def line_magic(func):
        return func
    def cell_magic(func):
        return func

from .core import exec_emoji_code, enable, disable
from .enhanced import print_emoji_code
from .mappings import view_mappings, add_custom_mapping

@magics_class
class EmojiMagics(Magics):
    """Jupyter magic commands for emoji Python."""
    
    def __init__(self, shell=None):
        super().__init__(shell)
        self.emoji_enabled = False
    
    @line_magic
    @magic_arguments()
    @argument('emoji', help='The emoji to map')
    @argument('module', help='The module name')
    def emoji_map(self, line):
        """Map an emoji to a module.
        
        Usage:
            %emoji_map 🎮 pygame
        """
        args = parse_argstring(self.emoji_map, line)
        add_custom_mapping(args.emoji, args.module)
        print(f"✅ Mapped {args.emoji} → {args.module}")
    
    @line_magic
    def emoji_on(self, line):
        """Enable emoji imports for the notebook.
        
        Usage:
            %emoji_on
        """
        enable()
        self.emoji_enabled = True
        print("✅ Emoji imports enabled")
    
    @line_magic
    def emoji_off(self, line):
        """Disable emoji imports for the notebook.
        
        Usage:
            %emoji_off
        """
        disable()
        self.emoji_enabled = False
        print("❌ Emoji imports disabled")
    
    @line_magic
    @magic_arguments()
    @argument('-c', '--category', help='Filter by category (data, web, util)')
    def emoji_list(self, line):
        """List available emoji mappings.
        
        Usage:
            %emoji_list
            %emoji_list -c data
        """
        args = parse_argstring(self.emoji_list, line)
        mappings = view_mappings(category=args.category)
        
        if args.category:
            print(f"📚 Emoji mappings for category: {args.category}")
        else:
            print("📚 All emoji mappings:")
        
        print("-" * 40)
        for emoji, module in sorted(mappings.items()):
            print(f"  {emoji} → {module}")
        print("-" * 40)
        print(f"Total: {len(mappings)} mappings")
    
    @cell_magic
    @magic_arguments()
    @argument('-v', '--verbose', action='store_true', help='Show transformed code')
    @argument('-h', '--highlight', action='store_true', help='Syntax highlight the code')
    def emoji(self, line, cell):
        """Execute a cell with emoji Python syntax.
        
        Usage:
            %%emoji
            import 🐼
            🎲 = 🐼.DataFrame({'data': [1, 2, 3]})
            print(🎲)
        """
        args = parse_argstring(self.emoji, line)
        
        if args.highlight:
            print("📝 Emoji code:")
            print_emoji_code(cell)
            print()
        
        if args.verbose:
            from .transformer import transform_source
            transformed, mappings = transform_source(cell)
            print("🔄 Transformed code:")
            print(transformed)
            print()
            print("📖 Emoji mappings:")
            for emoji, name in mappings.items():
                print(f"  {emoji} → {name}")
            print()
        
        # Execute the emoji code
        result = exec_emoji_code(cell, self.shell.user_ns)
        
        # Update notebook namespace with results
        if isinstance(result, dict):
            self.shell.user_ns.update(result)
    
    @cell_magic
    def emoji_debug(self, line, cell):
        """Debug emoji Python code with step-by-step execution.
        
        Usage:
            %%emoji_debug
            import 🐼
            🎲 = [1, 2, 3]
        """
        import ast
        from .transformer import transform_source
        
        print("🔍 Debugging emoji code...")
        print("=" * 40)
        
        # Transform the code
        transformed, mappings = transform_source(cell)
        
        # Parse into AST
        tree = ast.parse(transformed)
        
        # Execute line by line
        for i, node in enumerate(ast.walk(tree)):
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign)):
                print(f"\n📍 Line {i+1}:")
                print(f"  Type: {node.__class__.__name__}")
                
                # Show the transformation
                if hasattr(node, 'lineno'):
                    original_lines = cell.split('\n')
                    if node.lineno <= len(original_lines):
                        print(f"  Original: {original_lines[node.lineno-1].strip()}")
                
                # Execute the node
                try:
                    code_obj = compile(ast.Module(body=[node], type_ignores=[]), '<emoji>', 'exec')
                    exec(code_obj, self.shell.user_ns)
                    print("  ✅ Executed successfully")
                except Exception as e:
                    print(f"  ❌ Error: {e}")
        
        print("\n" + "=" * 40)
        print("✅ Debug complete")
    
    @line_magic
    def emoji_test(self, line):
        """Run emoji Python tests.
        
        Usage:
            %emoji_test
        """
        test_code = """
import 🐼
import 📦
import 🎲

# Test basic imports
assert 🐼.__name__ == 'pandas'
assert 📦.__name__ == 'json'
assert 🎲.__name__ == 'random'

# Test emoji variables
🎯 = 42
🎨 = "art"
📊 = [1, 2, 3]

assert 🎯 == 42
assert 🎨 == "art"
assert 📊 == [1, 2, 3]

print("✅ All tests passed!")
"""
        
        print("🧪 Running emoji tests...")
        try:
            exec_emoji_code(test_code)
        except Exception as e:
            print(f"❌ Test failed: {e}")

def load_jupyter_extension(ipython):
    """Load the emoji extension in Jupyter."""
    if not JUPYTER_AVAILABLE:
        print("⚠️ Jupyter/IPython not available")
        return
    
    ipython.register_magics(EmojiMagics)
    print("🎉 Emoji Python magic commands loaded!")
    print("Use %emoji_on to enable, %%emoji for cells")

def install_jupyter_magic():
    """Install emoji magic commands in current Jupyter session."""
    if not JUPYTER_AVAILABLE:
        print("⚠️ This feature requires Jupyter/IPython")
        return False
    
    ip = get_ipython()
    if ip is None:
        print("⚠️ Not running in IPython/Jupyter")
        return False
    
    load_jupyter_extension(ip)
    return True

# Auto-install if running in Jupyter
if JUPYTER_AVAILABLE:
    ip = get_ipython()
    if ip is not None and 'IPKernelApp' in ip.config:
        # We're in a Jupyter notebook
        install_jupyter_magic()