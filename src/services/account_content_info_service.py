import uuid
from datetime import datetime
from typing import Optional, List

from src.enums.EModelAI import EModelAI
from src.schemas.accounts import AccountSocial
from src.services.manager_image_ai_item_store_service import ManagerImageAIItemStoreService


class AccountContentInfoService:
    """Service for Account Content Info business logic."""

    def __init__(self):
        pass

    def find_account_content_info(self) -> list[AccountSocial]:
        return [
            AccountSocial(
                id="00000000-0000-0000-0000-000000000000",  # TODO: Change to UUID
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
                version=1,
                createdBy="admin",
                updatedBy="admin",
                accountAI="tranchung23101982@gmail.com",
                model=EModelAI.GPT,
                versionModel="gpt-4o",
                provider="openai",
                password="qacjjjfhu1106",
                code2FA="tc7y mv7u v4w6 b5lb vcrt vuv4 fovy drbv",
                isActive=True,
                status="Active",
            )
        ]

    def mapp_account_with_manager_image_ai_item_store(
            self,
            accounts: list[AccountSocial],
            service: ManagerImageAIItemStoreService
    ) -> Optional[List[AccountSocial]] | None:
        if accounts is None:
            return None
        for account in accounts:
            account.manager_image_ai_item_store = service.find_manager_image_ai_item_store(account.id)
        return accounts
