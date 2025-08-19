import multiprocessing as mp
import re
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urljoin

import scrapy

from sciop_scraping.mixins.s3 import S3Mixin, S3V2ListItem
from sciop_scraping.quests.smithsonian.const import BUCKET_URL


class SmithsonianSpider(scrapy.Spider, S3Mixin):
    name = "smithsonian"

    custom_settings = {
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 10,
        "RETRY_HTTP_CODES": [422, 500, 502, 503, 504, 522, 524, 408],
        "CONCURRENT_REQUESTS": int(round(mp.cpu_count() * 1.5)),
        "CONCURRENT_REQUESTS_PER_DOMAIN": int(round(mp.cpu_count() * 1.5)),
        "DOWNLOAD_WARNSIZE": 1 * (2**30),  # 1 GiB
        "DOWNLOAD_TIMEOUT": 60 * 15,
    }

    def __init__(self, output: Path, dataset: str, format: Literal["jpg", "tif"]):
        super().__init__()
        self.output = Path(output)
        self.dataset = dataset
        self.format = format

    async def start(self) -> AsyncGenerator[scrapy.Request]:
        yield next(self.iter_s3_items(BUCKET_URL, "media/" + self.dataset))

    def parse_s3_items(self, response: scrapy.http.Response, items: list[S3V2ListItem]) -> Any:
        for item in items:
            path = self.path_from_key(item.key)

            if self.format == "jpg" and path.suffix not in (".jpg", ".jpeg"):  # noqa: SIM114
                continue
            elif self.format == "tif" and path.suffix not in (".tif", ".tiff"):
                continue

            yield item

            if path.exists():
                continue

            yield scrapy.Request(
                urljoin(BUCKET_URL, item.key), callback=self.parse_file, cb_kwargs={"item": item}
            )

    def parse_file(self, response: scrapy.http.Response, item: S3V2ListItem) -> None:
        path = self.path_from_key(item.key)
        with open(path, "wb") as f:
            f.write(response.body)

    def path_from_key(self, key: str) -> Path:
        key = re.sub(r"^media/", "", key)
        path = self.output / "smithsonian" / f"{self.dataset}-{self.format}" / key
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
