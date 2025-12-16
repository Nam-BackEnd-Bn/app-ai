import os
import uuid
from typing import Optional

import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilActions, UtilDownloadFile


class DownloadAudio:
    def __init__(self, tab, account):
        self.tab = tab
        self.account_email = account

    async def audio_wait_for_generation(self) -> None:
        while True:
            try:
                logger.info("Waiting generating...")
                await UtilActions.getElement(
                    tab=self.tab,
                    parentTag="button",
                    parentAttributes={"type": "button"},
                    rootTag="span",
                    text="Stop",
                    timeout=2,
                )
            except:
                logger.info("✅🎶 Generated voice success 🎶✅")
                break

    async def execute_download_audio(self) -> Optional[str]:
        audio_voice: nd.Element = await UtilActions.getElement(
            tab=self.tab,
            parentTag="div",
            parentAttributes={"class": "speech-prompt-footer-actions"},
            rootTag="audio",
            timeout=10,
        )
        src_audio_base64 = audio_voice.attrs.get("src")  # Base 64
        name_file = f"voice_{uuid.uuid4()}"

        try:
            current_file_path = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file_path)
            dir_store = os.path.join(current_dir, "generated", "voices", self.account_email)

            file_path = await UtilDownloadFile.download(
                self.tab,
                src_audio_base64,
                dir_store,
                name_file,
            )
            logger.info(f"✅ Successfully downloaded: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"❌ Failed to download audio: {e}")
            return None
