#!/usr/bin/env python
"""
🎯 Emojify Python - Complete Feature Showcase
==============================================
This example demonstrates all features of emojify-python v1.1.0
"""

from emojify_python import (
    enable, disable, exec_emoji_code, 
    add_custom_mapping, get_module_for_emoji,
    is_emoji, contains_emoji, extract_emojis
)

print("🌟 EMOJIFY PYTHON SHOWCASE 🌟")
print("=" * 50)

# ============================================
# 1. BASIC EMOJI IMPORTS
# ============================================
print("\n📦 1. EMOJI IMPORTS")
print("-" * 30)

code = """
# Import modules using emojis
import 🔢  # numpy
import 📐  # math
import 🎲  # random
import 📅  # datetime

# Use the imported modules
print(f"  π = {📐.pi:.4f}")
print(f"  e = {📐.e:.4f}")
print(f"  Random number: {🎲.randint(1, 100)}")
print(f"  Today: {📅.date.today()}")
"""

exec_emoji_code(code)

# ============================================
# 2. EMOJI VARIABLES & FUNCTIONS
# ============================================
print("\n🔤 2. EMOJI VARIABLES & FUNCTIONS")
print("-" * 30)

code = """
# Variables with emojis
🍎 = "apple"
🍌 = "banana"
🍊 = "orange"
🧺 = [🍎, 🍌, 🍊]

print(f"  Fruit basket 🧺: {🧺}")

# Functions with emoji names
def 🎯_calculate(x, y):
    '''Calculate target value'''
    return x * y + 10

def 🔮_predict(data):
    '''Make a prediction'''
    return sum(data) / len(data)

result = 🎯_calculate(5, 3)
prediction = 🔮_predict([10, 20, 30, 40])

print(f"  🎯 Calculation: {result}")
print(f"  🔮 Prediction: {prediction}")
"""

exec_emoji_code(code)

# ============================================
# 3. EMOJI CLASSES
# ============================================
print("\n🏗️ 3. EMOJI CLASSES")
print("-" * 30)

code = """
# Classes with emoji names and methods
class 🤖_Robot:
    def __init__(self, name):
        self.name = name
        self.🔋 = 100  # Battery level
        self.📍 = (0, 0)  # Position
        
    def 👋(self):
        return f"Hello! I'm {self.name}"
    
    def 🚶(self, x, y):
        self.📍 = (x, y)
        self.🔋 -= 5
        return f"Moved to {self.📍}, battery: {self.🔋}%"
    
    def 🔌(self):
        self.🔋 = 100
        return "Fully charged!"

# Create and use robot
robot = 🤖_Robot("EmojiBo ")
print(f"  {robot.👋()}")
print(f"  {robot.🚶(10, 20)}")
print(f"  {robot.🔌()}")
"""

exec_emoji_code(code)

# ============================================
# 4. EMOJI DECORATORS
# ============================================
print("\n🎨 4. EMOJI DECORATORS")
print("-" * 30)

code = """
import time
from functools import wraps

# Decorator with emoji name
def timer_⏱(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"  ⏱ {func.__name__} took {end-start:.4f}s")
        return result
    return wrapper

def 🎁_gift_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"  🎁 Wrapping {func.__name__}...")
        result = func(*args, **kwargs)
        print(f"  🎁 Unwrapped result: {result}")
        return result
    return wrapper

@timer_⏱
@🎁_gift_wrapper
def calculate_sum(n):
    return sum(range(n))

result = calculate_sum(10000)
"""

exec_emoji_code(code)

# ============================================
# 5. EMOJI TYPE HINTS
# ============================================
print("\n🔍 5. EMOJI TYPE HINTS")
print("-" * 30)

code = """
from typing import List, Dict, Optional

# Type aliases with emojis
📝 = str
🔢 = int
📋 = List
📚 = Dict
❓ = Optional

def process_data(
    name: 📝,
    age: 🔢,
    scores: 📋[🔢],
    metadata: ❓[📚] = None
) -> 📝:
    avg_score = sum(scores) / len(scores) if scores else 0
    result = f"{name} (age {age}): avg score {avg_score:.1f}"
    if metadata:
        result += f", metadata: {len(metadata)} items"
    return result

output = process_data(
    name="Alice",
    age=25,
    scores=[85, 90, 95],
    metadata={"level": "advanced"}
)
print(f"  {output}")
"""

exec_emoji_code(code)

# ============================================
# 6. EMOJI ERROR HANDLING
# ============================================
print("\n❌ 6. EMOJI ERROR HANDLING")
print("-" * 30)

