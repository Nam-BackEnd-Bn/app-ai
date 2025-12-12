"""Example Worker that uses GPM service with multiprocessing."""

import multiprocessing
import queue
import threading
from typing import Optional
from loguru import logger

from src.schemas.accounts import AccountSocial
from src.schemas.manager_image_ai_item_store import ManagerImageAIItemStore
from src.schemas.task_aI_image_voice_canva_instagram import TaskAIImageVoiceCanvaInstagram
from workers.worker import Worker


class GPMWorker(Worker):
    """
    Worker that launches multiple browsers using GPM service with multiprocessing.
    
    This worker demonstrates how to use the GPM service within a QThread worker.
    Workers only run in QThread/multiprocessing, never in the main thread.
    """

    def __init__(
            self,
            accounts: list[AccountSocial],
            tasks: list[TaskAIImageVoiceCanvaInstagram],
    ):
        """
        Initialize the GPM worker.
        
        Args:
            accounts: List of accounts to launch
            tasks: Optional list of tasks to launch
        """
        super().__init__()
        self.accounts = accounts
        # DO NOT create GPMService here - create it in do_work() which runs in QThread
        self.gpm_service = None
        self.tasks = tasks
        self.log_queue: Optional[object] = None
        self._log_listener_stop = threading.Event()
        self._log_listener_thread: threading.Thread | None = None

    def do_work(self):
        """
        Launch multiple browsers using GPM service with multiprocessing.
        
        This method runs in a QThread, so it's safe to import COM-related modules here.
        """
        try:
            # Lazy import GPMService here (runs in QThread, after QApplication is created)
            from workers.no_drive_services.browser_services.gpm_service import GPMService

            self.status.emit("Initializing GPM service...")
            self.progress.emit(10)

            if self.should_stop():
                return

            # Create GPMService here (in QThread context)
            self.gpm_service = GPMService()

            # Set up cross-process log forwarding
            self.log_queue = multiprocessing.Queue()
            self._start_log_listener()

            self.status.emit(f"Launching {len(self.accounts)} browsers...")
            self.progress.emit(20)

            # Launch multiple browsers in parallel processes
            processes = self.gpm_service.launch_multiple_browsers(
                accounts=self.accounts,
                tasks=self.tasks,
                log_queue=self.log_queue,
            )

            # Hide overlay when browsers are launched (launch_multiple_browsers returns)
            # Emit 100% progress to trigger hideLoading in the UI
            self.progress.emit(100)
            self.status.emit(f"✅ {len(processes)} browsers launched successfully")

            # Wait for browsers to actually start and become alive
            # Check periodically until at least one browser is alive, or timeout after 10 seconds
            from time import sleep
            browsers_opened_emitted = False  # Track if we've already emitted BROWSERS_OPENED
            max_wait_time = 10  # Maximum time to wait for browsers to become alive (seconds)
            check_interval = 0.5  # Check every 0.5 seconds
            waited_time = 0

            while waited_time < max_wait_time and not browsers_opened_emitted:
                if self.should_stop():
                    self.gpm_service.stop_all_browsers()
                    return

                # Check if any processes are alive
                alive_processes = [p for p in processes if p.is_alive()]
                if len(alive_processes) > 0:
                    # Browsers are opening, emit status to show Stop button
                    self.status.emit("BROWSERS_OPENED")  # Special status to indicate browsers are opened
                    browsers_opened_emitted = True
                    logger.debug(
                        f"Browsers detected as alive - Stop button should be visible now ({len(alive_processes)} processes)")
                    break

                sleep(check_interval)
                waited_time += check_interval

            if self.should_stop():
                self.gpm_service.stop_all_browsers()
                return

            # Monitor processes and check for stop signal
            running = len([p for p in processes if p.is_alive()])  # Initialize running count
            while processes and not self.should_stop():
                # Remove finished processes
                processes = [p for p in processes if p.is_alive()]

                # Update status
                running = len(processes)
                if running > 0:
                    # Emit BROWSERS_OPENED if we haven't already and browsers are running
                    if not browsers_opened_emitted:
                        self.status.emit("BROWSERS_OPENED")
                        browsers_opened_emitted = True
                        logger.debug("Browsers are running - Stop button should be visible now")
                    # self.status.emit(f"Running: {running} browsers active")

                # Check stop flag every 0.1 seconds
                for _ in range(10):  # 1 second total
                    if self.should_stop():
                        break
                    from time import sleep
                    sleep(0.1)

            # Get final running count
            running = len([p for p in processes if p.is_alive()]) if processes else 0

            # Stop all browsers when stop is requested
            if self.should_stop():
                self.status.emit("Stopping all browsers...")
                self.gpm_service.stop_all_browsers()
                self.progress.emit(100)
                self.result.emit({
                    "success": True,
                    "message": f"Stopped {running} browsers",
                    "browsers_launched": running
                })
            else:
                # All processes finished naturally
                self.progress.emit(100)
                self.status.emit("All browsers finished")
                self.result.emit({
                    "success": True,
                    "message": f"All {running} browsers finished",
                    "browsers_launched": running
                })

        except Exception as e:
            logger.error(f"Error in GPMWorker.do_work: {e}")
            self.error.emit(str(e))
            self.result.emit({
                "success": False,
                "message": f"Error: {str(e)}"
            })
            # Make sure to stop browsers on error
            if self.gpm_service:
                try:
                    self.gpm_service.stop_all_browsers()
                except:
                    pass
        finally:
            self._stop_log_listener()
            self.gpm_service = None
            self.status.emit("GPM worker finished")

    def stop(self):
        """Override stop to also stop GPM service."""
        super().stop()
        if self.gpm_service:
            try:
                self.gpm_service.stop_all_browsers()
            except Exception as e:
                logger.error(f"Error stopping GPM service: {e}")
        self._stop_log_listener()

    def _start_log_listener(self):
        """Start a background thread to forward child-process logs to main logger."""
        if self.log_queue is None or self._log_listener_thread:
            return

        def _listen():
            while not self._log_listener_stop.is_set():
                try:
                    record = self.log_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                if record is None:
                    break
                try:
                    level = record.get("level", "info").upper()
                    message = record.get("message", "")
                    logger.log(level, message)
                except Exception as e:
                    logger.debug(f"Log listener error: {e}")

        self._log_listener_stop.clear()
        self._log_listener_thread = threading.Thread(target=_listen, daemon=True)
        self._log_listener_thread.start()

    def _stop_log_listener(self):
        """Stop the log forwarding thread and clean up the queue."""
        self._log_listener_stop.set()
        if self.log_queue:
            try:
                self.log_queue.put_nowait(None)
            except Exception:
                pass
        if self._log_listener_thread:
            self._log_listener_thread.join(timeout=1.0)
        self._log_listener_thread = None
        if self.log_queue:
            try:
                self.log_queue.close()
            except Exception:
                pass
        self.log_queue = None
