# flask_api/db.py
from flask import current_app, g
from psycopg2.pool import SimpleConnectionPool

_pool: SimpleConnectionPool | None = None


def init_app(app):
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=app.config["DB_HOST"],
            port=app.config["DB_PORT"],
            dbname=app.config["DB_NAME"],
            user=app.config["DB_USER"],
            password=app.config["DB_PASSWORD"],
        )

    @app.teardown_appcontext
    def close_db(exception=None):
        conn = g.pop("db_conn", None)
        if conn is not None and _pool is not None:
            _pool.putconn(conn)


def get_db():
    global _pool
    if _pool is None:
        raise RuntimeError("Database pool belum diinisialisasi. Panggil init_app(app) dulu.")

    if "db_conn" not in g:
        g.db_conn = _pool.getconn()
    return g.db_conn
