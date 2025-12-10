"""User model for database."""

from sqlalchemy import Integer, String, Text, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
import uuid
from src.config.database import Base


class User(Base):
    """User model representing a user in the database."""
    
    __tablename__ = 'users'
    
    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    createdAt: Mapped[datetime] = mapped_column(DateTime(3), nullable=False, server_default=func.current_timestamp(3))
    user_fullName: Mapped[str] = mapped_column(String(255), nullable=False)
    updatedAt: Mapped[Optional[datetime]] = mapped_column(DateTime(3), nullable=True, onupdate=func.current_timestamp(3))
    user_email: Mapped[str] = mapped_column(String(100), nullable=False)
    user_avatar: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_password: Mapped[str] = mapped_column(String(100), nullable=False)
    user_phone: Mapped[str] = mapped_column(String(50), nullable=False)
    user_attachmentAccountNameLark: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    user_attachmentAccountIdLark: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    user_gender: Mapped[str] = mapped_column(String(50), nullable=False)
    user_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_isRootAdmin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    user_isSubAdmin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    user_status: Mapped[str] = mapped_column(String(50), nullable=False, default='Active')
    createdBy: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    updatedBy: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Index on user_email
    __table_args__ = (
        Index('IDX_643a0bfb9391001cf11e581bdd', 'user_email'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, fullName='{self.user_fullName}', email='{self.user_email}', status='{self.user_status}')>"
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': str(self.id) if self.id else None,
            'version': self.version,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None,
            'user_fullName': self.user_fullName,
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None,
            'user_email': self.user_email,
            'user_avatar': self.user_avatar,
            'user_phone': self.user_phone,
            'user_attachmentAccountNameLark': self.user_attachmentAccountNameLark,
            'user_attachmentAccountIdLark': self.user_attachmentAccountIdLark,
            'user_gender': self.user_gender,
            'user_address': self.user_address,
            'user_isRootAdmin': self.user_isRootAdmin,
            'user_isSubAdmin': self.user_isSubAdmin,
            'user_status': self.user_status,
            'createdBy': self.createdBy,
            'updatedBy': self.updatedBy
        }

