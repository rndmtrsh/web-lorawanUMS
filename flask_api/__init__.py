# flask_api/__init__.py
from flask import Flask
from .config import Config
from .db import init_app as init_db
from .routes import bp as api_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_db(app)
    app.register_blueprint(api_bp)

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    return app
