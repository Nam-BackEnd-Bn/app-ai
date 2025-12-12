"""Image generation module for AI image creation and downloading."""

import asyncio
from typing import List, TypedDict

import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilActions

from src.enums.ETypeRatioImage import ETypeRatioImage
from src.schemas.accounts import AccountEmail
from src.schemas.manager_image_ai_item_store import ManagerImageAIItemStore
from src.schemas.task_aI_image_voice_canva_instagram import TaskAIImageVoiceCanvaInstagram
from workers.configs.image_genarator_config import ImageGeneratorConstants
from workers.no_drive_services.web_page_services.image_generate.dowload_after_generate import DownloadAfterGenerate
from workers.no_drive_services.web_page_services.image_generate.download_image_local import DownloadImageLocal
from workers.no_drive_services.web_page_services.image_generate.image_click_upload import ImageClickUpload
from workers.no_drive_services.web_page_services.image_generate.image_login import ImageLogin
from workers.no_drive_services.web_page_services.image_generate.image_upload import ImageUpload


class TResultImageGenerate(TypedDict):
    """Type definition for image generation result."""
    typeRatioImage: ETypeRatioImage
    promptImageThumbOutput: str
    promptImagePage1Output: str
    promptImagePage2Output: str
    promptImageNiche3Output: str
    promptImageNiche4Output: str
    promptImageNiche5Output: str


