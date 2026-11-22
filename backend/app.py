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
    # Frontend directory path for static serving
    frontend_dir = os.path.join(PROJECT_DIR, "frontend")
    
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
        init_db()

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

    # Serve Frontend static pages for single-port convenience
    @app.route("/", defaults={"path": "index.html"})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path.startswith("api/"):
            return jsonify({"success": False, "message": "API endpoint not found."}), 404
        
        file_path = os.path.join(frontend_dir, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_from_directory(frontend_dir, path)
        elif os.path.exists(os.path.join(frontend_dir, f"{path}.html")):
            return send_from_directory(frontend_dir, f"{path}.html")
        else:
            return send_from_directory(frontend_dir, "index.html")

    # Global Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "message": "Resource not found"}), 404
        return send_from_directory(frontend_dir, "index.html")

    @app.errorhandler(500)
    def handle_server_error(e):
        return jsonify({"success": False, "message": "An unexpected server error occurred."}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    port = Config.PORT
    print(f"\n=======================================================")
    print(f"  आयुCare (AyuCare) Health Platform Server")
    print(f"  Running at: http://localhost:{port}")
    print(f"  Frontend:   http://localhost:{port}/index.html")
    print(f"  API Health: http://localhost:{port}/api/health")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)
