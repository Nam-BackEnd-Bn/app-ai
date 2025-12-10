"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os
from urllib.parse import quote_plus
from typing import Optional

# Base class for all models
Base = declarative_base()


class DatabaseConfig:
    """Database configuration class."""
    
    def __init__(self):
        # MySQL connection string
        # Format: mysql+pymysql://user:password@host:port/database
        self.db_user = os.getenv('DB_USER', 'root')
        self.db_password = os.getenv('DB_PASSWORD', 'Aa@123456')
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '3306')
        self.db_name = os.getenv('DB_NAME', 'automation')
        
        # URL-encode password and username to handle special characters like @, #, etc.
        encoded_user = quote_plus(self.db_user)
        encoded_password = quote_plus(self.db_password)
        
        self.connection_string = (
            f"mysql+pymysql://{encoded_user}:{encoded_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )
    
    def get_connection_string(self) -> str:
        """Get the database connection string."""
        return self.connection_string


# Global database config
_db_config: Optional[DatabaseConfig] = None
_engine = None
_session_factory = None


def init_db(config: Optional[DatabaseConfig] = None):
    """
    Initialize the database connection.
    
    Args:
        config: DatabaseConfig instance. If None, creates a new one.
    """
    global _db_config, _engine, _session_factory
    
    if config is None:
        _db_config = DatabaseConfig()
    else:
        _db_config = config
    
    _engine = create_engine(
        _db_config.get_connection_string(),
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,   # Recycle connections after 1 hour
        echo=False  # Set to True for SQL query logging
    )
    
    _session_factory = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    )
    
    # Create all tables (import models to register them)
    try:
        from src.models.user import User  # Import to register the model
        from src.models.task_ai_image_voice_canva_instagram import TaskAIImageVoiceCanvaInstagram  # Import to register the model
        Base.metadata.create_all(bind=_engine)
    except ImportError:
        # Models not available yet, tables will be created when models are imported
        pass


def get_db_session():
    """
    Get a database session.
    
    Returns:
        Database session
    """
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _session_factory()

