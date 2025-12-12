from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, Any, Literal, Union, List
from uuid import UUID
from src.enums.EModelAI import EModelAI
from src.schemas.manager_image_ai_item_store import ManagerImageAIItemStore

class AccountSocial(BaseModel):
    # Core account fields
    id: Optional[Union[str, UUID]] = None
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_id_to_string(cls, v):
        if v is None:
            return None
        if isinstance(v, UUID):
            return str(v)
        return v
    
   
    accountAI: Optional[str] = None
    model: Optional[EModelAI] = None
    versionModel: Optional[str] = None
    provider: Optional[str] = None
    password: str
    code2FA: str
    isActive: Optional[bool] = None
    status: Optional[str] = None
    
    manager_image_ai_item_store: Optional[List[ManagerImageAIItemStore]] = None

class AccountEmail(BaseModel):
    email: str
    password: str
    code2FA: str