"""Manager Image AI User Attached service for business logic."""

from typing import List, Optional
from src.repositories.manager_image_ai_user_attached_repository import ManagerImageAIUserAttachedRepository
from src.enums.ETypeSocial import ETypeSocial
from src.enums.EFolderImageAI import EFolderImageAI
from src.schemas.manager_image_ai_user_attached import ManagerImageAIUserAttached
from datetime import datetime
import uuid


class ManagerImageAIUserAttachedService:
    """Service for Manager Image AI User Attached business logic."""
    
    def __init__(self, repository: ManagerImageAIUserAttachedRepository):
        """
        Initialize service with repository.
        
        Args:
            repository: ManagerImageAIUserAttachedRepository instance
        """
        self.repository = repository
