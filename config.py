import os
from dotenv import load_dotenv
from datetime import timedelta
from urllib.parse import quote_plus
import cloudinary

load_dotenv()

class Config:
    
    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_DATABASE = os.environ.get("DB_DATABASE")
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = quote_plus(os.environ.get("DB_PASSWORD", ""))

    # ================= CLOUDINARY =================
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")

    # ================= SECURITY =================
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # ================= DATABASE =================
    #SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    )
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
    
# Initialize Cloudinary Configuration
cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET,
    secure=True
)