import os
import uuid
from asyncio import sleep as asyncio_sleep
from typing import Optional

import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilActions
from nodrive_gpm_package.utils import UtilDownloadFile


class DownloadVideo:
    def __init__(self, tab, account):
        self.tab = tab
        self.account_email = account

    async def execute_wait_for_video_to_generate(self):
        logger.info("Waiting for video to generate... (waiting for <video> tag)")
        video_found = False
        while not video_found:
            try:
                video_elem = await UtilActions.getElement(
                    tab=self.tab,
                    rootTag="video",
                    timeout=2,
                )
                if video_elem:
                    logger.info("Video generation complete. <video> element appeared.")
                    video_found = True
                    await asyncio_sleep(2)
                    break
            except Exception as e:
                # Check for failed generation message on the page
                try:
                    fail_text_elem = await UtilActions.getElement(
                        tab=self.tab,
                        rootTag="div",
                        parentTag="div",
                        parentAttributes={"data-testid": "virtuoso-item-list"},
                        text="Failed to generate",
                        timeout=1,
                    )
                    if fail_text_elem:
                        logger.error("❌ Video generation failed: 'Failed to generate' message detected.")
                        break
                except Exception as e2:
                    logger.warning(f"Waiting for <video> element: {e2}")
                    await asyncio_sleep(1)

    async def execute_download_video(self) -> Optional[str]:
        video_elem: nd.Element = await UtilActions.getElement(
            tab=self.tab,
            rootTag="video",
            timeout=10,
        )
        src_video_url = video_elem.attrs.get("src")  # Base 64
        name_file = f"video_{uuid.uuid4()}"

        try:
            current_file_path = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file_path)
            account_dir = self.account_email

            dir_store = os.path.join(current_dir, "generated", "videos", account_dir)

            file_path = await UtilDownloadFile.download(
                self.tab,
                src_video_url,
                dir_store,
                name_file,
            )
            logger.info(f"✅ Successfully downloaded: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"❌ Failed to download video: {e}")
            return None

    @staticmethod
    async def check_download(file_path):
        if file_path:
            logger.info(f"✅ Video Successfully downloaded: {file_path}")
        else:
            logger.error("❌ Failed to download video")
        return file_path
