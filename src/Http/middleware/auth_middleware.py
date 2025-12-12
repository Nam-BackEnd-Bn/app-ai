"""Authentication middleware for PyQt6 application."""

import json
from typing import Any, Optional, Callable, Dict

from loguru import logger

from src.services.auth_service import AuthService
from src.services.cache_service import CacheService


class AuthMiddleware:
    """
    Authentication Middleware for PyQt6 Application
    
    Validates user authentication and handles exceptions.
    Caches user sessions for performance.
    Stores user info in state for access in controllers.
    """
    
    def __init__(self, auth_service: Optional[AuthService] = None, 
                 cache_service: Optional[CacheService] = None,
                 public_paths: Optional[list] = None):
        """
        Initialize auth middleware
        
        Args:
            auth_service: AuthService instance
            cache_service: CacheService instance (optional)
            public_paths: List of method names that skip authentication (e.g., ['login', 'generate_login_html'])
        """
        self.auth_service = auth_service
        self.cache_service = cache_service
        self.public_paths = public_paths or ['login', 'generate_login_html']
        self.current_user: Optional[dict] = None
        self.tenant_id: Optional[str] = None
    
    def set_auth_service(self, auth_service: AuthService):
        """Set the auth service."""
        self.auth_service = auth_service
    
    def set_cache_service(self, cache_service: CacheService):
        """Set the cache service."""
        self.cache_service = cache_service
    
    def set_current_user(self, user: Optional[dict]):
        """Set the current authenticated user."""
        self.current_user = user
        if user and self.cache_service:
            # Cache user info
            user_id = user.get('id') or user.get('user_email')
            if user_id:
                cache_key = f"user:{user_id}"
                try:
                    self.cache_service.set(cache_key, json.dumps(user), expire=3600)
                    logger.debug(f"User session cached: {user_id}")
                except Exception as e:
                    logger.warning(f"Failed to cache user: {e}")
    
    def get_current_user(self) -> Optional[dict]:
        """Get the current authenticated user."""
        return self.current_user
    
    def is_authenticated(self) -> bool:
        """Check if current user is authenticated."""
        return self.current_user is not None
    
    def check_auth(self, method_name: str) -> Optional[Dict]:
        """
        Check if method requires authentication and if user is authenticated.
        
        Args:
            method_name: Method name to check
            
        Returns:
            None if authentication passes, error dict if authentication fails
        """
        # Skip auth check for public paths
        if method_name in self.public_paths:
            logger.debug(f"Public path, skipping auth: {method_name}")
            return None
        
        # Check authentication for protected paths
        if not self.is_authenticated():
            logger.warning(f"Authentication required for: {method_name}")
            return {
                'success': False,
                'message': 'Authentication required',
                'code': 'AUTH_REQUIRED'
            }
        
        logger.debug(f"Authenticated request: {method_name}")
        return None
    
    def handle_exception(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with exception handling.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or error dict
        """
        try:
            result = func(*args, **kwargs)
            return result
        except ValueError as e:
            # Handle validation errors
            logger.warning(f"Validation error: {e}")
            return {
                'success': False,
                'message': str(e),
                'code': 'VALIDATION_ERROR'
            }
        except Exception as e:
            # Handle all other exceptions
            logger.error(f"Error: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'code': 'INTERNAL_ERROR'
            }
    
    def _get_cached_user(self, user_id: str) -> Optional[dict]:
        """Get user info from cache"""
        if not self.cache_service:
            return None
        
        try:
            cache_key = f"user:{user_id}"
            cached_data = self.cache_service.get(cache_key)
            if cached_data:
                # Deserialize JSON string back to dict
                return json.loads(cached_data) if isinstance(cached_data, (str, bytes)) else cached_data
            return None
        except Exception as e:
            logger.warning(f"Failed to get cached user: {e}")
            return None

