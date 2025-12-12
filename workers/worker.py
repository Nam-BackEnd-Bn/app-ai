"""Base Worker class for QThread operations."""

import threading
import multiprocessing
from time import sleep
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from typing import Any, Optional, Dict, List
from loguru import logger


class Worker(QObject):
    """
    Base Worker class that runs in a QThread.
    
    This class provides a foundation for background tasks with signal-based
    communication. Subclasses should override the run() method to implement
    their specific work logic.
    """
    
    # Signals for communication with the main thread
    finished = pyqtSignal()  # Emitted when work is complete
    error = pyqtSignal(str)  # Emitted when an error occurs (error message)
    progress = pyqtSignal(int)  # Emitted to report progress (0-100)
    status = pyqtSignal(str)  # Emitted to report status messages
    result = pyqtSignal(dict)  # Emitted with result data
    
    def __init__(self):
        """Initialize the worker."""
        super().__init__()
        self._is_running = False
        self._should_stop = False
        self._threads: List[threading.Thread] = []  # Track all sub-threads
        self._processes: List[multiprocessing.Process] = []  # Track all sub-processes
    
    @pyqtSlot()
    def run(self):
        """
        Main work method. Override this in subclasses to implement specific tasks.
        
        This method is called when the thread starts. It should:
        - Perform the actual work
        - Emit progress/status signals as needed
        - Handle errors and emit error signal
        - Emit finished signal when done
        """
        try:
            self._is_running = True
            self._should_stop = False
            logger.info("Worker started")
            
            # Override this method in subclasses
            self.do_work()
            
        except Exception as e:
            logger.error(f"Worker error: {e}")
            self.error.emit(str(e))
        finally:
            self._is_running = False
            self.finished.emit()
            logger.info("Worker finished")
    
    def do_work(self):
        pass
    
    @pyqtSlot()
    def stop(self):
        """
        Request the worker to stop.
        
        This sets a flag that should be checked periodically in do_work().
        The worker should stop gracefully when this is called.
        All sub-threads and sub-processes should also check should_stop() and exit.
        """
        self._should_stop = True
        logger.info("Stop requested for worker")
        
        # Wait for all sub-threads to finish
        if self._threads:
            logger.info(f"Waiting for {len(self._threads)} sub-threads to finish...")
            for thread in self._threads:
                if thread.is_alive():
                    thread.join(timeout=1.0)  # Wait up to 1 second per thread
        
        # Wait for all sub-processes to finish
        if self._processes:
            logger.info(f"Waiting for {len(self._processes)} sub-processes to finish...")
            for process in self._processes:
                if process.is_alive():
                    process.join(timeout=2.0)  # Wait up to 2 seconds per process
                    if process.is_alive():
                        logger.warning(f"Process {process.pid} did not stop, terminating")
                        process.terminate()
                        process.join(timeout=1.0)
                        if process.is_alive():
                            process.kill()
    
    def is_running(self) -> bool:
        """Check if the worker is currently running."""
        return self._is_running
    
    def should_stop(self) -> bool:
        """Check if the worker should stop."""
        return self._should_stop
    
    def create_worker_thread(self, target, args=(), kwargs=None, daemon=True):
        """
        Helper method to create and start a worker thread.
        
        Args:
            target: Function to run in the thread
            args: Arguments for the target function
            kwargs: Keyword arguments for the target function
            daemon: Whether the thread should be a daemon thread
            
        Returns:
            The created and started thread
        """
        if kwargs is None:
            kwargs = {}
        thread = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=daemon)
        thread.start()
        self._threads.append(thread)
        return thread
    
    def wait_for_threads(self, timeout=None):
        """
        Wait for all tracked threads to finish.
        
        Args:
            timeout: Maximum time to wait (None = wait indefinitely)
        """
        for thread in self._threads:
            if thread.is_alive():
                thread.join(timeout=timeout)
    
    def create_worker_process(self, target, args=(), kwargs=None):
        """
        Helper method to create and start a worker process.
        
        Args:
            target: Function to run in the process
            args: Arguments for the target function
            kwargs: Keyword arguments for the target function
            
        Returns:
            The created and started process
        """
        if kwargs is None:
            kwargs = {}
        process = multiprocessing.Process(target=target, args=args, kwargs=kwargs, daemon=True)
        process.start()
        self._processes.append(process)
        return process
    
    def wait_for_processes(self, timeout=None):
        """
        Wait for all tracked processes to finish.
        
        Args:
            timeout: Maximum time to wait (None = wait indefinitely)
        """
        for process in self._processes:
            if process.is_alive():
                process.join(timeout=timeout)

