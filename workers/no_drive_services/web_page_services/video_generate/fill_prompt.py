from asyncio import sleep as asyncio_sleep

import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilActions
from nodrive_gpm_package.utils import UtilDownloadFile


class FillPrompt:
    def __init__(self, tab):
        self.tab = tab

    async def execute_fill_prompt_to_input(self, prompt: str, type_prompt: str):
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

    async def click_generate_button(self):
        await UtilActions.click(
            tab=self.tab,
            rootTag="button",
            text="arrow_forward",
            timeout=10,
        )
        await asyncio_sleep(2)
