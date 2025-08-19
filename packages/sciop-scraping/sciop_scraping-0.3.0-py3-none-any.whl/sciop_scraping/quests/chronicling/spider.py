import hashlib
import multiprocessing as mp
import random
import re
from collections.abc import AsyncIterator, Generator
from io import BytesIO
from pathlib import Path
from typing import Any, cast
from urllib.parse import urljoin

import scrapy
from scrapy.http import HtmlResponse, Response, TextResponse
from scrapy.settings import BaseSettings
from scrapy.spidermiddlewares.httperror import HttpError
from tqdm import tqdm
from twisted.python.failure import Failure

from sciop_scraping.const import USER_AGENTS
from sciop_scraping.validation import BAGIT_ALGO_PRIORITY, BAGIT_MANIFEST

BASE_URL = "https://chroniclingamerica.loc.gov/data/batches/"
# standard files that we will look for in all cases
ALL_BAGIT_FILES = ["bag-info.txt", "bagit.txt"]
# data manifest files - we expect at least one
ALL_MANIFEST_FILES = [f"manifest-{hash_type}.txt" for hash_type in BAGIT_ALGO_PRIORITY]
# tagmanifest files - optional, but if present, they may contain other metadata filenames
ALL_TAGMANIFEST_FILES = [f"tag{file}" for file in ALL_MANIFEST_FILES]
# initial list to try
ALL_META_FILES = ALL_BAGIT_FILES + ALL_MANIFEST_FILES + ALL_TAGMANIFEST_FILES


