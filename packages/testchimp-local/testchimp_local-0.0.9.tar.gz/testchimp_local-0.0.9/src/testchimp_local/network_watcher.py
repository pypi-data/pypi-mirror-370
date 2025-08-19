import asyncio
import time
import random
import re
from collections import deque
from typing import Deque, List, Optional, Pattern
from playwright.async_api import BrowserContext, Page, Response
from .datas import RequestResponsePair
from.network_utils import clean_request_response_pair
import logging

logger = logging.getLogger(__name__)

class NetworkWatcher:
    def __init__(
        self,
        context: BrowserContext,
        urlRegexToCapture: Optional[str] = None,
        samplingRate: float = 0.2  # 1.0 = log all, 0.1 = log 10%
    ):
        self.context = context
        self.samplingRate = samplingRate
        self.url_pattern: Optional[Pattern] = re.compile(urlRegexToCapture, re.IGNORECASE) if urlRegexToCapture else None
        self.network_logs: Deque[RequestResponsePair] = deque(maxlen=100)

    async def start(self):
        for page in self.context.pages:
            await self._attach_to_page(page)

        def on_new_page(page: Page):
            asyncio.create_task(self._attach_to_page(page))

        self.context.on("page", on_new_page)

    async def _attach_to_page(self, page: Page):
        logger.info("Attaching network listener to new page")

        async def on_response(response: Response):
            try:
                url = response.url

                # Filter using regex if provided
                if self.url_pattern and not self.url_pattern.search(url):
                    return

                # Apply sampling
                if self.samplingRate < 1.0 and random.random() > self.samplingRate:
                    return

                request = response.request
                timing = request.timing
                duration = timing['responseStart'] if timing else None

                pair = RequestResponsePair(
                    url=url,
                    method=request.method,
                    requestHeaders=request.headers,
                    responseHeaders=await response.all_headers(),
                    status=response.status,
                    responseTimeMs=duration,
                    timestamp=int(time.time() * 1000),
                )

                cleaned = clean_request_response_pair(pair)
                self.network_logs.append(cleaned)

            except Exception:
                logger.exception("[NetworkWatcher] Failed to process response")

        page.on("response", on_response)

    def get_network_logs_since(self, timestamp: int) -> List[RequestResponsePair]:
        return [log for log in self.network_logs if log.timestamp >= timestamp]