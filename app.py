import os
import sys
from flask import Flask

# Setup paths so backend package and modules are cleanly discoverable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(BASE_DIR, "backend")
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from backend.app import create_app

# Literal Flask initialization so Vercel AST framework analyzer detects the entrypoint
app = Flask(__name__)

# Re-assign to the fully initialized application with blueprints, db, and routes
app = create_app()
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
