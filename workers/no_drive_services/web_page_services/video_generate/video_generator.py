from asyncio import sleep as asyncio_sleep
from typing import Optional

import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilActions
from nodrive_gpm_package.utils import UtilDownloadFile

from src.models import TaskAIImageVoiceCanvaInstagram
from src.schemas.accounts import AccountEmail
from workers.no_drive_services.web_page_services.video_generate.create_new_project import CreateNewProject
from workers.no_drive_services.web_page_services.video_generate.download_thumb import DownloadThumb
from workers.no_drive_services.web_page_services.video_generate.download_video import DownloadVideo
from workers.no_drive_services.web_page_services.video_generate.fill_prompt import FillPrompt


class VideoGenerator:
    def __init__(self, flow_url: str):
        self.tab = None
        self.task = None
        self.account_email = None
        self.flow_url = flow_url
        # Cache for last generated thumbnail so we can reliably download it
        self._last_thumbnail_src: Optional[str] = None
        self._last_thumbnail_prompt: Optional[str] = None

    async def execute_video_generate(
            self,
            tab: nd.Tab,
            account_email: AccountEmail,
            task: TaskAIImageVoiceCanvaInstagram
    ):
        self.tab = tab
        self.account_email = account_email.email
        self.task = task

        new_project = CreateNewProject(tab)
        fill_prompt = FillPrompt(tab)
        down_thumb = DownloadThumb(tab, self.account_email, self._last_thumbnail_src, self._last_thumbnail_prompt)
        down_video = DownloadVideo(tab, self.account_email)

        prompt_flow_inputs = getattr(self.task, "promptFlowInputs", None)
        if not prompt_flow_inputs:
            logger.warning("No promptFlowInputs found on task; skipping video generation.")
            return None

        for prompts in prompt_flow_inputs:
            # Each `prompts` is a dict mapping type -> prompt text
            for type_prompt, prompt in prompts.items():
                if not prompt:
                    logger.warning(f"No prompt found for {type_prompt}")
                    continue

                await self.tab.get(self.flow_url)

                await asyncio_sleep(5)

                logger.info("Step 1: Create new project")
                await new_project.execute_create_new_project()

                logger.info("Step 2: fll prompt to input")
                await fill_prompt.execute_fill_prompt_to_input(prompt, type_prompt)

                logger.info(f"Step 3: generate {type_prompt}")
                await fill_prompt.click_generate_button()

                if type_prompt == "video":
                    logger.info("Step 4: Wait for video to generate")
                    await down_video.execute_wait_for_video_to_generate()

                    logger.info("Step 5: Download video")
                    file_path = await down_video.execute_download_video()

                    return await down_video.check_download(file_path)

                elif type_prompt == "thumbnail":
                    logger.info("Step 4: Wait for thumbnail to generate")
                    await down_thumb.execute_wait_for_thumbnail_to_generate(prompt)

                    logger.info("Step 5: Download thumbnail")
                    file_path = await down_thumb.execute_download_thumbnail(prompt)

                    return await down_thumb.check_download(file_path)

