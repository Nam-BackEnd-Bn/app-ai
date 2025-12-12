from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, Union
from uuid import UUID
from src.enums.EFolderImageAI import EFolderImageAI


class ManagerImageAIItemStore(BaseModel):
    """Schema for Manager Image AI Item Store."""
    
    # Core fields
    id: Optional[Union[str, UUID]] = None
    # Item store fields
    managerImage: str
    typeFolderStore: EFolderImageAI
    file: str
    
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_id_to_string(cls, v):
        if v is None:
            return None
        if isinstance(v, UUID):
            return str(v)
        return v
    


