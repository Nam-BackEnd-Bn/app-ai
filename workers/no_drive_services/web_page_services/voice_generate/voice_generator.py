import asyncio
import os
import random
import uuid
from typing import TypedDict, List, Optional

import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilActions, UtilDownloadFile
from pydantic import BaseModel

from src.schemas.accounts import AccountEmail
from src.schemas.task_aI_image_voice_canva_instagram import TaskAIImageVoiceCanvaInstagram
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
        list_voice_character = "Zephyr, Puck, Charon, Kore, Fenrir, Leda, Orus, Aoede, Callirrhoe, Autonoe, Enceladus, Iapetus, Umbriel, Algieba, Despina, Erinome, Algenib, Rasalgethi, Laomedeia, Achernar, Alnilam, Schedar, Gacrux, Pulcherrima, Achird, Zubenelgenubi, Vindemiatrix, Sadachbia, Sadaltager, Sulafat"
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
        for data_gen in list_data_prompt:
            logger.info(f"Step 1: Open run settings")
            await self._open_run_settings()
            logger.info(f"Step 2: Select model")
            # await self._select_model()
            logger.info(f"Step 3: Enable multi-speaker audio")
            await self._enable_multi_speaker_audio()
            logger.info(f"Step 4: Set temperature")
            await self._set_temperature()
            logger.info(f"Step 5: Select voice character")
            await self._select_voice_character(data_gen.character)
            logger.info(f"Step 6: Close settings panel")
            await self._close_settings_panel()
            logger.info(f"Step 7: Send prompt")
            await self._send_prompt(data_gen.prompt)
            logger.info(f"Step 8: Submit generation")
            await self._submit_generation()
            logger.info(f"Step 9: Wait for generation")
            await self._wait_for_generation()
            logger.info(f"Step 10: Download audio")
            await self._download_audio()
            logger.info(f"Step 11: Download audio success")
        return None

    async def _open_run_settings(self) -> None:
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

    async def _enable_multi_speaker_audio(self) -> None:
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

    async def _set_temperature(self) -> None:
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


    async def _select_voice_character(self, character: str) -> None:
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

    async def _close_settings_panel(self) -> None:
        logger.info("Click 'X'")
        await UtilActions.click(
            tab=self.tab,
            rootTag="button",
            attributes={"aria-label": "Close run settings panel"},
            timeout=10,
        )

    async def _send_prompt(self, prompt: str) -> None:
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

    async def _submit_generation(self) -> None:
        logger.info("Click 'Submit'")
        await UtilActions.click(
            tab=self.tab,
            parentTag="button",
            parentAttributes={"aria-label": "Run", "type": "submit"},
            rootTag="span",
            text="Run",
            timeout=10,
        )

    async def _wait_for_generation(self) -> None:
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

    async def _download_audio(self) -> Optional[str]:
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
