"""Module for initializing repositories, services, and controllers."""

from pathlib import Path
from sqlalchemy.orm import Session

from src.Http.controllers import AuthController
from src.Http.controllers.action_controller import ActionController
from src.Http.controllers.settings_controller import SettingsController
from src.Http.controllers.task_ai_image_voice_canva_instagram_controller import TaskAIImageVoiceCanvaInstagramController
from src.Http.middleware.auth_middleware import AuthMiddleware
from src.repositories.manager_image_ai_item_store_repository import ManagerImageAIItemStoreRepository
from src.repositories.manager_image_ai_user_attached_repository import ManagerImageAIUserAttachedRepository
from src.repositories.task_ai_image_voice_canva_instagram_repository import TaskAIImageVoiceCanvaInstagramRepository
from src.repositories.user_repository import UserRepository
from src.services.account_content_info_service import AccountContentInfoService
from src.services.auth_service import AuthService
from src.services.cache_service import CacheService
from src.services.manager_image_ai_item_store_service import ManagerImageAIItemStoreService
from src.services.manager_image_ai_user_attached_service import ManagerImageAIUserAttachedService
from src.services.settings_service import SettingsService
from src.services.task_ai_image_voice_canva_instagram_service import TaskAIImageVoiceCanvaInstagramService
from src.services.user_service import UserService


def initialize_modules(
        session: Session
) -> tuple[
    AuthController,
    TaskAIImageVoiceCanvaInstagramController,
    SettingsController,
    ActionController,
    AuthMiddleware
]:
    """
    Initialize repositories, services, and controllers.
    
    Args:
        session: Database session
        
    Returns:
        Tuple of (AuthController, TaskAIImageVoiceCanvaInstagramController, SettingsController, AuthMiddleware)
    """
    # Get HTML directory path if not provided
    html_dir = Path(__file__).parent / "views" / "html"

    # Initialize repositories
    user_repository = UserRepository(session)
    task_repository = TaskAIImageVoiceCanvaInstagramRepository(session)
    manager_image_ai_user_attached_repository = ManagerImageAIUserAttachedRepository(session)
    manager_image_ai_item_store_repository = ManagerImageAIItemStoreRepository(session)
    # Initialize services
    task_ai_image_voice_canva_instagram_service = TaskAIImageVoiceCanvaInstagramService(task_repository)
    user_service = UserService(user_repository)
    manager_image_ai_user_attached_service = ManagerImageAIUserAttachedService(
        manager_image_ai_user_attached_repository
    )
    manager_image_ai_item_store_service = ManagerImageAIItemStoreService(manager_image_ai_item_store_repository)
    auth_service = AuthService(user_repository)
    account_content_info_service = AccountContentInfoService()

    # Initialize cache service with default TTL of 1 hour and cleanup every 5 minutes
    cache_service = CacheService(default_ttl=3600, cleanup_interval=300)
    settings_service = SettingsService(cache_service)

    # Initialize controllers
    auth_controller = AuthController(auth_service, html_dir=html_dir, cache_service=cache_service)
    task_ai_image_voice_canva_instagram_controller = TaskAIImageVoiceCanvaInstagramController(
        task_ai_image_voice_canva_instagram_service, html_dir=html_dir)
    settings_controller = SettingsController(settings_service)
    action_controller = ActionController(
        account_content_info_service,
        task_ai_image_voice_canva_instagram_service,
        manager_image_ai_item_store_service
    )

    # Initialize middleware
    public_paths = ['login', 'generate_login_html']
    auth_middleware = AuthMiddleware(
        auth_service=auth_service,
        cache_service=cache_service,
        public_paths=public_paths
    )

    return auth_controller, task_ai_image_voice_canva_instagram_controller, settings_controller, action_controller, auth_middleware
