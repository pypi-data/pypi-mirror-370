#!/usr/bin/env python
"""Web application example using emoji imports."""

from emojify_python import enable

# Enable emoji imports
enable()

print("🌐 Web Application with Emoji Imports\n")
print("=" * 40)

# Import standard libraries with emojis
import 📅  # datetime
import 📦  # json
import 🎲  # random

# Try to import Flask
try:
    from 🌐 import Flask, jsonify, request
    print("✅ Successfully imported Flask as 🌐")
    
    # Create Flask app with emoji variable
    🚀 = Flask(__name__)
    
    # In-memory data store
    📚 = []
    
    @🚀.route('/')
    def home():
        """Home endpoint."""
        return jsonify({
            '🎉': 'Welcome to Emoji Flask!',
            '📅': str(📅.datetime.now()),
            '🔢': 🎲.randint(1, 100)
        })
    
    @🚀.route('/api/items', methods=['GET'])
    def get_items():
        """Get all items."""
        return jsonify({'📚': 📚, 'count': len(📚)})
    
    @🚀.route('/api/items', methods=['POST'])
    def add_item():
        """Add a new item."""
        📝 = request.get_json()
        📝['id'] = 🎲.randint(1000, 9999)
        📝['created'] = str(📅.datetime.now())
        📚.append(📝)
        return jsonify({'✅': 'Item added', '📝': 📝}), 201
    
    @🚀.route('/api/random')
    def random_data():
        """Generate random data."""
        🎯 = {
            '🎲': 🎲.randint(1, 100),
            '🃏': 🎲.choice(['♠️', '♥️', '♦️', '♣️']),
            '🎰': [🎲.randint(1, 10) for _ in range(3)],
            '📅': str(📅.datetime.now())
        }
        return jsonify(🎯)
    
    @🚀.route('/api/emoji')
    def emoji_info():
        """Show emoji variable usage."""
        🔥 = "This is a fire variable!"
        🌟 = ["star", "item", "list"]
        🎨 = {"color": "rainbow", "style": "awesome"}
        
        return jsonify({
            '🔥': 🔥,
            '🌟': 🌟,
            '🎨': 🎨
        })
    
    print("\n🚀 Flask app created with emoji routes!")
    print("\nAvailable endpoints:")
    print("  GET  /              - Home")
    print("  GET  /api/items     - Get all items")
    print("  POST /api/items     - Add new item")
    print("  GET  /api/random    - Random data")
    print("  GET  /api/emoji     - Emoji variables demo")
    
    print("\nTo run the app, uncomment the last line:")
    print("  🚀.run(debug=True, port=5000)")
    
    # Uncomment to actually run the server:
    # 🚀.run(debug=True, port=5000)
    
except ImportError:
    print("⚠️ Flask is not installed.")
    print("To run this example, install: pip install flask")
    
    # Create a mock web app using standard library
    print("\n📦 Creating mock web app with standard library...")
    
    class 🌐:
        """Mock web application."""
        
        def __init__(self):
            self.🗺️ = {}  # Routes
            self.📚 = []   # Data store
        
        def route(self, path):
            """Register a route."""
            def decorator(func):
                self.🗺️[path] = func
                return func
            return decorator
        
        def handle_request(self, path):
            """Handle a request."""
            if path in self.🗺️:
                return self.🗺️[path]()
            return {'error': 'Not found'}, 404
    
    # Create mock app
    🚀 = 🌐()
    
    @🚀.route('/')
    def home():
        return {
            '🎉': 'Welcome to Mock Emoji Web!',
            '📅': str(📅.datetime.now()),
            '🔢': 🎲.randint(1, 100)
        }
    
    @🚀.route('/api/data')
    def get_data():
        🎲_data = [🎲.randint(1, 100) for _ in range(5)]
        return {
            '📊': 🎲_data,
            '📈': max(🎲_data),
            '📉': min(🎲_data),
            '➗': sum(🎲_data) / len(🎲_data)
        }
    
    # Simulate requests
    print("\n🔄 Simulating requests...")
    
    for path in ['/', '/api/data']:
        print(f"\nGET {path}")
        response = 🚀.handle_request(path)
        print(f"Response: {📦.dumps(response, indent=2)}")

print("\n✨ Web apps with emojis are awesome! ✨")