import os
import sys

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(BASE_DIR, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import create_app from backend.app
from backend.app import create_app

# Expose 'app' and 'application' at top level for Vercel, WSGI, Gunicorn
app = create_app()
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
