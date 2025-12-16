import random
from typing import TypedDict, List, Optional

import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilActions, UtilDownloadFile
from pydantic import BaseModel

from src.schemas.accounts import AccountEmail
from src.schemas.task_aI_image_voice_canva_instagram import TaskAIImageVoiceCanvaInstagram
from workers.no_drive_services.web_page_services.voice_generate.download_audio import DownloadAudio
from workers.no_drive_services.web_page_services.voice_generate.setup_voice import SetupVoice
from workers.no_drive_services.web_page_services.voice_generate.submit_prompt import SubmitPrompt
from workers.no_drive_services.web_page_services.voice_generate.voice_login import VoiceLogin


class TData(TypedDict):
    promptVoicePage1: str
    promptVoicePage3456: str
    characterVoice1: str
    characterVoice2: str


class TResultDataImage(TypedDict):
    promptVoicePage1Output: str
    promptVoicePage345Output: str


class TDataGen(BaseModel):
    prompt: str
    character: str


list_voice_character = "Zephyr, Puck, Charon, Kore, Fenrir, Leda, Orus, Aoede, Callirrhoe, Autonoe, Enceladus, Iapetus, Umbriel, Algieba, Despina, Erinome, Algenib, Rasalgethi, Laomedeia, Achernar, Alnilam, Schedar, Gacrux, Pulcherrima, Achird, Zubenelgenubi, Vindemiatrix, Sadachbia, Sadaltager, Sulafat"


class VoiceGenerator:
    def __init__(self):
        self.tab = None
        self.task_voice = None
        self.account_email = None
        self.voice_login = VoiceLogin()

    async def execute_voice_generate(
            self,
            tab: nd.Tab,
            account_email: AccountEmail,
            task_voice: TaskAIImageVoiceCanvaInstagram,
    ) -> Optional[str]:
        self.tab = tab
        self.task_voice = task_voice
        self.account_email = account_email.email

        await self.voice_login.execute_login_google_speech(tab)

        list_data_prompt = await self._get_prompt()

        return await self._generate(list_data_prompt)

    async def _get_prompt(self) -> List[TDataGen]:
        voice_characters = list_voice_character.split(",")
        character = random.choice(voice_characters).strip()

        return [
            TDataGen(
                prompt=self.task_voice.promptVoicePage1Input,
                character=character
            ),
            TDataGen(
                prompt=self.task_voice.promptVoicePage3456Input,
                character=character
            ),
        ]

    async def _generate(
            self,
            list_data_prompt: List[TDataGen],
    ) -> Optional[str]:
        setup = SetupVoice(self.tab, self.account_email)
        submit = SubmitPrompt(self.tab)
        download = DownloadAudio(self.tab, self.account_email)

        for data_gen in list_data_prompt:
            logger.info(f"Step 1: Open run settings")
            await setup.set_open_run_settings()

            logger.info(f"Step 2: Select model")
            # await self._select_model()

            logger.info(f"Step 3: Enable multi-speaker audio")
            await setup.set_enable_multi_speaker_audio()

            logger.info(f"Step 4: Set temperature")
            await setup.set_temperature()

            logger.info(f"Step 5: Select voice character")
            await setup.set_select_voice_character(data_gen.character)

            logger.info(f"Step 6: Close settings panel")
            await setup.set_close_settings_panel()

            logger.info(f"Step 7: Send prompt")
            await submit.audio_send_prompt(data_gen.prompt)

            logger.info(f"Step 8: Submit generation")
            await submit.execute_submit_generation()

            logger.info(f"Step 9: Wait for generation")
            await download.audio_wait_for_generation()

            logger.info(f"Step 10: Download audio")
            await download.execute_download_audio()

            logger.info(f"Step 11: Download audio success")
        return None

    async def _select_model(self) -> None:
        logger.info("Click 'Select model'")
        await UtilActions.click(
            tab=self.tab,
            rootTag="div",
            attributes={"class": "settings-model-selector"},
            timeout=10,
        )

        logger.info("Click 'Gemini 2.5 Flash Preview TTS'")
        await UtilActions.click(
            tab=self.tab,
            rootTag="span",
            attributes={"class": "model-name"},
            text="Gemini 2.5 Flash Preview TTS",
            timeout=10,
        )
