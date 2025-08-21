import click

from ..utils.printer import print_result

import typing

if typing.TYPE_CHECKING:
    from ..client import Primitive


@click.group()
@click.pass_context
def cli(context):
    """Projects Commands"""
    pass


@cli.command("list")
@click.pass_context
def list(context):
    """List Projects"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    message = primitive.projects.get_projects()
    print_result(message=message, context=context)
