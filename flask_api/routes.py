# flask_api/routes.py
import os
import json
import binascii
import threading

from flask import Blueprint, jsonify, request
from psycopg2.extras import RealDictCursor
import paho.mqtt.client as mqtt

from .auth import require_api_key
from .db import get_db

bp = Blueprint("api", __name__)

# -----------------------
# KONFIGURASI MQTT
# -----------------------

MQTT_HOST = os.getenv("MQTT_HOST", "192.168.0.232")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER", "wisgate")
MQTT_PASS = os.getenv("MQTT_PASS", "lorawanums")

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)


def run_mqtt():
    mqtt_client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
    mqtt_client.loop_forever()


# Jalankan MQTT loop di background thread
threading.Thread(target=run_mqtt, daemon=True).start()


# -----------------------
# HELPER FUNCTIONS
# -----------------------

def normalize_dev_eui(dev_eui: str) -> str:
    dev_eui = dev_eui.strip()
    if len(dev_eui) != 16:
        raise ValueError("dev_eui harus 16 karakter hex")
    return dev_eui.upper()


def parse_pagination():
    try:
        limit = int(request.args.get("limit", 50))
    except ValueError:
        limit = 50
    try:
        offset = int(request.args.get("offset", 0))
    except ValueError:
        offset = 0

    limit = max(1, min(limit, 500))
    offset = max(0, offset)
    return limit, offset


def parse_time_filter():
    ts_from = request.args.get("from")
    ts_to = request.args.get("to")
    return ts_from, ts_to


def build_ts_where_clause(ts_from, ts_to, params):
    where_parts = []
    if ts_from:
        where_parts.append("ts >= %s")
        params.append(ts_from)
    if ts_to:
        where_parts.append("ts <= %s")
        params.append(ts_to)
    if not where_parts:
        return ""
    return " AND " + " AND ".join(where_parts)


def parse_last_n(default=10, maximum=500):
    try:
        n = int(request.args.get("n", default))
    except ValueError:
        n = default
    n = max(1, min(n, maximum))
    return n


def to_hex(value):
    if value is None:
        return None
    b = value if isinstance(value, bytes) else str(value).encode("utf-8")
    return binascii.hexlify(b).decode("ascii").upper()


# ------------------------------------------------
# UPLINKS - LIST DEVICES (overview & debugging)
# ------------------------------------------------

@bp.route("/api/uplinks/devices", methods=["GET"])
@require_api_key
def list_uplink_devices():
    """Daftar dev_eui yang memiliki data uplink dan jumlah paketnya."""
    conn = get_db()
    sql = """
        SELECT UPPER(dev_eui) AS dev_eui, COUNT(*) AS uplink_count
        FROM iot.uplinks
        GROUP BY UPPER(dev_eui)
        ORDER BY dev_eui;
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql)
        rows = cur.fetchall()

    return jsonify(rows)


# -----------------------
# UPLINKS - DATA PENTING
# -----------------------

@bp.route("/api/uplinks/<dev_eui>", methods=["GET"])
@require_api_key
def list_uplinks_compact(dev_eui):
    try:
        dev_eui = normalize_dev_eui(dev_eui)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    limit, offset = parse_pagination()
    ts_from, ts_to = parse_time_filter()

    conn = get_db()
    params = [dev_eui]
    where_clause = build_ts_where_clause(ts_from, ts_to, params)

    sql = f"""
        SELECT
            uplink_id,
            inserted_at,
            app_name,
            dev_eui,
            device_name,
            ts,
            fcnt,
            fport,
            data_hex,
            data_text,
            data_json,
            rssi_dbm,
            snr_db,
            dr,
            freq_hz
        FROM iot.uplinks
        WHERE UPPER(dev_eui) = %s
        {where_clause}
        ORDER BY ts DESC NULLS LAST, inserted_at DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    return jsonify(rows)


