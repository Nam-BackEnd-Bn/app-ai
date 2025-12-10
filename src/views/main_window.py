"""Main window view."""

from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from src.controllers.auth_controller import AuthController
from src.controllers.task_controller import TaskController
from src.controllers.settings_controller import SettingsController
from src.controllers.action_controller import ActionController
from src.middleware.auth_middleware import AuthMiddleware
from src.views.backend import Backend
from loguru import logger


class MainWindow(QMainWindow):
    """Main application window (View layer)."""
    
    def __init__(self, auth_controller: AuthController, task_controller: TaskController,
                 settings_controller: SettingsController, action_controller: ActionController,
                 auth_middleware: AuthMiddleware):
        """
        Initialize main window.
        
        Args:
            auth_controller: AuthController instance
            task_controller: TaskController instance
            settings_controller: SettingsController instance
            action_controller: ActionController instance
            auth_middleware: AuthMiddleware instance
        """
        super().__init__()
        self.setWindowTitle("PyQt6 Task Management App")
        self.setGeometry(100, 100, 1400, 800)
        
        # Controllers
        self.auth_controller = auth_controller
        self.task_controller = task_controller
        self.settings_controller = settings_controller
        self.action_controller = action_controller
        self.auth_middleware = auth_middleware
        
        # Pagination state
        self.current_page = 1
        self.items_per_page = 10
        
        # Connect action controller signals
        self._connect_action_signals()
        
        # Setup UI
        self.setup_ui()
    
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
            self.task_controller.generate_table_html, self.current_page, self.items_per_page
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
            self.task_controller.generate_table_html, self.current_page, self.items_per_page
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
            self.web.page().runJavaScript("""
                // Disable logout button
                var logoutBtn = document.getElementById('logoutBtn');
                if (logoutBtn) {
                    logoutBtn.disabled = true;
                    logoutBtn.style.opacity = '0.6';
                    logoutBtn.style.cursor = 'not-allowed';
                }
                // Hide Start button and show Stop button
                document.getElementById('startBtn').style.display = 'none';
                document.getElementById('stopBtn').style.display = 'inline-block';
            """)
        except Exception as e:
            logger.error(f"Error in _on_action_started: {e}")
    
    def _on_action_stopped(self):
        """Handle action stopped signal from controller."""
        try:
            # Update UI when action thread stops - show Start button and hide Stop button
            self.web.page().runJavaScript("""
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
            logger.debug("Action thread stopped - UI updated")
        except Exception as e:
            logger.error(f"Error in _on_action_stopped: {e}")
    
    def _on_action_result(self, result: dict):
        """Handle action result from controller."""
        try:
            if result.get('success'):
                message = result.get('message', 'Action completed successfully')
                self.web.page().runJavaScript(f"""
                    if (typeof toastr !== 'undefined') {{
                        toastr.success('{message.replace("'", "\\'")}');
                    }} else {{
                        document.getElementById('status').innerHTML = 
                            '<span style="color: green;">✓ {message.replace("'", "\\'")}</span>';
                    }}
                """)
            else:
                message = result.get('message', 'Action failed')
                self.web.page().runJavaScript(f"""
                    if (typeof toastr !== 'undefined') {{
                        toastr.error('{message.replace("'", "\\'")}');
                    }} else {{
                        document.getElementById('status').innerHTML = 
                            '<span style="color: red;">✗ {message.replace("'", "\\'")}</span>';
                    }}
                """)
            
            # Update UI buttons - check if it's a stop action result
            if result.get('action_type') == 'stop':
                self.web.page().runJavaScript("""
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
                if (typeof toastr !== 'undefined') {{
                    toastr.error('Error: {error_msg}');
                }} else {{
                    document.getElementById('status').innerHTML = 
                        '<span style="color: red;">✗ Error: {error_msg}</span>';
                }}
            """)
            
            # Reset UI buttons on error
            self.web.page().runJavaScript("""
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
            # You can update UI with status messages here if needed
            logger.debug(f"Action status: {status_message}")
        except Exception as e:
            logger.error(f"Error in _on_action_status: {e}")
    
    def _on_action_progress(self, progress: int):
        """Handle action progress update from controller."""
        try:
            # You can update progress bar or UI here if needed
            logger.debug(f"Action progress: {progress}%")
        except Exception as e:
            logger.error(f"Error in _on_action_progress: {e}")
    
    def closeEvent(self, event):
        """Handle window close event - cleanup threads via controller."""
        try:
            # Stop any running threads via controller
            # This will safely handle deleted QThread objects
            if self.action_controller:
                self.action_controller.cleanup()
        except Exception as e:
            logger.error(f"Error in closeEvent: {e}")
        finally:
            # Always accept the close event to allow the window to close
            event.accept()

