import json
import typing
from pathlib import Path

import click

from ..utils.printer import print_result

if typing.TYPE_CHECKING:
    from ..client import Primitive


@click.group("files")
@click.pass_context
def cli(context):
    """Files"""
    pass


@cli.command("upload")
@click.pass_context
@click.argument("path", type=click.Path(exists=True))
@click.option("--public", "-p", help="Is this a Public file", is_flag=True)
@click.option("--key-prefix", "-k", help="Key Prefix", default="")
@click.option("--direct", "-k", help="direct", is_flag=True)
def file_upload_command(context, path, public, key_prefix, direct):
    """File Upload"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    path = Path(path)
    if direct:
        result = primitive.files.upload_file_direct(
            path, is_public=public, key_prefix=key_prefix
        )
    else:
        result = primitive.files.upload_file_via_api(
            path, is_public=public, key_prefix=key_prefix
        )
    try:
        message = json.dumps(result.data)
    except AttributeError:
        message = "File Upload Failed"

    print_result(message=message, context=context)
