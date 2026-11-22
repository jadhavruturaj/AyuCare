import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory for the backend and project
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

# Load environment variables from .env file if it exists
dotenv_path = PROJECT_DIR / ".env"
if not dotenv_path.exists():
    dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path)

class Config:
    """AyuCare Configuration Class"""
    BASE_DIR = BASE_DIR
    PROJECT_DIR = PROJECT_DIR
    SECRET_KEY = os.getenv("SECRET_KEY", "ayucare-secure-secret-key-engineering-2026")
    
    # Environment detection
    is_serverless = (
        os.getenv("VERCEL") == "1"
        or "VERCEL" in os.environ
        or os.getenv("NOW_REGION") is not None
        or os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None
    )

    # Database Settings
    _raw_db_type = os.getenv("DB_TYPE", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "ayucare_db")

    # In serverless without a remote MySQL host, automatically default to SQLite
    if not _raw_db_type:
        if is_serverless and DB_HOST in ("localhost", "127.0.0.1", "::1"):
            DB_TYPE = "sqlite"
        else:
            DB_TYPE = "mysql"
    else:
        DB_TYPE = _raw_db_type

    # SQLite database file (writable /tmp on serverless environments like Vercel)
    default_sqlite = "/tmp/ayucare.db" if is_serverless else str(PROJECT_DIR / "database" / "ayucare_fallback.db")
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", default_sqlite)
    
    # SQL Schema & Seed scripts
    SCHEMA_PATH = str(PROJECT_DIR / "database" / "schema.sql")
    SEED_PATH = str(PROJECT_DIR / "database" / "seed.sql")
    
    # Security & Tokens
    TOKEN_EXPIRATION_HOURS = int(os.getenv("TOKEN_EXPIRATION_HOURS", 24))
    OTP_EXPIRATION_MINUTES = int(os.getenv("OTP_EXPIRATION_MINUTES", 10))
    PASSWORD_RESET_EXPIRATION_HOURS = int(os.getenv("PASSWORD_RESET_EXPIRATION_HOURS", 1))

    # Email Delivery Settings (SMTP)
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", os.getenv("SMTP_USER", "noreply@ayucare.health"))
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "आयुCare (AyuCare)")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True").lower() in ("true", "1", "yes")
    FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5001").rstrip("/")

    # SMS Gateway Settings
    SMS_GATEWAY = os.getenv("SMS_GATEWAY", "console").lower()  # 'twilio', 'fast2sms', or 'console'
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
    FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY", "")
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    
    # Server configuration
    PORT = int(os.getenv("PORT", 5001))
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")

    @classmethod
    def get_mysql_config(cls):
        return {
            "host": cls.DB_HOST,
            "port": cls.DB_PORT,
            "user": cls.DB_USER,
            "password": cls.DB_PASSWORD,
            "database": cls.DB_NAME,
            "charset": "utf8mb4",
            "autocommit": True
        }
