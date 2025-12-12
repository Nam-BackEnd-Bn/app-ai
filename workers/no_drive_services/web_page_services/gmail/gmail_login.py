import nodriver as nd
from src.schemas.accounts import AccountEmail
from loguru import logger


class GmailLogin:
    def __init__(self):
        pass

    async def execute_gmail_login(
            self,
            tab: nd.Tab,
            account_email: AccountEmail
    ):
        """
        Execute Gmail login flow.
        
        Args:
            tab: Browser tab
            account_email: Account email information
            
        Raises:
            ValueError: If account credentials are invalid
            Exception: If login fails at any step
        """
        # Validate input
        if not account_email.email or not account_email.password:
            raise ValueError("Email and password are required")

        await self._change_param_name(tab=tab)

        # Check if account is already available on the page
        account_clicked = await self._check_and_click_existing_account(tab=tab, account_email=account_email)
        
        # Only input email if account wasn't found/clicked
        if not account_clicked:
            # Input email
            if not await self._input_email(tab=tab, account_email=account_email):
                raise Exception("Failed to input email")

        # Input password (required regardless of whether account was clicked or email was entered)
        if not await self._input_password(tab=tab, account_email=account_email):
            raise Exception("Failed to input password - password may be incorrect")

        # Check if 2FA is required (this may enter 2FA code if detected)
        await self._check_2fa(tab=tab, account_email=account_email)

        await self._try_another_way(tab=tab)
        await self._google_authenticator(tab=tab)

        # Enter 2FA code
        logger.info("Entering 2FA code...")
        await self._enter_code_2FA(tab=tab, account_email=account_email)

    async def _change_param_name(self, tab: nd.Tab):
        """
        Wait for the Gmail login page to load by checking for the 'Forgot email?' button.
        
        This method waits for the page to be ready before proceeding with login.
        """
        # Import here to avoid multiprocessing import issues on Windows
        from nodrive_gpm_package.utils import UtilActions
        try:
            await UtilActions.getElement(
                tab=tab,  # Changed parameter name only
                rootTag="button",
                text="Forgot email?",
                timeout=10,
            )
            logger.info("Page loaded successfully")
        except IndexError as e:
            # Element not found - page might not be loaded or element doesn't exist
            logger.warning(f"Could not find 'Forgot email?' button - page may not be fully loaded: {e}")
            # Continue anyway - the page might still be usable
        except Exception as e:
            logger.warning(f"Unexpected error waiting for page load: {e}")
            # Continue anyway - don't block the login flow

    async def _check_and_click_existing_account(
            self,
            tab: nd.Tab,
            account_email: AccountEmail
    ):
        """
        Check if the account is already available on the "Choose an account" page and click it.
        
        Args:
            tab: Browser tab
            account_email: Account email information
            
        Returns:
            True if account was found and clicked, False otherwise
        """
        logger.info(f"Checking if account {account_email.email} is already available...")
        
        # Import here to avoid multiprocessing import issues on Windows
        from nodrive_gpm_package.utils import UtilActions
        try:
            # Try to find the account by clicking on the parent div with role="link"
            # The email text is in a nested div, so we find the inner div by text and click its parent
            await UtilActions.click(
                tab=tab,
                parentTag="div",
                parentAttributes={
                    "role": "link"
                },
                rootTag="div",
                text=account_email.email,
                timeout=5,
            )
            logger.info(f"Found and clicked existing account: {account_email.email}")
            return True
        except (IndexError, Exception) as e:
            # Account not found on the page - this is normal if it's a fresh login
            logger.debug(f"Account not found on page (will proceed with email input): {e}")
            return False

    async def _input_email(
            self,
            tab: nd.Tab,
            account_email: AccountEmail
    ):
        # Import here to avoid multiprocessing import issues on Windows
        from nodrive_gpm_package.utils import UtilActions
        import asyncio
        
        # Wait for email input field to be available
        logger.info("Waiting for email input field to be available...")
        max_wait_attempts = 5
        for attempt in range(max_wait_attempts):
            try:
                await UtilActions.getElement(
                    tab=tab,
                    rootTag="input",
                    attributes={"type": "email"},
                    timeout=3,
                )
                logger.info("Email input field found")
                break
            except Exception as e:
                if attempt < max_wait_attempts - 1:
                    logger.debug(f"Email input field not found yet (attempt {attempt + 1}/{max_wait_attempts}), waiting...")
                    await asyncio.sleep(1)
                else:
                    logger.warning(f"Email input field not found after {max_wait_attempts} attempts, proceeding anyway...")
        
        # Try multiple strategies to input email
        strategies = [
            # Strategy 1: Standard email input
            {
                "name": "standard email input",
                "sendKey": {
                    "rootTag": "input",
                    "attributes": {"type": "email"},
                    "contentInput": account_email.email,
                    "typeSendKey": "human",
                    "timeDelayAction": 1,
                    "timeout": 10,
                }
            },
            # Strategy 2: Try with id attribute
            {
                "name": "email input by id",
                "sendKey": {
                    "rootTag": "input",
                    "attributes": {"id": "identifierId"},
                    "contentInput": account_email.email,
                    "typeSendKey": "human",
                    "timeDelayAction": 1,
                    "timeout": 10,
                }
            },
            # Strategy 3: Try with name attribute
            {
                "name": "email input by name",
                "sendKey": {
                    "rootTag": "input",
                    "attributes": {"name": "identifier"},
                    "contentInput": account_email.email,
                    "typeSendKey": "human",
                    "timeDelayAction": 1,
                    "timeout": 10,
                }
            },
        ]
        
        for strategy in strategies:
            try:
                logger.info(f"Trying {strategy['name']}...")
                await UtilActions.sendKey(
                    tab=tab,
                    **strategy["sendKey"]
                )
                
                # Wait a bit for the input to be processed
                await asyncio.sleep(1)
                
                # Try to click Next button with multiple strategies
                # Based on HTML: button with id="identifierNext" contains span with text "Tiếp theo" (Vietnamese) or "Next" (English)
                next_clicked = False
                next_strategies = [
                    # Strategy 1: Use button ID (most reliable)
                    {
                        "rootTag": "button",
                        "attributes": {"id": "identifierNext"},
                        "timeout": 5,
                    },
                    # Strategy 2: Use jsname attribute
                    {
                        "rootTag": "button",
                        "attributes": {"jsname": "LgbsSe"},
                        "timeout": 5,
                    },
                    # Strategy 3: Button with span containing "Next" (English)
                    {
                        "parentTag": "button",
                        "rootTag": "span",
                        "text": "Next",
                        "timeout": 5,
                    },
                    # Strategy 4: Button with span containing "Tiếp theo" (Vietnamese)
                    {
                        "parentTag": "button",
                        "rootTag": "span",
                        "text": "Tiếp theo",
                        "timeout": 5,
                    },
                    # Strategy 5: Direct button with "Next" text
                    {
                        "rootTag": "button",
                        "text": "Next",
                        "timeout": 5,
                    },
                    # Strategy 6: Direct button with "Tiếp theo" text
                    {
                        "rootTag": "button",
                        "text": "Tiếp theo",
                        "timeout": 5,
                    },
                    # Strategy 7: Div with role="button" containing "Next"
                    {
                        "rootTag": "div",
                        "attributes": {"role": "button"},
                        "text": "Next",
                        "timeout": 5,
                    },
                    # Strategy 8: Div with role="button" containing "Tiếp theo"
                    {
                        "rootTag": "div",
                        "attributes": {"role": "button"},
                        "text": "Tiếp theo",
                        "timeout": 5,
                    },
                ]
                
                for next_strategy in next_strategies:
                    try:
                        await UtilActions.click(tab=tab, **next_strategy)
                        next_clicked = True
                        logger.info(f"✅ Successfully clicked Next button using {strategy['name']}")
                        break
                    except Exception as e:
                        logger.debug(f"Next button click strategy failed: {e}")
                        continue
                
                if next_clicked:
                    return True
                else:
                    logger.warning(f"Email input succeeded but Next button not found for {strategy['name']}")
                    
            except Exception as e:
                logger.debug(f"Strategy {strategy['name']} failed: {e}")
                continue
        
        # If all strategies failed, try the fallback method
        logger.warning("All email input strategies failed, trying fallback method...")
        try:
            return await self._try_input_email_again(tab=tab, account_email=account_email)
        except Exception as e:
            logger.error(f"Fallback method also failed: {e}")
            return False

    async def _try_input_email_again(
            self,
            tab: nd.Tab,
            account_email: AccountEmail
    ):
        # Import here to avoid multiprocessing import issues on Windows
        from nodrive_gpm_package.utils import UtilActions
        try:
            logger.info("Try input email again...")
            await UtilActions.click(
                tab=tab,  # Keep parameter name as driver to match UtilActions
                rootTag="a",
                attributes={
                    "aria-label": "Try again",
                },
                timeout=5,
            )

            logger.info("Input email again...")
            await UtilActions.sendKey(
                tab=tab,  # Keep parameter name as driver to match UtilActions
                rootTag="input",
                attributes={
                    "type": "email",
                },
                contentInput=account_email.email,
                typeSendKey="human",
                timeDelayAction=2,
            )
            # Try multiple strategies to click Next button (supports both English and Vietnamese)
            next_strategies = [
                {"rootTag": "button", "attributes": {"id": "identifierNext"}, "timeout": 5},
                {"rootTag": "button", "attributes": {"jsname": "LgbsSe"}, "timeout": 5},
                {"parentTag": "button", "rootTag": "span", "text": "Next", "timeout": 5},
                {"parentTag": "button", "rootTag": "span", "text": "Tiếp theo", "timeout": 5},
                {"rootTag": "button", "text": "Next", "timeout": 5},
                {"rootTag": "button", "text": "Tiếp theo", "timeout": 5},
            ]
            next_clicked = False
            for next_strategy in next_strategies:
                try:
                    await UtilActions.click(tab=tab, **next_strategy)
                    next_clicked = True
                    logger.info("✅ Successfully clicked Next button in fallback method")
                    break
                except Exception as e:
                    logger.debug(f"Next button click strategy failed in fallback: {e}")
                    continue
            
            if not next_clicked:
                raise Exception("Could not click Next button in fallback method")
        except Exception as e:
            logger.error(f"Error try input email again: {e}")
            return False
        return True

    async def _input_password(
            self,
            tab: nd.Tab,
            account_email: AccountEmail
    ):
        # Import here to avoid multiprocessing import issues on Windows
        from nodrive_gpm_package.utils import UtilActions
        try:
            logger.info("Input password...")
            await UtilActions.sendKey(
                tab=tab,  # Keep parameter name as driver to match UtilActions
                rootTag="input",
                attributes={
                    "type": "password",
                },
                contentInput=account_email.password,
                typeSendKey="human",
            )
            # Try multiple strategies to click Next button (supports both English and Vietnamese)
            next_strategies = [
                {"rootTag": "button", "attributes": {"id": "identifierNext"}, "timeout": 5},
                {"rootTag": "button", "attributes": {"jsname": "LgbsSe"}, "timeout": 5},
                {"parentTag": "button", "rootTag": "span", "text": "Next", "timeout": 5},
                {"parentTag": "button", "rootTag": "span", "text": "Tiếp theo", "timeout": 5},
                {"rootTag": "button", "text": "Next", "timeout": 5},
                {"rootTag": "button", "text": "Tiếp theo", "timeout": 5},
            ]
            next_clicked = False
            for next_strategy in next_strategies:
                try:
                    await UtilActions.click(tab=tab, **next_strategy)
                    next_clicked = True
                    logger.info("✅ Successfully clicked Next button after password input")
                    break
                except Exception as e:
                    logger.debug(f"Next button click strategy failed after password: {e}")
                    continue
            
            if not next_clicked:
                raise Exception("Could not click Next button after password input")

            isWrongPass = False
            try:
                logger.info("Check password is correct???")
                await UtilActions.getElement(
                    tab=tab,  # Keep parameter name as driver to match UtilActions
                    text="Wrong password",
                    timeout=7,
                )
                isWrongPass = True
            except (IndexError, Exception) as e:
                # Element not found means password was correct
                # IndexError can occur if UtilActions.getElement can't find the element
                logger.debug(f"Password check element not found (password likely correct): {e}")
                return True

            if isWrongPass:
                # TODO: Update status Wrong Password to Database
                logger.error("Password incorrect, please try again")
                return False
        except Exception as e:
            logger.error(f"Error input password: {e}")
            return False
        return True

    async def _try_another_way(
            self,
            tab: nd.Tab,
    ):
        # Import here to avoid multiprocessing import issues on Windows
        from nodrive_gpm_package.utils import UtilActions
        try:
            logger.info("Try another way...")
            await UtilActions.click(
                tab=tab,  # Keep parameter name as driver to match UtilActions
                rootTag="span",
                text="Try another way",
                timeout=5,
                timeDelayAction=2,
                scrollToElement="vertical",
            )
        except Exception as e:
            logger.error(f"Error try another way: {e}")
            return False
        return True

    async def _google_authenticator(
            self,
            tab: nd.Tab,
    ):
        # Import here to avoid multiprocessing import issues on Windows
        from nodrive_gpm_package.utils import UtilActions
        try:
            logger.info("Google Authenticator ...")
            await UtilActions.click(
                tab=tab,  # Keep parameter name as driver to match UtilActions
                parentTag="div",
                rootTag="strong",
                text="Google Authenticator",
                timeDelayAction=3,
                scrollToElement="vertical",
            )
        except Exception as e:
            # Google Authenticator option may not be available, which is fine
            logger.debug(f"Google Authenticator option not available: {e}")

    async def _check_2fa(
            self,
            tab: nd.Tab,
            account_email: AccountEmail
    ):
        """
        Check if 2FA is required and enter code if detected.
        
        Returns:
            True if 2FA was detected and entered successfully
            False if 2FA was not detected (login may have succeeded or different flow)
        """
        # Import here to avoid multiprocessing import issues on Windows
        from nodrive_gpm_package.utils import UtilActions
        try:
            logger.info("Check 2FA...")
            await UtilActions.getElement(
                tab=tab,  # Keep parameter name as driver to match UtilActions
                parentTag="h2",
                rootTag="span",
                text="2-Step Verification",
                timeout=5,
            )
            logger.info("2FA detected, entering code...")
            await self._enter_code_2FA(tab=tab, account_email=account_email)
            return True
        except (IndexError, Exception) as e:
            # 2FA not detected - this is normal if login succeeded without 2FA
            # IndexError can occur if UtilActions.getElement can't find the element
            logger.debug(f"2FA not detected (may have logged in successfully): {e}")
            return False

    async def _enter_code_2FA(
            self,
            tab: nd.Tab,
            account_email: AccountEmail
    ):
        """
        Enter 2FA code with retry logic.
        
        Raises:
            Exception: If 2FA code is incorrect after max attempts
        """
        if not account_email.code2FA:
            raise ValueError("2FA code is required but not provided")

        # Import here to avoid multiprocessing import issues on Windows
        from nodrive_gpm_package.utils import UtilDecode, UtilActions

        countWrong = 0
        maxCountWrong = 2
        maxAttempts = 3  # Maximum total attempts to prevent infinite loop

        attempt = 0
        while attempt < maxAttempts:
            attempt += 1
            code2fa = account_email.code2FA
            logger.info(f"Attempting 2FA code (attempt {attempt}/{maxAttempts})")
            logger.debug(f"code2fa: {code2fa}")

            try:
                code2faDecode = UtilDecode.code2Fa(code2fa)
                logger.debug(f"code2faDecode: {code2faDecode}")
            except Exception as e:
                logger.error(f"Error decoding 2FA code: {e}")
                raise

            # Try multiple strategies to input 2FA code
            # Based on HTML: input with id="totpPin", name="totpPin", type="tel", aria-label="Nhập mã" (Vietnamese) or "Enter code" (English)
            input_strategies = [
                # Strategy 1: Use input ID (most reliable)
                {
                    "rootTag": "input",
                    "attributes": {"id": "totpPin"},
                    "contentInput": code2faDecode,
                    "typeSendKey": "human",
                    "isRemove": True,
                    "timeDelayAction": 2,
                    "timeout": 10,
                },
                # Strategy 2: Use input name
                {
                    "rootTag": "input",
                    "attributes": {"name": "totpPin"},
                    "contentInput": code2faDecode,
                    "typeSendKey": "human",
                    "isRemove": True,
                    "timeDelayAction": 2,
                    "timeout": 10,
                },
                # Strategy 3: Use aria-label in Vietnamese
                {
                    "rootTag": "input",
                    "attributes": {"aria-label": "Nhập mã"},
                    "contentInput": code2faDecode,
                    "typeSendKey": "human",
                    "isRemove": True,
                    "timeDelayAction": 2,
                    "timeout": 10,
                },
                # Strategy 4: Use aria-label in English
                {
                    "rootTag": "input",
                    "attributes": {"aria-label": "Enter code"},
                    "contentInput": code2faDecode,
                    "typeSendKey": "human",
                    "isRemove": True,
                    "timeDelayAction": 2,
                    "timeout": 10,
                },
                # Strategy 5: Use type="tel" with jsname
                {
                    "rootTag": "input",
                    "attributes": {"type": "tel", "jsname": "YPqjbf"},
                    "contentInput": code2faDecode,
                    "typeSendKey": "human",
                    "isRemove": True,
                    "timeDelayAction": 2,
                    "timeout": 10,
                },
                # Strategy 6: Use type="tel" only
                {
                    "rootTag": "input",
                    "attributes": {"type": "tel"},
                    "contentInput": code2faDecode,
                    "typeSendKey": "human",
                    "isRemove": True,
                    "timeDelayAction": 2,
                    "timeout": 10,
                },
            ]
            
            input_success = False
            for input_strategy in input_strategies:
                try:
                    logger.debug(f"Trying 2FA input strategy: {input_strategy.get('attributes', {})}")
                    await UtilActions.sendKey(tab=tab, **input_strategy)
                    input_success = True
                    logger.info("✅ Successfully entered 2FA code")
                    break
                except Exception as e:
                    logger.debug(f"2FA input strategy failed: {e}")
                    continue
            
            if not input_success:
                raise Exception("Could not find 2FA input field with any strategy")

            logger.info("Next")
            # Try multiple strategies to click Next button (supports both English and Vietnamese)
            next_strategies = [
                {"rootTag": "button", "attributes": {"id": "identifierNext"}, "timeout": 5},
                {"rootTag": "button", "attributes": {"jsname": "LgbsSe"}, "timeout": 5},
                {"parentTag": "button", "rootTag": "span", "text": "Next", "timeout": 5},
                {"parentTag": "button", "rootTag": "span", "text": "Tiếp theo", "timeout": 5},
                {"rootTag": "button", "text": "Next", "timeout": 5},
                {"rootTag": "button", "text": "Tiếp theo", "timeout": 5},
            ]
            next_clicked = False
            for next_strategy in next_strategies:
                try:
                    await UtilActions.click(tab=tab, **next_strategy)
                    next_clicked = True
                    logger.info("✅ Successfully clicked Next button after 2FA code")
                    break
                except Exception as e:
                    logger.debug(f"Next button click strategy failed after 2FA: {e}")
                    continue
            
            if not next_clicked:
                raise Exception("Could not click Next button after 2FA code")

            try:
                logger.info("Checking if 2FA code was accepted...")
                # Check for wrong code message in both English and Vietnamese
                wrong_code_found = False
                wrong_code_messages = ["Wrong code", "Mã không đúng", "Sai mã"]  # English, Vietnamese variations
                
                for wrong_msg in wrong_code_messages:
                    try:
                        await UtilActions.getElement(
                            tab=tab,
                            text=wrong_msg,
                            timeout=3,
                            timeDelay=1,
                        )
                        wrong_code_found = True
                        logger.warning(f"Wrong 2FA code message found: {wrong_msg}")
                        break
                    except (IndexError, Exception):
                        continue
                
                if wrong_code_found:
                    countWrong += 1
                    logger.warning(f"Wrong 2FA code entered (attempt {countWrong}/{maxCountWrong})")
                else:
                    # "Wrong code" element not found means code was accepted
                    logger.debug("Wrong code message not found (code likely accepted)")
                    logger.info("2FA code accepted successfully")
                    return True
            except (IndexError, Exception) as e:
                # "Wrong code" element not found means code was accepted
                # IndexError can occur if UtilActions.getElement can't find the element
                logger.debug(f"2FA code check element not found (code likely accepted): {e}")
                logger.info("2FA code accepted successfully")
                return True

            if countWrong >= maxCountWrong:
                # TODO: Update status Wrong 2FA to Database
                # ApiAccountAIInfoImageVoice(master=master).updateStatus(
                #     id=account_email.id, status=EStatusAccountAI.Wrong2FA.value
                # )
                raise Exception(f"2FA incorrect after {maxCountWrong} attempts")

        # If we exit the loop without returning, all attempts failed
        raise Exception(f"Failed to enter correct 2FA code after {maxAttempts} attempts")
