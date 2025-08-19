#!/usr/bin/env python
"""Basic demonstration of emojify-python capabilities."""

from emojify_python import enable, add_mapping, exec_emoji_code

# Enable emoji imports
print("🎉 Enabling emoji imports...")
enable()

# Since Python doesn't natively support emoji imports, 
# we'll use exec_emoji_code for the demonstration
code = '''
# Standard library imports with emojis
print("\\n📦 Importing standard libraries with emojis...")
import 📦  # json
import 📅  # datetime
import 🎲  # random
import 🔍  # re

# Using emoji aliases
print("\n🔄 Using emoji aliases...")
import json as 📋
import random as 🎰
import datetime as ⏰

# Emoji variables
print("\n🎯 Creating emoji variables...")
🎪 = "Welcome to Emoji Python!"
🔢 = [1, 2, 3, 4, 5]
🗂️ = {"name": "Emoji", "version": "1.0"}

print(f"String: {🎪}")
print(f"List: {🔢}")
print(f"Dict: {🗂️}")

# Emoji functions
print("\n🚀 Defining emoji functions...")
def 🎯(x, y):
    """Add two numbers."""
    return x + y

def 🔥(text):
    """Make text uppercase and exciting!"""
    return f"🔥 {text.upper()} 🔥"

print(f"🎯(5, 3) = {🎯(5, 3)}")
print(f"🔥('hello') = {🔥('hello')}")

# Emoji classes
print("\n🏠 Creating emoji classes...")
class 🏠:
    """A house class with emoji methods."""
    
    def __init__(self):
        self.🔑 = "secret_key"
        self.🚪 = "closed"
    
    def 🔓(self):
        """Unlock the house."""
        self.🚪 = "open"
        return f"House unlocked with {self.🔑}"
    
    def 🔒(self):
        """Lock the house."""
        self.🚪 = "closed"
        return "House locked"

🏡 = 🏠()
print(f"House door is: {🏡.🚪}")
print(🏡.🔓())
print(f"House door is now: {🏡.🚪}")

# Working with JSON using emojis
print("\n📦 Working with JSON...")
📝 = {"users": ["Alice", "Bob"], "count": 2}
📄 = 📦.dumps(📝, indent=2)
print(f"JSON string:\n{📄}")

# Working with dates using emojis
print("\n📅 Working with dates...")
🕐 = 📅.datetime.now()
print(f"Current time: {🕐}")
🎂 = 📅.datetime(2024, 1, 1)
print(f"New Year 2024: {🎂}")

# Random operations with emojis
print("\n🎲 Random operations...")
🎰 = 🎲.randint(1, 100)
print(f"Random number: {🎰}")
🃏 = 🎲.choice(['♠️', '♥️', '♦️', '♣️'])
print(f"Random card suit: {🃏}")

# Regular expressions with emojis
print("\n🔍 Regular expressions...")
📋 = "Hello123World456"
🔢_pattern = 🔍.compile(r'\d+')
🔢_found = 🔢_pattern.findall(📋)
print(f"Numbers found in '{📋}': {🔢_found}")

# Custom mapping example
print("\n🎨 Adding custom emoji mapping...")
add_mapping('💡', 'collections')
import 💡
🗂️ = 💡.Counter(['a', 'b', 'c', 'a', 'b', 'a'])
print(f"Counter result: {dict(🗂️)}")

print("\n✅ Demo complete! Emoji Python is working! 🎉")