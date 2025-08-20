from pathlib import Path
from typing import Any

from sciop_scraping.quests import Quest, QuestStatus
from sciop_scraping.quests.chronicling.spider import ChroniclingAmericaSpider
from sciop_scraping.validation import pick_bagit_manifest, validate_bagit_manifest


class ChroniclingAmericaQuest(Quest):
    name = "chronicling-america"
    dataset_slug = "chronicling-america"
    spider = ChroniclingAmericaSpider
    resume: bool = False

    @property
    def subquest_path(self) -> Path:
        return self.output / self.name / self.subquest.replace("-", "_")

    def before_scrape(self, res: "QuestStatus", **kwargs: Any) -> tuple["QuestStatus", dict]:
        """Set classvars on spider before scraping, add output dir to kwargs"""

        self.spider.USER_AGENT_OVERRIDE = kwargs.get("user_agent")
        self.spider.JOBDIR_OVERRIDE = kwargs.get("job_dir")
        if kwargs.get("retries"):
            self.spider.custom_settings["RETRY_TIMES"] = int(kwargs.get("retries"))

        # URLS contain the batch/subquest name, so we give the parent dir to the spider
        kwargs["output"] = self.subquest_path.parent
        return res, kwargs

    def validate_scrape(self, res: QuestStatus) -> QuestStatus:
        """Compare the crawled files to the *-manifest"""

        manifest = pick_bagit_manifest(self.subquest_path)
        errors = validate_bagit_manifest(
            self.subquest_path, manifest[0], remove=not self.resume, hash_when_missing=False
        )

        # since we exclude .tif files from the scrape, validation errors don't count here
        errors = [e for e in errors if e.path.suffix not in (".tif", ".tiff")]

        res.validation_errors = errors
        if errors:
            res.result = "validation_error"
        else:
            res.result = "success"
        return res
