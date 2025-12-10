"""Task service for business logic."""

from typing import List, Optional, Dict
from src.repositories.task_repository import TaskRepository
from src.models.task_ai_image_voice_canva_instagram import TaskAIImageVoiceCanvaInstagram


class TaskService:
    """Service for task-related business logic."""
    
    def __init__(self, task_repository: TaskRepository):
        """
        Initialize service with task repository.
        
        Args:
            task_repository: TaskRepository instance
        """
        self.task_repository = task_repository
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict]:
        """
        Get task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task dictionary or None if not found
        """
        task = self.task_repository.get_by_id(task_id)
        return task.to_dict() if task else None
    
    def get_all_tasks(self, page: int = 1, per_page: int = 10) -> Dict:
        """
        Get paginated list of tasks.
        
        Args:
            page: Page number (1-based)
            per_page: Number of items per page
            
        Returns:
            Dictionary with tasks, total count, and pagination info
        """
        tasks, total = self.task_repository.get_paginated(page, per_page)
        
        return {
            'tasks': [task.to_dict() for task in tasks],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page if total > 0 else 0
        }

