# MVC Architecture with SQLAlchemy

This application follows the MVC (Model-View-Controller) architecture pattern with clear separation of concerns.

## Project Structure

```
src/
├── main.py                 # Application entry point
├── config/                 # Configuration
│   ├── __init__.py
│   └── database.py         # Database configuration and session management
├── models/                 # SQLAlchemy models (Data layer)
│   ├── __init__.py
│   └── user.py             # User model
├── repositories/           # Data access layer
│   ├── __init__.py
│   └── user_repository.py  # User repository for database queries
├── services/               # Business logic layer
│   ├── __init__.py
│   ├── user_service.py     # User business logic
│   └── auth_service.py     # Authentication business logic
├── controllers/            # Request handling layer
│   ├── __init__.py
│   ├── auth_controller.py  # Authentication controller
│   └── user_controller.py  # User controller
├── views/                  # Presentation layer
│   ├── __init__.py
│   └── main_window.py      # Main window view
└── html/                   # HTML templates
    ├── login.html
    └── table_template.html
```

## Architecture Layers

### 1. Models (`models/`)
- **Purpose**: Define database schema using SQLAlchemy ORM
- **Contains**: 
  - `User`: User model with id, name, email, and status fields

### 2. Repositories (`repositories/`)
- **Purpose**: Handle all database queries and operations
- **Contains**:
  - `UserRepository`: CRUD operations for users
  - Methods: `get_by_id()`, `get_by_email()`, `get_all()`, `create()`, `update()`, `delete()`, `get_paginated()`

### 3. Services (`services/`)
- **Purpose**: Business logic and validation
- **Contains**:
  - `UserService`: User-related business logic
  - `AuthService`: Authentication business logic
  - Handles validation, error handling, and business rules

### 4. Controllers (`controllers/`)
- **Purpose**: Handle requests from views and coordinate with services
- **Contains**:
  - `AuthController`: Handles authentication requests
  - `UserController`: Handles user-related requests
  - Returns standardized response dictionaries

### 5. Views (`views/`)
- **Purpose**: User interface and presentation
- **Contains**:
  - `MainWindow`: PyQt6 main window that displays HTML content
  - Communicates with controllers, not directly with services or repositories

## Database Configuration

The database configuration is in `config/database.py`. You can configure it using environment variables:

```bash
export DB_USER=root
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=app_database
```

Or modify the defaults in `DatabaseConfig` class.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create MySQL database:
```sql
CREATE DATABASE app_database;
```

3. Configure database connection in `src/config/database.py` or use environment variables.

4. Run the application:
```bash
python src/main.py
```

## Data Flow

1. **View** (MainWindow) receives user action
2. **View** calls **Controller** method
3. **Controller** calls **Service** method
4. **Service** calls **Repository** method
5. **Repository** executes database query using SQLAlchemy
6. Data flows back through the layers
7. **View** updates the UI

## Example Flow: Login

1. User enters credentials in HTML form
2. JavaScript calls `backend.login(username, password)`
3. `Backend` object calls `MainWindow.handle_login()`
4. `MainWindow` calls `AuthController.login()`
5. `AuthController` calls `AuthService.authenticate()`
6. `AuthService` calls `UserRepository.get_by_email()`
7. Repository queries database via SQLAlchemy
8. Result flows back through layers
9. View updates to show table or error

## Benefits

- **Separation of Concerns**: Each layer has a single responsibility
- **Testability**: Easy to test each layer independently
- **Maintainability**: Changes in one layer don't affect others
- **Scalability**: Easy to add new features following the same pattern
- **Database Abstraction**: SQLAlchemy provides database independence

