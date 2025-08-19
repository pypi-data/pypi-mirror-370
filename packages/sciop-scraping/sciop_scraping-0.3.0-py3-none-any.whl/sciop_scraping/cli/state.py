from pathlib import Path

import click
from rich.console import Console

from sciop_scraping.cli.common import log_path
from sciop_scraping.quests.base import QuestLog


@click.group("state", invoke_without_command=True)
@click.pass_context
@log_path
def state_cli(
    ctx: click.Context,
    quest_log: str | Path,
) -> None:
    """
    Display or modify the state in a quest log.

    To display, call with no arguments or a --quest-log,
    otherwise, see --help of subcommands
    """
    quest_log = Path(quest_log)
    ctx.ensure_object(dict)
    ctx.obj["quest_log"] = quest_log
    if ctx.invoked_subcommand is None:
        log = QuestLog.from_json(quest_log)
        console = Console()
        console.print(log)
