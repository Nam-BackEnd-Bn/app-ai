import asyncio

import nodriver as nd
from loguru import logger


class ImageLogin:
    def __init__(self):
        pass

    async def execute_image_login(
            self,
            tab: nd.Tab,
    ) -> bool:
        # Import here to avoid multiprocessing import issues on Windows
        from nodrive_gpm_package.utils import UtilActions

        while True:
            try:
                await UtilActions.click(
                    tab=tab,  # Changed parameter name only
                    rootTag="button",
                    text="Continue",
                    timeout=5,
                )
            except:
                break

        try:
            await UtilActions.click(
                tab=tab,  # Changed parameter name only
                rootTag="button",
                text="Get started",
                timeout=5,
            )
        except:
            pass

        try:
            await UtilActions.click(
                tab=tab,  # Changed parameter name only
                rootTag="button",
                attributes={"id": "marketing-emails", "role": "checkbox"},
                timeout=5,
            )
            await UtilActions.click(
                tab=tab,  # Changed parameter name only
                rootTag="button",
                attributes={"id": "research-emails", "role": "checkbox"},
                timeout=10,
            )
            await UtilActions.click(
                tab=tab,  # Changed parameter name only
                rootTag="button",
                text="Next",
                timeDelayAction=2,
                timeout=10,
            )
            await asyncio.sleep(5)
        except:
            pass

        try:
            elmBoxPolicy: nd.Element = await UtilActions.getElement(
                tab=tab,  # Changed parameter name only
                rootTag="div",
                attributes={"class": "iRBQdk"},
                timeout=3,
            )
            # Scroll 200px xuống
            await elmBoxPolicy.apply(
                """
                    (div) => {
                        div.scrollTo({
                            top: div.scrollTop + 200px,
                            behavior: 'smooth'
                        });
                    }
                """
            )

            await tab.evaluate(
                """
                    const policyContainer = document.querySelector('div[class*="iRBQdk"]');
                    if (policyContainer) {
                        policyContainer.scrollTop = policyContainer.scrollHeight;
                    }
                """
            )

            await UtilActions.click(
                tab=tab,  # Changed parameter name only
                rootTag="button",
                text="Continue",
                timeout=10,
            )
        except:
            pass

        logger.info("✅ Image Login success")

        await asyncio.sleep(2)
