"""Extended emoji to module mappings for emojify-python v1.1.0+"""

# Extended mappings organized by category
EXTENDED_MAPPINGS = {
    # ============================================
    # DATA SCIENCE & ANALYTICS (Extended)
    # ============================================
    '📊': 'matplotlib.pyplot',     # Plotting
    '📈': 'seaborn',               # Statistical plots
    '📉': 'plotly',                # Interactive plots
    '📐': 'scipy.stats',           # Statistics
    '🧮': 'scipy',                 # Scientific computing
    '🔢': 'numpy',                 # Numerical computing
    '🐼': 'pandas',                # Data manipulation
    '⚗️': 'scikit-learn',          # Machine learning
    '🔬': 'statsmodels',           # Statistical models
    '🎲': 'random',                # Random operations
    '📏': 'scipy.optimize',        # Optimization
    '🗃️': 'dask',                  # Parallel computing
    '💹': 'yfinance',              # Financial data
    '📊': 'altair',                # Declarative visualization
    '🎨': 'bokeh',                 # Interactive visualization
    '🗂️': 'vaex',                  # Big data DataFrames
    
    # ============================================
    # AI & MACHINE LEARNING (Extended)
    # ============================================
    '🧠': 'tensorflow',            # Deep learning
    '🔥': 'torch',                 # PyTorch
    '⚡': 'pytorch_lightning',     # High-level PyTorch
    '🎯': 'keras',                 # High-level neural networks
    '🤖': 'transformers',          # Hugging Face transformers
    '🌳': 'xgboost',               # Gradient boosting
    '💡': 'lightgbm',              # Gradient boosting
    '🎁': 'catboost',              # Categorical boosting
    '🔮': 'prophet',               # Time series forecasting
    '👁️': 'opencv-python',         # Computer vision (cv2)
    '🗣️': 'speechrecognition',     # Speech recognition
    '💬': 'nltk',                  # Natural language toolkit
    '📚': 'spacy',                 # NLP library
    '🎭': 'gensim',                # Topic modeling
    '🧬': 'biopython',             # Bioinformatics
    '🔬': 'rdkit',                 # Cheminformatics
    '🎵': 'librosa',               # Audio analysis
    '🖼️': 'pillow',                # Image processing (PIL)
    '🌐': 'networkx',              # Network analysis
    '🧮': 'sympy',                 # Symbolic math
    
    # ============================================
    # WEB DEVELOPMENT (Extended)
    # ============================================
    '🌐': 'flask',                 # Micro framework
    '⚡': 'fastapi',               # Modern API framework
    '🎪': 'django',                # Full framework
    '🌪️': 'tornado',               # Async framework
    '🍷': 'bottle',                # Micro framework
    '🔥': 'sanic',                 # Async framework
    '🦅': 'falcon',                # API framework
    '⭐': 'starlette',             # ASGI framework
    '🎭': 'aiohttp',               # Async HTTP
    '🚀': 'requests',              # HTTP library
    '🌍': 'httpx',                 # Async HTTP client
    '🕸️': 'scrapy',                # Web scraping
    '🍲': 'beautifulsoup4',        # HTML parsing
    '🎯': 'selenium',              # Browser automation
    '🎨': 'jinja2',                # Templating
    '🔌': 'websockets',            # WebSocket client/server
    '📨': 'celery',                # Task queue
    '🐰': 'pika',                  # RabbitMQ client
    '📮': 'kombu',                 # Messaging library
    
    # ============================================
    # DATABASES & STORAGE (Extended)
    # ============================================
    '🗄️': 'sqlite3',               # SQLite
    '🐘': 'psycopg2',              # PostgreSQL
    '🍃': 'pymongo',               # MongoDB
    '🔴': 'redis',                 # Redis
    '🔶': 'sqlalchemy',            # SQL toolkit
    '🏺': 'peewee',                # Simple ORM
    '📀': 'dataset',               # Simple database
    '🗃️': 'tinydb',                # Document database
    '🌊': 'influxdb',              # Time series DB
    '🔷': 'neo4j',                 # Graph database
    '🎯': 'elasticsearch',         # Search engine
    '📊': 'clickhouse-driver',     # Analytics DB
    '☁️': 'boto3',                 # AWS SDK
    '🌥️': 'google-cloud-storage',  # Google Cloud
    '🌤️': 'azure-storage-blob',    # Azure Storage
    
    # ============================================
    # CLOUD & DEVOPS (Extended)
    # ============================================
    '🐳': 'docker',                # Docker SDK
    '☸️': 'kubernetes',            # Kubernetes client
    '📦': 'ansible',               # Automation
    '🔧': 'fabric',                # Remote execution
    '🚢': 'paramiko',              # SSH client
    '☁️': 'boto3',                 # AWS
    '🌩️': 'apache-libcloud',       # Multi-cloud
    '📡': 'paho-mqtt',             # MQTT client
    '🔌': 'pyserial',              # Serial communication
    '🎯': 'consul',                # Service discovery
    '🔐': 'vault',                 # Secrets management
    '📊': 'prometheus_client',     # Metrics
    '📈': 'datadog',               # Monitoring
    
    # ============================================
    # TESTING & QUALITY (Extended)
    # ============================================
    '🧪': 'pytest',                # Testing framework
    '🔬': 'unittest',              # Built-in testing
    '🎭': 'pytest-mock',           # Mocking
    '🎯': 'hypothesis',            # Property testing
    '📊': 'coverage',              # Code coverage
    '🔍': 'pylint',                # Linting
    '✨': 'black',                 # Code formatting
    '🎨': 'autopep8',              # PEP8 formatting
    '📏': 'flake8',                # Style checker
    '🔧': 'mypy',                  # Type checking
    '🏃': 'tox',                   # Test automation
    '🎪': 'behave',                # BDD testing
    '🥒': 'pytest-bdd',            # BDD for pytest
    
    # ============================================
    # GAME DEVELOPMENT (Extended)
    # ============================================
    '🎮': 'pygame',                # 2D games
    '🕹️': 'arcade',                # Modern Python game
    '🎲': 'panda3d',               # 3D engine
    '🎯': 'pyglet',                # Windowing/multimedia
    '🏃': 'cocos2d',               # 2D framework
    '⚔️': 'pygame_gui',            # GUI for Pygame
    '🗺️': 'pytmx',                 # Tiled map loader
    '🎵': 'pygame.mixer',          # Sound/music
    
    # ============================================
    # GUI DEVELOPMENT (Extended)
    # ============================================
    '🖥️': 'tkinter',               # Built-in GUI
    '🪟': 'PyQt5',                 # Qt bindings
    '🎛️': 'kivy',                  # Multi-touch GUI
    '🖼️': 'wxPython',              # Native GUI
    '🎨': 'PySimpleGUI',           # Simple GUI
    '✨': 'customtkinter',         # Modern tkinter
    '🌈': 'dear_pygui',            # GPU-accelerated
    '🎯': 'toga',                  # Native mobile/desktop
    
    # ============================================
    # BLOCKCHAIN & CRYPTO (New)
    # ============================================
    '₿': 'bitcoin',                # Bitcoin tools
    '🔗': 'web3',                  # Ethereum Web3
    '⛓️': 'eth-account',           # Ethereum accounts
    '💎': 'pyethereum',            # Ethereum
    '🪙': 'mnemonic',              # BIP39 mnemonics
    '🔐': 'cryptography',          # Cryptography
    '🛡️': 'pycryptodome',          # Cryptographic library
    '🔑': 'ecdsa',                 # Elliptic curve
    '📜': 'py-solc',               # Solidity compiler
    
    # ============================================
    # SCIENTIFIC COMPUTING (Extended)
    # ============================================
    '🔬': 'scipy',                 # Scientific tools
    '🧬': 'biopython',             # Bioinformatics
    '🌌': 'astropy',               # Astronomy
    '⚛️': 'qiskit',                # Quantum computing
    '🧲': 'pennylane',             # Quantum ML
    '📡': 'pyserial',              # Serial communication
    '🌡️': 'pint',                  # Physical quantities
    '🔭': 'skyfield',              # Astronomy calculations
    '🧮': 'sympy',                 # Symbolic math
    '📐': 'shapely',               # Geometric operations
    
    # ============================================
    # AUDIO & VIDEO (Extended)
    # ============================================
    '🎵': 'pydub',                 # Audio manipulation
    '🎼': 'music21',               # Music analysis
    '🎸': 'pretty_midi',           # MIDI manipulation
    '🎤': 'pyaudio',               # Audio I/O
    '📻': 'python-vlc',            # VLC bindings
    '🎬': 'moviepy',               # Video editing
    '📹': 'ffmpeg-python',         # FFmpeg wrapper
    '🎞️': 'imageio',               # Image/video I/O
    
    # ============================================
    # DOCUMENTATION & REPORTING (New)
    # ============================================
    '📚': 'sphinx',                # Documentation
    '📖': 'mkdocs',                # Project documentation
    '📝': 'jupyter',               # Notebooks
    '📊': 'streamlit',             # Data apps
    '🎯': 'dash',                  # Analytical apps
    '📈': 'gradio',                # ML demos
    '🎨': 'panel',                 # Data apps
    '📑': 'reportlab',             # PDF generation
    '📄': 'python-docx',           # Word documents
    '📊': 'xlsxwriter',            # Excel files
    
    # ============================================
    # UTILITIES & HELPERS (Extended)
    # ============================================
    '📅': 'arrow',                 # Better dates
    '⏰': 'schedule',              # Job scheduling
    '🔄': 'retrying',              # Retry logic
    '💾': 'joblib',                # Efficient pickling
    '🎯': 'click',                 # CLI creation
    '🎨': 'rich',                  # Rich terminal
    '🌈': 'colorama',              # Terminal colors
    '📦': 'pip',                   # Package installer
    '🔧': 'setuptools',            # Package setup
    '📋': 'pyperclip',             # Clipboard
    '🖨️': 'python-escpos',         # Receipt printing
    '📧': 'yagmail',               # Email sending
    '📨': 'python-telegram-bot',   # Telegram bots
    '💬': 'discord.py',            # Discord bots
    '🐦': 'tweepy',                # Twitter API
    
    # ============================================
    # IOT & HARDWARE (New)
    # ============================================
    '🔌': 'pyserial',              # Serial communication
    '💡': 'gpiozero',              # Raspberry Pi GPIO
    '🎛️': 'adafruit-circuitpython', # CircuitPython
    '📡': 'bleak',                 # Bluetooth LE
    '📻': 'pyrtlsdr',              # Software radio
    '🌡️': 'w1thermsensor',         # Temperature sensors
    '🎮': 'pygame.joystick',       # Game controllers
    '📷': 'picamera2',             # Raspberry Pi camera
    
    # ============================================
    # GEOSPATIAL (New)
    # ============================================
    '🗺️': 'folium',                # Interactive maps
    '🌍': 'geopandas',             # Geographic data
    '📍': 'geopy',                 # Geocoding
    '🧭': 'pyproj',                # Cartographic projections
    '🛰️': 'rasterio',              # Raster data
    '🏔️': 'elevation',             # Elevation data
    '🌊': 'cartopy',               # Cartographic plotting
}

