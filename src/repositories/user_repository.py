"""User repository for database queries."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.user import User


class UserRepository:
    """Repository for User database operations."""
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID (UUID string)
            
        Returns:
            User object or None if not found
        """
        return self.session.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User object or None if not found
        """
        return self.session.query(User).filter(User.user_email == email).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of User objects
        """
        return self.session.query(User).offset(skip).limit(limit).all()
    
    def get_count(self) -> int:
        """
        Get total count of users.
        
        Returns:
            Total number of users
        """
        return self.session.query(func.count(User.id)).scalar()
    
    def create(self, user_fullName: str, user_email: str, user_password: str, 
               user_phone: str, user_gender: str, user_status: str = "Active",
               user_isRootAdmin: bool = False, user_isSubAdmin: bool = False,
               **kwargs) -> User:
        """
        Create a new user.
        
        Args:
            user_fullName: User full name
            user_email: User email
            user_password: User password (should be hashed)
            user_phone: User phone number
            user_gender: User gender
            user_status: User status (default: "Active")
            user_isRootAdmin: Is root admin (default: False)
            user_isSubAdmin: Is sub admin (default: False)
            **kwargs: Additional optional fields (user_avatar, user_address, etc.)
            
        Returns:
            Created User object
        """
        import uuid
        user = User(
            id=str(uuid.uuid4()),
            user_fullName=user_fullName,
            user_email=user_email,
            user_password=user_password,
            user_phone=user_phone,
            user_gender=user_gender,
            user_status=user_status,
            user_isRootAdmin=user_isRootAdmin,
            user_isSubAdmin=user_isSubAdmin,
            **kwargs
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def update(self, user: User) -> User:
        """
        Update an existing user.
        
        Args:
            user: User object to update
            
        Returns:
            Updated User object
        """
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def delete(self, user: User) -> None:
        """
        Delete a user.
        
        Args:
            user: User object to delete
        """
        self.session.delete(user)
        self.session.commit()
    
    def get_paginated(self, page: int, per_page: int) -> tuple[List[User], int]:
        """
        Get paginated users.
        
        Args:
            page: Page number (1-based)
            per_page: Number of items per page
            
        Returns:
            Tuple of (list of users, total count)
        """
        skip = (page - 1) * per_page
        users = self.get_all(skip=skip, limit=per_page)
        total = self.get_count()
        return users, total

