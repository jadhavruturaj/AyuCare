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
    SECRET_KEY = os.getenv("SECRET_KEY", "ayucare-secure-secret-key-engineering-2026")
    
    # Database Settings
    DB_TYPE = os.getenv("DB_TYPE", "mysql")  # 'mysql' or 'sqlite'
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "ayucare_db")
    
    # SQLite fallback database file
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", str(PROJECT_DIR / "database" / "ayucare_fallback.db"))
    
    # SQL Schema & Seed scripts
    SCHEMA_PATH = str(PROJECT_DIR / "database" / "schema.sql")
    SEED_PATH = str(PROJECT_DIR / "database" / "seed.sql")
    
    # Security & Tokens
    TOKEN_EXPIRATION_HOURS = int(os.getenv("TOKEN_EXPIRATION_HOURS", 24))
    
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