# Category groupings for better organization
CATEGORIES = {
    'DATA_SCIENCE': ['🐼', '📊', '📈', '📉', '🧮', '🔢', '📐', '⚗️'],
    'AI_ML': ['🧠', '🔥', '⚡', '🎯', '🤖', '🌳', '💡', '🔮'],
    'WEB': ['🌐', '⚡', '🎪', '🌪️', '🍷', '🚀', '🕸️'],
    'DATABASE': ['🗄️', '🐘', '🍃', '🔴', '🔶'],
    'CLOUD': ['🐳', '☸️', '☁️', '🌩️'],
    'TESTING': ['🧪', '🔬', '🎭', '📊'],
    'GAME': ['🎮', '🕹️', '🎲', '🎯'],
    'GUI': ['🖥️', '🪟', '🎛️', '🖼️'],
    'BLOCKCHAIN': ['₿', '🔗', '⛓️', '💎', '🪙'],
    'SCIENTIFIC': ['🔬', '🧬', '🌌', '⚛️', '🧲'],
    'MEDIA': ['🎵', '🎼', '🎬', '📹'],
    'IOT': ['🔌', '💡', '📡', '🌡️'],
    'GEO': ['🗺️', '🌍', '📍', '🧭', '🛰️'],
}

# Aliases for common variations
EMOJI_ALIASES = {
    # Multiple emojis for the same module
    'numpy': ['🔢', '🔣', '#️⃣'],
    'pandas': ['🐼', '🐻'],
    'matplotlib': ['📊', '📈', '📉'],
    'requests': ['🚀', '🌐', '📡'],
    'flask': ['🌐', '🍶'],
    'django': ['🎪', '🎠'],
    'pytest': ['🧪', '🔬', '🧫'],
    'docker': ['🐳', '🐋'],
    'redis': ['🔴', '🟥'],
    'postgresql': ['🐘', '🐡'],
    'mongodb': ['🍃', '🌿'],
}

