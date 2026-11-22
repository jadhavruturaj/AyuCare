import os
from flask import Flask, jsonify, send_from_directory, request, redirect
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
    import os
    from pathlib import Path
    from flask import render_template

    base_dir = os.path.abspath(os.path.dirname(__file__))
    root_dir = os.path.abspath(os.path.join(base_dir, ".."))

    # Template directories candidates
    template_candidates = [
        os.path.join(root_dir, "templates"),
        os.path.join(base_dir, "templates"),
        os.path.join(os.getcwd(), "templates"),
        os.path.join(root_dir, "public"),
        os.path.join(root_dir, "frontend"),
        root_dir
    ]
    template_dir = next((d for d in template_candidates if os.path.isdir(d) and os.path.exists(os.path.join(d, "index.html"))), template_candidates[0])

    # Static directories candidates
    static_candidates = [
        os.path.join(root_dir, "static"),
        os.path.join(root_dir, "public"),
        os.path.join(root_dir, "frontend"),
        os.path.join(base_dir, "static"),
        root_dir
    ]
    static_dir = next((d for d in static_candidates if os.path.isdir(d) and (os.path.exists(os.path.join(d, "css")) or os.path.exists(os.path.join(d, "js")))), static_candidates[0])

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
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

    # About section removal redirect
    @app.route("/about", methods=["GET"])
    @app.route("/about.html", methods=["GET"])
    def redirect_about():
        return redirect("/index.html", code=301)

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

    # Explicit static assets routing
    @app.route("/css/<path:filename>")
    def serve_css(filename):
        for candidate in static_candidates:
            target = os.path.join(candidate, "css")
            if os.path.isfile(os.path.join(target, filename)):
                return send_from_directory(target, filename)
        return jsonify({"error": "CSS not found"}), 404

    @app.route("/js/<path:filename>")
    def serve_js(filename):
        for candidate in static_candidates:
            target = os.path.join(candidate, "js")
            if os.path.isfile(os.path.join(target, filename)):
                return send_from_directory(target, filename)
        return jsonify({"error": "JS not found"}), 404

    @app.route("/assets/<path:filename>")
    def serve_assets(filename):
        for candidate in static_candidates:
            target = os.path.join(candidate, "assets")
            if os.path.isfile(os.path.join(target, filename)):
                return send_from_directory(target, filename)
        return jsonify({"error": "Asset not found"}), 404

    # HTML page rendering (supports render_template, send_from_directory, and clean URLs)
    @app.route("/", defaults={"path": "index.html"})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path.startswith("api/"):
            return jsonify({"success": False, "message": "API endpoint not found."}), 404

        clean_path = path.strip("/")
        if not clean_path or clean_path == "index":
            clean_path = "index.html"

        # Check template rendering
        tpl_name = clean_path if clean_path.endswith(".html") else f"{clean_path}.html"
        for t_dir in template_candidates:
            if os.path.isfile(os.path.join(t_dir, tpl_name)):
                try:
                    return render_template(tpl_name)
                except Exception:
                    return send_from_directory(t_dir, tpl_name)

        # Check static file direct match
        for s_dir in static_candidates:
            if os.path.isfile(os.path.join(s_dir, clean_path)):
                return send_from_directory(s_dir, clean_path)

        # Fallback to index.html
        for t_dir in template_candidates:
            if os.path.isfile(os.path.join(t_dir, "index.html")):
                try:
                    return render_template("index.html")
                except Exception:
                    return send_from_directory(t_dir, "index.html")

        return render_template("index.html")

    # Global Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "message": "Resource not found"}), 404
        
        clean_path = request.path.strip("/")
        tpl_name = clean_path if clean_path.endswith(".html") else f"{clean_path}.html"
        for t_dir in template_candidates:
            if os.path.isfile(os.path.join(t_dir, tpl_name)):
                try:
                    return render_template(tpl_name)
                except Exception:
                    return send_from_directory(t_dir, tpl_name)

        for t_dir in template_candidates:
            if os.path.isfile(os.path.join(t_dir, "index.html")):
                try:
                    return render_template("index.html")
                except Exception:
                    return send_from_directory(t_dir, "index.html")
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
