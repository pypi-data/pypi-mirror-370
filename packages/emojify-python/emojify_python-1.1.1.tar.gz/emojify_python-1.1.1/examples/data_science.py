#!/usr/bin/env python
"""Data science example using emoji imports."""

from emojify_python import enable

# Enable emoji imports
enable()

print("📊 Data Science with Emoji Imports\n")
print("=" * 40)

# Try to import data science libraries with emojis
# Note: This example will only work if you have these libraries installed

try:
    import 🐼  # pandas
    import 🔢  # numpy
    print("✅ Successfully imported pandas as 🐼 and numpy as 🔢")
    
    # Create sample data
    print("\n📈 Creating sample dataset...")
    
    # Create a DataFrame with emoji variable
    🎲 = 🐼.DataFrame({
        '📅': 🐼.date_range('2024-01-01', periods=30),
        '💰': 🔢.random.randint(100, 1000, 30),
        '📊': 🔢.random.randn(30).cumsum() + 100,
        '🏷️': 🔢.random.choice(['A', 'B', 'C'], 30)
    })
    
    print(f"\nDataset shape: {🎲.shape}")
    print(f"\nFirst 5 rows:")
    print(🎲.head())
    
    # Basic statistics
    print("\n📊 Basic Statistics:")
    print(🎲.describe())
    
    # Group operations
    print("\n🏷️ Group by category:")
    📊_grouped = 🎲.groupby('🏷️')['💰'].mean()
    print(📊_grouped)
    
    # Data manipulation with emoji variables
    🔝 = 🎲.nlargest(5, '💰')
    print(f"\n💰 Top 5 highest values:")
    print(🔝[['📅', '💰', '🏷️']])
    
    # Array operations with numpy
    print("\n🔢 NumPy operations:")
    🎯 = 🔢.array([1, 2, 3, 4, 5])
    🎪 = 🔢.array([6, 7, 8, 9, 10])
    
    ➕ = 🎯 + 🎪
    ✖️ = 🎯 * 2
    🔷 = 🔢.sqrt(🎯)
    
    print(f"Array 1: {🎯}")
    print(f"Array 2: {🎪}")
    print(f"Sum: {➕}")
    print(f"Doubled: {✖️}")
    print(f"Square root: {🔷}")
    
    # Matrix operations
    print("\n🔢 Matrix operations:")
    🅰️ = 🔢.array([[1, 2], [3, 4]])
    🅱️ = 🔢.array([[5, 6], [7, 8]])
    
    🆚 = 🔢.dot(🅰️, 🅱️)
    print(f"Matrix A:\n{🅰️}")
    print(f"Matrix B:\n{🅱️}")
    print(f"A × B:\n{🆚}")
    
except ImportError as e:
    print(f"⚠️ Some libraries are not installed: {e}")
    print("To run this example, install: pip install pandas numpy")
    
    # Demonstrate with standard library instead
    print("\n📦 Using standard library alternatives...")
    import 📦  # json
    import 🎲  # random
    import 📅  # datetime
    
    # Create mock data
    🗂️ = []
    for i in range(10):
        🗂️.append({
            'date': str(📅.datetime.now() + 📅.timedelta(days=i)),
            'value': 🎲.randint(50, 150),
            'category': 🎲.choice(['A', 'B', 'C'])
        })
    
    print("Sample data (using standard library):")
    print(📦.dumps(🗂️[:3], indent=2))
    
    # Calculate simple statistics
    values = [item['value'] for item in 🗂️]
    📈_mean = sum(values) / len(values)
    📉_min = min(values)
    📊_max = max(values)
    
    print(f"\nStatistics:")
    print(f"Mean: {📈_mean:.2f}")
    print(f"Min: {📉_min}")
    print(f"Max: {📊_max}")

print("\n✨ Data science with emojis is fun! ✨")