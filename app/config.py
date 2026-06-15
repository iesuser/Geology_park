import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
  SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-in-production")
  SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'museum.db'}"
  )
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
  ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

  BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000").rstrip("/")

  UPLOAD_FOLDER = BASE_DIR / "app" / "static" / "uploads"
  QR_FOLDER = UPLOAD_FOLDER / "qrcodes"
  ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
  MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

  WTF_CSRF_ENABLED = True
  SESSION_COOKIE_HTTPONLY = True
  SESSION_COOKIE_SAMESITE = "Lax"
