"""
Database Connection Manager
Handles PostgreSQL connections and sessions
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import logging

from .models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manage database connections and sessions
    """
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialized = False
    
    def initialize(self, database_url: str = None):
        """
        Initialize database connection
        """
        if self._initialized:
            return
        
        # Get database URL from env or parameter
        if database_url is None:
            database_url = os.getenv(
                'DATABASE_URL',
                'postgresql://localhost/trading_framework'
            )
        
        # Create engine with connection pooling
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connections before using
            echo=False  # Set to True for SQL debugging
        )
        
        # Create session factory
        self.SessionLocal = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        )
        
        self._initialized = True
        logger.info("Database connection initialized")
    
    def create_tables(self):
        """
        Create all tables
        """
        if not self._initialized:
            self.initialize()
        
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")
    
    def drop_tables(self):
        """
        Drop all tables (use with caution!)
        """
        if not self._initialized:
            self.initialize()
        
        Base.metadata.drop_all(bind=self.engine)
        logger.info("Database tables dropped")
    
    @contextmanager
    def get_session(self) -> Generator:
        """
        Get database session with automatic cleanup
        
        Usage:
            with db.get_session() as session:
                session.query(Prediction).all()
        """
        if not self._initialized:
            self.initialize()
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def close(self):
        """
        Close all connections
        """
        if self.SessionLocal:
            self.SessionLocal.remove()
        if self.engine:
            self.engine.dispose()
        self._initialized = False
        logger.info("Database connections closed")


# Global database manager instance
db_manager = DatabaseManager()


# Convenience functions
def get_db():
    """Get database session"""
    return db_manager.get_session()


def init_db(database_url: str = None):
    """Initialize database"""
    db_manager.initialize(database_url)
    db_manager.create_tables()


def close_db():
    """Close database connections"""
    db_manager.close()


if __name__ == "__main__":
    # Test database connection
    print("Testing database connection...")
    
    try:
        init_db()
        print("✅ Database initialized successfully")
        
        with get_db() as session:
            print("✅ Database session created successfully")
        
        print("✅ All database tests passed!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
    
    finally:
        close_db()
