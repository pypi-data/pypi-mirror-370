"""
Database connection and session management
"""

from contextlib import contextmanager
import logging
import os
from typing import Generator, Optional

from reasoning_kernel.database.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker


logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage PostgreSQL database connections"""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")

        # Create engine with connection pooling
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=300,  # Recycle connections after 5 minutes
            echo=False,  # Set to True for SQL debugging
        )

        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    logger.info("Database manager initialized")

    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped")
        except Exception as e:
            logger.error(f"Error dropping database tables: {e}")
            raise

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def get_db(self) -> Generator[Session, None, None]:
        """Dependency for FastAPI endpoints"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def cleanup(self):
        """Clean up database connections"""
        self.engine.dispose()
        logger.info("Database connections closed")


# Global database manager instance
db_manager: Optional[DatabaseManager] = None


def init_database(database_url: Optional[str] = None) -> DatabaseManager:
    """Initialize the database manager"""
    global db_manager

    if db_manager is None:
        db_manager = DatabaseManager(database_url)
        db_manager.create_tables()

    return db_manager


def get_db_manager() -> DatabaseManager:
    """Get the current database manager instance"""
    if db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return db_manager
