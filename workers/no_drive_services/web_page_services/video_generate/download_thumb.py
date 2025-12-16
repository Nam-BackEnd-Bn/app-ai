import os
import uuid
from asyncio import sleep as asyncio_sleep
from typing import Optional

import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilActions
from nodrive_gpm_package.utils import UtilDownloadFile


class DownloadThumb:
    def __init__(self, tab, account, src, prompt):
        self.tab = tab
        self.account_email = account
        self._last_thumbnail_src = src
        self._last_thumbnail_prompt = prompt

    async def execute_wait_for_thumbnail_to_generate(self, prompt: str):
        logger.info("Waiting for thumbnail to generate... (waiting for <img> tag)")
        thumbnail_found = False
        while not thumbnail_found:
            try:
                thumbnail_elem = await UtilActions.getElement(
                    tab=self.tab,
                    rootTag="img",
                    attributes={"alt": f"Flow Image: {prompt}"},
                    timeout=2,
                )
                if thumbnail_elem:
                    logger.info("Thumbnail generation complete. <img> element appeared.")
                    # Cache for later download step
                    try:
                        self._last_thumbnail_src = thumbnail_elem.attrs.get("src")
                        self._last_thumbnail_prompt = prompt
                    except Exception as cache_err:
                        logger.warning(f"Failed to cache thumbnail src: {cache_err}")
                    thumbnail_found = True
                    await asyncio_sleep(2)
                    break
            except Exception as e:
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
                        logger.error("❌ Thumbnail generation failed: 'Failed to generate' message detected.")
                        break
                except Exception as e2:
                    logger.warning(f"Waiting for <img> element: {e2}")
                    await asyncio_sleep(1)

    async def execute_download_thumbnail(self, prompt: str) -> Optional[str]:
        src_thumbnail_url = getattr(self, "_last_thumbnail_src", None)

        # Fallback: try to locate the image again by alt text if cache is missing
        if not src_thumbnail_url:
            thumbnail_elems: list[nd.Element] = await UtilActions.getElement(
                tab=self.tab,
                rootTag="img",
                attributes={"alt": f"Flow Image: {prompt}"},
                timeout=10,
            )
            thumbnail_elem = thumbnail_elems[0] if thumbnail_elems else None
            if not thumbnail_elem:
                logger.error(f"❌ No thumbnail element found for prompt: {prompt}")
                return None

            src_thumbnail_url = thumbnail_elem.attrs.get("src")

        name_file = f"thumbnail_{uuid.uuid4()}"

        try:
            current_file_path = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file_path)
            account_dir = self.account_email

            dir_store = os.path.join(current_dir, "generated", "thumbnails", account_dir)

            file_path = await UtilDownloadFile.download(
                self.tab,
                src_thumbnail_url,
                dir_store,
                name_file,
            )
            logger.info(f"✅ Successfully downloaded: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"❌ Failed to download thumbnail: {e}")
            return None

    async def check_download(self, file_path):
        if file_path:
            logger.info(f"✅ Thumbnail Successfully downloaded: {file_path}")
            return file_path
        else:
            logger.error("❌ Failed to download thumbnail")
