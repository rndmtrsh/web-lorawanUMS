#!/usr/bin/env python3
import os
import json
import base64
from pathlib import Path
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import Json
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# ----------------------------
# Load .env
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))

MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC")


# ----------------------------
# DB connection
# ----------------------------
def connect_db():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


conn = connect_db()
conn.autocommit = False


def ensure_conn():
    global conn
    if conn is None or conn.closed:
        conn = connect_db()
        conn.autocommit = False


# ----------------------------
# Helper payload
# ----------------------------
def normalize_dev_eui(dev_eui: str) -> str:
    dev_eui = dev_eui.strip()
    if len(dev_eui) != 16:
        raise ValueError(f"Invalid devEUI length: {dev_eui}")
    return dev_eui


def decode_data_fields(data_value: str, encode_type: str | None):
    """
    Menghasilkan:
      - data_hex  : hex uppercase dari payload bytes
      - data_text : string yang 'paling berguna' (UTF-8 jika wajar, kalau tidak pakai hex)
      - data_json : dict/list jika data_text adalah JSON yang valid, selain itu None

    encode_type:
      - "hexstring"  -> data_value diasumsikan hex
      - lainnya / None -> data_value diasumsikan base64 (format default ChirpStack)
    """
    if not data_value:
        return "", None, None

    encode_type = (encode_type or "").strip().lower()

    # 1) Decode ke bytes
    data_bytes = b""
    if encode_type.startswith("hex"):
        # data adalah hexstring
        try:
            data_bytes = bytes.fromhex(data_value)
        except ValueError:
            # kalau gagal, anggap konten text biasa
            data_bytes = data_value.encode("utf-8", errors="replace")
    else:
        # fallback: assume base64
        try:
            data_bytes = base64.b64decode(data_value)
        except Exception:
            # kalau gagal, anggap konten text biasa
            data_bytes = data_value.encode("utf-8", errors="replace")

    # 2) data_hex: representasi hex dari payload bytes
    data_hex = data_bytes.hex().upper()

    # 3) coba decode sebagai UTF-8
    data_text = None
    try:
        candidate_text = data_bytes.decode("utf-8")
        # cek karakter kontrol (kecuali tab/newline/carriage return)
        has_bad_ctrl = any(
            (ord(ch) < 32 and ch not in ("\t", "\n", "\r")) for ch in candidate_text
        )
        if has_bad_ctrl:
            # banyak karakter 'aneh', lebih aman pakai hex sebagai text
            data_text = data_hex
        else:
            data_text = candidate_text
    except UnicodeDecodeError:
        # tidak bisa di-decode sebagai UTF-8, pakai hex string
        data_text = data_hex

    # 4) kalau text-nya JSON, parse ke data_json
    data_json = None
    if data_text:
        stripped = data_text.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                data_json = json.loads(data_text)
            except json.JSONDecodeError:
                data_json = None

    return data_hex, data_text, data_json


def extract_timestamp(payload: dict):
    """
    Mengambil timestamp dari beberapa kemungkinan field:
      1. rxInfo[0].time (string RFC3339)
      2. payload["time"] (string)
      3. payload["timestamp"] (UNIX epoch, detik)
    Mengembalikan:
      - datetime (timezone-aware UTC) atau
      - string time (biarkan PG parse) atau
      - None
    """
    rx_infos = payload.get("rxInfo") or []
    if rx_infos and isinstance(rx_infos, list):
        t = rx_infos[0].get("time")
        if t:
            # biarkan PostgreSQL yang parse string ISO8601 / RFC3339
            return t

    t = payload.get("time")
    if t:
        return t

    ts_epoch = payload.get("timestamp")
    if ts_epoch is not None:
        try:
            # bisa datang sebagai string atau int
            ts_int = int(ts_epoch)
            return datetime.fromtimestamp(ts_int, tz=timezone.utc)
        except Exception:
            pass

    return None


