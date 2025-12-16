import nodriver as nd
from loguru import logger
from asyncio import sleep as asyncio_sleep
from src.schemas.accounts import AccountEmail
from src.schemas.manager_image_ai_item_store import ManagerImageAIItemStore
from src.schemas.task_aI_image_voice_canva_instagram import TaskAIImageVoiceCanvaInstagram
from workers.no_drive_services.web_page_services.gmail.gmail_login import GmailLogin
from workers.no_drive_services.web_page_services.image_generate.check_in_whisk import CheckInWhisk
from workers.no_drive_services.web_page_services.image_generate.image_generator import ImageGenerator
from workers.no_drive_services.web_page_services.voice_generate.check_in_speech import CheckInSpeech
from workers.no_drive_services.web_page_services.voice_generate.voice_generator import VoiceGenerator
from workers.no_drive_services.web_page_services.video_generate.video_generator import VideoGenerator


class TaskExecute:
    def __init__(self, tab: nd.Tab):
        self.account_email = None
        self.task = None
        self.images_ai = None

        self.whisk_url = "https://labs.google/fx/tools/whisk"
        self.speech_url = "https://aistudio.google.com/generate-speech"
        self.flow_url = "https://labs.google/fx/tools/flow"
        self.tab = tab

        self.login_gmail = GmailLogin()
        self.image_generator = ImageGenerator()
        self.voice_generator = VoiceGenerator()
        self.video_generator = VideoGenerator(self.flow_url)

    async def execute_work_flow(
            self,
            task: TaskAIImageVoiceCanvaInstagram,
            account_email: AccountEmail,
            manager_image_ai_item_store: list[ManagerImageAIItemStore]
    ):
        self.account_email = account_email
        self.task = task
        self.images_ai = manager_image_ai_item_store

        # Step 1: Generate Image in Whisk
        await self._whisk_generate()

        # TODO: step 2 generate video
        await self._flow_generate()

        # # TODO: step 3 generate voice
        await self._speech_generate()

        # TODO: step 4 upload file to drive
        logger.info("Start upload video to drive...")
        await asyncio_sleep(60)


    async def _whisk_generate(self):
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

    async def _speech_generate(self):
        logger.info("Check in google speech")
        await CheckInSpeech(self.tab, self.speech_url).check_in_generate_tool_speech(self.account_email.email)

        logger.info("Check login gmail if needed...")
        await self._login_gmail(False)

        logger.info("Executing voice generation...")
        await self.voice_generator.execute_voice_generate(
            self.tab,
            self.account_email,
            self.task,
        )
    async def _flow_generate(self):
        await self.tab.get(self.flow_url)
        await asyncio_sleep(5)

        logger.info("Check login gmail if needed...")
        await self._login_gmail(False)

        logger.info("Executing video generation...")
        await self.video_generator.execute_video_generate(
            self.tab,
            self.account_email,
            self.task,
        )

    async def _login_gmail(self, click_success):
        if click_success:
            logger.info("✅ Successfully entered tool - no Gmail login needed")
        else:
            await self.login_gmail.execute_gmail_login(self.tab, self.account_email)
            logger.info(f"✅ Gmail login successful for account: {self.account_email.email}")
