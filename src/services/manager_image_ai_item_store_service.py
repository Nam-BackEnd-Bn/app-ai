"""Manager Image AI Item Store service for business logic."""

from typing import List, Optional, Dict
from src.repositories.manager_image_ai_item_store_repository import ManagerImageAIItemStoreRepository

from src.enums.EFolderImageAI import EFolderImageAI
from src.schemas.manager_image_ai_item_store import ManagerImageAIItemStore
import uuid


class ManagerImageAIItemStoreService:
    """Service for Manager Image AI Item Store business logic."""
    
    def __init__(self, repository: ManagerImageAIItemStoreRepository):
        """
        Initialize service with repository.
        
        Args:
            repository: ManagerImageAIItemStoreRepository instance
        """
        self.repository = repository
    
    def find_manager_image_ai_item_store(self, account_id: str) -> Optional[List]:
        import random

        all_types = list(EFolderImageAI)
        num_per_type = 1

        result = []
        for type_ in all_types:
            for _ in range(num_per_type):
                result.append(
                    ManagerImageAIItemStore(
                        id=str(uuid.uuid4()),
                        version=1,
                        managerImage="00000000-0000-0000-0000-000000000000",  # TODO: Change to UUID if needed
                        typeFolderStore=type_,
                        file=random.choice([
                            "https://fastly.picsum.photos/id/197/200/300.jpg?hmac=p4Xo0YBZC4uaAtKFs7gx7d5446a8gUo7X6bEI9mgkpg",
                            "https://fastly.picsum.photos/id/497/200/300.jpg?hmac=IqTAOsl408FW-5QME1woScOoZJvq246UqZGGR9UkkkY",
                            "https://fastly.picsum.photos/id/178/200/300.jpg?hmac=o3W6XkZMX-Pv9EKaOaE6vvt4JpToHfjivAGRrpFuhiw",
                            "hthttps://fastly.picsum.photos/id/363/200/300.jpg?hmac=LvonEMeE2QnwxULuBZW5xHtdjkz844GnAPpEhDwGvMY",
                            "https://fastly.picsum.photos/id/528/200/300.jpg?hmac=nQ5klrDwddW0du03zqKfOpyHkFBDaspI729AfK_FXPY",
                        ]),
                        createdBy="admin",
                        updatedBy="admin",
                    )
                )
        return result