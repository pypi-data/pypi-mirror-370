from typing import Any

import scrapy
from scrapy import Request
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.http import Response
from scrapy.utils.response import response_status_message
from twisted.internet import defer, reactor


async def async_sleep(delay: float, return_value: Any | None = None) -> defer.Deferred:
    deferred = defer.Deferred()
    reactor.callLater(delay, deferred.callback, return_value)
    return await deferred


class TooManyRequestsRetryMiddleware(RetryMiddleware):
    """
    Modifies RetryMiddleware to delay retries on status 429.

    References:
        https://stackoverflow.com/a/66131114/13113166
    """

    DEFAULT_DELAY = 60  # Delay in seconds.
    MAX_DELAY = 600  # Sometimes, RETRY-AFTER has absurd values

    async def process_response(
        self, request: scrapy.Request, response: Response, spider: scrapy.Spider
    ) -> Response | Request | None:
        """
        Like RetryMiddleware.process_response, but, if response status is 429,
        retry the request only after waiting at most self.MAX_DELAY seconds.
        Respect the Retry-After header if it's less than self.MAX_DELAY.
        If Retry-After is absent/invalid, wait only self.DEFAULT_DELAY seconds.
        """

        if request.meta.get("dont_retry", False):
            return response

        if response.status in self.retry_http_codes:
            if response.status == 429:
                retry_after = response.headers.get("retry-after")
                try:
                    retry_after = int(retry_after)
                except (ValueError, TypeError):
                    delay = self.DEFAULT_DELAY
                else:
                    delay = min(self.MAX_DELAY, retry_after)
                spider.logger.info(f"Retrying {request} in {delay} seconds.")

                spider.crawler.engine.pause()
                await async_sleep(delay)
                spider.crawler.engine.unpause()

            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response

        return response
