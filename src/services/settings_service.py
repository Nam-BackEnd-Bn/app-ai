"""Settings service for managing user settings."""

import json
from typing import Optional, Dict, Any
from src.services.cache_service import CacheService


class SettingsService:
    """Service for managing user settings."""
    
    def __init__(self, cache_service: CacheService):
        """
        Initialize settings service.
        
        Args:
            cache_service: CacheService instance
        """
        self.cache_service = cache_service
        self.default_ttl = 86400 * 30  # 30 days
    
    def get_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Get user settings from cache.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user settings or empty dict if not found
        """
        cache_key = f"task_table_settings_{user_id}"
        settings = self.cache_service.get(cache_key)
        
        if settings is None:
            return self.get_default_settings()
        
        # Merge with defaults to ensure all keys exist
        defaults = self.get_default_settings()
        defaults.update(settings)
        return defaults
    
    def save_settings(self, user_id: str, settings: Dict[str, Any]) -> bool:
        """
        Save user settings to cache.
        
        Args:
            user_id: User ID
            settings: Settings dictionary to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            cache_key = f"task_table_settings_{user_id}"
            # Validate and merge with defaults
            validated_settings = self.validate_settings(settings)
            self.cache_service.set(cache_key, validated_settings, expire=self.default_ttl)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def delete_settings(self, user_id: str) -> bool:
        """
        Delete user settings from cache.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        cache_key = f"task_table_settings_{user_id}"
        return self.cache_service.delete(cache_key)
    
    def get_default_settings(self) -> Dict[str, Any]:
        """
        Get default settings.
        
        Returns:
            Dictionary with default settings
        """
        return {
            'itemsPerPage': '10',
            'autoRefresh': '0',
            'defaultStatusFilter': 'all',
            'tableTheme': 'default',
            'showColumns': ''
        }
    
    def validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize settings.
        
        Args:
            settings: Settings dictionary to validate
            
        Returns:
            Validated settings dictionary
        """
        defaults = self.get_default_settings()
        validated = {}
        
        # Validate itemsPerPage
        if 'itemsPerPage' in settings:
            items = str(settings['itemsPerPage'])
            if items in ['10', '25', '50', '100']:
                validated['itemsPerPage'] = items
            else:
                validated['itemsPerPage'] = defaults['itemsPerPage']
        else:
            validated['itemsPerPage'] = defaults['itemsPerPage']
        
        # Validate autoRefresh
        if 'autoRefresh' in settings:
            try:
                refresh = int(settings['autoRefresh'])
                validated['autoRefresh'] = str(max(0, refresh))  # Ensure non-negative
            except (ValueError, TypeError):
                validated['autoRefresh'] = defaults['autoRefresh']
        else:
            validated['autoRefresh'] = defaults['autoRefresh']
        
        # Validate defaultStatusFilter
        if 'defaultStatusFilter' in settings:
            status = str(settings['defaultStatusFilter'])
            if status in ['all', 'Pending', 'In Progress', 'Completed', 'Failed']:
                validated['defaultStatusFilter'] = status
            else:
                validated['defaultStatusFilter'] = defaults['defaultStatusFilter']
        else:
            validated['defaultStatusFilter'] = defaults['defaultStatusFilter']
        
        # Validate tableTheme
        if 'tableTheme' in settings:
            theme = str(settings['tableTheme'])
            if theme in ['default', 'dark', 'light']:
                validated['tableTheme'] = theme
            else:
                validated['tableTheme'] = defaults['tableTheme']
        else:
            validated['tableTheme'] = defaults['tableTheme']
        
        # Validate showColumns (just ensure it's a string)
        if 'showColumns' in settings:
            validated['showColumns'] = str(settings['showColumns'])[:500]  # Limit length
        else:
            validated['showColumns'] = defaults['showColumns']
        
        return validated

