"""Image generation module for AI image creation and downloading."""

import asyncio
import os
from typing import Optional

import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilDownloadFile


class DownloadAfterGenerate:
    def __init__(
            self,
            constants,
    ):
        self.constants = constants

    async def download(
            self,
            tab: nd.Tab,
            account_email: str,
            current_page: int,
            total_inputs: int,
    ):
        logger.info(f"📥 Downloading image for page {current_page}")

        # Wait for generation and get image URL
        src_url = await self._wait_for_generation_and_get_url(tab, total_inputs)

        # Determine file name
        file_name = self._get_file_name(current_page)

        # Download the image
        success = await self._download_image(tab, src_url, account_email, file_name)

        return success

    async def _wait_for_generation_and_get_url(self, tab: nd.Tab, total_inputs: int) -> str:
        logger.info("⏳ Waiting for image generation...")
        src_url = None
        for _ in range(self.constants.MAX_GENERATION_CHECK):
            # Check if still generating
            await asyncio.sleep(self.constants.SLEEP_AFTER_GENERATION_CHECK)
            images_generated = await self._is_generating(tab, total_inputs)
            if images_generated is None:
                logger.debug("🧬 Still generating...")
                continue

            # Try to get generated image
            src_url = await self._get_generated_image_url(images_generated)

            if src_url:
                break

        if src_url is None:
            logger.error("❌ Failed to get image URL")
            raise ValueError("Failed to get image URL")

        return src_url

    def _get_file_name(self, current_page: int) -> str:
        file_name_map = {
            0: self.constants.FILE_THUMB,
            1: self.constants.FILE_PAGE_1,
            2: self.constants.FILE_PAGE_2,
            3: self.constants.FILE_NICHE_3,
            4: self.constants.FILE_NICHE_4,
            5: self.constants.FILE_NICHE_5,
        }
        return file_name_map.get(current_page, f"image_page_{current_page}")

    async def _download_image(
            self,
            tab: nd.Tab,
            src_url: str,
            account_email: str,
            file_name: str
    ):
        """
        Download image from URL to disk.

        Args:
            tab: Browser tab instance
            src_url: Image source URL
            account_email: Email for directory organization
            file_name: Name for the downloaded file
        """
        try:
            # Determine storage directory
            current_file_path = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file_path)
            dir_store = os.path.join(current_dir, "generated", "images", account_email)

            # Download file
            file_path = await UtilDownloadFile.download(
                tab, src_url, dir_store, file_name
            )
            logger.info(f"✅ Successfully downloaded: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to download image: {e}")
            return False

    async def _is_generating(self, tab: nd.Tab, total_inputs: int) -> Optional[list[nd.Element]]:
        try:
            div_targets = await tab.query_selector_all("div[id^='DndDescribedBy-']")
            div_target = div_targets[0] if div_targets else None

            root_imgs = await tab.query_selector_all(
                f'div[aria-roledescription="draggable"][aria-describedby="{div_target.attrs.get("id")}"]' if div_target else 'div[aria-roledescription="draggable"]'
            )

            if not root_imgs:
                return None

            imgs = []
            for root_img in root_imgs:
                img = await root_img.query_selector("img")
                if img:
                    imgs.append(img)

            total_images_generated = len(imgs) - total_inputs

            logger.info(f"🔢 Number of images generated: {total_images_generated}")

            if not total_images_generated:
                return None

            return imgs[total_inputs:]
        except Exception:
            return None

    async def _get_generated_image_url(self, images_generated: list[nd.Element]) -> str:
        """
        Get the URL of a generated image.

        Args:
            tab: Browser tab instance

        Returns:
            Image URL or None if not found
        """
        try:
            # img_random: nd.Element = random.choice(images_generated[-2:])
            # Get the last image from the list
            img_random: nd.Element = images_generated[-1]
            src_url = img_random.attrs.get("src")
            logger.info(f"🔢 Selected image src: {src_url}")

            return src_url
        except Exception as e:
            logger.warning(f"Could not get generated image URL: {e}")
            return None
