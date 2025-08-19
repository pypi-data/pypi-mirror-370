from pathlib import Path
from typing import Any

import click
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from sciop_cli.api import claim_next
from sciop_cli.config import get_config
from sciop_cli.models.sciop import Upload

from sciop_scraping.cli.common import spider_options
from sciop_scraping.quests.base import QuestLog, QuestStatus, upload_subquest
from sciop_scraping.quests.chronicling import ChroniclingAmericaQuest
from sciop_scraping.quests.chronicling.spider import ChroniclingAmericaSpider


@click.command("chronicling-america")
@click.option("-b", "--batch", help="Which batch to crawl. If None, crawl everything", default=None)
@click.option(
    "-o",
    "--output",
    help="Output directory to save files in. "
    "If None, $PWD/data/chronicling-america. "
    "Data will be saved in a chronicling-america subdirectory, "
    "and the crawl state will be saved in crawl_state.",
    default=None,
    type=click.Path(),
)
@click.option(
    "-c",
    "--cloudflare-cookie",
    help="When you get rate limited, you need to go solve a cloudflare challenge, "
    "grab the cookie with the key 'cf_clearance' and pass it here",
    default=None,
)
@click.option(
    "-u",
    "--user-agent",
    help="When you get rate limited, the cookie is tied to a specific user agent, "
    "copy paste that and pass it here",
    default=None,
)
@click.option(
    "--crawl-state",
    help="Use scrapy crawl state. Defaults False, "
    "because we can resume crawling using the manifest.",
    default=False,
    is_flag=True,
)
@click.option(
    "--next",
    help="Claim, download, and upload the next available dataset part from the quest. "
    "Must have already logged in with `sciop-cli login` or `sciop-scrape api login`. "
    "Mutually exclusive with --batch and --auto.",
    is_flag=True,
    default=False,
)
@click.option(
    "--auto",
    help="Keep getting dataset parts from the quest until stopped or none remain. "
    "Must have already logged in with `sciop-cli login` or `sciop-scrape api login`. "
    "Mutually exclusive with --batch and --next.",
    is_flag=True,
    default=False,
)
@click.option(
    "--upload/--no-upload",
    help="Create a torrent and upload it to the configured sciop instance.",
    default=True,
    is_flag=True,
    show_default=True,
)
@click.option(
    "--resume",
    help="Attempt to resume partially downloaded files, rather than removing and starting again",
    default=False,
    is_flag=True,
    show_default=True,
)
@click.option(
    "--new",
    help="Ignore incomplete subquests in the quest log, get a new claim and start it. "
    "(for when we want to move on and come back and get the missing files later)",
    default=False,
    is_flag=True,
    show_default=True,
)
@spider_options
def chronicling_america(
    batch: str | None,
    output: Path | None = None,
    cloudflare_cookie: str | None = None,
    user_agent: str | None = None,
    crawl_state: bool = False,
    retries: int = 100,
    timeout: float = 20,
    next: bool = False,
    auto: bool = False,
    upload: bool = True,
    resume: bool = False,
    new: bool = False,
) -> None:
    """
    Scrape the Chronicling America dataset from the Library of Congress in batches

    https://chroniclingamerica.loc.gov/data/batches/

    If you get a 429 redirect, you will need to manually bypass the cloudflare ratelimit check.

    - Open https://chroniclingamerica.loc.gov/data/batches/ in a browser,
    - Pass the cloudflare check
    - Open your developer tools (often right click + inspect element)
    - Open the networking tab to watch network requests
    - Reload the page
    - Click on the request made to the page you're on to see the request headers
    - Copy your user agent and the part of the cookie after `cf_clearance=`
      and pass them to the -u and -c cli options, respectively.
    """
    if output is None:
        output = Path.cwd() / "data"
    if retries is None:
        retries = 100
    if timeout is None:
        timeout = 20

    output.mkdir(exist_ok=True, parents=True)

    job_dir = None
    if crawl_state:
        job_dir = output / "crawl_state" / batch
        job_dir.mkdir(exist_ok=True, parents=True)
    torrent_dir = output / "torrents"
    if upload:
        torrent_dir.mkdir(exist_ok=True, parents=True)

    scrape_kwargs = {
        "job_dir": job_dir,
        "user_agent": user_agent,
        "cf_cookie": cloudflare_cookie,
        "retries": retries,
        "download_timeout": timeout,
        "resume": resume,
    }

    assert (
        sum([bool(batch), bool(next), bool(auto)]) <= 1
    ), "Can only pass one of batch, next, or auto"
    if batch:
        res = _run_chronam(subquest=batch, output=output, scrape_kwargs=scrape_kwargs)
        click.echo(f"Completed scraping {batch}")
        rprint(res)
        if upload:
            _upload_chronam(res=res, torrent_dir=torrent_dir)
    elif next:
        _next_chronam(
            output=output,
            scrape_kwargs=scrape_kwargs,
            upload=upload,
            torrent_dir=torrent_dir,
            new=new,
        )

    elif auto:
        _auto_chronam(
            output=output,
            scrape_kwargs=scrape_kwargs,
            upload=upload,
            torrent_dir=torrent_dir,
            new=new,
        )

    else:
        raise ValueError("Need to pass one of batch, next, or auto")


