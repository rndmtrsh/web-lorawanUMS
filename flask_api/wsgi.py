
import os

try:
    # Jika app.py punya factory function: create_app()
    from flask_api.app import create_app

    app = create_app()
except ImportError:
    # Jika tidak ada create_app, ambil langsung objek app
    from flask_api.app import app  # type: ignore


if __name__ == "__main__":
    # Untuk testing langsung: python -m flask_api.wsgi
    port = int(os.environ.get("FLASK_PORT"))
    app.run(host="0.0.0.0", port=port)
