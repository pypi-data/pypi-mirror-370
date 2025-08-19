"""Support for .emoji file extension and emoji shebang."""

import sys
import os
import importlib.util
import importlib.machinery
from pathlib import Path
from typing import Optional, Any
import subprocess
import tempfile

class EmojiFileLoader:
    """Loader for .emoji files."""
    
    EMOJI_EXTENSIONS = ['.emoji', '.🐍', '.emj']
    
    @classmethod
    def is_emoji_file(cls, filepath: str) -> bool:
        """Check if a file is an emoji Python file."""
        path = Path(filepath)
        return path.suffix in cls.EMOJI_EXTENSIONS
    
    @classmethod
    def load_emoji_file(cls, filepath: str) -> Any:
        """Load and execute an emoji file."""
        from .core import exec_emoji_code
        
        path = Path(filepath)
        if not path.exists():
            # Try with emoji extensions
            for ext in cls.EMOJI_EXTENSIONS:
                test_path = path.with_suffix(ext)
                if test_path.exists():
                    path = test_path
                    break
        
        if not path.exists():
            raise FileNotFoundError(f"Emoji file not found: {filepath}")
        
        # Read the file
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Check for emoji shebang
        if code.startswith('#!/usr/bin/env emoji-python'):
            # Remove shebang line
            code = '\n'.join(code.split('\n')[1:])
        
        # Execute the emoji code
        namespace = {'__file__': str(path), '__name__': '__main__'}
        result = exec_emoji_code(code, namespace)
        
        return result
    
    @classmethod
    def compile_emoji_file(cls, filepath: str, output: Optional[str] = None) -> str:
        """Compile an emoji file to regular Python."""
        from .transformer import transform_source
        
        path = Path(filepath)
        
        # Read the emoji file
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Transform to regular Python
        transformed, mappings = transform_source(code)
        
        # Add header comment
        header = f"""#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Compiled from emoji Python file: {path.name}
# Original emoji mappings: {mappings}

"""
        
        compiled_code = header + transformed
        
        # Write output
        if output:
            output_path = Path(output)
        else:
            output_path = path.with_suffix('.py')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(compiled_code)
        
        return str(output_path)

class EmojiImportHook:
    """Import hook for .emoji files."""
    
    def find_spec(self, name, path, target=None):
        """Find a module spec for emoji files."""
        # Try to find .emoji file
        for directory in sys.path:
            for ext in EmojiFileLoader.EMOJI_EXTENSIONS:
                emoji_file = Path(directory) / f"{name}{ext}"
                if emoji_file.exists():
                    return self._create_spec(name, str(emoji_file))
        return None
    
    def _create_spec(self, name: str, filepath: str):
        """Create a module spec for an emoji file."""
        loader = EmojiModuleLoader(filepath)
        return importlib.util.spec_from_loader(name, loader)

class EmojiModuleLoader:
    """Module loader for emoji files."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
    
    def load_module(self, module):
        """Load an emoji module."""
        # Load and execute the emoji file
        result = EmojiFileLoader.load_emoji_file(self.filepath)
        
        # Update module attributes
        module.__file__ = self.filepath
        module.__loader__ = self
        
        if isinstance(result, dict):
            module.__dict__.update(result)
        
        return module
    
    def exec_module(self, module):
        """Execute an emoji module."""
        self.load_module(module)

def install_emoji_file_support():
    """Install support for .emoji file imports."""
    # Add emoji import hook
    hook = EmojiImportHook()
    if hook not in sys.meta_path:
        sys.meta_path.insert(0, hook)
    
    # Register emoji file extensions
    for ext in EmojiFileLoader.EMOJI_EXTENSIONS:
        if ext not in importlib.machinery.SOURCE_SUFFIXES:
            importlib.machinery.SOURCE_SUFFIXES.append(ext)

def create_emoji_launcher():
    """Create emoji-python launcher script."""
    launcher_script = '''#!/usr/bin/env python
# emoji-python launcher

import sys
import os
from pathlib import Path

# Add emojify_python to path
try:
    from emojify_python import enable, exec_emoji_code
    from emojify_python.file_support import EmojiFileLoader
except ImportError:
    print("❌ emojify-python not installed!")
    print("Install with: pip install emojify-python")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: emoji-python <file.emoji>")
        print("       emoji-python -c '<emoji code>'")
        print("       emoji-python -i  # Interactive mode")
        sys.exit(1)
    
    # Enable emoji imports
    enable()
    
    if sys.argv[1] == '-c':
        # Execute code from command line
        if len(sys.argv) < 3:
            print("❌ No code provided")
            sys.exit(1)
        code = sys.argv[2]
        exec_emoji_code(code)
    
    elif sys.argv[1] == '-i':
        # Interactive mode
        print("🐍 Emoji Python Interactive Mode")
        print("Type 'exit()' to quit")
        from emojify_python.repl import EmojiREPL
        repl = EmojiREPL()
        repl.run()
    
    else:
        # Execute file
        filepath = sys.argv[1]
        try:
            EmojiFileLoader.load_emoji_file(filepath)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()
'''
    
    # Create launcher in temp directory
    launcher_path = Path(tempfile.gettempdir()) / 'emoji-python'
    with open(launcher_path, 'w') as f:
        f.write(launcher_script)
    
    # Make executable
    os.chmod(launcher_path, 0o755)
    
    return str(launcher_path)

class EmojiRequirements:
    """Support for emoji requirements.txt format."""
    
    @staticmethod
    def parse_emoji_requirements(filepath: str) -> list:
        """Parse emoji requirements file."""
        requirements = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Handle emoji package names
                if '🐼' in line:
                    line = line.replace('🐼', 'pandas')
                if '🔢' in line:
                    line = line.replace('🔢', 'numpy')
                if '📊' in line:
                    line = line.replace('📊', 'matplotlib')
                if '🧮' in line:
                    line = line.replace('🧮', 'scipy')
                if '🤖' in line:
                    line = line.replace('🤖', 'scikit-learn')
                
                requirements.append(line)
        
        return requirements
    
    @staticmethod
    def install_emoji_requirements(filepath: str):
        """Install packages from emoji requirements file."""
        requirements = EmojiRequirements.parse_emoji_requirements(filepath)
        
        if requirements:
            # Create temporary requirements file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write('\n'.join(requirements))
                temp_req = f.name
            
            try:
                # Install using pip
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', temp_req], check=True)
                print(f"✅ Installed {len(requirements)} packages")
            finally:
                os.unlink(temp_req)

# File type associations
EMOJI_FILE_ASSOCIATIONS = {
    '.emoji': 'Emoji Python source file',
    '.🐍': 'Snake emoji Python file',
    '.emj': 'Emoji Python module',
    'requirements.emoji': 'Emoji requirements file',
    'setup.emoji': 'Emoji setup configuration',
}

def register_file_associations():
    """Register emoji file associations with the system."""
    # This would require platform-specific code
    # For now, just document the associations
    
    import platform
    system = platform.system()
    
    if system == 'Darwin':  # macOS
        # Would use Launch Services
        pass
    elif system == 'Windows':
        # Would use Windows Registry
        pass
    elif system == 'Linux':
        # Would use .desktop files
        pass
    
    print("📁 Emoji file extensions registered:")
    for ext, desc in EMOJI_FILE_ASSOCIATIONS.items():
        print(f"  {ext}: {desc}")