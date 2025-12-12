"""Manager Image AI Item Store model for database."""

from sqlalchemy import Integer, String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from src.config.database import Base


class ManagerImageAIItemStore(Base):
    """Manager Image AI Item Store model representing stored image items in the database."""
    
    __tablename__ = 'manager-image-ai-item-store'
    __table_args__ = (
        Index('idx_managerImage_typeFolderStore', 'managerImage', 'typeFolderStore'),
        {'quote': True}  # Quote table name to handle hyphens in MySQL
    )
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    createdAt: Mapped[datetime] = mapped_column(DateTime(3), nullable=False, server_default=func.current_timestamp(3))
    updatedAt: Mapped[Optional[datetime]] = mapped_column(DateTime(3), nullable=True, onupdate=func.current_timestamp(3))
    
    # Item store fields
    managerImage: Mapped[str] = mapped_column(String(100), nullable=False)
    typeFolderStore: Mapped[str] = mapped_column(String(100), nullable=False)  # Stored as string, validated by EFolderImageAI enum in schema
    file: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Audit fields
    createdBy: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    updatedBy: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<ManagerImageAIItemStore(id={self.id}, managerImage='{self.managerImage}', typeFolderStore='{self.typeFolderStore}', file='{self.file}')>"
    
    def to_dict(self):
        """Convert manager image AI item store to dictionary."""
        return {
            'id': self.id,
            'version': self.version,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None,
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None,
            'managerImage': self.managerImage,
            'typeFolderStore': self.typeFolderStore,
            'file': self.file,
            'createdBy': self.createdBy,
            'updatedBy': self.updatedBy
        }