@bp.route("/api/uplinks/<dev_eui>/latest", methods=["GET"])
@require_api_key
def latest_uplink_compact(dev_eui):
    try:
        dev_eui = normalize_dev_eui(dev_eui)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    conn = get_db()
    sql = """
        SELECT
            uplink_id,
            inserted_at,
            app_name,
            dev_eui,
            device_name,
            ts,
            fcnt,
            fport,
            data_hex,
            data_text,
            data_json,
            rssi_dbm,
            snr_db,
            dr,
            freq_hz
        FROM iot.uplinks
        WHERE UPPER(dev_eui) = %s
        ORDER BY ts DESC NULLS LAST, inserted_at DESC
        LIMIT 1
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (dev_eui,))
        row = cur.fetchone()

    if not row:
        return jsonify({"error": "No uplink found for this dev_eui"}), 404

    return jsonify(row)


@bp.route("/api/uplinks/<dev_eui>/last10", methods=["GET"])
@require_api_key
def last_10_uplinks(dev_eui):
    """
    N data uplink terakhir (versi compact) untuk dev_eui tertentu.
    Gunakan query ?n=jumlah, default 10, maksimal 500.
    Contoh: /api/uplinks/<dev_eui>/last10?n=25
    """
    try:
        dev_eui = normalize_dev_eui(dev_eui)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    last_n = parse_last_n(default=10, maximum=500)

    conn = get_db()
    sql = """
        SELECT
            uplink_id,
            inserted_at,
            app_name,
            dev_eui,
            device_name,
            ts,
            fcnt,
            fport,
            data_hex,
            data_text,
            data_json,
            rssi_dbm,
            snr_db,
            dr,
            freq_hz
        FROM iot.uplinks
        WHERE UPPER(dev_eui) = %s
        ORDER BY ts DESC NULLS LAST, inserted_at DESC
        LIMIT %s
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (dev_eui, last_n))
        rows = cur.fetchall()

    if not rows:
        return jsonify({"error": "No uplink found for this dev_eui"}), 404

    return jsonify(rows)


# -----------------------
# UPLINKS - DATA LENGKAP
# -----------------------

@bp.route("/api/uplinks/<dev_eui>/full", methods=["GET"])
@require_api_key
def list_uplinks_full(dev_eui):
    try:
        dev_eui = normalize_dev_eui(dev_eui)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    limit, offset = parse_pagination()
    ts_from, ts_to = parse_time_filter()

    conn = get_db()
    params = [dev_eui]
    where_clause = build_ts_where_clause(ts_from, ts_to, params)

    sql = f"""
        SELECT
            uplink_id,
            inserted_at,
            app_id,
            app_name,
            dev_eui,
            device_name,
            ts,
            fcnt,
            fport,
            data_hex,
            data_text,
            data_json,
            rssi_dbm,
            snr_db,
            dr,
            freq_hz,
            raw
        FROM iot.uplinks
        WHERE UPPER(dev_eui) = %s
        {where_clause}
        ORDER BY ts DESC NULLS LAST, inserted_at DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    return jsonify(rows)


@bp.route("/api/uplinks/<dev_eui>/latest/full", methods=["GET"])
@require_api_key
def latest_uplink_full(dev_eui):
    try:
        dev_eui = normalize_dev_eui(dev_eui)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    conn = get_db()
    sql = """
        SELECT
            uplink_id,
            inserted_at,
            app_id,
            app_name,
            dev_eui,
            device_name,
            ts,
            fcnt,
            fport,
            data_hex,
            data_text,
            data_json,
            rssi_dbm,
            snr_db,
            dr,
            freq_hz,
            raw
        FROM iot.uplinks
        WHERE UPPER(dev_eui) = %s
        ORDER BY ts DESC NULLS LAST, inserted_at DESC
        LIMIT 1
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (dev_eui,))
        row = cur.fetchone()

    if not row:
        return jsonify({"error": "No uplink found for this dev_eui"}), 404

    return jsonify(row)


# -----------------------
# DOWNLINK VIA MQTT
# -----------------------

@bp.route("/api/downlink", methods=["POST"])
@require_api_key
def api_downlink():
    """
    Mengirim perintah downlink ke perangkat melalui MQTT.
    Body JSON minimal:
    {
      "applicationName": "LabElektro",
      "devEUI": "be078ddb76f70371",
      "fPort": 1,
      "confirmed": false,
      "data_hex": "414243",
      "data_text": "ABC"
    }

    - Jika data_hex tidak diisi, akan menggunakan data_text dan dikonversi ke hex.
    - devEUI akan dikirim ke broker dalam format lowercase.
    """
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    try:
        appname = data["applicationName"]
        deveui = data["devEUI"].lower()
    except KeyError as e:
        return jsonify({"error": f"Missing field: {e.args[0]}"}), 400

    try:
        fport = int(data.get("fPort", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "fPort must be integer"}), 400

    confirmed = bool(data.get("confirmed", False))

    data_hex = data.get("data_hex")
    if not data_hex:
        data_hex = to_hex(data.get("data_text", ""))
    if not data_hex:
        return jsonify({"error": "Either data_hex or data_text must be provided"}), 400

    payload = {
        "confirmed": confirmed,
        "fPort": fport,
        "data": data_hex,
        "data_encode": "hexstring",
    }

    topic = f"application/{appname}/device/{deveui}/tx"

    info = mqtt_client.publish(topic, json.dumps(payload), qos=1, retain=False)
    info.wait_for_publish()

    return jsonify({
        "published": True,
        "topic": topic,
        "payload": payload
    })
