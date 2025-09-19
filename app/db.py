from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Get DATABASE_URL and ensure SSL mode for production
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/icc_rules"
)

# Render.com provides DATABASE_URL starting with postgres:// but SQLAlchemy 2.0 expects postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Add SSL mode for production databases if not already present
if DATABASE_URL and "sslmode=" not in DATABASE_URL and not DATABASE_URL.startswith("sqlite"):
    # Use connection pooling for Supabase compatibility
    if "?" in DATABASE_URL:
        DATABASE_URL += "&sslmode=require&pgbouncer=true"
    else:
        DATABASE_URL += "?sslmode=require&pgbouncer=true"

# Create engine with production-ready settings
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        pool_size=5,         # Connection pool size
        max_overflow=10,     # Maximum overflow connections
        echo=False           # Set to True for SQL debugging
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modern SQLAlchemy 2.0 style Base class
class Base(DeclarativeBase):
    pass

def get_db() -> Session:
    """
    Database dependency for FastAPI endpoints
    Provides database session with proper cleanup
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """
    Create all tables in the database
    Safe for production - won't fail if tables exist
    """
    try:
        from app.models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        # Don't re-raise - allow app to start even if DB is temporarily unavailable

def drop_tables():
    """
    Drop all tables in the database (for testing/development only)
    """
    try:
        from app.models import Base
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise

def test_connection():
    """
    Test database connection
    Returns True if connection is successful, False otherwise
    """
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()  # Ensure the query actually executes
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        # Try alternative approach for compatibility
        try:
            with engine.connect() as connection:
                connection.exec_driver_sql("SELECT 1")
            logger.info("Database connection test successful (fallback method)")
            return True
        except Exception as e2:
            logger.error(f"Database connection test failed (fallback): {e2}")
            return False