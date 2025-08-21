import os
import webbrowser
from typing import TYPE_CHECKING, Optional

import click

from ..utils.config import PRIMITIVE_CREDENTIALS_FILEPATH
from ..utils.printer import print_result
from .actions import Auth

if TYPE_CHECKING:
    from ..client import Primitive


@click.group()
@click.pass_context
def cli(context):
    """Authentication"""
    pass


@cli.command("whoami")
@click.pass_context
def whoami_command(context):
    """Whoami"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    result = primitive.auth.whoami()
    if context.obj["DEBUG"] or context.obj["JSON"]:
        message = result.data
    else:
        message = f"Logged in as {result.data['whoami']['username']}"
    print_result(message=message, context=context)


@cli.command("config")
@click.pass_context
@click.option(
    "--transport",
    required=False,
    default="https",
    show_default="https",
    help="Transport protocol for Primitive API",
)
@click.option(
    "--auth-token",
    prompt=True,
    default=lambda: os.environ.get("PRIMITIVE_TOKEN", ""),
    hide_input=True,
    help="Authentication token for Primitive API",
)
def config_command(context, transport: str, auth_token: Optional[str] = None):
    """Configure the CLI"""
    token = os.environ.get("PRIMITIVE_TOKEN", auth_token)
    if not token and context.obj.get("YES"):
        raise click.ClickException(
            "PRIMITIVE_TOKEN environment variable is required for non-interactive mode"
        )
    host = context.obj.get("HOST", "api.primitive.tech")
    while not token:
        account_settings_url = (
            f"{transport}://{host.replace('api', 'app')}/account/tokens"
        )
        if "localhost" in host:
            account_settings_url = "http://localhost:3000/account/tokens"
        click.secho(
            f"You can find or create a Primitive API token at {account_settings_url}",
            fg="yellow",
        )

        webbrowser.open_new_tab(account_settings_url)
        token = click.prompt(
            "Please enter your Primitive API token", hide_input=True, type=str
        )

    auth = Auth(primitive=None)
    auth.setup_config(token=token, host=host, transport=transport)
    message = f"Config created at '{PRIMITIVE_CREDENTIALS_FILEPATH}' on host '{host}'"  # noqa
    print_result(message=message, context=context, fg="green")
