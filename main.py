"""Main entry point for the application."""

import sys
from PyQt6.QtWidgets import QApplication
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
    auth_controller, task_controller, settings_controller, action_controller, auth_middleware = initialize_modules(session)
    
    public_paths = [
        'login',
        'generate_login_html',
    ]
    auth_middleware.public_paths = public_paths
    
    # Create and show application
    app = QApplication(sys.argv)
    window = MainWindow(auth_controller, task_controller, settings_controller, action_controller, auth_middleware)
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
