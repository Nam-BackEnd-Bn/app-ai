"""Sample user data creation."""

import bcrypt
from sqlalchemy.orm import Session
from src.repositories.user_repository import UserRepository


def create_sample_data(session: Session):
    """Create sample data if admin user doesn't exist."""
    admin_email = "admin@example.com"
    user_repo = UserRepository(session)
    try:
        # Check if admin user exists
        existing_admin = user_repo.get_by_email(admin_email)
        
        if existing_admin is None:
            # Hash password using bcrypt
            password = "admin123"
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create superadmin user using repository
            superadmin = user_repo.create(
                user_fullName="Super Admin",
                user_email=admin_email,
                user_password=hashed_password,
                user_phone="+1234567890",
                user_gender="Male",
                user_status="Active",
                user_isRootAdmin=True,
                user_isSubAdmin=False
            )
            print(f"Superadmin sample data created successfully! ID: {superadmin.id}")
        else:
            print(f"Admin user ({admin_email}) already exists. Skipping creation.")
    except Exception as e:
        print(f"Error creating sample data: {e}")
        raise

