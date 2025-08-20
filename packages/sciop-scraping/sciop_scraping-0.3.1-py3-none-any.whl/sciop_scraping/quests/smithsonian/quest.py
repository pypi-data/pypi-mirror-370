import hashlib
import json
import re
from pathlib import Path
from typing import Any, Literal

from tqdm import tqdm

from sciop_scraping.quests import Quest, QuestStatus, ValidationError
from sciop_scraping.quests.smithsonian.spider import SmithsonianSpider


class SmithsonianQuest(Quest):
    name = "smithsonian"
    spider = SmithsonianSpider

    dataset_slug: str
    format: Literal["jpg", "tif"]

    def before_scrape(self, res: QuestStatus, **kwargs: Any) -> tuple[QuestStatus, dict]:
        kwargs["format"] = self.format
        kwargs["dataset"] = self.archive_name
        kwargs["output"] = self.output
        return res, kwargs

    def validate_scrape(self, res: QuestStatus) -> QuestStatus:
        res.validation_errors = []
        with open(self.meta_path) as f:
            lines = f.readlines()
        if len(lines) == 0:
            res.validation_errors.append(
                ValidationError(path=self.data_path, type="no_files", msg="No files found!")
            )

        meta = [json.loads(line) for line in lines]
        for item in tqdm(meta, desc="Validating item presence"):
            key = re.sub(r"^media/", "", item["key"])
            path = self.output / "smithsonian" / f"{self.archive_name}-{self.format}" / key
            if not path.exists():
                res.validation_errors.append(
                    ValidationError(path=path, type="missing", msg="Expected file not found!")
                )

        if res.validation_errors:
            return res

        for item in tqdm(meta, desc="Validating item hashes"):
            key = re.sub(r"^media/", "", item["key"])
            path = self.output / "smithsonian" / f"{self.archive_name}-{self.format}" / key
            with open(path, "rb") as f:
                file_hash = hashlib.file_digest(f, "md5").hexdigest()
            if file_hash != item["etag"]:
                res.validation_errors.append(
                    ValidationError(
                        path=path, type="invalid", msg="File did not match etag and was removed!"
                    )
                )
                path.unlink(missing_ok=True)

        return res

    def pack(self, res: QuestStatus) -> QuestStatus:
        """Sort the item metadata"""
        items = {}
        with open(self.meta_path) as f:
            for line in f:
                parsed = json.loads(line)
                if parsed:
                    items[parsed["key"]] = parsed
        items = dict(sorted(items.items()))
        with open(self.meta_path, "w") as f:
            for item in items.values():
                f.write(json.dumps(item) + "\n")
        return res

    @property
    def archive_name(self) -> str:
        return re.sub(r"^si-", "", self.dataset_slug)

    @property
    def data_path(self) -> Path:
        return (
            self.output / "smithsonian" / f"{self.archive_name}-{self.format}" / self.archive_name
        )

    @property
    def subquest_path(self) -> Path:
        return self.data_path

    @property
    def meta_path(self) -> Path:
        return self.data_path / "metadata.jsonl"
