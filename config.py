import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # ================= SECURITY =================
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # ================= DATABASE =================
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ================= SESSION / LOGIN =================
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # set True in production (HTTPS)

    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = False  # set True in production

    # ================= EMAIL (Flask-Mail) =================
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True") == "True"
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "False") == "True"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    MAIL_DEFAULT_SENDER = (
        os.environ.get("MAIL_SENDER_NAME", "Rice Disease System 🌾"),
        os.environ.get("MAIL_USERNAME")
    )

    # ================= API KEYS =================
    OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")

    # ================= UPLOAD (optional future use) =================
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB file upload limit