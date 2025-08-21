import typing

import click

if typing.TYPE_CHECKING:
    from ..client import Primitive


@click.command("exec")
@click.pass_context
@click.argument(
    "hardware_identifier",
    type=str,
    required=True,
)
@click.argument("command", nargs=-1, required=False)
def cli(context, hardware_identifier: str, command: str) -> None:
    """Exec"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    primitive.exec.execute_command(
        hardware_identifier=hardware_identifier, command=command
    )
