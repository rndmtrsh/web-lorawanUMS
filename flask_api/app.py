# flask_api/app.py
import os
from . import create_app
from flask_cors import CORS

app = create_app()

CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    supports_credentials=False,
    allow_headers=["Content-Type", "X-API-KEY"],
    expose_headers=["Content-Type"],
)

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT"))
    app.run(host="127.0.0.1", port=port, debug=app.config["DEBUG"])
