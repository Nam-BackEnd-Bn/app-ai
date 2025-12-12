"""Main window view."""

from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from src.Http.controllers import AuthController
from src.Http.controllers.task_ai_image_voice_canva_instagram_controller import TaskAIImageVoiceCanvaInstagramController
from src.Http.controllers.settings_controller import SettingsController
from src.Http.controllers.action_controller import ActionController
from src.Http.middleware.auth_middleware import AuthMiddleware
from src.views.backend import Backend
from utils.logger_handler import LoggerHandler
from loguru import logger


class MainWindow(QMainWindow):
    """Main application window (View layer)."""
    
    def __init__(
        self, 
        auth_controller: AuthController, 
        task_ai_image_voice_canva_instagram_controller: TaskAIImageVoiceCanvaInstagramController,
        settings_controller: SettingsController, 
        action_controller: ActionController, 
        auth_middleware: AuthMiddleware
    ):
        """
        Initialize main window.
        
        Args:
            auth_controller: AuthController instance
            task_controller: TaskAIImageVoiceCanvaInstagramController instance
            settings_controller: SettingsController instance
            action_controller: ActionController instance
            auth_middleware: AuthMiddleware instance
        """
        super().__init__()
        self.setWindowTitle("PyQt6 Task Management App")
        self.setGeometry(100, 100, 1400, 800)
        
        # Controllers
        self.auth_controller = auth_controller
        self.task_ai_image_voice_canva_instagram_controller = task_ai_image_voice_canva_instagram_controller
        self.settings_controller = settings_controller
        self.action_controller = action_controller
        self.auth_middleware = auth_middleware
        
        # Pagination state
        self.current_page = 1
        self.items_per_page = 10
        
        # Setup logger handler (don't start yet - wait until UI is ready)
        self.logger_handler = LoggerHandler()
        self.logger_handler.log_message.connect(self._on_log_message)
        
        # Connect action controller signals
        self._connect_action_signals()
        
        # Setup UI first
        self.setup_ui()
        
        # Now start logger handler and log welcome message
        self.logger_handler.start()
        logger.info("🚀 Application started - All logs will appear in the terminal")
    
    def setup_ui(self):
        """Setup the user interface."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Web view
        self.web = QWebEngineView()
        layout.addWidget(self.web)
        
        # Setup web channel for JS-Python communication
        self.channel = QWebChannel()
        self.backend = Backend(self)
        self.channel.registerObject('backend', self.backend)
        self.web.page().setWebChannel(self.channel)
        
        # Load login page
        self.show_login()
    
    def _connect_action_signals(self):
        """Connect action controller signals to UI handlers."""
        self.action_controller.action_result.connect(self._on_action_result)
        self.action_controller.action_error.connect(self._on_action_error)
        self.action_controller.action_status.connect(self._on_action_status)
        self.action_controller.action_progress.connect(self._on_action_progress)
        self.action_controller.action_started.connect(self._on_action_started)
        self.action_controller.action_stopped.connect(self._on_action_stopped)
    
    def show_login(self):
        """Display the login page."""
        html = self.auth_controller.generate_login_html()
        self.web.setHtml(html)
    
    def handle_login(self, username: str, password: str):
        """Handle login logic using controller with middleware."""
        # Check auth (login is public, so this will return None)
        auth_error = self.auth_middleware.check_auth('login')
        if auth_error:
            self.web.page().runJavaScript("showError();")
            return
        
        # Execute with exception handling
        result = self.auth_middleware.handle_exception(
            self.auth_controller.login, username, password
        )
        
        # Check if result is an error dict
        if isinstance(result, dict) and not result.get('success', True):
            self.web.page().runJavaScript("showError();")
            return
        
        if result.get('success'):
            # Set current user after successful login
            if 'user' in result:
                self.auth_middleware.set_current_user(result['user'])
                logger.info(f"✓ Authenticated: {result['user'].get('user_email', 'N/A')}")
            self.show_table()
        else:
            self.web.page().runJavaScript("showError();")
    
    def show_table(self):
        """Display the table page."""
        # Check auth for get_tasks (called inside generate_table_html)
        auth_error = self.auth_middleware.check_auth('get_tasks')
        if auth_error:
            # Show error or redirect to login
            self.show_login()
            return
        
        # Execute with exception handling
        html = self.auth_middleware.handle_exception(
            self.task_ai_image_voice_canva_instagram_controller.generate_table_html, self.current_page, self.items_per_page
        )
        
        # If result is error dict, handle it
        if isinstance(html, dict) and not html.get('success', True):
            self.show_login()
            return
        
        self.web.setHtml(html)
    
    def handle_change_page(self, page: int):
        """Handle page change logic using controller."""
        self.current_page = page
        
        # Check auth for get_tasks
        auth_error = self.auth_middleware.check_auth('get_tasks')
        if auth_error:
            self.show_login()
            return
        
        # Execute with exception handling
        html = self.auth_middleware.handle_exception(
            self.task_ai_image_voice_canva_instagram_controller.generate_table_html, self.current_page, self.items_per_page
        )
        
        # If result is error dict, handle it
        if isinstance(html, dict) and not html.get('success', True):
            self.show_login()
            return
        
        self.web.setHtml(html)
    
    def handle_start_action(self):
        """Handle start action logic - delegates to controller."""
        try:
            # Call controller's async method
            self.action_controller.start_action_async()
        except Exception as e:
            logger.error(f"Error in handle_start_action: {e}")
            error_msg = str(e).replace("'", "\\'")
            self.web.page().runJavaScript(f"""
                if (typeof toastr !== 'undefined') {{
                    toastr.error('Error: {error_msg}');
                }} else {{
                    document.getElementById('status').innerHTML = 
                        '<span style="color: red;">✗ Error: {error_msg}</span>';
                }}
            """)
    
    def handle_stop_action(self):
        """Handle stop action logic - delegates to controller."""
        try:
            # Call controller's async method
            self.action_controller.stop_action_async()
        except Exception as e:
            logger.error(f"Error in handle_stop_action: {e}")
            error_msg = str(e).replace("'", "\\'")
            self.web.page().runJavaScript(f"""
                if (typeof toastr !== 'undefined') {{
                    toastr.error('Error: {error_msg}');
                }} else {{
                    document.getElementById('status').innerHTML = 
                        '<span style="color: red;">✗ Error: {error_msg}</span>';
                }}
                // Show Start button and hide Stop button on error
                document.getElementById('startBtn').style.display = 'inline-block';
                document.getElementById('stopBtn').style.display = 'none';
                // Enable logout button
                var logoutBtn = document.getElementById('logoutBtn');
                if (logoutBtn) {{
                    logoutBtn.disabled = false;
                    logoutBtn.style.opacity = '1';
                    logoutBtn.style.cursor = 'pointer';
                }}
            """)
    
    def handle_save_settings(self, settings_json: str):
        """Handle save settings to cache."""
        try:
            # Get current user ID
            current_user = self.auth_middleware.get_current_user()
            user_id = current_user.get('id', 'anonymous') if current_user else 'anonymous'
            
            # Use settings controller to save
            result = self.settings_controller.save_settings(user_id, settings_json)
            
            if result.get('success'):
                logger.info(f"Settings saved successfully for user: {user_id}")
            else:
                logger.warning(f"Failed to save settings: {result.get('message')}")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def handle_get_settings(self) -> str:
        """Get settings from cache."""
        try:
            # Get current user ID
            current_user = self.auth_middleware.get_current_user()
            user_id = current_user.get('id', 'anonymous') if current_user else 'anonymous'
            
            # Use settings controller to get settings
            return self.settings_controller.get_settings_json(user_id)
        except Exception as e:
            logger.error(f"Error getting settings: {e}")
            return "{}"
    
    def handle_logout(self):
        """Handle logout logic."""
        try:
            # Stop any running action threads via controller
            self.action_controller.cleanup()
            
            # Get current user before logout
            current_user = self.auth_middleware.get_current_user()
            self.auth_controller.logout(current_user)
            
            # Redirect to login page
            self.show_login()
            
            logger.info("User logged out successfully")
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            # Still redirect to login even if there's an error
            self.show_login()
    
    def _on_action_started(self):
        """Handle action started signal from controller."""
        try:
            # Update UI to show action is running
            # Don't show Stop button yet - wait for browsers to open
            self.web.page().runJavaScript("""
                // Disable logout button
                var logoutBtn = document.getElementById('logoutBtn');
                if (logoutBtn) {
                    logoutBtn.disabled = true;
                    logoutBtn.style.opacity = '0.6';
                    logoutBtn.style.cursor = 'not-allowed';
                }
                // Hide Start button but don't show Stop button yet (browsers still opening)
                document.getElementById('startBtn').style.display = 'none';
                document.getElementById('stopBtn').style.display = 'none';
                // Show progress bar
                if (typeof showProgressBar === 'function') {
                    showProgressBar();
                }
            """)
            # Update terminal
            self._update_terminal("Action started - Initializing...", "info")
        except Exception as e:
            logger.error(f"Error in _on_action_started: {e}")
    
    def _on_action_stopped(self):
        """Handle action stopped signal from controller."""
        try:
            # Update UI when action thread stops - show Start button and hide Stop button
            self.web.page().runJavaScript("""
                hideLoading();
                // Hide progress bar
                if (typeof hideProgressBar === 'function') {
                    hideProgressBar();
                }
                // Show Start button and hide Stop button
                document.getElementById('startBtn').style.display = 'inline-block';
                document.getElementById('stopBtn').style.display = 'none';
                // Enable logout button
                var logoutBtn = document.getElementById('logoutBtn');
                if (logoutBtn) {
                    logoutBtn.disabled = false;
                    logoutBtn.style.opacity = '1';
                    logoutBtn.style.cursor = 'pointer';
                }
            """)
            # Update terminal
            self._update_terminal("Action stopped", "warning")
            logger.debug("Action thread stopped - UI updated")
        except Exception as e:
            logger.error(f"Error in _on_action_stopped: {e}")
    
    def _update_terminal(self, message: str, log_type: str = "info"):
        """
        Update terminal output in the UI.
        
        Args:
            message: Message to display
            log_type: Type of log (info, success, warning, error, debug)
        """
        try:
            # Check if web view is initialized
            if not hasattr(self, 'web') or self.web is None:
                return  # Silently skip if UI not ready yet
            
            # Escape single quotes and newlines for JavaScript
            escaped_message = message.replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
            self.web.page().runJavaScript(f"""
                if (typeof updateTerminal === 'function') {{
                    updateTerminal('{escaped_message}', '{log_type}');
                }}
            """)
        except Exception as e:
            # Use print to avoid recursive logging
            print(f"Error updating terminal: {e}")
    
    def _on_action_result(self, result: dict):
        """Handle action result from controller."""
        try:
            # Hide overlay when action completes
            hide_overlay_js = "hideLoading();"
            
            if result.get('success'):
                message = result.get('message', 'Action completed successfully')
                self.web.page().runJavaScript(f"""
                    {hide_overlay_js}
                    // Hide progress bar on completion
                    if (typeof hideProgressBar === 'function') {{
                        hideProgressBar();
                    }}
                    if (typeof toastr !== 'undefined') {{
                        toastr.success('{message.replace("'", "\\'")}');
                    }} else {{
                        document.getElementById('status').innerHTML = 
                            '<span style="color: green;">✓ {message.replace("'", "\\'")}</span>';
                    }}
                """)
                # Update terminal
                self._update_terminal(f"✓ {message}", "success")
            else:
                message = result.get('message', 'Action failed')
                self.web.page().runJavaScript(f"""
                    {hide_overlay_js}
                    // Hide progress bar on failure
                    if (typeof hideProgressBar === 'function') {{
                        hideProgressBar();
                    }}
                    if (typeof toastr !== 'undefined') {{
                        toastr.error('{message.replace("'", "\\'")}');
                    }} else {{
                        document.getElementById('status').innerHTML = 
                            '<span style="color: red;">✗ {message.replace("'", "\\'")}</span>';
                    }}
                """)
                # Update terminal
                self._update_terminal(f"✗ {message}", "error")
            
            # Update UI buttons - check if it's a stop action result
            if result.get('action_type') == 'stop':
                self.web.page().runJavaScript("""
                    // Hide progress bar
                    if (typeof hideProgressBar === 'function') {
                        hideProgressBar();
                    }
                    // Show Start button and hide Stop button
                    document.getElementById('startBtn').style.display = 'inline-block';
                    document.getElementById('stopBtn').style.display = 'none';
                    // Enable logout button
                    var logoutBtn = document.getElementById('logoutBtn');
                    if (logoutBtn) {
                        logoutBtn.disabled = false;
                        logoutBtn.style.opacity = '1';
                        logoutBtn.style.cursor = 'pointer';
                    }
                """)
        except Exception as e:
            logger.error(f"Error in _on_action_result: {e}")
    
    def _on_action_error(self, error_message: str):
        """Handle action error from controller."""
        try:
            error_msg = error_message.replace("'", "\\'")
            self.web.page().runJavaScript(f"""
                hideLoading();
                if (typeof toastr !== 'undefined') {{
                    toastr.error('Error: {error_msg}');
                }} else {{
                    document.getElementById('status').innerHTML = 
                        '<span style="color: red;">✗ Error: {error_msg}</span>';
                }}
            """)
            # Update terminal
            self._update_terminal(f"Error: {error_message}", "error")
            
            # Reset UI buttons on error
            self.web.page().runJavaScript("""
                // Hide progress bar
                if (typeof hideProgressBar === 'function') {
                    hideProgressBar();
                }
                // Show Start button and hide Stop button
                document.getElementById('startBtn').style.display = 'inline-block';
                document.getElementById('stopBtn').style.display = 'none';
                // Enable logout button
                var logoutBtn = document.getElementById('logoutBtn');
                if (logoutBtn) {
                    logoutBtn.disabled = false;
                    logoutBtn.style.opacity = '1';
                    logoutBtn.style.cursor = 'pointer';
                }
            """)
        except Exception as e:
            logger.error(f"Error in _on_action_error: {e}")
    
    def _on_action_status(self, status_message: str):
        """Handle action status update from controller."""
        try:
            # Check if browsers are opened - show Stop button when ready
            if status_message == "BROWSERS_OPENED":
                self.web.page().runJavaScript("""
                    // Show Stop button now that browsers are fully opened
                    document.getElementById('stopBtn').style.display = 'inline-block';
                """)
                logger.debug("Browsers opened - Stop button shown")
                # Update terminal
                self._update_terminal("Browsers opened - Stop button available", "success")
            else:
                # Update terminal with status message
                self._update_terminal(status_message, "info")
                # logger.debug(f"Action status: {status_message}")
        except Exception as e:
            logger.error(f"Error in _on_action_status: {e}")
    
    def _on_action_progress(self, progress: int):
        """Handle action progress update from controller."""
        try:
            # Update progress bar
            self.web.page().runJavaScript(f"""
                if (typeof updateProgressBar === 'function') {{
                    updateProgressBar({progress});
                }}
            """)
            
            # Hide overlay when progress reaches 100% (browsers are launching)
            # But don't show Stop button yet - wait for BROWSERS_OPENED status
            if progress >= 100:
                self.web.page().runJavaScript("""
                    hideLoading();
                    // Don't show Stop button yet - wait for browsers to fully open
                """)
            
            # Update terminal with progress
            self._update_terminal(f"Progress: {progress}%", "info")
            logger.debug(f"Action progress: {progress}%")
        except Exception as e:
            logger.error(f"Error in _on_action_progress: {e}")
    
    def _on_log_message(self, message: str, level: str):
        """
        Handle log message from logger handler.
        
        Args:
            message: Log message text
            level: Log level (info, success, warning, error, debug)
        """
        try:
            self._update_terminal(message, level)
        except Exception as e:
            print(f"Error handling log message: {e}")
    
    def closeEvent(self, event):
        """Handle window close event - cleanup threads via controller."""
        try:
            # Stop logger handler
            if hasattr(self, 'logger_handler') and self.logger_handler:
                self.logger_handler.stop()
            
            # Stop any running threads via controller
            # This will safely handle deleted QThread objects
            if self.action_controller:
                self.action_controller.cleanup()
        except Exception as e:
            logger.error(f"Error in closeEvent: {e}")
        finally:
            # Always accept the close event to allow the window to close
            event.accept()

