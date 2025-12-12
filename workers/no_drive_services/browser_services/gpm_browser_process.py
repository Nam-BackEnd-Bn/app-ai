"""Browser process runner for GPM service.

This module contains a class that runs in separate multiprocessing processes
to launch and manage browser instances. This class is designed to run
in isolated processes, not in the main thread or QThread.
"""

import asyncio

from loguru import logger

from src.schemas.accounts import AccountEmail
from src.schemas.manager_image_ai_item_store import ManagerImageAIItemStore
from src.schemas.task_aI_image_voice_canva_instagram import TaskAIImageVoiceCanvaInstagram
from workers.no_drive_services.browser_services.task_execute import TaskExecute


class GPMBrowserProcess:
    """
    Browser process runner for GPM service.
    
    This class handles browser launching and management in separate
    multiprocessing processes. It manages the event loop and async operations
    for browser instances.
    """

    def __init__(
            self,
            profile_name: str,
            position: int,
            tasks: list[TaskAIImageVoiceCanvaInstagram],
            account_email: AccountEmail,
            manager_image_ai_item_store: list[ManagerImageAIItemStore],
            should_stop_flag=None
    ):
        """
        Initialize the browser process runner.
        
        Args:
            profile_name: Name of the browser profile
            position: Position index
            tasks: List of tasks to launch
            account_email: Account email information for login
            manager_image_ai_item_store: List of manager image AI item store
            should_stop_flag: Shared multiprocessing flag for stopping (optional)
        """
        self.profile_name = profile_name
        self.position = position
        self.tasks = tasks
        self.account_email = account_email
        self.should_stop_flag = should_stop_flag
        self.manager_image_ai_item_store = manager_image_ai_item_store
        self.loop = None

    @staticmethod
    def run(
            profile_name: str,
            position: int,
            tasks: list[TaskAIImageVoiceCanvaInstagram],
            account_email: AccountEmail,
            manager_image_ai_item_store: list[ManagerImageAIItemStore],
            should_stop_flag=None
    ):
        """
        Run browser async code in a process (static method for multiprocessing).
        
        This static method is designed to be used as a target for
        multiprocessing.Process. It creates an instance and runs the browser.
        
        Args:
            profile_name: Name of the browser profile
            position: Position index
            tasks: List of tasks to launch
            account_email: Account email information for login
            manager_image_ai_item_store: List of manager image AI item store
            should_stop_flag: Shared multiprocessing flag for stopping (optional)
        """
        runner = GPMBrowserProcess(profile_name, position, tasks, account_email, manager_image_ai_item_store,
                                   should_stop_flag)
        runner._run()

    def _run(self):
        """
        Run the browser process with event loop management.
        
        This method creates and manages the asyncio event loop,
        runs the async browser code, and handles cleanup.
        """
        try:
            # Import here to avoid issues with multiprocessing
            from nodrive_gpm_package import GPMClient

            # Create new event loop for this process
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # Set exception handler to catch and log unhandled exceptions from background tasks
            def exception_handler(loop, context):
                """Handle exceptions from tasks that weren't properly handled."""
                exception = context.get('exception')
                if exception:
                    # Filter out expected exceptions
                    if isinstance(exception, asyncio.CancelledError):
                        return  # Ignore cancellation errors
                    elif isinstance(exception, (ConnectionRefusedError, ConnectionError, OSError)):
                        # These are common when browser is closed - log at debug level
                        logger.debug(
                            f"[{self.profile_name}] Background task connection error (browser closed): {exception}")
                    else:
                        logger.warning(f"[{self.profile_name}] Unhandled exception in background task: {exception}")
                else:
                    message = context.get('message', 'Unknown error')
                    logger.debug(f"[{self.profile_name}] Background task message: {message}")

            self.loop.set_exception_handler(exception_handler)

            # Create the main task
            main_task = self.loop.create_task(self._launch_and_use_browser())

            # Create a monitoring task that checks the stop flag and cancels main task if needed
            async def monitor_stop_flag():
                """Monitor stop flag and cancel main task when flag is set."""
                while not main_task.done():
                    if self.should_stop_flag and self.should_stop_flag.value:
                        logger.info(f"[{self.profile_name}] Stop flag detected, cancelling browser task...")
                        main_task.cancel()
                        break
                    await asyncio.sleep(0.2)  # Check every 0.2 seconds

            monitor_task = self.loop.create_task(monitor_stop_flag())

            # Run the async browser code
            try:
                # Run both tasks until main task completes
                self.loop.run_until_complete(
                    asyncio.gather(main_task, monitor_task, return_exceptions=True)
                )
            except asyncio.CancelledError:
                logger.info(f"[{self.profile_name}] Browser task was cancelled")
            except Exception as e:
                logger.error(f"Error in async browser code for {self.profile_name}: {e}")

        except Exception as e:
            logger.error(f"Error in browser process for {self.profile_name}: {e}")
        finally:
            self._cleanup_loop()

    async def _launch_and_use_browser(self):
        """
        Launch a browser and use it (async method).

        This method handles the browser launch, navigation, and lifecycle.
        """
        from nodrive_gpm_package import GPMClient

        client = GPMClient()

        logger.info(f"🚀 [{self.profile_name}] Launching at position {self.position}...")

        try:
            browser = await client.launch(
                profile_name=self.profile_name,
                position=self.position,
                # proxy_type="socks5",
                # proxy=random.choice(PROXIES),
            )

            await self._execute_tasks(browser, client)

        except Exception as e:
            logger.error(f"Error launching browser {self.profile_name}: {e}")
            return False

    async def _execute_tasks(self, browser, client):
        if not browser:
            logger.error(f"❌ [{self.profile_name}] Failed to launch")
            return False

        logger.info(f"✅ [{self.profile_name}] Browser launched successfully")

        # Check stop flag before navigating
        if self.should_stop_flag and self.should_stop_flag.value:
            logger.info(f"⏹️ [{self.profile_name}] Stop requested before navigation")
            client.close(self.profile_name)
            return False

        tab = await browser.get()
        # Import here to avoid multiprocessing import issues on Windows
        from nodrive_gpm_package.utils import UtilActions
        await UtilActions.goOnTopBrowser(tab=tab)

        # Check stop flag before executing tasks
        if self.should_stop_flag and self.should_stop_flag.value:
            logger.info(f"⏹️ [{self.profile_name}] Stop requested before task execution")
            client.close(self.profile_name)
            return False

        # Initialize TaskExecute
        task_execute = TaskExecute(tab=tab)

        # Execute each task
        for task in self.tasks:
            # Check stop flag before each task
            if self.should_stop_flag and self.should_stop_flag.value:
                logger.info(f"⏹️ [{self.profile_name}] Stop requested during task execution")
                break

            try:
                logger.info(f"[{self.profile_name}] Executing task {task.id}...")

                await task_execute.execute_work_flow(task, self.account_email, self.manager_image_ai_item_store)

                logger.info(f"[{self.profile_name}] Task {task.id} completed successfully")
            except Exception as e:
                logger.error(f"[{self.profile_name}] Error executing task {task.id}: {e}")
                # Attempt to recover from detached tab (e.g., "Not attached to an active page" / -32000)
                if "-32000" in str(e) or "Not attached to an active page" in str(e):
                    logger.info(f"[{self.profile_name}] Attempting tab refresh after detachment...")
                    new_tab = await self._refresh_tab(browser)
                    if new_tab:
                        task_execute.tab = new_tab
                        try:
                            await task_execute.execute_work_flow(task, self.account_email,
                                                                 self.manager_image_ai_item_store)
                            logger.info(f"[{self.profile_name}] Task {task.id} recovered after tab refresh")
                        except Exception as retry_err:
                            logger.error(f"[{self.profile_name}] Retry failed for task {task.id}: {retry_err}")
                # Continue with next task even if one fails

        # Keep browser open, checking stop flag periodically
        try:
            while not (self.should_stop_flag and self.should_stop_flag.value):
                # Use shorter sleep interval for more responsive shutdown
                await asyncio.sleep(0.5)  # Check every 0.5 seconds
        except asyncio.CancelledError:
            logger.info(f"[{self.profile_name}] Browser loop was cancelled")
            raise
        finally:
            logger.info(f"🔒 [{self.profile_name}] Closing browser...")
            try:
                client.close(self.profile_name)
            except Exception as e:
                logger.warning(f"[{self.profile_name}] Error closing browser: {e}")

    async def _refresh_tab(self, browser):
        """
        Reacquire a fresh tab when the current one becomes detached.
        """
        try:
            new_tab = await browser.get()
            from nodrive_gpm_package.utils import UtilActions
            await UtilActions.goOnTopBrowser(tab=new_tab)
            logger.info(f"[{self.profile_name}] Tab refreshed successfully")
            return new_tab
        except Exception as e:
            logger.error(f"[{self.profile_name}] Unable to refresh tab: {e}")
            return None

    def _cleanup_loop(self):
        """Clean up the event loop and cancel pending tasks."""
        if self.loop:
            try:
                # Cancel all pending tasks
                try:
                    pending_tasks = [task for task in asyncio.all_tasks(self.loop) if not task.done()]
                    if pending_tasks:
                        logger.info(f"[{self.profile_name}] Cancelling {len(pending_tasks)} pending tasks")
                        for task in pending_tasks:
                            task.cancel()

                        # Wait for tasks to be cancelled (with shorter timeout for faster shutdown)
                        if pending_tasks:
                            try:
                                results = self.loop.run_until_complete(
                                    asyncio.wait_for(
                                        asyncio.gather(*pending_tasks, return_exceptions=True),
                                        timeout=1.0
                                    )
                                )
                                # Log any exceptions from cancelled tasks to prevent "Task exception was never retrieved" warnings
                                for i, result in enumerate(results):
                                    if isinstance(result, Exception):
                                        # Filter out expected exceptions (CancelledError, ConnectionRefusedError from closed browsers)
                                        if isinstance(result, asyncio.CancelledError):
                                            logger.debug(f"[{self.profile_name}] Task {i} was cancelled (expected)")
                                        elif isinstance(result, ConnectionRefusedError):
                                            logger.debug(
                                                f"[{self.profile_name}] Task {i} connection refused (browser likely closed): {result}")
                                        elif isinstance(result, (ConnectionError, OSError)):
                                            logger.debug(
                                                f"[{self.profile_name}] Task {i} connection error (browser likely closed): {result}")
                                        else:
                                            logger.warning(
                                                f"[{self.profile_name}] Task {i} raised exception during cleanup: {result}")
                            except asyncio.TimeoutError:
                                logger.warning(f"[{self.profile_name}] Timeout waiting for tasks to cancel")
                                # Set exception handlers for remaining tasks to prevent unretrieved exceptions
                                for task in pending_tasks:
                                    if not task.done():
                                        task.add_done_callback(self._log_task_exception)
                            except Exception as e:
                                logger.warning(f"[{self.profile_name}] Error waiting for task cancellation: {e}")
                except Exception as e:
                    logger.warning(f"[{self.profile_name}] Error getting pending tasks: {e}")

                # Exception handler is already set when loop was created, but ensure it's still active

                # Stop the loop gracefully
                try:
                    # Stop any remaining callbacks
                    self.loop.stop()
                except Exception as e:
                    logger.debug(f"[{self.profile_name}] Error stopping loop: {e}")

                # Close the loop
                self.loop.close()
            except Exception as e:
                logger.error(f"Error closing event loop for {self.profile_name}: {e}")

    def _log_task_exception(self, task):
        """Callback to log exceptions from tasks that complete after cancellation."""
        try:
            if task.done() and not task.cancelled():
                exception = task.exception()
                if exception:
                    # Filter out expected exceptions
                    if isinstance(exception, (ConnectionRefusedError, ConnectionError, OSError)):
                        logger.debug(f"[{self.profile_name}] Task connection error (browser closed): {exception}")
                    else:
                        logger.warning(f"[{self.profile_name}] Task exception: {exception}")
        except Exception as e:
            logger.debug(f"[{self.profile_name}] Error checking task exception: {e}")


