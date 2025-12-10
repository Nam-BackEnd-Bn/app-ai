"""Authentication service for business logic."""

from typing import Optional, Dict
from src.repositories.user_repository import UserRepository


class AuthService:
    """Service for authentication-related business logic."""
    
    def __init__(self, user_repository: UserRepository):
        """
        Initialize service with user repository.
        
        Args:
            user_repository: UserRepository instance
        """
        self.user_repository = user_repository
    
    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate a user.
        
        Args:
            username: Username (can be email or username)
            password: Password
            
        Returns:
            True if authentication successful, False otherwise
        """
        import bcrypt
        
        # Check if username is an email and user exists
        user = self.user_repository.get_by_email(username)
        if user:
            # Verify password hash
            try:
                if bcrypt.checkpw(password.encode('utf-8'), user.user_password.encode('utf-8')):
                    return True
            except Exception:
                return False
        
        return False
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """
        Get user by username or email.
        
        Args:
            username: Username or email
            
        Returns:
            User dictionary or None if not found
        """
        user = self.user_repository.get_by_email(username)
        return user.to_dict() if user else None

