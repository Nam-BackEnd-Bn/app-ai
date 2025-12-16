import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilActions, UtilDownloadFile


class SubmitPrompt:
    def __init__(self, tab):
        self.tab = tab

    async def audio_send_prompt(self, prompt: str) -> None:
        logger.info("Send prompt")
        await UtilActions.sendKey(
            tab=self.tab,
            rootTag="textarea",
            attributes={"class": "multi-speaker-raw-prompt"},
            contentInput=prompt,
            typeSendKey="fast",
            timeout=10,
            splitKeyword="Speaker",
        )

    async def execute_submit_generation(self) -> None:
        logger.info("Click 'Submit'")
        await UtilActions.click(
            tab=self.tab,
            parentTag="button",
            parentAttributes={"aria-label": "Run", "type": "submit"},
            rootTag="span",
            text="Run",
            timeout=10,
        )
