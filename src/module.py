"""Module for initializing repositories, services, and controllers."""

from pathlib import Path
from sqlalchemy.orm import Session
from src.repositories.user_repository import UserRepository
from src.repositories.task_repository import TaskRepository
from src.services.task_service import TaskService
from src.services.auth_service import AuthService
from src.services.cache_service import CacheService
from src.services.settings_service import SettingsService
from src.controllers.auth_controller import AuthController
from src.controllers.task_controller import TaskController
from src.controllers.settings_controller import SettingsController
from src.controllers.action_controller import ActionController
from src.middleware.auth_middleware import AuthMiddleware


def initialize_modules(session: Session) -> tuple[AuthController, TaskController, SettingsController, ActionController, AuthMiddleware]:
    """
    Initialize repositories, services, and controllers.
    
    Args:
        session: Database session
        
    Returns:
        Tuple of (AuthController, TaskController, SettingsController, AuthMiddleware)
    """
    # Get HTML directory path if not provided
    html_dir = Path(__file__).parent / "views" / "html"
    
    # Initialize repositories
    user_repository = UserRepository(session)
    task_repository = TaskRepository(session)
    
    # Initialize services
    task_service = TaskService(task_repository)
    auth_service = AuthService(user_repository)
    # Initialize cache service with default TTL of 1 hour and cleanup every 5 minutes
    cache_service = CacheService(default_ttl=3600, cleanup_interval=300)
    settings_service = SettingsService(cache_service)
    
    # Initialize controllers
    auth_controller = AuthController(auth_service, html_dir=html_dir, cache_service=cache_service)
    task_controller = TaskController(task_service, html_dir=html_dir)
    settings_controller = SettingsController(settings_service)
    action_controller = ActionController()
    
    # Initialize middleware
    public_paths = ['login', 'generate_login_html']
    auth_middleware = AuthMiddleware(
        auth_service=auth_service,
        cache_service=cache_service,
        public_paths=public_paths
    )
    
    return auth_controller, task_controller, settings_controller, action_controller, auth_middleware

