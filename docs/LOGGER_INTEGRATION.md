# Logger Integration with Frontend Terminal

## Overview

All `loguru` logger messages throughout the application are now automatically displayed in the frontend terminal in real-time.

## How It Works

### 1. Logger Handler (`src/utils/logger_handler.py`)

The `LoggerHandler` class:
- Captures all loguru log messages using a custom sink function
- Maps loguru log levels to frontend terminal types
- Emits Qt signals that the main window can receive

**Level Mapping:**
- `TRACE` → `debug`
- `DEBUG` → `debug`
- `INFO` → `info`
- `SUCCESS` → `success`
- `WARNING` → `warning`
- `ERROR` → `error`
- `CRITICAL` → `error`

### 2. Main Window Integration

In `MainWindow.__init__()`:
```python
# Setup logger handler to send logs to terminal
self.logger_handler = LoggerHandler()
self.logger_handler.log_message.connect(self._on_log_message)
self.logger_handler.start()
```

### 3. Terminal Display

The `_on_log_message()` method receives log messages and forwards them to the terminal:
```python
def _on_log_message(self, message: str, level: str):
    """Handle log message from logger handler."""
    self._update_terminal(message, level)
```

## Usage

Simply use loguru's logger anywhere in your code:

```python
from loguru import logger

logger.debug("Debug message")
logger.info("Info message")
logger.success("Success message")
logger.warning("Warning message")
logger.error("Error message")
```

All messages will automatically appear in the frontend terminal with:
- ✅ Appropriate color coding
- ⏰ Timestamps
- 📝 Log level indication

## Features

1. **Real-time Updates**: Logs appear instantly as they're generated
2. **Color-coded**: Different colors for different log levels
3. **Thread-safe**: Works with multiprocessing and QThreads
4. **No Code Changes Required**: Existing logger calls work automatically
5. **Auto-scroll**: Terminal auto-scrolls to show latest logs (can be toggled)
6. **Performance**: Limited to 1000 lines to prevent memory issues

## Cleanup

The logger handler is properly cleaned up when the application closes:
```python
def closeEvent(self, event):
    # Stop logger handler
    if hasattr(self, 'logger_handler') and self.logger_handler:
        self.logger_handler.stop()
```

## Benefits

- **Debugging**: See all application logs in one place
- **Monitoring**: Watch real-time progress of browser automation
- **User Experience**: Users can see what's happening behind the scenes
- **Troubleshooting**: Easier to diagnose issues without checking console/files

## Example Output

When the app starts:
```
[14:53:46] 🚀 Application started - All logs will appear in the terminal
[14:53:47] Initializing GPM service...
[14:53:48] Launching 2 browsers...
[14:53:50] ✅ 2 browsers launched successfully
[14:53:52] Browsers opened - Stop button available
[14:53:55] 🎨 Generating image with prompt: Create a sunset scene...
[14:54:10] ✅ Image generation completed
```

## Notes

- The logger handler captures **all** loguru logs, including from:
  - Main application code
  - Workers (QThreads)
  - Browser processes (multiprocessing)
  - Service classes
  - Feature modules

- Logs from child processes are captured when they use the same loguru logger instance

- The terminal display is independent of console/file logging - all outputs work simultaneously

