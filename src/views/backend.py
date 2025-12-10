"""Backend object for JavaScript-Python communication via QWebChannel."""

from PyQt6.QtCore import QObject, pyqtSlot


class Backend(QObject):
    """Backend object for JavaScript-Python communication via QWebChannel."""
    
    def __init__(self, main_window):
        """
        Initialize backend.
        
        Args:
            main_window: MainWindow instance
        """
        super().__init__()
        self.main_window = main_window
    
    @pyqtSlot(str, str)
    def login(self, username, password):
        """Handle login request from JavaScript."""
        self.main_window.handle_login(username, password)
    
    @pyqtSlot(int)
    def change_page(self, page):
        """Handle page change request from JavaScript."""
        self.main_window.handle_change_page(page)
    
    @pyqtSlot()
    def start_action(self):
        """Handle start action request from JavaScript."""
        self.main_window.handle_start_action()
    
    @pyqtSlot()
    def stop_action(self):
        """Handle stop action request from JavaScript."""
        self.main_window.handle_stop_action()
    
    @pyqtSlot(str)
    def save_settings(self, settings_json):
        """Handle save settings request from JavaScript."""
        self.main_window.handle_save_settings(settings_json)
    
    @pyqtSlot(result=str)
    def get_settings(self):
        """Get settings from cache."""
        return self.main_window.handle_get_settings()
    
    @pyqtSlot()
    def reload_table(self):
        """Reload the table data."""
        self.main_window.show_table()
    
    @pyqtSlot()
    def logout(self):
        """Handle logout request from JavaScript."""
        self.main_window.handle_logout()

