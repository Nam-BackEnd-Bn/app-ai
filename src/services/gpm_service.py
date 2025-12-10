"""GPM (Google Profile Manager) service for managing multiple browsers using multiprocessing."""

import multiprocessing
import asyncio
import sys
from typing import List, Dict, Optional, Callable
from loguru import logger

# Set multiprocessing start method for Windows compatibility
if sys.platform == 'win32':
    multiprocessing.set_start_method('spawn', force=True)


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
    
    def launch_browser_process(self, profile_name: str, position: int, 
                               urls: Optional[List[str]] = None,
                               should_stop_flag=None) -> multiprocessing.Process:
        """
        Launch a browser in a separate process.
        
        Args:
            profile_name: Name of the browser profile
            position: Position index for the browser
            urls: Optional list of URLs to navigate to
            should_stop_flag: Optional shared multiprocessing flag for stopping
            
        Returns:
            The created process
        """
        if urls is None:
            urls = [
                "https://www.google.com",
                "https://www.github.com",
                "https://www.stackoverflow.com",
                "https://www.reddit.com",
            ]
        
        if should_stop_flag is None:
            should_stop_flag = self._should_stop
        
        process = multiprocessing.Process(
            target=_run_browser_async,
            args=(profile_name, position, urls, should_stop_flag),
            daemon=True
        )
        process.start()
        self.processes.append(process)
        self.profile_names.append(profile_name)  # Track profile name
        return process
    
    def launch_multiple_browsers(self, num_browsers: int, 
                                 profile_prefix: str = "profile",
                                 urls: Optional[List[str]] = None) -> List[multiprocessing.Process]:
        """
        Launch multiple browsers in parallel processes.
        
        Args:
            num_browsers: Number of browsers to launch
            profile_prefix: Prefix for profile names (e.g., "profile_0", "profile_1")
            urls: Optional list of URLs to navigate to
            
        Returns:
            List of created processes
        """
        logger.info(f"🚀 Launching {num_browsers} browsers in parallel processes...")
        
        processes = []
        for i in range(num_browsers):
            profile_name = f"{profile_prefix}_{i}"
            process = self.launch_browser_process(profile_name, i, urls)
            processes.append(process)
        
        logger.info(f"✅ Started {len(processes)} browser processes")
        return processes
    
    def stop_all_browsers(self):
        """Stop all running browser processes."""
        logger.info("🔒 Stopping all browser processes...")
        
        # First, close all browsers explicitly
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
                process.join(timeout=5.0)  # Wait up to 5 seconds
                if process.is_alive():
                    logger.warning(f"Process {process.pid} did not stop gracefully, terminating")
                    process.terminate()
                    process.join(timeout=2.0)
                    if process.is_alive():
                        process.kill()
        
        self.processes.clear()
        self.profile_names.clear()
        self._should_stop.value = False
        logger.info("✅ All browser processes stopped")
    
    def get_running_processes(self) -> List[multiprocessing.Process]:
        """Get list of currently running processes."""
        # Remove finished processes and their corresponding profile names
        running_processes = []
        running_profiles = []
        for i, process in enumerate(self.processes):
            if process.is_alive():
                running_processes.append(process)
                if i < len(self.profile_names):
                    running_profiles.append(self.profile_names[i])
        
        self.processes = running_processes
        self.profile_names = running_profiles
        return self.processes
    
    def wait_for_all_processes(self, timeout: Optional[float] = None):
        """
        Wait for all processes to finish.
        
        Args:
            timeout: Maximum time to wait (None = wait indefinitely)
        """
        for process in self.processes:
            if process.is_alive():
                process.join(timeout=timeout)


