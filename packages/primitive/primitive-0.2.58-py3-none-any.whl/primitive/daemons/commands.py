import click

import typing
from typing import Optional
from .ui import render_daemon_list

from loguru import logger

if typing.TYPE_CHECKING:
    from ..client import Primitive


@click.group()
@click.pass_context
def cli(context):
    """Daemon"""
    pass


@cli.command("install")
@click.pass_context
@click.argument(
    "name",
    type=str,
    required=False,
)
def install_daemon_command(context, name: Optional[str]):
    """Install the full primitive daemon"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    installed = primitive.daemons.install(name=name)

    if installed:
        logger.info(":white_check_mark: daemon(s) installed successfully!")
    else:
        logger.error("Unable to install daemon(s).")


@cli.command("uninstall")
@click.pass_context
@click.argument(
    "name",
    type=str,
    required=False,
)
def uninstall_daemon_command(context, name: Optional[str]):
    """Uninstall the full primitive Daemon"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    uninstalled = primitive.daemons.uninstall(name=name)

    if uninstalled:
        logger.info(":white_check_mark: daemon(s) uninstalled successfully!")
    else:
        logger.error("Unable to uninstall daemon(s).")


@cli.command("stop")
@click.pass_context
@click.argument(
    "name",
    type=str,
    required=False,
)
def stop_daemon_command(context, name: Optional[str]):
    """Stop primitive Daemon"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    stopped = primitive.daemons.stop(name=name)

    if stopped:
        logger.info(":white_check_mark: daemon(s) stopped successfully!")
    else:
        logger.error("Unable to stop daemon(s).")


@cli.command("start")
@click.pass_context
@click.argument(
    "name",
    type=str,
    required=False,
)
def start_daemon_command(context, name: Optional[str]):
    """Start primitive Daemon"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    started = primitive.daemons.start(name=name)

    if started:
        logger.info(":white_check_mark: daemon(s) started successfully!")
    else:
        logger.error("Unable to start daemon(s).")


@cli.command("logs")
@click.pass_context
@click.argument(
    "name",
    type=str,
    required=True,
)
def log_daemon_command(context, name: str):
    """Logs from primitive Daemon"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    primitive.daemons.logs(name=name)


@cli.command("list")
@click.pass_context
def list_daemon_command(context):
    """List all daemons"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    daemon_list = primitive.daemons.list()
    render_daemon_list(daemons=daemon_list)
