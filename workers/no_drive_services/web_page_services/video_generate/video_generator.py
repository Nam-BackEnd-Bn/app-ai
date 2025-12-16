import os
import uuid
from asyncio import sleep as asyncio_sleep
from typing import Optional

import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilActions
from nodrive_gpm_package.utils import UtilDownloadFile

from src.schemas.accounts import AccountEmail
from src.schemas.task_aI_image_voice_canva_instagram import TaskAIImageVoiceCanvaInstagram


class VideoGenerator:
    def __init__(self, flow_url: str):
        self.tab = None
        self.task = None
        self.account_email = None
        self.flow_url = flow_url
        # Cache for last generated thumbnail so we can reliably download it
        self._last_thumbnail_src: Optional[str] = None
        self._last_thumbnail_prompt: Optional[str] = None

    async def execute_video_generate(self, tab: nd.Tab, account_email: AccountEmail,
                                     task: TaskAIImageVoiceCanvaInstagram):
        self.tab = tab
        self.account_email = account_email.email
        self.task = task

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
                await self._create_new_project()

                logger.info("Step 2: fll prompt to input")
                await self._fill_prompt_to_input(prompt, type_prompt)

                logger.info(f"Step 3: generate {type_prompt}")
                await self._click_generate_button()

                if type_prompt == "video":
                    logger.info("Step 4: Wait for video to generate")
                    await self._wait_for_video_to_generate()

                    logger.info("Step 5: Download video")
                    file_path = await self._download_video()

                    if file_path:
                        logger.info(f"✅ Successfully downloaded: {file_path}")
                        return file_path
                    else:
                        logger.error("❌ Failed to download video")
                elif type_prompt == "thumbnail":
                    logger.info("Step 4: Wait for thumbnail to generate")
                    await self._wait_for_thumbnail_to_generate(prompt)

                    logger.info("Step 5: Download thumbnail")
                    file_path = await self._download_thumbnail(prompt)

                    if file_path:
                        logger.info(f"✅ Successfully downloaded: {file_path}")
                        return file_path
                    else:
                        logger.error("❌ Failed to download thumbnail")

    async def _download_video(self) -> Optional[str]:
        video_elem: nd.Element = await UtilActions.getElement(
            tab=self.tab,
            rootTag="video",
            timeout=10,
        )
        src_video_url = video_elem.attrs.get("src")  # Base 64
        name_file = f"video_{uuid.uuid4()}"

        try:
            current_file_path = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file_path)
            account_dir = self.account_email

            dir_store = os.path.join(current_dir, "generated", "videos", account_dir)

            file_path = await UtilDownloadFile.download(
                self.tab,
                src_video_url,
                dir_store,
                name_file,
            )
            logger.info(f"✅ Successfully downloaded: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"❌ Failed to download video: {e}")
            return None

    async def _download_thumbnail(self, prompt: str) -> Optional[str]:
        """
        Download the last generated thumbnail.

        Prefer using the cached src from `_wait_for_thumbnail_to_generate` to avoid
        brittle re-querying the DOM by alt text (which may change or disappear).
        """
        src_thumbnail_url = getattr(self, "_last_thumbnail_src", None)

        # Fallback: try to locate the image again by alt text if cache is missing
        if not src_thumbnail_url:
            thumbnail_elems: list[nd.Element] = await UtilActions.getElement(
                tab=self.tab,
                rootTag="img",
                attributes={"alt": f"Flow Image: {prompt}"},
                timeout=10,
            )
            thumbnail_elem = thumbnail_elems[0] if thumbnail_elems else None
            if not thumbnail_elem:
                logger.error(f"❌ No thumbnail element found for prompt: {prompt}")
                return None

            src_thumbnail_url = thumbnail_elem.attrs.get("src")
        name_file = f"thumbnail_{uuid.uuid4()}"
        try:
            current_file_path = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file_path)
            account_dir = self.account_email

            dir_store = os.path.join(current_dir, "generated", "thumbnails", account_dir)

            file_path = await UtilDownloadFile.download(
                self.tab,
                src_thumbnail_url,
                dir_store,
                name_file,
            )
            logger.info(f"✅ Successfully downloaded: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"❌ Failed to download thumbnail: {e}")
            return None

    async def _wait_for_video_to_generate(self):
        logger.info("Waiting for video to generate... (waiting for <video> tag)")
        video_found = False
        while not video_found:
            try:
                video_elem = await UtilActions.getElement(
                    tab=self.tab,
                    rootTag="video",
                    timeout=2,
                )
                if video_elem:
                    logger.info("Video generation complete. <video> element appeared.")
                    video_found = True
                    await asyncio_sleep(2)
                    break
            except Exception as e:
                # Check for failed generation message on the page
                try:
                    fail_text_elem = await UtilActions.getElement(
                        tab=self.tab,
                        rootTag="div",
                        parentTag="div",
                        parentAttributes={"data-testid": "virtuoso-item-list"},
                        text="Failed to generate",
                        timeout=1,
                    )
                    if fail_text_elem:
                        logger.error("❌ Video generation failed: 'Failed to generate' message detected.")
                        break
                except Exception as e2:
                    logger.warning(f"Waiting for <video> element: {e2}")
                    await asyncio_sleep(1)

    async def _wait_for_thumbnail_to_generate(self, prompt: str):
        logger.info("Waiting for thumbnail to generate... (waiting for <img> tag)")
        thumbnail_found = False
        while not thumbnail_found:
            try:
                thumbnail_elem = await UtilActions.getElement(
                    tab=self.tab,
                    rootTag="img",
                    attributes={"alt": f"Flow Image: {prompt}"},
                    timeout=2,
                )
                if thumbnail_elem:
                    logger.info("Thumbnail generation complete. <img> element appeared.")
                    # Cache for later download step
                    try:
                        self._last_thumbnail_src = thumbnail_elem.attrs.get("src")
                        self._last_thumbnail_prompt = prompt
                    except Exception as cache_err:
                        logger.warning(f"Failed to cache thumbnail src: {cache_err}")
                    thumbnail_found = True
                    await asyncio_sleep(2)
                    break
            except Exception as e:
                try:
                    fail_text_elem = await UtilActions.getElement(
                        tab=self.tab,
                        rootTag="div",
                        parentTag="div",
                        parentAttributes={"data-testid": "virtuoso-item-list"},
                        text="Failed to generate",
                        timeout=1,
                    )
                    if fail_text_elem:
                        logger.error("❌ Thumbnail generation failed: 'Failed to generate' message detected.")
                        break
                except Exception as e2:
                    logger.warning(f"Waiting for <img> element: {e2}")
                    await asyncio_sleep(1)

    async def _click_generate_button(self):
        await UtilActions.click(
            tab=self.tab,
            rootTag="button",
            text="arrow_forward",
            timeout=10,
        )
        await asyncio_sleep(2)

    async def _fill_prompt_to_input(self, prompt: str, type_prompt: str):
        if type_prompt == "video":
            await UtilActions.click(
                tab=self.tab,
                rootTag="button",
                parentTag="div",
                parentAttributes={"role": "group"},
                text="videocam",
                timeout=10,
            )
            await asyncio_sleep(1)
            logger.info("Clicked video button")
        elif type_prompt == "thumbnail":
            await UtilActions.click(
                tab=self.tab,
                rootTag="button",
                parentTag="div",
                parentAttributes={"role": "group"},
                text="image",
                timeout=10,
            )
            await asyncio_sleep(1)
            await UtilActions.click(
                tab=self.tab,
                rootTag="button",
                parentTag="div",
                parentAttributes={"role": "group"},
                text="videocam",
                timeout=10,
            )
            await UtilActions.click(
                tab=self.tab,
                rootTag="button",
                parentTag="div",
                parentAttributes={"role": "group"},
                text="image",
                timeout=10,
            )
            logger.info("Clicked thumbnail button")

        logger.info("Filling prompt to input...")
        try:
            await UtilActions.sendKey(
                tab=self.tab,
                rootTag="textarea",
                attributes={'id': 'PINHOLE_TEXT_AREA_ELEMENT_ID'},
                contentInput=prompt,
                typeSendKey="human",
                # typeSendKey="fast",
                # timeDelay=1,
                # timeDelayAction=1,
                timeout=10,
            )
            await asyncio_sleep(2)
        except Exception as e:
            logger.error(f"Error while filling prompt to input: {e}")
            raise

    async def _create_new_project(self):
        """
        Create a new project by clicking the 'Get started' and 'add_x' buttons,
        using UtilActions.click instead of the unavailable query_element.
        """
        # Click "Get started" if the button is visible
        try:
            logger.info("Checking if 'Get started' button is visible...")
            await UtilActions.click(
                tab=self.tab,
                rootTag="button",
                text="Get started",
                timeout=2,
            )
            logger.info("Clicked 'Get started' button")
            await asyncio_sleep(2)
        except Exception as e:
            logger.warning(f"Could not find or click 'Get started' button: {e}")

        logger.info("Creating new project...")
        try:
            # Locate and click the "add_2" button using UtilActions.click
            await UtilActions.click(
                tab=self.tab,
                rootTag="button",
                text="add_2",
                timeout=10,
            )
            await asyncio_sleep(3)
        except Exception as e:
            logger.error(f"Exception while trying to find or click 'add_2' button: {e}")
