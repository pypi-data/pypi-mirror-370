import click

from ..utils.printer import print_result

import typing

if typing.TYPE_CHECKING:
    from ..client import Primitive


@click.group()
@click.pass_context
def cli(context):
    """Jobs Commands"""
    pass


@cli.command("list")
@click.pass_context
def list(
    context,
    organization_slug: str = None,
    organization_id: str = None,
):
    """List Job"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    message = primitive.jobs.get_jobs()
    print_result(message=message, context=context)


@cli.command("details")
@click.argument("job_slug")
@click.pass_context
def details(
    context,
    job_slug: str = None,
):
    """List Job"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    message = primitive.jobs.get_jobs(slug=job_slug)
    print_result(message=message, context=context)
