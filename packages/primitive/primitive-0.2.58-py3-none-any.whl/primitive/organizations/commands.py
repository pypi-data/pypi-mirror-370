import click

from ..utils.printer import print_result

import typing

if typing.TYPE_CHECKING:
    from ..client import Primitive


@click.group()
@click.pass_context
def cli(context):
    """Organizations Commands"""
    pass


@cli.command("list")
@click.pass_context
def details(context):
    """List Organizations"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    message = primitive.organizations.get_organizations()
    print_result(message=message, context=context)