# Function-specific emojis
FUNCTION_EMOJIS = {
    # Math operations
    'sum': '➕',
    'subtract': '➖',
    'multiply': '✖️',
    'divide': '➗',
    'power': '💪',
    'sqrt': '√',
    'log': '📊',
    
    # Data operations
    'filter': '🔍',
    'map': '🗺️',
    'reduce': '📉',
    'sort': '🔤',
    'group': '📦',
    'merge': '🔗',
    'split': '✂️',
    
    # File operations
    'read': '📖',
    'write': '✏️',
    'delete': '🗑️',
    'copy': '📋',
    'move': '📦',
    
    # Network operations
    'get': '📥',
    'post': '📤',
    'put': '📝',
    'delete': '❌',
    'connect': '🔌',
    'disconnect': '🔕',
    
    # Status indicators
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'debug': '🐛',
    'critical': '🚨',
}

# Development workflow emojis
WORKFLOW_EMOJIS = {
    'plan': '📝',
    'develop': '💻',
    'test': '🧪',
    'debug': '🐛',
    'review': '👀',
    'deploy': '🚀',
    'monitor': '📊',
    'optimize': '⚡',
    'document': '📚',
    'release': '🎉',
}

def get_extended_mapping(emoji: str) -> str:
    """Get module name from extended mappings.
    
    Args:
        emoji: The emoji to look up
        
    Returns:
        Module name if found, otherwise None
    """
    return EXTENDED_MAPPINGS.get(emoji)

