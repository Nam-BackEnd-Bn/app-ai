import asyncio
from typing import List

import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilActions


class ImageClickUpload:
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

    async def click_add_images_button(self, tab: nd.Tab):
        """Click the 'Add Images' button and wait for panel to open."""
        logger.info("Clicking 'Add Images' button")
        await UtilActions.click(
            tab=tab,
            parentTag="button",
            rootTag="span",
            text=self.constants.BTN_ADD_IMAGES,
            timeout=self.constants.CLICK_TIMEOUT,
        )
        # Wait for the panel to open and file inputs to be available
        await asyncio.sleep(1.0)
        logger.debug("Add Images panel should be open now")

    async def prepare_category_inputs(self, tab: nd.Tab) -> int:
        """
        Click the 'Add new category' button for each section (Subject, Scene, Style)
        based on the number of images available for that section.
        Returns the total number of category inputs (Subject + Scene + Style).
        """
        try:
            logger.debug("Preparing category inputs for Subject/Scene/Style")
            list_btn_add_input: List[nd.Element] = await UtilActions.getElement(
                tab=tab,
                rootTag="button",
                attributes={"aria-label": "Add new category"},
                typeFind="multi",
            )

            if not list_btn_add_input:
                logger.warning("⚠️ No 'Add new category' buttons found")
                return 0

            category_counts = [
                (self.constants.TITLE_SUBJECT, len(self.list_image_subject)),
                (self.constants.TITLE_SCENE, len(self.list_image_scene)),
                (self.constants.TITLE_STYLE, len(self.list_image_style)),
            ]

            for idx, (title, count) in enumerate(category_counts):
                logger.debug(f"Section '{title}' has {count} image(s)")
                extra_inputs = max(count - 1, 0)
                if extra_inputs == 0:
                    logger.debug(f"No extra inputs needed for '{title}'")
                    continue

                if idx >= len(list_btn_add_input):
                    logger.warning(f"⚠️ Missing 'Add new category' button for section: {title}")
                    continue

                btn_add_input: nd.Element = list_btn_add_input[idx]
                logger.debug(f"Using add-category button index {idx} for '{title}'")
                await btn_add_input.scroll_into_view()
                await asyncio.sleep(self.constants.SLEEP_BEFORE_SCROLL)

                for _ in range(extra_inputs):
                    logger.debug(f"Clicking add-category for '{title}' (remaining: {extra_inputs})")
                    await btn_add_input.mouse_click()
                    await asyncio.sleep(self.constants.SLEEP_BEFORE_SCROLL)
                    logger.debug(f"Added new category input for {title}")
        except Exception as e:
            logger.error(f"Error preparing category inputs: {e}")

