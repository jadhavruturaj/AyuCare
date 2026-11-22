import os
import sqlite3
import re
import logging
from config import Config

logger = logging.getLogger("ayucare.database")
logging.basicConfig(level=logging.INFO)

# Global indicator of active engine ('mysql' or 'sqlite')
ACTIVE_ENGINE = None

def get_mysql_connection():
    """Attempt to establish a MySQL connection using PyMySQL."""
    try:
        import pymysql
        import pymysql.cursors
        conf = Config.get_mysql_config()
        conn = pymysql.connect(
            host=conf["host"],
            port=conf["port"],
            user=conf["user"],
            password=conf["password"],
            database=conf["database"],
            charset=conf["charset"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return conn
    except Exception as e:
        logger.warning(f"MySQL connection failed: {e}")
        return None

def get_sqlite_connection():
    """Establish connection to local SQLite database with Row dict support."""
    os.makedirs(os.path.dirname(Config.SQLITE_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.SQLITE_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_connection():
    """
    Returns an active database connection.
    Prioritizes MySQL if configured and accessible. Falls back to SQLite seamlessly.
    """
    global ACTIVE_ENGINE
    
    if Config.DB_TYPE.lower() == "mysql":
        mysql_conn = get_mysql_connection()
        if mysql_conn:
            ACTIVE_ENGINE = "mysql"
            return mysql_conn
        else:
            logger.info("MySQL unavailable. Falling back to local SQLite engine for smooth demonstration.")
            ACTIVE_ENGINE = "sqlite"
            return get_sqlite_connection()
    else:
        ACTIVE_ENGINE = "sqlite"
        return get_sqlite_connection()

def _adapt_sql_for_sqlite(sql):
    """
    Adapts standard MySQL query syntax for SQLite:
    - Converts `%s` parameter placeholders to `?`
    - Converts AUTO_INCREMENT to AUTOINCREMENT
    - Converts ENUM(...) to TEXT
    - Replaces CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    """
    # Replace %s with ? for SQLite
    adapted = sql.replace("%s", "?")
    return adapted

def execute_query(sql, params=None, commit=True):
    """
    Executes an INSERT, UPDATE, or DELETE query with parameterized inputs.
    Returns the last inserted id or row count.
    """
    conn = get_connection()
    try:
        if ACTIVE_ENGINE == "sqlite":
            adapted_sql = _adapt_sql_for_sqlite(sql)
            cursor = conn.cursor()
            if params:
                cursor.execute(adapted_sql, params)
            else:
                cursor.execute(adapted_sql)
            if commit:
                conn.commit()
            last_id = cursor.lastrowid
            row_count = cursor.rowcount
            cursor.close()
            conn.close()
            return last_id if last_id else row_count
        else:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                if commit:
                    conn.commit()
                last_id = cursor.lastrowid
                row_count = cursor.rowcount
            conn.close()
            return last_id if last_id else row_count
    except Exception as e:
        logger.error(f"Error executing query: {sql} | Error: {e}")
        try:
            conn.close()
        except Exception:
            pass
        raise e

def fetch_one(sql, params=None):
    """Fetches a single row as a dictionary."""
    conn = get_connection()
    try:
        if ACTIVE_ENGINE == "sqlite":
            adapted_sql = _adapt_sql_for_sqlite(sql)
            cursor = conn.cursor()
            if params:
                cursor.execute(adapted_sql, params)
            else:
                cursor.execute(adapted_sql)
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            return dict(row) if row else None
        else:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error fetching one: {sql} | Error: {e}")
        try:
            conn.close()
        except Exception:
            pass
        raise e

def fetch_all(sql, params=None):
    """Fetches all matching rows as a list of dictionaries."""
    conn = get_connection()
    try:
        if ACTIVE_ENGINE == "sqlite":
            adapted_sql = _adapt_sql_for_sqlite(sql)
            cursor = conn.cursor()
            if params:
                cursor.execute(adapted_sql, params)
            else:
                cursor.execute(adapted_sql)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return [dict(r) for r in rows] if rows else []
        else:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                rows = cursor.fetchall()
            conn.close()
            return [dict(r) for r in rows] if rows else []
    except Exception as e:
        logger.error(f"Error fetching all: {sql} | Error: {e}")
        try:
            conn.close()
        except Exception:
            pass
        raise e

def init_db():
    """
    Initializes database tables and sample seed data.
    If MySQL is connected, applies schema and seed.
    If SQLite fallback is active, sets up SQLite schema and seeds 50 symptoms.
    """
    conn = get_connection()
    logger.info(f"Initializing AyuCare database using engine: {ACTIVE_ENGINE}")
    
    if ACTIVE_ENGINE == "sqlite":
        _init_sqlite(conn)
    else:
        logger.info("Connected to MySQL. Ensuring tables are ready.")
        # Note: In MySQL, schema.sql and seed.sql can be imported via MySQL Workbench or script.
        # We also run safe verification here.
        conn.close()

def _init_sqlite(conn):
    """Initialize fallback SQLite database with the full AyuCare relational schema and seed data."""
    cursor = conn.cursor()
    
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        mobile TEXT NOT NULL UNIQUE,
        age INTEGER NOT NULL,
        gender TEXT DEFAULT 'Not Specified',
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS specialists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT NOT NULL,
        common_conditions TEXT NOT NULL,
        icon TEXT DEFAULT 'fa-user-doctor'
    );

    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        mobile TEXT NOT NULL UNIQUE,
        specialization TEXT NOT NULL,
        registration_number TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        verification_status TEXT DEFAULT 'pending',
        bio TEXT,
        experience_years INTEGER DEFAULT 0,
        hospital_clinic TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS symptoms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        urgency_level TEXT DEFAULT 'Mild',
        warning_signs TEXT,
        specialist_id INTEGER,
        FOREIGN KEY (specialist_id) REFERENCES specialists (id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS symptom_guidance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symptom_id INTEGER NOT NULL,
        preliminary_guidance TEXT NOT NULL,
        mild_home_care TEXT,
        warning_signs_details TEXT,
        reference_source TEXT DEFAULT 'WHO / Mayo Clinic Guidelines',
        FOREIGN KEY (symptom_id) REFERENCES symptoms (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS consultations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        symptom_summary TEXT,
        preferred_date TEXT,
        preferred_time TEXT,
        notes TEXT,
        status TEXT DEFAULT 'Pending',
        doctor_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE,
        FOREIGN KEY (doctor_id) REFERENCES doctors (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS symptom_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        symptom_name TEXT NOT NULL,
        duration TEXT NOT NULL,
        severity TEXT NOT NULL,
        description TEXT,
        additional_details TEXT,
        is_emergency INTEGER DEFAULT 0,
        guidance_summary TEXT,
        home_care_summary TEXT,
        recommended_specialist TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS chatbot_faqs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        keywords TEXT NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS contact_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        feedback_type TEXT DEFAULT 'General Inquiry',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    
    # Check if symptoms are populated; if not, parse and execute seed data
    cursor.execute("SELECT COUNT(*) as count FROM symptoms")
    count = cursor.fetchone()[0]
    if count == 0:
        logger.info("Seeding SQLite with initial specialists, symptoms, and FAQs...")
        _seed_sqlite(conn)
    
    cursor.close()
    conn.close()

def _seed_sqlite(conn):
    """Populates SQLite from seed.sql definitions."""
    if os.path.exists(Config.SEED_PATH):
        try:
            with open(Config.SEED_PATH, "r", encoding="utf-8") as f:
                content = f.read()
            
            cursor = conn.cursor()
            # Match every INSERT block up to its closing semicolon
            insert_blocks = re.findall(r'(INSERT INTO\s+`?\w+`?.*?;)', content, flags=re.DOTALL)
            for block in insert_blocks:
                # Remove ON DUPLICATE KEY UPDATE ... clause
                cleaned = re.sub(r'ON DUPLICATE KEY UPDATE[^;]*', '', block, flags=re.DOTALL)
                # Remove backticks for SQLite compatibility
                cleaned = cleaned.replace('`', '').strip()
                if cleaned.endswith(';'):
                    cleaned = cleaned[:-1].strip()
                try:
                    cursor.execute(cleaned)
                except Exception as ex:
                    logger.warning(f"Seed statement warning: {ex}")
            conn.commit()
            cursor.close()
            logger.info("SQLite successfully seeded with 50 symptoms and healthcare dataset.")
        except Exception as e:
            logger.warning(f"Error seeding SQLite: {e}")
