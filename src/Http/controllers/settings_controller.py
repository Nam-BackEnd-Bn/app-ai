"""Settings controller."""

import json
from typing import Optional, Dict, Any
from src.services.settings_service import SettingsService


class SettingsController:
    """Controller for handling settings-related requests."""
    
    def __init__(self, settings_service: SettingsService):
        """
        Initialize controller with settings service.
        
        Args:
            settings_service: SettingsService instance
        """
        self.settings_service = settings_service
    
    def get_settings(self, user_id: str) -> dict:
        """
        Get user settings.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with settings data
        """
        try:
            settings = self.settings_service.get_settings(user_id)
            return {
                'success': True,
                'data': settings
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching settings: {str(e)}',
                'data': None
            }
    
    def save_settings(self, user_id: str, settings_json: str) -> dict:
        """
        Save user settings.
        
        Args:
            user_id: User ID
            settings_json: JSON string of settings
            
        Returns:
            Dictionary with save result
        """
        try:
            settings = json.loads(settings_json)
            success = self.settings_service.save_settings(user_id, settings)
            
            if not success:
                raise Exception('Failed to save settings')
            return {
                'success': True,
                'message': 'Settings saved successfully'
            }
        except Exception as e:
            raise e
    
    def delete_settings(self, user_id: str) -> dict:
        """
        Delete user settings.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with delete result
        """
        try:
            deleted = self.settings_service.delete_settings(user_id)
            if deleted:
                return {
                    'success': True,
                    'message': 'Settings deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Settings not found'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting settings: {str(e)}'
            }
    
    def get_settings_json(self, user_id: str) -> str:
        """
        Get user settings as JSON string.
        
        Args:
            user_id: User ID
            
        Returns:
            JSON string of settings
        """
        try:
            settings = self.settings_service.get_settings(user_id)
            return json.dumps(settings)
        except Exception as e:
            return json.dumps({'error': str(e)})

