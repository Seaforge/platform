"""SeaForge — the open-source life-at-sea platform."""

import os
from flask import Flask
from src.data.models import init_db


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.secret_key = os.environ.get("SEAFORGE_SECRET_KEY", "dev-key-change-me")

    # Initialize database
    with app.app_context():
        init_db()

    # Register API blueprints
    from src.api.navigation import bp as nav_bp
    from src.api.wellbeing import bp as wellbeing_bp
    from src.api.training import bp as training_bp
    from src.api.ops import bp as ops_bp

    app.register_blueprint(nav_bp)
    app.register_blueprint(wellbeing_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(ops_bp)

    # Main page — serve the maritime intelligence dashboard
    @app.route("/")
    def index():
        from flask import render_template
        return render_template("index.html")

    # Health check
    @app.route("/api/health")
    def health():
        from src.core.ais import _running, get_vessel_count
        return {
            "status": "ok",
            "version": "0.1.0",
            "ais_streaming": _running,
            "ais_vessels": get_vessel_count()
        }

    # Start AIS stream if API key is configured
    ais_key = os.environ.get("AISSTREAM_API_KEY", "").strip()
    if ais_key:
        from src.core.ais import start_stream
        start_stream(ais_key)

    return app


if __name__ == "__main__":
    app = create_app()
    host = os.environ.get("SEAFORGE_HOST", "0.0.0.0")
    port = int(os.environ.get("SEAFORGE_PORT", 5000))
    debug = os.environ.get("SEAFORGE_DEBUG", "false").lower() == "true"
    app.run(host=host, port=port, debug=debug)
