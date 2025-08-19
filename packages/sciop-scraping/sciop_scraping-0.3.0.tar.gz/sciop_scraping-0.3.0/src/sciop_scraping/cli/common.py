"""
Common options for cli commands
"""

from pathlib import Path

import click


def spider_options(f: click.Command) -> click.Command:
    """Common options that all spider cli commands should support"""
    f = click.option("--retries", type=int, help="Number of retries")(f)
    f = click.option("--timeout", type=int, help="Timeout for spider in seconds")(f)
    return f


def log_path(f: click.Command) -> click.Command:
    default_logfile = Path.cwd() / "data" / "quest-log.json"
    f = click.option(
        "-l",
        "--quest-log",
        type=click.Path(exists=True, file_okay=True, dir_okay=False),
        help="Path to quest log.",
        default=default_logfile,
        show_default=True,
    )(f)
    return f
