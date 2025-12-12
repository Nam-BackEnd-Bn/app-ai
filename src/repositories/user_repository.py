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

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User object or None if not found
        """
        return self.session.query(User).filter(User.user_email == email).first()

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
