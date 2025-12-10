"""Example Worker that uses GPM service with multiprocessing."""

from src.workers.worker import Worker
from src.services.gpm_service import GPMService
from loguru import logger


class GPMWorker(Worker):
    """
    Worker that launches multiple browsers using GPM service with multiprocessing.
    
    This worker demonstrates how to use the GPM service within a QThread worker.
    """
    
    def __init__(self, num_browsers: int = 4, profile_prefix: str = "profile", 
                 urls: list = None):
        """
        Initialize the GPM worker.
        
        Args:
            num_browsers: Number of browsers to launch
            profile_prefix: Prefix for profile names
            urls: Optional list of URLs to navigate to
        """
        super().__init__()
        self.num_browsers = num_browsers
        self.profile_prefix = profile_prefix
        self.urls = urls
        self.gpm_service = GPMService()
    
    def do_work(self):
        """
        Launch multiple browsers using GPM service with multiprocessing.
        """
        try:
            self.status.emit("Initializing GPM service...")
            self.progress.emit(10)
            
            if self.should_stop():
                return
            
            self.status.emit(f"Launching {self.num_browsers} browsers...")
            self.progress.emit(20)
            
            # Launch multiple browsers in parallel processes
            processes = self.gpm_service.launch_multiple_browsers(
                num_browsers=self.num_browsers,
                profile_prefix=self.profile_prefix,
                urls=self.urls
            )
            
            if self.should_stop():
                self.gpm_service.stop_all_browsers()
                return
            
            self.progress.emit(50)
            self.status.emit(f"✅ {len(processes)} browsers launched successfully")
            
            # Monitor processes and check for stop signal
            while processes and not self.should_stop():
                # Remove finished processes
                processes = [p for p in processes if p.is_alive()]
                
                # Update status
                running = len(processes)
                if running > 0:
                    self.status.emit(f"Running: {running} browsers active")
                
                # Check stop flag every 0.1 seconds
                for _ in range(10):  # 1 second total
                    if self.should_stop():
                        break
                    from time import sleep
                    sleep(0.1)
            
            # Stop all browsers when stop is requested
            if self.should_stop():
                self.status.emit("Stopping all browsers...")
                self.gpm_service.stop_all_browsers()
                self.progress.emit(100)
                self.result.emit({
                    "success": True,
                    "message": f"Stopped {self.num_browsers} browsers",
                    "browsers_launched": self.num_browsers
                })
            else:
                # All processes finished naturally
                self.progress.emit(100)
                self.status.emit("All browsers finished")
                self.result.emit({
                    "success": True,
                    "message": f"All {self.num_browsers} browsers finished",
                    "browsers_launched": self.num_browsers
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
    
    def stop(self):
        """Override stop to also stop GPM service."""
        super().stop()
        if self.gpm_service:
            try:
                self.gpm_service.stop_all_browsers()
            except Exception as e:
                logger.error(f"Error stopping GPM service: {e}")

