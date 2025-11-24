# flask_api/app.py
import os
from . import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT"))
    app.run(host="127.0.0.1", port=port, debug=app.config["DEBUG"])
