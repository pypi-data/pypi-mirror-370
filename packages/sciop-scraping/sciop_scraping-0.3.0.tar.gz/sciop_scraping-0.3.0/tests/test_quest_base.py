from pathlib import Path

from rich.console import Console

from sciop_scraping.quests.base import QuestLog, QuestStatus, ValidationError


def test_status_table(tmp_path: Path):
    """
    Literally just check that the table prints, not trying to do ser/des for the table atm.
    """
    log = QuestLog(
        subquests=[
            QuestStatus(
                quest="sup",
                dataset_slug="sup",
                subquest="hey",
                path=tmp_path / "hey",
                validation_errors=[
                    ValidationError(
                        path=tmp_path / "hey" / "howdy.exe", type="uhh", msg="it was bad"
                    )
                ],
                status="scraping",
                result=None,
            ),
            QuestStatus(
                quest="sup",
                dataset_slug="sup",
                subquest="hello",
                path=tmp_path / "hello",
                status="complete",
                result="success",
            ),
            QuestStatus(
                quest="goodbye",
                dataset_slug="bye",
                subquest="bye",
                path=tmp_path / "bye",
                status="uploaded",
                result="success",
            ),
        ]
    )
    _ = log.to_tables()
    console = Console()
    console.print(log)
