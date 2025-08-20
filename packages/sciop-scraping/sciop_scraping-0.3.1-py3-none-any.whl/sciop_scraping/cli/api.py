import click
from sciop_cli.cli import api as _api


# mount sciop-cli API commands
@click.group("api")
def sciop_api() -> None:
    """API commands from sciop-cli"""


sciop_api.add_command(_api.login)
sciop_api.add_command(_api.upload)
sciop_api.add_command(_api.claims)