def get_category_emojis(category: str) -> list:
    """Get all emojis for a specific category.
    
    Args:
        category: Category name (e.g., 'DATA_SCIENCE', 'AI_ML')
        
    Returns:
        List of emojis in that category
    """
    return CATEGORIES.get(category.upper(), [])

def get_module_aliases(module_name: str) -> list:
    """Get all emoji aliases for a module.
    
    Args:
        module_name: The module name
        
    Returns:
        List of emoji aliases
    """
    return EMOJI_ALIASES.get(module_name, [])

def suggest_emoji_for_module(module_name: str) -> str:
    """Suggest the best emoji for a module.
    
    Args:
        module_name: The module name
        
    Returns:
        Suggested emoji or None
    """
    # Check if we have aliases
    aliases = get_module_aliases(module_name)
    if aliases:
        return aliases[0]
    
    # Search in extended mappings
    for emoji, module in EXTENDED_MAPPINGS.items():
        if module == module_name or module.startswith(module_name):
            return emoji
    
    return None

def get_all_extended_mappings() -> dict:
    """Get all extended mappings."""
    return EXTENDED_MAPPINGS.copy()

# Popular combinations for quick setup
POPULAR_SETS = {
    'data_science': {
        '🐼': 'pandas',
        '🔢': 'numpy',
        '📊': 'matplotlib.pyplot',
        '📈': 'seaborn',
        '🧮': 'scipy',
        '📐': 'scipy.stats',
    },
    'web_dev': {
        '🌐': 'flask',
        '⚡': 'fastapi',
        '🚀': 'requests',
        '🍲': 'beautifulsoup4',
        '🗄️': 'sqlite3',
        '🔴': 'redis',
    },
    'machine_learning': {
        '🧠': 'tensorflow',
        '🔥': 'torch',
        '🤖': 'transformers',
        '👁️': 'cv2',
        '💬': 'nltk',
        '📚': 'spacy',
    },
    'cloud_native': {
        '🐳': 'docker',
        '☸️': 'kubernetes',
        '☁️': 'boto3',
        '📦': 'ansible',
        '📡': 'paho-mqtt',
    },
    'blockchain': {
        '₿': 'bitcoin',
        '🔗': 'web3',
        '⛓️': 'eth-account',
        '💎': 'pyethereum',
        '🔐': 'cryptography',
    },
}