# 🐍 Emojify Python - The Ultimate Emoji Programming Experience

**Transform Python into a fully emoji-powered language!** Import modules, write operators, create classes, and more - all with emojis! 

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/emojify-python.svg)](https://badge.fury.io/py/emojify-python)

## 🚀 Features

### ✨ Core Features
- 🎯 **Import modules using emojis**: `import 🐼` for pandas
- 🔄 **Emoji aliases**: `import pandas as 🐼`
- 📦 **Emoji variables**: `🎲 = random.randint(1, 6)`
- 🎨 **Custom mappings**: Map any emoji to any module

### 🆕 Enhanced Features
- ➕➖✖️➗ **Emoji operators**: Math with `x ➕ y`, `a ✖️ b`
- 🎨 **Emoji decorators**: Time functions, cache results, handle errors
- 🔄 **Emoji control flow**: `❓` for if, `🔁` for loops
- 📝 **Emoji functions & classes**: Define with emojis
- 🖥️ **Emoji REPL**: Interactive Python with full emoji support
- 🔍 **Emoji type hints**: Type annotations with emojis
- 🎨 **Syntax highlighting**: Beautiful colored emoji code
- 📁 **Emoji file support**: Save code as `.🐍` files
- ❌ **Emoji error messages**: Friendly error handling
- 🧪 **Emoji assertions**: Testing with emoji asserts

## 📦 Installation

```bash
pip install emojify-python
```

## 🚀 Quick Start

### Basic Usage

```python
from emojify_python import enable

# Enable emoji imports globally
enable()

# Now you can import using emojis!
import 🐼  # Imports pandas
import 📊  # Imports matplotlib
import 🔢  # Imports numpy

# Use emoji aliases
import pandas as 🐼
import numpy as 🔢

# Create emoji variables
🎲 = 🐼.DataFrame({'data': [1, 2, 3]})
📈 = 🎲.plot()
```

### Context Manager

Use emojis only within a specific context:

```python
from emojify_python import emojified

with emojified():
    import 🐼
    🎲 = 🐼.DataFrame({'data': [1, 2, 3]})
    print(🎲)

# Outside the context, emoji imports won't work
```

### Decorator

Enable emoji imports for specific functions:

```python
from emojify_python import emojify_function

@emojify_function
def analyze_data():
    import 🐼
    import 📊
    
    🎲 = 🐼.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
    📊.pyplot.plot(🎲['x'], 🎲['y'])
    return 🎲
```

## 🗺️ Default Emoji Mappings

### Data Science & Analysis
- 🐼 → `pandas`
- 📊 → `matplotlib`
- 🔢 → `numpy`
- 🧮 → `scipy`
- 🤖 → `sklearn`
- 📈 → `seaborn`

### Web Frameworks
- 🌐 → `flask`
- ⚡ → `fastapi`
- 🎪 → `django`
- 🚀 → `requests`

### Utilities
- 📅 → `datetime`
- 🔍 → `re`
- 📁 → `pathlib`
- 🎲 → `random`
- 📦 → `json`
- 🔐 → `hashlib`

[See all mappings](https://github.com/arpanghoshal/emojify-python/blob/main/emojify_python/mappings.py)

## 🎨 Custom Mappings

### Add Your Own Mappings

```python
from emojify_python import add_mapping, enable

# Add custom mapping
add_mapping('🎮', 'pygame')
add_mapping('🎨', 'pillow')

enable()

# Now use your custom emojis
import 🎮
import 🎨

🎮.init()
```

### View and Manage Mappings

```python
from emojify_python import (
    view_mappings,
    list_mappings,
    search_mapping,
    update_default_mapping,
    save_custom_mappings,
    load_custom_mappings
)

# View all mappings
all_mappings = view_mappings()

# Search for specific mappings
results = search_mapping('pandas')  # Find mappings related to pandas

# List mappings by category
data_mappings = view_mappings(category='data')

# Update default mappings (use with caution)
update_default_mapping('🆕', 'new_module')

# Save custom mappings to file
save_custom_mappings('my_mappings.json')

# Load custom mappings from file
load_custom_mappings('my_mappings.json')
```

## 🛠️ Advanced Usage

### Execute Emoji Code

```python
from emojify_python import exec_emoji_code

code = '''
import 🐼
import 🔢

🎲 = 🐼.DataFrame({
    'x': 🔢.array([1, 2, 3]),
    'y': 🔢.array([4, 5, 6])
})
print(🎲.describe())
'''

exec_emoji_code(code)
```

### Compile Emoji Code

```python
from emojify_python import compile_emoji_code

code = "🎲 = [i for i in range(10)]"
compiled = compile_emoji_code(code)
exec(compiled)
```

## 🎮 Command Line Interface

Emojify Python comes with a CLI tool:

```bash
# List all emoji mappings
python -m emojify_python list

# Search for mappings
python -m emojify_python search pandas

# Add custom mapping
python -m emojify_python add 🎮 pygame

# Run a Python file with emoji support
python -m emojify_python run my_emoji_script.py
```

## 📚 Examples

### Data Analysis with Emojis

```python
from emojify_python import enable
enable()

import 🐼 as pd
import 🔢 as np
import 📊 as mpl

# Create data
🎲 = pd.DataFrame({
    '📅': pd.date_range('2024-01-01', periods=100),
    '📈': np.random.randn(100).cumsum(),
    '📉': np.random.randn(100).cumsum()
})

# Plot data
🖼️ = 🎲.plot(x='📅', y=['📈', '📉'])
mpl.pyplot.show()
```

### Web API with Emojis

```python
from emojify_python import enable
enable()

from 🌐 import Flask, jsonify
import 📅 as datetime

🚀 = Flask(__name__)

@🚀.route('/api/time')
def get_time():
    ⏰ = datetime.datetime.now()
    return jsonify({'time': str(⏰)})

if __name__ == '__main__':
    🚀.run(debug=True)
```

### Machine Learning Pipeline

```python
from emojify_python import enable
enable()

import 🐼 as pd
import 🔢 as np
from 🤖 import model_selection, ensemble

# Load data
📊 = pd.read_csv('data.csv')
🎯 = 📊['target']
📥 = 📊.drop('target', axis=1)

# Split data
X_train, X_test, y_train, y_test = model_selection.train_test_split(
    📥, 🎯, test_size=0.2, random_state=42
)

# Train model
🌳 = ensemble.RandomForestClassifier()
🌳.fit(X_train, y_train)

# Evaluate
📈 = 🌳.score(X_test, y_test)
print(f"Accuracy: {📈}")
```

## 🤔 How It Works

Emojify Python uses Python's import hook system to intercept import statements and translate emoji names to their corresponding module names. It:

1. **Registers a custom import finder** in `sys.meta_path`
2. **Transforms emoji identifiers** to valid Python names using AST manipulation
3. **Maps emojis to modules** using a configurable dictionary
4. **Maintains compatibility** with standard Python imports

## ⚠️ Limitations

- Emoji support in Python is handled through transformation, not native support
- Some IDEs may not provide autocomplete for emoji imports
- Debugging may show transformed names instead of emojis
- Not recommended for production code (but great for fun projects!)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the playful nature of Python
- Thanks to all contributors and emoji enthusiasts
- Special thanks to the Python import system documentation

## 📮 Contact

- GitHub: [@arpanghoshal](https://github.com/arpanghoshal)
- PyPI: [emojify-python](https://pypi.org/project/emojify-python/)

---

**Remember**: While emoji imports are fun, use them responsibly! 🎉