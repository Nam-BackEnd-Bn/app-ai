from asyncio import sleep as asyncio_sleep

import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilActions
from nodrive_gpm_package.utils import UtilDownloadFile


class CreateNewProject:
    def __init__(self, tab):
        self.tab = tab

    async def execute_create_new_project(self):
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
