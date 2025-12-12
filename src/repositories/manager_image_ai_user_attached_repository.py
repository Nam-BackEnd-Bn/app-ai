"""Manager Image AI User Attached repository for database queries."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.manager_image_ai_user_attached import ManagerImageAIUserAttached
import uuid


class ManagerImageAIUserAttachedRepository:
    """Repository for ManagerImageAIUserAttached database operations."""
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
    