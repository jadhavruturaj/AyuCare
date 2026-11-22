import os
import sys

# Ensure backend directory is accessible
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(BASE_DIR, "backend")
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from backend.app import create_app

# Expose app and application for WSGI / Vercel Python runtime
app = create_app()
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
