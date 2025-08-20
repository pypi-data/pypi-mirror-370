from abc import ABC, abstractmethod
from collections.abc import Generator
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Self
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

import scrapy


@dataclass
class S3V2ListItem:
    key: str
    last_modified: datetime
    etag: str
    size: int
    storage_class: str
    checksum_algorithm: str | None = None
    checksum_type: str | None = None
    owner: dict | None = None
    restore_status: dict | None = None

    @classmethod
    def from_xml(cls, item: scrapy.Selector) -> Self:
        return S3V2ListItem(
            key=item.xpath("s3:Key/text()").get(),
            last_modified=datetime.fromisoformat(item.xpath("s3:LastModified/text()").get()),
            etag=item.xpath("s3:ETag/text()").get().lstrip('"').rstrip('"'),
            size=int(item.xpath("s3:Size/text()").get()),
            storage_class=item.xpath("s3:StorageClass/text()").get(),
            checksum_algorithm=item.xpath("s3:ChecksumAlgorithm/text()").get(),
            checksum_type=item.xpath("s3:ChecksumType/text()").get(),
            owner=item.xpath("s3:Owner/text()").get(),
            restore_status=item.xpath("s3:RestoreStatus/text()").get(),
        )


class S3Mixin(ABC):
    def iter_s3_items(
        self, bucket_url: str, prefix: str | None = None
    ) -> Generator[scrapy.Request]:
        """
        Iterate through pages in an AWS bucket (given as the URL of the bucket)

        Yields requests to two parsing callbacks:
        - `parse_s3_page`: defined here, receive the page and yield a request for the next page
        - `parse_s3_items`: Must be defined in a subclass -
          receives the actual items to be used for further processing
        """
        query = {
            "list-type": 2,
            "encoding-type": "url",
        }
        if prefix is not None:
            query["prefix"] = prefix
        url = urljoin(bucket_url, "?" + urlencode(query))
        yield scrapy.Request(url, callback=self.parse_s3_page)

    def parse_s3_page(self, response: scrapy.http.XmlResponse) -> Generator[scrapy.Request]:
        # yield the request for the next page
        parsed = urlparse(response.request.url)
        query = parse_qs(parsed.query)
        selector = scrapy.Selector(response, type="xml")
        selector.register_namespace("s3", "http://s3.amazonaws.com/doc/2006-03-01/")
        next_token = selector.xpath("//s3:NextContinuationToken/text()").get()
        if next_token:
            # this is seriously so annoying to have to do
            query = {k: v[0] for k, v in query.items()}
            query["continuation-token"] = next_token
            encoded_query = urlencode(query)
            unparsed = urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    encoded_query,
                    parsed.fragment,
                )
            )
            yield scrapy.Request(unparsed, priority=1, callback=self.parse_s3_page)

        # call the overridden callback with the items
        items = selector.xpath("//s3:Contents")
        items_cast = [S3V2ListItem.from_xml(item) for item in items]
        yield from self.parse_s3_items(response, items_cast)

    @abstractmethod
    def parse_s3_items(self, response: scrapy.http.Response, items: list[S3V2ListItem]) -> Any: ...
