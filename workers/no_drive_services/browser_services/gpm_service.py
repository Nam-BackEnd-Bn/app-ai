"""GPM (Google Profile Manager) service for managing multiple browsers using multiprocessing."""

import multiprocessing
import sys
from loguru import logger
from typing import List, Dict, Optional, Callable

from src.schemas.accounts import AccountSocial, AccountEmail
from src.schemas.manager_image_ai_item_store import ManagerImageAIItemStore
from src.schemas.task_aI_image_voice_canva_instagram import TaskAIImageVoiceCanvaInstagram
# Import browser process runner (backward compatible function)
from workers.no_drive_services.browser_services.gpm_browser_process import _run_browser_async

# Set multiprocessing start method for Windows compatibility
# This must be done before creating any Process objects
if sys.platform == 'win32':
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        # Start method already set, which is fine
        pass


class GPMService:
    """
    Service for managing multiple browser instances using multiprocessing.
    
    This service launches multiple browsers in parallel processes,
    each running in its own process for better isolation and performance.
    """

    def __init__(self):
        """Initialize the GPM service."""
        self.processes: List[multiprocessing.Process] = []
        self.profile_names: List[str] = []  # Track profile names for closing browsers
        self._should_stop = multiprocessing.Value('b', False)  # Shared flag for stopping

    def launch_multiple_browsers(
            self,
            accounts: list[AccountSocial],
            tasks: list[TaskAIImageVoiceCanvaInstagram],
            log_queue: Optional[object] = None,
    ) -> List[multiprocessing.Process]:
        logger.info(f"🚀 Launching {len(accounts)} browsers in parallel processes...")

        processes = []
        for i, account in enumerate(accounts):
            profile_name = account.accountAI
            tasks = list(filter(lambda task: task.accountSocial == account.id, tasks))
            # Create AccountEmail from AccountSocial
            account_email = AccountEmail(
                email=account.accountAI,
                password=account.password,
                code2FA=account.code2FA
            )
            manager_image_ai_item_store = account.manager_image_ai_item_store
            logger.info(f'Total tasks of {account_email.email}: {len(tasks)}')
            process = self.launch_browser_process(
                profile_name,
                i,
                tasks,
                account_email,
                manager_image_ai_item_store,
                log_queue=log_queue,
            )
            processes.append(process)

        logger.info(f"✅ Started {len(processes)} browser processes")
        return processes

    def launch_browser_process(
            self,
            profile_name: str,
            position: int,
            tasks: list[TaskAIImageVoiceCanvaInstagram],
            account_email: AccountEmail,
            manager_image_ai_item_store: list[ManagerImageAIItemStore],
            should_stop_flag=None,
            log_queue: Optional[object] = None,
    ) -> multiprocessing.Process:
        if should_stop_flag is None:
            should_stop_flag = self._should_stop

        process = multiprocessing.Process(
            target=_run_browser_async,
            args=(
                profile_name,
                position,
                tasks,
                account_email,
                manager_image_ai_item_store,
                should_stop_flag,
                log_queue,
            ),
            daemon=True
        )
        process.start()
        self.processes.append(process)
        self.profile_names.append(profile_name)  # Track profile name
        return process

    def stop_all_browsers(self):
        """
        Stop all running browser processes.
        
        This method can be called from main thread or worker thread.
        GPMClient import is lazy to avoid COM initialization issues.
        """
        logger.info("🔒 Stopping all browser processes...")

        # First, close all browsers explicitly
        # Lazy import GPMClient here to avoid COM initialization before Qt
        try:
            from nodrive_gpm_package import GPMClient
            client = GPMClient()

            logger.info(f"Closing {len(self.profile_names)} browsers...")
            for profile_name in self.profile_names:
                try:
                    client.close(profile_name)
                    logger.info(f"✅ Closed browser: {profile_name}")
                except Exception as e:
                    logger.warning(f"Error closing browser {profile_name}: {e}")
        except ImportError:
            logger.warning("GPMClient not available, skipping explicit browser close")
        except Exception as e:
            logger.error(f"Error closing browsers: {e}")

        # Set stop flag to signal processes to stop
        self._should_stop.value = True

        # Wait for all processes to finish
        for process in self.processes:
            if process.is_alive():
                logger.debug(f"Waiting for process {process.pid} to stop gracefully...")
                process.join(timeout=5.0)  # Wait up to 5 seconds
                if process.is_alive():
                    logger.warning(f"Process {process.pid} did not stop gracefully, terminating")
                    try:
                        process.terminate()
                        process.join(timeout=2.0)
                        if process.is_alive():
                            logger.warning(f"Process {process.pid} did not respond to terminate, killing")
                            process.kill()
                            process.join(timeout=1.0)
                    except Exception as e:
                        logger.error(f"Error terminating process {process.pid}: {e}")
                        try:
                            process.kill()
                        except Exception as e2:
                            logger.error(f"Error killing process {process.pid}: {e2}")
                else:
                    logger.debug(f"Process {process.pid} stopped gracefully")

        self.processes.clear()
        self.profile_names.clear()
        self._should_stop.value = False
        logger.info("✅ All browser processes stopped")


