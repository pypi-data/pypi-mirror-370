"""
Spider to crawl reports from the office of the inspector general
"""

import multiprocessing as mp
import random
from collections.abc import Generator
from pathlib import Path

import scrapy
from scrapy.http import HtmlResponse, Request, Response
from scrapy.settings import BaseSettings

from sciop_scraping.const import USER_AGENTS
from sciop_scraping.mixins.wayback import WaybackMixin

BASE_URL = "https://www.stateoig.gov/reports"
PAGE_TEMPLATE = BASE_URL + "?page={n}"
PDF_ROOT = "https://www.stateoig.gov/uploads/report/"


class ReportMeta(scrapy.Item):
    report_id = scrapy.Field()
    title = scrapy.Field()
    timestamp = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    terms = scrapy.Field()
    files = scrapy.Field()
    file_urls = scrapy.Field()


class OIGSpider(scrapy.Spider, WaybackMixin):
    """
    Outputs
    - a `metadata.jsonl` file containing the title, description, date and
      terms for each of the reports as well as a map to the files
    - a `files/` directory containing the pdfs
    - a `archive/` directory that contains all PDFs from archive.org,
      potentially including duplicates of the files from the main site.
    """

    name = "us-oig"
    custom_settings = {
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 10,
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 522, 524, 408],
        "CONCURRENT_REQUESTS": int(round(mp.cpu_count() * 1.5)),
        "CONCURRENT_REQUESTS_PER_DOMAIN": int(round(mp.cpu_count() * 1.5)),
    }

    def __init__(self, output: Path | None = None, metadata: list[dict] = None):
        super().__init__()
        if output is None:
            output = Path().cwd() / "data" / "us-oig"
            output.mkdir(exist_ok=True)
        self.output = output
        (self.output / "archive").mkdir(exist_ok=True)
        (self.output / "files").mkdir(exist_ok=True)
        self.metadata = {item["report_id"]: item for item in metadata}

    @classmethod
    def update_settings(cls, settings: BaseSettings) -> None:
        settings.set("USER_AGENT", random.choice(USER_AGENTS))
        settings.set("ROBOTSTXT_OBEY", False, priority="spider")

    @property
    def metadata_path(self) -> Path:
        return self.output / "metadata.json"

    async def start(self) -> Generator[Request, None, None]:
        self.logger.info(self.settings["USER_AGENT"])
        yield scrapy.Request(PAGE_TEMPLATE.format(n=0), callback=self.parse_first)
        # yield next(self.wb_get_prefix(PDF_ROOT, self.parse_archive_urls))

    def parse_first(self, response: HtmlResponse) -> Generator[Request, None, None]:
        """
        Parse the first page first to get the max number of pages,
        then parse normally
        """
        self.parse_page(response)
        buttons = response.css("a.usa-pagination__button::text").getall()
        page_ns = []
        for button in buttons:
            try:
                page_ns.append(int(button.strip()))
            except ValueError:
                continue
        max_page = max(page_ns)
        for page_n in range(1, max_page):
            yield scrapy.Request(PAGE_TEMPLATE.format(n=page_n), callback=self.parse_page)

    def parse_page(self, response: HtmlResponse) -> Generator[Request, None, None]:
        links = response.css("div.views-row a::attr(href)").getall()
        for link in links:
            report_n = link.split("/")[-1]
            if report_n in self.metadata:
                continue
            yield response.follow(link, callback=self.parse_report)

    def parse_report(self, response: HtmlResponse) -> Generator[Request | ReportMeta, None, None]:
        report_id = response.url.split("/")[-1]
        title = response.css("h1.page-title span::text").get()
        timestamp = response.css("time::attr(datetime)").get()
        description = "\n".join(response.css(".field--name-body p::text").getall())
        terms_html = response.css("#report-terms .field")
        terms = {}
        for term in terms_html:
            key = term.css(".field__label::text").get()
            value = term.css(".field__item a::text").getall()
            terms[key] = value
        file_urls = response.css(".field--type-file a::attr(href)").getall()
        rel_paths = [
            str(self.get_file_path(url, report_id).relative_to(self.output)) for url in file_urls
        ]
        meta = ReportMeta(
            **{
                "report_id": report_id,
                "title": title,
                "timestamp": timestamp,
                "description": description,
                "terms": terms,
                "files": rel_paths,
                "file_urls": file_urls,
                "url": response.url,
            }
        )
        yield meta
        for file_url in file_urls:
            yield response.follow(
                file_url, callback=self.parse_report_file, cb_kwargs={"report_id": report_id}
            )

    def parse_report_file(self, response: Response, report_id: str) -> None:
        out_path = self.get_file_path(response.url, report_id)
        with open(out_path, "wb") as f:
            f.write(response.body)

    def parse_archive_urls(self, urls: list[str]) -> Generator[Request, None, None]:
        self.logger.info("Got archive urls: %s", urls)
        urls = [url for url in urls if not (self.output / "archive" / url.split("/")[-1]).exists()]
        for url in urls:
            yield scrapy.Request(url, callback=self.parse_archive_pdf)

    def parse_archive_pdf(self, response: Response) -> None:
        report_path = self.output / "archive" / response.url.split("/")[-1]
        with open(report_path, "wb") as f:
            f.write(response.body)

    def get_file_path(self, url: str, report_id: str) -> Path:
        report_path = self.output / "files" / report_id
        report_path.mkdir(exist_ok=True)
        return report_path / url.split("/")[-1]
