import asyncio
import random
from typing import List

import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilActions, UtilDownloadFile


class SetupVoice:
    def __init__(self, tab, account):
        self.tab = tab
        self.account_email = account

    async def set_open_run_settings(self) -> None:
        try:
            await UtilActions.getElement(
                tab=self.tab,
                rootTag="h2",
                text="Run settings",
                timeout=3,
            )
        except:
            await asyncio.sleep(1)
            run_settings: nd.Element = await UtilActions.getElement(
                tab=self.tab,
                rootTag="button",
                attributes={"aria-label": "Toggle run settings panel"},
                timeout=3,
            )
            await run_settings.click()
            await asyncio.sleep(1)

            await UtilActions.getElement(
                tab=self.tab,
                rootTag="h2",
                text="Run settings",
                timeout=3,
            )

    async def set_enable_multi_speaker_audio(self) -> None:
        try:
            logger.info("Click 'Multi-speaker audio'")
            await UtilActions.click(
                tab=self.tab,
                rootTag="div",
                text="Multi-speaker audio",
                timeout=5,
            )
        except:
            pass

    async def set_temperature(self) -> None:
        logger.info("Set 'Temperature'")
        try:
            await UtilActions.getElement(
                tab=self.tab,
                rootTag="h3",
                text="Temperature",
                timeout=1,
            )

            # Find the input[type="number"] in element with data-test-id="temperatureSliderContainer"
            await UtilActions.sendKey(
                tab=self.tab,
                rootTag="input",
                parentAttributes={"data-test-id": "temperatureSliderContainer"},
                attributes={"type": "number"},
                contentInput=str(random.randint(1, 2)),
                timeout=10,
            )

        except:
            await UtilActions.click(
                tab=self.tab,
                rootTag="h3",
                text="Model settings",
                timeout=10,
            )

            await UtilActions.sendKey(
                tab=self.tab,
                rootTag="input",
                parentAttributes={"data-test-id": "temperatureSliderContainer"},
                attributes={"type": "number"},
                contentInput=str(random.randint(1, 2)),
                timeout=10,
            )

    async def set_select_voice_character(self, character: str) -> None:
        list_selected_voice: List[nd.Element] = await UtilActions.getElement(
            tab=self.tab,
            rootTag="ms-voice-selector",
            typeFind="multi",
            timeout=10,
        )

        for idx, selected_voice in enumerate(list_selected_voice):
            await selected_voice.scroll_into_view()

            await UtilActions.getElement(
                tab=self.tab,
                parentAttributes={"id": f"cdk-accordion-child-{idx}"},
                rootTag="input",
                attributes={"type": "text"},
                timeout=10,
            )

            await UtilActions.clickOnElement(
                tab=self.tab,
                elm=selected_voice,
                timeDelayAction=1,
            )

            await UtilActions.click(
                tab=self.tab,
                parentTag="span",
                parentAttributes={"class": "mdc-list-item__primary-text"},
                rootTag="div",
                text=character,
                timeout=10,
                scrollToElement="vertical",
                timeDelay=1,
                timeDelayAction=1,
            )

    async def set_close_settings_panel(self) -> None:
        logger.info("Click 'X'")
        await UtilActions.click(
            tab=self.tab,
            rootTag="button",
            attributes={"aria-label": "Close run settings panel"},
            timeout=10,
        )