def _run_browser_async(profile_name: str, position: int, 
                      urls: List[str], should_stop_flag=None):
    """
    Run browser async code in a process.
    
    This function runs in a separate process and executes the async browser code.
    
    Args:
        profile_name: Name of the browser profile
        position: Position index
        urls: List of URLs to navigate to
        should_stop_flag: Shared multiprocessing flag for stopping (optional)
    """
    loop = None
    try:
        # Import here to avoid issues with multiprocessing
        from nodrive_gpm_package import GPMClient
        
        # Create new event loop for this process
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the async browser code
        try:
            loop.run_until_complete(
                _launch_and_use_browser(profile_name, position, urls, should_stop_flag)
            )
        except asyncio.CancelledError:
            logger.info(f"[{profile_name}] Browser task was cancelled")
        except Exception as e:
            logger.error(f"Error in async browser code for {profile_name}: {e}")
        
    except ImportError as e:
        logger.error(f"Failed to import GPMClient: {e}")
        print(f"❌ [{profile_name}] Failed to import GPMClient: {e}")
    except Exception as e:
        logger.error(f"Error in browser process for {profile_name}: {e}")
        print(f"❌ [{profile_name}] Error: {e}")
    finally:
        if loop:
            try:
                # Cancel all pending tasks
                try:
                    pending_tasks = [task for task in asyncio.all_tasks(loop) if not task.done()]
                    if pending_tasks:
                        logger.info(f"[{profile_name}] Cancelling {len(pending_tasks)} pending tasks")
                        for task in pending_tasks:
                            task.cancel()
                        
                        # Wait for tasks to be cancelled (with timeout)
                        if pending_tasks:
                            try:
                                loop.run_until_complete(
                                    asyncio.wait_for(
                                        asyncio.gather(*pending_tasks, return_exceptions=True),
                                        timeout=2.0
                                    )
                                )
                            except asyncio.TimeoutError:
                                logger.warning(f"[{profile_name}] Timeout waiting for tasks to cancel")
                            except Exception as e:
                                logger.warning(f"[{profile_name}] Error waiting for task cancellation: {e}")
                except Exception as e:
                    logger.warning(f"[{profile_name}] Error getting pending tasks: {e}")
                
                # Close the loop
                loop.close()
            except Exception as e:
                logger.error(f"Error closing event loop for {profile_name}: {e}")


async def _launch_and_use_browser(profile_name: str, position: int,
                                  urls: List[str], should_stop_flag=None):
    """
    Launch a browser and use it (async function).
    
    Args:
        profile_name: Name of the browser profile
        position: Position index
        urls: List of URLs to navigate to
        should_stop_flag: Shared multiprocessing flag for stopping (optional)
    """
    from nodrive_gpm_package import GPMClient
    
    client = GPMClient()
    
    print(f"🚀 [{profile_name}] Launching at position {position}...")
    
    try:
        browser = await client.launch(
            profile_name=profile_name,
            position=position
        )
        
        if browser:
            print(f"✅ [{profile_name}] Browser launched successfully")
            
            # Check stop flag before navigating
            if should_stop_flag and should_stop_flag.value:
                print(f"⏹️ [{profile_name}] Stop requested before navigation")
                client.close(profile_name)
                return False
            
            # Navigate to a URL
            url = urls[position % len(urls)]
            tab = await browser.get(url)
            await asyncio.sleep(2)  # Wait for page to load
            
            # Check stop flag periodically
            if should_stop_flag and should_stop_flag.value:
                print(f"⏹️ [{profile_name}] Stop requested")
                client.close(profile_name)
                return False
            
            try:
                title = await tab.evaluate("document.title")
                print(f"📄 [{profile_name}] Loaded: {title}")
            except Exception as e:
                print(f"📄 [{profile_name}] Loaded: {url} (could not get title: {e})")
            
            # Keep browser open, checking stop flag periodically
            try:
                while not (should_stop_flag and should_stop_flag.value):
                    await asyncio.sleep(1)  # Check every second
                    # You can add more browser interaction here
            except asyncio.CancelledError:
                logger.info(f"[{profile_name}] Browser loop was cancelled")
                raise
            finally:
                # Close browser when stop is requested or cancelled
                print(f"🔒 [{profile_name}] Closing browser...")
                try:
                    client.close(profile_name)
                except Exception as e:
                    logger.warning(f"Error closing browser {profile_name}: {e}")
            
            return True
        else:
            print(f"❌ [{profile_name}] Failed to launch")
            return False
            
    except Exception as e:
        logger.error(f"Error launching browser {profile_name}: {e}")
        print(f"❌ [{profile_name}] Error: {e}")
        return False

