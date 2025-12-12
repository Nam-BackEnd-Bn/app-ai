"""Authentication controller."""

import json
from pathlib import Path
from typing import Optional, Dict
from loguru import logger
from src.services.auth_service import AuthService
from src.services.cache_service import CacheService


class AuthController:
    """Controller for handling authentication requests."""
    
    def __init__(self, auth_service: AuthService, html_dir: Path, cache_service: Optional[CacheService] = None):
        """
        Initialize controller with auth service.
        
        Args:
            auth_service: AuthService instance
            html_dir: Path to HTML templates directory
            cache_service: CacheService instance (optional)
        """
        self.auth_service = auth_service
        self.html_dir = html_dir
        self.cache_service = cache_service
    
    def login(self, username: str, password: str) -> dict:
        """
        Handle login request.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Dictionary with success status and message
        """
        try:
            is_authenticated = self.auth_service.authenticate(username, password)
            
            if is_authenticated:
                user = self.auth_service.get_user_by_username(username)
          
                return {
                    'success': True,
                    'message': 'Login successful',
                    'user': user
                }
            else:
                return {
                    'success': False,
                    'message': 'Invalid credentials'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Login error: {str(e)}'
            }
    
    def logout(self, current_user: Optional[Dict] = None) -> dict:
        """
        Handle logout request.
        Clears current user cache and session data.
        
        Args:
            current_user: Current user dictionary (optional)
        
        Returns:
            Dictionary with success status and message
        """
        try:
            if current_user:
                # Clear user cache
                user_id = current_user.get('id') or current_user.get('user_email')
                if user_id:
                    cache_key = f"user:{user_id}"
                    try:
                        self.cache_service.delete(cache_key)
                        logger.debug(f"User session cache cleared: {user_id}")
                    except Exception as e:
                        logger.warning(f"Failed to clear user cache: {e}")
            
            logger.info("User logged out successfully")
            return {
                'success': True,
                'message': 'Logout successful'
            }
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return {
                'success': False,
                'message': f'Logout error: {str(e)}'
            }
    
    def generate_login_html(self) -> str:
        """
        Generate login page HTML.
        
        Returns:
            HTML string for the login page
        """
        html_file = self.html_dir / "login.html"
        with open(html_file, 'r', encoding='utf-8') as f:
            html = f.read()
        return html

