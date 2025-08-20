"""
Helper mixin for scraping files (and maybe pages) from archive.org's wayback machine
"""

from collections.abc import Callable, Generator
from datetime import datetime
from typing import Any, Self, TypedDict
from urllib.parse import quote

import scrapy
from scrapy.http import JsonRequest, JsonResponse
from scrapy.responsetypes import Response

from sciop_scraping.mixins.filter import URLFilter


class WaybackDatetime(datetime):
    """
    Wayback machine uses flat timestamps that are like
    YYYYMMDDHHMMSS with no delimiters.

    Simple convenience methods for parsing/rendering
    """

    WAYBACK_STRF = "%Y%m%d%H%M%S"

    @staticmethod
    def format_str(timestamp: datetime) -> str:
        return timestamp.strftime(WaybackDatetime.WAYBACK_STRF)

    @classmethod
    def from_str(cls, timestamp: str) -> Self:
        return cls.strptime(timestamp, cls.WAYBACK_STRF)

    def to_str(self) -> str:
        return self.strftime(self.WAYBACK_STRF)


class TimeMapDict(TypedDict, total=False):
    """
    Response type when requesting "time maps",
    or the set of urls beneath a given prefix
    """

    original: str
    """url of the original page"""
    mimetype: str
    timestamp: str
    endtimestamp: str
    groupcount: str
    uniqcount: str


class WaybackMixin:
    TIMEMAP_TEMPLATE = "https://web.archive.org/web/timemap/json?url={url}&matchType=prefix&collapse=urlkey&output=json&fl=original%2Cmimetype%2Ctimestamp%2Cendtimestamp%2Cgroupcount%2Cuniqcount&filter=!statuscode%3A%5B45%5D..&limit=10000"

    def wb_get_prefix(
        self,
        url: str,
        callback: Callable[[list[str]], Any],
        **kwargs: Any,
    ) -> Generator[JsonRequest, None, None]:
        """
        Get the urls for the latest snapshots of files beneath some url prefix,
        returning the list of urls to a given callback function.

        To call a parser callback for *requested* copies of each of the urls,
        use :meth:`.wb_expand_prefix`
        """
        timemap_url = self.TIMEMAP_TEMPLATE.format(url=quote(url))
        yield JsonRequest(
            timemap_url,
            callback=self._wb_extract_prefix_urls,
            cb_kwargs={"callback": callback},
            **kwargs,
        )

    def _wb_extract_prefix_urls(
        self, response: JsonResponse, callback: Callable[[list[str]], Generator[Any, None, None]]
    ) -> None:

        res_json = response.json()
        headers = res_json[0]
        items: list[TimeMapDict] = [
            {key: val for key, val in zip(headers, item)} for item in res_json[1:]
        ]
        urls = [
            self.wb_url_from_timestamp(item["original"], item["endtimestamp"]) for item in items
        ]
        yield from callback(urls)

    def wb_expand_prefix(
        self,
        url: str,
        callback: Callable[[Response], Any],
        url_filter: URLFilter | None = None,
        request_kwargs: dict | None = None,
    ) -> Generator[JsonRequest, None, None]:
        """
        Given some url prefix, get the latest version of all urls that match some url filter,
        and then process with some passed callback method.

        First gather the urls by making a request to an undocumented wayback api,
        then yield requests for each matching url using :meth:`.wb_parse_prefix_json`,
        then the results of those urls are passed to the provided callback method.

        The :class:`.TimeMap` dict that contains metadata for the item,
        including the timestamp of the snapshot, will be in the request's
        `meta` attr with a `"timemap"` key.
        """
        if request_kwargs is None:
            request_kwargs = {}
        timemap_url = self.TIMEMAP_TEMPLATE.format(url=quote(url))

        yield scrapy.JsonRequest(
            timemap_url,
            callback=self.wb_parse_prefix_json,
            dont_filter=True,
            cb_kwargs={
                "callback": callback,
                "url_filter": url_filter,
                "request_kwargs": request_kwargs,
            },
            **request_kwargs,
        )

    def wb_parse_prefix_json(
        self,
        response: JsonResponse,
        callback: Callable[[Response], Any],
        url_filter: URLFilter | None = None,
        request_kwargs: dict | None = None,
    ) -> Generator[scrapy.Request, None, None]:
        """
        Parse the response from a wb_expand_prefix request for a "timemap" of urls beneath a prefix,
        requesting any that match a filter with the provided callback.

        The format of the response is a table in the form of a list of lists,
        where the first item in the list are the keys for each of the subsequent lists.

        so like

        ```
        [
            ["letter", "number", "whatever"],
            ["a", 1, "something"]
        ]
        ```

        corresponds to

        ```
        {
            "letter": "a",
            "number": 1,
            "whatever": "something",
        }
        ```

        and the fields from this response correspond to :class:`.TimeMapDict`
        """
        if request_kwargs is None:
            request_kwargs = {}

        res_json = response.json()
        headers = res_json[0]
        items: list[TimeMapDict] = [
            {key: val for key, val in zip(headers, item)} for item in res_json[1:]
        ]
        for item in items:
            if url_filter is not None and not url_filter.url_valid(item["original"]):
                continue
            yield response.follow(
                self.wb_url_from_timestamp(item["original"], item["endtimestamp"]),
                callback=callback,
                dont_filter=True,
                meta={"timemap": item},
                **request_kwargs,
            )

    def wb_follow(
        self, response: Response, callback: Callable, **kwargs: Any
    ) -> Generator[scrapy.Request, None, None]:
        """
        Follow some response and get the latest wayback machine copy of that url,
        calling some callback with the result
        """
        yield response.follow(
            f"https://web.archive.org/{quote(response.url)}", callback=callback, **kwargs
        )

    @staticmethod
    def wb_url_from_timestamp(url: str, timestamp: datetime | str) -> str:
        """
        Construct a wayback machine url from the target page url and a timestamp.

        Just a string formatting method, use :meth:`.get_snapshots` to find valid timestamps.

        Args:
            url: Target page url
            timestamp: Timestamp of a snapshot either as a datetime object or a
                :class:`.WaybackDatetime` YYYYMMDDHHMMSS string

        """
        if isinstance(timestamp, datetime):
            timestamp = WaybackDatetime.format_str(timestamp)

        return f"https://web.archive.org/web/{timestamp}/{url}"
