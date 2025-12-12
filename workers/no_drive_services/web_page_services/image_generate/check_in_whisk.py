import asyncio

from loguru import logger


class CheckInWhisk:
    def __init__(self, tab, whisk_url):
        self.tab = tab
        self.whisk_url = whisk_url

    async def check_in_generate_tool_whisk(self) -> bool:
        """
        Check if already inside the tool by attempting to click 'Enter tool' button.

        Returns:
            bool: True if button was clicked successfully (already inside), False otherwise
        """
        await self.tab.get(self.whisk_url)
        import random
        await asyncio.sleep(random.uniform(2.1, 3.1))
        await self.tab.reload()
        await asyncio.sleep(random.uniform(2.1, 3.1))
        await self.tab.reload()
        await asyncio.sleep(random.uniform(2.1, 3.1))

        try:
            # Strategy 1: Try using JavaScript to find and click by text content (most reliable for nested elements)
            logger.info("Attempting to click 'Enter tool' button...")
            try:
                clicked = await self.tab.evaluate("""
                    async () => {
                        const buttons = Array.from(document.querySelectorAll('button'));
                        const button = buttons.find(btn => {
                            const text = (btn.textContent || btn.innerText || '').trim();
                            return text.toLowerCase().includes('enter tool');
                        });
                        if (button) {
                            // Scroll into view
                            button.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            await new Promise(resolve => setTimeout(resolve, 500));

                            // Check if button is visible and enabled
                            const rect = button.getBoundingClientRect();
                            const isVisible = rect.width > 0 && rect.height > 0 && 
                                            window.getComputedStyle(button).display !== 'none' &&
                                            window.getComputedStyle(button).visibility !== 'hidden';

                            if (isVisible && !button.disabled) {
                                button.click();
                                return true;
                            }
                        }
                        return false;
                    }
                """, await_promise=True)

                if clicked:
                    await asyncio.sleep(1)
                    logger.info("✅ Successfully clicked 'Enter tool' button (JavaScript method)")
                    return True
                else:
                    logger.warning("Button found but not clickable or not visible")
            except Exception as e1:
                logger.debug(f"JavaScript click method failed: {e1}")

            # Strategy 2: Try with text matching using UtilActions (contains)
            # Import here to avoid multiprocessing import issues on Windows
            from nodrive_gpm_package.utils import UtilActions
            try:
                await UtilActions.click(
                    tab=self.tab,
                    rootTag="button",
                    text="Enter tool",
                    timeDelayAction=2,
                    timeout=15,
                    scrollToElement="vertical",
                    isContains=True,
                    isGoOnTop=True,
                )
                logger.info("✅ Successfully clicked 'Enter tool' button (UtilActions text match)")
                return True
            except Exception as e2:
                logger.debug(f"UtilActions text match failed: {e2}")

            # Strategy 3: Try with exact text match
            try:
                await UtilActions.click(
                    tab=self.tab,
                    rootTag="button",
                    text="Enter tool",
                    timeDelayAction=2,
                    timeout=15,
                    scrollToElement="vertical",
                    isContains=False,
                    isGoOnTop=True,
                )
                logger.info("✅ Successfully clicked 'Enter tool' button (exact match)")
                return True
            except Exception as e3:
                logger.debug(f"Exact match failed: {e3}")

            # If all strategies fail, log error and return False
            logger.warning("❌ All strategies failed to click 'Enter tool' button - will proceed with Gmail login")
            return False

        except Exception as e:
            logger.error(f"Error clicking 'Enter tool' button: {e}")
            return False
