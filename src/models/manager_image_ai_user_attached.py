"""Manager Image AI User Attached model for database."""

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from src.config.database import Base


class ManagerImageAIUserAttached(Base):
    """Manager Image AI User Attached model representing attachments in the database."""
    
    __tablename__ = 'manager-image-ai-user-attached'
    __table_args__ = {'quote': True}  # Quote table name to handle hyphens in MySQL
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    createdAt: Mapped[datetime] = mapped_column(DateTime(3), nullable=False, server_default=func.current_timestamp(3))
    updatedAt: Mapped[Optional[datetime]] = mapped_column(DateTime(3), nullable=True, onupdate=func.current_timestamp(3))
    
    # Account and social fields
    accountSocial: Mapped[str] = mapped_column(String(100), nullable=False)
    typeSocial: Mapped[str] = mapped_column(String(100), nullable=False)  # Stored as string, validated by ETypeSocial enum in schema
    managerImageAI: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Audit fields
    createdBy: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    updatedBy: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<ManagerImageAIUserAttached(id={self.id}, accountSocial='{self.accountSocial}', typeSocial='{self.typeSocial}')>"
    
    def to_dict(self):
        """Convert manager image AI user attached to dictionary."""
        return {
            'id': self.id,
            'version': self.version,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None,
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None,
            'accountSocial': self.accountSocial,
            'typeSocial': self.typeSocial,
            'managerImageAI': self.managerImageAI,
            'createdBy': self.createdBy,
            'updatedBy': self.updatedBy
        }