class ChroniclingAmericaSpider(scrapy.Spider):
    """
    Crawl chronicling america data from the Library of Congress,
    either by batch or as a whole.

    Excludes `.tif` and `.tiff` files, since they are redundant with the .jp2 files.
    """

    name = "chronicling-america"
    allowed_domains = ["chroniclingamerica.loc.gov", "tile.loc.gov"]

    USER_AGENT_OVERRIDE: str | None = None
    JOBDIR_OVERRIDE: str | None = None
    custom_settings = {
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 100,
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 522, 524, 408],
        "CONCURRENT_REQUESTS": int(round(mp.cpu_count() * 1.5)),
        "CONCURRENT_REQUESTS_PER_DOMAIN": int(round(mp.cpu_count() * 1.5)),
    }

    def __init__(
        self,
        batch: str | None = None,
        output: Path | None = None,
        cf_cookie: str | None = None,
        download_timeout: int = 20,
        resume: bool = False,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        if batch:
            self.batch = batch.replace("-", "_")
        else:
            self.batch = batch
        if output is None:
            self.output = Path.cwd() / "data" / "chronicling-america"
        else:
            self.output = Path(output).resolve()
        self.output.mkdir(exist_ok=True, parents=True)
        self.cf_cookie = {"cf_clearance": cf_cookie} if cf_cookie else None
        self.crawl_root = self.crawl_root(self.batch)
        if not self.batch:
            self.start_urls = [BASE_URL]
        else:
            self.start_urls = [urljoin(self.crawl_root, f) for f in ALL_META_FILES]
        self.download_timeout = download_timeout
        self.resume = resume
        # logging.getLogger('scrapy').propagate = False

    async def start(self) -> AsyncIterator[Any]:

        for url in self.start_urls:
            # tagmanifest is an optional manifest for other meta files.
            # we parse up to one in case there are any unexpected meta files to add to the url list.
            # we will download all tagmanifest files
            if url.split("/")[-1] in ALL_TAGMANIFEST_FILES:
                yield scrapy.Request(
                    self.tile_url(url),
                    callback=self.parse_tagmanifest,
                    dont_filter=True,
                    cookies=self.cf_cookie,
                    errback=self.errback,
                    cb_kwargs={"batch_url": self.crawl_root, "original_url": url},
                )

            # manifest is the main manifest for the data in the batch.
            # there should be one, there could be more (different hashing algorithms).
            # we parse the first one and download any others.
            elif url.split("/")[-1] in ALL_MANIFEST_FILES:
                yield scrapy.Request(
                    self.tile_url(url),
                    callback=self.parse_manifest,
                    dont_filter=True,
                    cookies=self.cf_cookie,
                    errback=self.errback,
                    cb_kwargs={"batch_url": self.crawl_root, "original_url": url},
                )

            # if there is no tagmanifest, we want to at least get certain predefined files anyway
            elif url.split("/")[-1] in ALL_BAGIT_FILES:
                yield scrapy.Request(
                    self.tile_url(url),
                    callback=self.parse_file,
                    dont_filter=True,
                    cookies=self.cf_cookie,
                    errback=self.errback,
                    cb_kwargs={"original_url": url},
                )

            # get any other data files
            # (including additional manifest/tagmanifest files after we have processed one)
            else:
                yield scrapy.Request(
                    url, dont_filter=True, cookies=self.cf_cookie, errback=self.errback
                )

    @classmethod
    def update_settings(cls, settings: BaseSettings) -> None:
        super().update_settings(settings)
        if cls.USER_AGENT_OVERRIDE:
            settings.set("USER_AGENT", cls.USER_AGENT_OVERRIDE, priority="spider")
        else:
            settings.set("USER_AGENT", random.choice(USER_AGENTS), priority="spider")
        if cls.JOBDIR_OVERRIDE:
            settings.set("JOBDIR", str(cls.JOBDIR_OVERRIDE))
        settings.set("ROBOTSTXT_OBEY", False, priority="spider")
        # there doesn't appear to be a rate limit on tile.loc.gov,
        # and since we can jump straight there when we have a batch name,
        # and i'm not sure how to dynamically modify this, leave this off by default.
        # settings.set("DOWNLOAD_DELAY", 0.5, priority="spider")

    def url_to_path(self, url: str) -> Path:
        """Get the output path for a given URL."""
        out_name = re.sub(BASE_URL, "", url)
        out_path = self.output / out_name
        out_path.parent.mkdir(exist_ok=True, parents=True)

        return out_path

    @staticmethod
    def crawl_root(batch: str | None = None) -> str:
        if not batch:
            return BASE_URL
        else:
            return BASE_URL + batch + "/"

    @staticmethod
    def tile_url(url: str) -> str:
        """Convert a chroniclingamerica.loc.gov url to a tile.loc.gov url"""
        if "tile.loc.gov" in url:
            return url
        pattern = re.compile(
            r"^https://chroniclingamerica\.loc\.gov/data/batches/(?P<batch>\w+)/(?P<path>.*)"
        )
        match = pattern.match(url)
        if not match:
            raise ValueError(f"Could not convert url to tile url: {url}")
        val = match.groupdict()
        prefix = val["batch"].split("_")[0]
        return f"https://tile.loc.gov/storage-services/service/ndnp/{prefix}/batch_{val['batch']}/{val['path']}"

    @staticmethod
    def webseed_urls(batch: str) -> list[str]:
        """
        Return a pair of URLs that can be used as webseed urls in created torrents.

        like:
        - https://chroniclingamerica.loc.gov/data/batches/
        - https://tile.loc.gov/storage-services/service/ndnp/{batch_prefix}/batch_
        """
        tile_url = ChroniclingAmericaSpider.tile_url(ChroniclingAmericaSpider.crawl_root(batch))
        # strip the part so that when we append the batch subdirectory we get the full url
        parts = re.split(r"(?<=batch_)", tile_url)
        return [BASE_URL, parts[0]]

    def parse(self, response: HtmlResponse) -> Generator[scrapy.Request, None, None]:
        links = response.css("a::attr(href)").getall()

        # TODO tagmanifest parsing for this scenario

        # if we are on a page that has a `manifest-*.txt` in it,
        # shortcut and just use that to enumerate the files
        manifest_links = [link for link in links if BAGIT_MANIFEST.fullmatch(link.split("/")[-1])]
        if manifest_links:
            for link in manifest_links:
                link = urljoin(response.url, link)
                yield response.follow(
                    link,
                    callback=self.parse_manifest,
                    errback=self.errback,
                    cookies=self.cf_cookie,
                    cb_kwargs={"batch_url": response.url, "original_url": link},
                )
        else:
            links = [urljoin(response.url, link) for link in links]
            # filter to only those underneath the crawl root
            links = [link for link in links if self.crawl_root in link]

            for link in links:
                if link.endswith("/"):
                    yield response.follow(
                        link, callback=self.parse, errback=self.errback, cookies=self.cf_cookie
                    )
                else:
                    if not self.url_to_path(link).exists():
                        tile_link = self.tile_url(link)
                        yield response.follow(
                            tile_link,
                            callback=self.parse_file,
                            errback=self.errback,
                            cb_kwargs={"original_url": link},
                            cookies=self.cf_cookie,
                        )
                    else:
                        self.logger.info("Skipping %s, already downloaded", link)

    def parse_tagmanifest(self, response: TextResponse, batch_url: str, original_url: str) -> None:
        """
        parse the first tagmanifest file (any others will be downloaded without parsing).
        we only need to enqueue any files listed in tagmanifest which are not in
        MANIFEST_FILES or BAGIT_FILES.
        """
        self.parse_file(response, original_url)

        lines = response.text.split("\n")
        path_hashes = [re.split(r"\s+", line) for line in lines if line]
        urls = [(p[0], urljoin(batch_url, p[1])) for p in path_hashes if p[1] not in ALL_META_FILES]

        self.logger.info(
            f"Downloading {len(urls)} additional unexpected files from tagmanifest {response.url}"
        )
        for url in urls:
            tile_url = self.tile_url(url[1])
            yield response.follow(
                tile_url,
                callback=self.parse_file,
                errback=self.errback,
                cb_kwargs={"original_url": url[1]},
                cookies=self.cf_cookie,
            )

    def parse_manifest(self, response: TextResponse, batch_url: str, original_url: str) -> None:
        # save the manifest
        manifest_file = original_url.split("/")[-1]
        hash_type = BAGIT_MANIFEST.match(manifest_file).groupdict()["hash_type"]
        self.parse_file(response, original_url=urljoin(batch_url, manifest_file))

        lines = response.text.split("\n")
        path_hashes = [re.split(r"\s+", line) for line in lines if line]
        # exclude .tif and .tiff files
        paths = [
            p for p in path_hashes if not p[-1].endswith(".tif") and not p[-1].endswith(".tiff")
        ]
        urls = [(p[0], urljoin(batch_url, p[1])) for p in paths]

        # separate completed, partial, and not started files
        # yeah this is a little inefficient but we only need to do it once
        existing = [url for url in urls if self.url_to_path(url[1]).exists()]
        not_existing = [url for url in urls if not self.url_to_path(url[1]).exists()]

        self.logger.info(f"Downloading {len(not_existing)} new files")

        for url in not_existing:
            tile_url = self.tile_url(url[1])
            yield response.follow(
                tile_url,
                callback=self.parse_file,
                errback=self.errback,
                cb_kwargs={"original_url": url[1]},
                cookies=self.cf_cookie,
            )

        # check existing files for completeness, retry partial files with byte offset ranges
        if existing and self.resume:
            self.logger.info(f"Checking {len(existing)} existing files for completion")
            yield from self._resume(existing, response, hash_type)
        else:
            return

    def _resume(
        self, existing: list[tuple[str, str]], response: TextResponse, hash_type: str
    ) -> None:
        partial = []

        for digest_url in tqdm(existing):
            expected_digest, url = digest_url
            path = self.url_to_path(url)
            with open(path, "rb") as f:
                digest = hashlib.file_digest(f, hash_type).hexdigest()
            if digest == expected_digest:
                continue
            partial.append(url)
            existing_size = path.stat().st_size
            yield response.follow(
                self.tile_url(url),
                callback=self.parse_partial_file,
                errback=self.errback,
                cb_kwargs={"original_url": url},
                cookies=self.cf_cookie,
                headers={"Range": f"bytes={existing_size}-"},
            )

        if partial:
            self.logger.info(f"Retrying {len(partial)} partial downloads")
        self.logger.info(f"Not downloading {len(existing) - len(partial)} completed files")

    def parse_file(self, response: Response, original_url: str) -> None:
        """
        Save a file underneath ``self.output``, removing the base url
        """
        out_path = self.url_to_path(original_url)
        self.logger.debug("Saving %s to %s", response.url, out_path)
        with open(out_path, "wb") as f:
            f.write(response.body)

    def parse_partial_file(self, response: Response, original_url: str) -> None:
        """
        Append to an already-existing partial file
        """
        out_path = self.url_to_path(original_url)

        # if partial range returned, append, otherwise write new
        mode = "ab" if response.status == 206 else "wb"
        if mode == "ab":
            self.logger.debug("Appending partial file %s to %s", response.url, out_path)
        else:
            self.logger.debug(
                "HTTP range ignored by server, saving %s to %s", response.url, out_path
            )
        with open(out_path, mode) as f:
            f: BytesIO
            f.write(response.body)

    def errback(self, failure: Failure) -> None:
        self.logger.error(f"A spider error occurred: {failure}")
        if failure.check(HttpError) and failure.value.response.status == 429:
            raise scrapy.exceptions.CloseSpider(
                "429 received - stopping scrape. We can't wait these out. \n"
                "You should \n"
                "- Open one of the recent pages in a browser,\n"
                "- Pass the cloudflare check\n"
                "- Open your developer tools (often right click + inspect element)\n"
                "- Open the networking tab to watch network requests\n"
                "- Reload the page\n"
                "- Click on the request made to the page you're on to see the request headers\n"
                "- Copy your user agent and the part of the cookie after `cf_clearance=` "
                "and pass them to the -u and -c cli options, respectively.\n"
                "If you are crawling *all* data, rather than a single batch, "
                "you will likely need to set DOWNLOAD_DELAY=1 until the manifests are scraped."
            )
        elif failure.check(HttpError) and failure.value.response.status == 416:
            # requested an impossible range, e.g. from when we have an incorrect hash
            # and try to resume. Resolves ambiguity between incomplete vs. incorrect hash mismatches
            failure.value.response = cast(Response, failure.value.response)
            if "original_url" in failure.request.cb_kwargs:
                original_url = failure.request.cb_kwargs["original_url"]
                path = self.url_to_path(original_url)

                self.logger.warning(
                    "Removing file with unsatisfiable request range %s from %s and retrying",
                    path,
                    original_url,
                )
                path.unlink(missing_ok=True)
                yield scrapy.Request(
                    self.tile_url(original_url),
                    callback=self.parse_file,
                    errback=self.errback,
                    cb_kwargs={"original_url": original_url},
                    cookies=self.cf_cookie,
                    dont_filter=True,
                )
