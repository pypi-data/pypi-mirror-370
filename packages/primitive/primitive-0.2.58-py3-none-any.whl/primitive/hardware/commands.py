from typing import TYPE_CHECKING, Optional

import click

from ..utils.printer import print_result
from .ui import render_hardware_table

if TYPE_CHECKING:
    from ..client import Primitive

from loguru import logger


@click.group()
@click.pass_context
def cli(context):
    """Hardware"""
    pass


@cli.command("systeminfo")
@click.pass_context
def systeminfo_command(context):
    """Get System Info"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    message = primitive.hardware.get_system_info()
    print_result(message=message, context=context)


@cli.command("register")
@click.option(
    "--organization",
    type=str,
    help="Organization [slug] to register hardware with",
)
@click.pass_context
def register_command(context, organization: Optional[str] = None):
    """Register Hardware with Primitive"""
    primitive: Primitive = context.obj.get("PRIMITIVE")

    organization_id = None
    if organization:
        organization_data = primitive.organizations.get_organization(slug=organization)
        organization_id = organization_data.get("id")

    if not organization_id:
        logger.info("Registering hardware with the default organization.")

    result = primitive.hardware.register(organization_id=organization_id)
    color = "green" if result else "red"
    if result.data.get("registerHardware"):
        message = "Hardware registered successfully"
    else:
        message = (
            "There was an error registering this device. Please review the above logs."
        )
    print_result(message=message, context=context, fg=color)


@cli.command("unregister")
@click.pass_context
def unregister_command(context):
    """Unregister Hardware with Primitive"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    result = primitive.hardware.unregister()
    color = "green" if result else "red"
    if not result:
        message = "There was an error unregistering this device. Please review the above logs."
        return
    elif result.data.get("unregisterHardware"):
        message = "Hardware unregistered successfully"
    print_result(message=message, context=context, fg=color)


@cli.command("checkin")
@click.pass_context
def checkin_command(context):
    """Checkin Hardware with Primitive"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    check_in_http_result = primitive.hardware.check_in_http()
    if messages := check_in_http_result.data.get("checkIn").get("messages"):
        print_result(message=messages, context=context, fg="yellow")
    else:
        message = "Hardware checked in successfully"
        print_result(message=message, context=context, fg="green")


@cli.command("list")
@click.pass_context
def list_command(context):
    """List Hardware"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    get_hardware_list_result = primitive.hardware.get_hardware_list(
        nested_children=True
    )

    hardware_list = [
        hardware.get("node")
        for hardware in get_hardware_list_result.data.get("hardwareList").get("edges")
    ]

    if context.obj["JSON"]:
        print_result(message=hardware_list, context=context)
        return
    else:
        render_hardware_table(hardware_list)


@cli.command("get")
@click.pass_context
@click.argument(
    "hardware_identifier",
    type=str,
    required=True,
)
def get_command(context, hardware_identifier: str) -> None:
    """Get Hardware"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    hardware = primitive.hardware.get_hardware_from_slug_or_id(
        hardware_identifier=hardware_identifier
    )

    if context.obj["JSON"]:
        print_result(message=hardware, context=context)
        return
    else:
        render_hardware_table([hardware])
