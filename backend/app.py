import os
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

from config import Config, PROJECT_DIR
from database import init_db, ACTIVE_ENGINE
from routes.auth_routes import auth_bp
from routes.symptom_routes import symptom_bp
from routes.specialist_routes import specialist_bp
from routes.consultation_routes import consultation_bp
from routes.chatbot_routes import chatbot_bp
from routes.contact_routes import contact_bp
from routes.profile_routes import profile_bp

def create_app():
    # Build list of static directories covering local, Docker, and Vercel Lambda contexts
    from pathlib import Path
    base_candidates = [
        Path(os.getcwd()),
        Path(PROJECT_DIR),
        Path(os.path.dirname(os.path.abspath(__file__))).parent,
        Path(os.path.dirname(os.path.abspath(__file__)))
    ]
    static_dirs = []
    for b in base_candidates:
        for sub in ["public", "frontend", ""]:
            d = b / sub if sub else b
            if d.is_dir() and str(d) not in static_dirs:
                static_dirs.append(str(d))

    frontend_dir = next((d for d in static_dirs if os.path.exists(os.path.join(d, "index.html"))), static_dirs[0] if static_dirs else str(PROJECT_DIR))

    app = Flask(__name__, static_folder=frontend_dir, static_url_path="")
    app.config.from_object(Config)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(symptom_bp)
    app.register_blueprint(specialist_bp)
    app.register_blueprint(consultation_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(profile_bp)

    # Initialize Database on launch
    with app.app_context():
        try:
            init_db()
        except Exception as db_init_err:
            app.logger.error(f"Database initialization error: {db_init_err}")

    # Health Check Endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        from database import ACTIVE_ENGINE
        return jsonify({
            "status": "healthy",
            "service": "आयुCare (AyuCare) REST API",
            "version": "1.0.0",
            "active_database_engine": ACTIVE_ENGINE or Config.DB_TYPE,
            "disclaimer": "AyuCare is an educational guidance prototype, not a medical diagnosis system."
        }), 200

    @app.route("/api/debug-files", methods=["GET"])
    def debug_files():
        import glob
        return jsonify({
            "cwd": os.getcwd(),
            "cwd_files": os.listdir(os.getcwd()) if os.path.exists(os.getcwd()) else [],
            "project_dir": str(PROJECT_DIR),
            "project_dir_files": os.listdir(str(PROJECT_DIR)) if os.path.exists(str(PROJECT_DIR)) else [],
            "static_dirs": static_dirs,
            "all_html": glob.glob("**/*.html", recursive=True),
            "app_file": os.path.abspath(__file__)
        }), 200

    # Serve Frontend static pages for single-port and serverless fallback
    @app.route("/", defaults={"path": "index.html"})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path.startswith("api/"):
            return jsonify({"success": False, "message": "API endpoint not found."}), 404

        # Search across static folders
        for d in static_dirs:
            if not os.path.isdir(d):
                continue
            # Direct file match
            candidate = os.path.join(d, path)
            if os.path.isfile(candidate):
                return send_from_directory(d, path)
            # Match with .html extension
            html_candidate = os.path.join(d, f"{path}.html")
            if os.path.isfile(html_candidate):
                return send_from_directory(d, f"{path}.html")

        # Fallback to index.html
        for d in static_dirs:
            if not os.path.isdir(d):
                continue
            idx = os.path.join(d, "index.html")
            if os.path.isfile(idx):
                return send_from_directory(d, "index.html")

        return "आयुCare Platform - Frontend ready. Visit /api/health for API status.", 200

    # Global Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "message": "Resource not found"}), 404
        
        # Check if clean URL corresponds to an existing .html page
        clean_path = request.path.strip("/")
        if clean_path:
            for d in static_dirs:
                if not os.path.isdir(d):
                    continue
                html_candidate = os.path.join(d, f"{clean_path}.html")
                if os.path.isfile(html_candidate):
                    return send_from_directory(d, f"{clean_path}.html")

        # Fallback to index.html
        for d in static_dirs:
            if not os.path.isdir(d):
                continue
            idx = os.path.join(d, "index.html")
            if os.path.isfile(idx):
                return send_from_directory(d, "index.html")
        return "Page not found", 404

    @app.errorhandler(500)
    def handle_server_error(e):
        return jsonify({"success": False, "message": "An unexpected server error occurred."}), 500

    return app

# Expose app at module level for Vercel, WSGI, and production runners
app = create_app()

if __name__ == "__main__":
    port = Config.PORT
    print(f"\n=======================================================")
    print(f"  आयुCare (AyuCare) Health Platform Server")
    print(f"  Running at: http://localhost:{port}")
    print(f"  Frontend:   http://localhost:{port}/index.html")
    print(f"  API Health: http://localhost:{port}/api/health")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)
