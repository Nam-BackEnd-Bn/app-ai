"""Action controller with QThread and Worker support."""

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from loguru import logger

from src.services.account_content_info_service import AccountContentInfoService
from src.services.task_ai_image_voice_canva_instagram_service import TaskAIImageVoiceCanvaInstagramService
from src.services.manager_image_ai_item_store_service import ManagerImageAIItemStoreService
# Import GPMWorker class (safe - only imports class definition, not COM-related code)
# Workers are only instantiated and run in QThread, never in main thread
from workers.gpm_worker import GPMWorker


class ActionController(QObject):
    """
    Controller for managing action operations with background threading.

    This controller manages QThread and Worker instances for running
    actions in the background without blocking the UI.

    IMPORTANT: Workers only run in QThread/multiprocessing, never in the main thread.
    QApplication must be created before any workers are started.
    """

    # Signals for communicating with the view layer
    action_result = pyqtSignal(dict)  # Emitted when action completes (result dict)
    action_error = pyqtSignal(str)  # Emitted when action fails (error message)
    action_status = pyqtSignal(str)  # Emitted for status updates
    action_progress = pyqtSignal(int)  # Emitted for progress updates (0-100)
    action_started = pyqtSignal()  # Emitted when action thread starts
    action_stopped = pyqtSignal()  # Emitted when action thread stops

    def __init__(
            self,
            account_content_info_service: AccountContentInfoService,
            task_ai_image_voice_canva_instagram_service: TaskAIImageVoiceCanvaInstagramService,
            manager_image_ai_item_store_service: ManagerImageAIItemStoreService,
    ):
        """Initialize the action controller."""
        super().__init__()
        self.action_thread = None
        self.action_worker = None
        self.account_content_info_service = account_content_info_service
        self.task_ai_image_voice_canva_instagram_service = task_ai_image_voice_canva_instagram_service
        self.manager_image_ai_item_store_service = manager_image_ai_item_store_service
        
    def start_action_async(self):
        """
        Start action asynchronously in a background thread.

        This method creates a QThread and Worker, connects signals,
        and starts the background task. Results are communicated
        via the controller's signals.

        IMPORTANT: Worker runs in QThread, not in main thread.
        QApplication must be created before calling this method.
        """
        try:
            # Stop any existing action thread
            self._check_action_is_running()

            # Create new thread and worker
            self.action_thread = QThread()
            accounts = self.account_content_info_service.find_account_content_info()
            tasks = self.task_ai_image_voice_canva_instagram_service.get_task_by_account_social()
            accounts = self.account_content_info_service.mapp_account_with_manager_image_ai_item_store(
                accounts,
                self.manager_image_ai_item_store_service
            )
            self.action_worker = GPMWorker(
                accounts,
                tasks,
            )

            # Move worker to thread
            self.action_worker.moveToThread(self.action_thread)

            # Connect worker signals to controller signals
            self._connect_worker_signals()

            # Connect thread lifecycle signals
            self._connect_thread_lifecycle_signals()

            # Start thread
            self.action_thread.start()

            logger.info("Action thread started")

        except Exception as e:
            logger.error(f"Error in start_action_async: {e}")
            self.action_error.emit(str(e))

    def stop_action_async(self):
        """
        Stop the currently running action thread.

        This method stops any running action thread gracefully.
        """
        try:
            # Stop existing action thread if running
            if self.action_thread is not None:
                try:
                    if self.action_thread.isRunning():
                        logger.info("Stopping action thread")
                        self._stop_action_thread()

                        # Emit result to indicate stop was successful
                        self.action_result.emit({
                            "success": True,
                            "message": "Action stopped successfully",
                            "action_type": "stop"
                        })
                    else:
                        logger.warning("No action thread running to stop")
                        self.action_result.emit({
                            "success": False,
                            "message": "No action running to stop",
                            "action_type": "stop"
                        })
                except RuntimeError:
                    # Thread has been deleted
                    logger.debug("Thread already deleted")
                    self.action_thread = None
                    self.action_result.emit({
                        "success": False,
                        "message": "No action running to stop",
                        "action_type": "stop"
                    })
            else:
                logger.warning("No action thread running to stop")
                self.action_result.emit({
                    "success": False,
                    "message": "No action running to stop",
                    "action_type": "stop"
                })

        except Exception as e:
            logger.error(f"Error in stop_action_async: {e}")
            self.action_error.emit(str(e))

    def cleanup(self):
        """Clean up threads and workers."""
        try:
            # Check if thread exists and is still valid before accessing it
            if self.action_thread is not None:
                try:
                    # Try to access the thread - if it's been deleted, this will raise RuntimeError
                    is_running = self.action_thread.isRunning()
                    if is_running:
                        self._stop_action_thread()
                except RuntimeError:
                    # Thread has been deleted, just clear the reference
                    logger.debug("Thread already deleted during cleanup")
                    self.action_thread = None
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            # Clear references to allow garbage collection
            self.action_thread = None
            self.action_worker = None

    def _check_action_is_running(self):
        if self.action_thread is not None:
            try:
                if self.action_thread.isRunning():
                    logger.warning("Stopping existing action thread before starting new one")
                    self._stop_action_thread()
            except RuntimeError:
                # Thread has been deleted, just clear the reference
                logger.debug("Previous thread already deleted")
                self.action_thread = None

    def _connect_worker_signals(self):
        self.action_thread.started.connect(self.action_worker.run)
        self.action_worker.finished.connect(self.action_thread.quit)
        self.action_worker.finished.connect(self.action_worker.deleteLater)
        self.action_thread.finished.connect(self.action_thread.deleteLater)
        self.action_worker.result.connect(self.action_result.emit)
        self.action_worker.error.connect(self.action_error.emit)
        self.action_worker.status.connect(self.action_status.emit)
        self.action_worker.progress.connect(self.action_progress.emit)

    def _connect_thread_lifecycle_signals(self):
        self.action_thread.started.connect(self.action_started.emit)
        self.action_thread.finished.connect(self.action_stopped.emit)

    def _stop_action_thread(self):
        """Stop the action thread gracefully."""
        try:
            if self.action_worker:
                # Set the stop flag directly (boolean assignment is atomic in Python)
                # This is faster than going through the event loop
                self.action_worker._should_stop = True

                # Also call stop() via event loop for any cleanup it might do
                from PyQt6.QtCore import QMetaObject, Qt
                QMetaObject.invokeMethod(
                    self.action_worker,
                    "stop",
                    Qt.ConnectionType.QueuedConnection
                )
        except RuntimeError:
            # Worker may have been deleted
            logger.debug("Worker already deleted")

        try:
            if self.action_thread:
                # Check if thread still exists and is running
                if self.action_thread.isRunning():
                    # Wait for the thread to finish (worker should exit when should_stop is True)
                    # The worker checks the flag every 0.1 seconds, so it should stop quickly
                    self.action_thread.quit()
                    if not self.action_thread.wait(3000):  # Wait up to 3 seconds
                        logger.warning("Thread did not stop gracefully, terminating")
                        self.action_thread.terminate()
                        self.action_thread.wait()
                    else:
                        logger.info("Thread stopped gracefully")
        except RuntimeError:
            # Thread may have been deleted
            logger.debug("Thread already deleted")
