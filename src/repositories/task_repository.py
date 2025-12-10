"""Task repository for database queries."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.task_ai_image_voice_canva_instagram import TaskAIImageVoiceCanvaInstagram


class TaskRepository:
    """Repository for Task database operations."""
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
    
    def get_by_id(self, task_id: str) -> Optional[TaskAIImageVoiceCanvaInstagram]:
        """
        Get task by ID.
        
        Args:
            task_id: Task ID (UUID string)
            
        Returns:
            Task object or None if not found
        """
        return self.session.query(TaskAIImageVoiceCanvaInstagram).filter(
            TaskAIImageVoiceCanvaInstagram.id == task_id
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[TaskAIImageVoiceCanvaInstagram]:
        """
        Get all tasks with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Task objects
        """
        return self.session.query(TaskAIImageVoiceCanvaInstagram).offset(skip).limit(limit).all()
    
    def get_count(self) -> int:
        """
        Get total count of tasks.
        
        Returns:
            Total number of tasks
        """
        return self.session.query(func.count(TaskAIImageVoiceCanvaInstagram.id)).scalar()
    
    def get_paginated(self, page: int, per_page: int) -> tuple[List[TaskAIImageVoiceCanvaInstagram], int]:
        """
        Get paginated tasks.
        
        Args:
            page: Page number (1-based)
            per_page: Number of items per page
            
        Returns:
            Tuple of (list of tasks, total count)
        """
        skip = (page - 1) * per_page
        tasks = self.get_all(skip=skip, limit=per_page)
        total = self.get_count()
        return tasks, total

