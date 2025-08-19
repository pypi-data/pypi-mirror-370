import re
from pathlib import Path
from typing import Any, Literal

import click
from rich import print as rprint
from sciop_cli.api import claim_next
from sciop_cli.config import get_config

from sciop_scraping.quests import QuestLog
from sciop_scraping.quests.base import upload_subquest
from sciop_scraping.quests.smithsonian.const import BUCKET_URL, DATASETS
from sciop_scraping.quests.smithsonian.quest import SmithsonianQuest


@click.command("smithsonian")
@click.option("-o", "--output", type=click.Path(dir_okay=True, file_okay=False), default=None)
@click.option("-d", "--dataset", type=click.Choice(DATASETS), required=False)
@click.option("-f", "--format", type=click.Choice(("jpg", "tif")), required=False)
@click.option(
    "--next",
    help="Claim, download, and upload the next available dataset part from the quest. "
    "Must have already logged in with `sciop-cli login` or `sciop-scrape api login`. "
    "Mutually exclusive with --batch and --auto.",
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
def smithsonian(
    output: Path = None,
    dataset: str | None = None,
    format: Literal["jpg", "tif"] | None = None,
    next: bool = False,
    upload: bool = True,
) -> None:
    """
    Batches from the smithsonian public s3 bucket
    """
    output = Path.cwd() / "data" if output is None else Path(output)
    torrent_dir = output / "torrents"

    if not next and (not dataset or not format):
        raise ValueError("If not using --next, must specify dataset and format explicitly")
    elif next:
        dataset_slug, format = _next_batch(output, upload)
        dataset = re.sub(r"^si-", "", dataset_slug)
        if dataset is None:
            return
    else:
        dataset_slug = "si-" + dataset

    quest = SmithsonianQuest(
        output=output,
        dataset_slug=dataset_slug,
        subquest=f"{dataset}-{format}",
        format=format,
        part_slugs=[format],
    )
    quest.meta_path.parent.mkdir(parents=True, exist_ok=True)
    res = quest.run(
        process_kwargs={
            "settings": {"FEEDS": {quest.meta_path: {"format": "jsonlines", "overwrite": True}}}
        }
    )
    if upload:
        torrent_dir.mkdir(exist_ok=True)
        upload, torrent_path = upload_subquest(
            status=res,
            torrent_dir=torrent_dir,
            torrent_path=torrent_dir / f"si-{dataset}-{format}.torrent",
            progress=True,
            torrent_kwargs={"webseeds": [BUCKET_URL + "/media/"]},
        )
        click.echo(f"Uploaded {res.quest} - {res.subquest}")
        rprint(upload)

        _upload_to_client(
            torrent_path=torrent_path, data_path=res.path.parent, tags=[res.quest, "sciop-scraper"]
        )
        res.status = "uploaded"
        quest_log = QuestLog.from_json(output / "quest-log.json")
        quest_log.update(res)
        quest_log.to_json(path=output / "quest-log.json")
    rprint(res)


def _next_batch(output: Path, upload: bool) -> tuple[str, str] | tuple[None, None]:
    log = QuestLog.from_json(output / "quest-log.json")
    if upload:
        existing = [
            subq
            for subq in log.subquests
            if subq.quest == "smithsonian"
            and (subq.status not in ("uploaded",) or subq.result != "success")
        ]
    else:
        existing = [
            subq
            for subq in log.subquests
            if subq.quest == "smithsonian"
            and (subq.status not in ("complete", "uploaded") or subq.result != "success")
        ]

    # filter impossible or disabled items
    existing = [e for e in existing if e.status != "disabled" and e.result != "impossible"]

    if len(existing) > 0:
        subquest = existing[0].subquest
        click.echo(f"Resuming previous incomplete subquest {subquest}")
        return existing[0].dataset_slug, existing[0].part_slugs[0]
    else:
        claim = None
        for ds in DATASETS:
            claim = claim_next(f"si-{ds}")
            if claim:
                click.echo(f"Claimed next subquest: {claim['dataset']} - {claim['dataset_part']}")
                return claim["dataset"], claim["dataset_part"]
        click.echo("No unclaimed dataset parts remaining! quest complete!")
        return None, None


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
