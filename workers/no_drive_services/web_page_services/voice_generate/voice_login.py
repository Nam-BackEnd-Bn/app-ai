import asyncio

import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilActions


class VoiceLogin:
    def __init__(self):
        self.tab = None

    async def execute_login_google_speech(self, tab: nd.Tab):
        try:
            self.tab = tab
            await self._click_x()
            await self._login_speech()
        except Exception as e:
            logger.error("No confirm show, keep continue")
            print(e)

    async def _click_x(self):
        logger.info("Start Click 'X'")
        await UtilActions.click(
            tab=self.tab,  # Changed parameter name only
            parentTag="button",
            rootTag="span",
            text="close-icon",
            timeout=10,
            isGoOnTop=True,
        )

    async def _login_speech(self):
        await UtilActions.click(
            tab=self.tab,  # Changed parameter name only
            rootTag="input",
            attributes={
                "type": "checkbox",
                "id": "mat-mdc-checkbox-0-input",
            },
            timeout=10,
            isGoOnTop=True,
        )
        await UtilActions.click(
            tab=self.tab,  # Changed parameter name only
            rootTag="input",
            attributes={
                "type": "checkbox",
                "id": "mat-mdc-checkbox-1-input",
            },
            timeout=10,
            isGoOnTop=True,
        )
        await UtilActions.click(
            tab=self.tab,  # Changed parameter name only
            parentTag="button",
            rootTag="span",
            text="I accept",
            timeDelayAction=2,
            timeout=10,
            isGoOnTop=True,
        )
        await asyncio.sleep(10)

    logger.info("👤👤👤 Login Google Speech Success 👤👤👤")
