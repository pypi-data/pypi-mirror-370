from pathlib import Path

import click
from scrapy.crawler import CrawlerProcess

from sciop_scraping.quests.poes.spider import PoesSpider


@click.command("noaa-poes")
@click.option(
    "-o",
    "--output",
    help="Output directory to save files in. "
    "If None, $PWD/data/noaa-poes. "
    "Data will be saved in a chronicling-america subdirectory, "
    "and the crawl state will be saved in crawl_state.",
    default=None,
    type=click.Path(),
)
def noaa_poes(output: str | None = None) -> None:
    output = Path.cwd() / "data" / "noaa-poes" if not output else Path(output)
    output.mkdir(exist_ok=True, parents=True)
    process = CrawlerProcess()
    process.crawl(PoesSpider, output=output)
    process.start()
