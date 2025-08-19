from playwright.async_api import async_playwright
import logging

logger = logging.getLogger(__name__)

async def launch_browser_context(browser_context_config: dict):
    logger.info(f"Launching browser with config: {browser_context_config}")  # Debugging

    playwright = await async_playwright().start()

    mode = browser_context_config.get('mode', 'launch')  # Default to launch

    if mode == 'cdp':
        cdpUrl = browser_context_config.get('cdpUrl', 'http://localhost:9222')

        if not cdpUrl.startswith("http://") and not cdpUrl.startswith("ws://"):
            cdpUrl = f"http://{cdpUrl}"

        logger.info(f"Connecting over CDP to {cdpUrl}")
        browser = await playwright.chromium.connect_over_cdp(cdpUrl)

        if not browser.contexts:
            raise Exception(f"No browser contexts found at {cdpUrl}. Is Chrome running with remote debugging?")

        context = browser.contexts[0]
        return context

    elif mode == 'launch':
        launch_options = browser_context_config.get('launch_options', {})
        # Honor the 'headless' setting if provided at the top level
        if 'headless' in browser_context_config and browser_context_config['headless'] is not None:
            launch_options['headless'] = browser_context_config['headless']
        else:
            launch_options['headless'] = False
        logger.info(f"Launching new Chromium browser with options: {launch_options}")
        browser = await playwright.chromium.launch(**launch_options)
        context_options = browser_context_config.get('context_options', {})
        context = await browser.new_context(**context_options)
        return context

    else:
        raise Exception("🚫 Only 'cdp' and 'launch' modes are supported in the packaged binary. Make sure you are passing --browser-mode cdp or launch and providing browser_context in the HTTP request.")