code = """
# Custom exceptions with emojis
class 💥_BoomError(Exception):
    pass

class 🚫_ForbiddenError(Exception):
    pass

def risky_operation(value):
    if value < 0:
        raise 💥_BoomError("💥 Negative value not allowed!")
    elif value > 100:
        raise 🚫_ForbiddenError("🚫 Value too high!")
    return value * 2

# Test error handling
test_values = [50, -10, 150]
for val in test_values:
    try:
        result = risky_operation(val)
        print(f"  ✅ Success with {val}: {result}")
    except 💥_BoomError as e:
        print(f"  💥 Caught: {e}")
    except 🚫_ForbiddenError as e:
        print(f"  🚫 Caught: {e}")
"""

exec_emoji_code(code)

# ============================================
# 7. EMOJI COMPREHENSIONS
# ============================================
print("\n🔄 7. EMOJI COMPREHENSIONS")
print("-" * 30)

code = """
# List comprehensions with emoji variables
🔢_numbers = [1, 2, 3, 4, 5]
🔲_squares = [n**2 for n in 🔢_numbers]
🎯_filtered = [n for n in 🔢_numbers if n > 2]

print(f"  Numbers: {🔢_numbers}")
print(f"  Squares: {🔲_squares}")
print(f"  Filtered: {🎯_filtered}")

# Dictionary comprehension
🍎_fruits = ['apple', 'banana', 'orange']
🏷_labels = {fruit: f"🏷 {fruit.upper()}" for fruit in 🍎_fruits}
print(f"  Labels: {🏷_labels}")

# Generator with emojis
def 🔄_fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

fib_nums = list(🔄_fibonacci(8))
print(f"  Fibonacci: {fib_nums}")
"""

exec_emoji_code(code)

# ============================================
# 8. EMOJI CONTEXT MANAGERS
# ============================================
print("\n🔒 8. EMOJI CONTEXT MANAGERS")
print("-" * 30)

code = """
class 🔐_SecureContext:
    def __init__(self, name):
        self.name = name
        
    def __enter__(self):
        print(f"  🔐 Entering secure context: {self.name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"  🔓 Exiting secure context: {self.name}")
        
    def process(self, data):
        return f"Securely processed: {data}"

# Use the context manager
with 🔐_SecureContext("Database") as ctx:
    result = ctx.process("sensitive data")
    print(f"  {result}")
"""

exec_emoji_code(code)

# ============================================
# 9. EMOJI UTILITIES
# ============================================
print("\n🛠️ 9. EMOJI UTILITIES")
print("-" * 30)

# Test utility functions
test_string = "Python 🐍 is awesome 🚀!"
emoji_char = "🎯"
regular_char = "A"

print(f"  String: '{test_string}'")
print(f"  Contains emoji? {contains_emoji(test_string)}")
print(f"  Extracted emojis: {extract_emojis(test_string)}")
print(f"  Is '🎯' an emoji? {is_emoji(emoji_char)}")
print(f"  Is 'A' an emoji? {is_emoji(regular_char)}")

# ============================================
# 10. CUSTOM EMOJI MAPPINGS
# ============================================
print("\n🗺️ 10. CUSTOM EMOJI MAPPINGS")
print("-" * 30)

# Add custom mappings
custom_mappings = {
    "🎨": "matplotlib.pyplot",
    "🌊": "wave",
    "🎵": "music21",
    "🏠": "homeassistant"
}

for emoji, module in custom_mappings.items():
    add_custom_mapping(emoji, module)
    print(f"  Added: {emoji} -> {module}")

# Verify mappings
print("\n  Verifying mappings:")
for emoji in custom_mappings:
    module = get_module_for_emoji(emoji)
    print(f"    {emoji} maps to: {module}")

# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 50)
print("🎉 SHOWCASE COMPLETE!")
print("\nEmojify Python Features Demonstrated:")
print("  ✅ Emoji imports")
print("  ✅ Emoji variables & functions")
print("  ✅ Emoji classes")
print("  ✅ Emoji decorators")
print("  ✅ Emoji type hints")
print("  ✅ Emoji error handling")
print("  ✅ Emoji comprehensions")
print("  ✅ Emoji context managers")
print("  ✅ Emoji utilities")
print("  ✅ Custom mappings")
print("\n📦 Install: pip install emojify-python")
print("🌐 PyPI: https://pypi.org/project/emojify-python/")
print("📚 Docs: https://github.com/arpanghoshal/emojify-python")