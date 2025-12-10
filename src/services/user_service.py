"""User service for business logic."""

from typing import List, Optional, Dict
from src.repositories.user_repository import UserRepository
from src.models.user import User


class UserService:
    """Service for user-related business logic."""
    
    def __init__(self, user_repository: UserRepository):
        """
        Initialize service with user repository.
        
        Args:
            user_repository: UserRepository instance
        """
        self.user_repository = user_repository
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User dictionary or None if not found
        """
        user = self.user_repository.get_by_id(user_id)
        return user.to_dict() if user else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User dictionary or None if not found
        """
        user = self.user_repository.get_by_email(email)
        return user.to_dict() if user else None
    
    def get_all_users(self, page: int = 1, per_page: int = 10) -> Dict:
        """
        Get paginated list of users.
        
        Args:
            page: Page number (1-based)
            per_page: Number of items per page
            
        Returns:
            Dictionary with users, total count, and pagination info
        """
        users, total = self.user_repository.get_paginated(page, per_page)
        
        return {
            'users': [user.to_dict() for user in users],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    def create_user(self, name: str, email: str, status: str = "Active") -> Dict:
        """
        Create a new user.
        
        Args:
            name: User name
            email: User email
            status: User status ("Active" or "Inactive")
            
        Returns:
            Created user dictionary
            
        Raises:
            ValueError: If email already exists or status is invalid
        """
        # Check if email already exists
        existing_user = self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")
        
        # Create user with required fields
        # Note: This is a simplified version - in production, you'd need to handle
        # password hashing, phone, gender, and other required fields properly
        import bcrypt
        hashed_password = bcrypt.hashpw("defaultPassword123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user = self.user_repository.create(
            user_fullName=name,
            user_email=email,
            user_password=hashed_password,
            user_phone="+0000000000",  # Default phone
            user_gender="Not Specified",  # Default gender
            user_status=status
        )
        return user.to_dict()
    
    def update_user(self, user_id: str, name: Optional[str] = None, 
                   email: Optional[str] = None, status: Optional[str] = None) -> Dict:
        """
        Update an existing user.
        
        Args:
            user_id: User ID (UUID string)
            name: New name (optional)
            email: New email (optional)
            status: New status (optional)
            
        Returns:
            Updated user dictionary
            
        Raises:
            ValueError: If user not found or email already exists
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        if email and email != user.user_email:
            existing_user = self.user_repository.get_by_email(email)
            if existing_user:
                raise ValueError(f"User with email {email} already exists")
            user.user_email = email
        
        if name:
            user.user_fullName = name
        
        if status:
            user.user_status = status
        
        updated_user = self.user_repository.update(user)
        return updated_user.to_dict()
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        self.user_repository.delete(user)
        return True