class ImageGenerator:
    """Handles AI image generation and downloading."""

    def __init__(self):
        self.tab = None
        self.temp_download_dir = None
        self.list_image_subject = []
        self.list_image_scene = []
        self.list_image_style = []
        self.image_login = ImageLogin()
        self.download_image_local = DownloadImageLocal(
            temp_download_dir=self.temp_download_dir,
            list_image_subject=self.list_image_subject,
            list_image_scene=self.list_image_scene,
            list_image_style=self.list_image_style
        )
        self.constants = ImageGeneratorConstants()
        self.image_upload = ImageUpload(
            constants=self.constants,
            list_image_subject=self.list_image_subject,
            list_image_scene=self.list_image_scene,
            list_image_style=self.list_image_style,
        )
        self.image_click_upload = ImageClickUpload(
            constants=self.constants,
            list_image_subject=self.list_image_subject,
            list_image_scene=self.list_image_scene,
            list_image_style=self.list_image_style,
        )
        self.download_after_generate = DownloadAfterGenerate(
            constants=self.constants,
        )

    async def execute_image_generate(
            self,
            tab: nd.Tab,
            account_email: AccountEmail,
            task_image: TaskAIImageVoiceCanvaInstagram,
            manager_image_ai_item_store: list[ManagerImageAIItemStore],
    ) -> TResultImageGenerate:
        self.tab = tab

        await self.image_login.execute_image_login(tab)

        # Prepare manager images
        await self.download_image_local.prepare_manager_images(manager_image_ai_item_store)

        # Prepare prompt list
        list_prompt = self._prepare_prompt_list(task_image)

        # Setup generation environment
        count_upload = await self._setup_generate(
            ratio_image=task_image.typeRatioImage,
        )

        # Generate and download images for each prompt
        for idx, prompt in enumerate(list_prompt):
            logger.info(f"Processing prompt {idx + 1}/{len(list_prompt)}")

            await self._generate(tab=tab, prompt=prompt)
            if await self.download_after_generate.download(
                    tab=tab,
                    account_email=account_email.email,
                    current_page=idx,
                    total_inputs=count_upload,
            ):
                await asyncio.sleep(self.constants.SLEEP_AFTER_GENERATION_CHECK)

        result = self._create_result(task_image)

        # Cleanup temporary downloaded images
        self.download_image_local.cleanup_temp_directory()

        return result

    @staticmethod
    def _prepare_prompt_list(task_image: TaskAIImageVoiceCanvaInstagram) -> List[str]:
        """
        Prepare the list of prompts to generate.
        
        Args:
            task_image: Task containing prompts
            
        Returns:
            List of prompt strings
        """
        list_prompt = [
            task_image.promptThumbInput,
            task_image.promptPage1Input,
            task_image.promptPage2Input,
        ]

        # Add niche prompts if they're not URLs
        niche_prompts = [
            task_image.promptNichePage3Input,
            task_image.promptNichePage4Input,
            task_image.promptNichePage5Input,
        ]

        for prompt in niche_prompts:
            if prompt and "http" not in prompt:
                list_prompt.append(prompt)

        return list_prompt

    async def _setup_generate(
            self,
            ratio_image: str,
    ):
        logger.info("🔧 Setting up image generation environment")

        # Click "Add Images" button
        await self.image_click_upload.click_add_images_button(self.tab)

        # Prepare category inputs based on available images per type
        await self.image_click_upload.prepare_category_inputs(self.tab)

        logger.info(f'Sleep for {self.constants.SLEEP_FOR_PREPARE_UPLOAD}s before upload images')
        await asyncio.sleep(self.constants.SLEEP_FOR_PREPARE_UPLOAD)

        # Upload subject, scene, style  images into prepared inputs
        count_upload = await self.image_upload.upload_images(self.tab)

        # Hide images panel
        await self._click_hide_images_button()

        # # Set aspect ratio
        await self._set_aspect_ratio(ratio_image)

        logger.info("✅ Setup completed")

        return count_upload

    async def _click_hide_images_button(self):
        """Click the 'Hide Images' button."""
        logger.info("Clicking 'Hide Images' button")
        await UtilActions.click(
            tab=self.tab,
            parentTag="button",
            rootTag="span",
            text=self.constants.BTN_HIDE_IMAGES,
            timeout=self.constants.DEFAULT_TIMEOUT,
        )

    async def _set_aspect_ratio(self, ratio_image: str):
        """
        Set the aspect ratio for image generation.
        
        Args:
            tab: Browser tab instance
            ratio_image: Desired aspect ratio
        """
        logger.info(f"Setting aspect ratio to: {ratio_image}")

        # Open aspect ratio menu
        await self._click_aspect_ratio_button()

        # Select ratio
        ratio_text = self._get_ratio_text(ratio_image)
        if ratio_text:
            await UtilActions.click(
                tab=self.tab,
                parentTag="button",
                rootTag="span",
                text=ratio_text,
                timeout=self.constants.DEFAULT_TIMEOUT,
            )

        # Close aspect ratio menu
        await self._click_aspect_ratio_button()

    async def _click_aspect_ratio_button(self):
        """Click the aspect ratio button to toggle the menu."""
        await UtilActions.click(
            tab=self.tab,
            parentTag="button",
            rootTag="i",
            text=self.constants.BTN_ASPECT_RATIO_ICON,
            timeout=self.constants.DEFAULT_TIMEOUT,
        )

    def _get_ratio_text(self, ratio_image: str) -> str:
        """
        Get the ratio text for UI selection.
        
        Args:
            ratio_image: Ratio type from enum
            
        Returns:
            Ratio text string
        """
        ratio_map = {
            ETypeRatioImage.SQUARE.value: self.constants.RATIO_SQUARE,
            ETypeRatioImage.VERTICAL.value: self.constants.RATIO_VERTICAL,
            ETypeRatioImage.HORIZONTAL.value: self.constants.RATIO_HORIZONTAL,
        }
        return ratio_map.get(ratio_image, self.constants.RATIO_SQUARE)

    async def _generate(self, tab: nd.Tab, prompt: str):
        """
        Generate an image from a prompt.
        
        Args:
            tab: Browser tab instance
            prompt: Text prompt for image generation
        """
        logger.info(f"🎨 Generating image with prompt: {prompt[:50]}...")

        # Enter prompt
        await UtilActions.sendKey(
            tab=tab,
            rootTag="textarea",
            attributes={"placeholder": self.constants.TEXTAREA_CLASS},
            contentInput=prompt,
            isRemove=True,
            typeSendKey="human",
            timeout=self.constants.DEFAULT_TIMEOUT,
        )
        logger.info("Submitting prompt")
        await UtilActions.click(
            tab=tab,
            rootTag="button",
            attributes={"type": "submit", "aria-label": "Submit prompt"},
            timeout=self.constants.DEFAULT_TIMEOUT,
        )

        # TODO:
        # "Your selection contains more than 3 context images allowed in precise mode."
        # check if this text above show, return task fail with reason above
        # Submit prompt
        await asyncio.sleep(self.constants.SLEEP_AFTER_SUBMIT)

    @staticmethod
    def _create_result(task_image: TaskAIImageVoiceCanvaInstagram) -> TResultImageGenerate:
        return TResultImageGenerate(
            typeRatioImage=task_image.typeRatioImage,
            promptImageThumbOutput=task_image.thumbOutputUrl or "",
            promptImagePage1Output=task_image.page1OutputUrl or "",
            promptImagePage2Output=task_image.page2OutputUrl or "",
            promptImageNiche3Output=task_image.nichePage3OutputUrl or "",
            promptImageNiche4Output=task_image.nichePage4OutputUrl or "",
            promptImageNiche5Output=task_image.nichePage5OutputUrl or "",
        )
