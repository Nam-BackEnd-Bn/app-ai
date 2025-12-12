"""Main entry point for the application."""

import sys
import os

# CRITICAL: Set Qt attributes BEFORE creating QApplication
# This prevents COM initialization errors (OleInitialize failed)
# and allows QtWebEngineWidgets to work properly
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtWidgets import QApplication

# Set application attribute for QtWebEngineWidgets BEFORE creating QApplication
# This is required for QWebEngineView to work
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)

# Note: Qt 6 is Per-Monitor DPI Aware V2 by default on Windows
# Qt automatically uses Windows display scale settings - no manual configuration needed
# If you need to change DPI awareness level, use qt.conf file with:
# [Platforms]
# WindowsArguments = dpiawareness=0,1,2
# See: https://doc.qt.io/qt-6/highdpi.html#configuring-windows

# Create QApplication immediately to initialize Qt before any COM imports
app = QApplication(sys.argv)

# NOW safe to import modules that might use COM
from src.config.database import init_db, get_db_session
from src.module import initialize_modules
from src.seeders import create_sample_data, create_task_sample_data
from src.views.main_window import MainWindow


def main():
    """Application entry point."""
    # Initialize database
    try:
        init_db()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        return
    
    # Create database session
    session = get_db_session()
    
    # Create sample data if needed
    try:
        create_sample_data(session)
        create_task_sample_data(session, count=10)
    except Exception as e:
        print(f"Error: Could not create sample data: {e}")
    
    # Initialize modules (repositories, services, controllers)
    # This is safe now because QApplication is already created
    auth_controller, task_controller, settings_controller, action_controller, auth_middleware = initialize_modules(session)
    
    public_paths = [
        'login',
        'generate_login_html',
    ]
    auth_middleware.public_paths = public_paths
    
    # Create and show window
    window = MainWindow(auth_controller, task_controller, settings_controller, action_controller, auth_middleware)
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
