import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
from loguru import logger

from src.enums.EFolderImageAI import EFolderImageAI
from src.schemas.manager_image_ai_item_store import ManagerImageAIItemStore


class DownloadImageLocal:
    def __init__(
            self,
            temp_download_dir: Optional[str] = None,
            list_image_subject: list[str] = None,
            list_image_scene: list[str] = None,
            list_image_style: list[str] = None,
    ):
        self._temp_download_dir = temp_download_dir
        self.list_image_subject = list_image_subject
        self.list_image_scene = list_image_scene
        self.list_image_style = list_image_style

    async def prepare_manager_images(
            self,
            manager_image_ai_item_store: list[ManagerImageAIItemStore]
    ):
        self._temp_download_dir = tempfile.mkdtemp(prefix="whisk_images_")
        logger.info(f"Created temporary directory for images: {self._temp_download_dir}")

        for manager_image_ai_item in manager_image_ai_item_store:
            try:
                local_path = await self._download_image_to_local(
                    manager_image_ai_item.file,
                    manager_image_ai_item.typeFolderStore
                )

                if local_path:
                    if manager_image_ai_item.typeFolderStore == EFolderImageAI.SUBJECT:
                        self.list_image_subject.append(local_path)
                    elif manager_image_ai_item.typeFolderStore == EFolderImageAI.SCENE:
                        self.list_image_scene.append(local_path)
                    elif manager_image_ai_item.typeFolderStore == EFolderImageAI.STYLE:
                        self.list_image_style.append(local_path)

            except Exception as e:
                logger.warning(f"Failed to download image {manager_image_ai_item.file}: {e}")

    async def _download_image_to_local(self, file_path_or_url: str, folder_type: EFolderImageAI) -> Optional[str]:
        """
        Download an image from URL or copy from local path to temporary directory.
        
        Args:
            file_path_or_url: URL or local file path
            folder_type: Type of folder (SUBJECT, SCENE, STYLE)
            
        Returns:
            Local file path if successful, None otherwise
        """
        try:
            # Check if it's a URL or local path
            parsed = urlparse(file_path_or_url)
            is_url = parsed.scheme in ('http', 'https')

            if is_url:
                # Download from URL using requests
                response = requests.get(file_path_or_url, stream=True, timeout=30)
                if response.status_code == 200:
                    # Get file extension from content type or URL
                    content_type = response.headers.get('Content-Type', '')
                    ext = '.jpg'  # default
                    if 'image/png' in content_type:
                        ext = '.png'
                    elif 'image/jpeg' in content_type or 'image/jpg' in content_type:
                        ext = '.jpg'
                    elif 'image/gif' in content_type:
                        ext = '.gif'
                    elif 'image/webp' in content_type:
                        ext = '.webp'
                    else:
                        # Try to get from URL
                        path = Path(parsed.path)
                        if path.suffix:
                            ext = path.suffix

                    # Generate unique filename
                    file_hash = hashlib.md5(file_path_or_url.encode()).hexdigest()[:8]
                    filename = f"{folder_type.value}_{file_hash}{ext}"
                    local_path = os.path.join(self._temp_download_dir, filename)

                    # Save file
                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                    logger.info(f"✅ Downloaded image from URL to: {local_path}")
                    return local_path
                else:
                    logger.warning(f"Failed to download image: HTTP {response.status_code}")
                    return None
            else:
                # It's a local path - check if file exists
                if os.path.exists(file_path_or_url) and os.path.isfile(file_path_or_url):
                    # Copy to temp directory
                    file_hash = hashlib.md5(file_path_or_url.encode()).hexdigest()[:8]
                    ext = Path(file_path_or_url).suffix or '.jpg'
                    filename = f"{folder_type.value}_{file_hash}{ext}"
                    local_path = os.path.join(self._temp_download_dir, filename)

                    shutil.copy2(file_path_or_url, local_path)
                    logger.debug(f"Copied local image to: {local_path}")
                    return local_path
                else:
                    logger.warning(f"Local file not found: {file_path_or_url}")
                    return None

        except Exception as e:
            logger.error(f"Error downloading image {file_path_or_url}: {e}")
            return None

    def cleanup_temp_directory(self):
        """Clean up temporary directory with downloaded images."""
        if self._temp_download_dir and os.path.exists(self._temp_download_dir):
            try:
                shutil.rmtree(self._temp_download_dir)
                logger.debug(f"Cleaned up temporary directory: {self._temp_download_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {e}")
