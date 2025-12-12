import asyncio
import os
from typing import List

import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilActions


class ImageUpload:
    def __init__(
            self,
            constants,
            list_image_subject,
            list_image_scene,
            list_image_style,
    ):
        self.constants = constants
        self.list_image_subject = list_image_subject
        self.list_image_scene = list_image_scene
        self.list_image_style = list_image_style
        self.total_images = 0
        self.images = []

    async def upload_images(
            self,
            tab: nd.Tab,
    ):
        self.images = self.list_image_subject + self.list_image_scene + self.list_image_style
        self.total_images = len(self.images)

        if not self.total_images:
            logger.warning("⚠️ No subject images available, skipping subject upload")
            return

        input_elements = await self._get_file_input(tab)

        logger.info(f'---- Find {len(input_elements)} inputs to upload images ---')
        logger.info(f"📤 Uploading {self.total_images} images")

        # Upload files one by one
        count_upload = 0
        while count_upload < self.total_images:
            if count_upload >= len(input_elements):
                logger.warning(f"Requested input index {count_upload} out of range (total {len(input_elements)})")
                logger.warning(f"Image file {count_upload}/{self.total_images} uploaded successfully")
                break

            file = self.images[count_upload]
            input_element = input_elements[count_upload]
            await self._send_file(input_element, file, count_upload)
            count_upload += 1
        return count_upload

    async def _send_file(
            self,
            input_element: nd.Element,
            path_file: str,
            count_upload: int,
    ):
        await asyncio.sleep(self.constants.SLEEP_BEFORE_SCROLL)
        await self._scroll_to_section(input_element)

        logger.info(f"📤 Uploading file {count_upload + 1}/{self.total_images}:")
        logger.info(f"{os.path.basename(path_file)}")

        await input_element.send_file(path_file)

        logger.info(f"✅ Image file {count_upload + 1}/{self.total_images} uploaded successfully")
        await asyncio.sleep(self.constants.SLEEP_AFTER_FILE_SEND)

    @staticmethod
    async def _get_file_input(
            tab: nd.Tab,
    ) -> List[nd.Element]:
        """
        Get the file input element for a given section and index.
        Uses section order (Subject -> Scene -> Style) to map to the correct input.
        """
        try:
            inputs: List[nd.Element] = await UtilActions.getElement(
                tab=tab,
                rootTag="input",
                attributes={"type": "file", "accept": "image/*"},
                typeFind="multi",
            )

            if not inputs:
                raise RuntimeError("No file input elements found")

            return inputs
        except Exception as e:
            logger.error(f'Error when get inputs to upload: {e}')
            raise

    async def _scroll_to_section(self, element):
        """
        Scroll to a specific section by title.

        Args:
            tab: Browser tab instance
            section_title: Title of the section to scroll to
        """
        try:
            await element.scroll_into_view()
            await asyncio.sleep(self.constants.SLEEP_BEFORE_SCROLL)
        except Exception as e:
            logger.warning(f"Could not scroll to section: {e}")
