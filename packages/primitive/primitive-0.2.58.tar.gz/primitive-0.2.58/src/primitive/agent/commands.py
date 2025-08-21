import typing

import click

if typing.TYPE_CHECKING:
    from ..client import Primitive


@click.command("agent")
@click.option("--job-run-id", type=str, help="Explicit Job Run to pull")
@click.pass_context
def cli(context, job_run_id: typing.Optional[str] = None):
    """agent"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    primitive.agent.start(job_run_id=job_run_id)
