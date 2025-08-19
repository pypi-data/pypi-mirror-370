"""
A quest is a distributed scraping journey :)
A sciop instance contains a list of dataset parts to scrape,
a crawler will get a series of unclaimed parts,
crawl them, and upload the resulting torrents!
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any, ClassVar, Literal, Self, cast

from pydantic import BaseModel, Field, model_validator
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from sciop_cli.api import create_upload
from sciop_cli.data import get_default_trackers
from sciop_cli.models.sciop import Upload
from sciop_cli.torrent import create_torrent, find_optimal_piece_size
from scrapy import Spider
from scrapy.crawler import CrawlerProcess

from sciop_scraping.const import METHOD_STR
from sciop_scraping.exceptions import QuestInvalidUploadError


class Quest(BaseModel):
    """
    A scrape journey to go on with your friends
    """

    name: ClassVar[str]
    """
    Name that will be used when calling from the CLI.
    Each quest needs an (instance) unique name
    """
    dataset_slug: ClassVar[str]
    """
    Dataset slug on the sciop instance that this quest belongs to.
    
    Usually the same as `name`, but allowed to differ e.g.
    in the case of multiple quests for the same dataset.
    """
    part_slugs: list[str] | None = None
    """
    Part slugs that this subquest corresponds to.
    
    Typically, but not always, equivalent to `subquest`
    """
    spider: ClassVar[type[Spider] | None] = None
    """
    Scrapy spider to use, if any
    """

    output: Path
    """
    Output directory to write to.
    
    The output directory stores data for *all* quests and subquests.
    
    Quests should ensure that their scraper outputs data in a structure like..
    
    ```
    output
    |- quest_status.json
    |- quest_1
    |  |- subquest_1
    |  |  |- (data)
    |  |  ...
    |  |- subquest_1
    |  ...
    |- quest_2
    ...
    ```
    """
    subquest: str
    """
    The currently active subquest.
    """

    def run(
        self, scrape_kwargs: dict | None = None, process_kwargs: dict | None = None
    ) -> QuestStatus:
        if scrape_kwargs is None:
            scrape_kwargs = {}
        if process_kwargs is None:
            process_kwargs = {}

        status = self.init_status()
        try:
            if status.status == "scraping":
                status, scrape_kwargs = self.before_scrape(status, **scrape_kwargs)
                status = self.scrape(status, scrape_kwargs, process_kwargs)
                status = self.after_scrape(status)
                status.status = "validating"
            if status.status == "validating":
                status = self.before_validate(status)
                status = self.validate_scrape(status)
                if not status.validation_errors:
                    status.status = "packing"
                else:
                    status.result = "validation_error"
                status = self.after_validate(status)
            if status.status == "packing":
                status = self.before_pack(status)
                status = self.pack(status)
                status = self.after_pack(status)
                status.status = "complete"
            if status.result is None:
                # status would otherwise be set to validation_error in validate_scrape
                status.result = "success"
        finally:
            self.update_log(status)

        return status

    def init_status(self) -> QuestStatus:
        """
        Load any intermediate result from the quest log,
        or create a new one if none found.

        If we have previously attempted a subquest and ended with a validation error,
        retry from the scraping stage.
        """
        status = None
        if self.log_path.exists():
            log = QuestLog.from_json(self.log_path)
            status = log.get_subquest(self.name, self.subquest)

        if status is None:
            status = QuestStatus(
                quest=self.name,
                subquest=self.subquest,
                path=self.subquest_path,
                dataset_slug=self.dataset_slug,
                part_slugs=[self.subquest] if not self.part_slugs else self.part_slugs,
            )
        else:
            # if we have previously completed with a validation error and are running again,
            # return to scraping state.
            if status.result == "validation_error":
                status.status = "scraping"

        status.n_attempts += 1

        return status

    @property
    def log_path(self) -> Path:
        return self.output / "quest-log.json"

    @property
    def subquest_path(self) -> Path:
        return self.output / self.name / self.subquest

    def update_log(self, res: QuestStatus) -> None:
        """
        Update the log, replacing the
        :param res:
        :return:
        """
        log = QuestLog.from_json(self.log_path)
        log = log.update(res)
        log.to_json(self.log_path)

    def scrape(self, res: QuestStatus, scrape_kwargs: dict, process_kwargs: dict) -> QuestStatus:
        """
        Run the spider - default is to use the scrapy spider
        """
        return self._scrape_with_spider(res, scrape_kwargs, process_kwargs)

    def validate_scrape(self, res: QuestStatus) -> QuestStatus:
        """
        After scraping, subclasses may override to perform validation.

        Default is no-op
        """
        return res

    def pack(self, res: QuestStatus) -> QuestStatus:
        """
        After validating, subclasses may override to perform packing.

        Default is no-op
        """
        return res

    def before_scrape(self, res: QuestStatus, **kwargs: any) -> tuple[QuestStatus, dict]:
        """Hook method called before scraping"""
        return res, kwargs

    def after_scrape(self, res: QuestStatus) -> QuestStatus:
        """Hook method called after scraping"""
        return res

    def before_validate(self, res: QuestStatus) -> QuestStatus:
        """Hook method called before validation"""
        return res

    def after_validate(self, res: QuestStatus) -> QuestStatus:
        """Hook method called after validation"""
        return res

    def before_pack(self, res: QuestStatus) -> QuestStatus:
        """Hook method called before packing"""
        return res

    def after_pack(self, res: QuestStatus) -> QuestStatus:
        """Hook method called after packing"""
        return res

    def _scrape_with_spider(
        self, res: QuestStatus, scrape_kwargs: dict, process_kwargs: dict
    ) -> QuestStatus:
        if self.spider is None:
            raise RuntimeError("No spider has been declared, but attempted to scrape with spider")

        process = CrawlerProcess(**process_kwargs)
        process.crawl(self.spider, **scrape_kwargs)
        process.start(install_signal_handlers=False)
        return res


class QuestStatus(BaseModel):
    quest: str
    subquest: str
    path: Path
    """Directory where the data was scraped to"""
    dataset_slug: str
    """
    Corresponding dataset in the sciop instance
    Usually equivalent to `quest`, but allowed to differ 
    e.g. for multiple quests for the same dataset.
    """
    part_slugs: list[str] | None
    """
    Part slugs that this subquest corresponds to.
    Allowed to be separable from subquest so that a subquest might refer to multiple dataset parts,
    or their names may differ.
    """
    scrape_errors: list[ScrapeError] = Field(default_factory=list)
    validation_errors: list[ValidationError] = Field(default_factory=list)
    status: Literal["scraping", "validating", "packing", "complete", "uploaded", "disabled"] = (
        "scraping"
    )
    n_attempts: int = 0
    result: None | Literal["success", "validation_error", "impossible"] = None

    _TABLE_COLS: ClassVar[tuple[str]] = ("subquest", "status", "result", "errors", "n_attempts")

    @model_validator(mode="before")
    @classmethod
    def fill_dataset_and_part_slugs(cls, data: dict | QuestStatus) -> dict | QuestStatus:
        """
        If dataset_slug or part_slugs are missing (e.g. from old version of quest status format,
        fill them.
        """
        if isinstance(data, dict):
            if "dataset_slug" not in data:
                data["dataset_slug"] = data["quest"]
            if "part_slugs" not in data:
                data["part_slugs"] = [data["subquest"]]
        elif isinstance(data, BaseModel):
            data = cast(QuestStatus, data)
            if not data.dataset_slug:
                data.dataset_slug = data.quest
            if not data.part_slugs:
                data.part_slugs = [data.subquest]
        return data

    @property
    def total_errors(self) -> int:
        return len(self.scrape_errors) + len(self.validation_errors)

    def to_comment(self) -> str:
        """Format quest status as a string to be used in a torrent comment"""
        dumped = self.model_dump(
            exclude_none=True, exclude={"path", "scrape_errors", "validation_errors"}
        )
        dumped["scrape_errors"] = len(self.scrape_errors)
        dumped["validation_errors"] = len(self.validation_errors)
        comment_parts = [f"Scraped with {METHOD_STR}"]
        comment_parts.extend([f"{key}: {value}" for key, value in dumped.items()])
        return "\n".join(comment_parts)

    def table_row(self) -> list[Text]:
        style_map = {
            "bright_green": {"success", "complete"},
            "bright_red": {"validation_error", "impossible"},
            "bright_blue": {"uploaded"},
        }
        styles = {value: style for style, values in style_map.items() for value in values}
        row = []
        for key in self._TABLE_COLS:
            if key == "errors":
                row.append(
                    Text(
                        str(self.total_errors),
                        style="bright_red" if self.total_errors > 0 else None,
                    )
                )
            else:
                value = str(getattr(self, key))
                row.append(Text(value, style=styles.get(value)))
        return row


class QuestLog(BaseModel):
    subquests: list[QuestStatus] = Field(default_factory=list)

    def get_subquest(self, quest: str, subquest: str) -> QuestStatus | None:
        matches = [q for q in self.subquests if q.quest == quest and q.subquest == subquest]
        if len(matches) > 1:
            raise KeyError(f"More than one match found for quest {quest}, subquest {subquest}")
        elif len(matches) == 1:
            return matches[0]
        else:
            return None

    def update(self, res: QuestStatus) -> Self:
        """
        Add new entry to log, replacing any previous matches
        """
        items = [q for q in self.subquests if q.quest != res.quest or q.subquest != res.subquest]
        existing = [
            q for q in self.subquests if q.quest == res.quest and q.subquest == res.subquest
        ]
        if existing:
            res = self.merge_errors(res, existing[0])
        items.append(res)
        self.subquests = items
        return self

    def merge_errors(self, res: QuestStatus, existing: QuestStatus) -> QuestStatus:
        """
        Merge errors from the previous status, updating the n_errors in each.
        """
        old_scrape_map = {e.url: e for e in existing.scrape_errors}
        old_validation_map = {e.path: e for e in existing.validation_errors}

        for e in res.scrape_errors:
            if e.url in old_scrape_map:
                e.n_failures = old_scrape_map[e.url].n_failures + 1
        for e in res.validation_errors:
            if e.path in old_validation_map:
                e.n_failures = old_validation_map[e.path].n_failures + 1
        return res

    @classmethod
    def from_json(cls, path: Path) -> QuestLog:
        if not path.exists():
            return QuestLog()

        try:
            with open(path) as f:
                log = json.load(f)
        except json.decoder.JSONDecodeError:
            warnings.warn(
                f"Quest log could not be read from {str(path)}, ignoring, will overwrite",
                stacklevel=2,
            )
            log = []
        return QuestLog(subquests=log)

    def to_json(self, path: Path) -> None:
        items = self.model_dump(by_alias=True)["subquests"]
        with open(path, "w") as f:
            json.dump(items, f, indent=2, default=str)

    def to_tables(self) -> dict[str, Table]:
        tables = {}
        for subquest in self.subquests:
            if subquest.quest not in tables:
                tables[subquest.quest] = Table(*QuestStatus._TABLE_COLS, title=subquest.quest)
            tables[subquest.quest].add_row(*subquest.table_row())
        return tables

    def __rich__(self) -> Panel:
        group = Group(*self.to_tables().values())
        return Panel(group, title="sciop quest log")


class ScrapeError(BaseModel):
    url: str
    type_: str = Field(..., alias="type")
    msg: str
    n_failures: int = 1


class ValidationError(BaseModel):
    path: Path
    type_: str = Field(..., alias="type")
    msg: str
    n_failures: int = 1


def _make_subquest_torrent(
    status: QuestStatus,
    torrent_path: Path,
    progress: bool = False,
    torrent_kwargs: dict | None = None,
) -> Path:
    """
    Make a torrent for a subquest.
    This ignores completeness/validation errors and just makes the torrent,
    it should typically be called from upload_subquest instead
    """
    default_torrent_kwargs: dict[str, Any] = {
        "version": "hybrid",
        "bencode": True,
        "pbar": progress,
        "comment": status.to_comment(),
    }
    if torrent_kwargs is None:
        torrent_kwargs = default_torrent_kwargs
    else:
        torrent_kwargs = {**default_torrent_kwargs, **torrent_kwargs}

    if "piece_size" not in torrent_kwargs:
        torrent_kwargs["piece_size"] = find_optimal_piece_size(
            status.path, version=torrent_kwargs["version"]
        )
    if "trackers" not in torrent_kwargs:
        torrent_kwargs["trackers"] = get_default_trackers()

    bencoded = create_torrent(path=status.path, **torrent_kwargs)
    with open(torrent_path, "wb") as f:
        f.write(bencoded)
    return torrent_path


def upload_subquest(
    status: QuestStatus,
    torrent_dir: Path,
    torrent_path: Path | None = None,
    force: bool = False,
    progress: bool = False,
    torrent_kwargs: dict = None,
) -> tuple[Upload, Path]:
    """
    Upload a subquest that has been completed!

    Create a torrent, then upload it to the configured sciop instance using a local sciop-cli config

    args:
        status (QuestStatus): The status object containing information about the given subquest
        torrent_dir (Path): Directory where the torrent will be created
        force (bool, optional): Upload even if quest was incomplete or not validated,
            and recreate torrent even if it's absent
        progress (bool): Display progress bar while creating torrent
        torrent_kwargs (dict, optional): Keyword arguments to pass to sciop-cli create_torrent
    """
    if (status.status != "complete" or status.result != "success") and not force:
        raise QuestInvalidUploadError(
            f"Quest could not be uploaded when it is incomplete or had validation errors: {status}"
        )

    if torrent_path is None:
        torrent_path = torrent_dir / (status.subquest + ".torrent")
    if torrent_path.exists() and not force:
        warnings.warn(
            f"Expected output torrent already exists and force was False, not recreating torrent.\n"
            f"path: {torrent_path}",
            stacklevel=2,
        )
    else:
        _make_subquest_torrent(
            status=status,
            torrent_path=torrent_path,
            progress=progress,
            torrent_kwargs=torrent_kwargs,
        )

    upload = create_upload(
        dataset=status.dataset_slug,
        dataset_parts=status.part_slugs,
        torrent_path=torrent_path,
        method=METHOD_STR,
    )

    # upload subquest status and save to quest log
    status.status = "uploaded"
    quest_log = QuestLog.from_json(torrent_dir.parent / "quest-log.json")
    quest_log.update(status)
    quest_log.to_json(path=torrent_dir.parent / "quest-log.json")

    return upload, torrent_path
