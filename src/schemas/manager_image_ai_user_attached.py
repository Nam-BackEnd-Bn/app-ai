from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, Union
from uuid import UUID
from src.enums.ETypeSocial import ETypeSocial

class ManagerImageAIUserAttached(BaseModel):
    """Schema for Manager Image AI User Attached."""
    
    # Core fields
    id: Optional[Union[str, UUID]] = None
    version: Optional[int] = None
    createdAt: Optional[Union[str, datetime]] = None
    updatedAt: Optional[Union[str, datetime]] = None
    
    # Account and social fields
    accountSocial: str
    typeSocial: ETypeSocial
    managerImageAI: str # 
    
    # Audit fields
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_id_to_string(cls, v):
        if v is None:
            return None
        if isinstance(v, UUID):
            return str(v)
        return v
    
    @field_validator('createdAt', 'updatedAt', mode='before')
    @classmethod
    def convert_datetime_to_string(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.isoformat()
        return v
