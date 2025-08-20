import json
from pathlib import Path

import click
from scrapy.crawler import CrawlerProcess

from sciop_scraping.quests.us_oig.spider import OIGSpider


@click.command("us-oig")
@click.option(
    "-o",
    "--output",
    help="Output directory to save files in. "
    "If None, $PWD/data/us-oig. "
    "Data will be saved in a chronicling-america subdirectory, "
    "and the crawl state will be saved in crawl_state.",
    default=None,
    type=click.Path(),
)
def us_oig(output: str | None = None) -> None:
    output = Path.cwd() / "data" / "us-oig" if not output else Path(output)
    output.mkdir(exist_ok=True, parents=True)
    meta_path = output / "metadata.jsonl"
    if meta_path.exists():
        metadata = []
        with open(meta_path) as f:
            for line in f:
                metadata.append(json.loads(line))
    else:
        metadata = []

    process = CrawlerProcess(settings={"FEEDS": {meta_path: {"format": "jsonlines"}}})
    process.crawl(OIGSpider, output=output, metadata=metadata)
    process.start()
