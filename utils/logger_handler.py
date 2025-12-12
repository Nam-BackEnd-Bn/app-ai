"""Custom logger handler to send logs to the frontend terminal."""

import builtins
import sys
from PyQt6.QtCore import QObject, pyqtSignal
from loguru import logger


class LoggerHandler(QObject):
    """Handler to capture loguru logs and emit them as Qt signals."""
    
    # Signal to emit log messages: (message, level)
    log_message = pyqtSignal(str, str)
    
    def __init__(self):
        """Initialize the logger handler."""
        super().__init__()
        self._handler_id = None
        self._original_print = None
    
    def _sink_function(self, message):
        """
        Sink function for loguru that processes log records.
        
        Args:
            message: Log record from loguru
        """
        try:
            # Get the log record
            record = message.record
            
            # Extract level and message
            level = record["level"].name.lower()
            log_text = record["message"]
            
            # Map loguru levels to frontend terminal types
            level_map = {
                "trace": "debug",
                "debug": "debug",
                "info": "info",
                "success": "success",
                "warning": "warning",
                "error": "error",
                "critical": "error",
            }
            
            terminal_level = level_map.get(level, "info")
            
            # Emit signal
            self.log_message.emit(log_text, terminal_level)
        except Exception as e:
            # Avoid infinite loop if logging the error fails
            print(f"Error in logger handler: {e}")
    
    def _install_print_hook(self):
        """Capture built-in print calls and forward them to the terminal."""
        if self._original_print is not None:
            return  # Already installed
        
        self._original_print = builtins.print
        
        def print_wrapper(*args, **kwargs):
            # Always execute the original print
            self._original_print(*args, **kwargs)
            
            # Only forward messages printed to stdout/stderr
            target = kwargs.get("file", sys.stdout)
            if target not in (sys.stdout, sys.stderr):
                return
            
            # Reconstruct the printed text
            sep = kwargs.get("sep", " ")
            end = kwargs.get("end", "\n")
            text = sep.join(map(str, args)) + end
            text = text.rstrip("\n")
            
            if not text.strip():
                return
            
            level = "error" if target is sys.stderr else "info"
            try:
                self.log_message.emit(text, level)
            except Exception:
                # Fall back silently to avoid recursion
                self._original_print("Error emitting print log", file=sys.stderr)
        
        builtins.print = print_wrapper
    
    def _remove_print_hook(self):
        """Restore the original built-in print function."""
        if self._original_print is not None:
            builtins.print = self._original_print
            self._original_print = None
    
    def start(self):
        """Start capturing logs."""
        if self._handler_id is None:
            self._handler_id = logger.add(
                self._sink_function,
                format="{message}",  # We only need the message, formatting is done in frontend
                level="DEBUG",  # Capture all levels
                colorize=False,
            )
        # Capture standard print output as info/error in the terminal
        self._install_print_hook()
    
    def stop(self):
        """Stop capturing logs."""
        if self._handler_id is not None:
            logger.remove(self._handler_id)
            self._handler_id = None
        self._remove_print_hook()

