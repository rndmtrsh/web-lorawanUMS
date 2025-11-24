# flask_api/auth.py
from functools import wraps
from flask import current_app, request, jsonify


def require_api_key(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        provided_key = request.headers.get("X-API-Key")
        expected_key = current_app.config.get("API_KEY")

        if not expected_key:
            return jsonify({"error": "API key belum dikonfigurasi"}), 500

        if provided_key != expected_key:
            return jsonify({"error": "Unauthorized"}), 401

        return view_func(*args, **kwargs)

    return wrapped
