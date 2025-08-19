#!/usr/bin/env python
"""Simple demonstration that works with standard Python interpreter."""

from emojify_python import enable, emoji_import, exec_emoji_code

print("🐍 Emojify Python - Simple Demo")
print("=" * 40)

# Enable emoji imports
print("\n✅ Enabling emoji import system...")
enable()

# Method 1: Programmatic emoji imports
print("\n📦 Method 1: Programmatic imports")
print("-" * 30)

# Import modules using emoji_import function
json_module = emoji_import('📦')  # Import json as 📦
datetime_module = emoji_import('📅')  # Import datetime
random_module = emoji_import('🎲')  # Import random

print(f"json module: {json_module.__name__}")
print(f"datetime module: {datetime_module.__name__}")
print(f"random module: {random_module.__name__}")

# Use the imported modules
data = {"hello": "world", "emoji": "🎉"}
json_str = json_module.dumps(data)
print(f"\nJSON encoding: {json_str}")

current_time = datetime_module.datetime.now()
print(f"Current time: {current_time}")

random_num = random_module.randint(1, 100)
print(f"Random number: {random_num}")

# Method 2: Execute emoji code
print("\n🚀 Method 2: Execute emoji code")
print("-" * 30)

emoji_code = """
# This code uses emoji syntax!
import 📦
import 🎲

# Create emoji variables
🎯 = {"score": 🎲.randint(50, 100)}
📄 = 📦.dumps(🎯)

print(f"Generated data: {📄}")

# Emoji function
def 🔥(text):
    return f"🔥 {text.upper()} 🔥"

result = 🔥("awesome")
print(f"Fire function result: {result}")
"""

print("Executing emoji code...")
exec_emoji_code(emoji_code)

# Method 3: Context manager (for interactive use)
print("\n🎨 Method 3: Context manager example")
print("-" * 30)

from emojify_python import emojified

with emojified():
    # Import using the context
    json_ctx = emoji_import('📦')
    test_data = {"context": "manager", "works": True}
    print(f"Context manager test: {json_ctx.dumps(test_data)}")

print("\n✨ Demo complete! All methods work! ✨")