import nodriver as nd
from loguru import logger

from src.schemas.accounts import AccountEmail
from src.schemas.manager_image_ai_item_store import ManagerImageAIItemStore
from src.schemas.task_aI_image_voice_canva_instagram import TaskAIImageVoiceCanvaInstagram
from workers.no_drive_services.web_page_services.gmail.gmail_login import GmailLogin
from workers.no_drive_services.web_page_services.image_generate.check_in_whisk import CheckInWhisk
from workers.no_drive_services.web_page_services.image_generate.image_generator import ImageGenerator


class TaskExecute:
    def __init__(self, tab: nd.Tab):
        self.account_email = None
        self.task = None
        self.images_ai = None

        self.whisk_url = "https://labs.google/fx/tools/whisk"
        self.tab = tab

        self.login_gmail = GmailLogin()
        self.image_generator = ImageGenerator()

    async def execute_work_flow(
            self,
            task: TaskAIImageVoiceCanvaInstagram,
            account_email: AccountEmail,
            manager_image_ai_item_store: list[ManagerImageAIItemStore]
    ):
        self.account_email = account_email
        self.task = task
        self.images_ai = manager_image_ai_item_store

        # # Step 1: Generate Image in Whisk
        # await self._whisk_generate()

        # TODO: step 2 generate voice
        # TODO: step 3 generate video
        # TODO: step 4 upload file to drive

    async def _whisk_generate(self, ):
        logger.info("Check in whisk")
        click_success = await CheckInWhisk(self.tab, self.whisk_url).check_in_generate_tool_whisk()

        logger.info("Check login gmail if needed...")
        await self._login_gmail(click_success)

        logger.info("Executing image generation...")
        await self.image_generator.execute_image_generate(
            self.tab,
            self.account_email,
            self.task,
            self.images_ai
        )

    async def _login_gmail(self, click_success):
        if click_success:
            logger.info("✅ Successfully entered tool - no Gmail login needed")
        else:
            await self.login_gmail.execute_gmail_login(self.tab, self.account_email)
            logger.info(f"✅ Gmail login successful for account: {self.account_email.email}")
