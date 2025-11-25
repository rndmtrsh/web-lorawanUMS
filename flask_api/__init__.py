# flask_api/__init__.py
from flask import Flask
from flask_cors import CORS
from .config import Config
from .db import init_app as init_db
from .routes import bp as api_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Aktifkan CORS untuk semua endpoint /api/*
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=False,
        allow_headers=["Content-Type", "X-API-Key"],
        methods=["GET", "POST", "OPTIONS"]
    )

    init_db(app)
    app.register_blueprint(api_bp)

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    return app
