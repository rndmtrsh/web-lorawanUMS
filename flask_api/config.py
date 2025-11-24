# flask_api/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# BASE_DIR = /home/akmal/lorawanums
BASE_DIR = Path(__file__).resolve().parent.parent

# Muat .env dari root project
load_dotenv(BASE_DIR / ".env")


class Config:
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT"))
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    API_KEY = os.getenv("API_KEY")

    FLASK_PORT = int(os.getenv("FLASK_PORT"))