def _run_chronam(subquest: str, output: Path, scrape_kwargs: dict) -> QuestStatus:
    scrape_kwargs["batch"] = subquest
    quest = ChroniclingAmericaQuest(
        subquest=subquest, output=output, resume=scrape_kwargs.get("resume", False)
    )
    return quest.run(
        scrape_kwargs=scrape_kwargs,
    )


def _upload_chronam(res: QuestStatus, torrent_dir: Path) -> Upload | None:
    click.echo(f"Uploading {res.quest} - {res.subquest}")
    try:
        # use the spider to get a webseed url
        webseed_urls = ChroniclingAmericaSpider.webseed_urls(res.subquest.replace("-", "_"))
        upload, torrent_path = upload_subquest(
            status=res,
            torrent_dir=torrent_dir,
            progress=True,
            torrent_kwargs={"webseeds": webseed_urls},
        )

        click.echo(f"Uploaded {res.quest} - {res.subquest}")
        rprint(upload)

        _upload_to_client(
            torrent_path=torrent_path, data_path=res.path.parent, tags=[res.quest, "sciop-scraper"]
        )

        return upload
    except Exception as e:
        click.echo(f"Error trying to upload {res.quest} - {res.subquest}:\n{e}", err=True)


def _upload_to_client(torrent_path: Path, data_path: Path, **kwargs: Any) -> None:
    """Upload to a locally configured bittorrent client, if any"""
    cfg = get_config()
    clients = [c for c in cfg.clients if c.host in ("localhost", "127.0.0.1")]
    if not clients:
        click.echo(
            "No local bittorrent clients configured, so not seeding yet. "
            f"Add the torrent {torrent_path} to your client manually. "
            "use `sciop-cli client login` to add a client!"
        )
        return

    for client in clients:
        try:
            adapter = client.make_adapter()
            adapter.add_torrent_file(torrent_path=torrent_path, data_path=data_path, **kwargs)
            click.echo(
                f"Uploaded {torrent_path} to {client.client} client at {client.host}:{client.port}"
            )
        except Exception as e:
            click.echo(
                f"Error trying to upload {torrent_path} to {client.client} at "
                f"{client.host}:{client.port}, "
                f"Got exception: \n{e}",
                err=True,
            )


def _next_chronam(
    output: Path, scrape_kwargs: dict, upload: bool, torrent_dir: Path, new: bool = False
) -> tuple[QuestStatus, Upload | None] | None:
    """Get any incomplete subquests, or else get the next one"""
    log = QuestLog.from_json(output / "quest-log.json")
    if upload:
        existing = [
            subq
            for subq in log.subquests
            if subq.quest == "chronicling-america"
            and (subq.status not in ("uploaded",) or subq.result != "success")
        ]
    else:
        existing = [
            subq
            for subq in log.subquests
            if subq.quest == "chronicling-america"
            and (subq.status not in ("complete", "uploaded") or subq.result != "success")
        ]

    # filter impossible or disabled items
    existing = [e for e in existing if e.status != "disabled" and e.result != "impossible"]

    if len(existing) > 0 and not new:
        subquest = existing[0].subquest
        click.echo(f"Resuming previous incomplete subquest {subquest}")
    else:
        claim = claim_next("chronicling-america")
        if claim is None:
            click.echo("No unclaimed dataset parts remaining! quest complete!")
            return
        click.echo(f"Claimed next subquest {claim['dataset_part']}")
        subquest = claim["dataset_part"]
    res = _run_chronam(subquest=subquest, output=output, scrape_kwargs=scrape_kwargs)
    click.echo(f"Completed scraping {res.subquest}")
    rprint(res)
    ul = None
    if upload:
        ul = _upload_chronam(res=res, torrent_dir=torrent_dir)
    return res, ul


def _auto_chronam(
    output: Path, scrape_kwargs: dict, upload: bool, torrent_dir: Path, new: bool = False
) -> list[tuple[QuestStatus, dict]]:
    results = []
    try:
        while True:
            res = _next_chronam(
                output=output,
                scrape_kwargs=scrape_kwargs,
                upload=upload,
                torrent_dir=torrent_dir,
                new=new,
            )
            if res is None:
                break
            results.append(res)

    except KeyboardInterrupt:
        pass
    finally:
        # format results as a table
        tab = Table(title="sciop-scrape --auto summary")
        tab.add_column("subquest")
        tab.add_column("result")
        tab.add_column("status")
        tab.add_column("uploaded")
        for res in results:
            qstatus, ul = res
            thash = "-"
            if ul is not None:
                thash = ul["torrent"]["short_hash"]
            tab.add_row(qstatus.subquest, qstatus.result, qstatus.status, thash)
        console = Console()
        console.print(tab)

    return results
