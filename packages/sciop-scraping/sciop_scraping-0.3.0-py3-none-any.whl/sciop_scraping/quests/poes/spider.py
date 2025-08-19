import multiprocessing as mp
import posixpath
import re
from collections.abc import AsyncIterator
from itertools import product
from pathlib import Path
from typing import Any

import scrapy
from scrapy.http import HtmlResponse, Response

URL_ROOT = "https://www.ncei.noaa.gov/data/poes-metop-space-environment-monitor/access/"
L1A_URL = "https://www.ncei.noaa.gov/data/poes-metop-space-environment-monitor/access/l1a/v01r00/"
L1B_URL = "https://www.ncei.noaa.gov/data/poes-metop-space-environment-monitor/access/l1b/v01r00/"
DECOMISSIONED = ("noaa15", "noaa19")
YEARS = [year for year in range(2012, 2026)]
IGNORE_LINKS = ("Parent Directory", "Name", "Last modified", "Size")


class PoesSpider(scrapy.Spider):
    """
    https://www.ncei.noaa.gov/products/poes-metop-space-environment-monitor
    """

    name = "noaa-poes"
    custom_settings = {
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 10,
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 522, 524, 408],
        "CONCURRENT_REQUESTS": int(round(mp.cpu_count() * 1.5)),
        "CONCURRENT_REQUESTS_PER_DOMAIN": int(round(mp.cpu_count() * 1.5)),
    }

    def __init__(self, output: Path):
        self.output = output

    def url_to_path(self, file_url: str) -> Path:
        relative = re.sub(URL_ROOT, "", file_url)
        return self.output / relative

    async def start(self) -> AsyncIterator[Any]:
        for group, year, sat in product((L1A_URL, L1B_URL), YEARS, DECOMISSIONED):
            full_url = posixpath.join(group, str(year), sat) + "/"
            yield scrapy.Request(
                full_url,
                callback=self.parse_files,
                dont_filter=True,
            )

    async def parse_files(self, response: HtmlResponse) -> None:
        links = response.css("td > a")
        for link in links:
            if link.css("a::text").get() in IGNORE_LINKS:
                continue
            file_url = response.urljoin(link.attrib["href"])
            file_path = self.url_to_path(file_url)
            if file_path.exists():
                continue
            file_path.parent.mkdir(exist_ok=True, parents=True)
            yield response.follow(file_url, callback=self.parse_file)

    def parse_file(self, response: Response) -> None:
        """
        Save a file underneath ``self.output``, removing the base url
        """

        out_path = self.url_to_path(response.url)
        self.logger.debug("Saving %s to %s", response.url, out_path)
        with open(out_path, "wb") as f:
            f.write(response.body)
