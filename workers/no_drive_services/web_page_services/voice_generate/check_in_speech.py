import asyncio
import random

from loguru import logger
from nodrive_gpm_package.utils import UtilActions


class CheckInSpeech:
    def __init__(self, tab, speech_url):
        self.tab = tab
        self.speech_url = speech_url

    async def check_in_generate_tool_speech(self, email_text: str) -> bool:
        await self.tab.get(self.speech_url)
        await asyncio.sleep(random.uniform(2.1, 3.1))
        try:
            logger.info("Start Click 'X' in Google Speech")
            await UtilActions.click(
                tab=self.tab,  # Changed parameter name only
                parentTag="button",
                rootTag="span",
                text="close-icon",
                timeout=10,
            )
        except Exception as e:
            logger.error(e)
            logger.info("Click 'X' in Google Speech timeout, continue action")
