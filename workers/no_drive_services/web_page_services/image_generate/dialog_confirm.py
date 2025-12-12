"""Dialog confirmation handler for upload dialogs."""

import asyncio
import nodriver as nd
from loguru import logger
from nodrive_gpm_package.utils import UtilActions


class DialogConfirm:
    """Handles confirmation dialogs that appear during image uploads."""
    
    def __init__(self):
        pass

    async def handle_upload_dialog(self, tab: nd.Tab):
        max_retries = 5
        retry_delay = 0.8

        for attempt in range(max_retries):
            try:
                # Wait for dialog to appear
                await asyncio.sleep(retry_delay)

                # Use JavaScript to find and click the button directly
                clicked = await tab.evaluate("""
                    () => {
                        // Look for dialog with role="dialog" and data-state="open"
                        const dialogs = Array.from(document.querySelectorAll('div[role="dialog"][data-state="open"]'));

                        for (const dialog of dialogs) {
                            // Check if dialog is visible
                            const style = window.getComputedStyle(dialog);
                            if (style.display === 'none' || style.visibility === 'hidden') {
                                continue;
                            }

                            // Find "I agree" button - try multiple ways
                            let agreeButton = null;

                            // Method 1: Find by text content
                            const buttons = Array.from(dialog.querySelectorAll('button'));
                            agreeButton = buttons.find(btn => {
                                const text = (btn.textContent || btn.innerText || '').trim();
                                return text.toLowerCase() === 'i agree';
                            });

                            // Method 2: If not found, try finding button that's not Cancel
                            if (!agreeButton) {
                                agreeButton = buttons.find(btn => {
                                    const text = (btn.textContent || btn.innerText || '').trim().toLowerCase();
                                    return text !== 'cancel' && text.length > 0;
                                });
                            }

                            if (agreeButton) {
                                // Check if button is visible and enabled
                                const btnStyle = window.getComputedStyle(agreeButton);
                                if (btnStyle.display === 'none' || btnStyle.visibility === 'hidden' || agreeButton.disabled) {
                                    continue;
                                }

                                // Scroll into view
                                agreeButton.scrollIntoView({ behavior: 'instant', block: 'center' });

                                // Try multiple click methods
                                try {
                                    // Method 1: Direct click
                                    agreeButton.click();
                                    return true;
                                } catch (e1) {
                                    try {
                                        // Method 2: MouseEvent
                                        const mouseEvent = new MouseEvent('click', {
                                            view: window,
                                            bubbles: true,
                                            cancelable: true,
                                            buttons: 1
                                        });
                                        agreeButton.dispatchEvent(mouseEvent);
                                        return true;
                                    } catch (e2) {
                                        try {
                                            // Method 3: Focus and Enter key
                                            agreeButton.focus();
                                            const keyEvent = new KeyboardEvent('keydown', {
                                                key: 'Enter',
                                                code: 'Enter',
                                                keyCode: 13,
                                                bubbles: true
                                            });
                                            agreeButton.dispatchEvent(keyEvent);
                                            const keyUpEvent = new KeyboardEvent('keyup', {
                                                key: 'Enter',
                                                code: 'Enter',
                                                keyCode: 13,
                                                bubbles: true
                                            });
                                            agreeButton.dispatchEvent(keyUpEvent);
                                            return true;
                                        } catch (e3) {
                                            console.error('All click methods failed:', e1, e2, e3);
                                            return false;
                                        }
                                    }
                                }
                            }
                        }
                        return false;
                    }
                """, await_promise=True)

                if clicked:
                    logger.info("✅ Clicked 'I agree' button")
                    # Wait for dialog to close
                    await asyncio.sleep(0.5)

                    # Verify dialog is closed
                    dialog_closed = await tab.evaluate("""
                        () => {
                            const dialogs = Array.from(document.querySelectorAll('div[role="dialog"]'));
                            for (const dialog of dialogs) {
                                const dataState = dialog.getAttribute('data-state');
                                const style = window.getComputedStyle(dialog);
                                // Check if dialog is closed or hidden
                                if (dataState === 'open' && 
                                    style.display !== 'none' && 
                                    style.visibility !== 'hidden') {
                                    return false;
                                }
                            }
                            return true;
                        }
                    """, await_promise=True)

                    if dialog_closed:
                        logger.info("✅ Dialog closed successfully")
                        return
                    else:
                        logger.warning("⚠️ Dialog may still be open, but continuing...")
                        return
                else:
                    # Try using UtilActions as fallback
                    if attempt == 0:
                        try:
                            await UtilActions.click(
                                tab=tab,
                                rootTag="button",
                                text="I agree",
                                timeout=3,
                                isContains=False,
                            )
                            await asyncio.sleep(0.5)
                            logger.info("✅ Clicked 'I agree' button using UtilActions")
                            return
                        except Exception as e:
                            logger.debug(f"UtilActions also failed: {e}")

                    if attempt < max_retries - 1:
                        logger.debug(f"Dialog not found or button not clickable (attempt {attempt + 1}/{max_retries})")

            except Exception as e:
                logger.warning(f"Error handling upload dialog (attempt {attempt + 1}/{max_retries}): {e}")

            # Wait before retry
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)

        logger.warning("⚠️ Could not click 'I agree' button after all retries, continuing anyway...")
