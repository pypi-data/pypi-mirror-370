"""Command-line interface for emoji Python."""

import sys
import argparse
from pathlib import Path
from .core import enable, exec_emoji_code, view_mappings, add_mapping
from .file_support import EmojiFileLoader, create_emoji_launcher, EmojiRequirements
from .repl import EmojiREPL
from .enhanced import create_emoji_project, EMOJI_TEMPLATES

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='🐍 Emoji Python - The Ultimate Emoji Programming Experience',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  emoji-python hello.emoji          # Run an emoji file
  emoji-python -c "import 🐼"       # Execute emoji code
  emoji-python -i                   # Interactive REPL
  emoji-python list                 # List emoji mappings
  emoji-python add 🎮 pygame        # Add custom mapping
  emoji-python compile hello.emoji  # Compile to regular Python
  emoji-python project myapp        # Create new emoji project
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Run command (default)
    run_parser = subparsers.add_parser('run', help='Run an emoji Python file')
    run_parser.add_argument('file', help='Emoji Python file to run')
    run_parser.add_argument('args', nargs='*', help='Arguments to pass to the script')
    
    # Execute command
    exec_parser = subparsers.add_parser('exec', help='Execute emoji Python code')
    exec_parser.add_argument('code', help='Emoji Python code to execute')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('repl', help='Start interactive REPL')
    interactive_parser.add_argument('--theme', choices=['dark', 'light'], default='dark',
                                   help='Color theme for REPL')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List emoji mappings')
    list_parser.add_argument('-c', '--category', help='Filter by category')
    
    # Add mapping command
    add_parser = subparsers.add_parser('add', help='Add custom emoji mapping')
    add_parser.add_argument('emoji', help='Emoji character')
    add_parser.add_argument('module', help='Module name')
    add_parser.add_argument('--persist', action='store_true', help='Save as default')
    
    # Compile command
    compile_parser = subparsers.add_parser('compile', help='Compile emoji file to Python')
    compile_parser.add_argument('file', help='Emoji file to compile')
    compile_parser.add_argument('-o', '--output', help='Output file')
    
    # Project command
    project_parser = subparsers.add_parser('project', help='Create new emoji project')
    project_parser.add_argument('name', help='Project name')
    project_parser.add_argument('-t', '--template', 
                               choices=list(EMOJI_TEMPLATES.keys()),
                               default='hello_world',
                               help='Project template')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install emoji requirements')
    install_parser.add_argument('file', nargs='?', default='requirements.emoji',
                               help='Emoji requirements file')
    
    # Launcher command
    launcher_parser = subparsers.add_parser('launcher', help='Create emoji-python launcher')
    
    # Handle direct file execution
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        # Check if first argument is a file
        if Path(sys.argv[1]).exists() or any(Path(sys.argv[1] + ext).exists() 
                                            for ext in EmojiFileLoader.EMOJI_EXTENSIONS):
            # Insert 'run' command
            sys.argv.insert(1, 'run')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Enable emoji imports
    enable()
    
    # Execute command
    if args.command == 'run' or (hasattr(args, 'file') and not args.command):
        # Run emoji file
        try:
            sys.argv = [args.file] + (args.args if hasattr(args, 'args') else [])
            EmojiFileLoader.load_emoji_file(args.file)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == 'exec':
        # Execute emoji code
        try:
            exec_emoji_code(args.code)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == 'repl':
        # Interactive REPL
        print("🐍 Emoji Python Interactive Mode")
        print("Type 'help()' for help, 'exit()' to quit")
        repl = EmojiREPL()
        repl.run()
    
    elif args.command == 'list':
        # List mappings
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
    
    elif args.command == 'add':
        # Add custom mapping
        add_mapping(args.emoji, args.module, persist=args.persist)
        print(f"✅ Added mapping: {args.emoji} → {args.module}")
        if args.persist:
            print("💾 Saved as default mapping")
    
    elif args.command == 'compile':
        # Compile emoji file
        try:
            output = EmojiFileLoader.compile_emoji_file(args.file, args.output)
            print(f"✅ Compiled to: {output}")
        except Exception as e:
            print(f"❌ Compilation failed: {e}")
            sys.exit(1)
    
    elif args.command == 'project':
        # Create new project
        create_emoji_project(args.name, args.template)
    
    elif args.command == 'install':
        # Install emoji requirements
        try:
            EmojiRequirements.install_emoji_requirements(args.file)
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            sys.exit(1)
    
    elif args.command == 'launcher':
        # Create launcher
        launcher_path = create_emoji_launcher()
        print(f"✅ Created launcher: {launcher_path}")
        print(f"💡 Add to PATH: export PATH=\"{Path(launcher_path).parent}:$PATH\"")
    
    else:
        # No command - show help
        parser.print_help()

if __name__ == '__main__':
    main()