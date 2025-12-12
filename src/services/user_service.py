"""User service for business logic."""

from typing import Dict
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
