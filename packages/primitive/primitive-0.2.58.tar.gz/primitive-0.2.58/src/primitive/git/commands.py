import os
import typing
from pathlib import Path

import click

from ..utils.printer import print_result

if typing.TYPE_CHECKING:
    from ..client import Primitive


import typing

if typing.TYPE_CHECKING:
    from ..client import Primitive


@click.group()
@click.pass_context
def cli(context):
    """Git related commands"""
    pass


@cli.command("download-ref")
@click.pass_context
@click.argument("git_repo_full_name", type=str)
@click.argument("git_ref", default="main", type=str)
@click.option(
    "--github-access-token",
    type=str,
    default=lambda: os.environ.get("GITHUB_ACCESS_TOKEN", ""),
)
@click.argument("destination", type=click.Path(exists=True), default=".")
def download_ref_command(
    context,
    git_repo_full_name: str,
    git_ref: str = "main",
    github_access_token: str = "",
    destination: Path = Path.cwd(),
):
    primitive: Primitive = context.obj.get("PRIMITIVE")
    path = primitive.git.download_git_repository_at_ref(
        git_repo_full_name=git_repo_full_name,
        git_ref=git_ref,
        github_access_token=github_access_token,
        destination=destination,
    )
    print_result(message=path, context=context)