# ----------------------------
# Insert / upsert ke database
# ----------------------------
def store_uplink(msg_topic: str, payload: dict):
    """
    payload mengikuti format built-in NS WisGate/ChirpStack, contoh:
    {
      "applicationID": "1",
      "applicationName": "LabElektro",
      "devEUI": "be078ddb76f70371",
      "deviceName": "Electrons",
      "timestamp": 1763644470,
      "fCnt": 0,
      "fPort": 1,
      "data": "7B2264617461223A7B224C4452223A3132392C224C4544223A2231227D7D",
      "data_encode": "hexstring",
      "rxInfo": [...],
      "txInfo": { "frequency": 921400000, "dr": 2 }
    }
    """
    ensure_conn()
    cur = conn.cursor()

    try:
        app_id = payload.get("applicationID")
        app_name = payload.get("applicationName") or (f"app_{app_id}" if app_id else "unknown_app")
        dev_eui = normalize_dev_eui(payload.get("devEUI", ""))
        device_name = payload.get("deviceName")

        fcnt = payload.get("fCnt")
        fport = payload.get("fPort")

        data_value = payload.get("data") or ""
        encode_type = payload.get("data_encode")  # misal: "hexstring"
        data_hex, data_text, data_json = decode_data_fields(data_value, encode_type)

        ts_value = extract_timestamp(payload)

        # radio info
        rx_infos = payload.get("rxInfo") or []
        rssi_dbm = None
        snr_db = None
        if rx_infos and isinstance(rx_infos, list):
            rssi_dbm = rx_infos[0].get("rssi")
            snr_db = rx_infos[0].get("loRaSNR")

        tx_info = payload.get("txInfo") or {}
        dr = tx_info.get("dr")
        freq_hz = tx_info.get("frequency")

        raw_json = payload

        # 1) Ensure application
        cur.execute(
            """
            INSERT INTO iot.applications (app_name)
            VALUES (%s)
            ON CONFLICT (app_name) DO NOTHING;
            """,
            (app_name,),
        )

        # 2) Upsert device
        cur.execute(
            """
            INSERT INTO iot.devices (dev_eui, app_name, device_name, first_seen, last_seen)
            VALUES (%s, %s, %s, COALESCE(%s, now()), COALESCE(%s, now()))
            ON CONFLICT (dev_eui) DO UPDATE
            SET
              app_name = EXCLUDED.app_name,
              device_name = COALESCE(EXCLUDED.device_name, iot.devices.device_name),
              last_seen = COALESCE(EXCLUDED.last_seen, iot.devices.last_seen);
            """,
            (dev_eui, app_name, device_name, ts_value, ts_value),
        )

        # 3) Insert uplink
        cur.execute(
            """
            INSERT INTO iot.uplinks (
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
            )
            VALUES (
              %s, %s, %s, %s, %s,
              %s, %s,
              %s, %s, %s,
              %s, %s,
              %s, %s,
              %s
            )
            ON CONFLICT (dev_eui, fcnt, data_hex) DO NOTHING;
            """,
            (
                app_id,
                app_name,
                dev_eui,
                device_name,
                ts_value,
                fcnt,
                fport,
                data_hex,
                data_text,
                Json(data_json) if data_json is not None else None,
                rssi_dbm,
                snr_db,
                dr,
                freq_hz,
                Json(raw_json),
            ),
        )

        conn.commit()
        print(f"[DB] Stored uplink devEUI={dev_eui}, fCnt={fcnt}, topic={msg_topic}")
        print(f"       encode={encode_type}, data_hex={data_hex}")
        print(f"       data_text={data_text!r}, data_json_type={type(data_json).__name__ if data_json is not None else 'None'}")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] store_uplink failed: {e}")
    finally:
        cur.close()


# ----------------------------
# MQTT callbacks
# ----------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] Connected to {MQTT_HOST}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        print(f"[MQTT] Subscribed to: {MQTT_TOPIC}")
    else:
        print(f"[MQTT] Failed to connect, rc={rc}")


def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode("utf-8")
        data = json.loads(payload_str)
    except Exception as e:
        print(f"[MQTT] Failed to parse message on {msg.topic}: {e}")
        return

    print(f"[MQTT] RX topic={msg.topic}")
    store_uplink(msg.topic, data)


def main():
    client = mqtt.Client()

    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message

    print(f"[MQTT] Connecting to {MQTT_HOST}:{MQTT_PORT} ...")
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)

    client.loop_forever()


if __name__ == "__main__":
    main()

