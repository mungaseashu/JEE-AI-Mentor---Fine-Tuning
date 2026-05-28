# ==============================================================================
# JEE MENTOR AI - TRANSACTIONAL DATABASE CONNECTOR (SQLAlchemy)
# ==============================================================================
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings

Base = declarative_base()

# Local SQLite fallback definition
SQLite_DB_PATH = os.path.join(os.path.dirname(__file__), "jee_mentor.db")
SQLITE_URL = f"sqlite:///{SQLite_DB_PATH}"

_engine = None
SessionLocal = None

def initialize_database():
    """Initializes the database connection, checking PostgreSQL availability first."""
    global _engine, SessionLocal
    
    db_url = settings.DATABASE_URL
    
    # Try PostgreSQL first if configured
    if db_url and db_url.startswith("postgresql"):
        try:
            print(f"[INFO] Connecting to PostgreSQL Database...")
            # Set pool_pre_ping to check active connections and recycle dead ones
            _engine = create_engine(db_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
            
            # Simple test query to assert active connection
            with _engine.connect() as conn:
                conn.execute(Base.metadata.schema.select_pre_execution_check() if hasattr(Base.metadata, 'schema') else "SELECT 1")
            print("[SUCCESS] Active PostgreSQL connection established.")
            return
        except Exception as e:
            print(f"[WARNING] PostgreSQL connection failed: {e}")
            print("[INFO] Rolling back to local SQLite fallback database...")
            
    # SQLite Fallback Configuration
    print(f"[INFO] Initializing SQLite database at: {SQLite_DB_PATH}")
    _engine = create_engine(
        SQLITE_URL, 
        connect_args={"check_same_thread": False} # Required for multi-threaded FastAPI calls
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    print("[SUCCESS] SQLite database successfully configured.")

# Trigger engine binding at module load
initialize_database()

# FastAPI Dependency to yield transactional session instances
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
