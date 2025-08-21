from typing import TYPE_CHECKING, Optional

import click

if TYPE_CHECKING:
    from ..client import Primitive


@click.command("monitor")
@click.option("--job-run-id", type=str, help="Explicit Job Run to pull")
@click.pass_context
def cli(context, job_run_id: Optional[str] = None):
    """monitor"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    primitive.monitor.start(job_run_id=job_run_id)
