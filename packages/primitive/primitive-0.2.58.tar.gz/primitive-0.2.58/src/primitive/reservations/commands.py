import typing

import click

if typing.TYPE_CHECKING:
    from ..client import Primitive
from typing import Optional

from ..utils.printer import print_result


@click.group()
@click.pass_context
def cli(context):
    """Reservations"""
    pass


@cli.command("list")
@click.pass_context
@click.option("--status", default="in_progress", type=str, help="Filter by status")
def list(context, status: Optional[str] = "in_progress"):
    """List reservations"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    get_reservations_result = primitive.reservations.get_reservations(status=status)
    message = get_reservations_result.data
    print_result(message=message, context=context)


@cli.command("get")
@click.pass_context
@click.argument("reservation_id", type=str)
def get(context, reservation_id: str):
    """Get a reservation"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    get_reservation_result = primitive.reservations.get_reservation(
        reservation_id=reservation_id
    )
    message = get_reservation_result.data
    print_result(message=message, context=context)


@cli.command("create")
@click.pass_context
@click.argument("hardware_identifier", type=str)
@click.argument("reason", type=str)
@click.option(
    "--wait", default=True, type=bool, help="Wait for reservation to be in progress."
)
def create_reservation(context, hardware_identifier: str, reason: str, wait: bool):
    """Crate a reservation by a Hardware's ID or Slug"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    create_reservation_result = primitive.reservations.create_reservation(
        hardware_identifier=hardware_identifier, reason=reason, wait=wait
    )
    message = create_reservation_result.data
    print_result(message=message, context=context)


@cli.command("release")
@click.pass_context
@click.argument("reservation_or_hardware_identifier", type=str)
def release_reservation(context, reservation_or_hardware_identifier: str):
    """Release a reservation by Reservation ID, Hardware ID or Hardware Slug"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    release_reservation_result = primitive.reservations.release_reservation(
        reservation_or_hardware_identifier=reservation_or_hardware_identifier
    )
    message = release_reservation_result.data
    print_result(message=message, context=context)