# Backward compatibility: provide a function wrapper for the static method
def _run_browser_async(
        profile_name: str,
        position: int,
        tasks: list[TaskAIImageVoiceCanvaInstagram],
        account_email: AccountEmail,
        manager_image_ai_item_store: list[ManagerImageAIItemStore],
        should_stop_flag=None,
        log_queue=None,
):
    """
    Run browser async code in a process (function wrapper for backward compatibility).
    
    This function is a wrapper around GPMBrowserProcess.run() to maintain
    backward compatibility with existing code.
    
    Args:
        profile_name: Name of the browser profile
        position: Position index
        tasks: List of tasks to launch
        account_email: Account email information for login
        manager_image_ai_item_store: List of manager image AI item store
        should_stop_flag: Shared multiprocessing flag for stopping (optional)
    """
    if log_queue is not None:
        try:
            # Forward loguru logs to parent process through the queue
            def _queue_sink(message):
                try:
                    record = message.record
                    log_queue.put({
                        "message": record["message"],
                        "level": record["level"].name.lower(),
                    })
                except Exception:
                    pass

            logger.add(
                _queue_sink,
                format="{message}",
                level="DEBUG",
                colorize=False,
                enqueue=False,  # Queue is handled manually
            )
        except Exception:
            # If queue setup fails, continue without crashing the browser process
            logger.warning("Failed to attach log queue; continuing without cross-process logs")

    GPMBrowserProcess.run(
        profile_name,
        position,
        tasks,
        account_email,
        manager_image_ai_item_store,
        should_stop_flag,
    )
