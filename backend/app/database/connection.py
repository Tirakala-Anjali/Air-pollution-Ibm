"""
Database connection and session management.
Uses SQLAlchemy with SQLite (can be swapped for PostgreSQL by
changing DATABASE_URL in .env).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.utils.config import settings
import logging

logger = logging.getLogger(__name__)

# Create engine
# For PostgreSQL: set DATABASE_URL=postgresql://user:pass@host/dbname in .env
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


def get_db():
    """FastAPI dependency – yields a database session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables on startup."""
    from app.models import air_quality, pollution_event  # noqa: F401 – register models
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created / verified.")
